"""
Test Oturumu sayfası — adım adım (Paket 38b): taslak, sıra, değer girişi, aykırı değer uyarısı, kayıt.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import json as _json
import os
import pandas as pd
import re
import streamlit as st
from datetime import date
from veri.metinler import ACIKLAMALAR
from veri.normlar_kategorik import NORMATIF_TEST
from olcut.analiz import _birim, _konum_sayi
from olcut.bilesenler import _calisma_duzenleyici, _ot_ekle, _sayfaya_git, _sira_listesi, bolum_terimleri, coklu_secim
from olcut.esik import NORMATIF_ESIK_YAS
from olcut.katalog_islemleri import (
    TEST_KATALOGU, kanonik_test, sira_uyarilari, test_ara, test_bilgisi, test_etiketli, test_izi, test_raflari,
    test_yolu)
from olcut.kayit import (
    GRUP_KOLON, TOPLU_GIRIS_DISI, calisma_dokun, calisma_oturum_adi, calisma_sporculari, calismalar_oku,
    deger_metni, kayitlari_yaz, oturum_kayitlari, oturum_kimligi, oturum_sutunu)
from olcut.norm import (
    NORMATIF, NORMATIF_KAPSAM, NORMATIF_YAS, OTURUM_ADI_KOLON, SPORCU_DOSYA, turetilmis_degerler,
    yas_persentil_bul)
from olcut.ortak import (
    DOGUM_KOLON, METIN_DEGISKEN_KALIBI, NOT_CIPLERI, _girildi, ad_bicimi, guvenli_float, not_coz, not_metni,
    tam_yas)
from olcut.raporlar import _aralik_sayi


OT_ADIMLAR = ("Testler", "Sporcular", "Oturum bilgisi", "Değerler")


OT_KIPLER = ("Sıradaki", "Tablo")


TASLAK_DOSYA = "oturum_taslagi.json"


NOT_DEGISKENI = "Not"                 # tablo kipinde test başına not sütunu: "Test › Not" (xlsx'te "Notlar" alanı)


OT_AYKIRI_SORU = "Bu değer olağan aralığın dışında, doğru mu?"


OT_TASLAK_NOTU = "✓ Taslak otomatik kaydedildi"


OT_KORUNMAYAN = ("ot_g::", "ot_n::", "ot_nm::", "ot_tablo", "ot::ara::", "ot::sira::")


_MOBIL_AJAN = re.compile(r"Mobi|Android|iPhone|iPad|Tablet|Silk|Kindle", re.I)


def varsayilan_kip(ajan):
    """Telefon/tablet tarayıcısı → "Sıradaki"; bilgisayar → "Tablo" (ekran genişliği sunucuya gelmez; tarayıcı kimliği)."""
    return "Sıradaki" if _MOBIL_AJAN.search(str(ajan or "")) else "Tablo"


def _istemci_ajani():
    try:
        return str(st.context.headers.get("User-Agent", "") or "")
    except Exception:
        return ""


def _qp_al(ad):
    try:
        return st.query_params.get(ad)
    except Exception:
        return None


def _qp_ayarla(ad, deger):
    """Adres çubuğu parametresi (sayfa yenilenince taslağa dönmek için); eski sürümde sessizce atlanır."""
    try:
        if deger is None:
            if ad in st.query_params:
                del st.query_params[ad]
        elif st.query_params.get(ad) != deger:
            st.query_params[ad] = deger
    except Exception:
        pass


def taslak_bos(testler, sporcular, bilgi=None):
    return {"surum": 1, "testler": list(testler), "sporcular": list(sporcular), "bilgi": dict(bilgi or {}),
            "degerler": {}, "notlar": {}, "durum": {}, "konum": None, "zaman": ""}


def taslak_birlestir(eski, yeni):
    """Adımlar yeniden geçilince: aynı sporcu × test için girilmiş değer, not ve durum korunur."""
    if not eski:
        return yeni
    testler = set(yeni["testler"])
    ait = lambda sutun: any(sutun.startswith(oturum_sutunu(t, "")) for t in testler)
    for s in yeni["sporcular"]:
        d = {c: v for c, v in (eski.get("degerler", {}).get(s) or {}).items() if ait(c)}
        if d:
            yeni["degerler"][s] = d
        for alan in ("notlar", "durum"):
            x = {t: v for t, v in (eski.get(alan, {}).get(s) or {}).items() if t in testler}
            if x:
                yeni[alan][s] = x
    k = eski.get("konum")
    if k and k[0] in testler and k[1] in yeni["sporcular"]:
        yeni["konum"] = list(k)
    return yeni


def taslak_oku(yol=TASLAK_DOSYA):
    """Diskteki taslak ya da None (yok, bozuk ya da boş)."""
    try:
        with open(yol, encoding="utf-8") as f:
            t = _json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(t, dict) or not t.get("testler") or not t.get("sporcular"):
        return None
    for alan in ("degerler", "notlar", "durum", "bilgi"):
        if not isinstance(t.get(alan), dict):
            t[alan] = {}
    return t


def taslak_yaz(t, yol=TASLAK_DOSYA):
    """Taslağı diske yazar (önce geçici dosya, sonra yer değiştirme: yarım yazılmış dosya kalmaz)."""
    from datetime import datetime as _an
    t["zaman"] = _an.now().strftime("%H:%M:%S")
    gecici = yol + ".yaziliyor"
    try:
        with open(gecici, "w", encoding="utf-8") as f:
            _json.dump(t, f, ensure_ascii=False)
        os.replace(gecici, yol)
        return True
    except OSError:
        return False


def taslak_sil(yol=TASLAK_DOSYA):
    try:
        os.remove(yol)
    except OSError:
        pass


def taslak_deger_sayisi(t):
    return sum(1 for d in (t or {}).get("degerler", {}).values() for v in d.values() if str(v).strip())


def sayi_girdisi(metin):
    """Elle girilen sayı: virgül ya da nokta ondalık ("32,5" = "32.5"). Dönen: (kayıt metni, geçerli mi)."""
    m = str(metin or "").strip().replace(" ", "")
    if not m:
        return "", True
    try:
        f = float(m.replace(",", "."))
    except ValueError:
        return m, False
    if f != f or f in (float("inf"), float("-inf")):
        return m, False
    return deger_metni(f), True


def taslak_tablosu(t, testler, notlu=False):
    """Taslak → toplu giriş tablosu (satır sporcu, sütun "Test › Değişken"; notlu: test başına "Test › Not")."""
    sutunlar = ["Sporcu"]
    for test, ds in testler.items():
        sutunlar += [oturum_sutunu(test, d) for d in ds] + ([oturum_sutunu(test, NOT_DEGISKENI)] if notlu else [])
    satirlar = []
    for s in t["sporcular"]:
        r = {"Sporcu": s}
        dv = t.get("degerler", {}).get(s) or {}
        for test, ds in testler.items():
            for d in ds:
                c = oturum_sutunu(test, d)
                v = dv.get(c, "")
                if METIN_DEGISKEN_KALIBI.search(d):
                    r[c] = str(v or "")
                else:
                    try:
                        r[c] = float(v) if str(v).strip() else float("nan")
                    except ValueError:
                        r[c] = float("nan")
            if notlu:
                r[oturum_sutunu(test, NOT_DEGISKENI)] = not_metni((t.get("notlar", {}).get(s) or {}).get(test))
        satirlar.append(r)
    df = pd.DataFrame(satirlar, columns=sutunlar)
    for test, ds in testler.items():
        for d in ds:
            c = oturum_sutunu(test, d)
            df[c] = df[c].astype("object" if METIN_DEGISKEN_KALIBI.search(d) else "float64")
        if notlu:
            df[oturum_sutunu(test, NOT_DEGISKENI)] = df[oturum_sutunu(test, NOT_DEGISKENI)].astype("object")
    return df


def taslak_duzenleme_tablosu(t, testler):
    """Tablo kipinin düzenleme tablosu: değer hücreleri METİN (boş hücre boş görünür, virgül kabul: "4,52")."""
    sutunlar = ["Sporcu"] + [x for test, ds in testler.items()
                             for x in [oturum_sutunu(test, d) for d in ds] + [oturum_sutunu(test, NOT_DEGISKENI)]]
    satirlar = []
    for s in t["sporcular"]:
        dv = t.get("degerler", {}).get(s) or {}
        r = {"Sporcu": s}
        for test, ds in testler.items():
            for d in ds:
                v = str(dv.get(oturum_sutunu(test, d), "") or "")
                r[oturum_sutunu(test, d)] = v if METIN_DEGISKEN_KALIBI.search(d) else v.replace(".", ",")
            r[oturum_sutunu(test, NOT_DEGISKENI)] = not_metni((t.get("notlar", {}).get(s) or {}).get(test))
        satirlar.append(r)
    return pd.DataFrame(satirlar, columns=sutunlar).astype("object")


def taslak_tablodan(t, tablo, testler):
    """
    Tablo kipinde düzenlenen tabloyu taslağa yazar. Dönen: (değişti mi, geçersiz hücreler [(sporcu, sütun, metin)]).
    Sayı olmayan hücre taslağa yazılmaz. Değer girilen 'gelmedi' sporcu açılır.
    """
    eski = _json.dumps([t.get("degerler"), t.get("notlar"), t.get("durum")], sort_keys=True, ensure_ascii=False)
    gecersiz = []
    for _, r in tablo.iterrows():
        s = r["Sporcu"]
        dv = dict(t["degerler"].get(s) or {})
        for test, ds in testler.items():
            dolu = False
            for d in ds:
                c = oturum_sutunu(test, d)
                ham = r.get(c)
                if METIN_DEGISKEN_KALIBI.search(d):
                    v, gecerli = deger_metni(ham), True
                elif isinstance(ham, (int, float)) and not isinstance(ham, bool):
                    v, gecerli = deger_metni(ham), True
                else:
                    v, gecerli = sayi_girdisi(deger_metni(ham))
                if not gecerli:
                    gecersiz.append((s, c, v))
                    continue
                if v:
                    dv[c], dolu = v, True
                else:
                    dv.pop(c, None)
            nc = oturum_sutunu(test, NOT_DEGISKENI)
            if nc in tablo.columns:
                n = not_coz("" if r.get(nc) is None or (isinstance(r.get(nc), float) and r.get(nc) != r.get(nc))
                            else r.get(nc))
                if n["etiketler"] or n["metin"]:
                    t["notlar"].setdefault(s, {})[test] = n
                else:
                    (t["notlar"].get(s) or {}).pop(test, None)
            if dolu and (t["durum"].get(s) or {}).get(test) == "gelmedi":
                t["durum"][s].pop(test)
        if dv:
            t["degerler"][s] = dv
        else:
            t["degerler"].pop(s, None)
    return eski != _json.dumps([t.get("degerler"), t.get("notlar"), t.get("durum")], sort_keys=True,
                               ensure_ascii=False), gecersiz


def taslak_kayitlari(t, bilgiler, testler, yollar, tarih, ot_bilgi):
    """Taslak → xlsx kayıtları (eski toplu giriş yolu) + test başına not "Notlar" alanına. Dönen (kayıtlar, uyarılar)."""
    kayitlar, uyari = oturum_kayitlari(taslak_tablosu(t, testler), bilgiler, testler, "-", "-", None, tarih, ot_bilgi,
                                       yollar=yollar)
    for k in kayitlar:
        notlar = {kanonik_test(x): n for x, n in (t.get("notlar", {}).get(k["Sporcu"]) or {}).items()}
        k["Notlar"] = not_metni(notlar.get(k["Test"]))
    return kayitlar, uyari


def ot_kuyrugu(t):
    """Test bazlı sıra: aynı test sporcudan sporcuya, sonra sıradaki test."""
    return [(test, s) for test in t["testler"] for s in t["sporcular"]]


def ot_durumu(t, test, sporcu):
    return (t.get("durum", {}).get(sporcu) or {}).get(test)


def ot_ilerleme(t, test):
    """(yapılan ya da gelmedi işaretli sporcu sayısı, toplam) — bu test için."""
    return sum(1 for s in t["sporcular"] if ot_durumu(t, test, s) in ("tamam", "gelmedi")), len(t["sporcular"])


def ot_siradaki(t, sonra=None):
    """Kuyrukta 'sonra'dan sonraki ilk bekleyen (test, sporcu); başa sarar; hepsi bittiyse None."""
    kuyruk = ot_kuyrugu(t)
    bas = kuyruk.index(tuple(sonra)) + 1 if sonra and tuple(sonra) in kuyruk else 0
    for test, s in kuyruk[bas:] + kuyruk[:bas]:
        if ot_durumu(t, test, s) is None:
            return [test, s]
    return None


def ot_hesaplanan(test, degerler, bilgi):
    """Girilen değerlerden otomatik hesaplananlar (ör. sıçrama yüksekliği). Karşılaştırma YOK — yalnız sayı."""
    bilgi = bilgi or {}
    kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
    try:
        h, _ = turetilmis_degerler(test, {d: v for d, v in degerler.items() if v}, bilgi, kilo)
    except Exception:
        return {}
    return {k: v for k, v in h.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in degerler}


def ot_aykiri_uyarilari(t, bilgiler, testler, tarih, test, sporcu):
    """Tek sporcu × tek test için olağandışı değer ve hesap uyarıları (kayıt engellenmez)."""
    tek = {**t, "sporcular": [sporcu]}
    _, uyari = oturum_kayitlari(taslak_tablosu(tek, {test: testler[test]}), bilgiler, {test: testler[test]},
                                "-", "-", None, tarih, {})
    return uyari


def ot_adim_seridi_html(adim):
    """Adım şeridi: renk + simge + kelime (✓ tamamlandı, ● şu an, ○ sırada); 'Adım N / 4' ilerleme olarak."""
    oge = []
    for i, ad in enumerate(OT_ADIMLAR, 1):
        d = "tamam" if i < adim else ("simdi" if i == adim else "sonra")
        isaret = {"tamam": "✓", "simdi": "●", "sonra": "○"}[d]
        kelime = {"tamam": "tamamlandı", "simdi": "şu an", "sonra": "sırada"}[d]
        oge.append(f'<li class="ot-adim ot-{d}"' + (' aria-current="step"' if d == "simdi" else "")
                   + f'><span aria-hidden="true">{isaret}</span> {i}. {_html.escape(ad)}'
                   f'<span class="ot-gizli"> ({kelime})</span></li>')
    return (f'<nav class="ot-serit" aria-label="Oturum adımları"><p class="ot-sayac" role="progressbar" '
            f'aria-valuenow="{adim}" aria-valuemin="1" aria-valuemax="{len(OT_ADIMLAR)}">Adım {adim} / '
            f'{len(OT_ADIMLAR)}</p><ol>{"".join(oge)}</ol></nav>')


def ot_ilerleme_html(yapilan, toplam, etiket):
    yuzde = round(100 * yapilan / toplam) if toplam else 0
    return (f'<div class="ot-ilerleme" role="progressbar" aria-valuenow="{yapilan}" aria-valuemin="0" '
            f'aria-valuemax="{toplam}" aria-label="{_html.escape(etiket)}"><div class="ot-ilerleme-dolu" '
            f'style="width:{yuzde}%"></div></div><p class="ot-ilerleme-yazi">{_html.escape(etiket)}</p>')


def ot_sira_cipleri_html(t, test, simdiki):
    """Sıra çipleri YALNIZ BİLGİ (tıklanmaz): ✓ yapıldı, ● şu an, ○ kalan, – gelmedi."""
    p = []
    for s in t["sporcular"]:
        d = ot_durumu(t, test, s)
        sinif, isaret, kelime = (("simdi", "●", "şu an") if s == simdiki else
                                 ("tamam", "✓", "yapıldı") if d == "tamam" else
                                 ("gelmedi", "–", "gelmedi") if d == "gelmedi" else ("kalan", "○", "kalan"))
        p.append(f'<li class="ot-cip ot-{sinif}"><span aria-hidden="true">{isaret}</span> {_html.escape(ad_bicimi(s))}'
                 f'<span class="ot-gizli"> ({kelime})</span></li>')
    return f'<ul class="ot-cipler" aria-label="Ölçüm sırası">{"".join(p)}</ul>'


def _ot_durum_koru():
    """Görünmeyen adımın seçimleri silinmesin: Streamlit, o çalışmada çizilmeyen bileşenin durumunu temizler."""
    for k in list(st.session_state.keys()):
        k = str(k)
        if not (k.startswith("ot_") or k.startswith("ot::")) or k.startswith(OT_KORUNMAYAN):
            continue
        v = st.session_state[k]
        if isinstance(v, (list, str, date)) or (isinstance(v, (int, float)) and not isinstance(v, bool)):
            st.session_state[k] = v


def _ot_adim_git(n):
    st.session_state["ot_adim"] = n
    st.session_state.pop("ots::aykiri", None)
    st.session_state.pop("ots::aykiri_tablo", None)


def _ot_tablo_yenile():
    st.session_state["ot_tablo_surum"] = st.session_state.get("ot_tablo_surum", 0) + 1
    st.session_state.pop("ots::aykiri", None)
    st.session_state.pop("ots::aykiri_tablo", None)


def _ot_grup_adlari(df_ot, sporcular):
    g = {(df_ot.loc[df_ot["_ad"] == s, "_grup"].iloc[0] if (df_ot["_ad"] == s).any() else "") or "(Grubu girilmemiş)"
         for s in sporcular}
    return sorted(x for x in g if x != "(Grubu girilmemiş)") + (["(Grubu girilmemiş)"] if "(Grubu girilmemiş)" in g else [])


def _ot_taslak_yukle(t, df_ot):
    """Yarım kalan oturum: seçimler ve değerler geri gelir, Adım 4 açılır."""
    st.session_state["ots::taslak"] = t
    st.session_state["ots::testler"] = list(t["testler"])
    st.session_state["ots::sporcular"] = list(t["sporcular"])
    b_ = t.get("bilgi", {})
    st.session_state["ots::calisma"] = {"ad": b_.get("calisma"), "zaman": b_.get("zaman")}
    st.session_state["ot::ek"] = list(t["testler"])
    st.session_state["ot::sira"] = list(t["testler"])
    try:
        st.session_state["ot_tarih"] = date.fromisoformat(str(b_.get("tarih")))
    except ValueError:
        pass
    st.session_state["ot_yer"] = str(b_.get("yer", "") or "")
    st.session_state["ot_uyg"] = str(b_.get("uygulayan", "") or "")
    st.session_state["ot_ad"] = str(b_.get("ad", "") or "")
    calismalar = calismalar_oku()
    if b_.get("calisma") in calismalar:
        c = calismalar[b_["calisma"]]
        st.session_state["ot_kaynak"] = "Çalışma"
        st.session_state["ot_calisma"] = b_["calisma"]
        st.session_state[f"ot_zaman::{b_['calisma']}"] = b_.get("zaman")
        if c["gruplar"]:
            st.session_state[f"ot_c_gruplar::{b_['calisma']}"] = list(c["gruplar"])
            st.session_state[f"ot_c_sporcular::{b_['calisma']}::{'|'.join(c['gruplar'])}"] = list(t["sporcular"])
    else:
        st.session_state["ot_kaynak"] = "Serbest seçim"
        gruplar = _ot_grup_adlari(df_ot, t["sporcular"])
        st.session_state["ot_gruplar"] = gruplar
        st.session_state[f"ot_sporcular_{'|'.join(gruplar)}"] = list(t["sporcular"])
    st.session_state["ot_adim"] = 4
    _ot_tablo_yenile()


def _ot_taslak_temizle():
    taslak_sil()
    st.session_state["ots::taslak"] = None
    st.session_state["ots::taslak_sorma"] = True
    for k in [k for k in st.session_state if str(k).startswith(("ot_g::", "ot_n::", "ot_nm::"))]:
        st.session_state.pop(k, None)
    _qp_ayarla("taslak", None)


def _ot_degerlere_gec():
    """Adım 3 → 4: seçimlerden taslak kurulur (önceki taslağın aynı sporcu × test değerleri korunur) ve diske yazılır."""
    c = st.session_state.get("ots::calisma") or {}
    tarih = st.session_state.get("ot_tarih") or date.today()
    bilgi = {"tarih": tarih.isoformat(), "yer": str(st.session_state.get("ot_yer", "") or "").strip(),
             "uygulayan": str(st.session_state.get("ot_uyg", "") or "").strip(),
             "ad": str(st.session_state.get("ot_ad", "") or "").strip(),          # Paket 38d
             "calisma": c.get("ad"), "zaman": c.get("zaman")}
    yeni = taslak_birlestir(st.session_state.get("ots::taslak"),
                            taslak_bos(st.session_state.get("ots::testler", []),
                                       st.session_state.get("ots::sporcular", []), bilgi))
    st.session_state["ots::taslak"] = yeni
    taslak_yaz(yeni)
    st.session_state["ot_adim"] = 4
    _ot_tablo_yenile()


def _ot_deger_cb(test, sporcu, sutun, anahtar, sayisal):
    """Sıradaki kipinde her alan değişiminde: değer taslağa ve diske (geçersiz sayı yazılmaz, alanın altında uyarı)."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    ham = st.session_state.get(anahtar, "")
    v, gecerli = sayi_girdisi(ham) if sayisal else (str(ham or "").strip(), True)
    hatalar = st.session_state.setdefault("ots::hatalar", {})
    if not gecerli:
        hatalar[anahtar] = True
        return
    hatalar.pop(anahtar, None)
    dv = t["degerler"].setdefault(sporcu, {})
    if v:
        dv[sutun] = v
        if ot_durumu(t, test, sporcu) == "gelmedi":
            t["durum"][sporcu].pop(test)
    else:
        dv.pop(sutun, None)
        if not dv:
            t["degerler"].pop(sporcu, None)
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_not_cb(test, sporcu, anahtar_cip, anahtar_metin):
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    cip = st.session_state.get(anahtar_cip) or []
    n = {"etiketler": [c for c in NOT_CIPLERI if c in cip],
         "metin": str(st.session_state.get(anahtar_metin, "") or "").strip()}
    if n["etiketler"] or n["metin"]:
        t["notlar"].setdefault(sporcu, {})[test] = n
    else:
        (t["notlar"].get(sporcu) or {}).pop(test, None)
    taslak_yaz(t)


def _ot_tamamla(t, test, sporcu):
    t["durum"].setdefault(sporcu, {})[test] = "tamam"
    t["konum"] = ot_siradaki(t, (test, sporcu))
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_sonraki_cb(test, sporcu, bilgiler, testler, tarih):
    """'Kaydet ve sıradaki →': boş/geçersiz alan varsa uyarı; olağandışı değer varsa sorar; yoksa sıradakine geçer."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    onek = f"ot_g::{sporcu}::{oturum_sutunu(test, '')}"
    if any(str(k).startswith(onek) for k in st.session_state.get("ots::hatalar", {})):
        st.session_state["ots::mesaj"] = "Sayı olmayan alanı düzeltin (virgül ya da nokta kullanılabilir)."
        return
    dv = t["degerler"].get(sporcu) or {}
    if not any(dv.get(oturum_sutunu(test, d)) for d in testler[test]):
        st.session_state["ots::mesaj"] = "Değer girin ya da 'Atla (gelmedi)' seçin."
        return
    uy = ot_aykiri_uyarilari(t, bilgiler, testler, tarih, test, sporcu)
    if uy:
        st.session_state["ots::aykiri"] = {"anahtar": [test, sporcu], "uyarilar": uy}
        return
    _ot_tamamla(t, test, sporcu)


def _ot_onayla_cb(test, sporcu):
    t = st.session_state.get("ots::taslak")
    if t:
        _ot_tamamla(t, test, sporcu)


def _ot_atla_cb(test, sporcu):
    """'Atla (gelmedi)': bu sporcunun bu testteki değerleri silinir, gelmedi işaretlenir; kayıt yazılmaz."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    dv = t["degerler"].get(sporcu) or {}
    for c in [c for c in dv if c.startswith(oturum_sutunu(test, ""))]:
        dv.pop(c)
        st.session_state.pop(f"ot_g::{sporcu}::{c}", None)
    if not dv:
        t["degerler"].pop(sporcu, None)
    t["durum"].setdefault(sporcu, {})[test] = "gelmedi"
    t["konum"] = ot_siradaki(t, (test, sporcu))
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_geri_al_cb(test, sporcu):
    """'Geri al': bir önceki sporcuya döner ve onun onayını kaldırır (değerleri durur, düzeltilebilir)."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    kuyruk = ot_kuyrugu(t)
    i = kuyruk.index((test, sporcu)) if (test, sporcu) in kuyruk else len(kuyruk)
    if i == 0:
        return
    pt, ps = kuyruk[i - 1]
    (t["durum"].get(ps) or {}).pop(pt, None)
    t["konum"] = [pt, ps]
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_kaydet_cb(bilgiler, testler, yollar, tarih, onayli):
    """'Oturumu kaydet': olağandışı değer varsa (onaysız) önce sorar; sonra xlsx'e yazar ve taslağı siler."""
    from datetime import datetime as _simdi
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    b_ = t.get("bilgi", {})
    ot_bilgi = {"kimlik": "", "yer": b_.get("yer", ""), "uygulayici": b_.get("uygulayan", "")}
    kayitlar, uyari = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, ot_bilgi)
    if not kayitlar:
        st.session_state["ots::mesaj"] = "Kaydedilecek değer yok."
        return
    if uyari and not onayli:
        st.session_state["ots::aykiri_tablo"] = uyari
        return
    ot_calisma_ad, ot_zaman = b_.get("calisma"), b_.get("zaman")
    ot_calisma = calismalar_oku().get(ot_calisma_ad) if ot_calisma_ad else None
    kimlik = oturum_kimligi(ot_calisma_ad if ot_calisma is not None else None, ot_zaman, _simdi.now())
    for k in kayitlar:
        k["Oturum"] = kimlik
        k[OTURUM_ADI_KOLON] = str(b_.get("ad", "") or "").strip()      # Paket 38d: eski dosyada sütun oluşur
    kayitlari_yaz(kayitlar)
    if ot_calisma is not None:
        calisma_dokun(ot_calisma_ad)                   # öneride "en son dokunulan" (Paket 33)
    dolu_sporcu = len({k["Sporcu"] for k in kayitlar})
    _ot_taslak_temizle()
    st.session_state.pop("ots::taslak_sorma", None)
    st.session_state.pop("ots::aykiri_tablo", None)
    st.session_state["ots::sonuc"] = (f"✅ {len(kayitlar)} test kaydı yazıldı ({dolu_sporcu} sporcu). Oturum: {kimlik}. "
                                      "Norm karşılaştırması ve yorum Sonuçları Görüntüle sayfasında.")
    st.session_state["ot_adim"] = 1


def test_norm_var_mi(ad):
    """Adım 1 işareti: testin normu ("norm"), yalnız örneklem karşılaştırması ("orneklem") ya da None."""
    ad = kanonik_test(ad)
    ds = (test_bilgisi(ad) or {}).get("degiskenler", [])
    if ad in NORMATIF_TEST or any(f"{ad} › {x}" in NORMATIF_YAS or f"{ad} › {x}" in NORMATIF_ESIK_YAS for x in ds):
        return "norm"
    nd = [x for x in ds if x in NORMATIF and (x not in NORMATIF_KAPSAM or NORMATIF_KAPSAM[x](ad))]
    if not nd:
        return None
    return "orneklem" if all(NORMATIF[x].get("tur") == "orneklem" for x in nd) else "norm"


NORM_ISARETI = {"norm": "✓ norm var", "orneklem": "✓ örneklem karşılaştırması", None: "○ norm yok"}


def _bant_ortancasi(bantlar):
    """P50; yoksa P50'yi çevreleyen iki yüzdeliğin doğrusal ara değeri; hesaplanamazsa None."""
    try:
        nok = sorted((int(k[1:]), float(v)) for k, v in (bantlar or {}).items()
                     if str(k).startswith("P") and str(k)[1:].isdigit())
    except (TypeError, ValueError):
        return None
    d = dict(nok)
    if 50 in d:
        return d[50]
    alt = [(q, v) for q, v in nok if q < 50]
    ust = [(q, v) for q, v in nok if q > 50]
    if not alt or not ust:
        return None
    (q0, v0), (q1, v1) = alt[-1], ust[0]
    return v0 + (v1 - v0) * (50 - q0) / (q1 - q0)


def ot_ornek_deger(test, degisken, bilgi):
    """
    Sayı kutusunun örneği (Paket 38c): testin yaş normunun bu sporcunun yaşı ve cinsiyetindeki ortancası
    ("ör. 1,9", "ör. 150"). Normu yoksa ya da yaş/cinsiyet bilinmiyorsa "" — genel bir örnek yazılmaz.
    """
    bilgi = bilgi or {}
    cins = str(bilgi.get("Cinsiyet", "") or "").strip()
    yas = tam_yas(bilgi.get(DOGUM_KOLON), date.today()) or bilgi.get("Yaş")
    if cins not in ("Erkek", "Kadın") or not _girildi(yas):
        return ""
    try:
        n = yas_persentil_bul(kanonik_test(test), degisken, yas, cins, 0.0, bilgi.get(DOGUM_KOLON), date.today())
    except Exception:
        return ""
    orta = _bant_ortancasi((n or {}).get("bantlar"))
    return "" if orta is None else f"ör. {_aralik_sayi(orta, _birim(degisken, test))}"


def _ot_sayi_klavyesi():
    """inputmode="decimal" (telefonda virgüllü rakam klavyesi): Streamlit metin kutusunda bu ayar yok; küçük betik
    yalnız büyük sayı alanlarına ekler. Betik çalışmazsa giriş yine çalışır (virgül/nokta kabul edilir)."""
    try:
        betik = ("<script>(function(){var d=window.parent.document;function k(){d.querySelectorAll("
                      "'.st-key-ot-sayilar input').forEach(function(i){if(i.getAttribute('inputmode')!=='decimal')"
                      "{i.setAttribute('inputmode','decimal');}});}k();new MutationObserver(k).observe(d.body,"
                      "{childList:true,subtree:true});})();</script>")
        with st.container(key="ot-betik"):                       # Paket 38c: çerçeve yer kaplamaz, çizgi bırakmaz
            if hasattr(st, "iframe"):
                st.iframe(betik, height=1)
            else:
                import streamlit.components.v1 as _bilesen
                _bilesen.html(betik, height=0)
    except Exception:
        pass


def _ot_adim_testler(df_ot):
    """Adım 1 — Testler (kategori ağacı, arama ya da kayıtlı Çalışma). Seçilen sıra ots::testler'e."""
    calismalar = calismalar_oku()
    with st.expander("Çalışmalar — kur / düzenle (ör. tez: gruplar, ölçüm zamanları, sıralı testler)"):
        _calisma_duzenleyici(df_ot["_ad"].tolist())
    ot_kaynak = st.radio("Test kaynağı", ["Serbest seçim", "Çalışma"], horizontal=True, key="ot_kaynak",
                         help="Serbest seçim: kategori ağacından ya da aramadan, sporcunun branşından bağımsız. "
                              "Çalışma: kayıtlı test listesi kayıtlı sırasıyla gelir.")
    ot_calisma, ot_calisma_ad, ot_zaman = None, None, None
    if ot_kaynak == "Çalışma":
        if not calismalar:
            st.info("Kayıtlı çalışma yok. Yukarıdaki 'Çalışmalar' bölümünden bir çalışma kurun.")
            ot_sira = []
        else:
            c1, c2 = st.columns(2)
            ot_calisma_ad = c1.selectbox("Çalışma", list(calismalar), key="ot_calisma")
            ot_calisma = calismalar[ot_calisma_ad]
            ot_zaman = c2.selectbox("Ölçüm zamanı", ot_calisma["zamanlar"], key=f"ot_zaman::{ot_calisma_ad}")
            ot_sira = list(ot_calisma["testler"])
            st.caption("Testler kayıtlı sırayla: " + " → ".join(ot_sira))
            for t_ in ot_sira:                                   # iz çubuğu (Paket 33)
                st.caption(f"📍 {test_izi(t_)}")
            st.caption(f"Oturum alanına yazılacak: **{calisma_oturum_adi(ot_calisma_ad, ot_zaman)}**")
    else:
        agac_anahtarlari = [k_ for k_, v_ in st.session_state.items()
                            if str(k_).startswith("ot_testler_") and isinstance(v_, list)]
        secili_simdi = {kanonik_test(t) for k_ in agac_anahtarlari for t in st.session_state[k_]} | set(
            st.session_state.get("ot::ek", []))
        with st.container(border=True):                      # arama paneli (ana sayfadaki "Test ara" deseni)
            st.markdown("**Test ara**")
            ot_ara = st.text_input("Test adı ya da ölçtüğü nitelik", key="ot_ara",
                                   placeholder="ör. T-testi, sürat, çeviklik, Nordic — yazıp Enter'a basın")
            if ot_ara.strip():
                ot_bulunan = [t for t in test_ara(ot_ara) if t["ad"] not in TOPLU_GIRIS_DISI
                              and (test_bilgisi(t["ad"]) or {}).get("degiskenler")]
                st.caption(f"{len(ot_bulunan)} test bulundu" + (" — ilk 12 gösteriliyor" if len(ot_bulunan) > 12 else ""))
                for i, t in enumerate(ot_bulunan[:12]):
                    c1, c2 = st.columns([4, 1], vertical_alignment="center")
                    diger = [r[2] or r[1] for r in test_raflari(t["ad"]) if r != t["yol"]]
                    c1.markdown(f"{_html.escape(test_etiketli(t['ad']))}  \n<span style='font-size:0.875rem'>"
                                f"{_html.escape(' › '.join(p for p in t['yol'] if p))}"
                                + (f" · ayrıca rafta: {_html.escape(', '.join(dict.fromkeys(diger)))}" if diger else "")
                                + "</span>", unsafe_allow_html=True)
                    c2.button("Eklendi" if t["ad"] in secili_simdi else "Ekle", key=f"ot::ara::ekle::{i}",
                              width="stretch", disabled=t["ad"] in secili_simdi, on_click=_ot_ekle, args=(t["ad"],))
        st.caption("Kategori ağacı gezinmek içindir; testler sporcunun branşından bağımsız seçilir. "
                   "Aramadan ve ağaçtan seçilen testler aşağıdaki sıralı listede birleşir.")
        b1, b2, b3 = st.columns(3)
        with b1:
            ot_kategori = st.selectbox("Kategori", list(TEST_KATALOGU.keys()), key="ot_kategori")
        with b2:
            ot_batarya = st.selectbox("Batarya", [k for k in TEST_KATALOGU[ot_kategori] if not k.startswith("_")],
                                      key="ot_batarya")
        ot_havuz = TEST_KATALOGU[ot_kategori][ot_batarya]
        ot_brans = None
        if ot_kategori == "Branşa Özgü Testler":
            with b3:
                ot_brans = st.selectbox("Branş", [k for k in ot_havuz if not k.startswith("_")], key="ot_brans")
            ot_havuz = ot_havuz[ot_brans]
        ot_test_adlari = [t for t, v in ot_havuz.items() if not t.startswith("_") and isinstance(v, dict)
                          and "degiskenler" in v and t not in TOPLU_GIRIS_DISI]
        if any(t in TOPLU_GIRIS_DISI for t in ot_havuz):
            st.caption("SWFT'nin özel giriş ekranı olduğu için toplu girişte yer almaz; Test Uygula sayfasından girin.")
        _ot_t_key = f"ot_testler_{ot_kategori}_{ot_batarya}_{ot_brans}"     # yönlendirme ekranı doldurabilir
        ot_testler_sec = coklu_secim("Bu oturumda uygulanan testler", ot_test_adlari, key=_ot_t_key, tumunu_sec=True,
                                     format_func=test_etiketli,
                                     help="Bu dalın testleri. Gezinirken hiçbir test kendiliğinden eklenmez; "
                                          "bataryanın tümü için kutudaki seçenekleri seçin.")
        # diğer ağaç düğümlerinden önceden seçilenler de korunur (kategori değiştirince kaybolmasın)
        agac_anahtarlari = [k_ for k_, v_ in st.session_state.items()
                            if str(k_).startswith("ot_testler_") and isinstance(v_, list)]
        agac = [t for k_ in agac_anahtarlari for t in st.session_state[k_]]
        secilen = list(dict.fromkeys(kanonik_test(t) for t in ot_testler_sec + agac
                                     + list(st.session_state.get("ot::ek", []))))
        st.markdown("**Sıralı test listesi** (↑ ↓ sırayı değiştirir, ✕ çıkarır)")
        ot_sira = (_sira_listesi("ot", secilen, tuple(agac_anahtarlari) + ("ot::ek",)) if secilen else [])
    for u in sira_uyarilari(ot_sira):                               # bildirir, engellemez
        st.warning(f"Sıra uyarısı: {u}", icon=":material/info:")
    ot_sira_giris = [t for t in ot_sira if t not in TOPLU_GIRIS_DISI and (test_bilgisi(t) or {}).get("degiskenler")]
    if len(ot_sira_giris) < len(ot_sira):
        st.caption("Özel giriş ekranı olan ya da değişkeni tanımsız testler (ör. SWFT) toplu girişte yer almaz; "
                   "Test Uygula sayfasından girin.")
    for t_ in ot_sira_giris:                                        # ○ / ✓ norm: renkle birlikte simge ve kelime
        st.caption(f"{NORM_ISARETI[test_norm_var_mi(t_)]} — {test_etiketli(t_)}")
    st.session_state["ots::testler"] = ot_sira_giris
    st.session_state["ots::calisma"] = {"ad": ot_calisma_ad if ot_calisma is not None else None, "zaman": ot_zaman}
    return {"etiket": "İleri: Sporcular →", "cb": _ot_adim_git, "args": (2,), "disabled": not ot_sira_giris}


def _ot_adim_sporcular(df_ot):
    """Adım 2 — Sporcular (grup ya da çalışma grubu, tümü seçili gelir). ots::sporcular'a."""
    calismalar = calismalar_oku()
    c = st.session_state.get("ots::calisma") or {}
    ot_calisma_ad = c.get("ad") if st.session_state.get("ot_kaynak") == "Çalışma" else None
    ot_calisma = calismalar.get(ot_calisma_ad) if ot_calisma_ad else None
    if ot_calisma is not None and ot_calisma["gruplar"]:
        _ot_cg_key = f"ot_c_gruplar::{ot_calisma_ad}"
        ot_c_gruplar = coklu_secim("Çalışma grubu", ot_calisma["gruplar"],
                                   default=None if _ot_cg_key in st.session_state else ot_calisma["gruplar"],
                                   key=_ot_cg_key)
        aday = [s for s in calisma_sporculari(ot_calisma, ot_c_gruplar) if s in set(df_ot["_ad"])]
        if not aday:
            st.caption("Bu gruplara atanmış sporcu yok; çalışmadaki atamayı kontrol edin. Bütün sporcular listelendi.")
            aday = df_ot["_ad"].tolist()
        _ot_s_key = f"ot_c_sporcular::{ot_calisma_ad}::{'|'.join(ot_c_gruplar)}"
    else:
        grup_listesi = sorted({g for g in df_ot["_grup"] if g})
        if (df_ot["_grup"] == "").any():
            grup_listesi.append("(Grubu girilmemiş)")
        ot_gruplar = coklu_secim("Grup / Sınıf", grup_listesi,
                                 default=None if "ot_gruplar" in st.session_state else grup_listesi[:1],
                                 key="ot_gruplar")
        aday = df_ot[df_ot["_grup"].map(lambda g: (g or "(Grubu girilmemiş)") in ot_gruplar)]["_ad"].tolist()
        _ot_s_key = f"ot_sporcular_{'|'.join(ot_gruplar)}"
    ot_sporcular = coklu_secim("Sporcular (gruptakilerin tümü seçili gelir)", aday, tumunu_sec=True, format_func=ad_bicimi,
                               default=None if _ot_s_key in st.session_state else aday, key=_ot_s_key)
    st.markdown(f"**{len(ot_sporcular)} sporcu seçili**")
    st.session_state["ots::sporcular"] = list(ot_sporcular)
    return {"etiket": "İleri: Oturum bilgisi →", "cb": _ot_adim_git, "args": (3,), "disabled": not ot_sporcular}


def _ot_adim_bilgi():
    """Adım 3 — Oturum bilgisi: tarih, yer, uygulayan (çalışmada ölçüm zamanı Adım 1'de)."""
    o1, o2, o3 = st.columns(3)
    with o1:
        st.date_input("Tarih", format="DD.MM.YYYY", key="ot_tarih",
                      **({} if "ot_tarih" in st.session_state else {"value": date.today()}))
    with o2:
        st.text_input("Yer", placeholder="ör. Okul spor salonu", key="ot_yer")
    with o3:
        st.text_input("Uygulayan", placeholder="ör. Ertuğrul K.", key="ot_uyg")
    st.text_input("Oturum adı (isteğe bağlı)", key="ot_ad", max_chars=60, placeholder="ör. 6-B Ekim taraması",
                  help="Sonuçlarda ve karşılaştırmada oturum bu adla görünür. Boş kalırsa tarih, yer ve uygulayan.")
    c = st.session_state.get("ots::calisma") or {}
    if c.get("ad") and c.get("zaman"):
        st.caption(f"Oturum alanına yazılacak: **{calisma_oturum_adi(c['ad'], c['zaman'])}**")
    return {"etiket": "İleri: Değerler →", "cb": _ot_degerlere_gec, "args": ()}


def _ot_siradaki_kipi(t, testler, bilgiler, tarih, yollar):
    """Sıradaki kipi: ekranda TEK sporcu, TEK test; büyük alanlar; otomatik değer canlı; karşılaştırma yok."""
    konum = t.get("konum")
    if not konum or konum[0] not in testler or konum[1] not in t["sporcular"] or ot_durumu(t, *konum):
        konum = ot_siradaki(t, konum)
        t["konum"] = konum
    if konum is None:
        gelmedi = sum(1 for s in t["sporcular"] for x in t["testler"] if ot_durumu(t, x, s) == "gelmedi")
        st.success(f"Tüm ölçümler girildi: {taslak_deger_sayisi(t)} değer"
                   + (f", {gelmedi} ölçümde sporcu gelmedi." if gelmedi else "."))
        st.caption("İsterseniz Tablo kipinde hepsini birlikte görüp düzeltebilirsiniz.")
        kayitlar, _ = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, {})
        return {"etiket": f"Oturumu kaydet ({len(kayitlar)} kayıt)", "cb": _ot_kaydet_cb,
                "args": (bilgiler, testler, yollar, tarih, True), "disabled": not kayitlar}
    test, sporcu = konum
    yap, top = ot_ilerleme(t, test)
    st.markdown(f"**Test {t['testler'].index(test) + 1} / {len(t['testler'])} · {_html.escape(test_etiketli(test))}**")
    st.markdown(ot_ilerleme_html(yap, top, f"{yap} / {top} sporcu"), unsafe_allow_html=True)
    sol, sag = st.columns([1, 2])
    with sol:
        st.markdown(ot_sira_cipleri_html(t, test, sporcu), unsafe_allow_html=True)
    with sag:
        st.markdown(f"### {_html.escape(ad_bicimi(sporcu))}")
        dv = t["degerler"].get(sporcu) or {}
        hatalar = st.session_state.get("ots::hatalar", {})

        def alan(d):
            c = oturum_sutunu(test, d)
            anahtar = f"ot_g::{sporcu}::{c}"
            sayisal = not METIN_DEGISKEN_KALIBI.search(d)
            v = str(dv.get(c, "") or "")
            st.text_input(d, key=anahtar, placeholder=ot_ornek_deger(test, d, bilgiler.get(sporcu)) if sayisal else "",
                          help=ACIKLAMALAR.get(d) or None, on_change=_ot_deger_cb,
                          args=(test, sporcu, c, anahtar, sayisal),
                          **({} if anahtar in st.session_state else {"value": v.replace(".", ",") if sayisal else v}))
            if hatalar.get(anahtar):
                st.error("Sayı girin (virgül ya da nokta kullanılabilir). Bu alan taslağa yazılmadı.")

        with st.container(key="ot-sayilar"):
            for d in [d for d in testler[test] if not METIN_DEGISKEN_KALIBI.search(d)]:
                alan(d)
        for d in [d for d in testler[test] if METIN_DEGISKEN_KALIBI.search(d)]:
            alan(d)
        _ot_sayi_klavyesi()
        for k_h, v_h in ot_hesaplanan(test, {d: dv.get(oturum_sutunu(test, d), "") for d in testler[test]},
                                      bilgiler.get(sporcu, {})).items():
            st.markdown(f'<div class="ot-otomatik" role="status"><span class="sp-etiket">{_html.escape(k_h)} · '
                        f'otomatik</span><div class="ot-otomatik-deger">{_html.escape(_konum_sayi(v_h))}</div></div>',
                        unsafe_allow_html=True)
        n = (t["notlar"].get(sporcu) or {}).get(test) or {}
        k_cip, k_not = f"ot_n::{sporcu}::{test}", f"ot_nm::{sporcu}::{test}"
        not_kutusu = st.container(key="ot-not")
        if hasattr(st, "pills"):
            not_kutusu.pills("Not (isteğe bağlı)", list(NOT_CIPLERI), selection_mode="multi", key=k_cip,
                     on_change=_ot_not_cb, args=(test, sporcu, k_cip, k_not),
                     **({} if k_cip in st.session_state else {"default": list(n.get("etiketler", []))}))
        else:
            with not_kutusu:
                coklu_secim("Not (isteğe bağlı)", list(NOT_CIPLERI), key=k_cip, on_change=_ot_not_cb,
                            args=(test, sporcu, k_cip, k_not),
                            **({} if k_cip in st.session_state else {"default": list(n.get("etiketler", []))}))
        st.text_input("Kısa not", key=k_not, placeholder="ör. ikinci denemede kaydı", on_change=_ot_not_cb,
                      args=(test, sporcu, k_cip, k_not),
                      **({} if k_not in st.session_state else {"value": str(n.get("metin", "") or "")}))
        mesaj = st.session_state.pop("ots::mesaj", None)
        if mesaj:
            st.error(mesaj)
        ayk = st.session_state.get("ots::aykiri")
        if ayk and list(ayk["anahtar"]) == [test, sporcu]:
            st.warning("**! Kontrol et** — " + OT_AYKIRI_SORU + "\n\n" + "\n".join(f"- {u}" for u in ayk["uyarilar"]))
            st.button("Düzelt", key="ot_duzelt", on_click=lambda: st.session_state.pop("ots::aykiri", None))
            return {"etiket": "Evet, kaydet", "cb": _ot_onayla_cb, "args": (test, sporcu)}
        g1, g2 = st.columns(2)
        g1.button("← Geri al", key="ot_geri_al", on_click=_ot_geri_al_cb, args=(test, sporcu), width="stretch",
                  disabled=ot_kuyrugu(t).index((test, sporcu)) == 0, help="Bir önceki sporcuya dön ve düzelt")
        g2.button("Atla (gelmedi)", key="ot_atla", on_click=_ot_atla_cb, args=(test, sporcu), width="stretch")
    return {"etiket": "Kaydet ve sıradaki →", "cb": _ot_sonraki_cb, "args": (test, sporcu, bilgiler, testler, tarih)}


def _ot_tablo_kipi(t, testler, bilgiler, tarih, yollar):
    """Tablo kipi: tüm sporcular satır, denemeler sütun (Enter alt hücre, Tab sağ hücre); test başına not sütunu."""
    surum = st.session_state.get("ot_tablo_surum", 0)
    taban = st.session_state.get("ots::tablo_taban")
    if not taban or taban[0] != surum:
        taban = (surum, taslak_duzenleme_tablosu(t, testler))
        st.session_state["ots::tablo_taban"] = taban
    yapilandirma = {"Sporcu": st.column_config.TextColumn("Sporcu", disabled=True)}
    for test, ds in testler.items():
        kisa = test if len(test) <= 26 else test.split(" (")[0].split(" — ")[0][:26]
        for d in ds:
            yardim = f"{test} — {ACIKLAMALAR.get(d, d)}"
            yapilandirma[oturum_sutunu(test, d)] = st.column_config.TextColumn(
                f"{kisa} · {d}", help=yardim + ("" if METIN_DEGISKEN_KALIBI.search(d) else " (virgül ya da nokta: 4,52)"))
        yapilandirma[oturum_sutunu(test, NOT_DEGISKENI)] = st.column_config.TextColumn(
            f"{kisa} · Not", help="Kısa not. Hazır notlar: " + "; ".join(NOT_CIPLERI) + " (noktalı virgülle ayırın).")
    tablo = st.data_editor(taban[1], column_config=yapilandirma, hide_index=True, num_rows="fixed", width="stretch",
                           key=f"ot_tablo::{surum}")
    degisti, gecersiz = taslak_tablodan(t, tablo, testler)
    if degisti:
        taslak_yaz(t)
    if gecersiz:
        st.error("**! Sayı değil** — bu hücreler taslağa yazılmadı:\n\n"
                 + "\n".join(f"- {s_}: {c_.split(' › ', 1)[1]} = “{v_}”" for s_, c_, v_ in gecersiz))
    hes = []
    for s in t["sporcular"]:
        dv = t["degerler"].get(s) or {}
        for test, ds in testler.items():
            h = ot_hesaplanan(test, {d: dv.get(oturum_sutunu(test, d), "") for d in ds}, bilgiler.get(s, {}))
            if h:
                hes.append({"Sporcu": s, "Test": test, **{f"{k} · otomatik": _konum_sayi(v) for k, v in h.items()}})
    if hes:
        st.markdown("**Otomatik hesaplanan** (girilen değerlerden)")
        st.dataframe(pd.DataFrame(hes), hide_index=True, width="stretch")
    kayitlar, _ = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, {})
    st.caption(f"Kaydedilecek: {len(kayitlar)} test kaydı, {len({k['Sporcu'] for k in kayitlar})} sporcu. "
               "Boş hücreler kaydedilmez.")
    mesaj = st.session_state.pop("ots::mesaj", None)
    if mesaj:
        st.error(mesaj)
    ayk = st.session_state.get("ots::aykiri_tablo")
    if ayk:
        st.warning("**! Kontrol et** — " + OT_AYKIRI_SORU + "\n\n" + "\n".join(f"- {u}" for u in ayk))
        st.button("Düzelt", key="ot_duzelt_t", on_click=lambda: st.session_state.pop("ots::aykiri_tablo", None))
        return {"etiket": "Evet, kaydet", "cb": _ot_kaydet_cb, "args": (bilgiler, testler, yollar, tarih, True)}
    return {"etiket": "Oturumu kaydet", "cb": _ot_kaydet_cb, "args": (bilgiler, testler, yollar, tarih, False),
            "disabled": not kayitlar}


def _ot_ozet_satirlari(adim, t):
    """Tamamlanan adımlar: tek satır özet + 'Düzenle' (her adımda geri dönüş)."""
    testler = (t or {}).get("testler") if adim == 4 else st.session_state.get("ots::testler", [])
    sporcular = (t or {}).get("sporcular") if adim == 4 else st.session_state.get("ots::sporcular", [])
    kisalt = lambda xs: ", ".join(ad_bicimi(x) for x in xs[:3]) + (f" ve {len(xs) - 3} daha" if len(xs) > 3 else "")
    tarih = st.session_state.get("ot_tarih") or date.today()
    ozet = {1: f"{len(testler or [])} test: {kisalt(list(testler or []))}",
            2: f"{len(sporcular or [])} sporcu: {kisalt(list(sporcular or []))}",
            3: " · ".join(x for x in (str(st.session_state.get("ot_ad", "") or "").strip(),
                                       tarih.strftime("%d.%m.%Y"), str(st.session_state.get("ot_yer", "") or "").strip(),
                                       str(st.session_state.get("ot_uyg", "") or "").strip()) if x)}
    for i in range(1, adim):
        c1, c2 = st.columns([5, 1], vertical_alignment="center")
        c1.markdown(f"✓ **{i}. {OT_ADIMLAR[i - 1]}** — {_html.escape(ozet[i])}")
        c2.button("Düzenle", key=f"ot_duzenle::{i}", on_click=_ot_adim_git, args=(i,), width="stretch")


def _ot_alt_cubuk(adim, ana, t):
    """Sabit alt çubuk: '← Geri' · 'N sporcu · M test · K değer' · tek ana düğme (sağda, ≥ 48 px)."""
    n_s = len((t or {}).get("sporcular") or []) if adim == 4 else len(st.session_state.get("ots::sporcular", []) or [])
    n_t = len((t or {}).get("testler") or []) if adim == 4 else len(st.session_state.get("ots::testler", []) or [])
    with st.container(key="ot-altcubuk"):
        c1, c2, c3 = st.columns([1, 2, 1.6], vertical_alignment="center")
        if adim > 1:
            c1.button("← Geri", key="ot_geri", on_click=_ot_adim_git, args=(adim - 1,), width="stretch")
        c2.markdown(f'<p class="ot-ozet">{n_s} sporcu · {n_t} test · {taslak_deger_sayisi(t) if adim == 4 else 0} '
                    f'değer</p>', unsafe_allow_html=True)
        if ana:
            with c3.container(key="ot-ana"):
                st.button(ana["etiket"], key="ot_ana", type="primary", width="stretch", on_click=ana["cb"],
                          args=tuple(ana.get("args", ())), disabled=bool(ana.get("disabled", False)))


def test_oturumu_sayfasi():
    """Test Oturumu (Paket 38b): 4 adım; değerler Sıradaki ya da Tablo kipinde; taslak her değişiklikte diske."""
    _ot_durum_koru()
    st.header("Test Oturumu — Toplu Giriş")
    st.caption("Testleri seç → sporcuları seç → tarih, yer ve uygulayanı gir → değerleri gir → tek düğmeyle kaydet. "
               "Ölçüm sırasında karşılaştırma gösterilmez; norm özeti kayıttan sonra Sonuçlar sayfasındadır.")
    bolum_terimleri(["Olağandışı değer (P1–P99)", "Norm", "Doğum çeyreği"])
    if not os.path.exists(SPORCU_DOSYA):
        st.info("Önce Sporcu Girişi sayfasından sporcu ekleyin.")
        return
    df_ot = pd.read_excel(SPORCU_DOSYA)
    df_ot["_ad"] = df_ot["Ad"].astype(str) + " " + df_ot["Soyad"].astype(str)
    if GRUP_KOLON not in df_ot.columns:
        df_ot[GRUP_KOLON] = ""
    df_ot["_grup"] = df_ot[GRUP_KOLON].map(lambda g: "" if not _girildi(g) else str(g).strip())
    bilgiler = {r["_ad"]: r.to_dict() for _, r in df_ot.iterrows()}
    sonuc = st.session_state.pop("ots::sonuc", None)
    if sonuc:
        st.success(sonuc)
        st.button("Sonuçları gör →", key="ot_sonuca", on_click=_sayfaya_git, args=("Sonuçları Görüntüle",))

    t = st.session_state.get("ots::taslak")
    if t is None and not st.session_state.get("ots::taslak_sorma"):
        disk = taslak_oku()
        if disk:
            if st.session_state.pop("ots::otomatik", False):        # sayfa yenilendi: doğrudan kaldığı yerden
                _ot_taslak_yukle(disk, df_ot)
                t = disk
            else:
                with st.container(border=True):
                    tarih_ = str(disk.get("bilgi", {}).get("tarih", ""))
                    st.markdown(f"**Yarım kalan oturum var.** {'.'.join(reversed(tarih_.split('-')))} · "
                                f"{len(disk['sporcular'])} sporcu · {len(disk['testler'])} test · "
                                f"{taslak_deger_sayisi(disk)} değer girildi"
                                + (f" (son kayıt {disk['zaman']})" if disk.get("zaman") else "") + ".")
                    d1, d2 = st.columns(2)
                    with d1.container(key="ot-taslak-devam"):
                        st.button("Devam et", type="primary", key="ot_taslak_devam", width="stretch",
                                  on_click=_ot_taslak_yukle, args=(disk, df_ot))
                    d2.button("Taslağı sil, yeni oturum", key="ot_taslak_sil", width="stretch",
                              on_click=_ot_taslak_temizle)
                return
    adim = int(st.session_state.get("ot_adim", 1))
    if adim == 4 and not t:
        adim = 3
    st.markdown(ot_adim_seridi_html(adim), unsafe_allow_html=True)
    _ot_ozet_satirlari(adim, t)
    st.markdown(f"##### {adim}. {OT_ADIMLAR[adim - 1]}")
    if adim == 1:
        ana = _ot_adim_testler(df_ot)
    elif adim == 2:
        ana = _ot_adim_sporcular(df_ot)
    elif adim == 3:
        ana = _ot_adim_bilgi()
    else:
        _qp_ayarla("taslak", "1")                                   # yenilenirse taslağa dön
        testler = {x: list(test_bilgisi(x)["degiskenler"]) for x in t["testler"]
                   if (test_bilgisi(x) or {}).get("degiskenler")}
        yollar = {x: test_yolu(x) for x in testler}
        try:
            tarih = date.fromisoformat(str(t.get("bilgi", {}).get("tarih")))
        except ValueError:
            tarih = date.today()
        st.radio("Giriş kipi", OT_KIPLER, horizontal=True, key="ot_kip", on_change=_ot_tablo_yenile,
                 help="Sıradaki: ekranda tek sporcu ve tek test (telefon/tablet). Tablo: tüm sporcular satır, "
                      "denemeler sütun (bilgisayar). Varsayılan cihaza göre gelir; buradan değiştirilebilir.",
                 **({} if "ot_kip" in st.session_state
                    else {"index": OT_KIPLER.index(varsayilan_kip(_istemci_ajani()))}))
        ana = (_ot_siradaki_kipi if st.session_state.get("ot_kip") == "Sıradaki" else _ot_tablo_kipi)(
            t, testler, bilgiler, tarih, yollar)
        st.caption(f"{OT_TASLAK_NOTU}" + (f" ({t['zaman']})" if t.get("zaman") else "")
                   + ". Kaydet'e basılana kadar sonuç dosyasına yazılmaz.")
    _ot_alt_cubuk(adim, ana, t)
