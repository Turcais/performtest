"""
Branş grubu fiziksel profilleri (Opstoel ve ark., 2015) ve bileşik Z tanımları.

Bölme Aşama 1: uygulama.py'den birebir taşındı (davranış değişmedi). Yalnız sabit değerler; fonksiyon, çağrı ya da
içe aktarma yok (test_44a denetler).
"""


# ── Bileşik skorlar: performans yönlü Z'lerin ortalaması ──
# Resmi bir "motor quotient" DEĞİLDİR. KTK3+ MQ'nun resmi dönüşüm tabloları
# (Coppens ve ark., 2021, ek dosya B-E) elde edildiğinde ayrıca eklenecek;
# bu motor değişmeden kalır.
BILESIK_Z = {
    "KTK3+ Ortalama Z": {
        "bilesenler": [
            ("Dengede Geriye Yürüme (Balancing Backwards)", "Toplam Adım (maks 72)"),
            ("Yana Sıçrama (Jumping Sideways)", "Toplam Sıçrama (2 deneme)"),
            ("Yana Platform Değiştirme (Moving Sideways)", "Toplam Puan (2 deneme)"),
            ("Göz-El Koordinasyonu (Duvara Atıp Yakalama)", "Toplam Yakalama (2 deneme)"),
        ],
        "aciklama": (
            "Dört KTK3+ testinin yaş/cinsiyet persentil sırasından türetilen Z skorlarının "
            "ortalaması (Coppens ve ark., 2021 Flaman normları). Resmi KTK3+ motor bölümü "
            "(MQ) değildir; MQ sınıfları (70/85/115/130) bu skora uygulanmaz."
        ),
        # Taban etkisi kuralı: kullanılan yaş/cinsiyet hücresinde medyan bu eşiğe
        # eşit ya da altındaysa bileşen ortalamaya girmez (tek yakalama Z'yi ~1 oynatıyor).
        # Bileşenin kendi Z'si tabloda ve radarda gösterilmeye devam eder.
        "taban_kurali": {
            "bilesen": ("Göz-El Koordinasyonu (Duvara Atıp Yakalama)", "Toplam Yakalama (2 deneme)"),
            "p50_esik": 1,
            "not": "6-7 yaşta göz-el koordinasyonu taban etkisi nedeniyle bileşiğe katılmadı",
        },
    },
}

BRANS_GRUBU_PROFILLERI = {
    "kaynak": ("Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., "
               "Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric "
               "characteristics, physical fitness and motor coordination of 9 to 11 year old "
               "children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. "
               "https://doi.org/10.1371/journal.pone.0126282 — Tablo 1-3"),
    "orneklem": "620 Flaman çocuk, 9-11 yaş (10.30 ± 0.88), 347 erkek / 273 kız; grup değerleri cinsiyet ve yaş karışık",
    "gruplar": {
        "Top sporları":   {"ad_en": "Ball sports",    "n": 193, "branslar": "basketbol (17), korfbol (3), futbol (163), voleybol (10)"},
        "Dans":           {"ad_en": "Dance",          "n": 111, "branslar": "bale (19), halk dansı (6), caz dansı (13), modern dans (19), diğer dans (54)"},
        "Jimnastik":      {"ad_en": "Gymnastics",     "n": 55,  "branslar": "akrobasi (11), akro jimnastik (6), artistik jimnastik (38)"},
        "Dövüş sporları": {"ad_en": "Martial arts",   "n": 51,  "branslar": "judo (21), karate (25), tekvando (5)"},
        "Raket sporları": {"ad_en": "Racquet sports", "n": 46,  "branslar": "badminton (4), tenis (42)"},
        "Yüzme":          {"ad_en": "Swimming",       "n": 61,  "branslar": "yüzme (61)"},
    },
    # Değişkenler ve bu uygulamadaki karşılıkları.
    # eslesme None ise değişken profile alınmaz (6 numaralı sabit karar: protokol
    # gerçekten örtüşmüyorsa ya da örtüştüğü doğrulanamıyorsa norm bağlanmaz).
    "degiskenler": {
        "BH":   {"ad": "Boy", "birim": "cm", "tur": "antropometri", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "profil", "alan": "Boy (cm)"}},
        "SH":   {"ad": "Oturma yüksekliği", "birim": "cm", "tur": "antropometri", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Oturma Yüksekliği",
                             "degiskenler": ["Oturma Yüksekliği (cm)"], "birlestir": "tek"}},
        "BW":   {"ad": "Vücut ağırlığı", "birim": "kg", "tur": "antropometri", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "profil", "alan": "Kilo (kg)"}},
        "BF":   {"ad": "Vücut yağ yüzdesi", "birim": "%", "tur": "antropometri", "dusuk_iyi": False,
                 "eslesme": None,
                 "neden": ("Opstoel ayaktan ayağa BIA tartısı (Tanita BC-420SMA) kullanmış. Uygulamadaki "
                           "BIA testi cihazdan bağımsız; farklı BIA cihazları ve deri kıvrımı yöntemi aynı "
                           "çocukta farklı yağ yüzdesi verir.")},
        "BMI":  {"ad": "Vücut kitle indeksi", "birim": "kg/m²", "tur": "antropometri", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "profil_vki"}},
        "SR":   {"ad": "20 m mekik koşusu", "birim": "dk", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 # Opstoel: "(SR) (0.5 min) (EUROFIT)". Eurofit testine aynı birimde alan eklendi;
                 # seviye/tekrardan dönüşüm yapılmaz (kuralı kaynakla doğrulanmadı).
                 "eslesme": {"kaynak": "test", "test": "20m Mekik Koşusu (Eurofit/Léger)",
                             "degiskenler": ["Koşulan Süre (dk)"], "birlestir": "tek"}},
        "SF":   {"ad": "Omuz esnekliği", "birim": "cm", "tur": "fiziksel uygunluk", "dusuk_iyi": True,
                 "eslesme": {"kaynak": "test", "test": "Omuz Rotasyon Testi (Sopa/İp)",
                             "degiskenler": ["En Dar El Aralığı (cm)"], "birlestir": "tek"}},
        "SAR":  {"ad": "Otur-uzan", "birim": "cm", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Otur-Uzan (Sit and Reach) Testi",
                             "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"], "birlestir": "en_buyuk"}},
        "10x5": {"ad": "10x5 m mekik koşusu", "birim": "sn", "tur": "fiziksel uygunluk", "dusuk_iyi": True,
                 "eslesme": {"kaynak": "test", "test": "10x5m Mekik Koşusu (Shuttle Run)",
                             "degiskenler": ["Süre (sn)"], "birlestir": "tek"}},
        "SBJ":  {"ad": "Durarak uzun atlama", "birim": "cm", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Durarak Uzun Atlama",
                             "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"],
                             "birlestir": "en_buyuk"}},
        "CMJ":  {"ad": "Aktif sıçrama (CMJ)", "birim": "cm", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 "eslesme": None,
                 "neden": ("Opstoel: Optojump, üç denemenin en iyisi; kol pozisyonu yazılmamış. Uygulamadaki "
                           "CMJ eller kalçada uygulanıyor. Kol salınımı sıçrama yüksekliğini belirgin "
                           "artırdığı için protokol örtüşmesi doğrulanamadı.")},
        "SU":   {"ad": "Mekik (30 sn)", "birim": "tekrar", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Mekik (Sit-Up) Testi - 30sn",
                             "degiskenler": ["Tekrar Sayısı (30sn)"], "birlestir": "tek"}},
        "KPU":  {"ad": "Diz üstü şınav (30 sn)", "birim": "tekrar", "tur": "fiziksel uygunluk", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Diz Üstü Şınav — 30 sn (BOT-2)",
                             "degiskenler": ["Diz Üstü Şınav Tekrarı (30 sn)"], "birlestir": "tek"}},
        "JS":   {"ad": "Yana sıçrama (KTK)", "birim": "sıçrama", "tur": "motor koordinasyon", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Yana Sıçrama (Jumping Sideways)",
                             "degiskenler": ["Toplam Sıçrama (2 deneme)"], "birlestir": "tek"}},
        "MS":   {"ad": "Yana platform değiştirme (KTK)", "birim": "puan", "tur": "motor koordinasyon", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Yana Platform Değiştirme (Moving Sideways)",
                             "degiskenler": ["Toplam Puan (2 deneme)"], "birlestir": "tek"}},
        "WB":   {"ad": "Dengede geriye yürüme (KTK)", "birim": "adım", "tur": "motor koordinasyon", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Dengede Geriye Yürüme (Balancing Backwards)",
                             "degiskenler": ["Toplam Adım (maks 72)"], "birlestir": "tek"}},
        "BD":   {"ad": "Top sektirme (BOT-2)", "birim": "sektirme", "tur": "motor koordinasyon", "dusuk_iyi": False,
                 "eslesme": {"kaynak": "test", "test": "Top Sektirme — Alternatif El (BOT-2)",
                             "degiskenler": ["Deneme 1 (doğru sektirme, maks 10)", "Deneme 2 (doğru sektirme, maks 10)"],
                             "birlestir": "en_buyuk"}},
    },
    # (ortalama, SD) — Tablo 1-3 grup satırları
    "degerler": {
        "Top sporları": {"BH": (141.65, 7.21), "SH": (74.26, 3.55), "BW": (34.90, 6.98), "BF": (17.24, 6.00), "BMI": (17.29, 2.55), "SR": (6.05, 2.38), "SF": (91.1, 17.5), "SAR": (18.7, 5.7), "10x5": (21.9, 1.6), "SBJ": (141.0, 20.5), "CMJ": (20.5, 4.1), "SU": (22.6, 6.8), "KPU": (26.5, 6.4), "JS": (63.1, 11.0), "MS": (42.6, 6.4), "WB": (45.2, 13.2), "BD": (9.02, 2.03)},
        "Dans": {"BH": (142.38, 7.54), "SH": (74.44, 3.93), "BW": (34.83, 7.47), "BF": (18.43, 6.27), "BMI": (17.03, 2.47), "SR": (5.35, 2.37), "SF": (88.7, 13.7), "SAR": (21.2, 5.6), "10x5": (22.0, 1.5), "SBJ": (140.2, 21.1), "CMJ": (20.0, 4.2), "SU": (22.9, 6.4), "KPU": (25.3, 7.0), "JS": (63.5, 10.9), "MS": (43.3, 6.9), "WB": (47.3, 13.6), "BD": (8.39, 2.30)},
        "Jimnastik": {"BH": (141.37, 8.10), "SH": (73.67, 3.89), "BW": (34.13, 7.00), "BF": (17.56, 6.23), "BMI": (16.94, 2.38), "SR": (5.35, 2.18), "SF": (87.3, 16.6), "SAR": (21.1, 7.8), "10x5": (21.9, 2.1), "SBJ": (141.6, 24.5), "CMJ": (21.5, 4.8), "SU": (24.7, 8.5), "KPU": (26.4, 7.5), "JS": (62.8, 12.5), "MS": (43.2, 7.5), "WB": (49.2, 13.9), "BD": (8.38, 2.55)},
        "Dövüş sporları": {"BH": (142.87, 8.44), "SH": (74.68, 3.84), "BW": (35.89, 7.25), "BF": (18.56, 5.65), "BMI": (17.45, 2.26), "SR": (5.12, 2.04), "SF": (91.4, 15.9), "SAR": (17.5, 6.9), "10x5": (22.5, 1.9), "SBJ": (138.7, 23.9), "CMJ": (20.3, 4.3), "SU": (22.0, 7.2), "KPU": (26.5, 6.6), "JS": (60.8, 12.7), "MS": (40.8, 7.9), "WB": (43.2, 13.5), "BD": (8.00, 2.66)},
        "Raket sporları": {"BH": (141.61, 6.59), "SH": (73.77, 3.10), "BW": (33.79, 5.59), "BF": (17.99, 5.74), "BMI": (16.78, 2.02), "SR": (5.39, 1.98), "SF": (88.9, 14.0), "SAR": (17.6, 6.3), "10x5": (22.2, 1.7), "SBJ": (139.8, 21.9), "CMJ": (20.1, 4.1), "SU": (22.0, 6.7), "KPU": (25.4, 6.3), "JS": (64.1, 13.1), "MS": (43.2, 7.0), "WB": (46.9, 13.6), "BD": (9.00, 1.90)},
        "Yüzme": {"BH": (141.87, 8.29), "SH": (74.55, 4.45), "BW": (35.56, 7.56), "BF": (19.34, 6.42), "BMI": (17.51, 2.56), "SR": (5.27, 1.88), "SF": (90.2, 15.3), "SAR": (18.9, 7.0), "10x5": (22.6, 2.2), "SBJ": (138.1, 20.5), "CMJ": (20.4, 4.2), "SU": (23.7, 6.2), "KPU": (26.2, 6.9), "JS": (61.7, 11.5), "MS": (41.5, 6.1), "WB": (46.6, 14.4), "BD": (9.02, 2.01)},
    },
}
