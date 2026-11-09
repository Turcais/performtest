"""
PerformTest — Özel ve Çok Bileşenli Test Sahneleri Fabrikası (`ozel_sahne_fabrikasi.py`).

Bu modül:
1. Orijinal `olcut/gorseller/` içinde durağan son kare için tasarlanmış olan `CMJ / SJ / DJ` dikey sıçrama
   testlerine tam döngülü (çömelme -> patlayıcı sıçrama -> uçuş zirvesi -> amortisman inişi) biyomekanik
   animasyon kazandırır.
2. Durağan olan `Boy ve Vücut Ağırlığı`, `Oturma Yüksekliği` ve `Top Sektirme (BOT-2)` sahnelerini
   tam hareketli hale getirir.
3. `TEST_GORSELSIZ` içindeki 28 laboratuvar, vücut kompozisyonu ve branş bataryası testinin her birine
   kendi cihazı, sensörü, grafiği ve biyomekanik hareketiyle benzersiz SVG animasyon sahnesi üretir.
4. Çoklu branş testlerine (`Yo-Yo IR1/IR2`, `Sprint` mesafeleri, `Wingate`) branşa ve mesafeye özgü
   saha/ekipman katmanları ekler.
"""
import math as _math
from typing import Any, Callable

from olcut.gorseller.cizim import (
    TG_KALINLIK,
    TG_OLCU_Y,
    TG_RENK,
    TG_ZEMIN,
    TgHareket,
    TgSahne,
    _TG_BOY,
    tg_eklemler,
    tg_poz,
    tg_yerlestir,
)


def _tam_cmj_hareketi(x: float, yukselme: float = 22.0, s: float = 0.78, eller_kalcada: bool = True) -> TgHareket:
    """Eller kalçada (veya serbest) tam döngülü CMJ: duruş -> ön çömelme -> patlayıcı sıçrama (tepe) -> iniş -> duruş."""
    kol = dict(k1=-42, o1=52, k2=-22, o2=70) if eller_kalcada else dict(k1=10, o1=8, k2=-8, o2=-6)
    dip_kol = dict(k1=-54, o1=-24, k2=-38, o2=-12) if eller_kalcada else dict(k1=-55, o1=-40, k2=-48, o2=-30)
    tepe_kol = dict(k1=-38, o1=48, k2=-20, o2=66) if eller_kalcada else dict(k1=155, o1=168, k2=145, o2=158)

    dur = tg_yerlestir(tg_poz(x, s=s, **kol))
    ayak_x = tg_eklemler(dur)["ayak1"][0]
    cok = tg_yerlestir(
        tg_poz(x, s=s, g=38, u1=82, b1=-30, u2=74, b2=-22, **dip_kol),
        ayak_x=ayak_x,
    )
    itis = tg_yerlestir(
        tg_poz(x, s=s, g=6, u1=8, b1=0, u2=4, b2=-2, a1=55, a2=50, **tepe_kol),
        ayak_x=ayak_x,
    )
    tepe = dict(itis, hy=dur["hy"] - yukselme, u1=4, b1=-2, u2=-4, b2=-6, a1=38, a2=34)
    inis = tg_yerlestir(
        tg_poz(x, s=s, g=28, u1=64, b1=-22, u2=56, b2=-16, **dip_kol),
        ayak_x=ayak_x,
    )
    e_tepe = tg_eklemler(tepe)
    ayaklar = ("ayak1", "ayak2", "parmak1", "parmak2")
    tepe_ayak_y = max(e_tepe[k][1] for k in ayaklar)
    an = [
        (0.0, dur),
        (0.12, dur),
        (0.32, cok),
        (0.44, itis),
        (0.62, tepe),
        (0.82, inis),
        (1.0, dur),
    ]
    return TgHareket(an, {"tepe_ayak_y": tepe_ayak_y, "kalca": e_tepe["kalca"]})


def _tam_sj_hareketi(x: float, yukselme: float = 19.0, s: float = 0.78) -> TgHareket:
    """Squat Jump (SJ): 90° diz açısında statik bekleme (0..0.38) -> ön çömelmesiz sıçrama (0.64) -> iniş."""
    kol = dict(k1=-44, o1=-16, k2=-30, o2=-4)
    dur = tg_yerlestir(tg_poz(x, s=s))
    ayak_x = tg_eklemler(dur)["ayak1"][0]
    statik_cok = tg_yerlestir(
        tg_poz(x, s=s, g=30, u1=74, b1=-24, u2=66, b2=-18, **kol),
        ayak_x=ayak_x,
    )
    itis = tg_yerlestir(
        tg_poz(x, s=s, g=5, u1=6, b1=0, u2=2, b2=-2, a1=52, a2=48, k1=-40, o1=50, k2=-22, o2=68),
        ayak_x=ayak_x,
    )
    tepe = dict(itis, hy=dur["hy"] - yukselme, a1=38, a2=34)
    inis = tg_yerlestir(
        tg_poz(x, s=s, g=24, u1=56, b1=-18, u2=48, b2=-14, **kol),
        ayak_x=ayak_x,
    )
    e_cok = tg_eklemler(statik_cok)
    an = [
        (0.0, statik_cok),
        (0.36, statik_cok),
        (0.46, itis),
        (0.64, tepe),
        (0.84, inis),
        (1.0, statik_cok),
    ]
    return TgHareket(an, {"diz": e_cok["diz1"], "kalca": e_cok["kalca"], "ayak": e_cok["ayak1"]})


def _tam_dj_hareketi(sol: float, sag: float, kutu_yuk: float, yukselme: float = 21.0, s: float = 0.75) -> TgHareket:
    """Drop Jump (DJ): 30 cm kutu üstünde -> öne adım ve düşüş -> kısa temas amortisman -> patlayıcı sıçrama -> iniş."""
    kol = dict(k1=-42, o1=52, k2=-22, o2=70)
    ust = TG_ZEMIN - kutu_yuk
    kutu_x = (sol + sag) / 2
    inis_x = sag + 22 * s

    uzerinde = tg_yerlestir(tg_poz(kutu_x, s=s, **kol), zemin=ust)
    adim = tg_yerlestir(tg_poz(sag + 4 * s, s=s, u1=26, b1=8, u2=-12, b2=-8, **kol), zemin=ust - 2)
    temas = tg_yerlestir(tg_poz(inis_x, s=s, g=32, u1=72, b1=-26, u2=64, b2=-20, k1=-50, o1=-20, k2=-36, o2=-10))
    itis = tg_yerlestir(tg_poz(inis_x, s=s, g=4, u1=6, b1=0, u2=2, b2=-2, a1=45, a2=40, **kol))
    normal_dur = tg_yerlestir(tg_poz(inis_x, s=s, **kol))
    tepe = dict(itis, hy=normal_dur["hy"] - yukselme, a1=36, a2=32)
    bitis = tg_yerlestir(tg_poz(inis_x, s=s, g=20, u1=48, b1=-16, u2=40, b2=-12, **kol))

    an = [
        (0.0, uzerinde),
        (0.16, uzerinde),
        (0.28, adim),
        (0.42, temas),
        (0.50, itis),
        (0.68, tepe),
        (0.88, bitis),
        (1.0, normal_dur),
    ]
    e0 = tg_eklemler(uzerinde)
    e_temas = tg_eklemler(temas)
    e_tepe = tg_eklemler(tepe)
    return TgHareket(
        an,
        {
            "dusus_yolu": (e0["ayak1"], e_temas["ayak1"], e_tepe["ayak1"]),
            "inis_x": inis_x,
            "tepe_y": max(e_tepe[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2")),
        },
    )


def sahne_cmj_tekli(baslik: str = "CMJ: eller kalçada, çök ve patlayıcı sıçra", notu: str = "3 deneme, en iyi yükseklik (cm)") -> TgSahne:
    """Tekli CMJ sahnesi (Dikey Sıçrama CMJ ve Badminton CMJ için gerçek sıçramalı sahne)."""
    S = TgSahne(2.8)
    S.esya(S.kutu(88, TG_ZEMIN - 3.5, 56, 3.5, dolgu="yuzey", rx=1))  # Kuvvet platformu
    h = _tam_cmj_hareketi(116, yukselme=24.0, s=0.80, eller_kalcada=True)
    S.figur(h)
    tepe_y = h.olay["tepe_ayak_y"]
    S.baslik(baslik)
    S.olcu(
        158,
        TG_ZEMIN,
        158,
        tepe_y,
        "CMJ yüksekliği (cm)",
        t=0.0,
        kilavuzlar=[(136, tepe_y, 158, tepe_y)],
    )
    S.isaret("Kuvvet platformu", (116, TG_ZEMIN - 2), (52, 86), hiza="end")
    S.not_(notu)
    return S


def sahne_cmj_sj_ikili(
    baslik: str = "Solda CMJ (ön-çömelmeli), sağda SJ (90° statik bekleme)",
    notu: str = "Eller kalçada · 3 deneme, en iyi sıçrama yüksekliği",
) -> TgSahne:
    """CMJ + SJ yan yana gerçek sıçrama karşılaştırması."""
    S = TgSahne(3.0)
    S.esya(S.kutu(48, TG_ZEMIN - 3, 46, 3, dolgu="yuzey", rx=1))
    S.esya(S.kutu(148, TG_ZEMIN - 3, 46, 3, dolgu="yuzey", rx=1))
    h_cmj = _tam_cmj_hareketi(70, yukselme=22.0, s=0.72, eller_kalcada=True)
    h_sj = _tam_sj_hareketi(170, yukselme=18.5, s=0.72)
    S.figur(h_cmj)
    S.figur(h_sj)
    S.baslik(baslik)
    S.isaret("CMJ (Ön çömelmeli)", (70, TG_ZEMIN - 3), (36, 34), hiza="start")
    S.isaret("SJ (2 sn 90° statik)", (170, TG_ZEMIN - 3), (152, 34), hiza="start")
    S.not_(notu)
    return S


def sahne_cmj_sj_dj_uclu(
    baslik: str = "Soldan: CMJ · SJ (90° statik) · DJ (30 cm kutudan reaktif sıçrama)",
    notu: str = "Eller kalçada · 3 deneme · RSI = Sıçrama Yüksekliği / Temas Süresi",
) -> TgSahne:
    """CMJ + SJ + DJ üçlü tam batarya gerçek sıçrama animasyonu."""
    S = TgSahne(3.2)
    S.esya(S.kutu(22, TG_ZEMIN - 3, 38, 3, dolgu="yuzey", rx=1))
    S.esya(S.kutu(88, TG_ZEMIN - 3, 38, 3, dolgu="yuzey", rx=1))
    S.esya(S.kutu(158, TG_ZEMIN - 16, 24, 16, rx=1.2))  # 30 cm DJ kutusu
    S.esya(S.kutu(186, TG_ZEMIN - 3, 42, 3, dolgu="yuzey", rx=1))
    h_cmj = _tam_cmj_hareketi(40, yukselme=20.0, s=0.66, eller_kalcada=True)
    h_sj = _tam_sj_hareketi(106, yukselme=17.0, s=0.66)
    h_dj = _tam_dj_hareketi(158, 182, 16.0, yukselme=21.0, s=0.66)
    S.figur(h_cmj)
    S.figur(h_sj)
    S.figur(h_dj)
    S.baslik(baslik)
    S.olcu(152, TG_ZEMIN, 152, TG_ZEMIN - 16, "30 cm", etiket_yer="sol")
    S.not_(notu)
    return S


def sahne_boy_kilo_canli() -> TgSahne:
    """Boy ve Vücut Ağırlığı (TSYT) — Canlı tartı ve stadiometre ölçüm animasyonu."""
    S = TgSahne(3.0)
    S.esya(S.kutu(86, 21, 5, TG_ZEMIN - 21, rx=1) + "".join(S.cizgi(91, y, 94, y) for y in range(30, TG_ZEMIN, 8)))
    S.esya(S.kutu(94, TG_ZEMIN - 4, 42, 4, dolgu="yuzey", rx=1))
    # Dijital tartı ekranı
    S.esya(S.cizgi(136, TG_ZEMIN - 2, 146, TG_ZEMIN - 26) + S.kutu(140, TG_ZEMIN - 36, 18, 10, dolgu="yuzey", rx=1.5))

    p_adim = tg_yerlestir(tg_poz(98, s=0.95, g=6, u1=16, b1=-8, u2=-12, b2=-18, k1=18, o1=30, k2=-12, o2=14))
    p_dik = tg_yerlestir(tg_poz(106, s=0.95, g=0, u1=4, b1=0, u2=-4, b2=0, k1=6, o1=4, k2=-6, o2=-4))
    p_nefes = dict(p_dik, hy=p_dik["hy"] - 1.5, k1=8, o1=6)
    an = [(0.0, p_adim), (0.28, p_dik), (0.55, p_nefes), (1.0, p_nefes)]
    e = S.figur(TgHareket(an, {}))
    ust = e["bas_ust"][1]
    S.kaydir(
        S.cizgi(86, ust - 1.5, 124, ust - 1.5, tur="vurgu"),
        [(0.0, 0, -12), (0.30, 0, -12), (0.60, 0, 0), (1.0, 0, 0)],
    )
    S.baslik("Topuk, kalça, sırt ve baş Frankfurt düzleminde dik")
    S.olcu(168, TG_ZEMIN, 168, ust, "Boy (cm)", kilavuzlar=[(124, ust, 168, ust)])
    S.isaret("Tartı (0,1 kg)", (149, TG_ZEMIN - 31), (186, 82), hiza="start")
    S.not_("Derin nefes alıp tutarken boy (0,1 cm) ve ağırlık (0,1 kg) ölçülür")
    return S


def sahne_oturma_yuksekligi_canli(baslik: str = "Dizler 90°, sırt dik, Frankfurt düzlemi", notu: str = "Oturma yüzeyinden başın en üst noktasına (cm)") -> TgSahne:
    """Oturma Yüksekliği — Canlı oturuş hizalama ve antropometrik başlık animasyonu."""
    S = TgSahne(2.8)
    oturak = TG_ZEMIN - 23
    S.esya(S.kutu(60, oturak, 32, TG_ZEMIN - oturak, rx=1))
    S.esya(S.kutu(54, 21, 4, TG_ZEMIN - 21, rx=1) + "".join(S.cizgi(58, y, 61, y) for y in range(28, TG_ZEMIN, 8)))
    p_rahat = tg_poz(72, s=0.95, hy=oturak, g=14, u1=90, b1=0, u2=84, b2=-6, k1=28, o1=72, k2=20, o2=62)
    p_dik = tg_poz(70, s=0.95, hy=oturak, g=0, u1=90, b1=0, u2=84, b2=-6, k1=22, o1=62, k2=16, o2=54)
    p_nefes = dict(p_dik, hy=oturak - 1.2)
    e = S.figur(TgHareket([(0.0, p_rahat), (0.35, p_dik), (0.62, p_nefes), (1.0, p_nefes)], {}))
    ust = e["bas_ust"][1]
    S.kaydir(
        S.cizgi(54, ust - 1.5, 92, ust - 1.5, tur="vurgu"),
        [(0.0, 0, -11), (0.35, 0, -11), (0.65, 0, 0), (1.0, 0, 0)],
    )
    S.baslik(baslik)
    S.olcu(
        132,
        oturak,
        132,
        ust,
        "Oturma yüksekliği (cm)",
        kilavuzlar=[(92, oturak, 132, oturak), (92, ust, 132, ust)],
    )
    S.not_(notu)
    return S


def sahne_top_sektirme_canli() -> TgSahne:
    """Top Sektirme — Alternatif El (BOT-2): Canlı sağ-sol el ve diz ritimli top sektirme."""
    S = TgSahne(3.4)
    x = 156
    s = 0.85
    p_sol = tg_yerlestir(
        tg_poz(x, s=s, cephe=True, g=8, u1=12, b1=-6, u2=-12, b2=6, a1=90, a2=-90, k1=34, o1=88, k2=-22, o2=-42)
    )
    p_orta = tg_yerlestir(
        tg_poz(x, s=s, cephe=True, g=14, u1=22, b1=-12, u2=-22, b2=12, a1=90, a2=-90, k1=24, o1=52, k2=-24, o2=-52)
    )
    p_sag = tg_yerlestir(
        tg_poz(x, s=s, cephe=True, g=8, u1=12, b1=-6, u2=-12, b2=6, a1=90, a2=-90, k1=22, o1=42, k2=-34, o2=-88)
    )
    an = [
        (0.0, p_sol),
        (0.16, p_orta),
        (0.33, p_sag),
        (0.50, p_orta),
        (0.66, p_sol),
        (0.83, p_orta),
        (1.0, p_sag),
    ]
    S.figur(TgHareket(an, {}))
    e_sol = tg_eklemler(p_sol)["el1"]
    e_sag = tg_eklemler(p_sag)["el2"]
    orta_x = (e_sol[0] + e_sag[0]) / 2
    top_yolu = [
        (0.0, e_sol[0], e_sol[1] + 2),
        (0.16, orta_x, TG_ZEMIN - 3),
        (0.33, e_sag[0], e_sag[1] + 2),
        (0.50, orta_x, TG_ZEMIN - 3),
        (0.66, e_sol[0], e_sol[1] + 2),
        (0.83, orta_x, TG_ZEMIN - 3),
        (1.0, e_sag[0], e_sag[1] + 2),
    ]
    S.top(top_yolu, r=2.8)
    sx0, sy0, sx1, sy1 = S.sayac(16, 40, [0.16, 0.50, 0.83])
    S.baslik("Bir elle sektir, öbür elle karşıla (alternatif el)")
    S.isaret("10 ardışık sektirme", (sx1, (sy0 + sy1) / 2), (sx1 + 10, 62), hiza="start")
    S.not_("Tenis topu · 2 deneme, en yüksek doğru sektirme (0–10)")
    return S


# ════════════════════════════════════════════════════════════════════════════
# 28 GÖRSELSİZ TEST İÇİN ÖZEL BİYOMEKANİK VE LABORATUVAR SAHNELERİ
# ════════════════════════════════════════════════════════════════════════════

def sahne_deri_kivrimi(test_adi: str) -> TgSahne:
    """Vücut Kompozisyonu — Deri Kıvrımı (Kaliper): Kaliper ile triceps/subskapular ölçüm + kaliper kadranı."""
    S = TgSahne(3.4)
    s = 0.86 if "PREFIT" not in test_adi and "Latorre" not in test_adi else 0.72
    # Ölçülen sporcu
    p0 = tg_yerlestir(tg_poz(116, s=s, g=0, k1=8, o1=12, k2=-6, o2=-4))
    p1 = tg_yerlestir(tg_poz(116, s=s, g=0, k1=-12, o1=22, k2=-6, o2=-4))
    S.figur(TgHareket([(0.0, p0), (0.3, p1), (0.7, p1), (1.0, p0)], {}))

    # Antropometrist (Uygulayıcı partner)
    u0 = tg_yerlestir(tg_poz(74, s=0.88, yon=1, g=8, k1=40, o1=85, k2=30, o2=70))
    u1 = tg_yerlestir(tg_poz(78, s=0.88, yon=1, g=14, k1=68, o1=110, k2=52, o2=95))
    S.figur(TgHareket([(0.0, u0), (0.35, u1), (0.75, u1), (1.0, u0)], {"rol": "partner"}))

    # Sağ tarafta büyütülmüş Harpenden Kaliper Kadranı & Deri Kıvrımı Şeması
    S.esya(S.kutu(166, 32, 78, 56, dolgu="yuzey", rx=3))
    S.esya(f'<circle cx="205" cy="56" r="14" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["olcu"]}" stroke-width="1.4"/>')
    ibre = S.cizgi(205, 56, 205, 44, "olcu")
    S.ogeler.append((
        f'<g><animateTransform attributeName="transform" type="rotate" values="0 205 56;115 205 56;115 205 56;0 205 56" '
        f'keyTimes="0;0.4;0.8;1" dur="{S.sure}s" repeatCount="indefinite"/>{ibre}</g>',
        ibre,
    ))
    S.baslik(f"{test_adi} — Kaliper ile Deri Altı Yağ Ölçümü")
    S.isaret("Triceps & Subskapular (mm)", (112, 64), (166, 98), hiza="start")
    S.not_("10 g/mm² sabit basınçlı kaliper · Siri / Slaughter vücut yağ % denklemi")
    return S


def sahne_bel_cevresi_vki() -> TgSahne:
    """Bel Çevresi ve VKİ: Antropometrik mezura ile umbilikus çevresi ve dijital VKİ platformu."""
    S = TgSahne(3.2)
    S.esya(S.kutu(92, TG_ZEMIN - 4, 56, 4, dolgu="yuzey", rx=1))
    p0 = tg_yerlestir(tg_poz(120, s=0.88, cephe=True, u1=6, b1=4, u2=-6, b2=-4, a1=90, a2=-90, k1=22, o1=20, k2=-22, o2=-20))
    p1 = tg_yerlestir(tg_poz(120, s=0.88, cephe=True, u1=6, b1=4, u2=-6, b2=-4, a1=90, a2=-90, k1=48, o1=44, k2=-48, o2=-44))
    e = S.figur(TgHareket([(0.0, p0), (0.3, p1), (0.75, p1), (1.0, p0)], {}))
    kx, ky = e["kalca"]
    # Bel mezurası halkası
    S.esya(f'<ellipse cx="{kx:.1f}" cy="{ky - 8:.1f}" rx="11" ry="3.2" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="2.0"/>')
    S.olcu(68, TG_ZEMIN, 68, e["bas_ust"][1], "Boy (m)")
    S.isaret("Bel Çevresi (cm) ·Bel/Boy < 0,5", (kx + 11, ky - 8), (154, 62), hiza="start")
    S.baslik("Bel Çevresi (Mezura) ve Vücut Kütle İndeksi (kg/m²)")
    S.not_("Mezura son kostanın altı ile krista iliaka ortasından yatay sarılır")
    return S


def sahne_dexa_tarama() -> TgSahne:
    """DEXA (Dual-Energy X-ray Absorptiometry): Yatar pozisyonda C-kol X-ışını tarayıcı ve 3-bölmeli doku haritası."""
    S = TgSahne(3.8)
    yatak_y = TG_ZEMIN - 22
    # DEXA Yatağı
    S.esya(S.kutu(36, yatak_y, 146, 5, dolgu="yuzey", rx=1.5) + S.kutu(46, yatak_y + 5, 8, 17) + S.kutu(164, yatak_y + 5, 8, 17))
    # Yatağa uzanan ve taranan sporcu
    p_otur = dict(tg_poz(96, s=0.82, g=55, u1=-15, b1=-5, u2=-10, b2=-2, a1=45, a2=45, k1=18, o1=28, k2=10, o2=20), hy=yatak_y - 5)
    p_yat = dict(tg_poz(96, s=0.82, g=90, u1=0, b1=0, u2=2, b2=2, a1=10, a2=12, k1=4, o1=4, k2=-2, o2=-2), hy=yatak_y - 4)
    S.figur(TgHareket([(0.0, p_otur), (0.18, p_yat), (0.88, p_yat), (1.0, p_otur)], {}))
    # C-Kol Tarayıcı Başlık + X-Işını Hüzmesi (Baştan ayağa kayar)
    tarayici_xml = (
        S.cizgi(60, yatak_y, 60, 28, "esya")
        + S.cizgi(60, 28, 82, 28, "esya")
        + S.kutu(72, 26, 14, 5, dolgu="yuzey", rx=1)
        + f'<path d="M79,31 L65,{yatak_y:.1f} L93,{yatak_y:.1f} Z" fill="{TG_RENK["olcu"]}" fill-opacity="0.22" stroke="{TG_RENK["olcu"]}" stroke-width="0.8" stroke-dasharray="2 2"/>'
    )
    S.kaydir(tarayici_xml, [(0.0, 0, 0), (0.5, 84, 0), (1.0, 0, 0)])
    # Sağda DEXA Konsol Ekranı (BMC / LBM / Fat %)
    S.esya(S.kutu(194, 30, 54, 62, dolgu="yuzey", rx=2.5))
    S.esya(S.kutu(200, 42, 42, 8, rx=1) + S.kutu(200, 56, 34, 8, rx=1) + S.kutu(200, 70, 22, 8, rx=1))
    S.baslik("DEXA — Çift Enerjili X-Işını Tüm Vücut Tarama")
    S.isaret("Kemik · Kas · Yağ %", (194, 58), (150, 40), hiza="end")
    S.not_("3 bölmeli altın standart: Kemik mineral yoğunluğu (BMD), yağsız doku ve yağ %")
    return S


def sahne_bia_analiz() -> TgSahne:
    """Biyoelektrik İmpedans Analizi (BIA): 8 elektrotlu tetrapolar platform ve 50 kHz empedans dalgası."""
    S = TgSahne(3.2)
    # BIA Platformu ve Konsolu
    S.esya(S.kutu(86, TG_ZEMIN - 5, 56, 5, dolgu="yuzey", rx=1.5))
    S.esya(S.cizgi(114, TG_ZEMIN - 5, 114, 42) + S.kutu(100, 32, 28, 14, dolgu="yuzey", rx=2))
    p0 = tg_yerlestir(tg_poz(114, s=0.86, cephe=True, u1=8, b1=6, u2=-8, b2=-6, a1=90, a2=-90, k1=32, o1=40, k2=-32, o2=-40), zemin=TG_ZEMIN - 5)
    p1 = dict(p0, k1=38, o1=48, k2=-38, o2=-48)
    e = S.figur(TgHareket([(0.0, p0), (0.5, p1), (1.0, p0)], {}))
    # El elektrot kabloları
    el1, el2 = e["el1"], e["el2"]
    S.esya(S.cizgi(100, 40, el2[0], el2[1], "olcu", kesik=True) + S.cizgi(128, 40, el1[0], el1[1], "olcu", kesik=True))
    # Sağda Empedans / Toplam Vücut Suyu (TBW) grafiği
    S.esya(S.kutu(166, 36, 78, 52, dolgu="yuzey", rx=2.5))
    S.esya(f'<path d="M174,64 Q186,44 198,64 T222,64 T238,64" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="1.6"/>')
    S.baslik("Tetrapolar Biyoelektrik İmpedans Analizi (BIA — 50 kHz)")
    S.isaret("El & Ayak Elektrotları (Ω)", (el1[0], el1[1]), (166, 98), hiza="start")
    S.not_("Aç karnına ve hidrasyon dengesinde · Empedans (Ω) → TBW, FFM ve Yağ %")
    return S


def sahne_hidrostatik_tartim() -> TgSahne:
    """Hidrostatik Tartım (Su Altı Tartımı): Su tankı, askılı tartı koltuğu, tam dalış ve Archimedes yoğunluğu."""
    S = TgSahne(3.8)
    su_y = 58
    # Su tankı ve su yüzeyi
    S.esya(f'<rect x="64" y="{su_y}" width="112" height="{TG_ZEMIN - su_y}" fill="{TG_RENK["dolgu"]}" fill-opacity="0.32" stroke="{TG_RENK["esya"]}" stroke-width="1.5"/>')
    S.esya(S.cizgi(64, su_y, 176, su_y, "olcu"))
    # Üst kantar kadranı
    S.esya(S.cizgi(120, 18, 120, 32) + f'<circle cx="120" cy="36" r="8" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["olcu"]}" stroke-width="1.4"/>')

    p_ust = tg_poz(116, s=0.76, hy=su_y + 22, g=10, u1=85, b1=-5, u2=80, b2=-8, k1=25, o1=65, k2=18, o2=55)
    p_dal = tg_poz(116, s=0.76, hy=su_y + 34, g=48, u1=92, b1=-12, u2=86, b2=-16, k1=40, o1=85, k2=32, o2=75)
    S.figur(TgHareket([(0.0, p_ust), (0.35, p_dal), (0.80, p_dal), (1.0, p_ust)], {}))
    # Askı koltuğu
    S.kaydir(
        S.cizgi(120, 44, 120, su_y + 24, "esya") + S.cizgi(104, su_y + 24, 132, su_y + 24, "vurgu"),
        [(0.0, 0, 0), (0.35, 0, 12), (0.80, 0, 12), (1.0, 0, 0)],
    )
    # Hava kabarcıkları (Ekshalasyon)
    S.top([(0.0, 132, su_y + 18), (0.35, 134, su_y + 14), (0.85, 138, su_y - 2), (1.0, 138, su_y - 4)], r=2.0)
    S.baslik("Hidrostatik Tartım — Maksimal Ekshalasyonla Su Altı Tartımı")
    S.isaret("Su altı ağırlığı (Archimedes)", (128, 36), (184, 42), hiza="start")
    S.not_("Vücut Yoğunluğu Db = Wa / [((Wa − Ww)/Dw) − (RV + 0,1 L)] → Siri Denklemi")
    return S


def sahne_vo2max_ergospirometri() -> TgSahne:
    """VO2max Direkt Ölçüm (Ergospirometri): Koşu bandı, metabolik gaz maskesi ve canlı VO2/VCO2 eğrisi."""
    S = TgSahne(3.2)
    # Koşu bandı (Treadmill)
    S.esya(
        S.kutu(32, TG_ZEMIN - 6, 108, 6, dolgu="yuzey", rx=2)
        + S.cizgi(124, TG_ZEMIN - 6, 134, 54, "esya")
        + S.kutu(128, 44, 16, 12, dolgu="yuzey", rx=1.5)
    )
    # Koşu bandında koşan sporcu
    p1 = tg_yerlestir(tg_poz(78, s=0.82, g=14, u1=36, b1=-4, u2=-30, b2=-76, k1=-34, o1=46, k2=40, o2=110), zemin=TG_ZEMIN - 6)
    p2 = tg_yerlestir(tg_poz(78, s=0.82, g=14, u1=-30, b1=-76, u2=36, b2=-4, k1=40, o1=110, k2=-34, o2=46), zemin=TG_ZEMIN - 6)
    an = [(i / 6, p1 if i % 2 == 0 else p2) for i in range(7)]
    e = S.figur(TgHareket(an, {}))
    # Metabolik gaz analizör hortumu ve VO2max grafik ekranı
    bx, by = e["bas"]
    S.esya(S.cizgi(bx + 5, by, 134, 48, "olcu", kesik=True))
    S.esya(S.kutu(158, 28, 88, 64, dolgu="yuzey", rx=3))
    S.esya(
        S.cizgi(166, 82, 238, 82, "kilavuz")
        + S.cizgi(166, 82, 166, 36, "kilavuz")
        + f'<path d="M166,78 Q186,62 204,46 L236,44" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="2.0"/>'
    )
    S.baslik("Ergospirometri — Nefes Nefese (Breath-by-Breath) VO2max")
    S.isaret("VO2 Platosu (ml/kg/dk)", (220, 44), (166, 102), hiza="start")
    S.not_("RER ≥ 1,10 · VO2 platosu · KAH ≥ %95 maks · Borg RPE ≥ 19")
    return S


def sahne_laktat_esigi() -> TgSahne:
    """Laktat Eşiği Testi: Kademeli koşu bandı + kan laktat (4 mmol/L OBLA) üstel eğrisi."""
    S = TgSahne(3.4)
    S.esya(S.kutu(28, TG_ZEMIN - 6, 98, 6, dolgu="yuzey", rx=2) + S.cizgi(114, TG_ZEMIN - 6, 122, 56, "esya"))
    p1 = tg_yerlestir(tg_poz(72, s=0.80, g=12, u1=34, b1=-4, u2=-28, b2=-72, k1=-32, o1=44, k2=38, o2=106), zemin=TG_ZEMIN - 6)
    p2 = tg_yerlestir(tg_poz(72, s=0.80, g=12, u1=-28, b1=-72, u2=34, b2=-4, k1=38, o1=106, k2=-32, o2=44), zemin=TG_ZEMIN - 6)
    S.figur(TgHareket([(i / 6, p1 if i % 2 == 0 else p2) for i in range(7)], {}))
    # Sağda Laktat-Hız Eğrisi (LT1 = 2 mmol/L, LT2/OBLA = 4 mmol/L)
    S.esya(S.kutu(144, 26, 102, 68, dolgu="yuzey", rx=3))
    S.esya(
        S.cizgi(154, 84, 238, 84, "kilavuz")
        + S.cizgi(154, 84, 154, 34, "kilavuz")
        + S.cizgi(154, 54, 238, 54, "olcu", kesik=True)  # 4 mmol/L OBLA eşik çizgisi
        + f'<path d="M156,80 L176,77 L196,70 L214,54 L234,36" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="2.0"/>'
    )
    for px, py in ((156, 80), (176, 77), (196, 70), (214, 54), (234, 36)):
        S.esya(S.nokta(px, py, 2.0, dolu=True))
    S.baslik("Kademeli Laktat Eşiği Testi (LT1: 2 mmol/L · OBLA: 4 mmol/L)")
    S.isaret("4,0 mmol/L Eşik Hızı", (214, 54), (148, 104), hiza="start")
    S.not_("3–5 dk kademeler · Kulak memesi/parmaktan kapiller kan laktatı (mmol/L) ve KAH")
    return S


def sahne_cpet_kardiyo() -> TgSahne:
    """Kardiyopulmoner Egzersiz Testi (CPET): 12 derivasyonlu EKG + bisiklet ergometresi + EKG dalgası."""
    S = TgSahne(3.2)
    from olcut.gorseller.hareketler import hk_pedal
    h = hk_pedal(76, s=0.82, tur=5)
    o = h.olay
    (cx, cy), (sx, sy), (gx, gy) = o["krank"], o["sele"], o["gidon"]
    volan = (cx + 30, cy - 5)
    S.esya(
        S.cizgi(cx - 28, TG_ZEMIN - 2, cx + 44, TG_ZEMIN - 2)
        + S.cizgi(cx - 22, TG_ZEMIN - 2, sx - 2, sy + 4)
        + S.cizgi(cx, cy, volan[0], volan[1])
        + S.cizgi(sx + 2, sy + 10, gx, gy + 16)
        + S.cizgi(gx, gy + 16, gx, gy)
        + f'<circle cx="{volan[0]:.1f}" cy="{volan[1]:.1f}" r="11" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="1.8"/>'
    )
    S.figur(h)
    # Sağda 12-Lead EKG QRS Monitörü & Wasserman Paneli
    S.esya(S.kutu(144, 28, 102, 62, dolgu="yuzey", rx=3))
    ekg_d = "M150,58 L164,58 L168,52 L172,62 L176,38 L180,70 L184,54 L190,58 L204,58 L208,38 L212,70 L216,58 L238,58"
    S.esya(f'<path d="{ekg_d}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="1.7"/>')
    S.baslik("CPET — 12 Derivasyonlu EKG, Spirometri ve Gaz Değişimi")
    S.isaret("EKG · VE/VCO2 · O2 Nabzı", (180, 38), (148, 102), hiza="start")
    S.not_("Rampa protokolü · Ventilatuvar eşik (VT1/VT2), O2 nabzı ve kardiyopulmoner yanıt")
    return S


def sahne_izokinetik_kuvvet() -> TgSahne:
    """İzokinetik Kuvvet Testi: Biodex dinamometre koltuğu ve Tork-Açı (Nm) eğrisi."""
    S = TgSahne(3.6)
    from olcut.gorseller.hareketler import hk_dinamometre
    kx, ky = 78, TG_ZEMIN - 44
    h = hk_dinamometre(kx, ky)
    dx, dy = h.olay["diz"]
    S.esya(
        S.kutu(50, ky + 3, 36, 5, rx=1)
        + S.cizgi(56, ky + 8, 56, TG_ZEMIN)
        + S.cizgi(82, ky + 8, 82, TG_ZEMIN)
        + S.cizgi(52, ky + 3, 44, ky - 36)
        + f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="6.5" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["olcu"]}" stroke-width="1.8"/>'
    )
    S.cubuk(dx, dy, h.olay["ayak_yolu"])
    S.figur(h)
    # Sağda Tork-Açı (60°/sn & 180°/sn) Grafiği
    S.esya(S.kutu(148, 28, 98, 62, dolgu="yuzey", rx=3))
    S.esya(
        S.cizgi(156, 80, 238, 80, "kilavuz")
        + f'<path d="M158,78 Q198,32 236,78" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="2.0"/>'
        + f'<path d="M158,78 Q198,50 236,78" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="1.5" stroke-dasharray="3 2"/>'
    )
    S.baslik("İzokinetik Dinamometre — Kuadriseps / Hamstring Pik Tork (Nm)")
    S.isaret("60°/sn & 180°/sn Tork Eğrisi", (198, 42), (148, 102), hiza="start")
    S.not_("Konsantrik/eksantrik pik tork (Nm/kg), H/Q oranı ve bilateral asimetri (%)")
    return S


def sahne_force_velocity_profili() -> TgSahne:
    """Force-Velocity Profili (F-V): Yüklü Squat Jump + Lineer Transdüser ve F0-V0-Pmax doğrusu."""
    S = TgSahne(3.2)
    S.esya(S.kutu(56, TG_ZEMIN - 3.5, 48, 3.5, dolgu="yuzey", rx=1))
    h = _tam_cmj_hareketi(80, yukselme=18.0, s=0.78, eller_kalcada=False)
    S.figur(h)
    # Sağda Samozino F-V ve Güç (Pmax) Parabolü
    S.esya(S.kutu(142, 26, 104, 66, dolgu="yuzey", rx=3))
    S.esya(
        S.cizgi(152, 82, 238, 82, "kilavuz")
        + S.cizgi(152, 82, 152, 34, "kilavuz")
        + S.cizgi(154, 38, 234, 80, "olcu")  # F-V doğrusu (F0 -> V0)
        + f'<path d="M154,80 Q194,34 234,80" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="1.5" stroke-dasharray="2 2"/>'
    )
    S.baslik("Force–Velocity (Kuvvet–Hız) Profili: F0, V0, Pmax ve Sfv")
    S.isaret("F0 – V0 Regresyonu & Pmax", (194, 58), (144, 102), hiza="start")
    S.not_("En az 3 farklı dış yükte sıçrama veya sprint · Kuvvet/Hız dengesizliği (FVimb %)")
    return S


def sahne_emg_kas_aktivasyonu() -> TgSahne:
    """EMG Tabanlı Kas Aktivasyonu: Kablosuz sEMG elektrotları ve canlı ham/RMS elektromiyografi sinyali."""
    S = TgSahne(3.2)
    h = _tam_cmj_hareketi(76, yukselme=16.0, s=0.80, eller_kalcada=True)
    S.figur(h)
    # Sağda 2 Kanallı sEMG Osiloskop ve %MVC RMS Zarfı
    S.esya(S.kutu(136, 26, 110, 66, dolgu="yuzey", rx=3))
    emg_raw = "M144,58 L150,58 L154,42 L158,74 L162,36 L166,78 L170,40 L174,72 L178,46 L182,68 L190,58 L238,58"
    S.esya(
        f'<path d="{emg_raw}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="1.5"/>'
        + f'<path d="M144,58 Q166,30 190,58 L238,58" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="1.8" stroke-dasharray="3 2"/>'
    )
    S.baslik("Yüzey Elektromiyografisi (sEMG) — Kas Aktivasyonu (%MVC)")
    S.isaret("SENIAM Elektrot · RMS %MVC", (166, 40), (138, 102), hiza="start")
    S.not_("1000–2000 Hz örnekleme · 20–450 Hz bant geçiren filtre · RMS (%MVC) ve ateşleme zamanı")
    return S


def sahne_rfd_imtp() -> TgSahne:
    """Rate of Force Development (RFD): İzometrik Mid-Thigh Pull (IMTP) kafesi ve ΔF/Δt eğimi."""
    S = TgSahne(3.2)
    # IMTP Güç Kafesi ve Kuvvet Platformu
    S.esya(
        S.kutu(54, TG_ZEMIN - 4, 52, 4, dolgu="yuzey", rx=1)
        + S.cizgi(62, TG_ZEMIN - 4, 62, 24, "esya")
        + S.cizgi(98, TG_ZEMIN - 4, 98, 24, "esya")
        + S.cizgi(58, 78, 102, 78, "vurgu")  # Sabit IMTP barı
    )
    p0 = tg_yerlestir(tg_poz(80, s=0.82, g=18, u1=42, b1=-18, u2=36, b2=-14, k1=12, o1=16, k2=8, o2=12), zemin=TG_ZEMIN - 4)
    p1 = tg_yerlestir(tg_poz(80, s=0.82, g=14, u1=38, b1=-14, u2=32, b2=-10, k1=10, o1=14, k2=6, o2=10), zemin=TG_ZEMIN - 4)
    S.figur(TgHareket([(0.0, p0), (0.25, p1), (0.80, p1), (1.0, p0)], {}))
    # Sağda Kuvvet-Zaman (F-t) ve RFD (0–200 ms) Eğrisi
    S.esya(S.kutu(138, 26, 108, 66, dolgu="yuzey", rx=3))
    S.esya(
        S.cizgi(148, 82, 238, 82, "kilavuz")
        + S.cizgi(148, 82, 148, 34, "kilavuz")
        + f'<path d="M148,80 L158,80 C164,42 178,38 234,38" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="2.2"/>'
        + S.cizgi(158, 80, 176, 36, "esya", kesik=True)  # ΔF/Δt teğet eğimi
    )
    S.baslik("Rate of Force Development (RFD = ΔF / Δt) — Patlayıcı Kuvvet Hızı")
    S.isaret("0–50 / 100 / 200 ms RFD (N/sn)", (172, 42), (140, 102), hiza="start")
    S.not_("En az 1000 Hz kuvvet platformu · 'Mümkün olduğunca hızlı ve güçlü çek!' komutu")
    return S


def sahne_capl_adim_sayisi() -> TgSahne:
    """CAPL Günlük Adım Sayısı: Belde pedometre/akselerometre ile yürüyüş ve 7 günlük adım grafiği."""
    S = TgSahne(3.4)
    from olcut.gorseller.hareketler import hk_duz_kos
    h = hk_duz_kos(28, 128, s=0.78, cikis_t=0.02)
    S.figur(h)
    # Sağda 7 Günlük Pedometre Adım Grafiği (12.000 adım hedef çizgisi)
    S.esya(S.kutu(148, 26, 98, 64, dolgu="yuzey", rx=3))
    yukler = (28, 36, 42, 32, 46, 40, 44)
    for i, bh in enumerate(yukler):
        bx = 156 + i * 11.5
        S.esya(S.kutu(bx, 82 - bh, 7.5, bh, rx=1))
    S.esya(S.cizgi(152, 44, 242, 44, "olcu", kesik=True))
    S.baslik("CAPL-2 — Pedometre ile 7 Günlük Fiziksel Aktivite (Adım/Gün)")
    S.isaret("Hedef: ≥ 12.000 adım/gün", (196, 44), (148, 102), hiza="start")
    S.not_("Kalça üstü pedometre · En az 4 geçerli gün (günde ≥ 10 saat kullanım) ortalaması")
    return S


def sahne_capl_motivasyon_anketi() -> TgSahne:
    """CAPL Motivasyon ve Güven Anketi (CSAPPA): Fiziksel okuryazarlık öz-değerlendirme profili."""
    S = TgSahne(3.0)
    p0 = tg_yerlestir(tg_poz(74, s=0.86, g=0, k1=34, o1=82, k2=26, o2=72))
    p1 = tg_yerlestir(tg_poz(74, s=0.86, g=0, k1=42, o1=96, k2=26, o2=72))
    S.figur(TgHareket([(0.0, p0), (0.5, p1), (1.0, p0)], {}))
    # Sağda 4 Alt Boyut Puan Kartı (30 puan üzerinden)
    S.esya(S.kutu(132, 26, 114, 66, dolgu="yuzey", rx=3))
    for i, w_bar in enumerate((76, 84, 68, 88)):
        by = 36 + i * 13
        S.esya(S.kutu(142, by, w_bar, 7, rx=1.5))
    S.baslik("CAPL-2 — Motivasyon ve Özgüven Ölçeği (Toplam 30 Puan)")
    S.isaret("Yatkınlık · Yeterlilik · Motivasyon", (180, 56), (134, 102), hiza="start")
    S.not_("4 alt boyut × 7,5 puan = 30 puan · Fiziksel okuryazarlık duyuşsal alanı")
    return S


def sahne_coklu_batarya(test_adi: str) -> TgSahne:
    """Çok bileşenli branş bataryaları için branşa özgü kombine biyomekanik sahne."""
    ad_k = test_adi.lower()
    if "judo" in ad_k:
        from olcut.gorseller.sahneler import _tg_sjft_judo
        S = _tg_sjft_judo()
        S.baslik("Judo Fiziksel Uygunluk Bataryası (JPFT — Judogi Barfiks & Atış)")
        return S
    if "mma" in ad_k:
        from olcut.gorseller.sahneler import _tg_vurus
        return _tg_vurus(
            ("jab", "cross", "knee", "roundhouse"),
            "MMA Fiziksel Uygunluk Bataryası — Sprawl, Güç ve Darbe Serisi",
            "Kuvvet (1RM) + Anaerobik Güç (CMJ/Wingate) + Kafes Kondisyonu",
            "Kombine Performans",
            [(3, True), (1, False), (3, True), (1, False), (3, True)],
            7.0,
            "torba",
        )
    if "kuru kara" in ad_k or "dry-land" in ad_k:
        from olcut.gorseller.sahneler import _tg_kayak_ergometre
        return _tg_kayak_ergometre(
            "Yüzme Kuru Kara (Dry-Land) — Swim-Bench Ergometre & Çekiş Gücü",
            "Üst gövde çekiş gücü (W), sağlık topu fırlatma, CMJ ve omuz esnekliği",
        )
    if "jimnastik" in ad_k or "gft" in ad_k:
        from olcut.gorseller.sahneler import _tg_barfiks
        return _tg_barfiks(
            "Jimnastik Fiziksel Uygunluk Bataryası (GFT — Barfiks, L-Sit & Sıçrama)",
            "Üst gövde çekiş + kor dayanıklılığı + patlayıcı sıçrama ve esneklik",
        )
    if "badminton" in ad_k or "bat" in ad_k:
        from olcut.gorseller.sahneler import _tg_parkur
        return _tg_parkur(
            "spider",
            "Badminton Spesifik Çeviklik Testi (BAT — Merkezden 6 Köşeye Raket Hamlesi)",
            "Merkez üsten 4 köşe + 2 yan kenara raketle uzanma · Fotosel süresi (sn)",
            "Merkez Üs",
        )
    if "nfl combine" in ad_k:
        from olcut.gorseller.sahneler import _tg_sprint
        return _tg_sprint(
            "40 yd (36,6 m)",
            "NFL Combine — 40 Yard Dash (10/20/40 yd Split) & 3-Cone Bataryası",
            "3 nokta çıkış duruşu · Lazer fotosel 10, 20 ve 40 yarda süreleri",
            3,
            blok=True,
        )
    if "nhl" in ad_k or "off-ice" in ad_k:
        from olcut.gorseller.sahneler import _tg_yana_sicrama
        return _tg_yana_sicrama(
            "NHL Off-Ice Combine — Slideboard Yanal Kayma, CMJ & Wingate Güç",
            "Kaygan zeminde yanal paten adımı + Dikey sıçrama + 30 sn Wingate",
            "Çoklu istasyon: patlayıcı bacak gücü ve anaerobik kapasite",
        )
    if "rugby" in ad_k:
        from olcut.gorseller.sahneler import _tg_rsa
        S = _tg_rsa()
        S.baslik(f"{test_adi} — Tekrarlı Sprint, Temas ve Mekik Dayanıklılığı")
        return S
    # Atletik Güç Testi Bataryası vb.
    from olcut.gorseller.sahneler import _tg_saglik_topu
    S = _tg_saglik_topu()
    S.baslik(f"{test_adi} — Patlayıcı Atış, Dikey/Yatay Sıçrama ve Sprint Gücü")
    return S


OZEL_SAHNE_HARITASI: dict[str, Callable[[], TgSahne]] = {
    # 1. Tam döngülü dikey sıçrama sahneleri (hareketsiz/yarım kalan CMJ/SJ/DJ düzeltmesi)
    "Dikey Sıçrama (CMJ)": lambda: sahne_cmj_tekli("Dikey Sıçrama (CMJ) — Eller Kalçada Ön-Çömelmeli Sıçrama", "3 deneme · Kuvvet platformu veya temas matı ile en iyi yükseklik (cm)"),
    "CMJ (Badminton)": lambda: sahne_cmj_tekli("Badminton CMJ — Eller Kalçada Patlayıcı Dikey Sıçrama", "3 deneme · Alt ekstremite patlayıcı gücü ve sıçrama yüksekliği (cm)"),
    "Dikey Sıçrama - Basketbol (CMJ + SJ)": lambda: sahne_cmj_sj_ikili("Basketbol Dikey Sıçrama — CMJ (Sol) ve SJ 2 sn Statik (Sağ)", "Eller kalçada · 3'er deneme · Elastik enerji kullanımı (CMJ − SJ farkı)"),
    "Dikey Sıçrama (Hentbol)": lambda: sahne_cmj_sj_ikili("Hentbol Dikey Sıçrama — CMJ (Sol) ve SJ Statik (Sağ)", "Standart CMJ ve SJ protokolü · 3'er deneme, en iyi yükseklik (cm)"),
    "Dikey Sıçrama ve CMJ (Halter)": lambda: sahne_cmj_sj_ikili("Halter Dikey Sıçrama — CMJ (Sol) ve SJ Statik (Sağ)", "Eller kalçada · CMJ − SJ farkı reaktif kuvvet göstergesidir"),
    "Dikey Sıçrama - Voleybol (CMJ + SJ + DJ)": lambda: sahne_cmj_sj_dj_uclu("Voleybol Sıçrama Bataryası — CMJ · SJ (90°) · DJ (30 cm Kutu)", "3'er deneme · Sıçrama yüksekliği (cm) ve Reaktif Kuvvet İndeksi (RSI)"),
    "Dikey Sıçrama Tam Batarya (CMJ + SJ + DJ)": lambda: sahne_cmj_sj_dj_uclu("Dikey Sıçrama Tam Batarya — CMJ · SJ (90° Statik) · DJ (30 cm)", "Eller kalçada · 3'er deneme · Eksantrik-konsantrik döngü ve RSI analizi"),
    # 2. Canlı antropometri ve BOT-2 sahneleri
    "Boy ve Vücut Ağırlığı (TSYT)": sahne_boy_kilo_canli,
    "Oturma Yüksekliği (TSYT)": lambda: sahne_oturma_yuksekligi_canli("Oturma Yüksekliği (TSYT) — Dizler 90°, Sırt ve Baş Dik", "Oturma yüzeyinden başın en üst noktasına (0,1 cm hassasiyet)"),
    "Oturma Yüksekliği": lambda: sahne_oturma_yuksekligi_canli("Oturma Yüksekliği — Gövde Dik, Baş Frankfurt Düzleminde", "Okunan toplam değerden oturak yüksekliği çıkarılarak net gövde boyu bulunur"),
    "Top Sektirme — Alternatif El (BOT-2)": sahne_top_sektirme_canli,
    # 3. 28 TEST_GORSELSIZ testin her biri için özel laboratuvar / saha sahneleri
    "Vücut Kompozisyonu - Deri Kıvrımı": lambda: sahne_deri_kivrimi("Vücut Kompozisyonu (Deri Kıvrımı)"),
    "Vücut Kompozisyonu (PYFP)": lambda: sahne_deri_kivrimi("PYFP Vücut Kompozisyonu (Triceps & Baldır)"),
    "Vücut Kompozisyonu (PREFIT)": lambda: sahne_deri_kivrimi("PREFIT Vücut Kompozisyonu (3–6 Yaş)"),
    "Vücut Kompozisyonu (CNPFM)": lambda: sahne_deri_kivrimi("CNPFM Vücut Kompozisyonu"),
    "Vücut Kompozisyonu (Latorre)": lambda: sahne_deri_kivrimi("Latorre Vücut Kompozisyonu (3–6 Yaş)"),
    "Bel Çevresi ve VKİ (Vücut Kompozisyonu)": sahne_bel_cevresi_vki,
    "DEXA (Dual-Energy X-ray Absorptiometry)": sahne_dexa_tarama,
    "Biyoelektrik İmpedans Analizi (BIA)": sahne_bia_analiz,
    "Hidrostatik Tartım (Su Altı Tartımı)": sahne_hidrostatik_tartim,
    "VO2max Direkt Ölçüm (Ergospirometri)": sahne_vo2max_ergospirometri,
    "Laktat Eşiği Testi": sahne_laktat_esigi,
    "Kardiyopulmoner Egzersiz Testi (CPET)": sahne_cpet_kardiyo,
    "İzokinetik Kuvvet Testi": sahne_izokinetik_kuvvet,
    "Force-Velocity Profili (F-V)": sahne_force_velocity_profili,
    "EMG Tabanlı Kas Aktivasyonu": sahne_emg_kas_aktivasyonu,
    "Rate of Force Development (RFD) Ölçümü": sahne_rfd_imtp,
    "CAPL Günlük Adım Sayısı (Günlük Davranış)": sahne_capl_adim_sayisi,
    "CAPL Motivasyon ve Güven Anketi": sahne_capl_motivasyon_anketi,
    "Judo Fiziksel Uygunluk Testi (JPFT)": lambda: sahne_coklu_batarya("Judo Fiziksel Uygunluk Testi (JPFT)"),
    "MMA Fiziksel Uygunluk Bataryası": lambda: sahne_coklu_batarya("MMA Fiziksel Uygunluk Bataryası"),
    "Atletik Güç Testi Bataryası": lambda: sahne_coklu_batarya("Atletik Güç Testi Bataryası"),
    "Kuru Kara Testleri (Dry-Land) — Yüzme": lambda: sahne_coklu_batarya("Kuru Kara Testleri (Dry-Land) — Yüzme"),
    "Jimnastik Fiziksel Uygunluk Testi (GFT)": lambda: sahne_coklu_batarya("Jimnastik Fiziksel Uygunluk Testi (GFT)"),
    "Badminton Spesifik Çeviklik Testi (BAT)": lambda: sahne_coklu_batarya("Badminton Spesifik Çeviklik Testi (BAT)"),
    "Rugby League Match Simulation Protocol (RLMSP)": lambda: sahne_coklu_batarya("Rugby League Match Simulation Protocol (RLMSP)"),
    "NFL Combine Testleri": lambda: sahne_coklu_batarya("NFL Combine Testleri"),
    "Rugby Union Fitness Test Bataryası": lambda: sahne_coklu_batarya("Rugby Union Fitness Test Bataryası"),
    "NHL/NHLTM Off-Ice Testleri": lambda: sahne_coklu_batarya("NHL/NHLTM Off-Ice Testleri"),
}
