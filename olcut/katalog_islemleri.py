"""
Katalog işlemleri: son TEST_KATALOGU (veri/katalog.py + HFZ bölümü), katalog dolaşımı, raflar, test arama ve
etiketler, protokol biçimleme, nitelik kartları, batarya kısaltmaları.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import pandas as pd
import re
from veri.katalog import TEST_KATALOGU
from veri.metinler import TERIM_SOZLUGU
from olcut.esik import _katalog_hfz_ekle


TEST_KATALOGU = _katalog_hfz_ekle(TEST_KATALOGU)


# ── Protokol bölüm başlıkları (Uygulama bölümünün nerede bittiğini belirler) ──
BOLUM_BASLIKLARI = (
    "Amaç", "Ekipman", "Hedef Grup", "Skorlama", "Normatif", "Not",
    "Klinik", "Güvenirlik", "Geçerlik", "HFZ", "Geçme Kriteri",
    "Dünya Rekoru", "Kaynak", "Değerlendirme", "Persentil",
    "Karşılaştırma", "Tavan", "Sınıflandırma", "Düzeltme",
    "Manken", "Yorum", "Referans", "Güncelleme",
    "Ölçüm Öncesi", "Formül",
)


_BOLUM_SONU = re.compile(
    r'^[ \t]*\*\*(?:' + '|'.join(re.escape(b) for b in BOLUM_BASLIKLARI) + r'|[^*\n]*?Farkı)',
    re.M
)


def _uygulama_araligi(metin):
    """Uygulama bölümünün (başlangıç, bitiş) karakter aralığını döndürür; yoksa None."""
    bas = re.search(r'^[ \t]*\*\*Uygulama', metin, re.M | re.IGNORECASE)
    if not bas:
        return None
    son = _BOLUM_SONU.search(metin, bas.end())
    return bas.start(), (son.start() if son else len(metin))


def protokol_formatla(metin: str) -> str:
    """
    Protokol metnindeki teknik terimlerin yanına Türkçe karşılığı ekler ve
    Uygulama bölümünü akademik görünümden çıkarır (saha özetinde gösterilir).
    """
    aralik = _uygulama_araligi(metin)
    if aralik:
        bas, son = aralik
        metin = metin[:bas] + metin[son:]

    sonuc = metin
    for orijinal, turkce in TERIM_SOZLUGU.items():
        if turkce in sonuc:
            continue
        # Parantezin hemen içindeki kısaltma açılmaz: "(HFZ)", "(bpm)", "(RSA)" ya zaten yanındaki
        # metinle açıklanmıştır ya da birim/ülke kodudur (Paket 8: "Niekerk (RSA)" Güney Afrika'ydı).
        sonuc = re.sub(rf'(?<!\()\b{re.escape(orijinal)}\b', turkce, sonuc)
    return sonuc


def protokol_ozet_cikar(protokol_metni: str) -> str:
    """Protokolün Uygulama bölümünden sade saha adımları çıkarır. API gerektirmez."""
    aralik = _uygulama_araligi(protokol_metni)
    if not aralik:
        adimlar = [s.strip() for s in protokol_metni.split('\n') if re.match(r'^\d+\.', s.strip())]
        return '\n'.join(adimlar[:6]) if adimlar else "Bu test için saha özeti oluşturulamadı."

    bas, son = aralik
    bolum = protokol_metni[bas:son]
    # Yalnızca düz "**Uygulama:**" başlığı atılır; "**Uygulama — Standart (...):**"
    # gibi alt başlıklar etiket olarak özette kalır.
    bolum = re.sub(r'^[ \t]*\*\*Uygulama:?\*\*[ \t]*', '', bolum, count=1)

    adimlar = []
    for satir in bolum.split('\n'):
        satir = satir.strip()
        if re.match(r'^\d+\.', satir):
            temiz = re.sub(r'\*\*([^*]+)\*\*', r'\1', satir)
            if len(temiz.strip()) > 3:
                adimlar.append(temiz)
        elif re.match(r'^\*\*(?:[A-ZÇĞİÖŞÜ]\)|Uygulama\b)', satir):
            # Alt başlıklar: "**A) CMJ:**" veya "**Uygulama — Saha (Partner):**"
            adimlar.append('**' + re.sub(r'\*\*', '', satir) + '**')

    if adimlar:
        return '\n'.join(adimlar[:16])

    duz = re.sub(r'\*\*', '', bolum).strip()
    return duz if duz else "Uygulama adımları bulunamadı."


# Batarya sayılan dallar: tamamı uygulanınca anlamlı olan bataryalar. Laboratuvar/branş koleksiyonları sayılmaz.
YON_BATARYA_KATEGORILERI = ("Türkiye Sportif Yetenek Modeli (TSYT)", "Çocuk ve Genç Fiziksel Uygunluk Bataryaları")


YON_BATARYA_DISI = ("Flaman Spor Pusulası (FSC) — Ek Testler",)


# Bataryanın cümlede geçen kısa adı ("Deniz Aydın'ın TSYT bataryasında …")
YON_BATARYA_KISA = {
    "TSYT Bataryası — 7-11 Yaş (GSB)": "TSYT",
    "Eurofit Fiziksel Uygunluk Test Bataryası": "Eurofit",
    "FitnessGram": "FitnessGram",
    "Presidential Youth Fitness Program": "PYFP",
    "Canadian Assessment of Physical Literacy (CAPL)": "CAPL",
    "ALPHA Health-Related Fitness Test Battery": "ALPHA",
    "PREFIT (Anaokulu Çocukları)": "PREFIT",
    "Chinese National Physical Fitness Measurement (CNPFM)": "CNPFM",
    "Karlsruher Motorik-Screening": "KMS",
    "Latorre Román Fitness Battery": "Latorre Román",
    "KTK3+ Motor Koordinasyon Test Bataryası": "KTK3+",
}


def katalog_testleri(katalog=None):
    """Katalogdaki her test: {"ad", "yol": (kategori, alt, branş|None), "kategori"} — Test ara bunu tarar."""
    katalog = TEST_KATALOGU if katalog is None else katalog
    liste = []
    for kat, altlar in katalog.items():
        for alt, icerik in altlar.items():
            if alt.startswith("_") or not isinstance(icerik, dict):
                continue
            if "protokol" in icerik:
                liste.append({"ad": alt, "yol": (kat, None, None), "kategori": kat})
                continue
            for ad, v in icerik.items():
                if ad.startswith("_") or not isinstance(v, dict):
                    continue
                if "protokol" in v:
                    liste.append({"ad": ad, "yol": (kat, alt, None), "kategori": kat})
                else:
                    for t, tv in v.items():
                        if not t.startswith("_") and isinstance(tv, dict) and "protokol" in tv:
                            liste.append({"ad": t, "yol": (kat, alt, ad), "kategori": kat})
    return liste


def katalog_bataryalari(katalog=None):
    """{(kategori, batarya): [test, …]} — yalnız YON_BATARYA_KATEGORILERI altındaki gerçek bataryalar."""
    katalog = TEST_KATALOGU if katalog is None else katalog
    out = {}
    for kat in YON_BATARYA_KATEGORILERI:
        for bat, icerik in katalog.get(kat, {}).items():
            if bat.startswith("_") or bat in YON_BATARYA_DISI or not isinstance(icerik, dict):
                continue
            testler = [t for t, v in icerik.items() if not t.startswith("_") and isinstance(v, dict) and "protokol" in v]
            if testler:
                out[(kat, bat)] = testler
    return out


def batarya_kisa(bat):
    return YON_BATARYA_KISA.get(bat, bat)


def test_kisa(test, bat):
    """Cümlede test adı: bataryanın kısa adı parantezde/tireyle tekrar ediyorsa atılır ('20m Sürat (TSYT)' → '20m Sürat')."""
    k = re.escape(batarya_kisa(bat))
    return re.sub(rf"\s*(\({k}\)|— {k})$", "", test).strip() or test


def batarya_yas_araligi(kategori, batarya, katalog=None):
    """Bataryanın _kunye'sindeki yas_araligi (min, max) ya da None."""
    katalog = TEST_KATALOGU if katalog is None else katalog
    k = (katalog.get(kategori, {}).get(batarya, {}) or {}).get("_kunye") or {}
    ya = k.get("yas_araligi") if isinstance(k, dict) else None
    return tuple(ya) if ya else None


# Aynı test iki yerde kayıtlı: takma ad → asıl ad. Kayıt asıl adla yazılır; eski kayıtlar okunurken asıl ada
# çevrilir (dosya yeniden yazılmaz — veri kaybolmaz, aynı sporcunun verisi ikiye bölünmez).
TEST_TAKMA_AD = {
    "Nordic Hamstring Kuvvet Testi (NHT)": "Nordic Hamstring Kuvvet Testi — Genel (NHT)",
    # Paket 30: eski ad (katalogda artık yok; eski kayıtlar okunurken yeni ada çevrilir)
    "Tenis Çeviklik T-Testi": "T-Testi (Çeviklik)",
    # Paket 30: branş raflarındaki gerçek tekrarlar — rafta görünürler, veri genel sürümde toplanır
    **{f"Yo-Yo IR1 ({b})": "Yo-Yo IR1 (Genel)" for b in (
        "Güreş", "Judo", "Tenis", "Muay Thai", "BJJ", "Badminton", "Masa Tenisi", "Squash", "Karate", "Taekwondo",
        "Boks", "Futbol", "Basketbol", "Voleybol", "Hentbol")},
    **{f"Wingate ({b})": "Wingate 30sn Bisiklet Testi" for b in ("Muay Thai", "MMA", "Kickboks")},
    "Yo-Yo IR2 (Futbol)": "Yo-Yo IR2 (Genel)",          # Paket 31: aynı gerekçe (değişkenler aynı)
}


def kanonik_test(ad):
    """Takma adı asıl test adına çevirir; başka her ad olduğu gibi döner."""
    return TEST_TAKMA_AD.get(ad, ad)


def test_tablosu_duzelt(df):
    """Okunan sonuç tablosunda takma adlı kayıtları asıl ada çevirir (yalnız bellekte; dosya değişmez)."""
    if isinstance(df, pd.DataFrame) and "Test" in df.columns:
        df = df.copy()
        df["Test"] = df["Test"].map(lambda t: kanonik_test(t) if isinstance(t, str) else t)
    return df


def test_raflari(ad, katalog=None):
    """Testin (ve takma adlarının) katalogdaki bütün yerleri [(kategori, alt, branş)] — "ayrıca şu raflarda"."""
    asil = kanonik_test(ad)
    return [t["yol"] for t in katalog_testleri(katalog) if kanonik_test(t["ad"]) == asil]


def test_izi_parcalari(ad, yol=None, katalog=None):
    """
    (seçili rafın yolu metni, ["ayrıca" rafları]) — yol (kategori, alt|None, branş|None) verilmezse testin kendi
    adıyla durduğu raf, o da yoksa ilk raf. "ayrıca" rafları kısa adla (branş, yoksa alt başlık).
    """
    raflar = test_raflari(ad, katalog)
    yol = tuple(yol) if yol else None
    if yol not in raflar:
        kendi = [t["yol"] for t in katalog_testleri(katalog) if t["ad"] == ad]
        yol = kendi[0] if kendi else (raflar[0] if raflar else None)
    if yol is None:
        return "", []
    diger = list(dict.fromkeys(r[2] or r[1] or r[0] for r in raflar if r != yol))
    return " › ".join(p for p in yol if p), diger


def test_izi(ad, yol=None, katalog=None):
    """Örnek: Branşa Özgü Testler › Bireysel Sporlar › Güreş › Special Wrestling Fitness Test (SWFT) · anaerobik."""
    yol_metni, diger = test_izi_parcalari(ad, yol, katalog)
    iz = " › ".join(p for p in (yol_metni, test_etiketli(ad)) if p)
    if diger:
        ek = ", ".join(diger[:ONERI_IZ_SINIRI]) + (f" ve {len(diger) - ONERI_IZ_SINIRI} rafta daha"
                                                   if len(diger) > ONERI_IZ_SINIRI else "")
        iz += f" — ayrıca: {ek}"
    return iz


def test_yolu(ad, katalog=None):
    """Testin katalogdaki ilk yeri → (kategori, batarya, branş|None); kayıttaki Kategori/Batarya/Branş için."""
    for t in katalog_testleri(katalog):
        if t["ad"] == ad:
            kat, alt, brans = t["yol"]
            return kat, alt if alt is not None else kat, brans
    return None


def test_bilgisi(ad, katalog=None):
    """Testin katalog kaydı (protokol, değişkenler…); takma ad asıl teste çözülür."""
    yol = test_yolu(kanonik_test(ad), katalog)
    if not yol:
        return None
    katalog = TEST_KATALOGU if katalog is None else katalog
    kat, bat, brans = yol
    d = katalog[kat] if bat == kat else katalog[kat][bat]
    d = d[brans] if brans else d
    return d[kanonik_test(ad)]


# ── C) Ölçülen nitelik ve sıra uyarısı (ExRx test bataryası ilkeleri) ──
# Tek taksonomi (Paket 30): her test bir NİTELİĞE eşlenir (gösterim: "10m Sprint (sürat)"); sıra denetimi
# niteliğin bağlı olduğu ExRx BİLEŞENİNİ kullanır. Sıra: antropometri → esneklik → sürat ve çeviklik → güç →
# kuvvet → kas dayanıklılığı → kardiyo; en yorucu sona. Eşleme test adındaki ölçülen niteliğe göre kuraldır.
# Niteliği olmayan testler (anket, pedometre, çok bileşenli batarya, EMG) sıra denetimine girmez.
TEST_BILESENLERI = ("antropometri", "esneklik", "sürat ve çeviklik", "güç", "kuvvet", "kas dayanıklılığı", "kardiyo")


TEST_NITELIKLERI = {                  # gösterilen nitelik → ExRx bileşeni (sıra uyarısı bunu kullanır)
    "maksimal kuvvet": "kuvvet",
    "çabuk kuvvet": "güç",
    "kuvvette devamlılık": "kas dayanıklılığı",
    "anaerobik": "kas dayanıklılığı",       # ExRx: kas dayanıklılığı ile aerobik arasında; aerobik en sonda kalır
    "aerobik": "kardiyo",
    "sürat": "sürat ve çeviklik",
    "çeviklik": "sürat ve çeviklik",
    "esneklik": "esneklik",
    "denge-koordinasyon": "sürat ve çeviklik",   # dinç sinir sistemi ister, düşük yorgunluk: erken
    "antropometri": "antropometri",
}


TEST_NITELIK_KURALLARI = [            # ilk eşleşen kural geçer (sıra önemli)
    (None, r"Anket|Adım Sayısı|Bataryası|Testleri$|Testleri \(|EMG|JPFT|GFT\)|Kuru Kara"),
    ("antropometri", r"Vücut Kompozisyonu|Deri Kıvrımı|VKİ|DEXA|İmpedans|Hidrostatik|Bel Çevresi|^Boy |"
                     r"Oturma Yüksekliği|Kulaç Uzunluğu"),
    ("esneklik", r"Esneklik|Otur-Uzan|Sit and Reach|Shoulder Stretch|Omuz Rotasyon|Uzan Eriş|Trunk Lift"),
    ("denge-koordinasyon", r"Yana Sıçrama|Yana Platform|Engel Üzerinden|Engel Parkuru|Koordinasyon|Denge|Balans|"
                           r"Flamingo|Top Yakalama|Top Sektirme|Göz-El"),
    ("anaerobik", r"Wingate|RSA|SWFT|SJFT|UKFT|BJJSFT|SSFT|Spesifik Dayanıklılık|Kondisyon Testi|Simulated"),
    ("aerobik", r"20m Mekik|Mekik Koşusu \((?:TSYT|50m)|Beep|PACER|Yo-Yo|Cooper|IFT|İntermittent|VO2max|Laktat|"
                r"CPET|1 Mil|1000m Koşusu|T-30|Critical Swimming|Aerobik Test|Ergometre|LIST|SIST|Simulation"),
    ("kuvvette devamlılık", r"Sit-Up|Curl-Up|Push-Up|Şınav|Pull-Up|Asılı|Bent Arm|Dayanıklılığı"),
    ("maksimal kuvvet", r"Kuvvet|1RM|Kavrama|Nordic|İzokinetik|İzometrik"),
    ("çabuk kuvvet", r"Force-Velocity|RFD|Sıçrama|CMJ|Atlama|Hopping|Sağlık Topu|Fırlatma|Servis Hızı"),
    ("çeviklik", r"Çeviklik|Agility|T-Test|Illinois|Spider|Shuttle Run|4x10m|10x5m|Ghost|S-Turn"),
    ("sürat", r"Sprint|Sürat|Hızlanma|Paten Hızı|Plate Tapping|Reaksiyon"),
]


def test_niteligi(ad):
    """Testin ölçtüğü nitelik (TEST_NITELIKLERI'nden) ya da None."""
    ad = kanonik_test(ad)
    for nitelik, kalip in TEST_NITELIK_KURALLARI:
        if re.search(kalip, ad):
            return nitelik
    return None


def test_bileseni(ad):
    """Testin sıra denetimindeki ExRx bileşeni — niteliğinden (tek taksonomi); niteliksizse None."""
    n = test_niteligi(ad)
    return TEST_NITELIKLERI[n] if n else None


def test_etiketli(ad):
    """Gösterim: "10m Sprint · sürat" (Paket 31: ayraç " · "). Nitelik adda zaten geçiyorsa yinelenmez ("T-Testi (Çeviklik)")."""
    n = test_niteligi(ad)
    if not n or ara_katla(n) in ara_katla(ad):
        return ad
    return f"{ad} · {n}"


def sira_uyarilari(testler):
    """
    Sıralı test listesi ExRx mantığını bozuyorsa uyarı metinleri (ENGELLEMEZ, yalnız bildirir). Her test için,
    kendisinden önce gelen ve bileşeni daha sonra gelmesi gereken testlerin en yorucusu adıyla anılır.
    """
    sira = {b: i for i, b in enumerate(TEST_BILESENLERI)}
    uyarilar = []
    for j, b in enumerate(testler):
        bb = test_bileseni(b)
        if bb is None:
            continue
        onceki = [(sira[test_bileseni(a)], a) for a in testler[:j]
                  if test_bileseni(a) is not None and sira[test_bileseni(a)] > sira[bb]]
        if onceki:
            _, a = max(onceki, key=lambda x: x[0])
            uyarilar.append(f"{a} ({test_niteligi(a)}) {b} ({test_niteligi(b)}) testinden önce geliyor; yorgunluk sonraki "
                            f"testleri etkiler. Önerilen sıra: {' → '.join(TEST_BILESENLERI)}.")
    return uyarilar


# ── D) Arama: eş anlamlı etiketler (ölçülen nitelikten) + sıralama + Türkçe/ek duyarsız ──
TEST_ETIKET_KURALLARI = [
    (r"Sprint|Sürat|Hızlanma|Paten Hızı", ["sürat", "hız", "sprint", "hızlanma"]),
    (r"\d+\s?m\b|\d+m\b", ["metre", "mesafe"]),
    (r"Çeviklik|Agility|T-Test|Illinois|Spider|Shuttle Run|4x10m|10x5m|Ghost|S-Turn|Yana Platform",
     ["çeviklik", "yön değiştirme", "agility"]),
    (r"Sıçrama|CMJ|\bSJ\b|\bDJ\b|Atlama|Hopping", ["sıçrama", "patlayıcı güç", "güç", "jump"]),
    (r"Sağlık Topu|Fırlatma", ["fırlatma", "atma", "patlayıcı güç", "güç"]),
    (r"Kuvvet|1RM|Kavrama|Nordic|İzokinetik|İzometrik|Force-Velocity|RFD|Koparma", ["kuvvet", "strength"]),
    (r"Nordic|Hamstring", ["hamstring", "eksantrik"]),
    (r"Kavrama", ["el kavrama", "dinamometre", "grip"]),
    (r"Mekik Koşusu|Beep|PACER|Yo-Yo|Cooper|IFT|İntermittent|VO2max|Laktat|CPET|Kardiyopulmoner|1 Mil|"
     r"1000m Koşusu|T-30|Critical Swimming|Aerobik|Ergometre|LIST|SIST|Simulat",
     ["dayanıklılık", "aerobik", "kondisyon", "kardiyo", "vo2max"]),
    (r"Wingate|RSA|Anaerobik|SJFT|SWFT|Spesifik Dayanıklılık|Kondisyon Testi", ["anaerobik", "dayanıklılık"]),
    (r"Sit-Up|Curl-Up|Mekik \(|Push-Up|Şınav|Pull-Up|Asılı|Bent Arm", ["kas dayanıklılığı", "tekrar"]),
    (r"Sit-Up|Curl-Up|Mekik \(", ["karın", "mekik"]),
    (r"Push-Up|Şınav", ["şınav", "üst ekstremite"]),
    (r"Esneklik|Otur-Uzan|Sit and Reach|Shoulder Stretch|Omuz Rotasyon|Uzan Eriş|Trunk Lift",
     ["esneklik", "hareket açıklığı", "flexibility"]),
    (r"Vücut Kompozisyonu|Deri Kıvrımı|VKİ|DEXA|İmpedans|Hidrostatik|Bel Çevresi", ["vücut kompozisyonu", "yağ", "antropometri"]),
    (r"^Boy |Oturma Yüksekliği|Kulaç Uzunluğu", ["antropometri", "boy", "uzunluk"]),
    (r"Denge|Balans|Flamingo|Balancing", ["denge", "balance"]),
    (r"Koordinasyon|Motor Beceri|Plate Tapping|Top Yakalama|Top Sektirme|Yana Sıçrama|Engel Parkuru|Göz-El",
     ["koordinasyon", "motor beceri"]),
    (r"Reaksiyon", ["reaksiyon", "tepki"]),
    (r"Yüzme|Swimming|Su Topu|Suda", ["yüzme", "su"]),
    (r"Paten", ["paten", "buz"]),
]


def test_etiketleri(ad):
    """Testin eş anlamlı arama etiketleri (adındaki ölçülen nitelikten türetilir; uydurma etiket yok)."""
    et = []
    for kalip, etiketler in TEST_ETIKET_KURALLARI:
        if re.search(kalip, ad):
            et += [e for e in etiketler if e not in et]
    return et


_ARA_HARF = str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u", "â": "a", "î": "i",
                           "û": "u", "é": "e", "è": "e", "ä": "a", "ë": "e"})


def ara_katla(m):
    """Türkçe karakter ve büyük/küçük harf duyarsız biçim: 'Süratı' → 'surati', 'İSTASYON' → 'istasyon'."""
    m = str(m).replace("İ", "i").replace("I", "i")
    return re.sub(r"[^a-z0-9]+", " ", m.casefold().translate(_ARA_HARF)).strip()


def _kelime_eslesir(q, kelime):
    """Kelime başı eşleşmesi; ek duyarsız: 'surati' 'surat'ı bulur (kök ≥ 4 harf, ek ≤ 4 harf)."""
    return kelime.startswith(q) or (len(kelime) >= 4 and q.startswith(kelime) and len(q) - len(kelime) <= 4)


# Paket 28: genel sözcükler (neredeyse her test adında geçer) sıralamaya katkı vermez; sorgu yalnız bunlardan
# oluşuyorsa normal aranır. Katlanmış biçimde (ara_katla) yazılır.
TEST_ARAMA_DURAK = ("test", "testi", "testleri", "olcum", "olcumu", "degerlendirme", "protokolu", "bataryasi")


TEST_ARAMA_KISA = 2          # bu uzunluğa kadar belirteç tek başına eşleşme saymaz (yalnız tam sözcük ya da eşlik)


def _bitisik_eslesir(sorgu_bitisik, jetonlar):
    """
    Sorgunun tamamı (boşluk/kısa çizgi/nokta kaldırılmış) ardışık sözcüklerde bir SÖZCÜK BAŞINDAN başlayarak
    geçiyor mu: "t-testi" = "t testi" = "ttesti" → "T-Testi (Çeviklik)" (t + testi). Sözcük ortasından başlayan
    eşleşme sayılmaz ("Trunk Lift Testi" içindeki "...t testi" değil). Döner: eşleşen ilk sözcük sırası ya da None.
    """
    for i in range(len(jetonlar)):
        if "".join(jetonlar[i:]).startswith(sorgu_bitisik):
            return i
    return None


def arama_branslari(katalog=None):
    """
    "Branşa Özgü Testler" altındaki branşlar → katlanmış sözcük dizileri (eş adlar ayrı dizi):
    "Kano/Kayak" → [["kano"], ["kayak"]], "BJJ (Jiujitsu)" → [["bjj"], ["jiujitsu"]], "Muay Thai" → [["muay", "thai"]].
    """
    katalog = TEST_KATALOGU if katalog is None else katalog
    out = {}
    for alt, v in katalog.get("Branşa Özgü Testler", {}).items():
        if str(alt).startswith("_") or not isinstance(v, dict):
            continue
        for brans, bv in v.items():
            if str(brans).startswith("_") or not isinstance(bv, dict):
                continue
            out[brans] = [ara_katla(p).split() for p in re.split(r"[/()]", brans) if ara_katla(p)]
    return out


def _brans_gecer(jetonlar, branslar):
    """Sözcük dizisinde geçen branşlar (ek duyarsız: "güreşçi" Güreş'i bulur; 3 harflik ad yalnız tam: "mma")."""
    def ayni(j, b):
        return j == b or (len(b) >= 4 and j.startswith(b) and len(j) - len(b) <= 4)
    bulunan = set()
    for brans, diziler in branslar.items():
        for d in diziler:
            for i in range(len(jetonlar) - len(d) + 1):
                if all(ayni(jetonlar[i + k], d[k]) for k in range(len(d))):
                    bulunan.add(brans)
    return bulunan


def arama_brans_cezasi(test, sorgu_jetonlari, branslar=None):
    """
    Eşitlik bozucu (Paket 29): puanı eşit sonuçlar arasında genel sürüm branş sürümünden önce gelir.
    Sorguda branş yoksa: adında bir branş geçen test ("Yo-Yo IR1 (Futbol)", "Wingate (MMA)", "CMJ (Badminton)")
    1 ceza alır, genel sürüm 0. Sorguda branş varsa kural tersine döner: o branşın testi (katalogda o branşın altında
    ya da adında o branş geçen) 0, diğerleri 1.
    """
    branslar = arama_branslari() if branslar is None else branslar
    sorguda = _brans_gecer(sorgu_jetonlari, branslar)
    adda = _brans_gecer(ara_katla(test["ad"]).split(), branslar)
    if sorguda:
        return 0 if (adda & sorguda or test["yol"][2] in sorguda) else 1
    return 1 if adda else 0


def test_ara(sorgu, kategori=None, katalog=None):
    """
    Test arama (Paket 27; sıralama Paket 28): ad + eş anlamlı etiketler + katalog yolu taranır; Türkçe karakter ve
    ek duyarsız. Puan (büyük önde; eşitlikte katalog sırası):
      ad tam aynı 1000 · sorgu adda bitişik, sözcük başından 500 (+50 adın başındaysa) · etiket tam aynı 300 ·
      sorgu etikette bitişik 250 · sözcük düzeyi: her içerik sözcüğü adda sözcük başı 2, etikette 1,5, herhangi
      bir yerde içinde 1 → 100 × en düşük + 10 × toplam (biri bile eşleşmezse 0).
    Genel sözcükler (TEST_ARAMA_DURAK) sözcük düzeyinde katkı vermez — sorgu yalnız onlardan oluşuyorsa normal
    aranır. 1-2 harflik sözcük tek başına içinde-eşleşme saymaz: yalnız sözcük başında ve başka bir sözcükle
    birlikteyken puan verir (durak sözcük eşlik sayılmaz); tek başına yazıldıysa yalnız bütün bir sözcüğe eşitse
    ("El", "T-Testi"deki "t") eşleşir.
    Takma adlı kayıt (TEST_TAKMA_AD) ayrıca listelenmez: onun adı ve rafı da taranır ama sonuç asıl teste toplanır
    ("yo-yo güreş" → Yo-Yo IR1 (Genel)); kategoriyle süzülen aramada raf kaydı kendisi döner. Boş sorgu: hepsi.
    Eşit puanda (Paket 29) genel sürüm branş sürümünden önce; sorguda branş adı varsa o branşın testi önce
    (arama_brans_cezasi); sonra katalog sırası.
    """
    q = ara_katla(sorgu or "")
    tum_kat = katalog_testleri(katalog)
    adaylar = [t for t in tum_kat
               if (not kategori or t["kategori"] == kategori) and (kategori or t["ad"] not in TEST_TAKMA_AD)]
    if not q:
        return adaylar
    if not kategori:                     # takma adlı raflar da taranır; eşleşme asıl teste toplanır (Paket 30)
        adaylar = tum_kat
    asil_kayit = {t["ad"]: t for t in reversed(tum_kat)}
    jetonlar = q.split()
    bitisik = "".join(jetonlar)
    icerik = [j for j in jetonlar if j not in TEST_ARAMA_DURAK] or jetonlar
    tek_kisa = len(jetonlar) == 1 and len(bitisik) <= TEST_ARAMA_KISA
    sonuc = []
    for i, t in enumerate(adaylar):
        ad_j = ara_katla(t["ad"]).split()
        etiketler = [ara_katla(e) for e in test_etiketleri(t["ad"])]
        et_j = [k for e in etiketler for k in e.split()]
        if tek_kisa:                                   # "el": yalnız bütün sözcük
            puan = 500 if bitisik in ad_j else (250 if bitisik in et_j else 0)
            if puan:
                sonuc.append((-puan, i, t))
            continue
        puanlar = [0]
        if q == " ".join(ad_j):
            puanlar.append(1000)
        b = _bitisik_eslesir(bitisik, ad_j)
        if b is not None:
            puanlar.append(500 + (50 if b == 0 else 0))
        if q in etiketler or bitisik in [e.replace(" ", "") for e in etiketler]:
            puanlar.append(300)
        elif any(_bitisik_eslesir(bitisik, e.split()) is not None for e in etiketler):
            puanlar.append(250)
        butun = " ".join(ad_j + etiketler + [ara_katla(y) for y in t["yol"] if y])
        seviye = []
        for j in icerik:
            kisa = len(j) <= TEST_ARAMA_KISA
            eslik = len([x for x in icerik if x != j and x not in TEST_ARAMA_DURAK]) > 0
            if kisa and not eslik:                     # kısa ve yalnız (durak sözcük eşlik sayılmaz): bütün sözcük
                seviye.append(2.0 if j in ad_j else (1.5 if j in et_j else 0.0))
            elif any(_kelime_eslesir(j, k) for k in ad_j):
                seviye.append(2.0)
            elif any(_kelime_eslesir(j, k) for k in et_j):
                seviye.append(1.5)
            elif not kisa and j in butun:
                seviye.append(1.0)
            else:
                seviye.append(0.0)
        if seviye and min(seviye) > 0:
            puanlar.append(100 * min(seviye) + 10 * sum(seviye))
        puan = max(puanlar)
        if puan:
            sonuc.append((-puan, i, t))
    branslar = arama_branslari(katalog)
    sirali = sorted(sonuc, key=lambda x: (x[0], arama_brans_cezasi(x[2], jetonlar, branslar), x[1]))
    if kategori:
        return [t for _, _, t in sirali]
    cikti = {}
    for _, _, t in sirali:                        # en iyi eşleşme asıl testin yerini belirler; tek sonuç
        asil = kanonik_test(t["ad"])
        if asil not in cikti and asil in asil_kayit:
            cikti[asil] = asil_kayit[asil]
    return list(cikti.values())


# ── B) Çalışma nesnesi (ayarlar.json → "calismalar") ──
CALISMA_ANAHTAR = "calismalar"


ONERI_IZ_SINIRI = 4                   # iz çubuğunda "ayrıca" ile adı yazılan raf sayısı


NITELIK_KARTLARI = (
    ("Maksimal kuvvet", ("maksimal kuvvet",)),
    ("Çabuk kuvvet (güç)", ("çabuk kuvvet",)),
    ("Kas dayanıklılığı", ("kuvvette devamlılık", "anaerobik")),
    ("Sürat", ("sürat",)),
    ("Çeviklik", ("çeviklik",)),
    ("Aerobik", ("aerobik",)),
    ("Esneklik", ("esneklik",)),
    ("Denge", ("denge-koordinasyon",)),
    ("Vücut ölçüleri", ("antropometri",)),
)


NITELIK_DIGER = "Diğer"


NITELIK_KARTI = {n: kart for kart, nl in NITELIK_KARTLARI for n in nl}


def nitelik_karti(ad):
    """Testin görünen nitelik kartı ("Kas dayanıklılığı" …) ya da "Diğer"."""
    n = test_niteligi(ad)
    return NITELIK_KARTI.get(n, NITELIK_DIGER) if n else NITELIK_DIGER


def nitelik_testleri(kart, katalog=None):
    """Kartın testleri, katalog sırasıyla; aynı test iki rafta ise bir kez (ilk rafı)."""
    gorulen, liste = set(), []
    for t in katalog_testleri(katalog):
        if t["ad"] not in gorulen and nitelik_karti(t["ad"]) == kart:
            gorulen.add(t["ad"])
            liste.append(t)
    return liste
