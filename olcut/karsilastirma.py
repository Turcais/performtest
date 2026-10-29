"""
Karşılaştırma (Paket 38g) — Streamlit'siz hesap katmanı. Ekran: olcut/sayfalar/karsilastirma.py.

Sporcular arası: iki grup (A, B; B boş olabilir), seçilen oturum(lar)da sporcu başına son ölçüm, grup özetleri.
Oturumlar arası: sol (önce) ve sağ (sonra) oturum kümeleri, aynı sporcu için Önce / Sonra / Fark; isteğe bağlı
Wilcoxon işaretli sıra testi ve etki büyüklüğü (n ≥ 6).
Kurallar: grupta n < 20 → yüzdelik yok; 11 yaş altı sporcu varsa sıralama ve "daha iyi / kötü" etiketi yok;
yaş/cinsiyet karışıksa uyarı (isteğe bağlı z-skoru). Değerler kayıttaki ham değerlerdir; hesap yeniden yapılmaz.
Eski "Kapsam" mantığı (Bireysel / Tek oturum / Oturumlar arası) kayit.oturum_degerleri ve oturumlar_arasi_fark ile
burada yeniden kullanılır.
"""
import math
import os
import pandas as pd
from olcut.analiz import GRUP_KONUM_YUZDELIK_N, VELI_KONUM_EN_AZ_YAS
from olcut.katalog_islemleri import kanonik_test
from olcut.kayit import _degisken_birimi, oturum_degerleri, oturum_secenekleri, oturumlar_arasi_fark
from olcut.norm import META_KOLONLAR, NORMATIF_YAS, OTURUM_ADI_KOLON, SPORCU_DOSYA, degisken_yonu, yas_z_skoru
from olcut.ortak import _yas_degeri, ad_bicimi


KARS_YUZDELIK_EN_AZ_N = GRUP_KONUM_YUZDELIK_N    # grupta n ≥ 20: çeyrekler (P25–P75) gösterilebilir
KARS_SIRALAMA_EN_AZ_YAS = VELI_KONUM_EN_AZ_YAS   # 11 yaş altında sıralama ve daha iyi / kötü etiketi yok
KARS_ISTATISTIK_EN_AZ_N = 6                      # Wilcoxon için en az eşleştirilmiş (sıfırdan farklı) fark
KARS_KESIN_EN_COK_N = 25                         # bu sayıya kadar (eşit |fark| yoksa) kesin dağılım
KARS_YON_ISARETI = {"daha iyi": "✓", "daha kötü": "!", "değişmedi": "=", "arttı": "▲", "azaldı": "▼"}
KARS_KARISIK_UYARI = "Yaş ve cinsiyet karışık; ham değerler karşılaştırılıyor."
KARS_KUCUK_NOTU = ("11 yaş altı sporcu var: sıralama ve “daha iyi / daha kötü” etiketi gösterilmez; yalnız "
                   "değerler ve her sporcunun kendi değişimi.")
KARS_YUZDELIK_YOK_NOTU = "Grupta 20'den az sporcu var: yüzdelik gösterilmez; ortalama ve aralık verilir."


def sporcu_ozellikleri(sporcular):
    """{sporcu: {"yas": int|None, "cinsiyet": str}} — sporcular.xlsx'ten (Ad + ' ' + Soyad), bir kez okunur."""
    sonuc = {s: {"yas": None, "cinsiyet": ""} for s in sporcular}
    if not sporcular or not os.path.exists(SPORCU_DOSYA):
        return sonuc
    df = pd.read_excel(SPORCU_DOSYA)
    if not {"Ad", "Soyad"} <= set(df.columns):
        return sonuc
    df["_ad"] = df["Ad"].astype(str) + " " + df["Soyad"].astype(str)
    for s in sporcular:
        e = df[df["_ad"] == s]
        if not e.empty:
            r = e.iloc[0]
            sonuc[s] = {"yas": _yas_degeri(r.get("Yaş")), "cinsiyet": str(r.get("Cinsiyet", "") or "").strip()}
    return sonuc


def ortak_testler(df, sporcular):
    """Seçili sporcuların HEPSİNİN en az bir kaydı olan testler (kanonik ad, sıralı)."""
    if df is None or df.empty or not sporcular:
        return []
    d = df[df["Sporcu"].isin(list(sporcular))]
    kume = None
    for s in set(sporcular):
        t = set(d.loc[d["Sporcu"] == s, "Test"].map(kanonik_test))
        kume = t if kume is None else kume & t
    return sorted(kume or [])


def oturum_testleri(df, sol, sag):
    """Sol ve sağ oturum kümelerinin İKİSİNDE de kaydı olan testler."""
    if df is None or df.empty or "Oturum" not in df.columns or not sol or not sag:
        return []
    o = df["Oturum"].astype(str)
    a = set(df.loc[o.isin([str(x) for x in sol]), "Test"].map(kanonik_test))
    b = set(df.loc[o.isin([str(x) for x in sag]), "Test"].map(kanonik_test))
    return sorted(a & b)


def _oturum_adi(g, kim):
    """Oturumun görünen adı: "Oturum Adı" sütunu; yoksa kimlik (OT- kodunda "Oturum")."""
    if OTURUM_ADI_KOLON in g.columns:
        adlar = [str(a).strip() for a in g[OTURUM_ADI_KOLON].dropna() if str(a).strip() not in ("", "nan")]
        if adlar:
            return adlar[0]
    return "Oturum" if str(kim).startswith("OT-") else str(kim)


def oturum_adlari(df, kimlikler):
    """Seçilen oturumların adları (etiket değil; adın kendisi " · " içerebilir), virgülle."""
    return ", ".join(_oturum_adi(df[df["Oturum"].astype(str) == str(k)], k) for k in kimlikler)


def oturum_etiketleri(df):
    """
    {oturum kimliği: "ad (tarih) · n sporcu"} — karşılaştırma seçim sütunu için; sıra oturum_secenekleri ile aynı
    (en yeni önce). Ad: "Oturum Adı" sütunu; yoksa kimlik (çalışma oturumu: "Çalışma · zaman"); OT- kodunda "Oturum".
    """
    sonuc = {}
    for kim in oturum_secenekleri(df):
        g = df[df["Oturum"].astype(str) == str(kim)]
        ad = _oturum_adi(g, kim)
        tarihler = sorted({str(t) for t in g["Tarih"].dropna()},
                          key=lambda t: pd.to_datetime(t, format="%d.%m.%Y", errors="coerce"))
        tarih = tarihler[0] if len(tarihler) == 1 else (f"{tarihler[0]}–{tarihler[-1]}" if tarihler else "tarih yok")
        sonuc[kim] = f"{ad} ({tarih}) · {g['Sporcu'].nunique()} sporcu"
    return sonuc


def sayisal_degiskenler(df, test):
    """Testin sayısal değeri olan değişkenleri (meta sütunlar hariç), tablodaki sırayla."""
    d = df[df["Test"].map(kanonik_test) == kanonik_test(test)]
    return [k for k in d.columns if k not in META_KOLONLAR and k not in ("Tarih_dt", "Test Yaşı")
            and pd.to_numeric(d[k], errors="coerce").notna().any()]


def degisken_birimi(test, degisken):
    n = NORMATIF_YAS.get(f"{kanonik_test(test)} › {degisken}") or {}
    return n.get("birim") or _degisken_birimi(degisken)


def grup_ozeti(degerler):
    """n, ortalama, en küçük, en büyük; n ≥ 20 ise çeyrekler (P25, P75). Boşsa n = 0."""
    x = sorted(float(v) for v in degerler)
    if not x:
        return {"n": 0}
    oz = {"n": len(x), "ortalama": sum(x) / len(x), "en_kucuk": x[0], "en_buyuk": x[-1], "p25": None, "p75": None}
    if len(x) >= KARS_YUZDELIK_EN_AZ_N:
        oz["p25"], oz["p75"] = _yuzdelik(x, 25), _yuzdelik(x, 75)
    return oz


def _yuzdelik(sirali, p):
    h = (len(sirali) - 1) * p / 100
    a = int(h)
    return sirali[a] + (sirali[min(a + 1, len(sirali) - 1)] - sirali[a]) * (h - a)


def karisik_mi(ozellik):
    """Seçilenler arasında birden çok yaş ya da cinsiyet var mı (bilinmeyenler sayılmaz)."""
    yaslar = {o["yas"] for o in ozellik.values() if o.get("yas") is not None}
    cinsler = {o["cinsiyet"] for o in ozellik.values() if o.get("cinsiyet")}
    return len(yaslar) > 1 or len(cinsler) > 1


def kucuk_var_mi(ozellik):
    """11 yaş altı sporcu var mı (yaşı bilinmeyen sporcu da temkinle 'küçük' sayılır)."""
    return any(o.get("yas") is None or o["yas"] < KARS_SIRALAMA_EN_AZ_YAS for o in ozellik.values())


def sporcular_arasi(df, test, degisken, grup_a, grup_b=(), oturumlar=None, z=False):
    """
    Dönen: {"satirlar": [{Grup, Sporcu, Yaş, Cinsiyet, Ölçüm tarihi, Değer, Birim[, Z]}], "ozet": {"A": …, "B": …},
            "karisik": bool, "kucuk": bool, "olcumsuz": [sporcu], "birim": str}
    B boşsa karşılaştırma yalnız A içinde. Sporcu iki grupta da seçildiyse iki satırda yer alır.
    Sıralama: 11 yaş altı sporcu yoksa testin yönüne göre (en iyi önce); varsa ada göre (sıralama yok).
    """
    secili = list(dict.fromkeys(list(grup_a) + list(grup_b)))
    ozellik = sporcu_ozellikleri(secili)
    degerler = oturum_degerleri(df, test, degisken, list(oturumlar) if oturumlar else None, tarihli=True)
    birim = degisken_birimi(test, degisken)
    kucuk = kucuk_var_mi(ozellik)
    yon = degisken_yonu(test, degisken)
    satirlar, olcumsuz, ozet = [], [], {}
    for grup, uyeler in (("A", grup_a), ("B", grup_b)):
        g = []
        for s in uyeler:
            if s not in degerler:
                olcumsuz.append(s)
                continue
            v, tarih = degerler[s]
            o = ozellik.get(s, {})
            satir = {"Grup": grup, "Sporcu": s, "Yaş": o.get("yas"), "Cinsiyet": o.get("cinsiyet") or "—",
                     "Ölçüm tarihi": tarih, "Değer": v, "Birim": birim}
            if z:
                zs = (yas_z_skoru(test, degisken, o.get("yas"), o.get("cinsiyet"), v)
                      if o.get("yas") is not None and o.get("cinsiyet") in ("Erkek", "Kadın") else None)
                satir["Z"] = round(zs["z_performans"], 2) if zs and zs.get("z_performans") is not None else None
            g.append(satir)
        if kucuk or yon is None:
            g.sort(key=lambda r: r["Sporcu"])
        else:
            g.sort(key=lambda r: r["Değer"], reverse=not yon)
        satirlar += g
        if uyeler:
            ozet[grup] = grup_ozeti([r["Değer"] for r in g])
    return {"satirlar": satirlar, "ozet": ozet, "karisik": karisik_mi(ozellik), "kucuk": kucuk,
            "olcumsuz": sorted(set(olcumsuz)), "birim": birim}


def oturumlar_arasi(df, test, degisken, sol, sag):
    """
    Aynı sporcu için Önce (sol oturumlar) / Sonra (sağ oturumlar) / Fark. Yorum testin yönünden (sürede düşüş iyi);
    11 yaş altı sporcunun satırında yalnız arttı / azaldı / değişmedi. Yön sütunu: simge + sözcük.
    Dönen: {"satirlar": [...], "kucuk": bool, "birim": str}
    """
    ham = oturumlar_arasi_fark(df, test, degisken, list(sol), list(sag))
    ozellik = sporcu_ozellikleri([r["Sporcu"] for r in ham])
    satirlar = []
    for r in ham:
        o = ozellik.get(r["Sporcu"], {})
        yorum = r["Yorum"]
        if (o.get("yas") is None or o["yas"] < KARS_SIRALAMA_EN_AZ_YAS) and yorum in ("daha iyi", "daha kötü"):
            yorum = "arttı" if r["Fark"] > 0 else "azaldı"
        satirlar.append({"Sporcu": r["Sporcu"], "Yaş": o.get("yas"), "Önce": r["Önceki"], "Sonra": r["Sonraki"],
                         "Fark": r["Fark"], "Yön": f"{KARS_YON_ISARETI[yorum]} {yorum}", "Yorum": yorum})
    return {"satirlar": satirlar, "kucuk": kucuk_var_mi(ozellik), "birim": degisken_birimi(test, degisken)}


# ── Wilcoxon işaretli sıra testi (SciPy'siz) ──
def _siralar(degerler):
    """Ortalama sıralar (eşitlerde ortalama sıra), 1'den başlar."""
    sira = sorted(range(len(degerler)), key=lambda i: degerler[i])
    r = [0.0] * len(degerler)
    i = 0
    while i < len(sira):
        j = i
        while j + 1 < len(sira) and degerler[sira[j + 1]] == degerler[sira[i]]:
            j += 1
        for k in range(i, j + 1):
            r[sira[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def wilcoxon_isaretli_sira(farklar):
    """
    Eşleştirilmiş farklar için iki yönlü Wilcoxon işaretli sıra testi. Sıfır farklar atılır (Wilcoxon yöntemi).
    n ≤ 25 ve eşit |fark| yoksa kesin dağılım; aksi hâlde normal yaklaşım (eşitlik ve süreklilik düzeltmesiyle).
    Etki büyüklüğü: eşleştirilmiş sıra-iki serili korelasyon r = (W+ − W−) / (W+ + W−), −1…+1.
    Dönen: {"n", "w_arti", "w_eksi", "w", "p", "r", "yontem"} ya da n < 6 ise {"n", "yetersiz": True}.
    """
    d = [float(x) for x in farklar if x is not None and not (isinstance(x, float) and math.isnan(x)) and x != 0]
    n = len(d)
    if n < KARS_ISTATISTIK_EN_AZ_N:
        return {"n": n, "yetersiz": True}
    mutlak = [abs(x) for x in d]
    r = _siralar(mutlak)
    w_arti = sum(ri for ri, x in zip(r, d) if x > 0)
    w_eksi = sum(ri for ri, x in zip(r, d) if x < 0)
    w = min(w_arti, w_eksi)
    esit_var = len(set(mutlak)) < n
    if n <= KARS_KESIN_EN_COK_N and not esit_var:
        # kesin dağılım: 1..n sıralarının alt küme toplamlarının sayısı
        enbuyuk = n * (n + 1) // 2
        say = [0] * (enbuyuk + 1)
        say[0] = 1
        for k in range(1, n + 1):
            for t in range(enbuyuk, k - 1, -1):
                say[t] += say[t - k]
        toplam = 2 ** n
        p = min(1.0, 2 * sum(say[:int(w) + 1]) / toplam)
        yontem = "kesin"
    else:
        ort = n * (n + 1) / 4
        esit_duz = sum(c ** 3 - c for c in pd.Series(mutlak).value_counts()) / 48
        sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24 - esit_duz)
        zz = (abs(w - ort) - 0.5) / sd if sd > 0 else 0.0
        p = min(1.0, math.erfc(zz / math.sqrt(2)))
        yontem = "normal yaklaşım"
    rr = (w_arti - w_eksi) / (w_arti + w_eksi) if (w_arti + w_eksi) else 0.0
    return {"n": n, "w_arti": w_arti, "w_eksi": w_eksi, "w": w, "p": p, "r": rr, "yontem": yontem}


def etki_metni(r):
    """|r| < 0,1 ihmal edilebilir · < 0,3 küçük · < 0,5 orta · ≥ 0,5 büyük (sıra-iki serili r için yaygın eşikler)."""
    a = abs(r)
    return "ihmal edilebilir" if a < 0.1 else "küçük" if a < 0.3 else "orta" if a < 0.5 else "büyük"


# ── Dışa aktarma (Paket 38i): ekrandaki sonuç olduğu gibi; hesap yeniden yapılmaz ──
def _olcum_oturumu(df, sporcu, test, degisken, tarih, oturumlar=None):
    """Değerin geldiği satırın oturum adı (aynı sporcu, test, tarih; değişken dolu). Kayıttan bakılır, hesap yok."""
    if "Oturum" not in df.columns or degisken not in df.columns:
        return ""
    d = df[(df["Sporcu"].astype(str) == str(sporcu)) & (df["Test"].map(kanonik_test) == kanonik_test(test))
           & (df["Tarih"].astype(str) == str(tarih)) & pd.to_numeric(df[degisken], errors="coerce").notna()]
    if oturumlar:
        d = d[d["Oturum"].astype(str).isin([str(o) for o in oturumlar])]
    kimlikler = [k for k in dict.fromkeys(d["Oturum"].dropna().astype(str)) if k not in ("", "nan")]
    return ", ".join(_oturum_adi(df[df["Oturum"].astype(str) == k], k) for k in kimlikler)


def _yas_tam_sayi(tablo):
    """Yaş ekrandaki gibi tam sayı ("10", "10,0" değil); bilinmeyen yaş boş kalır."""
    if "Yaş" in tablo.columns:
        tablo["Yaş"] = pd.to_numeric(tablo["Yaş"], errors="coerce").round().astype("Int64")
    return tablo


def sporcular_arasi_disa(df, r, test, degisken, oturumlar=None):
    """
    Sporcular arası sonucun dışa aktarılan tablosu: ekrandaki satırlar, sıra ve değerler (r["satirlar"]); test,
    değişken ve değerin geldiği oturum eklenir. Sıra/yüzdelik sütunu yazılmaz (11 yaş altı ve n < 20 kuralları).
    """
    satirlar = []
    for x in r["satirlar"]:
        d = {"Sporcu": ad_bicimi(x["Sporcu"]), "Grup": x["Grup"], "Yaş": x["Yaş"], "Cinsiyet": x["Cinsiyet"],
             "Test": test, "Değişken": degisken, "Birim": x["Birim"], "Ölçüm tarihi": x["Ölçüm tarihi"],
             "Oturum": _olcum_oturumu(df, x["Sporcu"], test, degisken, x["Ölçüm tarihi"], oturumlar),
             "Değer": x["Değer"]}
        if "Z" in x:
            d["Z"] = x["Z"]
        satirlar.append(d)
    return _yas_tam_sayi(pd.DataFrame(satirlar))


def grup_ozeti_disa(r):
    """Grup özetleri (ekrandaki satırla aynı sayılar). Çeyrek sütunları yalnız her grupta n ≥ 20 ise yazılır."""
    gruplar = {g: oz for g, oz in r["ozet"].items() if oz.get("n")}
    ceyrek = bool(gruplar) and all(oz.get("p25") is not None for oz in gruplar.values())
    satirlar = []
    for g, oz in gruplar.items():
        d = {"Grup": g, "n": oz["n"], "Ortalama": oz["ortalama"], "En küçük": oz["en_kucuk"],
             "En büyük": oz["en_buyuk"], "Birim": r["birim"]}
        if ceyrek:
            d["P25"], d["P75"] = oz["p25"], oz["p75"]
        satirlar.append(d)
    return pd.DataFrame(satirlar)


def oturumlar_arasi_disa(r, test, degisken, once="", sonra=""):
    """
    Oturumlar arası sonucun dışa aktarılan tablosu: ekrandaki Sporcu, Yaş, Önce, Sonra, Fark, Yön (11 yaş altında
    yalnız arttı/azaldı — r["satirlar"]'da zaten öyle); test, değişken, birim ve oturum adları eklenir.
    """
    return _yas_tam_sayi(pd.DataFrame([{"Sporcu": ad_bicimi(x["Sporcu"]), "Yaş": x["Yaş"], "Test": test,
                                        "Değişken": degisken, "Birim": r["birim"], "Önce oturum": once,
                                        "Sonra oturum": sonra, "Önce": x["Önce"], "Sonra": x["Sonra"],
                                        "Fark": x["Fark"], "Yön": x["Yön"]} for x in r["satirlar"]]))


def istatistik_disa(w):
    """Wilcoxon sonucu tek satır (ekrandaki sayılar); n küçükse yalnız n ve not."""
    if not w:
        return pd.DataFrame()
    if w.get("yetersiz"):
        return pd.DataFrame([{"n": w["n"], "Not": f"n < {KARS_ISTATISTIK_EN_AZ_N}: yalnız tanımlayıcı; test yapılmadı"}])
    return pd.DataFrame([{"Test": "Wilcoxon işaretli sıra", "Yöntem": w["yontem"], "n": w["n"], "W": w["w"],
                          "p": w["p"], "Etki büyüklüğü r": w["r"], "Etki": etki_metni(w["r"])}])


def csv_ile_istatistik(tablo, w):
    """CSV tek sayfa: istatistik açıksa p ve r her satıra ayrı sütun olarak eklenir."""
    if not w or w.get("yetersiz"):
        return tablo
    t = tablo.copy()
    t["p (Wilcoxon)"], t["Etki büyüklüğü r"] = w["p"], w["r"]
    return t
