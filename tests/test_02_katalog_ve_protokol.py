"""
Test kataloğu alanları, protokol biçimlendirme, terim sözlüğü, test arama ve nitelik sınıflandırması.
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
# 3. Katalog alanları
# ════════════════════════════════════════════════════════════
def test_03_katalog_alanlari(app):
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        eksik = []
        if not isinstance(t.get("protokol"), str) or not t.get("protokol", "").strip():
            eksik.append("protokol")
        if not isinstance(t.get("kaynak"), str) or not t.get("kaynak", "").strip():
            eksik.append("kaynak")
        if not isinstance(t.get("degiskenler"), (list, tuple)) or not t.get("degiskenler"):
            eksik.append("degiskenler")
        if eksik:
            sorunlar.append(f"{yol}: eksik/boş {eksik}")
    assert not sorunlar, "Eksik alanlı test:" + _ozet(sorunlar)


# ════════════════════════════════════════════════════════════
# 4. Protokol cümle ortasında başlamıyor (LIST ve EMG böyle kesikti)
# ════════════════════════════════════════════════════════════
def test_04_protokol_basliktan_basliyor(app):
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        ilk = next((s.strip() for s in str(t.get("protokol", "")).splitlines() if s.strip()), "")
        if not ilk.startswith("**"):
            sorunlar.append(f"{yol}: ilk satır → {ilk[:60]!r}")
    assert not sorunlar, "Protokol bir başlıkla (**...) başlamıyor — metin kesik olabilir:" + _ozet(sorunlar)



# ════════════════════════════════════════════════════════════
# 7-9. Protokol biçimlendirme
# ════════════════════════════════════════════════════════════
def test_07_protokol_formatla_adim_kalintisi_yok(app):
    """Akademik görünümden Uygulama bölümü çıkarılır; numaralı adım kalmamalı (23 testte kalıyordu)."""
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        p = t.get("protokol", "")
        if not re.search(r"^[ \t]*\*\*Uygulama", p, re.M | re.I):
            continue
        cikti = app["protokol_formatla"](p)
        kalinti = re.findall(r"^\s*\d+\.\s.*$", cikti, re.M)
        if kalinti:
            sorunlar.append(f"{yol}: {kalinti[0].strip()[:60]!r}")
    assert not sorunlar, "protokol_formatla sonrası numaralı adım kaldı:" + _ozet(sorunlar)


def test_08_protokol_ozeti_bos_degil(app):
    """Saha özeti her testte üretilmeli (36 testte boş çıkıyordu)."""
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        ozet = app["protokol_ozet_cikar"](t.get("protokol", ""))
        if not ozet.strip() or ozet.startswith(("Bu test için saha özeti", "Uygulama adımları bulunamadı")):
            sorunlar.append(f"{yol}: {ozet[:50]!r}")
    assert not sorunlar, "Saha özeti boş:" + _ozet(sorunlar)


def test_09_uygulama_icinde_taninmayan_baslik_yok(app):
    """
    Uygulama bölümü, BOLUM_BASLIKLARI'ndaki ilk başlıkta biter. Bu listede olmayan bir
    bölüm başlığı ("Ölçüm Öncesi", "Formül" böyle kaybolmuştu) Uygulama'nın içine yutulur:
    akademik görünümden silinir ve saha özetinde görünmez. Bu yüzden Uygulama aralığının
    içindeki her satır başı kalın başlık ya bir adım etiketi ("**A) CMJ:**",
    "**Uygulama — Saha:**") ya da bir numaralı adımın parçası olmalı. (Uygulama aralığını
    kapatan başlıktan SONRA gelen başlıklar — ör. Not bölümündeki "**Dikkat:**" — yutulmaz.)
    """
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        p = t.get("protokol", "")
        aralik = app["_uygulama_araligi"](p)
        if not aralik:
            continue
        bolum = p[aralik[0]:aralik[1]]
        for m in re.finditer(r"^[ \t]*\*\*([^*\n]+?)\*\*", bolum, re.M):
            baslik = m.group(1).strip()
            if re.match(r"(?i)^uygulama\b", baslik) or re.match(r"^[A-ZÇĞİÖŞÜ]\)", baslik):
                continue
            sorunlar.append(f"{yol}: '**{baslik}**' Uygulama bölümüne yutuluyor "
                            f"(BOLUM_BASLIKLARI'na eklenmeli ya da adım etiketi olmalı)")
    assert not sorunlar, "Tanınmayan bölüm başlığı:" + _ozet(sorunlar)



# ════════════════════════════════════════════════════════════
# 13. Terim açıklamaları tek kaynaktan (Paket 8)
# ════════════════════════════════════════════════════════════
ZORUNLU_TERIMLER = [
    "Z skoru", "Persentil", "Performans persentili", "P5 / P95", "Norm", "Düşük-iyi test", "MQ", "PQ", "Ortalama Z",
    "Havuzlanmış standart sapma", "Ortalama standart uzaklık", "Güven düzeyi", "Taban / tavan etkisi",
    "Sınır değer (P5 altı / P95 üstü)", "HFZ", "VKİ", "Asimetri indeksi", "VO2max",
    "Reaktif kuvvet indeksi", "Nötr (tanımlayıcı) ölçüm", "Doğum çeyreği",
]


def test_13a_zorunlu_terimler_tanimli(app):
    acik = app["ACIKLAMALAR"]
    eksik = [t for t in ZORUNLU_TERIMLER if not str(acik.get(t, "")).strip()]
    assert not eksik, "ACIKLAMALAR'da açıklaması olmayan terim:" + _ozet(eksik)


def test_13b_kullanilan_her_terimin_aciklamasi_var(app, agac):
    """baslik_ac / ac_dugmesi / sutun_yardimi çağrılarındaki ve terim listelerindeki her terim ACIKLAMALAR'da olmalı."""
    acik = app["ACIKLAMALAR"]
    sorunlar = []
    for d in ast.walk(agac):
        if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
                and d.func.id in ("baslik_ac", "ac_dugmesi", "sutun_yardimi", "bolum_terimleri")):
            continue
        arg = d.args[1] if d.func.id == "baslik_ac" and len(d.args) > 1 else (d.args[0] if d.args else None)
        if arg is None:
            continue
        adaylar = []
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            adaylar = [arg.value]
        elif isinstance(arg, (ast.List, ast.Tuple)):
            adaylar = [e.value for e in arg.elts if isinstance(e, ast.Constant)]
        elif isinstance(arg, ast.BinOp):   # ["Norm"] + (["Düşük-iyi test"] if ... else [])
            adaylar = [e.value for liste in ast.walk(arg) if isinstance(liste, ast.List)
                       for e in liste.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        elif isinstance(arg, ast.Dict):    # sutun_yardimi({"sütun": "terim"})
            adaylar = [v.value for v in arg.values if isinstance(v, ast.Constant)]
        for t in adaylar:
            if t not in acik:
                sorunlar.append(f"satır {d.lineno}: {d.func.id}(…{t!r}…)")
    for liste in ("TERIM_ARAMA", "RAPOR_TERIMLERI"):
        for t in app.get(liste, []):
            if t not in acik:
                sorunlar.append(f"{liste}: {t!r}")
    # terimler_ys = [...] gibi ara listeler
    for d in ast.walk(agac):
        if isinstance(d, ast.Assign) and any(isinstance(h, ast.Name) and h.id.startswith("terimler")
                                             for h in d.targets) and isinstance(d.value, ast.List):
            for e in d.value.elts:
                if isinstance(e, ast.Constant) and e.value not in acik:
                    sorunlar.append(f"satır {d.lineno}: {e.value!r}")
    assert not sorunlar, "Açıklaması olmayan terim (ⓘ açılınca hata verir):" + _ozet(sorunlar)


def test_13c_terim_sozlugu_cift_acilim_yapmiyor(app):
    """protokol_formatla, metinde açılımı zaten olan kısaltmayı ikinci kez açmamalı: 'X (… (X …))'."""
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        cikti = app["protokol_formatla"](t.get("protokol", ""))
        for kisa, acilim in app["TERIM_SOZLUGU"].items():
            ic = acilim.split(" (", 1)[-1]
            if f"({acilim}" in cikti or f"{ic.rstrip(')')} ({acilim}" in cikti:
                sorunlar.append(f"{yol}: {acilim!r} iç içe açıldı")
                break
    assert not sorunlar, "Çift açılım:" + _ozet(sorunlar)




# ── Paket 28: arama sıralaması ──
def test_35a_arama_genel_sozcuk_bitisik_kisa(app):
    """
    Genel sözcükler (test, testi, ölçüm…) sıralamaya katkı vermez; sorgunun tamamı bir adda sözcük başından bitişik
    geçiyorsa öne çıkar (kısa çizgi, boşluk, nokta eşdeğer); 1-2 harflik sözcük tek başına içinde-eşleşme saymaz.
    Ölçüt ve korunması gerekenler kullanıcının listesinden.
    """
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    T = "T-Testi (Çeviklik)"
    for q in ("T-Testi", "t testi", "ttesti", "t.testi"):
        assert T in ara(q)[:3], (q, ara(q)[:5])
    assert T in ara("çeviklik")[:5]
    assert ara("10m")[0] == "10m Sprint"
    assert ara("nordic") == ["Nordic Hamstring Kuvvet Testi — Genel (NHT)"]
    for q in ("sürat", "surat", "süratı"):
        assert "10m Sprint" in ara(q)[:5], q
    assert ara("swft")[0] == "Special Wrestling Fitness Test (SWFT)"
    hepsi = {t["ad"] for t in app["test_ara"]("")}
    assert len(ara("testi")) > 50 and set(ara("testi")) <= hepsi            # yalnız durak sözcük: normal arama
    assert "Trunk Lift Testi" not in ara("t-testi")                            # sözcük ortasından bitişik sayılmaz
    assert "Hentbol Çeviklik ve Sprint Testi" not in ara("t testi")
    assert ara("el")[:1] == ["El Kavrama Kuvveti (TSYT)"]                      # kısa: yalnız bütün sözcük
    assert all("el" in app["ara_katla"](a).split() or "el" in [w for e in app["test_etiketleri"](a)
                                                            for w in app["ara_katla"](e).split()] for a in ara("el"))
    assert len(ara("T-Testi")) < 10, "tek harflik 't' sözcük başı gevşek eşleşmesi geri geldi"
    ilk = ara("çeviklik testi")[:3]                                            # bitişik geçen ad önce
    assert all("ceviklik testi" in app["ara_katla"](a) for a in ilk), ilk
    assert set(ara("çeviklik testi")) == set(ara("çeviklik"))                  # durak sözcük sonucu daraltmaz/genişletmez


# ── Paket 29: genel sürüm branş sürümünden önce ──
def test_36a_genel_surum_once_brans_sorguda_tersine(app):
    """
    Eşit puanda genel sürüm branş sürümünden (adında branş geçen) önce gelir; sorguda branş adı varsa o branşın
    testi öne geçer. Paket 28 ölçütleri ve her testin tam adıyla 1. bulunması korunur.
    """
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    assert "Yo-Yo IR1 (Genel)" in ara("yo-yo")[:3]
    assert ara("wingate")[0] == "Wingate 30sn Bisiklet Testi"
    assert "Dikey Sıçrama (CMJ)" in ara("cmj")[:3]
    # Paket 30: branş rafındaki Yo-Yo IR1 / Wingate kayıtları genel sürümün takma adı — sonuç genel sürüm
    assert ara("yo-yo güreş")[0] == "Yo-Yo IR1 (Genel)"
    assert ara("yo-yo futbol")[0] == "Yo-Yo IR1 (Genel)" and ara("wingate mma")[0] == "Wingate 30sn Bisiklet Testi"
    assert ara("güreşçi yo-yo")[0] == "Yo-Yo IR1 (Genel)"                    # ek duyarsız branş
    T = "T-Testi (Çeviklik)"
    for q in ("T-Testi", "t testi", "ttesti", "t.testi"):
        assert T in ara(q)[:3], q
    assert T in ara("çeviklik")[:5] and ara("10m")[0] == "10m Sprint"
    assert ara("nordic") == ["Nordic Hamstring Kuvvet Testi — Genel (NHT)"]
    for q in ("sürat", "surat", "süratı"):
        assert "10m Sprint" in ara(q)[:5], q
    assert ara("swft")[0] == "Special Wrestling Fitness Test (SWFT)"
    for t in app["katalog_testleri"]():
        assert ara(t["ad"])[0] == app["kanonik_test"](t["ad"]), t["ad"]
    tst = {t["ad"]: t for t in app["katalog_testleri"]()}
    ceza = app["arama_brans_cezasi"]
    assert ceza(tst["Yo-Yo IR1 (Futbol)"], ["yo", "yo"]) == 1 and ceza(tst["Yo-Yo IR1 (Genel)"], ["yo", "yo"]) == 0
    assert ceza(tst["Yo-Yo IR1 (Futbol)"], ["futbol"]) == 0 and ceza(tst["Yo-Yo IR1 (Genel)"], ["futbol"]) == 1
    assert ceza(tst["Illinois Çeviklik Testi"], ["futbol"]) == 0                # katalogda Futbol altında
    assert ceza(tst["10m Sprint"], ["surat"]) == 0                              # adında branş yok: genel sayılır
    br = app["arama_branslari"]()
    assert br["Kano/Kayak"] == [["kano"], ["kayak"]] and br["BJJ (Jiujitsu)"] == [["bjj"], ["jiujitsu"]]


# ── Paket 30: test adları, nitelik, branş varyantları, arama paneli ──
def _norm_kapsami(app):
    """Normu olan katalog kaydı sayısı (değişken normu, test normu ya da yaşa göre norm)."""
    N, K, NT = app["NORMATIF"], app["NORMATIF_KAPSAM"], app["NORMATIF_TEST"]
    NY, NE = app["NORMATIF_YAS"], app.get("NORMATIF_ESIK_YAS", {})
    n = 0
    for t in app["katalog_testleri"]():
        kat, alt, br = t["yol"]
        d = app["TEST_KATALOGU"][kat]
        d = d[alt] if alt else d
        d = d[br] if br else d
        ds = d[t["ad"]].get("degiskenler", [])
        if (t["ad"] in NT or any((x in N and (x not in K or K[x](t["ad"]))) or f"{t['ad']} › {x}" in NY
                                 or f"{t['ad']} › {x}" in NE for x in ds)):
            n += 1
    return n


def test_37a_t_testi_genel_ad(app):
    """
    "Tenis Çeviklik T-Testi" → "T-Testi (Çeviklik)" (Pauole ve ark., 2000: genel çeviklik testi). Rafı Tenis'te
    kalır ama genel sayılır (adında branş yok); eski adla kayıtlı veri ve çalışma yeni ada bellekte çevrilir.
    """
    import pandas as _pd
    yeni, eski = "T-Testi (Çeviklik)", "Tenis Çeviklik T-Testi"
    tum = {t["ad"]: t for t in app["katalog_testleri"]()}
    assert yeni in tum and eski not in tum and tum[yeni]["yol"][2] == "Tenis"
    assert app["TEST_TAKMA_AD"][eski] == yeni and yeni in app["TEST_GORSELLERI"] and eski not in app["TEST_GORSELLERI"]
    assert "Pauole" in app["test_bilgisi"](yeni)["kaynak"]
    assert app["arama_brans_cezasi"](tum[yeni], ["t", "testi"]) == 0
    assert set(app["test_tablosu_duzelt"](_pd.DataFrame({"Test": [eski, yeni]}))["Test"]) == {yeni}
    assert app["ara_katla"]("Tenis") not in app["ara_katla"](app["test_etiketli"](yeni))


def test_37b_nitelik_tek_taksonomi(app):
    """
    Gösterilen nitelik 10'lu listeden; her nitelik yedi ExRx bileşeninden birine eşli ve sıra uyarısı bu eşlemeyi
    kullanır (ayrı bir bileşen kural listesi yok). Etiket (Paket 31: ayraç " · "): "10m Sprint · sürat", "SWFT · anaerobik".
    """
    N = app["TEST_NITELIKLERI"]
    assert list(N) == ["maksimal kuvvet", "çabuk kuvvet", "kuvvette devamlılık", "anaerobik", "aerobik", "sürat",
                       "çeviklik", "esneklik", "denge-koordinasyon", "antropometri"]
    assert set(N.values()) <= set(app["TEST_BILESENLERI"]) and set(N.values()) == set(app["TEST_BILESENLERI"])
    assert "TEST_BILESEN_KURALLARI" not in app
    niteliksiz = []
    for t in app["katalog_testleri"]():
        n = app["test_niteligi"](t["ad"])
        assert app["test_bileseni"](t["ad"]) == (N[n] if n else None)
        if not n:
            niteliksiz.append(t["ad"])
    assert len(niteliksiz) <= 12 and all(a in app["TEST_GORSELSIZ"] for a in niteliksiz), niteliksiz
    e = app["test_etiketli"]
    assert e("10m Sprint") == "10m Sprint · sürat" and e("T-Testi (Çeviklik)") == "T-Testi (Çeviklik)"
    assert e("Yo-Yo IR1 (Genel)") == "Yo-Yo IR1 (Genel) · aerobik"
    assert e("Special Wrestling Fitness Test (SWFT)") == "Special Wrestling Fitness Test (SWFT) · anaerobik"
    assert e("Nordic Hamstring Kuvvet Testi — Genel (NHT)").endswith(" · maksimal kuvvet")
    u = app["sira_uyarilari"](["Nordic Hamstring Kuvvet Testi — Genel (NHT)", "10m Sprint"])
    assert "(maksimal kuvvet)" in u[0] and "(sürat)" in u[0]


def test_37c_brans_varyantlari_takma_ad(app):
    """
    Yo-Yo IR1'in 15 ve Wingate'in 3 branş kaydı genel sürümün takma adı: rafta görünür, veri tek adda toplanır;
    genel sürüm her rafın değişkenlerini kapsar (Yo-Yo IR1 (Futbol)'un "Son Seviye"si dahil). Normları farklı
    testler birleştirilmez. Katalog 189 kayıt (Paket 35: 195); norm kapsamı değişmez.
    """
    T = app["TEST_TAKMA_AD"]
    yoyo = [a for a, g in T.items() if g == "Yo-Yo IR1 (Genel)"]
    wing = [a for a, g in T.items() if g == "Wingate 30sn Bisiklet Testi"]
    assert len(yoyo) == 15 and len(wing) == 3
    tum = {t["ad"] for t in app["katalog_testleri"]()}
    assert len(app["katalog_testleri"]()) == 196   # Paket 35c: + Sargent and set(yoyo + wing) <= tum
    for a, g in T.items():
        if a in tum:
            assert set(app["test_bilgisi"](a)["degiskenler"]) <= set(app["test_bilgisi"](g)["degiskenler"]), a
    assert "Son Seviye" in app["test_bilgisi"]("Yo-Yo IR1 (Genel)")["degiskenler"]
    assert len(app["test_raflari"]("Yo-Yo IR1 (Genel)")) == 16
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    assert [a for a in ara("yo-yo") if a.startswith("Yo-Yo IR1")] == ["Yo-Yo IR1 (Genel)"]
    assert ara("wingate") == ["Wingate 30sn Bisiklet Testi"]
    yy = app["test_ara"]("yo-yo", "Branşa Özgü Testler")                     # kategoriyle: raf kayıtları
    assert len(yy) >= 15 and all(t["kategori"] == "Branşa Özgü Testler" for t in yy)
    for dokunma in ("El Kavrama Kuvveti (Eurofit)", "20m Mekik Koşusu (ALPHA)", "Durarak Uzun Atlama (CNPFM)",
                    "Vücut Kompozisyonu (PREFIT)", "Back-Saver Sit and Reach (ALPHA)", "Dikey Sıçrama (Hentbol)",
                    "20m Sprint (KMS)", "20m Mekik Koşusu (Beep Test)"):
        assert dokunma not in T and dokunma not in T.values(), dokunma
    assert _norm_kapsami(app) == 84


def test_37d_arama_paneli_agacin_ustunde(kaynak):
    """Test Oturumu: arama paneli kategori ağacının ÜSTÜNDE; sonuç satırında "Ekle"; ayrı "Aramadan ekle" kutusu yok."""
    sayfa = _test_oturumu_kaynagi(kaynak)
    assert sayfa.index('key="ot_ara"') < sayfa.index('key="ot_kategori"')
    assert 'key=f"ot::ara::ekle::{i}"' in sayfa and "Aramadan ekle" not in sayfa
    assert "format_func=test_etiketli" in sayfa



# ── Paket 31 ──
def test_38a_ir2_takma_ad_ve_yoyo_aramasi(app):
    """
    Yo-Yo IR2 (Futbol) → Yo-Yo IR2 (Genel) takma adı (değişkenleri aynı); "yo-yo" araması 2 sonuç (IR1 Genel, IR2
    Genel). Katalog 189 (Paket 35: 195); takma ad olmayan her kayıt tam adıyla 1. sırada; norm kapsamı değişmez.
    """
    T = app["TEST_TAKMA_AD"]
    assert T["Yo-Yo IR2 (Futbol)"] == "Yo-Yo IR2 (Genel)"
    assert set(app["test_bilgisi"]("Yo-Yo IR2 (Futbol)")["degiskenler"]) <= set(app["test_bilgisi"]("Yo-Yo IR2 (Genel)")["degiskenler"])
    tum = app["katalog_testleri"]()
    assert len(tum) == 196   # Paket 35c: + Sargent
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    assert ara("yo-yo") == ["Yo-Yo IR1 (Genel)", "Yo-Yo IR2 (Genel)"]
    asil = [t["ad"] for t in tum if t["ad"] not in T]
    assert len(asil) == 176                    # 196 − 20 takma adlı raf kaydı ("Modified Pull-Up Testi" iki rafta)
    for a in asil:
        assert ara(a)[0] == a, a
    assert _norm_kapsami(app) == 84


