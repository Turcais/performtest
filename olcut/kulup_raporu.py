"""
Kulüp raporu (Paket 38n-2): seçili kulübün toplu özeti — A4 HTML (PDF'e disa_aktarma.pdf_cevir ile).

Yeni hesap YOK; var olan işlevler sporcu başına çalıştırılır ve sonuçları sayılır:
- Yaş bandı × cinsiyet: karsilastirma.sporcu_ozellikleri + yas_bandi.
- Oturumlar: kayit.oturum_secenekleri / karsilastirma.oturum_adlari.
- Test başına konum: sporcu başına norm.sporcu_z_profili → raporlar.veli_test_ozeti (veli raporunun seçtiği son gün,
  en iyi deneme) → raporlar.veli_aralik_konumu; aralığın altında / içinde / üstünde KAÇ sporcu (isim yok).
- Oturumlar arası: ilk ve son oturum, karsilastirma.oturumlar_arasi (11 yaş altında yalnız arttı/azaldı) +
  wilcoxon_isaretli_sira (n ≥ 6; altında yalnız tanımlayıcı).
Yeni olan yalnız iki seçim kuralı: ilk ↔ son oturum; çok değişkenli testte "En İyi" adlı değişken, yoksa ilki.
Kurallar: sporcu adı yok (isteğe bağlı ek hariç: ad, yaş, cinsiyet, oturumlar — değer ve sıra yok); sıralama yok;
yüzdelik yok; normsuz testte norm kıyası yok.
"""
import collections
import re
from datetime import date
import pandas as pd
from olcut.analiz import RAPOR_CSS, _sonuc_degiskenleri, ana_sonuc_tanimi
from olcut.karsilastirma import (
    KARS_ISTATISTIK_EN_AZ_N, KARS_YON_ISARETI, YAS_BANTLARI, _oturum_adi, degisen_yetersiz_metni, etki_metni,
    olcum_yasi, oturum_testleri, oturumlar_arasi, p_metni, sporcu_ozellikleri, wilcoxon_isaretli_sira, yas_bandi)
from olcut.katalog_islemleri import kanonik_test, test_niteligi
from olcut.kayit import oturum_secenekleri
from olcut.norm import degisken_yonu, ktk3_toplamlari, sporcu_z_profili
from olcut.ortak import _e, ad_bicimi
from olcut.raporlar import VELI_GRUPLARI, veli_aralik_konumu, veli_test_ozeti
from olcut.tema import kimlik_html

KULUP_RAPOR_ACIKLAMA = (
    "Bu rapor kulübün toplu durumunu gösterir; hiçbir çocuğun adı ve tek tek değeri yoktur. Sayılar karar değil, "
    "antrenörlerle konuşmayı başlatacak bilgidir.")
KULUP_RAPOR_KONUM_NOTU = (
    "Konum, her sporcunun son ölçümünün aynı yaş ve cinsiyetteki çocuklar/sporcular için yayımlanmış değerlere göre "
    "yeridir (veli raporundaki aralık diliyle; birden çok denemede en iyi deneme). “Üstünde/altında” yön bildirir, iyi "
    "ya da kötü anlamına gelmez: süre testlerinde düşük değer daha iyidir. Konum verilmeyenler: bu kayıtlar için normu "
    "olmayan test (“norm kıyası yok”), sporcunun yaşı normun kapsamı dışında, ya da veli raporundaki gibi dayanıklılık (uzun koşu) ve vücut "
    "ölçüsü testleri. Yüzdelik kullanılmaz; sporcular sıralanmaz.")
KULUP_RAPOR_DEGISIM_NOTU = (
    f"İlk ve son oturumda ölçülen aynı sporcular karşılaştırılır (fark = son − ilk). 11 yaş altında (son ölçüm "
    f"günündeki yaşla) yalnız “arttı / azaldı” yazılır. Değeri değişen sporcu {KARS_ISTATISTIK_EN_AZ_N}'dan azsa "
    f"istatistik testi yapılmaz, yalnız tanımlayıcı değer verilir. Her testte uygulamanın ana sonucu kullanılır: KTK "
    f"toplamı, “En İyi” değer ya da denemelerin en iyisi. Vücut ölçülerinde (boy, kilo, oturma yüksekliği, kulaç) "
    f"istatistik testi yapılmaz, yalnız ortalama fark verilir.")
KULUP_RAPOR_COK_BILESENLI = "Çok bileşenli testler (ör. {ornek}) bu özete girmez."
KULUP_RAPOR_VUCUT = "vücut ölçüsü: istatistik testi yok"
CINSIYETLER = ("Kadın", "Erkek")


def _tablo(basliklar, satirlar):
    bas = "".join(f"<th>{_e(b)}</th>" for b in basliklar)
    gov = "".join("<tr>" + "".join(f"<td>{_e(h)}</td>" for h in s) + "</tr>" for s in satirlar)
    return f"<table><thead><tr>{bas}</tr></thead><tbody>{gov}</tbody></table>"


def _sporcu_adlari(df_sp):
    if df_sp is None or df_sp.empty or not {"Ad", "Soyad"} <= set(df_sp.columns):
        return []
    d = df_sp.dropna(subset=["Ad"])
    return sorted(dict.fromkeys(d["Ad"].astype(str) + " " + d["Soyad"].astype(str)))


def _virgul(x, ondalik=2):
    return f"{float(x):.{ondalik}f}".replace(".", ",")


def bugunku_yas(oz, bugun=None):
    """Paket 38p: kulüp raporunun yaş tablosu — doğum tarihinden bugünkü yaş; yoksa profil yaşı."""
    return olcum_yasi(oz, None, (bugun or date.today()).strftime("%d.%m.%Y"))


def yas_cinsiyet_dagilimi(df_sp, bugun=None):
    """[(bant, kadın, erkek, belirtilmemiş, toplam)] + toplam satırı; yaşı yoksa / 6'dan küçükse 'Bilinmiyor'."""
    adlar = _sporcu_adlari(df_sp)
    oz = sporcu_ozellikleri(adlar, df_sp)
    sayim = collections.Counter()
    for s in adlar:
        bant = yas_bandi(bugunku_yas(oz[s], bugun)) or "Bilinmiyor"
        cins = oz[s]["cinsiyet"] if oz[s]["cinsiyet"] in CINSIYETLER else "Belirtilmemiş"
        sayim[(bant, cins)] += 1
    bantlar = [f"{a}–{u}" if u else f"{a}+" for a, u in YAS_BANTLARI] + ["Bilinmiyor"]
    satir = []
    for b in bantlar:
        k, e, x = sayim[(b, "Kadın")], sayim[(b, "Erkek")], sayim[(b, "Belirtilmemiş")]
        if k + e + x:
            satir.append((b, k, e, x, k + e + x))
    toplam = tuple(sum(r[i] for r in satir) for i in range(1, 5))
    return satir, ("Toplam",) + toplam


def oturum_ozeti(df):
    """[(oturum adı, tarih, sporcu sayısı)] — en eski önce."""
    if df is None or df.empty or "Oturum" not in df.columns:
        return []
    sonuc = []
    for kim in oturum_secenekleri(df):
        g = df[df["Oturum"].astype(str) == str(kim)]
        t = pd.to_datetime(g["Tarih"], format="%d.%m.%Y", errors="coerce").dropna()
        tarih = t.min().strftime("%d.%m.%Y") if len(t) else ""
        if len(t) and t.min() != t.max():
            tarih += f"–{t.max().strftime('%d.%m.%Y')}"
        sonuc.append((_oturum_adi(g, kim), tarih, g["Sporcu"].nunique(), t.min() if len(t) else pd.NaT, kim))
    sonuc.sort(key=lambda r: (pd.isna(r[3]), r[3]))
    return sonuc


def test_konum_dagilimi(df):
    """
    {test: {"n": ölçülen sporcu, "altinda", "icinde", "ustunde", "konumsuz", "normlu"}} — konum veli raporunun
    yolundan. normlu: herhangi bir sporcuda norm satırı oluştu mu (antrenör raporundaki "normsuz" tanımıyla aynı).
    """
    sonuc = {}
    if df is None or df.empty:
        return sonuc
    for t, g in df.groupby(df["Test"].map(kanonik_test)):
        sonuc[t] = {"n": g["Sporcu"].nunique(), "altinda": 0, "icinde": 0, "ustunde": 0, "normlu": False}
    for s in sorted(df["Sporcu"].dropna().astype(str).unique()):
        zp = sporcu_z_profili(df, s)
        for r in zp.get("satirlar", []):
            if kanonik_test(r["Test"]) in sonuc:
                sonuc[kanonik_test(r["Test"])]["normlu"] = True
        oz = veli_test_ozeti(zp)
        for grup in VELI_GRUPLARI:
            for t in oz[grup]["testler"]:
                if t.get("p10") is None or kanonik_test(t["test"]) not in sonuc:
                    continue
                yer = veli_aralik_konumu({"deger": t["deger"], "p10": t["p10"], "p90": t["p90"]})
                sonuc[kanonik_test(t["test"])][yer.split("_")[0]] += 1
    for d in sonuc.values():
        d["konumsuz"] = d["n"] - d["altinda"] - d["icinde"] - d["ustunde"]
    return sonuc


def ana_sonuc(df, test):
    """
    Testin ana sonucu (uygulamanın kuralı): KTK toplamı (ktk3_toplamlari) varsa o; yoksa ana_sonuc_tanimi — "En İyi"
    değişkeni, denemelerin en iyisi (testin yönüne göre) ya da tek değişken. Döner: (testin kayıtları — ana sonuç bir
    sütunda, sütun adı, ekranda etiket) ya da çok bileşenliyse None.
    """
    g = df[df["Test"].map(kanonik_test) == kanonik_test(test)].copy()
    if g.empty:
        return None
    toplam = {}
    for i, r in g.iterrows():
        for k, v in ktk3_toplamlari(kanonik_test(test), r.to_dict()).items():
            toplam.setdefault(k, {})[i] = v
    if toplam:
        k = next(iter(toplam))
        mevcut = pd.to_numeric(g[k], errors="coerce") if k in g.columns else pd.Series(index=g.index, dtype=float)
        g[k] = mevcut.where(mevcut.notna(), pd.Series(toplam[k]))
        return g, k, k
    tanim = ana_sonuc_tanimi(test, _sonuc_degiskenleri(g))
    if tanim is None:
        return None
    tur, d = tanim
    if tur == "deneme":
        sayilar = g[d].apply(pd.to_numeric, errors="coerce")
        g[d[0]] = sayilar.min(axis=1) if degisken_yonu(test, d[0]) is True else sayilar.max(axis=1)
        return g, d[0], re.sub(r"^Deneme \d+", "En iyi deneme", d[0])
    return g, d, d


def oturumlar_arasi_ozeti(df, oturumlar):
    """
    İlk ↔ son oturum, her ortak test (ana sonuç): n, yön sayıları, ortalama fark, Wilcoxon (değişen ≥ 6; vücut
    ölçüsünde yok). Döner: (ilk, son), satırlar, çok bileşenli olduğu için çıkarılan testler.
    """
    if len(oturumlar) < 2:
        return None, [], []
    ilk, son = oturumlar[0], oturumlar[-1]
    satir, disarida = [], []
    for test in oturum_testleri(df, [ilk[4]], [son[4]]):
        a = ana_sonuc(df, test)
        if a is None:
            disarida.append(test)
            continue
        g, deg, etiket = a
        r = oturumlar_arasi(g, test, deg, [ilk[4]], [son[4]])
        if not r["satirlar"]:
            continue
        farklar = [x["Fark"] for x in r["satirlar"]]
        yon = collections.Counter(x["Yorum"] for x in r["satirlar"])
        yon_metni = " · ".join(f"{KARS_YON_ISARETI[y]} {y} {yon[y]}" for y in
                               ("daha iyi", "daha kötü", "arttı", "azaldı", "değişmedi") if yon[y])
        if test_niteligi(test) == "antropometri":
            ist = KULUP_RAPOR_VUCUT
        else:
            w = wilcoxon_isaretli_sira(farklar)
            ist = (degisen_yetersiz_metni(w) if w.get("yetersiz") else
                   f"{p_metni(w['p'])}, r = {_virgul(w['r'])} ({etki_metni(w['r'])})")
        satir.append((test, etiket, len(farklar), yon_metni,
                      f"{_virgul(sum(farklar) / len(farklar))} {r['birim']}".strip(), ist))
    return (ilk, son), satir, disarida


def kulup_raporu_html(bilgi, df_sp, df, sporcu_listesi=False, bugun=None):
    """
    bilgi: kulup.json; df_sp: sporcular; df: sonuçlar (kanonik test adı). sporcu_listesi: ek (ad, yaş, cinsiyet,
    ölçüldüğü oturumlar; değer ve sıra yok). Döner: A4 HTML (RAPOR_CSS).
    """
    ad = _e(bilgi.get("ad", ""))
    tarih = (bugun or date.today()).strftime("%d.%m.%Y")
    adlar = _sporcu_adlari(df_sp)
    p = [f'<!doctype html><html lang="tr"><head><meta charset="utf-8">'
         f'<meta name="viewport" content="width=device-width, initial-scale=1">'
         f'<title>Kulüp raporu — {ad}</title>{RAPOR_CSS}</head><body><div class="sayfa">{kimlik_html()}',
         f"<h1>{ad} — Kulüp raporu</h1>",
         f'<div class="alt">Rapor tarihi: {tarih} · Kayıtlı sporcu: {len(adlar)}'
         + (f" · {_e(bilgi.get('sehir'))}" if bilgi.get("sehir") else "")
         + (f" · Branşlar: {_e(', '.join(bilgi.get('branslar') or []))}" if bilgi.get("branslar") else "") + "</div>",
         f"<p>{_e(KULUP_RAPOR_ACIKLAMA)}</p>"]

    satir, toplam = yas_cinsiyet_dagilimi(df_sp, bugun)
    p.append("<h2>Sporcular: yaş bandı ve cinsiyet</h2>")
    p.append(_tablo(["Yaş bandı", "Kadın", "Erkek", "Belirtilmemiş", "Toplam"], satir + [toplam]) if satir
             else "<p>Kayıtlı sporcu yok.</p>")

    oturumlar = oturum_ozeti(df)
    p.append("<h2>Oturumlar</h2>")
    p.append(_tablo(["Oturum", "Tarih", "Sporcu sayısı"], [(o[0], o[1], o[2]) for o in oturumlar]) if oturumlar
             else "<p>Kayıtlı oturum yok.</p>")

    konum = test_konum_dagilimi(df)
    p.append("<h2>Testler: kaç sporcu ölçüldü, normlara göre nerede</h2>")
    if konum:
        p.append(_tablo(["Test", "Ölçülen sporcu", "▼ Aralığın altında", "● Aralığın içinde", "▲ Aralığın üstünde",
                         "Konum yok"],
                        [(t, d["n"], d["altinda"], d["icinde"], d["ustunde"],
                          f"{d['konumsuz']} (norm kıyası yok)" if not d["normlu"] else d["konumsuz"])
                         for t, d in sorted(konum.items())]))
        p.append(f'<p class="kucuk">{_e(KULUP_RAPOR_KONUM_NOTU)}</p>')
    else:
        p.append("<p>Kayıtlı test sonucu yok.</p>")

    cift, degisim, cok_bilesenli = oturumlar_arasi_ozeti(df, oturumlar)
    p.append("<h2>Oturumlar arası değişim</h2>")
    if cift and degisim:
        p.append(f"<p>{_e(cift[0][0])} ({_e(cift[0][1])}) → {_e(cift[1][0])} ({_e(cift[1][1])})</p>")
        p.append(_tablo(["Test", "Değişken", "n", "Yön", "Ortalama fark", "İstatistik (Wilcoxon)"], degisim))
        if cok_bilesenli:
            p.append(f'<p class="kucuk">{_e(KULUP_RAPOR_COK_BILESENLI.format(ornek=", ".join(cok_bilesenli[:3])))}</p>')
        p.append(f'<p class="kucuk">{_e(KULUP_RAPOR_DEGISIM_NOTU)}</p>')
    else:
        p.append("<p>Karşılaştırmak için aynı sporcuların ölçüldüğü en az iki oturum gerekli.</p>")

    if sporcu_listesi and adlar:
        oz = sporcu_ozellikleri(adlar, df_sp)
        ot_ad = {o[4]: o[0] for o in oturumlar}
        olculen = {}
        if df is not None and not df.empty and "Oturum" in df.columns:
            for s, g in df.groupby("Sporcu"):
                olculen[s] = [ot_ad[k] for k in ot_ad if k in set(g["Oturum"].astype(str))]
        p.append("<h2>Ek: Sporcu listesi</h2><p class=\"kucuk\">Yalnız ad, yaş, cinsiyet ve ölçüldüğü oturumlar; "
                 "değer ve sıra yoktur.</p>")
        p.append(_tablo(["Ad Soyad", "Yaş", "Cinsiyet", "Ölçüldüğü oturumlar"],
                        [(ad_bicimi(s), "" if bugunku_yas(oz[s], bugun) is None else int(bugunku_yas(oz[s], bugun)),
                          oz[s]["cinsiyet"],
                          ", ".join(olculen.get(s, [])) or "—") for s in adlar]))
    p.append("</div></body></html>")
    return "".join(p)
