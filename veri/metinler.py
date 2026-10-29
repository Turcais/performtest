"""
Metin sözlükleri: kaynakça, terim açıklamaları ve sözlüğü, veli raporu test grupları ve yorum şablonları,
ilgi anketi maddeleri ve kaynakları, güven düzeyleri, dünya rekorları.

Bölme Aşama 1: uygulama.py'den birebir taşındı (davranış değişmedi). Yalnız sabit değerler; fonksiyon, çağrı ya da
içe aktarma yok (test_44a denetler).
"""


# Opstoel ve ark. (2015): antrenman hacmine göre doğru sınıflama oranları
# (onların diskriminant modeli; 5+ saatte dövüş sporları grubu yoktu).
GUVEN_DUZEYLERI = {
    "Haftada 5 saat ve üzeri": {
        "oran": 85.2, "n": 81, "anlamli": True,
        "metin": ("Opstoel ve ark. (2015) modelinde haftada 5 saat ve üzeri antrenman yapan 81 çocuğun "
                  "%85.2'si kendi branş grubuna doğru sınıflandı (5 grup; bu hacimde dövüş sporları yoktu)."),
    },
    "Haftada 1-5 saat": {
        "oran": 48.8, "n": 252, "anlamli": False,
        "metin": ("Opstoel ve ark. (2015) modelinde haftada 1-5 saat antrenman yapan 252 çocukta doğru "
                  "sınıflama %48.8'de kaldı ve model anlamlı değildi. Bu hacimde profil, branşı güvenilir "
                  "biçimde ayırt etmiyor."),
    },
    "Haftada 1 saat veya daha az": {
        "oran": 48.4, "n": 184, "anlamli": False,
        "metin": ("Opstoel ve ark. (2015) modelinde haftada 1 saat veya daha az antrenman yapan 184 çocukta "
                  "doğru sınıflama %48.4'te kaldı ve model anlamlı değildi. Bu hacimde profil, branşı "
                  "güvenilir biçimde ayırt etmiyor."),
    },
}

# Madde havuzunun dayandığı hakemli kaynaklar (özeti okunarak tarandı).
ILGI_KAYNAKLARI = {
    "OPS15": "Opstoel, K., Pion, J., Elferink-Gemser, M., et al. (2015). PLoS ONE, 10(5), e0126282. (branş grupları)",
    "DOL20": "Dolci, F., Hart, N. H., Kilding, A. E., Chivers, P., Piggott, B., & Spiteri, T. (2020). Physical and energetic demand of soccer: A brief review. Strength & Conditioning Journal, 42(3), 70-77.",
    "MON10": "Montgomery, P. G., Pyne, D. B., & Minahan, C. L. (2010). The physical and physiological demands of basketball training and competition. International Journal of Sports Physiology and Performance, 5(1), 75-86.",
    "BVB25": "Marzano-Felisatti, J. M., Pino-Ortega, J., Priego-Quesada, J. I., Guzmán-Luján, J. F., & García-de-Alcaraz, A. (2025). Physical performance and game demands in beach volleyball: A systematic review. Journal of Human Sport and Exercise, 20(1), 79-92. https://doi.org/10.55860/g1z4az52",
    "LUB10": "Lubans, D. R., Morgan, P. J., Cliff, D. P., Barnett, L. M., & Okely, A. D. (2010). Fundamental movement skills in children and adolescents: review of associated health benefits. Sports Medicine, 40(12), 1019-1035.",
    "ANG09": "Angioi, M., Metsios, G., Koutedakis, Y., & Wyon, M. A. (2009). Fitness in contemporary dance: a systematic review. International Journal of Sports Medicine, 30(7), 475-484.",
    "BAL21": "Shaw, J. W., Mattiussi, A. M., Brown, D. D., Springham, M., Pedlar, C. R., & Tallent, J. (2021). The activity demands and physiological responses observed in professional ballet: A systematic review. The Journal of Sport and Exercise Science, 5(4), 254-269. https://doi.org/10.36905/jses.2021.04.04",
    "MOE19": "Moeskops, S., Oliver, J. L., Read, P. J., Cronin, J. B., Myer, G. D., & Lloyd, R. S. (2019). The physiological demands of youth artistic gymnastics: applications to strength and conditioning. Strength and Conditioning Journal, 41(1), 1-13.",
    "BRI14": "Bridge, C. A., Ferreira da Silva Santos, J., Chaabène, H., Pieter, W., & Franchini, E. (2014). Physical and physiological profiles of taekwondo athletes. Sports Medicine, 44(6), 713-733.",
    "KOR11": "Koropanovski, N., Berjan, B., Bozic, P. R., Pazin, N., Sanader, A., Jovanovic, S., & Jaric, S. (2011). Anthropometric and physical performance profiles of elite karate kumite and kata competitors. Journal of Human Kinetics, 30, 107-114. https://doi.org/10.2478/v10078-011-0078-x",
    "PHO15": "Phomsoupha, M., & Laffaye, G. (2015). The science of badminton: game characteristics, anthropometry, physiology, visual fitness and biomechanics. Sports Medicine, 45(4), 473-495.",
    "PYN14": "Pyne, D. B., & Sharp, R. L. (2014). Physical and energy requirements of competitive swimming events. International Journal of Sport Nutrition and Exercise Metabolism, 24(4), 351-359.",
    "PRI24": "Price, T., Cimadoro, G., & Legg, H. S. (2024). Physical performance determinants in competitive youth swimmers: a systematic review. BMC Sports Science, Medicine and Rehabilitation, 16, 20.",
    "VIA19": "Viana, E., Bentley, D. J., & Logan-Sprenger, H. M. (2019). A physiological overview of the demands, characteristics, and adaptations of highly trained artistic swimmers: a literature review. Sports Medicine - Open, 5, 16.",
    "COT09": "Côté, J., Lidor, R., & Hackfort, D. (2009). ISSP position stand: To sample or to specialize? Seven postulates about youth sport activities that lead to continued participation and elite performance. International Journal of Sport and Exercise Psychology, 7(1), 7-17",
}

ILGI_MADDELERI = {
    "Top sporları": [
        ("I2-TOP1", "Topu ayağınla sürüp rakipten kaçırmak ya da gol atmaya çalışmak", ["DOL20", "LUB10"]),
        ("I2-TOP2", "Topu potaya atmak ya da zıplayıp fileye doğru vurmak", ["MON10", "BVB25", "LUB10"]),
        ("I2-TOP3", "Takım arkadaşlarına pas verip birlikte bir oyun kurmak", ["DOL20", "OPS15"]),
        ("I2-TOP4", "Oyun boyunca durup kalkarak, aniden hızlanıp yön değiştirerek koşmak", ["DOL20", "MON10"]),
    ],
    "Dans": [
        ("I2-DAN1", "Müzik çalınca dans etmek", ["ANG09", "BAL21"]),
        ("I2-DAN2", "Bir dansı ezberleyip başkalarının önünde sergilemek", ["ANG09"]),
        ("I2-DAN3", "Müziğin ritmine uyarak sıçramak ve dönmek", ["BAL21"]),
        ("I2-DAN4", "Bir hareketi aynada izleyip daha düzgün ve güzel yapmaya çalışmak", ["ANG09", "BAL21"]),
    ],
    "Jimnastik": [
        ("I2-JIM1", "Takla atmak, amuda kalkmak, köprü yapmak", ["MOE19", "LUB10"]),
        ("I2-JIM2", "Barda ya da halkada asılıp sallanmak, kendini yukarı çekmek", ["MOE19"]),
        ("I2-JIM3", "Dar bir yerde (denge tahtası gibi) dengede durup hareket yapmak", ["MOE19", "LUB10"]),
        ("I2-JIM4", "Bir hareket dizisini hatasız yapana kadar tekrar tekrar çalışmak", ["MOE19"]),
    ],
    "Dövüş sporları": [
        ("I2-DOV1", "Minderde, kurallı bir oyun olarak itişip çekişmek, güreşmek", ["OPS15"]),
        ("I2-DOV2", "Tekme ve yumruk tekniklerini bir hedefe çalışmak", ["BRI14", "KOR11"]),
        ("I2-DOV3", "Karşındaki rakibi dikkatle izleyip onun hamlesine hızla karşılık vermek", ["BRI14", "KOR11"]),
        ("I2-DOV4", "Kurallı bir oyunda rakibi tutup dengesini bozarak yere indirmeye çalışmak", ["OPS15"]),
    ],
    "Raket sporları": [
        ("I2-RAK1", "Raketle bir topa ya da tüye vurmak", ["PHO15"]),
        ("I2-RAK2", "Filenin karşısındaki bir rakibe karşı tek başına oynamak", ["PHO15"]),
        ("I2-RAK3", "Hızla gelen bir topu gözünle izleyip zamanında yetişmek", ["PHO15"]),
        ("I2-RAK4", "Kısa, hızlı adımlarla sağa sola, öne arkaya atılarak topa uzanmak", ["PHO15"]),
    ],
    "Yüzme": [
        ("I2-YUZ1", "Havuzda ya da denizde yüzmek", ["PYN14"]),
        ("I2-YUZ2", "Suyun altına dalıp süzülmek", ["VIA19"]),
        ("I2-YUZ3", "Havuzun bir ucundan öbürüne, uzun süre durmadan yüzmek", ["PYN14", "PRI24"]),
        ("I2-YUZ4", "Duvardan güçlü bir itişle ya da atlayarak suya girip hızla ilerlemek", ["PRI24"]),
    ],
}

# Test → (grup, velinin okuyacağı ad). Normu olan her performans testi ya burada ya VELI_DISARIDA'da.
VELI_TEST_GRUBU = {
    "10x5m Mekik Koşusu (Shuttle Run)": ("Hız ve çabukluk", "10×5 m mekik koşusu"),
    "4x10m Mekik Koşusu (ALPHA)": ("Hız ve çabukluk", "4×10 m mekik koşusu"),
    "4x10m Mekik Koşusu (PREFIT)": ("Hız ve çabukluk", "4×10 m mekik koşusu"),
    "20m Sprint (KMS)": ("Hız ve çabukluk", "20 m sürat koşusu"),
    "20m Sprint (Latorre)": ("Hız ve çabukluk", "20 m sürat koşusu"),
    "20m Sürat (TSYT)": ("Hız ve çabukluk", "20 m sürat koşusu"),
    "Çeviklik — Pro Agility 5-10-5 (TSYT)": ("Hız ve çabukluk", "Çeviklik koşusu (5-10-5)"),
    "Plate Tapping (Disk Dokunma) Testi": ("Hız ve çabukluk", "El hızı (disklere dokunma)"),
    "El Kavrama Kuvveti (Eurofit)": ("Kuvvet", "El kavrama kuvveti"),
    "El Kavrama Kuvveti (ALPHA)": ("Kuvvet", "El kavrama kuvveti"),
    "El Kavrama Kuvveti (PREFIT)": ("Kuvvet", "El kavrama kuvveti"),
    "El Kavrama Kuvveti (Latorre)": ("Kuvvet", "El kavrama kuvveti"),
    "El Kavrama Kuvveti (TSYT)": ("Kuvvet", "El kavrama kuvveti"),
    "Durarak Uzun Atlama": ("Kuvvet", "Durarak uzun atlama"),
    "Durarak Uzun Atlama (ALPHA)": ("Kuvvet", "Durarak uzun atlama"),
    "Durarak Uzun Atlama (PREFIT)": ("Kuvvet", "Durarak uzun atlama"),
    "Durarak Uzun Atlama (CNPFM)": ("Kuvvet", "Durarak uzun atlama"),
    "Durarak Uzun Atlama (Latorre)": ("Kuvvet", "Durarak uzun atlama"),
    "CAPL Duran Uzun Atlama (Fiziksel Uygunluk)": ("Kuvvet", "Durarak uzun atlama"),
    "Dikey Sıçrama (TSYT, kollar serbest)": ("Kuvvet", "Dikey sıçrama"),
    "Geriye Sağlık Topu Atma (TSYT)": ("Kuvvet", "Geriye sağlık topu atma"),
    "Mekik (Sit-Up) Testi - 30sn": ("Kuvvet", "Mekik (30 saniye)"),
    "Curl-Up (Kademeli Mekik) Testi": ("Kuvvet", "Kademeli mekik"),
    "Curl-Up (Mekik) Testi": ("Kuvvet", "Kademeli mekik"),
    "Push-Up (Şınav) Testi": ("Kuvvet", "Şınav"),
    "Push-Up Testi": ("Kuvvet", "Şınav"),
    "Asılı Durma - Bükümlü Kol (Bent Arm Hang)": ("Kuvvet", "Bükülü kolla asılı durma"),
    "Otur-Uzan (Sit and Reach) Testi": ("Esneklik", "Otur-uzan"),
    "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)": ("Esneklik", "Tek bacak otur-uzan"),
    "Back-Saver Sit and Reach": ("Esneklik", "Tek bacak otur-uzan"),
    "Back-Saver Sit and Reach (ALPHA)": ("Esneklik", "Tek bacak otur-uzan"),
    "Esneklik (Uzan Eriş) — TSYT": ("Esneklik", "Uzan-eriş"),
    "Flamingo Denge Testi": ("Koordinasyon ve denge", "Tek ayak üstünde denge"),
    "Dengede Geriye Yürüme (Balancing Backwards)": ("Koordinasyon ve denge", "Denge tahtasında geriye yürüme"),
    "Yana Sıçrama (Jumping Sideways)": ("Koordinasyon ve denge", "Yana çift ayak sıçrama"),
    "Yana Sıçrama (KMS)": ("Koordinasyon ve denge", "Yana çift ayak sıçrama"),
    "Yana Platform Değiştirme (Moving Sideways)": ("Koordinasyon ve denge", "Yana platform değiştirme"),
    "Göz-El Koordinasyonu (Duvara Atıp Yakalama)": ("Koordinasyon ve denge", "Topu duvara atıp yakalama"),
}

# 24 şablon: (grup, kategori) → tek cümle. Kategori adları NORM_SKALASI'ndaki altı ad.
VELI_YORUMLARI = {
    ("Hız ve çabukluk", "Üstün"): "Bu hız ve çabukluk testinde akranlarının neredeyse hepsinden daha iyi bir sonuç aldı.",
    ("Hız ve çabukluk", "İyi"): "Bu hız ve çabukluk testinde akranlarının çoğundan daha iyi bir sonuç aldı.",
    ("Hız ve çabukluk", "Ortalama Üstü"): "Bu hız ve çabukluk testinde akranlarının ortalamasının biraz üstünde bir sonuç aldı.",
    ("Hız ve çabukluk", "Ortalama Altı"): "Bu hız ve çabukluk testinde akranlarının ortalamasının biraz altında, yaşıtlarının çoğuna yakın bir sonuç aldı.",
    ("Hız ve çabukluk", "Düşük"): "Bu hız ve çabukluk testinde sonucu şu an akranlarının çoğunun altında; hız ve çabukluk, koşu ve hareketli oyunlarla gelişen bir alandır.",
    ("Hız ve çabukluk", "Çok Düşük"): "Bu hız ve çabukluk testinde sonucu şu an akranlarının neredeyse hepsinin altında; hız ve çabukluk, koşu ve hareketli oyunlarla gelişen bir alandır.",
    ("Kuvvet", "Üstün"): "Bu kuvvet testinde akranlarının neredeyse hepsinden daha iyi bir sonuç aldı.",
    ("Kuvvet", "İyi"): "Bu kuvvet testinde akranlarının çoğundan daha iyi bir sonuç aldı.",
    ("Kuvvet", "Ortalama Üstü"): "Bu kuvvet testinde akranlarının ortalamasının biraz üstünde bir sonuç aldı.",
    ("Kuvvet", "Ortalama Altı"): "Bu kuvvet testinde akranlarının ortalamasının biraz altında, yaşıtlarının çoğuna yakın bir sonuç aldı.",
    ("Kuvvet", "Düşük"): "Bu kuvvet testinde sonucu şu an akranlarının çoğunun altında; kuvvet, bu yaşta tırmanma, atlama ve oyunla düzenli olarak gelişen bir alandır.",
    ("Kuvvet", "Çok Düşük"): "Bu kuvvet testinde sonucu şu an akranlarının neredeyse hepsinin altında; kuvvet, bu yaşta tırmanma, atlama ve oyunla düzenli olarak gelişen bir alandır.",
    ("Esneklik", "Üstün"): "Bu esneklik testinde akranlarının neredeyse hepsinden daha iyi bir sonuç aldı.",
    ("Esneklik", "İyi"): "Bu esneklik testinde akranlarının çoğundan daha iyi bir sonuç aldı.",
    ("Esneklik", "Ortalama Üstü"): "Bu esneklik testinde akranlarının ortalamasının biraz üstünde bir sonuç aldı.",
    ("Esneklik", "Ortalama Altı"): "Bu esneklik testinde akranlarının ortalamasının biraz altında, yaşıtlarının çoğuna yakın bir sonuç aldı.",
    ("Esneklik", "Düşük"): "Bu esneklik testinde sonucu şu an akranlarının çoğunun altında; esneklik, düzenli esneme hareketleriyle gelişen bir alandır.",
    ("Esneklik", "Çok Düşük"): "Bu esneklik testinde sonucu şu an akranlarının neredeyse hepsinin altında; esneklik, düzenli esneme hareketleriyle gelişen bir alandır.",
    ("Koordinasyon ve denge", "Üstün"): "Bu koordinasyon ve denge testinde akranlarının neredeyse hepsinden daha iyi bir sonuç aldı.",
    ("Koordinasyon ve denge", "İyi"): "Bu koordinasyon ve denge testinde akranlarının çoğundan daha iyi bir sonuç aldı.",
    ("Koordinasyon ve denge", "Ortalama Üstü"): "Bu koordinasyon ve denge testinde akranlarının ortalamasının biraz üstünde bir sonuç aldı.",
    ("Koordinasyon ve denge", "Ortalama Altı"): "Bu koordinasyon ve denge testinde akranlarının ortalamasının biraz altında, yaşıtlarının çoğuna yakın bir sonuç aldı.",
    ("Koordinasyon ve denge", "Düşük"): "Bu koordinasyon ve denge testinde sonucu şu an akranlarının çoğunun altında; koordinasyon ve denge, bu yaşta en hızlı gelişen alanlardan biridir ve düzenli hareketle değişir.",
    ("Koordinasyon ve denge", "Çok Düşük"): "Bu koordinasyon ve denge testinde sonucu şu an akranlarının neredeyse hepsinin altında; koordinasyon ve denge, bu yaşta en hızlı gelişen alanlardan biridir ve düzenli hareketle değişir.",
}

KAYNAKCA = [
    {"k": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3", "s": "İndekslenmeyen", "d": "", "n": "kurum yayını (kitap); TSYT norm tabloları 9.1.1-9.5.21"},
    {"k": "Gençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı)", "s": "İndekslenmeyen", "d": "", "n": "kurum belgesi; yıl belgede yok (kitapta TSYTSYP Uygulama Talimatı, 2022)"},
    {"k": "Gençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Koordinasyon testine ve mekik koşusuna ait protokol (uygulama talimatı)", "s": "İndekslenmeyen", "d": "", "n": "kurum belgesi; yıl belgede yok"},
    {"k": "Aagaard, P. et al. (2002). Increased rate of force development and neural drive of human skeletal muscle following resistance training. Journal of Applied Physiology, 93(4), 1318-1326", "s": "Q1", "d": "Journal of Applied Physiology", "n": ""},
    {"k": "Abian-Vicen, J., Del Coso, J., González-Millán, C., Salinero, J. J., & Abian, P. (2012). Analysis of dehydration and strength in elite badminton players. PLoS One, 7(5), e37821", "s": "Q1", "d": "PLoS One", "n": ""},
    {"k": "Adam, C. et al. (1988). Eurofit: European Test of Physical Fitness. Council of Europe, Rome", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Al Attar, W. S. A., Soomro, N., Sinclair, P. J., Pappas, E., & Sanders, R. H. (2017). Effect of injury prevention programs that include the Nordic hamstring exercise on hamstring injury rates in soccer players: a systematic review and meta-analysis. Sports Medicine, 47(5), 907-916", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Andreato, L. V., Franchini, E., de Moraes, S. M. F., Pastório, J. J., da Silva, D. F., Esteves, J. V. D. C., & Gomes, T. L. M. (2013). Physiological and technical-tactical analysis in Brazilian jiu-jitsu competition. Asian Journal of Sports Medicine, 4(2), 137-143", "s": "Q3/Q4", "d": "Asian Journal of Sports Medicine", "n": "en iyi çeyrek Q3"},
    {"k": "Angioi, M., Metsios, G., Koutedakis, Y., & Wyon, M. A. (2009). Fitness in contemporary dance: a systematic review. International Journal of Sports Medicine, 30(7), 475-484", "s": "Q1", "d": "International Journal of Sports Medicine", "n": ""},
    {"k": "Arkaev, L. I., & Suchilin, N. G. (2004). Gymnastics: How to Create Champions. Meyer & Meyer Sport", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "ATS/ACCP Statement on Cardiopulmonary Exercise Testing (2003). American Journal of Respiratory and Critical Care Medicine, 167(2), 211-277", "s": "Q1", "d": "American Journal of Respiratory and Critical Care Medicine", "n": ""},
    {"k": "Aydos, L., Pepe, H., & Karakuş, H. (2004). Bazı takım ve ferdi sporlarda rölatif kuvvet değerlerinin araştırılması. Gazi Üniversitesi Kırşehir Eğitim Fakültesi Dergisi, 5(2), 305-315", "s": "Belirlenemedi", "d": "Gazi Üniversitesi Kırşehir Eğitim Fakültesi Dergisi", "n": "Kademe 2 örneklem (rölatif squat ve bench press, Paket 35); SJR listesinde doğrulanmadı"},
    {"k": "Baechle, T. R., & Earle, R. W. (Eds.). (2008). Essentials of Strength Training and Conditioning (3rd ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Balady, G. J. et al. (2010). Clinician's guide to cardiopulmonary exercise testing in adults. Circulation, 122(2), 191-225", "s": "Q1", "d": "Circulation", "n": ""},
    {"k": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test: a useful tool for evaluation of physical performance in intermittent sports. Sports Medicine, 38(1), 37-51", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Bar-Or, O. (1987). The Wingate anaerobic test: An update on methodology, reliability and validity. Sports Medicine, 4(6), 381-394", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Bianco, A. et al. (2015). The FitnessGram trunk lift test: a critical review. Measurement in Physical Education and Exercise Science, 19(4), 204-213", "s": "Q2", "d": "Measurement in Physical Education and Exercise Science", "n": ""},
    {"k": "Bosco, C., Luhtanen, P., & Komi, P. V. (1983). A simple method for measurement of mechanical power in jumping. European Journal of Applied Physiology, 50(2), 273-282", "s": "Q1", "d": "European Journal of Applied Physiology", "n": ""},
    {"k": "Bridge, C. A., Santos, J. F. S., Chaabène, H., Pieter, W., & Franchini, E. (2014). Physical and physiological profiles of taekwondo athletes. Sports Medicine, 44(6), 713-733", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Brozek, J. et al. (1963). Densitometric analysis of body composition. Annals of the New York Academy of Sciences, 110, 113-140", "s": "Q1", "d": "Annals of the New York Academy of Sciences", "n": ""},
    {"k": "Bruininks, R. H., & Bruininks, B. D. (2005). Bruininks-Oseretsky Test of Motor Proficiency, Second Edition (BOT-2). Minneapolis, MN: Pearson Assessment", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Buchheit, M. (2008). The 30-15 intermittent fitness test: accuracy for individualizing interval training of young intermittent sport players. Journal of Strength and Conditioning Research, 22(2), 365-374", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Buchheit, M. (2010). The 30-15 intermittent fitness test: 10 year review. Myorobie Journal, 1(9), 278", "s": "İndekslenmeyen", "d": "Myorobie Journal", "n": "dergi — SJR listesinde hiç yok"},
    {"k": "Burr, J. F. et al. (2008). Relationship of physical fitness test results and hockey playing potential in elite-level ice hockey players. Journal of Strength and Conditioning Research, 22(5), 1535-1543", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Buse, G. J. (2006). British Journal of Sports Medicine, 40(2), 169-172", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Bös, K., Schlenker, L., Kunz, R., & Seidel, I. (2010). Motorischer Test fur Nordrhein-Westfalen — Testanleitung (2. Aufl.). Ministerium fur Familie, Kinder, Jugend, Kultur und Sport des Landes NRW / Forschungszentrum fur den Schulsport (FoSS), Karlsruhe. Ayni test ogeleri: Bös, K. et al. (2009). Deutscher Motorik-Test 6-18 (DMT 6-18). Hamburg: Czwalina. — Normlar Almanya temsili MoMo calismasi ve 'Fitness in der Grundschule' arastirmasindan hesaplanmistir; sinif sinirlari yuzdelik dilimlere (P20/P40/P60/P80) karsilik gelir. NOT: Norm kaynagi DMT'nin orta cizgili alan uzerinde yapilan yan sicrama protokoludur; KMS 3-6 versiyonunda 2 cm yuksekliginde tahta engel kullanilir — skorlama (15 sn gecerli sicrama sayisi) ayni olmakla birlikte kucuk bir protokol farki vardir", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Cadenas-Sanchez, C. et al. (2016). Assessing physical fitness in preschool children: feasibility and reliability of the PREFIT battery. Journal of Science and Medicine in Sport, 19(11), 910-915", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Can, İ., & Bayrakdaroğlu, S. (2019). Türk milli boksör ve kickbokscularda üst vücut kuvvet özelliği ve bench throw hareketi esnasındaki bazı parametrelerin karşılaştırılması. CBÜ Beden Eğitimi ve Spor Bilimleri Dergisi, 14(1), 121-128", "s": "Belirlenemedi", "d": "CBÜ Beden Eğitimi ve Spor Bilimleri Dergisi", "n": "yalnız protokol bilgi notu (Paket 35); SJR listesinde doğrulanmadı"},
    {"k": "Castagna, C., Impellizzeri, F. M., Rampinini, E., D'Ottavio, S., & Manzi, V. (2008). The Yo-Yo intermittent recovery test in basketball players. Journal of Science and Medicine in Sport, 11(2), 202-208. https://doi.org/10.1016/j.jsams.2007.02.013", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Castro-Piñero, J. et al. (2009). Criterion-related validity of field-based fitness tests in youth. British Journal of Sports Medicine, 43(13), 964-969", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Chaabène, H., Hachana, Y., Franchini, E., Mkaouer, B., & Chamari, K. (2012). Physical and physiological profile of elite karate athletes. Sports Medicine, 42(10), 829-843", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Chovanová, E., Majherová, M., & Bendíková, E. (2023). Level of motor coordination in school-aged children. Physical Activity Review, 11(2)", "s": "Q2", "d": "Physical Activity Review", "n": ""},
    {"k": "Coombs, R., & Garbutt, G. (2002). Developments in the use of the hamstring/quadriceps ratio. Journal of Sports Science and Medicine, 1(3), 56-62", "s": "Q1", "d": "Journal of Sports Science and Medicine", "n": ""},
    {"k": "Cooper, K. H. (1968). A means of assessing maximal oxygen intake. JAMA, 203(3), 201-204", "s": "Q1", "d": "JAMA", "n": ""},
    {"k": "Coppens, E., Laureys, F., Mostaert, M., D'Hondt, E., Deconinck, F. J. A., & Lenoir, M. (2021). Validation of a motor competence assessment tool for children and adolescents (KTK3+) with normative values for 6- to 19-year-olds. Frontiers in Physiology, 12, 652952. (Tablo 4)", "s": "Q2", "d": "Frontiers in Physiology", "n": ""},
    {"k": "Corbin, C. B., Welk, G. J., Corbin, W. R., & Welk, K. A. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423", "s": "Q1", "d": "Research Quarterly for Exercise and Sport", "n": ""},
    {"k": "Crisafulli, A. et al. (2009). JSAMS, 12(6), 639-644", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Crisafulli, A., Vitelli, S., Cappai, I., Milia, R., Tocco, F., Melis, F., & Concu, A. (2009). Physiological responses and energy cost during a simulation of a Muay Thai boxing match. Applied Physiology, Nutrition, and Metabolism, 34(2), 143-150", "s": "Q2", "d": "Applied Physiology, Nutrition and Metabolism", "n": ""},
    {"k": "Croisier, J. L., Ganteaume, S., Binet, J., Genty, M., & Ferret, J. M. (2008). Strength imbalances and prevention of hamstring injury in professional soccer players: a prospective study. American Journal of Sports Medicine, 36(8), 1469-1475", "s": "Q1", "d": "American Journal of Sports Medicine", "n": ""},
    {"k": "Cureton, K. J. et al. (1995). Validation of the one-mile run as a test of aerobic capacity in children. Research Quarterly for Exercise and Sport, 66(4), 402-412", "s": "Q1", "d": "Research Quarterly for Exercise and Sport", "n": ""},
    {"k": "Cuthbert, M. et al. (2019). The effect of specific strength and power training on key physical qualities of elite rugby league players. Journal of Strength and Conditioning Research, 33(10), 2872-2880", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Davis, P. et al. (2013). International Journal of Sports Physiology and Performance, 8(1), 3-12", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Davis, P., Benson, P. R., Pitty, J. D., Connorton, A. J., & Waldock, R. (2015). The activity profile of elite male amateur boxing. International Journal of Sports Physiology and Performance, 10(1), 53-57", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Dell'Isola, A. M. B. et al. (2016). Journal of Strength and Conditioning Research, 30(6), 1766-1772", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Dolci, F., Hart, N. H., Kilding, A. E., Chivers, P., Piggott, B., & Spiteri, T. (2020). Physical and energetic demand of soccer: A brief review. Strength & Conditioning Journal, 42(3), 70-77", "s": "Q1", "d": "Strength and Conditioning Journal", "n": ""},
    {"k": "Drinkwater, E. J., Pyne, D. B., & McKenna, M. J. (2008). Design and interpretation of anthropometric and fitness testing of basketball players. Sports Medicine, 38(7), 565-578", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Duthie, G., Pyne, D., & Hooper, S. (2003). Applied physiology and game analysis of rugby union. Sports Medicine, 33(13), 973-991", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Dvir, Z. (2004). Isokinetics: Muscle testing, interpretation and clinical applications (2nd ed.). Churchill Livingstone", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Ekstrand, J., Hägglund, M., & Waldén, M. (2011). Epidemiology of muscle injuries in professional football (soccer). American Journal of Sports Medicine, 39(6), 1226-1232", "s": "Q1", "d": "American Journal of Sports Medicine", "n": ""},
    {"k": "Erzurum Caf, C. et al. (2019). Physical and physiological characteristics of elite water polo players. Journal of Human Kinetics, 70, 169-178", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Farrell, P. et al. (2009). Ice hockey performance testing battery. Strength and Conditioning Journal, 31(4), 44-49", "s": "Q1", "d": "Strength and Conditioning Journal", "n": ""},
    {"k": "Faude, O., Kindermann, W., & Meyer, T. (2009). Lactate threshold concepts. Sports Medicine, 39(6), 469-490", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Fernandez-Fernandez, J., Sanz-Rivas, D., & Mendez-Villanueva, A. (2009). A review of the activity profile and physiological demands of tennis match play. Strength and Conditioning Journal, 31(4), 15-26", "s": "Q1", "d": "Strength and Conditioning Journal", "n": ""},
    {"k": "Fetz, F., & Kornexl, E. (1993). Sportmotorische Tests (3. Aufl.). Wien: ÖBV", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "FIG (2022). Code of Points. International Gymnastics Federation", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Filimonov, V. I. et al. (1983). Means of increasing strength of the punch. NSCA Journal, 7(6), 65-66", "s": "Q1", "d": "NSCA Journal", "n": ""},
    {"k": "Franchini, E., & Del Vecchio, F. B. (2011). Estudos em modalidades esportivas de combate. Revista Brasileira de Educação Física e Esporte, 25(esp), 67-81", "s": "İndekslenmeyen", "d": "Revista Brasileira de Educação Física e Esporte", "n": "dergi — SJR listesinde hiç yok"},
    {"k": "Franchini, E., Brito, C. J., & Artioli, G. G. (2012). Weight loss in combat sports: physiological, psychological and performance effects. Journal of the International Society of Sports Nutrition, 9(1), 52", "s": "Q1", "d": "Journal of the International Society of Sports Nutrition", "n": ""},
    {"k": "Franchini, E., Del Vecchio, F. B., Matsushigue, K. A., & Artioli, G. G. (2011). Physiological profiles of elite judo athletes. Sports Medicine, 41(2), 147-166", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Franchini, E., Julio, U. F., Panissa, V. L. G., Lira, F. S., Gerosa-Neto, J., & Branco, B. H. M. (2015). Short-term low-volume high-intensity intermittent training is superior to continuous training for fat loss and muscular gains in judo athletes. Journal of Exercise Rehabilitation, 11(5), 261-269", "s": "Q2", "d": "Journal of Exercise Rehabilitation", "n": ""},
    {"k": "Franchini, E., Nakamura, F. Y., Takito, M. Y., Kiss, M. A., & Sterkowicz, S. (1998). Specific fitness test development for judo. Revista Brasileira de Medicina do Esporte, 4(3), 73-77", "s": "İndekslenmeyen", "d": "Revista Brasileira de Medicina do Esporte", "n": "dergi — SJR 2025 listesinde yok (son SJR yılı 2023, 'discontinued')"},
    {"k": "Franchini, E., Sterkowicz, S., Meira Jr, C. M., Gomes, F. R., & Tani, G. (2011). Technical variation in a sample of high level judo players. Perceptual and Motor Skills, 112(3), 768-776", "s": "Q3/Q4", "d": "Perceptual and Motor Skills", "n": "en iyi çeyrek Q3"},
    {"k": "Fry, R. W., & Morton, A. R. (1991). Physiological and kinanthropometric attributes of elite flatwater kayakists. Medicine & Science in Sports & Exercise, 23(11), 1297-1301", "s": "Q1", "d": "Medicine & Science in Sports & Exercise", "n": ""},
    {"k": "Gabbet, T. J. (2010). The development of a test of repeated-sprint ability for elite women's soccer players. Journal of Strength and Conditioning Research, 24(5), 1191–1194", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Gabbett, T. et al. (2006). International Journal of Sports Physiology and Performance, 1(3), 269-279", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Gabbett, T. J. (2005). Science of rugby league football: a review. Journal of Sports Sciences, 23(9), 961-976", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Gabbett, T. J., & Georgieff, B. (2007). Physiological and anthropometric characteristics of junior national, state, and novice volleyball players. Journal of Strength and Conditioning Research, 21(3), 902-908", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Gabbett, T. J., Jenkins, D. G., & Abernethy, B. (2012). Physical demands of professional rugby league training and competition using microtechnology. Journal of Science and Medicine in Sport, 15(1), 80-86", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Gabbett, T., Georgieff, B., Anderson, S., Cotton, B., Savovic, D., & Nicholson, L. (2006). Changes in skill and physical fitness following training in talent-identified volleyball players. Journal of Strength and Conditioning Research, 20(1), 29-35", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Garkavy, G. A. (2007). Physical preparation of sambo wrestlers. Theory and Practice of Physical Culture, 9, 45-48", "s": "Q3/Q4", "d": "Theory and Practice of Physical Culture", "n": "en iyi çeyrek Q4"},
    {"k": "Garstecki, M. A., Latin, R. W., & Cuppett, M. M. (2004). Comparison of selected physical fitness and performance variables between NCAA Division I and II football players. Journal of Strength and Conditioning Research, 18(2), 292-297", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Girard, O., Mendez-Villanueva, A., & Bishop, D. (2011). Repeated-sprint ability — part I: factors contributing to fatigue. Sports Medicine, 41(8), 673–694", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Giuriato, M., Biino, V., Bellafiore, M., Battaglia, G., Palma, A., Baldari, C., Guidetti, L., Gallotta, M. C., Schena, F., & Lanza, M. (2021). Gross motor coordination: We have a problem! A study with the Körperkoordinations Test für Kinder in youth (6-13 years). Frontiers in Pediatrics, 9, 785990. https://doi.org/10.3389/fped.2021.785990", "s": "Q1", "d": "Frontiers in Pediatrics", "n": ""},
    {"k": "Haff, G. G. et al. (2015). Force-time curve characteristics of dynamic and isometric muscle actions. Journal of Strength and Conditioning Research, 19(4), 741-748", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Haff, G. G., & Triplett, N. T. (2016). Essentials of Strength Training and Conditioning (4th ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Haugen, T. et al. (2022). IJSPP, 17(4), 505-507", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Hayes, P. R., & Quinn, M. D. (2009). A mathematical model for quantifying training. European Journal of Applied Physiology, 107(4), 517-522", "s": "Q1", "d": "European Journal of Applied Physiology", "n": ""},
    {"k": "Hermens, H. J. et al. (2000). Development of recommendations for SEMG sensors and sensor placement procedures. Journal of Electromyography and Kinesiology, 10(5), 361-374", "s": "Q2", "d": "Journal of Electromyography and Kinesiology", "n": ""},
    {"k": "Heyward, V. H. (2010). Advanced Fitness Assessment (6th ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Hoare, D. G. (2000). Predicting success in junior elite basketball players: the contribution of anthropometric and physiological attributes. Journal of Science and Medicine in Sport, 3(4), 391-405", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Hoffmann, M. D., et al. (2019). Canadian Health Measures Survey. Health Reports, 30(10), 14-22. (20-69 yaş)", "s": "Q1", "d": "Health Reports", "n": ""},
    {"k": "IAAF (2023). World Athletics Performance Standards", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Côté, J., Lidor, R., & Hackfort, D. (2009). ISSP position stand: To sample or to specialize? Seven postulates about youth sport activities that lead to continued participation and elite performance. International Journal of Sport and Exercise Psychology, 7(1), 7-17", "s": "Q1", "d": "International Journal of Sport and Exercise Psychology", "n": ""},
    {"k": "IWF Technical and Competition Rules (2022). International Weightlifting Federation", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Jeanguyot, N. et al. (2023). JSAMS, 26(4), 215-222", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Johnson, B. L., & Nelson, J. K. (1986). Practical measurements for evaluation in physical education (4th ed.). Minneapolis, MN: Burgess", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Keytsman, C., Verbrugghe, J., & Eijnde, B. O. (2024). The isometric and isokinetic knee extension and flexion muscle strength profile of elite soccer players. BMC Sports Science, Medicine and Rehabilitation, 16(1), 180. https://doi.org/10.1186/s13102-024-00961-y", "s": "Q1", "d": "BMC Sports Science, Medicine and Rehabilitation", "n": ""},
    {"k": "Kiphard, E. J., & Schilling, F. (2007). Körperkoordinationstest für Kinder (KTK), 2. Auflage. Beltz Test GmbH, Weinheim", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Kirk, C., Clark, D. R., Langan-Evans, C., & Morton, J. P. (2020). The physical demands of mixed martial arts: a systematic review using perceived exertion scores. Physiology & Behavior, 225, 113-125", "s": "Q2", "d": "Physiology & Behavior", "n": ""},
    {"k": "Kolimechkov, S., Petrov, L., & Alexandrova, A. (2019). Alpha-fit test battery norms for children and adolescents from 5 to 18 years of age obtained by a linear interpolation of existing European physical fitness references. European Journal of Physical Education and Sport Science, 5(4), 1-14. https://doi.org/10.5281/zenodo.2546360 — Temel veri: Miguel-Etayo et al. (2014) IDEFICS (n=18.745, 6-9.9 yas) + Ortega et al. (2011) HELENA (n=3.428, 13-17 yas); 9.9-12.9 yas araligi orijinal yazarlarca linear enterpolasyonla doldurulmustur. NOT: kaynaktaki yuzdelik sutunlari performans siralamasi yonundedir (P1=en yavas, P100=en hizli); bu veri bizim ham-deger persentil kurallmiza (dusuk sure = dusuk persentil) donusturulerek islenmis, P5/P95 kaynaktaki P3-P10 ve P90-P97 arasindan linear enterpolasyonla hesaplanmistir", "s": "İndekslenmeyen", "d": "", "n": "veri seti (Zenodo)"},
    {"k": "Korhonen, R. K. et al. (2022). Reliability and validity of the NordBord for hamstring muscle strength assessment. Journal of Strength and Conditioning Research, 36(4), 934-940", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Koropanovski, N., Berjan, B., Bozic, P. R., Pazin, N., Sanader, A., Jovanovic, S., & Jaric, S. (2011). Anthropometric and physical performance profiles of elite karate kumite and kata competitors. Journal of Human Kinetics, 30, 107-114. https://doi.org/10.2478/v10078-011-0078-x", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Kovacs, M. S. (2007). Tennis physiology: training the competitive athlete. Sports Medicine, 37(3), 189-198", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Kyle, U. G. et al. (2004). Bioelectrical impedance analysis — part I: review of principles and methods. Clinical Nutrition, 23(5), 1226-1243", "s": "Q1", "d": "Clinical Nutrition", "n": ""},
    {"k": "Latorre-Román, P. A. et al. (2017). Physical fitness in preschool children. European Journal of Pediatrics, 176(3), 365-371", "s": "Q1", "d": "European Journal of Pediatrics", "n": ""},
    {"k": "Latorre-Román, P. A., Mora-López, D., & García-Pinillos, F. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526", "s": "Scopus (çeyreklik dışı)", "d": "Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte", "n": "SJR 2025 listesinde, çeyreği yok (dergi 'discontinued' olarak işaretli)"},
    {"k": "Lawton, T. W., Cronin, J. B., & McGuigan, M. R. (2011). Strength testing and training of rowers: a review. Sports Medicine, 41(5), 413-432", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Longmuir, P. E. et al. (2018). CAPL-2: Canadian Assessment of Physical Literacy, Second Edition. Healthy Active Living and Obesity Research Group, CHEO Research Institute", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Longmuir, P. E., Boyer, C., Lloyd, M., Yang, Y., McGarry, J., Borghese, M. M., & Tremblay, M. S. (2015). The Canadian Assessment of Physical Literacy: methods for children in grades 4 to 6 (8 to 12 years). BMC Public Health, 15(1), 1-11", "s": "Q1", "d": "BMC Public Health", "n": ""},
    {"k": "Lopes-Silva, J. P. et al. (2021). Uchi-komi fitness test for monitoring judo-specific physical fitness. International Journal of Sports Physiology and Performance, 16(3), 430-436", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Loturco, I. et al. (2016). Strength and power qualities are highly associated with swimming performance in elite competitive swimmers with physical disability. Journal of Strength and Conditioning Research, 30(7), 2007-2014", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Lubans, D. R., Morgan, P. J., Cliff, D. P., Barnett, L. M., & Okely, A. D. (2010). Fundamental movement skills in children and adolescents: review of associated health benefits. Sports Medicine, 40(12), 1019-1035", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Lucia, A. et al. (2001). Sports Medicine, 31(5), 325-337", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Léger, L. A., Mercier, D., Gadoury, C., & Lambert, J. (1988). The multistage 20 metre shuttle run test for aerobic fitness. Journal of Sports Sciences, 6(2), 93-101", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Mackala, K., & Mero, A. (2013). A kinematic analysis of three best 100m performances ever. Journal of Human Kinetics, 36, 149-160", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Mahar, M. T. et al. (2006). Development and validation of a regression model to estimate VO2peak from PACER. Journal of Physical Activity and Health, 3(s2), S34-S46", "s": "Q1", "d": "Journal of Physical Activity and Health", "n": ""},
    {"k": "Malcolm, R., & Mahony, N. (2018). Rowing physiology and performance testing. British Journal of Sports Medicine, 52(3), 150-155", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Malina, R. M. (2007). Body composition in athletes: assessment and estimated fatness. Clinics in Sports Medicine, 26(1), 37-68", "s": "Q2", "d": "Clinics in Sports Medicine", "n": ""},
    {"k": "Marcelino, R. et al. (2014). Volleyball game related statistics that discriminate between winning and losing teams. Journal of Sports Science and Medicine, 13(1), 24-31", "s": "Q1", "d": "Journal of Sports Science and Medicine", "n": ""},
    {"k": "Markovic, G. (2007). Does plyometric training improve vertical jump height? British Journal of Sports Medicine, 41(6), 349-355", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Markovic, M., Dopsaj, M., Kasum, G. et al. (2017). Reliability of the two new specific wrestling tests. Archives of Budo, 13, 17–28", "s": "Q3/Q4", "d": "Archives of Budo", "n": "en iyi çeyrek Q3"},
    {"k": "Marković, M., Kukić, F., Dopsaj, M., Kasum, G., Toskić, L., & Zarić, I. (2021). Validity of a novel specific wrestling fitness test. Journal of Strength and Conditioning Research, 35(12S), S51–S57", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "McGee, K. J., & Burkett, L. N. (2003). The National Football League combine: a reliable predictor of draft status? Journal of Strength and Conditioning Research, 17(1), 6-11", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Merletti, R., & Farina, D. (2016). Surface Electromyography: Physiology, Engineering and Applications. Wiley-IEEE Press", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Meylan, C. M., Cronin, J. B., Oliver, J. L., Hopkins, W. G., & Contreras, B. (2014). The effect of maturation on adaptations to strength training and detraining in 11–15-year-olds. Scandinavian Journal of Medicine & Science in Sports, 24(3), e156-e164", "s": "Q1", "d": "Scandinavian Journal of Medicine & Science in Sports", "n": ""},
    {"k": "Michalsik, L. B., Madsen, K., & Aagaard, P. (2015). Technical activity profile and influence of body anthropometry on playing performance in male elite team handball. Journal of Strength and Conditioning Research, 29(2), 416-428", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Midgley, A. W. et al. (2007). Sports Medicine, 37(2), 117-132", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Mirzaei, B. et al. (2009). Journal of Human Kinetics, 21, 73-79", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Moeskops, S., Oliver, J. L., Read, P. J., Cronin, J. B., Myer, G. D., & Lloyd, R. S. (2019). The physiological demands of youth artistic gymnastics: applications to strength and conditioning. Strength and Conditioning Journal, 41(1), 1-13", "s": "Q1", "d": "Strength and Conditioning Journal", "n": ""},
    {"k": "Mohr, M. et al. (2014). Physiological responses to elite team handball. Scandinavian Journal of Medicine & Science in Sports, 24(6), 994-1001", "s": "Q1", "d": "Scandinavian Journal of Medicine & Science in Sports", "n": ""},
    {"k": "Montgomery, P. G., Pyne, D. B., & Minahan, C. L. (2010). The physical and physiological demands of basketball training and competition. International Journal of Sports Physiology and Performance, 5(1), 75-86", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Moon, J. R. (2013). Body composition in athletes and sports nutrition. Proceedings of the Nutrition Society, 72(3), 325-333", "s": "Q1", "d": "Proceedings of the Nutrition Society", "n": ""},
    {"k": "Morais, J. E., Silva, A. J., Marinho, D. A., Seifert, L., & Barbosa, T. M. (2019). Cluster analysis of the kinematics of young swimmers' technique during the front-crawl. International Journal of Performance Analysis in Sport, 19(2), 229-246", "s": "Q2", "d": "International Journal of Performance Analysis in Sport", "n": ""},
    {"k": "Morassutti, O. N., van Wyk, P. M., & Duquette, A. M. (2025). Vertical jumping power normative-reference values: Utilizing a large cohort of Canadian university students. Biomedical Human Kinetics, 17, 147-157", "s": "Belirlenemedi", "d": "Biomedical Human Kinetics", "n": "Sargent örneklemi (Kademe 2, Paket 36); SJR listesinde doğrulanmadı"},
    {"k": "Morin, J. B., & Samozino, P. (2016). Interpreting power-force-velocity profiles for individualized and specific training. International Journal of Sports Physiology and Performance, 11(2), 267-272", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Morrow, J. R., Beets, M. W., & Welk, G. J. (2013). Reliability and validity of FitnessGram. American Journal of Preventive Medicine, 44(1S1), S12-S20", "s": "Q1", "d": "American Journal of Preventive Medicine", "n": ""},
    {"k": "Nana, A. et al. (2015). Methodology review: using dual-energy X-ray absorptiometry (DXA) for the assessment of body composition in athletes. International Journal of Sport Nutrition and Exercise Metabolism, 25(2), 198-215", "s": "Q1", "d": "International Journal of Sport Nutrition and Exercise Metabolism", "n": ""},
    {"k": "NBA Draft Combine Official Test Protocols (2023). NBA Basketball Operations", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Nicholas, C. W., Nuttall, F. E., & Williams, C. (2000). The Loughborough Intermittent Shuttle Test: a field test that simulates the activity pattern of soccer. Journal of Sports Sciences, 18(2), 97–104", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Nikolaidis, P. T. et al. (2018). Journal of Human Kinetics, 61, 95-105", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric characteristics, physical fitness and motor coordination of 9 to 11 year old children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. https://doi.org/10.1371/journal.pone.0126282 — Tablo 1-3", "s": "Q1", "d": "PLoS One", "n": ""},
    {"k": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children: the PREFIT battery. Sports Medicine, 45(8), 1125-1155", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Ouergui, I., Hammouda, O., Chtourou, H., Gmada, N., & Franchini, E. (2014). Physiological responses and time-motion analysis of kickboxing competition. Journal of Strength and Conditioning Research, 28(12), 3340-3347", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Patrick, D. G. et al. (1999). Criterion-referenced health standards for back saver sit and reach. Research Quarterly for Exercise and Sport, 70(4), 423-427", "s": "Q1", "d": "Research Quarterly for Exercise and Sport", "n": ""},
    {"k": "Pauole, K., Madole, K., Garhammer, J., Lacourse, M., & Rozenek, R. (2000). Reliability and validity of the T-test as a measure of agility, leg power, and leg speed in college-aged men and women. Journal of Strength and Conditioning Research, 14(4), 443-450", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Payne, N., Gledhill, N., Katzmarzyk, P. T., & Jamnik, V. (2000). Canadian musculoskeletal fitness norms. Canadian Journal of Applied Physiology, 25(6), 430-442. (20-69 yas)", "s": "Q2", "d": "Canadian Journal of Applied Physiology", "n": ""},
    {"k": "Peyer, K. L., Pivarnik, J. M., Eisenmann, J. C., & Vorkapich, M. (2011). Physiological characteristics of National Hockey League (NHL) draft picks. Journal of Strength and Conditioning Research, 25(9), 2365-2369", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Pyne, D. B., & Sharp, R. L. (2014). Physical and energy requirements of competitive swimming events. International Journal of Sport Nutrition and Exercise Metabolism, 24(4), 351-359", "s": "Q1", "d": "International Journal of Sport Nutrition and Exercise Metabolism", "n": ""},
    {"k": "Marzano-Felisatti, J. M., Pino-Ortega, J., Priego-Quesada, J. I., Guzmán-Luján, J. F., & García-de-Alcaraz, A. (2025). Physical performance and game demands in beach volleyball: A systematic review. Journal of Human Sport and Exercise, 20(1), 79-92. https://doi.org/10.55860/g1z4az52", "s": "Q3/Q4", "d": "Journal of Human Sport and Exercise", "n": "en iyi çeyrek Q3"},
    {"k": "Placek, J. et al. (2020). Fitness characteristics of elite table tennis players. Journal of Human Kinetics, 72, 175-184", "s": "Q1", "d": "Journal of Human Kinetics", "n": ""},
    {"k": "Platanou, T. (2005). On-water and dryland vertical jump in water polo players. Journal of Sports Medicine and Physical Fitness, 45(1), 26-31", "s": "Q2", "d": "Journal of Sports Medicine and Physical Fitness", "n": ""},
    {"k": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Poole, D. C., & Jones, A. M. (2017). Measurement of the maximum oxygen uptake (VO2max): VO2peak is no longer acceptable. Journal of Applied Physiology, 122(4), 997-1002", "s": "Q1", "d": "Journal of Applied Physiology", "n": ""},
    {"k": "Price, T., Cimadoro, G., & Legg, H. S. (2024). Physical performance determinants in competitive youth swimmers: a systematic review. BMC Sports Science, Medicine and Rehabilitation, 16, 20", "s": "Q1", "d": "BMC Sports Science, Medicine and Rehabilitation", "n": ""},
    {"k": "Pritchard, H. J., Phelan, L., & Hopkins, W. G. (2020). Validity and reliability of the critical swimming speed test. Journal of Science and Medicine in Sport, 23(11), 1067-1071", "s": "Q1", "d": "Journal of Science and Medicine in Sport", "n": ""},
    {"k": "Raya, M. A., et al. (2013). Journal of Orthopaedic & Sports Physical Therapy, 43(7), 444-452", "s": "Q1", "d": "Journal of Orthopaedic & Sports Physical Therapy", "n": ""},
    {"k": "Reid, M., Elliott, B., & Crespo, M. (2013). Mechanics and learning practices associated with the tennis forehand: a review. Journal of Sports Science and Medicine, 12(2), 225-231", "s": "Q1", "d": "Journal of Sports Science and Medicine", "n": ""},
    {"k": "Roetert, E. P., & Ellenbecker, T. S. (2007). Complete conditioning for tennis (2nd ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Ruiz, J. R., Castro-Piñero, J., España-Romero, V., Artero, E. G., Ortega, F. B., Cuenca, M. M., ... & Castillo, M. J. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery for children and adolescents. British Journal of Sports Medicine, 45(6), 518-524", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Saltin, B., & Åstrand, P. O. (1967). JAP, 23(3), 353-358", "s": "Q1", "d": "Journal of Applied Physiology", "n": ""},
    {"k": "Samozino, P. et al. (2012). Optimal force-velocity profile in ballistic movements. Medicine & Science in Sports & Exercise, 44(2), 313-322", "s": "Q1", "d": "Medicine & Science in Sports & Exercise", "n": ""},
    {"k": "Santos, R., Mota, J., Santos, D. A., Silva, A. M., Baptista, F., & Sardinha, L. B. (2014). Physical fitness percentiles for Portuguese children and adolescents aged 10-18 years. Journal of Sports Sciences, 32(16), 1510-1518. https://doi.org/10.1080/02640414.2014.906046", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Sargent, D. A. (1921). The physical test of a man. American Physical Education Review, 26, 188-194", "s": "Belirlenemedi", "d": "American Physical Education Review", "n": "Sargent dikey sıçrama testinin orijinal kaynağı (Paket 35c); SJR listesinde doğrulanmadı"},
    {"k": "Seitz, L. B. et al. (2014). Journal of Strength and Conditioning Research, 28(2), 401-409", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Sheppard, J. M., & Young, W. B. (2006). Agility literature review: Classifications, training and testing. Journal of Sports Sciences, 24(9), 919–932", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Sheppard, J. M., Gabbett, T. J., & Stanganelli, L. C. R. (2009). An analysis of playing positions in elite men's volleyball: considerations for competition demands and physiologic characteristics. Journal of Strength and Conditioning Research, 23(6), 1858-1866", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Siri, W. E. (1956). The gross composition of the body. Advances in Biological and Medical Physics, 4, 239-280", "s": "İndekslenmeyen", "d": "Advances in Biological and Medical Physics", "n": "künye PDF ile doğrulandı; 1956 tarihli derleme dizisi, SJR 1999 öncesini kapsamıyor. Yaygın 4.95/D − 4.50 hali Siri (1961) bölümüne atfedilir, görülmedi"},
    {"k": "Sjödin, B., & Jacobs, I. (1981). Onset of blood lactate accumulation and marathon running performance. International Journal of Sports Medicine, 2(01), 23-26", "s": "Q1", "d": "International Journal of Sports Medicine", "n": ""},
    {"k": "Slater, L. V. et al. (2019). Journal of Strength and Conditioning Research, 33(11), 3064-3073", "s": "Q1", "d": "Journal of Strength and Conditioning Research", "n": ""},
    {"k": "Slaughter, M. H. et al. (1988). Skinfold equations for estimation of body fatness in children and youth. Human Biology, 60(5), 709-723", "s": "Q3/Q4", "d": "Human Biology", "n": "en iyi çeyrek Q4"},
    {"k": "Sleivert, G., & Taingahue, M. (2004). The relationship between maximal jump-squat power and sprint acceleration in athletes. European Journal of Applied Physiology, 91(1), 46-52", "s": "Q1", "d": "European Journal of Applied Physiology", "n": ""},
    {"k": "Stein, C. J., Gans, I., Griffith, K., Kinderknecht, J., Yates, B., & Micheli, L. J. (2021). Hamstring injury prevention in youth soccer using the Nordic hamstring exercise. Orthopaedic Journal of Sports Medicine, 9(3), 2325967121989169", "s": "Q1", "d": "Orthopaedic Journal of Sports Medicine", "n": ""},
    {"k": "Stølen, T. et al. (2005). Sports Medicine, 35(6), 501-536", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Suchomel, T. J., Nimphius, S., & Stone, M. H. (2016). The importance of muscular strength in athletic performance. Sports Medicine, 46(10), 1419-1449", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Sun, H. et al. (2014). Physical fitness of children and adolescents in China. Journal of Sport and Health Science, 3(4), 263-267", "s": "Q1", "d": "Journal of Sport and Health Science", "n": ""},
    {"k": "Tabben, M. et al. (2015). Physiological and fitness differences between karate and judo. Journal of Sports Sciences, 33(8), 819-826", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Shaw, J. W., Mattiussi, A. M., Brown, D. D., Springham, M., Pedlar, C. R., & Tallent, J. (2021). The activity demands and physiological responses observed in professional ballet: A systematic review. The Journal of Sport and Exercise Science, 5(4), 254-269. https://doi.org/10.36905/jses.2021.04.04", "s": "İndekslenmeyen", "d": "The Journal of Sport and Exercise Science", "n": "dergi — SJR listesinde hiç yok"},
    {"k": "The Cooper Institute (2017). FitnessGram Administration Manual (5th ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Phomsoupha, M., & Laffaye, G. (2015). The science of badminton: game characteristics, anthropometry, physiology, visual fitness and biomechanics. Sports Medicine, 45(4), 473-495", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Tomkinson, G. R., et al. (2018). European normative values for physical fitness in children and adolescents aged 9-17 years. British Journal of Sports Medicine, 52(22), 1445-1456. (ölçek: 15 cm = ayak parmakları)", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Tomkinson, G. R., Lang, J. J., Blanchard, J., et al. (2023). European normative values for standing broad jump (FitBack network). British Journal of Sports Medicine, 57(5), 299-310. https://doi.org/10.1136/bjsports-2022-106176", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Tomkinson, G. R., Lang, J. J., Tremblay, M. S., et al. (2017). International normative 20 m shuttle run values from 1 142 026 children and youth representing 50 countries. British Journal of Sports Medicine, 51(21), 1545-1554. https://doi.org/10.1136/bjsports-2016-095987", "s": "Q1", "d": "British Journal of Sports Medicine", "n": ""},
    {"k": "Toubekis, A. G., Tsami, A. P., & Tokmakidis, S. P. (2006). Critical velocity and lactate threshold in young swimmers. International Journal of Sports Medicine, 27(2), 117-123", "s": "Q1", "d": "International Journal of Sports Medicine", "n": ""},
    {"k": "Tremblay, M. S. et al. (2011). Canadian Physical Activity Guidelines for Children. Applied Physiology, Nutrition and Metabolism, 36(1), 59-64", "s": "Q2", "d": "Applied Physiology, Nutrition and Metabolism", "n": ""},
    {"k": "Tsigilis, N., Douda, H., & Tokmakidis, S. P. (2001). Test-retest reliability of the Eurofit test battery. Perceptual and Motor Skills, 92(3), 1295-1300", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "van Someren, K. A., & Palmer, G. S. (2003). Prediction of 200-m sprint kayaking performance. Canadian Journal of Applied Physiology, 28(4), 505-517", "s": "Q2", "d": "Canadian Journal of Applied Physiology", "n": ""},
    {"k": "Vandorpe, B., Vandendriessche, J., Lefevre, J., et al. (2011). The KörperkoordinationsTest für Kinder: reference values and suitability for 6-12-year-old children in Flanders. Scandinavian Journal of Medicine & Science in Sports, 21(3), 378-388", "s": "Q1", "d": "Scandinavian Journal of Medicine & Science in Sports", "n": ""},
    {"k": "Viana, E., Bentley, D. J., & Logan-Sprenger, H. M. (2019). A physiological overview of the demands, characteristics, and adaptations of highly trained artistic swimmers: a literature review. Sports Medicine - Open, 5, 16", "s": "Q1", "d": "Sports Medicine - Open", "n": ""},
    {"k": "Wakayoshi, K., Yoshida, T., Udo, M., Kasai, T., Moritani, T., Mutoh, Y., & Miyashita, M. (1992). A simple method for determining critical speed as swimming fatigue threshold in competitive swimming. International Journal of Sports Medicine, 13(5), 367-371", "s": "Q1", "d": "International Journal of Sports Medicine", "n": ""},
    {"k": "Wang, Y. C., et al. (2025). iGRIPS: International norms for adult handgrip strength. Journal of Sport and Health Science. (20+ yaş)", "s": "Q1", "d": "Journal of Sport and Health Science", "n": ""},
    {"k": "Wasserman, K. et al. (2005). Principles of Exercise Testing and Interpretation (4th ed.). Lippincott Williams & Wilkins", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Welk, G. J., & Meredith, M. D. (Eds.). (2008). FitnessGram/ActivityGram Test Administration Manual (4th ed.). Human Kinetics", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Whitehead, M. (2010). Physical literacy: Throughout the lifecourse. Routledge", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Wilkinson, M., Leedale-Brown, D., & Winter, E. M. (2009). Validity of a squash-specific fitness test. International Journal of Sports Physiology and Performance, 4(1), 29-40", "s": "Q1", "d": "International Journal of Sports Physiology and Performance", "n": ""},
    {"k": "Worth, A., & Bös, K. (2015). Das Karlsruher Motorik-Screening für Kindergartenkinder (KMSK). Motorik, 38(1), 15-22", "s": "İndekslenmeyen", "d": "", "n": "kitap / kurum kılavuzu / el kitabı"},
    {"k": "Yoon, J. (2002). Physiological profiles of elite senior wrestlers. Sports Medicine, 32(4), 225-233", "s": "Q1", "d": "Sports Medicine", "n": ""},
    {"k": "Zagatto, A. M. et al. (2010). Journal of Sports Sciences, 28(1), 71-79", "s": "Q1", "d": "Journal of Sports Sciences", "n": ""},
    {"k": "Zhou, B. F. (2002). Predictive values of body mass index and waist circumference for risk factors of certain related diseases in Chinese adults. Biomedical and Environmental Sciences, 15(1), 83-96", "s": "Q2", "d": "Biomedical and Environmental Sciences", "n": ""},
    {"k": "Özer, B. K., & Özdemir, A. (2020). Secular changes in anthropometric measurements of schoolchildren in Ankara, Turkey (1950–2017). Papers on Anthropology, 29(1), 121-139. https://doi.org/10.12697/poa.2020.29.1.09 (Tablo 3-4, 2017 taraması)", "s": "İndekslenmeyen", "d": "Papers on Anthropology", "n": "dergi — SJR listesinde hiç yok"},
]

DUNYA_REKORU = {
    "100m Sprint (sn)": {
        "Erkek": {"deger": 9.58, "sahibi": "Usain Bolt (JAM)", "yil": 2009, "etkinlik": "DS Berlin"},
        "Kadın": {"deger": 10.49, "sahibi": "Florence Griffith-Joyner (USA)", "yil": 1988, "etkinlik": "ABD Trialları"},
        "olimpiyat_Erkek": {"deger": 9.63, "sahibi": "Usain Bolt (JAM)", "yil": 2012},
        "olimpiyat_Kadın": {"deger": 10.61, "sahibi": "E. Thompson-Herah (JAM)", "yil": 2021},
        "kaynak_notu": "resmi",
    },
    "200m Sprint (sn)": {
        "Erkek": {"deger": 19.19, "sahibi": "Usain Bolt (JAM)", "yil": 2009, "etkinlik": "DS Berlin"},
        "Kadın": {"deger": 21.34, "sahibi": "Florence Griffith-Joyner (USA)", "yil": 1988, "etkinlik": "Seul Olimpiyatları"},
        "olimpiyat_Erkek": {"deger": 19.30, "sahibi": "Usain Bolt (JAM)", "yil": 2008},
        "kaynak_notu": "resmi",
    },
    "400m Sprint (sn)": {
        "Erkek": {"deger": 43.03, "sahibi": "Wayde van Niekerk (RSA)", "yil": 2016, "etkinlik": "Rio Olimpiyatları"},
        "Kadın": {"deger": 47.60, "sahibi": "Marita Koch (GDR)", "yil": 1985, "etkinlik": "Canberra"},
        "kaynak_notu": "resmi",
    },
    "10m Sprint (sn)": {
        "Erkek": {"deger": 1.61, "sahibi": "Usain Bolt (tahmini - 100m WR bölüm analizi)", "yil": 2009},
        "kaynak_notu": "tahmini",
    },
    "20m Sprint (sn)": {
        "Erkek": {"deger": 2.63, "sahibi": "Usain Bolt (tahmini - 100m WR bölüm analizi)", "yil": 2009},
        "kaynak_notu": "tahmini",
    },
    "30m Sprint En İyi (sn)": {
        "Erkek": {"deger": 3.78, "sahibi": "Usain Bolt (tahmini - bölüm analizi)", "yil": 2009},
        "kaynak_notu": "tahmini",
    },
    "CMJ En İyi (cm)": {
        "Erkek": {"deger": 99.0, "sahibi": "Brett Williams (AUS) - Guinness rekoru", "yil": 2019},
        "Kadın": {"deger": 72.0, "sahibi": "Kayıtlı en yüksek - literatür", "yil": 2012},
        "kaynak_notu": "resmi",
    },
    "SJFT İndeksi": {
        "Erkek": {"deger": 9.0, "sahibi": "Elit DS judocular (Franchini meta-analizi)", "yil": 2019},
        "Kadın": {"deger": 11.0, "sahibi": "Elit DS judocular", "yil": 2014},
        "kaynak_notu": "tahmini",
    },
    "Illinois Çeviklik En İyi (sn)": {
        "Erkek": {"deger": 13.3, "sahibi": "Kayıtlı en iyi - elit sporcu", "yil": 2020},
        "Kadın": {"deger": 15.2, "sahibi": "Kayıtlı en iyi - elit sporcu", "yil": 2020},
        "kaynak_notu": "tahmini",
    },
}

ACIKLAMALAR = {
    # Paket 35: Genel Kuvvet Rafı — rölatif değerler girilmez, kayıtlı vücut ağırlığından hesaplanır
    "1RM Bench Press (kg)": "Tam hareket açıklığında başarıyla kaldırılan en yüksek yük (kg)",
    "1RM Squat (kg)": "Diz açısı 90°'yi geçen derinlikte başarıyla kaldırılan en yüksek yük (kg)",
    "1RM Leg Press (kg)": "Belirlenen hareket açıklığında başarıyla itilen en yüksek yük (kg); makine tipini notlara yazın",
    "Barfiks (tekrar)": "Tam açık asılıdan çene barın üstüne doğru formda tamamlanan tekrar sayısı",
    "Şınav (tekrar)": "Ara vermeden, doğru formda tamamlanan şınav sayısı",
    "Mekik (tekrar)": "1 dakikada tamamlanan doğru mekik sayısı",
    "Periyot 1 Atış Sayısı": "1. turda yapılan suplex atış sayısı (0-30 sn)",
    "Periyot 2 Atış Sayısı": "2. turda yapılan suplex atış sayısı (50-80 sn)",
    "Periyot 3 Atış Sayısı": "3. turda yapılan suplex atış sayısı (100-130 sn)",
    "Periyot 1 Atış": "1. periyotta yapılan atış sayısı",
    "Periyot 2 Atış": "2. periyotta yapılan atış sayısı",
    "Periyot 3 Atış": "3. periyotta yapılan atış sayısı",
    "HR0 (bpm)": "Test bitiminde ölçülen kalp atım hızı (atım/dakika)",
    "HR1-dk (bpm)": "Testten 1 dakika sonra ölçülen kalp atım hızı (atım/dakika)",
    "Manken Ağırlığı (kg)": "Otomatik belirlendi — <75 kg: 22 kg · 75–89.99 kg: 27 kg · ≥90 kg: 32 kg",
    "Deneme 1 (sn)": "1. deneme süresi (saniye)",
    "Deneme 2 (sn)": "2. deneme süresi (saniye)",
    "Deneme 3 (sn)": "3. deneme süresi (saniye)",
    "Deneme 1 (cm)": "1. deneme mesafesi (santimetre)",
    "Deneme 2 (cm)": "2. deneme mesafesi (santimetre)",
    "Deneme 3 (cm)": "3. deneme mesafesi (santimetre)",
    "Pik Güç (W)": "Wingate testinde ulaşılan maksimal güç (Watt)",
    "Ortalama Güç (W)": "30 saniyelik testteki ortalama güç (Watt)",
    "Min Güç (W)": "Test sonundaki minimum güç (Watt)",
    "Tamamlanan Mesafe (m)": "Kat edilen toplam mesafe (metre)",
    "Son Seviye": "Bip testinde ulaşılan son seviye numarası",
    "Koşulan Süre (dk)": "Eurofit skoru: bırakılan ana kadar koşulan süre, 0.5 dk hassasiyetle (ör. 5.5). Seviyeden otomatik çevrilmez",
    "Son Tekrar": "Son seviyede tamamlanan tekrar sayısı",
    "Düşme Sayısı (1 dk)": "1 dakikada denge kaybı sayısı — az = iyi",
    "Dominant Ayak (Sağ/Sol)": "Testte kullanılan baskın ayak",
    "RPE Periyot 1 (6-20)": "Borg skalası: 6=çok kolay, 20=maksimal",
    "RPE Periyot 2 (6-20)": "Borg skalası: 6=çok kolay, 20=maksimal",
    "Tamamlanan Tur Sayısı": "PACER testinde tamamlanan toplam tur sayısı",
    "Tekrar Sayısı": "Doğru formda tamamlanan toplam tekrar sayısı",
    "Sağ Omuz (Geçti/Kalmadı)": "Sağ omuz esneklik sonucu: 'Geçti' veya 'Kalmadı'",
    "Sol Omuz (Geçti/Kalmadı)": "Sol omuz esneklik sonucu: 'Geçti' veya 'Kalmadı'",
    "Sağ Bacak - En İyi (cm)": "Back-Saver Sit and Reach — sağ bacak en iyi denemesi (cm)",
    "Sol Bacak - En İyi (cm)": "Back-Saver Sit and Reach — sol bacak en iyi denemesi (cm)",
    "Triceps Deri Kıvrımı (mm)": "Sağ kolun arka orta noktasından alınan dikey deri kıvrımı (mm)",
    "Baldır Deri Kıvrımı (mm)": "Sağ baldır iç yüzeyinden maksimum çevre noktasında alınan deri kıvrımı (mm)",
    "Cinsiyet (E/K)": "E = Erkek, K = Kız — yağ % formülü için gerekli (boş bırakılırsa profil kullanılır)",
    "Süre (dakika)": "1 Mil testinde tam dakika kısmı (örn. 8 dk 45 sn için '8' girin)",
    "Süre (saniye)": "1 Mil testinde saniye kısmı (örn. 8 dk 45 sn için '45' girin)",
    "HR Test Sonu (bpm)": "Test bitimindeki ilk 15 saniyede ölçülen kalp atım hızı × 4",
    "Deneme 1 (doğru sektirme, maks 10)": "Art arda doğru (eller sırayla değişen) sektirme sayısı, 0-10",
    "Deneme 2 (doğru sektirme, maks 10)": "Yalnızca 1. denemede 10'a ulaşılamadıysa yapılır; yapılmadıysa boş bırakın",
    "En Dar El Aralığı (cm)": "Sopanın baş üzerinden geçirilebildiği en dar el aralığı, 0.5 cm hassasiyet — düşük = iyi",
    "Biakromiyal Genişlik (cm) — opsiyonel": "İki akromiyon arası omuz genişliği; girilirse net skor (aralık − genişlik) hesaplanır",
    "Diz Üstü Şınav Tekrarı (30 sn)": "30 saniyede doğru formda tamamlanan diz üstü şınav sayısı",
    "Oturma Yüksekliği (cm)": "Net değer: okunan yükseklikten oturak yüksekliği çıkarılmış hali (cm, 0.1)",
    "Kulaç Uzunluğu (cm)": "Kollar yere paralel yana açıkken iki orta parmak ucu arası (cm)",
    "Vücut Ağırlığı (kg)": "Ayakkabısız, spor kıyafetiyle (kg)",
    "Sağ El (kg)": "Sağ el kavrama kuvveti — kol gergin ve aşağıda, tek ölçüm (kg)",
    "Sol El (kg)": "Sol el kavrama kuvveti — kol gergin ve aşağıda, tek ölçüm (kg)",
    "Tamamlanan Mekik Sayısı": "TSYT mekik koşusunda tamamlanan 20 m tur sayısı (iki sinyal üst üste kaçırılınca biter)",

    # ── TERİMLER (Paket 8) ──────────────────────────────────────────────
    # Uygulamadaki her ⓘ açıklaması buradan gelir (baslik_ac / ac_dugmesi).
    # Aynı terim başka yerde ayrıca anlatılmaz. Ölçüt: beden eğitimi öğretmeni
    # okuyunca anlasın.
    "Z skoru": ("Çocuğun aynı yaş ve cinsiyetteki akranlarına göre nerede durduğunu gösterir. 0 akran "
                "ortalamasıdır. +1 ortalamanın bir standart sapma üstü, −1 bir standart sapma altı demektir. "
                "Bu uygulamada Z persentilden hesaplanır ve her testte + yön \"daha iyi\" demektir (süre gibi "
                "düşük değerin iyi olduğu testlerde işaret çevrilir)."),
    "Standart sapma": ("Bir gruptaki değerlerin ortalamadan ne kadar dağıldığını gösteren ölçü. Çocukların "
                       "yaklaşık üçte ikisi ortalamanın bir standart sapma altı ile bir standart sapma üstü "
                       "arasında yer alır."),
    "Persentil": ("Akranlar sıraya dizilse çocuğun nerede duracağını gösterir. 100 akranı düşünün: P70, "
                  "70'inin altında, 30'unun üstünde kalan değer demektir; P50 tam ortadır. Ham persentil "
                  "sayının büyüklüğüne göredir: süre gibi düşük değerin iyi olduğu testlerde yüksek ham "
                  "persentil daha yavaş demektir. Ekranda bu yüzden performans persentili gösterilir; ham "
                  "persentil yalnızca antrenör raporunun teknik tablosundadır."),
    "Performans persentili": ("Persentilin her testte \"büyük = iyi\" olacak şekilde yazılmış hali. P70, "
                              "çocuğun akranlarının yaklaşık %70'inden iyi olduğu anlamına gelir. Süre gibi düşük "
                              "değerin iyi olduğu testlerde sıra ters çevrilir (100 − ham persentil). Boy, kilo "
                              "gibi vücut ölçülerinde iyi/kötü olmadığı için ham sıra gösterilir: P70, "
                              "akranlarının %70'inden uzun ya da ağır demektir."),
    "P5 / P95": ("Norm tablosunun uç sınırları. P5 akranların en zayıf %5'inin, P95 en iyi %5'inin "
                 "sınırıdır; çocukların %90'ı bu ikisinin arasında kalır. Süre testlerinde de aynı anlamdadır: "
                 "P95 en hızlı %5'in süresidir. (Vücut ölçülerinde P5 en kısa/hafif, P95 en uzun/ağır %5.)"),
    "Sınır değer (P5 altı / P95 üstü)": (
        "Ölçüm norm tablosunun en uç sınırının dışında kalıyorsa tablo daha ötesini göstermez. Uygulama "
        "değeri sınırda tutar: Z en fazla ±1.64 olur (P20-P80 tablolarında ±0.84). Gerçek konum daha da "
        "uçta olabilir; ekranda \"sınırda tutuldu\" notu çıkar."),
    "Norm": ("Karşılaştırma tablosu: aynı yaş ve cinsiyetteki çok sayıda çocuğun bu testte aldığı "
             "değerlerin dağılımı. Bir sonucun \"iyi\" ya da \"zayıf\" olduğu bu tabloya bakılarak söylenir. "
             "Her normun kaynağı ve kaç çocuktan elde edildiği ekranda yazar. Norm, ancak testin uygulanış "
             "biçimi normun ölçüldüğü biçimle aynıysa kullanılır."),
    "Düşük-iyi test": ("Değeri düştükçe performansın iyi olduğu test: koşu ve mekik süreleri, düşme sayısı, "
                       "omuz esnekliğinde el aralığı gibi. Bu testlerde Z'nin işareti çevrilir; böylece her "
                       "testte + iyi, − zayıf demektir."),
    "Nötr (tanımlayıcı) ölçüm": ("Boy, kilo, VKİ, oturma yüksekliği gibi vücut ölçüleri. Performans "
                                 "değildir; \"iyi\" ya da \"zayıf\" denmez, yalnızca akranlara göre konum "
                                 "gösterilir ve gri renkle yazılır. Bileşik skorlara ve branş eşleştirmesine "
                                 "girmez."),
    "Taban / tavan etkisi": ("Test çok zor ya da çok kolay olduğu için çocukların çoğunun en düşük (taban) "
                             "ya da en yüksek (tavan) puanda toplanması. Örneğin 6-7 yaşta çoğu çocuk duvara "
                             "atıp yakalamada neredeyse hiç yakalayamaz; tek bir yakalama sıralamayı çok "
                             "değiştirir. Bu durumda küçük puan farkları yanıltıcıdır."),
    "Doğum çeyreği": ("Çocuğun yılın hangi çeyreğinde doğduğu: 1. çeyrek Ocak-Mart, 2. çeyrek Nisan-Haziran, "
                      "3. çeyrek Temmuz-Eylül, 4. çeyrek Ekim-Aralık. Aynı yaş grubunda yılın başında doğan çocuk "
                      "sonunda doğandan neredeyse bir yıl büyük olabilir; bu fark özellikle küçük yaşta test "
                      "sonuçlarına yansır (göreceli yaş etkisi). TSYT normları bu yüzden her yaşı dört çeyreğe "
                      "ayırır. Uygulama, sporcunun doğum tarihi kayıtlıysa onun çeyreğinin tablosunu kullanır "
                      "(yaş = test yılı − doğum yılı); kayıtlı değilse dört çeyreğin ortalamasını kullanır ve "
                      "bunu ekranda yazar."),
    "Ortalama Z": ("Dört KTK3+ koordinasyon testinin Z skorlarının ortalaması. 0 akran ortalamasıdır. Resmi "
                   "MQ değildir ve persentile çevrilmez; dört testin genel tablosunu tek sayıda özetler. "
                   "6-7 yaşta göz-el koordinasyonu taban etkisi nedeniyle ortalamaya katılmayabilir."),
    "MQ": ("Motor bölüm (motor quotient): koordinasyon testlerinden çıkan tek özet sayı. Klasik KTK'da "
           "ortalaması 100, standart sapması 15 olacak şekilde ölçeklenir ve 70/85/115/130 sınırlarıyla "
           "sınıflanır. Bu dönüşümün resmi tabloları (Coppens ve ark., 2021 ek dosyası) uygulamada olmadığı "
           "için MQ hesaplanmaz; yerine \"Ortalama Z\" gösterilir. Opstoel ve ark. (2015) ise MQ adını başka "
           "anlamda, dört koordinasyon testinin (yana sıçrama, yana platform değiştirme, geriye denge "
           "yürüyüşü, top sektirme) yaşa göre Z'lerinin toplamı için kullanır; orada 0 örneklem ortalamasıdır."),
    "PQ": ("Fiziksel uygunluk bölümü (physical fitness quotient). Opstoel ve ark. (2015) çalışmasında sekiz "
           "testin (20 m mekik, omuz esnekliği, otur-uzan, 10x5 m, durarak uzun atlama, CMJ, mekik, diz üstü "
           "şınav) yaşa göre Z skorlarının toplamı; 0 o çalışmadaki çocukların ortalamasıdır. Hesap için "
           "gereken yaş ortalamaları yayımlanmadığı ve CMJ eşleşmediği için uygulamada hesaplanmaz."),
    "Havuzlanmış standart sapma": ("Altı spor grubunun her birinin kendi içindeki dağılımının, grup "
                                   "büyüklüğüne göre ağırlıklandırılıp birleştirilmiş hali. Gruplarla "
                                   "karşılaştırırken her gruba aynı ölçüyle bakmayı sağlar; her grubun kendi "
                                   "dağılımı kullanılsaydı dağınık gruplar yapay olarak \"yakın\" görünürdü."),
    "Ortalama standart uzaklık": ("Çocuğun test sonuçlarının bir spor grubunun ortalamasına ne kadar uzak "
                                  "olduğunun tek sayılık özeti (standart sapma cinsinden). 0 grubun "
                                  "ortalamasıyla aynı demektir; küçük sayı daha yakın demektir. Gruplar "
                                  "birbirine çok yakın olduğu için 0.1-0.2'lik farklar yorumlanmamalıdır."),
    "Güven düzeyi": ("Fiziksel profilin spor grubunu ne kadar doğru gösterebildiği. Dayanak araştırmada "
                     "(Opstoel ve ark., 2015) haftada 5 saat ve üzeri antrenman yapan çocukların %85'i doğru "
                     "gruba yerleşti; 5 saatten az antrenmanda bu oran %49'da kaldı, yani tahminden pek iyi "
                     "değildi. Bu yüzden haftalık antrenman süresi sporcu profiline kaydedilir."),
    "Branş grubu katmanı": ("Radarda sporcunun çizgisinin yanına, seçilen spor grubundaki ortalama bir "
                            "çocuğun çizgisi eklenir. Grup ortalaması sporcunun kendi norm tablosundan (aynı "
                            "test, yaş, cinsiyet) geçirilir; normu olmayan değişken radarda gösterilmez."),
    "HFZ": ("Sağlık uygunluk zonu (Healthy Fitness Zone): FitnessGram'ın sağlık için yeterli kabul ettiği "
            "değer aralığı. Sıralama değil eşiktir: çocuk ya bu zonun içindedir ya da \"gelişime ihtiyaç var\" "
            "bölgesindedir."),
    "VKİ": ("Vücut kitle indeksi: kilo (kg) ÷ boy² (m). Çocuklarda yorum yaşa ve cinsiyete göre yapılır; "
            "yetişkin sınırları (25, 30) çocuklara uygulanmaz. Uygulamada tanımlayıcı bilgi olarak gösterilir."),
    "Asimetri indeksi": ("Sağ ve sol taraf (ya da güçlü ve zayıf taraf) arasındaki farkın yüzdesi: "
                         "(güçlü − zayıf) ÷ güçlü × 100. %10'un altı genellikle normal kabul edilir; %15'in "
                         "üstü daha yakından bakılmasını gerektirir (ilgili testin protokolüne bakın)."),
    "VO2max": ("Vücudun egzersiz sırasında kullanabildiği en yüksek oksijen miktarı (ml/kg/dk); aerobik "
               "dayanıklılığın temel göstergesi. Saha testlerinde (20 m mekik, Cooper gibi) doğrudan ölçülmez, "
               "formülle tahmin edilir; laboratuvar ölçümüyle aynı değildir."),
    "Reaktif kuvvet indeksi": ("Derinlik sıçramasında (bir kasadan inip yere değer değmez sıçrama) sıçrama "
                               "yüksekliğinin yere temas süresine bölümü. Kısa temasla yüksek sıçrayan "
                               "sporcunun değeri yüksektir; kasların hızlı esneyip kasılma (yaylanma) "
                               "becerisini gösterir."),
    "Olağandışı değer (P1–P99)": ("Girilen değer, aynı yaş ve cinsiyetteki çocukların yaklaşık %98'inin "
                                  "dışında kalıyorsa (P1'in altı ya da P99'un üstü) program kaydetmeden önce sorar. "
                                  "Çoğu zaman yazım hatasıdır: kiloya boy yazmak, virgülü unutmak (185 yerine 18,5). "
                                  "Değer doğruysa onaylanır ve kaydedilir; program engellemez. Normlar P1/P99 vermediği "
                                  "için bu sınırlar norm tablosunun uç bantlarından tahmin edilir. Normu olmayan testte "
                                  "kontrol yapılmaz."),
    "SJR çeyreği": ("Derginin kendi alanındaki dergiler arasındaki yeri (SCImago Journal Rank). Q1 alanın en "
                    "üst %25'idir, Q4 en alt %25'i. Kitaplar ve kurum kılavuzları dergi olmadığı için çeyrek "
                    "almaz."),
}

TERIM_SOZLUGU = {
    # Sıçrama Testleri
    "CMJ":   "CMJ (Ön-Çömelme Sıçraması)",
    "SJ":    "SJ (Statik Sıçrama)",
    "DJ":    "DJ (Derinlik Sıçraması)",

    # Fizyoloji
    "VO2max":  "VO2max (Maksimal Oksijen Tüketimi)",
    "VO2peak": "VO2peak (Tepe Oksijen Tüketimi)",
    "RER":     "RER (Solunum Değişim Oranı)",
    "VT1":     "VT1 (1. Ventilasyon Eşiği)",
    "VT2":     "VT2 (2. Ventilasyon Eşiği)",
    "LT1":     "LT1 (1. Laktat Eşiği)",
    "LT2":     "LT2 (2. Laktat Eşiği)",
    "OBLA":    "OBLA (Kan Laktat Birikimi Başlangıcı)",
    "CPET":    "CPET (Kardiyopulmoner Egzersiz Testi)",
    "VIFT":    "VIFT (Ara Fitness Testi Hızı)",
    "MET":     "MET (Metabolik Eşdeğer)",

    # Kuvvet / Güç
    "MVC":   "MVC (Maksimal İstemli Kasılma)",
    "RFD":   "RFD (Kuvvet Gelişim Hızı)",
    "1RM":   "1RM (Tek Tekrar Maksimal Kuvvet)",
    "IMTP":  "IMTP (İzometrik Orta Uyluk Çekişi)",
    "F-V":   "F-V (Kuvvet-Hız Profili)",

    # EMG / Nöromüsküler
    "RMS":   "RMS (Kök Ortalama Kare — Aktivasyon Şiddeti)",
    "MPF":   "MPF (Ortalama Güç Frekansı)",
    "EMG":   "EMG (Elektromiyografi)",

    # Vücut Kompozisyonu
    "DEXA":  "DEXA (Çift Enerjili X-Işını Absorpsiyometrisi)",
    "BIA":   "BIA (Biyoelektrik İmpedans Analizi)",
    "LBM":   "LBM (Yağsız Vücut Kütlesi)",
    "BMD":   "BMD (Kemik Mineral Yoğunluğu)",
    "BMI":   "BMI/VKİ (Vücut Kitle İndeksi)",
    "RED-S": "RED-S (Sporda Göreceli Enerji Eksikliği)",
    "VKİ":   "VKİ (Vücut Kitle İndeksi)",

    # Esneklik / ROM
    "ROM":   "ROM (Eklem Hareket Açıklığı)",

    # Testler
    "RSA":   "RSA (Tekrarlı Sprint Kabiliyeti)",
    "HFZ":   "HFZ (Sağlık Uygunluk Zonu)",
    "HFS":   "HFS (Sağlıklı Uygunluk Standardı)",
    "MVPA":  "MVPA (Orta-Şiddetli Fiziksel Aktivite)",
    "CSS":   "CSS (Kritik Yüzme Hızı)",

    # Oranlar
    "H:Q":   "H:K (Hamstring/Kuadriseps Oranı)",
    "spm":   "spm (vuruş/dakika)",
    "bpm":   "bpm (atım/dakika)",
    "Watt":  "Watt (güç birimi, W)",
    "RSI":   "RSI (Reaktif Kuvvet İndeksi)",
}

# ── Metinde geçen terimleri bulmak için arama kalıpları (açıklama metni ACIKLAMALAR'dadır) ──
TERIM_ARAMA = {
    "VO2max": r"VO2\s?max|VO₂\s?max",
    "VKİ": r"\bVKİ\b|\bBMI\b",
    "HFZ": r"\bHFZ\b|Sağlık Uygunluk Zonu",
    "Asimetri indeksi": r"[Aa]simetri",
    "Reaktif kuvvet indeksi": r"\bRSI\b|RKİ|[Rr]eaktif [Kk]uvvet [İi]ndeksi",
    "Persentil": r"[Pp]ersentil",
    "P5 / P95": r"\bP5\b|\bP95\b",
    "MQ": r"\bMQ\b",
    "PQ": r"\bPQ\b",
    "Taban / tavan etkisi": r"[Tt]aban etkisi|[Tt]avan etkisi",
    "Doğum çeyreği": r"[Dd]oğum çeyre|[Gg]öreceli yaş",
}


# Bölme Aşama 2 eki: uygulama.py'deki birleştirmeler (saf metin) buraya taşındı.
# Paket 38a: kullanıcıya dönük teknik terimlerin sade karşılığı (aynı "Bu ne demek?" düğmesinde)
ACIKLAMALAR = {**ACIKLAMALAR,
    "Örneklem": ("Karşılaştırma grubu: bir araştırmada ölçülen sporcuların ortalaması. Sıralama ya da not değildir; "
                 "değer bu grubun ortalamasının yanında gösterilir."),
    "SD (standart sapma)": ("Yayılım: grubun değerlerinin ortalamadan ne kadar uzaklaştığı. Ortalamadan 1 SD uzak "
                            "olmak, grubun büyük kısmının içinde olmak demektir."),
    "Rölatif değer": "Vücut ağırlığına bölünmüş değer (ör. kaldırılan kg ÷ vücut ağırlığı): farklı kilodaki sporcular karşılaştırılabilir.",
    "Kademe 2": "Karşılaştırma bir araştırma grubunun ortalamasıyla yapılır; yaşa göre yüzdelik tablo (norm) değildir.",
    "Batarya": "Birlikte uygulanan test takımı (ör. TSYT bataryası: aynı gün sırayla yapılan testler).",
}
TERIM_ARAMA = {**TERIM_ARAMA,
    "Örneklem": r"[Öö]rneklem",
    "SD (standart sapma)": r"\bSD\b",
    "Rölatif değer": r"[Rr]ölatif",
    "Kademe 2": r"Kademe 2",
    "Batarya": r"[Bb]atarya",
}
