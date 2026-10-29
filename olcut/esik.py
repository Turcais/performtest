"""
Yaşa göre eşik (kriter) normları — FitnessGram Sağlıklı Uygunluk Zonu (HFZ): eşik tabloları, değerlendirme ve
protokol metnine eklenen HFZ bölümü (_katalog_hfz_ekle). Katalog işlemlerinden ÖNCE gelir: son TEST_KATALOGU buna dayanır.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
from olcut.tema import kategori_rengi


def _hfz_tablo(erkek, kiz):
    """{yaş: değer} ya da {(ilk, son): değer} → {yaş: {"Erkek": (alt, üst), "Kadın": (alt, üst)}} (5-17)."""
    def ac(d):
        out = {}
        for k, v in d.items():
            for y in (range(k[0], k[1] + 1) if isinstance(k, tuple) else (k,)):
                out[y] = v if isinstance(v, tuple) else (v, None)
        return out
    e, k = ac(erkek), ac(kiz)
    return {y: {"Erkek": e[y], "Kadın": k[y]} for y in range(5, 18)}


_HFZ_KAYNAK = ("The Cooper Institute. FitnessGram Healthy Fitness Zone standartları — Welk, G. J., & Meredith, M. D. "
               "(Eds.) (2008). FitnessGram/ActivityGram Test Administration Manual (4th ed.), Tablo 9.1-9.2. "
               "Human Kinetics.")


_HFZ_BACK_SAVER = _hfz_tablo({(5, 17): 8}, {(5, 10): 9, (11, 14): 10, (15, 17): 12})


NORMATIF_ESIK_YAS = {
    "Trunk Lift (Gövde Kaldırma) Testi › En İyi Kaldırma (cm)": {
        "olcut": "HFZ", "birim": "cm", "kaynak_birim": "inç", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _hfz_tablo({(5, 9): (6, 12), (10, 17): (9, 12)}, {(5, 9): (6, 12), (10, 17): (9, 12)}),
    },
    "Curl-Up (Kademeli Mekik) Testi › Tekrar Sayısı": {
        "olcut": "HFZ", "birim": "tekrar", "kaynak_birim": "tekrar", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _hfz_tablo({(5, 6): 2, 7: 4, 8: 6, 9: 9, 10: 12, 11: 15, 12: 18, 13: 21, (14, 17): 24},
                             {(5, 6): 2, 7: 4, 8: 6, 9: 9, 10: 12, 11: 15, (12, 17): 18}),
    },
    "Push-Up (Şınav) Testi › Tekrar Sayısı": {
        "olcut": "HFZ", "birim": "tekrar", "kaynak_birim": "tekrar", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _hfz_tablo({(5, 6): 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 10, 13: 12, 14: 14, 15: 16, (16, 17): 18},
                             {(5, 6): 3, 7: 4, 8: 5, 9: 6, (10, 17): 7}),
    },
    "Modified Pull-Up Testi › Tekrar Sayısı": {
        "olcut": "HFZ", "birim": "tekrar", "kaynak_birim": "tekrar", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _hfz_tablo({(5, 6): 2, 7: 3, 8: 4, (9, 10): 5, 11: 6, 12: 7, 13: 8, 14: 9, 15: 10, 16: 12, 17: 14},
                             {(5, 6): 2, 7: 3, (8, 17): 4}),
    },
    "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan) › Sağ Bacak - En İyi (cm)": {
        "olcut": "HFZ", "birim": "cm", "kaynak_birim": "inç", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _HFZ_BACK_SAVER,
    },
    "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan) › Sol Bacak - En İyi (cm)": {
        "olcut": "HFZ", "birim": "cm", "kaynak_birim": "inç", "dusuk_iyi": False, "kaynak": _HFZ_KAYNAK,
        "yaslar": _HFZ_BACK_SAVER,
    },
}


HFZ_KATEGORI = ("Sağlıklı Uygunluk Zonu", "Gelişim Gerekli")


def _hfz_cm(norm, v):
    """Kaynak birimi → programın birimi (inç → cm, 0,1 cm'e yuvarlanır)."""
    if v is None:
        return None
    return round(v * 2.54, 1) if norm.get("kaynak_birim") == "inç" and norm.get("birim") == "cm" else v


def esik_degerlendir(test_adi, degisken, deger, yas, cinsiyet):
    """
    Yaşa ve cinsiyete göre eşik (HFZ) değerlendirmesi. Dönen: kategori, renk, kaynak, esik (alt, üst — programın
    biriminde), kullanilan_yas, yas_notu. Norm ya da yaş yoksa None.
    """
    norm = NORMATIF_ESIK_YAS.get(f"{test_adi} › {degisken}")
    if not norm or cinsiyet not in ("Erkek", "Kadın"):
        return None
    try:
        yas, d = int(float(yas)), float(deger)
    except (TypeError, ValueError):
        return None
    yaslar = sorted(norm["yaslar"])
    if yas < yaslar[0]:
        return None
    kullanilan = min(yas, yaslar[-1])
    alt, ust = (_hfz_cm(norm, v) for v in norm["yaslar"][kullanilan][cinsiyet])
    if ust is not None:
        d = min(d, ust)                      # tavanın üstü tavana kırpılır (ör. 33 cm → 30,5 cm), eşik değil
    icinde = d >= alt
    kategori = HFZ_KATEGORI[0] if icinde else HFZ_KATEGORI[1]
    return {"kategori": kategori, "renk": kategori_rengi(kategori), "kaynak": norm["kaynak"],
            "dusuk_iyi": norm.get("dusuk_iyi", False), "esik": (alt, ust), "birim": norm["birim"],
            "olcut": norm["olcut"], "kullanilan_yas": kullanilan,
            "yas_notu": f"{yaslar[-1]}+ yaş satırı" if yas > yaslar[-1] else None}


def _hfz_deger_metni(norm, alt, ust):
    def s(v):
        return f"{v:g}".replace(".", ",")
    if norm.get("kaynak_birim") == "inç":
        cm = [_hfz_cm(norm, v) for v in (alt, ust)]
        if ust is None:
            return f"≥ {s(cm[0])} cm ({s(alt)} inç)"
        return f"{s(cm[0])}–{s(cm[1])} cm ({s(alt)}–{s(ust)} inç)"
    return f"≥ {s(alt)}" if ust is None else f"{s(alt)}–{s(ust)}"


def hfz_metni(test_adi):
    """Protokoldeki HFZ bölümü — NORMATIF_ESIK_YAS'tan üretilir (yaş grupları birleştirilir). Norm yoksa ""."""
    normlar = [n for k, n in NORMATIF_ESIK_YAS.items() if k.split(" › ")[0] == test_adi]
    if not normlar:
        return ""
    norm = normlar[0]
    yaslar = sorted(norm["yaslar"])

    def satir(cins):
        gruplar = []
        for y in yaslar:
            v = norm["yaslar"][y][cins]
            if gruplar and gruplar[-1][2] == v:
                gruplar[-1][1] = y
            else:
                gruplar.append([y, y, v])
        parca = []
        for ilk, son, (alt, ust) in gruplar:
            ad = f"{ilk}" + ("+" if son == yaslar[-1] and ilk == son else "") if ilk == son else (
                f"{ilk}–{son}" + ("+" if son == yaslar[-1] else ""))
            parca.append(f"{ad} yaş {_hfz_deger_metni(norm, alt, ust)}")
        return " · ".join(parca)
    e, k = satir("Erkek"), satir("Kadın")
    ek = " Her bacakta ayrı ayrı sağlanmalı." if len(normlar) > 1 else ""
    govde = f"- Erkek ve kız: {e}" if e == k else f"- Erkek: {e}\n- Kız: {k}"
    return ("**HFZ (Sağlık Uygunluk Zonu) — yaşa ve cinsiyete göre:** Eşiğin altı \"Gelişim Gerekli\"." + ek
            + "\n" + govde)


def _katalog_hfz_ekle(katalog):
    """TEST_KATALOGU'nun kopyası: eşik tablosu olan testlerin protokolüne HFZ bölümü eklenir (tek kaynak)."""
    out = {}
    for ad, deger in katalog.items():
        if isinstance(deger, dict) and "protokol" in deger:
            metin = hfz_metni(ad)
            out[ad] = {**deger, "protokol": deger["protokol"].rstrip() + "\n\n" + metin + "\n"} if metin else deger
        elif isinstance(deger, dict):
            out[ad] = _katalog_hfz_ekle(deger)
        else:
            out[ad] = deger
    return out
