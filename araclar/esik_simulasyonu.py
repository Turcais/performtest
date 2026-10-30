"""
Eşik simülasyonu (Paket 38p): branş grubu eşleştirmesinde "yayılım" (en uzak − en yakın grup uzaklığı) ile doğruluk
ilişkisi. Her gruptan 6000 sanal çocuk: Opstoel (2015) grup ortalaması ve SD'sinden normal, değişkenler bağımsız,
tohum 1; eşleştirmedeki 11 değişken; uzaklık olcut.analiz.grup_uzakliklari (brans_grubu_eslestir ile AYNI formül:
havuz SD ile Z, iki ondalık, RMS); pencere olcut.analiz.pencere_gruplari (ilk 3 + 3. ile eşit uzaklıktakiler).
Çıktı: yayılım dilimine göre "doğru grup pencerede" oranı ve çocukların payı. Değişkenler arası korelasyon bilinmediği
için gerçek doğruluk farklı olabilir.

    python araclar/esik_simulasyonu.py          (tablo + veri/brans_profilleri.py ile karşılaştırma)
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from veri.brans_profilleri import BRANS_GRUBU_PROFILLERI  # noqa: E402
from olcut.analiz import ESLESTIRME_DEGISKENLERI, grup_uzakliklari, pencere_gruplari  # noqa: E402

COCUK_SAYISI = 6000
TOHUM = 1
DILIMLER = ((0.0, 0.05), (0.05, 0.10), (0.10, 0.15), (0.15, 0.20), (0.20, 0.30), (0.30, None))


def dilim_adi(alt, ust):
    return f"{alt:.2f}–{ust:.2f}" if ust is not None else f"≥ {alt:.2f}"


def simule(cocuk_sayisi=COCUK_SAYISI, tohum=TOHUM):
    """{dilim: (pencerede doğru oranı %, çocuk payı %)}, şans oranı %, eşik altı pay %."""
    rnd = random.Random(tohum)
    gruplar = list(BRANS_GRUBU_PROFILLERI["degerler"])
    sayac = {d: [0, 0] for d in DILIMLER}
    sans, toplam = [], 0
    for gercek in gruplar:
        tablo = BRANS_GRUBU_PROFILLERI["degerler"][gercek]
        for _ in range(cocuk_sayisi):
            degerler = {k: rnd.gauss(tablo[k][0], tablo[k][1]) for k in ESLESTIRME_DEGISKENLERI}
            uz = grup_uzakliklari(degerler)
            siralama = sorted(((g, round(u, 2)) for g, (u, _) in uz.items()), key=lambda x: x[1])
            ham = [u for u, _ in uz.values()]
            yayilim = max(ham) - min(ham)
            pencere = pencere_gruplari(siralama)
            for d in DILIMLER:
                if yayilim >= d[0] and (d[1] is None or yayilim < d[1]):
                    sayac[d][0] += gercek in pencere
                    sayac[d][1] += 1
                    break
            sans.append(len(pencere) / len(gruplar))
            toplam += 1
    tablo = {dilim_adi(*d): (round(100 * a / b, 1) if b else None, round(100 * b / toplam, 1))
             for d, (a, b) in sayac.items()}
    esik_alti = round(100 * (sayac[DILIMLER[0]][1] + sayac[DILIMLER[1]][1]) / toplam, 1)
    return tablo, round(100 * sum(sans) / len(sans), 1), esik_alti


if __name__ == "__main__":
    from veri.brans_profilleri import ESLESTIRME_YAYILIM_SIMULASYONU as KAYIT
    tablo, sans, esik_alti = simule()
    print(f"{'Yayılım':<12}{'Doğru grup pencerede':>22}{'Çocukların payı':>18}")
    for ad, (oran, pay) in tablo.items():
        print(f"{ad:<12}{('%' + format(oran, '.1f')) if oran is not None else '—':>22}{'%' + format(pay, '.1f'):>18}")
    print(f"Şans (pencere büyüklüğü / 6): %{sans}   ·   0,10 altındaki çocuklar: %{esik_alti}")
    ayni = KAYIT["dilimler"] == {k: v[0] for k, v in tablo.items()} and KAYIT["sans"] == sans
    print("veri/brans_profilleri.py ESLESTIRME_YAYILIM_SIMULASYONU ile", "AYNI" if ayni else "FARKLI")
