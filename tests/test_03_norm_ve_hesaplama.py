"""
Normatif tablolar, persentil bantları, Z-skoru motoru, TSYT çeyrekleri, makullük ve Kademe 2 örneklemleri.
"""
import ast
import collections
import glob
import math
import os
import re
import types

import pytest

from tests.conftest import *  # noqa: F401,F403

# ════════════════════════════════════════════════════════════
# 5. Öksüz norm anahtarı yok
# ════════════════════════════════════════════════════════════
def test_05_oksuz_norm_anahtari_yok(app):
    adlar = {_test_adi(y) for y, _ in _testler(app["TEST_KATALOGU"])}
    sorunlar = []
    for sozluk in ("NORMATIF_YAS", "NORMATIF_TEST"):
        for anahtar in app[sozluk]:
            test_adi = anahtar.split(" › ")[0]
            if " › " not in anahtar:
                sorunlar.append(f"{sozluk}: {anahtar!r} — 'Test › Değişken' biçiminde değil")
            elif test_adi not in adlar:
                sorunlar.append(f"{sozluk}: {anahtar!r} — '{test_adi}' katalogda yok")
    assert not sorunlar, "Katalogda karşılığı olmayan norm anahtarı:" + _ozet(sorunlar)


# ════════════════════════════════════════════════════════════
# 6. Persentil bantları artan sırada (Kolimechkov'da yön ters girilmişti)
# ════════════════════════════════════════════════════════════
def test_06_persentil_bantlari_artan(app):
    sorunlar = []
    for anahtar, norm in app["NORMATIF_YAS"].items():
        for yas, cinsler in norm["yaslar"].items():
            for cins, bant in cinsler.items():
                if not isinstance(bant, dict):
                    continue
                noktalar = sorted((int(p[1:]), v) for p, v in bant.items() if p.startswith("P") and p[1:].isdigit())
                for (p1, v1), (p2, v2) in zip(noktalar, noktalar[1:]):
                    if v1 > v2:
                        sorunlar.append(f"{anahtar} | {yas} yaş {cins}: P{p1}={v1} > P{p2}={v2}")
    for anahtar, norm in app["NORMATIF_YAS"].items():   # çeyrek hücreleri (TSYT, Paket 9)
        for yas, cinsler in norm.get("ceyrekler", {}).items():
            for cins, ceyrekler in cinsler.items():
                for ceyrek, bant in ceyrekler.items():
                    noktalar = sorted((int(p[1:]), v) for p, v in bant.items())
                    for (p1, v1), (p2, v2) in zip(noktalar, noktalar[1:]):
                        if v1 > v2:
                            sorunlar.append(f"{anahtar} | {yas} yaş {cins} {ceyrek}. çeyrek: P{p1}={v1} > P{p2}={v2}")
    assert not sorunlar, "Persentil bandı azalıyor (ham değer P5→P95 artan olmalı):" + _ozet(sorunlar)


def test_06c_ceyrekli_normlar_eksiksiz(app):
    """
    Çeyrekli normlar (TSYT): her yaş × cinsiyet × 4 çeyrekte 19 persentil (P5…P95), her yaşın tablo
    numarası ve kaynağında tam künye (ISBN) olmalı; 'yaslar' dört çeyreğin n ağırlıklı ortalaması olmalı.
    """
    beklenen = {f"P{k}" for k in range(5, 100, 5)}
    sorunlar = []
    sayi = 0
    for anahtar, norm in app["NORMATIF_YAS"].items():
        if "ceyrekler" not in norm:
            continue
        sayi += 1
        if "ISBN" not in norm.get("kaynak", ""):
            sorunlar.append(f"{anahtar}: kaynakta tam künye (ISBN) yok")
        for yas, cinsler in norm["ceyrekler"].items():
            if not str(norm.get("tablolar", {}).get(yas, "")).startswith("Tablo "):
                sorunlar.append(f"{anahtar} | {yas} yaş: tablo numarası yok")
            for cins in ("Erkek", "Kadın"):
                ceyrekler = cinsler.get(cins, {})
                if sorted(ceyrekler) != [1, 2, 3, 4]:
                    sorunlar.append(f"{anahtar} | {yas} {cins}: çeyrekler {sorted(ceyrekler)}")
                    continue
                for q, bant in ceyrekler.items():
                    if set(bant) != beklenen:
                        sorunlar.append(f"{anahtar} | {yas} {cins} {q}. çeyrek: {len(bant)} persentil")
                ort = norm["yaslar"][yas][cins]
                for p in beklenen:
                    agirlik = norm.get("ceyrek_n", {}).get(yas, {}).get(cins)
                    if not agirlik or sorted(agirlik) != [1, 2, 3, 4]:
                        sorunlar.append(f"{anahtar} | {yas} {cins}: çeyrek n'leri yok")
                        break
                    o = sum(agirlik[q] * ceyrekler[q][p] for q in range(1, 5)) / sum(agirlik.values())
                    if abs(ort[p] - o) > 0.01:
                        sorunlar.append(f"{anahtar} | {yas} {cins} {p}: ortalama {ort[p]} ≠ {o:.3f}")
                        break
    assert sayi >= 13, f"Çeyrekli (TSYT) norm sayısı {sayi}; en az 13 bekleniyor (11 ölçüm, 3'ü iki denemeli)"
    assert not sorunlar, "Çeyrekli norm sorunu:" + _ozet(sorunlar)


def test_06b_kategori_araliklari_tutarli(app):
    """NORMATIF_TEST ve NORMATIF: aralıklar çakışmıyor, boşluk yok, yön dusuk_iyi ile uyumlu."""
    sira = ["Zayıf", "Orta", "İyi", "Mükemmel"]
    sorunlar = []
    for sozluk in ("NORMATIF_TEST", "NORMATIF"):
        for anahtar, norm in app[sozluk].items():
            dusuk = norm.get("dusuk_iyi", False)
            hucreler = [(c, norm[c]) for c in ("Erkek", "Kadın") if isinstance(norm.get(c), dict)]
            for brans, bn in norm.get("branslar", {}).items():
                hucreler += [(f"{brans}/{c}", bn[c]) for c in ("Erkek", "Kadın") if isinstance(bn.get(c), dict)]
            for cins, hucre in hucreler:
                araliklar = sorted(((k, v) for k, v in hucre.items() if k in sira), key=lambda x: x[1][0])
                for (k1, (a1, b1)), (k2, (a2, b2)) in zip(araliklar, araliklar[1:]):
                    if b1 > a2 + 1e-9:
                        sorunlar.append(f"{sozluk}: {anahtar} | {cins}: {k1} {a1}-{b1} ile {k2} {a2}-{b2} çakışıyor")
                    elif b1 < a2 - 1e-9:
                        sorunlar.append(f"{sozluk}: {anahtar} | {cins}: {k1} ile {k2} arasında boşluk ({b1}-{a2})")
                gercek = [k for k, _ in araliklar]
                beklenen = [k for k in (sira[::-1] if dusuk else sira) if k in gercek]
                if gercek != beklenen:
                    sorunlar.append(f"{sozluk}: {anahtar} | {cins}: düşükten yükseğe {gercek}, "
                                    f"dusuk_iyi={dusuk} için beklenen {beklenen}")
    assert not sorunlar, "Kategori aralığı sorunu:" + _ozet(sorunlar)



# ════════════════════════════════════════════════════════════
# 10. Z motoru
# ════════════════════════════════════════════════════════════
def _norm_hucreleri(app):
    for anahtar, norm in app["NORMATIF_YAS"].items():
        test_adi, degisken = anahtar.split(" › ", 1)
        for yas, cinsler in norm["yaslar"].items():
            for cins, bant in cinsler.items():
                if isinstance(bant, dict) and len(bant) >= 2:
                    yield anahtar, test_adi, degisken, norm, yas, cins, bant


def _supur(bant, dusuk_iyi, n=40):
    """Ham değerleri kötüden iyiye sıralı üretir (bant dışı uçlar dahil)."""
    v = sorted(float(x) for x in bant.values())
    aciklik = (v[-1] - v[0]) or 1.0
    alt, ust = v[0] - 0.3 * aciklik - 1, v[-1] + 0.3 * aciklik + 1
    degerler = sorted(set([alt + (ust - alt) * i / n for i in range(n + 1)] + v))
    return degerler[::-1] if dusuk_iyi else degerler


def test_10a_z_motoru_tekduze(app):
    """Ham değer kötüden iyiye süpürülünce z_performans hiç düşmemeli ve sonunda artmış olmalı."""
    yas_z = app["yas_z_skoru"]
    sorunlar = []
    for anahtar, test_adi, degisken, norm, yas, cins, bant in _norm_hucreleri(app):
        if norm.get("notr"):
            continue
        zler = []
        for x in _supur(bant, norm.get("dusuk_iyi", False)):
            s = yas_z(test_adi, degisken, yas, cins, x)
            if s is None or s["z_performans"] is None:
                sorunlar.append(f"{anahtar} | {yas} {cins}: {x:.2f} için Z üretilmedi")
                break
            zler.append((x, s["z_performans"]))
        else:
            dusus = [(a, b) for a, b in zip(zler, zler[1:]) if b[1] < a[1] - 1e-9]
            if dusus:
                (x1, z1), (x2, z2) = dusus[0]
                sorunlar.append(f"{anahtar} | {yas} {cins}: {x1:.2f}→{x2:.2f} iyileşirken Z {z1}→{z2} düştü")
            elif not zler[-1][1] > zler[0][1]:
                sorunlar.append(f"{anahtar} | {yas} {cins}: Z hiç artmadı ({zler[0][1]} → {zler[-1][1]})")
    assert not sorunlar, "Z motoru tekdüze değil:" + _ozet(sorunlar)


def test_10b_z_motoru_dusuk_iyi_isaret(app):
    """dusuk_iyi testlerde z_performans = −z; diğerlerinde z_performans = z."""
    yas_z = app["yas_z_skoru"]
    sorunlar = []
    for anahtar, test_adi, degisken, norm, yas, cins, bant in _norm_hucreleri(app):
        if norm.get("notr"):
            continue
        orta = sorted(float(x) for x in bant.values())
        for x in (orta[0], orta[len(orta) // 2], orta[-1]):
            s = yas_z(test_adi, degisken, yas, cins, x)
            if s is None:
                continue
            beklenen = -s["z"] if norm.get("dusuk_iyi") else s["z"]
            if not math.isclose(s["z_performans"], beklenen, abs_tol=0.011):
                sorunlar.append(f"{anahtar} | {yas} {cins} x={x}: z={s['z']}, z_performans={s['z_performans']}, "
                                f"dusuk_iyi={norm.get('dusuk_iyi', False)}")
                break
    assert not sorunlar, "Z işareti yanlış:" + _ozet(sorunlar)


def test_10c_notr_olcum_performans_z_uretmiyor(app):
    """Antropometrik (nötr) ölçüler iyi/kötü değildir: z_performans None olmalı."""
    yas_z = app["yas_z_skoru"]
    sorunlar = []
    notr_sayisi = 0
    for anahtar, test_adi, degisken, norm, yas, cins, bant in _norm_hucreleri(app):
        if not norm.get("notr"):
            continue
        notr_sayisi += 1
        for x in sorted(float(v) for v in bant.values()):
            s = yas_z(test_adi, degisken, yas, cins, x)
            if s is not None and s["z_performans"] is not None:
                sorunlar.append(f"{anahtar} | {yas} {cins}: nötr ölçü z_performans={s['z_performans']} üretti")
                break
    assert notr_sayisi > 0, "Hiç nötr ölçü bulunamadı (Oturma Yüksekliği notr=True olmalı)"
    assert not sorunlar, "Nötr ölçü performans Z'si üretiyor:" + _ozet(sorunlar)


def test_10d_performans_persentili_z_ile_ayni_yonde(app):
    """
    Ekrandaki persentil performans yönündedir (büyük = iyi): z_performans'ın normal dağılımdaki
    karşılığıyla aynı olmalı. Nötr ölçülerde ham persentil kalır.
    """
    from statistics import NormalDist
    yas_z = app["yas_z_skoru"]
    sorunlar = []
    for anahtar, test_adi, degisken, norm, yas, cins, bant in _norm_hucreleri(app):
        for x in sorted(float(v) for v in bant.values()):
            s = yas_z(test_adi, degisken, yas, cins, x)
            if s is None:
                continue
            if norm.get("notr"):
                beklenen = s["persentil"]
            else:
                beklenen = NormalDist().cdf(s["z_performans"]) * 100
            if abs(s["persentil_performans"] - beklenen) > 0.6:
                sorunlar.append(f"{anahtar} | {yas} {cins} x={x}: persentil_performans="
                                f"{s['persentil_performans']}, beklenen ≈{beklenen:.1f}")
                break
    assert not sorunlar, "Performans persentili Z ile tutarsız:" + _ozet(sorunlar)



# ════════════════════════════════════════════════════════════
# 14. TSYT hücre seçimi kitabın tablosunu birebir veriyor (Paket 9)
# ════════════════════════════════════════════════════════════
def test_14_tsyt_hucre_kitap_degerleriyle(app):
    """
    Tablo 9.4.19 (10 yaş Pro Agility), erkek 1. çeyrek: kitapta 50 → 6,60 sn; 95 → 5,68 sn (95 = en iyi).
    Şubat 2014 doğumlu, Mart 2024'te test edilen çocuk bu hücreye düşmeli. Doğum tarihi yoksa
    dört çeyreğin ortalamasına düşülmeli ve not yazılmalı.
    """
    yas_z = app["yas_z_skoru"]
    t, d = "Çeviklik — Pro Agility 5-10-5 (TSYT)", "Süre (sn)"
    for sure, beklenen in ((6.60, 50.0), (5.68, 95.0), (7.76, 5.0)):
        s = yas_z(t, d, 10, "Erkek", sure, "15.02.2014", "10.03.2024")
        assert s and s["ceyrek"] == 1 and s["kullanilan_yas"] == 10, f"hücre yanlış: {s and (s['kullanilan_yas'], s['ceyrek'])}"
        assert abs(s["persentil_performans"] - beklenen) < 0.01, (
            f"{sure} sn → performans persentili {s['persentil_performans']}, kitapta {beklenen}")
        assert "Tablo 9.4.19" == s["tablo"], s["tablo"]
    # Kasım doğumlu: 4. çeyrek; aynı süre 4. çeyrekte daha iyi bir konuma düşer (küçükler daha yavaş)
    s4 = yas_z(t, d, 10, "Erkek", 6.60, "15.11.2014", "10.03.2024")
    assert s4["ceyrek"] == 4 and s4["persentil_performans"] > 50, s4["persentil_performans"]
    # Doğum tarihi yok → ortalama + not
    s0 = yas_z(t, d, 10, "Erkek", 6.60)
    assert s0["ceyrek"] is None and "ortalama" in (s0["ceyrek_notu"] or ""), s0["ceyrek_notu"]
    # Doğum yılına göre yaş: Kasım 2014 doğumlu, Mart 2024'te tam yaşı 9 ama TSYT hücresi 10 yaş
    assert app["tsyt_hucre"]("15.11.2014", "10.03.2024") == (10, 4)
    assert app["tam_yas"]("15.11.2014", "10.03.2024") == 9



# ════════════════════════════════════════════════════════════
# 16. Makullük kontrolü (Paket 10)
# ════════════════════════════════════════════════════════════
def test_16a_makullük_siniri_her_norm_hucresinde(app):
    """Her yaş normu hücresinde (çeyrekler dahil) P1-P99 hesaplanabilmeli ve uç bantları kapsamalı."""
    hesapla = app["makul_aralik_bantlardan"]
    sorunlar, sayi = [], 0
    for anahtar, norm in app["NORMATIF_YAS"].items():
        hucreler = [(f"{y} {c}", b) for y, cs in norm["yaslar"].items() for c, b in cs.items() if isinstance(b, dict)]
        hucreler += [(f"{y} {c} {q}.ç", b) for y, cs in norm.get("ceyrekler", {}).items()
                     for c, qs in cs.items() for q, b in qs.items()]
        for ad, bant in hucreler:
            sayi += 1
            sonuc = hesapla(bant)
            vs = [float(v) for v in bant.values()]
            if not sonuc:
                sorunlar.append(f"{anahtar} | {ad}: sınır hesaplanamadı")
                continue
            p1, p99 = sonuc
            if not (math.isfinite(p1) and math.isfinite(p99)) or p1 > min(vs) + 1e-9 or p99 < max(vs) - 1e-9:
                sorunlar.append(f"{anahtar} | {ad}: P1={p1}, P99={p99}, bantlar {min(vs)}–{max(vs)}")
    assert sayi > 1000, f"yalnızca {sayi} hücre denetlendi"
    assert not sorunlar, "Makullük sınırı sorunu:" + _ozet(sorunlar)


def test_16b_makullük_gercek_hata_ornegi(app):
    """Kilo yerine boy yazılması (174 kg, 10 yaş erkek) yakalanmalı; olağan değer uyarı vermemeli."""
    uyar = app["profil_uyarilari"]
    u = uyar(141, 174, 10, "Erkek")
    assert any("174" in x and "10 yaş erkek" in x and "olağandışı" in x for x in u), u
    assert uyar(141, 34, 10, "Erkek") == [], uyar(141, 34, 10, "Erkek")
    assert any("aynı sayı" in x for x in uyar(140, 140, 10, "Erkek"))
    from datetime import date
    dogum = date(date.today().year - 12, 1, 1)          # 12 yaşında doğum tarihi, 10 yaş girilmiş
    assert any("doğum tarihine göre" in x for x in uyar(150, 40, 10, "Erkek", dogum))
    t = app["makullukte_uyarilar"]
    assert t("10x5m Mekik Koşusu (Shuttle Run)", {"Süre (sn)": "45"}, 10, "Erkek")
    assert t("10x5m Mekik Koşusu (Shuttle Run)", {"Süre (sn)": "21.7"}, 10, "Erkek") == []


def test_16c_normu_olmayan_testte_kontrol_yok(app):
    t = app["makullukte_uyarilar"]
    assert t("Koordinasyon Parkuru (TSYT)", {"Süre (sn)": "999"}, 10, "Erkek") == []
    assert t("Omuz Rotasyon Testi (Sopa/İp)", {"En Dar El Aralığı (cm)": "5000"}, 10, "Erkek") == []



# ════════════════════════════════════════════════════════════
# 42. Paket 35 — Genel Kuvvet Rafı: 6 bağımsız test, rölatif kuvvet, Kademe 2 örneklem (Aydos 2004), normsuz uyarı
# ════════════════════════════════════════════════════════════
_P35_RAF = ("Laboratuvar ve Fizyolojik Testler", "Maksimal Kuvvet ve Kas Dayanıklılığı")
_P35_TESTLER = {   # ad → (değişkenler, nitelik, bileşen)
    "1RM Bench Press": (["1RM Bench Press (kg)"], "maksimal kuvvet", "kuvvet"),
    "1RM Squat (Arka Çömelme)": (["1RM Squat (kg)"], "maksimal kuvvet", "kuvvet"),
    "1RM Leg Press": (["1RM Leg Press (kg)"], "maksimal kuvvet", "kuvvet"),
    "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)": (["Barfiks (tekrar)"], "kuvvette devamlılık", "kas dayanıklılığı"),
    "Şınav (Push-Up) — Maksimum Tekrar (Genel)": (["Şınav (tekrar)"], "kuvvette devamlılık", "kas dayanıklılığı"),
    "Mekik (Sit-Up) — 1 Dakika (Genel)": (["Mekik (tekrar)"], "kuvvette devamlılık", "kas dayanıklılığı"),
}
_P35_NORMSUZ = ("1RM Leg Press", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)",
                "Şınav (Push-Up) — Maksimum Tekrar (Genel)", "Mekik (Sit-Up) — 1 Dakika (Genel)")
# uygulama (90).py'nin NORMATIF anahtarları (25) — v91'de hiçbiri kaybolmaz
_P34_NORMATIF = {
    '100m Sprint (sn)', '10m Sprint (sn)', '200m Sprint (sn)', '20m Sprint (sn)', '30m Sprint En İyi (sn)',
    '400m Sprint (sn)', 'Asimetri İndeksi (%)', 'Askıda Kol Bükme (sn)', 'CMJ En İyi (cm)', 'Düşme Sayısı (1 dk)',
    'Düşme Sayısı (30 sn)', 'H:K Oranı Dom. (%)', 'H:K Oranı N-Dom. (%)', 'Illinois Çeviklik En İyi (sn)', 'Pik Güç (W)',
    'SJFT İndeksi', 'SWFT Index', 'Sağ Bacak (N/kg)', 'Sağ El (kg)', 'Sol Bacak (N/kg)', 'Sol El (kg)',
    'Tamamlanan Mesafe (m)', 'Tekrar Sayısı (30sn)', 'VO2max Tahmini (ml/kg/min)', 'Vücut Yağ % (Tahmini)'}
# Aydos, Pepe ve Karakuş (2004) tabloları: branş → (n, squat ort, SD, bench ort, SD)
_P35_AYDOS = {"Halter": (10, 2.897, 0.196, 1.453, 0.106), "Güreş": (11, 1.915, 0.360, 1.301, 0.210),
              "Boks": (10, 1.827, 0.376, 1.178, 0.145), "Judo": (10, 1.606, 0.305, 1.273, 0.241),
              "Basketbol": (10, 1.566, 0.325, 1.027, 0.145), "Futbol": (15, 1.405, 0.304, 1.089, 0.228),
              "Voleybol": (11, 1.307, 0.171, 1.015, 0.185)}


def test_42a_kuvvet_rafi_alti_test(app):
    """
    Yeni alt raf altı testi birebir adlarla taşır; nitelik/bileşen taksonomiden (1-3 maksimal kuvvet → kuvvet; 4-6
    kuvvette devamlılık → kas dayanıklılığı). "(Genel)" eki yalnız 4-6'da. Testler hem serbest seçimde (raf) hem
    Çalışma'da (aramayla) seçilebilir. Benzersiz ad 188 → 194, kayıt 189 → 195. Paket 35c
    (Sargent): benzersiz ad 195, kayıt 196.
    """
    raf = app["TEST_KATALOGU"][_P35_RAF[0]][_P35_RAF[1]]
    assert [t for t in raf if not t.startswith("_")] == list(_P35_TESTLER)
    for ad, (deg, nit, bil) in _P35_TESTLER.items():
        assert raf[ad]["degiskenler"] == deg, ad
        assert app["test_niteligi"](ad) == nit and app["test_bileseni"](ad) == bil, ad
        assert ad in app["TEST_NITELIKLERI"] or nit in app["TEST_NITELIKLERI"]
        assert bil in app["TEST_BILESENLERI"]
        assert ad.endswith("(Genel)") == (ad in list(_P35_TESTLER)[3:]), ad
        assert app["test_ara"](ad)[0]["ad"] == ad                       # Çalışma: aramayla seçilir
        assert ad not in app["TOPLU_GIRIS_DISI"]                         # Test Oturumu: serbest seçimde listelenir
        assert ad not in app["TEST_TAKMA_AD"]
    tum = app["katalog_testleri"]()
    assert len(tum) == 196 and len({t["ad"] for t in tum}) == 195
    assert app["sira_uyarilari"](["1RM Squat (Arka Çömelme)", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)"]) == []
    assert app["sira_uyarilari"](["Mekik (Sit-Up) — 1 Dakika (Genel)", "1RM Bench Press"])     # dayanıklılık önce: uyarır


def test_42b_benzer_adlar_birbirini_bastirmaz(app):
    """Tam ad araması: "(Genel)" ekli üç test ve depodaki benzerleri kendi tam adıyla 1. sırada; 175 asıl kaydın hepsi."""
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    for ad in ("Push-Up (Şınav) Testi", "Push-Up Testi", "Modified Pull-Up Testi", "Mekik (Sit-Up) 1 Dakika (CNPFM)",
               "Mekik (Sit-Up) Testi - 30sn", *_P35_TESTLER):
        assert ara(ad)[0] == ad, (ad, ara(ad)[:3])
    asil = [t["ad"] for t in app["katalog_testleri"]() if t["ad"] not in app["TEST_TAKMA_AD"]]
    assert len(asil) == 176 and all(ara(a)[0] == a for a in asil)


def test_42c_alti_testin_gorseli_var(app):
    """
    Altısı da TEST_GORSELLERI'nde, hiçbiri TEST_GORSELSIZ'de. Şınav ve mekik mevcut hareketle; barfiks
    hk_modifiye_barfiks'in asılı/bantsız varyantıyla; üç 1RM yeni hareketle (kitaplıkta).
    """
    G, GS = app["TEST_GORSELLERI"], app["TEST_GORSELSIZ"]
    sahne = {ad: getattr(G[ad][0], "func", G[ad][0]).__name__ for ad in _P35_TESTLER}
    assert not set(_P35_TESTLER) & set(GS)
    assert sahne == {"1RM Bench Press": "_tg_bench_press", "1RM Squat (Arka Çömelme)": "_tg_arka_comelme",
                     "1RM Leg Press": "_tg_leg_press", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)": "_tg_barfiks",
                     "Şınav (Push-Up) — Maksimum Tekrar (Genel)": "_tg_sinav",
                     "Mekik (Sit-Up) — 1 Dakika (Genel)": "_tg_govde_fleksiyonu"}
    assert G["Mekik (Sit-Up) — 1 Dakika (Genel)"][0].args[0] == "situp"
    assert {"hk_bench_press", "hk_arka_comelme", "hk_leg_press"} <= set(app["TG_HAREKET_KITAPLIGI"])
    for ad in _P35_TESTLER:
        S = app["tg_sahne"](ad)
        assert S.yazi_sayisi <= app["TG_EN_COK_YAZI"] and S.son_eklemler is not None, ad
    for ad in ("1RM Bench Press", "1RM Squat (Arka Çömelme)", "1RM Leg Press"):
        assert "spotçu zorunlu" in G[ad][1] and "ısınma" in G[ad][1], ad
    E = app["tg_eklemler"]
    # barfiks: asılı varyant — altta ayaklar yerden kesik, kollar tam açık; üstte çene barın üstünde; bant yok
    h = app["hk_modifiye_barfiks"](160, s=0.8, asili=True, bar_y=30)
    alt, ust = E(h.anahtarlar[0][1]), E(h.anahtarlar[-1][1])
    assert max(alt["ayak1"][1], alt["ayak2"][1], alt["parmak1"][1], alt["parmak2"][1]) < app["TG_ZEMIN"] - 2
    assert ust["cene"][1] < h.olay["bar"][1] and h.olay["cene_y"] < h.olay["bar"][1]
    assert 'r="1.3"' not in app["tg_sahne"]("Barfiks (Pull-Up) — Maksimum Tekrar (Genel)").svg(False)   # elastik bant yok
    assert 'r="1.3"' in app["tg_sahne"]("Modified Pull-Up Testi").svg(False)
    # arka çömelme: son kare en alt nokta, diz iç açısı 90°'nin altında; ayak sabit
    h = app["hk_arka_comelme"](140, s=0.85)
    son = E(h.anahtarlar[-1][1])
    import math as _m
    a = _m.degrees(_m.atan2(son["kalca"][1] - son["diz1"][1], son["kalca"][0] - son["diz1"][0])
                   - _m.atan2(son["ayak1"][1] - son["diz1"][1], son["ayak1"][0] - son["diz1"][0]))
    a = abs((a + 180) % 360 - 180)
    assert a < 90 and h.olay["diz_acisi"] < 90, a
    assert abs(E(h.anahtarlar[0][1])["ayak1"][0] - son["ayak1"][0]) < 0.5
    # bench press: bar göğse iner, son kare kollar tam açık (bar en yüksekte)
    h = app["hk_bench_press"](150, app["TG_ZEMIN"] - 18, s=0.85)
    ys = [y for _, _, y in h.olay["bar"]]
    assert abs(max(ys) - h.olay["gogus_y"]) < 1.0 and abs(ys[-1] - min(ys)) < 0.5
    # leg press: platform ray boyunca gider (merkezlerin doğrultusu rayla aynı)
    h = app["hk_leg_press"]((92, app["TG_ZEMIN"] - 22), s=0.85)
    m = [((x1 + x2) / 2, (y1 + y2) / 2) for _, x1, y1, x2, y2 in h.olay["platform"]]
    rx, ry = h.olay["ray"]
    assert all(abs((p[0] - m[0][0]) * ry - (p[1] - m[0][1]) * rx) < 1.5 for p in m)
    assert max(_m.dist(m[0], p) for p in m) > 10


def test_42d_rolatif_kayitli_vucut_agirligindan(app):
    """Rölatif = 1RM / profildeki Kilo (kg), 3 basamak; kullanıcıdan istenmez; kilo yoksa uyarı ve değer yok; kayda girer."""
    f = app["turetilmis_degerler"]
    for test, (gir, cik) in app["ROLATIF_KUVVET"].items():
        assert gir in app["test_bilgisi"](test)["degiskenler"] and cik not in app["test_bilgisi"](test)["degiskenler"]
        h, u = f(test, {gir: "137.5"}, {"Kilo (kg)": 71.3, "Boy (cm)": 178}, 71.3)       # boy değil, kilo
        assert h == {cik: round(137.5 / 71.3, 3)} and not u, (test, h)
        h, u = f(test, {gir: "100"}, {}, 0)
        assert h == {} and len(u) == 1 and "vücut ağırlığı" in u[0]
        assert f(test, {gir: ""}, {}, 80) == ({}, [])
    import pandas as _pd
    tablo = _pd.DataFrame({"Sporcu": ["Ali A"], "1RM Squat (Arka Çömelme) › 1RM Squat (kg)": ["160"]})
    kay, _ = app["oturum_kayitlari"](tablo, {"Ali A": {"Kilo (kg)": 80, "Boy (cm)": 175, "Cinsiyet": "Erkek", "Yaş": 24}},
                                     {"1RM Squat (Arka Çömelme)": ["1RM Squat (kg)"]}, *_P35_RAF, None,
                                     __import__("datetime").date(2026, 10, 1), {"kimlik": "x"})
    assert kay[0]["Rölatif Squat (kg/kg)"] == 2.0 and kay[0]["1RM Squat (kg)"] == "160"


def test_42e_aydos_orneklemi_kademe2(app):
    """
    NORMATIF: yalnız iki rölatif değişken, Kademe 2 örneklem (ort ± SD, kategori/bant yok), yalnız 'Erkek', tablo
    birebir; künye kayıtları (yüzdelik değil, protokol notu, kulüp örneklemi) kayıtta. v90 anahtarlarının hiçbiri kaybolmadı.
    """
    N = app["NORMATIF"]
    assert _P34_NORMATIF <= set(N) and set(N) - _P34_NORMATIF == {"Rölatif Squat (kg/kg)", "Rölatif Bench Press (kg/kg)",
                                                                 "Sıçrama Yüksekliği — En İyi (cm)"}   # Paket 36: Sargent örneklemi
    for deg, sutun in (("Rölatif Squat (kg/kg)", 1), ("Rölatif Bench Press (kg/kg)", 3)):
        n = N[deg]
        assert n["tur"] == "orneklem" and n["yas_alt"] == 18 and "Erkek" not in n and "Kadın" not in n
        assert "5(2), 305-315" in n["kaynak"] and "Aydos" in n["kaynak"]
        assert set(n["branslar"]) == set(_P35_AYDOS)
        for b, v in n["branslar"].items():
            assert list(v) == ["Erkek"], (deg, b)
            r = _P35_AYDOS[b]
            assert v["Erkek"] == {"ort": r[sutun], "sd": r[sutun + 1], "n": r[0]}, (deg, b)
        ku = n["kunye"]
        assert ku["kademe"] == 2 and "yüzdelik norm değil" in ku["tur"] and "milli takım değil" in ku["orneklem"]
        assert "n=10-15" in ku["orneklem"] and "2004" in ku["orneklem"] and "90°'yi geçene kadar" in ku["protokol"]
    assert sum(r[0] for r in _P35_AYDOS.values()) == 77
    # protokol metinleri: Kademe 2, örneklem dili, squat derinliği birebir, bilgi notu (Can & Bayrakdaroğlu) değerlendirmede değil
    sq = app["test_bilgisi"]("1RM Squat (Arka Çömelme)")["protokol"]
    bp = app["test_bilgisi"]("1RM Bench Press")["protokol"]
    for p in (sq, bp):
        assert "Kademe 2" in p and "yüzdelik norm değil" in p and "milli takım değil" in p and "n=10-15" in p
        assert "standart 1RM protokolü" in p and "maksimal ağırlık" in p
    assert "diz açısı 90°'yi geçene kadar" in sq
    assert "boks 1,44 ± 0,19 (n=7), kickboks 1,31 ± 0,14 (n=6)" in bp and "14(1), 121-128" in bp
    assert not any("1.44" in str(v) or "Smith" in str(v) for v in N.values())    # bilgi notu NORMATIF'e girmez


def test_42f_kapsam_cinsiyet_yas(app):
    """
    Örneklem yalnız iki testte; kadında (Erkek'e düşmeden), 18 yaş altında ve yaş bilinmezken referans yok; branş tam
    adla (güreş alt dalları Güreş'e) eşleşir — "Amerikan Futbolu" Futbol değildir. Sonuçta kategori yok.
    """
    nd, K = app["normatif_degerlendir"], app["NORMATIF_KAPSAM"]
    sq, bp = "Rölatif Squat (kg/kg)", "Rölatif Bench Press (kg/kg)"
    assert K[sq]("1RM Squat (Arka Çömelme)") and K[bp]("1RM Bench Press")
    for t in ("1RM Leg Press", "1RM Bench Press", "NFL Combine Testleri", None):
        assert nd(sq, 2.0, "Erkek", "Güreş (Serbest)", t, yas=24) is None, t
    assert nd(bp, 1.2, "Erkek", "Boks", "1RM Squat (Arka Çömelme)", yas=24) is None
    for cins, yas in (("Kadın", 24), ("Kadın", 17), ("Erkek", 17), ("Erkek", 17.9), ("Erkek", None), ("", 24),
                      ("Erkek", float("nan"))):
        assert nd(sq, 2.0, cins, "Güreş (Serbest)", "1RM Squat (Arka Çömelme)", yas=yas) is None, (cins, yas)
        assert not app["orneklem_uygun"](sq, cins, yas, "1RM Squat (Arka Çömelme)")
    r = nd(sq, 2.0, "Erkek", "Güreş (Grekoromen)", "1RM Squat (Arka Çömelme)", yas=18)
    assert r["tur"] == "orneklem" and r["kategori"] is None and r["brans"] == "Güreş"
    assert (r["ort"], r["sd"], r["n"], r["fark"], r["sd_fark"]) == (1.915, 0.360, 11, 0.085, 0.24)
    assert nd(bp, 1.2, "Erkek", "Amerikan Futbolu", "1RM Bench Press", yas=25)["brans"] is None
    assert nd(bp, 1.2, "Erkek", "Futbol", "1RM Bench Press", yas=25)["brans"] == "Futbol"
    notlar = " ".join(app["orneklem_notlari"](r, 18))
    assert "Güreş örneklemi (n=11): 1,915 ± 0,360 kg/kg" in notlar and "Yüzdelik norm değil" in notlar
    assert not any(k in notlar for k in ("Mükemmel", "İyi", "Orta", "Zayıf", "norm:", "persentil"))
    tab = app["orneklem_tablosu"](r)
    assert "| **Güreş** | 11 | 1,915 ± 0,360 |" in tab and tab.count("\n|") == 8


def test_42g_normsuz_dort_test(app):
    """Leg Press, barfiks, şınav, mekik: normu yok (hiçbir norm sözlüğünde değişkeni yok), uyarı metni sabit."""
    assert tuple(app["NORMSUZ_TESTLER"]) == _P35_NORMSUZ
    assert app["NORM_YOK_METNI"] == "Bu test için doğrulanmış norm bulunmamaktadır."
    sozluk = [app["NORMATIF"], app["NORMATIF_TEST"], app["NORMATIF_YAS"], app.get("NORMATIF_ESIK_YAS", {})]
    for t in _P35_NORMSUZ:
        deg = app["test_bilgisi"](t)["degiskenler"] + ([app["ROLATIF_KUVVET"][t][1]] if t in app["ROLATIF_KUVVET"] else [])
        for d in deg:
            assert d not in sozluk[0] and all(f"{t} › {d}" not in s for s in sozluk[1:]), (t, d)
        assert "Bu test için doğrulanmış norm bulunmamaktadır." in app["test_bilgisi"](t)["protokol"], t
    assert "Barfiks tekrar sayısı vücut ağırlığına bağımlıdır; sıklet sporlarında mutlak tekrar yerine zaman içindeki " \
           "değişim yorumlanmalıdır." in app["test_bilgisi"]("Barfiks (Pull-Up) — Maksimum Tekrar (Genel)")["protokol"]
    for t in ("1RM Bench Press", "1RM Squat (Arka Çömelme)", "1RM Leg Press"):
        p = app["test_bilgisi"](t)["protokol"]
        assert "Kademeli ısınma setleri zorunludur" in p and "Spotçu zorunludur" in p and "teknik yetkinlik" in p, t
    assert app["sira_uyarilari"](list(_P35_TESTLER)) == []


def _p35_uygula(tmp_path, monkeypatch, test, cins="Erkek", yas=24, kilo=80, spor="Güreş (Serbest)", deger=None):
    import pandas as _pd

    def veri(d):
        _pd.DataFrame({"Ad": ["Ali"], "Soyad": ["A"], "Yaş": [yas], "Cinsiyet": [cins], "Kilo (kg)": [kilo],
                       "Spor Dalı": [spor]}).to_excel(d / "sporcular.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    kat, alt = _P35_RAF
    for k, v in (("sayfa", "Test Uygula"), ("tu_mod", "📂 Kategoriye Göre"), ("tu_kategori", kat),
                 (f"tu_alt::{kat}", alt), (f"tu_test::{kat}::{alt}::None", test)):
        at.session_state[k] = v
    at.run()
    if deger is not None:
        [w for w in at.text_input if w.label == _P35_TESTLER[test][0][0]][0].input(deger).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_42h_test_uygula_ornekleme_karsilastirma(tmp_path, monkeypatch):
    """Erkek, 24 yaş, güreş: rölatif değer kayıtlı kilodan (160/80 = 2,0) hesaplanır; kart örneklem dilinde, kategori yok."""
    at = _p35_uygula(tmp_path, monkeypatch, "1RM Squat (Arka Çömelme)", deger="160")
    assert any(m.label == "Rölatif Squat (kg/kg)" and str(m.value) in ("2.0", "2") for m in at.metric)
    kart = [m.value for m in at.markdown if "sp-kart" in m.value and "Rölatif Squat" in m.value]
    assert len(kart) == 1 and "Güreş örneklemi (n=11): 1,915 ± 0,360 kg/kg" in kart[0]
    assert "örneklem karşılaştırması" in kart[0] and "sp-kart-alt" not in kart[0]        # rozet/kategori satırı yok
    assert not any(k in kart[0] for k in ("Mükemmel", "İyi", "Orta", "Zayıf", "Üstün", "Düşük"))
    assert any(e.label.startswith("Örneklem değerleri") for e in _acilirlar(at))
    etiket = [e.label for e in _acilirlar(at)]
    assert "Örneklem kaynağı (Kademe 2 — yüzdelik norm değil)" in etiket and "Kategorik norm kaynakları" not in etiket


def test_42i_kadinda_ve_18_altinda_referans_yok(tmp_path, monkeypatch):
    """Kadın ve 17 yaş: squat/bench örneklem değeri hiçbir yerde görünmez; yerine kısa açıklama."""
    for test, deger, cins, yas in (("1RM Squat (Arka Çömelme)", "100", "Kadın", 24),
                                   ("1RM Bench Press", "60", "Erkek", 17), ("1RM Bench Press", None, "Kadın", 30)):
        at = _p35_uygula(tmp_path, monkeypatch, test, cins=cins, yas=yas, deger=deger)
        metin = " ".join([m.value for m in at.markdown] + [i.value for i in at.info] + [c.value for c in at.caption])
        aydos = [f"{v:.3f}".replace(".", ",") for r in _P35_AYDOS.values() for v in r[1:]]
        assert not any(s in metin for s in aydos + ["örneklemi (n="]), (test, cins, yas)
        assert not any(e.label.startswith("Örneklem değerleri") for e in _acilirlar(at))
        assert any("kadın ve 18 yaş altı sporcu için referans gösterilmez" in i.value for i in at.info), (test, cins, yas)


def test_42j_normsuz_testte_uyari_metni(tmp_path, monkeypatch):
    """Normsuz dört testte değerlendirme alanında boş tablo değil "Bu test için doğrulanmış norm bulunmamaktadır." görünür."""
    for test in _P35_NORMSUZ:
        at = _p35_uygula(tmp_path, monkeypatch, test, deger="12")
        assert [i.value for i in at.info if "doğrulanmış norm" in i.value] == ["Bu test için doğrulanmış norm bulunmamaktadır."], test
        assert not [i.value for i in at.info if "henüz mevcut değil" in i.value]


