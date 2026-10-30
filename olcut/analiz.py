"""
Sporcu analizi: Z profili kullanan branş grubu eşleştirmesi (Opstoel ve ark., 2015), ilgi anketi puanları ve
iki pencere, sporcu profili ve antrenman bilgisi, grup içi konum ve gelişim (Paket 36), rapor verisi.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import os
import pandas as pd
import re
from datetime import date
from veri.brans_profilleri import BILESIK_Z, BRANS_GRUBU_PROFILLERI
from veri.metinler import GUVEN_DUZEYLERI, ILGI_MADDELERI
from veri.normlar_kategorik import NORMATIF_TEST
from olcut.esik import NORMATIF_ESIK_YAS
from olcut.katalog_islemleri import kanonik_test, test_tablosu_duzelt
from olcut.norm import (
    META_KOLONLAR, NORMATIF_YAS, SPORCU_DOSYA, TEST_DOSYA, bilesik_z_hesapla, degisken_yonu, ktk3_toplamlari,
    sporcu_z_profili, yas_z_skoru)
from olcut.ortak import METIN_DEGISKEN_KALIBI, _girildi, _yas_degeri, guvenli_float, veri_yolu
from olcut.tema import BILESEN_CSS, YAZI_AILESI, b, palet, renk_css, sonuc_karti_html


def sporcu_fsc_profili(df_test, sporcu):
    """
    Sporcunun Opstoel (2015) değişkenlerine karşılık gelen ham değerleri.
    Her eşleşen test için EN SON kayıt kullanılır; boy/kilo sporcu profilinden gelir.
    Dönen: {"degerler": {kod: {"deger", "tarih", "kaynak"}}, "eksik": [kod], "eslesmeyen": [kod]}
    Paket 5'teki branş grubu eşleştirmesi bu fonksiyonun çıktısını kullanır.
    """
    tanim = BRANS_GRUBU_PROFILLERI["degiskenler"]
    sonuc = {"degerler": {}, "eksik": [], "eslesmeyen": [k for k, t in tanim.items() if not t["eslesme"]]}

    bilgi = {}
    if os.path.exists(veri_yolu(SPORCU_DOSYA)):
        df_sp = pd.read_excel(veri_yolu(SPORCU_DOSYA))
        esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
        if not esl.empty:
            bilgi = esl.iloc[0].to_dict()

    df_s = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" in df_s.columns:
        df_s = df_s.sort_values("Tarih_dt", na_position="first")

    for kod, t in tanim.items():
        e = t["eslesme"]
        if not e:
            continue
        if e["kaynak"] in ("profil", "profil_vki"):
            boy = guvenli_float(bilgi.get("Boy (cm)", 0)) if _girildi(bilgi.get("Boy (cm)")) else 0
            kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
            if e["kaynak"] == "profil":
                v = boy if e["alan"] == "Boy (cm)" else kilo
            else:
                v = round(kilo / (boy / 100) ** 2, 2) if boy > 0 and kilo > 0 else 0
            if v > 0:
                sonuc["degerler"][kod] = {"deger": v, "tarih": None, "kaynak": "Sporcu profili"}
            else:
                sonuc["eksik"].append(kod)
            continue

        son = None
        # Paket 38j: takma adlı kayıt da (kanonik_test) ve protokolü aynı ek testler de (ör. TSYT oturma yüksekliği)
        testler = {kanonik_test(x) for x in (e["test"], *e.get("ek_testler", ()))}
        for _, satir in df_s[df_s["Test"].map(kanonik_test).isin(testler)].iterrows():
            test_adi = kanonik_test(satir["Test"])
            vals = satir.to_dict()
            for k_t, v_t in ktk3_toplamlari(test_adi, vals).items():
                if not _girildi(vals.get(k_t)):
                    vals[k_t] = v_t
            sayilar = []
            for d in e["degiskenler"]:
                if _girildi(vals.get(d)):
                    try:
                        sayilar.append(float(vals.get(d)))
                    except (TypeError, ValueError):
                        pass
            if not sayilar:
                continue
            v = sayilar[0] if e["birlestir"] == "tek" else max(sayilar)
            test_yasi = vals.get("Test Yaşı")
            son = {"deger": v, "tarih": satir.get("Tarih", ""), "kaynak": test_adi,
                   "test_yasi": guvenli_float(test_yasi) if _girildi(test_yasi) else None}
        if son is None:
            sonuc["eksik"].append(kod)
        else:
            sonuc["degerler"][kod] = son
    return sonuc


ESLESTIRME_YAS_ARALIGI = (9, 11)


ESLESTIRME_EN_AZ_DEGISKEN = 6


ESLESTIRME_DEGISKENLERI = [k for k, t in BRANS_GRUBU_PROFILLERI["degiskenler"].items()
                           if t["tur"] != "antropometri" and t["eslesme"]]


def _havuz_sd(kod):
    """Altı grubun grup içi SD'lerinin n ağırlıklı havuzu."""
    gruplar = BRANS_GRUBU_PROFILLERI["gruplar"]
    pay = sum((gruplar[g]["n"] - 1) * BRANS_GRUBU_PROFILLERI["degerler"][g][kod][1] ** 2 for g in gruplar)
    payda = sum(gruplar[g]["n"] - 1 for g in gruplar)
    return (pay / payda) ** 0.5


ESLESTIRME_HAVUZ_SD = {k: round(_havuz_sd(k), 3) for k in ESLESTIRME_DEGISKENLERI}


# Yöntemin beklenen ayırt ediciliği (simülasyon, 6 × 3000 sanal çocuk): çocuklar
# kendi grubunun ortalama ve SD'sinden normal ve bağımsız dağılımla üretildi;
# 11 değişkenin tamamı kullanıldı. Değişkenler arası korelasyon bilinmediği için
# gerçek doğruluk farklı olabilir.
ESLESTIRME_SIMULASYON = {"ilk_sira": 29, "ilk_uc": 67, "sans_ilk": 17, "sans_ilk_uc": 50}


def brans_grubu_eslestir(fsc_profil, sporcu_yas):
    """
    Dönen: {"uygun": bool, "neden": str|None, "siralama": [(grup, uzaklik)],
            "kullanilan": [kod], "dislanan_yas": [kod], "katki": {grup: {kod: z}}}
    """
    sonuc = {"uygun": False, "neden": None, "siralama": [], "kullanilan": [],
             "dislanan_yas": [], "katki": {}}
    try:
        yas = float(sporcu_yas)
    except (TypeError, ValueError):
        sonuc["neden"] = "Sporcu profilinde yaş yok."
        return sonuc
    alt, ust = ESLESTIRME_YAS_ARALIGI
    if not (alt <= int(yas) <= ust):
        sonuc["neden"] = (f"Karşılaştırma yapılamaz: branş grubu profilleri {alt}-{ust} yaş çocuklardan "
                          f"elde edildi (Opstoel ve ark., 2015); sporcu {int(yas)} yaşında.")
        return sonuc

    degerler = {}
    for kod in ESLESTIRME_DEGISKENLERI:
        d = fsc_profil["degerler"].get(kod)
        if not d:
            continue
        ty = d.get("test_yasi")
        if ty is not None and not (alt <= int(ty) <= ust):
            sonuc["dislanan_yas"].append(kod)   # ölçüm 9-11 yaş dışında yapılmış
            continue
        degerler[kod] = d["deger"]
    sonuc["kullanilan"] = list(degerler)
    if len(degerler) < ESLESTIRME_EN_AZ_DEGISKEN:
        sonuc["neden"] = (f"Karşılaştırma için en az {ESLESTIRME_EN_AZ_DEGISKEN} performans testi gerekli; "
                          f"şu an {len(degerler)} test var.")
        return sonuc

    for grup, tablo in BRANS_GRUBU_PROFILLERI["degerler"].items():
        zler = {}
        for kod, x in degerler.items():
            ort = tablo[kod][0]
            z = (x - ort) / ESLESTIRME_HAVUZ_SD[kod]
            # Yön: + = gruptan iyi (düşük-iyi değişkenlerde işaret çevrilir); uzaklığı etkilemez
            if BRANS_GRUBU_PROFILLERI["degiskenler"][kod]["dusuk_iyi"]:
                z = -z
            zler[kod] = round(z, 2)
        uzaklik = (sum(z * z for z in zler.values()) / len(zler)) ** 0.5
        sonuc["siralama"].append((grup, round(uzaklik, 2)))
        sonuc["katki"][grup] = zler
    sonuc["siralama"].sort(key=lambda g: g[1])
    sonuc["uygun"] = True
    return sonuc


ILGI_DOSYA = "ilgi_anketi.xlsx"


ILGI_ANKET_ADI = "Uygulamanın kendi ilgi anketi (sürüm 2, 24 madde)"


ILGI_UYARI = ("Bu, uygulamanın kendi anketidir; Flaman Spor Pusulası'nın doğrulanmış I LIKE aracı "
              "değildir. Geçerlik ve güvenirlik çalışması henüz yapılmamıştır.")


ILGI_OLCEK = {1: "😢 Hiç sevmiyorum", 2: "🙁 Pek sevmiyorum", 3: "😐 Kararsızım",
              4: "🙂 Seviyorum", 5: "😄 Çok seviyorum", 0: "❔ Bilmiyorum / hiç yapmadım"}


ILGI_EN_AZ_MADDE = 2      # grup puanı için en az bu kadar madde yanıtlanmalı


ILGI_SEVIYOR_ESIGI = 3.5  # bu ve üstü "seviyor" penceresine girer


ILGI_TARANAN_SAYISI = 14   # özeti okunan hakemli kaynak (Opstoel 2015 hariç)


ILGI_TERCIHLERI = [
    ("T-TAKIM", "Takımla oynamak", "Tek başına yapmak"),
    ("T-YER", "İçeride (salonda)", "Dışarıda (açık havada)"),
    ("T-TEMAS", "Rakiple temaslı", "Rakibe dokunmadan"),
    ("T-MUZIK", "Müzikle", "Müziksiz"),
]


ILGI_HAKKINDA = (
    "**Bu anket hakkında**\n\n"
    "Bu anketin maddeleri bu uygulama için yazılmıştır; doğrulanmış bir ölçek değildir.\n\n"
    "Maddeler, Opstoel ve ark. (2015) tarafından tanımlanan altı branş grubunun hareket içeriği esas "
    f"alınarak, {ILGI_TARANAN_SAYISI} hakemli kaynağın taranmasıyla oluşturulan bir madde havuzundan "
    "seçilmiştir. Hazırlık yapay zeka desteğiyle yapılmış, araştırmacı tarafından gözden geçirilmiştir.\n\n"
    "Geçerlik ve güvenirlik çalışması henüz yapılmamıştır. Uygulama üzerinden toplanacak verilerle madde "
    "analizi, test–tekrar test güvenirliği ve anketin branş seçimiyle ilişkisi incelenecektir. Bu çalışma "
    "tamamlanana kadar anketin çıktıları bağlayıcı bir değerlendirme değil, yönlendirici bilgi olarak ele "
    "alınmalıdır.\n\n"
    "Çalışma Prof. Dr. Ömer Şenel ve Prof. Dr. Cengiz Akarçeşme danışmanlığında yürütülmektedir."
)


def ilgi_son_anket(sporcu):
    """Sporcunun en son ilgi anketi kaydı (sözlük) ya da None."""
    if not os.path.exists(veri_yolu(ILGI_DOSYA)):
        return None
    df_i = pd.read_excel(veri_yolu(ILGI_DOSYA))
    df_i = df_i[df_i["Sporcu"] == sporcu]
    if df_i.empty:
        return None
    df_i = df_i.assign(_t=pd.to_datetime(df_i["Tarih"], format="%d.%m.%Y", errors="coerce"))
    return df_i.sort_values("_t", na_position="first").iloc[-1].to_dict()


def ilgi_grup_puanlari(kayit):
    """Grup başına ilgi puanı (1-5) ya da bilinmiyorsa None. 0 = bilmiyorum, ortalamaya girmez."""
    puanlar = {}
    for grup, maddeler in ILGI_MADDELERI.items():
        yanitlar = []
        for kod, _, _ in maddeler:
            v = kayit.get(kod) if kayit else None
            try:
                v = int(float(v))
            except (TypeError, ValueError):
                continue
            if 1 <= v <= 5:
                yanitlar.append(v)
        puanlar[grup] = (round(sum(yanitlar) / len(yanitlar), 1)
                         if len(yanitlar) >= ILGI_EN_AZ_MADDE else None)
    return puanlar


def ilgi_etiketi(p):
    if p is None:
        return "Bilinmiyor"
    if p >= 4.5:
        return "Çok seviyor"
    if p >= 3.5:
        return "Seviyor"
    if p >= 2.5:
        return "Kararsız"
    return "Pek sevmiyor"


def ilgi_fiziksel_pencereler(esl, ilgi_puanlari):
    """
    İlgi ve fiziksel profil AYRI pencereler olarak döner; tek skor üretilmez (sabit karar 4).
    Dönen: {"seviyor": [grup], "fiziksel": [grup], "kesisim": [grup],
            "yalniz_ilgi": [grup], "yalniz_fiziksel": [grup], "bilinmeyen": [grup]}
    """
    seviyor = sorted(g for g, p in ilgi_puanlari.items() if p is not None and p >= ILGI_SEVIYOR_ESIGI)
    fiziksel = sorted(g for g, _ in esl["siralama"][:3]) if esl and esl.get("uygun") else []
    kesisim = sorted(set(seviyor) & set(fiziksel))
    return {
        "seviyor": seviyor, "fiziksel": fiziksel, "kesisim": kesisim,
        "yalniz_ilgi": sorted(set(seviyor) - set(fiziksel)),
        "yalniz_fiziksel": sorted(set(fiziksel) - set(seviyor)),
        "bilinmeyen": sorted(g for g, p in ilgi_puanlari.items() if p is None),
    }


ANTRENMAN_KOLON = "Haftalık Antrenman"


ANTRENMAN_TARIH_KOLON = "Antrenman Bilgisi Tarihi"


ANTRENMAN_SECENEKLERI = ["Bilinmiyor"] + list(GUVEN_DUZEYLERI.keys())


ANTRENMAN_YARDIM = ("Haftalık organize (kulüp/okul takımı) antrenman süresi. Branşa yönlendirmedeki güven düzeyi "
                    "yalnızca buna göre belirlenir (Opstoel ve ark., 2015).")


def sporcu_profil_bilgisi(sporcu):
    """sporcular.xlsx'teki satır (sözlük) ya da boş sözlük."""
    if not os.path.exists(veri_yolu(SPORCU_DOSYA)):
        return {}
    df_sp = pd.read_excel(veri_yolu(SPORCU_DOSYA))
    esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
    return esl.iloc[0].to_dict() if not esl.empty else {}


def sporcu_antrenman(bilgi):
    """(seçenek, kayıt tarihi metni) — kayıt yoksa ("Bilinmiyor", "")."""
    v = bilgi.get(ANTRENMAN_KOLON)
    v = str(v).strip() if _girildi(v) else "Bilinmiyor"
    if v not in ANTRENMAN_SECENEKLERI:
        v = "Bilinmiyor"
    t = bilgi.get(ANTRENMAN_TARIH_KOLON)
    return v, (str(t).strip() if _girildi(t) else "")


def sporcu_antrenman_kaydet(sporcu, secenek):
    """Profildeki haftalık antrenman süresini ve kayıt tarihini günceller. Başarılıysa True."""
    if not os.path.exists(veri_yolu(SPORCU_DOSYA)):
        return False
    df_sp = pd.read_excel(veri_yolu(SPORCU_DOSYA))
    maske = df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu
    if not maske.any():
        return False
    for kolon in (ANTRENMAN_KOLON, ANTRENMAN_TARIH_KOLON):
        if kolon not in df_sp.columns:
            df_sp[kolon] = ""
        df_sp[kolon] = df_sp[kolon].astype(object)
    df_sp.loc[maske, ANTRENMAN_KOLON] = secenek
    df_sp.loc[maske, ANTRENMAN_TARIH_KOLON] = date.today().strftime("%d.%m.%Y")
    df_sp.to_excel(veri_yolu(SPORCU_DOSYA), index=False)
    return True


# ── Branş grubu katmanı: hangi Opstoel değişkeni hangi norm tablosundan Z'ye çevrilir ──
def _grup_radar_norm_anahtari(kod):
    """(test, norm değişkeni) ya da (None, neden). Eşleştirme Paket 4 kuralıyla aynıdır."""
    t = BRANS_GRUBU_PROFILLERI["degiskenler"][kod]
    if t["tur"] == "antropometri":
        return None, "antropometrik — tanımlayıcı veri, performans radarına girmez"
    e = t["eslesme"]
    if not e:
        return None, "protokol eşleşmedi"
    anahtarlar = [f"{e['test']} › {d}" for d in e["degiskenler"] if f"{e['test']} › {d}" in NORMATIF_YAS]
    if not anahtarlar:
        return None, "yaş/cinsiyet normu yok"
    ilk = NORMATIF_YAS[anahtarlar[0]]["yaslar"]
    if any(NORMATIF_YAS[a]["yaslar"] != ilk for a in anahtarlar[1:]):
        return None, "denemelerin normları birbirinden farklı"
    return (e["test"], anahtarlar[0].split(" › ", 1)[1]), None


GRUP_RADAR_ESLESME = {k: _grup_radar_norm_anahtari(k) for k in BRANS_GRUBU_PROFILLERI["degiskenler"]}


GRUP_RENKLERI = palet("acik")["seri"]          # rapor radarı (kâğıt: açık palet); uygulama grafiği grafik_renk()


def grup_radar_katmani(df_test, sporcu, gruplar):
    """
    Radarın ortak eksenleri: sporcunun Z'si ve seçilen grupların Z'si aynı norm hücresinden.
    Dönen: {"uygun", "neden", "eksenler": [{kod, ad, test, degisken, yas, deger, z, persentil,
            durum, gruplar: {grup: {ort, z, persentil, durum}}}], "cikarilan": [(ad, neden)],
            "cinsiyet"}
    """
    tanim = BRANS_GRUBU_PROFILLERI["degiskenler"]
    sonuc = {"uygun": False, "neden": None, "eksenler": [], "cikarilan": [], "cinsiyet": ""}
    bilgi = sporcu_profil_bilgisi(sporcu)
    cins = str(bilgi.get("Cinsiyet", "")).strip()
    sonuc["cinsiyet"] = cins
    if cins not in ("Erkek", "Kadın"):
        sonuc["neden"] = "Sporcu profilinde cinsiyet yok."
        return sonuc
    alt, ust = ESLESTIRME_YAS_ARALIGI
    try:
        profil_yas = int(float(bilgi.get("Yaş")))
    except (TypeError, ValueError):
        profil_yas = None
    if profil_yas is not None and not (alt <= profil_yas <= ust):
        sonuc["neden"] = (f"branş grubu profilleri {alt}-{ust} yaş çocuklardan elde edildi (Opstoel ve ark., 2015); "
                          f"sporcu {profil_yas} yaşında.")
        return sonuc
    fsc = sporcu_fsc_profili(df_test, sporcu)
    for kod, (anahtar, neden) in GRUP_RADAR_ESLESME.items():
        ad = tanim[kod]["ad"]
        if tanim[kod]["tur"] == "antropometri":
            continue   # tek satırlık notla belirtilir
        if anahtar is None:
            sonuc["cikarilan"].append((ad, neden))
            continue
        d = fsc["degerler"].get(kod)
        if not d:
            sonuc["cikarilan"].append((ad, "sporcuda ölçüm yok"))
            continue
        yas = d.get("test_yasi")
        if yas is None and _girildi(bilgi.get("Yaş")):
            yas = guvenli_float(bilgi.get("Yaş"))
        if yas is None or not (alt <= int(yas) <= ust):
            sonuc["cikarilan"].append((ad, f"ölçüm {alt}-{ust} yaş dışında (grup profilleri {alt}-{ust} yaş)"))
            continue
        test, degisken = anahtar
        zs = yas_z_skoru(test, degisken, yas, cins, d["deger"])
        if not zs or zs["z_performans"] is None:
            sonuc["cikarilan"].append((ad, "sporcunun değeri Z'ye çevrilemedi"))
            continue
        gz_hepsi, cevrilemedi = {}, False
        for g in gruplar:
            ort = BRANS_GRUBU_PROFILLERI["degerler"][g][kod][0]
            gz = yas_z_skoru(test, degisken, yas, cins, ort)
            if not gz or gz["z_performans"] is None:
                cevrilemedi = True
                break
            gz_hepsi[g] = {"ort": ort, "z": gz["z_performans"], "persentil": gz["persentil_performans"], "durum": gz["durum"]}
        if cevrilemedi:
            sonuc["cikarilan"].append((ad, "grup ortalaması Z'ye çevrilemedi"))
            continue
        sonuc["eksenler"].append({"kod": kod, "ad": ad, "test": test, "degisken": degisken, "yas": int(yas),
                                  "deger": d["deger"], "z": zs["z_performans"], "persentil": zs["persentil_performans"],
                                  "durum": zs["durum"], "kullanilan_yas": zs["kullanilan_yas"],
                                  "gruplar": gz_hepsi})
    if len(sonuc["eksenler"]) < 3:
        sonuc["neden"] = (f"Grup katmanı için sporcuda ve grupta ortak, Z'ye çevrilebilen en az 3 değişken gerekli; "
                          f"şu an {len(sonuc['eksenler'])}.")
        return sonuc
    sonuc["uygun"] = True
    return sonuc


GRUP_KATMANI_NOTU = (
    "Grup çizgileri, Opstoel ve ark. (2015) grup ortalamasının sporcunun kendi norm hücresindeki (aynı test, "
    "aynı yaş, aynı cinsiyet) Z'sidir; yani \"o gruptaki ortalama bir çocuk bu sporcunun akranları arasında "
    "nerede durur\". Grup ortalamaları erkek-kız karışık olduğundan cinsiyet farkı düzeltilmemiştir. "
    "Ortalamanın Z'si, grup üyelerinin Z'lerinin ortalamasıyla aynı şey değildir.")


# Raporlar (veli/antrenör, yazdırılır, dosya olarak verilir) bağımsız belgedir: tema yok, her zaman açık palet.
_RAPOR_RENK = palet("acik")["renk"]


_RAPOR_VURGU = palet("acik")["vurgu"]


# ── Rapor için bağımsız SVG radar (internet ve ek paket gerektirmez) ──
def radar_svg(eksenler, katmanlar, aralik=(-3, 3)):
    """
    eksenler: [etiket]; katmanlar: [(ad, [z], renk, kesikli)] — z değerleri aralığa sınırlanır.
    Kendi başına SVG (internet ve ek paket gerektirmez); yazdırmada da aynı görünür.
    """
    import math
    n = len(eksenler)
    gen, yuk = 760, 600
    cx, cy = gen / 2, 285
    r_max = 205
    lo, hi = aralik

    def nokta(i, z, r_ek=0.0):
        z = max(lo, min(hi, z))
        r = (z - lo) / (hi - lo) * r_max + r_ek
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * math.cos(a), cy + r * math.sin(a)

    parcalar = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {gen} {yuk}" width="100%" '
                f'style="max-width:{gen}px" role="img" aria-label="Z profili radarı" '
                f'font-family=\'{YAZI_AILESI.replace(chr(34), "")}\'>']
    for z in range(lo, hi + 1):
        if z == lo:
            continue
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (nokta(i, z) for i in range(n)))
        stil = (f'stroke="{_RAPOR_RENK["ikincil"]}" stroke-width="2"' if z == 0
                else f'stroke="{_RAPOR_RENK["cizgi"]}" stroke-width="1"')
        parcalar.append(f'<polygon points="{pts}" fill="none" {stil}/>')
    for i in range(n):
        x, y = nokta(i, hi)
        parcalar.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{_RAPOR_RENK["cizgi"]}"/>')
    for ad, zler, renk, kesikli in katmanlar:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (nokta(i, z) for i, z in enumerate(zler)))
        dolgu = 'fill="none"' if kesikli else f'fill="{renk}" fill-opacity="0.13"'
        cizgi = ' stroke-dasharray="7 4"' if kesikli else ""
        parcalar.append(f'<polygon points="{pts}" {dolgu} stroke="{renk}" stroke-width="2.4"{cizgi}/>')
        if not kesikli:
            for i, z in enumerate(zler):
                x, y = nokta(i, z)
                parcalar.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.8" fill="{renk}"/>')
    # Ölçek etiketleri: ilk eksenin hemen sağında, beyaz zeminli
    for z in (-2, 0, 2):
        x, y = nokta(0, z)
        et = "0 = akran ort." if z == 0 else f"{z:+d}"
        parcalar.append(f'<text x="{x + 5:.1f}" y="{y + 4:.1f}" font-size="10.5" fill="{_RAPOR_RENK["ikincil"]}" '
                        f'stroke="{_RAPOR_RENK["yuzey"]}" stroke-width="3" paint-order="stroke">{et}</text>')
    for i, et in enumerate(eksenler):
        lx, ly = nokta(i, hi, r_ek=16)
        anchor = "middle" if abs(lx - cx) < 25 else ("start" if lx > cx else "end")
        satirlar, satir = [], ""
        for k in str(et).split():
            if satir and len(satir) + len(k) + 1 > 24:
                satirlar.append(satir)
                satir = k
            else:
                satir = f"{satir} {k}".strip()
        satirlar.append(satir)
        if ly < cy - r_max * 0.8:
            ly -= 12 * (len(satirlar) - 1)      # üstteki etiket yukarı doğru büyür
        elif abs(ly - cy) <= r_max * 0.8:
            ly -= 6 * (len(satirlar) - 1)       # yandaki etiket ortalanır
        for j, s_ in enumerate(satirlar):
            parcalar.append(f'<text x="{lx:.1f}" y="{ly + 4 + j * 13:.1f}" font-size="11.5" fill="{_RAPOR_RENK["murekkep"]}" '
                            f'text-anchor="{anchor}">{_html.escape(s_)}</text>')
    lx = 20
    for ad, _, renk, kesikli in katmanlar:
        cizgi = ' stroke-dasharray="7 4"' if kesikli else ""
        parcalar.append(f'<line x1="{lx}" y1="{yuk - 18}" x2="{lx + 28}" y2="{yuk - 18}" stroke="{renk}" '
                        f'stroke-width="3"{cizgi}/>')
        parcalar.append(f'<text x="{lx + 34}" y="{yuk - 14}" font-size="12" fill="{_RAPOR_RENK["murekkep"]}">{_html.escape(ad)}</text>')
        lx += 52 + 7 * len(ad)
    parcalar.append("</svg>")
    return "".join(parcalar)


# ── Rapor verisi ──
def _kisa_kaynak(kaynak):
    ilk = str(kaynak).split("\n")[0].strip()
    m = re.match(r"^(.*?\(\d{4}[a-z]?\))", ilk)
    return m.group(1) if m else ilk[:80]


def z_satiri_karti(r, zb, teknik=False, not_metni=None):
    """sporcu_z_profili satırını TEK sonuç kartına çevirir (Sonuçlar sayfası ve antrenör raporu)."""
    norm = NORMATIF_YAS.get(f"{r['Test']} › {r['Değişken']}", {})
    notr = r["Tür"] != "Performans"
    kaynak = _kisa_kaynak(zb.get("kaynak", "")) + (f" · {zb['tablo']}" if zb.get("tablo") else "")
    kaynak += f" · {r['Norm yaşı']} yaş normu · ölçüm {r['Tarih']}"
    ek = ""
    if teknik:
        z_m = f"Z {r['Z']:+.2f}" + (" (nötr)" if notr else "") if r.get("Z") is not None else "Z —"
        ham = zb.get("persentil")
        ek = z_m + (f" · ham persentil P{ham:.0f}" if ham is not None else "")
        if not_metni:
            not_metni = re.sub(r" \(Z [+\-−]?\d+\.\d+\)", "", not_metni)   # Z zaten teknik satırda
    return sonuc_karti_html(f"{r['Test']} — {r['Değişken']}", r["Değer"], norm.get("birim", ""),
                            r.get("Kategori") or None, notr=notr, persentil=r.get("Performans persentili"),
                            kaynak=kaynak, notlar=[not_metni if not_metni is not None else r.get("Not", "")],
                            ek=ek)


def _brans_ornekleri(grup):
    """Opstoel grubundaki branşlar, sayılar çıkarılarak (ör. 'basketbol, korfbol, futbol, voleybol')."""
    adlar = re.sub(r"\s*\(\d+\)", "", BRANS_GRUBU_PROFILLERI["gruplar"][grup]["branslar"]).split(", ")
    return ", ".join(a for a in adlar if not a.startswith("diğer"))


GRUP_KONUM_YUZDELIK_N = 20          # n ≥ 20: yüzdelik gösterilebilir


GRUP_KONUM_BANT_YIL = 2             # yaş bandı genişliği (yıl)


KENDI_DEGISIM_YASI = 16             # bu yaşın altında pencerenin varsayılan görünümü "Kendi değişimin"


VELI_KONUM_EN_AZ_YAS = 11           # veli raporunda konum bölümü: yaş ≥ 11 ve n ≥ GRUP_KONUM_YUZDELIK_N


VELI_KONUM_METNI = ("Bu değer aynı yaş bandı ve cinsiyetteki n={n} çocuğun ölçümleriyle karşılaştırılmıştır; gelişim "
                    "hızı bireyler arasında farklıdır, tek ölçüm sporcu yeteneğini belirlemez.")


KONUM_YETERSIZ_METNI = "Yeterli karşılaştırma verisi yok."


# Paket 37: veli raporunda çeyrek/yüzdelik/sıra dili yok. Havuzun P10–P90 aralığı ("çocukların çoğu", ~%80'i) ve
# çocuğun bu aralığa göre yeri anlatılır. P10/P90: sıralı değerlerde doğrusal ara değer (numpy "linear" ile aynı).
VELI_ARALIK_YUZDELIK = (10, 90)


# Paket 38b: özne cinsiyetli ("Bu yaştaki erkek çocukların çoğu …"); yetişkinde "sporcuların". Yer cümlesi kısa;
# altında her zaman aynı not (aralık dışı bir sorun değildir).
VELI_ARALIK_METNI = "Bu yaştaki {kim} çoğu {a}–{b} {birim} arasında."


VELI_ARALIK_KIM = {("Erkek", False): "erkek çocukların", ("Kadın", False): "kız çocukların",
                   ("Erkek", True): "erkek sporcuların", ("Kadın", True): "kadın sporcuların"}


VELI_ARALIK_YERI = {"icinde": "{ad} bu aralığın içinde.",
                    "altinda": "{ad} bu aralığın biraz altında.",
                    "ustunde": "{ad} bu aralığın biraz üstünde.",
                    "altinda_belirgin": "{ad} bu aralığın belirgin şekilde altında.",
                    "ustunde_belirgin": "{ad} bu aralığın belirgin şekilde üstünde.",
                    "altinda_cok": "{ad} bu aralığın çok altında.",
                    "ustunde_cok": "{ad} bu aralığın çok üstünde."}


# Paket 38f: sapmanın büyüklüğü. P10–P90 normal dağılımda ±1,2816 SD'dir; bant genişliğinden SD tahmin edilir ve
# değerin yaklaşık z'si bulunur. |z| > 1,96 (dışarıda kalan ~%5) "belirgin şekilde"; |z| > 3 (~%0,3) "çok" ve
# "Değer doğru mu?" uyarısı (yargı değil, ölçüm/kayıt denetimi çağrısı).
VELI_SAPMA_Z = (1.96, 3.0)


VELI_DOGRU_MU_BASLIK = "Değer doğru mu?"


VELI_DOGRU_MU = ("Bu sonuç aralıktan çok uzak; ölçüm ya da kayıt hatası olabilir. Değeri antrenörle birlikte "
                 "kontrol edin.")


VELI_ARALIK_NOTU ="Aralığın dışında olmak bir sorun anlamına gelmez."


VELI_YASIT_BASLIK = "Yaşıtlarına göre nerede?"


YETISKIN_YAS = 18                    # bu yaştan itibaren veli raporu "Çocuğunuz…" yerine "Sporcu…" der


# Yetişkin sporcuda hitap: "Çocuğunuzun …" → "Sporcunun …" (yalnız hitap biçimleri; araştırma tanımı değişmez)
VELI_YETISKIN_HITAP = (("Çocuğunuzun", "Sporcunun"), ("çocuğunuzun", "sporcunun"), ("Çocuğunuzla", "Sporcuyla"),
                       ("çocuğunuzla", "sporcuyla"), ("Çocuğunuzu", "Sporcuyu"), ("çocuğunuzu", "sporcuyu"),
                       ("Çocuğunuza", "Sporcuya"), ("çocuğunuza", "sporcuya"), ("Çocuğunuz", "Sporcu"),
                       ("çocuğunuz", "sporcu"), ("çocuğun ölçümleriyle", "sporcunun ölçümleriyle"))


# Paket 38f: yetişkinde raporun kendi cümleleri (çocuk/büyüme dili). Araştırma tanımları ("9-11 yaş çocuklar",
# "620 çocukla") değişmez.
VELI_YETISKIN_IFADE = (
    ("aynı yaş ve cinsiyetteki çocuklar için", "aynı yaş ve cinsiyetteki sporcular için"),
    ("Koyu bant çocukların çoğunun", "Koyu bant sporcuların çoğunun"),
    ("hangi spor gruplarındaki çocuklara benzediğini", "hangi spor gruplarına benzediğini"),
    ("Bu yaşta fiziksel özellikler antrenmanla ve büyümeyle hızla değişir", "Fiziksel özellikler antrenmanla değişir"),
    ("Bu yaşta birden fazla sporu denemek önerilir.", "Birden fazla sporu denemek önerilir."),
)


def yetiskin_mi(bilgi):
    """Profil yaşı ≥ YETISKIN_YAS ise True (veli raporunda hitap 'Sporcu…')."""
    y = _yas_degeri((bilgi or {}).get("Yaş"))
    return y is not None and y >= YETISKIN_YAS


def veli_hitabi(metin, yetiskin):
    """Yetişkin sporcuda 'Çocuğunuz…' hitabını 'Sporcu…' yapar; çocukta metin aynen kalır."""
    if not yetiskin:
        return metin
    for eski, yeni in VELI_YETISKIN_HITAP + VELI_YETISKIN_IFADE:
        metin = metin.replace(eski, yeni)
    return metin


def _dogrusal_yuzdelik(sirali, p):
    """Sıralı değerlerin p. yüzdelik değeri — doğrusal ara değer (numpy.percentile varsayılanı)."""
    if not sirali:
        return None
    h = (len(sirali) - 1) * p / 100
    a = int(h)
    return sirali[a] + (sirali[min(a + 1, len(sirali) - 1)] - sirali[a]) * (h - a)


def _konum_sayi(x):
    """Ekran ve rapor sayısı: en çok 2 ondalık, Türkçe virgül (4.1 → "4,1", -0.2 → "-0,2")."""
    return f"{round(float(x), 2):g}".replace(".", ",")


# Paket 38a: parantez içi YALNIZ bilinen birimse birim sayılır; "(1 dk)", "(30 sn)" gibi süre belirten parantezler
# başlığa aittir (birim boş). Sayım değişkenlerinde kısa sözcük: "Düşme Sayısı" → "düşme", "Tekrar" → "tekrar".
BILINEN_BIRIMLER = frozenset({"cm", "kg", "sn", "dk", "kg/kg", "%", "W", "m", "m/sn", "bpm", "tekrar", "adet",
                              "m/s", "ms", "W/kg", "N/kg", "ml/kg/min", "km/sa", "N", "Nm"})


SAYIM_BIRIMLERI = (("düşme", "düşme"), ("tekrar", "tekrar"), ("atış", "atış"))


def _birim(degisken, test=None):
    """Birim: test verilirse önce normun kendi 'birim' alanı; yoksa değişken adındaki bilinen birim ya da sayım sözcüğü."""
    if test is not None:
        anahtar = f"{kanonik_test(test)} › {degisken}"
        for sozluk in (NORMATIF_YAS, NORMATIF_TEST, NORMATIF_ESIK_YAS):
            b_ = str((sozluk.get(anahtar) or {}).get("birim", "") or "").strip()
            if b_:
                return b_
    m = re.search(r"\(([^()]*)\)\s*$", str(degisken))
    if m and m.group(1).strip() in BILINEN_BIRIMLER:
        return m.group(1).strip()
    ad = str(degisken).lower()
    for anahtar, birim in SAYIM_BIRIMLERI:
        if anahtar in ad:
            return birim
    return ""


def _olcum_satirlari(df_test, test, degisken):
    """(Sporcu, tarih, değer, test yaşı) — kanonik test adıyla; sayısal olmayan değer atılır."""
    if df_test is None or df_test.empty or degisken not in df_test.columns:
        return pd.DataFrame(columns=["Sporcu", "Tarih_dt", "Deger", "Test Yaşı"])
    d = df_test[df_test["Test"].map(kanonik_test) == kanonik_test(test)].copy()
    d["Deger"] = pd.to_numeric(d[degisken], errors="coerce")
    if "Tarih_dt" not in d.columns:
        d["Tarih_dt"] = pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce")
    if "Test Yaşı" not in d.columns:
        d["Test Yaşı"] = None
    return d.dropna(subset=["Deger"]).sort_values("Tarih_dt")[["Sporcu", "Tarih_dt", "Deger", "Test Yaşı"]]


def gelisim_ozeti(df_test, sporcu, test, degisken):
    """
    Aynı sporcunun aynı testteki ölçümleri (zaman sırası) ve son ölçümün öncekine göre farkı (mutlak, %).
    iyi_yonde: yön biliniyorsa True/False (süre testlerinde azalma iyi), değilse None. Tek ölçüm: ilk=True.
    """
    d = _olcum_satirlari(df_test, test, degisken)
    d = d[d["Sporcu"] == sporcu]
    olc = [(t.strftime("%d.%m.%Y") if pd.notna(t) else "", float(v)) for t, v in zip(d["Tarih_dt"], d["Deger"])]
    o = {"test": kanonik_test(test), "degisken": degisken, "birim": _birim(degisken, test), "olcumler": olc,
         "yon": degisken_yonu(test, degisken), "ilk": len(olc) == 1, "fark": None, "yuzde": None, "iyi_yonde": None}
    if len(olc) >= 2:
        onceki, son = olc[-2][1], olc[-1][1]
        o["fark"] = round(son - onceki, 2)
        o["yuzde"] = round((son - onceki) / abs(onceki) * 100, 1) if onceki else None
        if o["yon"] is not None and o["fark"] != 0:
            o["iyi_yonde"] = (o["fark"] < 0) if o["yon"] else (o["fark"] > 0)
    return o


# Paket 38c: veli/antrenör "Kendi gelişimi" test başına çalışır. Bir testin ANA SONUCU: "En İyi" değişkeni; yoksa
# deneme değişkenlerinin kayıt içindeki en iyisi (yön tanımına göre); yoksa tek değişken. Bunların hiçbiri yoksa test
# ÇOK BİLEŞENLİDİR (ör. NHT sağ/sol kuvvet): veli raporunda tek satır özet, ham bileşenler antrenör raporunda.
# Neden: değişken başına çalışınca, ikinci oturumda yalnız Deneme 1 girilen bir testin Deneme 2'si "ilk ölçüm"
# tablosunda eski değeriyle kalıyordu (aynı test raporda iki farklı değerle).
_DENEME_KALIBI = re.compile(r"(^|— )Deneme \d")


def ana_sonuc_tanimi(test, degiskenler):
    """("eniyi", d) | ("deneme", [d…]) | ("tek", d) | None (çok bileşenli). Rölatif değer (kayıtlı kilodan
    hesaplanan) başka değişken varken bileşen sayılmaz: "1RM Squat (kg)" + "Rölatif Squat (kg/kg)" → tek."""
    ds = [d for d in degiskenler if not str(d).startswith("Rölatif")] or list(degiskenler)
    en_iyi = [d for d in ds if "En İyi" in d]
    if en_iyi:
        return ("eniyi", en_iyi[0])
    deneme = [d for d in ds if _DENEME_KALIBI.search(d)]
    if deneme and len(deneme) == len(ds):
        return ("deneme", deneme)
    if len(ds) == 1:
        return ("tek", ds[0])
    return None


def _sonuc_degiskenleri(g):
    return [c for c in g.columns if c not in META_KOLONLAR and not METIN_DEGISKEN_KALIBI.search(str(c))
            and pd.to_numeric(g[c], errors="coerce").notna().any()]


def test_sonuc_serisi(g, test):
    """
    Tek testin kayıtları (aynı sporcu) → ana sonuç serisi {test, degisken, birim, olcumler, yon, ilk, fark, yuzde,
    iyi_yonde, tur}; çok bileşenliyse {"tur": "bilesik", test, degiskenler, son_tarih, olcum_sayisi}.
    Aynı gün iki kayıt varsa son kayıt sayılır.
    """
    g = g.sort_values("Tarih_dt") if "Tarih_dt" in g.columns else g
    ds = _sonuc_degiskenleri(g)
    tanim = ana_sonuc_tanimi(test, ds)
    tarihler = [t.strftime("%d.%m.%Y") if pd.notna(t) else str(s) for t, s in
                zip(g.get("Tarih_dt", pd.Series([pd.NaT] * len(g))), g["Tarih"])]
    if tanim is None:
        dolu = [tr for tr, (_, r) in zip(tarihler, g.iterrows()) if any(_girildi(r.get(d)) for d in ds)]
        return {"tur": "bilesik", "test": kanonik_test(test), "degiskenler": ds,
                "son_tarih": dolu[-1] if dolu else "", "olcum_sayisi": len(dict.fromkeys(dolu))}
    tur, d = tanim
    yon = degisken_yonu(test, d if tur != "deneme" else d[0])
    olc = {}
    for tr, (_, r) in zip(tarihler, g.iterrows()):
        if tur == "deneme":
            vs = [float(x) for x in pd.to_numeric(pd.Series([r.get(x) for x in d]), errors="coerce").dropna()]
            if not vs:
                continue
            v = min(vs) if yon is True else max(vs)
        else:
            v = pd.to_numeric(pd.Series([r.get(d)]), errors="coerce").iloc[0]
            if pd.isna(v):
                continue
            v = float(v)
        olc[tr] = v                                         # aynı gün: son kayıt
    birim_kaynagi = d[0] if tur == "deneme" else d
    etiket = (f"En iyi deneme ({_birim(birim_kaynagi)})" if _birim(birim_kaynagi) else "En iyi deneme") \
        if tur == "deneme" else d
    liste = list(olc.items())
    o = {"tur": tur, "test": kanonik_test(test), "degisken": etiket, "birim": _birim(birim_kaynagi, test),
         "olcumler": liste, "yon": yon, "ilk": len(liste) == 1, "fark": None, "yuzde": None, "iyi_yonde": None}
    if len(liste) >= 2:
        onceki, son = liste[-2][1], liste[-1][1]
        o["fark"] = round(son - onceki, 2)
        o["yuzde"] = round((son - onceki) / abs(onceki) * 100, 1) if onceki else None
        if yon is not None and o["fark"] != 0:
            o["iyi_yonde"] = (o["fark"] < 0) if yon else (o["fark"] > 0)
    return o


def test_gelisim_ozetleri(df_test, sporcu):
    """Sporcunun her testi için test_sonuc_serisi (ana sonuçlu ve çok bileşenli olanlar ayrı 'tur' ile)."""
    if df_test is None or df_test.empty:
        return []
    d = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" not in d.columns:
        d = d.assign(Tarih_dt=pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce"))
    sonuc = []
    for test, g in d.groupby(d["Test"].map(kanonik_test), sort=True):
        s = test_sonuc_serisi(g, test)
        if s.get("tur") == "bilesik" and not s["degiskenler"]:
            continue
        if s.get("tur") != "bilesik" and not s["olcumler"]:
            continue
        sonuc.append(s)
    return sonuc


def _profil_haritasi(df_sp):
    if df_sp is None or df_sp.empty or not {"Ad", "Soyad"} <= set(df_sp.columns):
        return {}
    return {f"{a} {s}": r for (a, s), r in zip(zip(df_sp["Ad"].astype(str), df_sp["Soyad"].astype(str)),
                                                  df_sp.to_dict("records"))}


def grup_ici_konum(df_test, df_sp, sporcu, test, degisken):
    """
    Sporcunun son ölçümünün, aynı testi yapan aynı cinsiyet ve aynı 2 yıllık yaş bandındaki sporcuların SON
    ölçümleri arasındaki yeri. Her sporcu havuzda bir kez; sporcunun kendisi havuzda (vurgulanır). Havuz yalnız
    kendisiyse durum "yetersiz". n ≥ GRUP_KONUM_YUZDELIK_N ise performans yönünde yüzdelik ve çeyrek bandı.
    """
    prof = _profil_haritasi(df_sp)
    d = _olcum_satirlari(df_test, test, degisken)
    yetersiz = {"durum": "yetersiz", "n": 0, "metin": KONUM_YETERSIZ_METNI, "degisken": degisken,
                "test": kanonik_test(test), "birim": _birim(degisken, test)}
    kendi = d[d["Sporcu"] == sporcu]
    cins = str(prof.get(sporcu, {}).get("Cinsiyet", "")).strip()
    if kendi.empty or cins not in ("Erkek", "Kadın"):
        return yetersiz
    son = kendi.iloc[-1]
    yas = _yas_degeri(son["Test Yaşı"]) or _yas_degeri(prof.get(sporcu, {}).get("Yaş"))
    if yas is None:
        return yetersiz
    bas = int(yas) // GRUP_KONUM_BANT_YIL * GRUP_KONUM_BANT_YIL
    bant = (bas, bas + GRUP_KONUM_BANT_YIL - 1)
    havuz = {}
    for _, r in d.iterrows():
        p = prof.get(r["Sporcu"], {})
        y = _yas_degeri(r["Test Yaşı"]) or _yas_degeri(p.get("Yaş"))
        if str(p.get("Cinsiyet", "")).strip() != cins or y is None or not bant[0] <= int(y) <= bant[1]:
            continue
        havuz[r["Sporcu"]] = float(r["Deger"])                    # tarih sırasıyla: son ölçüm kalır
    if sporcu not in havuz or len(havuz) < 2:
        return {**yetersiz, "n": len(havuz), "cinsiyet": cins, "bant": bant}
    deger, degerler = havuz[sporcu], sorted(havuz.values())
    ort = sum(degerler) / len(degerler)
    yon = degisken_yonu(test, degisken)
    k = {"durum": "tamam", "n": len(degerler), "deger": deger, "ortalama": round(ort, 2), "degerler": degerler,
         "cinsiyet": cins, "bant": bant, "yas": yas, "yon": yon, "test": kanonik_test(test), "degisken": degisken,
         "birim": _birim(degisken, test), "taraf": ("üstü" if deger > ort else "altı" if deger < ort else "ortası"),
         "yuzdelik": None, "ceyrek": None,
         "p10": _dogrusal_yuzdelik(degerler, VELI_ARALIK_YUZDELIK[0]),          # Paket 37: veli aralığı
         "p90": _dogrusal_yuzdelik(degerler, VELI_ARALIK_YUZDELIK[1])}
    if k["n"] >= GRUP_KONUM_YUZDELIK_N and yon is not None:
        digerleri = list(degerler)
        digerleri.remove(deger)
        iyi = lambda a, b: (a < b) if yon else (a > b)
        alt = sum(1 for x in digerleri if iyi(deger, x)) + 0.5 * sum(1 for x in digerleri if x == deger)
        k["yuzdelik"] = round(alt / len(digerleri) * 100)
        k["ceyrek"] = ("grubun alt çeyreği" if k["yuzdelik"] < 25 else
                       "grubun üst çeyreği" if k["yuzdelik"] > 75 else "grubun orta yarısı")
    return k


def konum_metinleri(k):
    """Pencere ve antrenör raporu metni. n < 20: yüzdelik/sıralama sözcüğü YOK (yalnız ortalamanın altı/üstü)."""
    if k.get("durum") != "tamam":
        return [f"n = {k.get('n', 0)}", KONUM_YETERSIZ_METNI]
    b = k["birim"]
    m = [f"n = {k['n']}",
         f"Havuz: {k['cinsiyet'].lower()}, {k['bant'][0]}-{k['bant'][1]} yaş, {k['test']} — {k['degisken']}",
         f"Değer {_konum_sayi(k['deger'])} {b} · grup ortalaması {_konum_sayi(k['ortalama'])} {b} · ortalamanın {k['taraf']}"]
    if k["yon"] is True:
        m.append("Bu testte düşük değer daha iyidir.")
    elif k["yon"] is None:
        m.append("Bu ölçümün iyi yönü tanımlı değil (tanımlayıcı ölçü).")
    if k.get("yuzdelik") is not None:
        m.append(f"Grup içi yüzdelik ≈ {k['yuzdelik']} ({k['ceyrek']}).")
    return m


def konum_seridi_svg(k, renk=None):
    """
    Konum şeridi: havuzdaki değerler (isimsiz noktalar), ortalama çizgisi, sporcunun değeri vurgulu. renk: {ad: renk}
    (uygulamada renk_css, raporda açık paletin düz tonları — saydam renk yok).
    """
    if k.get("durum") != "tamam":
        return ""
    r = renk or {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}
    en, en_b = min(k["degerler"]), max(k["degerler"])
    aralik = (en_b - en) or 1.0
    x = lambda v: 12 + (v - en) / aralik * 296
    p = [f'<svg viewBox="0 0 320 40" width="320" height="40" role="img" aria-label="Konum şeridi">',
         f'<line x1="12" y1="22" x2="308" y2="22" stroke="{r["cizgi"]}" stroke-width="2"/>']
    p += [f'<circle cx="{x(v):.1f}" cy="22" r="3" fill="{r["ikincil"]}"/>' for v in k["degerler"]]
    p.append(f'<line x1="{x(k["ortalama"]):.1f}" y1="12" x2="{x(k["ortalama"]):.1f}" y2="32" stroke="{r["murekkep"]}" '
             f'stroke-width="1.5"/>')
    p.append(f'<circle cx="{x(k["deger"]):.1f}" cy="22" r="6" fill="{r["ana"]}"/></svg>')
    return "".join(p)


def rapor_konum_degiskenleri(df_test, sporcu):
    """Sporcunun testleri × sonuç değişkenleri (sayısal). Testte "En İyi" türü hesaplanan değişken varsa yalnız o."""
    if df_test is None or df_test.empty:
        return []
    d = df_test[df_test["Sporcu"] == sporcu]
    cift = []
    for test, g in d.groupby(d["Test"].map(kanonik_test)):
        sayisal = [c for c in g.columns if c not in META_KOLONLAR and pd.to_numeric(g[c], errors="coerce").notna().any()]
        en_iyi = [c for c in sayisal if "En İyi" in c]
        cift += [(test, c) for c in (en_iyi or sayisal)]
    return cift


def rapor_verisi(sporcu):
    """Veli ve antrenör raporunun ortak verisi. Test kaydı olmayan sporcu için de çalışır."""
    bilgi = sporcu_profil_bilgisi(sporcu)
    if os.path.exists(veri_yolu(TEST_DOSYA)):
        df_test = test_tablosu_duzelt(pd.read_excel(veri_yolu(TEST_DOSYA)))
    else:
        df_test = pd.DataFrame(columns=["Sporcu", "Test", "Tarih"])
    df_test["Tarih_dt"] = pd.to_datetime(df_test["Tarih"], format="%d.%m.%Y", errors="coerce")
    df_s = df_test[df_test["Sporcu"] == sporcu]

    zp = sporcu_z_profili(df_test, sporcu)
    fsc = sporcu_fsc_profili(df_test, sporcu)
    esl = brans_grubu_eslestir(fsc, bilgi.get("Yaş"))
    ilgi = ilgi_son_anket(sporcu)
    puan = ilgi_grup_puanlari(ilgi) if ilgi else {}
    pen = ilgi_fiziksel_pencereler(esl, puan) if ilgi else None
    hacim, hacim_tarih = sporcu_antrenman(bilgi)
    fiziksel_uc = sorted(g for g, _ in esl["siralama"][:3]) if esl["uygun"] else []
    katman = grup_radar_katmani(df_test, sporcu, fiziksel_uc) if fiziksel_uc else None
    bilesikler = {ad: bilesik_z_hesapla(ad, zp["z_sozlugu"]) for ad in BILESIK_Z} if not zp["hata"] else {}

    # Kayıtlı testler: son tarih ve ölçüm sayısı
    testler = []
    for test_adi, grp in df_s.groupby("Test"):
        t_son = grp["Tarih_dt"].max()
        testler.append({"Test": test_adi, "Ölçüm sayısı": len(grp),
                        "Son ölçüm": t_son.strftime("%d.%m.%Y") if pd.notna(t_son) else str(grp["Tarih"].iloc[-1])})
    normlu_testler = {r["Test"] for r in zp["satirlar"]}
    normsuz = sorted(t["Test"] for t in testler if t["Test"] not in normlu_testler)
    tarihler = df_s["Tarih_dt"].dropna()
    tarih_araligi = ((tarihler.min().strftime("%d.%m.%Y"), tarihler.max().strftime("%d.%m.%Y"))
                     if not tarihler.empty else None)

    # Sınır durumları (antrenör raporu)
    sinirlar = []
    cins = str(bilgi.get("Cinsiyet", "")).strip()
    for (test_z, degisken_z), zbilgi in zp["z_sozlugu"].items():
        etiket = f"{test_z} — {degisken_z}"
        if zbilgi.get("durum") in ("alt_sinir", "ust_sinir", "esit_bant"):
            z_s = zbilgi.get("z_performans")
            ek = f" (Z {z_s:+.2f})" if z_s is not None and zbilgi.get("durum") != "esit_bant" else ""
            sinirlar.append((etiket, zbilgi.get("durum_notu", "") + ek))
        if zbilgi.get("yas_notu"):
            sinirlar.append((etiket, str(zbilgi["yas_notu"]).replace("⚠️ ", "")
                             + " (yaş aralığı dışı norm kullanımı)"))
        elif zbilgi.get("yas") is not None and zbilgi.get("kullanilan_yas") is not None \
                and int(zbilgi["yas"]) != int(zbilgi["kullanilan_yas"]):
            sinirlar.append((etiket, f"{int(zbilgi['yas'])} yaş için norm satırı yok — en yakın "
                                     f"{zbilgi['kullanilan_yas']} yaş normu kullanıldı"))
        if zbilgi.get("ceyrek_notu") and "ortalama" in zbilgi["ceyrek_notu"]:
            sinirlar.append((etiket, zbilgi["ceyrek_notu"]))
        if not zbilgi.get("cins_norm_var", True):
            sinirlar.append((etiket, f"{cins} normu yok — erkek normu kullanıldı"))
    for ad_b, bz in bilesikler.items():
        for n_b in bz.get("notlar", []):
            sinirlar.append((ad_b, n_b + " Testin kendi Z'si tabloda ve radarda duruyor."))
    if zp["eski_yas"]:
        sinirlar.append(("Eski kayıtlar", "Test günündeki yaş kaydedilmemiş; profildeki güncel yaş kullanıldı."))
    for kod in esl.get("dislanan_yas", []):
        sinirlar.append((BRANS_GRUBU_PROFILLERI["degiskenler"][kod]["ad"],
                         "9-11 yaş dışında ölçüldüğü için branş eşleştirmesine girmedi"))

    kaynaklar = sorted({str(z.get("kaynak", "")).split("\n")[0].strip()
                        for z in zp["z_sozlugu"].values() if z.get("kaynak")})
    # Paket 36: kendi gelişimi ve grup içi konum (başka sporcuların adı veride tutulmaz)
    df_sp_r = pd.read_excel(veri_yolu(SPORCU_DOSYA)) if os.path.exists(veri_yolu(SPORCU_DOSYA)) else pd.DataFrame()
    ciftler = rapor_konum_degiskenleri(df_test, sporcu)
    gelisim = [gelisim_ozeti(df_test, sporcu, t, d_) for t, d_ in ciftler]
    konum = [grup_ici_konum(df_test, df_sp_r, sporcu, t, d_) for t, d_ in ciftler]
    gelisim_test = test_gelisim_ozetleri(df_test, sporcu)                 # Paket 38c: test başına
    return {"sporcu": sporcu, "bilgi": bilgi, "zp": zp, "fsc": fsc, "esl": esl, "ilgi": ilgi, "puan": puan,
            "pen": pen, "hacim": hacim, "hacim_tarih": hacim_tarih, "fiziksel_uc": fiziksel_uc,
            "katman": katman, "bilesikler": bilesikler, "testler": testler, "normsuz": normsuz,
            "tarih_araligi": tarih_araligi, "sinirlar": sinirlar, "kaynaklar": kaynaklar,
            "gelisim": gelisim, "gelisim_test": gelisim_test, "konum": konum, "rapor_tarihi": date.today().strftime("%d.%m.%Y")}


RAPOR_CSS = f"""
<style>
  :root {{ --ink:{_RAPOR_RENK["murekkep"]}; --muted:{_RAPOR_RENK["ikincil"]}; --line:{_RAPOR_RENK["cizgi"]}; --soft:{_RAPOR_RENK["zemin"]};
          --accent:{_RAPOR_RENK["ana"]}; --love:{_RAPOR_VURGU["sevgi"]}; --phys:{_RAPOR_VURGU["fiziksel"]};
          --star:{_RAPOR_VURGU["yildiz"]}; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: {YAZI_AILESI};
         color: var(--ink); background:{_RAPOR_RENK["yuzey"]}; margin:0; padding:24px; line-height:1.5; font-size:14px; }}
  .sayfa {{ max-width: 820px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  h2 {{ font-size: 16px; margin: 26px 0 8px; padding-bottom:4px; border-bottom: 2px solid var(--line); }}
  h3 {{ font-size: 14px; margin: 14px 0 6px; }}
  .alt {{ color: var(--muted); font-size: 12.5px; }}
  .iki {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  .kutu {{ border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; background: var(--soft); }}
  .kutu.sev {{ border-top: 4px solid var(--love); }}
  .kutu.fiz {{ border-top: 4px solid var(--phys); }}
  .kutu ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .kesisim {{ border: 2px solid var(--star); background: {_RAPOR_VURGU["yildiz_zemin"]}; border-radius: 10px; padding: 12px 14px; margin-top: 12px; }}
  .not {{ border-left: 4px solid var(--accent); background: {_RAPOR_VURGU["not_zemin"]}; padding: 10px 12px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
  .uyari {{ border-left: 4px solid {_RAPOR_VURGU["uyari"]}; background: {_RAPOR_VURGU["uyari_zemin"]}; padding: 10px 12px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
  .tablo {{ overflow-x: auto; margin: 6px 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12.5px; }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 5px 6px; text-align: left; vertical-align: top; }}
  th {{ background: var(--soft); font-weight: 600; }}
  td.sayi {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .yildiz {{ color: var(--star); font-weight: 700; }}
  .radar {{ text-align: center; margin: 8px 0; }}
  .kucuk {{ font-size: 11.5px; color: var(--muted); }}
  body.veli {{ border-top: {b(0.75)} solid var(--accent); }}
  .veli-grup {{ display: flex; align-items: center; gap: {b(1)}; margin-top: {b(3)}; }}
  .kutu .veli-grup {{ margin-top: {b(0.75)}; }}
  .veli-satir {{ display: grid; grid-template-columns: 300px 1fr; gap: {b(2)}; align-items: center; margin: 0 0 {b(1.5)}; }}
  .veli-satir .sp-kart {{ margin: 0; }}
  .veli-yorum {{ margin: 0; }}
  .veli-aralik {{ border: 1px solid {_RAPOR_RENK["cizgi"]}; border-radius: 10px; padding: 10px 14px; margin: 0 0 {b(1.5)};
                 break-inside: avoid; }}
  .veli-aralik h4 {{ margin: 0 0 2px; font-size: 15px; }}
  .veli-aralik p {{ margin: 4px 0; }}
  .veli-deger {{ font-size: 16px; }}
  .veli-durum {{ margin: {b(0.5)} 0 {b(1.5)}; color: var(--muted); }}
  .veli-son {{ margin: {b(3)} 0 0; padding: {b(2)}; border: 1px solid var(--line); border-radius: {b(1)};
               background: var(--soft); font-weight: 600; }}
  @media (max-width: 640px) {{ .iki {{ grid-template-columns: 1fr; }} .veli-satir {{ grid-template-columns: 1fr; gap: {b(1)}; }} body {{ padding: 14px; }} }}
  @page {{ size: A4; margin: 16mm 14mm; }}
  @media print {{ body {{ padding: 0; }} h2 {{ break-after: avoid; }}
    .kutu, .kesisim, table, .sp-kart, .veli-satir, .veli-aralik, .veli-grup, .veli-konum, .gelisim-kart, .bilesik,
    .uyari, .not, .radar, svg {{ break-inside: avoid; page-break-inside: avoid; }} }}
{BILESEN_CSS}
</style>
"""


def _tablolari_sar(metin):
    """Dar ekranda tablolar sayfayı taşırmasın: yatay kaydırılabilir kapsayıcı."""
    return metin.replace("<table>", '<div class="tablo"><table>').replace("</table>", "</table></div>")
