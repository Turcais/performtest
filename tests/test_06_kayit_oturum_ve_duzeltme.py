"""
Tekli/toplu kayıt, çalışma şablonları, adım adım Test Oturumu, kayıt düzeltme (38s) ve tam yedek (38t).
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
# 15. Test oturumu / toplu giriş (Paket 10)
# ════════════════════════════════════════════════════════════
_ORNEK_SPORCU = {"Ad": "Deniz", "Soyad": "Deneme", "Yaş": 10, "Cinsiyet": "Erkek", "Boy (cm)": 141,
                 "Kilo (kg)": 34.0, "Doğum Tarihi": "15.02.2016", "Grup/Sınıf": "5-A"}


def _tekli_ve_toplu(app, test_adi, degerler_metin, tablo_degerleri):
    import pandas as pd
    from datetime import date
    tarih = date(2026, 3, 10)
    katalog = app["TEST_KATALOGU"]["Çocuk ve Genç Fiziksel Uygunluk Bataryaları"]["Eurofit Fiziksel Uygunluk Test Bataryası"]
    hes, _ = app["turetilmis_degerler"](test_adi, degerler_metin, _ORNEK_SPORCU, 34.0)
    tekli = app["test_kaydi_olustur"]("Deniz Deneme", _ORNEK_SPORCU, "Çocuk ve Genç Fiziksel Uygunluk Bataryaları",
                                      "Eurofit Fiziksel Uygunluk Test Bataryası", None, test_adi, tarih,
                                      degerler_metin, hes, "", None)
    tablo = pd.DataFrame([{"Sporcu": "Deniz Deneme",
                           **{app["oturum_sutunu"](test_adi, d): v for d, v in tablo_degerleri.items()}}])
    toplu, _ = app["oturum_kayitlari"](tablo, {"Deniz Deneme": _ORNEK_SPORCU},
                                       {test_adi: list(katalog[test_adi]["degiskenler"])},
                                       "Çocuk ve Genç Fiziksel Uygunluk Bataryaları",
                                       "Eurofit Fiziksel Uygunluk Test Bataryası", None, tarih,
                                       {"kimlik": "OT-test", "yer": "Salon", "uygulayici": "EK"})
    return tekli, toplu


def test_15a_toplu_kayit_tekli_ile_ayni_bicimde(app):
    """Aynı ölçüm tekli girişten ve toplu girişten geçince, oturum alanları dışında kayıt birebir aynı olmalı."""
    for test_adi, metin, sayisal in (
            ("Durarak Uzun Atlama", {"Deneme 1 (cm)": "140", "Deneme 2 (cm)": "146.5", "Deneme 3 (cm)": ""},
             {"Deneme 1 (cm)": 140.0, "Deneme 2 (cm)": 146.5, "Deneme 3 (cm)": None}),
            ("10x5m Mekik Koşusu (Shuttle Run)", {"Süre (sn)": "21.7"}, {"Süre (sn)": 21.7})):
        tekli, toplu = _tekli_ve_toplu(app, test_adi, metin, sayisal)
        assert len(toplu) == 1, f"{test_adi}: toplu giriş {len(toplu)} kayıt üretti"
        oturum = set(app["OTURUM_KOLONLARI"])
        t1 = {k: v for k, v in tekli.items() if k not in oturum}
        t2 = {k: v for k, v in toplu[0].items() if k not in oturum}
        assert list(tekli) == list(toplu[0]), f"{test_adi}: sütun sırası/kümesi farklı:\n{list(tekli)}\n{list(toplu[0])}"
        assert t1 == t2, f"{test_adi}: değerler farklı:\n{t1}\n{t2}"


def test_15b_oturum_alanlari_kayitta(app):
    """Oturum, Yer, Uygulayıcı her kayıtta olmalı (tekli girişte boş); META_KOLONLAR'da yer almalı."""
    tekli, toplu = _tekli_ve_toplu(app, "10x5m Mekik Koşusu (Shuttle Run)", {"Süre (sn)": "21.7"}, {"Süre (sn)": 21.7})
    for k in app["OTURUM_KOLONLARI"]:
        assert k in tekli and k in toplu[0], f"'{k}' kayıtta yok"
        assert k in app["META_KOLONLAR"], f"'{k}' META_KOLONLAR'da yok (grafiklerde değişken sanılır)"
    assert (toplu[0]["Oturum"], toplu[0]["Yer"], toplu[0]["Uygulayıcı"]) == ("OT-test", "Salon", "EK")
    assert tekli["Oturum"] == ""


def test_15c_bos_hucre_kaydedilmez_kismi_kayit_normal(app):
    import pandas as pd
    from datetime import date
    testler = {"Durarak Uzun Atlama": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"],
               "10x5m Mekik Koşusu (Shuttle Run)": ["Süre (sn)"]}
    s = app["oturum_sutunu"]
    tablo = pd.DataFrame([
        {"Sporcu": "A", s("Durarak Uzun Atlama", "Deneme 1 (cm)"): 150.0, s("Durarak Uzun Atlama", "Deneme 2 (cm)"): None,
         s("Durarak Uzun Atlama", "Deneme 3 (cm)"): None, s("10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)"): None},
        {"Sporcu": "B", s("Durarak Uzun Atlama", "Deneme 1 (cm)"): None, s("Durarak Uzun Atlama", "Deneme 2 (cm)"): None,
         s("Durarak Uzun Atlama", "Deneme 3 (cm)"): None, s("10x5m Mekik Koşusu (Shuttle Run)", "Süre (sn)"): None}])
    kayitlar, _ = app["oturum_kayitlari"](tablo, {"A": _ORNEK_SPORCU, "B": _ORNEK_SPORCU}, testler, "K", "B", None,
                                         date(2026, 3, 10), {"kimlik": "OT-x"})
    ozet = [(k["Sporcu"], k["Test"]) for k in kayitlar]
    assert ozet == [("A", "Durarak Uzun Atlama")], f"beklenen yalnız A/uzun atlama, çıkan {ozet}"
    assert kayitlar[0]["Deneme 2 (cm)"] == "" and kayitlar[0]["Deneme 1 (cm)"] == "150"


def test_15d_kayit_tek_yerde_uretiliyor(app, agac):
    """
    Kayıt sözlüğü ("Sporcu" ve "Test" anahtarlı) yalnızca test_kaydi_olustur'da kurulmalı; tekli ve toplu
    giriş bu fonksiyonu çağırmalı. turetilmis_degerler ekran (st.) çağrısı içermemeli.
    """
    sorunlar = []
    fonksiyonlar = {d.name: d for d in agac.body if isinstance(d, ast.FunctionDef)}
    kurucu = fonksiyonlar.get("test_kaydi_olustur")
    assert kurucu is not None, "test_kaydi_olustur yok"
    icindekiler = {id(n) for n in ast.walk(kurucu)}
    for d in ast.walk(agac):
        if isinstance(d, ast.Dict):
            anahtarlar = {k.value for k in d.keys if isinstance(k, ast.Constant)}
            if {"Sporcu", "Test", "Tarih"} <= anahtarlar and id(d) not in icindekiler:
                sorunlar.append(f"satır {d.lineno}: kayıt sözlüğü test_kaydi_olustur dışında kuruluyor")
    cagrilar = [d.lineno for d in ast.walk(agac) if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
                and d.func.id == "test_kaydi_olustur"]
    if len(cagrilar) < 2:
        sorunlar.append(f"test_kaydi_olustur yalnızca {len(cagrilar)} yerde çağrılıyor (tekli + toplu bekleniyor)")
    for ad in ("turetilmis_degerler", "oturum_kayitlari", "test_kaydi_olustur", "makul_aralik_bantlardan"):
        f = fonksiyonlar.get(ad)
        if f and any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "st"
                     for n in ast.walk(f)):
            sorunlar.append(f"{ad} Streamlit (st.) çağırıyor — toplu girişte ve denetimde kullanılamaz")
    assert not sorunlar, "Kayıt üretimi sorunu:" + _ozet(sorunlar)




# ── Paket 27: kendi test setini kurabilme ──
_NHT_G = "Nordic Hamstring Kuvvet Testi — Genel (NHT)"


def test_34a_arama_es_anlamli_sirali_turkce(app):
    """
    Arama: eş anlamlı etiketler (ölçülen nitelikten), sıralama tam > kelime başı > içinde, Türkçe karakter ve ek
    duyarsız (surat/sürat/süratı aynı). "sürat" ve "metre" 10m Sprint'i, "çeviklik/yön değiştirme/agility" T-testini bulur.
    """
    ara = lambda q: [t["ad"] for t in app["test_ara"](q)]
    for q in ("sürat", "hız", "metre", "hızlanma", "sprint"):
        assert "10m Sprint" in ara(q), q
    for q in ("çeviklik", "yön değiştirme", "agility"):
        assert "T-Testi (Çeviklik)" in ara(q), q
    assert ara("surat") == ara("sürat") == ara("süratı") == ara("SÜRAT")
    assert ara("10m Sprint")[0] == "10m Sprint"                                   # tam eşleşme önde
    k = app["ara_katla"]
    for q in ("güç", "el", "kuvvet"):     # "güç", "el": katalog sırasında içinde geçenler kelime başlarından önce
        seviye = []
        for t in app["test_ara"](q):
            kel = k(t["ad"]).split() + [w for e in app["test_etiketleri"](t["ad"]) for w in k(e).split()]
            seviye.append(any(app["_kelime_eslesir"](k(q), w) for w in kel))
        assert seviye == sorted(seviye, reverse=True), (q, "kelime başı eşleşmeler içinde geçenlerden önce gelmeli")
    for kalip, etiketler in app["TEST_ETIKET_KURALLARI"]:                        # etiket yalnız kuraldan
        assert etiketler and all(isinstance(e, str) and e for e in etiketler)
    assert app["test_etiketleri"]("Laktat Eşiği Testi") and not app["test_etiketleri"]("CAPL Motivasyon ve Güven Anketi")
    assert ara("Nordic") == [_NHT_G]                                             # takma ad ayrıca çıkmaz


def test_34b_sira_uyarisi_bildirir_engellemez(app, tmp_path, monkeypatch):
    """
    Test sırası ExRx ilkesine göre denetlenir (antropometri → esneklik → sürat/çeviklik → güç → kuvvet → kas
    dayanıklılığı → kardiyo): bozuk sırada uyarı adlarıyla çıkar; doğru sırada çıkmaz; uyarı kaydı ENGELLEMEZ.
    """
    u = app["sira_uyarilari"]([_NHT_G, "10m Sprint"])
    assert len(u) == 1 and _NHT_G in u[0] and "10m Sprint" in u[0] and "yorgunluk" in u[0]
    dogru = ["Boy ve Vücut Ağırlığı (TSYT)", "Otur-Uzan (Sit and Reach) Testi", "10m Sprint", "Dikey Sıçrama (CMJ)",
             _NHT_G, "Push-Up Testi", "Yo-Yo IR1 (Genel)"]
    assert app["sira_uyarilari"](dogru) == []
    assert [app["test_bileseni"](t) for t in dogru] == list(app["TEST_BILESENLERI"])
    assert app["sira_uyarilari"](["Flamingo Denge Testi", "10m Sprint"]) == []      # belirsiz bileşen denetlenmez
    assert app["sira_uyarilari"](["Yo-Yo IR1 (Genel)", "10m Sprint", _NHT_G])
    monkeypatch.chdir(tmp_path)
    assert app["calisma_kaydet"]({"ad": "Ters", "testler": [_NHT_G, "10m Sprint"], "zamanlar": ["Ön test"]}) == []
    assert app["calismalar_oku"]()["Ters"]["testler"] == [_NHT_G, "10m Sprint"]


def test_34c_calisma_ayarlarda_saklanir(app, tmp_path, monkeypatch):
    """
    Çalışma ayarlar.json'da ("calismalar"): ad, SIRALI testler (kategoriden bağımsız), gruplar, ölçüm zamanları,
    sporcu → grup ataması. Diğer tercihler korunur; sorunlu çalışma yazılmaz; ad değişince eskisi kalmaz.
    """
    import json
    monkeypatch.chdir(tmp_path)
    app["ayar_yaz"]("yonlendirme_gizle", True)
    c = {"ad": "NHE Tez Çalışması", "testler": ["T-Testi (Çeviklik)", "10m Sprint", "Nordic Hamstring Kuvvet Testi (NHT)"],
         "gruplar": ["Kontrol", "Deney"], "zamanlar": ["Ön test", "Ara test", "Son test"],
         "atamalar": {"Ali A": "Deney", "Can B": "Kontrol"}}
    assert app["calisma_kaydet"](c) == []
    veri = json.loads((tmp_path / "ayarlar.json").read_text(encoding="utf-8"))
    assert veri["yonlendirme_gizle"] is True
    k = app["calismalar_oku"]()["NHE Tez Çalışması"]
    assert k["testler"] == ["T-Testi (Çeviklik)", "10m Sprint", _NHT_G]           # sıra korunur, takma ad çözülür
    assert k["gruplar"] == ["Kontrol", "Deney"] and k["zamanlar"] == ["Ön test", "Ara test", "Son test"]
    assert app["calisma_sporculari"](k, ["Deney"]) == ["Ali A"]
    assert app["calisma_oturum_adi"]("NHE Tez Çalışması", "Ön test") == "NHE Tez Çalışması · Ön test"
    from datetime import datetime
    an = datetime(2026, 10, 22, 10, 26, 5)
    assert app["oturum_kimligi"]("NHE Tez Çalışması", "Son test", an) == "NHE Tez Çalışması · Son test"
    assert app["oturum_kimligi"](None, None, an) == "OT-20261022-102605"
    bozuk = dict(c, ad="Bozuk", zamanlar=[], atamalar={"Ali A": "Plasebo"}, testler=["Yok Böyle Test"])
    sorun = app["calisma_kaydet"](bozuk)
    assert len(sorun) >= 3 and "Bozuk" not in app["calismalar_oku"]()
    assert app["calisma_kaydet"](dict(c, ad="NHE"), eski_ad="NHE Tez Çalışması") == []
    assert list(app["calismalar_oku"]()) == ["NHE"]
    app["calisma_sil"]("NHE")
    assert app["calismalar_oku"]() == {} and json.loads((tmp_path / "ayarlar.json").read_text(encoding="utf-8"))["yonlendirme_gizle"]


def test_34d_kayit_yolu_ve_takma_ad(app):
    """
    Kategoriden bağımsız seçilen testler kendi katalog yoluyla kaydedilir (Kategori/Batarya/Branş); NHT'nin Futbol
    kaydı Genel'e takma addır: yeni kayıt asıl adla yazılır, eski kayıtlar okunurken asıl ada çevrilir (veri bölünmez).
    """
    import pandas as _pd
    from datetime import date
    tablo = _pd.DataFrame({"Sporcu": ["Ali A"], "10m Sprint › Deneme 1 (sn)": [1.9],
                           f"{_NHT_G} › Sağ Bacak Pik Kuvveti (N)": [350.0]})
    testler = {"10m Sprint": ["Deneme 1 (sn)"], _NHT_G: ["Sağ Bacak Pik Kuvveti (N)"]}
    yollar = {t: app["test_yolu"](t) for t in testler}
    kay, _ = app["oturum_kayitlari"](tablo, {"Ali A": {"Cinsiyet": "Erkek", "Yaş": 22}}, testler, "-", "-", None,
                                     date(2026, 10, 22), {"kimlik": "NHE · Ön test", "yer": "", "uygulayici": ""}, yollar=yollar)
    yol = {k["Test"]: (k["Kategori"], k["Batarya"], k["Branş"]) for k in kay}
    assert yol["10m Sprint"] == ("Branşa Özgü Testler", "Bireysel Sporlar", "Atletizm")
    assert yol[_NHT_G] == ("Laboratuvar ve Fizyolojik Testler", "Anaerobik, Güç ve Nöromüsküler", "-")
    assert all(k["Oturum"] == "NHE · Ön test" for k in kay)
    a, g = "Nordic Hamstring Kuvvet Testi (NHT)", _NHT_G
    assert app["TEST_TAKMA_AD"][a] == g
    assert app["test_bilgisi"](a)["degiskenler"] == app["test_bilgisi"](g)["degiskenler"]
    eski = _pd.DataFrame({"Sporcu": ["Ali A", "Ali A"], "Test": [a, g]})
    assert set(app["test_tablosu_duzelt"](eski)["Test"]) == {g}
    k = app["test_kaydi_olustur"]("Ali A", {}, "Branşa Özgü Testler", "Takım Sporları", "Futbol", a,
                                  date(2026, 10, 22), {}, {})
    assert k["Test"] == g
    assert a in {t["ad"] for t in app["katalog_testleri"]()}                      # takma ad katalogdan silinmedi


def test_34e_test_oturumu_calisma_akisi(tmp_path, monkeypatch, app):
    """
    Test Oturumu: (1) serbest seçimde aramadan eklenen test sıralı listeye girer, ↓ ile sıra değişir; (2) Çalışma
    seçilince ölçüm zamanı ve gruba atanmış sporcular gelir, testler kayıtlı sırayla, Oturum alanına
    "çalışma · zaman" yazılacağı görünür, bozuk sırada uyarı çıkar; (3) çalışma düzenleyiciden kaydedilir.
    """
    import json
    import pandas as _pd

    def app_ara(q):
        return [t for t in app["test_ara"](q) if t["ad"] not in app["TOPLU_GIRIS_DISI"]
                and (app["test_bilgisi"](t["ad"]) or {}).get("degiskenler")]

    def veri(d):
        _pd.DataFrame({"Ad": ["Ali", "Can", "Ece"], "Soyad": ["A", "B", "C"], "Yaş": [20, 21, 22],
                       "Cinsiyet": ["Erkek", "Erkek", "Kadın"], "Spor Dalı": ["Güreş"] * 3}).to_excel(d / "sporcular.xlsx", index=False)
        (d / "ayarlar.json").write_text(json.dumps({"calismalar": {"NHE": {
            "testler": [_NHT_G, "10m Sprint"], "gruplar": ["Kontrol", "Deney"], "zamanlar": ["Ön test", "Son test"],
            "atamalar": {"Ali A": "Deney", "Can B": "Kontrol"}}}}, ensure_ascii=False), encoding="utf-8")
    at = _apptest(tmp_path, monkeypatch, veri)
    at.session_state["sayfa"] = "Test Oturumu"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    at.text_input(key="ot_ara").input("sürat").run()
    assert not list(at.session_state["ot::sira"] if "ot::sira" in at.session_state else [])   # gezinmek eklemez
    sonuc = [t["ad"] for t in app_ara("sürat")]
    agac_once = {k: list(at.session_state[k]) for k in _durum_anahtarlari(at) if str(k).startswith("ot_testler_")}
    for ad in ("20m Sprint", "10m Sprint"):                         # arama panelindeki "Ekle" düğmeleri
        at.button(key=f"ot::ara::ekle::{sonuc.index(ad)}").click().run()
    assert list(at.session_state["ot::sira"]) == ["20m Sprint", "10m Sprint"]
    assert at.button(key=f"ot::ara::ekle::{sonuc.index('10m Sprint')}").disabled                # eklendi
    assert {k: list(at.session_state[k]) for k in _durum_anahtarlari(at) if str(k).startswith("ot_testler_")} == agac_once
    assert not [m for m in at.multiselect if m.label == "Aramadan ekle"]       # ayrı çoklu seçim kutusu yok
    at.button(key="ot::sira::asagi::0").click().run()
    assert list(at.session_state["ot::sira"]) == ["10m Sprint", "20m Sprint"]
    at.radio(key="ot_kaynak").set_value("Çalışma").run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.selectbox(key="ot_zaman::NHE").value == "Ön test"
    assert any("NHE · Ön test" in c.value for c in at.caption)
    assert any("Sıra uyarısı" in w.value and "10m Sprint" in w.value for w in at.warning)
    at.button(key="ot_ana").click().run()                       # Paket 38b: sporcular Adım 2'de
    sec = [m for m in at.multiselect if m.label.startswith("Sporcular")][0]
    assert sec.value == ["Ali A", "Can B"]
    at.button(key="ot_geri").click().run()                      # çalışma düzenleyicisi Adım 1'de
    at.text_input(key="cl::➕ Yeni çalışma::ad").input("Tez").run()
    at.text_input(key="cl::➕ Yeni çalışma::ara").input("çeviklik").run()
    at.multiselect(key="cl::➕ Yeni çalışma::testler").select("T-Testi (Çeviklik)").run()
    at.text_input(key="cl::➕ Yeni çalışma::zamanlar").input("Ön test, Son test").run()
    at.button(key="cl::➕ Yeni çalışma::kaydet").click().run()
    assert not at.exception, [e.value for e in at.exception]
    kayit = json.loads((tmp_path / "ayarlar.json").read_text(encoding="utf-8"))["calismalar"]
    assert kayit["Tez"]["testler"] == ["T-Testi (Çeviklik)"] and kayit["Tez"]["zamanlar"] == ["Ön test", "Son test"]
    assert "NHE" in kayit


def test_34f_pedal_ileri_doner(app):
    """Wingate: sürücü sağa bakar (gidon kalçanın önünde); krank merkezinin üstündeyken pedal +x yönünde ilerler."""
    E = app["tg_eklemler"]
    h = app["hk_pedal"](110, s=0.85, tur=6)
    cx, cy = h.olay["krank"]
    assert h.olay["gidon"][0] > h.anahtarlar[0][1]["hx"]
    for ayak in ("ayak1", "ayak2"):
        k = [E(p)[ayak] for _, p in h.anahtarlar]
        tepe = [b[0] - a[0] for a, b in zip(k, k[1:]) if min(a[1], b[1]) < cy - 0.6 * h.olay["r"]]
        assert tepe and all(d > 0 for d in tepe), (ayak, tepe)


def test_34g_kayak_govde_calisir(app):
    """
    Kano/kayak ergometresi: gövde eğimi yakalamada öne kapanır, çekişte açılır (en az 25° aralık); omuz alçalıp
    yükselir, kalça koltukta kalır (oturuşta kalça yüksekliği koltuğa bağlı).
    """
    h = app["hk_kayak_ergometre"](96, s=0.9)
    gs = [p["g"] for _, p in h.anahtarlar]
    assert max(gs) - min(gs) >= 25
    assert len({round(p["hy"], 3) for _, p in h.anahtarlar}) == 1
    omuz = [app["tg_eklemler"](p)["boyun"][1] for _, p in h.anahtarlar]
    assert max(omuz) - min(omuz) > 3
    assert h.anahtarlar[-1][1]["g"] == max(gs), "son kare yakalama: gövde önde"


def test_34h_gorselsiz_neden_yazilir(app, tmp_path, monkeypatch):
    """Görseli bilerek olmayan testte görselin yerinde neden yazılır ('Bu test için görsel yok — …'); boş kalmaz."""
    for ad, neden in app["TEST_GORSELSIZ"].items():
        assert app["gorselsiz_metni"](ad) == f"Bu test için görsel yok — {neden}"
    assert app["gorselsiz_metni"]("10m Sprint") is None
    import pandas as _pd

    def veri(d):
        _pd.DataFrame({"Ad": ["Ali"], "Soyad": ["A"], "Yaş": [20], "Cinsiyet": ["Erkek"]}).to_excel(d / "sporcular.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    kat, alt = "Laboratuvar ve Fizyolojik Testler", "Antropometri ve Vücut Kompozisyonu"
    for k, v in (("sayfa", "Test Uygula"), ("tu_mod", "📂 Kategoriye Göre"), ("tu_kategori", kat),
                 (f"tu_alt::{kat}", alt), (f"tu_test::{kat}::{alt}::None", "DEXA (Dual-Energy X-ray Absorptiometry)")):
        at.session_state[k] = v
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("Bu test için görsel yok — laboratuvar ölçümü" in i.value or "Bu test için görsel yok" in i.value
               for i in at.info)


def test_34i_laboratuvar_uc_alt_baslik(app):
    """
    Laboratuvar ve Fizyolojik Testler: Paket 34'teki 3 alt başlık ve 20 test duruyor; Paket 35 dördüncü alt başlığı
    (Maksimal Kuvvet ve Kas Dayanıklılığı, 6 test) ekledi. Katalog 189 → 195; Paket 35c Sargent'i
    (Anaerobik, Güç ve Nöromüsküler) ekledi: 196.
    """
    L = app["TEST_KATALOGU"]["Laboratuvar ve Fizyolojik Testler"]
    assert list(L) == ["Aerobik (Saha ve Laboratuvar)", "Anaerobik, Güç ve Nöromüsküler", "Antropometri ve Vücut Kompozisyonu",
                       "Maksimal Kuvvet ve Kas Dayanıklılığı"]
    assert [len([t for t in v if not t.startswith("_")]) for v in L.values()] == [8, 10, 3, 6]   # _kunye test değil
    assert len(app["katalog_testleri"]()) == 196


def _test_oturumu_kaynagi(kaynak):
    """
    Test Oturumu sayfasının kaynağı. Paket 38b gövdeyi 'elif sayfa == "Test Oturumu":' bloğundan
    test_oturumu_sayfasi() ve _ot_* adım fonksiyonlarına taşıdı; bunlar dosyadaki sırayla birleştirilir.
    """
    return "\n".join(ast.get_source_segment(kaynak, d) for d in ast.parse(kaynak).body
                     if isinstance(d, ast.FunctionDef) and (d.name == "test_oturumu_sayfasi" or d.name.startswith("_ot_")))


def test_34j_oturum_kaydi_kimlik_fonksiyonundan(kaynak):
    """Test Oturumu kaydı "Oturum" alanını oturum_kimligi ile yazar (çalışmayla: "çalışma · ölçüm zamanı")."""
    sayfa = _test_oturumu_kaynagi(kaynak)
    assert re.search(r"kimlik = oturum_kimligi\(ot_calisma_ad if ot_calisma is not None else None, ot_zaman,", sayfa)
    assert 'k["Oturum"] = kimlik' in sayfa



# ── Paket 38s: kayıtlı oturumu düzeltme, taşıma, silme ──
def _p38s_veri(d):
    """İki sporcu (doğum tarihli 10 ve 12 yaş), bir çalışmalı oturum: uzun atlama (en iyi türetilir) ve NHT."""
    import pandas as _pd
    _pd.DataFrame({"Ad": ["Elif", "Kaan"], "Soyad": ["Demo"] * 2, "Yaş": [10, 12], "Cinsiyet": ["Kadın", "Erkek"],
                   "Kilo (kg)": [33, 40], "Doğum Tarihi": ["01.01.2016", "01.01.2014"]}).to_excel(
        d / "sporcular.xlsx", index=False)
    b = {"Sporcu": "Elif Demo", "Tarih": "15.09.2026", "Oturum": "Tez · Ön test", "Test Yaşı": 10}
    _pd.DataFrame([
        dict(b, Test="Durarak Uzun Atlama", **{"Deneme 1 (cm)": 128, "Deneme 2 (cm)": 131, "En İyi Değer (cm)": 131}),
        dict(b, Test="Nordic Hamstring Kuvvet Testi — Genel (NHT)",
             **{"Sağ Bacak Pik Kuvveti (N)": 300, "Sol Bacak Pik Kuvveti (N)": 270, "Asimetri İndeksi (%)": 10.0}),
        dict(b, Sporcu="Kaan Demo", Test="Durarak Uzun Atlama", **{"Deneme 1 (cm)": 150, "En İyi Değer (cm)": 150,
                                                                    "Test Yaşı": 12}),
    ]).to_excel(d / "test_sonuclari.xlsx", index=False)


def test_55a_duzeltme_turetilenleri_yeniden_hesaplar_kayit_ve_yedek(tmp_path, monkeypatch):
    """Tek değer düzeltmesi: en iyi deneme ve asimetri yeniden hesaplanır, aykırı değer uyarısı çıkar (engel değil),
    yazmadan önce yedek alınır, değişiklik kaydına satır (Excel satırı), alan, eski ve yeni değer yazılır."""
    import os as _os
    D = _modul("olcut.duzeltme")
    monkeypatch.chdir(tmp_path)
    _p38s_veri(tmp_path)
    o = D.duzeltme_onizleme(0, "Deneme 1 (cm)", "135,5")
    assert o["degisiklikler"] == [("Deneme 1 (cm)", 128, 135.5), ("En İyi Değer (cm)", 131, 135.5)]
    assert not o["uyarilar"]
    assert D.duzeltme_onizleme(0, "Deneme 1 (cm)", "900")["uyarilar"]                 # ≈P1–P99 dışı
    with pytest.raises(D.DuzeltmeHatasi):
        D.duzeltme_onizleme(0, "En İyi Değer (cm)", "140")                              # hesaplanan değer düzeltilmez
    assert D.kayit_duzelt(0, "Deneme 1 (cm)", "135,5", "kâğıttan yanlış") == 2
    df = D.ham_tablo()
    assert df.at[0, "Deneme 1 (cm)"] == 135.5 and df.at[0, "En İyi Değer (cm)"] == 135.5
    assert D.kayit_duzelt(1, "Sol Bacak Pik Kuvveti (N)", "240") == 2
    assert D.ham_tablo().at[1, "Asimetri İndeksi (%)"] == 20.0                     # (300 − 240) / 300 × 100
    log = D.degisiklik_kaydi_oku()
    assert list(log.columns) == D.DEGISIKLIK_KOLONLARI and len(log) == 4
    assert list(log.iloc[0][["İşlem", "Satır", "Sporcu", "Alan", "Eski değer", "Yeni değer", "Açıklama"]]) == [
        "Düzeltme", 2, "Elif Demo", "Deneme 1 (cm)", "128", "135.5", "kâğıttan yanlış"]
    assert len(_os.listdir(tmp_path / "yedekler")) == 2
    # SWFT: Test Uygula ile düzeltme aynı formül
    from olcut.norm import swft_turetilmis
    assert swft_turetilmis({"Periyot 1 Atış Sayısı": 5, "Periyot 2 Atış Sayısı": 10, "Periyot 3 Atış Sayısı": 9,
                            "HR0 (bpm)": 180, "HR1-dk (bpm)": 150}, 80) == {
        "Toplam Atış (TnThrows)": 24, "TnThrows/BM": 0.3, "SWFT Index": 1375.0}


def test_55b_tasima_test_yasini_yeni_sporcuya_gore_hesaplar(tmp_path, monkeypatch):
    D = _modul("olcut.duzeltme")
    monkeypatch.chdir(tmp_path)
    _p38s_veri(tmp_path)
    o = D.tasima_onizleme([0], "Kaan Demo")
    assert ("Sporcu", "Elif Demo", "Kaan Demo") in o[0]["degisiklikler"]
    assert ("Test Yaşı", 10, 12) in o[0]["degisiklikler"]                           # 01.01.2014 → 15.09.2026: 12
    with pytest.raises(D.DuzeltmeHatasi):
        D.tasima_onizleme([0], "Yok Demo")
    D.kayit_tasi([0], "Kaan Demo")
    df = D.ham_tablo()
    assert df.at[0, "Sporcu"] == "Kaan Demo" and df.at[0, "Test Yaşı"] == 12
    assert set(D.degisiklik_kaydi_oku()["İşlem"]) == {"Taşıma"}


def test_55c_silme_isaretler_hesaplara_girmez_geri_alinir(tmp_path, monkeypatch):
    """Silme kalıcı değil: satır dosyada kalır, test_tablosu_duzelt (bütün okumalar) ve önceki ölçüm çıkarır;
    Geri al ile döner. Satır numaraları değişmez."""
    D = _modul("olcut.duzeltme")
    from olcut.katalog_islemleri import test_tablosu_duzelt, SILINDI_KOLON
    from olcut.kayit import onceki_olcumler
    monkeypatch.chdir(tmp_path)
    _p38s_veri(tmp_path)
    satirlar = D.oturum_satirlari(D.ham_tablo(), "Tez · Ön test", "Elif Demo")
    assert satirlar == [0, 1]
    assert D.kayit_sil(satirlar, "protokol dışı") == 2
    ham = D.ham_tablo()
    assert len(ham) == 3 and ham[SILINDI_KOLON].notna().sum() == 2
    gor = test_tablosu_duzelt(ham)
    assert list(gor.index) == [2] and SILINDI_KOLON not in gor.columns
    assert onceki_olcumler("Elif Demo", "Durarak Uzun Atlama") == {}
    with pytest.raises(D.DuzeltmeHatasi):
        D.kayit_duzelt(0, "Deneme 1 (cm)", "130")                                     # silinmiş kayıt düzeltilmez
    assert D.oturum_satirlari(ham, "Tez · Ön test", silinmis=True) == [0, 1]
    assert D.kayit_geri_al([0, 1]) == 2
    assert len(test_tablosu_duzelt(D.ham_tablo())) == 3
    assert list(D.degisiklik_kaydi_oku()["İşlem"]) == ["Silme"] * 2 + ["Geri alma"] * 2


def test_55d_taslagi_acik_oturum_duzenlenemez(tmp_path, monkeypatch):
    import json as _json
    D = _modul("olcut.duzeltme")
    monkeypatch.chdir(tmp_path)
    _p38s_veri(tmp_path)
    (tmp_path / "oturum_taslagi.json").write_text(_json.dumps(
        {"testler": ["Durarak Uzun Atlama"], "sporcular": ["Elif Demo"], "bilgi": {"calisma": "Tez", "zaman": "Ön test"},
         "degerler": {}}), encoding="utf-8")
    assert D.kilitli_oturum() == "Tez · Ön test"
    for islem in (lambda: D.kayit_duzelt(0, "Deneme 1 (cm)", "130"), lambda: D.kayit_sil([2]),
                  lambda: D.kayit_tasi([0], "Kaan Demo")):
        with pytest.raises(D.DuzeltmeHatasi, match="taslağı"):
            islem()
    assert not (tmp_path / "degisiklik_kaydi.xlsx").exists() and not (tmp_path / "yedekler").exists()
    (tmp_path / "oturum_taslagi.json").write_text(_json.dumps(
        {"testler": ["Durarak Uzun Atlama"], "sporcular": ["Elif Demo"], "bilgi": {}}), encoding="utf-8")
    assert D.kilitli_oturum() is None                                                 # serbest seçim taslağı
    assert D.kayit_duzelt(0, "Deneme 1 (cm)", "130") == 1


def test_55e_kulupte_yedek_ve_kayit_kulup_klasorunde(tmp_path, monkeypatch):
    """Çalışma alanı yalıtımı: kulüp seçiliyken test dosyası, yedek ve değişiklik kaydı kulübün klasöründe."""
    import olcut.ortak as O
    D = _modul("olcut.duzeltme")
    monkeypatch.chdir(tmp_path)
    k = tmp_path / "kulupler" / "a-sk"
    k.mkdir(parents=True)
    _p38s_veri(k)
    monkeypatch.setattr(O, "aktif_kulup", lambda: "a-sk")
    D.kayit_sil([2])
    assert (k / "degisiklik_kaydi.xlsx").exists() and len(list((k / "yedekler").iterdir())) == 1
    assert not (tmp_path / "degisiklik_kaydi.xlsx").exists() and not (tmp_path / "yedekler").exists()


def test_55f_kayit_duzelt_ekrani_onay_penceresiyle_yazar(tmp_path, monkeypatch):
    """Sonuçlar → Kayıt düzelt: Önizle ve onayla → pencere (uyarı engel değil) → Onayla → dosya; Vazgeç yazmaz.
    Veli raporundaki yüzme örneği 'yüzme, su topu'."""
    from olcut.analiz import _brans_ornekleri
    at = _apptest(tmp_path, monkeypatch, _p38s_veri)
    at.session_state["sayfa"] = "Sonuçları Görüntüle"
    at.session_state["sonuc_bolum"] = "Kayıt düzelt"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    yeni = next(t for t in at.text_input if str(t.key).startswith("kd_yeni"))
    yeni.set_value("900").run()
    at.button(key="kd_duzelt").click().run()
    assert any("olağandışı" in w.value for w in at.warning)
    at.button(key="kd_vazgec").click().run()
    assert not (tmp_path / "degisiklik_kaydi.xlsx").exists()
    at.button(key="kd_duzelt").click().run()
    at.button(key="kd_onayla").click().run()
    assert not at.exception and any("İşlem kaydedildi" in s.value for s in at.success)
    assert (tmp_path / "degisiklik_kaydi.xlsx").exists()
    assert _brans_ornekleri("Yüzme") == "yüzme, su topu"


# ── Paket 38t: tek tıkla tam yedek ──
def test_56a_tam_yedek_yalniz_secili_calisma_alani(tmp_path, monkeypatch):
    """Zip: çalışma alanının veri dosyaları + yedek_bilgisi.txt; yedekler/ ve başka kulübün dosyası girmez.
    Kulüpte kulup.json da girer; dosya adı Olcut_yedek_<ad>_<GGAAYYYY>.zip."""
    import datetime as _dt
    import io as _io
    import json as _json
    import zipfile as _zip
    import olcut.ortak as O
    K = _modul("olcut.kulup")
    monkeypatch.chdir(tmp_path)
    _p38s_veri(tmp_path)
    (tmp_path / "yedekler").mkdir()
    (tmp_path / "yedekler" / "eski.xlsx").write_bytes(b"x")
    a = tmp_path / "kulupler" / "a-sk"
    a.mkdir(parents=True)
    (a / "kulup.json").write_text(_json.dumps({"ad": "Arslan SK"}), encoding="utf-8")
    (a / "sporcular.xlsx").write_bytes(b"a")
    gun = _dt.datetime(2026, 11, 3, 10, 0)
    veri, ad, dosyalar = K.calisma_alani_yedegi("", gun)
    z = _zip.ZipFile(_io.BytesIO(veri))
    assert ad == "Olcut_yedek_Genel_03112026.zip"
    assert sorted(z.namelist()) == sorted(["sporcular.xlsx", "test_sonuclari.xlsx", "yedek_bilgisi.txt"])
    assert z.read("sporcular.xlsx") == (tmp_path / "sporcular.xlsx").read_bytes()
    assert "Çalışma alanı: Genel" in z.read("yedek_bilgisi.txt").decode("utf-8")
    monkeypatch.setattr(O, "aktif_kulup", lambda: "a-sk")
    veri, ad, dosyalar = K.calisma_alani_yedegi("a-sk", gun)
    z = _zip.ZipFile(_io.BytesIO(veri))
    assert ad == "Olcut_yedek_Arslan_SK_03112026.zip" and dosyalar == ["sporcular.xlsx", "kulup.json"]
    assert z.read("sporcular.xlsx") == b"a"
    monkeypatch.setattr(O, "aktif_kulup", lambda: "")
    (tmp_path / "sporcular.xlsx").unlink()
    (tmp_path / "test_sonuclari.xlsx").unlink()
    assert K.calisma_alani_yedegi("", gun) == (None, None, [])


def test_56b_kulupler_sayfasinda_yedek_dugmesi(tmp_path, monkeypatch):
    at = _apptest(tmp_path, monkeypatch, _p38s_veri)
    at.session_state["sayfa"] = "Kulüpler"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert "Veri yedeği · Genel" in _agac_metni(at)
    assert "Tüm veriyi yedekle (.zip)" in _agac_metni(at)
