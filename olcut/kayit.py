"""
Test kaydı ve oturum: kayıt sözlüğü (test_kaydi_olustur), dosyaya yazma, makullük kontrolü, sporcu formu, oturum
sütunları ve oturumlar arası fark, çalışma (araştırma deseni) kalıcılığı ve oturum kimliği.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import os
import pandas as pd
import streamlit as st
from datetime import date
from olcut.katalog_islemleri import CALISMA_ANAHTAR, kanonik_test, katalog_testleri
from olcut.norm import (
    NORMATIF_YAS, OTURUM_ADI_KOLON, TEST_DOSYA, _STANDART_NORMAL, degisken_yonu, sifir_gecerli,
    turetilmis_degerler, yas_persentil_bul)
from olcut.ortak import DOGUM_KOLON, _dt_simdi, _girildi, ayar_oku, ayar_yaz, guvenli_float, tam_yas


GRUP_KOLON = "Grup/Sınıf"


OTURUM_KOLONLARI = ["Oturum", "Yer", "Uygulayıcı"]


TOPLU_GIRIS_DISI = {"Special Wrestling Fitness Test (SWFT)"}   # özel giriş ekranı olan test


def deger_metni(v):
    """Toplu girişteki sayıyı tekli girişin yazdığı biçime çevirir (\"17\", \"18.5\"); boşsa \"\"."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(v, (int, float)):
        f = float(v)
        return str(int(f)) if f.is_integer() else repr(round(f, 4))
    return str(v).strip()


def test_kaydi_olustur(sporcu, sporcu_satir, kategori, batarya, brans, test_adi, tarih, degerler,
                       hesaplanan, notlar="", oturum=None):
    """
    test_sonuclari.xlsx'e yazılacak TEK kayıt. Tekli giriş ve Test Oturumu bu fonksiyonu kullanır.
    oturum: {"kimlik", "yer", "uygulayici"} ya da None (tekli giriş — alanlar boş yazılır).
    """
    oturum = oturum or {}
    kayit = {
        "Sporcu": sporcu,
        "Kategori": kategori,
        "Batarya": batarya,
        "Branş": brans if brans else "-",
        "Test": kanonik_test(test_adi),          # takma ad asıl adla yazılır (Paket 27)
        "Tarih": tarih.strftime("%d.%m.%Y"),
        "Notlar": notlar or "",
        "Oturum": oturum.get("kimlik", ""),
        "Yer": oturum.get("yer", ""),
        "Uygulayıcı": oturum.get("uygulayici", ""),
    }
    kayit.update(degerler)
    profil_yas = sporcu_satir.get("Yaş") if hasattr(sporcu_satir, "get") else None
    # Test günündeki yaş: Z/persentil sonradan doğru yaş normuyla hesaplansın
    kayit["Test Yaşı"] = tam_yas(sporcu_satir.get(DOGUM_KOLON), tarih) or profil_yas
    # Otomatik hesaplanan sayısal değerler de kaydedilir (ör. KTK3+ toplamları)
    for k_h, v_h in hesaplanan.items():
        if k_h not in kayit and isinstance(v_h, (int, float)):
            kayit[k_h] = v_h
    return kayit


def kayitlari_yaz(kayitlar):
    """Kayıtları test dosyasına ekler."""
    if not kayitlar:
        return
    yeni = pd.DataFrame(kayitlar)
    if os.path.exists(TEST_DOSYA):
        df_eski = pd.read_excel(TEST_DOSYA)
        yeni = pd.concat([df_eski, yeni], ignore_index=True)
    yeni.to_excel(TEST_DOSYA, index=False)


# ── Makullük sınırları ──
def makul_aralik_bantlardan(bantlar):
    """
    Persentil bantlarından (P5…P95, P20…P80 ya da 19 persentil) yaklaşık P1 ve P99.
    Normlar P1/P99 vermez; alt ve üst kuyruk ayrı ayrı normal yaklaşımla uzatılır:
      medyan = P50 (yoksa iki komşu bandın doğrusal ara değeri)
      SS_alt = (medyan − en alt bant) / |z(en alt)|,  SS_üst = (en üst bant − medyan) / z(en üst)
      P1 = medyan − 2.326·SS_alt,  P99 = medyan + 2.326·SS_üst
    Çarpık dağılımlarda iki kuyruk ayrı uzadığı için simetrik bir aralıktan daha gerçekçidir.
    Dönen: (p1, p99) ya da None.
    """
    try:
        noktalar = sorted((int(k[1:]), float(v)) for k, v in bantlar.items()
                          if str(k).startswith("P") and str(k)[1:].isdigit())
    except (TypeError, ValueError):
        return None
    if len(noktalar) < 2:
        return None
    ps = [p for p, _ in noktalar]
    vs = [v for _, v in noktalar]
    if 50 in ps:
        medyan = vs[ps.index(50)]
    else:
        alt_i = max(i for i, p in enumerate(ps) if p < 50) if any(p < 50 for p in ps) else 0
        ust_i = min(i for i, p in enumerate(ps) if p > 50) if any(p > 50 for p in ps) else len(ps) - 1
        p_a, p_u = ps[alt_i], ps[ust_i]
        medyan = vs[alt_i] + (vs[ust_i] - vs[alt_i]) * ((50 - p_a) / (p_u - p_a) if p_u != p_a else 0)
    z_alt = _STANDART_NORMAL.inv_cdf(ps[0] / 100)
    z_ust = _STANDART_NORMAL.inv_cdf(ps[-1] / 100)
    z99 = _STANDART_NORMAL.inv_cdf(0.99)
    ss_alt = max(medyan - vs[0], 0) / abs(z_alt) if z_alt < 0 else 0
    ss_ust = max(vs[-1] - medyan, 0) / z_ust if z_ust > 0 else 0
    p1 = min(medyan - z99 * ss_alt, vs[0])
    p99 = max(medyan + z99 * ss_ust, vs[-1])
    return p1, p99


def makul_aralik(test_adi, degisken, yas, cinsiyet, dogum=None, tarih=None):
    """Bu sporcunun norm hücresinde yaklaşık P1-P99. Normu yoksa None."""
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_YAS or cinsiyet not in ("Erkek", "Kadın"):
        return None
    norm = NORMATIF_YAS[anahtar]
    ornek = next(iter(norm["yaslar"].values())).get(cinsiyet) or {}
    ys = yas_persentil_bul(test_adi, degisken, yas, cinsiyet, ornek.get("P50", 0) or 0, dogum, tarih)
    if not ys or ys.get("yas_notu"):
        return None   # yaş normun aralığı dışında: başka yaşın normuyla makullük denetlenmez (Paket 11)
    sinir = makul_aralik_bantlardan(ys["bantlar"])
    if not sinir:
        return None
    kim = "kız" if cinsiyet == "Kadın" and ys["kullanilan_yas"] < 18 else cinsiyet.lower()
    hucre = f"{ys['kullanilan_yas']} yaş {kim}" + (f" ({ys['ceyrek']}. doğum çeyreği)" if ys.get("ceyrek") else "")
    return {"alt": sinir[0], "ust": sinir[1], "hucre": hucre, "birim": ys.get("birim") or norm.get("birim", "")}


def _sayi_kisa(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if abs(x) < 1000 else f"{x:.0f}"


def makullukte_uyarilar(test_adi, degerler, yas, cinsiyet, dogum=None, tarih=None, etiket=""):
    """Norm aralığı (≈P1-P99) dışındaki değerler için uyarı metinleri. Normu olmayanlar atlanır."""
    uyarilar = []
    for degisken, v in degerler.items():
        if not _girildi(v):
            continue
        try:
            x = float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            continue
        if x == 0 and not sifir_gecerli(test_adi, degisken):
            continue
        ar = makul_aralik(test_adi, degisken, yas, cinsiyet, dogum, tarih)
        if not ar or ar["alt"] <= x <= ar["ust"]:
            continue
        on = f"{etiket}: " if etiket else ""
        uyarilar.append(f"{on}{test_adi} — {degisken} = {_sayi_kisa(x)} {ar['birim']}: {ar['hucre']} için olağandışı "
                        f"(beklenen ≈ {_sayi_kisa(ar['alt'])}–{_sayi_kisa(ar['ust'])} {ar['birim']}, P1–P99). "
                        f"Emin misiniz?")
    return uyarilar


# Profildeki boy ve kilo için norm: TSYT (7-11 yaş). Başka yaşta norm olmadığı için kontrol yok.
PROFIL_MAKULLUK = {"Boy (cm)": ("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)"),
                   "Kilo (kg)": ("Boy ve Vücut Ağırlığı (TSYT)", "Vücut Ağırlığı (kg)")}


# Paket 38a: yeni sporcu formu boş açılır (varsayılan sayı yok); bu alt sınırların altı kaydedilmez.
SPORCU_FORM_ALT_SINIR = {"Yaş": 4, "Boy (cm)": 80, "Kilo (kg)": 10}


SPORCU_FORM_ALANLARI = ("sg_ad", "sg_soyad", "sg_yas", "sg_boy", "sg_kilo", "sg_grup", "sg_dogum_var", "sg_dogum")


def sporcu_form_hatalari(yas, boy, kilo):
    """Alan → Türkçe hata. Boş alan "giriniz", alt sınırın altı açıklamalı. Boş sözlük: kayıt yapılabilir."""
    h = {}
    for alan, deger, bos, kucuk in (("Yaş", yas, "Yaşı giriniz.", "Yaş 4'ten küçük olamaz."),
                                    ("Boy (cm)", boy, "Boyu giriniz (cm).", "Boy 80 cm'den kısa olamaz."),
                                    ("Kilo (kg)", kilo, "Kiloyu giriniz (kg).", "Kilo 10 kg'dan az olamaz.")):
        if deger is None:
            h[alan] = bos
        elif float(deger) < SPORCU_FORM_ALT_SINIR[alan]:
            h[alan] = kucuk
    return h


def _sporcu_formunu_temizle():
    """'Başka sporcu ekle': formun alanlarını boşaltır."""
    for k in SPORCU_FORM_ALANLARI:
        st.session_state.pop(k, None)


def profil_uyarilari(boy, kilo, yas, cinsiyet, dogum=None, ad=""):
    uyarilar = []
    for alan, deger in (("Boy (cm)", boy), ("Kilo (kg)", kilo)):
        test_adi, degisken = PROFIL_MAKULLUK[alan]
        for u in makullukte_uyarilar(test_adi, {degisken: deger}, yas, cinsiyet, dogum, date.today()):
            uyarilar.append(u.replace(f"{test_adi} — {degisken}", alan))
    yas_dogumdan = tam_yas(dogum, date.today()) if dogum else None
    try:
        if yas_dogumdan is not None and yas not in (None, "") and int(float(yas)) != yas_dogumdan:
            uyarilar.append(f"Yaş {int(float(yas))} girildi ama doğum tarihine göre {yas_dogumdan} — biri yanlış olabilir.")
    except (TypeError, ValueError):
        pass
    try:
        if boy and kilo and float(boy) > 0 and abs(float(boy) - float(kilo)) < 0.01:
            uyarilar.append(f"Boy ve kilo aynı sayı ({_sayi_kisa(float(boy))}) — biri yanlış alana yazılmış olabilir.")
    except (TypeError, ValueError):
        pass
    return [f"{ad}: {u}" if ad else u for u in uyarilar]


# ── Test oturumu ──
def oturum_sutunu(test_adi, degisken):
    return f"{test_adi} › {degisken}"


def oturum_kayitlari(tablo, sporcu_bilgileri, testler, kategori, batarya, brans, tarih, oturum, yollar=None):
    """
    Toplu giriş tablosunu kayıtlara çevirir. Satır = sporcu ("Sporcu" sütunu), sütun = "Test › Değişken".
    Boş hücreler kaydedilmez; bir sporcunun bir testte en az bir dolu hücresi varsa o test kaydedilir
    (kısmi kayıt normaldir). Streamlit çağrısı yoktur.
    testler: {test_adi: [değişkenler]}; sporcu_bilgileri: {sporcu: profil satırı (dict)}.
    yollar: {test_adi: (kategori, batarya, branş)} — testler farklı kategorilerden seçildiyse (Paket 27).
    Dönen: (kayitlar, uyarilar) — uyarilar makullük ve hesaplama uyarılarıdır.
    """
    kayitlar, uyarilar = [], []
    for _, satir in tablo.iterrows():
        sporcu = satir["Sporcu"]
        bilgi = sporcu_bilgileri.get(sporcu, {})
        kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
        cins = str(bilgi.get("Cinsiyet", "")).strip()
        yas = tam_yas(bilgi.get(DOGUM_KOLON), tarih) or bilgi.get("Yaş")
        for test_adi, degiskenler in testler.items():
            degerler = {d: deger_metni(satir.get(oturum_sutunu(test_adi, d))) for d in degiskenler}
            if not any(degerler.values()):
                continue
            hesaplanan, h_uyari = turetilmis_degerler(test_adi, degerler, bilgi, kilo)
            uyarilar += [f"{sporcu}: {test_adi} — {u}" for u in h_uyari]
            tum = {**degerler, **{k: v for k, v in hesaplanan.items() if isinstance(v, (int, float))}}
            uyarilar += makullukte_uyarilar(test_adi, tum, yas, cins, bilgi.get(DOGUM_KOLON), tarih, sporcu)
            kat_, bat_, br_ = (yollar or {}).get(test_adi, (kategori, batarya, brans))
            kayitlar.append(test_kaydi_olustur(sporcu, bilgi, kat_, bat_, br_, test_adi, tarih,
                                               degerler, hesaplanan, "", oturum))
    return kayitlar, uyarilar


def oturum_secenekleri(df):
    """{oturum kimliği: etiket} — kayıt sırasının tersi (en yeni önce). Sonuçlar süzgeci ve karşılaştırma ortak."""
    if df is None or "Oturum" not in df.columns:
        return {}
    o = df["Oturum"].fillna("").astype(str).str.strip()
    d = df[(o != "") & (o != "nan")]
    et = {kim: f"{oturum_etiketi(grp.iloc[0])} · {grp['Sporcu'].nunique()} sporcu, {len(grp)} kayıt"
          for kim, grp in d.groupby("Oturum", sort=False)}
    return dict(reversed(list(et.items())))


# Paket 38d: Sporcu Karşılaştırma kapsamı. Bireysel = her sporcunun son ölçümü (eski davranış); Tek oturum = yalnız
# o oturumun ölçümleri; Oturumlar arası = iki oturumda da ölçülen sporcunun iki değeri ve farkı (yön tanımından
# "daha iyi / daha kötü"; yön yoksa yalnız fark). Hesap yok: kayıttaki değerler, oturum içinde son ölçüm.
KARSILASTIRMA_KAPSAMLARI = ("Bireysel", "Tek oturum", "Oturumlar arası")


def oturum_degerleri(df, test, degisken, oturum=None):
    """{sporcu: değer} — testin değişkeni; oturum verilirse yalnız o oturum; sporcu başına son ölçüm."""
    d = df[df["Test"].map(kanonik_test) == kanonik_test(test)].copy()
    if oturum is not None:
        d = d[d["Oturum"].astype(str) == str(oturum)] if "Oturum" in d.columns else d.iloc[0:0]
    if degisken not in d.columns or d.empty:
        return {}
    d["_v"] = pd.to_numeric(d[degisken], errors="coerce")
    if "Tarih_dt" not in d.columns:
        d["Tarih_dt"] = pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce")
    d = d.dropna(subset=["_v"]).sort_values("Tarih_dt", na_position="first")
    return {s: float(v) for s, v in d.groupby("Sporcu")["_v"].last().items()}


def oturumlar_arasi_fark(df, test, degisken, once, sonra):
    """İki oturumda da ölçülen sporcular: [{Sporcu, Önceki, Sonraki, Fark, Yorum}] — yorum sözcükle."""
    a = oturum_degerleri(df, test, degisken, once)
    b_ = oturum_degerleri(df, test, degisken, sonra)
    yon = degisken_yonu(test, degisken)
    satir = []
    for s in sorted(set(a) & set(b_)):
        fark = round(b_[s] - a[s], 2)
        if fark == 0:
            yorum = "değişmedi"
        elif yon is None:
            yorum = "arttı" if fark > 0 else "azaldı"
        else:
            yorum = "daha iyi" if ((fark < 0) if yon else (fark > 0)) else "daha kötü"
        satir.append({"Sporcu": s, "Önceki": a[s], "Sonraki": b_[s], "Fark": fark, "Yorum": yorum})
    return satir


def oturum_etiketi(satir):
    """Sonuç filtresinde gösterilecek oturum adı. Paket 38d: kullanıcı ad verdiyse "Ad (tarih)"."""
    ad = str(satir.get(OTURUM_ADI_KOLON, "") or "").strip()
    if ad and ad != "nan":
        return f"{ad} ({satir.get('Tarih', '')})"
    parcalar = [str(satir.get(k, "")) for k in ("Tarih", "Yer", "Batarya")]
    uyg = str(satir.get("Uygulayıcı", "") or "")
    return " — ".join(p for p in parcalar if p and p != "nan") + (f" ({uyg})" if uyg and uyg != "nan" else "")


def calisma_bos(ad=""):
    return {"ad": ad, "testler": [], "gruplar": [], "zamanlar": [], "atamalar": {}, "dokunuldu": ""}


def calismalar_oku():
    """Kayıtlı çalışmalar {ad: çalışma}. Bozuk kayıt atlanır; dosya yoksa boş."""
    ham = ayar_oku().get(CALISMA_ANAHTAR, {})
    out = {}
    if isinstance(ham, dict):
        for ad, c in ham.items():
            if isinstance(c, dict):
                d = calisma_bos(ad)
                for k in ("testler", "gruplar", "zamanlar"):
                    d[k] = [str(x) for x in c.get(k, []) if str(x).strip()]
                d["testler"] = list(dict.fromkeys(kanonik_test(x) for x in d["testler"]))   # eski ad → yeni (Paket 30)
                d["atamalar"] = {str(s): str(g) for s, g in (c.get("atamalar") or {}).items()}
                d["dokunuldu"] = str(c.get("dokunuldu") or "")          # Paket 33: ISO zaman damgası
                out[ad] = d
    return out


def calisma_dogrula(c, katalog=None):
    """Kaydetmeyi ENGELLEYEN sorunlar (ad, test, zaman yok; bilinmeyen test; tanımsız gruba atama)."""
    sorun = []
    if not str(c.get("ad", "")).strip():
        sorun.append("Çalışmanın adı yok.")
    if not c.get("testler"):
        sorun.append("En az bir test seçin.")
    adlar = {t["ad"] for t in katalog_testleri(katalog)}
    sorun += [f"Katalogda olmayan test: {t}" for t in c.get("testler", []) if t not in adlar]
    if len(set(c.get("testler", []))) != len(c.get("testler", [])):
        sorun.append("Aynı test iki kez seçilmiş.")
    if not c.get("zamanlar"):
        sorun.append("En az bir ölçüm zamanı girin (ör. Ön test).")
    gruplar = set(c.get("gruplar", []))
    sorun += [f"{s}: '{g}' grubu tanımlı değil." for s, g in c.get("atamalar", {}).items() if g and g not in gruplar]
    return sorun


def calisma_kaydet(c, eski_ad=None):
    """Çalışmayı ayarlar.json'a yazar (ad değiştiyse eskisi silinir). Sorun varsa yazmaz, sorunları döner."""
    c = {**calisma_bos(), **c}
    c["testler"] = [kanonik_test(t) for t in c["testler"]]
    sorun = calisma_dogrula(c)
    if sorun:
        return sorun
    hepsi = {k: v for k, v in calismalar_oku().items() if k != eski_ad}
    hepsi[c["ad"].strip()] = {**{k: c[k] for k in ("testler", "gruplar", "zamanlar", "atamalar")},
                              "dokunuldu": _dt_simdi().isoformat(timespec="seconds")}
    ayar_yaz(CALISMA_ANAHTAR, hepsi)
    return []


def calisma_dokun(ad):
    """Çalışmayla oturum kaydedilince: "en son dokunulan" çalışma öneride öne geçer (Paket 33)."""
    ham = ayar_oku().get(CALISMA_ANAHTAR, {})
    if isinstance(ham, dict) and isinstance(ham.get(ad), dict):
        ham[ad] = {**ham[ad], "dokunuldu": _dt_simdi().isoformat(timespec="seconds")}
        ayar_yaz(CALISMA_ANAHTAR, ham)


def calisma_sil(ad):
    ayar_yaz(CALISMA_ANAHTAR, {k: v for k, v in calismalar_oku().items() if k != ad})


def calisma_oturum_adi(calisma_adi, zaman):
    """Çalışmayla yapılan oturumda "Oturum" alanına yazılan değer: çalışma · ölçüm zamanı."""
    return f"{calisma_adi} · {zaman}"


def oturum_kimligi(calisma_adi, zaman, simdi):
    """Kaydedilen oturumun "Oturum" değeri: çalışmayla "çalışma · ölçüm zamanı", serbest seçimde "OT-zaman damgası"."""
    if calisma_adi and zaman:
        return calisma_oturum_adi(calisma_adi, zaman)
    return f"OT-{simdi:%Y%m%d-%H%M%S}"


def calisma_sporculari(c, gruplar=None):
    """Çalışmada gruba atanmış sporcular (gruplar verilirse yalnız o gruplar), atama sırasıyla."""
    return [s for s, g in c.get("atamalar", {}).items() if g and (not gruplar or g in gruplar)]
