"""
Norm motoru: son NORMATIF (Kademe 2 Aydos/Morassutti eklenmiş) ve son NORMATIF_YAS (TSYT eklenmiş), yaşa göre
persentil ve Z skoru, kategorik ve teste özgü değerlendirme, örneklem karşılaştırması, genel norm kapsamı,
türetilmiş değerler ve değişken yönü.

- Z-Skor Motoru (Paket 3): persentil tabanlı sıra dönüşümü (ham skordan (değer − ortalama) / SD alınmaz; bantlar
  arasında doğrusal ara değer → ters normal). Düşük-iyi testlerde işaret çevrilir (+ = akranlarından iyi);
  antropometrik (nötr) ölçüler tanımlayıcıdır, bileşik skorlara girmez.
- Kademe 2 Örneklem Karşılaştırması (Paket 35): yüzdelik norm değil, örneklem ortalaması ± SD (Aydos 2004, Morassutti 2025).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import os
import pandas as pd
import re
from statistics import NormalDist
from veri.brans_profilleri import BILESIK_Z
from veri.normlar_kategorik import (
    NORMATIF, NORMATIF_TEST, ORNEKLEM_KAYNAK_AYDOS_2004, ORNEKLEM_KAYNAK_MORASSUTTI_2025,
    ORNEKLEM_KUNYE_AYDOS_2004, ORNEKLEM_KUNYE_MORASSUTTI_2025, _AYDOS_2004)
from veri.normlar_tsyt import TSYT_KAYNAK, TSYT_NORMLARI
from veri.normlar_yas import NORMATIF_YAS
from olcut.esik import NORMATIF_ESIK_YAS
from olcut.katalog_islemleri import TEST_KATALOGU, kanonik_test
from olcut.ortak import DOGUM_KOLON, _girildi, dogum_ceyregi, guvenli_float, tarih_coz, veri_yolu
from olcut.tema import kategori_rengi


def _aydos_branslari(sutun):
    """sutun 2 = squat, 4 = bench press. Yalnız 'Erkek' (örneklem erkek)."""
    return {r[0]: {"Erkek": {"ort": r[sutun], "sd": r[sutun + 1], "n": r[1]}} for r in _AYDOS_2004}


NORMATIF = {**NORMATIF,                       # atama: otomatik denetim de görsün (modül düzeyinde .update yok)
    "Rölatif Squat (kg/kg)": {
        "tur": "orneklem", "birim": "kg/kg", "dusuk_iyi": False, "yas_alt": 18, "orneklem_yas": (18, 30),
        "kaynak": ORNEKLEM_KAYNAK_AYDOS_2004, "kunye": ORNEKLEM_KUNYE_AYDOS_2004, "branslar": _aydos_branslari(2),
    },
    "Rölatif Bench Press (kg/kg)": {
        "tur": "orneklem", "birim": "kg/kg", "dusuk_iyi": False, "yas_alt": 18, "orneklem_yas": (18, 30),
        "kaynak": ORNEKLEM_KAYNAK_AYDOS_2004, "kunye": ORNEKLEM_KUNYE_AYDOS_2004, "branslar": _aydos_branslari(4),
    },
}


NORMATIF = {**NORMATIF,                       # atama: otomatik denetim de görsün (modül düzeyinde .update yok)
    "Sıçrama Yüksekliği — En İyi (cm)": {
        "tur": "orneklem", "birim": "cm", "basamak": 1, "dusuk_iyi": False, "yas_alt": 20, "yas_ust": 29,
        "orneklem_yas": (20, 29), "kaynak": ORNEKLEM_KAYNAK_MORASSUTTI_2025, "kunye": ORNEKLEM_KUNYE_MORASSUTTI_2025,
        "genel_orneklem": "Üniversite öğrencisi (karma düzey)",
        "branslar": {"Üniversite öğrencisi (karma düzey)": {"Erkek": {"ort": 53.0, "sd": 14.0, "n": 422},
                                                             "Kadın": {"ort": 37.0, "sd": 11.0, "n": 538}}},
    },
}


# Profildeki spor dalı → örneklem branşı (tam ad eşleşir; alt gruplar burada). "Amerikan Futbolu" Futbol değildir.
ORNEKLEM_SPOR_DALI = {"Güreş (Serbest)": "Güreş", "Güreş (Grekoromen)": "Güreş"}


# Rölatif kuvvet: test → (girilen mutlak yük, hesaplanan rölatif değer). Rölatif değer kullanıcıdan istenmez.
ROLATIF_KUVVET = {
    "1RM Bench Press": ("1RM Bench Press (kg)", "Rölatif Bench Press (kg/kg)"),
    "1RM Squat (Arka Çömelme)": ("1RM Squat (kg)", "Rölatif Squat (kg/kg)"),
    "1RM Leg Press": ("1RM Leg Press (kg)", "Rölatif Leg Press (kg/kg)"),
}


# Doğrulanmış normu olmayan testler: değerlendirme alanında boş tablo değil bu metin görünür. Uydurma norm yok.
NORM_YOK_METNI = "Bu test için doğrulanmış norm bulunmamaktadır."


NORMSUZ_TESTLER = ("1RM Leg Press", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)",
                   "Şınav (Push-Up) — Maksimum Tekrar (Genel)", "Mekik (Sit-Up) — 1 Dakika (Genel)")


# Paket 36: Sargent normsuz listeden çıktı (Morassutti 2025 örneklemi). Testin hesaplanan değişkenleri — kapsam ve
# "değer girilince" metni için (girişten önce de bilinsin).
TURETILEN_DEGISKENLER = {"Sargent Dikey Sıçrama Testi (Duvar)": ["Sıçrama Yüksekliği — En İyi (cm)"]}


SARGENT_DENEMELER = ("Sıçrama Erişimi — Deneme 1 (cm)", "Sıçrama Erişimi — Deneme 2 (cm)",
                     "Sıçrama Erişimi — Deneme 3 (cm)")


ORNEKLEM_DISI_METNI = ("Bu değerin karşılaştırma örneklemi yalnız 18-30 yaş erkek sporculardan oluşur (Aydos ve ark., "
                       "2004); kadın ve 18 yaş altı sporcu için referans gösterilmez.")


def normatif_test_degerlendir(test_adi, degisken, deger, cinsiyet):
    """Teste özgü kategorik normatif değerlendirme."""
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_TEST:
        return None
    norm = NORMATIF_TEST[anahtar]
    cins_normu = norm.get(cinsiyet) or norm.get("Erkek")
    if cins_normu is None:
        return None
    try:
        d = float(deger)
    except (ValueError, TypeError):
        return None
    kategori = "Bilinmiyor"
    for kat, (alt, ust) in cins_normu.items():
        if alt <= d < ust:
            kategori = kat
            break
    renk = kategori_rengi(kategori)
    return {
        "kategori": kategori,
        "renk": renk,
        "kaynak": norm.get("kaynak", ""),
        "dusuk_iyi": norm.get("dusuk_iyi", False),
    }


NORMATIF_YAS = {**NORMATIF_YAS, **TSYT_NORMLARI}   # atama: otomatik denetim de görsün


def yas_persentil_bul(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum=None, test_tarihi=None):
    """
    Yaş ve cinsiyete göre persentil kategorisini bulur.
    Dönen: {kategori, renk, persentil_aralik, kaynak, n, bantlar, ceyrek_notu, ...} veya None

    Çeyrek boyutu (Paket 9, TSYT): norm "ceyrekler" içeriyorsa ve doğum + test tarihi biliniyorsa
    hücre = (doğum yılına göre yaş, takvim doğum çeyreği). Bilinmiyorsa dört çeyreğin ortalaması
    ("yaslar") kullanılır ve ceyrek_notu bunu söyler.
    """
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_YAS:
        return None

    norm = NORMATIF_YAS[anahtar]
    yaslar = norm["yaslar"]

    try:
        yas = int(float(sporcu_yas))
        d = float(deger)
    except (ValueError, TypeError):
        hucre_y = tsyt_hucre(dogum, test_tarihi) if "ceyrekler" in norm else None
        if hucre_y is None:
            return None
        yas, d = hucre_y[0], None
        try:
            d = float(deger)
        except (ValueError, TypeError):
            return None

    ceyrek, ceyrek_notu = None, None
    if "ceyrekler" in norm:
        hucre = tsyt_hucre(dogum, test_tarihi)
        if hucre:
            yas, ceyrek = hucre   # TSYT tabloları doğum yılına göre yaşla kurulmuş
        else:
            ceyrek_notu = ("Doğum tarihi bilinmediği için dört doğum çeyreğinin ortalaması kullanıldı "
                           "(çocuk sayısıyla ağırlıklı; yaklaşık değer; profil yaşıyla).")

    # En yakın yaş grubunu bul
    mevcut_yaslar = sorted(yaslar.keys())
    if yas < mevcut_yaslar[0]:
        secili_yas = mevcut_yaslar[0]
        yas_notu = f"⚠️ {yas} yaş için norm yok — {secili_yas} yaş normu kullanıldı"
    elif yas > mevcut_yaslar[-1]:
        secili_yas = mevcut_yaslar[-1]
        yas_notu = f"⚠️ {yas} yaş için norm yok — {secili_yas} yaş normu kullanıldı"
    else:
        secili_yas = min(mevcut_yaslar, key=lambda y: abs(y - yas))
        yas_notu = None

    cins_veri = yaslar[secili_yas].get(cinsiyet)
    if cins_veri is None:
        cins_veri = yaslar[secili_yas].get("Erkek")
    if ceyrek is not None:
        cey_tablo = norm["ceyrekler"].get(secili_yas, {}).get(cinsiyet, {})
        if ceyrek in cey_tablo:
            cins_veri = cey_tablo[ceyrek]
            ceyrek_notu = f"TSYT hücresi: {secili_yas} yaş (doğum yılına göre), {ceyrek}. doğum çeyreği"
        else:
            ceyrek_notu = "Bu yaş/cinsiyet için çeyrek tablosu yok — dört çeyreğin ortalaması kullanıldı."
    if cins_veri is None:
        return None
    tum_bantlar = {k: v for k, v in cins_veri.items() if k.startswith("P") and k[1:].isdigit()}
    tablo_no = norm.get("tablolar", {}).get(secili_yas)

    dusuk_iyi = norm.get("dusuk_iyi", False)

    # ── Persentil seti: P5/P25/P50/P75/P95 (varsayilan) veya P20/P40/P60/P80 ──
    if "P20" in cins_veri and "P5" not in cins_veri:
        # Alman DMT / NRW tipi 5 sinifli sistem (sinirlar P20, P40, P60, P80)
        p20, p40, p60, p80 = (cins_veri["P20"], cins_veri["P40"],
                              cins_veri["P60"], cins_veri["P80"])
        bantlar = {"P20": p20, "P40": p40, "P60": p60, "P80": p80}
        if dusuk_iyi:
            if d <= p20:    kategori, aralik = "Üstün", "≥ P80"
            elif d <= p40:  kategori, aralik = "İyi", "P60-P80"
            elif d <= p60:  kategori, aralik = "Ortalama", "P40-P60"
            elif d <= p80:  kategori, aralik = "Ortalama Altı", "P20-P40"
            else:           kategori, aralik = "Düşük", "< P20"
        else:
            if d >= p80:    kategori, aralik = "Üstün", "≥ P80"
            elif d >= p60:  kategori, aralik = "İyi", "P60-P80"
            elif d >= p40:  kategori, aralik = "Ortalama", "P40-P60"
            elif d >= p20:  kategori, aralik = "Ortalama Altı", "P20-P40"
            else:           kategori, aralik = "Düşük", "< P20"
        return {
            "kategori": kategori, "renk": kategori_rengi(kategori), "persentil_aralik": aralik,
            "kaynak": norm.get("kaynak", ""), "n": norm.get("n", ""),
            "birim": norm.get("birim", ""), "yas_notu": yas_notu,
            "kullanilan_yas": secili_yas, "bantlar": bantlar, "dusuk_iyi": dusuk_iyi,
            "ceyrek": ceyrek, "ceyrek_notu": ceyrek_notu, "tablo": tablo_no,
        }

    p5, p25, p50, p75, p95 = (cins_veri["P5"], cins_veri["P25"],
                               cins_veri["P50"], cins_veri["P75"], cins_veri["P95"])

    # Kategori belirle
    if dusuk_iyi:
        if d <= p5:      kategori, aralik = "Üstün", "≥ P95"
        elif d <= p25:   kategori, aralik = "İyi", "P75-P95"
        elif d <= p50:   kategori, aralik = "Ortalama Üstü", "P50-P75"
        elif d <= p75:   kategori, aralik = "Ortalama Altı", "P25-P50"
        elif d <= p95:   kategori, aralik = "Düşük", "P5-P25"
        else:            kategori, aralik = "Çok Düşük", "< P5"
    else:
        if d >= p95:     kategori, aralik = "Üstün", "≥ P95"
        elif d >= p75:   kategori, aralik = "İyi", "P75-P95"
        elif d >= p50:   kategori, aralik = "Ortalama Üstü", "P50-P75"
        elif d >= p25:   kategori, aralik = "Ortalama Altı", "P25-P50"
        elif d >= p5:    kategori, aralik = "Düşük", "P5-P25"
        else:            kategori, aralik = "Çok Düşük", "< P5"

    # Antropometrik (nötr) ölçüler: iyi/kötü değil, akranlara göre konum
    notr = norm.get("notr", False)
    if notr:
        notr_etiket = {
            "≥ P95":   "Çok Yüksek",
            "P75-P95": "Yüksek",
            "P50-P75": "Ortalama (üst yarı)",
            "P25-P50": "Ortalama (alt yarı)",
            "P5-P25":  "Düşük",
            "< P5":    "Çok Düşük",
        }
        kategori = notr_etiket[aralik]

    return {
        "kategori": kategori,
        "renk": kategori_rengi(kategori, notr),
        "persentil_aralik": aralik,
        "kaynak": norm.get("kaynak", ""),
        "n": norm.get("n", ""),
        "birim": norm.get("birim", ""),
        "yas_notu": yas_notu,
        "kullanilan_yas": secili_yas,
        # 19 persentilli tablolarda (TSYT) Z tüm bantlarla hesaplanır; gösterimde 5 ana bant kullanılır
        "bantlar": tum_bantlar if len(tum_bantlar) > 5 else {"P5": p5, "P25": p25, "P50": p50, "P75": p75, "P95": p95},
        "dusuk_iyi": dusuk_iyi,
        "notr": notr,
        "ceyrek": ceyrek, "ceyrek_notu": ceyrek_notu, "tablo": tablo_no,
    }


_STANDART_NORMAL = NormalDist()


def persentil_sirasi(bantlar, deger):
    """
    Persentil bantlarından (ör. {"P5":..,"P25":..,...}) değerin persentil
    sırasını bulur. Dönen: (persentil, durum) — durum: None, "alt_sinir",
    "ust_sinir" veya "esit_bant" (değer birden fazla bantla aynı).
    Bantlar ham değer yönünde artan değilse None döner.
    """
    try:
        noktalar = sorted((int(k[1:]), float(v)) for k, v in bantlar.items()
                          if k.startswith("P") and k[1:].isdigit())
        d = float(deger)
    except (TypeError, ValueError):
        return None
    if len(noktalar) < 2:
        return None
    ps = [p for p, _ in noktalar]
    vs = [v for _, v in noktalar]
    if any(vs[i] > vs[i + 1] for i in range(len(vs) - 1)):
        return None  # bant sırası bozuk — veri hatası, uydurma Z üretme

    esit = [p for p, v in noktalar if v == d]
    if len(esit) > 1:
        # Aynı değere birden fazla bant düşüyor (taban/tavan etkisi):
        # bu bantların en altı ile en üstünün ortası kullanılır.
        return (min(esit) + max(esit)) / 2, "esit_bant"
    if d < vs[0]:
        return float(ps[0]), "alt_sinir"
    if d > vs[-1]:
        return float(ps[-1]), "ust_sinir"
    if len(esit) == 1:
        return float(esit[0]), None
    for i in range(len(vs) - 1):
        if vs[i] < d < vs[i + 1]:
            oran = (d - vs[i]) / (vs[i + 1] - vs[i])
            return ps[i] + oran * (ps[i + 1] - ps[i]), None
    return None


def yas_z_skoru(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum=None, test_tarihi=None):
    """
    Yaş/cinsiyet normundan persentil sırası ve Z skoru.
    Dönen sözlük: persentil, z (ham değer yönünde), z_performans
    (+ = iyi; nötr ölçülerde None), durum, notr, yas_notu, kullanilan_yas,
    kaynak, n. Norm yoksa None.
    """
    ys = yas_persentil_bul(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum, test_tarihi)
    if not ys:
        return None
    sonuc = persentil_sirasi(ys["bantlar"], deger)
    if sonuc is None:
        return None
    persentil, durum = sonuc
    z = _STANDART_NORMAL.inv_cdf(persentil / 100.0)
    notr = bool(ys.get("notr"))
    if notr:
        z_perf = None
    else:
        z_perf = -z if ys.get("dusuk_iyi") else z
    # Performans persentili: her testte büyük = iyi. Düşük-iyi testlerde sıra ters çevrilir
    # (100 − P). Nötr (antropometrik) ölçülerde iyi/kötü olmadığı için ham sıra kalır.
    persentil_perf = persentil if notr or not ys.get("dusuk_iyi") else 100.0 - persentil
    return {
        "persentil": round(persentil, 1),
        "persentil_performans": round(persentil_perf, 1),
        "z": round(z, 2),
        "z_performans": None if z_perf is None else round(z_perf, 2),
        "durum": durum,
        "notr": notr,
        "dusuk_iyi": ys.get("dusuk_iyi", False),
        "yas_notu": ys.get("yas_notu"),
        "kullanilan_yas": ys.get("kullanilan_yas"),
        "kaynak": ys.get("kaynak", ""),
        "n": ys.get("n", ""),
        "birim": ys.get("birim", ""),
        "bantlar": ys["bantlar"],
        "bant_araligi": (min(int(k[1:]) for k in ys["bantlar"]),
                         max(int(k[1:]) for k in ys["bantlar"])),
        "ceyrek": ys.get("ceyrek"), "ceyrek_notu": ys.get("ceyrek_notu"), "tablo": ys.get("tablo"),
        "kategori": ys.get("kategori"), "persentil_aralik": ys.get("persentil_aralik"),
    }


def bant_metni(bantlar, ters):
    """
    Norm bantlarını yazıya döker. ters=True (düşük-iyi test): etiketler performans yönüne
    çevrilir (ham P5 → P95), böylece her testte P95 "en iyi %5'in sınırı" demektir.
    """
    sirali = sorted(((int(k[1:]), v) for k, v in bantlar.items()), key=lambda x: x[0])
    if len(sirali) > 5:   # TSYT: 19 persentil — ekranda 5 ana bant
        sirali = [(p, v) for p, v in sirali if p in (5, 25, 50, 75, 95)]
    parcalar = []
    for p, v in sirali:
        p_g = 100 - p if ters else p
        etiket = f"**P50 (medyan): {v}**" if p_g == 50 else f"P{p_g}: {v}"
        parcalar.append(etiket)
    return " | ".join(parcalar)


def z_durum_notu(zs):
    """Z sonucunun yanında gösterilecek kısa uyarı (performans yönünde yazılır)."""
    alt, ust = zs["bant_araligi"]
    if zs["durum"] in ("alt_sinir", "ust_sinir"):
        if zs.get("notr"):
            uc = f"P{alt} altında" if zs["durum"] == "alt_sinir" else f"P{ust} üstünde"
            return f"{uc} — tablonun dışında; konum sınırda tutuldu"
        iyi_uc = (zs["z_performans"] or 0) > 0
        yuzde = 100 - ust if iyi_uc else alt
        return (f"Akranlarının en {'iyi' if iyi_uc else 'zayıf'} %{yuzde:g}'inin de "
                f"{'üstünde' if iyi_uc else 'altında'} — Z sınırda tutuldu "
                f"(gerçek konum daha {'iyi' if iyi_uc else 'zayıf'} olabilir)")
    if zs["durum"] == "esit_bant":
        return "Değer birden fazla persentil bandına eşit (taban/tavan etkisi) — bu bantların ortası kullanıldı"
    return None


def sifir_gecerli(test_adi, degisken):
    """0 değeri bu normda gerçek bir skor mu? (ör. göz-el koordinasyonunda 0 yakalama)"""
    norm = NORMATIF_YAS.get(f"{test_adi} › {degisken}")
    if not norm:
        return False
    for cinsler in norm["yaslar"].values():
        for bant in cinsler.values():
            if isinstance(bant, dict) and any(
                    isinstance(v, (int, float)) and v <= 0 for v in bant.values()):
                return True
    return False


def ktk3_toplamlari(test_adi, degerler):
    """
    KTK3+ testlerinin norma bağlanan toplam skorları. Hem test ekranında hem
    de eski kayıtlardan Z profili çıkarılırken kullanılır. 0 geçerli bir
    skordur: toplam, alanlardan en az biri doldurulmuşsa hesaplanır.
    """
    def al(k):
        return guvenli_float(degerler.get(k, 0)) if _girildi(degerler.get(k)) else 0.0

    def herhangi(*ks):
        return any(_girildi(degerler.get(k)) for k in ks)

    sonuc = {}
    if test_adi == "Dengede Geriye Yürüme (Balancing Backwards)":
        ks = ["6 cm Kiriş - Toplam Adım", "4.5 cm Kiriş - Toplam Adım", "3 cm Kiriş - Toplam Adım"]
        if herhangi(*ks):
            sonuc["Toplam Adım (maks 72)"] = min(int(sum(al(k) for k in ks)), 72)
    elif test_adi == "Yana Sıçrama (Jumping Sideways)":
        ks = ["Deneme 1 (sıçrama sayısı)", "Deneme 2 (sıçrama sayısı)"]
        if herhangi(*ks):
            sonuc["Toplam Sıçrama (2 deneme)"] = int(sum(al(k) for k in ks))
    elif test_adi == "Yana Platform Değiştirme (Moving Sideways)":
        ks = ["Deneme 1 (puan)", "Deneme 2 (puan)"]
        if herhangi(*ks):
            sonuc["Toplam Puan (2 deneme)"] = int(sum(al(k) for k in ks))
    elif test_adi == "Göz-El Koordinasyonu (Duvara Atıp Yakalama)":
        ks = ["Deneme 1 (yakalama)", "Deneme 2 (yakalama)"]
        if herhangi(*ks):
            sonuc["Toplam Yakalama (2 deneme)"] = int(sum(al(k) for k in ks))
    return sonuc


BILESIK_MAKS_GUN = 90  # bileşenler arasında izin verilen en uzun tarih farkı


def bilesik_z_hesapla(ad, z_sozlugu):
    """
    z_sozlugu: {(test, değişken): {"z_performans": .., "tarih": Timestamp/None}}
    Dönen: {"deger", "eksik", "tarih_farki_gun"} — eksik bileşen varsa deger None.
    """
    tanim = BILESIK_Z[ad]
    eksik = [t for t, d in tanim["bilesenler"] if (t, d) not in z_sozlugu
             or z_sozlugu[(t, d)].get("z_performans") is None]
    if eksik:
        return {"deger": None, "eksik": eksik, "tarih_farki_gun": None, "dislanan": [], "notlar": []}

    kullanilan = list(tanim["bilesenler"])
    dislanan, notlar = [], []
    kural = tanim.get("taban_kurali")
    if kural:
        b = kural["bilesen"]
        p50 = (z_sozlugu[b].get("bantlar") or {}).get("P50")
        if p50 is not None and p50 <= kural["p50_esik"]:
            kullanilan.remove(b)
            dislanan.append(b[0])
            hucre = z_sozlugu[b].get("hucre", "")
            notlar.append(kural["not"] + (f" ({hucre} normunda medyan {p50} yakalama)." if hucre else "."))

    zler = [z_sozlugu[b]["z_performans"] for b in kullanilan]
    tarihler = [z_sozlugu[b].get("tarih") for b in tanim["bilesenler"]]
    tarihler = [t for t in tarihler if t is not None and not pd.isna(t)]
    fark = (max(tarihler) - min(tarihler)).days if len(tarihler) >= 2 else None
    return {"deger": round(sum(zler) / len(zler), 2), "eksik": [], "tarih_farki_gun": fark,
            "dislanan": dislanan, "notlar": notlar, "bilesen_sayisi": len(zler)}


def sporcu_z_profili(df_test, sporcu):
    """
    Sporcunun yaş bazlı normu olan her (test, değişken) için EN SON ölçümünün Z skoru.
    Dönen: {"hata": str|None, "satirlar": [..], "z_sozlugu": {..}, "eski_yas": bool}
    Z-Skor Profili sekmesi, radar ve ileride branş eşleştirmesi bu tek kaynağı kullanır.
    """
    bilgi = {}
    if os.path.exists(veri_yolu(SPORCU_DOSYA)):
        df_sp = pd.read_excel(veri_yolu(SPORCU_DOSYA))
        esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
        if not esl.empty:
            bilgi = esl.iloc[0].to_dict()
    cinsiyet = str(bilgi.get("Cinsiyet", "")).strip()
    profil_yas = bilgi.get("Yaş")
    sonuc = {"hata": None, "satirlar": [], "z_sozlugu": {}, "eski_yas": False}
    if cinsiyet not in ("Erkek", "Kadın"):
        sonuc["hata"] = "Sporcu profilinde cinsiyet bulunamadı; Z skoru hesaplanamaz."
        return sonuc

    df_s = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" in df_s.columns:
        df_s = df_s.sort_values("Tarih_dt", na_position="first")

    son_olcum = {}
    for _, satir in df_s.iterrows():
        test_z = satir.get("Test", "")
        vals = satir.to_dict()
        for k_t, v_t in ktk3_toplamlari(test_z, vals).items():
            if not _girildi(vals.get(k_t)):
                vals[k_t] = v_t   # eski kayıtlarda toplam kaydedilmemişti
        yas_z = vals.get("Test Yaşı")
        if not _girildi(yas_z):
            yas_z = profil_yas
            sonuc["eski_yas"] = True
        on_ek = f"{test_z} › "
        for anahtar in NORMATIF_YAS:
            if not anahtar.startswith(on_ek):
                continue
            degisken_z = anahtar[len(on_ek):]
            v = vals.get(degisken_z)
            if not _girildi(v):
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if v == 0 and not sifir_gecerli(test_z, degisken_z):
                continue
            son_olcum[(test_z, degisken_z)] = (v, satir.get("Tarih_dt"), satir.get("Tarih", ""), yas_z)

    for (test_z, degisken_z), (v, tarih_dt, tarih_str, yas_z) in son_olcum.items():
        zs = yas_z_skoru(test_z, degisken_z, yas_z, cinsiyet, v, bilgi.get(DOGUM_KOLON), tarih_dt)
        if not zs:
            continue
        try:
            yas_say = int(float(yas_z))
        except (TypeError, ValueError):
            yas_say = None
        norm_yaslar = NORMATIF_YAS[f"{test_z} › {degisken_z}"]["yaslar"]
        sonuc["z_sozlugu"][(test_z, degisken_z)] = {
            "z_performans": zs["z_performans"], "tarih": tarih_dt,
            "bantlar": zs["bantlar"], "hucre": f"{zs['kullanilan_yas']} yaş {cinsiyet.lower()}",
            # Rapor için (Paket 7): sınır durumları ve norm dayanağı
            "durum": zs["durum"], "durum_notu": z_durum_notu(zs), "yas_notu": zs.get("yas_notu"),
            "persentil": zs["persentil"], "ceyrek_notu": zs.get("ceyrek_notu"), "tablo": zs.get("tablo"),
            "yas": yas_say, "kullanilan_yas": zs["kullanilan_yas"], "kaynak": zs.get("kaynak", ""),
            "cins_norm_var": norm_yaslar.get(zs["kullanilan_yas"], {}).get(cinsiyet) is not None,
        }
        notlar_z = [n for n in (z_durum_notu(zs), zs.get("yas_notu"), zs.get("ceyrek_notu")) if n]
        sonuc["satirlar"].append({
            "Test": test_z,
            "Değişken": degisken_z,
            "Değer": v,
            "Tarih": tarih_str,
            "Norm yaşı": zs["kullanilan_yas"],
            "Performans persentili": zs["persentil_performans"],
            "Kategori": zs.get("kategori", ""),
            "Z": zs["z"] if zs["notr"] else zs["z_performans"],
            "Tür": "Tanımlayıcı (antropometrik)" if zs["notr"] else "Performans",
            "Not": " · ".join(notlar_z),
        })
    return sonuc


def tsyt_hucre(dogum, test_tarihi):
    """
    TSYT norm hücresi: (doğum yılına göre yaş, takvim doğum çeyreği). Kitabın tabloları bu tanımla
    tutarlıdır: çeyrekler boyunca ortalamalar kesintisiz bir yaş merdiveni oluşturur
    (ör. 7 yaş 1. çeyrek boy 128.2 < 8 yaş 4. çeyrek 129.5 cm). Doğum ya da test tarihi yoksa None.
    """
    d, t = tarih_coz(dogum), tarih_coz(test_tarihi)
    if d is None or t is None:
        return None
    return t.year - d.year, dogum_ceyregi(d)


# Normu olmayan ama yönü tanımdan belli olan hesaplanan değişkenler (norm sözlüklerinde yönü olanlar oradan okunur)
DEGISKEN_YONU = {"En İyi Süre (sn)": True, "En İyi Değer (cm)": False, "Rölatif Bench Press (kg/kg)": False,
                 "Rölatif Squat (kg/kg)": False, "Rölatif Leg Press (kg/kg)": False}


def degisken_yonu(test, degisken):
    """True: düşük değer iyi · False: yüksek değer iyi · None: yön tanımsız (nötr ölçü ya da bilinmiyor)."""
    test = kanonik_test(test)
    anahtar = f"{test} › {degisken}"
    for sozluk in (NORMATIF_YAS, NORMATIF_TEST, NORMATIF_ESIK_YAS):
        n = sozluk.get(anahtar)
        if n is not None:
            return None if n.get("notr") else bool(n.get("dusuk_iyi", False))
    n = NORMATIF.get(degisken)
    if n is not None and (degisken not in NORMATIF_KAPSAM or NORMATIF_KAPSAM[degisken](test)):
        return bool(n.get("dusuk_iyi", False))
    if degisken in DEGISKEN_YONU:
        return DEGISKEN_YONU[degisken]
    return True if SAYIM_DUSUK_IYI.search(str(degisken)) else None       # Paket 38c: düşme/hata sayısı


# Paket 38c: düşme ya da hata SAYISI: az olan iyidir (normu olmayan sürümlerde de, ör. Latorre tek ayak denge)
SAYIM_DUSUK_IYI = re.compile(r"düşme|hata", re.I)


def _yaprak_testler(d):
    for ad, v in d.items():
        if isinstance(v, dict) and "protokol" in v:
            yield ad
        elif isinstance(v, dict):
            yield from _yaprak_testler(v)


_COCUK_BATARYA_TESTLERI = frozenset(_yaprak_testler(TEST_KATALOGU["Çocuk ve Genç Fiziksel Uygunluk Bataryaları"]))


NORMATIF_KAPSAM = {
    # Yo-Yo IR1 bantları (Bangsbo 2008). IR2, Cooper 12 dk ve
    # 6 dk kürek ergometresi de bu değişken adını kullanır — onlara uygulanmaz.
    "Tamamlanan Mesafe (m)": lambda test: test.startswith("Yo-Yo IR1"),
    # VO2max bantları yetişkin (Haugen 2022, Saltin 1967): çocuk ve genç bataryalarının testlerine uygulanmaz.
    # FitnessGram'ın aerobik HFZ'si yaşa ve cinsiyete göre VO2max eşiğidir; tablo girilmedi (Paket 20).
    "VO2max Tahmini (ml/kg/min)": lambda test: test not in _COCUK_BATARYA_TESTLERI,
    # Paket 35: Aydos 2004 örneklemi (Kademe 2) yalnız bu iki testin rölatif değerine; Leg Press ve öbürleri normsuz
    "Rölatif Squat (kg/kg)": lambda test: test == "1RM Squat (Arka Çömelme)",
    "Rölatif Bench Press (kg/kg)": lambda test: test == "1RM Bench Press",
    # Paket 36: Morassutti 2025 örneklemi yalnız Sargent (duvar) sıçrama yüksekliğine
    "Sıçrama Yüksekliği — En İyi (cm)": lambda test: test == "Sargent Dikey Sıçrama Testi (Duvar)",
}


def orneklem_uygun(degisken, cinsiyet, yas, test_adi=None):
    """
    Kademe 2 örneklem karşılaştırması bu sporcuya gösterilebilir mi (Paket 35): değişken kapsamdaki testte, cinsiyet
    örneklemde TANIMLI (Erkek'e düşme yok) ve yaş ≥ yas_alt. Yaş bilinmiyorsa gösterilmez.
    """
    norm = NORMATIF.get(degisken)
    if not norm or norm.get("tur") != "orneklem":
        return False
    kapsam = NORMATIF_KAPSAM.get(degisken)
    if kapsam is not None and (test_adi is None or not kapsam(test_adi)):
        return False
    cinsler = {c for b in norm["branslar"].values() for c in b if c in ("Erkek", "Kadın")}
    if str(cinsiyet).strip() not in cinsler:
        return False
    try:
        y = float(yas)
    except (TypeError, ValueError):
        return False
    if norm.get("yas_ust") is not None and y > norm["yas_ust"]:         # Paket 36 (Aydos'ta yok → aynı)
        return False
    return y == y and y >= norm.get("yas_alt", 0)


def orneklem_bransi(norm, spor_dali):
    """Sporcunun spor dalına karşılık gelen örneklem branşı (tam ad ya da ORNEKLEM_SPOR_DALI); yoksa None."""
    s = str(spor_dali or "").strip()
    b = ORNEKLEM_SPOR_DALI.get(s, s)
    return b if b in norm.get("branslar", {}) else None


def orneklem_karsilastir(degisken, deger, cinsiyet, spor_dali="Genel/Yok", yas=None, test_adi=None):
    """
    Kademe 2: değeri örneklem ortalaması ± SD ile yan yana koyar — kategori, bant, yüzdelik YOK. Branş örneklemde
    varsa fark (değer − ort) ve SD cinsinden fark; yoksa yalnız tüm branş satırları. Uygun değilse None.
    """
    if not orneklem_uygun(degisken, cinsiyet, yas, test_adi):
        return None
    try:
        d = float(deger)
    except (TypeError, ValueError):
        return None
    norm, c = NORMATIF[degisken], str(cinsiyet).strip()
    sonuc = {"tur": "orneklem", "kategori": None, "kaynak": norm["kaynak"], "dusuk_iyi": norm.get("dusuk_iyi", False),
             "birim": norm.get("birim", ""), "kunye": norm.get("kunye", {}), "orneklem_yas": norm.get("orneklem_yas"),
             "deger": d, "brans": orneklem_bransi(norm, spor_dali) or norm.get("genel_orneklem"),
             "basamak": norm.get("basamak", 3),
             "satirlar": [(b, v[c]["n"], v[c]["ort"], v[c]["sd"]) for b, v in norm["branslar"].items() if c in v]}
    if sonuc["brans"] and c in norm["branslar"][sonuc["brans"]]:
        o = norm["branslar"][sonuc["brans"]][c]
        sonuc.update(ort=o["ort"], sd=o["sd"], n=o["n"], fark=round(d - o["ort"], 3),
                     sd_fark=round((d - o["ort"]) / o["sd"], 2))
    return sonuc


def _orneklem_sayi(x, basamak=3):
    return f"{x:.{basamak}f}".replace(".", ",")


def orneklem_notlari(sonuc, yas=None):
    """Kart notları (örneklem dili; kategori sözcüğü yok)."""
    n = []
    if sonuc.get("ort") is not None:
        isaret = "üstünde" if sonuc["fark"] >= 0 else "altında"
        b_ = sonuc.get("basamak", 3)
        n.append(f"{sonuc['brans']} örneklemi (n={sonuc['n']}): {_orneklem_sayi(sonuc['ort'], b_)} ± "
                 f"{_orneklem_sayi(sonuc['sd'], b_)} {sonuc['birim']}")
        n.append(f"Örneklem ortalamasının {_orneklem_sayi(abs(sonuc['fark']), b_)} {sonuc['birim']} "
                 f"({_orneklem_sayi(abs(sonuc['sd_fark']), 1)} SD) {isaret}" if abs(sonuc["fark"]) > 1e-9
                 else "Örneklem ortalamasına eşit")
    else:
        n.append("Sporcunun branşı örneklemde yok; yedi branşın örneklem değerleri tabloda.")
    oy = sonuc.get("orneklem_yas")
    try:
        if oy and yas is not None and float(yas) > oy[1]:
            n.append(f"Örneklem {oy[0]}-{oy[1]} yaş; sporcu {int(float(yas))} yaşında.")
    except (TypeError, ValueError):
        pass
    n.append((sonuc.get("kunye") or {}).get("kart_notu", "Yüzdelik norm değil."))
    return n


def orneklem_disi_metni(degisken):
    """Kapsam dışı (yaş/cinsiyet) açıklaması: örneklemin künyesinden; yoksa Aydos metni (Paket 35)."""
    return (NORMATIF.get(degisken, {}).get("kunye") or {}).get("disi_metni", ORNEKLEM_DISI_METNI)


def orneklem_tablosu(sonuc):
    """Örneklem satırları (markdown); sporcunun branşı kalın."""
    birim = sonuc.get("birim", "")
    satir = [f"| Branş | n | Ortalama ± SD ({birim}) |", "|---|---|---|"]
    for b, n, ort, sd in sonuc["satirlar"]:
        ad = f"**{b}**" if b == sonuc.get("brans") else b
        satir.append(f"| {ad} | {n} | {_orneklem_sayi(ort, sonuc.get('basamak', 3))} ± "
                     f"{_orneklem_sayi(sd, sonuc.get('basamak', 3))} |")
    return "\n".join(satir) + f"\n\nKaynak: {sonuc['kaynak']}"


def normatif_degerlendir(degisken, deger, cinsiyet, spor_dali="Genel/Yok", test_adi=None, yas=None):
    """Girilen değeri normatif tabloya göre değerlendirir. Kademe 2 örneklem kaydı orneklem_karsilastir'a gider."""
    if degisken not in NORMATIF:
        return None
    kapsam = NORMATIF_KAPSAM.get(degisken)
    if kapsam is not None and (test_adi is None or not kapsam(test_adi)):
        return None
    norm = NORMATIF[degisken]
    if norm.get("tur") == "orneklem":                 # Paket 35: Erkek'e düşme yok, yaş sınırı var, kategori yok
        return orneklem_karsilastir(degisken, deger, cinsiyet, spor_dali, yas, test_adi)
    dusuk_iyi = norm.get("dusuk_iyi", False)
    kaynak = norm.get("kaynak", "")

    # Branşa özgü norm ara
    cinsiyet_normu = None
    branslar = norm.get("branslar", {})
    for brans_adi, brans_veri in branslar.items():
        if brans_adi in spor_dali or spor_dali in brans_adi:
            if cinsiyet in brans_veri:
                cinsiyet_normu = brans_veri[cinsiyet]
                kaynak = brans_veri.get("kaynak", kaynak)
            break

    # Genel norm
    if cinsiyet_normu is None:
        cinsiyet_normu = norm.get(cinsiyet) or norm.get("Erkek")
    if cinsiyet_normu is None:
        return None

    try:
        d = float(deger)
    except (ValueError, TypeError):
        return None

    kategori = "Bilinmiyor"
    for kat, (alt, ust) in cinsiyet_normu.items():
        if alt <= d < ust:
            kategori = kat
            break

    renk = kategori_rengi(kategori)
    return {"kategori": kategori, "renk": renk, "kaynak": kaynak, "dusuk_iyi": dusuk_iyi}


SPORCU_DOSYA = "sporcular.xlsx"


# Sonuç dosyasındaki ölçüm olmayan sütunlar (grafiklerde değişken sayılmaz)
OTURUM_ADI_KOLON = "Oturum Adı"         # Paket 38d: kullanıcının oturuma verdiği ad (isteğe bağlı)


META_KOLONLAR = ["Sporcu", "Kategori", "Batarya", "Branş", "Test", "Tarih", "Notlar",
                 "Tarih_dt", "Test Yaşı", "Oturum", "Yer", "Uygulayıcı", OTURUM_ADI_KOLON]


TEST_DOSYA = "test_sonuclari.xlsx"


SWFT_TEST = "Special Wrestling Fitness Test (SWFT)"


def swft_turetilmis(degerler, sporcu_kilo):
    """
    SWFT'nin hesaplanan üç değeri (Test Uygula ekranı ve Paket 38s düzeltmesi aynı formül): toplam atış,
    vücut ağırlığına bölünmüş atış, SWFT indeksi = (HR0 + HR1) / toplam atış × 100.
    """
    p = [int(guvenli_float(degerler.get(f"Periyot {i} Atış Sayısı", 0))) for i in (1, 2, 3)]
    hr0, hr1 = guvenli_float(degerler.get("HR0 (bpm)", 0)), guvenli_float(degerler.get("HR1-dk (bpm)", 0))
    tn = sum(p)
    return {"Toplam Atış (TnThrows)": tn,
            "TnThrows/BM": round(tn / sporcu_kilo, 3) if sporcu_kilo > 0 else 0,
            "SWFT Index": round((hr0 + hr1) / tn * 100, 2) if tn > 0 else 0}


def turetilmis_degerler(test_adi, degerler, sporcu_satir, sporcu_kilo):
    """
    Girilen değerlerden otomatik hesaplanan değerler (en iyi deneme, KTK3+ toplamları, VO2max,
    asimetri…). Tekli giriş ve toplu giriş (Test Oturumu) AYNI fonksiyonu kullanır; Streamlit
    çağrısı yoktur. Dönen: (hesaplanan: dict, uyarilar: [str]).
    """
    uyarilar = []
    hesaplanan = {}

    sure_anahtarlari = [k for k in degerler if k.startswith("Deneme") and "(sn)" in k]
    if sure_anahtarlari:
        sureler = [guvenli_float(degerler[k]) for k in sure_anahtarlari if degerler[k]]
        sureler = [s for s in sureler if s > 0]
        if sureler:
            en_iyi = min(sureler)
            hesaplanan["En İyi Süre (sn)"] = en_iyi
            if test_adi == "30m Sprint":
                hesaplanan["Hız (m/s)"] = round(30 / en_iyi, 2)

    mesafe_anahtarlari = [k for k in degerler if "(cm)" in k]
    # Tek ölçüm / farklı anlamlı cm değişkenleri olan testlerde "en iyi" hesaplanmaz
    if test_adi in ("Omuz Rotasyon Testi (Sopa/İp)", "Oturma Yüksekliği", "Oturma Yüksekliği (TSYT)",
                    "Kulaç Uzunluğu (TSYT)", "Boy ve Vücut Ağırlığı (TSYT)", "Sargent Dikey Sıçrama Testi (Duvar)"):
        mesafe_anahtarlari = []
    if mesafe_anahtarlari:
        mesafeler = [guvenli_float(degerler[k]) for k in mesafe_anahtarlari if degerler[k]]
        mesafeler = [m for m in mesafeler if m > 0]
        if mesafeler:
            hesaplanan["En İyi Değer (cm)"] = max(mesafeler)

    # ── Paket 35c: Sargent — en iyi sıçrama erişimi − ayakta erişim (kullanıcıdan istenmez) ──
    if test_adi == "Sargent Dikey Sıçrama Testi (Duvar)":
        ayakta = guvenli_float(degerler.get("Ayakta Erişim (cm)", 0))
        erisim = [v for v in (guvenli_float(degerler.get(k, 0)) for k in SARGENT_DENEMELER) if v > 0]
        if erisim and ayakta <= 0:
            uyarilar.append("⚠️ Ayakta erişim girilmedi; sıçrama yüksekliği hesaplanamadı.")
        elif erisim and max(erisim) <= ayakta:
            uyarilar.append("⚠️ En yüksek sıçrama erişimi ayakta erişimden büyük değil; değerleri kontrol edin.")
        elif erisim:
            hesaplanan["Sıçrama Yüksekliği — En İyi (cm)"] = round(max(erisim) - ayakta, 1)

    # ── Paket 35: rölatif kuvvet = 1RM / kayıtlı vücut ağırlığı (kullanıcıdan istenmez) ──
    if test_adi in ROLATIF_KUVVET:
        giris, cikis = ROLATIF_KUVVET[test_adi]
        yuk = guvenli_float(degerler.get(giris, 0))
        if yuk > 0 and sporcu_kilo > 0:
            hesaplanan[cikis] = round(yuk / sporcu_kilo, 3)
        elif yuk > 0:
            uyarilar.append("⚠️ Sporcunun kayıtlı vücut ağırlığı yok; rölatif değer hesaplanamadı. "
                            "Sporcu profiline kilo (kg) girin.")

    if "Pik Güç (W)" in degerler and "Min Güç (W)" in degerler:
        pik = guvenli_float(degerler.get("Pik Güç (W)"))
        ort = guvenli_float(degerler.get("Ortalama Güç (W)"))
        mn = guvenli_float(degerler.get("Min Güç (W)"))
        if pik > 0 and sporcu_kilo > 0:
            hesaplanan["Pik Güç (W/kg)"] = round(pik / sporcu_kilo, 2)
            hesaplanan["Ortalama Güç (W/kg)"] = round(ort / sporcu_kilo, 2)
            hesaplanan["Yorgunluk İndeksi (%)"] = round((pik - mn) / pik * 100, 1)

    if test_adi == "Cooper 12 Dakika Koşusu" and "Tamamlanan Mesafe (m)" in degerler:
        mesafe = guvenli_float(degerler.get("Tamamlanan Mesafe (m)"))
        if mesafe > 0:
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round((mesafe - 504.9) / 44.73, 1)

    if test_adi in ["20m Mekik Koşusu (Beep Test)", "20m Mekik Koşusu (Eurofit/Léger)"] and "Son Seviye" in degerler:
        seviye = guvenli_float(degerler.get("Son Seviye"))
        if seviye > 0:
            # Léger et al. (1988) 20m MSRT VO2max denklemi
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(22.859 + (seviye * 1.593), 1)

    # ── PACER / 20m mekik tur sayisindan VO2max (Mahar 2006) ──
    if test_adi in ["PACER Testi", "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)",
                    "20m Mekik Koşusu (PREFIT)"] and "Tamamlanan Tur Sayısı" in degerler:
        tur = guvenli_float(degerler.get("Tamamlanan Tur Sayısı"))
        _yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        _cins = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        if tur > 0 and _yas > 0:
            _kod = 1 if _cins == "Erkek" else 0
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(
                47.438 - (0.265 * _yas) + (4.571 * _kod) + (0.182 * tur), 1)

    if test_adi == "20m Mekik Koşusu (ALPHA)" and "Son Hız (km/h)" in degerler:
        hiz = guvenli_float(degerler.get("Son Hız (km/h)"))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        if hiz > 0 and sporcu_yas > 0:
            vo2_alpha = 31.025 + (3.238 * hiz) - (3.248 * sporcu_yas) + (0.1536 * sporcu_yas * hiz)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_alpha, 1)

    if test_adi == "Bel Çevresi ve VKİ (Vücut Kompozisyonu)":
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        if sporcu_boy > 0 and sporcu_kilo > 0:
            boy_m = sporcu_boy / 100
            vki = round(sporcu_kilo / (boy_m ** 2), 1)
            hesaplanan["VKİ (kg/m²)"] = vki

    # ── Yo-Yo: VO2max tahmini (Bangsbo et al., 2008) ──
    # Tüm Yo-Yo testleri (18 adet) ada göre ayrılır:
    #   IR1 → VO2max = mesafe × 0.0084 + 36.4
    #   IR2 → VO2max = mesafe × 0.0136 + 45.3
    if test_adi.startswith("Yo-Yo") and "Tamamlanan Mesafe (m)" in degerler:
        mesafe = guvenli_float(degerler.get("Tamamlanan Mesafe (m)"))
        if mesafe > 0:
            if "IR2" in test_adi:
                hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(mesafe * 0.0136 + 45.3, 1)
            elif "IR1" in test_adi:
                hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(mesafe * 0.0084 + 36.4, 1)

    # ── FitnessGram: PACER VO2max ──
    if test_adi == "PACER (20m Mekik Koşusu)" and "Tamamlanan Tur Sayısı" in degerler:
        tur = guvenli_float(degerler.get("Tamamlanan Tur Sayısı"))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        if tur > 0 and sporcu_yas > 0:
            # Mahar et al. (2006) PACER VO2peak formülü
            cinsiyet_kodu = 1 if sporcu_cinsiyet == "Erkek" else 0
            vo2_pacer = 47.438 - (0.265 * sporcu_yas) + (4.571 * cinsiyet_kodu) + (0.182 * tur)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_pacer, 1)

    # ── CAPL-2 CAMSA: toplam = beceri (0-14) + süre puanı (1-14, CAPL-2 tablosundan girilir) ──
    if test_adi == "CAPL Engel Parkuru (Motor Beceri)":
        _b = guvenli_float(degerler.get("Beceri Puanı (0-14)", 0))
        _sp = guvenli_float(degerler.get("Süre Puanı (1-14)", 0))
        if _sp > 0:
            hesaplanan["Toplam CAMSA Puanı (1-28)"] = round(_b + _sp, 1)

    # ── Yüzme T-30: ortalama hız = mesafe / 1800 sn (Olbrecht ve ark. 1985) ──
    if test_adi == "T-30 Yüzme Testi":
        _m30 = guvenli_float(degerler.get("Toplam Mesafe (m)", 0))
        if _m30 > 0:
            hesaplanan["T-30 Hızı (m/sn)"] = round(_m30 / 1800, 3)

    # ── FitnessGram: Trunk Lift en iyi değer ──
    if test_adi == "Trunk Lift (Gövde Kaldırma) Testi":
        d1 = guvenli_float(degerler.get("Deneme 1 (cm)", 0))
        d2 = guvenli_float(degerler.get("Deneme 2 (cm)", 0))
        en_iyi_tl = max(d1, d2)
        if en_iyi_tl > 0:
            # FitnessGram maks. 30.5 cm sınırı
            hesaplanan["En İyi Kaldırma (cm)"] = min(en_iyi_tl, 30.5)

    # ── FitnessGram: 1 Mil VO2max ──
    if test_adi == "1 Mil Yürüyüş/Koşu Testi":
        dk = guvenli_float(degerler.get("Süre (dakika)", 0))
        sn = guvenli_float(degerler.get("Süre (saniye)", 0))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        cinsiyet_kodu = 1 if sporcu_cinsiyet == "Erkek" else 0
        sure_toplam_dk = dk + (sn / 60)
        if sure_toplam_dk > 0 and sporcu_yas > 0 and sporcu_boy > 0 and sporcu_kilo > 0:
            vki = sporcu_kilo / ((sporcu_boy / 100) ** 2)
            vo2_mil = 108.94 - (8.41 * sure_toplam_dk) + (0.34 * (sure_toplam_dk ** 2)) + (0.21 * sporcu_yas * cinsiyet_kodu) - (0.84 * vki)
            hesaplanan["Toplam Süre (dk)"] = round(sure_toplam_dk, 2)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_mil, 1)

    # ── FitnessGram: Deri Kıvrımı Vücut Yağ % ──
    if test_adi == "Vücut Kompozisyonu - Deri Kıvrımı":
        triceps = guvenli_float(degerler.get("Triceps Deri Kıvrımı (mm)", 0))
        baldır = guvenli_float(degerler.get("Baldır Deri Kıvrımı (mm)", 0))
        # e/k küçük girilse de kabul (harf dönüştürme işlevi yerine eşleme: Türkçe i/İ kuralına dokunmaz)
        cinsiyet_gir = {"e": "E", "E": "E", "k": "K", "K": "K"}.get(str(degerler.get("Cinsiyet (E/K)", "")).strip(), "")
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        # Girişten yoksa sporcu profilinden al
        if cinsiyet_gir not in ["E", "K"]:
            cinsiyet_gir = "E" if sporcu_cinsiyet == "Erkek" else "K"
        if triceps > 0 and baldır > 0:
            toplam_mm = triceps + baldır
            hesaplanan["Toplam Deri Kıvrımı (mm)"] = toplam_mm
            if cinsiyet_gir == "E":
                yag_yuzde = 0.735 * toplam_mm + 1.0
            else:
                yag_yuzde = 0.610 * toplam_mm + 5.1
            hesaplanan["Vücut Yağ % (Tahmini)"] = round(yag_yuzde, 1)
            # Yağsız vücut kütlesi
            if sporcu_kilo > 0:
                hesaplanan["Yağsız Kütle (kg)"] = round(sporcu_kilo * (1 - yag_yuzde / 100), 1)

    # ── CMJ / SJ / DJ en iyi değer ──
    if "CMJ" in test_adi or "Dikey Sıçrama" in test_adi:
        for prefix in ["CMJ", "SJ", "DJ"]:
            denemeleri = [guvenli_float(degerler.get(f"{prefix} Deneme {i} (cm)", 0)) for i in range(1, 4)]
            en_iyi = max(denemeleri)
            if en_iyi > 0:
                hesaplanan[f"{prefix} En İyi (cm)"] = en_iyi
        # CMJ-SJ elastik enerji farkı
        cmj_en_iyi = hesaplanan.get("CMJ En İyi (cm)", 0)
        sj_en_iyi  = hesaplanan.get("SJ En İyi (cm)", 0)
        if cmj_en_iyi > 0 and sj_en_iyi > 0:
            hesaplanan["Elastik Enerji Katkısı (cm)"] = round(cmj_en_iyi - sj_en_iyi, 1)
        # Tek CMJ varsa (Deneme 1/2/3 cm)
        if "CMJ En İyi (cm)" not in hesaplanan:
            denemeleri = [guvenli_float(degerler.get(f"Deneme {i} (cm)", 0)) for i in range(1, 4)]
            en_iyi = max(denemeleri)
            if en_iyi > 0:
                hesaplanan["CMJ En İyi (cm)"] = en_iyi
    if "Nordic" in test_adi and "NHT" in test_adi:
        sag = guvenli_float(degerler.get("Sağ Bacak Pik Kuvveti (N)", 0))
        sol = guvenli_float(degerler.get("Sol Bacak Pik Kuvveti (N)", 0))
        sag_kg = guvenli_float(degerler.get("Sağ Bacak (N/kg)", 0))
        sol_kg = guvenli_float(degerler.get("Sol Bacak (N/kg)", 0))
        if sag > 0 and sol > 0:
            guclu = max(sag, sol)
            zayif = min(sag, sol)
            asimetri = round((guclu - zayif) / guclu * 100, 1)
            hesaplanan["Asimetri İndeksi (%)"] = asimetri
            guclu_taraf = "Sağ" if sag >= sol else "Sol"
            hesaplanan["Güçlü Taraf"] = guclu_taraf
            if asimetri < 10:
                hesaplanan["Klinik Yorum"] = "✅ Simetrik (< %10)"
            elif asimetri < 15:
                hesaplanan["Klinik Yorum"] = "⚠️ Dikkat: Takip önerilir (%10-15)"
            else:
                hesaplanan["Klinik Yorum"] = "🔴 Yüksek Risk: Müdahale gerekli (> %15)"
        if sag_kg > 0 and sol_kg > 0:
            guclu_kg = max(sag_kg, sol_kg)
            zayif_kg = min(sag_kg, sol_kg)
            asimetri_kg = round((guclu_kg - zayif_kg) / guclu_kg * 100, 1)
            hesaplanan["Asimetri İndeksi N/kg (%)"] = asimetri_kg

    # ── İzokinetik H:K Oranı Otomatik ──
    if "İzokinetik" in test_adi or "Keytsman" in test_adi:
        quad_dom = guvenli_float(degerler.get("İzokinetik Kuadriseps 180°/sn Dom. (Nm/kg)", 0))
        ham_dom  = guvenli_float(degerler.get("İzokinetik Hamstring 180°/sn Dom. (Nm/kg)", 0))
        quad_nd  = guvenli_float(degerler.get("İzokinetik Kuadriseps 180°/sn N-Dom. (Nm/kg)", 0))
        ham_nd   = guvenli_float(degerler.get("İzokinetik Hamstring 180°/sn N-Dom. (Nm/kg)", 0))
        if quad_dom > 0 and ham_dom > 0:
            hk_dom = round(ham_dom / quad_dom * 100, 1)
            hesaplanan["H:K Oranı Dom. (%)"] = hk_dom
            hesaplanan["H:K Dom. Yorum"] = "✅ Normal" if hk_dom >= 60 else "🔴 Risk: < %60"
        if quad_nd > 0 and ham_nd > 0:
            hk_nd = round(ham_nd / quad_nd * 100, 1)
            hesaplanan["H:K Oranı N-Dom. (%)"] = hk_nd
            hesaplanan["H:K N-Dom. Yorum"] = "✅ Normal" if hk_nd >= 60 else "🔴 Risk: < %60"
        if quad_dom > 0 and quad_nd > 0:
            asim_quad = round(abs(quad_dom - quad_nd) / max(quad_dom, quad_nd) * 100, 1)
            hesaplanan["Kuadriseps Asimetri (%)"] = asim_quad
        if ham_dom > 0 and ham_nd > 0:
            asim_ham = round(abs(ham_dom - ham_nd) / max(ham_dom, ham_nd) * 100, 1)
            hesaplanan["Hamstring Asimetri (%)"] = asim_ham

    # ── KTK3+ Motor Koordinasyon otomatik toplamları (0 geçerli skordur) ──
    hesaplanan.update(ktk3_toplamlari(test_adi, degerler))

    if test_adi == "Tek Ayak Engel Üzerinden Sıçrama (Hopping for Height)":
        hh_sag = guvenli_float(degerler.get("Sağ Bacak Puanı (maks 39)", 0))
        hh_sol = guvenli_float(degerler.get("Sol Bacak Puanı (maks 39)", 0))
        if hh_sag > 0 or hh_sol > 0:
            hesaplanan["Toplam Puan (maks 78)"] = int(min(hh_sag, 39) + min(hh_sol, 39))
        if hh_sag > 0 and hh_sol > 0:
            hh_asim = round(abs(hh_sag - hh_sol) / max(hh_sag, hh_sol) * 100, 1)
            hesaplanan["Bacak Asimetrisi (%)"] = hh_asim
            hesaplanan["Güçlü Bacak"] = "Sağ" if hh_sag >= hh_sol else "Sol"
            if hh_asim < 10:
                hesaplanan["Asimetri Yorumu"] = "✅ Simetrik (< %10)"
            elif hh_asim < 15:
                hesaplanan["Asimetri Yorumu"] = "⚠️ Takip önerilir (%10-15)"
            else:
                hesaplanan["Asimetri Yorumu"] = "🔴 Belirgin fark (> %15)"

    # ── FSC: Top Sektirme (BOT-2) — iki denemenin en iyisi, maks 10 ──
    if test_adi == "Top Sektirme — Alternatif El (BOT-2)":
        bd = [guvenli_float(degerler.get(k, 0)) for k in
              ["Deneme 1 (doğru sektirme, maks 10)", "Deneme 2 (doğru sektirme, maks 10)"]]
        if max(bd) > 0:
            en_iyi_bd = int(min(max(bd), 10))
            hesaplanan["En İyi Sektirme (maks 10)"] = en_iyi_bd
            if en_iyi_bd == 10:
                hesaplanan["Tavan Notu"] = "Üst sınıra ulaştı (10/10)"

    # ── FSC: Omuz Rotasyonu — biakromiyal genişlik girildiyse net skor ──
    if test_adi == "Omuz Rotasyon Testi (Sopa/İp)":
        aralik = guvenli_float(degerler.get("En Dar El Aralığı (cm)", 0))
        biak = guvenli_float(degerler.get("Biakromiyal Genişlik (cm) — opsiyonel", 0))
        if aralik > 0 and biak > 0:
            hesaplanan["Net Omuz Rotasyon Skoru (cm)"] = round(aralik - biak, 1)

    # ── FSC: Oturma Yüksekliği — bacak uzunluğu ve OY/Boy oranı ──
    if test_adi == "Oturma Yüksekliği":
        oy = guvenli_float(degerler.get("Oturma Yüksekliği (cm)", 0))
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        if oy > 0 and sporcu_boy > 0:
            if oy >= sporcu_boy:
                uyarilar.append("⚠️ Oturma yüksekliği boydan büyük ya da eşit girildi. "
                           "Oturak yüksekliğinin çıkarıldığını ve profildeki boyu kontrol edin.")
            else:
                hesaplanan["Bacak Uzunluğu (cm)"] = round(sporcu_boy - oy, 1)
                hesaplanan["Oturma Yüksekliği / Boy Oranı"] = round(oy / sporcu_boy, 3)
    return hesaplanan, uyarilar
