"""
Kategorik normlar (test değişkeni → cinsiyet → seviye → (alt, üst)), Kademe 2 örneklem tabloları ve
kaynak/künye kayıtları (Aydos ve ark. 2004; Morassutti ve ark. 2025), test bazlı normlar (NORMATIF_TEST).

Bölme Aşama 1: uygulama.py'den birebir taşındı (davranış değişmedi). Yalnız sabit değerler; fonksiyon, çağrı ya da
içe aktarma yok (test_44a denetler).
"""


NORMATIF = {
    "VO2max Tahmini (ml/kg/min)": {
        "Erkek": {"Mükemmel":(60,999),"İyi":(52,60),"Orta":(43,52),"Zayıf":(0,43)},
        "Kadın": {"Mükemmel":(54,999),"İyi":(45,54),"Orta":(36,45),"Zayıf":(0,36)},
        "dusuk_iyi": False,
        "kaynak": "Haugen, T. et al. (2022). IJSPP, 17(4), 505-507. | Saltin, B., & Åstrand, P. O. (1967). JAP, 23(3), 353-358.",
        "branslar": {
            "Futbol": {
                "Erkek":{"Mükemmel":(58,999),"İyi":(53,58),"Orta":(47,53),"Zayıf":(0,47)},
                "Kadın":{"Mükemmel":(52,999),"İyi":(46,52),"Orta":(40,46),"Zayıf":(0,40)},
                "kaynak":"Stølen, T. et al. (2005). Sports Medicine, 35(6), 501-536.",
            },
            "Güreş (Serbest)": {
                "Erkek":{"Mükemmel":(58,999),"İyi":(53,58),"Orta":(47,53),"Zayıf":(0,47)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Güreş (Grekoromen)": {
                "Erkek":{"Mükemmel":(58,999),"İyi":(53,58),"Orta":(47,53),"Zayıf":(0,47)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Judo": {
                "Erkek":{"Mükemmel":(57,999),"İyi":(52,57),"Orta":(46,52),"Zayıf":(0,46)},
                "Kadın":{"Mükemmel":(50,999),"İyi":(44,50),"Orta":(38,44),"Zayıf":(0,38)},
                "kaynak":"Franchini, E. et al. (2011). Sports Medicine, 41(2), 147-166.",
            },
            "Karate": {
                "Erkek":{"Mükemmel":(56,999),"İyi":(50,56),"Orta":(44,50),"Zayıf":(0,44)},
                "Kadın":{"Mükemmel":(49,999),"İyi":(43,49),"Orta":(37,43),"Zayıf":(0,37)},
                "kaynak":"Chaabène, H. et al. (2012). Sports Medicine, 42(10), 829-843.",
            },
            "Taekwondo": {
                "Erkek":{"Mükemmel":(57,999),"İyi":(52,57),"Orta":(46,52),"Zayıf":(0,46)},
                "Kadın":{"Mükemmel":(50,999),"İyi":(44,50),"Orta":(38,44),"Zayıf":(0,38)},
                "kaynak":"Bridge, C. A. et al. (2014). Sports Medicine, 44(6), 713-733.",
            },
            "Kickboks": {
                "Erkek":{"Mükemmel":(56,999),"İyi":(50,56),"Orta":(44,50),"Zayıf":(0,44)},
                "kaynak":"Ouergui, I. et al. (2014). JSCR, 28(12), 3340-3347.",
            },
            "Muay Thai": {
                "Erkek":{"Mükemmel":(55,999),"İyi":(49,55),"Orta":(43,49),"Zayıf":(0,43)},
                "kaynak":"Crisafulli, A. et al. (2009). JSAMS, 12(6), 639-644.",
            },
            "Boks": {
                "Erkek":{"Mükemmel":(56,999),"İyi":(50,56),"Orta":(44,50),"Zayıf":(0,44)},
                "kaynak":"Davis, P. et al. (2013). IJSPP, 8(1), 3-12.",
            },
            "Bisiklet": {
                "Erkek":{"Mükemmel":(75,999),"İyi":(65,75),"Orta":(55,65),"Zayıf":(0,55)},
                "Kadın":{"Mükemmel":(65,999),"İyi":(55,65),"Orta":(45,55),"Zayıf":(0,45)},
                "kaynak":"Lucia, A. et al. (2001). Sports Medicine, 31(5), 325-337.",
            },
            "Atletizm (Uzun Mesafe)": {
                "Erkek":{"Mükemmel":(75,999),"İyi":(68,75),"Orta":(60,68),"Zayıf":(0,60)},
                "Kadın":{"Mükemmel":(65,999),"İyi":(58,65),"Orta":(50,58),"Zayıf":(0,50)},
                "kaynak":"Midgley, A. W. et al. (2007). Sports Medicine, 37(2), 117-132.",
            },
            "Basketbol": {
                "Erkek":{"Mükemmel":(55,999),"İyi":(48,55),"Orta":(42,48),"Zayıf":(0,42)},
                "Kadın":{"Mükemmel":(48,999),"İyi":(42,48),"Orta":(36,42),"Zayıf":(0,36)},
                "kaynak":"Drinkwater, E. J. et al. (2008). Sports Medicine, 38(7), 565-578.",
            },
        },
    },
    "CMJ En İyi (cm)": {
        "Erkek": {"Mükemmel":(55,999),"İyi":(45,55),"Orta":(35,45),"Zayıf":(0,35)},
        "Kadın": {"Mükemmel":(42,999),"İyi":(33,42),"Orta":(25,33),"Zayıf":(0,25)},
        "dusuk_iyi": False,
        "kaynak": "Markovic, G. (2007). British Journal of Sports Medicine, 41(6), 349-355.",
        "branslar": {
            "Voleybol": {
                "Erkek":{"Mükemmel":(65,999),"İyi":(55,65),"Orta":(45,55),"Zayıf":(0,45)},
                "Kadın":{"Mükemmel":(50,999),"İyi":(42,50),"Orta":(34,42),"Zayıf":(0,34)},
                "kaynak":"Sheppard, J. M. et al. (2009). JSCR, 23(6), 1858-1866.",
            },
            "Basketbol": {
                "Erkek":{"Mükemmel":(70,999),"İyi":(60,70),"Orta":(50,60),"Zayıf":(0,50)},
                "Kadın":{"Mükemmel":(55,999),"İyi":(45,55),"Orta":(35,45),"Zayıf":(0,35)},
                "kaynak":"Drinkwater, E. J. et al. (2008). Sports Medicine, 38(7), 565-578.",
            },
        },
    },
    "Sağ El (kg)": {
        "Erkek": {"Mükemmel":(56,999),"İyi":(47,56),"Orta":(38,47),"Zayıf":(0,38)},
        "Kadın": {"Mükemmel":(36,999),"İyi":(29,36),"Orta":(22,29),"Zayıf":(0,22)},
        "dusuk_iyi": False,
        "kaynak": "Ruiz, J. R. et al. (2011). British Journal of Sports Medicine, 45(6), 518-524.",
        "branslar": {
            "Güreş (Serbest)": {
                "Erkek":{"Mükemmel":(65,999),"İyi":(55,65),"Orta":(45,55),"Zayıf":(0,45)},
                "kaynak":"Mirzaei, B. et al. (2009). Journal of Human Kinetics, 21, 73-79.",
            },
            "Güreş (Grekoromen)": {
                "Erkek":{"Mükemmel":(65,999),"İyi":(55,65),"Orta":(45,55),"Zayıf":(0,45)},
                "kaynak":"Mirzaei, B. et al. (2009). Journal of Human Kinetics, 21, 73-79.",
            },
            "Judo": {
                "Erkek":{"Mükemmel":(60,999),"İyi":(50,60),"Orta":(40,50),"Zayıf":(0,40)},
                "kaynak":"Franchini, E. et al. (2011). Sports Medicine, 41(2), 147-166.",
            },
        },
    },
    "Sol El (kg)": {
        "Erkek": {"Mükemmel":(53,999),"İyi":(45,53),"Orta":(36,45),"Zayıf":(0,36)},
        "Kadın": {"Mükemmel":(34,999),"İyi":(27,34),"Orta":(20,27),"Zayıf":(0,20)},
        "dusuk_iyi": False,
        "kaynak": "Ruiz, J. R. et al. (2011). British Journal of Sports Medicine, 45(6), 518-524.",
        "branslar": {},
    },
    "Pik Güç (W)": {
        "Erkek": {"Mükemmel":(1100,99999),"İyi":(900,1100),"Orta":(700,900),"Zayıf":(0,700)},
        "Kadın": {"Mükemmel":(750,99999),"İyi":(600,750),"Orta":(450,600),"Zayıf":(0,450)},
        "dusuk_iyi": False,
        "kaynak": "Bar-Or, O. (1987). Sports Medicine, 4(6), 381-394.",
        "branslar": {},
    },
    "SWFT Index": {
        "Erkek": {"Mükemmel":(0,8.0),"İyi":(8.0,10.0),"Orta":(10.0,13.0),"Zayıf":(13.0,999)},
        "Kadın": {"Mükemmel":(0,9.0),"İyi":(9.0,11.0),"Orta":(11.0,14.0),"Zayıf":(14.0,999)},
        "dusuk_iyi": True,
        "kaynak": "Marković, M. et al. (2021). JSCR, 35(12S), S51-S57.",
        "branslar": {},
    },
    "SJFT İndeksi": {
        "Erkek": {"Mükemmel":(0,11.0),"İyi":(11.0,13.0),"Orta":(13.0,15.0),"Zayıf":(15.0,999)},
        "Kadın": {"Mükemmel":(0,13.0),"İyi":(13.0,15.0),"Orta":(15.0,17.0),"Zayıf":(17.0,999)},
        "dusuk_iyi": True,
        "kaynak": "Franchini, E. et al. (1998). Rev. Bras. Med. Esporte, 4(3), 73-77.",
        "branslar": {},
    },
    "Vücut Yağ % (Tahmini)": {
        "Erkek": {"Mükemmel":(0,10),"İyi":(10,15),"Orta":(15,20),"Zayıf":(20,999)},
        "Kadın": {"Mükemmel":(0,18),"İyi":(18,24),"Orta":(24,30),"Zayıf":(30,999)},
        "dusuk_iyi": True,
        "kaynak": "Heyward, V. H. (2010). Advanced Fitness Assessment (6th ed.). Human Kinetics.",
        "branslar": {
            "Güreş (Serbest)": {
                "Erkek":{"Mükemmel":(0,8),"İyi":(8,12),"Orta":(12,16),"Zayıf":(16,999)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Güreş (Grekoromen)": {
                "Erkek":{"Mükemmel":(0,8),"İyi":(8,12),"Orta":(12,16),"Zayıf":(16,999)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Judo": {
                "Erkek":{"Mükemmel":(0,10),"İyi":(10,14),"Orta":(14,18),"Zayıf":(18,999)},
                "kaynak":"Franchini, E. et al. (2011). Sports Medicine, 41(2), 147-166.",
            },
            "Karate": {
                "Erkek":{"Mükemmel":(0,9),"İyi":(9,13),"Orta":(13,17),"Zayıf":(17,999)},
                "kaynak":"Chaabène, H. et al. (2012). Sports Medicine, 42(10), 829-843.",
            },
        },
    },

    # ── Eurofit Normatif Değerleri ──
    "Düşme Sayısı (1 dk)": {
        "Erkek": {"Mükemmel":(0,5),"İyi":(5,10),"Orta":(10,15),"Zayıf":(15,999)},
        "Kadın": {"Mükemmel":(0,6),"İyi":(6,11),"Orta":(11,16),"Zayıf":(16,999)},
        "dusuk_iyi": True,
        "kaynak": "Adam, C. et al. (1988). Eurofit: European Test of Physical Fitness. Council of Europe, Rome.",
    },
    "Düşme Sayısı (30 sn)": {
        "Erkek": {"Mükemmel":(0,3),"İyi":(3,7),"Orta":(7,12),"Zayıf":(12,999)},
        "Kadın": {"Mükemmel":(0,4),"İyi":(4,8),"Orta":(8,13),"Zayıf":(13,999)},
        "dusuk_iyi": True,
        "kaynak": "Adam, C. et al. (1988). Eurofit. Council of Europe.",
    },
    "Tekrar Sayısı (30sn)": {
        "Erkek": {"Mükemmel":(27,999),"İyi":(22,27),"Orta":(17,22),"Zayıf":(0,17)},
        "Kadın": {"Mükemmel":(25,999),"İyi":(20,25),"Orta":(15,20),"Zayıf":(0,15)},
        "dusuk_iyi": False,
        "kaynak": "Adam, C. et al. (1988). Eurofit. Council of Europe.",
    },
    "Askıda Kol Bükme (sn)": {
        "Erkek": {"Mükemmel":(45,999),"İyi":(30,45),"Orta":(15,30),"Zayıf":(0,15)},
        "Kadın": {"Mükemmel":(30,999),"İyi":(18,30),"Orta":(8,18),"Zayıf":(0,8)},
        "dusuk_iyi": False,
        "kaynak": "Adam, C. et al. (1988). Eurofit. Council of Europe.",
    },

    # FitnessGram HFZ eşikleri yaşa ve cinsiyete göre değişir: NORMATIF_ESIK_YAS (Paket 20). Burada tek bant yok.

    # ── Sprint Normları ──
    "30m Sprint En İyi (sn)": {
        "Erkek": {"Mükemmel":(0,3.80),"İyi":(3.80,4.10),"Orta":(4.10,4.50),"Zayıf":(4.50,999)},
        "Kadın": {"Mükemmel":(0,4.20),"İyi":(4.20,4.60),"Orta":(4.60,5.00),"Zayıf":(5.00,999)},
        "dusuk_iyi": True,
        "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.\nNSCA (2016). Essentials of Strength Training and Conditioning (4th ed.).",
        "branslar": {
            "Futbol": {
                "Erkek":{"Mükemmel":(0,3.95),"İyi":(3.95,4.20),"Orta":(4.20,4.50),"Zayıf":(4.50,999)},
                "kaynak":"Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
            },
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,3.60),"İyi":(3.60,3.85),"Orta":(3.85,4.10),"Zayıf":(4.10,999)},
                "Kadın":{"Mükemmel":(0,4.00),"İyi":(4.00,4.30),"Orta":(4.30,4.60),"Zayıf":(4.60,999)},
                "kaynak":"Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
            },
        },
    },
    "10m Sprint (sn)": {
        "Erkek": {"Mükemmel":(0,1.65),"İyi":(1.65,1.80),"Orta":(1.80,2.00),"Zayıf":(2.00,999)},
        "Kadın": {"Mükemmel":(0,1.80),"İyi":(1.80,1.95),"Orta":(1.95,2.15),"Zayıf":(2.15,999)},
        "dusuk_iyi": True,
        "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.\nSeitz, L. B. et al. (2014). Journal of Strength and Conditioning Research, 28(2), 401-409.",
        "branslar": {
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,1.55),"İyi":(1.55,1.68),"Orta":(1.68,1.82),"Zayıf":(1.82,999)},
                "Kadın":{"Mükemmel":(0,1.70),"İyi":(1.70,1.82),"Orta":(1.82,1.96),"Zayıf":(1.96,999)},
                "kaynak":"Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
            },
            "Futbol": {
                "Erkek":{"Mükemmel":(0,1.70),"İyi":(1.70,1.82),"Orta":(1.82,1.95),"Zayıf":(1.95,999)},
                "kaynak":"Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
            },
        },
    },
    "20m Sprint (sn)": {
        "Erkek": {"Mükemmel":(0,2.75),"İyi":(2.75,3.00),"Orta":(3.00,3.30),"Zayıf":(3.30,999)},
        "Kadın": {"Mükemmel":(0,3.00),"İyi":(3.00,3.28),"Orta":(3.28,3.60),"Zayıf":(3.60,999)},
        "dusuk_iyi": True,
        "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
        "branslar": {
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,2.55),"İyi":(2.55,2.75),"Orta":(2.75,2.98),"Zayıf":(2.98,999)},
                "Kadın":{"Mükemmel":(0,2.80),"İyi":(2.80,3.00),"Orta":(3.00,3.25),"Zayıf":(3.25,999)},
                "kaynak":"Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
            },
        },
    },
    "100m Sprint (sn)": {
        "Erkek": {"Mükemmel":(0,10.50),"İyi":(10.50,11.20),"Orta":(11.20,12.00),"Zayıf":(12.00,999)},
        "Kadın": {"Mükemmel":(0,11.50),"İyi":(11.50,12.20),"Orta":(12.20,13.20),"Zayıf":(13.20,999)},
        "dusuk_iyi": True,
        "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.\nIAAF (2023). World Athletics Performance Standards.",
        "branslar": {
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,10.20),"İyi":(10.20,10.80),"Orta":(10.80,11.50),"Zayıf":(11.50,999)},
                "Kadın":{"Mükemmel":(0,11.20),"İyi":(11.20,11.80),"Orta":(11.80,12.50),"Zayıf":(12.50,999)},
                "kaynak":"World Athletics (2023). Performance Standards.",
            },
        },
    },
    "200m Sprint (sn)": {
        "Erkek": {"Mükemmel":(0,21.50),"İyi":(21.50,23.00),"Orta":(23.00,25.00),"Zayıf":(25.00,999)},
        "Kadın": {"Mükemmel":(0,23.50),"İyi":(23.50,25.00),"Orta":(25.00,27.50),"Zayıf":(27.50,999)},
        "dusuk_iyi": True,
        "kaynak": "World Athletics (2023). Performance Standards.\nHaugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
        "branslar": {
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,20.50),"İyi":(20.50,21.80),"Orta":(21.80,23.50),"Zayıf":(23.50,999)},
                "Kadın":{"Mükemmel":(0,22.50),"İyi":(22.50,24.00),"Orta":(24.00,26.00),"Zayıf":(26.00,999)},
                "kaynak":"World Athletics (2023). Performance Standards.",
            },
        },
    },
    "Illinois Çeviklik En İyi (sn)": {
        "Erkek": {"Mükemmel":(0,15.2),"İyi":(15.2,16.1),"Orta":(16.1,18.2),"Zayıf":(18.2,999)},
        "Kadın": {"Mükemmel":(0,17.0),"İyi":(17.0,17.9),"Orta":(17.9,21.8),"Zayıf":(21.8,999)},
        "dusuk_iyi": True,
        "kaynak": "Raya, M. A. et al. (2013). JOSPT, 43(7), 444-452.\nNSCA (2016). Essentials of Strength Training and Conditioning (4th ed.).",
    },

    # ── Yo-Yo IR1 Branş Normları ──
    "Tamamlanan Mesafe (m)": {
        "Erkek": {"Mükemmel":(2400,999999),"İyi":(1920,2400),"Orta":(1200,1920),"Zayıf":(0,1200)},
        "Kadın": {"Mükemmel":(1680,999999),"İyi":(1200,1680),"Orta":(800,1200),"Zayıf":(0,800)},
        "dusuk_iyi": False,
        "kaynak": "Bangsbo, J. et al. (2008). Sports Medicine, 38(1), 37-51.",
        "branslar": {
            "Futbol": {
                "Erkek":{"Mükemmel":(2400,999999),"İyi":(2000,2400),"Orta":(1400,2000),"Zayıf":(0,1400)},
                "Kadın":{"Mükemmel":(1800,999999),"İyi":(1400,1800),"Orta":(900,1400),"Zayıf":(0,900)},
                "kaynak":"Bangsbo, J. et al. (2008). Sports Medicine, 38(1), 37-51.",
            },
            "Güreş (Serbest)": {
                "Erkek":{"Mükemmel":(2000,999999),"İyi":(1600,2000),"Orta":(1100,1600),"Zayıf":(0,1100)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Güreş (Grekoromen)": {
                "Erkek":{"Mükemmel":(2000,999999),"İyi":(1600,2000),"Orta":(1100,1600),"Zayıf":(0,1100)},
                "kaynak":"Yoon, J. (2002). Sports Medicine, 32(4), 225-233.",
            },
            "Judo": {
                "Erkek":{"Mükemmel":(2000,999999),"İyi":(1600,2000),"Orta":(1100,1600),"Zayıf":(0,1100)},
                "kaynak":"Franchini, E. et al. (2011). Sports Medicine, 41(2), 147-166.",
            },
            "Basketbol": {
                "Erkek":{"Mükemmel":(1800,999999),"İyi":(1400,1800),"Orta":(1000,1400),"Zayıf":(0,1000)},
                "kaynak":"Castagna, C., Impellizzeri, F. M., Rampinini, E., D'Ottavio, S., & Manzi, V. (2008). The Yo-Yo intermittent recovery test in basketball players. Journal of Science and Medicine in Sport, 11(2), 202-208. https://doi.org/10.1016/j.jsams.2007.02.013 — NOT: Bant sınırları testin protokol metnindeki pozisyon değerleriyle (Guard >1600, Forward >1400, Center >1200 m) uyumlu; makalenin özetinde mesafe ortalaması verilmediği için sınırlar tam metinle teyit edilmemiştir.",
            },
            "Voleybol": {
                "Erkek":{"Mükemmel":(2000,999999),"İyi":(1600,2000),"Orta":(1000,1600),"Zayıf":(0,1000)},
                "Kadın":{"Mükemmel":(1400,999999),"İyi":(1000,1400),"Orta":(600,1000),"Zayıf":(0,600)},
                "kaynak":"Gabbett, T. et al. (2006). International Journal of Sports Physiology and Performance, 1(3), 269-279.",
            },
            "Karate": {
                "Erkek":{"Mükemmel":(1800,999999),"İyi":(1400,1800),"Orta":(900,1400),"Zayıf":(0,900)},
                "kaynak":"Chaabène, H. et al. (2012). Sports Medicine, 42(10), 829-843.",
            },
            "Taekwondo": {
                "Erkek":{"Mükemmel":(1800,999999),"İyi":(1400,1800),"Orta":(900,1400),"Zayıf":(0,900)},
                "kaynak":"Bridge, C. A. et al. (2014). Sports Medicine, 44(6), 713-733.",
            },
            "Badminton": {
                "Erkek":{"Mükemmel":(2000,999999),"İyi":(1600,2000),"Orta":(1000,1600),"Zayıf":(0,1000)},
                "kaynak":"Abian-Vicen, J. et al. (2012). PLoS One, 7(5), e37821.",
            },
            "Squash": {
                "Erkek":{"Mükemmel":(2200,999999),"İyi":(1800,2200),"Orta":(1200,1800),"Zayıf":(0,1200)},
                "kaynak":"Nikolaidis, P. T. et al. (2018). Journal of Human Kinetics, 61, 95-105.",
            },
            "Hentbol": {
                "Erkek":{"Mükemmel":(2200,999999),"İyi":(1800,2200),"Orta":(1200,1800),"Zayıf":(0,1200)},
                "kaynak":"Michalsik, L. B. et al. (2015). Journal of Strength and Conditioning Research, 29(12), 3483-3493.",
            },
        },
    },

    # ── Nordic Hamstring Normatif ──
    "Asimetri İndeksi (%)": {
        "Erkek": {"Mükemmel":(0,5),"İyi":(5,10),"Orta":(10,15),"Zayıf":(15,999)},
        "Kadın": {"Mükemmel":(0,5),"İyi":(5,10),"Orta":(10,15),"Zayıf":(15,999)},
        "dusuk_iyi": True,
        "kaynak": "Ekstrand, J. et al. (2011). American Journal of Sports Medicine, 39(6), 1226-1232.\nAl Attar, W. S. A. et al. (2017). Sports Medicine, 47(5), 907-916.",
    },
    "Sağ Bacak (N/kg)": {
        "Erkek": {"Mükemmel":(4.5,999),"İyi":(3.8,4.5),"Orta":(3.0,3.8),"Zayıf":(0,3.0)},
        "Kadın": {"Mükemmel":(3.5,999),"İyi":(2.8,3.5),"Orta":(2.2,2.8),"Zayıf":(0,2.2)},
        "dusuk_iyi": False,
        "kaynak": "Jeanguyot, N. et al. (2023). JSAMS, 26(4), 215-222.",
    },
    "Sol Bacak (N/kg)": {
        "Erkek": {"Mükemmel":(4.5,999),"İyi":(3.8,4.5),"Orta":(3.0,3.8),"Zayıf":(0,3.0)},
        "Kadın": {"Mükemmel":(3.5,999),"İyi":(2.8,3.5),"Orta":(2.2,2.8),"Zayıf":(0,2.2)},
        "dusuk_iyi": False,
        "kaynak": "Jeanguyot, N. et al. (2023). JSAMS, 26(4), 215-222.",
    },

    # ── İzokinetik H:K Normları (Keytsman + Croisier) ──
    "H:K Oranı Dom. (%)": {
        "Erkek": {"Mükemmel":(65,80),"İyi":(60,65),"Orta":(55,60),"Zayıf":(0,55)},
        "Kadın": {"Mükemmel":(65,80),"İyi":(60,65),"Orta":(55,60),"Zayıf":(0,55)},
        "dusuk_iyi": False,
        "kaynak": "Keytsman, C. et al. (2024). BMC Sports Science, Medicine and Rehabilitation, 16(1), 180.\nCroisier, J. L. et al. (2008). American Journal of Sports Medicine, 36(8), 1469-1475.",
    },
    "H:K Oranı N-Dom. (%)": {
        "Erkek": {"Mükemmel":(65,80),"İyi":(60,65),"Orta":(55,60),"Zayıf":(0,55)},
        "Kadın": {"Mükemmel":(65,80),"İyi":(60,65),"Orta":(55,60),"Zayıf":(0,55)},
        "dusuk_iyi": False,
        "kaynak": "Keytsman, C. et al. (2024). BMC Sports Science, Medicine and Rehabilitation, 16(1), 180.",
    },

    # ── Sprint (Atletizm) ──
    "400m Sprint (sn)": {
        "Erkek": {"Mükemmel":(0,46.00),"İyi":(46.00,49.00),"Orta":(49.00,54.00),"Zayıf":(54.00,999)},
        "Kadın": {"Mükemmel":(0,52.00),"İyi":(52.00,55.00),"Orta":(55.00,60.00),"Zayıf":(60.00,999)},
        "dusuk_iyi": True,
        "kaynak": "World Athletics (2023). Performance Standards.",
        "branslar": {
            "Atletizm (Sprint)": {
                "Erkek":{"Mükemmel":(0,45.00),"İyi":(45.00,47.50),"Orta":(47.50,51.00),"Zayıf":(51.00,999)},
                "Kadın":{"Mükemmel":(0,50.00),"İyi":(50.00,53.00),"Orta":(53.00,57.00),"Zayıf":(57.00,999)},
                "kaynak":"World Athletics (2023). Performance Standards.",
            },
        },
    },

    # ── Tenis Spider Test ──
}

ORNEKLEM_KAYNAK_AYDOS_2004 = ("Aydos, L., Pepe, H., & Karakuş, H. (2004). Bazı takım ve ferdi sporlarda rölatif kuvvet "
                              "değerlerinin araştırılması. Gazi Üniversitesi Kırşehir Eğitim Fakültesi Dergisi, 5(2), 305-315.")

ORNEKLEM_KUNYE_AYDOS_2004 = {
    "kademe": 2,
    "tur": "örneklem ortalaması ± SD (yüzdelik norm değil)",
    "orneklem": "n=77 erkek, 18-30 yaş, üniversite kulüp sporcusu (milli takım değil); branş başına n=10-15; 2004",
    "protokol": ("Standart 1RM protokolü tarif edilmez: kaldırılan maksimal ağırlık kaydedilmiş, ısınma 10 dk hafif "
                 "ağırlıkla; squat derinliği diz açısı 90°'yi geçene kadar."),
    "kart_notu": "Yüzdelik norm değil: üniversite kulüp sporcusu örneklemi (2004), branş başına n=10-15.",   # Paket 36
}

# (branş, n, rölatif squat ort, SD, rölatif bench press ort, SD) — kg/kg, makaledeki tablolardan birebir
_AYDOS_2004 = (
    ("Halter", 10, 2.897, 0.196, 1.453, 0.106),
    ("Güreş", 11, 1.915, 0.360, 1.301, 0.210),
    ("Boks", 10, 1.827, 0.376, 1.178, 0.145),
    ("Judo", 10, 1.606, 0.305, 1.273, 0.241),
    ("Basketbol", 10, 1.566, 0.325, 1.027, 0.145),
    ("Futbol", 15, 1.405, 0.304, 1.089, 0.228),
    ("Voleybol", 11, 1.307, 0.171, 1.015, 0.185),
)

# ── Paket 36: Sargent — Morassutti, van Wyk ve Duquette (2025), Tablo 2 (m → cm × 100). Kademe 2, örneklem ort ± SD.
# n=960 (422 E / 538 K), 20-29 yaş, Kanadalı üniversite öğrencisi, karma atletik düzey. Tek örneklem satırı: spor
# dalından bağımsız kullanılır (genel_orneklem; ORNEKLEM_SPOR_DALI eşlemesi yok). Yaş 20-29 dışında gösterilmez.
# Değerler (Tablo 2) denetçi tarafından makalenin tam metninden kontrol edildi; Tablo 5/6 medyanları (E 0,53 m;
# K 0,36 m) ortalamalarla tutarlı (künye notu, Paket 37).
ORNEKLEM_KAYNAK_MORASSUTTI_2025 = ("Morassutti, O. N., van Wyk, P. M., & Duquette, A. M. (2025). Vertical jumping power "
                                   "normative-reference values: Utilizing a large cohort of Canadian university students. "
                                   "Biomedical Human Kinetics, 17, 147-157. https://doi.org/10.2478/bhk-2025-0014")

ORNEKLEM_KUNYE_MORASSUTTI_2025 = {
    "kademe": 2,
    "tur": "örneklem ortalaması ± SD",
    "orneklem": ("n=960 (422 E / 538 K), 20-29 yaş, Kanadalı üniversite öğrencisi, karma atletik düzey "
                 "(nicelleştirilmemiş), 2010-2019"),
    "protokol": ("1,27 m duvar skalası, alt uç yerden 1,91 m; baskın el ve yan duruş; tek kol savurma + tek hazırlık "
                 "çömelmesi (ek karşı hareket yok); 3 deneme, en iyisi; ayakkabılı"),
    "not": ("Protokolümüz kolları ve çömelmeyi serbest bırakıyorsa değerler kaynakla birebir karşılaştırılamaz; "
            "elit/branşa özgü norm değildir."),
    "dogrulama": ("Değerler (Tablo 2: erkek 53 ± 14 cm, n=422; kadın 37 ± 11 cm, n=538) denetçi tarafından makalenin "
                  "tam metninden kontrol edildi; Tablo 5/6 medyanları (erkek 0,53 m; kadın 0,36 m) ortalamalarla "
                  "tutarlıdır."),
    "kart_notu": ("Yüzdelik norm değil: Kanadalı üniversite öğrencisi örneklemi (karma düzey); elit/branşa özgü norm "
                  "değildir."),
    "disi_metni": ("Bu değerin karşılaştırma örneklemi 20-29 yaş üniversite öğrencilerinden oluşur (Morassutti ve "
                   "ark., 2025); bu yaş aralığı dışında, yaşı ya da cinsiyeti bilinmeyen sporcuda referans "
                   "gösterilmez."),
}

NORMATIF_TEST = {

    # Spider Test: önceki "<15.5 sn" bantları kaynakla doğrulanamadı — kaldırıldı (Paket 23).

    # ── Futbol: Illinois Çeviklik ──
    "Illinois Çeviklik Testi › Deneme 1 (sn)": {
        "Erkek": {"Mükemmel":(0,15.2),"İyi":(15.2,16.1),"Orta":(16.1,18.2),"Zayıf":(18.2,999)},
        "Kadın": {"Mükemmel":(0,17.0),"İyi":(17.0,17.9),"Orta":(17.9,21.8),"Zayıf":(21.8,999)},
        "dusuk_iyi": True,
        "kaynak": "Raya, M. A., et al. (2013). Journal of Orthopaedic & Sports Physical Therapy, 43(7), 444-452.",
    },
    "Illinois Çeviklik Testi › Deneme 2 (sn)": {
        "Erkek": {"Mükemmel":(0,15.2),"İyi":(15.2,16.1),"Orta":(16.1,18.2),"Zayıf":(18.2,999)},
        "Kadın": {"Mükemmel":(0,17.0),"İyi":(17.0,17.9),"Orta":(17.9,21.8),"Zayıf":(21.8,999)},
        "dusuk_iyi": True,
        "kaynak": "Raya, M. A., et al. (2013). JOSPT, 43(7), 444-452.",
    },
    "Illinois Çeviklik Testi › Deneme 3 (sn)": {
        "Erkek": {"Mükemmel":(0,15.2),"İyi":(15.2,16.1),"Orta":(16.1,18.2),"Zayıf":(18.2,999)},
        "Kadın": {"Mükemmel":(0,17.0),"İyi":(17.0,17.9),"Orta":(17.9,21.8),"Zayıf":(21.8,999)},
        "dusuk_iyi": True,
        "kaynak": "Raya, M. A., et al. (2013). JOSPT, 43(7), 444-452.",
    },
}
