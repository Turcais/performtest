"""
Test görselleri — sahneler: teste özgü çizimler (_tg_*), TEST_GORSELLERI kaydı, görseli olmayan testler,
tg_sahne giriş noktası ve görsel penceresi (st.dialog).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import functools as _functools
import math as _math
import streamlit as st
from olcut.gorseller.cizim import (
    TG_KALINLIK, TG_OLCEK, TG_OLCU_Y, TG_RENK, TG_ZEMIN, TgHareket, TgSahne, _TG_BOY, _TG_PARKURLAR,
    _TG_WINGATE, _TG_WINGATE_KRITIK, _TG_YOYO2_KRITIK, _TG_YOYO_IR1, _TG_YOYO_KRITIK)
from olcut.gorseller.hareketler import (
    hk_antropometri, hk_arka_comelme, hk_asilma, hk_asilma_bukumlu, hk_atma, hk_bench_press, hk_camsa_turu,
    hk_denge, hk_dikey_sicrama, hk_dinamometre, hk_donuslu_kos, hk_duz_kos, hk_eggbeater_sicrama, hk_egil_al,
    hk_flamingo, hk_govde_kaldirma, hk_iki_uke_atis, hk_ikinci_figur, hk_iz, hk_kavisli_yol, hk_kavrama,
    hk_kayak_ergometre, hk_koordinasyon_turu, hk_koparma, hk_kurek_ergometre, hk_leg_press, hk_masa_dokunma,
    hk_mekik, hk_modifiye_barfiks, hk_nordic, hk_omuz_esneme, hk_omuz_rotasyon, hk_oturarak_uzanma, hk_paten,
    hk_pedal, hk_sargent, hk_serbest_stil, hk_servis, hk_sicrama_ani, hk_silkme, hk_sinav, hk_split,
    hk_tek_ayak_sekme, hk_top_sektirme, hk_top_yakala, hk_tutus, hk_uchikomi, hk_uzun_atlama, hk_vurus,
    hk_yan_adim, hk_yana_sicrama)
from olcut.katalog_islemleri import protokol_ozet_cikar


# ── 3) SAHNELER: hareket + ekipman + ölçülen büyüklük + en çok üç yazı ──
def _tg_parabol(x0, y0, x1, y1, tepe, t0, t1, n=10):
    return [(t0 + (t1 - t0) * i / n, x0 + (x1 - x0) * i / n,
             y0 + (y1 - y0) * i / n - 4 * tepe * (i / n) * (1 - i / n)) for i in range(n + 1)]


def _tg_direk(S, x, alt=3):
    """Zemin çizgisini kesen kısa çizgi (başlangıç/dönüş çizgisi): alt şeride girmez."""
    S.esya(S.cizgi(x, TG_ZEMIN - 5, x, TG_ZEMIN + alt, tur="figur"))


def _tg_boy():
    S = TgSahne(2.6)
    S.esya(S.kutu(86, 21, 5, TG_ZEMIN - 21, rx=1) + "".join(S.cizgi(91, y, 94, y) for y in range(30, TG_ZEMIN, 10)))
    S.esya(S.kutu(96, TG_ZEMIN - 4, 40, 4))
    h = hk_antropometri(106)
    e = S.figur(h)
    ust = e["bas_ust"][1]
    S.kaydir(S.cizgi(86, ust - 1.6, 124, ust - 1.6, tur="figur"), [(0, 0, -9), (0.15, 0, -9), (0.5, 0, 0), (1, 0, 0)])
    S.baslik("Topuk, kalça, sırt ve baş aynı dikeyde")
    S.olcu(150, TG_ZEMIN, 150, ust, "Boy (cm)", t=0.55, kilavuzlar=[(124, ust, 150, ust)],
           bag=[(1, "y", ("bas_ust",), "min")])
    S.not_("Derin nefes alıp tutarken ölçülür · tartı: kg", t=0.7)
    return S


def _tg_oturma(baslik="Dizler 90°, gözler karşıya", notu="Oturma yüzeyinden başın üstüne"):
    S = TgSahne(2.4)
    oturak = TG_ZEMIN - 23
    S.esya(S.kutu(60, oturak, 32, TG_ZEMIN - oturak))
    S.esya(S.kutu(54, 21, 4, TG_ZEMIN - 21, rx=1))
    h = hk_antropometri(70, "oturarak", oturak_y=oturak)
    e = S.figur(h)
    ust = e["bas_ust"][1]
    S.kaydir(S.cizgi(54, ust - 1.6, 92, ust - 1.6, tur="figur"), [(0, 0, -9), (0.15, 0, -9), (0.5, 0, 0), (1, 0, 0)])
    S.baslik(baslik)
    S.olcu(126, oturak, 126, ust, "Oturma yüksekliği", t=0.55,
           kilavuzlar=[(92, oturak, 126, oturak), (92, ust, 126, ust)], bag=[(1, "y", ("bas_ust",), "min")])
    S.not_(notu, t=0.7)
    return S


def _tg_kulac():
    S = TgSahne(2.4)
    S.esya(S.cizgi(70, 34, 190, 34) + "".join(S.cizgi(x, 34, x, 37) for x in range(70, 191, 10)))
    h = hk_antropometri(130, "kulac")
    S.figur(h)
    (sx, sy), (dx, dy) = h.olay["eller"]
    S.baslik("Kollar yere paralel, avuç içleri karşıya")
    S.olcu(sx, 22, dx, 22, "Kulaç", t=0.65, kilavuzlar=[(sx, sy - 2, sx, 22), (dx, dy - 2, dx, 22)],
           bag=[(0, "x", ("el1", "el2"), "min"), (1, "x", ("el1", "el2"), "max")])
    S.not_("İki orta parmak ucu arası (cm)", t=0.7)
    return S


def _tg_esneklik():
    S = TgSahne(3.2)
    z = TG_ZEMIN
    S.esya(S.kutu(170, z - 20, 50, 20))
    S.esya(S.cizgi(160, z - 21, 240, z - 21) + "".join(S.cizgi(x, z - 24, x, z - 21) for x in range(164, 240, 6)))
    h = hk_oturarak_uzanma(170)
    S.figur(h)
    el = h.olay["el"][0]
    S.kaydir(S.kutu(176, z - 28, 5, 7, dolgu="yuzey", rx=1),
             [(0, 0, 0), (0.45, 0, 0), (0.8, el - 178.5, 0), (1, el - 178.5, 0)])
    S.baslik("Ayak tabanı sehpaya dayalı, dizler gergin")
    S.isaret("Cetvelin itildiği nokta", (el, z - 28), (el + 4, 52), hiza="start", t=0.82)
    S.not_("Sıfır noktası: TSYT sehpasının kendi cetveli", t=0.82)
    return S


def _tg_dikey():
    S = TgSahne(2.8)
    S.esya(S.kutu(92, TG_ZEMIN - 3, 48, 3))
    h = hk_dikey_sicrama(116, yukselme=20, s=0.75)
    e = S.figur(h)
    ayaklar = ("ayak1", "ayak2", "parmak1", "parmak2")
    tepe = max(e[k][1] for k in ayaklar)              # son karede (tepe) en alttaki ayak noktası
    ayak_x = max(e[k][0] for k in ayaklar)
    S.baslik("Kollar serbest, beklemeden çök ve sıçra")
    S.olcu(152, TG_ZEMIN, 152, tepe, "Sıçrama yüksekliği", t=0.95, kilavuzlar=[(ayak_x + 2, tepe, 152, tepe)],
           bag=[(1, "y", ayaklar, "max")])
    S.not_("Aynı noktaya, dizler gergin in", t=0.95)
    return S


def _tg_kavrama(baslik="Ayakta, kol gergin ve aşağıda", isaret="Olanca kuvvetle sık (kg)",
                notu="Her el bir kez, tek ölçüm"):
    S = TgSahne(2.6)
    h = hk_kavrama(118)
    S.figur(h)
    x, y = h.olay["el"]
    S.belir(f'<rect x="{x - 4:.1f}" y="{y - 7:.1f}" width="8" height="14" rx="2.5" fill="{TG_RENK["yuzey"]}" '
            f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>', 0.45)
    S.belir("".join(S.cizgi(x + 7 + i * 3, y - 4 - i, x + 7 + i * 3, y + 4 + i, "olcu") for i in range(2)), 0.85,
            tur="isaret")
    S.baslik(baslik)
    S.isaret(isaret, (x + 4, y), (x + 34, y - 30), hiza="start", t=0.85)
    S.not_(notu, t=0.85)
    return S


def _tg_saglik_topu():
    S = TgSahne(3.0)
    _tg_direk(S, 80)
    h = hk_atma(72, "geriye", yon=-1, s=0.85)
    S.figur(h)
    (_, x0, y0) = h.olay["el_yolu"][-1]
    dusus = 176
    ucus = _tg_parabol(x0, y0, dusus, TG_ZEMIN - 4, 16, h.olay["birakma_t"], 0.92)
    S.top(h.olay["el_yolu"] + ucus[1:])
    iz = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (_, x, y) in enumerate(ucus))
    S.belir(f'<path d="{iz}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
            f'stroke-dasharray="2 2"/>' + S.nokta(dusus, TG_ZEMIN - 1, 2.2), 0.93, tur="isaret")
    S.baslik("Sırt atış alanına dönük, atış çizgisinde")
    S.olcu(80, TG_OLCU_Y, dusus, TG_OLCU_Y, "Atış mesafesi", uc="son", t=0.93)
    S.not_("Baş üzerinden geriye, yaklaşık 45° ile", t=0.6)
    return S


def _tg_pro_agility():
    S = TgSahne(4.2)
    for x in (55, 130, 205):
        _tg_direk(S, x)
    h = hk_donuslu_kos([130, 205, 55, 150], s=0.8)
    S.figur(h)
    for t, x in h.olay["dokunma"]:
        S.belir(S.nokta(x, TG_ZEMIN, 3.2), t, tur="isaret")
    S.baslik("Orta → 4,57 m → 9,14 m → orta (18,28 m)")
    S.olcu(55, TG_OLCU_Y, 130, TG_OLCU_Y, "4,57 m", uc="ilk", metre=4.57)
    S.olcu(130, TG_OLCU_Y, 205, TG_OLCU_Y, es=0, metre=4.57)
    S.not_("Her dönüşte çizgiye elle dokun", t=0.3)
    return S


def _tg_surat():
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_surat"][0]              # 1 m (20 m = 190 birim)
    cizgi_x, f1, f2 = 25, 25 + m, 25 + 21 * m
    _tg_direk(S, cizgi_x)
    for x in (f1, f2):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    S.esya(S.cizgi(cizgi_x, TG_OLCU_Y, f1, TG_OLCU_Y, "olcu"), tur="isaret")
    h = hk_duz_kos(17, f2 + 3, s=0.8, bitis_x=f2)       # ön ayak ucu çıkış çizgisinde
    S.figur(h)
    S.baslik("Çıkış çizgisi, başlangıç fotoselinin 1 m gerisi")
    S.olcu(f1, 30, f2, 30, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(f1, TG_ZEMIN - 28, f1, 30), (f2, TG_ZEMIN - 28, f2, 30)])
    S.not_("Bitiş fotoselini yavaşlamadan geç", t=0.8)
    return S


def _tg_koordinasyon_genel():
    """Koordinasyon Parkuru — GENEL GÖRÜNÜM (durağan kopya): dokuz istasyon yan yana, sıra numaralı."""
    S = TgSahne(4.6)
    y = TG_ZEMIN
    k = TG_KALINLIK["esya"]
    S.esya(S.kutu(22, y - 3, 18, 3)                                                       # takla minderi
           + S.kutu(44, y - 6, 22, 3) + S.cizgi(46, y - 3, 46, y) + S.cizgi(64, y - 3, 64, y)   # denge tahtası
           + S.cizgi(72, y, 72, y - 48) + S.cizgi(84, y, 84, y - 48) + S.cizgi(72, y - 48, 84, y - 48)  # yüksek engel
           + "".join(f'<ellipse cx="{x}" cy="{y - 1}" rx="4" ry="1.6" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
                     for x in (94, 102, 110))                                             # sekme çemberleri
           + "".join(f'<circle cx="{x}" cy="{y - 4}" r="3" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
                     for x in (122, 134, 146))                                            # top yer değiştirme
           + S.kutu(156, y - 50, 4, 50, rx=0.8)                                              # duvar
           + "".join(S.cizgi(x, y, x, y - hh) + S.cizgi(x, y - hh, x + 4, y - hh)
                     for x, hh in ((168, 30), (175, 15), (182, 30), (189, 15)))           # alttan-üstten
           + "".join(S.cizgi(x, y, x, y - 22) for x in (202, 208, 214, 220)))             # slalom
    for x in (12, 230):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    # istasyon sırası (protokol 2-10. adımlar): takla, denge, engel üstünden top, sekme, elle top, ayakla top,
    # duvara top, alttan-üstten, slalom. Elle ve ayakla yer değiştirme aynı düzeneği paylaşır (5 ve 6).
    for n, x in enumerate((31, 55, 78, 102, 128, 140, 158, 178, 211), 1):
        S.numara(x, 56 if n != 6 else 46, n)
    h = hk_duz_kos(22, 228, s=0.55, cikis_t=0.04, bitis_x=230)
    S.figur(h)
    S.baslik("Dokuz istasyon, tek parkur")
    S.olcu(12, 30, 230, 30, "Süre", etiket_yer="orta", kilavuzlar=[(12, TG_ZEMIN - 28, 12, 30), (230, TG_ZEMIN - 28, 230, 30)])
    S.not_("Hatalı istasyon yeniden yapılır (süre cezası yok)", t=0.05)
    return S


def _tg_cember(x, y, r):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="1.6" fill="none" stroke="{TG_RENK["esya"]}" '
            f'stroke-width="{TG_KALINLIK["esya"]}"/>')


def _tg_koordinasyon():
    """
    Koordinasyon Parkuru (TSYT) — KAYAN SAHNE (Paket 21). Parkur tuvalden geniş çizilir ve bir grup olarak sola
    kayar; figür tuvalin ortasına yakın kalır ve yanından geçen istasyonun hareketini yapar (sıra protokolden,
    hk_koordinasyon_turu). Başlık, not, istasyon numarası ve süreölçer sabit katmanda — parkurla kaymaz.
    Durağan kopya BİLEREK farklı: genel görünüm, dokuz istasyon numaralı (_tg_koordinasyon_genel).
    """
    m = TG_OLCEK["_tg_koordinasyon"][0]
    h = hk_koordinasyon_turu(x_c=118, s=0.7, m=m)
    o, ek, Z = h.olay, h.olay["ekipman"], TG_ZEMIN
    S = TgSahne(o["sure"])
    r = 0.3 * m                                                          # 60 cm çember
    xml = "".join(S.kutu(x - 1.5, Z - 26, 3, 26, dolgu="yuzey", rx=0.8) for x in (ek["baslangic"], ek["bitis"]))
    a, b = ek["minder"]
    xml += S.kutu(a, Z - 3, b - a, 3)                                                    # 1 minder
    a, b, ust = ek["denge"]
    xml += (S.kutu(a, ust, b - a, Z - ust, rx=0.6)                                       # 2 denge tahtası
            + "".join(S.cizgi(x, ust - 2, x, ust, "olcu") for x in (a + 0.3 * m, b - 0.3 * m)))  # 30 cm bölgeler
    ex, eh = ek["engel_ust"]
    xml += S.cizgi(ex - 6, Z, ex - 6, Z - eh) + S.cizgi(ex + 6, Z, ex + 6, Z - eh) + S.cizgi(ex - 6, Z - eh, ex + 6, Z - eh)
    xml += _tg_cember(ek["cember3"], Z - 1, r)                                          # 3 topun çemberi
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["sekme"])                          # 4 sekme çemberleri
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["el_cember"] + ek["ayak_cember"])  # 5-6
    xml += S.kutu(ek["duvar"], Z - 1.6 * m, 4, 1.6 * m, rx=0.8)                          # 7 duvar
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["duvar_cember"])
    for x, hh in ek["alttan_ustten"]:                                                    # 8 alttan-üstten
        xml += S.cizgi(x - 5, Z, x - 5, Z - hh) + S.cizgi(x + 5, Z, x + 5, Z - hh) + S.cizgi(x - 5, Z - hh, x + 5, Z - hh)
    xml += "".join(S.cizgi(x, Z, x, Z - 0.9 * m) for x in ek["slalom"])                   # 9 slalom
    S.kaydir(xml, [(t, dx, 0) for t, dx in o["kayma"]])
    for yol in o["toplar"]:
        S.top(yol, r=2.2)
    S.figur(h, donus=o["donus"])
    S.istasyon_araliklari = [(a, b) for _, a, b in o["istasyonlar"]]
    S.parkur_kaymasi = list(o["kayma"])
    for n, t0, t1 in o["istasyonlar"]:                                                  # sabit katman
        S.numara(22, 32, n, t0, t_bitis=t1)
    S.kronometre(238, 34, t0=o["istasyonlar"][0][1] * 0.5)
    S.baslik_nobet("Dokuz istasyon sırayla, tek parkur",                # istasyon adı başlık yerinde (Paket 25)
                   [(ad, t0, t1) for ad, (_, t0, t1) in zip(o["istasyon_adlari"], o["istasyonlar"])])
    S.not_("Hatalı istasyon yeniden yapılır (süre cezası yok)", t=0.02)
    S.duragan = _tg_koordinasyon_genel()
    return S


def _tg_mekik(baslik="Her sinyalde karşı çizgiye", notu="Sinyali iki kez üst üste kaçıran bitirir"):
    """20 m mekik (TSYT; Eurofit/Léger, PACER, ALPHA, PREFIT, CAPL aynı çizim — etiket protokolün kendisinden)."""
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_mekik"][0]
    a, b = 30, 30 + 20 * m
    for x in (a, b):
        _tg_direk(S, x)
    h = hk_donuslu_kos([a, b, a + 4], s=0.8, dokun=False, baslangic="kos")
    S.figur(h)
    for t, x in ((0.5, b), (0.98, a)):     # sinyal anı: çizgide küçük ses dalgası
        S.belir("".join(f'<path d="M{x - 6 - 3 * i:.1f},{56 - 2 * i} q{-3 - i},{4 + 2 * i} 0,{8 + 4 * i}" fill="none" '
                        f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>' for i in range(2)), t,
                tur="isaret")
    S.baslik(baslik)
    S.olcu(a, 30, b, 30, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(a, TG_ZEMIN - 7, a, 30), (b, TG_ZEMIN - 7, b, 30)])
    S.not_(notu, t=0.05)
    return S


def _tg_geriye_denge(tur="kiris_geriye", baslik="Kiriş üzerinde geriye doğru, en çok 8 adım",
                     notu="Kiriş 3 m · genişlik 6 / 4,5 / 3 cm"):
    """Kirişte yürüme: KTK geriye; KMS balans öne (tur="kiris_ileri")."""
    S = TgSahne(3.6)
    taban = TG_ZEMIN - 10
    S.esya(S.kutu(26, taban, 208, 5, rx=0.8) + S.kutu(36, taban + 5, 6, 5, rx=0.5) + S.kutu(218, taban + 5, 6, 5, rx=0.5))
    h = hk_denge(tur, 60, 170, taban=taban, s=0.85)
    S.figur(h)
    for i, x in enumerate(h.olay["adimlar"][1:], 1):
        S.belir(S.cizgi(x, taban - 2, x, taban + 2, "olcu"), i / 6, tur="isaret")
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_yana_sicrama(baslik="Çift ayakla sağa-sola, 15 sn", isaret="Çıtanın üzerinden",
                     notu="2 deneme · çıtaya basmak, tek ayakla inmek geçersiz"):
    """Yana sıçrama (KTK3+; KMS aynı çizim, etiket kendi protokolünden)."""
    S = TgSahne(3.2)
    S.esya(S.kutu(80, TG_ZEMIN - 3, 100, 3) + S.kutu(128.5, TG_ZEMIN - 8, 3, 5, rx=0.5))
    h = hk_yana_sicrama(112, 148, s=0.85)
    S.figur(h)
    _tg_periyot_seridi(S, [(15, True), (None, None), (15, True)], x0=12, y=22, olcek=2.0)
    S.baslik(baslik)
    S.isaret(isaret, (130, TG_ZEMIN - 8), (176, 86), hiza="start", t=0.05)
    S.not_(notu, t=0.5)
    return S


def _tg_yana_platform():
    S = TgSahne(3.8)
    yuk = 7

    def platform(x):
        return (S.kutu(x, TG_ZEMIN - yuk, 22, 4, dolgu="yuzey", rx=1)
                + S.cizgi(x + 3, TG_ZEMIN - 3, x + 3, TG_ZEMIN) + S.cizgi(x + 19, TG_ZEMIN - 3, x + 19, TG_ZEMIN))
    S.esya(platform(122))
    h = hk_denge("platform", 103, taban=TG_ZEMIN - yuk, s=0.85)
    S.kaydir(platform(92), h.olay["platform"])
    S.figur(h)
    _tg_periyot_seridi(S, [(20, True), (None, None), (20, True)], x0=12, y=22, olcek=1.6)
    S.baslik("20 sn: boştaki platformu yana koy, üstüne bas")
    S.isaret("Koy + bas = puan", (174, TG_ZEMIN - yuk), (200, 60), hiza="start", t=0.62)
    S.not_("2 deneme · yön serbest, hep aynı yöne", t=0.05)
    return S


def _tg_goz_el():
    S = TgSahne(3.8)
    m = TG_OLCEK["_tg_goz_el"][0]            # 1 m (0,66 ölçekli çocuğa göre)
    duvar = 231                              # duvar yüzü
    S.esya(S.kutu(duvar + 1, 21, 6, TG_ZEMIN - 21, rx=0.8))
    S.esya(f'<line x1="{duvar}" y1="{TG_ZEMIN - m}" x2="{duvar}" y2="{TG_ZEMIN - 2 * m}" stroke="{TG_RENK["olcu"]}" '
           f'stroke-width="{TG_KALINLIK["vurgu"]}" stroke-linecap="round"/>')
    ayaklar = ("ayak1", "ayak2", "parmak1", "parmak2")
    h = hk_atma(duvar - m - 10, "duvara", s=0.66, on_ayak_x=duvar - m)      # en öndeki ayak ucu duvardan 1 m geride
    e = S.figur(h)
    on = max(e[k][0] for k in ayaklar)
    el = h.olay["tut"]
    hedef = (duvar - 2, TG_ZEMIN - 1.5 * m)
    yol = [(0, *el)]
    for b0 in (0.12, 0.54):
        yol += [(b0, *el), (b0 + 0.12, *hedef), (b0 + 0.3, *el)]
    S.top(yol, r=3.2)
    S.esya(S.cizgi(246, TG_ZEMIN, 246, TG_ZEMIN - m, "olcu", kesik=True), tur="isaret")
    _tg_periyot_seridi(S, [(30, True), (None, None), (30, True)], x0=12, y=22, olcek=1.2)
    S.baslik("30 sn: kareye at, sektikten sonra yakala")
    oy = TG_ZEMIN - 30                       # duvar ile ayak ucu arası boşlukta, kılavuzla zemine bağlı
    S.olcu(on, oy, duvar, oy, "1 m", etiket_yer="orta", etiket_dx=8, metre=1, kilavuzlar=[(on, TG_ZEMIN - 1, on, oy)],
           bag=[(0, "x", ayaklar, "max")])
    S.not_("Hedef kare 1 × 1 m, alt kenarı yerden 1 m")
    return S


def _tg_tek_ayak():
    S = TgSahne(3.4)
    for i in range(3):
        S.esya(S.kutu(124, TG_ZEMIN - 3.5 * (i + 1), 14, 3.5, rx=0.6))
    h = hk_tek_ayak_sekme(96, 131, s=0.8, adim=12, yukselme=20)
    S.figur(h)
    iz = h.olay["iz"]
    S.belir(f'<path d="M{iz[0][0]:.1f},{iz[0][1]:.1f} Q{iz[1][0]:.1f},{iz[1][1] - 18:.1f} {iz[2][0]:.1f},{iz[2][1]:.1f}" '
            f'fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.45,
            tur="isaret")
    S.baslik("Tek ayak; diğer ayak yere değmez")
    S.isaret("5'er cm sünger blok", (131, TG_ZEMIN - 10.5), (70, 70), hiza="end", t=0.05)
    S.not_("İnişten sonra aynı ayakla en az 2 sıçrama", t=0.5)
    return S


# ── Branşa özgü sahneler (Paket 15-16) ──
def _tg_periyot_seridi(S, parcalar, x0=20, y=20, olcek=1.0, t=0.0, imlec=None):
    """
    Zaman çubuğu: protokolün aralık yapısı tek şeritte. parcalar [(süre, aktif_mi[, yükseklik])] — aktif dolu,
    dinlenme açık kutu; (None, None) = süresi protokolde verilmeyen ara (kesik bağ); yükseklik (≤ 2) blokları
    yukarı doğru büyütür (30-15 IFT'de artan hız). Yazı içermez.
    imlec: [(t, oran)] — şeridin altındaki küçük üçgen bu anlarda şeridin bu oranındadır (hareketle eşleşir).
    Döndürür (x0, x1, y, aktif_bloklar[(xa, xb)]).
    """
    xml, x, bloklar = "", x0, []
    for parca in parcalar:
        sure, aktif = parca[0], parca[1]
        oran = parca[2] if len(parca) > 2 else 1.0     # (süre, aktif, yükseklik oranı): artımlı hız basamağı
        if sure is None:
            xml += (f'<line x1="{x + 1:.1f}" y1="{y + 3}" x2="{x + 7:.1f}" y2="{y + 3}" stroke="{TG_RENK["olcu"]}" '
                    f'stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="1.5 1.5"/>')
            x += 8
            continue
        w = sure * olcek
        hh = 6 * oran
        xml += (f'<rect x="{x:.1f}" y="{y + 6 - hh:.1f}" width="{w:.1f}" height="{hh:.1f}" rx="1" '
                f'fill="{TG_RENK["olcu"] if aktif else TG_RENK["yuzey"]}" stroke="{TG_RENK["yuzey"] if aktif else TG_RENK["olcu"]}" '
                f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
        if aktif:
            bloklar.append((x, x + w))
        x += w
    S.belir(xml, t)
    if imlec:
        uc = f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>'
        S.kaydir(uc, [(tt, (x - x0) * o, 0) for tt, o in imlec], tur="isaret")
    S.zaman_seritleri.append((x0, x, y))
    return x0, x, y, bloklar


def _tg_yoyo(brans="", surum="IR1"):
    """
    Yo-Yo IR1 ve IR2 — bütün branşlar aynı sahneyi kullanır; branş adı yalnız başlıkta. IR2 farkı yalnız notta:
    protokolde dinlenme aynı (10 sn aktif), başlangıç hızı yüksek (13 km/h).
    """
    S = TgSahne(4.6)
    m = TG_OLCEK["_tg_yoyo"][0]
    bas_x, dinlenme_x, uzak_x = 60, 60 - 5 * m, 60 + 20 * m
    for x in (dinlenme_x, bas_x, uzak_x):
        S.esya(f'<path d="M{x - 3.5:.1f},{TG_ZEMIN} L{x:.1f},{TG_ZEMIN - 9} L{x + 3.5:.1f},{TG_ZEMIN} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.esya(S.cizgi(dinlenme_x, TG_OLCU_Y, bas_x, TG_OLCU_Y, "kilavuz"), tur="isaret")   # 5 m dinlenme alanı
    s = 0.8
    mekik = hk_donuslu_kos([bas_x, uzak_x - 4, bas_x + 2], s=s, dokun=False, baslangic="kos", t1=0.72)
    dinlenme = hk_donuslu_kos([bas_x + 2, dinlenme_x + 4, bas_x], s=s, dokun=False, baslangic="kos", t0=0.74)
    S.figur(TgHareket(mekik.anahtarlar + dinlenme.anahtarlar, {}))
    for t, x in ((0.36, uzak_x), (0.72, bas_x)):
        S.belir("".join(f'<path d="M{x - 6 - 3 * i:.1f},{50 - 2 * i} q{-3 - i},{4 + 2 * i} 0,{8 + 4 * i}" fill="none" '
                        f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>' for i in range(2)), t,
                tur="isaret")
    # şematik şerit: koşu blokları bip hızlandıkça kısalır, her koşudan sonra eşit dinlenme bloğu
    kosular = [16, 14, 12.5, 11, 10, 9]
    parca = [p for k in kosular for p in ((k, True), (10, False))]
    toplam = sum(k for k, _ in parca)
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.8,
                       imlec=[(0, 0), (0.72, kosular[0] / toplam), (1.0, (kosular[0] + 10) / toplam)])
    S.baslik(f"{brans} · Bip sesiyle 20 m çift yön koşu" if brans else "Bip sesiyle 20 m çift yön koşu")
    S.olcu(bas_x, TG_OLCU_Y, uzak_x, TG_OLCU_Y, "20 m", uc="son", metre=20)
    S.not_("Her turda 10 sn aktif dinlenme (5 m gidip gelme)" if surum == "IR1"
           else "Başlangıç 13 km/h · her turda 10 sn aktif dinlenme", t=0.72)
    return S


def _tg_imlec_atis(atislar, bloklar, x0, x1):
    """Zaman çubuğu imleci: her atış, sırasıyla bir aktif bloğun sonuna denk gelir."""
    uz = (x1 - x0) or 1
    an = [(0.0, 0.0)]
    for t, (xa, xb) in zip(atislar, bloklar):
        an.append((t, (xb - 2 - x0) / uz))
    if an[-1][0] < 1:
        an.append((1.0, 1.0))
    return an


def _tg_swft():
    """SWFT: suplex (geriye köprüyle sırtüstü devirme); ölçülen = TOPLAM atış (tek sayaç)."""
    S = TgSahne(6.0)
    S.esya(S.kutu(96, TG_ZEMIN - 3, 152, 3, rx=1))
    h = hk_atma(176, "suplex", tekrar=3)
    S.figur(h.olay["partner"])
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(30, True), (20, False), (30, True), (20, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.8, imlec=None)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    sx0, sy0, sx1, sy1 = S.sayac(44, 60, atis, boy=20)
    S.baslik("Manken suplex tekniğiyle sırtüstü devrilir")
    S.isaret("Toplam atış sayısı", ((sx0 + sx1) / 2, sy0), (12, 50), hiza="start", t=atis[0])
    S.not_("3 × 30 sn aktif, aralarında 20 sn pasif dinlenme")
    return S


def _tg_sjft():
    """Modified SJFT: öne devirme (manken sırttan öne); ölçülen = HER PERİYOTTA atış (periyot başına sayaç)."""
    S = TgSahne(6.0)
    S.esya(S.kutu(60, TG_ZEMIN - 3, 188, 3, rx=1))
    h = hk_atma(170, "one", tekrar=3)
    S.figur(h.olay["partner"])
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(15, True), (10, False), (30, True), (10, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=1.2, imlec=None)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(atis, bloklar):
        S.sayac((xa + xb) / 2 - 7, 36, [t], boy=14)
    S.baslik("Her periyotta manken en çok sayıda devrilir")
    ilk = S.sayaclar[0]
    S.isaret("Periyot başına atış", ((ilk[0] + ilk[2]) / 2, ilk[3]), (12, 76), hiza="start", t=atis[0])
    S.not_("15 sn / 30 sn / 30 sn, aralarında 10 sn dinlenme")
    return S


def _tg_gures_mac():
    return _tg_mac([(60, True), (10, False), (60, True)], 0.7, "Eşit ağırlık kategorisinde iki sporcu",
                   "2 × 3 dk, 30 sn ara", "Her periyot sonunda KAH ve RPE (Borg)")


def _tg_paten_30():
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_paten_30"][0]
    x0, x1 = 28, 28 + 30 * m
    for x in (x0, x1):
        _tg_direk(S, x)
    S.figur(hk_paten(x0 - 6, x1, s=0.8))
    S.baslik("Durarak başlangıç, 30 m maksimal hız")
    S.olcu(x0, 30, x1, 30, "30 m", etiket_yer="orta", metre=30, kilavuzlar=[(x0, TG_ZEMIN - 7, x0, 30), (x1, TG_ZEMIN - 7, x1, 30)])
    S.not_("3 deneme, en iyi süre kaydedilir", t=0.8)
    return S


def _tg_paten_6_30():
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_paten_6_30"][0]
    x0, x6, x30 = 28, 28 + 6 * m, 28 + 30 * m
    for x in (x0, x6, x30):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    S.figur(hk_paten(x0 - 6, x30, s=0.8))
    S.baslik("Durarak başlangıç; fotosel 6. ve 30. metrede")
    S.olcu(x0, 52, x6, 52, "6 m", uc="son", metre=6, kilavuzlar=[(x0, TG_ZEMIN - 28, x0, 52), (x6, TG_ZEMIN - 28, x6, 52)])
    S.olcu(x0, 30, x30, 30, "30 m", etiket_yer="orta", metre=30, kilavuzlar=[(x0, 52, x0, 30), (x30, TG_ZEMIN - 28, x30, 30)])
    return S


def _tg_s_turn():
    """
    S-Turn (yandan): buz yüzeyi zemin çizgisinin gerisinde ince bir şerit (derinlik). Koniler şeridin ortasında,
    güzergâh konilerin bir önünden bir arkasından geçer; figürün ayakları her karede güzergâhın üzerindedir.
    """
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_s_turn"][0]
    arka, orta, sapma = TG_ZEMIN - 18, TG_ZEMIN - 9, 6   # buz şeridi derinliği: arka, orta (koniler), ön = zemin
    koniler = [48 + i * 3 * m for i in range(5)]
    bas_x, bit_x = 22, koniler[-1] + 40
    for x in (bas_x, bit_x):                              # başlangıç/bitiş: buzdaki çizgi (derinliğe yatık)
        S.esya(S.cizgi(x + 3, arka + 1, x - 3, TG_ZEMIN - 1, tur="esya"))
    noktalar = ([(bas_x, orta)] + [(x, orta + (sapma if i % 2 == 0 else -sapma)) for i, x in enumerate(koniler)]
                + [(bit_x, orta)])
    h = hk_kavisli_yol(noktalar, s=0.5, kip="paten")
    S.yol(h.olay["yol"])
    for i, x in enumerate(koniler):                        # koni: yolun yanında (önden geçilen koni yoldan önce çizilir)
        S.esya(f'<path d="M{x - 3:.1f},{orta + 1} L{x:.1f},{orta - 7} L{x + 3:.1f},{orta + 1} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(h)
    S.baslik("5 koni S şeklinde, 3 m aralıkla")
    S.olcu(koniler[0], TG_OLCU_Y, koniler[1], TG_OLCU_Y, "3 m", uc="son", metre=3,
           kilavuzlar=[(koniler[0], orta + 2, koniler[0], TG_OLCU_Y), (koniler[1], orta + 2, koniler[1], TG_OLCU_Y)])
    S.not_("3 deneme, en iyi süre kaydedilir", t=0.8)
    return S


def _tg_wingate(brans=""):
    """Wingate: ergometrede oturarak 30 sn maksimal pedal; direnç vücut ağırlığının %7,5'i. Branş adı yalnız başlıkta."""
    S = TgSahne(3.0)
    h = hk_pedal(110, s=0.85, tur=6)
    o = h.olay
    (cx, cy), (sx, sy), (gx, gy) = o["krank"], o["sele"], o["gidon"]
    k = TG_KALINLIK["esya"]
    volan = (cx + 34, cy - 6)
    S.esya(S.cizgi(cx - 34, TG_ZEMIN - 2, cx + 52, TG_ZEMIN - 2)                        # taban
           + S.cizgi(cx - 26, TG_ZEMIN - 2, sx - 2, sy + 4) + S.cizgi(sx - 8, sy + 2, sx + 6, sy + 2)   # sele borusu
           + S.cizgi(cx, cy, volan[0], volan[1]) + S.cizgi(volan[0], volan[1], volan[0] + 6, TG_ZEMIN - 2)
           + S.cizgi(sx + 2, sy + 10, gx, gy + 18) + S.cizgi(gx, gy + 18, gx, gy) + S.cizgi(gx - 4, gy, gx + 3, gy)
           + f'<circle cx="{volan[0]:.1f}" cy="{volan[1]:.1f}" r="13" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{k}"/>'
           + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.2" fill="{TG_RENK["esya"]}"/>')
    S.figur(h)
    _tg_periyot_seridi(S, [(30, True)], x0=12, y=22, olcek=3.0, imlec=[(0, 0), (1, 1)])
    S.baslik(f"{brans} · 30 sn oturarak maksimal pedal" if brans else "30 sn oturarak maksimal pedal")
    S.not_("Direnç: vücut ağırlığının %7,5'i")
    return S


# ── Branşa özgü sahneler, 2. parti (Paket 17): Futbol, Voleybol, Basketbol, Hentbol, Atletizm ──
def _tg_zemin_seridi(x0, sx, sz):
    """
    İki boyutlu güzergâhı yandan görünüşe indirger (Paket 18; Pro Agility ve S-Turn ile aynı yol): yan eksen
    (metre) zemin çizgisi boyunca uzanır, derinlik yalnız zeminin hemen gerisinde ince bir şeride sıkışır
    (perspektif saha çizilmez). Döndürür: P(x_m, z_m) → tuval noktası.
    """
    def P(xm, zm):
        return x0 + xm * sx, TG_ZEMIN - 2 - zm * sz
    return P


def _tg_koni(S, x, y, h=7):
    S.esya(f'<path d="M{x - 3:.1f},{y + 1:.1f} L{x:.1f},{y - h:.1f} L{x + 3:.1f},{y + 1:.1f} z" '
           f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')


def _tg_fotosel(S, x):
    S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))


def _tg_deneme_seridi(S, deneme, sag=248, y=20, w=8, olcek=1.6, t=0.0):
    """Deneme yapısı: her deneme bir blok, araları protokolde süre verilmeyen ya da aralıklı toparlanma (kesik)."""
    parca = []
    for i in range(deneme):
        parca += [(w, True)] + ([(None, None)] if i < deneme - 1 else [])
    gen = deneme * w * olcek + (deneme - 1) * 8
    return _tg_periyot_seridi(S, parca, x0=sag - gen, y=y, olcek=olcek, t=t)


def _tg_sprint(mesafe, baslik, notu, deneme, blok=False, fotosel=True):
    """
    Düz sprint (Atletizm 10/20/100/200/400 m, NBA 3/4 saha, Voleybol 20 m): çıkış ve bitiş fotoseli, üstte mesafe
    oku (şematik — mesafe ok boyuyla değil etiketle verilir), sağ üstte deneme şeridi.
    fotosel=False: protokol yalnız kronometre diyorsa çıkış ve bitiş yalnız çizgi.
    """
    S = TgSahne(3.2)
    x0, x1 = 30, 222
    for x in (x0, x1):
        (_tg_fotosel if fotosel else _tg_direk)(S, x)
    if blok:                                           # blok başlangıç (blok ya da ayakta)
        S.esya(f'<path d="M{x0 - 22:.1f},{TG_ZEMIN} L{x0 - 10:.1f},{TG_ZEMIN} L{x0 - 10:.1f},{TG_ZEMIN - 6:.1f} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(hk_duz_kos(x0 - 8, x1 + 3, s=0.8, bitis_x=x1))
    if deneme:                                          # 0: dayanıklılık koşusu (tek koşu, şerit yok)
        _tg_deneme_seridi(S, deneme)
    S.baslik(baslik)
    S.olcu(x0, 32, x1, 32, mesafe, etiket_yer="orta",
           kilavuzlar=[(x0, TG_ZEMIN - 28, x0, 32), (x1, TG_ZEMIN - 28, x1, 32)])
    S.not_(notu, t=0.8)
    return S


def _tg_hizlanma_profili():
    """Sprint hızlanma profili: fotosel 0, 10, 20, 30 m; bölüm okları eş uzunlukta (ölçekli)."""
    S = TgSahne(3.4)
    m = TG_OLCEK["_tg_hizlanma_profili"][0]
    xs = [30 + i * 10 * m for i in range(4)]
    for x in xs:
        _tg_fotosel(S, x)
    S.figur(hk_duz_kos(xs[0] - 8, xs[-1] + 3, s=0.8, bitis_x=xs[-1]))
    _tg_deneme_seridi(S, 3)
    S.baslik("Fotosel 10., 20. ve 30. metrede: bölüm süreleri")
    S.olcu(xs[0], 32, xs[1], 32, "10 m", etiket_yer="orta", metre=10,
           kilavuzlar=[(x, TG_ZEMIN - 28, x, 32) for x in xs])
    for a, b in zip(xs[1:], xs[2:]):
        S.olcu(a, 32, b, 32, es=0, metre=10)
    S.not_("3 deneme; her bölüm için en iyi değer", t=0.8)
    return S


def _tg_rsa():
    """RSA: 30 m tekrarlı sprint; zaman çubuğu 6 sprint ve aralarındaki 25 sn pasif dinlenme."""
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_rsa"][0]
    x0, x1 = 36, 36 + 30 * m
    for x in (x0, x1):
        _tg_fotosel(S, x)
    S.figur(hk_duz_kos(x0 - 8, x1 + 3, s=0.8, bitis_x=x1))
    sprint = 5                                         # şematik: sprint süresi protokolde yok, dar blok
    parca = [p for i in range(6) for p in ([(sprint, True)] + ([(25, False)] if i < 5 else []))]
    toplam = 6 * sprint + 5 * 25
    _tg_periyot_seridi(S, parca, x0=248 - toplam * 0.55, y=20, olcek=0.55, imlec=[(0, 0), (1, sprint / toplam)])
    S.baslik("6 × 30 m sprint, arada 25 sn pasif dinlenme")
    S.olcu(x0, TG_OLCU_Y, x1, TG_OLCU_Y, "30 m", uc="ilk", metre=30)      # zeminde, fotoseller arası
    S.not_("Durarak başlangıç; en iyi ve ortalama süre", t=0.8)
    return S


def _tg_list():
    """LIST: 20 m mekik; zaman çubuğu 5 × 15 dk bölüm (her bölüm yürüyüş → koşu → hızlı koşu → sprint → dinlenme)."""
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_list"][0]
    a, b = 30, 30 + 20 * m
    for x in (a, b):
        _tg_direk(S, x)
    S.figur(hk_donuslu_kos([a + 4, b - 4, a + 30], s=0.8, dokun=False, baslangic="kos"))
    _tg_periyot_seridi(S, [(15, True)] * 5, x0=248 - 75 * 1.1, y=20, olcek=1.1, imlec=[(0, 0), (1, 0.06)])
    S.baslik("Yürü → koş → hızlı koş → sprint → dinlen")
    S.olcu(a, 32, b, 32, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(a, TG_ZEMIN - 7, a, 32), (b, TG_ZEMIN - 7, b, 32)])
    S.not_("5 × 15 dk bölüm (toplam 75 dk), 20 m alan", t=0.05)
    return S


def _tg_30_15():
    """
    30-15 IFT: 40 m; 30 sn koşu (mekik) + 15 sn yürüme. Zaman çubuğunda koşu blokları her aşamada YÜKSELİR
    (hız +0,5 km/h) — Yo-Yo'da ise koşu blokları kısalır, dinlenme sabittir: iki testin farkı şeritte görünür.
    """
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_30_15"][0]
    a, b = 36, 36 + 40 * m
    for x in (a, b):
        _tg_direk(S, x)
    for x in (a + 3 * m, b - 3 * m):                   # 3 m güvenlik bölgeleri
        S.esya(S.cizgi(x, TG_ZEMIN, x, TG_ZEMIN - 22, "kilavuz"), tur="isaret")
    kos = hk_donuslu_kos([a + 4, b - 6], s=0.7, dokun=False, baslangic="kos", t1=0.7)
    yuru = hk_donuslu_kos([b - 6, b - 30], s=0.7, dokun=False, baslangic="kos", t0=0.72)
    S.figur(TgHareket(kos.anahtarlar + yuru.anahtarlar, {}))
    parca = [p for i in range(5) for p in ((30, True, 0.6 + 0.2 * i), (15, False, 0.4))]   # yürüme alçak, koşu yükselir
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.6, imlec=[(0, 0), (0.7, 30 / 225), (1.0, 45 / 225)])
    S.baslik("30 sn koşu / 15 sn yürüme; hız artarak")
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, "40 m", uc="ilk", metre=40)        # zeminde, çizgiler arası
    S.not_("Başlangıç 8 km/h, her aşamada +0,5 km/h", t=0.05)
    return S


def _tg_parkur_bacaklari(S, noktalar):
    """
    Merkezden çıkıp merkeze dönen güzergâh (Spider, Paket 24): her gidiş-dönüş (merkez → hedef → merkez) yalnız
    figür o bacaktayken görünür (goster t0–t1); son bacak sona kadar kalır (durağan kopyada o görünür). Zamanlar
    hk_kavisli_yol(yumusak=False) ile aynı: süre güzergâh uzunluğuyla orantılı.
    """
    uz = [0.0]
    for a, b in zip(noktalar, noktalar[1:]):
        uz.append(uz[-1] + _math.dist(a, b))
    for i in range(0, len(noktalar) - 2, 2):
        d = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(noktalar[i:i + 3]))
        t0 = uz[i] / uz[-1]
        t1 = uz[i + 2] / uz[-1] if i + 2 < len(noktalar) - 1 else None
        S.goster(f'<path d="{d}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
                 f'stroke-dasharray="3 2" stroke-linecap="round"/>', t0, t1, tur="isaret")
        S.bacaklar.append((t0, 1.0 if t1 is None else t1))


def _tg_parkur(tur, baslik, notu, isaret_yazi=None, isaret_yeri=(150, 52), serit=None):
    """
    Çeviklik parkuru (Illinois, VAT, NBA Lane, Hentbol, T-testi, Ghost Drill): yandan görünüş; güzergâh zemin
    çizgisi boyunca, derinlik ince şeritte. Dönüş noktaları SIRA NUMARALI (Paket 19): aynı yerden birden çok kez
    dönülüyorsa numaralar o noktanın üstünde alt alta durur (ör. Illinois sağ uç: 1, 3, 5). serit: zaman çubuğu.
    """
    d = _TG_PARKURLAR[tur]
    S = TgSahne(7.0)
    P = _tg_zemin_seridi(d["x0"], *d["olcek"])
    noktalar = [P(*n) for n in d["yol"]]
    h = hk_kavisli_yol(noktalar, s=d["s"], kip="kos", yumusak=False, baslangic=d["baslangic"], dokun=d["dokun"])
    if d.get("tek_tek"):
        _tg_parkur_bacaklari(S, noktalar)
    else:
        S.yol(h.olay["yol"])
    for x, y in sorted((P(*k) for k in d["koniler"]), key=lambda q: q[1]):     # arkadaki koni önce
        _tg_koni(S, x, y)
    for x, y in noktalar[1:-1]:                                                   # dönüş noktaları
        S.esya(S.nokta(x, y, 1.6), tur="isaret")
    ust = min(y for _, y in noktalar) - 8                                         # numara sütunları güzergâhın üstünde
    orta = sum(x for x, _ in noktalar) / len(noktalar)
    sutun = []                                                                     # [(x, kaç numara)]
    for n, (i, (rx, ry)) in enumerate(zip(d["donus"], d.get("rozet", ()))):    # rozet: noktanın yanında, ayrık
        S.numara(noktalar[i][0] + rx, noktalar[i][1] + ry, n + 1)
    for n, i in enumerate(() if d.get("rozet") else d["donus"], 1):
        x, _ = noktalar[i]
        x += -9 if x <= orta else 9                    # sütun noktanın dış yanında: figür numaranın üstüne binmesin
        j = next((k for k, (sx, _) in enumerate(sutun) if abs(sx - x) < 10), None)
        if j is None:
            sutun.append((x, 0))
            j = len(sutun) - 1
        sx, kac = sutun[j]
        S.numara(sx, ust - 10 * kac, n)
        sutun[j] = (sx, kac + 1)
    if serit:
        _tg_periyot_seridi(S, serit[0], x0=12, y=22, olcek=serit[1])
    for t, x, y in h.olay["dokunma"]:
        S.belir(S.nokta(x, y, 2.6, dolu=True), t, tur="isaret")
    S.figur(h)
    S.baslik(baslik)
    if isaret_yazi:
        bx, by = noktalar[0]
        S.isaret(isaret_yazi, (bx, by), isaret_yeri, hiza="start", t=0.02)
    S.not_(notu, t=0.6)
    return S


def _tg_sicrama_turleri(turler, baslik, notu, bekleme=None):
    """
    CMJ / SJ / DJ yan yana (soldan), her varyant için TEK figür; durağan karede her biri kendi ayırt edici anında
    (Paket 18): CMJ ön-çömelmenin en alt noktası + aşağı-yukarı ok; SJ 90° statik çömelme + diz açısı ve bekleme
    işareti (protokol süre veriyorsa etiketle, ör. "2 sn bekleme"), çöküş oku yok; DJ kutudan düşüş anı + düşüş yolu.
    """
    S = TgSahne(2.4)
    s = 0.7
    m = TG_OLCEK["_tg_sicrama_turleri"][0]
    yer = {"CMJ": 40, "SJ": 102} if "DJ" in turler else {"CMJ": 80, "SJ": 176}
    ok = TG_RENK["olcu"]
    for t in turler:
        if t == "DJ":
            yuk = 0.3 * m
            sol, sag = 162, 186
            S.esya(S.kutu(sol, TG_ZEMIN - yuk, sag - sol, yuk, rx=1))
            h = hk_sicrama_ani((sol + sag) / 2, "dj", s=s, kutu=(sol, sag, yuk))
            a, b, c = h.olay["dusus_yolu"]
            S.belir(f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{b[0]:.1f},{a[1] - 2:.1f} {b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f}" '
                    f'fill="none" stroke="{ok}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.6,
                    tur="isaret")
            hx_, hy_ = h.olay["kalca"]
            S.belir(S.cizgi(hx_ + 22, hy_ - 10, hx_ + 22, hy_ + 14, "olcu", ok="son"), 0.9, tur="isaret")   # düşüş: aşağı ok
        else:
            h = hk_sicrama_ani(yer[t], t.lower(), s=s)
        S.figur(h)
        kx, ky = h.olay["kalca"]
        if t == "CMJ":                       # çök-sıçra: kalçanın yanında aşağı-yukarı ok
            y0, y1 = h.olay["kalca_yolu"]
            S.belir(S.cizgi(kx + 24, y0 - 6, kx + 24, y1 + 8, "olcu", ok=True), 0.9, tur="isaret")
        elif t == "SJ":                      # 90° diz açısı yayı + bekleme (iki dikey çizgi), çöküş oku yok
            dx, dy = h.olay["diz"]
            r = 6
            ua = _math.atan2(kx - dx, ky - dy)
            ba = _math.atan2(h.olay["ayak"][0] - dx, h.olay["ayak"][1] - dy)
            p1 = (dx + r * _math.sin(ua), dy + r * _math.cos(ua))
            p2 = (dx + r * _math.sin(ba), dy + r * _math.cos(ba))
            S.esya(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} Q{dx + 1.4 * r * _math.sin((ua + ba) / 2):.1f},'
                   f'{dy + 1.4 * r * _math.cos((ua + ba) / 2):.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{ok}" '
                   f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>', tur="isaret")
            S.esya(S.cizgi(kx + 22, ky - 30, kx + 22, ky - 18, "vurgu") + S.cizgi(kx + 29, ky - 30, kx + 29, ky - 18, "vurgu"),
                   tur="isaret")                                                   # bekleme (duraklat) işareti
            if bekleme:
                S.isaret(bekleme, (kx + 25.5, ky - 30), (kx + 30, ky - 48), hiza="start", t=0.3)
    S.baslik(baslik)
    if "DJ" in turler:
        S.olcu(156, TG_ZEMIN, 156, TG_ZEMIN - 0.3 * m, "30 cm", metre=0.3, etiket_yer="sol", t=0.05)
    S.not_(notu, t=0.4)
    return S


def _tg_nordic():
    """Nordic hamstring (NordBord): diz üstü, bilekler kancada; gövde yavaşça öne. Kanca kuvveti ölçer (her bacak)."""
    S = TgSahne(4.0)
    tahta = TG_ZEMIN - 4
    S.esya(S.kutu(50, tahta, 128, 4, rx=1))
    h = hk_nordic(124, tahta - 2, s=0.9)
    bx, by = h.olay["bilek"]
    S.esya(S.cizgi(bx - 3, tahta, bx - 3, by - 5) + S.kutu(bx - 6, by - 6.5, 7, 3, dolgu="yuzey", rx=1))   # kanca + sensör
    S.figur(hk_iz(h))                     # başlangıç: dik diz üstü
    S.figur(h)
    S.baslik("Diz üstü, bilekler sabit; gövde yavaşça öne")
    S.isaret("Pik kuvvet (N)", (bx - 3, by - 6.5), (172, 50), hiza="start", t=0.1)
    S.not_("3 tekrar, her bacak ayrı; en yüksek değer", t=0.6)
    return S


def _tg_diz_dinamometre():
    """İzokinetik dinamometre: koltuk, cihaz başı diz ekseninde, kol kavala bağlı; 90° / 45° kılavuzları."""
    S = TgSahne(5.0)
    kx, ky = 96, TG_ZEMIN - 44
    h = hk_dinamometre(kx, ky)
    dx, dy = h.olay["diz"]
    L = _TG_BOY["baldir"]
    S.esya(S.kutu(66, ky + 3, 38, 5, rx=1) + S.cizgi(72, ky + 8, 72, TG_ZEMIN) + S.cizgi(98, ky + 8, 98, TG_ZEMIN)
           + S.cizgi(68, ky + 3, 60, ky - 36))                                       # koltuk + sırtlık
    S.esya(S.cizgi(dx - 8, dy + 6, dx - 8, TG_ZEMIN) + S.cizgi(dx - 16, TG_ZEMIN, dx, TG_ZEMIN)
           + f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="7" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{TG_KALINLIK["esya"]}"/>')                             # cihaz başı diz ekseninde
    for aci in (0, 45):                                                               # 90° ve 45° fleksiyon kılavuzu
        r = _math.radians(aci)
        S.esya(S.cizgi(dx, dy, dx + L * _math.sin(r), dy + L * _math.cos(r), "kilavuz"), tur="isaret")
    S.cubuk(dx, dy, h.olay["ayak_yolu"])
    S.figur(h)
    S.baslik("Diz 90° ve 45°'de izometrik, 180°/sn izokinetik")
    S.isaret("Pik tork (Nm/kg)", (dx, dy - 7), (150, 44), hiza="start", t=0.05)
    S.not_("Her iki bacak; H:K oranı ve asimetri", t=0.6)
    return S


# ── Branşa özgü sahneler, 3. parti (Paket 18): mücadele sporları ──
def _tg_minder(S, x0=40, x1=246):
    S.esya(S.kutu(x0, TG_ZEMIN - 3, x1 - x0, 3, rx=1))


def _tg_sjft_judo():
    """
    Judo SJFT: iki uke 6 m arayla (ikinci kişi rengi), tori ortadan başlar; A, B, C periyotlarında birer atış
    gösterilir (sağ → sol → sağ). Zaman çubuğu 15/10/30/10/30 sn; her aktif bloğun altında periyot sayacı.
    """
    S = TgSahne(7.0)
    m = TG_OLCEK["_tg_sjft_judo"][0]
    x_sol, x_sag = 70, 70 + 6 * m
    _tg_minder(S, 30, 250)
    h = hk_iki_uke_atis(x_sol, x_sag, s=0.7)
    for u in h.olay["ukeler"]:
        S.figur(u)
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(15, True), (10, False), (30, True), (10, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=1.0)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(atis, bloklar):
        S.sayac((xa + xb) / 2 - 6, 34, [t], boy=14)
    S.baslik("İki uke 6 m arayla; tori ortadan koşup atar")
    ilk = S.sayaclar[-1]
    S.isaret("Periyot başına atış", (ilk[2], (ilk[1] + ilk[3]) / 2), (110, 42), hiza="start", t=atis[0])
    S.not_("A 15 sn, B 30 sn, C 30 sn; aralarda 10 sn dinlenme")
    return S


def _tg_ukft():
    """UKFT: tutuş, giriş-çıkış tekrarı (atış yok); 3 × 30 sn set, 30 sn dinlenme; set başına giriş sayacı."""
    S = TgSahne(5.0)
    _tg_minder(S, 70, 230)
    h = hk_uchikomi(140, tekrar=3, s=0.8)
    S.figur(h.olay["partner"])
    S.figur(h)
    giris = h.olay["giris_anlari"]
    parca = [(30, True), (30, False), (30, True), (30, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.7)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(giris, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(giris, bloklar):
        S.sayac((xa + xb) / 2 - 6, 34, [t], boy=14)
    S.baslik("Tutuş alınır, giriş-çıkış tekrarlanır; atış yok")
    ilk = S.sayaclar[0]
    S.isaret("Set başına giriş", ((ilk[0] + ilk[2]) / 2, ilk[3]), (12, 70), hiza="start", t=giris[0])
    S.not_("3 × 30 sn set, aralarında 30 sn dinlenme")
    return S


def _tg_vurus(teknikler, baslik, notu, sayac_yazi, parca, olcek, hedef=None):
    """
    Vuruş protokolleri (TSAT, KSDT, MTSDT, KSKT, Boks): tek çizim, parametreyle ayrışır — teknik dizisi (tekme
    yüksekliği tekniğin kendisinden: dollyo baş, roundhouse/geri gövde), hedef ("torba": kum torbası; "ped": ayaklı
    tekme pedi, yüksekliği son tekniğin erişim noktasında — branşa göre parametre) ve tempo (zaman çubuğu).
    Sayaç vuruşları çeteleyle sayar.
    """
    S = TgSahne(5.0)
    x = 166
    h = hk_vurus(x, teknikler, s=0.75)
    ex, ey = h.olay["erisim"]
    if hedef == "torba":                         # tavana asılı kum torbası; ön yüzü son vuruşun erişim noktasında
        S.esya(S.cizgi(ex + 8, 21, ex + 8, 30) + S.kutu(ex + 1, 30, 14, 66, rx=4))
        S.hedefler.append(("torba", ex + 8, 63))
    elif hedef == "ped":                         # ayaklı tekme pedi; yüksekliği son tekniğin erişim noktası
        S.esya(S.cizgi(ex + 9, TG_ZEMIN, ex + 9, ey + 9) + S.kutu(ex + 1, ey - 9, 10, 18, rx=3))
        S.hedefler.append(("ped", ex + 6, ey))
    S.figur(h)
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=olcek)
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, h.olay["darbe_anlari"], boy=16)
    S.baslik(baslik)
    S.isaret(sayac_yazi, (sx1, (sy0 + sy1) / 2), (36, 76), hiza="start", t=h.olay["darbe_anlari"][0])
    S.not_(notu)
    return S


def _tg_mac(parca, olcek, baslik, sure_yazi, notu):
    """Simüle maç (Güreş, Sambo, MMA, BJJ): iki sporcu tutuşta (rakip ikinci kişi renginde); tur yapısı şeritte."""
    S = TgSahne(3.6)
    S.esya(f'<ellipse cx="150" cy="{TG_ZEMIN - 1}" rx="92" ry="4.5" fill="{TG_RENK["dolgu"]}" '
           f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(hk_ikinci_figur(hk_tutus(168, yon=-1)))
    S.figur(hk_tutus(132, yon=1))
    x0, x1, y, _ = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=olcek, imlec=[(0, 0), (1, 1)])
    S.baslik(baslik)
    S.isaret(sure_yazi, ((x0 + x1) / 2, y + 6), (12, 52), hiza="start")
    S.not_(notu)
    return S


def _tg_asilma(baslik, notu):
    """Gi/kurtka yakasından asılı kalma (BJJ, Sambo): bar, yakalar, asılı sporcu; süreölçer saniye sayar."""
    S = TgSahne(5.0)
    x, bar_y, tut_y = 110, 26, 34
    S.esya(S.cizgi(74, TG_ZEMIN, 74, bar_y) + S.cizgi(146, TG_ZEMIN, 146, bar_y) + S.cizgi(70, bar_y, 150, bar_y))
    S.esya(f'<path d="M{x - 9},{bar_y} L{x - 3},{tut_y + 2} M{x + 9},{bar_y} L{x + 3},{tut_y + 2}" fill="none" '
           f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["vurgu"]}" stroke-linecap="round"/>')   # yakalar
    h = hk_asilma(x, tut_y, s=0.75)
    S.figur(h)
    kx0, ky0, kx1, ky1 = S.kronometre(206, 76, t0=0.25)
    S.baslik(baslik)
    S.isaret("Asılma süresi (sn)", ((kx0 + kx1) / 2, ky0), (162, 46), hiza="start", t=0.25)
    S.not_(notu)
    return S


def _tg_yan_adim():
    """Masa tenisi yan adım: 3 m sağ-sol, 15 sn; önden görünüş."""
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_yan_adim"][0]
    a, b = 92, 92 + 3 * m
    for x in (a, b):
        _tg_direk(S, x)
    S.figur(hk_yan_adim(a + 6, b - 6, tekrar=3, s=0.8))
    _tg_periyot_seridi(S, [(15, True)], x0=12, y=22, olcek=2.0, imlec=[(0, 0), (1, 1)])
    S.baslik("Yan adım: 3 m sağ-sol, 15 sn")
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, "3 m", uc="son", metre=3)
    S.not_("Reaksiyon: 20 deneme · masa başı vuruş: 30 sn")
    return S


# ── Çocuk ve genç fiziksel uygunluk bataryaları (Paket 19) ──
def _tg_mat(S, x0, x1):
    S.esya(S.kutu(x0, TG_ZEMIN - 2, x1 - x0, 2, rx=1))


def _tg_uzun_atlama(baslik, notu, etiket="Mesafe (cm)"):
    """Durarak uzun atlama (Eurofit, ALPHA, PREFIT, CNPFM, Latorre, CAPL): çizgi, iniş; ok çizgiden en geri topuğa."""
    S = TgSahne(3.0)
    cizgi = 90
    _tg_direk(S, cizgi)
    h = hk_uzun_atlama(cizgi, 96, s=0.8)
    S.figur(h)
    S.baslik(baslik)
    S.olcu(cizgi, TG_OLCU_Y, h.olay["topuk_x"], TG_OLCU_Y, etiket, uc="ilk", t=0.95,
           bag=[(1, "x", ("ayak1", "ayak2"), "min")])
    S.not_(notu, t=0.3)
    return S


def _tg_mekik_kosusu(mesafe, baslik, notu, gidis=4, blok=False):
    """Kısa mekik koşusu (10 × 5 m, 4 × 10 m, 8 × 25 m): iki çizgi arası dönüşlü koşu; ok şematik, mesafe etikette."""
    S = TgSahne(4.0)
    a, b = 44, 222
    for x in (a, b):
        _tg_direk(S, x)
    if blok:                                              # sünger bloklar: dönüşte biri alınıp karşıya taşınır
        S.esya("".join(S.kutu(x - 3, TG_ZEMIN - 5, 6, 5, dolgu="yuzey", rx=1) for x in (a - 10, a - 18)))
    duraklar = [a + 4] + [b - 4 if i % 2 == 0 else a + 4 for i in range(gidis)]
    S.figur(hk_donuslu_kos(duraklar, s=0.75, dokun=blok, baslangic="kos"))
    S.baslik(baslik)
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, mesafe, uc="son")
    S.not_(notu, t=0.05)
    return S


def _tg_otur_uzan(baslik, notu, sifir_cm, tek_bacak=False):
    """
    Otur-uzan varyantları. Cetvelin SIFIR NOKTASI varyantın kendi protokolünden çizilir (varsayılan yok):
    sifir_cm = ayak tabanı hizasının ölçekteki değeri (Eurofit 15, FitnessGram/ALPHA Back-Saver 22,9, CNPFM 0).
    Sıfır, ayak tabanının bu kadar gerisindedir (gövdeye doğru); ok sıfırdan ayak tabanına. tek_bacak: Back-Saver.
    """
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_otur_uzan"][0]
    z, ayak = TG_ZEMIN, 170
    sifir = ayak - sifir_cm / 100 * m
    S.esya(S.kutu(ayak, z - 20, 50, 20))
    S.esya(S.cizgi(min(sifir, ayak) - 8, z - 21, 240, z - 21)
           + "".join(S.cizgi(x, z - 24, x, z - 21) for x in range(int(min(sifir, ayak)) - 6, 240, 6)))
    S.esya(S.cizgi(sifir, z - 27, sifir, z - 21, "vurgu"), tur="isaret")          # ölçeğin sıfırı
    h = hk_oturarak_uzanma(ayak, tek_bacak=tek_bacak)
    S.figur(h)
    el = h.olay["el"][0]
    S.kaydir(S.kutu(176, z - 28, 5, 7, dolgu="yuzey", rx=1),
             [(0, 0, 0), (0.45, 0, 0), (0.8, el - 178.5, 0), (1, el - 178.5, 0)])
    S.baslik(baslik)
    if sifir_cm:
        yazi = f"{sifir_cm:g} cm".replace(".", ",")
        S.olcu(sifir, z - 46, ayak, z - 46, yazi, uc="son", metre=sifir_cm / 100,
               kilavuzlar=[(sifir, z - 27, sifir, z - 46), (ayak, z - 21, ayak, z - 46)])
    else:
        S.isaret("Sıfır: ayak tabanı", (sifir, z - 27), (sifir - 40, z - 52), hiza="end", t=0.05)
    S.not_(notu, t=0.3)
    return S


def _tg_govde_fleksiyonu(tur, baslik, notu, isaret="Tekrar sayısı"):
    """Mekik (sit-up) ve curl-up: mat, figür, tekrarları sayan çetele. Curl-up'ta parmak ucu ölçüm şeridini aşar."""
    S = TgSahne(3.4)
    _tg_mat(S, 70, 210)
    h = hk_mekik(140, tur, tekrar=2, s=0.85)
    if tur == "curlup":                                   # ölçüm şeridi: parmak uçlarının altında
        (x0, _), (x1, _) = h.olay["el_yolu"]
        S.esya(S.kutu(min(x0, x1) - 1, TG_ZEMIN - 3.5, abs(x1 - x0) + 2, 1.5, dolgu="yuzey", rx=0.5))
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret(isaret, (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_sinav(baslik, notu, diz=False):
    """Şınav (FitnessGram, PYFP) ve diz üstü şınav (BOT-2): alt nokta dirsek 90°; çetele tekrarları sayar."""
    S = TgSahne(3.0)
    _tg_mat(S, 60, 220)
    h = hk_sinav(140, s=0.85, diz=diz)
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_modifiye_barfiks(baslik, notu):
    """Modified pull-up: alçak bar (uçtan görünüş), sırtüstü düz vücut, çene bara; çetele tekrarları sayar."""
    S = TgSahne(3.0)
    h = hk_modifiye_barfiks(206, s=0.85)
    bx, by = h.olay["bar"]
    S.esya(S.cizgi(bx, TG_ZEMIN, bx, by + 3) + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="{TG_RENK["esya"]}"/>')
    bant = by + 0.19 * TG_OLCEK["_tg_modifiye_barfiks"][0]       # elastik bant bardan 7-8 inç (18-20 cm) aşağıda
    S.esya(f'<circle cx="{bx:.1f}" cy="{bant:.1f}" r="1.3" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_plaka(S, yol, r=7.0):
    """Bar ucundaki plaka diski (yandan): yol [(t, x, y)] boyunca kayar (halter ile aynı çizim)."""
    b0 = yol[0]
    S.kaydir(f'<circle cx="{b0[1]:.1f}" cy="{b0[2]:.1f}" r="{r}" fill="{TG_RENK["dolgu"]}" '
             f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>',
             [(t, x - b0[1], y - b0[2]) for t, x, y in yol])


def _tg_bench_press(baslik, notu):
    """1RM bench press: sehpa + bar dikmesi; bar göğse iner, kollar tam açılır; spotçu barın başında (ikinci figür)."""
    S = TgSahne(3.0)
    s, sehpa_y = 0.85, TG_ZEMIN - 18
    h = hk_bench_press(150, sehpa_y, s=s)
    bas_x = h.olay["bas"][0]
    S.esya(S.kutu(bas_x - 6, sehpa_y, 150 - bas_x + 14, 3.5, rx=1)
           + S.cizgi(bas_x + 2, sehpa_y + 3.5, bas_x + 2, TG_ZEMIN) + S.cizgi(156, sehpa_y + 3.5, 156, TG_ZEMIN))
    ust_y = min(y for _, _, y in h.olay["bar"])
    dx = bas_x - 9
    S.esya(S.cizgi(dx, TG_ZEMIN, dx, ust_y + 4) + S.cizgi(dx, ust_y + 4, dx + 4, ust_y + 4))   # bar dikmesi (kanca)
    S.figur(h.olay["spotcu"])                                               # spotçu: barın başında, eller hazır
    _tg_plaka(S, h.olay["bar"])
    S.figur(h)
    S.baslik(baslik)
    sb = h.olay["spotcu_bas"]
    S.isaret("Spotçu", (sb[0] - 5, sb[1] - 4), (sb[0] - 30, 38), hiza="middle", t=0.0)
    S.not_(notu)
    return S


def _tg_arka_comelme(baslik, notu):
    """1RM arka çömelme: kafes (iki dikme + güvenlik demiri), bar üst sırtta; diz açısı 90°'yi geçene kadar."""
    S = TgSahne(3.0)
    s, xa = 0.85, 140
    h = hk_arka_comelme(xa, s=s)
    alt_y = h.olay["bar"][-1][2]
    ust_y = h.olay["bar"][0][2]
    arka = xa - 52                                                            # kafes dikmesi (yandan: dikmeler üst üste)
    demir = alt_y + 9.5                                                       # güvenlik demiri: en alt noktanın hemen altında
    S.esya(S.cizgi(arka, TG_ZEMIN, arka, ust_y - 8) + S.cizgi(arka - 3, demir, xa + 20, demir))
    S.figur(hk_iz(h))                                                         # başlangıç: dik duruş
    _tg_plaka(S, h.olay["bar"])
    S.figur(h)
    S.baslik(baslik)
    dx_, dy_ = h.olay["diz"]
    S.isaret("Diz 90°'yi geçer", (dx_, dy_), (176, 58), hiza="start", t=0.98)
    S.not_(notu)
    return S


def _tg_leg_press(baslik, notu):
    """1RM leg press (45° kızak): minder, ray, platform + plaka; platform belirlenen derinliğe iner, bacaklar açılır."""
    S = TgSahne(3.2)
    s = 0.85
    kalca = (92, TG_ZEMIN - 22)
    h = hk_leg_press(kalca, s=s)
    rx, ry = h.olay["ray"]
    px, py = -ry, rx                                                          # rayya dik (aşağı-sağ)
    hx, hy = kalca
    boyun = h.olay["boyun"]
    # oturak ve sırt minderi (kalçanın altından boyun gerisine), gövde çerçevesi
    S.esya(S.cizgi(hx - 4, hy + 4, hx + 8, hy + 4) + S.cizgi(hx - 4, hy + 4, boyun[0] - 3, boyun[1] + 3)
           + S.cizgi(hx + 2, hy + 4, hx + 2, TG_ZEMIN) + S.cizgi(hx - 30, TG_ZEMIN, 236, TG_ZEMIN, "esya"))
    a0 = (hx + rx * 26 + px * 7, hy + ry * 26 + py * 7)                    # ray: platformun alt ucunun altından
    a1 = (hx + rx * 72 + px * 7, hy + ry * 72 + py * 7)
    S.esya(S.cizgi(*a0, *a1) + S.cizgi(a1[0], a1[1], a1[0], TG_ZEMIN))     # ray + arka dikme
    S.cubuk_iki(h.olay["platform"], kalinlik="vurgu")
    plaka = [(t, (x1 + x2) / 2 + rx * 7 + px * 2, (y1 + y2) / 2 + ry * 7 + py * 2)
             for t, x1, y1, x2, y2 in h.olay["platform"]]
    S.figur(hk_iz(h, sira=h.olay["alt"]))                                     # belirlenen derinlik
    _tg_plaka(S, plaka, r=6.0)
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_barfiks(baslik, notu):
    """Genel barfiks: _tg_modifiye_barfiks'in yüksek bar, bantsız varyantı (bar uçtan görünüş, dikmeye bağlı); çetele."""
    S = TgSahne(3.0)
    bar_y = 30
    h = hk_modifiye_barfiks(160, s=0.8, asili=True, bar_y=bar_y)
    bx, by = h.olay["bar"]
    dikme = bx + 34
    S.esya(S.cizgi(bx, by, dikme, by) + S.cizgi(dikme, by, dikme, TG_ZEMIN)
           + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="{TG_RENK["esya"]}"/>')
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_sargent(baslik, notu):
    """
    Sargent: duvar (önden, sporcunun yanında), ayakta erişimde alt tebeşir izi, zirvede üst iz; iki iz arası ölçü
    oku. Ok şematiktir (figür ölçeği 0,85; tuvale sığsın diye sıçrama yüksekliği küçük çizilir).
    """
    S = TgSahne(3.4)
    dx = 146
    h = hk_sargent(dx, s=0.85)
    (_, ya), (_, yu) = h.olay["alt_iz"], h.olay["ust_iz"]
    S.esya(S.kutu(dx, 20.5, 6, TG_ZEMIN - 20.5, dolgu="dolgu", rx=0.5))                 # duvar
    S.belir(S.cizgi(dx - 3, ya, dx + 6, ya, "olcu"), h.olay["alt_t"], tur="isaret")     # alt iz: ayakta erişim
    S.belir(S.cizgi(dx - 3, yu, dx + 6, yu, "olcu"), 0.99, tur="isaret")               # üst iz: sıçrama
    S.figur(h)
    S.baslik(baslik)
    S.olcu(dx + 14, ya, dx + 14, yu, "Sıçrama yüksekliği", t=0.99,
           kilavuzlar=[(dx + 6, ya, dx + 14, ya), (dx + 6, yu, dx + 14, yu)], bag=[(1, "y", ("el1",), "min")])
    S.not_(notu)
    return S


def _tg_govde_kaldirma(baslik, notu):
    """
    Trunk lift: yüzüstü, üst gövde kalkar; dikey ok yerden ÇENEYE (son kare). Yerdeki işaret göz hizasındadır ama
    yalnız başı nötr tutmak içindir — ölçüm noktası değildir (Paket 20: önceki sürüm göze ölçüyordu).
    """
    S = TgSahne(3.0)
    _tg_mat(S, 6, 96)
    h = hk_govde_kaldirma(58, s=0.9)
    e = S.figur(h)
    cx, cy = e["cene"]
    bx = e["bas"][0]
    S.baslik(baslik)
    S.olcu(bx + 16, TG_ZEMIN, bx + 16, cy, "Çeneye kadar (en çok 30,5 cm)", t=0.85,
           kilavuzlar=[(cx + 2, cy, bx + 16, cy)], bag=[(1, "y", ("cene",), "min")])
    S.not_(notu)
    return S


def _tg_bukumlu_asilma(baslik, notu):
    """Bent Arm Hang: yüksek bar, avuçlar öne, çene barın üstünde, dirsekler bükük; süreölçer."""
    S = TgSahne(5.0)
    x, bar_y = 112, 36
    S.esya(S.cizgi(84, TG_ZEMIN, 84, bar_y) + S.cizgi(140, TG_ZEMIN, 140, bar_y) + S.cizgi(80, bar_y, 144, bar_y))
    S.figur(hk_asilma_bukumlu(x, bar_y, s=0.8))
    kx0, ky0, kx1, ky1 = S.kronometre(214, 84, t0=0.3)
    S.baslik(baslik)
    S.isaret("Asılı kalma süresi", ((kx0 + kx1) / 2, ky0), (158, 56), hiza="start", t=0.3)
    S.not_(notu)
    return S


def _tg_flamingo(baslik, notu, kiris=False, tutar=True):
    """Tek ayak denge (Eurofit kirişte, PREFIT ve Latorre yerde): bir denge kaybı ve çetelesi."""
    S = TgSahne(4.0)
    m = TG_OLCEK["_tg_flamingo"][0]
    taban = TG_ZEMIN
    if kiris:                                             # 50 cm × 4 cm kiriş
        yuk, uz = 0.04 * m, 0.5 * m
        S.esya(S.kutu(170 - uz / 2, TG_ZEMIN - yuk, uz, yuk, rx=0.5))
        taban = TG_ZEMIN - yuk
    h = hk_flamingo(170, s=0.85, tutar=tutar, zemin=taban)
    S.figur(h)
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, [h.olay["kayip_t"]])
    S.baslik(baslik)
    S.isaret("Denge kaybı sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=h.olay["kayip_t"])
    S.not_(notu)
    return S


def _tg_plate_tapping(baslik, notu):
    """Plate tapping (önden): masa, 60 cm arayla iki disk, ortada plaka; baskın el disklere sırayla dokunur."""
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_plate_tapping"][0]
    x, masa = 130, TG_ZEMIN - 0.7 * m
    dx = 0.3 * m
    S.esya(S.cizgi(x - 68, masa, x + 68, masa) + S.cizgi(x - 62, masa, x - 62, TG_ZEMIN) + S.cizgi(x + 62, masa, x + 62, TG_ZEMIN))
    r = 0.1 * m
    S.esya("".join(f'<ellipse cx="{x + k * dx:.1f}" cy="{masa - 1:.1f}" rx="{r:.1f}" ry="1.6" fill="{TG_RENK["dolgu"]}" '
                   f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>' for k in (-1, 1))
           + S.kutu(x - 6, masa - 2.5, 6, 1.5, dolgu="yuzey", rx=0.5))
    h = hk_masa_dokunma(x, masa, dx, s=0.9)
    S.figur(h)
    S.baslik(baslik)
    S.olcu(x - dx, masa + 14, x + dx, masa + 14, "60 cm", uc="ilk", metre=0.6,
           kilavuzlar=[(x - dx, masa + 2, x - dx, masa + 14), (x + dx, masa + 2, x + dx, masa + 14)])
    S.not_(notu)
    return S


def _tg_omuz_esneme(baslik, notu):
    """Shoulder stretch (arkadan): bir el omuz üstünden, öbürü bel altından; parmak uçları sırtta buluşur mu."""
    S = TgSahne(3.0)
    h = hk_omuz_esneme(110, s=0.95)
    S.figur(h)
    S.baslik(baslik)
    S.isaret("Parmak uçları değerse: geçti", h.olay["bulusma"], (150, 56), hiza="start", t=0.9)
    S.not_(notu)
    return S


def _tg_omuz_rotasyon(baslik, notu):
    """Omuz rotasyonu (sopa/ip): kollar düz, sopa önden baş üstünden sırta; elin izlediği yay kesik çizgi."""
    S = TgSahne(3.6)
    h = hk_omuz_rotasyon(120, s=0.75)
    S.yol(h.olay["el_yolu"])
    S.figur(h)
    yol = h.olay["el_yolu"]
    x0, y0 = yol[0]
    S.kaydir(S.cizgi(x0 - 4, y0, x0 + 4, y0, "vurgu"),
             [(i / (len(yol) - 1), x - x0, y - y0) for i, (x, y) in enumerate(yol)])
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_top_sektirme(baslik, notu):
    """Alternatif elle top sektirme (BOT-2): top elden yere, yerden öbür ele; çetele doğru sektirmeleri sayar."""
    S = TgSahne(3.6)
    h = hk_top_sektirme(170, s=0.85)
    S.figur(h)
    yol = h.olay["top_yolu"]
    S.top(yol, r=2.4)
    anlar = [t for t, _, y in yol if y > TG_ZEMIN - 4][:4]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru sektirme sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_top_yakalama(baslik, notu):
    """KMS top yakalama: uygulayıcı (ikinci kişi) 1,5 m'den atar, çocuk iki eliyle yakalar."""
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_top_yakalama"][0]
    xc, xa = 84, 84 + 1.5 * m
    h = hk_top_yakala(xc, xa)
    S.figur(h.olay["atan"])
    S.figur(h)
    S.top(h.olay["top_yolu"], r=3.2)
    S.baslik(baslik)
    S.olcu(xc, TG_OLCU_Y, xa, TG_OLCU_Y, "1,5 m", uc="son", metre=1.5)
    S.not_(notu)
    return S


def _tg_top_firlatma(baslik, notu):
    """Latorre top fırlatma: çizgi gerisinden iki elle baş üzerinden ileri; ok çizgiden düşüşe (üstte, kılavuzlu)."""
    S = TgSahne(3.0)
    cizgi = 70
    _tg_direk(S, cizgi)
    h = hk_atma(cizgi - 10, "ileri", s=0.75)
    S.figur(h)
    (_, x0, y0) = h.olay["el_yolu"][-1]
    dusus = 214
    ucus = _tg_parabol(x0, y0, dusus, TG_ZEMIN - 3, 20, h.olay["birakma_t"], 0.92)
    S.top(h.olay["el_yolu"] + ucus[1:], r=3.6)
    S.baslik(baslik)
    S.olcu(cizgi, 34, dusus, 34, "Fırlatma mesafesi", etiket_yer="orta", t=0.93,
           kilavuzlar=[(cizgi, TG_ZEMIN - 6, cizgi, 34), (dusus, TG_ZEMIN - 8, dusus, 34)])
    S.not_(notu)
    return S


def _tg_capl_genel(baslik, notu):
    """CAMSA — GENEL GÖRÜNÜM (durağan kopya): yedi beceri yan yana, sıra numaralı; figür 3. beceride (yakalama)."""
    S = TgSahne(3.0)
    Z, k = TG_ZEMIN, TG_KALINLIK["esya"]
    cember = lambda x: (f'<ellipse cx="{x:.1f}" cy="{Z - 1}" rx="4" ry="1.4" fill="none" stroke="{TG_RENK["esya"]}" '
                        f'stroke-width="{k}"/>')
    xml = "".join(cember(x) for x in (24, 33, 42))                                   # 1 çift ayak: 3 çember
    for x in (54, 76):                                                               # 2 yana kayma konileri
        xml += f'<path d="M{x - 3},{Z} L{x},{Z - 7} L{x + 3},{Z} z" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
    xml += S.kutu(128, Z - 46, 4, 46, rx=0.8) + S.kutu(124, Z - 40, 4, 8, dolgu="yuzey", rx=0.8)   # 4 hedef
    xml += S.cizgi(140, Z + 2, 176, Z + 2, "kilavuz")                                  # 5 skipping 5 m
    xml += "".join(cember(x) for x in (184, 193, 202, 211, 220, 229))                   # 6 tek ayak: 6 çember
    for x in (244, 252):                                                             # 7 vuruş konileri
        xml += f'<path d="M{x - 3},{Z} L{x},{Z - 7} L{x + 3},{Z} z" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
    S.esya(xml)
    for n, x in enumerate((33, 65, 100, 126, 158, 206, 248), 1):
        S.numara(x, 56, n)
    h = hk_egil_al(100, s=0.55, tur="tut")                                           # 3: top yakalama anı
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu, t=0.05)
    return S


def _tg_capl_parkur(baslik, notu):
    """
    CAPL-2 motor beceri testi CAMSA — KAYAN SAHNE (Paket 22; Koordinasyon Parkuru ile aynı yapı). Parkur tuvalden
    geniş, grup olarak kayar; figür ortada kalır ve yanından geçen becerinin hareketini yapar (sıra protokolden,
    hk_camsa_turu). Topu atan uygulayıcı parkurun içinde (ikinci kişi, durağan). Başlık, not, beceri numarası ve
    süreölçer sabit katmanda; süreölçer vuruşta durur. Durağan kopya: genel görünüm (_tg_capl_genel).
    """
    m = TG_OLCEK["_tg_capl_parkur"][0]
    h = hk_camsa_turu(x_c=118, s=0.7, m=m)
    o, ek, Z = h.olay, h.olay["ekipman"], TG_ZEMIN
    S = TgSahne(o["sure"])
    r = 0.3 * m
    koni = lambda x: (f'<path d="M{x - 4:.1f},{Z} L{x:.1f},{Z - 10:.1f} L{x + 4:.1f},{Z} z" fill="{TG_RENK["dolgu"]}" '
                      f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    xml = "".join(_tg_cember(x, Z - 1, r) for x in ek["cift_cember"] + ek["tek_cember"])  # 1 ve 6 çemberler
    xml += "".join(koni(x) for x in ek["kayma_koni"] + ek["koniler"])                       # 2 ve 7 koniler
    hx, hy = ek["hedef"]                                                                      # 4 hedef
    xml += S.kutu(hx + 4, Z - 1.6 * m, 4, 1.6 * m, rx=0.8) + S.kutu(hx, hy - 5, 4, 10, dolgu="yuzey", rx=0.8)
    a, b = ek["skip"]                                                                         # 5 skipping 5 m
    xml += S.cizgi(a, Z + 2, a, Z - 3, "kilavuz") + S.cizgi(b, Z + 2, b, Z - 3, "kilavuz")
    xml += S.figur_xml(o["uygulayici"], "partner", o["uygulayici_s"])                          # 3 uygulayıcı
    S.kaydir(xml, [(t, dx, 0) for t, dx in o["kayma"]])
    for yol in o["toplar"]:
        S.top(yol, r=2.2)
    S.figur(h)
    S.istasyon_araliklari = [(a, b) for _, a, b in o["beceriler"]]
    S.parkur_kaymasi = list(o["kayma"])
    for n, t0, t1 in o["beceriler"]:
        S.numara(22, 32, n, t0, t_bitis=t1)
    S.kronometre(238, 34, t0=o["beceriler"][0][1], t1=o["bitis_t"])
    S.baslik_nobet(baslik, [(ad, t0, t1) for ad, (_, t0, t1) in zip(o["beceri_adlari"], o["beceriler"])])
    S.not_(notu, t=0.02)
    S.duragan = _tg_capl_genel(baslik, notu)
    return S


def _tg_tenis_servis(baslik, notu):
    """
    Tenis servisi (yandan, kort şematik): arka çizgi gerisinden top havaya, raket yukarıdan; son kare TEMAS anı
    (Paket 24) — raket yukarıda, top temasta, hız oku topun çıkış yönünde, radarın kesik ışını oka bağlı. Servis
    karesi işaretli. Radar servis atanın arkasında. Raket başı vuran elin uzantısı (kayan halka).
    """
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_tenis_servis"][0]
    Z = TG_ZEMIN
    arka = 46                                                   # arka çizgi
    file_x = arka + 11.89 * m
    servis_x = file_x + 6.40 * m
    S.esya(S.cizgi(arka, Z - 3, arka, Z + 3) + S.cizgi(servis_x, Z - 3, servis_x, Z + 3)
           + S.cizgi(file_x, Z, file_x, Z - 0.914 * m) + S.kutu(file_x - 1, Z - 0.914 * m - 1, 2, 2, rx=0.5))
    S.esya(S.kutu(14, Z - 34, 8, 6, dolgu="yuzey", rx=1) + S.cizgi(18, Z - 28, 18, Z))   # radar tabancası (sehpada)
    h = hk_servis(arka - 10, s=0.75)
    S.figur(h)
    ry = h.olay["raket"]
    x0, y0 = ry[0][1], ry[0][2]
    S.kaydir(f'<ellipse cx="{x0:.1f}" cy="{y0:.1f}" rx="2.4" ry="3.6" fill="none" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{TG_KALINLIK["esya"]}"/>', [(t, x - x0, y - y0) for t, x, y in ry])
    tv = h.olay["vurus_t"]
    ax, ay = h.olay["atan_el"]
    tx, ty = h.olay["temas"]
    hedef = (file_x + 4.5 * m, Z - 2)
    bx, by = h.olay["tutan_el"]
    yol = [(0.0, bx, by), (0.25, ax, ay)] + [(0.25 + (tv - 0.25) * f, ax + (tx - ax) * f, ay + (ty - ay) * f - 18 * f * (1 - f))
                                             for f in (0.25, 0.5, 0.75, 1.0)]      # elde → atış → tepe → temas
    S.top(yol, r=2.0)                       # top temas noktasında kalır (Paket 24): durağan kare = vuruş anı
    ux, uy = hedef[0] - tx, hedef[1] - ty
    u = _math.hypot(ux, uy) or 1
    ox, oy = tx + ux / u * 6, ty + uy / u * 6
    sx, sy = tx + ux / u * 30, ty + uy / u * 30
    S.belir(S.cizgi(ox, oy, sx, sy, "olcu", ok="son"), 0.97, tur="isaret")              # hız oku: topun çıkış yönü
    S.belir(f'<path d="M22,{Z - 31:.1f} L{(ox + sx) / 2:.1f},{(oy + sy) / 2:.1f}" fill="none" stroke="{TG_RENK["olcu"]}" '
            f'stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.97, tur="isaret")   # radar ışını
    S.baslik(baslik)
    S.isaret("Servis karesi", hedef, (hedef[0] - 2, 70), hiza="middle", t=0.9)
    S.not_(notu)
    return S


def _tg_yuzme(baslik, notu):
    """
    Yüzme (CSS, T-30): havuz yandan — zemin çizgisi havuz tabanı, su çizgisi aynı kalınlıkta ikinci yatay çizgi;
    yüzücü serbest stil, kollar sırayla (toparlanma suyun üstünden). Su açık dolguyla gövdeyi örter; durağan kare
    kulaç ortası (Paket 24). Mesafe/süre farkı etiketlerde.
    """
    S = TgSahne(4.0)
    su = 72
    S.esya(f'<rect x="14" y="{su}" width="232" height="{TG_ZEMIN - su}" fill="{TG_RENK["dolgu"]}" fill-opacity="0.35"/>'
           + S.cizgi(14, su, 246, su, "zemin") + S.cizgi(14, su - 8, 14, TG_ZEMIN) + S.cizgi(246, su - 8, 246, TG_ZEMIN))
    S.figur(hk_serbest_stil(54, 200, su, s=0.75))         # son kare: bir kol suda çeker, öbürü suyun üstünde önde
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_split(baslik, notu):
    """Jimnastik esneklik profili — split: ayaktan hamleyle ön split; ölçü kasıktan zemine (0 = tam split)."""
    S = TgSahne(3.0)
    h = hk_split(120, s=0.85, uzaklik=10)
    e = S.figur(h)
    kx, ky = e["kalca"]
    S.baslik(baslik)
    S.olcu(kx + 52, TG_ZEMIN, kx + 52, ky, "Kasık–zemin (cm)", t=0.9,
           kilavuzlar=[(kx + 4, ky, kx + 52, ky)], bag=[(1, "y", ("kalca",), "min")])
    S.not_(notu)
    return S


def _tg_kurek_ergometre(baslik, notu):
    """
    Kürek ergometresi (2000 m ve 6 dk aynı çizim, fark etiketlerde): ray, önde volan gövdesi ve ekran, ayaklık;
    koltuk rayda kalçayla kayar; zincir volandan tutamağa. Son kare = kulacın bitişi (bacaklar gergin, tutamak göğüste).
    """
    S = TgSahne(4.0)
    s = 0.9
    ayak_x = 172
    h = hk_kurek_ergometre(ayak_x, s=s)
    ky = h.olay["koltuk_y"]
    fx, fy = ayak_x + 22, TG_ZEMIN - 20
    S.esya(S.cizgi(40, TG_ZEMIN - 7, fx, TG_ZEMIN - 7) + S.cizgi(46, TG_ZEMIN - 7, 46, TG_ZEMIN)
           + S.cizgi(fx + 6, TG_ZEMIN - 10, fx + 12, TG_ZEMIN))                              # ray ve ayakları
    S.esya(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="11" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["esya"]}"/>' + S.cizgi(fx - 2, fy - 11, fx - 8, fy - 30)
           + S.kutu(fx - 15, fy - 38, 12, 8, dolgu="yuzey", rx=1))                           # volan, ekran kolu, ekran
    ax, ay = h.olay["ayaklik"]
    S.esya(S.kutu(ax + 1, ay - 8, 4, 14, rx=1))                                              # ayaklık
    k0 = h.olay["koltuk"][0]
    S.kaydir(S.kutu(k0[1] - 7, ky + 1, 14, 4, rx=1), [(t, x - k0[1], 0) for t, x, _ in h.olay["koltuk"]])
    S.cubuk(fx, fy, h.olay["tutamak"], kalinlik="kilavuz")                                   # zincir
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_kayak_ergometre(baslik, notu):
    """
    Kano/kayak ergometresi (200, 500, 1000 m aynı çizim, fark etiketlerde): alçak koltuk, ayaklık, önde volan
    gövdesi; çift palalı kürek iki yana sırayla çekilir. Son kare = yakalama (pala aşağıda, öne uzanmış).
    """
    S = TgSahne(4.0)
    s = 0.9
    x = 96
    h = hk_kayak_ergometre(x, s=s)
    ky = h.olay["koltuk_y"]
    ax, ay = h.olay["ayaklik"]
    S.esya(S.cizgi(60, TG_ZEMIN - 6, 228, TG_ZEMIN - 6) + S.cizgi(66, TG_ZEMIN - 6, 66, TG_ZEMIN)
           + S.cizgi(222, TG_ZEMIN - 6, 222, TG_ZEMIN))                                      # gövde kirişi
    S.esya(S.kutu(x - 10, ky + 1, 20, TG_ZEMIN - 6 - ky - 1, rx=1)                            # koltuk
           + S.kutu(ax + 1, ay - 8, 4, TG_ZEMIN - 6 - ay + 8, rx=1))                           # ayaklık
    S.esya(f'<circle cx="{ax + 26:.1f}" cy="{TG_ZEMIN - 18}" r="10" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["esya"]}"/>')                                         # volan gövdesi
    S.cubuk_iki(h.olay["kurek"], kalinlik="esya")                                            # çift palalı kürek
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_halter(baslik, notu):
    """
    Halter 1RM: solda koparma (yerden tek hareketle baş üstüne, derin çömelişte karşılama), sağda silkme (omuzdan
    baş üstüne, makas). Bar yandan plaka diski olarak görünür. Son kare = her ikisinde bar baş üstünde, kollar kilitli.
    """
    S = TgSahne(3.0)
    s = 0.6
    k = hk_koparma(78, s=s)
    j = hk_silkme(182, s=s)
    r = k.olay["plaka"]
    for h in (k, j):
        b0 = h.olay["bar"][0]
        S.kaydir(f'<circle cx="{b0[1]:.1f}" cy="{b0[2]:.1f}" r="{r}" fill="{TG_RENK["dolgu"]}" '
                 f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>',
                 [(t, x - b0[1], y - b0[2]) for t, x, y in h.olay["bar"]])
        S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_suda_sicrama(baslik, notu):
    """
    Su topu suda dikey sıçrama: derin su (dip yok), su çizgisi ve açık dolgu; eggbeater beklemesi, sonra sıçrama.
    Ölçü: su yüzeyinden uzanan elin ucuna (son kare, tepe).
    """
    S = TgSahne(3.0)
    su = 76
    S.esya(f'<rect x="20" y="{su}" width="220" height="{TG_ZEMIN - su}" fill="{TG_RENK["dolgu"]}" fill-opacity="0.35"/>'
           + S.cizgi(20, su, 240, su, "zemin"))
    h = hk_eggbeater_sicrama(120, su, s=0.6)
    S.figur(h)
    ex, ey = h.olay["el"]
    S.baslik(baslik)
    S.olcu(ex + 26, su, ex + 26, ey, "Su yüzeyinden (cm)", t=0.9,
           kilavuzlar=[(ex + 3, ey, ex + 26, ey)], bag=[(1, "y", ("el1",), "min")])
    S.not_(notu)
    return S


# Test → (sahne, en kritik ayrıntı — protokolden)
TEST_GORSELLERI = {
    "Boy ve Vücut Ağırlığı (TSYT)": (_tg_boy, "Topuk, kalça, sırt ve baş aynı dikey doğrultuda; sırt cetvele değmez, gözler karşıya; ölçüm derin nefes tutulurken alınır."),
    "Oturma Yüksekliği (TSYT)": (_tg_oturma, "Dizler 90°, kalça-sırt-baş aynı dikeyde; oturma yüzeyinden başın üstüne ölçülür."),
    "Kulaç Uzunluğu (TSYT)": (_tg_kulac, "Kollar yere paralel ve gergin, avuç içleri karşıya; iki orta parmak ucu arası ölçülür."),
    "Esneklik (Uzan Eriş) — TSYT": (_tg_esneklik, "Ayak tabanları sehpaya tam dayalı, dizler gergin; cetvel yavaşça itilir ve en uzak noktada beklenir. Sıfır noktası talimatta yazmaz: yalnız TSYT sehpasıyla ölçülür."),
    "Dikey Sıçrama (TSYT, kollar serbest)": (_tg_dikey, "Kollar serbest, beklemeden çöküp sıçrar; aynı noktaya ve dizler gergin iner — uzağa düşerse deneme tekrarlanır."),
    "El Kavrama Kuvveti (TSYT)": (_tg_kavrama, "Ayakta, kol gergin ve aşağıya uzanmış; her el için tek ölçüm."),
    "Geriye Sağlık Topu Atma (TSYT)": (_tg_saglik_topu, "Sırt atış alanına dönük; top baş üzerinden geriye, yaklaşık 45° ile atılır; çizgiyi aşıp geriye düşen atış tekrarlanır."),
    "Çeviklik — Pro Agility 5-10-5 (TSYT)": (_tg_pro_agility, "Orta çizgiden 4,57 m → 9,14 m → orta; her dönüşte çizgiye elle dokunulur."),
    "20m Sürat (TSYT)": (_tg_surat, "Çıkış çizgisi başlangıç fotoselinin 1 m gerisinde; bitiş fotoseli yavaşlamadan geçilir."),
    "Koordinasyon Parkuru (TSYT)": (_tg_koordinasyon, "Dokuz istasyon tek parkurda, fotoselle ölçülür; hatalı istasyon yeniden yapılır (süre cezası yok)."),
    "Mekik Koşusu (TSYT)": (_tg_mekik, "Her sinyalde 20 m ilerideki çizgiye basılır; sinyali iki kez üst üste kaçıran çocuğun testi biter."),
    "Dengede Geriye Yürüme (Balancing Backwards)": (_tg_geriye_denge, "Kiriş üzerinde geriye doğru yürünür; bir denemede en çok 8 adım sayılır, ayak yere değince deneme biter."),
    "Yana Sıçrama (Jumping Sideways)": (_tg_yana_sicrama, "15 sn boyunca çıtanın üzerinden çift ayakla sağa-sola; çıtaya basma ve tek ayakla iniş geçersiz."),
    "Yana Platform Değiştirme (Moving Sideways)": (_tg_yana_platform, "20 sn: boştaki platformu yana koy, üstüne bas; her koyma ve her basma bir puan."),
    "Göz-El Koordinasyonu (Duvara Atıp Yakalama)": (_tg_goz_el, "Duvardan 1 m uzakta; top 1 × 1 m kareye (alt kenarı 1 m yükseklikte) atılır, sektikten sonra yakalanır."),
    "Tek Ayak Engel Üzerinden Sıçrama (Hopping for Height)": (_tg_tek_ayak, "Tek ayakla engelin üzerinden geçilir; inişten sonra aynı ayakla en az 2 sıçrama daha yapılmalı."),
    # Paket 15 — Güreş
    "Special Wrestling Fitness Test (SWFT)": (_tg_swft, "3 × 30 sn aktif periyot, aralarında 20 sn pasif dinlenme; manken suplex tekniğiyle sırtüstü devrilir; test bitiminde ve 1. dakikada KAH ölçülür."),
    "Modified SJFT (Güreş için)": (_tg_sjft, "3 periyot: 15 sn / 30 sn / 30 sn, aralarında 10 sn dinlenme; her periyotta manken en çok sayıda devrilir; test bitiminde ve 1. dakikada KAH ölçülür."),
    "Simulated Wrestling Match (6 dk)": (_tg_gures_mac, "Eşit ağırlık kategorisinde iki sporcu; 2 × 3 dakika mat süresi, 30 sn ara; her periyot sonunda KAH ve RPE (Borg)."),
    # Paket 15 — Buz Hokeyi (NHL/NHLTM Off-Ice bir bataryadır, tek sahneye sığmaz: görseli yok)
    "30m Paten Hızı": (_tg_paten_30, "Durarak başlangıç; 30 m düz buz maksimal hızla kat edilir; 3 deneme, en iyi süre."),
    "Hızlanma Paten Testi (6m + 30m)": (_tg_paten_6_30, "Durarak başlangıç; fotosel 6. ve 30. metredeki süreleri ayrı kaydeder; 3 deneme, en iyi değerler."),
    "S-Turn Testi": (_tg_s_turn, "5 koni S şeklinde 3 m aralıkla; koniler slalom yaparak geçilir; 3 deneme, en iyi süre."),
    # Yo-Yo IR1: 16 test tek sahne, branş adı yalnız başlıkta
    **{f"Yo-Yo IR1 ({b})": (_functools.partial(_tg_yoyo, "" if b == "Genel" else b), _TG_YOYO_KRITIK) for b in _TG_YOYO_IR1},
    # Paket 17 — Futbol, Voleybol, Basketbol, Hentbol, Atletizm (+ Halter dikey sıçrama, Yo-Yo IR2 Genel)
    "Yo-Yo IR2 (Futbol)": (_functools.partial(_tg_yoyo, "Futbol", "IR2"), _TG_YOYO2_KRITIK),
    "Yo-Yo IR2 (Genel)": (_functools.partial(_tg_yoyo, "", "IR2"), _TG_YOYO2_KRITIK),
    "10m Sprint": (_functools.partial(_tg_sprint, "10 m", "Durarak başlangıç, 10 m maksimal hız",
                                      "3 deneme · arada 3-5 dk tam toparlanma", 3),
                   "Durarak başlangıç (ayakta veya blok); 10 m maksimal hız; 3 deneme, arada 3-5 dk tam toparlanma; en iyi süre."),
    "20m Sprint": (_functools.partial(_tg_sprint, "20 m", "Durarak başlangıç, 20 m maksimal hız",
                                      "3 deneme; en iyi süre kaydedilir", 3),
                   "Durarak başlangıç; 20 m maksimal hız (hızlanma + geçiş fazı); 3 deneme, en iyi süre."),
    "100m Sprint": (_functools.partial(_tg_sprint, "100 m", "Blok veya ayakta başlangıç, 100 m",
                                       "2-3 deneme · arada 8-10 dk tam toparlanma", 3, True),
                    "Blok veya ayakta başlangıç; 100 m maksimal; 2-3 deneme, arada 8-10 dk tam toparlanma; en iyi süre."),
    "200m Sprint": (_functools.partial(_tg_sprint, "200 m", "Virajlı pistte 200 m, blok ya da ayakta",
                                       "2 deneme · arada 10-15 dk tam toparlanma", 2, True),
                    "Virajlı pistte, blok veya ayakta başlangıç; 200 m maksimal; 2 deneme, arada 10-15 dk toparlanma."),
    "400m Sprint": (_functools.partial(_tg_sprint, "400 m", "Blok veya ayakta başlangıç, pistte 400 m",
                                       "2 deneme · arada 15-20 dk tam toparlanma", 2, True),
                    "Blok veya ayakta başlangıç; 400 m maksimal; 2 deneme, arada 15-20 dk tam toparlanma; en iyi süre."),
    "Sprint Hızlanma Profili (10-20-30m)": (_tg_hizlanma_profili, "Fotosel 10, 20 ve 30. metrede; 0-10, 10-20, 20-30 m bölüm süreleri ayrı; 3 deneme, her bölümde en iyi değer."),
    "30-15 İntermittent Fitness Test (30-15 IFT)": (_tg_30_15, "40 m alan (3 m güvenlik bölgeleri); 30 sn koşu + 15 sn yürüme; hız 8 km/h'den her aşamada 0,5 km/h artar; 2 kez üst üste yetişemeyen bitirir."),
    "RSA Testi (Repeated Sprint Ability)": (_tg_rsa, "6 × 30 m sprint, her sprint arasında 25 sn pasif dinlenme; durarak başlangıç; en iyi, ortalama süre ve yorgunluk indeksi."),
    "Loughborough İntermittent Shuttle Test (LIST)": (_tg_list, "20 m alanda yürüyüş → koşu → hızlı koşu → sprint → dinlenme döngüsü; standart 5 × 15 dk bölüm (toplam 75 dk)."),
    "Illinois Çeviklik Testi": (_functools.partial(_tg_parkur, "illinois", "10 × 5 m, 8 koni: zigzag + slalom (~60 m)",
                                                   "3 deneme, en iyi süre kaydedilir", "Yüzüstü başlangıç"),
                                "Yüzüstü, baş başlangıç çizgisinde başlar; 10 × 5 m alanda 8 koniyle zigzag + slalom (~60 m); 3 deneme, en iyi süre."),
    "Hentbol Çeviklik ve Sprint Testi": (_functools.partial(_tg_parkur, "illinois", "Illinois çeviklik parkuru",
                                                            "30 m sprint ayrıca; 3 deneme, en iyi süre", "Yüzüstü başlangıç"),
                                         "İki bileşen: 30 m sprint (durarak) ve standart Illinois çeviklik; her biri 3 deneme, en iyi süre."),
    "Voleybol Çeviklik Testi (VAT)": (_functools.partial(_tg_parkur, "vat", "Ortadan 4 köşeye, her köşede yere dokun",
                                                         "Saha 9 × 18 m · 2 deneme, en iyi süre"),
                                      "Orta noktadan sol ön → sağ ön → sağ arka → sol arka köşe → başlangıç; her köşede zemine dokunulur; 2 deneme."),
    "NBA Lane Agility Testi": (_functools.partial(_tg_parkur, "nba_lane", "Aşağı → sol → yukarı → sağ → aşağı",
                                                  "2 deneme; en iyi süre (az = iyi)", "Serbest atış çizgisi köşesi"),
                               "Serbest atış çizgisi köşesinden, savunma duruşunda; boya alanı çevresinde aşağı → sol → yukarı → sağ → aşağı; 2 deneme."),
    "NBA 3/4 Saha Sprint Testi": (_functools.partial(_tg_sprint, "Yaklaşık 21 m", "Basket altından karşı basket altına",
                                                     "Durarak başlangıç; 2 deneme, en iyi süre", 2),
                                  "Basket altından karşı basket altına (yaklaşık 3/4 saha ≈ 21 m), durarak başlangıç; 2 deneme, en iyi süre."),
    "20m Sprint - Voleybol": (_functools.partial(_tg_sprint, "20 m", "Durarak başlangıç, 20 m maksimal hız",
                                                 "3 deneme yapılır; en iyi süre kaydedilir", 3),
                              "Durarak başlangıç; 20 m maksimal hız; 3 deneme, en iyi süre."),
    "Dikey Sıçrama - Voleybol (CMJ + SJ + DJ)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ", "DJ"),
                                                                     "Soldan: CMJ, SJ (90° statik), DJ (30 cm)",
                                                                     "Eller kalçada; 3 deneme, en iyi yükseklik"),
                                                 "CMJ: eller kalçada, ön-çömelmeyle; SJ: 90° statik başlangıç, ön-çömelme yok; DJ: 30 cm'den inip minimal temasla sıçrama; 3'er deneme."),
    "Dikey Sıçrama - Basketbol (CMJ + SJ)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                                 "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                                 "Eller kalçada; 3 deneme, en iyi değer", "2 sn bekleme"),
                                             "CMJ: eller kalçada, serbest ön-çömelmeyle; SJ: 90° statik çömelme, 2 sn bekleme, ön-çömelme yok; 3'er deneme."),
    "Dikey Sıçrama (Hentbol)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                    "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                    "Standart CMJ ve SJ protokolü"),
                                "Standart CMJ (ön-çömelmeyle) ve SJ (statik çömelmeden, ön-çömelme yok) protokolü."),
    "Dikey Sıçrama ve CMJ (Halter)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                          "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                          "Eller kalçada; CMJ − SJ farkı da izlenir"),
                                      "Standart CMJ ve SJ, eller kalçada; CMJ − SJ farkı reaktif kuvvet göstergesidir."),
    "Nordic Hamstring Kuvvet Testi (NHT)": (_tg_nordic, "Diz üstü, bacaklar cihaza (ya da partnere) sabit; gövde öne kontrollü ve yavaşça iner; her bacak eksantrik pik kuvveti; 3 tekrar, en yüksek."),
    "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)": (_tg_diz_dinamometre, "Dinamometrede izometrik: kuadriseps 90°, hamstring 45° diz fleksiyonunda; izokinetik 180°/sn; her iki bacak, pik tork (Nm/kg)."),
    # Paket 18 — mücadele sporları (JPFT ve MMA Fiziksel Uygunluk Bataryası çok bileşenli: görselsiz)
    "Special Judo Fitness Test (SJFT)": (_tg_sjft_judo, "İki uke 6 m aralıkla, tori ortada; A = 15 sn, B = 30 sn, C = 30 sn, aralarında 10 sn; her periyotta en çok ippon atış; HR0 ve HR1."),
    "Uchi-Komi Fitness Test (UKFT)": (_tg_ukft, "Uke direnmez; tori seçtiği teknikle 30 sn boyunca giriş-çıkış yapar, tam devirme yok; 3 set, aralarında 30 sn dinlenme."),
    "Taekwondo Spesifik Aerobik Test (TSAT)": (_functools.partial(
        _tg_vurus, ("ap", "yop", "dollyo"), "Ap chagi, dollyo chagi, yop chagi; 2 dk",
        "Kombinasyon her 20 sn'de değişir; HR0, HR3", "Toplam teknik sayısı", [(20, True)] * 6, 0.8, "ped"),
        "2 dakika boyunca ap chagi, dollyo chagi, yop chagi maksimal hızda; kombinasyon her 20 sn'de değişir; HR0 ve HR3."),
    "Karate Spesifik Dayanıklılık Testi (KSDT)": (_functools.partial(
        _tg_vurus, ("tsuki", "uchi", "geri"), "Tsuki, uchi, geri; 2 dk kumite simülasyonu",
        "Kombinasyon her 30 sn'de değişir; HR0, HR1, HR3", "Toplam teknik sayısı", [(30, True)] * 4, 0.8, "ped"),
        "2 dk maksimal kumite simülasyonu (tsuki, uchi, geri); kombinasyon her 30 sn'de değişir; HR0, HR1, HR3."),
    "Muay Thai Spesifik Dayanıklılık Testi (MTSDT)": (_functools.partial(
        _tg_vurus, ("jab", "cross", "teep", "knee", "roundhouse"), "Jab-cross-hook, teep, roundhouse, knee",
        "5 × 3 dk tur, aralarında 2 dk pasif dinlenme", "Tur başına teknik sayısı",
        [(3, True), (2, False)] * 4 + [(3, True)], 4.5, "torba"),
        "Kum torbası ya da pao; 5 × 3 dk tur, aralarında 2 dk pasif dinlenme; her tur teknik sayısı ve HR."),
    "Kickboks Spesifik Kondisyon Testi (KSKT)": (_functools.partial(
        _tg_vurus, ("jab", "cross", "roundhouse"), "Kum torbasına yumruk + tekme serisi",
        "3 × 2 dk tur, aralarında 1 dk pasif dinlenme", "Tur başına darbe sayısı",
        [(2, True), (1, False)] * 2 + [(2, True)], 12, "torba"),
        "Kum torbasına 3 × 2 dk maksimal yumruk + tekme serisi, aralarında 1 dk pasif dinlenme; tur başına darbe ve HR."),
    "Boks Spesifik Dayanıklılık Testi": (_functools.partial(
        _tg_vurus, ("hook", "uppercut", "jab", "cross"), "Jab, cross, hook, uppercut kombinasyonları",
        "3 × 3 dk tur, aralarında 1 dk pasif dinlenme", "Tur başına darbe sayısı",
        [(3, True), (1, False)] * 2 + [(3, True)], 9, "torba"),
        "Kum torbası ya da lapa; 3 × 3 dk maksimal kombinasyon serisi, aralarında 1 dk pasif dinlenme; HR ve RPE."),
    "Sambo Spesifik Fitness Testi (SSFT)": (_functools.partial(
        _tg_mac, [(3, True), (1, False)] * 2 + [(3, True)], 8, "Kurtkalı simüle maç; atış ve kilit sayılır",
        "3 × 3 dk, 1 dk ara", "HR her tur sonunda ölçülür"),
        "3 × 3 dk simüle maç (resmi sambo süreleri), aralarında 1 dk pasif dinlenme; atış ve kilit sayısı, HR."),
    "MMA Spesifik Kondisyon Testi (MMA-SCT)": (_functools.partial(
        _tg_mac, [(5, True), (1, False)] * 2 + [(5, True)], 5.5, "Simüle maç (UFC/Bellator formatı)",
        "3 × 5 dk, 1 dk ara", "Vuruş, takedown, yerden kontrol sayılır; HR"),
        "3 × 5 dk simüle maç, aralarında 1 dk pasif dinlenme; vuruş, takedown ve yerden kontrol sayısı; HR."),
    "BJJ Spesifik Dayanıklılık Testi (BJJSFT)": (_functools.partial(
        _tg_mac, [(5, True), (1, False)] * 2 + [(5, True)], 5.5, "Simüle maç; her turda partner değişir",
        "3 × 5 dk, 1 dk ara", "Teknik/geçiş sayısı; HR her tur sonunda"),
        "3 × 5 dk simüle maç, aralarında 1 dk pasif dinlenme; partner her turda değişir; teknik/geçiş sayısı, HR."),
    "BJJ Kavrama Kuvveti ve Dayanıklılığı": (_functools.partial(
        _tg_asilma, "Gi yakasına iki elle asılı kalma", "MVC 3 deneme · %60 MVC'de 60 sn tutma"),
        "Gi yakasına iki elle asılı kalma süresi (sn); ayrıca her el MVC 3 deneme ve %60 MVC'de 60 sn tutma."),
    "El Kavrama ve Kurtka Kavrama (Sambo)": (_functools.partial(
        _tg_asilma, "Kurtka yakasından tek el ve çift el asılma", "MVC: her el için 3 deneme (kg)"),
        "Kurtka yakasına tek el ve çift el asılı kalma süreleri (sn); ayrıca her el için 3 deneme MVC (kg)."),
    "Karate Çeviklik Testi (KAT)": (_functools.partial(
        _tg_parkur, "t_testi", "A → B → C → D → B → A", "4 koni T şeklinde · 3 deneme, en iyi süre",
        "A: başlangıç"),
        "4 koni T şeklinde; standart T-testi sırası A → B → C → D → B → A; 3 deneme, en iyi süre."),
    "Taekwondo Çeviklik ve Hız Testi": (_functools.partial(
        _tg_parkur, "t_testi", "T-testi; 10 m sprint ayrıca ölçülür", "3 deneme, en iyi süre", "A: başlangıç"),
        "İki bileşen: 10 m sprint (durarak) ve standart T-testi; her biri 3 deneme, en iyi süre."),
    "Masa Tenisi Reaksiyon ve Çeviklik Testi": (_tg_yan_adim, "Üç bileşen: görsel uyarana reaksiyon (20 deneme), 3 m sağ-sol yan adım (15 sn), masa başı vuruş (30 sn)."),
    # Paket 19 — Çocuk ve genç fiziksel uygunluk bataryaları. Aynı hareket tek çizim; etiketler testin kendi protokolünden.
    # Eurofit
    "Flamingo Denge Testi": (_functools.partial(
        _tg_flamingo, "Kirişte tek ayak, öbür ayak elde, 1 dk", "Kiriş 50 cm × 4 cm · her yere değişte sayaç", kiris=True),
        "Dominant ayakla 50 cm × 4 cm kirişte durulur, öbür bacak dizden bükülüp elle tutulur; 1 dakikada yere dokunma sayısı."),
    "Plate Tapping (Disk Dokunma) Testi": (_functools.partial(
        _tg_plate_tapping, "Öbür el ortadaki plakada", "Diskler arasında 25 tur (50 dokunma) · süre"),
        "Baskın olmayan el ortadaki plakada; baskın el 60 cm arayla duran iki diske sırayla 25 tur (50 dokunma) dokunur; süre."),
    "Otur-Uzan (Sit and Reach) Testi": (_functools.partial(
        _tg_otur_uzan, "Bacaklar düz, ayak tabanları kutuda", "Ayak tabanı hizası 15 cm, sıfır değil", 15),
        "Eurofit kutusunda ayak tabanı hizası ölçekte 15 cm'dir (sıfır değil); parmak uçlarına uzanan 15 cm alır. 2 deneme."),
    "Durarak Uzun Atlama": (_functools.partial(
        _tg_uzun_atlama, "İki ayak çizginin arkasında, kol salınımı", "3 deneme, en iyisi"),
        "İki ayak başlangıç çizgisinin arkasında; kol salınımıyla maksimal yatay atlama. 3 deneme, en iyi mesafe (cm)."),
    "El Kavrama Kuvveti (Eurofit)": (_functools.partial(
        _tg_kavrama, "Ayakta, kol gövdeye paralel ve uzatılmış", "Maksimal güçle sık (kg)", "Her el 2 deneme · iki elin en iyisi toplanır"),
        "Ayakta, kol gövdeye paralel ve uzatılmış; her el 2 deneme. Skor iki elin en iyi değerlerinin toplamıdır (kg)."),
    "Asılı Durma - Bükümlü Kol (Bent Arm Hang)": (_functools.partial(
        _tg_bukumlu_asilma, "Çene barın üstünde, avuçlar öne", "Çene barın altına düşünce süre durur"),
        "Çene bar seviyesinin üstünde, avuçlar öne (pronasyon) asılı kalınır; çene barın altına düştüğünde süre durur."),
    "Mekik (Sit-Up) Testi - 30sn": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında kenetli", "30 sn içinde doğru tekrar sayısı"),
        "Sırtüstü, dizler 90° bükülü, eller ense arkasında kenetli; 30 saniyede tamamlanan doğru tekrar sayısı."),
    "10x5m Mekik Koşusu (Shuttle Run)": (_functools.partial(
        _tg_mekik_kosusu, "5 m", "İki çizgi arası 10 kez (5 gidiş-5 dönüş)", "Her dönüşte çizgiyi bir ayakla geç", 10),
        "5 m aralıklı iki çizgi arasında 10 kez (5 gidiş-5 dönüş); her dönüşte çizgi bir ayakla geçilir. Toplam süre."),
    "20m Mekik Koşusu (Eurofit/Léger)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "Bipe 2 kez üst üste yetişemeyince biter"),
        "20 m ardışık bip sesleri arasında koşulur; hız her dakika artar; bipe 2 kez üst üste yetişemeyince test biter."),
    # FitnessGram (PYFP aynı protokolü uygular — aynı ad aynı çizim)
    "PACER (20m Mekik Koşusu)": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "20 m ardışık ses sinyalleri arasında koşulur; hız her dakika artar; 2 kez üst üste yetişemeyince test biter."),
    "Push-Up (Şınav) Testi": (_functools.partial(
        _tg_sinav, "Dakikada 20 vuruş, alt noktada dirsek 90°", "Form bozulana kadar"),
        "Standart şınav, alt noktada dirsek 90°; metronom dakikada 20 vuruş; form bozulana kadar doğru tekrar sayısı."),
    "Modified Pull-Up Testi": (_functools.partial(
        _tg_modifiye_barfiks, "Sırtüstü, vücut düz, avuçlar öne", "Çene elastik bandın üstüne · form bozulana kadar"),
        "Sırtüstü, bar uzanmış kolların 1-2 inç üstünde, avuçlar öne, vücut düz; çene bardan 7-8 inç aşağıdaki bandın üstüne çekilir."),
    "Curl-Up (Kademeli Mekik) Testi": (_functools.partial(
        _tg_govde_fleksiyonu, "curlup", "Dizler yaklaşık 140°, eller uyluklarda", "Dakikada 20 vuruş · en çok 75 tekrar",
        "Parmaklar şeridi aşar"),
        "Dizler yaklaşık 140°, eller uyluklarda; baş ve omuzlar kalkarken parmaklar ölçüm şeridini aşar; en çok 75 tekrar."),
    "Trunk Lift (Gövde Kaldırma) Testi": (_functools.partial(
        _tg_govde_kaldirma, "Yüzüstü, baş ve gövde yavaşça kalkar", "Yerden çeneye · 2 deneme"),
        "Yüzüstü; gözler yerdeki işarette (baş nötr), üst gövde yavaşça kaldırılır; yerden ÇENEYE ölçülür; en çok 30,5 cm."),
    "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ayak tabanı hizası 22,9 cm (9 inç), sıfır değil",
        22.9, tek_bacak=True),
        "Bir bacak düz, öbürü dizden bükülü ve ayak tabanı yerde; cetvelin 22,9 cm (9 inç) işareti kutunun ayak kenarındadır."),
    "Shoulder Stretch (Omuz Esnekliği) Testi": (_functools.partial(
        _tg_omuz_esneme, "Bir el omuz üstünden, öbürü bel altından", "Her omuz ayrı · geçti / kalmadı"),
        "Bir el omuz üzerinden, öbürü bel altından sırta uzatılır; parmak uçları sırtta değiyorsa geçti. Her omuz ayrı."),
    "1 Mil Yürüyüş/Koşu Testi": (_functools.partial(
        _tg_sprint, "1 mil (1609 m)", "Mümkün olduğunca hızlı, 4 tur × 400 m", "Bitişte kalp atımı: ilk 15 sn × 4", 0,
        fotosel=False),
        "1 mil (1609 m; 400 m pistte 4 tur) olabildiğince hızlı tamamlanır; bitişte kalp atımı ilk 15 saniye × 4."),
    # Presidential (PYFP): FitnessGram'la aynı protokol — çizim aynı, ad farklıysa kendi kaydı
    "Curl-Up (Mekik) Testi": (_functools.partial(
        _tg_govde_fleksiyonu, "curlup", "Dizler yaklaşık 140°, eller uyluklarda", "Dakikada 20 vuruş · en çok 75 tekrar",
        "Parmaklar şeridi aşar"),
        "FitnessGram curl-up ile aynı: dizler yaklaşık 140°, parmaklar ölçüm şeridini aşar; en çok 75 tekrar."),
    "PACER Testi": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "FitnessGram PACER ile aynı: 20 m ardışık sinyaller arasında; 2 kez üst üste yetişemeyince test biter."),
    "Push-Up Testi": (_functools.partial(
        _tg_sinav, "Dakikada 20 vuruş, alt noktada dirsek 90°", "Form bozulana kadar"),
        "FitnessGram şınav ile aynı: alt noktada dirsek 90°, dakikada 20 vuruş, form bozulana kadar."),
    "Trunk Lift Testi": (_functools.partial(
        _tg_govde_kaldirma, "Yüzüstü, baş ve gövde yavaşça kalkar", "Yerden çeneye · 2 deneme"),
        "FitnessGram trunk lift ile aynı: yüzüstü, yerden çeneye ölçülür; kayıt en çok 30,5 cm."),
    "Back-Saver Sit and Reach": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ayak tabanı hizası 22,9 cm (9 inç), sıfır değil",
        22.9, tek_bacak=True),
        "FitnessGram ile aynı: cetvelin 22,9 cm (9 inç) işareti kutunun ayak kenarında; her bacak ayrı ölçülür."),
    "Shoulder Stretch Testi": (_functools.partial(
        _tg_omuz_esneme, "Bir el omuz üstünden, öbürü bel altından", "Her omuz ayrı · geçti / kalmadı"),
        "FitnessGram ile aynı: parmak uçları sırtta değiyorsa geçti; her omuz ayrı değerlendirilir."),
    # CAPL
    "CAPL Engel Parkuru (Motor Beceri)": (_functools.partial(
        _tg_capl_parkur, "Yedi beceri sırayla; süre vuruşla durur", "Beceri 0–14 + süre 1–14 = toplam 1–28"),
        "CAMSA: çift ayak sıçrama, yana kayma, top yakalama, hedefe atış, 5 m skipping, tek ayak sekme, topa vuruş; "
        "süre vuruşla durur; beceri 0–14 + süre 1–14 = 1–28."),
    "CAPL Duran Uzun Atlama (Fiziksel Uygunluk)": (_functools.partial(
        _tg_uzun_atlama, "Ayak uçları çizginin gerisinde, kol salınımı", "2 deneme, en iyisi"),
        "Ayak uçları çizginin gerisinde, ayaklar omuz genişliğinde; kollar salınarak çift ayakla atlanır. 2 deneme, en iyisi."),
    "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "FitnessGram PACER ile aynı protokol: 20 m sinyaller arasında; sonuç CAPL-2 normlarıyla puana dönüştürülür."),
    # ALPHA
    "20m Mekik Koşusu (ALPHA)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "PACER/Léger ile aynı protokol"),
        "PACER/Léger ile aynı 20 m protokol; ALPHA'da VO2max tahmin formülü farklıdır (son hız ve yaş)."),
    "El Kavrama Kuvveti (ALPHA)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Var gücüyle sık (kg)", "Her el 2 deneme · iki elin ortalaması"),
        "Ayakta, dirsek tam ekstansiyonda; dinamometre yaş ve ele göre ayarlanır; her el 2 deneme, iki elin en iyilerinin ortalaması."),
    "Durarak Uzun Atlama (ALPHA)": (_functools.partial(
        _tg_uzun_atlama, "Ayak uçları çizginin gerisinde, çift ayak", "2 deneme, en iyisi"),
        "Ayaklar omuz genişliğinde, ayak uçları çizginin gerisinde; çift ayakla maksimum mesafeye atlanır. 2 deneme."),
    "4x10m Mekik Koşusu (ALPHA)": (_functools.partial(
        _tg_mekik_kosusu, "10 m", "10 m'yi 4 kez (2 gidiş-2 dönüş)", "Her dönüşte bir blok alınıp karşıya taşınır", 4,
        blok=True),
        "10 m aralıklı iki çizgi arasında 4 kez (2 gidiş-2 dönüş); her dönüşte yerden bir sünger blok alınıp taşınır."),
    "Back-Saver Sit and Reach (ALPHA)": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ölçek FitnessGram'dan: taban hizası 22,9 cm",
        22.9, tek_bacak=True),
        "Bir bacak düz, öbürü bükülü; ölçek FitnessGram ile aynı kabul edilir (taban hizası 22,9 cm) — ALPHA kılavuzundan doğrulanamadı."),
    "Plate Tapping (El Plakası Vurma)": (_functools.partial(
        _tg_plate_tapping, "Öbür el iki diskin arasındaki plakada", "25 tur (50 dokunuş) · 2 deneme, en az süre"),
        "Dominant olmayan el plakada; dominant el 60 cm arayla duran iki diske sırayla 25 tur (50 dokunuş); 2 deneme."),
    # PREFIT (3-6 yaş)
    "Durarak Uzun Atlama (PREFIT)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin arkasından çift ayak, kollar öne", "2 deneme, en iyisi", "Topuğa kadar"),
        "Başlangıç çizgisinin arkasından çift ayakla atlanır, kollar öne sallanabilir; topuğun değdiği noktaya kadar ölçülür."),
    "20m Mekik Koşusu (PREFIT)": (_functools.partial(
        _tg_mekik, "Ses sinyalleri arasında 20 m, yavaş başlangıç", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "PREFIT'e özel yavaş başlangıç hızıyla 20 m sinyaller arasında koşulur; 2 kez üst üste yetişemeyince biter."),
    "El Kavrama Kuvveti (PREFIT)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Çocuk dinamometresi (kg)", "Her el 2 deneme · dominant elin en iyisi"),
        "Ayakta, dirsek tam ekstansiyonda; çocuk dinamometresi zorunlu; her el 2 deneme, dominant elin en iyi değeri."),
    "4x10m Mekik Koşusu (PREFIT)": (_functools.partial(
        _tg_mekik_kosusu, "10 m", "10 m'yi 4 kez (2 gidiş-2 dönüş)", "Her dönüşte bir blok alınıp taşınır · 2 deneme", 4,
        blok=True),
        "10 m'yi 4 kez (2 gidiş-2 dönüş) koşar; her dönüşte yerden bir blok alıp karşı çizgiye taşır. 2 deneme, en iyi süre."),
    "Flamingo Denge Testi (PREFIT)": (_functools.partial(
        _tg_flamingo, "Düz zeminde tek ayak, 30 sn", "Denge tahtası yok · her denge kaybında sayaç", tutar=False),
        "Düz zeminde (denge tahtası yok) dominant ayakta durulur, öbür ayak kalçaya yakın; 30 saniyede denge kaybı sayısı."),
    # CNPFM
    "50m Sprint": (_functools.partial(
        _tg_sprint, "50 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2),
        "Ayakta başlangıç pozisyonundan 50 m maksimal hızla koşulur; kronometre ya da fotosel; 2 deneme, en iyi süre."),
    "Mekik Koşusu (50m × 8)": (_functools.partial(
        _tg_mekik_kosusu, "25 m", "25 m'yi 8 kez (4 gidiş-4 dönüş)", "Her dönüşte çizgiyi geçip dön · toplam 200 m", 8),
        "25 m'yi 8 kez (4 gidiş-4 dönüş) maksimal hızla koşar; her dönüşte çizgiyi geçip döner; toplam 200 m."),
    "Durarak Uzun Atlama (CNPFM)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin gerisinde, kol salınımıyla çift ayak", "3 deneme, en iyisi"),
        "Çizginin gerisinde ayaklar omuz genişliğinde; kollar sallanarak çift ayakla atlanır. 3 deneme, en iyi mesafe."),
    "Otur-Uzan Testi (CNPFM)": (_functools.partial(
        _tg_otur_uzan, "İki bacak düz, ayak tabanları plakada", "Kılavuzdan doğrulanamadı · 2 deneme", 0),
        "Ayak tabanları plakaya dayalı; skor sınırları eksi değer içerdiğinden sıfır ayak tabanında kabul edilir (kılavuzdan doğrulanamadı)."),
    "1000m Koşusu - Erkek / 800m Koşusu - Kadın (CNPFM)": (_functools.partial(
        _tg_sprint, "1000 m (E) / 800 m (K)", "Tempolu koşu, yürüyüşe izin var", "400 m pist: 2,5 tur / 2 tur", 0,
        fotosel=False),
        "Erkekler 1000 m (2,5 tur), kadınlar 800 m (2 tur); tempolu koşu önerilir, yürümeye izin verilir ama skor düşer."),
    "Mekik (Sit-Up) 1 Dakika (CNPFM)": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında, ayaklar sabit", "1 dk · dirsekler dizlere, sırt yere"),
        "Dizler 90°, eller ense arkasında kenetli, ayaklar sabit; her tekrarda dirsekler dizlere, sırt yere değmeli; 1 dakika."),
    # KMS (3-6 yaş)
    "Yana Sıçrama (KMS)": (_functools.partial(
        _tg_yana_sicrama, "Çift ayakla sağa-sola, 15 sn", "Engel 50 cm × 2 cm", "2 deneme · her iki yöne geçiş bir tekrar"),
        "50 cm × 2 cm engelin üzerinden 15 saniye çift ayakla sağa-sola sıçranır; her iki yöne geçiş bir tekrar; 2 deneme."),
    "Balans (Denge) Testi (KMS)": (_functools.partial(
        _tg_geriye_denge, "kiris_ileri", "Kiriş üzerinde öne doğru yürü", "Kiriş 3 m × 6 cm · düşmeden adım sayısı, 2 deneme"),
        "3 m × 6 cm kiriş (ya da bant) üzerinde öne yürünür; düşmeden tamamlanan adım sayısı ya da mesafe; 2 deneme."),
    "Top Yakalama Testi (KMS)": (_functools.partial(
        _tg_top_yakalama, "Uygulayıcı atar, çocuk iki eliyle yakalar", "10 denemede başarılı yakalama sayısı"),
        "Uygulayıcı topu 1,5 m mesafeden atar; çocuk iki eliyle yakalamaya çalışır; 10 denemede başarılı yakalama sayısı."),
    "20m Sprint (KMS)": (_functools.partial(
        _tg_sprint, "20 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2, fotosel=False),
        "Ayakta başlangıç pozisyonundan işaretle 20 m maksimal hızla koşulur; kronometreyle; 2 deneme, en iyi süre."),
    # Latorre Román (3-6 yaş)
    "20m Sprint (Latorre)": (_functools.partial(
        _tg_sprint, "20 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2),
        "Ayakta başlangıç pozisyonundan işaretle 20 m maksimal hızla koşulur; kronometre ya da fotosel; 2 deneme."),
    "Durarak Uzun Atlama (Latorre)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin gerisinde, kol salınımıyla çift ayak", "2 deneme, en iyisi"),
        "Çizginin gerisinde ayaklar omuz genişliğinde; kollar sallanarak çift ayakla atlanır. 2 deneme, en iyi mesafe."),
    "El Kavrama Kuvveti (Latorre)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Çocuk dinamometresi (kg)", "Her el 2 deneme · dominant elin en iyisi"),
        "Ayakta, dirsek tam ekstansiyonda, çocuk boyutunda dinamometre; her el 2 deneme, dominant elin en iyi değeri."),
    "Tek Ayak Denge Testi (Latorre)": (_functools.partial(
        _tg_flamingo, "Düz zeminde tek ayak, gözler açık, 30 sn", "Her denge kaybında sayaç · 2 deneme", tutar=False),
        "Düz zeminde dominant ayakta, gözler açık; 30 saniyede denge kaybı sayısı; 2 deneme."),
    "Top Fırlatma Testi (Latorre)": (_functools.partial(
        _tg_top_firlatma, "İki elle baş üzerinden, çizginin gerisinden", "2 deneme, en iyisi (cm)"),
        "Çizginin gerisinden (oturarak ya da ayakta) top iki elle başın üzerinden fırlatılır; 2 deneme, en iyi mesafe."),
    # Flaman Spor Pusulası
    "Top Sektirme — Alternatif El (BOT-2)": (_functools.partial(
        _tg_top_sektirme, "Bir elle sektir, öbür elle karşıla", "Art arda en çok 10 doğru sektirme · 2 deneme"),
        "Tenis topu bir elle sektirilir, öbür elle karşılanır, eller sırayla değişir; art arda en çok 10 doğru sektirme."),
    "Omuz Rotasyon Testi (Sopa/İp)": (_functools.partial(
        _tg_omuz_rotasyon, "Dirsekler bükülmeden baş üstünden sırta", "En dar el aralığı (cm) · düşük skor iyi"),
        "Sopa avuçlar aşağı geniş tutulur, dirsek bükülmeden baş üstünden sırta geçirilip geri getirilir; en dar el aralığı."),
    "Diz Üstü Şınav — 30 sn (BOT-2)": (_functools.partial(
        _tg_sinav, "Dizler matta, gövde baştan dizlere düz", "30 sn içinde doğru tekrar", diz=True),
        "Diz üstü: dizler matta, eller omuz genişliğinde, gövde baştan dizlere düz; 30 saniyede doğru tekrar sayısı."),
    "Oturma Yüksekliği": (_functools.partial(
        _tg_oturma, "Gövde dik, eller uyluklarda", "Oturak yüksekliği çıkarılır: net değer"),
        "Oturağa oturulur, sırt ve kalça ölçüm çubuğunda, baş Frankfurt düzleminde; okunan değerden oturak yüksekliği çıkarılır."),
    # Paket 25 — açıkta kalan testler: çizimleri zaten vardı, kayıtları eksikti (etiketler kendi protokollerinden)
    "20m Mekik Koşusu (Beep Test)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "Bipe 2 kez yetişemeyince biter"),
        "20 m çift yönlü koşu; hız bip sesleriyle artar; bipe 2 kez yetişemeyen sporcu testi bitirir."),
    "Cooper 12 Dakika Koşusu": (_functools.partial(
        _tg_sprint, "400 m pist", "12 dakikada olabildiğince uzun mesafe", "Yürüyüşe izin var · mesafe (m) ölçülür", 0,
        fotosel=False),
        "400 m pistte 12 dakika boyunca olabildiğince uzun mesafe; yürüyüşe izin var; kat edilen mesafe ölçülür."),
    "30-15 Aralıklı Fitness Testi (IFT)": (_tg_30_15,
        "40 m'de ses sinyaline göre 30 sn koşu, 15 sn yürüyüş; her aşamada hız 0,5 km/h artar."),
    "Nordic Hamstring Kuvvet Testi — Genel (NHT)": (_tg_nordic,
        "Diz üstü, bilekler sabit; gövde kontrollü öne indirilir; her bacak ayrı, 3 tekrar, en yüksek değer."),
    "Dikey Sıçrama (CMJ)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ",), "CMJ: eller kalçada, çök ve sıçra", "3 deneme, en iyi değer"),
        "Eller kalçada, ön-çömelmeyle maksimal dikey sıçrama; 3 deneme, en iyi değer."),
    "Dikey Sıçrama Tam Batarya (CMJ + SJ + DJ)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ", "SJ", "DJ"), "Soldan: CMJ, SJ (90° statik), DJ (30 cm)",
        "Eller kalçada; 3 deneme, en iyi yükseklik"),
        "CMJ (ön-çömelmeli), SJ (90° statik çömelmeden, 2 sn bekleme) ve DJ (30 cm'den); her biri 3 deneme."),
    "30m Sprint": (_functools.partial(
        _tg_sprint, "30 m", "Durarak başlangıç, 30 m maksimal hız", "3 deneme · arada 3-5 dk dinlenme", 3),
        "Durarak başlangıç, 30 m düz pist, maksimal hız; 3 deneme, aralarında 3-5 dk dinlenme."),
    # Paket 24 — kürek, kano/kayak, halter, squash, su topu (protokoller önce kaynakla karşılaştırıldı)
    "2000m Kürek Ergometre Testi": (_functools.partial(
        _tg_kurek_ergometre, "2000 m, en kısa sürede", "Süre, ortalama güç (watt) ve tempo (spm)"),
        "Kürek ergometresinde 2000 m en kısa sürede; süre, ortalama güç ve tempo monitörden kaydedilir."),
    "6 Dakika Kürek Ergometre Testi": (_functools.partial(
        _tg_kurek_ergometre, "6 dakikada en uzun mesafe", "Mesafe (m) ve ortalama güç (watt)"),
        "Kürek ergometresinde 6 dakikada en uzun mesafe; mesafe ve ortalama güç kaydedilir."),
    "200m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "200 m, maksimal", "Süre (sn), ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 200 m maksimal; süre, ortalama güç ve kürek frekansı kaydedilir."),
    "500m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "500 m, maksimal", "Süre (sn), ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 500 m maksimal; süre, ortalama güç ve kürek frekansı kaydedilir."),
    "1000m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "1000 m, maksimal", "Süre, ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 1000 m maksimal; süre, ortalama güç, kürek frekansı ve test sonu KAH kaydedilir."),
    "Koparma (Snatch) / Silkme (Clean & Jerk) 1RM": (_functools.partial(
        _tg_halter, "Koparma (sol) · silkme (sağ)", "1RM: en ağır başarılı kaldırış (kg)"),
        "Koparmada bar yerden tek hareketle baş üstüne, silkmede omuzdan baş üstüne; 1RM en ağır başarılı kaldırış."),
    "Squash Artımlı Mekik Testi (SIST)": (_functools.partial(
        _tg_parkur, "sist", "T'den köşeye, ayak hedefte, vuruş taklidi", "1 dk kademe: 14 hareketle başlar, dakikada +1",
        "T: başlangıç", (150, 50)),
        "T'den sinyalin gösterdiği köşeye (dört köşe), ayak hedefte, vuruş taklidi, T'ye dönüş; istemli tükenmeye kadar."),
    "Su Topu Spesifik Aerobik Test (WPOAT)": (_functools.partial(
        _tg_yuzme, "Serbest stil, 100 m tekrarlar", "Her 100 m süresi (sn) kaydedilir"),
        "Serbest stil 100 m tekrarlar; her 100 m süresi kaydedilir (düzen kaynakla doğrulanamadı, protokol notu)."),
    "Dikey Sıçrama - Suda (Su Topu)": (_functools.partial(
        _tg_suda_sicrama, "Eggbeater ile bekle, sonra sıçra", "3 deneme, en iyi değer"),
        "Derin suda eggbeater ile bekleyip maksimal sıçrama; yükseklik su yüzeyinden ölçülür; 3 deneme, en iyi değer."),
    # Paket 23 — tenis, yüzme, jimnastik, badminton (protokoller önce kaynakla karşılaştırıldı)
    "Spider Test (Tenis Çeviklik Testi)": (_functools.partial(
        _tg_parkur, "spider", "Arka çizginin gerisinden 5 topa, sağdan başla", "Her top tek tek kareye · 2 deneme, en iyisi",
        "Başlangıç karesi", (150, 50)),
        "Arka çizginin gerisindeki kareden 5 topu sağdan başlayarak tek tek toplayıp kareye bırakır; 2 deneme, en iyi süre."),
    "T-Testi (Çeviklik)": (_functools.partial(
        _tg_parkur, "t_testi", "A → B → C → D → B → A", "Yana kaymada ayak çaprazlanmaz · 3 deneme, en iyisi",
        "A: başlangıç"),
        "Standart T-testi: A'dan 9,14 m ileri B, 4,57 m sola C, 9,14 m sağa D, B'ye dön, A'ya geri koş; 3 deneme."),
    "CMJ (Badminton)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ",), "Eller kalçada, çök ve sıçra", "3 deneme, en iyi değer"),
        "Standart CMJ: eller kalçada, ani çökmeyle maksimal sıçrama; 3 deneme, en iyi değer."),
    "Tenis Servis Hızı ve İsabeti": (_functools.partial(
        _tg_tenis_servis, "Top havaya, raket yukarıdan", "Radar: hız (km/h) · 10 + 10 servis, isabet (%)"),
        "Arka çizginin gerisinden servis; radar hızı (km/h) ve isabet (%) kaydedilir; 10 birinci + 10 ikinci servis."),
    "Critical Swimming Speed (CSS) Testi": (_functools.partial(
        _tg_yuzme, "400 m ve 200 m, ayrı ayrı maksimal", "CSS = (400 − 200) / (T400 − T200)"),
        "Tam toparlanmayla iki maksimal yüzüş (400 m ve 200 m); CSS = (400 − 200) / (T400 − T200), m/sn."),
    "T-30 Yüzme Testi": (_functools.partial(
        _tg_yuzme, "30 dakika kesintisiz, düzenli tempo", "Toplam mesafe (m) · hız = mesafe / 1800 sn"),
        "30 dakika boyunca kesintisiz, düzenli tempoyla en uzun mesafe; T-30 hızı = mesafe / 1800 sn."),
    "Jimnastik Esneklik Profili": (_functools.partial(
        _tg_split, "Ön split, gövde dik", "Split: 0 = tam split · omuz, kalça, köprü ayrıca"),
        "Dört ölçüm: omuz fleksiyonu (°), kalça fleksiyonu (°), split (kasık–zemin, 0 = tam split), köprü (omuz yüksekliği)."),
    # Paket 19 — Squash Ghost Drill (çok dönüşlü parkur, numaralı)
    "Ghost Drill (Squash Çeviklik Testi)": (_functools.partial(
        _tg_parkur, "ghost", "T'den 6 köşeye sırayla, her köşeden T'ye", "30 sn × 6 set, aralarında 30 sn dinlenme",
        "T noktası", (150, 50), ([(30, True), (30, False)] * 5 + [(30, True)], 0.45)),
        "T noktasından 6 köşeye belirli sırayla; her noktada raketle duvara vurup T'ye dönülür; 30 sn × 6 set, aralarında 30 sn."),
    # Paket 16 — Wingate: dört test tek sahne, branş adı yalnız başlıkta
    **{t: (_functools.partial(_tg_wingate, b), _TG_WINGATE_KRITIK) for t, b in _TG_WINGATE.items()},
    # Paket 35 — Genel Kuvvet Rafı (Laboratuvar › Maksimal Kuvvet ve Kas Dayanıklılığı)
    "1RM Bench Press": (_functools.partial(
        _tg_bench_press, "Bar göğse iner, kollar tam açılır", "Kademeli ısınma · spotçu zorunlu"),
        "Sırtüstü, baş-sırt-kalça sehpada, ayaklar yerde, kapalı kavrayış; bar göğse iner, kollar tam açılır. "
        "Kademeli ısınma ve spotçu zorunlu."),
    "1RM Squat (Arka Çömelme)": (_functools.partial(
        _tg_arka_comelme, "Bar üst sırtta, diz açısı 90°'yi geçene kadar", "Kademeli ısınma · spotçu zorunlu"),
        "Bar üst sırtta; diz açısı 90°'yi geçene kadar çömelinir, dik duruşa dönülür. Güvenlik demiri en alt "
        "noktanın hemen altında; kademeli ısınma ve spotçu zorunlu."),
    "1RM Leg Press": (_functools.partial(
        _tg_leg_press, "Ayak yeri ve hareket açıklığı sabit", "Kademeli ısınma · spotçu zorunlu · diz kilitlenmez"),
        "Sırt ve kalça minderde, ayaklar platformda; platform belirlenen derinliğe iner, bacaklar açılır (diz "
        "kilitlenmez). Kademeli ısınma ve spotçu zorunlu."),
    "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)": (_functools.partial(
        _tg_barfiks, "Tam açık asılıdan çene barın üstüne", "Sallanma yok · form bozulana kadar"),
        "Avuçlar öne, kollar tam açık asılı; çene barın üstüne çekilir, kollar tam açılana dek inilir. Doğru "
        "tekrar sayısı; vücut ağırlığına bağımlıdır."),
    "Şınav (Push-Up) — Maksimum Tekrar (Genel)": (_functools.partial(
        _tg_sinav, "Alt noktada dirsek 90°, gövde düz", "Ara vermeden · form bozulana kadar"),
        "Eller omuz altında, gövde düz; alt noktada dirsek 90°, üstte kollar tam açık. Metronom yok; ara vermeden "
        "doğru tekrar sayısı."),
    "Mekik (Sit-Up) — 1 Dakika (Genel)": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında kenetli", "1 dakikada doğru tekrar sayısı"),
        "Sırtüstü, dizler 90° bükülü, eller ense arkasında kenetli, ayaklar sabit; 1 dakikada doğru tekrar sayısı."),
    # Paket 35c — Sargent (duvar + tebeşir)
    "Sargent Dikey Sıçrama Testi (Duvar)": (_functools.partial(
        _tg_sargent, "Sıçrama yüksekliği = üst iz − alt iz", "Üç deneme, en yüksek iz"),
        "Duvara yan, parmak uçları tebeşirli: ayakta erişim duvara işaretlenir; kollar ve hazırlık çömelmesi serbest "
        "sıçranır, zirvede duvara dokunulur. Sıçrama yüksekliği = üst iz − alt iz; üç denemenin en iyisi."),
}


# Bilerek GÖRSELSİZ testler (Paket 23): hareket değil (ölçüm, anket, laboratuvar cihazı) ya da tek harekete
# inmeyen çok bileşenli batarya ya da protokolü doğrulanamamış test. Eksik sayılmaz; sonraki paketlerde gündeme
# gelmez. Test adı → neden. Bir test hem burada hem TEST_GORSELLERI'nde olamaz (denetim).
TEST_GORSELSIZ = {
    **{ad: "hareket değil: vücut kompozisyonu ölçümü" for ad in (
        "Vücut Kompozisyonu - Deri Kıvrımı", "Vücut Kompozisyonu (PYFP)", "Bel Çevresi ve VKİ (Vücut Kompozisyonu)",
        "Vücut Kompozisyonu (PREFIT)", "Vücut Kompozisyonu (CNPFM)", "Vücut Kompozisyonu (Latorre)",
        "DEXA (Dual-Energy X-ray Absorptiometry)", "Biyoelektrik İmpedans Analizi (BIA)",
        "Hidrostatik Tartım (Su Altı Tartımı)")},
    "CAPL Günlük Adım Sayısı (Günlük Davranış)": "hareket değil: pedometre kaydı",
    "CAPL Motivasyon ve Güven Anketi": "hareket değil: anket",
    **{ad: "laboratuvar ölçümü: cihaz ve fizyolojik çıktı, hareketin kendisi değil" for ad in (
        "VO2max Direkt Ölçüm (Ergospirometri)", "Laktat Eşiği Testi", "Kardiyopulmoner Egzersiz Testi (CPET)",
        "İzokinetik Kuvvet Testi", "EMG Tabanlı Kas Aktivasyonu", "Force-Velocity Profili (F-V)",
        "Rate of Force Development (RFD) Ölçümü")},
    **{ad: "çok bileşenli batarya: tek harekete inmiyor" for ad in (
        "Judo Fiziksel Uygunluk Testi (JPFT)", "MMA Fiziksel Uygunluk Bataryası", "Atletik Güç Testi Bataryası",
        "Kuru Kara Testleri (Dry-Land) — Yüzme", "Jimnastik Fiziksel Uygunluk Testi (GFT)")},
    "Badminton Spesifik Çeviklik Testi (BAT)": "protokol kaynakla doğrulanamadı: güzergâh uydurulmaz (protokol notu)",
    "Rugby League Match Simulation Protocol (RLMSP)": "maç benzetimi: yürüme, koşu, sprint ve temas dizisi; tek harekete inmiyor",
    "NFL Combine Testleri": "çok bileşenli batarya: tek harekete inmiyor",
    "Rugby Union Fitness Test Bataryası": "çok bileşenli batarya: tek harekete inmiyor",
    "NHL/NHLTM Off-Ice Testleri": "çok bileşenli batarya: tek harekete inmiyor",
}


def tg_sahne(test_adi):
    """Sahneyi kurar (denetim ve görsel üretimi aynı yoldan geçer)."""
    return TEST_GORSELLERI[test_adi][0]()


def test_gorseli_html(test_adi, buyuk=False, kabuk=0, duragan=False):
    """
    Hareketli + durağan (reduced-motion) kopya. Görseli olmayan test için None.
    kabuk (0/1): görsel değiştiğinde (başka test ya da "tekrar oynat") sayfa kodu bunu çevirir; iç içe
    yapı bir kat değişir, tarayıcı SVG'yi yeniden kurar ve hareket baştan bir kez oynar (JavaScript yok).
    """
    if test_adi not in TEST_GORSELLERI:
        return None
    S = tg_sahne(test_adi)
    sinif = "tg-svg tg-buyuk" if buyuk else "tg-svg"
    ic = (f'<div class="tg-hareketli">{S.svg(True, test_adi, sinif)}</div>'
          f'<div class="tg-duragan">{S.svg(False, test_adi, sinif)}</div>')
    if duragan:                                     # Paket 38a: "Durdur" — yalnız son kare
        ic = f'<div>{S.svg(False, test_adi, sinif)}</div>'
    if kabuk % 2:
        ic = f'<div class="tg-ic">{ic}</div>'
    return f'<div class="tg-kap">{ic}</div>'


@st.dialog("Test görseli", width="large")
def test_gorseli_penceresi(test_adi, protokol):
    """Büyük görsel + en kritik ayrıntı + saha özeti adımları."""
    st.markdown(f"**{test_adi}**")
    st.markdown(test_gorseli_html(test_adi, buyuk=True), unsafe_allow_html=True)
    st.info(TEST_GORSELLERI[test_adi][1], icon=":material/priority_high:")
    st.markdown("**Adım adım**")
    st.markdown(protokol_ozet_cikar(protokol))
