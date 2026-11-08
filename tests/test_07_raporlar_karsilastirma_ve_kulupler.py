"""
Veli, antrenör ve kulüp raporları, karşılaştırma sekmeleri, PDF/Excel/CSV dışa aktarma, menüler ve kulüpler.
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
# 18. Veli raporu yorumları (Paket 12): şablonlu, sonucu tarif eder, gelecek yordaması yok
# ════════════════════════════════════════════════════════════
VELI_GELECEK = ["ileride", "gelecekte", "olacak", "olabilir", "başarılı", "başarı", "yetenek", "potansiyel",
                "sporcu ol", "şampiyon", "kariyer", "uygun branş", "yatkın"]
VELI_KISILIK = ["güçlü bir", "zayıf", "yavaş", "hızlı bir çocuk", "esnek değil", "esnek bir", "beceriksiz", "sakar",
                "eksik", "yetersiz", "başarısız", "kötü", "geride", "tembel", "çocuk güçlü", "çocuk hızlı"]
VELI_TEKNIK = [r"\bZ\b", r"persentil", r"\bP\d", r"\bnorm", r"sınırda", r"Tablo \d", r"Tomkinson", r"Coppens",
               r"Gençlik ve Spor Bakanlığı", r"Ortega", r"Latorre", r"standart sapma"]


def _veli_yasaklari(metin):
    m = metin.lower()
    return ([f"gelecek: '{w}'" for w in VELI_GELECEK if w in m]
            + [f"kişilik: '{w}'" for w in VELI_KISILIK if w in m])


def test_18a_veli_sablonlari_kurallara_uyuyor(app):
    """
    24 şablon (6 kategori × 4 grup), her biri tek cümle; çocuğu değil sonucu tarif eder ('Bu ... testinde');
    gelecekle ilgili bir şey söylemez; düşük sonuçta 'şu an' ve gelişim alanı dili vardır; sayı ve teknik terim yok.
    """
    sablon = app["VELI_YORUMLARI"]
    kategoriler = [k for k, *_ in app["NORM_SKALASI"]]
    beklenen = {(g, k) for g in app["VELI_GRUPLARI"] for k in kategoriler}
    assert set(sablon) == beklenen and len(sablon) == 24, sorted(beklenen ^ set(sablon))
    sorunlar = []
    for (g, k), c in sablon.items():
        et = f"{g} / {k}"
        if not c.startswith(f"Bu {g.lower()} testinde"):
            sorunlar.append(f"{et}: sonucu tarif etmiyor (\'Bu {g.lower()} testinde\' ile başlamalı)")
        if not c.endswith(".") or c[:-1].count(".") or "!" in c or "?" in c:
            sorunlar.append(f"{et}: tek cümle değil")
        sorunlar += [f"{et}: {y}" for y in _veli_yasaklari(c)]
        sorunlar += [f"{et}: teknik ifade {t}" for t in VELI_TEKNIK if re.search(t, c)]
        if re.search(r"\d", c):
            sorunlar.append(f"{et}: sayı içeriyor")
        seviye = app["kategori_bilgisi"](k)["seviye"]
        if seviye <= 2 and not ("şu an" in c and "gelişen" in c):
            sorunlar.append(f"{et}: düşük sonuç gelişim alanı olarak yazılmamış")
        if seviye >= 3 and ("şu an" in c or "gelişen" in c):
            sorunlar.append(f"{et}: gelişim dili yalnız düşük sonuçta kullanılır")
    for ad in ("VELI_GRUP_TEK_TEST", "VELI_GRUP_TEST_YOK", "VELI_SON_PARAGRAF", "VELI_DISARIDA_NOTU"):
        sorunlar += [f"{ad}: {y}" for y in _veli_yasaklari(app[ad])]
    sorunlar += [f"VELI_GRUP_DUZEY: {y}" for y in _veli_yasaklari(" ".join(app["VELI_GRUP_DUZEY"].values()))]
    assert not sorunlar, "Veli şablonu kuralı çiğniyor:" + _ozet(sorunlar)


def test_18b_her_performans_testi_bir_basliga_ya_da_disariya(app):
    """Normu olan her performans testi dört başlıktan birine ya da açıkça dışarıda bırakılanlara girmeli."""
    grup, disari = app["VELI_TEST_GRUBU"], app["VELI_DISARIDA"]
    testler = {k.split(" › ")[0] for k, n in app["NORMATIF_YAS"].items() if not n.get("notr")}
    eksik = sorted(t for t in testler if t not in grup and t not in disari)
    iki_kez = sorted(set(grup) & disari)
    yanlis = sorted(t for t, (g, _) in grup.items() if g not in app["VELI_GRUPLARI"])
    assert not (eksik or iki_kez or yanlis), f"başlıksız: {eksik} · iki yerde: {iki_kez} · bilinmeyen grup: {yanlis}"


def _veli_ornek(app):
    satirlar, z_sozlugu = [], {}
    for test, deg, deger in [("20m Sürat (TSYT)", "Süre (sn)", 6.5), ("El Kavrama Kuvveti (TSYT)", "Sağ El (kg)", 19),
                             ("El Kavrama Kuvveti (TSYT)", "Sol El (kg)", 14.5),
                             ("Dikey Sıçrama (TSYT, kollar serbest)", "Deneme 1 (cm)", 27),
                             ("Esneklik (Uzan Eriş) — TSYT", "Deneme 1 (cm)", 12),
                             ("20m Mekik Koşusu (Eurofit/Léger)", "VO2max Tahmini (ml/kg/min)", 45),
                             ("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)", 141)]:
        zs = app["yas_z_skoru"](test, deg, 10, "Erkek", deger)
        assert zs, (test, deg)
        satirlar.append({"Test": test, "Değişken": deg, "Değer": deger, "Tarih": "01.10.2026", "Norm yaşı": 10,
                         "Performans persentili": zs["persentil_performans"], "Kategori": zs["kategori"],
                         "Z": zs["z_performans"], "Tür": "Tanımlayıcı (antropometrik)" if zs["notr"] else "Performans",
                         "Not": app["z_durum_notu"](zs) or ""})
        # Paket 38c: veli kutusu P10–P90 aralığını z_sozlugu'ndaki bantlardan alır (sporcu_z_profili gibi)
        z_sozlugu[(test, deg)] = {"z_performans": zs["z_performans"], "bantlar": zs["bantlar"]}
    zp = {"satirlar": satirlar, "z_sozlugu": z_sozlugu, "hata": None, "eski_yas": False}
    v = {"sporcu": "Deneme Çocuk", "bilgi": {"Ad": "Deneme", "Soyad": "Çocuk", "Yaş": 10, "Cinsiyet": "Erkek"}, "zp": zp,
         "esl": {"uygun": False, "kullanilan": [], "siralama": []}, "pen": None, "puan": {}, "ilgi": None,
         "hacim": "Bilinmiyor", "fiziksel_uc": [], "tarih_araligi": ("01.10.2026", "01.10.2026"),
         "rapor_tarihi": "15.10.2026"}
    return v, zp


def test_18c_veli_raporunda_teknik_bilgi_yok_yapi_dogru(app):
    """
    Veli raporu (Paket 38c): dört başlık; her test TEK kutuda, son ölçümüyle, aralık diliyle ("aralığın içinde/
    üstünde/altında"); sınıf etiketi ve şablon yargı cümlesi yok; son paragraf sabit.
    Z, persentil, norm kaynağı, tablo numarası ve sınır notları geçmez (bunlar antrenör raporunda).
    """
    v, zp = _veli_ornek(app)
    h = app["veli_raporu_html"](v)
    metin = re.sub(r"<style.*?</style>|<[^>]+>", " ", h, flags=re.S)
    assert "Henüz bu dört başlığa giren bir test sonucu yok" not in metin   # denetim dolu rapor üzerinde
    teknik = [t for t in app_teknik_kaliplari() if re.search(t, metin)]
    assert not teknik, f"Veli raporunda teknik ifade: {teknik}"
    for g in app["VELI_GRUPLARI"]:
        assert f"<span>{g}</span></h3>" in h, g
    kutular = re.findall(r'<div class="veli-aralik"><h4>(.*?)</h4>', h)
    assert len(kutular) == len(set(kutular)) == 4, kutular   # sürat, el kavrama (tek kutu), sıçrama, esneklik
    assert 'class="veli-satir"' not in h and 'class="veli-yorum"' not in h   # eski kart + şablon cümlesi düzeni
    etiketler = [k for k, _, _, _ in app["palet"]("acik")["norm"]]
    assert not [k for k in etiketler if re.search(r"\b" + re.escape(k) + r"\b", metin)], "Veli raporunda sınıf etiketi"
    yer_sozcukleri = [kelime for _, kelime in app["VELI_YER_ISARETI"].values()]
    for kutu in re.findall(r'<div class="veli-aralik">.*?</svg>', h, flags=re.S):   # her kutuda tek yer sözcüğü
        assert sum(y in kutu for y in yer_sozcukleri) == 1, kutu[:120]
    import html as _h
    son = re.findall(r'<div class="veli-son">(.*?)</div>', h)
    assert son and _h.unescape(son[0]) == app["VELI_SON_PARAGRAF"]
    assert h.rstrip().endswith(f'{son[0]}</div></div></body></html>'), "Sabit paragraf raporun sonunda değil"
    assert app["VELI_DISARIDA_NOTU"] in _h.unescape(h)   # dayanıklılık testi vardı
    assert "141" not in metin   # vücut ölçüsü (nötr) veli kutularına girmez


def app_teknik_kaliplari():
    return VELI_TEKNIK


def test_18d_tek_testten_genel_sonuc_yok(app):
    """Bir başlıkta tek test varsa grubun 'genel durumu' yazılmaz; birden çoksa yalnız sayım yapılır."""
    d = app["veli_grup_durumu"]
    assert d([2]) == app["VELI_GRUP_TEK_TEST"] and d([6]) == app["VELI_GRUP_TEK_TEST"]
    assert d([]) == app["VELI_GRUP_TEST_YOK"]
    m = d([6, 5, 3, 1])
    assert "4 test yapıldı" in m and "2 testte" in m and "1 testte" in m, m
    assert not _veli_yasaklari(m), m



# ════════════════════════════════════════════════════════════
# 43. Paket 38f: en iyi deneme, yetişkin metni, sapmanın büyüklüğü (veli raporu)
# ════════════════════════════════════════════════════════════
def _p38f_satir(test, deg, deger, p, kategori="Çok Düşük"):
    return {"Test": test, "Değişken": deg, "Değer": deger, "Tarih": "29.07.2026", "Tür": "Performans",
            "Kategori": kategori, "Performans persentili": p}


def test_43a_en_iyi_deneme_ham_degerden(app):
    """
    Persentil tablonun ucunda sabitlenince (P5) denemeler eşit görünüyordu ve ilk deneme seçiliyordu (atlama
    50/54/60 → 50). Şimdi: "En İyi …" varsa o; yoksa ham değer ve test yönü; eşitlikte yüksek persentil;
    sağ/sol gibi deneme olmayan değişkenlerde en yüksek persentil (önceki davranış).
    """
    sec = app["veli_en_iyi_satir"]
    s = lambda *a: (a[3], _p38f_satir(*a), 1)
    atl = [s("Durarak Uzun Atlama", f"Deneme {i} (cm)", v, 5) for i, v in ((1, 50), (2, 54), (3, 60))]
    assert sec("Durarak Uzun Atlama", atl)[1]["Değer"] == 60
    sprint = [s("20m Sprint (KMS)", "Deneme 1 (sn)", 4.1, 95), s("20m Sprint (KMS)", "Deneme 2 (sn)", 3.9, 95)]
    assert sec("20m Sprint (KMS)", sprint)[1]["Değer"] == 3.9                       # düşük daha iyi
    esit = [s("Durarak Uzun Atlama", "Deneme 1 (cm)", 60, 5), s("Durarak Uzun Atlama", "Deneme 2 (cm)", 60, 7)]
    assert sec("Durarak Uzun Atlama", esit)[1]["Değişken"] == "Deneme 2 (cm)"     # eşit değer: yüksek persentil
    en_iyi = atl + [s("Durarak Uzun Atlama", "En İyi Değer (cm)", 58, 5)]
    assert sec("Durarak Uzun Atlama", en_iyi)[1]["Değişken"] == "En İyi Değer (cm)"  # testin En İyi değişkeni önce
    el = [s("El Kavrama Kuvveti (TSYT)", "Sağ El (kg)", 19, 40), s("El Kavrama Kuvveti (TSYT)", "Sol El (kg)", 21, 30)]
    assert sec("El Kavrama Kuvveti (TSYT)", el)[1]["Değişken"] == "Sağ El (kg)"   # sağ/sol: persentil
    # uçtan uca: veli özeti tek kutu, en iyi deneme 60
    zp = {"satirlar": [r for _, r, _ in atl], "z_sozlugu": {}}
    grup = app["VELI_TEST_GRUBU"]["Durarak Uzun Atlama"][0]
    kutu = app["veli_test_ozeti"](zp)[grup]["testler"]
    assert len(kutu) == 1 and kutu[0]["deger"] == 60 and kutu[0]["ad"].endswith("(en iyi deneme)")


def test_43b_yetiskin_raporunda_cocuk_dili_yok(app):
    """Yetişkinde 'çocuklar için', 'çocukların çoğunun', 'büyümeyle', 'Bu yaşta' yok; araştırma tanımları aynen kalır."""
    v, _ = _veli_ornek(app)
    cocuk = app["veli_raporu_html"](v)
    v["bilgi"] = {**v["bilgi"], "Yaş": 23}
    yetiskin = app["veli_raporu_html"](v)
    cocuk_dili = ["çocuklar için yayımlanmış", "Koyu bant çocukların", "spor gruplarındaki çocuklara", "büyümeyle",
                  "Bu yaşta "]
    assert all(c in cocuk for c in cocuk_dili), [c for c in cocuk_dili if c not in cocuk]   # çocukta değişmedi
    assert not [c for c in cocuk_dili if c in yetiskin]
    assert "sporcular için yayımlanmış" in yetiskin and "Fiziksel özellikler antrenmanla değişir" in yetiskin
    assert "620 çocukla" in yetiskin                                     # araştırma tanımı değişmez


def test_43c_buyuk_sapma_belirgin_ve_dogru_mu(app):
    """
    Bant P10–P90 = ±1,2816 SD. |z| ≤ 1,96 'biraz', 1,96–3 'belirgin şekilde', > 3 'çok' + 'Değer doğru mu?'.
    Aralığın içindeki ve 'biraz' dışındaki metinler önceki gibi.
    """
    yer = app["veli_aralik_konumu"]
    k = lambda d: {"deger": d, "p10": 10.0, "p90": 20.0}
    assert [yer(k(d)) for d in (15, 21, 25, 26.5, 27, 5, 0)] == [
        "icinde", "ustunde", "ustunde_belirgin", "ustunde_belirgin", "ustunde_cok", "altinda_belirgin", "altinda_cok"]
    renk = app["palet"]("acik")["renk"]
    t = lambda d: {"ad": "Durarak uzun atlama", "deger": d, "p10": 10.0, "p90": 20.0, "birim": "cm", "kesin": True,
                   "tarih": "29.07.2026", "dusuk_iyi": False}
    kutu = lambda d: app["veli_sonuc_kutusu_html"](t(d), "Ali", "Erkek", False, renk)
    assert "aralığın biraz üstünde" in kutu(21) and app["VELI_DOGRU_MU_BASLIK"] not in kutu(21)
    assert "aralığın belirgin şekilde üstünde" in kutu(25) and app["VELI_DOGRU_MU_BASLIK"] not in kutu(25)
    assert "aralığın çok üstünde" in kutu(30) and "⚠ Değer doğru mu?" in kutu(30)
    d = app["veli_grup_aralik_durumu"]
    assert d(["icinde", "ustunde", "altinda"]) == ("Bu başlıkta 3 test yapıldı: 1 testte aralığın içinde, 1 testte "
                                                   "aralığın biraz üstünde, 1 testte aralığın biraz altında.")
    assert d(["icinde", "ustunde_belirgin"]) == ("Bu başlıkta 2 test yapıldı: 1 testte aralığın içinde, 1 testte "
                                                 "aralığın belirgin şekilde üstünde.")
    km = app["veli_konum_metni"]({**k(0), "cinsiyet": "Erkek", "birim": "cm"}, "Ali")
    assert "Ali bu aralığın çok altında." in km and app["VELI_DOGRU_MU"] in km




# ════════════════════════════════════════════════════════════
# 46. Paket 38g: karşılaştırma ekranı, olağandışı değer (normsuz), yaşıt kartı dili
# ════════════════════════════════════════════════════════════
def _modul(ad):
    import importlib
    return importlib.import_module(ad)


def _p38g_veri(d):
    """Üç sporcu (10 yaş kız, 24 ve 26 yaş erkek), iki oturum; atlama (yüksek iyi) ve mekik koşusu (düşük iyi)."""
    import pandas as _pd
    _pd.DataFrame({"Ad": ["Elif", "Onur", "Tolga"], "Soyad": ["Demo"] * 3, "Yaş": [10, 24, 26],
                   "Cinsiyet": ["Kadın", "Erkek", "Erkek"]}).to_excel(d / "sporcular.xlsx", index=False)
    satir = []
    for oturum, tarih, ek in (("S1", "15.09.2026", 0), ("S2", "25.10.2026", 1)):
        for s, atl, kos in (("Elif Demo", 120, 21.0), ("Onur Demo", 230, 17.0), ("Tolga Demo", 220, 18.0)):
            satir.append({"Sporcu": s, "Test": "Durarak Uzun Atlama", "Tarih": tarih, "Oturum": oturum,
                          "Deneme 1 (cm)": atl + 5 * ek})
            satir.append({"Sporcu": s, "Test": "10x5m Mekik Koşusu (Shuttle Run)", "Tarih": tarih, "Oturum": oturum,
                          "Süre (sn)": kos - 0.5 * ek})
    _pd.DataFrame(satir).to_excel(d / "test_sonuclari.xlsx", index=False)


def test_46a_karsilastirma_ekrani_sekmeler_ve_pasif(tmp_path, monkeypatch):
    """
    Sonuçlar → 'Karşılaştırma' bölümü (üst düzey segment): iki sekme, 'Kapsam' radio'su yok; Karşılaştır'a basılmadan
    sonuç bölümü pasif (ipucu); basınca tablo + grup özetleri; karışık yaş/cinsiyet uyarısı ve 11 yaş altı notu;
    seçim değişince 'eski' notu.
    """
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.run()
    assert [b.label for b in at.get("button_group")] == ["Bölüm"]
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs] == ["Genel", "Oturumlar arası", "Kulüpler arası"]   # 38o: Genel = sporcular arası
    assert not [r for r in at.radio if r.label == "Kapsam"]
    assert any("Önce sporcuları seçip Karşılaştır'a basın." in m.value for m in at.markdown)
    assert not at.dataframe
    for s in ("Elif Demo", "Onur Demo"):
        at.checkbox(key=f"ksa_a::k::{s}").check()
    at.checkbox(key="ksa_b::k::Tolga Demo").check()
    at.run()
    at.selectbox(key="ksa_test").select("Durarak Uzun Atlama").run()
    at.button(key="ksa_karsilastir").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert not any("Önce sporcuları seçip" in m.value for m in at.markdown)
    tablo = at.dataframe[0].value
    assert list(tablo["Grup"]) == ["A", "A", "B"] and set(tablo["Değer"]) == {125.0, 235.0, 225.0}   # son oturum
    assert any(w.value.startswith("Yaş ve cinsiyet karışık; ham değerler karşılaştırılıyor.") for w in at.warning)
    assert any("11 yaş altı sporcu var" in i.value for i in at.info)
    ozet = [m.value for m in at.markdown if m.value.startswith("**Grup")]
    assert len(ozet) == 2 and all("ortalama" in o and "aralık" in o and "P25" not in o for o in ozet)   # n < 20
    at.checkbox(key="ksa_a::k::Elif Demo").uncheck().run()
    assert any("sonuç eski" in i.value for i in at.info)


def test_46b_kars_kurallari_yuzdelik_siralama_karisik(tmp_path, monkeypatch):
    """n < 20: yüzdelik yok, n ≥ 20: çeyrekler; 11 yaş altı varsa sıralama yok (ada göre), yoksa yöne göre; karışık."""
    K = _modul("olcut.karsilastirma")
    assert K.grup_ozeti([1, 2, 3])["p25"] is None and K.grup_ozeti([])["n"] == 0
    oz = K.grup_ozeti(list(range(1, 21)))
    assert oz["n"] == 20 and oz["p25"] == 5.75 and oz["p75"] == 15.25
    monkeypatch.chdir(tmp_path)
    _p38g_veri(tmp_path)
    import pandas as _pd
    df = _pd.read_excel(tmp_path / "test_sonuclari.xlsx")
    r = K.sporcular_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["Tolga Demo", "Onur Demo", "Elif Demo"])
    assert r["kucuk"] and r["karisik"] and [x["Sporcu"] for x in r["satirlar"]] == ["Elif Demo", "Onur Demo", "Tolga Demo"]
    r2 = K.sporcular_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["Tolga Demo", "Onur Demo"], oturumlar=["S1"])
    assert not r2["kucuk"] and [x["Değer"] for x in r2["satirlar"]] == [230.0, 220.0]             # en iyi önce
    r3 = K.sporcular_arasi(df, "10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)", ["Tolga Demo", "Onur Demo"])
    assert [x["Sporcu"] for x in r3["satirlar"]] == ["Onur Demo", "Tolga Demo"]                    # süre: kısa iyi
    assert K.karisik_mi({"a": {"yas": 24, "cinsiyet": "Erkek"}, "b": {"yas": 24, "cinsiyet": "Erkek"}}) is False


def test_46c_oturumlar_arasi_yon_ve_cocuk(tmp_path, monkeypatch):
    """Önce/Sonra/Fark: sürede düşüş 'daha iyi', atlamada artış 'daha iyi'; 11 yaş altında yalnız arttı/azaldı."""
    K = _modul("olcut.karsilastirma")
    monkeypatch.chdir(tmp_path)
    _p38g_veri(tmp_path)
    import pandas as _pd
    df = _pd.read_excel(tmp_path / "test_sonuclari.xlsx")
    kos = {x["Sporcu"]: x for x in K.oturumlar_arasi(df, "10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)",
                                                       ["S1"], ["S2"])["satirlar"]}
    assert kos["Onur Demo"]["Fark"] == -0.5 and kos["Onur Demo"]["Yön"] == "✓ daha iyi"
    assert kos["Elif Demo"]["Yön"] == "▼ azaldı"                                     # 10 yaş: etiket yok
    atl = {x["Sporcu"]: x for x in K.oturumlar_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)",
                                                       ["S1"], ["S2"])["satirlar"]}
    assert atl["Tolga Demo"]["Yön"] == "✓ daha iyi" and atl["Elif Demo"]["Yön"] == "▲ arttı"
    assert set(K.oturum_etiketleri(df).values()) == {"S2 (25.10.2026) · 3 sporcu", "S1 (15.09.2026) · 3 sporcu"}


def test_46d_wilcoxon_ve_etki():
    """Kesin dağılım (SciPy ile aynı), sıfır fark atılır, n < 6 test yok, eşitlikte normal yaklaşım."""
    W = _modul("olcut.karsilastirma").wilcoxon_isaretli_sira
    a = W([1, 2, 3, 4, 5, 6])
    assert a["p"] == 0.03125 and a["r"] == 1.0 and a["yontem"] == "kesin"
    assert W([1, -2, 3, 4, 5, 6, 7, 8])["p"] == 0.0234375
    assert W([1, 2, 0, 0, 3, 4, 5]) == {"n": 5, "yetersiz": True}
    e = W([1, 1, 2, 2, 3, -3, 4, 5])
    assert e["yontem"] == "normal yaklaşım" and abs(e["p"] - 0.09169) < 1e-4


def test_46e_normsuz_testte_olagandisi_uyari_engel_yok(tmp_path, monkeypatch, app):
    """
    Normu olmayan değişkende: önceki ölçümün ×3'ü / ÷3'ü ve dünya rekorunun ötesi uyarılır; norm varsa eski yol aynen;
    uyarı kaydı engellemez (oturum_kayitlari kaydı yine üretir).
    """
    t = app["makullukte_uyarilar"]
    test, deg = "Koordinasyon Parkuru (TSYT)", "Süre (sn)"
    assert t(test, {deg: "999"}, 10, "Erkek") == []                                # önceki yok: sınır yok
    u = t(test, {deg: "90"}, 10, "Erkek", onceki={deg: (25.0, "01.09.2026")})
    assert len(u) == 1 and "üç katından fazla" in u[0] and "01.09.2026" in u[0]
    assert "üçte birinden az" in t(test, {deg: "7"}, 10, "Erkek", onceki={deg: (25.0, "")})[0]
    assert t(test, {deg: "30"}, 10, "Erkek", onceki={deg: (25.0, "")}) == []
    r = t("100m Sprint", {"100m Sprint (sn)": "9.1"}, 24, "Erkek")
    assert len(r) == 1 and "dünya rekorunun" in r[0] and "Usain Bolt" in r[0]       # sürede rekordan kısa
    assert t("100m Sprint", {"100m Sprint (sn)": "10.5"}, 24, "Erkek") == []
    assert t("10x5m Mekik Koşusu (Shuttle Run)", {"Süre (sn)": "21.7"}, 10, "Erkek",
             onceki={"Süre (sn)": (5.0, "")}) == []                                  # norm var: eski yol
    import pandas as _pd
    monkeypatch.chdir(tmp_path)
    _pd.DataFrame({"Sporcu": ["Ali A"], "Test": [test], "Tarih": ["01.09.2026"], deg: [25.0]}).to_excel(
        tmp_path / "test_sonuclari.xlsx", index=False)
    tablo = _pd.DataFrame({"Sporcu": ["Ali A"], f"{test} › {deg}": ["90"]})
    kay, uy = app["oturum_kayitlari"](tablo, {"Ali A": {"Yaş": 10, "Cinsiyet": "Erkek"}}, {test: [deg]}, "-", "-",
                                      None, __import__("datetime").date(2026, 10, 1), {})
    assert len(kay) == 1 and kay[0][deg] == "90" and any("üç katından fazla" in x for x in uy)


def test_46f_yasit_karti_ve_veli_notu(app):
    """Yaşıt kartı: biraz / belirgin şekilde / çok + doğru mu (antrenör dili). Veli kutusu: uyarı varken sabit not yok."""
    yk = _modul("olcut.sayfalar.sonuclar").yasit_karti_metni
    k = lambda d: {"n": 25, "p10": 10.0, "p90": 20.0, "birim": "cm", "deger": d}
    assert "biraz üstünde" in yk(k(21), "Ali") and "Değer doğru mu?" not in yk(k(21), "Ali")
    assert "belirgin şekilde üstünde" in yk(k(25), "Ali")
    m = yk(k(30), "Ali")
    assert "çok üstünde" in m and "Değer doğru mu?" in m and "antrenörle" not in m and "sorun" not in m
    renk = app["palet"]("acik")["renk"]
    t = lambda d: {"ad": "Atlama", "deger": d, "p10": 10.0, "p90": 20.0, "birim": "cm", "kesin": True,
                   "tarih": "29.07.2026", "dusuk_iyi": False}
    not_ = app["VELI_ARALIK_NOTU"]
    assert not_ in app["veli_sonuc_kutusu_html"](t(21), "Ali", "Erkek", False, renk)
    cok = app["veli_sonuc_kutusu_html"](t(30), "Ali", "Erkek", False, renk)
    assert "Değer doğru mu?" in cok and not_ not in cok



# ════════════════════════════════════════════════════════════
# 47. Paket 38i: tek tıkla PDF (veli / antrenör raporu), karşılaştırma tablosunu Excel / CSV indirme
# ════════════════════════════════════════════════════════════
def _indirme_kaydi(monkeypatch):
    """st.download_button çağrılarını (etiket, veri, dosya adı, anahtar) kaydeder; düğme yine çizilir."""
    from streamlit.delta_generator import DeltaGenerator
    asil, kayit = DeltaGenerator.download_button, []

    def sar(self, label, data, file_name=None, *a, **k):
        kayit.append({"etiket": label, "veri": data, "ad": file_name, "anahtar": k.get("key")})
        return asil(self, label, data, file_name, *a, **k)
    monkeypatch.setattr(DeltaGenerator, "download_button", sar)
    return kayit


def _rapor_sayfasi(tmp_path, monkeypatch, cevir):
    D = _modul("olcut.disa_aktarma")
    R = _modul("olcut.sayfalar.raporlar")
    girdi = []

    def sahte(html, ceviriciler=None):
        girdi.append(html)
        return cevir(html)
    monkeypatch.setattr(R, "pdf_cevir", sahte)
    R.rapor_pdf.clear()
    kayit = _indirme_kaydi(monkeypatch)
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    at.session_state["sayfa"] = "Raporlar"
    at.session_state["rapor_sporcu"] = "Elif Demo"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    R.rapor_pdf.clear()
    return at, kayit, girdi, D


def test_47a_guvenli_dosya_adi_ve_cevirici_yedegi():
    """Türkçe harf/boşluk dosya adında güvenli; çevirici yoksa ya da hata verirse (None, None), hata fırlamaz."""
    D = _modul("olcut.disa_aktarma")
    import datetime as _dt
    assert D.tarih_eki(_dt.date(2026, 10, 9)) == "09102026"
    assert D.guvenli_dosya_adi("Veli_raporu", "Şükrü Çağlar İğdeli", "09102026") == \
        "Veli_raporu_Sukru_Caglar_Igdeli_09102026"
    assert D.guvenli_dosya_adi("a/b:c*?", "  ") == "a_b_c"

    def bozuk(_):
        raise RuntimeError("yok")
    assert D.pdf_cevir("<p>x</p>", (("bozuk", bozuk), ("bos", lambda h: None), ("html", lambda h: b"<html>"))) \
        == (None, None)
    assert D.pdf_cevir("<p>x</p>", (("bozuk", bozuk), ("iyi", lambda h: b"%PDF-1.7 ..."))) == (b"%PDF-1.7 ...", "iyi")


def test_47b_gercek_pdf_turkce_ve_svg():
    """Kurulu çevirici varsa gerçek çıktı %PDF ile başlar ve tamdır (Edge/Chrome/WeasyPrint/xhtml2pdf)."""
    D = _modul("olcut.disa_aktarma")
    if not D.pdf_cevirici():
        pytest.skip("Bu bilgisayarda PDF çevirici yok (yedek yol 47d'de sınanıyor)")
    html = ('<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>@page{size:A4;margin:16mm}</style>'
            '</head><body><h1>Çağrı Işık — ğüşiöç İĞÜŞÖÇ</h1><svg width="120" height="40"><rect width="120" '
            'height="40"/></svg></body></html>')
    veri, ad = D.pdf_cevir(html)
    assert veri[:4] == b"%PDF" and b"%%EOF" in veri[-1024:], ad


def test_47c_rapor_pdf_dugmesi_ve_icerik_ozdesligi(tmp_path, monkeypatch, app):
    """
    Veri varken iki raporda da 'PDF olarak indir'; bayt %PDF, dosya adı güvenli (Veli_raporu_Elif_Demo_GGAAYYYY.pdf).
    PDF'e giren HTML ekrandaki rapor HTML'inin kendisi (yeni metin/alan yok, başka sporcu adı yok).
    """
    at, kayit, girdi, D = _rapor_sayfasi(tmp_path, monkeypatch, lambda h: (b"%PDF-1.7 sahte\n%%EOF", "sahte"))
    pdf = [k for k in kayit if k["etiket"] == "PDF olarak indir"]
    assert [k["ad"] for k in pdf] == [f"Veli_raporu_Elif_Demo_{D.tarih_eki()}.pdf",
                                      f"Antrenor_raporu_Elif_Demo_{D.tarih_eki()}.pdf"]
    assert all(k["veri"][:4] == b"%PDF" for k in pdf)
    assert all(re.fullmatch(r"[A-Za-z0-9_.-]+", k["ad"]) for k in kayit)
    v = app["rapor_verisi"]("Elif Demo")
    assert girdi[:2] == [app["veli_raporu_html"](v), app["antrenor_raporu_html"](v)]
    html_indir = {k["anahtar"]: k["veri"].decode("utf-8") for k in kayit if k["ad"].endswith(".html")}
    assert html_indir == {"veli_indir": girdi[0], "ant_indir": girdi[1]}
    assert "Onur" not in girdi[0] and "Tolga" not in girdi[0]
    assert "@page { size: A4;" in girdi[0] and "page-break-inside: avoid" in girdi[0]


def test_47d_rapor_pdf_cevirici_yoksa_yazdirma_yolu(tmp_path, monkeypatch):
    """Çevirici yoksa PDF düğmesi yok; yazdırmaya hazır HTML ve adım adım talimat; uygulama çökmez."""
    at, kayit, girdi, D = _rapor_sayfasi(tmp_path, monkeypatch, lambda h: (None, None))
    assert not [k for k in kayit if k["ad"].endswith(".pdf")]
    assert [k["etiket"] for k in kayit] == ["Yazdırmaya hazır HTML indir"] * 2
    assert sum("PDF olarak kaydet" in i.value for i in at.info) == 2


def _kars_df(tmp_path, monkeypatch):
    import pandas as _pd
    monkeypatch.chdir(tmp_path)
    _p38g_veri(tmp_path)
    return _pd.read_excel(tmp_path / "test_sonuclari.xlsx")


def test_47e_kars_disa_aktarma_ekranla_ayni(tmp_path, monkeypatch):
    """
    Sporcular arası / oturumlar arası dışa aktarma: satırlar, sıra ve değerler hesap sonucuyla (ekran tablosu) aynı;
    oturum adı kayıttan; 11 yaş altında sıra/yüzdelik/iyi-kötü sütunu ve etiketi yok; n < 20'de çeyrek yok.
    """
    K = _modul("olcut.karsilastirma")
    df = _kars_df(tmp_path, monkeypatch)
    r = K.sporcular_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["Elif Demo", "Onur Demo"], ["Tolga Demo"])
    t = K.sporcular_arasi_disa(df, r, "Durarak Uzun Atlama", "Deneme 1 (cm)")
    assert list(t.columns) == ["Sporcu", "Grup", "Yaş", "Cinsiyet", "Test", "Değişken", "Birim", "Ölçüm tarihi",
                               "Oturum", "Değer"]
    assert list(t["Değer"]) == [x["Değer"] for x in r["satirlar"]] and list(t["Grup"]) == ["A", "A", "B"]
    assert set(t["Oturum"]) == {"S2"} and set(t["Ölçüm tarihi"]) == {"25.10.2026"}
    yasak = {"Sıra", "Yüzdelik", "Persentil", "P25", "P75", "Yorum"}
    oz = K.grup_ozeti_disa(r)
    assert not (yasak & set(t.columns)) and not (yasak & set(oz.columns))
    assert list(oz["Ortalama"]) == [r["ozet"]["A"]["ortalama"], r["ozet"]["B"]["ortalama"]]
    r1 = K.sporcular_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["Onur Demo"], oturumlar=["S1"])
    t1 = K.sporcular_arasi_disa(df, r1, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["S1"])
    assert list(t1["Oturum"]) == ["S1"] and list(t1["Değer"]) == [230.0]
    ro = K.oturumlar_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["S1"], ["S2"])
    to = K.oturumlar_arasi_disa(ro, "Durarak Uzun Atlama", "Deneme 1 (cm)", "S1", "S2")
    assert list(to.columns) == ["Sporcu", "Yaş", "Test", "Değişken", "Birim", "Önce oturum", "Sonra oturum", "Önce",
                                "Sonra", "Fark", "Yön"]
    assert list(to["Fark"]) == [x["Fark"] for x in ro["satirlar"]]
    elif_ = to[to["Sporcu"] == "Elif Demo"].iloc[0]
    assert elif_["Yön"] == "▲ arttı" and "iyi" not in elif_["Yön"] and "kötü" not in elif_["Yön"]
    w = K.wilcoxon_isaretli_sira([1, 2, 3, 4, 5, 6])
    ist = K.istatistik_disa(w)
    assert ist.iloc[0]["p"] == w["p"] and ist.iloc[0]["Etki büyüklüğü r"] == w["r"]
    assert list(K.csv_ile_istatistik(to, w).columns)[-2:] == ["p (Wilcoxon)", "Etki büyüklüğü r"]
    assert list(K.csv_ile_istatistik(to, None).columns) == list(to.columns)
    assert "Not" in K.istatistik_disa(K.wilcoxon_isaretli_sira([1, 2])).columns


def test_47f_csv_ve_excel_geri_okuma(tmp_path, monkeypatch):
    """CSV: UTF-8 BOM, ';' ayırıcı, ondalık virgül — geri okununca Türkçe başlıklar ve değerler aynı. Excel: sayfalar."""
    import io as _io
    import pandas as _pd
    D, K = _modul("olcut.disa_aktarma"), _modul("olcut.karsilastirma")
    df = _kars_df(tmp_path, monkeypatch)
    r = K.sporcular_arasi(df, "10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)", ["Onur Demo", "Tolga Demo"])
    t = K.sporcular_arasi_disa(df, r, "10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)")
    b = D.tablo_csv(t)
    assert b[:3] == b"\xef\xbb\xbf" and b"\r\n" in b and ";" in b.decode("utf-8-sig").splitlines()[0]
    geri = _pd.read_csv(_io.BytesIO(b), sep=";", decimal=",", encoding="utf-8-sig")
    assert list(geri.columns) == list(t.columns) and "Ölçüm tarihi" in geri.columns and "Değişken" in geri.columns
    assert list(geri["Değer"]) == list(t["Değer"]) and list(geri["Sporcu"]) == ["Onur Demo", "Tolga Demo"]
    assert "16,5" in b.decode("utf-8-sig") and ";24;" in b.decode("utf-8-sig")     # yaş tam sayı (ekrandaki gibi)
    x = _pd.read_excel(_io.BytesIO(D.tablo_xlsx({"Sonuçlar": t, "Grup özeti": K.grup_ozeti_disa(r),
                                                  "İstatistik": _pd.DataFrame()})), sheet_name=None)
    assert list(x) == ["Sonuçlar", "Grup özeti"] and list(x["Sonuçlar"]["Değer"]) == list(t["Değer"])


def test_47g_kars_ekraninda_indirme_dugmeleri(tmp_path, monkeypatch):
    """Karşılaştır'dan sonra iki sekmede de Excel + CSV; dosya adı Karsilastirma_<tur>_<GGAAYYYY>; CSV değerleri
    ekrandaki tablonun değerleri."""
    import io as _io
    import pandas as _pd
    D = _modul("olcut.disa_aktarma")
    kayit = _indirme_kaydi(monkeypatch)
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert not kayit                                            # Karşılaştır'a basılmadan indirme yok
    for s in ("Onur Demo", "Tolga Demo"):
        at.checkbox(key=f"ksa_a::k::{s}").check()
    at.run()
    at.selectbox(key="ksa_test").select("Durarak Uzun Atlama").run()
    at.button(key="ksa_karsilastir").click().run()
    assert not at.exception, [e.value for e in at.exception]
    son = {k["anahtar"]: k for k in kayit}
    assert son["ksa_indir_xlsx"]["ad"] == f"Karsilastirma_sporcular_{D.tarih_eki()}.xlsx"
    assert son["ksa_indir_csv"]["ad"] == f"Karsilastirma_sporcular_{D.tarih_eki()}.csv"
    ekran = at.dataframe[0].value
    geri = _pd.read_csv(_io.BytesIO(son["ksa_indir_csv"]["veri"]), sep=";", decimal=",", encoding="utf-8-sig")
    assert list(geri["Sporcu"]) == list(ekran["Sporcu"]) and list(geri["Değer"]) == list(ekran["Değer"])
    at.checkbox(key="koa_once::k::S1").check()
    at.checkbox(key="koa_sonra::k::S2").check()
    at.run()
    at.selectbox(key="koa_test").select("Durarak Uzun Atlama").run()
    at.checkbox(key="koa_ist").check().run()
    at.button(key="koa_karsilastir").click().run()
    assert not at.exception, [e.value for e in at.exception]
    son = {k["anahtar"]: k for k in kayit}
    assert son["koa_indir_xlsx"]["ad"] == f"Karsilastirma_oturumlar_{D.tarih_eki()}.xlsx"
    geri = _pd.read_csv(_io.BytesIO(son["koa_indir_csv"]["veri"]), sep=";", decimal=",", encoding="utf-8-sig")
    ekran = at.dataframe[-1].value
    assert list(geri["Fark"]) == list(ekran["Fark"]) and list(geri["Yön"]) == list(ekran["Yön"])
    assert list(geri["Önce oturum"].unique()) == ["S1"]                    # Paket 38j: oturumun adı, etiket değil



# ════════════════════════════════════════════════════════════
# 47 (devam). Paket 38j: 38i denetim düzeltmeleri
# ════════════════════════════════════════════════════════════
def _p38j_noktali_oturumlar(d):
    """_p38g_veri, oturum adları " · " içerir (demo verisindeki gibi)."""
    import pandas as _pd
    _p38g_veri(d)
    t = _pd.read_excel(d / "test_sonuclari.xlsx")
    t["Oturum"] = t["Oturum"].map({"S1": "Demo · Ön Test", "S2": "Demo · Son Test"})
    t.to_excel(d / "test_sonuclari.xlsx", index=False)


def test_47h_oturum_adi_nokta_isaretiyle_bozulmaz(tmp_path, monkeypatch):
    """Oturum adında " · " varken dışa aktarmada 'Önce oturum' / 'Sonra oturum' tam ad ve birbirinden farklı."""
    import io as _io
    import pandas as _pd
    kayit = _indirme_kaydi(monkeypatch)
    at = _apptest(tmp_path, monkeypatch, _p38j_noktali_oturumlar)
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    at.checkbox(key="koa_once::k::Demo · Ön Test").check()
    at.checkbox(key="koa_sonra::k::Demo · Son Test").check()
    at.run()
    at.selectbox(key="koa_test").select("Durarak Uzun Atlama").run()
    at.button(key="koa_karsilastir").click().run()
    assert not at.exception, [e.value for e in at.exception]
    son = {k["anahtar"]: k for k in kayit}
    geri = _pd.read_csv(_io.BytesIO(son["koa_indir_csv"]["veri"]), sep=";", decimal=",", encoding="utf-8-sig")
    assert set(geri["Önce oturum"]) == {"Demo · Ön Test"} and set(geri["Sonra oturum"]) == {"Demo · Son Test"}
    x = _pd.read_excel(_io.BytesIO(son["koa_indir_xlsx"]["veri"]), sheet_name="Sonuçlar")
    assert set(x["Önce oturum"]) != set(x["Sonra oturum"])
    K = _modul("olcut.karsilastirma")
    df = _pd.read_excel(tmp_path / "test_sonuclari.xlsx")
    assert K.oturum_adlari(df, ["Demo · Ön Test", "Demo · Son Test"]) == "Demo · Ön Test, Demo · Son Test"


def test_47i_pdf_cevirici_sure_siniri(monkeypatch):
    """
    Tarayıcı süreci + dosya yoklaması tek toplam süre (PDF_SURE_SN = 20). Dosya yazmadan hemen dönen ya da hiç
    dönmeyen sahte tarayıcıda pdf_cevir sınır + küçük pay içinde (None, None) döner; süreç kapatılır.
    """
    import sys as _sys
    import time as _time
    D = _modul("olcut.disa_aktarma")
    assert D.PDF_SURE_SN == 20
    monkeypatch.setattr(D, "PDF_SURE_SN", 1.5)
    for sahte in ([_sys.executable, "-c", "pass"], [_sys.executable, "-c", "import time; time.sleep(60)"]):
        bas = _time.monotonic()
        sonuc = D.pdf_cevir("<p>x</p>", (("tarayıcı", lambda h: D._tarayici_ile(h, sahte)),))
        gecen = _time.monotonic() - bas
        assert sonuc == (None, None) and gecen < 1.5 + 2.5, (sahte[-1], gecen)


def test_47j_formul_enjeksiyonu_yalniz_metinde(tmp_path, monkeypatch):
    """Metin '=1+1' → "'=1+1" (CSV ve Excel); sayısal Fark -0.5 sayı olarak kalır."""
    import io as _io
    import openpyxl
    import pandas as _pd
    D = _modul("olcut.disa_aktarma")
    t = _pd.DataFrame({"Sporcu": ["=1+1", "@SUM(A1)", "Ali", "-Ali", "\tx"], "Fark": [-0.5, 1.0, -2.25, 0.0, 3.0],
                       "Yön": ["✓ daha iyi"] * 5})
    geri = _pd.read_csv(_io.BytesIO(D.tablo_csv(t)), sep=";", decimal=",", encoding="utf-8-sig")
    assert list(geri["Sporcu"])[:4] == ["'=1+1", "'@SUM(A1)", "Ali", "'-Ali"]
    assert list(geri["Fark"]) == [-0.5, 1.0, -2.25, 0.0] + [3.0] and geri["Fark"].dtype.kind == "f"
    assert "\r\n=1+1" not in D.tablo_csv(t).decode("utf-8-sig") and "-0,5" in D.tablo_csv(t).decode("utf-8-sig")
    sayfa = openpyxl.load_workbook(_io.BytesIO(D.tablo_xlsx({"Sonuçlar": t})))["Sonuçlar"]
    assert sayfa["A2"].value == "'=1+1" and sayfa["A2"].data_type == "s"
    assert sayfa["B2"].value == -0.5 and sayfa["B2"].data_type == "n"
    assert list(t["Sporcu"])[0] == "=1+1"                       # kaynak tablo değişmez


def test_47k_oturma_yuksekligi_tsyt_eslesir_eslestirme_degismez(tmp_path, monkeypatch):
    """
    SH (Opstoel 2015) TSYT oturma yüksekliği kaydından da okunur (aynı ölçü: oturma yüzeyinden vertekse net yükseklik).
    SH antropometri: eşleştirme değişkenlerine girmez, eşleştirme sonucu değişmez.
    """
    import pandas as _pd
    A = _modul("olcut.analiz")
    monkeypatch.chdir(tmp_path)
    _pd.DataFrame({"Ad": ["Elif"], "Soyad": ["Demo"], "Yaş": [10], "Cinsiyet": ["Kadın"], "Boy (cm)": [140],
                   "Kilo (kg)": [33]}).to_excel(tmp_path / "sporcular.xlsx", index=False)
    df = _pd.DataFrame([{"Sporcu": "Elif Demo", "Test": "Oturma Yüksekliği (TSYT)", "Tarih": "01.09.2026",
                         "Oturma Yüksekliği (cm)": 73.5, "Test Yaşı": 10}])
    f = A.sporcu_fsc_profili(df, "Elif Demo")
    assert f["degerler"]["SH"]["deger"] == 73.5 and f["degerler"]["SH"]["kaynak"] == "Oturma Yüksekliği (TSYT)"
    assert "SH" not in f["eksik"] and "SH" not in A.ESLESTIRME_DEGISKENLERI
    eski = A.sporcu_fsc_profili(df.assign(Test="Başka test"), "Elif Demo")
    assert "SH" in eski["eksik"]
    # FSC testi de okunur; ikisi varsa en son tarihli kayıt
    df2 = _pd.concat([df, _pd.DataFrame([{"Sporcu": "Elif Demo", "Test": "Oturma Yüksekliği", "Tarih": "01.10.2026",
                                          "Oturma Yüksekliği (cm)": 74.0, "Test Yaşı": 10}])])
    df2["Tarih_dt"] = _pd.to_datetime(df2["Tarih"], format="%d.%m.%Y")
    assert A.sporcu_fsc_profili(df2, "Elif Demo")["degerler"]["SH"]["deger"] == 74.0



# ════════════════════════════════════════════════════════════
# 48. Paket 38k: Ana Sayfa düğmesi, Hakkında sayfası, alt bilgi satırı, kullanım istatistiği kapalı
# ════════════════════════════════════════════════════════════
_P38K_SAYFALAR = ["Ana Sayfa", "Sporcu Girişi", "Niteliğe göre test bul", "Test Uygula", "Test Oturumu",
                  "Sonuçları Görüntüle", "Raporlar", "Kaynakça", "Hakkında"]


def _duz_agac(at):
    """Ana gövdedeki öğeler belge sırasıyla (iç içe kapsayıcılar açılır)."""
    sira = []

    def yuru(d):
        for c in (d.children.values() if isinstance(getattr(d, "children", None), dict) else ()):
            sira.append(c)
            yuru(c)
    yuru(at.main)
    return sira


def _alt_bilgi_sayisi(at, M):
    return sum(M.ALT_BILGI_METNI in str(getattr(m, "value", "")) for m in at.markdown)


def test_48a_hakkinda_sayfasi(tmp_path, monkeypatch):
    """Menüde Kaynakça'dan sonra 'Hakkında'; bütün bölümler, verilen metinler aynen, mailto ve sürüm sabiti."""
    M, O = _modul("veri.metinler"), _modul("olcut.ortak")
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    # Paket 38k: Ana Sayfa · Raporlar · Kaynakça · Hakkında üst menüde; sol menüde yalnız iş sayfaları
    assert [b.label for b in at.button if (b.key or "").startswith("ust-menu-")] ==         ["⌂ Ana Sayfa", "Raporlar", "Kaynakça", "Hakkında"]
    assert [b.label for b in at.sidebar.button if (b.key or "").startswith("yan-menu-")] ==         ["Sporcu Girişi", "Niteliğe göre test bul", "Test Uygula", "Test Oturumu", "Sonuçları Görüntüle"]
    at.button(key="ust-menu-hakkinda").click().run()
    assert at.session_state["sayfa"] == "Hakkında"
    assert not at.exception, [e.value for e in at.exception]
    assert [h.value for h in at.subheader] == ["Ölçüt nedir?", "Misyon", "Vizyon", "İlkelerimiz", "Ekip",
                                               "Bilgilendirme", "Veri gizliliği", "İletişim", "Sürüm"]
    metin = "\n".join(m.value for m in at.markdown)
    for _, govde in M.HAKKINDA_BOLUMLERI:
        assert govde in metin
    for m in M.HAKKINDA_ILKELER + M.HAKKINDA_BILGILENDIRME + [M.HAKKINDA_GIZLILIK]:
        assert m in metin, m
    for _, kisiler in M.HAKKINDA_EKIP:
        assert all(k in metin for k in kisiler)
    assert "- **Geliştirici:** Öğr. Gör. Müslim Ertuğrul KAYIŞOĞLU\n" in metin and "doktora" not in metin
    assert "Amacımız, hiçbir çocuğun kendisine uymayan bir branşta yıllarını kaybetmemesidir." in metin
    assert "[ertugrulkayisoglu@gmail.com](mailto:ertugrulkayisoglu@gmail.com)" in metin
    assert O.SURUM.startswith("Paket ") and O.SURUM in metin
    assert [h.value for h in at.header] == ["Ölçüt Hakkında"] and "Öğr. Gör. Dr. İlyas KARAKAŞ" in metin
    assert M.ALT_BILGI_METNI == "© 2026 Ölçüt · Tüm hakları saklıdır."


def test_48b_ust_menu_ve_alt_bilgi_her_sayfada(tmp_path, monkeypatch):
    """
    Üst menü (⌂ Ana Sayfa · Raporlar · Kaynakça · Hakkında) her sayfada ana alanın en üstünde; bulunulan sayfa '-aktif'
    (kalın + altı çizili). Sol menü iş sayfaları (38l: alt alta düğmeler); üst menü sayfasındayken hiçbiri etkin
    değil. Alt bilgi her sayfada tek ve en sonda.
    """
    M = _modul("veri.metinler")
    kod = {"Ana Sayfa": "ana-sayfa", "Raporlar": "raporlar", "Kaynakça": "kaynakca", "Hakkında": "hakkinda"}
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    for sayfa in _P38K_SAYFALAR:
        at.session_state["sayfa"] = sayfa
        at.run()
        assert not at.exception, (sayfa, [e.value for e in at.exception])
        ust = [b.key for b in at.button if (b.key or "").startswith("ust-menu-")]
        beklenen = [f"ust-menu-{k}" + ("-aktif" if s_ == sayfa else "") for s_, k in kod.items()]
        assert ust == beklenen, sayfa
        etkin = [b.label for b in at.sidebar.button if (b.key or "").endswith("-aktif")]
        assert etkin == ([] if sayfa in kod else [sayfa]), sayfa
        assert _alt_bilgi_sayisi(at, M) == 1, sayfa
        assert len([b for b in at.button if b.key == "alt_hakkinda"]) == (0 if sayfa == "Hakkında" else 1), sayfa
        sira = _duz_agac(at)
        dugmeler = [c.key for c in sira if type(c).__name__ == "Button"]
        assert dugmeler[:2] == ["ust-kulup-ekle", beklenen[0]], sayfa     # menü ana alanın en üstünde (38n: + Kulüp)
        assert getattr(sira[-1], "key", None) in ("alt_hakkinda", "alt_kulupler") or M.ALT_BILGI_METNI in str(
            getattr(sira[-1], "value", "")), sayfa                        # alt bilgi en sonda (38n: + Kulüpler)
    at.session_state["sayfa"] = "Kaynakça"
    at.run()
    at.button(key="ust-menu-ana-sayfa").click().run()
    assert at.session_state["sayfa"] == "Ana Sayfa"
    at.button(key="ust-menu-raporlar").click().run()
    assert at.session_state["sayfa"] == "Raporlar" and any(h.value == "Raporlar" for h in at.header)
    at.button(key="yan-menu-test-uygula").click().run()
    assert at.session_state["sayfa"] == "Test Uygula" and         [b.key for b in at.sidebar.button if (b.key or "").endswith("-aktif")] == ["yan-menu-test-uygula-aktif"]
    at.button(key="alt_hakkinda").click().run()
    assert at.session_state["sayfa"] == "Hakkında" and any(h.value == "Misyon" for h in at.subheader)
    assert not [b for b in at.sidebar.button if (b.key or "").endswith("-aktif")]


def test_48c_test_oturumundan_cikista_taslak_kalir(tmp_path, monkeypatch):
    """
    Test Oturumu Sıradaki kipinde üst menüden ⌂ Ana Sayfa: taslak diskte aynen kalır (veri kaybı yok). Alt bilgi alt çubuğun
    ALTINDA (belgede sonra), ölçüm düğmelerinin arasına girmez.
    """
    T, K = _modul("olcut.sayfalar.test_oturumu"), _modul("olcut.kayit")
    M = _modul("veri.metinler")

    def hazirla(d):
        _p38g_veri(d)
        t = T.taslak_bos(["Durarak Uzun Atlama"], ["Elif Demo", "Onur Demo"], {"tarih": "2026-10-29"})
        t["degerler"]["Elif Demo"] = {K.oturum_sutunu("Durarak Uzun Atlama", "Deneme 1 (cm)"): "131"}
        assert T.taslak_yaz(t, str(d / T.TASLAK_DOSYA))
    at = _apptest(tmp_path, monkeypatch, hazirla)
    at.session_state["sayfa"] = "Test Oturumu"
    at.session_state["ots::otomatik"] = True
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    sira = _duz_agac(at)
    anahtar = [getattr(c, "key", None) for c in sira]
    alt = next(i for i, c in enumerate(sira) if M.ALT_BILGI_METNI in str(getattr(c, "value", "")))
    assert "ot_geri" in anahtar and anahtar.index("ot_geri") < alt and anahtar.index("ust-kulup-ekle") == min(
        i for i, k in enumerate(anahtar) if k)
    at.button(key="ust-menu-ana-sayfa").click().run()
    assert not at.exception and at.session_state["sayfa"] == "Ana Sayfa"
    disk = T.taslak_oku(str(tmp_path / T.TASLAK_DOSYA))
    assert disk and disk["degerler"]["Elif Demo"] == {K.oturum_sutunu("Durarak Uzun Atlama", "Deneme 1 (cm)"): "131"}


def test_48d_kullanim_istatistigi_kapali_ve_ag_cagrisi_yok(app):
    """
    config.toml'da browser.gatherUsageStats = false (Streamlit'in varsayılanı açık). Uygulama kodunda ağ kitaplığı
    (requests, urllib, http, socket…) içe aktarılmaz ve dış adrese bağlantı yoktur.
    """
    import tomllib
    for yer in ("kurulu", "tema", "ortak", None):
        assert tomllib.loads(app["tema_toml"](yer))["browser"]["gatherUsageStats"] is False
    kok = os.path.dirname(DOSYA)
    sorun = []
    for yol in _kaynak_dosyalari(veri=True):
        agac = ast.parse(_oku(yol))
        for d in ast.walk(agac):
            adlar = ([a.name for a in d.names] if isinstance(d, ast.Import)
                     else [d.module or ""] if isinstance(d, ast.ImportFrom) else [])
            sorun += [f"{os.path.relpath(yol, kok)}: {a}" for a in adlar
                      if a.split(".")[0] in ("requests", "urllib", "urllib3", "http", "socket", "httpx", "aiohttp",
                                             "ftplib", "smtplib")]
    assert not sorun, sorun


def test_48e_raporlara_alt_bilgi_girmez(app):
    """Alt bilgi ve gezinme yalnız uygulama sayfasında; veli/antrenör rapor HTML'inde yok."""
    M = _modul("veri.metinler")
    v = app["rapor_verisi"]("Yok Sporcu")
    for html in (app["veli_raporu_html"](v), app["antrenor_raporu_html"](v)):
        assert M.ALT_BILGI_METNI not in html and "⌂" not in html and "Tüm hakları saklıdır" not in html


# ════════════════════════════════════════════════════════════
# 49. Paket 38l: sol menü listesi ve "Bugün" kartı
# ════════════════════════════════════════════════════════════
def test_49a_yan_menu_liste_simge_ve_tek_tik(tmp_path, monkeypatch):
    """Sol menü: beş iş sayfası alt alta, her biri simgeli; tek tık sayfayı açar, etkin satır '-aktif'."""
    B = _modul("olcut.bilesenler")
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    assert not at.sidebar.selectbox                                  # açılır kutu kalktı
    yan = [b for b in at.sidebar.button if (b.key or "").startswith("yan-menu-")]
    assert [b.label for b in yan] == list(B.YAN_MENU_SIMGELERI)
    assert all(b.proto.icon == B.YAN_MENU_SIMGELERI[b.label] for b in yan)
    for b in list(B.YAN_MENU_SIMGELERI):
        anahtar = next(x.key for x in at.sidebar.button if x.label == b)
        at.button(key=anahtar).click().run()
        assert not at.exception, (b, [e.value for e in at.exception])
        assert at.session_state["sayfa"] == b
        assert [x.label for x in at.sidebar.button if (x.key or "").endswith("-aktif")] == [b]


def test_49b_bugun_karti_ozet_ve_taslaga_donus(tmp_path, monkeypatch):
    """
    'Bugün' kartı: sporcu sayısı ve son oturum (ad · tarih · sporcu sayısı); sporcu adı yok. Diskte taslak varsa
    'Yarım kalan oturum: N değer' + 'Devam et' → Test Oturumu taslakla açılır; Test Oturumu'ndayken düğme yok.
    """
    T, K = _modul("olcut.sayfalar.test_oturumu"), _modul("olcut.kayit")
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "<b>3</b> sporcu kayıtlı" in kart and "Son oturum: S2 (25.10.2026) · 3 sporcu" in kart
    assert not any(ad in kart for ad in ("Elif", "Onur", "Tolga")) and "Yarım kalan" not in kart
    assert not [b for b in at.sidebar.button if b.key == "bugun_taslak"]
    t = T.taslak_bos(["Durarak Uzun Atlama"], ["Elif Demo", "Onur Demo"], {"tarih": "2026-10-29"})
    t["degerler"]["Elif Demo"] = {K.oturum_sutunu("Durarak Uzun Atlama", "Deneme 1 (cm)"): "131"}
    assert T.taslak_yaz(t, str(tmp_path / T.TASLAK_DOSYA))
    at.run()
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "Yarım kalan oturum: <b>1</b> değer girildi" in kart
    at.button(key="bugun_taslak").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["sayfa"] == "Test Oturumu" and at.session_state["ots::taslak"]["degerler"] == t["degerler"]
    assert not [b for b in at.sidebar.button if b.key == "bugun_taslak"]


def test_49c_bugun_karti_bos_veride_cokmez(tmp_path, monkeypatch):
    """Sporcu/sonuç dosyası yokken kart: 0 sporcu, 'Henüz kayıtlı ölçüm yok.'; hata yok."""
    at = _apptest(tmp_path, monkeypatch, lambda d: None)
    assert not at.exception, [e.value for e in at.exception]
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "<b>0</b> sporcu kayıtlı" in kart and "Henüz kayıtlı ölçüm yok." in kart



# ════════════════════════════════════════════════════════════
# 50. Paket 38n-1: kulüp bazında çalışma alanı (veri yalıtımı), Kulüpler sayfası
# ════════════════════════════════════════════════════════════
def _p38n_kulupler(d):
    """
    Genel: _p38g_veri (Elif 10 K, Onur 24 E, Tolga 26 E). Kulüp A: Elif + Onur; Kulüp B: yalnız Tolga (adı 'Tolga
    Demo' — A'da hiçbir yerde görünmemeli). Kulüpler kulupler/<kod>/ altında, bugünkü dosya adlarıyla.
    """
    import pandas as _pd
    K = _modul("olcut.kulup")
    _p38g_veri(d)
    sp = _pd.read_excel(d / "sporcular.xlsx")
    ts = _pd.read_excel(d / "test_sonuclari.xlsx")
    for ad, kisiler in (("Demo Kulüp A", ["Elif", "Onur"]), ("Demo Kulüp B", ["Tolga"])):
        kod = K.kulup_olustur({"ad": ad, "sehir": "Ankara"})
        k = d / "kulupler" / kod
        sp[sp["Ad"].isin(kisiler)].to_excel(k / "sporcular.xlsx", index=False)
        ts[ts["Sporcu"].isin([f"{x} Demo" for x in kisiler])].to_excel(k / "test_sonuclari.xlsx", index=False)


def _agac_metni(at):
    parca = []

    def yuru(n):
        for c in (n.children.values() if isinstance(getattr(n, "children", None), dict) else ()):
            p = getattr(c, "proto", None)
            parca.append(str(p) if p is not None else "")
            yuru(c)
    yuru(at._tree)
    return "\n".join(parca)


def test_50a_veri_yolu_genel_ve_kulup(tmp_path, monkeypatch):
    """Genel ya da Streamlit dışı: dosya adı olduğu gibi (bugünkü davranış); kulüpte kulupler/<kod>/ad; geçersiz kod
    (../ gibi) Genel'e düşer — klasör dışına çıkılmaz."""
    O = _modul("olcut.ortak")
    assert O.veri_yolu("sporcular.xlsx") == "sporcular.xlsx" and O.aktif_kulup() == ""
    for kotu in ("../x", "A B", "arslan_sk", "", "-a"):
        assert not O.KULUP_KODU_KALIBI.match(kotu), kotu
    assert O.KULUP_KODU_KALIBI.match("arslan-sk") and O.kulup_klasoru("arslan-sk") == os.path.join("kulupler",
                                                                                                    "arslan-sk")


def test_50b_kulup_olustur_kod_arsiv_ve_klasorsuz_bugunku_gibi(tmp_path, monkeypatch):
    """Kod Türkçe harfsiz ve tekil; klasör + kulup.json + başlık satırlı boş xlsx; arşiv gizler, silmez. 'kulupler'
    yokken seçici hiç görünmez (ekran bugünkü gibi)."""
    import json as _json
    K = _modul("olcut.kulup")
    monkeypatch.chdir(tmp_path)
    assert K.kulupler() == {}
    assert K.kulup_kodu("Gordion Buz Sporları") == "gordion-buz-sporlari"
    assert K.kulup_kodu("Poyraz Karate Kulübü") == "poyraz-karate-kulubu"
    assert K.kulup_kodu("Arslan SK", ["arslan-sk"]) == "arslan-sk-2"
    kod = K.kulup_olustur({"ad": "Arslan SK", "branslar": ["Futbol"]})
    k = tmp_path / "kulupler" / kod
    assert sorted(os.listdir(k)) == ["ilgi_anketi.xlsx", "kulup.json", "sporcular.xlsx", "test_sonuclari.xlsx"]
    b = _json.loads((k / "kulup.json").read_text(encoding="utf-8"))
    assert b["ad"] == "Arslan SK" and b["karsilastirma_onayi"] is False and b["arsiv"] is False
    assert set(b) == set(K.KULUP_ALANLARI)
    assert K.kulup_arsivle(kod) and K.kulupler() == {} and list(K.kulupler(arsiv=True)) == [kod] and k.exists()
    bos = tmp_path / "bos"
    bos.mkdir()
    at = _apptest(bos, monkeypatch, _p38g_veri)
    assert not at.exception and not [s for s in at.selectbox if s.key == "calisma_alani_secici"]


def test_50c_kulup_a_seciliyken_b_hicbir_yerde_yok(tmp_path, monkeypatch):
    """
    A seçiliyken her sayfada (sporcu listelerinin göründüğü hâller dahil), indirmelerde ve Bugün kartında B'nin sporcusu
    (Tolga Demo) yok; A'nın sporcusu var. Genel'e dönünce üçü de görünür.
    """
    import io as _io
    import pandas as _pd
    kayit = _indirme_kaydi(monkeypatch)
    at = _apptest(tmp_path, monkeypatch, _p38n_kulupler)
    secici = at.selectbox(key="calisma_alani_secici")
    assert secici.options == [
        "Çalışma alanı: Genel", "Çalışma alanı: Demo Kulüp A", "Çalışma alanı: Demo Kulüp B"]
    secici.select("demo-kulup-a").run()
    assert at.session_state["calisma_alani"] == "demo-kulup-a" and at.session_state["sayfa"] == "Ana Sayfa"
    durumlar = [("Ana Sayfa", {}), ("Sporcu Girişi", {}), ("Test Uygula", {}), ("Test Oturumu", {}),
                ("Test Oturumu", {"ot_adim": 2, "ots::testler": ["Durarak Uzun Atlama"]}),
                ("Sonuçları Görüntüle", {}), ("Sonuçları Görüntüle", {"sonuc_bolum": "Karşılaştırma"}),
                ("Sonuçları Görüntüle", {"sonuc_bolum": "Kayıt düzelt"}),          # Paket 38s
                ("Raporlar", {}), ("Niteliğe göre test bul", {}), ("Kulüpler", {})]
    for sayfa, ek in durumlar:
        at.session_state["sayfa"] = sayfa
        for k, v in ek.items():
            at.session_state[k] = v
        at.run()
        assert not at.exception, (sayfa, [e.value for e in at.exception])
        metin = _agac_metni(at)
        assert "Tolga Demo" not in metin, (sayfa, ek)
    # sporcu seçicileri yalnız A
    at.session_state["sayfa"] = "Raporlar"
    at.run()
    assert set(at.selectbox(key="rapor_sporcu").options) == {"Elif Demo", "Onur Demo"}
    assert all(b"Tolga" not in (k["veri"] if isinstance(k["veri"], bytes) else str(k["veri"]).encode())
               for k in kayit)
    # karşılaştırma indirmesi: A'nın 'Tümünü seç'i yalnız A
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    for s in ("Elif Demo", "Onur Demo"):
        at.checkbox(key=f"ksa_a::k::{s}").check()
    assert not [c for c in at.checkbox if (c.key or "").endswith("Tolga Demo")]
    at.run()
    at.selectbox(key="ksa_test").select("Durarak Uzun Atlama").run()
    at.button(key="ksa_karsilastir").click().run()
    csv = next(k["veri"] for k in reversed(kayit) if k["anahtar"] == "ksa_indir_csv")
    geri = _pd.read_csv(_io.BytesIO(csv), sep=";", decimal=",", encoding="utf-8-sig")
    assert set(geri["Sporcu"]) == {"Elif Demo", "Onur Demo"}
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "<b>2</b> sporcu kayıtlı" in kart
    # Genel: üçü de
    at.selectbox(key="calisma_alani_secici").select("").run()
    at.session_state["sayfa"] = "Raporlar"
    at.run()
    assert set(at.selectbox(key="rapor_sporcu").options) == {"Elif Demo", "Onur Demo", "Tolga Demo"}


def test_50d_kulup_degisince_secimler_taslak_ve_onbellek_karismaz(tmp_path, monkeypatch):
    """A'da seçimler + diskte taslak; B'ye geçince seçimler silinir, Ana Sayfa açılır, B'de taslak yok, Bugün kartı B'nin
    sayısını gösterir; A'ya dönünce A'nın taslağı (diskte) yine görünür."""
    T, K = _modul("olcut.sayfalar.test_oturumu"), _modul("olcut.kayit")
    at = _apptest(tmp_path, monkeypatch, _p38n_kulupler)
    at.selectbox(key="calisma_alani_secici").select("demo-kulup-a").run()
    t = T.taslak_bos(["Durarak Uzun Atlama"], ["Elif Demo"], {"tarih": "2026-10-29"})
    t["degerler"]["Elif Demo"] = {K.oturum_sutunu("Durarak Uzun Atlama", "Deneme 1 (cm)"): "131"}
    assert T.taslak_yaz(t, str(tmp_path / "kulupler" / "demo-kulup-a" / T.TASLAK_DOSYA))
    assert not (tmp_path / T.TASLAK_DOSYA).exists()
    at.session_state["sayfa"] = "Raporlar"
    at.run()
    at.session_state["ksa_a::secim"] = ["Elif Demo"]
    at.run()
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "Yarım kalan oturum" in kart and "<b>2</b> sporcu" in kart
    at.selectbox(key="calisma_alani_secici").select("demo-kulup-b").run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["sayfa"] == "Ana Sayfa" and "ksa_a::secim" not in at.session_state
    assert "rapor_sporcu" not in at.session_state
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "Yarım kalan oturum" not in kart and "<b>1</b> sporcu" in kart
    assert "Elif Demo" not in _agac_metni(at)
    at.selectbox(key="calisma_alani_secici").select("demo-kulup-a").run()
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "Yarım kalan oturum: <b>1</b> değer girildi" in kart


def test_50e_kulupler_sayfasi_olustur_duzenle_arsivle(tmp_path, monkeypatch):
    """Kulüpler sayfası (alt bilgiden): yeni kulüp formu klasörü açar; 'Bu kulübe geç'; aktif kulüp arşivlenince
    Genel'e dönülür; arşiv hiçbir dosyayı silmez."""
    K = _modul("olcut.kulup")
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    at.button(key="alt_kulupler").click().run()
    assert at.session_state["sayfa"] == "Kulüpler" and not at.exception
    assert not [b for b in at.button if b.key == "alt_kulupler"]
    at.text_input(key="kl_yeni_ad").input("Gordion Buz Sporları")
    at.text_input(key="kl_yeni_sehir").input("Ankara")
    at.button(key="FormSubmitter:kl_yeni-Kulübü oluştur").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert (tmp_path / "kulupler" / "gordion-buz-sporlari" / "sporcular.xlsx").exists()
    assert K.kulup_oku("gordion-buz-sporlari")["sehir"] == "Ankara"
    at.run()
    assert [s for s in at.selectbox if s.key == "calisma_alani_secici"]          # artık seçici görünür
    at.button(key="kl_gec").click().run()
    assert at.session_state["calisma_alani"] == "gordion-buz-sporlari" and at.session_state["sayfa"] == "Ana Sayfa"
    kart = " ".join(m.value for m in at.sidebar.markdown if "sp-bugun" in m.value)
    assert "<b>0</b> sporcu kayıtlı" in kart
    at.session_state["sayfa"] = "Kulüpler"
    at.run()
    at.button(key="kl_arsivle").click().run()
    assert at.session_state["calisma_alani"] == "" and K.kulupler() == {}
    assert (tmp_path / "kulupler" / "gordion-buz-sporlari" / "kulup.json").exists()


def test_50f_yeni_kulupte_her_sayfa_bos_veriyle_acilir(tmp_path, monkeypatch):
    """Yeni (boş) kulüpte bütün sayfalar hata vermeden açılır."""
    K = _modul("olcut.kulup")

    def hazirla(d):
        K.kulup_olustur({"ad": "Boş Kulüp"})
    at = _apptest(tmp_path, monkeypatch, hazirla)
    at.selectbox(key="calisma_alani_secici").select("bos-kulup").run()
    for sayfa in _P38K_SAYFALAR + ["Kulüpler"]:
        at.session_state["sayfa"] = sayfa
        at.run()
        assert not at.exception, (sayfa, [e.value for e in at.exception])


def test_50g_ust_satirda_kulup_ekle(tmp_path, monkeypatch):
    """Üst satırda her zaman (kulüp yokken de) '+ Kulüp'; tıklayınca Kulüpler sayfası, 'Yeni kulüp' formu açık."""
    at = _apptest(tmp_path, monkeypatch, _p38g_veri)
    b = at.button(key="ust-kulup-ekle")
    assert b.label == "Kulüp" and b.proto.icon == ":material/add:"
    b.click().run()
    assert not at.exception and at.session_state["sayfa"] == "Kulüpler"
    assert [e for e in _acilirlar(at) if e.label == "Yeni kulüp" and e.proto.expanded]
    assert "kl_yeni_ac" not in at.session_state                       # bir kez açar



# ════════════════════════════════════════════════════════════
# 51. Paket 38o: Karşılaştırma sekmeleri (Genel · Oturumlar arası · Kulüpler arası)
# ════════════════════════════════════════════════════════════
def _p38o_kulup_tablolari(ad_on, n_kiz, n_erkek, yas, atlama0):
    """n_kiz kız + n_erkek erkek, hepsi aynı yaşta; Durarak Uzun Atlama bir oturumda. Adlar '<ad_on><i> Kulup'."""
    import pandas as _pd
    sp, ts = [], []
    for i in range(n_kiz + n_erkek):
        cins = "Kadın" if i < n_kiz else "Erkek"
        sp.append({"Ad": f"{ad_on}{i}", "Soyad": "Kulup", "Yaş": yas, "Cinsiyet": cins})
        ts.append({"Sporcu": f"{ad_on}{i} Kulup", "Test": "Durarak Uzun Atlama", "Tarih": "01.10.2026",
                   "Oturum": "S1", "Deneme 1 (cm)": atlama0 + i})
    return _pd.DataFrame(sp), _pd.DataFrame(ts)


def _p38o_kulupler(onay_a=True, onay_b=True, onay_c=False):
    def hazirla(d):
        K = _modul("olcut.kulup")
        _p38g_veri(d)
        for ad, on, onay, kiz, erkek in (("Arslan SK", "Arslan", onay_a, 12, 3), ("Poyraz Karate", "Poyraz", onay_b, 11, 0),
                                         ("Gordion Buz", "Gordion", onay_c, 12, 0)):
            kod = K.kulup_olustur({"ad": ad, "karsilastirma_onayi": onay})
            sp, ts = _p38o_kulup_tablolari(on, kiz, erkek, 10, 120)
            sp.to_excel(d / "kulupler" / kod / "sporcular.xlsx", index=False)
            ts.to_excel(d / "kulupler" / kod / "test_sonuclari.xlsx", index=False)
    return hazirla


def test_51a_kulupler_arasi_hesap_kurallari():
    """Hücre: yaş bandı × cinsiyet; n < 10 değer yok; en küçük/en büyük yok; çeyrek yalnız n ≥ 20; sporcu adı yok;
    sıra bant → cinsiyet → verilen kulüp sırası (başarıya göre değil)."""
    K = _modul("olcut.karsilastirma")
    assert [K.yas_bandi(y) for y in (5, 6, 8.9, 9, 11, 11.5, 12, 17, 18, 40, None)] == \
        [None, "6–8", "6–8", "9–11", "9–11", "9–11", "12–14", "15–17", "18+", "18+", None]
    sp_a, ts_a = _p38o_kulup_tablolari("A", 12, 3, 10, 100)     # kız 12 (gösterilir), erkek 3 (yetersiz)
    sp_b, ts_b = _p38o_kulup_tablolari("B", 25, 0, 13, 150)     # 12–14 kız 25 → çeyrekler de
    r = K.kulupler_arasi([("Arslan SK", sp_a, ts_a), ("Kulüp 1", sp_b, ts_b)], "Durarak Uzun Atlama",
                         "Deneme 1 (cm)")
    s = {(x["Kulüp"], x["Cinsiyet"]): x for x in r["satirlar"]}
    assert [(x["Yaş bandı"], x["Cinsiyet"], x["Kulüp"]) for x in r["satirlar"]] == [
        ("9–11", "Erkek", "Arslan SK"), ("9–11", "Kadın", "Arslan SK"), ("12–14", "Kadın", "Kulüp 1")]
    kiz = s[("Arslan SK", "Kadın")]
    assert kiz["n"] == 12 and kiz["Ortalama"] == round(sum(range(100, 112)) / 12, 2) and kiz["P25"] is None
    erkek = s[("Arslan SK", "Erkek")]
    assert erkek["n"] == 3 and erkek["Ortalama"] is None and erkek["Not"].startswith("yetersiz")
    assert s[("Kulüp 1", "Kadın")]["P25"] is not None and s[("Kulüp 1", "Kadın")]["n"] == 25
    assert all(not ({"En küçük", "En büyük", "Sporcu"} & set(x)) for x in r["satirlar"])
    assert "Kulup" not in repr(r) and "A0" not in repr(r)


def test_51b_karsilastirma_sekmeleri_ve_kulupler_arasi(tmp_path, monkeypatch):
    """
    Sekmeler: Genel · Oturumlar arası · Kulüpler arası. Kulüpler arası: yalnız onaylı kulüpler; seçili kulüp adıyla,
    öteki kodlu ('Kulüp 1'); onaysız kulüp seçiliyken kilitli; Genel'de hepsi kodlu; sonuçta sporcu adı yok.
    """
    at = _apptest(tmp_path, monkeypatch, _p38o_kulupler())
    at.selectbox(key="calisma_alani_secici").select("arslan-sk").run()
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs] == ["Genel", "Oturumlar arası", "Kulüpler arası"]
    assert any("Katılan kulüpler: Arslan SK, Kulüp 1" in c.value for c in at.caption)
    assert not any("Gordion" in c.value or "Poyraz" in c.value for c in at.caption)
    at.button(key="kka_karsilastir").click().run()
    tablo = at.dataframe[-1].value
    assert set(tablo["Kulüp"]) == {"Arslan SK", "Kulüp 1"} and "Sporcu" not in tablo.columns
    kiz = tablo[(tablo["Kulüp"] == "Arslan SK") & (tablo["Cinsiyet"] == "Kadın")].iloc[0]
    assert kiz["n"] == 12 and abs(kiz["Ortalama"] - 125.5) < 1e-9
    assert tablo[(tablo["Kulüp"] == "Kulüp 1")].iloc[0]["n"] == 11
    sonuc = _agac_metni(at)
    assert "Poyraz0" not in sonuc and "Gordion0" not in sonuc               # başka kulübün sporcusu hiçbir yerde yok
    assert not ({"Poyraz Karate", "Gordion Buz"} & set(tablo["Kulüp"]))     # başka kulübün adı karşılaştırmada yok
    # Genel çalışma alanı: hepsi kodlu
    at.selectbox(key="calisma_alani_secici").select("").run()
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert any("Katılan kulüpler: Kulüp 1, Kulüp 2" in c.value for c in at.caption)
    # onaysız kulüp: kilitli
    at.selectbox(key="calisma_alani_secici").select("gordion-buz").run()
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert any("onay vermemiş" in i.value for i in at.info) and not [b for b in at.button if b.key == "kka_karsilastir"]


def test_51c_kulupler_arasi_tek_onayda_kapali(tmp_path, monkeypatch):
    """İkiden az onaylı kulüp: karşılaştırma yok, açıklama var."""
    at = _apptest(tmp_path, monkeypatch, _p38o_kulupler(onay_b=False))
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Karşılaştırma"
    at.run()
    assert not at.exception and any("en az iki kulübün onayı gerekli (şu an 1)" in i.value for i in at.info)



# ════════════════════════════════════════════════════════════
# 52. Paket 38n-2: kulüp raporu
# ════════════════════════════════════════════════════════════
def _p38n2_tablolar(yas=10, n=8):
    """n sporcu (yarısı kız), iki oturum; Durarak Uzun Atlama (normlu) ve BOT-2 diz üstü şınav (kıyas yok)."""
    import pandas as _pd
    sp, ts = [], []
    for i in range(n):
        ad = f"Cocuk{i}"
        sp.append({"Ad": ad, "Soyad": "Kulup", "Yaş": yas, "Cinsiyet": "Kadın" if i % 2 else "Erkek"})
        for oturum, tarih, ek in (("Ön Test", "15.09.2026", 0), ("Son Test", "25.10.2026", 3)):
            ts.append({"Sporcu": f"{ad} Kulup", "Test": "Durarak Uzun Atlama", "Tarih": tarih, "Oturum": oturum,
                       "Test Yaşı": yas, "Deneme 1 (cm)": 110 + 5 * i + ek})
            ts.append({"Sporcu": f"{ad} Kulup", "Test": "Diz Üstü Şınav — 30 sn (BOT-2)", "Tarih": tarih,
                       "Oturum": oturum, "Test Yaşı": yas, "Tekrar": 10 + i + ek})
    df_sp, df = _pd.DataFrame(sp), _pd.DataFrame(ts)
    df["Tarih_dt"] = _pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
    return df_sp, df


def _kr_html(tmp_path, monkeypatch, yas=10, n=8, ek=False):
    """oturumlar_arasi yaşı aktif çalışma alanının sporcular.xlsx'inden okur: test klasörü kulübün klasörü gibi."""
    KR = _modul("olcut.kulup_raporu")
    monkeypatch.chdir(tmp_path)
    df_sp, df = _p38n2_tablolar(yas, n)
    df_sp.to_excel(tmp_path / "sporcular.xlsx", index=False)
    df.drop(columns="Tarih_dt").to_excel(tmp_path / "test_sonuclari.xlsx", index=False)
    import datetime as _dt
    return KR.kulup_raporu_html({"ad": "Arslan SK", "sehir": "Ankara"}, df_sp, df, sporcu_listesi=ek,
                                bugun=_dt.date(2026, 10, 30))


def test_52a_kulup_raporu_icerik_ve_isim_yok(tmp_path, monkeypatch):
    """Başlık, tarih, sayı, yaş bandı × cinsiyet, oturumlar, test konumu, değişim; ek kapalıyken hiçbir ad yok; yüzdelik
    yok; 11 yaş altında 'daha iyi/kötü' yok; normsuz testte konum yok; n ≥ 6'da Wilcoxon."""
    h = _kr_html(tmp_path, monkeypatch)
    for parca in ("Arslan SK — Kulüp raporu", "Rapor tarihi: 30.10.2026", "Kayıtlı sporcu: 8",
                  "<td>9–11</td><td>4</td><td>4</td><td>0</td><td>8</td>", "<td>Ön Test</td><td>15.09.2026</td><td>8</td>",
                  "Ön Test (15.09.2026) → Son Test (25.10.2026)", "<td>Durarak Uzun Atlama</td><td>8</td>",
                  "8 (norm kıyası yok)", "p = ", "▲ arttı 8"):
        assert parca in h, parca
    assert "Cocuk" not in h and "Kulup</td>" not in h
    assert "✓ daha iyi" not in h and "! daha kötü" not in h                 # 11 yaş altı: yön etiketi yok
    assert not re.search(r"\bP\d{1,2}\b|persentil|yüzdelik dilim", h.split("</style>")[1])
    satir = re.search(r"<td>Durarak Uzun Atlama</td><td>8</td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td>",
                      h)
    assert satir and sum(map(int, satir.groups())) == 8                      # altında + içinde + üstünde + yok = n


def test_52b_kulup_raporu_kurallar_kucuk_n_yetiskin_ek(tmp_path, monkeypatch):
    """n < 6: yalnız tanımlayıcı. Yetişkinde 'daha iyi' olabilir. Ek açık: ad, yaş, cinsiyet, oturum — değer yok."""
    h = _kr_html(tmp_path, monkeypatch, n=4)
    assert "değişen sporcu 4 &lt; 6: yalnız tanımlayıcı" in h and "p = " not in h     # 38p: değişen sporcu dili
    (tmp_path / "y").mkdir()
    hy = _kr_html(tmp_path / "y", monkeypatch, yas=24, n=8)
    assert "✓ daha iyi 8" in hy
    (tmp_path / "e").mkdir()
    he = _kr_html(tmp_path / "e", monkeypatch, ek=True)
    ek = he.split("Ek: Sporcu listesi")[1]
    assert "<td>Cocuk0 Kulup</td><td>10</td><td>Erkek</td><td>Ön Test, Son Test</td>" in ek
    assert not re.search(r"<td>1[1-9]\d</td>", ek)                            # atlama değerleri (110+) yok
    assert "Cocuk" not in he.split("Ek: Sporcu listesi")[0]                  # ek dışında yine ad yok


def test_52c_raporlar_sayfasinda_kulup_raporu_sekmesi(tmp_path, monkeypatch):
    """Sekme yalnız kulüp seçiliyken; PDF adı Kulup_raporu_<Kulüp>_<GGAAYYYY>.pdf; ek kapalıyken PDF'e giren HTML'de ad yok,
    açılınca var; başka kulübün sporcusu yok."""
    D, R = _modul("olcut.disa_aktarma"), _modul("olcut.sayfalar.raporlar")
    girdi = []
    monkeypatch.setattr(R, "pdf_cevir", lambda html, c=None: (girdi.append(html), (b"%PDF-1.7 x\n%%EOF", "s"))[1])
    R.rapor_pdf.clear()
    R.kulup_raporu_onbellekli.clear()
    kayit = _indirme_kaydi(monkeypatch)
    at = _apptest(tmp_path, monkeypatch, _p38o_kulupler())
    at.session_state["sayfa"] = "Raporlar"
    at.run()
    assert [t.label for t in at.tabs] == ["Veli raporu", "Antrenör raporu"]          # Genel: kulüp sekmesi yok
    at.selectbox(key="calisma_alani_secici").select("arslan-sk").run()
    at.session_state["sayfa"] = "Raporlar"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs] == ["Veli raporu", "Antrenör raporu", "Kulüp raporu"]
    pdf = [k for k in kayit if k["anahtar"] == "kulup_indir_pdf"][-1]
    assert pdf["ad"] == f"Kulup_raporu_Arslan_SK_{D.tarih_eki()}.pdf"
    kr = next(h for h in reversed(girdi) if "Kulüp raporu" in h)
    assert "Arslan SK — Kulüp raporu" in kr and "Kayıtlı sporcu: 15" in kr
    assert "Arslan0" not in kr and "Poyraz" not in kr and "Gordion" not in kr
    at.checkbox(key="kr_ek").check().run()
    kr2 = next(h for h in reversed(girdi) if "Kulüp raporu" in h)
    assert "Ek: Sporcu listesi" in kr2 and "Arslan0 Kulup" in kr2 and "Poyraz" not in kr2
    R.rapor_pdf.clear()
    R.kulup_raporu_onbellekli.clear()




# ════════════════════════════════════════════════════════════
# 54. Paket 38p-2: ölçüm yaşı, kulüpler arası yaş/Z, birim, kulüp raporu düzeltmeleri
# ════════════════════════════════════════════════════════════
def _p38p_yas_verisi(d):
    """Kaan: profil yaşı bilerek 2 yıl geride (9), ölçüm günü yaşı 11 (Test Yaşı). Onur: 24."""
    import pandas as _pd
    _pd.DataFrame({"Ad": ["Kaan", "Onur"], "Soyad": ["Demo", "Demo"], "Yaş": [9, 24],
                   "Cinsiyet": ["Erkek", "Erkek"]}).to_excel(d / "sporcular.xlsx", index=False)
    satir = []
    for oturum, tarih, ek in (("S1", "15.09.2026", 0), ("S2", "25.10.2026", 6)):
        for s, yas, atl in (("Kaan Demo", 11, 165), ("Onur Demo", 24, 230)):
            satir.append({"Sporcu": s, "Test": "Durarak Uzun Atlama", "Tarih": tarih, "Oturum": oturum,
                          "Test Yaşı": yas, "Deneme 1 (cm)": atl + ek})
    _pd.DataFrame(satir).to_excel(d / "test_sonuclari.xlsx", index=False)


def test_54a_karsilastirma_z_olcum_yasiyla(tmp_path, monkeypatch):
    """Profil yaşı 2 yıl geride: karşılaştırma Yaş'ı ve Z'si ölçüm günündeki yaşla — sporcunun kendi Z'siyle aynı."""
    import pandas as _pd
    K, N = _modul("olcut.karsilastirma"), _modul("olcut.norm")
    monkeypatch.chdir(tmp_path)
    _p38p_yas_verisi(tmp_path)
    df = _pd.read_excel(tmp_path / "test_sonuclari.xlsx")
    df["Tarih_dt"] = _pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
    r = K.sporcular_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["Kaan Demo"], z=True)
    kaan = r["satirlar"][0]
    kendi = next(x for x in N.sporcu_z_profili(df, "Kaan Demo")["satirlar"] if x["Değişken"] == "Deneme 1 (cm)")
    assert kaan["Yaş"] == 11 and kaan["Z"] == round(kendi["Z"], 2)
    profil_z = N.yas_z_skoru("Durarak Uzun Atlama", "Deneme 1 (cm)", 9, "Erkek", 171)["z_performans"]
    assert abs(kaan["Z"] - round(profil_z, 2)) > 0.1                  # eski (profil yaşıyla) Z farklıydı
    assert r["kucuk"] is False                                        # ölçüm yaşı 11: 11 yaş kuralı uygulanmaz
    o = K.oturumlar_arasi(df, "Durarak Uzun Atlama", "Deneme 1 (cm)", ["S1"], ["S2"])
    satir = {x["Sporcu"]: x for x in o["satirlar"]}
    assert satir["Kaan Demo"]["Yaş"] == 11 and satir["Kaan Demo"]["Yön"] == "✓ daha iyi" and o["kucuk"] is False
    assert K.olcum_yasi({"yas": 9, "dogum": "01.01.2015"}, None, "02.01.2026") == 11.0
    assert K.olcum_yasi({"yas": 9, "dogum": None}, None, "02.01.2026") == 9


def test_54b_kulupler_arasi_olcum_yasi_ort_yas_ve_z():
    """Bant ölçüm yaşına göre; n ≥ 10 hücrede 'Ort. yaş'; isteğe bağlı 'Ort. Z' (Z'si olan ≥ 10)."""
    import pandas as _pd
    K = _modul("olcut.karsilastirma")
    sp = _pd.DataFrame({"Ad": [f"S{i}" for i in range(12)], "Soyad": ["K"] * 12, "Yaş": [8] * 12,
                        "Cinsiyet": ["Erkek"] * 12})
    ts = _pd.DataFrame([{"Sporcu": f"S{i} K", "Test": "Durarak Uzun Atlama", "Tarih": "01.10.2026", "Oturum": "S1",
                         "Test Yaşı": 10 + (i % 2), "Deneme 1 (cm)": 140 + i} for i in range(12)])
    r = K.kulupler_arasi([("Arslan SK", sp, ts)], "Durarak Uzun Atlama", "Deneme 1 (cm)", z=True)
    hucre = r["satirlar"][0]
    assert hucre["Yaş bandı"] == "9–11" and hucre["n"] == 12 and hucre["Ort. yaş"] == 10.5   # profil 8 değil
    assert hucre["Ort. Z"] is not None and list(hucre)[:6] == ["Yaş bandı", "Cinsiyet", "Kulüp", "n", "Ort. yaş",
                                                               "Ortalama"]
    kucuk = K.kulupler_arasi([("A", sp.head(5), ts.head(5))], "Durarak Uzun Atlama", "Deneme 1 (cm)", z=True)
    assert kucuk["satirlar"][0]["Ort. yaş"] is None and kucuk["satirlar"][0]["Ort. Z"] is None
    assert K.normlu_degisken("Durarak Uzun Atlama", "Deneme 1 (cm)") and \
        not K.normlu_degisken("Diz Üstü Şınav — 30 sn (BOT-2)", "Diz Üstü Şınav Tekrarı (30 sn)")


def test_54c_birim_p_ve_degisen_dili():
    """Parantez içi yalnız bilinen birimse birim; p < 0,001; 'değişen sporcu k < 6'."""
    Ky, K = _modul("olcut.kayit"), _modul("olcut.karsilastirma")
    assert [Ky._degisken_birimi(d) for d in ("Süre (sn)", "Diz Üstü Şınav Tekrarı (30 sn)", "Deneme 1 (puan)",
                                              "Deneme 1 (doğru sektirme, maks 10)", "Toplam Sıçrama (2 deneme)",
                                              "Asimetri İndeksi (%)")] == ["sn", "", "puan", "", "", "%"]
    assert K.degisken_birimi("Diz Üstü Şınav — 30 sn (BOT-2)", "Diz Üstü Şınav Tekrarı (30 sn)") == ""
    assert K.p_metni(0.0004) == "p < 0,001" and K.p_metni(0.0234) == "p = 0,023"
    assert K.degisen_yetersiz_metni({"n": 4, "yetersiz": True}) == "değişen sporcu 4 < 6: yalnız tanımlayıcı"


def test_54d_kulup_raporu_ana_sonuc_ve_vucut_olcusu(tmp_path, monkeypatch):
    """Değişim tablosu ana sonuçla: KTK toplamı, en iyi deneme; çok bileşenli test çıkar (not); vücut ölçüsünde test
    yok; ondalık virgül; yaş tablosu bugünkü yaşla (doğum tarihinden)."""
    import datetime as _dt
    import pandas as _pd
    KR = _modul("olcut.kulup_raporu")
    monkeypatch.chdir(tmp_path)
    sp = _pd.DataFrame({"Ad": [f"C{i}" for i in range(8)], "Soyad": ["K"] * 8, "Yaş": [8] * 8,
                        "Cinsiyet": ["Kadın"] * 8, "Doğum Tarihi": ["01.01.2016"] * 8})
    sp.to_excel(tmp_path / "sporcular.xlsx", index=False)
    ts = []
    for oturum, tarih, ek in (("Ön", "15.09.2026", 0), ("Son", "25.10.2026", 2)):
        for i in range(8):
            s = f"C{i} K"
            b = {"Sporcu": s, "Tarih": tarih, "Oturum": oturum, "Test Yaşı": 10}
            ts += [dict(b, Test="Yana Sıçrama (Jumping Sideways)", **{"Deneme 1 (sıçrama sayısı)": 20 + i + ek,
                                                                       "Deneme 2 (sıçrama sayısı)": 22 + i + ek}),
                   dict(b, Test="Top Sektirme — Alternatif El (BOT-2)",
                        **{"Deneme 1 (doğru sektirme, maks 10)": 5, "Deneme 2 (doğru sektirme, maks 10)": 6 + ek // 2}),
                   dict(b, Test="Kulaç Uzunluğu (TSYT)", **{"Kulaç Uzunluğu (cm)": 140 + i + ek}),
                   dict(b, Test="Boy ve Vücut Ağırlığı (TSYT)", **{"Boy (cm)": 140 + ek, "Vücut Ağırlığı (kg)": 33})]
    df = _pd.DataFrame(ts)
    df.to_excel(tmp_path / "test_sonuclari.xlsx", index=False)
    df["Tarih_dt"] = _pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
    _, satir, disari = KR.oturumlar_arasi_ozeti(df, KR.oturum_ozeti(df))
    s = {r[0]: r for r in satir}
    assert s["Yana Sıçrama (Jumping Sideways)"][1] == "Toplam Sıçrama (2 deneme)"
    assert s["Yana Sıçrama (Jumping Sideways)"][4] == "4,00 sıçrama"          # toplamda +4; birim normdan, "2 deneme" değil
    assert s["Top Sektirme — Alternatif El (BOT-2)"][1].startswith("En iyi deneme")
    assert s["Kulaç Uzunluğu (TSYT)"][5] == KR.KULUP_RAPOR_VUCUT and s["Kulaç Uzunluğu (TSYT)"][4] == "2,00 cm"
    assert disari == ["Boy ve Vücut Ağırlığı (TSYT)"]
    assert s["Yana Sıçrama (Jumping Sideways)"][5].startswith(("p = 0,", "p < 0,001"))
    h = KR.kulup_raporu_html({"ad": "A"}, sp, df, bugun=_dt.date(2026, 11, 2))
    assert "Çok bileşenli testler (ör. Boy ve Vücut Ağırlığı (TSYT)) bu özete girmez." in h
    assert "<td>9–11</td><td>8</td>" in h                                    # 01.01.2016 → bugün 10 (profil 8)

