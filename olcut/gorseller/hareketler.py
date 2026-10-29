"""
Test görselleri — hareket kitaplığı (hk_*): sporcu pozları ve hareket anahtarları (koşu, sıçrama, atma, kuvvet,
denge, ergometre…). Sahneler pozu kendisi kurmaz, bu kitaplıktan alır (test_20f).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import math as _math
from olcut.gorseller.cizim import (
    TG_KALINLIK, TG_TEMEL_POZ, TG_ZEMIN, TgHareket, _TG_BOY, _tg_ara, _tg_kareler, tg_eklemler, tg_poz,
    tg_yerlestir)


def _hk_kos_pozu(hx, faz, yon=1, s=1.0, g=12):
    a = dict(u1=38, b1=-2, u2=-32, b2=-80, k1=-38, o1=45, k2=42, o2=115)
    b = dict(u1=-32, b1=-80, u2=38, b2=-2, k1=42, o1=115, k2=-38, o2=45)
    return tg_yerlestir(tg_poz(hx, yon=yon, s=s, g=g, **(a if faz % 2 == 0 else b)))


def _hk_kos_anahtarlari(x0, x1, t0, t1, yon, s, faz0=0):
    adim = max(2, int(abs(x1 - x0) / (26 * s)))
    return [(t0 + (t1 - t0) * i / adim, _hk_kos_pozu(x0 + (x1 - x0) * i / adim, faz0 + i, yon, s)) for i in range(adim + 1)]


def hk_duz_kos(x0, x1, s=1.0, cikis_t=0.12, bitis_x=None):
    """Düz koşu: çıkış duruşunda bekler, x0 → x1 koşar. Son anahtar = bitiş_x çizgisini geçiş (ölçüm anı)."""
    yon = 1 if x1 >= x0 else -1
    cikis = tg_yerlestir(tg_poz(x0, s=s, yon=yon, g=25, u1=20, b1=-8, u2=-10, b2=-25, k1=-30, o1=20, k2=35, o2=90))
    # ilk adım çıkış duruşunun önünde başlar: koşu pozunda geride kalan ayak çıkış çizgisinin gerisine taşmasın
    an = [(0.0, cikis), (cikis_t, cikis)] + _hk_kos_anahtarlari(x0 + yon * 22 * s, x1, cikis_t + 0.03, 1.0, yon, s)
    return TgHareket(an, {"cikis_x": x0, "bitis_x": bitis_x if bitis_x is not None else x1})


def hk_donuslu_kos(duraklar, s=1.0, dokun=True, baslangic="yan", t0=0.0, t1=1.0):
    """
    Dönüşlü koşu: duraklar [x0, x1, x2, ...] arası koşar; ara duraklarda öne eğilip çizgiye elle dokunur
    (dokun=True). olay["dokunma"] = [(t, x)]. Son anahtar = son durağı geçiş.
    """
    an = []
    bolum = len(duraklar) - 1
    dokunma = []
    if baslangic == "yan":
        bas = tg_yerlestir(tg_poz(duraklar[0], s=s, cephe=True, g=10, u1=20, b1=-5, u2=-20, b2=5, a1=90, a2=-90,
                                  k1=25, o1=60, k2=-25, o2=-60))
        an += [(0.0, bas), (0.06, bas)]
        t_bas = 0.08
    else:
        t_bas = 0.0
    sure = (1.0 - t_bas) / bolum
    for i in range(bolum):
        xa, xb = duraklar[i], duraklar[i + 1]
        yon = 1 if xb > xa else -1
        son_bolum = i == bolum - 1
        hedef = xb - yon * (0 if son_bolum else 7 * s)
        # ayak penceresi ta–tb: t0/t1 (hareketin kendi zaman aralığı) parametre olarak korunur. Paket 20'ye dek
        # döngü t0/t1'i eziyor, sondaki yeniden ölçekleme bütün kareleri son ayağın penceresine yığıyordu.
        ta = t_bas + i * sure
        tb = ta + sure * (1.0 if son_bolum or not dokun else 0.8)
        an += _hk_kos_anahtarlari(xa + (0 if i == 0 else yon * 7 * s), hedef, ta + (0.01 if an else 0), tb, yon, s)[(1 if an else 0):]
        if dokun and not son_bolum:
            td = ta + sure
            an.append((td, tg_yerlestir(tg_poz(xb - yon * 2 * s, yon=yon, s=s, g=68, u1=62, b1=-22, u2=10, b2=-30,
                                               k1=-6, o1=-2, k2=30, o2=40))))
            dokunma.append((td, xb))
    if (t0, t1) != (0.0, 1.0):        # başka bir hareketle art arda kullanım için zaman aralığı
        an = [(t0 + (t1 - t0) * t, p) for t, p in an]
        dokunma = [(t0 + (t1 - t0) * t, x) for t, x in dokunma]
    return TgHareket(an, {"dokunma": dokunma})


def hk_dikey_sicrama(x, yukselme=12, s=1.0):
    """
    Kollar serbest aktif sıçrama (TSYT): dur → çök (kollar geride) → kalk (kollar yukarı) → TEPE (ölçüm anı).
    CMJ / SJ / DJ'nin ayırt edici anları için hk_sicrama_ani (Paket 18).
    """
    dur = tg_poz(x, s=s)
    cok = tg_yerlestir(tg_poz(x, s=s, g=35, u1=78, b1=-25, u2=72, b2=-22, k1=-55, o1=-40, k2=-48, o2=-30),
                       ayak_x=tg_eklemler(dur)["ayak1"][0])
    kalk = tg_yerlestir(tg_poz(x, s=s, k1=112, o1=126, k2=102, o2=116))
    tepe = dict(kalk, hy=kalk["hy"] - yukselme, a1=40, a2=36, u2=-6, b2=-4)
    e = tg_eklemler(tepe)
    return TgHareket([(0, dur), (0.12, dur), (0.4, cok), (0.62, kalk), (1.0, tepe)],
                     {"zemin_ayak_y": TG_ZEMIN,
                      "tepe_ayak_y": max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))})


def hk_sicrama_ani(x, kip, s=1.0, kutu=None):
    """
    Sıçrama varyantının AYIRT EDİCİ ANI (Paket 18): son anahtar o andır ve durağan görselde o kalır.
    "cmj": ayakta → ön-çömelmenin en alt noktası (çök-sıçra'nın çök'ü); "sj": 90° diz açısında statik çömelme,
    bekler (ön-çömelme yok); "dj": kutunun üstünden öne iner — düşüş anı (havada, kutu ile zemin arasında).
    Eller kalçada. kutu = (sol_x, sag_x, yükseklik). olay: "kalca", "diz", "ayak" (son kare), "kalca_yolu" (cmj),
    "dusus_yolu" (dj).
    """
    kol = dict(k1=-42, o1=52, k2=-22, o2=70)
    dur = tg_poz(x, s=s, **kol)
    cok = tg_yerlestir(tg_poz(x, s=s, g=30, u1=70, b1=-20, u2=58, b2=-8, k1=-44, o1=-16, k2=-30, o2=-4),
                       ayak_x=tg_eklemler(dur)["ayak1"][0])         # 90° çömelme; gövde eğikken eller kalçada
    olay = {"kip": kip}
    if kip == "cmj":                         # ön-çömelme SJ'nin 90°'sinden derin: iki an durağan karede ayrışsın
        dip_kol = dict(k1=-56, o1=-28, k2=-40, o2=-14)          # gövde öne eğikken de eller kalçada
        dip = tg_yerlestir(tg_poz(x, s=s, g=42, u1=88, b1=-34, u2=80, b2=-22, **dip_kol),
                           ayak_x=tg_eklemler(dur)["ayak1"][0])
        an = [(0, dur), (0.3, dur), (1.0, dip)]
        olay["kalca_yolu"] = (dur["hy"], dip["hy"])
    elif kip == "sj":
        kollar_asagi = dict(cok, k1=8, o1=6, k2=-6, o2=-4)
        an = [(0, kollar_asagi), (0.25, cok), (1.0, cok)]
    else:
        sol, sag, yuk = kutu
        ust = TG_ZEMIN - yuk
        uzerinde = tg_yerlestir(tg_poz((sol + sag) / 2, s=s, **kol), zemin=ust)
        adim = tg_yerlestir(tg_poz(sag + 2 * s, s=s, u1=30, b1=10, u2=-10, b2=-6, **kol), zemin=ust)
        adim["hy"] -= 2 * s
        dusus = tg_yerlestir(tg_poz(sag + 14 * s, s=s, u1=10, b1=6, u2=-6, b2=-2, a1=60, a2=60, **kol),
                             zemin=(ust + TG_ZEMIN) / 2)
        an = [(0, uzerinde), (0.3, uzerinde), (0.6, adim), (1.0, dusus)]
        e0, e1 = tg_eklemler(uzerinde), tg_eklemler(dusus)
        olay["dusus_yolu"] = (e0["ayak1"], e1["ayak1"], (e1["ayak1"][0] + 4 * s, TG_ZEMIN))
    e = tg_eklemler(an[-1][1])
    olay.update({"kalca": e["kalca"], "diz": e["diz1"], "ayak": e["ayak1"]})
    return TgHareket(an, olay)


def hk_yana_sicrama(x_sol, x_sag, sicrama=6, s=1.0):
    """Çift ayakla yana sıçrama (önden); son anahtar havada, çıtanın üstünde (sayılan an)."""
    on = dict(cephe=True, u1=4, b1=4, u2=-4, b2=-4, a1=90, a2=-90, k1=35, o1=80, k2=-35, o2=-80, s=s)
    orta = (x_sol + x_sag) / 2
    an = []
    for i in range(sicrama):
        x = x_sol if i % 2 == 0 else x_sag
        yer = tg_poz(x, **on)
        an.append((i / sicrama, yer))
    son_hava = tg_poz(orta, **on)
    son_hava = dict(son_hava, hy=son_hava["hy"] - 10, u1=10, b1=-2, u2=-10, b2=2, k1=50, o1=95, k2=-50, o2=-95)
    an.append((1.0, son_hava))
    return TgHareket(an, {"orta": orta})


def hk_tek_ayak_sekme(x0, engel_x, sekme_sonra=2, adim=14, yukselme=22, s=1.0, ayak="1"):
    """
    Tek ayak sekme: yaklaş, engelin üstünden geç (yüksek), inişten sonra aynı ayakla `sekme_sonra` sıçrama.
    Diğer ayak kalkık kalır. olay["iz"]: engel üstünden geçişin yolu (kesik iz için).
    engel_x=None: engel yok, x0'dan `sekme_sonra` sekme (ör. çember dizisi). ayak: destek ayağı ("1" yakın, "2" uzak).
    """
    d, k = ("1", "2") if ayak in ("1", "cift") else ("2", "1")       # d: destek, k: kalkık bacak
    kalkik = {"u" + k: 55, "b" + k: -70, "k1": 30, "o1": 60, "k2": -25, "o2": 20}
    yer = lambda x: tg_poz(x, s=s, **kalkik)
    hava = lambda x, h: dict(yer(x), hy=yer(x)["hy"] - h, **{"u" + d: 15, "b" + d: -15})
    if ayak == "cift":          # çift ayak sıçrama (CAMSA 1): iki ayak birlikte, inişte dizler bükük, havada toplanır
        yer = lambda x: _hk_uclari_ayir(tg_yerlestir(tg_poz(x, s=s, g=16, u1=30, b1=-16, u2=26, b2=-20,
                                                             k1=-40, o1=-20, k2=-34, o2=-14)))
        hava = lambda x, h: dict(_hk_uclari_ayir(tg_poz(x, s=s, g=8, u1=50, b1=-6, u2=46, b2=-10,
                                                         k1=60, o1=80, k2=54, o2=74)),
                                 hy=yer(x)["hy"] - h)
    if engel_x is None:
        an, x = [(0, yer(x0))], x0
        for i in range(sekme_sonra):
            an += [((i + 0.5) / sekme_sonra, hava(x + adim / 2, yukselme)), ((i + 1) / sekme_sonra, yer(x + adim))]
            x += adim
        return TgHareket(an, {"iz": [], "inisler": [x0 + adim * (i + 1) for i in range(sekme_sonra)]})
    inis = engel_x + 2 * adim
    an = [(0, yer(x0)), (0.14, yer(engel_x - 2 * adim)), (0.3, hava(engel_x, yukselme)), (0.44, yer(inis))]
    x = inis
    for i in range(sekme_sonra):
        t0 = 0.44 + (i + 0.5) * 0.56 / sekme_sonra
        an += [(t0, hava(x + adim / 2, 8)), (0.44 + (i + 1) * 0.56 / sekme_sonra, yer(x + adim))]
        x += adim
    iz = [tg_eklemler(p)["ayak" + d] for p in (yer(engel_x - 2 * adim), hava(engel_x, yukselme), yer(inis))]
    return TgHareket(an, {"iz": iz})


def hk_atma(x, tur="geriye", yon=1, s=1.0, tekrar=2, on_ayak_x=None):
    """
    Atma. tur="geriye": topu önde tutar, hafif çöker, gövdeyi gererek baş üzerinden geriye bırakır
    (ölçüm anı = bırakma; figür bırakma pozunda durur). tur="duvara": göğüs önünden at, yakala.
    tur="suplex": manken geriye köprüyle baş üstünden; tur="one": sporcu mankene sırtını döner, öne eğilir,
    manken sırtının üstünden öne devrilir (iki güreş atışı ayrı hareketlerdir). `tekrar`: atış sayısı.
    olay["birakma_t"], olay["el"] = bırakma anında el; olay["el_yolu"] = bırakmaya kadar el konumları.
    """
    if tur == "suplex":
        return _hk_suplex(x, tekrar=tekrar, s=s)
    if tur == "one":
        return _hk_one_devirme(x, tekrar=tekrar, s=s)
    if tur == "ileri":                                    # iki elle baş üzerinden ileri fırlatma (Latorre)
        p0 = tg_poz(x, yon=yon, s=s, k1=20, o1=40, k2=14, o2=34)
        p1 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=-22, u1=6, b1=-4, u2=-14, b2=-6, k1=176, o1=-150, k2=170, o2=-156))
        p2 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=14, u1=16, b1=2, u2=-18, b2=-8, k1=120, o1=112, k2=104, o2=96))
        an = [(0, p0), (0.15, p0), (0.42, p1), (0.6, p2), (1.0, p2)]
        el_yolu = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an) if t <= 0.6 + 1e-9]
        return TgHareket(an, {"birakma_t": 0.6, "el": tg_eklemler(p2)["el1"], "el_yolu": el_yolu,
                              "tut": tg_eklemler(p2)["el1"]})
    if tur == "geriye":
        p0 = tg_poz(x, yon=yon, s=s, k1=25, o1=40, k2=18, o2=34)
        p1 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=22, u1=42, b1=-28, u2=36, b2=-24, k1=8, o1=25, k2=2, o2=18))
        p2 = tg_poz(x, yon=yon, s=s, g=-16, k1=150, o1=166, k2=138, o2=154, a1=118, a2=112)
        an = [(0, p0), (0.15, p0), (0.38, p1), (0.6, p2), (1.0, p2)]
        t_b = 0.6
    else:   # duvara at - yakala (on_ayak_x: en öndeki ayak ucu bu x'te durur — ör. duvardan 1 m)
        if on_ayak_x is not None:
            e = tg_eklemler(tg_poz(x, s=s, yon=yon))
            x += on_ayak_x - max(e[k][0] * yon for k in ("ayak1", "ayak2", "parmak1", "parmak2")) * yon
        tut = tg_poz(x, s=s, yon=yon, k1=95, o1=120, k2=78, o2=105)
        at = tg_poz(x, s=s, yon=yon, k1=150, o1=125, k2=78, o2=105)
        an = [(0, tut), (0.12, at), (0.42, tut), (0.54, at), (1.0, tut)]
        t_b = 0.12
    el_yolu = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an) if t <= t_b + 1e-9]
    return TgHareket(an, {"birakma_t": t_b, "el": tg_eklemler(dict(an[-1][1]) if tur == "geriye" else an[0][1])["el1"],
                          "el_yolu": el_yolu, "tut": tg_eklemler(an[-1][1])["el1"]})


def hk_kavrama(x, s=1.0):
    """El kavrama: aleti göğüs önünden indirir, kol gergin ve aşağıda SIKAR (ölçüm anı: parmaklar kapanır)."""
    p0 = tg_poz(x, s=s, k1=45, o1=150)
    p1 = tg_poz(x, s=s, k1=10, o1=8)
    p2 = dict(p1, k1=11, o1=11)
    return TgHareket([(0, p0), (0.12, p0), (0.5, p1), (0.75, p1), (1.0, p2)], {"el": tg_eklemler(p2)["el1"]})


def hk_oturarak_uzanma(ayak_x, s=1.0, egim=50, tek_bacak=False):
    """
    Bacaklar gergin oturuş; kalçadan bükülüp iki kolla öne uzanır, EN UZAK noktada durur.
    tek_bacak=True (Back-Saver): yalnız yakın bacak düz ve kutuda; uzak bacak dizden bükülü, ayak tabanı yerde.
    """
    hx = ayak_x - (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s - 1
    # uzak bacak yerde, yakın bacak hafif yukarıda (yandan bakışta iki ayak tabanı da sehpaya dayalı, üst üste değil)
    temel = dict(hy=TG_ZEMIN - 5, u1=90, b1=90, u2=84, b2=84, a1=180, a2=172, s=s)
    if tek_bacak:
        temel.update(u2=140, b2=26, a2=80)
    p0 = tg_poz(hx, g=0, k1=30, o1=60, k2=20, o2=48, **temel)
    p1 = tg_poz(hx, g=egim, k1=96, o1=94, k2=86, o2=78, **temel)
    return TgHareket([(0, p0), (0.2, p0), (0.8, p1), (1.0, p1)], {"el": tg_eklemler(p1)["el1"]})


def hk_denge(tur="kiris_geriye", x0=60, x1=170, taban=None, adim=6, s=1.0):
    """
    Denge. tur="kiris_geriye": kirişte geriye yürüme (yüz bir yöne, ilerleme ters yöne), kollar yanda;
    tur="kiris_ileri": kirişte öne yürüme.
    tur="platform": iki platform arasında yana geçiş — olay["platform"] platformun öteleme anahtarları.
    """
    if tur in ("kiris_geriye", "kiris_ileri"):           # ileri: yüz ilerleme yönünde (KMS balans)
        taban = TG_ZEMIN if taban is None else taban
        an = []
        for i in range(adim + 1):
            f = 1 if i % 2 else -1
            p = tg_poz(x0 + (x1 - x0) * i / adim, yon=-1 if tur == "kiris_geriye" else 1, s=s, u1=12 * f, b1=6 * f,
                       u2=-12 * f, b2=-6 * f, k1=72, o1=84, k2=-64, o2=-78)
            an.append((i / adim, tg_yerlestir(p, zemin=taban)))
        return TgHareket(an, {"adimlar": [x0 + (x1 - x0) * i / adim for i in range(adim + 1)]})
    taban = TG_ZEMIN - 7 if taban is None else taban
    on = dict(cephe=True, u1=5, b1=5, u2=-6, b2=-5, a1=90, a2=-90, k1=20, o1=18, k2=-22, o2=-18, s=s)
    a, b_, c = (tg_yerlestir(tg_poz(x, **on), zemin=taban) for x in (x0, x0 + 30, x0 + 60))
    egil = dict(b_, g=-35, k1=-30, o1=-26, k2=-50, o2=-46, u1=20, b1=-10, u2=10, b2=-15)
    egil = tg_yerlestir(egil, zemin=taban)
    an = [(0, a), (0.15, a), (0.32, b_), (0.45, egil), (0.62, dict(b_, k1=60, o1=60)), (1.0, c)]
    return TgHareket(an, {"platform": [(0, 0, 0), (0.42, 0, 0), (0.52, 15, -30), (0.62, 60, 0), (1, 60, 0)]})


def hk_antropometri(x, tur="ayakta", oturak_y=None, s=1.0):
    """
    Ayakta antropometri. tur="ayakta": dik duruş (boy); "oturarak": dizler 90° oturuş (oturma yüksekliği);
    "kulac": önden, kollar aşağıdan yere paralel açılır. Son anahtar = ölçüm anı.
    """
    if tur == "ayakta":
        p = tg_poz(x, s=s)
        return TgHareket([(0, p), (1, p)], {"bas_ust": tg_eklemler(p)["bas"][1] - _TG_BOY["bas"] * s})
    if tur == "oturarak":
        p = tg_poz(x, s=s, hy=oturak_y, u1=90, b1=0, u2=82, b2=-8, k1=24, o1=64, k2=16, o2=56)
        return TgHareket([(0, p), (1, p)], {"bas_ust": tg_eklemler(p)["bas"][1] - _TG_BOY["bas"] * s})
    p0 = tg_poz(x, s=s, cephe=True, u1=5, b1=5, u2=-5, b2=-5, a1=90, a2=-90, k1=10, o1=6, k2=-10, o2=-6)
    p1 = dict(p0, k1=90, o1=90, k2=-90, o2=-90)
    return TgHareket([(0, p0), (0.15, p0), (0.6, p1), (1, p1)], {"eller": (tg_eklemler(p1)["el2"], tg_eklemler(p1)["el1"])})


def hk_iz(hareket, sira=0, dx=0.0):
    """
    Hareketin bir anahtar pozunu (varsayılan: başlangıç) sabit, çok soluk bir iz olarak verir: durağan görselde
    hareketin nereden başladığı görünür (CMJ ayakta, SJ çömelik, DJ kutunun üstünde başlar). Ölçülen figür değildir.
    """
    p = dict(hareket.anahtarlar[sira][1])
    p["hx"] += dx                                   # dx: hareketin gerisine kaydırılmış iz (art arda okunsun)
    return TgHareket([(0.0, p), (1.0, p)], {"rol": "iz"})


def hk_ikinci_figur(hareket, rol="partner"):
    """
    Aynı sahnede ikinci figür (partner, manken, rakip). Ölçülen sporcu normal kalınlıkta ve tam opak;
    ikinci figür GÖRSEL SİSTEM'deki "ikinci_kisi" katmanıyla (ayrı renk tonu, ince) çizilir. Temas (tutuş, atış)
    için iki figürün anahtarları aynı zamanlarla kurulur; eller ve kalçalar aynı noktaya getirilebilir.
    """
    anahtarlar = hareket.anahtarlar if hasattr(hareket, "anahtarlar") else hareket
    olay = dict(hareket.olay) if hasattr(hareket, "olay") else {}
    olay["rol"] = rol
    return TgHareket(anahtarlar, olay)


def _hk_catmull(noktalar, n=10):
    """Noktalardan geçen yumuşak eğri (Catmull-Rom)."""
    p = [noktalar[0]] + list(noktalar) + [noktalar[-1]]
    cikti = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for j in range(n):
            t = j / n
            cikti.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                      + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    cikti.append(tuple(noktalar[-1]))
    return cikti


def hk_kavisli_yol(noktalar, s=0.5, kip="kos", yumusak=True, t0=0.0, t1=1.0, baslangic=None, dokun=()):
    """
    Düz olmayan güzergâh (zemin düzleminde): viraj, S çizgisi, köşe dönüşü, çeviklik parkuru. noktalar: [(x, y)]
    geçiş noktaları — y zemindeki derinliktir; figürün ayakları bu noktada durur. yumusak=False: köşeli yol.
    kip="kos" ya da "paten". baslangic="yuzustu": ilk noktada yüzüstü yatar, kalkıp koşar (Illinois).
    dokun: bu sıradaki noktalarda öne eğilip yere elle dokunur (VAT köşeleri). olay["yol"]: kesik çizgi noktaları,
    olay["dokunma"]: [(t, x, y)].
    """
    if baslangic == "yuzustu":
        t_bas = t0 + 0.12 * (t1 - t0)
        ilk = TgHareket([], {})
        x0, y0 = noktalar[0]
        yon0 = 1 if noktalar[1][0] >= x0 else -1
        yat = tg_poz(x0 - yon0 * 24 * s, s=s, yon=yon0, g=88, u1=-88, b1=-90, u2=-92, b2=-94, a1=0, a2=4,
                     k1=8, o1=70, k2=-4, o2=62)
        yat = dict(yat, hy=y0 - 3 * s)
        alt = hk_kavisli_yol(noktalar, s, kip, yumusak, t_bas, t1, None, dokun)
        return TgHareket([(t0, yat), (t0 + 0.05 * (t1 - t0), yat)] + alt.anahtarlar, alt.olay)
    yol = _hk_catmull(noktalar) if yumusak else list(noktalar)
    uz = [0.0]
    for a, b in zip(yol, yol[1:]):
        uz.append(uz[-1] + _math.dist(a, b))
    adim = 20 * s
    sayi = max(2, int(uz[-1] / adim))
    an, yon = [], 1
    for i in range(sayi + 1):
        hedef = uz[-1] * i / sayi
        j = max(0, min(len(yol) - 2, next((k for k in range(len(uz) - 1) if uz[k + 1] >= hedef), len(yol) - 2)))
        f = (hedef - uz[j]) / ((uz[j + 1] - uz[j]) or 1)
        x = yol[j][0] + (yol[j + 1][0] - yol[j][0]) * f
        y = yol[j][1] + (yol[j + 1][1] - yol[j][1]) * f
        dx = yol[j + 1][0] - yol[j][0]
        if abs(dx) > 0.3:
            yon = 1 if dx > 0 else -1
        p = _hk_paten_pozu(x, i, yon, s) if kip == "paten" else _hk_kos_pozu(x, i, yon, s)
        an.append((t0 + (t1 - t0) * i / sayi, tg_yerlestir(p, zemin=y)))
    dokunma = []
    for j in dokun:                          # en yakın kareyi o noktada yere dokunma pozuyla değiştir
        nx, ny = noktalar[j]
        i = min(range(len(an)), key=lambda k: _math.dist((an[k][1]["hx"], tg_eklemler(an[k][1])["ayak1"][1]), (nx, ny)))
        yon_i = an[i][1].get("yon", 1)
        an[i] = (an[i][0], tg_yerlestir(tg_poz(nx - yon_i * 6 * s, yon=yon_i, s=s, g=68, u1=62, b1=-22, u2=10, b2=-30,
                                                k1=-6, o1=-2, k2=30, o2=40), zemin=ny))
        dokunma.append((an[i][0], nx, ny))
    return TgHareket(an, {"yol": yol, "dokunma": dokunma})


def _hk_paten_pozu(hx, faz, yon=1, s=1.0):
    """Paten süzülme pozu: gövde öne eğik, destek dizi bükük, iten bacak geride-yanda gergin."""
    a = dict(g=40, u1=38, b1=-18, u2=-52, b2=-64, a2=150, k1=-34, o1=6, k2=58, o2=82)
    b = dict(g=40, u2=38, b2=-18, u1=-52, b1=-64, a1=150, k2=-34, o2=6, k1=58, o1=82)
    return tg_yerlestir(tg_poz(hx, yon=yon, s=s, **(a if faz % 2 == 0 else b)))


def hk_paten(x0, x1, s=1.0, cikis_t=0.1, adim=None):
    """
    Buz üstü kayma adımı: durarak başlangıç (çömelik), sonra iten bacak geride-yanda gerilir ve uzun süzülme
    (aynı poz ilerler), ardından bacak değişir. Son anahtar = x1 (bitiş çizgisini geçiş — ölçüm anı).
    Zemin çizgisi değişmez; yalnız hareket farklıdır.
    """
    yon = 1 if x1 >= x0 else -1
    adim = adim or 34 * s
    cikis = tg_yerlestir(tg_poz(x0, s=s, yon=yon, g=42, u1=55, b1=-25, u2=40, b2=-30, k1=-20, o1=20, k2=40, o2=70))
    an = [(0.0, cikis), (cikis_t, cikis)]
    sayi = max(2, int(abs(x1 - x0) / adim))
    for i in range(sayi):
        ta = cikis_t + (1 - cikis_t) * i / sayi
        tb = cikis_t + (1 - cikis_t) * (i + 0.75) / sayi
        xa = x0 + (x1 - x0) * i / sayi + yon * (30 if i == 0 else 8) * s   # ilk itiş çıkışın önünde
        xb = x0 + (x1 - x0) * (i + 0.75) / sayi
        an += [(ta + 0.01, _hk_paten_pozu(xa, i, yon, s)), (tb, _hk_paten_pozu(xb, i, yon, s))]   # it + süzül
    an.append((1.0, _hk_paten_pozu(x1, sayi, yon, s)))
    return TgHareket(an, {"cikis_x": x0, "bitis_x": x1})


def _hk_suplex(x, tekrar=2, s=1.0, mesafe=22):
    """
    Güreş atışı (suplex): sporcu mankeni belinden kavrar, kaldırır, gövdesini geriye gererek mankeni başının
    üstünden arkasına sırtüstü devirir. `tekrar` atış; son anahtar = son atışın tamamlandığı an (sayılan an).
    Manken hk_ikinci_figur ile soluk çizilir; kavrama karesinde sporcunun elleri mankenin kalçasındadır.
    """
    xm = x + mesafe
    dur = tg_poz(x, s=s, k1=40, o1=70, k2=30, o2=60)
    kavra = tg_yerlestir(tg_poz(x, s=s, g=15, u1=38, b1=-22, u2=30, b2=-24, k1=25, o1=40, k2=18, o2=34))
    kaldir = tg_yerlestir(tg_poz(x, s=s, g=-30, u1=28, b1=-32, u2=20, b2=-30, k1=150, o1=170, k2=140, o2=160))
    bitir = tg_yerlestir(tg_poz(x + 4, s=s, g=-12, u1=20, b1=-20, u2=10, b2=-22, k1=95, o1=112, k2=80, o2=100))
    m_dur = tg_poz(xm, s=s, yon=-1, k1=55, o1=80, k2=45, o2=72)
    m_kavra = tg_poz(xm - 2, s=s, yon=-1, g=10, k1=60, o1=85, k2=50, o2=78)
    m_havada = dict(tg_poz(x + 2, s=s, yon=-1, g=95, u1=-35, b1=-45, u2=-25, b2=-40, k1=150, o1=150, k2=140, o2=140),
                    hy=TG_ZEMIN - 60 * s)
    m_yerde = dict(tg_poz(x - 40 * s, s=s, yon=-1, g=92, u1=-150, b1=-70, u2=-140, b2=-80, k1=160, o1=170, k2=150, o2=160),
                   hy=TG_ZEMIN - 7 * s)
    a_an, m_an = [], []
    pay = 1.0 / tekrar
    sayac = []
    for i in range(tekrar):
        b = i * pay
        a_an += [(b, dur), (b + 0.18 * pay, kavra), (b + 0.5 * pay, kaldir), (b + 0.85 * pay, bitir)]
        m_an += [(b, m_dur), (b + 0.18 * pay, m_kavra), (b + 0.5 * pay, m_havada), (b + 0.85 * pay, m_yerde)]
        sayac.append(b + 0.85 * pay)
    a_an.append((1.0, bitir))
    m_an.append((1.0, m_yerde))
    temas = (tg_eklemler(kavra)["el1"], tg_eklemler(m_kavra)["kalca"])
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an, "partner"), "atis_anlari": sayac, "temas": temas})


def _hk_ayna(p, merkez):
    """Pozun x = merkez çevresinde aynası (yön döner; açılar yöne göre tanımlı olduğu için değişmez)."""
    return dict(p, hx=2 * merkez - p["hx"], yon=-p.get("yon", 1))


def _hk_one_pozlari(x, s=1.0, mesafe=22):
    """Öne devirmenin anahtar pozları: sporcu x'te sağa bakar, manken x + mesafe'de sola bakar."""
    xm = x + mesafe
    return {
        "dur": tg_poz(x, s=s, k1=40, o1=70, k2=30, o2=60),
        "gir": tg_yerlestir(tg_poz(x + 12 * s, s=s, yon=-1, g=22, u1=30, b1=-18, u2=22, b2=-24,
                                   k1=-150, o1=-110, k2=-135, o2=-95)),
        "yukle": tg_yerlestir(tg_poz(x + 10 * s, s=s, yon=-1, g=62, u1=48, b1=-14, u2=36, b2=-22,
                                     k1=-60, o1=-20, k2=-48, o2=-12)),
        "bitir": tg_yerlestir(tg_poz(x + 6 * s, s=s, yon=-1, g=52, u1=40, b1=-16, u2=-20, b2=-34,
                                     k1=40, o1=20, k2=26, o2=8)),
        "m_dur": tg_poz(xm, s=s, yon=-1, k1=55, o1=80, k2=45, o2=72),
        "m_gir": tg_poz(xm - 4 * s, s=s, yon=-1, g=24, k1=60, o1=85, k2=50, o2=78),
        "m_ucus": dict(tg_poz(x + 4 * s, s=s, yon=-1, g=150, u1=160, b1=170, u2=150, b2=165,
                              k1=-40, o1=-20, k2=-30, o2=-10), hy=TG_ZEMIN - 50 * s),
        "m_yerde": dict(tg_poz(x - 22 * s, s=s, yon=1, g=-92, u1=88, b1=92, u2=84, b2=96,
                               k1=-100, o1=-95, k2=-108, o2=-100), hy=TG_ZEMIN - 7 * s),
    }


def _hk_one_devirme(x, tekrar=2, s=1.0, mesafe=22):
    """
    Öne devirme: sporcu mankene sırtını dönerek içeri girer (yön değişir), kollarıyla mankeni omzunun üstünden
    kavrar, öne eğilip mankeni sırtının üstünden önüne sırtüstü devirir. Son anahtar = atışın tamamlandığı an.
    Suplex'ten ayrımı: bitişte sporcu öne eğik ve atış yönüne bakar; manken önüne düşer.
    """
    P = _hk_one_pozlari(x, s, mesafe)
    dur = P["dur"]
    gir, yukle, bitir = P["gir"], P["yukle"], P["bitir"]
    m_dur, m_gir, m_ucus, m_yerde = P["m_dur"], P["m_gir"], P["m_ucus"], P["m_yerde"]
    a_an, m_an, sayac = [], [], []
    pay = 1.0 / tekrar
    for i in range(tekrar):
        b = i * pay
        a_an += [(b, dur), (b + 0.2 * pay, gir), (b + 0.5 * pay, yukle), (b + 0.85 * pay, bitir)]
        m_an += [(b, m_dur), (b + 0.2 * pay, m_gir), (b + 0.5 * pay, m_ucus), (b + 0.85 * pay, m_yerde)]
        sayac.append(b + 0.85 * pay)
    a_an.append((1.0, bitir))
    m_an.append((1.0, m_yerde))
    temas = (tg_eklemler(gir)["el1"], tg_eklemler(m_gir)["boyun"])
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an, "partner"), "atis_anlari": sayac, "temas": temas})


def hk_pedal(x, s=1.0, tur=4):
    """
    Bisiklet ergometresinde oturarak pedal çevirme. Kalça selede sabit; ayaklar krank çemberinde döner
    (iki bacak yarım tur farkla), diz öne bakar (iki parçalı ters kinematik). Gövde öne eğik, eller gidonda.
    olay: "krank" (merkez), "sele", "gidon", "r" (krank yarıçapı). Son anahtar = 30 sn'nin sonu.
    """
    hx, hy = x, TG_ZEMIN - 50 * s
    cx, cy = hx + 8 * s, hy + 30 * s
    r = 7.5 * s
    L1, L2 = _TG_BOY["uyluk"] * s, _TG_BOY["baldir"] * s
    ust = dict(g=28, k1=58, o1=84, k2=52, o2=76, s=s)
    govde = tg_eklemler(tg_poz(hx, hy=hy, **ust))
    gidon = (govde["el1"][0] + 1, govde["el1"][1])

    def bacak(aci):
        px, py = cx + r * _math.cos(aci), cy + r * _math.sin(aci)
        d = min(_math.dist((hx, hy), (px, py)), L1 + L2 - 0.01)
        a = _math.atan2(px - hx, py - hy)                       # kalçadan pedala (aşağıdan ölçülen)
        ic = _math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        u = a + ic                                                # diz öne
        dx, dy = hx + L1 * _math.sin(u), hy + L1 * _math.cos(u)
        b = _math.atan2(px - dx, py - dy)
        return _math.degrees(u), _math.degrees(b)
    an, adim = [], 8
    for i in range(tur * adim + 1):
        aci = 2 * _math.pi * i / adim                # tepe noktada pedal öne (+x) gider: sürücü sağa bakar (Paket 27)
        u1, b1 = bacak(aci)
        u2, b2 = bacak(aci + _math.pi)
        an.append((i / (tur * adim), tg_poz(hx, hy=hy, u1=u1, b1=b1, u2=u2, b2=b2, a1=96, a2=96, **ust)))
    return TgHareket(an, {"krank": (cx, cy), "sele": (hx, hy + 2), "gidon": gidon, "r": r})


def hk_nordic(diz_x, diz_y, s=1.0, son_aci=58, yon=1):
    """
    Nordic hamstring: diz üstü, ayak bilekleri sabit (baldır geride yatay); diz eklemi çevresinde gövde + uyluk
    düz bir çizgi halinde öne YAVAŞÇA iner (eksantrik). Son anahtar = kopma anı (son_aci, dikeyden).
    olay: "diz" (sabit), "bilek" (sabit tutulan nokta), "aci_yolu" [(t, açı)].
    """
    L = _TG_BOY["uyluk"] * s

    def poz(aci, kol):
        r = _math.radians(aci)
        return dict(tg_poz(diz_x + yon * L * _math.sin(r), s=s, yon=yon, g=aci, u1=-aci, b1=-90, u2=-aci, b2=-80,
                           a1=0, a2=6, **kol), hy=diz_y - L * _math.cos(r))
    dik = dict(k1=28, o1=96, k2=20, o2=88)            # kollar göğüs önünde çapraz
    hazir = dict(k1=70, o1=60, k2=60, o2=52)          # kopma anında eller düşüşü karşılamaya hazır
    acilar = [(0.0, 0), (0.15, 0), (0.45, 18), (0.75, 38), (1.0, son_aci)]
    an = [(t, poz(a, dik if t < 0.75 else hazir)) for t, a in acilar]
    e = tg_eklemler(an[-1][1])
    return TgHareket(an, {"diz": (diz_x, diz_y), "bilek": e["ayak1"], "aci_yolu": acilar})


def hk_dinamometre(kalca_x, kalca_y, s=1.0):
    """
    İzokinetik dinamometre koltuğunda oturuş: uyluk yatay ve sabit, diz ekseni cihaz başında, kaval kemiği kola
    bağlı. Sıra: 90° izometrik (kaval dik) → 180°/sn izokinetik ekstansiyon-fleksiyon → 45° izometrik (son anahtar).
    b1 = kavalın dikeyden açısı: 0 → diz 90° fleksiyon, 45 → diz 45° fleksiyon. olay: "diz", "ayak_yolu" (kol ucu).
    """
    ust = dict(g=-12, u1=90, u2=88, b2=8, a1=90, a2=96, k1=8, o1=-6, k2=14, o2=2, s=s)
    an = [(t, dict(tg_poz(kalca_x, hy=kalca_y, b1=b, **ust))) for t, b in
          [(0.0, 0), (0.22, 0), (0.36, 82), (0.5, 4), (0.64, 82), (0.78, 4), (0.86, 45), (1.0, 45)]]
    yol = [(t, *tg_eklemler(p)["ayak1"]) for t, p in _tg_kareler(an)]
    return TgHareket(an, {"diz": tg_eklemler(an[0][1])["diz1"], "ayak_yolu": yol})


def hk_iki_uke_atis(x_sol, x_sag, s=1.0, mesafe=22):
    """
    Judo SJFT: iki uke (atılan) x_sol ve x_sag'da durur, tori ortadan başlar; sağdaki ukeye koşup öne devirme
    (sırttan atış), soldakine koşup aynısı, sonra kalkmış olan sağdakine bir kez daha: 3 atış (A, B, C periyotları).
    olay: "ukeler" [sol, sağ] (hk_ikinci_figur), "atis_anlari" [3].
    """
    orta = (x_sol + x_sag) / 2
    xa = x_sag - mesafe * s                                  # sağdakine atış konumu (sağa bakar)
    Rp = _hk_one_pozlari(xa, s, mesafe * s)
    c = (x_sag + x_sol) / 2                                   # ayna: sağdaki ukeyi soldakine taşır
    Lp = {k: _hk_ayna(v, c) for k, v in Rp.items()}
    t_an = [(0.0, tg_poz(orta, s=s, k1=40, o1=70, k2=30, o2=60)), (0.05, tg_poz(orta, s=s, k1=40, o1=70, k2=30, o2=60))]
    t_an += _hk_kos_anahtarlari(orta, xa, 0.06, 0.13, 1, s)[1:]
    t_an += [(0.14, Rp["dur"]), (0.18, Rp["gir"]), (0.23, Rp["yukle"]), (0.28, Rp["bitir"])]
    t_an += _hk_kos_anahtarlari(Rp["bitir"]["hx"], Lp["dur"]["hx"], 0.3, 0.42, -1, s)[1:]
    t_an += [(0.43, Lp["dur"]), (0.47, Lp["gir"]), (0.52, Lp["yukle"]), (0.57, Lp["bitir"])]
    t_an += _hk_kos_anahtarlari(Lp["bitir"]["hx"], Rp["dur"]["hx"], 0.59, 0.71, 1, s)[1:]
    t_an += [(0.72, Rp["dur"]), (0.76, Rp["gir"]), (0.81, Rp["yukle"]), (0.86, Rp["bitir"]), (1.0, Rp["bitir"])]
    sag = [(0.0, Rp["m_dur"]), (0.14, Rp["m_dur"]), (0.18, Rp["m_gir"]), (0.23, Rp["m_ucus"]), (0.28, Rp["m_yerde"]),
           (0.42, Rp["m_yerde"]), (0.6, Rp["m_dur"]), (0.72, Rp["m_dur"]), (0.76, Rp["m_gir"]), (0.81, Rp["m_ucus"]),
           (0.86, Rp["m_yerde"]), (1.0, Rp["m_yerde"])]
    sol = [(0.0, Lp["m_dur"]), (0.43, Lp["m_dur"]), (0.47, Lp["m_gir"]), (0.52, Lp["m_ucus"]), (0.57, Lp["m_yerde"]),
           (1.0, Lp["m_yerde"])]
    return TgHareket(t_an, {"ukeler": [hk_ikinci_figur(sol), hk_ikinci_figur(sag)], "atis_anlari": [0.28, 0.57, 0.86]})


def hk_uchikomi(x, tekrar=3, s=1.0, mesafe=22):
    """
    Uchi-komi: tutuş alınır, tori giriş yapar (sırtını döner, kalçayı ukenin önüne sokar) ve çıkar; ATIŞ YOK.
    Son anahtar = son giriş anı (durağan görselde giriş görünür). olay: "partner", "giris_anlari".
    """
    P = _hk_one_pozlari(x, s, mesafe * s)
    tut = tg_poz(x, s=s, g=12, u1=14, b1=2, u2=-14, b2=-6, k1=68, o1=92, k2=58, o2=84)
    m_tut = tg_poz(x + mesafe * s, s=s, yon=-1, g=10, u1=12, b1=2, u2=-12, b2=-6, k1=64, o1=88, k2=54, o2=80)
    gir = P["gir"]
    m_gir = P["m_gir"]
    a_an, m_an, giris = [(0.0, tut)], [(0.0, m_tut)], []
    pay = 1.0 / tekrar
    for i in range(tekrar):
        b = i * pay
        a_an += [(b + 0.15 * pay, tut), (b + 0.55 * pay, gir)]
        m_an += [(b + 0.15 * pay, m_tut), (b + 0.55 * pay, m_gir)]
        giris.append(b + 0.55 * pay)
        if i < tekrar - 1:
            a_an.append((b + 0.95 * pay, tut))
            m_an.append((b + 0.95 * pay, m_tut))
    a_an.append((1.0, gir))
    m_an.append((1.0, m_gir))
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an), "giris_anlari": giris})


# Vuruş teknikleri (yan görünüş, sağa bakan sporcu; 1 = yakın/ön, 2 = uzak/arka uzuv). Değerler gardan farktır.
_HK_GARD = dict(g=8, u1=14, b1=4, u2=-16, b2=-8, k1=30, o1=150, k2=20, o2=160)


_HK_TEKNIK = {
    "jab": dict(k1=88, o1=90), "tsuki": dict(k1=88, o1=90),
    "cross": dict(g=16, k2=88, o2=90, u2=-24),
    "hook": dict(g=12, k1=96, o1=150), "uchi": dict(g=12, k1=96, o1=150),
    "uppercut": dict(g=4, k2=44, o2=172),
    "teep": dict(g=-10, u1=95, b1=86, u2=-4, b2=0), "ap": dict(g=-10, u1=95, b1=86, u2=-4, b2=0),
    "geri": dict(g=-10, u1=95, b1=86, u2=-4, b2=0),
    "yop": dict(g=-30, u1=92, b1=92, u2=-4, b2=0),
    "knee": dict(g=-6, u2=100, b2=-20, k1=60, o1=110, k2=56, o2=104),
    "roundhouse": dict(g=-18, u2=88, b2=82, u1=4, b1=0),
    "dollyo": dict(g=-28, u2=116, b2=110, u1=6, b1=0),
}


def hk_vurus(x, teknikler, s=1.0, yon=1):
    """
    Vuruş serisi (boks, kickboks, Muay Thai, karate, taekwondo): gardda bekler, sıradaki tekniği uzatır, garda
    döner. Son anahtar = son tekniğin vuruş anı (durağan görselde vuruş görünür). olay: "darbe_anlari",
    "erisim" (son vuruşta en öndeki uç: el ya da ayak — hedef bu noktaya konur).
    """
    gard = tg_yerlestir(tg_poz(x, s=s, yon=yon, **_HK_GARD))
    an, darbe = [(0.0, gard), (0.08, gard)], []
    pay = 0.92 / len(teknikler)
    for i, t in enumerate(teknikler):
        b = 0.08 + i * pay
        vur = tg_yerlestir(tg_poz(x, s=s, yon=yon, **dict(_HK_GARD, **_HK_TEKNIK[t])))
        an.append((b + 0.45 * pay, vur))
        darbe.append(b + 0.45 * pay)
        if i < len(teknikler) - 1:
            an.append((b + 0.9 * pay, gard))
    an.append((1.0, an[-1][1]))
    e = tg_eklemler(an[-1][1])
    uc = max((e[k] for k in ("el1", "el2", "ayak1", "ayak2", "parmak1", "parmak2")), key=lambda q: q[0] * yon)
    return TgHareket(an, {"darbe_anlari": darbe, "erisim": uc})


def hk_asilma_bukumlu(x, bar_y, s=1.0):
    """
    Asılı durma, bükümlü kol (Eurofit BAH): bara avuçlar öne tutunur, dirsekler bükük, çene barın ÜSTÜNDE; ayaklar
    yerden kesik. Son anahtar = asılı (süre ölçülürken). olay: "el", "cene_y".
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    kol = dict(k1=24, o1=172, k2=30, o2=178)
    govde = tg_poz(x, s=s, u1=50, b1=-30, u2=36, b2=-44, a1=70, a2=64, **kol)
    e = tg_eklemler(govde)
    asili = dict(govde, hy=govde["hy"] + (bar_y - e["el1"][1]))          # eller barda
    asili = _hk_uclari_ayir(asili, el=(-4.2, 0))                         # öbür el barda, biraz geride
    uzan = tg_yerlestir(tg_poz(x, s=s, k1=170, o1=172, k2=186, o2=184))
    an = [(0.0, uzan), (0.12, uzan), (0.3, asili), (1.0, asili)]
    son = tg_eklemler(asili)
    return TgHareket(an, {"el": son["el1"], "cene_y": son["bas"][1] + L["bas"] * 0.8})


def hk_asilma(x, tutma_y, s=1.0):
    """
    Askıda kavrama (gi/kurtka yakası): altında durup uzanır, yakayı kavrar, ayaklar yerden kesilir ve asılı
    kalır; son anahtar = asılı (süre ölçülürken). Eller tutma noktasında. olay: "el" (tutma noktası).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    asili = dict(tg_poz(x, s=s, u1=56, b1=-34, u2=40, b2=-50, k1=174, o1=176, k2=188, o2=186, a1=70, a2=64),
                 hy=tutma_y + L["govde"] + L["ust"] + L["on"])
    uzan = tg_yerlestir(tg_poz(x, s=s, k1=170, o1=172, k2=186, o2=184))
    an = [(0.0, uzan), (0.12, uzan), (0.25, asili), (1.0, asili)]
    return TgHareket(an, {"el": tg_eklemler(asili)["el1"]})


def hk_yan_adim(x_sol, x_sag, tekrar=3, s=1.0):
    """Yana karışık adım (önden): ayaklar açılıp kapanarak sağ-sol çizgiler arası gidip gelir; son anahtar sağda."""
    on = dict(cephe=True, a1=90, a2=-90, k1=40, o1=80, k2=-40, o2=-80, s=s, g=6)
    acik = dict(on, u1=12, b1=8, u2=-12, b2=-8)
    kapali = dict(on, u1=5, b1=3, u2=-5, b2=-3)
    an, n = [], 2 * tekrar
    for i in range(n + 1):
        x = x_sol if i % 2 == 0 else x_sag
        an.append((i / n, tg_poz(x, **acik)))
        if i < n:
            an.append(((i + 0.5) / n, tg_poz((x_sol + x_sag) / 2, **kapali)))
    return TgHareket(an, {})


def _hk_iki_parca(kok, hedef, L1, L2, yon=1, bukum=1):
    """
    İki parçalı uzuv ters kinematiği: kökten hedefe (el ya da ayak) uzanan iki açıyı verir (aşağıdan ölçülen,
    + = yöne doğru). bukum: ara eklemin (dirsek/diz) hangi yana kırılacağı (+1 / −1).
    """
    dx, dy = hedef[0] - kok[0], hedef[1] - kok[1]
    d = max(1e-6, min(_math.hypot(dx, dy), L1 + L2 - 1e-6))
    a = _math.atan2(dx * yon, dy)
    ic = _math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    t1 = a + bukum * ic
    ex, ey = kok[0] + yon * L1 * _math.sin(t1), kok[1] + L1 * _math.cos(t1)
    t2 = _math.atan2((hedef[0] - ex) * yon, hedef[1] - ey)
    return _math.degrees(t1), _math.degrees(t2)


def _hk_kollar_hedefe(p, el1, el2=None, bukum1=1, bukum2=1):
    """Pozun kollarını hedef noktalara uzatır (omuz yerinden). Gövde ve bacaklar aynı kalır."""
    s, yon = p.get("s", 1.0), p.get("yon", 1)
    e = tg_eklemler(p)
    L1, L2 = _TG_BOY["ust"] * s, _TG_BOY["on"] * s
    q = dict(p)
    q["k1"], q["o1"] = _hk_iki_parca(e["kok_k1"], el1, L1, L2, yon, bukum1)
    if el2 is not None:
        q["k2"], q["o2"] = _hk_iki_parca(e["kok_k2"], el2, L1, L2, yon, bukum2)
    return q


def _hk_kol_sec(p, kol, hedef, olcut):
    """
    Tek kolu hedefe uzatır; iki dirsek çözümünden olcut(dirsek, omuz) değeri küçük olanı seçer
    (ör. dirsek yukarıda: lambda d, o: d[1]; dirsek dışta: lambda d, o: -abs(d[0] - o[0])).
    """
    en = None
    for b in (1, -1):
        q = _hk_kollar_hedefe(p, hedef, None, b, b) if kol == "1" else dict(p)
        if kol == "2":
            s_, yon = p.get("s", 1.0), p.get("yon", 1)
            e0 = tg_eklemler(p)
            q["k2"], q["o2"] = _hk_iki_parca(e0["kok_k2"], hedef, _TG_BOY["ust"] * s_, _TG_BOY["on"] * s_, yon, b)
        e = tg_eklemler(q)
        puan = olcut(e["dirsek" + kol], e["kok_k" + kol])
        if en is None or puan < en[0]:
            en = (puan, q)
    return en[1]


def _hk_yere_koy(p, noktalar):
    """Pozu dikey kaydırır: verilen eklemlerden en alttaki zemine değer (yatış, diz üstü, şınav)."""
    e = tg_eklemler(p)
    return dict(p, hy=p["hy"] + (TG_ZEMIN - max(e[k][1] for k in noktalar)))


def _hk_uclari_ayir(p, el=(4.0, 0.0), pay=3.4):
    """
    Yandan bakışta uzak el/ayak yakınınkinin tam arkasına düşerse (TG_EN_YAKIN_UC) ayırır — figür tek çubuk gibi
    görünmesin. Uzak el, yakın elin el=(dx, dy) kadar yanına uzanır (yerde/barda kalsın diye yön çağırandan);
    uzak ayak için uyluk ve baldır açısı en az değişecek biçimde aranır; ayak yere girmez, en çok 5,5 birim
    yukarıda kalabilir (uzak uzuv tuvalde biraz yukarıda: derinlik).
    """
    q = dict(p)
    e = tg_eklemler(q)
    if _math.dist(e["el1"], e["el2"]) < pay:
        hedef = (e["el1"][0] + el[0], e["el1"][1] + el[1])
        eski = e["dirsek2"]
        q = _hk_kol_sec(q, "2", hedef, lambda d, o: _math.dist(d, eski))
        e = tg_eklemler(q)
    if _math.dist(e["ayak1"], e["ayak2"]) < pay:
        alt = max(e["ayak2"][1], e["parmak2"][1])
        en = None
        for du in range(-16, 17):
            for db in range(-16, 17):
                r = dict(q, u2=q.get("u2", 0) + du, b2=q.get("b2", 0) + db)
                f = tg_eklemler(r)
                yuk = alt - max(f["ayak2"][1], f["parmak2"][1])      # uzak ayak biraz yukarıda olabilir (derinlik)
                if _math.dist(f["ayak1"], f["ayak2"]) < pay or not -0.6 <= yuk <= 5.5:
                    continue
                if en is None or abs(du) + abs(db) < en[0]:
                    en = (abs(du) + abs(db), r)
        if en:
            q = en[1]
    return q


def _hk_ayir_hepsi(an, **kw):
    """Anahtarların hepsine _hk_uclari_ayir; aynı poz nesnesi aynı kalır (tekrarlı hareketlerde 'is' karşılaştırması)."""
    hazir = {}
    return [(t, hazir.setdefault(id(p), _hk_uclari_ayir(p, **kw))) for t, p in an]


def hk_uzun_atlama(x_cizgi, mesafe, s=1.0):
    """
    Durarak uzun atlama: ayak uçları çizginin gerisinde çöker (kollar geride), kol salınımıyla sıçrar, havada
    dizler öne, iki ayak birlikte iner. Son anahtar = iniş (ölçüm anı). olay: "cizgi", "topuk_x" (en geri ayak).
    """
    ayak = ("ayak1", "ayak2", "parmak1", "parmak2")
    hazir = tg_yerlestir(tg_poz(x_cizgi - 10 * s, s=s, g=40, u1=72, b1=-30, u2=66, b2=-26,
                                k1=-62, o1=-52, k2=-52, o2=-42))
    on = max(tg_eklemler(hazir)[k][0] for k in ayak)
    hazir = dict(hazir, hx=hazir["hx"] - (on - x_cizgi) - 1)               # ayak uçları çizginin hemen gerisinde
    dur = tg_poz(hazir["hx"], s=s, k1=40, o1=50, k2=34, o2=44)
    dur = dict(dur, hx=dur["hx"] - max(tg_eklemler(dur)[k][0] for k in ayak) + x_cizgi - 1)
    kalk = tg_yerlestir(tg_poz(x_cizgi + 6 * s, s=s, g=42, u1=-24, b1=-30, u2=-30, b2=-36, a1=20, a2=16,
                               k1=152, o1=156, k2=144, o2=150), ayak_x=x_cizgi, bacak="2")
    ucus = dict(tg_poz(x_cizgi + mesafe * 0.55, s=s, g=24, u1=96, b1=22, u2=88, b2=16, k1=112, o1=100, k2=104, o2=94),
                hy=TG_ZEMIN - 52 * s)
    inis = tg_yerlestir(tg_poz(0, s=s, g=38, u1=78, b1=-8, u2=70, b2=-14, k1=96, o1=84, k2=88, o2=78))
    geri = min(tg_eklemler(inis)[k][0] for k in ("ayak1", "ayak2"))
    inis = dict(inis, hx=inis["hx"] + (x_cizgi + mesafe - geri))           # en geri ayak (topuk) mesafede
    an = [(0, dur), (0.12, dur), (0.35, hazir), (0.5, kalk), (0.72, ucus), (1.0, inis)]
    return TgHareket(an, {"cizgi": x_cizgi, "topuk_x": x_cizgi + mesafe})


def hk_mekik(x_kalca, tur="situp", tekrar=2, s=1.0):
    """
    Sırtüstü gövde fleksiyonu. tur="situp": dizler 90°, eller ense arkasında, gövde dizlere kadar kalkar;
    tur="curlup": dizler ≈ 140°, eller uyluklarda, yalnız baş ve omuzlar kalkar, parmaklar ileri kayar.
    Son anahtar = üst nokta (sayılan an). olay: "el_yolu" (curl-up'ta parmak ucunun ileri kayışı).
    """
    hy = TG_ZEMIN - 3 * s
    if tur == "situp":
        bacak = dict(u1=135, b1=47, u2=128, b2=40, a1=90, a2=96)
        yat = tg_poz(x_kalca, s=s, hy=hy, g=-88, **bacak)
        kalk = tg_poz(x_kalca, s=s, hy=hy, g=28, **bacak)
    else:
        bacak = dict(u1=112, b1=68, u2=106, b2=62, a1=90, a2=96)
        yat = tg_poz(x_kalca, s=s, hy=hy, g=-88, **bacak)
        kalk = tg_poz(x_kalca, s=s, hy=hy, g=-62, **bacak)
    if tur == "situp":                                   # eller ense arkasında: başın gerisine uzanır, dirsekler önde
        def kollar(p):
            e = tg_eklemler(p)
            gx, gy = e["bas"][0] - e["boyun"][0], e["bas"][1] - e["boyun"][1]
            hed = (e["bas"][0] - 0.2 * gx, e["bas"][1] - 0.2 * gy)
            q = _hk_kol_sec(p, "1", hed, lambda d, o: -(d[0] - o[0]) * p.get("yon", 1))
            return _hk_kol_sec(q, "2", (hed[0] - 1.5 * s, hed[1] + 1.5 * s), lambda d, o: -(d[0] - o[0]) * p.get("yon", 1))
        yat, kalk = kollar(yat), kollar(kalk)
        el_yolu = []
    else:                                                # eller uyluk üstünde, kalkınca öne kayar
        def kollar(p, ileri):
            e = tg_eklemler(p)
            kx, ky = e["kalca"]
            dx, dy = e["diz1"][0] - kx, e["diz1"][1] - ky
            hed = (kx + dx * ileri, ky + dy * ileri - 1)
            return _hk_kollar_hedefe(p, hed, (hed[0] - 2 * s, hed[1] + 1.2 * s), 1, 1)
        yat, kalk = kollar(yat, 0.12), kollar(kalk, 0.9)
        el_yolu = [tg_eklemler(yat)["el1"], tg_eklemler(kalk)["el1"]]
    an, pay = [(0.0, yat)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, kalk)] + ([(i * pay + pay, yat)] if i < tekrar - 1 else [])
    an.append((1.0, kalk))
    return TgHareket(_hk_ayir_hepsi(an, el=(-4.2, 0)), {"el_yolu": el_yolu})


def _hk_sinav_pozu(x, s, diz, kol):
    """Şınav pozu: gövde (diz üstüde gövde + uyluk) düz çizgi; eller omuz altında yerde, destek ayak ucu ya da diz."""
    en_iyi = None
    for g10 in range(400, 900, 5):
        g = g10 / 10
        p = tg_poz(x, s=s, g=g, u1=-g, b1=(-90 if diz else -g), u2=-g + 2, b2=(-96 if diz else -g + 2),
                   a1=0 if not diz else -90, a2=4 if not diz else -94, **kol)
        destek = ("diz1", "diz2") if diz else ("parmak1", "parmak2")
        p = _hk_yere_koy(p, destek)
        e = tg_eklemler(p)
        hata = abs(e["el1"][1] - TG_ZEMIN)
        if en_iyi is None or hata < en_iyi[0]:
            en_iyi = (hata, p)
    return en_iyi[1]


def hk_sinav(x, s=1.0, diz=False, tekrar=2):
    """
    Şınav (FitnessGram/PYFP; diz üstü: BOT-2): üstte kollar düz, altta dirsek 90°; gövde düz çizgi.
    Son anahtar = alt nokta (dirsek 90°). olay: "dirsek_acisi" (son karede).
    """
    ust = _hk_sinav_pozu(x, s, diz, dict(k1=0, o1=0, k2=4, o2=4))
    alt = _hk_sinav_pozu(x, s, diz, dict(k1=-58, o1=32, k2=-52, o2=38))
    an, pay = [(0.0, ust)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, alt)] + ([(i * pay + pay, ust)] if i < tekrar - 1 else [])
    an.append((1.0, alt))
    return TgHareket(_hk_ayir_hepsi(an, el=(-4.2, 0)), {"dirsek_acisi": 180 - abs(-58 - 32)})


def hk_modifiye_barfiks(x_topuk, s=1.0, tekrar=2, asili=False, bar_y=None):
    """
    Modified pull-up: sırtüstü, topuklar yerde, vücut düz; avuçlar öne bakarak bara tutunur. Altta kollar düz,
    üstte göğüs/çene bara çekilir. Bar yeri alttaki ellerden. Son anahtar = üst nokta. olay: "bar".
    asili=True (Paket 35, genel barfiks): aynı hareketin bantsız, yüksek bardaki varyantı — x_topuk gövdenin x'i,
    bar_y barın yüksekliği; altta kollar tam açık asılı (ayaklar yerden kesik), üstte çene barın üstünde.
    olay: "bar", "cene_y" (üst noktada çenenin y'si).
    """
    if asili:
        return _hk_asili_barfiks(x_topuk, bar_y, s, tekrar)

    def govde(g):
        p = tg_poz(0, s=s, g=-g, u1=g, b1=g, u2=g - 2, b2=g - 2, a1=150, a2=146, k1=180, o1=180, k2=176, o2=176)
        p = tg_yerlestir(p, ayak_x=x_topuk)
        return p
    alt = govde(80)
    bar = tg_eklemler(alt)["el1"]
    ust = govde(62)                                  # çene bardan 7-8 inç aşağıdaki elastik bandın üstüne çıkar
    ust = _hk_kollar_hedefe(ust, bar, (bar[0] - 2 * s, bar[1]), -1, -1)
    an, pay = [(0.0, alt)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, ust)] + ([(i * pay + pay, alt)] if i < tekrar - 1 else [])
    an.append((1.0, ust))
    return TgHareket(_hk_ayir_hepsi(an, el=(-2.6, 2.6)), {"bar": bar})


# Paket 35b: bench press kol açıları (aşağıdan ölçülür, + = kalçaya doğru). Üstte kollar omuz üstünde dik;
# altta üst kol gövde boyunca (dirsek gövde çizgisinin hemen üstünde), ön kol yaklaşık dikey → bar alt göğüste.
BENCH_KOL_UST = (170, 172)


BENCH_KOL_ALT = (94, 178)


BENCH_KAVRAMA = (-4.2, 0.5)          # uzak el, yakın ele göre (yandan kavrama genişliğinin izdüşümü)


BENCH_ARA_ADIM = 8                   # iniş ve çıkışta ara anahtar sayısı (eller her karede barda)


BARFIKS_ARA_ADIM = 6


def _hk_asili_barfiks(x, bar_y, s, tekrar):
    """Genel barfiks (hk_modifiye_barfiks(asili=True)): pronasyon, tam açık asılı → çene bar üstünde."""
    L = {k: v * s for k, v in _TG_BOY.items()}
    bacak = dict(u1=14, b1=-28, u2=8, b2=-34, a1=150, a2=146)          # dizler hafif bükük: ayaklar yerden kesik
    alt = tg_poz(x, s=s, g=0, k1=178, o1=178, k2=182, o2=182, **bacak)
    alt = dict(alt, hy=alt["hy"] + (bar_y - tg_eklemler(alt)["el1"][1]))
    bar = tg_eklemler(alt)["el1"]
    ust = tg_poz(x - 3.5 * s, s=s, g=-6, **bacak)                       # baş barın gerisinden geçer, çene üstte
    ust = dict(ust, hy=ust["hy"] + (bar_y - 1.6 * s - tg_eklemler(ust)["cene"][1]))
    ust = _hk_kol_sec(ust, "1", bar, lambda d, o: -d[1])                # dirsek aşağıda
    ust = _hk_kol_sec(ust, "2", (bar[0] - 4.0, bar[1] + 0.5), lambda d, o: -d[1])
    alt = _hk_uclari_ayir(alt, el=(-4.0, 0.5))
    ust = _hk_aci_yakin(alt, ust)
    # Paket 35b: yalnız alt ve üst anahtar bara kilitliyse ara karede eller bardan kopuyordu (açı ara değeri).
    # Gövde ve bacaklar ara değerle yükselir; her ara anahtarda iki el IK ile barda (uzak el kavrama ofsetinde),
    # dirsek alt ve üst anahtarın dirsekleri arasındaki noktaya en yakın çözüm; açılar bir öncekine yakın (±360° yok).
    ea, eu = tg_eklemler(alt), tg_eklemler(ust)
    yol, onceki = [alt], alt
    for j in range(1, BARFIKS_ARA_ADIM):
        f = j / BARFIKS_ARA_ADIM
        p = _tg_ara(alt, ust, f)
        for kol, hedef in (("1", bar), ("2", (bar[0] - 4.0, bar[1] + 0.5))):
            ref = tuple(ea["dirsek" + kol][i] + (eu["dirsek" + kol][i] - ea["dirsek" + kol][i]) * f for i in (0, 1))
            p = _hk_kol_sec(p, kol, hedef, lambda d, o, r=ref: _math.dist(d, r))
        onceki = _hk_aci_yakin(onceki, p)
        yol.append(onceki)
    yol.append(ust)
    an, pay = [], 1.0 / tekrar
    for i in range(tekrar):
        cik = [(i * pay + 0.5 * pay * j / BARFIKS_ARA_ADIM, p) for j, p in enumerate(yol)]
        in_ = [(i * pay + 0.5 * pay + 0.5 * pay * j / BARFIKS_ARA_ADIM, p) for j, p in enumerate(yol[::-1])][1:]
        an += (cik if i == 0 else cik[1:]) + (in_ if i < tekrar - 1 else [])
    an.append((1.0, ust))
    return TgHareket(an, {"bar": bar, "cene_y": tg_eklemler(ust)["cene"][1]})


def hk_bench_press(x_kalca, sehpa_y, s=1.0):
    """
    Bench press (1RM, yandan): sehpada sırtüstü (baş, üst sırt, kalça sehpada; iki ayak yerde), kapalı kavrayış.
    Kollar tam açık → bar alt göğse iner → kollar tam açılır. Son anahtar = kollar tam açık (geçerli kaldırış).
    Paket 35b: altta üst kol gövde boyunca (dirsek gövde çizgisinin üstünde), ön kol yaklaşık dikey; bar boyundan
    kalçaya doğru alt göğüs hizasında. Kol açıları üst ↔ alt arasında BENCH_ARA_ADIM ara anahtarla değişir; her
    anahtarda uzak el yakın elin kavrama ofsetinde (BENCH_KAVRAMA) IK ile. Uzak ayak da zemine IK ile basar.
    olay: "bar" [(t, x, y)] bar ekseni (el), "gogus_y" (alt noktada barın y'si), "ayak" (ayak bileği).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    hy = sehpa_y - 2.0 * s
    ayak = (x_kalca + 27 * s, TG_ZEMIN - 1.0)
    ayak2 = (ayak[0] - 4.0, TG_ZEMIN - 1.0)                             # uzak ayak: ayrık ve zeminde
    u, b = _hk_iki_bag((x_kalca, hy), ayak, L["uyluk"], L["baldir"], 1)
    u2, b2 = _hk_iki_bag((x_kalca, hy), ayak2, L["uyluk"], L["baldir"], 1)
    yat = dict(tg_poz(x_kalca, s=s, g=-90, u1=u, b1=b, u2=u2, b2=b2, a1=100, a2=96), hy=hy)

    def kollar(k, o, onceki):
        p = dict(yat, k1=k, o1=o)
        e = tg_eklemler(p)
        hedef = (e["el1"][0] + BENCH_KAVRAMA[0], e["el1"][1] + BENCH_KAVRAMA[1])
        ref = (tg_eklemler(onceki)["dirsek2"] if onceki                 # dirsek dalı bir öncekinden sürer
               else (e["dirsek1"][0] + BENCH_KAVRAMA[0], e["dirsek1"][1] + BENCH_KAVRAMA[1]))
        p = _hk_kol_sec(p, "2", hedef, lambda d, o_: _math.dist(d, ref))
        return _hk_aci_yakin(onceki, p) if onceki else p
    (k0, o0), (k1, o1) = BENCH_KOL_UST, BENCH_KOL_ALT
    inis, onceki = [], None
    for j in range(BENCH_ARA_ADIM, -1, -1):                              # alttan üste: dal altta belirgin
        f = j / BENCH_ARA_ADIM
        onceki = kollar(k0 + (k1 - k0) * f, o0 + (o1 - o0) * f, onceki)
        inis.insert(0, onceki)
    acik, gogus = inis[0], inis[-1]
    alt_el = tg_eklemler(gogus)["el1"]
    n = BENCH_ARA_ADIM
    an = ([(0.0, acik)] + [(0.15 + 0.35 * j / n, p) for j, p in enumerate(inis)]
          + [(0.5 + 0.35 * j / n, p) for j, p in enumerate(inis[::-1])][1:] + [(1.0, acik)])
    bar = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an)]
    bas = tg_eklemler(acik)["bas"]
    # spotçu (ikinci figür): barın başında, hafif öne eğik, eller barın hemen üstünde hazır
    bx_, by_ = bar[-1][1], bar[-1][2]
    sp = tg_yerlestir(tg_poz(bas[0] - 26, s=s, g=18, u1=14, b1=-4, u2=4, b2=-10))
    sp = _hk_kollar_hedefe(sp, (bx_ - 3, by_ - 3), (bx_ - 7, by_ - 2), -1, -1)
    return TgHareket(an, {"bar": bar, "gogus_y": alt_el[1], "ayak": ayak, "bas": bas,
                          "spotcu": hk_ikinci_figur([(0.0, sp), (1.0, sp)]), "spotcu_bas": tg_eklemler(sp)["bas"]})


def _hk_comelme_pozu(x_ayak, s, g, u, b):
    """Arka çömelme pozu: ayak bileği x_ayak'ta sabit, bar üst sırtta, eller barda (dirsekler aşağıda)."""
    p = tg_yerlestir(tg_poz(x_ayak, s=s, g=g, u1=u, b1=b, u2=u - 5, b2=b - 5, a1=90, a2=88), ayak_x=x_ayak)
    e = tg_eklemler(p)
    r = _math.radians(g)
    bar = (e["boyun"][0] - 2.8 * s * _math.cos(r) - 1.5 * s * _math.sin(r),     # boynun gerisinde, omuzların üstünde
           e["boyun"][1] - 2.8 * s * _math.sin(r) + 1.5 * s * _math.cos(r))
    ref = (e["boyun"][0] - 5 * s * _math.cos(r) - 10 * s * _math.sin(r),            # dirsek: gövdenin gerisinde, aşağıda
           e["boyun"][1] - 5 * s * _math.sin(r) + 10 * s * _math.cos(r))
    p = _hk_kol_sec(p, "1", (bar[0] + 1.2 * s, bar[1]), lambda d, o: _math.dist(d, ref))
    p = _hk_kol_sec(p, "2", (bar[0] - 3.4, bar[1] + 0.6), lambda d, o: _math.dist(d, ref))
    return _hk_uclari_ayir(p, el=(-3.6, 0.6)), bar


def _hk_aci_yakin(onceki, p, adlar=("k1", "o1", "k2", "o2")):
    """Uzuv açılarını önceki poza en yakın eşdeğerine (±360°) çeker: ara karede kol tersine dönmesin."""
    q = dict(p)
    for k in adlar:
        if k in q and k in onceki:
            q[k] = q[k] + 360 * round((onceki[k] - q[k]) / 360)
    return q


def hk_arka_comelme(x_ayak, s=1.0, g=40, u=80, b=-24):
    """
    Arka çömelme (back squat 1RM, yandan): bar üst sırtta; dik duruş → diz açısı 90°'yi geçene kadar çömelme.
    Son anahtar = en alt nokta (ayırt edici an: derinlik). olay: "bar" [(t, x, y)], "diz_acisi" (altta, iç açı),
    "diz" (altta diz noktası).
    """
    dik, _ = _hk_comelme_pozu(x_ayak, s, 0, 7, -1)
    ara, _ = _hk_comelme_pozu(x_ayak, s, g * 0.55, u * 0.5, b * 0.5)          # ara poz: eller inişte barda kalsın
    cok, _ = _hk_comelme_pozu(x_ayak, s, g, u, b)
    ara = _hk_aci_yakin(dik, ara)
    cok = _hk_aci_yakin(ara, cok)
    an = [(0.0, dik), (0.25, dik), (0.62, ara), (1.0, cok)]
    bar = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        r = _math.radians(p.get("g", 0))
        bar.append((t, e["boyun"][0] - 2.8 * s * _math.cos(r) - 1.5 * s * _math.sin(r),
                    e["boyun"][1] - 2.8 * s * _math.sin(r) + 1.5 * s * _math.cos(r)))
    return TgHareket(an, {"bar": bar, "diz_acisi": 180 - (u - b), "diz": tg_eklemler(cok)["diz1"]})


def hk_leg_press(kalca, s=1.0, egim=45, uzak=0.94, yakin=0.5, g=-58):
    """
    Leg press (1RM, yandan, kızak egim° açılı): kalça ve sırt minderde, ayaklar platformda; bacaklar açık → platform
    belirlenen derinliğe iner (dizler göğse yaklaşır) → bacaklar açılır (diz kilitlenmez). Son anahtar = itiş sonu.
    olay: "platform" [(t, x1, y1, x2, y2)], "ray" (yön birim vektörü), "alt" (en alt anahtarın sırası).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    hx, hy = kalca
    r = _math.radians(egim)
    ray = (_math.cos(r), -_math.sin(r))
    bacak = L["uyluk"] + L["baldir"]

    def poz(oran):
        ayak = (hx + ray[0] * bacak * oran, hy + ray[1] * bacak * oran)
        el = (hx - 2 * s, hy - 1 * s)                                         # tutamaklar kalçanın yanında
        return _hk_uclari_ayir(_hk_oturus(hx, hy, ayak, s, g, el, (el[0] - 4.2, el[1] + 0.5), a=-90 - egim))
    acik, alt = poz(uzak), poz(yakin)
    an = [(0.0, acik), (0.15, acik), (0.55, alt), (1.0, acik)]
    platform = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        cx, cy = e["ayak1"][0] + ray[0] * 1.6 * s, e["ayak1"][1] + ray[1] * 1.6 * s    # tabanın hemen önünde
        dx, dy = -ray[1], ray[0]                                               # rayya dik
        platform.append((t, cx - dx * 10 * s, cy - dy * 10 * s, cx + dx * 6 * s, cy + dy * 6 * s))
    return TgHareket(an, {"platform": platform, "ray": ray, "alt": 2, "boyun": tg_eklemler(acik)["boyun"]})


def _hk_ara_ekle(an, en_cok=60.0):
    """
    Ardışık anahtarlar arasında uzuv açısı en_cok dereceden fazla değişiyorsa araya _tg_ara ile anahtar ekler:
    _tg_kareler'in kare başına açı adımı ≈ 0,25 × anahtar farkı → ≤ 15°. Açılar önce bir öncekine yakınlaştırılır
    (±360° ters dönme yok).
    """
    adlar = ("u1", "b1", "u2", "b2", "k1", "o1", "k2", "o2", "a1", "a2", "g")

    def taban(p):
        e = tg_eklemler(p)
        return max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))
    sonuc = [an[0]]
    for (t1, p1) in an[1:]:
        t0, p0 = sonuc[-1]
        p1 = _hk_aci_yakin(p0, p1, adlar)
        fark = max([abs(p1.get(k, 0) - p0.get(k, 0)) for k in adlar])
        n = max(1, _math.ceil(fark / en_cok))
        ayni_zemin = abs(taban(p0) - taban(p1)) < 0.5             # iki uç yerdeyse ara anahtar da yerde
        for j in range(1, n):
            q = _tg_ara(p0, p1, j / n)
            if ayni_zemin:
                q = dict(q, hy=q["hy"] + (taban(p0) - taban(q)))
            sonuc.append((t0 + (t1 - t0) * j / n, q))
        sonuc.append((t1, p1))
    return sonuc


def hk_sargent(duvar_x, s=1.0, yukselme=6.0):
    """
    Sargent dikey sıçrama (duvar + tebeşir, önden: sporcu duvara yan, duvar figürün yanında dikey çizgi). Duvara
    yaklaşır → duvara yakın kol yukarı, parmak ucu duvarda (ayakta erişim, alt iz) → hafif uzaklaşır → çömelir
    (hazırlık çömelmesi) → sıçrar → ZİRVEDE duvara dokunur (üst iz). Son anahtar = zirve (ölçüm anı).
    olay: "alt_iz", "ust_iz" (duvardaki tebeşir izleri = el noktası), "alt_t" (ayakta erişim anı), "duvar_x".
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    kol = (L["ust"] + L["on"]) * 0.99
    on = dict(cephe=True, s=s, a1=90, a2=-90)

    def duz(hx, **k):
        return tg_yerlestir(tg_poz(hx, **{**on, "u1": 5, "b1": 5, "u2": -5, "b2": -5,
                                          "k1": 10, "o1": 6, "k2": -10, "o2": -6, **k}))

    def duvara(p):                                    # yakın kol duvara, en yükseğe (parmak ucu duvarda)
        kok = tg_eklemler(p)["kok_k1"]
        hx_ = duvar_x - 1.0
        hedef = (hx_, kok[1] - _math.sqrt(max(0.0, kol * kol - (hx_ - kok[0]) ** 2)))
        return _hk_kol_sec(p, "1", hedef, lambda d, o: -d[0]), hedef
    # Paket 36: önden çizimde kolu yandan (abdüksiyonla) kaldırmak eli duvarın içinden geçiriyordu. Yakın kol
    # gövdeye yakın bükülerek yükselir; her ara anahtarda el IK ile duvarın solundaki bir hedefte (dirsek gövdeye
    # doğru). Sıçrama için duvardan bir adım uzaklaşılır.
    def el1(p, hedef):
        return _hk_kol_sec(p, "1", hedef, lambda d, o: d[0])

    def omuz(p):
        return tg_eklemler(p)["kok_k1"]
    yakin = duvar_x - 1.0 - L["bas"] - 2.5            # baş duvara değmez
    uzak = yakin - 8.0 * s                             # duvardan bir adım uzaklaşır
    gel = duz(yakin - 34 * s)
    dur = duz(yakin)
    ko = omuz(dur)
    kaldir = el1(duz(yakin, k2=-14, o2=-10), (ko[0] + 4 * s, ko[1] - 2 * s))            # el omuz hizasında, önde
    eris, alt_iz = duvara(duz(yakin, k2=-14, o2=-10))
    ara_x = (yakin + uzak) / 2
    indir = el1(duz(ara_x), (omuz(duz(ara_x))[0] + 4 * s, omuz(duz(ara_x))[1] - 2 * s))
    geri = duz(uzak)
    cok = tg_yerlestir(tg_poz(uzak, **{**on, "u1": 34, "b1": -26, "u2": -34, "b2": 26,
                                       "k1": 20, "o1": 12, "k2": -28, "o2": -20}))
    kc = omuz(cok)
    cok = el1(cok, (kc[0] + 3 * s, kc[1] + kol * 0.85))                                  # kol aşağıda, gövdeye yakın
    kalk = tg_yerlestir(tg_poz(uzak, **{**on, "u1": 4, "b1": 4, "u2": -4, "b2": -4, "a1": 150, "a2": -150,
                                        "k2": -150, "o2": -160}))
    kk = omuz(kalk)
    savur = el1(dict(kalk, k2=-90, o2=-110), (kk[0] + 4 * s, kk[1] - 2 * s))             # kol önden yukarı
    savur = tg_yerlestir(dict(cok, k1=savur["k1"], o1=savur["o1"], k2=-80, o2=-100))
    kalk = el1(kalk, (duvar_x - 3.0, kk[1] - kol * 0.9))
    hy0 = kalk["hy"]
    kh = omuz(kalk)                                                    # zirve: üst iz tuvalin üst payında
    dx = duvar_x - 1.0 - kh[0]
    yukselme = max(yukselme, kh[1] - _math.sqrt(max(0.0, kol * kol - dx * dx)) - 21.5)
    tepe = dict(kalk, hy=hy0 - yukselme, k2=-148, o2=-156)            # uzak kol yukarı-yana (başlık payı)
    tepe, ust_iz = duvara(tepe)
    def yol(p0, p1, adim=4):
        """p0 → p1 arası: gövde ara değer, yakın el iki ucun elleri arasındaki doğru üzerinde (IK, dirsek sürekli)."""
        e0, e1 = tg_eklemler(p0), tg_eklemler(p1)
        sonuc, dirsek = [], e0["dirsek1"]
        tab = [max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2")) for e in (e0, e1)]
        zemin0 = tab[0] if abs(tab[0] - TG_ZEMIN) < 0.5 and abs(tab[1] - TG_ZEMIN) < 0.5 else None
        for j in range(1, adim):
            f = j / adim
            q = _tg_ara(p0, p1, f)
            hedef = (e0["el1"][0] + (e1["el1"][0] - e0["el1"][0]) * f, e0["el1"][1] + (e1["el1"][1] - e0["el1"][1]) * f)
            q = _hk_kol_sec(q, "1", hedef, lambda d, o, r=dirsek: _math.dist(d, r) + 100 * max(0.0, d[0] - (duvar_x - 1.5)))
            if zemin0 is not None:                                     # iki uç yerdeyse ara poz da yerde
                q = tg_yerlestir(q)
            dirsek = tg_eklemler(q)["dirsek1"]
            sonuc.append(q)
        return sonuc
    duraklar = [(0.0, gel), (0.06, gel), (0.2, dur), (0.27, kaldir), (0.34, eris), (0.44, eris), (0.5, indir),
                (0.56, geri), (0.68, cok), (0.77, savur), (0.86, kalk), (1.0, tepe)]
    an = [duraklar[0]]
    for (t0, p0), (t1, p1) in zip(duraklar, duraklar[1:]):
        if p0 is not p1:
            ara = yol(p0, p1)
            an += [(t0 + (t1 - t0) * (j + 1) / (len(ara) + 1), q) for j, q in enumerate(ara)]
        an.append((t1, p1))
    return TgHareket(_hk_ara_ekle(an), {"alt_iz": alt_iz, "ust_iz": ust_iz, "alt_t": 0.34, "duvar_x": duvar_x})


def hk_govde_kaldirma(x_kalca, s=1.0):
    """Trunk lift: yüzüstü, eller kalça yanında; baş ve üst gövde yavaşça kalkar. Son anahtar = en yüksek nokta."""
    hy = TG_ZEMIN - 3 * s
    ortak = dict(u1=-90, b1=-90, u2=-88, b2=-88, a1=-90, a2=-88, k1=-86, o1=-90, k2=-80, o2=-86)
    yat = tg_poz(x_kalca, s=s, hy=hy, g=90, **ortak)
    kalk = tg_poz(x_kalca, s=s, hy=hy, g=58, **ortak)
    return TgHareket(_hk_ayir_hepsi([(0, yat), (0.2, yat), (0.8, kalk), (1.0, kalk)], el=(4.2, 0)), {})


def hk_flamingo(x, s=1.0, tutar=True, zemin=None, kayip=0.45):
    """
    Tek ayak denge: destek ayağı düz, öbür bacak dizden bükülü geride (tutar=True: eliyle bileğinden tutar).
    kayip anında denge kaybı: serbest ayak yere değer, sonra pozisyon yeniden alınır. Son anahtar = dengede.
    olay: "kayip_t".
    """
    zemin = TG_ZEMIN if zemin is None else zemin
    serbest = dict(u2=-14, b2=-150, a2=-170)
    kol1 = dict(k1=70, o1=86)
    p = tg_yerlestir(tg_poz(x, s=s, u1=2, b1=0, **serbest, **kol1, k2=-30, o2=-40), zemin=zemin)
    if tutar:
        e = tg_eklemler(p)
        p = _hk_kollar_hedefe(p, e["el1"], e["ayak2"], 1, -1)          # öbür el serbest ayağın bileğinde
    sallan = dict(p, g=-8, k1=110, o1=120)
    yere = tg_yerlestir(tg_poz(x + 4 * s, s=s, u1=6, b1=2, u2=-12, b2=-8, k1=40, o1=60, k2=-36, o2=-50), zemin=zemin)
    an = [(0, p), (kayip - 0.15, p), (kayip - 0.05, sallan), (kayip, yere), (kayip + 0.2, p), (1.0, p)]
    return TgHareket(an, {"kayip_t": kayip})


def hk_masa_dokunma(x, masa_y, disk_dx, s=1.0, tur=4):
    """
    Plate tapping (önden): baskın olmayan el ortadaki plakada; baskın el iki disk arasında sırayla dokunur.
    Son anahtar = bir diske dokunuş. olay: "diskler" [(x, y), (x, y)], "plaka".
    """
    p = tg_poz(x, s=s, cephe=True, u1=5, b1=5, u2=-5, b2=-5, a1=90, a2=-90, g=10)
    plaka = (x - 3 * s, masa_y - 1)
    sol, sag = (x - disk_dx, masa_y - 1), (x + disk_dx, masa_y - 1)
    disari = lambda d, o: -abs(d[0] - x)                  # dirsekler gövdenin dışında
    def el(h):
        q = _hk_kol_sec(p, "1", h, disari)
        return _hk_kol_sec(q, "2", plaka, disari)
    an = [(i / tur, el(sag if i % 2 == 0 else sol)) for i in range(tur + 1)]
    return TgHareket(an, {"diskler": [sol, sag], "plaka": plaka})


def hk_omuz_esneme(x, s=1.0):
    """
    Shoulder stretch (arkadan): bir el omuz üstünden sırta, öbürü bel altından yukarı; parmak uçları sırtta
    buluşur. Son anahtar = buluşma. olay: "bulusma".
    """
    p = tg_poz(x, s=s, cephe=True, u1=4, b1=4, u2=-4, b2=-4, a1=90, a2=-90)
    e = tg_eklemler(p)
    # üstteki kol: dirsek yukarıda ve dışta (başın arkasında kalmasın); alttaki: dirsek belde, dışta
    ust = dict(p, k1=145, o1=-34, k2=-40, o2=128)
    acik = dict(p, k1=145, o1=-62, k2=-40, o2=152)       # eller henüz buluşmamış
    q = tg_eklemler(ust)
    bx, by = (q["el1"][0] + q["el2"][0]) / 2, (q["el1"][1] + q["el2"][1]) / 2
    bas = dict(p, k1=8, o1=6, k2=-8, o2=-6)
    return TgHareket([(0, bas), (0.2, bas), (0.6, acik), (1.0, ust)], {"bulusma": (bx, by)})


def hk_omuz_rotasyon(x, s=1.0):
    """
    Omuz rotasyonu (sopa/ip): kollar dirsekten bükülmeden önden-aşağıdan baş üstünden sırta geçer ve döner.
    Yandan; olay["el_yolu"] sopanın izlediği yay. Son anahtar = sırtta.
    """
    an, yol = [], []
    for i, a in enumerate([10, 10, 60, 120, 180, 240, 300, 330]):
        t = [0, 0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0][i]
        q = tg_poz(x, s=s, k1=a, o1=a, k2=a + 9, o2=a + 9)
        an.append((t, q))
    for t, q in _tg_kareler(an):
        yol.append(tg_eklemler(q)["el1"])
    return TgHareket(an, {"el_yolu": yol})


def hk_top_sektirme(x, s=1.0, tekrar=4):
    """Tek elle aşağı sektirme, top yerden sekip öbür ele; eller sırayla. olay: "top_yolu" [(t, x, y)]."""
    ust = lambda k: dict(k1=30 if k == 1 else 24, o1=70 if k == 1 else 64, k2=24 if k == 2 else 18,
                         o2=64 if k == 2 else 40)
    an, yol = [], []
    for i in range(tekrar + 1):
        k = 1 + i % 2
        p = tg_poz(x, s=s, g=10, u1=8, b1=-2, u2=-8, b2=-4, **ust(k))
        an.append((i / tekrar, p))
        e = tg_eklemler(p)
        el = e["el1"] if k == 1 else e["el2"]
        yol.append((i / tekrar, el[0] + 2, el[1] + 3))
        if i < tekrar:
            yol.append(((i + 0.5) / tekrar, el[0] + 3, TG_ZEMIN - 2.5))
    return TgHareket(an, {"top_yolu": yol})


def hk_top_yakala(x_cocuk, x_atan, s_cocuk=0.7, s_atan=0.95):
    """
    Uygulayıcı (ikinci kişi) alttan atar, çocuk iki eliyle yakalar. olay: "atan" (hk_ikinci_figur),
    "top_yolu" [(t, x, y)]. Son anahtar = yakalama.
    """
    c0 = tg_poz(x_cocuk, s=s_cocuk, k1=30, o1=60, k2=24, o2=54)
    c1 = tg_poz(x_cocuk, s=s_cocuk, g=6, k1=74, o1=96, k2=60, o2=84)
    a0 = tg_poz(x_atan, s=s_atan, yon=-1, k1=-30, o1=-10, k2=10, o2=20)
    a1 = tg_poz(x_atan, s=s_atan, yon=-1, g=10, k1=70, o1=80, k2=12, o2=22)
    e0, e1 = tg_eklemler(a1), tg_eklemler(c1)
    bas_t, bit_t = 0.35, 0.8
    yol = [(0.0, *tg_eklemler(a0)["el1"]), (bas_t, *e0["el1"])]
    for i in range(1, 9):
        f = i / 8
        yol.append((bas_t + (bit_t - bas_t) * f, e0["el1"][0] + (e1["el1"][0] - e0["el1"][0]) * f,
                    e0["el1"][1] + (e1["el1"][1] - e0["el1"][1]) * f - 34 * f * (1 - f)))
    yol.append((1.0, *e1["el1"]))
    atan = hk_ikinci_figur([(0, a0), (0.2, a0), (bas_t, a1), (1.0, a1)])
    return TgHareket([(0, c0), (0.3, c0), (0.6, c0), (bit_t, c1), (1.0, c1)], {"atan": atan, "top_yolu": yol})


def hk_takla(x, s=1.0, mesafe=None):
    """
    Öne takla (TSYT koordinasyon 1. istasyon): dur → çömel, eller minderde → BÜZÜL (dizler göğüste, baş içeri) →
    büzük gövde döner (olay["donus"]: (t0, t1, merkez_x, merkez_y) — sahne figür grubunu bu aralıkta 360° çevirir)
    → çömel, kollar önde → kalk. mesafe: dönüş boyunca ileri yuvarlanma (kayan sahnede parkur bu kadar kayar).
    """
    mesafe = 30 * s if mesafe is None else mesafe
    dur = tg_poz(x, s=s)
    comel = tg_yerlestir(tg_poz(x, s=s, g=62, u1=118, b1=-28, u2=112, b2=-34, a1=150, a2=146))
    comel = _hk_kollar_hedefe(comel, (x + 13 * s, TG_ZEMIN), (x + 11 * s, TG_ZEMIN), 1, 1)
    # büzük: gövde dik-öne yuvarlak (20°), uyluklar gövdenin önünde göğse (145°), baldırlar geriye-aşağı,
    # eller baldırları kavrar; uzak el/ayak yakınınkinden ayrı (uzuv uçları ≥ 3 birim — düğüm gibi görünmesin)
    buzul = tg_yerlestir(tg_poz(x, s=s, g=20, u1=145, b1=-25, u2=137, b2=-33, a1=120, a2=114))
    e = tg_eklemler(buzul)
    baldir = ((e["diz1"][0] + e["ayak1"][0]) / 2, (e["diz1"][1] + e["ayak1"][1]) / 2)
    buzul = _hk_uclari_ayir(_hk_kollar_hedefe(buzul, baldir, (baldir[0] - 2 * s, baldir[1] + 2 * s), 1, 1), el=(-3.6, 0))
    kalk = tg_yerlestir(tg_poz(x, s=s, g=50, u1=112, b1=-30, u2=106, b2=-36, a1=150, a2=146,
                               k1=96, o1=96, k2=90, o2=90))
    # dönüş merkezi: büzük gövdenin çevreleyen kutusunun ortası; yarıçap R = merkezden en uzak nokta (baş çemberi
    # ve çizgi kalınlığı dahil). Gövde, merkez zeminden R yukarıda olacak biçimde kaldırılır → 360° boyunca en alt
    # nokta hiçbir an zemin çizgisini geçmez (Paket 22: önceki merkez eklem ortalamasıydı, 10,7 birim gömülüyordu).
    e = tg_eklemler(buzul)
    noktalar = list(e.values())
    cx = (min(p[0] for p in noktalar) + max(p[0] for p in noktalar)) / 2
    cy = (min(p[1] for p in noktalar) + max(p[1] for p in noktalar)) / 2
    r_bas = _TG_BOY["bas"] * s
    R = max(max(_math.dist((cx, cy), p) for p in noktalar), _math.dist((cx, cy), e["bas"]) + r_bas)
    R += TG_KALINLIK["govde"] * s / 2
    kalkis = (TG_ZEMIN - R) - cy
    buzul = dict(buzul, hy=buzul["hy"] + kalkis)
    cy += kalkis
    an = [(0.0, dur), (0.16, comel), (0.28, buzul), (0.72, buzul), (0.86, kalk), (1.0, dur)]
    return TgHareket(an, {"donus": (0.28, 0.72, cx, cy), "yuvarlanma": mesafe})


def hk_alttan_gec(x, h, s=1.0, uzunluk=None):
    """
    Engelin altından eğilerek geçme: gövde öne eğik, dizler bükük; başın tepesi engel yüksekliği h'nin
    (zeminden) altında kalır. x → x + uzunluk ilerler. olay["bas_ust_en_yuksek"]: geçişteki en yüksek baş noktası.
    """
    uzunluk = 40 * s if uzunluk is None else uzunluk
    dur = tg_poz(x, s=s)
    egik = []
    for i, f in enumerate((0.0, 0.5, 1.0)):
        a = dict(u1=70, b1=-40, u2=40, b2=-70) if i % 2 == 0 else dict(u1=40, b1=-70, u2=70, b2=-40)
        p = tg_yerlestir(tg_poz(x + 8 * s + uzunluk * f, s=s, g=74, k1=60, o1=40, k2=50, o2=30, **a))
        egik.append(p)
    son = tg_poz(x + uzunluk + 16 * s, s=s)
    an = [(0.0, dur), (0.2, egik[0]), (0.5, egik[1]), (0.8, egik[2]), (1.0, son)]
    ust = min(tg_eklemler(p)["bas_ust"][1] for p in egik)
    return TgHareket(an, {"bas_ust_en_yuksek": ust})


def hk_engel_ustu(x, h, s=1.0, uzunluk=None):
    """
    Alçak engelin üstünden adımlayarak geçme: öndeki bacak dizden kalkar ve engeli aşar, arkadaki çekilir.
    x → x + uzunluk. olay["ayak_en_alt_ustte"]: engelin üstündeyken öndeki ayağın en alt noktası (zeminden yükseklik).
    """
    uzunluk = 36 * s if uzunluk is None else uzunluk
    dur = tg_poz(x, s=s)
    kaldir = tg_yerlestir(tg_poz(x + 6 * s, s=s, g=14, u1=96, b1=10, u2=-14, b2=-24, k1=-30, o1=10, k2=40, o2=70),
                          bacak="2")
    ustte = dict(tg_poz(x + uzunluk * 0.5, s=s, g=16, u1=70, b1=-6, u2=-60, b2=-10, k1=40, o1=70, k2=-30, o2=10))
    e = tg_eklemler(ustte)
    ustte = dict(ustte, hy=ustte["hy"] - (max(e["ayak1"][1], e["parmak1"][1]) - (TG_ZEMIN - h - 3 * s)))
    cek = tg_yerlestir(tg_poz(x + uzunluk * 0.8, s=s, g=10, u1=-10, b1=-20, u2=96, b2=10, k1=40, o1=70, k2=-30, o2=10))
    son = tg_poz(x + uzunluk, s=s)
    an = [(0.0, dur), (0.25, kaldir), (0.5, ustte), (0.75, cek), (1.0, son)]
    e = tg_eklemler(ustte)
    return TgHareket(an, {"ayak_en_alt_ustte": TG_ZEMIN - max(e["ayak1"][1], e["parmak1"][1])})


def hk_egil_al(x, s=1.0, tur="al", hedef_dx=None):
    """
    Eğilip yerden alma/bırakma ve top yönetimi. tur="al": eğil, eller yerde (topun üstünde), kalk, top göğüste;
    tur="birak": aynı hareket ters (göğüsten yere). tur="ayak": tek ayak üstünde, öbür ayakla topu ileri iter.
    tur="tut": ayakta, kollar önde göğüs hizasında (yakalama). olay["el"]: en alt anda el (ayak: ayak ucu).
    """
    hedef_dx = 16 * s if hedef_dx is None else hedef_dx
    dur = tg_poz(x, s=s)
    if tur == "ayak":
        it = tg_yerlestir(tg_poz(x, s=s, g=8, u1=-6, b1=-6, u2=40, b2=24, a2=110, k1=30, o1=50, k2=-30, o2=-10))
        return TgHareket([(0.0, dur), (0.5, it), (1.0, dur)], {"el": tg_eklemler(it)["parmak2"], "an": 0.5})
    if tur == "tut":
        tut = tg_poz(x, s=s, k1=74, o1=92, k2=66, o2=86)
        return TgHareket([(0.0, dur), (0.4, tut), (1.0, tut)], {"el": tg_eklemler(tut)["el1"], "an": 0.4})
    egil = tg_yerlestir(tg_poz(x, s=s, g=72, u1=70, b1=-60, u2=64, b2=-66))     # derin çömelme: el yere değer
    egil = _hk_kollar_hedefe(egil, (x + hedef_dx, TG_ZEMIN - 3 * s), (x + hedef_dx - 2 * s, TG_ZEMIN - 3 * s), 1, 1)
    gogus = tg_poz(x, s=s, k1=40, o1=110, k2=34, o2=104)
    an = [(0.0, gogus if tur == "birak" else dur), (0.5, egil), (1.0, dur if tur == "birak" else gogus)]
    return TgHareket(an, {"el": tg_eklemler(egil)["el1"], "an": 0.5})


def _hk_yerinde(hareket, x_c, t0, t1, w0, ref_x):
    """
    Kayan sahne yardımcısı: bir hareketin anahtarlarını [t0, t1] (saniye) aralığına koyar, figürü tuvalde x_c'de
    tutar; hareketin x'teki yol alışı dünyadaki ilerleme olur (w0 + hx − ref_x). [(T, poz, W)] döndürür.
    """
    out = []
    for t, p in hareket.anahtarlar:
        w = w0 + (p["hx"] - ref_x)
        out.append((t0 + (t1 - t0) * t, dict(p, hx=x_c), w))
    return out


KAYAN_HIZ_ISTASYON = 130.0    # birim/sn (≈ 0,50 tuval/sn): bir beceri yapılırken parkurun kayma hızı sınırı (Paket 23)


KAYAN_HIZ_GECIS = 225.0       # birim/sn (≈ 0,87 tuval/sn): istasyonlar arası geçişte (Paket 23)


def _hk_hiz_siniri(K, araliklar, v_ist=KAYAN_HIZ_ISTASYON, v_gecis=KAYAN_HIZ_GECIS):
    """
    Kayan turda zaman gerdirme (Paket 22). K: [(T sn, poz, W)]; araliklar: istasyon pencereleri [(t0, t1)] (sn).
    Her ardışık anahtar çifti en az |ΔW| / v sürer (istasyon içinde v_ist, geçişte v_gecis); kısa olan uzatılır,
    yerinde yapılan beceriler (ΔW = 0) süresini korur. Döndürür: (yeni K, ger) — ger eski zamanı yeniye çevirir.
    """
    eski = [t for t, _, _ in K]
    yeni = [eski[0]]
    for i in range(1, len(K)):
        dt, dw = eski[i] - eski[i - 1], abs(K[i][2] - K[i - 1][2])
        orta = (eski[i] + eski[i - 1]) / 2
        v = v_ist if any(a <= orta <= b for a, b in araliklar) else v_gecis
        yeni.append(yeni[-1] + max(dt, dw / v * 1.001))

    def ger(t):
        if t <= eski[0]:
            return yeni[0] + (t - eski[0])
        for i in range(1, len(eski)):
            if t <= eski[i]:
                f = (t - eski[i - 1]) / ((eski[i] - eski[i - 1]) or 1)
                return yeni[i - 1] + (yeni[i] - yeni[i - 1]) * f
        return yeni[-1] + (t - eski[-1])
    return [(yeni[i], p, w) for i, (_, p, w) in enumerate(K)], ger


KAYAN_DURAKLAMA = 0.5         # sn: her istasyon penceresinin başında parkur durur, ad belirir (Paket 25)


def _hk_hazir_durus(p, pay=1.5):
    """
    Duraklama pozu (Paket 26): iki ayak zaten zemindeyse (bilekler TG_ZEMIN'den ≤ pay) poz aynen döner. Değilse hx,
    g ve kol açıları korunur; bacaklar (u1, b1, u2, b2, a1, a2) nötr duruşa (TG_TEMEL_POZ) alınır, hy iki ayak
    zemine değecek biçimde düzeltilir — koşu ortasındaki havadaki ayak 0,5 sn donmuş görünmesin.
    """
    e = tg_eklemler(p)
    if max(TG_ZEMIN - e["ayak1"][1], TG_ZEMIN - e["ayak2"][1]) <= pay:
        return p
    q = dict(p, **{k: TG_TEMEL_POZ[k] for k in ("u1", "b1", "u2", "b2", "a1", "a2")})
    return tg_yerlestir(q)


def _hk_duraklat(K, baslar, sure=KAYAN_DURAKLAMA):
    """
    Kayan turda ritim (Paket 25): her istasyon başlangıcında (baslar, sn) figür ve parkur `sure` kadar durur —
    dünya ilerlemesi sıfır; göz hareketin başladığını fark eder. Figür duraklamada iki ayağı yerde, nötr hazır
    duruştadır (_hk_hazir_durus, Paket 26). Başlangıç anahtarı kopyalanır, sonraki
    bütün anahtarlar kaydırılır. Döndürür: (yeni K, kay) — kay(t, sonra): eski zamanı yeniye çevirir; sonra=True
    ise tam başlangıç anındaki olay duraklamadan SONRAya düşer (top olayları, dönüş), False ise önceye (pencere).
    """
    baslar = sorted(baslar)

    def kay(t, sonra=True):
        return t + sure * sum(1 for b in baslar if b < t - 1e-9 or (sonra and abs(b - t) <= 1e-9))
    yeni = []
    for t, p, w in K:
        yeni.append((kay(t, False), p, w))
        if any(abs(b - t) <= 1e-9 for b in baslar):
            q = _hk_hazir_durus(p)                       # iki ayak yerde (Paket 26)
            if q is not p:                               # kısa geçişle hazır duruşa, sonra bekler
                yeni.append((kay(t, False) + min(0.12, sure / 3), q, w))
            yeni.append((kay(t, True), dict(q), w))
    return yeni, kay


KOORDINASYON_ISTASYONLARI = ("Öne takla", "Denge tahtası", "Engel üzerinden top atma", "Tek ayak sekme",
                             "Elle top yer değiştirme", "Ayakla top yer değiştirme", "Duvara top atma",
                             "Alttan-üstten engel geçişi", "Slalom")   # TSYT protokolü 2-10. adımlar, aynı sıra


def hk_koordinasyon_turu(x_c=118, s=0.7, m=34.5):
    """
    TSYT Koordinasyon Parkuru — KAYAN SAHNE turu. Figür tuvalde x_c'de kalır, parkur (dünya) altından kayar;
    figür o anda yanından geçtiği istasyonun hareketini yapar. Sıra ve içerik protokolden (dokuz istasyon):
    1 öne takla · 2 denge tahtası (koşarak) · 3 engel üzerinden top atma (at, altından geç, tut, altından dön, bırak)
    · 4 tek ayak sekme (3 sağ, 3 sol) · 5 elle top yer değiştirme · 6 ayakla top yer değiştirme · 7 duvara top
    atma (al, at, tut, bırak) · 8 alttan-üstten engel (80-40-80-40) · 9 slalom (4 dikey engel), bitiş fotoseli.
    m: 1 m kaç birim (figürle aynı ölçek). 3. ve 7. istasyonlarda protokoldeki 2 ve 3 topun ilki gösterilir.
    olay: "sure" (sn), "kayma" [(t, dx)] (tuval x = dünya x + dx), "ekipman" (dünya konumları), "istasyonlar"
    [(no, t0, t1)], "toplar" [[(t, x, y)] tuvalde], "donus" (t0, t1, cx, cy) tuvalde.
    """
    Z = TG_ZEMIN
    K, T, W = [], 0.0, 0.0                              # anahtarlar [(T sn, poz, W)], şimdiki zaman ve dünya x'i
    ek = {}
    ist = []
    olaylar = []                                         # top olayları: (top, T, tur, veri)

    def ekle(hareket, sure, ref_x=None):
        nonlocal T, W
        ref = hareket.anahtarlar[0][1]["hx"] if ref_x is None else ref_x
        parca = _hk_yerinde(hareket, x_c, T, T + sure, W, ref)
        K.extend(parca[1:] if K and abs(parca[0][0] - K[-1][0]) < 1e-9 else parca)
        T, W = parca[-1][0], parca[-1][2]

    def kos(mesafe, sure, yon=1, adim=24):
        nonlocal T, W
        n = max(2, int(abs(mesafe) / (adim * s)))
        for i in range(1, n + 1):
            K.append((T + sure * i / n, _hk_kos_pozu(x_c, i, yon, s), W + mesafe * i / n))
        T, W = T + sure, W + mesafe

    def dur(sure):
        nonlocal T
        K.append((T + sure, dict(K[-1][1]), W))
        T += sure

    # başlangıç: başlama çizgisinde (fotosel), "çık" komutu
    K.append((0.0, tg_poz(x_c, s=s), 0.0))
    ek["baslangic"] = W + 10 * s
    dur(0.25)
    kos(0.45 * m, 0.3, adim=9)
    # 1 — öne takla (minder)
    t0 = T
    ek["minder"] = (W - 0.15 * m, W + 1.6 * m)
    tk = hk_takla(0, s, mesafe=1.0 * m)
    d0, d1, cx, cy = tk.olay["donus"]
    sure = 0.75
    a0 = len(K)
    ekle(tk, sure)
    for i in range(a0, len(K)):                         # dönüş boyunca ileri yuvarlanma (dünya ilerler)
        tt, p, w = K[i]
        f = min(1.0, max(0.0, ((tt - t0) / sure - d0) / (d1 - d0)))
        K[i] = (tt, p, w + tk.olay["yuvarlanma"] * f)
    W = K[-1][2]
    donus = (t0 + d0 * sure, t0 + d1 * sure, x_c + cx, cy)
    ist.append((1, t0, T))
    kos(0.4 * m, 0.25, adim=12)
    # 2 — denge tahtası 3 m; başlangıç ve bitişte 30 cm'lik bölgeler; koşarak geçer
    t0 = T
    ust = Z - 0.2 * m
    ek["denge"] = (W - 0.1 * m, W + 2.9 * m, ust)
    n = 10                                               # tahta üstünde 10 adım (sık kare: zaman dengesi)
    for i in range(1, n + 1):
        K.append((T + 0.6 * i / n, tg_yerlestir(_hk_kos_pozu(x_c, i, 1, s), zemin=ust), W + 3.0 * m * i / n))
    T, W = T + 0.6, W + 3.0 * m
    K.append((T + 0.05, _hk_kos_pozu(x_c, 1, 1, s), W + 0.3 * m))
    T, W = T + 0.05, W + 0.3 * m
    ist.append((2, t0, T))
    kos(0.4 * m, 0.2, adim=12)
    # 3 — engel (130 cm) üzerinden top: çemberden al, at, altından geç, tut, altından dön, çembere bırak
    t0 = T
    cember3 = W + 0.35 * m
    engel = W + 0.9 * m
    ek["engel_ust"] = (engel, 1.3 * m)
    ek["cember3"] = cember3
    al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
    olaylar.append(("t3", 0.0, "dunya", (cember3, Z - 3.2 * s)))
    olaylar.append(("t3", T + 0.25 * al.olay["an"], "el", None))
    ekle(al, 0.25)
    at = hk_atma(0, "ileri", s=s)
    t_at = T + 0.22 * at.olay["birakma_t"]
    ekle(at, 0.22)
    alt = hk_alttan_gec(0, 1.3 * m, s, uzunluk=1.3 * m)
    t_tut = T + 0.32
    olaylar.append(("t3", t_at, "ucus", (engel, Z - 1.3 * m - 14 * s, t_tut)))
    ekle(alt, 0.3)
    tut = hk_egil_al(0, s, "tut")
    ekle(tut, 0.1)
    olaylar.append(("t3", T, "el", None))
    # son eğik karede kalça direklerin (engel ± 6) dışında: doğrulma ancak sonra başlar (Paket 26)
    geri = hk_alttan_gec(0, 1.3 * m, s, uzunluk=(W - 8 * s) - (engel - 6 - 1.5))
    geri = TgHareket([(t, dict(p, hx=-p["hx"], yon=-1)) for t, p in geri.anahtarlar], geri.olay)
    ekle(geri, 0.3)
    bir = hk_egil_al(0, s, "birak", hedef_dx=W - cember3)      # top yine çemberin ortasına
    bir = TgHareket([(t, dict(p, hx=-p["hx"], yon=-1)) for t, p in bir.anahtarlar], bir.olay)
    t_bir = T + 0.22 * bir.olay["an"]
    ekle(bir, 0.22)
    olaylar.append(("t3", t_bir, "dunya", None))
    gec = hk_alttan_gec(0, 1.3 * m, s, uzunluk=(engel + 0.6 * m) - W - 16 * s)
    ekle(gec, 0.3)
    ist.append((3, t0, T))
    kos(0.3 * m, 0.15)
    # 4 — tek ayak sekme: bitişik 6 çember (60 cm), ilk üçü sağ (yakın), sonraki üçü sol (uzak) ayak
    t0 = T
    ek["sekme"] = [W + 0.3 * m + i * 0.6 * m for i in range(6)]
    for ayak, bas in (("1", W), ("2", W + 1.8 * m)):
        sk = hk_tek_ayak_sekme(bas, None, sekme_sonra=3, adim=0.6 * m, yukselme=8 * s, s=s, ayak=ayak)
        ekle(sk, 0.33)
    ist.append((4, t0, T))
    kos(0.3 * m, 0.15)
    # 5 — elle top yer değiştirme: üç çember, aralarında 1 m; A ve B'de top, C boş → A→C, B→A, C→B
    t0 = T
    A, B, C = W + 0.5 * m, W + 1.5 * m, W + 2.5 * m
    ek["el_cember"] = (A, B, C)
    olaylar += [("t5a", 0.0, "dunya", (A, Z - 3.2 * s)), ("t5b", 0.0, "dunya", (B, Z - 3.2 * s))]
    for top, kaynak, hedef in (("t5a", A, C), ("t5b", B, A), ("t5a", C, B)):
        kos(kaynak - 0.35 * m - W, 0.08, 1 if kaynak - 0.35 * m >= W else -1)
        al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
        olaylar.append((top, T + 0.12 * al.olay["an"], "el", None))
        ekle(al, 0.12)
        yon = 1 if hedef > kaynak else -1
        kos(hedef - kaynak, 0.08, yon)
        bir = hk_egil_al(0, s, "birak", hedef_dx=0.35 * m)
        olaylar.append((top, T + 0.12 * bir.olay["an"], "dunya", None))
        ekle(bir, 0.12)
    ist.append((5, t0, T))
    kos(C + 0.25 * m - W, 0.15)
    # 6 — ayakla top yer değiştirme (aynı düzen, 3 numara hentbol topları)
    t0 = T
    A, B, C = W + 0.5 * m, W + 1.5 * m, W + 2.5 * m
    ek["ayak_cember"] = (A, B, C)
    olaylar += [("t6a", 0.0, "dunya", (A, Z - 2.6 * s)), ("t6b", 0.0, "dunya", (B, Z - 2.6 * s))]
    for top, kaynak, hedef in (("t6a", A, C), ("t6b", B, A), ("t6a", C, B)):
        yon = 1 if hedef > kaynak else -1
        kos(kaynak - yon * 0.4 * m - W, 0.07, 1 if kaynak - yon * 0.4 * m >= W else -1)
        it = hk_egil_al(0, s, "ayak")
        it = TgHareket([(t, dict(p, yon=yon)) for t, p in it.anahtarlar], it.olay)
        t_it = T + 0.1 * it.olay["an"]
        ekle(it, 0.1)
        olaylar.append((top, t_it, "yuvarlan", (hedef, Z - 2.6 * s, t_it + 0.1)))
        kos(hedef - yon * 0.4 * m - W, 0.1, yon)
    ist.append((6, t0, T))
    kos(C + 0.25 * m - W, 0.15)
    # 7 — duvara top atma: duvardan 1,5 m'deki üç çember (aralarında 20 cm); al, at, tut, bırak
    t0 = T
    c7 = W + 0.35 * m
    duvar = c7 + 1.5 * m
    ek["duvar"] = duvar
    ek["duvar_cember"] = [c7, c7 - 0.8 * m, c7 - 1.6 * m]
    olaylar += [("t7", 0.0, "dunya", (c7, Z - 2.4 * s))]
    al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
    olaylar.append(("t7", T + 0.15 * al.olay["an"], "el", None))
    ekle(al, 0.15)
    at = hk_atma(0, "duvara", s=s)
    at = TgHareket([(t / 0.42, p) for t, p in at.anahtarlar if t <= 0.42 + 1e-9], at.olay)   # tek atış: at, tut
    tb = at.olay["birakma_t"] / 0.42
    t_b = T + 0.4 * tb
    t_don = T + 0.4
    olaylar.append(("t7", t_b, "duvar", (duvar, Z - 0.9 * m, t_don)))
    ekle(at, 0.4)
    olaylar.append(("t7", t_don, "el", None))
    bir = hk_egil_al(0, s, "birak", hedef_dx=0.35 * m)
    olaylar.append(("t7", T + 0.15 * bir.olay["an"], "dunya", None))
    ekle(bir, 0.15)
    ist.append((7, t0, T))
    kos(duvar - W + 0.25 * m, 0.2)
    # 8 — alttan-üstten: dört engel (80-40-80-40 cm), aralarında 1 m
    t0 = T
    engeller = [(W + 0.6 * m + i * 1.0 * m, (0.8, 0.4)[i % 2] * m) for i in range(4)]
    ek["alttan_ustten"] = engeller
    for i, (ex, eh) in enumerate(engeller):
        hedef_x = ex + 0.5 * m
        if i % 2 == 0:
            ekle(hk_alttan_gec(0, eh, s, uzunluk=hedef_x - W - 24 * s), 0.22)
        else:
            ekle(hk_engel_ustu(0, eh, s, uzunluk=hedef_x - W), 0.18)
    ist.append((8, t0, T))
    kos(0.3 * m, 0.12)
    # 9 — slalom: dört dikey engel, aralarında 80 cm; başlama yönü serbest
    t0 = T
    kazik = [W + 0.4 * m + i * 0.8 * m for i in range(4)]
    ek["slalom"] = kazik
    nok = [(W, Z)] + [(k + 0.0, Z + (2.5 if i % 2 == 0 else -2.5) * s) for i, k in enumerate(kazik)] + [(kazik[-1] + 0.6 * m, Z)]
    sl = hk_kavisli_yol(nok, s=s)
    ekle(sl, 0.65)
    ist.append((9, t0, T))
    # bitiş fotoseli
    ek["bitis"] = W + 0.4 * m
    kos(0.6 * m, 0.25)
    # hız sınırı (Paket 22): istasyon süresi kat ettiği mesafeden; bütün zamanlar aynı gerdirmeyle taşınır
    K[:], ger = _hk_hiz_siniri(K, [(a, b) for _, a, b in ist])
    ist[:] = [(n, ger(a), ger(b)) for n, a, b in ist]
    olaylar[:] = [(k, ger(t) if t > 0 else t, tur,
                   (veri[0], veri[1], ger(veri[2])) if tur in ("ucus", "duvar", "yuvarlan") else veri)
                  for k, t, tur, veri in olaylar]
    donus = (ger(donus[0]), ger(donus[1]), donus[2], donus[3])
    K[:], kay = _hk_duraklat(K, [a for _, a, _ in ist])          # ritim (Paket 25): istasyon başında duraklama
    ist[:] = [(n, kay(a, False), kay(b, False)) for n, a, b in ist]
    olaylar[:] = [(k, kay(t) if t > 0 else t, tur,
                   (veri[0], veri[1], kay(veri[2])) if tur in ("ucus", "duvar", "yuvarlan") else veri)
                  for k, t, tur, veri in olaylar]
    donus = (kay(donus[0]), kay(donus[1]), donus[2], donus[3])
    T = K[-1][0]
    toplam = T

    # zaman → 0-1; kayma dx(t) = x_c − W(t)
    an = [(t / toplam, p) for t, p, _ in K]
    kayma = [(t / toplam, x_c - w) for t, _, w in K]

    def dx_at(t):
        for (ta, da), (tb_, db) in zip(kayma, kayma[1:]):
            if ta <= t <= tb_:
                return da + (db - da) * ((t - ta) / ((tb_ - ta) or 1))
        return kayma[-1][1]

    def el_at(t):
        for (ta, pa), (tb_, pb) in zip(an, an[1:]):
            if ta <= t <= tb_:
                ea, eb = tg_eklemler(pa), tg_eklemler(pb)
                f = (t - ta) / ((tb_ - ta) or 1)
                ka = "el1"
                return (ea[ka][0] + (eb[ka][0] - ea[ka][0]) * f, ea[ka][1] + (eb[ka][1] - ea[ka][1]) * f)
        return tg_eklemler(an[-1][1])["el1"]

    # toplar: dünya/el/uçuş durumları → tuvalde [(t, x, y)]
    zamanlar = sorted({t for t, _ in an})
    toplar = {}
    for top in dict.fromkeys(o[0] for o in olaylar):
        ev = sorted([o for o in olaylar if o[0] == top], key=lambda o: o[1])
        ev = [(t / toplam, tur, veri) for _, t, tur, veri in ev]
        yol = []
        konum = None
        for i, (te, tur, veri) in enumerate(ev):
            sonraki = ev[i + 1][0] if i + 1 < len(ev) else 1.0
            if tur == "dunya":
                konum = veri if veri is not None else (yol[-1][1] - dx_at(te), Z - 3.2 * s)
                aralik = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
                yol += [(z, konum[0] + dx_at(z), konum[1]) for z in aralik]
            elif tur == "el":
                aralik = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
                yol += [(z, el_at(z)[0] + 2 * s, el_at(z)[1] - 2 * s) for z in aralik]
            elif tur in ("ucus", "duvar", "yuvarlan"):
                hx_, hy_, t_son = veri
                t_son /= toplam
                bas = (el_at(te)[0], el_at(te)[1]) if tur != "yuvarlan" else (yol[-1][1], yol[-1][2])
                if tur == "duvar":                       # duvara gidip döner, ele
                    orta = (te + t_son) / 2
                    for j in range(5):
                        f = j / 4
                        z = te + (orta - te) * f
                        yol.append((z, bas[0] + (hx_ + dx_at(z) - 2 - bas[0]) * f, bas[1] + (hy_ - bas[1]) * f))
                    son = el_at(t_son)
                    for j in range(1, 5):
                        f = j / 4
                        z = orta + (t_son - orta) * f
                        yol.append((z, hx_ + dx_at(z) - 2 + (son[0] - hx_ - dx_at(z) + 2) * f, hy_ + (son[1] - hy_) * f))
                elif tur == "ucus":                      # engelin üstünden: tepe hy_ (dünya x hx_ üstünde)
                    son_d = el_at(t_son)
                    b_d = (bas[0] - dx_at(te), bas[1])   # dünyada
                    s_d = (son_d[0] - dx_at(t_son), son_d[1])
                    for j in range(1, 9):
                        f = j / 8
                        z = te + (t_son - te) * f
                        xd = b_d[0] + (s_d[0] - b_d[0]) * f
                        yd = b_d[1] + (s_d[1] - b_d[1]) * f - 4 * (min(b_d[1], s_d[1]) - hy_) * f * (1 - f)
                        yol.append((z, xd + dx_at(z), yd))
                else:                                     # ayakla itilen top yerde yuvarlanır
                    b_d = bas[0] - dx_at(te)
                    for j in range(1, 6):
                        f = j / 5
                        z = te + (t_son - te) * f
                        yol.append((z, b_d + (hx_ - b_d) * f + dx_at(z), hy_))
                    yol += [(z, hx_ + dx_at(z), hy_) for z in zamanlar if t_son < z < sonraki] + [(sonraki, hx_ + dx_at(sonraki), hy_)]
        yol = [(0.0, *yol[0][1:])] + yol if yol[0][0] > 0 else yol
        temiz = []
        for p in yol:
            if not temiz or p[0] > temiz[-1][0] + 1e-6:
                temiz.append(p)
        toplar[top] = temiz
    # oynatma süresi = tur süresi (Paket 22: sıkıştırma yok; hız sınırı yukarıda)
    olay = {"sure": round(toplam, 2), "kayma": kayma, "ekipman": ek,
            "istasyonlar": [(n, a / toplam, b / toplam) for n, a, b in ist],
            "istasyon_adlari": [KOORDINASYON_ISTASYONLARI[n - 1] for n, _, _ in ist],
            "toplar": list(toplar.values()), "donus": (donus[0] / toplam, donus[1] / toplam, donus[2], donus[3]),
            "dunya_son": W}
    return TgHareket(an, olay)


def hk_yana_kayma(x0, x1, s=1.0, adim=None):
    """
    Yana kayma (side slide, önden görünüş): ayaklar açılır-kapanır, gövde dik, ayaklar çapraz geçmez; x0 → x1.
    Her adım: açık (ayaklar ayrık) → kapalı (ayaklar yanaşık), hafif yaylanma.
    """
    adim = 14 * s if adim is None else adim
    n = max(2, int(abs(x1 - x0) / adim))
    on = dict(cephe=True, a1=90, a2=-90, k1=40, o1=70, k2=-40, o2=-70, s=s, g=0)
    an = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        acik = i % 2 == 1
        p = tg_poz(x, **on, **(dict(u1=16, b1=16, u2=-16, b2=-16) if acik else dict(u1=4, b1=4, u2=-4, b2=-4)))
        an.append((i / n, tg_yerlestir(p) if not acik else dict(tg_yerlestir(p), hy=tg_yerlestir(p)["hy"] - 2 * s)))
    an[-1] = (1.0, tg_yerlestir(tg_poz(x1, **on, u1=4, b1=4, u2=-4, b2=-4)))
    return TgHareket(an, {})


def hk_skipping(x0, x1, s=1.0, adim=None):
    """
    Skipping (adım-sekme; ipli atlama değil): her adımda destek ayağında küçük sekme, öbür diz öne-yukarı kalkar,
    karşı kol öne; ayaklar sırayla. x0 → x1.
    """
    adim = 20 * s if adim is None else adim
    n = max(2, int(abs(x1 - x0) / adim))
    an = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        if i % 2 == 0:
            p = tg_poz(x, s=s, g=6, u1=0, b1=0, u2=70, b2=-10, k1=-30, o1=20, k2=50, o2=110)   # sağ diz yukarı
        else:
            p = tg_poz(x, s=s, g=6, u1=70, b1=-10, u2=0, b2=0, k1=50, o1=110, k2=-30, o2=20)   # sol diz yukarı
        p = tg_yerlestir(p)
        an.append((i / n, dict(p, hy=p["hy"] - (4 * s if i % 2 else 3 * s))))     # sekme: destek ayağı yerden kalkar
    an[-1] = (1.0, tg_yerlestir(tg_poz(x1, s=s)))
    return TgHareket(an, {})


def hk_topa_vurus(x, s=1.0):
    """
    Topa vuruş (iç-üst ayak/ayak üstü): destek ayağı topun yanında, vuran bacak geriden öne savrulur; vuruş anı
    olay["vurus_t"], ayak ucu olay["ayak"]. Son anahtar = vuruş sonrası (bacak önde).
    """
    yaklas = tg_yerlestir(tg_poz(x - 16 * s, s=s, g=10, u1=30, b1=-10, u2=-30, b2=-60, k1=-30, o1=10, k2=30, o2=60))
    geri = tg_yerlestir(tg_poz(x, s=s, g=6, u1=0, b1=0, u2=-40, b2=-100, k1=40, o1=60, k2=-40, o2=-10), bacak="1")
    vur = tg_yerlestir(tg_poz(x, s=s, g=-6, u1=0, b1=0, u2=40, b2=30, a2=120, k1=-40, o1=-10, k2=50, o2=70), bacak="1")
    son = tg_yerlestir(tg_poz(x + 4 * s, s=s, g=-4, u1=-6, b1=-6, u2=70, b2=60, a2=130, k1=-40, o1=-10, k2=60, o2=80),
                       bacak="1")
    an = [(0.0, yaklas), (0.35, geri), (0.6, vur), (1.0, son)]
    return TgHareket(an, {"vurus_t": 0.6, "ayak": tg_eklemler(vur)["parmak2"]})


CAMSA_BECERILERI = ("Çift ayak sıçrama", "Yana kayma", "Top yakalama", "Hedefe atış", "Skipping",
                    "Tek ayak sekme", "Topa vuruş")   # CAMSA (CAPL-2), sabit sıra


def _hk_tur_toplari(an, kayma, olaylar, toplam, Z, s):
    """
    Kayan turda topların tuval yolu. olaylar: (top, T sn, tür, veri). Türler: "dunya" (dünyada duran; veri (x, y)
    ya da None = bulunduğu yer), "el" (elde), "ucus" ((tepe_y, T_son, hedef) — hedef "el" ya da dünya (x, y);
    başlangıç verilmezse elden), "dunyadan" ((x0, y0) dünyadan fırlar → sonraki "el" anına uçar, tepe yüksek).
    """
    zamanlar = sorted({t for t, _ in an})

    def dx_at(t):
        for (ta, da), (tb, db) in zip(kayma, kayma[1:]):
            if ta <= t <= tb:
                return da + (db - da) * ((t - ta) / ((tb - ta) or 1))
        return kayma[-1][1]

    def el_at(t):
        for (ta, pa), (tb, pb) in zip(an, an[1:]):
            if ta <= t <= tb:
                ea, eb = tg_eklemler(pa)["el1"], tg_eklemler(pb)["el1"]
                f = (t - ta) / ((tb - ta) or 1)
                return (ea[0] + (eb[0] - ea[0]) * f, ea[1] + (eb[1] - ea[1]) * f)
        return tg_eklemler(an[-1][1])["el1"]

    sonuc = []
    for top in dict.fromkeys(o[0] for o in olaylar):
        ev = sorted([(t / toplam, tur, veri) for k, t, tur, veri in olaylar if k == top], key=lambda o: o[0])
        yol, konum = [], None
        for i, (te, tur, veri) in enumerate(ev):
            sonraki = ev[i + 1][0] if i + 1 < len(ev) else 1.0
            ara = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
            if tur == "dunya":
                konum = veri if veri is not None else (yol[-1][1] - dx_at(te), yol[-1][2])
                yol += [(z, konum[0] + dx_at(z), konum[1]) for z in ara]
            elif tur == "el":
                yol += [(z, el_at(z)[0] + 2 * s, el_at(z)[1] - 2 * s) for z in ara]
            elif tur == "ucus":
                tepe_y, t_son, hedef = veri
                t_son /= toplam
                b = (yol[-1][1] - dx_at(te), yol[-1][2]) if yol else (el_at(te)[0] - dx_at(te), el_at(te)[1])
                if hedef == "el":
                    sv = el_at(t_son)
                    h = (sv[0] - dx_at(t_son), sv[1])
                else:
                    h = hedef
                for j in range(1, 11):
                    f = j / 10
                    z = te + (t_son - te) * f
                    xd = b[0] + (h[0] - b[0]) * f
                    yd = b[1] + (h[1] - b[1]) * f - 4 * (min(b[1], h[1]) - tepe_y) * f * (1 - f)
                    yol.append((z, xd + dx_at(z), yd))
                if hedef != "el":
                    yol += [(z, h[0] + dx_at(z), h[1]) for z in ara if z > t_son]
        if yol[0][0] > 0:
            yol = [(0.0, *yol[0][1:])] + yol
        temiz = []
        for p in yol:
            if not temiz or p[0] > temiz[-1][0] + 1e-6:
                temiz.append(p)
        sonuc.append(temiz)
    return sonuc


def hk_camsa_turu(x_c=118, s=0.7, m=34.5):
    """
    CAPL-2 motor beceri testi CAMSA — KAYAN SAHNE turu (Koordinasyon Parkuru ile aynı yapı). Figür x_c'de kalır,
    parkur altından kayar. Sabit sıra (Cao ve ark. 2020; Chang ve ark. 2021): 1 çift ayak sıçrama (3 çember) ·
    2 yana kayma (iki kez, biri ters yönde) · 3 uygulayıcının attığı topu yakalama · 4 hedefe atış · 5 skipping (5 m)
    · 6 tek ayak sekme (6 çember) · 7 iki koni arasından topa vuruş — süre vuruşla durur.
    Protokolde yalnız skipping mesafesi (5 m) ve çember sayıları var; öbür aralıklar şematik.
    olay: "sure", "kayma", "ekipman", "beceriler" [(no, t0, t1)], "beceri_adlari", "toplar", "uygulayici" (eklemler).
    """
    Z = TG_ZEMIN
    K, T, W = [], 0.0, 0.0
    ek, bec, olaylar = {}, [], []

    def ekle(hareket, sure):
        nonlocal T, W
        ref = hareket.anahtarlar[0][1]["hx"]
        parca = _hk_yerinde(hareket, x_c, T, T + sure, W, ref)
        K.extend(parca[1:] if K and abs(parca[0][0] - K[-1][0]) < 1e-9 else parca)
        T, W = parca[-1][0], parca[-1][2]

    def kos(mesafe, sure, yon=1, adim=12):
        nonlocal T, W
        n = max(2, int(abs(mesafe) / (adim * s)))
        for i in range(1, n + 1):
            K.append((T + sure * i / n, _hk_kos_pozu(x_c, i, yon, s), W + mesafe * i / n))
        T, W = T + sure, W + mesafe

    K.append((0.0, tg_poz(x_c, s=s), 0.0))
    K.append((0.2, tg_poz(x_c, s=s), 0.0))
    T = 0.2
    # 1 — çift ayak sıçrama: üç çemberin üzerinden
    t0 = T
    ek["cift_cember"] = [W + (0.45 + 0.6 * i) * m for i in range(3)]
    ekle(hk_tek_ayak_sekme(0, None, sekme_sonra=4, adim=0.6 * m, yukselme=7 * s, s=s, ayak="cift"), 0.9)
    bec.append((1, t0, T))
    kos(0.5 * m, 0.15)
    # 2 — yana kayma: koniye kadar ve geri (iki kez, biri ters yönde)
    t0 = T
    ek["kayma_koni"] = (W - 0.2 * m, W + 2.2 * m)
    ekle(hk_yana_kayma(0, 2.0 * m, s), 0.45)
    ekle(hk_yana_kayma(2.0 * m, 0.4 * m, s), 0.4)
    bec.append((2, t0, T))
    kos(0.8 * m, 0.15)
    # 3 — top yakalama: uygulayıcı karşıdan atar
    t0 = T
    ek["uygulayici"] = W + 2.6 * m
    tut = hk_egil_al(0, s, "tut")
    olaylar.append(("top", 0.0, "dunya", (ek["uygulayici"] - 6 * s, Z - 0.95 * m)))
    olaylar.append(("top", T + 0.05, "ucus", (Z - 1.6 * m, T + 0.5 * tut.olay["an"] + 0.12, "el")))
    olaylar.append(("top", T + 0.5 * tut.olay["an"] + 0.12, "el", None))
    ekle(TgHareket([(0, tut.anahtarlar[0][1]), (0.3, tut.anahtarlar[0][1])] + [(0.3 + 0.7 * t, p) for t, p in tut.anahtarlar[1:]], tut.olay), 0.5)
    bec.append((3, t0, T))
    kos(ek["uygulayici"] + 0.6 * m - W, 0.2)            # uygulayıcının yanından geçer: hedef önünde açık kalır
    # 4 — hedefe atış: hedef karşıda (duvarda)
    t0 = T
    ek["hedef"] = (W + 3.0 * m, Z - 1.2 * m)
    at = hk_atma(0, "duvara", s=s)
    at = TgHareket([(t / 0.42, p) for t, p in at.anahtarlar if t <= 0.42 + 1e-9], at.olay)
    t_b = T + 0.45 * (at.olay["birakma_t"] / 0.42)
    olaylar.append(("top", t_b, "ucus", (Z - 1.5 * m, t_b + 0.18, ek["hedef"])))
    ekle(at, 0.45)
    bec.append((4, t0, T))
    kos(0.5 * m, 0.12)
    # 5 — skipping 5 m
    t0 = T
    ek["skip"] = (W, W + 5.0 * m)
    ekle(hk_skipping(0, 5.0 * m, s), 0.9)
    bec.append((5, t0, T))
    kos(0.5 * m, 0.12)
    # 6 — tek ayak sekme: altı çemberin üzerinden
    t0 = T
    ek["tek_cember"] = [W + (0.3 + 0.6 * i) * m for i in range(6)]
    ekle(hk_tek_ayak_sekme(0, None, sekme_sonra=7, adim=0.6 * m, yukselme=7 * s, s=s), 0.9)
    bec.append((6, t0, T))
    kos(0.5 * m, 0.12)
    # 7 — iki koni arasından topa vuruş; süre vuruşla durur
    t0 = T
    vur = hk_topa_vurus(0, s)
    top_x = W + 16 * s + (vur.olay["ayak"][0] - vur.anahtarlar[0][1]["hx"]) - 16 * s
    ek["vurus_top"] = top_x
    ek["koniler"] = (top_x + 2.6 * m, top_x + 3.4 * m)
    olaylar.append(("futbol", 0.0, "dunya", (top_x + 2 * s, Z - 2.8 * s)))
    t_v = T + 0.45 * vur.olay["vurus_t"]
    olaylar.append(("futbol", t_v, "ucus", (Z - 3.5 * s, t_v + 0.35, (sum(ek["koniler"]) / 2, Z - 2.8 * s))))
    ekle(vur, 0.45)
    ek["bitis_t"] = t_v
    bec.append((7, t0, T))
    K.append((T + 0.35, dict(K[-1][1]), W))
    # hız sınırı (Koordinasyon turuyla aynı kural): beceri süresi kat ettiği mesafeden
    K[:], ger = _hk_hiz_siniri(K, [(a, b) for _, a, b in bec])
    bec[:] = [(n, ger(a), ger(b)) for n, a, b in bec]
    olaylar[:] = [(k, ger(t) if t > 0 else t, tur, (veri[0], ger(veri[1]), veri[2]) if tur == "ucus" else veri)
                  for k, t, tur, veri in olaylar]
    ek["bitis_t"] = ger(ek["bitis_t"])
    K[:], kay = _hk_duraklat(K, [a for _, a, _ in bec])           # ritim (Paket 25): beceri başında duraklama
    bec[:] = [(n, kay(a, False), kay(b, False)) for n, a, b in bec]
    olaylar[:] = [(k, kay(t) if t > 0 else t, tur, (veri[0], kay(veri[1]), veri[2]) if tur == "ucus" else veri)
                  for k, t, tur, veri in olaylar]
    ek["bitis_t"] = kay(ek["bitis_t"])
    T = K[-1][0]
    toplam = T
    an = [(t / toplam, p) for t, p, _ in K]
    kayma = [(t / toplam, x_c - w) for t, _, w in K]
    uyg = tg_poz(ek["uygulayici"], s=s, yon=-1, k1=60, o1=90, k2=50, o2=80)
    return TgHareket(an, {"sure": round(toplam, 2), "kayma": kayma, "ekipman": ek,
                          "beceriler": [(n, a / toplam, b / toplam) for n, a, b in bec],
                          "beceri_adlari": [CAMSA_BECERILERI[n - 1] for n, _, _ in bec],
                          "bitis_t": ek["bitis_t"] / toplam,
                          "toplar": _hk_tur_toplari(an, kayma, olaylar, toplam, Z, s),
                          "uygulayici": tg_eklemler(uyg), "uygulayici_s": s})


def hk_servis(x, s=1.0):
    """
    Tenis servisi (yandan): top havaya atılır (atan kol yukarı), raket kolu arkada bükülü, sonra yukarıdan vuruş
    (vuruş anı olay["vurus_t"], temas noktası olay["temas"]; top başta olay["tutan_el"]de). Son anahtar = TEMAS
    anı (Paket 24): raket yukarıda, kol uzanmış — durağan kare başlıktaki anı gösterir, vuruş sonrası çizilmez.
    hk_atma'nın baş üstü kol yolundan türetilmiştir. olay["raket"]: [(t, x, y)] raket başı (vuran elin uzantısı).
    """
    dur = tg_poz(x, s=s, k1=20, o1=60, k2=10, o2=30)
    atis = tg_poz(x, s=s, g=-8, u1=8, b1=-4, u2=-12, b2=-20, k1=-40, o1=-110, k2=170, o2=175)     # top elden çıkar
    yay = tg_poz(x, s=s, g=-14, u1=20, b1=-10, u2=-16, b2=-40, k1=150, o1=-30, k2=170, o2=178)     # raket sırtta
    vur = tg_yerlestir(tg_poz(x + 4 * s, s=s, g=10, u1=10, b1=-6, u2=-30, b2=-60, k1=168, o1=175, k2=60, o2=40))
    an = [(0.0, dur), (0.25, atis), (0.6, yay), (1.0, vur)]
    raket = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        (ex, ey), (dx, dy) = e["el1"], e["dirsek1"]
        u = _math.hypot(ex - dx, ey - dy) or 1
        raket.append((t, ex + (ex - dx) / u * 9 * s, ey + (ey - dy) / u * 9 * s))
    e = tg_eklemler(vur)
    temas = (e["el1"][0] + 2 * s, e["el1"][1] - 10 * s)
    return TgHareket(an, {"vurus_t": 1.0, "temas": temas, "atan_el": tg_eklemler(atis)["el2"],
                            "tutan_el": tg_eklemler(dur)["el2"], "raket": raket})


def hk_serbest_stil(x0, x1, su_y, s=1.0, kulac=4):
    """
    Serbest stil (yandan): gövde su çizgisinde yatay, yüz suda; kollar sırayla — biri su altında çeker
    (öne → aşağı → kalçaya), öbürü suyun ÜSTÜNDEN öne döner; bacaklar küçük çırpış. x0 → x1.
    Açılar sürekli azalır (−45°/anahtar): toparlanma suyun üstünden geçer, ara değer su altına kaçmaz.
    """
    an = []
    n = kulac * 8 - 5                    # son kare kulaç ortası (Paket 24): i ≡ 3 (mod 8) → yakın kol −45° (suda
                                         # çekişte), uzak kol 135° (suyun üstünde önde, toparlanmada)
    for i in range(n + 1):
        f = i / n
        a = 90 - 45 * i                                   # yakın kol: 90 (öne) → 0 (aşağı) → −90 (kalça) → −180 (üst)…
        cirp = 8 if i % 2 else -8
        p = tg_poz(x0 + (x1 - x0) * f, s=s, g=88, u1=-88 + cirp, b1=-84 + cirp, u2=-88 - cirp, b2=-84 - cirp,
                   a1=-180, a2=-176, k1=a, o1=a - 10, k2=a - 180, o2=a - 190)
        p = dict(p, hy=su_y + 2 * s)
        an.append((f, p))
    return TgHareket(an, {"su_y": su_y})


def hk_split(x, s=1.0, uzaklik=6.0):
    """
    Ön split (yandan): öndeki bacak öne, arkadaki geriye uzanır, gövde dik, kollar yanlarda. Kalça (kasık)
    zeminden `uzaklik` birim yukarıda kalır (0 = tam split). Ayaktan hamle → split; son anahtar = ölçüm anı.
    olay["kasik"]: son karede kasık noktası (ölçü bağı için kalça eklemi).
    """
    dur = tg_poz(x, s=s, k1=20, o1=20, k2=-20, o2=-20)
    hamle = tg_yerlestir(tg_poz(x, s=s, u1=50, b1=10, u2=-40, b2=-70, a2=150, k1=60, o1=70, k2=-60, o2=-70))
    L = (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s
    a = _math.degrees(_math.acos(max(0.0, min(1.0, uzaklik / L))))     # bacak açısı: kasık zeminden uzaklik kadar
    split = tg_yerlestir(tg_poz(x, s=s, u1=a, b1=a, u2=-a, b2=-a, a1=180, a2=-180, k1=90, o1=95, k2=-90, o2=-95))
    an = [(0.0, dur), (0.3, hamle), (0.85, split), (1.0, split)]
    return TgHareket(an, {"kasik": tg_eklemler(split)["kalca"], "L": L})


def _hk_iki_bag(kok, uc, L1, L2, isaret=1):
    """
    İki parçalı uzuv için ters kinematik (uyluk–baldır, üst kol–ön kol): kökten uca ulaşan iki açı (0 = aşağı,
    90 = ileri, 180 = yukarı; figür sağa bakar). isaret=+1: orta eklem yukarı/öne (diz yukarı), −1: aşağı/geriye
    (dirsek aşağıda). Uç erişilemiyorsa uzuv o yöne gergin uzanır.
    """
    dx, dy = uc[0] - kok[0], uc[1] - kok[1]
    d = max(1e-6, min(_math.hypot(dx, dy), L1 + L2 - 1e-6))
    th = _math.degrees(_math.atan2(dx, dy))
    al = _math.degrees(_math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))))
    a1 = th + isaret * al
    r = _math.radians(a1)
    ox, oy = kok[0] + _math.sin(r) * L1, kok[1] + _math.cos(r) * L1
    a2 = _math.degrees(_math.atan2(uc[0] - ox, uc[1] - oy))
    return a1, a2


def _hk_oturus(hx, hy, ayak, s, g, el1, el2, a=100):
    """Oturuş pozu: kalça (hx, hy) koltukta, ayaklar `ayak` noktasında (dizler yukarı), eller el1/el2 hedeflerinde."""
    L = _TG_BOY
    u, b = _hk_iki_bag((hx, hy), ayak, L["uyluk"] * s, L["baldir"] * s, 1)
    p = dict(tg_poz(hx, s=s, g=g, u1=u, b1=b, u2=u - 6, b2=b - 6, a1=a, a2=a), hy=hy)   # uzak bacak ayrışık
    boyun = tg_eklemler(p)["boyun"]
    k1, o1 = _hk_iki_bag(boyun, el1, L["ust"] * s, L["on"] * s, -1)
    k2, o2 = _hk_iki_bag(boyun, el2, L["ust"] * s, L["on"] * s, -1)
    return dict(p, k1=k1, o1=o1, k2=k2, o2=o2)


def hk_kurek_ergometre(ayak_x, s=0.7, kulac=2):
    """
    Kürek ergometresi (yandan, sağa bakar): ayaklar ayaklıkta sabit, koltuk rayda kayar. Kulaç: yakalama (dizler
    göğüste, kollar uzun, gövde önde) → itiş (bacaklar) → bitiş (bacaklar gergin, gövde geride, tutamak göğüste)
    → dönüş. Son anahtar = BİTİŞ anı (kulacın ayırt edici konumu). olay: "ayaklik", "tutamak" [(t, x, y)],
    "koltuk" [(t, x, y)] (kalça), "koltuk_y".
    """
    hy = TG_ZEMIN - 16 * s
    ayak = (ayak_x, TG_ZEMIN - 13 * s)
    yakala_x, bitis_x = ayak_x - 25 * s, ayak_x - 44.5 * s
    ust = (_TG_BOY["govde"] + 0) * s

    def omuz(hx, g):
        r = _math.radians(g)
        return hx + _math.sin(r) * ust, hy - _math.cos(r) * ust

    def poz(hx, g, tut):
        return _hk_oturus(hx, hy, ayak, s, g, tut, (tut[0] - 4.5 * s, tut[1] + 3 * s))   # uzak el ayrışık (Paket 25)   # uzak el ayrışık

    sx, sy = omuz(yakala_x, 28)
    yakala = poz(yakala_x, 28, (ayak_x - 3 * s, ayak[1] - 20 * s))
    itis = poz(ayak_x - 36 * s, 22, (ayak_x - 10 * s, ayak[1] - 21 * s))
    bx, by = omuz(bitis_x, -24)
    bitis = poz(bitis_x, -24, (bx + 9 * s, by + 12 * s))
    donus = poz(bitis_x + 3 * s, 20, (ayak_x - 6 * s, ayak[1] - 22 * s))
    an = []
    for i in range(kulac):
        t = i / kulac
        d = 1 / kulac
        an += [(t, yakala), (t + 0.22 * d, itis), (t + 0.45 * d, bitis)]
        if i < kulac - 1:
            an += [(t + 0.7 * d, donus)]
    an[-1] = (1.0, bitis)
    tut, kol = [], []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        tut.append((t, e["el1"][0], e["el1"][1]))
        kol.append((t, p["hx"], p["hy"]))
    return TgHareket(an, {"ayaklik": ayak, "tutamak": tut, "koltuk": kol, "koltuk_y": hy})


def hk_kayak_ergometre(x, s=0.7, kulac=2):
    """
    Kano/kayak ergometresi (yandan, sağa bakar): koltukta oturuş, bacaklar öne uzanık (dizler hafif bükük),
    çift palalı kürek iki elde. Bir yanda yakalama (alttaki el önde-aşağıda, üstteki el baş hizasında), çekiş
    (alttaki el kalçaya, üstteki el öne iter); sonra öbür yan. Son anahtar = YAKALAMA (pala suya girer).
    Üst el yüzün önünde kalır; sap hiçbir karede baş çemberinden geçmez (Paket 25). Gövde çalışır (Paket 27):
    yakalamada öne kapanır (g = 34°), çekişte açılır (g = 6°) — omuz alçalıp yükselir; kalça koltukta kalır.
    olay: "kurek" [(t, x1, y1, x2, y2)] kürek sapı (alt uç → üst uç), "ayaklik", "koltuk_y".
    """
    hy = TG_ZEMIN - 16 * s
    ayak = (x + 40 * s, TG_ZEMIN - 10 * s)
    g_yak, g_cek = 34, 6           # gövde: yakalamada öne kapanır, çekişte açılır (28° aralık; Paket 27)

    def boyun(g):
        r = _math.radians(g)
        return x + _math.sin(r) * _TG_BOY["govde"] * s, hy - _math.cos(r) * _TG_BOY["govde"] * s

    def poz(g, alt, ust, yakin_alt):
        e1, e2 = (alt, ust) if yakin_alt else (ust, alt)
        return _hk_oturus(x, hy, ayak, s, g, e1, e2, a=110)

    bx, by = boyun(g_yak)
    yak_alt, yak_ust = (bx + 26 * s, by + 22 * s), (bx + 18 * s, by - 8 * s)    # üst el yüzün önünde (Paket 25)
    bx, by = boyun(g_cek)
    cek_alt, cek_ust = (bx + 2 * s, by + 25 * s), (bx + 22 * s, by - 2 * s)
    an = []
    yanlar = [True, False] * kulac
    n = len(yanlar)
    for i, yakin in enumerate(yanlar):
        t = i / n
        an += [(t, poz(g_yak, yak_alt, yak_ust, yakin)), (t + 0.6 / n, poz(g_cek, cek_alt, cek_ust, yakin))]
    an.append((1.0, poz(g_yak, yak_alt, yak_ust, True)))
    kurek = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        (ax, ay), (cx, cy) = e["el1"], e["el2"]        # uçlar ellere bağlı: kareler arası uç değiş tokuşu yok
        ux, uy = cx - ax, cy - ay                      # (sıralama değişince sap baştan geçecek biçimde süpürüyordu)
        u = _math.hypot(ux, uy) or 1
        kurek.append((t, ax - ux / u * 24 * s, ay - uy / u * 24 * s, cx + ux / u * 24 * s, cy + uy / u * 24 * s))
    return TgHareket(an, {"kurek": kurek, "ayaklik": ayak, "koltuk_y": hy})


def _hk_bar_uzanis(p, hedef_y, s):
    """Gövde eğimini ayarlayıp kolları düz aşağı uzatarak elleri zemindeki barın yüksekliğine getirir (koparma çıkışı)."""
    en_iyi = None
    for g in range(20, 80):
        q = tg_yerlestir(dict(p, g=g))
        e = tg_eklemler(q)
        a = 8                                            # kollar dik aşağı, hafif öne
        q = dict(q, k1=a, o1=a, k2=a - 2, o2=a - 2)
        y = tg_eklemler(q)["el1"][1]
        if en_iyi is None or abs(y - hedef_y) < en_iyi[0]:
            en_iyi = (abs(y - hedef_y), q)
    return en_iyi[1]


def hk_koparma(x, s=0.6, plaka=7.0):
    """
    Koparma (snatch, yandan): bar yerde (plaka zemine değer), geniş tutuş → çekiş (gövde ve bacaklar açılır,
    parmak ucu) → bar baş üstünde, kollar kilitli, derin çömelişte karşılama. Son anahtar = KARŞILAMA (ayırt
    edici an: tek hareketle yerden baş üstüne). olay["bar"]: [(t, x, y)] bar ekseni (el).
    """
    bas = _hk_bar_uzanis(tg_poz(x, s=s, u1=78, b1=-28, u2=74, b2=-32), TG_ZEMIN - plaka, s)   # diz önde, kalça diz üstünde
    cek = tg_yerlestir(tg_poz(x + 2 * s, s=s, g=-6, u1=8, b1=-6, u2=4, b2=-10, a1=150, a2=150, k1=4, o1=4, k2=2, o2=2))
    karsila = tg_yerlestir(tg_poz(x - 2 * s, s=s, g=22, u1=112, b1=-30, u2=108, b2=-34, k1=-168, o1=-170, k2=-158, o2=-160))
    karsila = _hk_uclari_ayir(karsila, el=(-5.5 * s / 0.6, 0.5), pay=5.0)     # uzak kol görünür (Paket 25)
    an = [(0.0, bas), (0.15, bas), (0.5, cek), (1.0, karsila)]
    bar = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an)]
    return TgHareket(an, {"bar": bar, "plaka": plaka})


def hk_silkme(x, s=0.6):
    """
    Silkme (jerk, yandan): bar omuzda (ön tutuş, dirsekler önde) → çöküş → itiş → makas: ön bacak önde bükük, arka
    bacak geride, bar baş üstünde kollar kilitli. Son anahtar = MAKAS karşılama (ayırt edici an). olay["bar"]: [(t, x, y)].
    """
    def omuzda(p):                                        # ön tutuş: bar boynun önünde, omuz hizasında; dirsek önde
        p = tg_yerlestir(p)
        bx, by = tg_eklemler(p)["boyun"]
        k, o = _hk_iki_bag((bx, by), (bx + 6 * s, by + 3 * s), _TG_BOY["ust"] * s, _TG_BOY["on"] * s, 1)
        return dict(p, k1=k, o1=o, k2=k - 2, o2=o - 2)
    raf = omuzda(tg_poz(x, s=s))
    cok = omuzda(tg_poz(x, s=s, u1=30, b1=-20, u2=26, b2=-24))
    it = tg_yerlestir(tg_poz(x, s=s, u1=4, b1=-4, u2=0, b2=-8, a1=150, a2=150, k1=178, o1=180, k2=176, o2=178))
    makas = tg_yerlestir(tg_poz(x, s=s, g=2, u1=62, b1=8, u2=-38, b2=-62, a2=150, k1=-178, o1=-178, k2=-168, o2=-168))
    makas = _hk_uclari_ayir(makas, el=(-5.5 * s / 0.6, 0.5), pay=5.0)         # uzak kol görünür (Paket 25)
    an = [(0.0, raf), (0.2, raf), (0.45, cok), (0.65, it), (1.0, makas)]
    bar = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        bar.append((t, e["el1"][0], e["el1"][1]))
    return TgHareket(an, {"bar": bar})


def hk_eggbeater_sicrama(x, su_y, s=0.6, bekle=4):
    """
    Suda dikey sıçrama (su topu, yandan): derin suda dik; bekleme sırasında bacaklar sırayla dairesel çırpar
    (eggbeater), eller suyu yanlara iter; "git" ile bacak ve kol itişiyle yükselir, yakın kol yukarı uzanır.
    Son anahtar = TEPE (ölçüm anı: elin su yüzeyinden yüksekliği). olay["el"]: son karede uzanan elin ucu.
    """
    hy0 = su_y + 24 * s
    an = []
    for i in range(bekle):
        a = 25 if i % 2 else -15
        p = dict(tg_poz(x, s=s, g=6, u1=78, b1=a, u2=74, b2=-a + 10, a1=150, a2=150,
                        k1=70 + a / 2, o1=95, k2=60 - a / 2, o2=88), hy=hy0)
        an.append((0.45 * i / (bekle - 1), p))
    cok = dict(tg_poz(x, s=s, g=8, u1=95, b1=-30, u2=90, b2=-34, a1=150, a2=150, k1=40, o1=70, k2=36, o2=66), hy=hy0 + 3 * s)
    tepe = dict(tg_poz(x, s=s, g=-2, u1=20, b1=-6, u2=10, b2=-16, a1=170, a2=170, k1=176, o1=178, k2=40, o2=20),
                hy=su_y + 2 * s)
    an += [(0.6, cok), (1.0, tepe)]
    return TgHareket(an, {"el": tg_eklemler(tepe)["el1"], "su_y": su_y})


def hk_tutus(x, yon=1, s=1.0, adim=6, tur=3):
    """Karşılıklı tutuş (güreş duruşu): gövde öne eğik, eller rakibin ense/omzunda; küçük yan adımlarla döner."""
    an = []
    for i in range(tur + 1):
        f = 1 if i % 2 else -1
        p = tg_yerlestir(tg_poz(x + f * adim * (i > 0), s=s, yon=yon, g=38, u1=30 + 6 * f, b1=-22, u2=-14 - 6 * f, b2=-30,
                                k1=95, o1=110, k2=80, o2=96))
        an.append((i / tur, p))
    return TgHareket(an, {})
