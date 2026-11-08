"""
Opstoel branş grubu eşleştirmesi, 0,10 yayılım eşiği simülasyonu, kaynakça, yönlendirme ve öneri motoru.
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
# 11. Branş grubu eşleştirmesi
# ════════════════════════════════════════════════════════════
def test_11_eslestirme_kendi_grubu_birinci(app):
    """Bir gruba kendi ortalama profili verilince o grup birinci ve uzaklık 0,00 çıkmalı."""
    profiller = app["BRANS_GRUBU_PROFILLERI"]
    eslestir = app["brans_grubu_eslestir"]
    sorunlar = []
    for grup, tablo in profiller["degerler"].items():
        fsc = {"degerler": {kod: {"deger": tablo[kod][0], "test_yasi": 10}
                            for kod in app["ESLESTIRME_DEGISKENLERI"]},
               "eksik": [], "eslesmeyen": []}
        sonuc = eslestir(fsc, 10)
        if not sonuc["uygun"]:
            sorunlar.append(f"{grup}: eşleştirme yapılmadı ({sonuc['neden']})")
            continue
        ilk_grup, ilk_uzaklik = sonuc["siralama"][0]
        if ilk_grup != grup or ilk_uzaklik != 0.0:
            sorunlar.append(f"{grup}: birinci {ilk_grup} ({ilk_uzaklik}); beklenen {grup} (0.00)")
    assert not sorunlar, "Eşleştirme kendi grubunu bulamıyor:" + _ozet(sorunlar)


# ════════════════════════════════════════════════════════════
# 12. Kaynakça sayıları
# ════════════════════════════════════════════════════════════
def test_12_kaynakca_sayilari_tutarli(app):
    kayitlar = app["KAYNAKCA"]
    siniflar = app["KAYNAKCA_SINIFLAR"]
    tanimsiz = [f"{x['k'][:60]} → {x['s']!r}" for x in kayitlar if x["s"] not in siniflar]
    assert not tanimsiz, "KAYNAKCA_SINIFLAR'da olmayan sınıf:" + _ozet(tanimsiz)
    sayim = {s: sum(1 for x in kayitlar if x["s"] == s) for s in siniflar}
    assert sum(sayim.values()) == len(kayitlar), (
        f"Sınıf sayılarının toplamı {sum(sayim.values())}, kayıt sayısı {len(kayitlar)}: {sayim}")
    tekrar = [k for k, c in collections.Counter(x["k"] for x in kayitlar).items() if c > 1]
    assert not tekrar, "Kaynakçada aynı künye birden fazla kez:" + _ozet(tekrar)



# ════════════════════════════════════════════════════════════
# 23. Yönlendirme ekranı (Paket 16): kural tabanlı, internetsiz, veride ne varsa onu söyler
# ════════════════════════════════════════════════════════════
def _tsyt_testleri(app):
    return app["katalog_bataryalari"]()[app["YON_TSYT"]]


def test_23a_yonlendirme_durumu_bos_ve_eksik_dosya(app):
    """Dosya yok (None), boş tablo, sütunsuz tablo: hata yok, durum 'sporcu_yok'."""
    import pandas as _pd
    f = app["yonlendirme_durumu"]
    for sp, ts in [(None, None), (_pd.DataFrame(), _pd.DataFrame()), (_pd.DataFrame({"x": []}), None),
                   (_pd.DataFrame({"Ad": [], "Soyad": []}), _pd.DataFrame({"Sporcu": [], "Test": []}))]:
        d = f(sp, ts)
        assert d["durum"] == "sporcu_yok" and not d["yarim"] and not d["tamam"], d
    sp = _pd.DataFrame({"Ad": ["Ece"], "Soyad": ["Su"], "Yaş": [9]})
    assert f(sp, None)["durum"] == "sonuc_yok"
    assert f(sp, _pd.DataFrame())["durum"] == "sonuc_yok"
    # kayıtlı olmayan sporcunun sonucu sayılmaz (yalnız veride eşleşen)
    assert f(sp, _pd.DataFrame({"Sporcu": ["Başka Biri"], "Test": ["20m Sürat (TSYT)"]}))["durum"] == "sonuc_yok"


def test_23b_yarim_ve_tamam_batarya_cumlesi(app):
    """Yarım batarya adıyla ve eksik testlerle söylenir; tamamlanan ayrı listelenir. Türkçe ilgi eki doğru."""
    import pandas as _pd
    tsyt = _tsyt_testleri(app)
    eksik = ["20m Sürat (TSYT)", "Mekik Koşusu (TSYT)"]
    sp = _pd.DataFrame({"Ad": ["Deniz", "Ece"], "Soyad": ["Aydın", "Su"], "Yaş": [9, 10]})
    ts = _pd.DataFrame({"Sporcu": ["Deniz Aydın"] * (len(tsyt) - 2) + ["Ece Su"] * len(tsyt),
                        "Test": [t for t in tsyt if t not in eksik] + tsyt,
                        "Tarih": ["10.10.2026"] * (2 * len(tsyt) - 2)})
    d = app["yonlendirme_durumu"](sp, ts, bugun="24.10.2026")      # Paket 32: yarım için son ölçüm ≤ 6 hafta
    assert d["durum"] == "sonuc_var"
    assert [k["sporcu"] for k in d["yarim"]] == ["Deniz Aydın"] and d["yarim"][0]["eksik"] == eksik
    assert app["yarim_cumlesi"](d["yarim"][0]) == "Deniz Aydın’ın TSYT bataryasında 2 test eksik: 20m Sürat, Mekik Koşusu"
    assert [k["sporcu"] for k in d["tamam"]] == ["Ece Su"]
    e = app["ilgi_eki"]
    assert [e("Ali Bir"), e("Ece"), e("Ayşe Kurt"), e("Gül Öztürk"), e("Oya")] == \
        ["Ali Bir’in", "Ece’nin", "Ayşe Kurt’un", "Gül Öztürk’ün", "Oya’nın"]
    assert set(app["katalog_bataryalari"]()) and all(b in app["YON_BATARYA_KISA"] for _, b in app["katalog_bataryalari"]())


def test_23c_test_ara_ad_ve_kategori(app):
    """Test ara: katalogdaki bütün testler; ada (Türkçe büyük/küçük harf duyarsız) ve kategoriye göre süzer."""
    tum = app["katalog_testleri"]()
    assert len(tum) == len({(t["yol"], t["ad"]) for t in tum}) and len(tum) > 150
    ara = app["test_ara"]
    assert any(t["ad"] == "20m Sürat (TSYT)" for t in ara("SÜRAT"))
    assert ara("i") == []        # Paket 28: 1-2 harflik sözcük tek başına içinde-eşleşme saymaz (bütün sözcük "i" yok)
    assert any(t["ad"].startswith("İ") for t in ara("izo"))
    yy = ara("yo-yo", "Branşa Özgü Testler")
    assert yy and all(t["kategori"] == "Branşa Özgü Testler" for t in yy)
    assert len(ara("", "Türkiye Sportif Yetenek Modeli (TSYT)")) == len(_tsyt_testleri(app))


def test_23d_kural_tabanli_internetsiz(agac):
    """Yönlendirme kodu dış servise bağlanmaz: uygulamada ağ kütüphanesi içe aktarılmaz."""
    ag = {"requests", "urllib", "http", "socket", "httpx", "aiohttp"}
    bulunan = []
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            bulunan += [a.name for a in d.names if a.name.split(".")[0] in ag]
        elif isinstance(d, ast.ImportFrom) and (d.module or "").split(".")[0] in ag:
            bulunan.append(d.module)
    assert not bulunan, bulunan


def test_23e_bir_daha_gosterme_hatirlanir(app, tmp_path, monkeypatch):
    """Tercih yerel ayar dosyasında kalır; dosya yok/bozuk ise boş sözlük (ekran açılır)."""
    monkeypatch.chdir(tmp_path)
    assert app["ayar_oku"]() == {}
    app["ayar_yaz"]("yonlendirme_gizle", True)
    assert app["ayar_oku"]() == {"yonlendirme_gizle": True}
    (tmp_path / app["AYAR_DOSYA"]).write_text("{bozuk", encoding="utf-8")
    assert app["ayar_oku"]() == {}


def _apptest(tmp_path, monkeypatch, hazirla):
    st_test = pytest.importorskip("streamlit.testing.v1")
    monkeypatch.chdir(tmp_path)
    hazirla(tmp_path)
    at = st_test.AppTest.from_file(DOSYA, default_timeout=120)
    at.run()
    return at


def _acilirlar(at):
    """
    Sayfadaki açılır paneller, belge sırasıyla. Streamlit 1.58 AppTest'i icon= verilmiş st.expander'ı
    'Status' olarak sınıflar (at.expander'da görünmez); ikisi birlikte toplanır.
    """
    bulunan = []

    def yuru(d):
        for c in (d.children.values() if isinstance(getattr(d, "children", None), dict) else ()):
            if type(c).__name__ in ("Expander", "Status"):
                bulunan.append(c)
            yuru(c)
    yuru(getattr(at, "_tree", None) or at.main)               # Paket 38g: iç ağaç yoksa ana gövde
    return bulunan


def _durum_anahtarlari(at):
    """
    Oturum durumu anahtarları — Streamlit sürümünden bağımsız (Paket 38g). 1.58'de SafeSessionState'te __iter__ yok
    (doğrudan döngü KeyError verir), filtered_state özellik; başka sürümlerde yöntem ya da iç nesnede olabilir.
    Sırayla denenir; hiçbiri yoksa doğrudan döngü.
    """
    ss = at.session_state
    for nesne in (ss, getattr(ss, "_state", None), getattr(getattr(ss, "_state", None), "_state", None)):
        fs = getattr(nesne, "filtered_state", None) if nesne is not None else None
        if fs is None:
            continue
        try:
            return list(fs() if callable(fs) else fs)
        except Exception:
            continue
    for ad in ("keys", "_keys"):
        f = getattr(ss, ad, None)
        if callable(f):
            try:
                return list(f())
            except Exception:
                pass
    return [k for k in ss]


def test_23f_yonlendirme_ekrani_bos_dosyayla_acilir(tmp_path, monkeypatch):
    """Sporcu/sonuç dosyası yok ya da boş: ekran hata vermeden açılır, tek büyük eylem 'İlk sporcuyu ekle'."""
    import pandas as _pd

    def bos(d):
        _pd.DataFrame().to_excel(d / "sporcular.xlsx", index=False)
        _pd.DataFrame().to_excel(d / "test_sonuclari.xlsx", index=False)
    for hazirla in (lambda d: None, bos):
        at = _apptest(tmp_path, monkeypatch, hazirla)
        assert not at.exception, [e.value for e in at.exception]
        # Paket 38k/38l: gezinme (üst menü, yan menü, alt bilgideki "Hakkında") eylem sayılmaz
        assert [b.label for b in at.main.button if b.key not in ("alt_hakkinda", "alt_kulupler", "ust-kulup-ekle")
                and not (b.key or "").startswith("ust-menu-")] == ["İlk sporcuyu ekle"]     # 38n: + Kulüp(ler)
        assert any("Ne yapmak istiyorsunuz?" in m.value for m in at.markdown)
        # Paket 33 B: düğmenin üstünde en fazla üç satır tanıtım (ne yapar + üç adım)
        tanitim = [m.value for m in at.markdown if "Sporcu ekle" in m.value and "Test uygula" in m.value]
        assert len(tanitim) == 1 and len(tanitim[0].split("\n")) <= 3 and "rapor" in tanitim[0]


def test_23g_yonlendirme_dugmeleri_secimi_doldurur(tmp_path, monkeypatch, app):
    """Paket 33: yarım batarya tek öneri olarak gelir; [Devam et] → eksik testler ve sporcu seçili Test Oturumu."""
    import pandas as _pd
    tsyt = _tsyt_testleri(app)

    from datetime import date as _date, timedelta as _td
    yakin = (_date.today() - _td(days=14)).strftime("%d.%m.%Y")      # Paket 32: yarım için son ölçüm ≤ 6 hafta

    def veri(d):
        _pd.DataFrame({"Ad": ["Deniz", "Ece"], "Soyad": ["Aydın", "Su"], "Yaş": [9, 10], "Cinsiyet": ["Erkek", "Kadın"],
                       "Grup/Sınıf": ["5-A", "5-A"]}).to_excel(d / "sporcular.xlsx", index=False)
        _pd.DataFrame({"Sporcu": ["Deniz Aydın"] * 9 + ["Ece Su"] * len(tsyt), "Test": tsyt[:9] + tsyt,
                       "Tarih": [yakin] * (9 + len(tsyt))}).to_excel(d / "test_sonuclari.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    assert not at.exception, [e.value for e in at.exception]
    assert at.selectbox(key="yon_secim").value == "sporcu::Deniz Aydın"          # en öncelikli öneri: yarım batarya
    assert any(m.value == "**Deniz Aydın · TSYT bataryasını tamamla (2 test)**" for m in at.markdown)
    assert any(c.value == "Neden: başlanmış batarya, 2 test kaldı" for c in at.caption)
    at.button(key="yon::devam").click().run()
    assert at.session_state["sayfa"] == "Test Oturumu"
    secili = {m.label: m.value for m in at.multiselect}
    assert secili["Bu oturumda uygulanan testler"] == tsyt[9:]
    at.button(key="ot_ana").click().run()                       # Paket 38b: sporcular Adım 2'de
    secili = {m.label: m.value for m in at.multiselect}
    assert secili["Grup / Sınıf"] == ["5-A"]
    assert secili["Sporcular (gruptakilerin tümü seçili gelir)"] == ["Deniz Aydın"]



# ════════════════════════════════════════════════════════════
# 39. Paket 32 — makine okunur yaş aralığı, yarım batarya eşiği, susturma
# ════════════════════════════════════════════════════════════
_P32_YAS = {                                  # hedef_yas metninden; metin yoksa None (uydurulmaz)
    "TSYT Bataryası — 7-11 Yaş (GSB)": (7, 11),
    "Eurofit Fiziksel Uygunluk Test Bataryası": (6, 18),
    "ALPHA Health-Related Fitness Test Battery": (6, 18),
    "KTK3+ Motor Koordinasyon Test Bataryası": (6, 19),
    "Flaman Spor Pusulası (FSC) — Ek Testler": (9, 11),
}


def _p32(app, kayitlar, yaslar, bugun="24.10.2026", **kw):
    """kayitlar: [(sporcu, test, tarih)]; yaslar: {sporcu: yaş}."""
    import pandas as _pd
    ad = list(yaslar)
    sp = _pd.DataFrame({"Ad": [a.split()[0] for a in ad], "Soyad": [a.split()[1] for a in ad],
                        "Yaş": [yaslar[a] for a in ad]})
    ts = _pd.DataFrame(kayitlar, columns=["Sporcu", "Test", "Tarih"])
    return app["yonlendirme_durumu"](sp, ts, bugun=bugun, **kw)


def test_39a_yas_araligi_hedef_yastan(app):
    """
    17 dalın (Paket 35: 18) hepsinde _kunye.yas_araligi var. Değer yalnız hedef_yas metninden: metinde "min-max yaş" olarak geçer;
    hedef_yas metni olmayan dalda None.
    """
    K = app["TEST_KATALOGU"]
    dallar = {a: v for k in K for a, v in K[k].items() if isinstance(v, dict)}
    assert len(dallar) == 18
    for a, v in dallar.items():
        ku = v.get("_kunye")
        assert isinstance(ku, dict) and "yas_araligi" in ku, a
        ya = ku["yas_araligi"]
        assert ya == _P32_YAS.get(a), (a, ya)
        if ya is None:
            assert "hedef_yas" not in ku, a
        else:
            assert ya[0] < ya[1] and f"{ya[0]}-{ya[1]} yaş" in ku["hedef_yas"], (a, ya)
    assert sum(v["_kunye"]["yas_araligi"] is not None for v in dallar.values()) == 5
    assert app["batarya_yas_araligi"](*app["YON_TSYT"]) == (7, 11)


def test_39b_yarim_batarya_uc_sart(app):
    """Yarım = en az yarısı yapılmış VE son ölçüm ≤ 6 hafta VE yaş aralıkta (aralık None ise aranmaz)."""
    tsyt = _tsyt_testleri(app)
    assert len(tsyt) == 11
    iki_hafta = "10.10.2026"
    yarim = lambda d: [(k["sporcu"], app["batarya_kisa"](k["batarya"]), len(k["eksik"])) for k in d["yarim"]]
    # yalnız "Boy ve Vücut Ağırlığı (TSYT)": hiçbir yarım uyarısı yok
    d = _p32(app, [("Ece Su", "Boy ve Vücut Ağırlığı (TSYT)", iki_hafta)], {"Ece Su": 9})
    assert d["yarim"] == [] and d["durum"] == "sonuc_var"
    # 11'in 6'sı, 2 hafta önce, yaş uygun → yarım
    d = _p32(app, [("Ece Su", t, iki_hafta) for t in tsyt[:6]], {"Ece Su": 9})
    assert yarim(d) == [("Ece Su", "TSYT", 5)]
    assert app["yarim_cumlesi"](d["yarim"][0]).startswith("Ece Su’nun TSYT bataryasında 5 test eksik")
    # 22 yaşında: TSYT (7-11) yarım sayılmaz
    assert _p32(app, [("Can Er", t, iki_hafta) for t in tsyt[:6]], {"Can Er": 22})["yarim"] == []
    # 5/11 yarıdan az
    assert _p32(app, [("Ece Su", t, iki_hafta) for t in tsyt[:5]], {"Ece Su": 9})["yarim"] == []
    # son ölçüm: 42 gün sınırda yarım, 43 gün değil; en yeni ölçüm sayılır; tarihsiz kayıt şartı sağlamaz
    s42, s43 = "12.09.2026", "11.09.2026"
    assert yarim(_p32(app, [("Ece Su", t, s42) for t in tsyt[:6]], {"Ece Su": 9})) == [("Ece Su", "TSYT", 5)]
    assert _p32(app, [("Ece Su", t, s43) for t in tsyt[:6]], {"Ece Su": 9})["yarim"] == []
    assert yarim(_p32(app, [("Ece Su", t, s43) for t in tsyt[:5]] + [("Ece Su", tsyt[5], iki_hafta)],
                      {"Ece Su": 9})) == [("Ece Su", "TSYT", 5)]
    assert _p32(app, [("Ece Su", t, "") for t in tsyt[:6]], {"Ece Su": 9})["yarim"] == []
    # yaş bilinmiyor ama aralık var: şart sağlanmaz
    assert _p32(app, [("Ece Su", t, iki_hafta) for t in tsyt[:6]], {"Ece Su": None})["yarim"] == []
    # yas_araligi None (FitnessGram): yaş şartı aranmaz
    fg = app["katalog_bataryalari"]()[("Çocuk ve Genç Fiziksel Uygunluk Bataryaları", "FitnessGram")]
    assert app["batarya_yas_araligi"]("Çocuk ve Genç Fiziksel Uygunluk Bataryaları", "FitnessGram") is None
    d = _p32(app, [("Can Er", t, iki_hafta) for t in fg[:-(len(fg) // 2)]], {"Can Er": 22})
    assert [k["batarya"] for k in d["yarim"]] == ["FitnessGram"]
    # tamamlanan batarya eşikten etkilenmez
    d = _p32(app, [("Ece Su", t, "01.01.2020") for t in tsyt], {"Ece Su": 9})
    assert d["yarim"] == [] and [k["sporcu"] for k in d["tamam"]] == ["Ece Su"]


def test_39c_susturma_sporcuya_ozel(app, tmp_path, monkeypatch):
    """'Bu bataryayı bitirmeyeceğim': sporcu+batarya ayarlar.json'da; o çift görünmez, başka sporcu görünür."""
    monkeypatch.chdir(tmp_path)
    tsyt = _tsyt_testleri(app)
    kay = [(s, t, "10.10.2026") for s in ("Ece Su", "Ali Bir") for t in tsyt[:6]]
    yas = {"Ece Su": 9, "Ali Bir": 10}
    assert {k["sporcu"] for k in _p32(app, kay, yas, susturulan=app["yarim_susturulanlar"]())["yarim"]} == {"Ece Su", "Ali Bir"}
    app["yarim_sustur"]("Ece Su", app["YON_TSYT"][1])
    assert app["ayar_oku"]()[app["YON_SUSTUR_ANAHTAR"]] == [["Ece Su", app["YON_TSYT"][1]]]
    app["yarim_sustur"]("Ece Su", app["YON_TSYT"][1])                 # ikinci basış yinelemez
    assert len(app["ayar_oku"]()[app["YON_SUSTUR_ANAHTAR"]]) == 1
    d = _p32(app, kay, yas, susturulan=app["yarim_susturulanlar"]())
    assert [k["sporcu"] for k in d["yarim"]] == ["Ali Bir"]
    (tmp_path / app["AYAR_DOSYA"]).write_text("{bozuk", encoding="utf-8")
    assert app["yarim_susturulanlar"]() == set()


def test_39d_susturma_dugmesi_ekranda(tmp_path, monkeypatch, app):
    """Yarım öneride düğme; basınca o sporcunun yarım önerisi gider, öteki sporcununki kalır; tercih dosyada."""
    import json as _json
    import pandas as _pd
    from datetime import date as _date, timedelta as _td
    tsyt = _tsyt_testleri(app)
    yakin = (_date.today() - _td(days=14)).strftime("%d.%m.%Y")

    def veri(d):
        _pd.DataFrame({"Ad": ["Deniz", "Ece"], "Soyad": ["Aydın", "Su"], "Yaş": [9, 10], "Cinsiyet": ["Erkek", "Kadın"],
                       "Grup": ["5-A", "5-A"]}).to_excel(d / "sporcular.xlsx", index=False)
        _pd.DataFrame({"Sporcu": ["Deniz Aydın"] * 6 + ["Ece Su"] * 7, "Test": tsyt[:6] + tsyt[:7],
                       "Tarih": [yakin] * 13}).to_excel(d / "test_sonuclari.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    assert not at.exception, [e.value for e in at.exception]
    baslik = lambda: [m.value for m in at.markdown if m.value.startswith("**") and " · " in m.value]
    assert baslik() == ["**Deniz Aydın · TSYT bataryasını tamamla (5 test)**"]
    assert [b.label for b in at.button].count("Bu bataryayı bitirmeyeceğim") == 1
    at.button(key="yon::sustur").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert not any("TSYT bataryasını tamamla" in x for x in baslik())          # Deniz: TSYT artık yarım değil
    at.selectbox(key="yon_secim").set_value("sporcu::Ece Su").run()
    assert baslik() == ["**Ece Su · TSYT bataryasını tamamla (4 test)**"]
    ayar = _json.loads((tmp_path / "ayarlar.json").read_text(encoding="utf-8"))
    assert ayar["yarim_susturulan"] == [["Deniz Aydın", app["YON_TSYT"][1]]]


def test_39e_paket32_degismeyenler(app):
    """Katalog 189, 160 görselli + 28 görselsiz, 169 asıl test tam adıyla 1. sırada, norm kapsamı değişmez.
    Paket 35: +6 test, hepsi görselli → 195, 166 + 28, 175 asıl; norm kapsamı yine 84 (Kademe 2 örneklem norm sayılmaz)."""
    tum = app["katalog_testleri"]()
    assert len(tum) == 196   # Paket 35c: + Sargent
    assert len(app["TEST_GORSELLERI"]) == 167 and len(app["TEST_GORSELSIZ"]) == 28
    asil = [t["ad"] for t in tum if t["ad"] not in app["TEST_TAKMA_AD"]]
    assert len(asil) == 176 and all(app["test_ara"](a)[0]["ad"] == a for a in asil)
    assert _norm_kapsami(app) == 84


# ════════════════════════════════════════════════════════════
# 40. Paket 33 — öneri motoru, boş durum, iz çubuğu
# ════════════════════════════════════════════════════════════
def _p33(app, sporcular, kayitlar=(), calismalar=None, bugun="24.10.2026", susturulan=()):
    """sporcular: [(ad soyad, yaş, dal, grup)]; kayitlar: [(sporcu, test, tarih, oturum)]."""
    import pandas as _pd
    sp = _pd.DataFrame({"Ad": [a.split()[0] for a, *_ in sporcular], "Soyad": [a.split()[1] for a, *_ in sporcular],
                        "Yaş": [y for _, y, _, _ in sporcular], "Spor Dalı": [d for _, _, d, _ in sporcular],
                        app["GRUP_KOLON"]: [g for *_, g in sporcular]})
    ts = _pd.DataFrame(list(kayitlar), columns=["Sporcu", "Test", "Tarih", "Oturum"])
    return app["oneri_baglami"](sp, ts, calismalar=calismalar or {}, bugun=bugun, susturulan=susturulan)


def _ilk(app, b, secim=None):
    secim = secim or app["oneri_secenekleri"](b)[1]
    liste = app["oneriler"](b, secim)
    return liste[0] if liste else None


_NHE = "NHE Tez Çalışması"
_NHE_TEST = ["Nordic Hamstring Kuvvet Testi — Genel (NHT)", "10m Sprint"]


def _nhe(app, n=26, olculen=4, dokunuldu="2026-10-20T10:00:00"):
    sp = [(f"Sporcu{i:02d} Ad{i:02d}", 22, "Güreş (Serbest)", "") for i in range(n)]
    sp[olculen] = ("Ali Yılmaz", 22, "Güreş (Serbest)", "")
    c = {"ad": _NHE, "testler": _NHE_TEST, "gruplar": ["Kontrol", "Deney"], "zamanlar": ["Ön test", "Son test"],
         "atamalar": {s[0]: ("Deney" if i % 2 == 0 else "Kontrol") for i, s in enumerate(sp)}, "dokunuldu": dokunuldu}
    kay = [(sp[i][0], t, "20.10.2026", f"{_NHE} · Ön test") for i in range(olculen) for t in _NHE_TEST]
    kay.append((sp[olculen][0], _NHE_TEST[0], "20.10.2026", f"{_NHE} · Ön test"))     # yarım ölçülen: ölçülmüş sayılmaz
    return sp, c, kay


def test_40a_kural0_aktif_calisma(app):
    """Çalışma varken 0. kural: 'N sporcunun K'sı ölçüldü, sıradaki: … (grup)'; en son dokunulan önce, öteki alternatif."""
    sp, c, kay = _nhe(app)
    b = _p33(app, sp, kay, {_NHE: c})
    secenekler, vars_ = app["oneri_secenekleri"](b)
    assert vars_ == f"calisma::{_NHE}" and secenekler[0] == vars_
    o = _ilk(app, b)
    assert o["kural"] == 0
    assert o["baslik"] == f"{_NHE} · Ön test — 26 sporcunun 4'ü ölçüldü, sıradaki: Ali Yılmaz (Deney)"
    assert o["gerekce"] == "başlanmış çalışma, 22 sporcu kaldı"
    assert o["eylem"] == {"tur": "calisma", "calisma": _NHE, "zaman": "Ön test", "sporcu": "Ali Yılmaz", "grup": "Deney"}
    # Ön test bitince sıradaki zaman
    kay2 = [(s[0], t, "20.10.2026", f"{_NHE} · Ön test") for s in sp for t in _NHE_TEST]
    o2 = _ilk(app, _p33(app, sp, kay2, {_NHE: c}))
    assert o2["baslik"].startswith(f"{_NHE} · Son test — 26 sporcunun 0'ı ölçüldü") and o2["gerekce"].startswith("kurulmuş")
    # her zaman tamamsa çalışma önerilmez
    kay3 = kay2 + [(s[0], t, "20.10.2026", f"{_NHE} · Son test") for s in sp for t in _NHE_TEST]
    assert app["oneri_secenekleri"](_p33(app, sp, kay3, {_NHE: c}))[1].startswith("sporcu::")
    # iki çalışma: en son dokunulan önerilir, öteki alternatif
    d = dict(c, ad="Pilot", dokunuldu="2026-10-23T09:00:00")
    b2 = _p33(app, sp, kay, {_NHE: c, "Pilot": d})
    liste = app["oneriler"](b2, app["oneri_secenekleri"](b2)[1])
    assert [x["calisma"] for x in liste] == ["Pilot", _NHE]
    # sporcu seçilince: o sporcunun çalışmadaki sırası 0. kural
    assert _ilk(app, b, "sporcu::Ali Yılmaz")["kural"] == 0
    assert [app["sayi_iyelik"](n) for n in (0, 1, 2, 3, 4, 6, 9, 10, 26, 40, 100)] == \
        ["0'ı", "1'i", "2'si", "3'ü", "4'ü", "6'sı", "9'u", "10'u", "26'sı", "40'ı", "100'ü"]


def test_40b_kural2_ve_brans_kapisi(app):
    """Çalışma ve ölçüm yokken 2. kural (7-11: TSYT); 10 yaşındaki güreşçide 3. kural yok; 11+ ve tarama tamamsa dal."""
    tsyt = _tsyt_testleri(app)
    o = _ilk(app, _p33(app, [("Ali Yılmaz", 10, "Güreş (Serbest)", "")]))
    assert o["kural"] == 2 and o["batarya"] == app["YON_TSYT"][1]
    assert o["gerekce"] == "yaşa uygun norm var: TSYT 7-11 yaş, sporcu 10 yaşında"
    # 10 yaş, tarama tamam: dal önerilmez (temel dönem) — 3. kural hiç yok
    b = _p33(app, [("Ali Yılmaz", 10, "Güreş (Serbest)", "")], [("Ali Yılmaz", t, "01.10.2026", "") for t in tsyt])
    assert all(x["kural"] != 3 for x in app["oneriler"](b, "sporcu::Ali Yılmaz"))
    # 12 yaş: önce tarama (Eurofit), tarama tamamsa Güreş
    eurofit = app["katalog_bataryalari"]()[("Çocuk ve Genç Fiziksel Uygunluk Bataryaları", "Eurofit Fiziksel Uygunluk Test Bataryası")]
    assert _ilk(app, _p33(app, [("Can Er", 12, "Güreş (Serbest)", "")]))["batarya"].startswith("Eurofit")
    b = _p33(app, [("Can Er", 12, "Güreş (Grekoromen)", "")], [("Can Er", t, "01.10.2026", "") for t in eurofit])
    o = _ilk(app, b)
    assert o["kural"] == 3 and o["batarya"] == "Güreş" and o["gerekce"] == "dalına özgü ölçüm: Güreş (Grekoromen)"
    assert o["eylem"]["tur"] == "oturum" and o["eylem"]["brans"] == "Güreş"
    assert "Special Wrestling Fitness Test (SWFT)" not in o["eylem"]["testler"]            # toplu girişte yok
    # yaşa uygun tarama olmayan yetişkin: doğrudan dal
    assert _ilk(app, _p33(app, [("Efe Kurt", 25, "Judo", "")]))["kural"] == 3
    # dalın katalogda karşılığı yok: 3. kural atlanır, boş liste yok
    assert app["oneriler"](_p33(app, [("Efe Kurt", 25, "Golf", "")]), "sporcu::Efe Kurt") == []
    # yas_araligi None olan batarya 2. kuralda önerilmez (4 yaş: PREFIT None)
    assert app["oneriler"](_p33(app, [("Ece Su", 4, "Genel/Yok", "")]), "sporcu::Ece Su") == []
    # dal eşlemesi: her değer katalogda bir branş rafı
    for dal in app["SPOR_DALI_BRANS"]:
        assert app["brans_rafi"](dal), dal


def test_40c_kural1_ve_kural4(app):
    """Yarım batarya (Paket 32 şartları) 1. kural; hepsi tamamsa son ölçümü en eski olan tekrar (N hafta)."""
    tsyt = _tsyt_testleri(app)
    b = _p33(app, [("Deniz Aydın", 9, "Genel/Yok", "5-A")], [("Deniz Aydın", t, "10.10.2026", "") for t in tsyt[:6]])
    o = _ilk(app, b)
    assert o["kural"] == 1 and o["gerekce"] == "başlanmış batarya, 5 test kaldı"
    assert o["eylem"]["testler"] == tsyt[6:] and o["eylem"]["grup"] == "5-A"
    # aynı tarama sürerken ikinci tarama önerilmez
    assert all(x["kural"] != 2 for x in app["oneriler"](b, "sporcu::Deniz Aydın"))
    # hepsi tamam: en eski ölçülen tekrar
    gures = [t for t in app["brans_rafi"]("Güreş (Serbest)")[2] if app["kayit_edilebilir"](t)]
    b = _p33(app, [("Efe Kurt", 25, "Güreş (Serbest)", "")],
             [("Efe Kurt", app["kanonik_test"](t), "15.08.2026", "") for t in gures])
    o = _ilk(app, b)
    assert o["kural"] == 4 and o["gerekce"] == "son ölçüm 10 hafta önce" and "Güreş" in o["baslik"]
    # her öneride gerekçe dolu
    for sp in ([("A B", 9, "Genel/Yok", "")], [("A B", 15, "Futbol", "")], [("A B", 30, "Halter", "")]):
        bb = _p33(app, sp)
        for x in app["oneriler"](bb, "sporcu::A B"):
            assert x["gerekce"].strip(), x


def test_40d_iz_cubugu(app):
    """Seçili testin yeri: kategori › alt › branş › test · nitelik; başka raflarda da varsa 'ayrıca'."""
    iz = app["test_izi"]
    assert iz("Special Wrestling Fitness Test (SWFT)") == \
        "Branşa Özgü Testler › Bireysel Sporlar › Güreş › Special Wrestling Fitness Test (SWFT) · anaerobik"
    assert iz("Modified Pull-Up Testi").endswith("— ayrıca: Presidential Youth Fitness Program")
    y = iz("Yo-Yo IR1 (Güreş)", ("Branşa Özgü Testler", "Bireysel Sporlar", "Güreş"))
    assert y.startswith("Branşa Özgü Testler › Bireysel Sporlar › Güreş › Yo-Yo IR1 (Güreş)")
    assert "ayrıca: Judo, Tenis" in y and "rafta daha" in y


def test_40e_ana_sayfa_tek_oneri(tmp_path, monkeypatch, app):
    """Ana sayfa: seçici + bir öneri + gerekçe + [Devam et] + bir alternatif + 'Başka bir test seç'; test listesi yok."""
    import json as _json
    import pandas as _pd
    sp, c, kay = _nhe(app, n=6, olculen=2)

    def veri(d):
        _pd.DataFrame({"Ad": [s[0].split()[0] for s in sp], "Soyad": [s[0].split()[1] for s in sp],
                       "Yaş": [s[1] for s in sp], "Spor Dalı": [s[2] for s in sp], "Cinsiyet": ["Erkek"] * len(sp)}
                      ).to_excel(d / "sporcular.xlsx", index=False)
        _pd.DataFrame(kay, columns=["Sporcu", "Test", "Tarih", "Oturum"]).to_excel(d / "test_sonuclari.xlsx", index=False)
        (d / "ayarlar.json").write_text(_json.dumps({"calismalar": {_NHE: {k: c[k] for k in c if k != "ad"}}},
                                                    ensure_ascii=False), encoding="utf-8")
    at = _apptest(tmp_path, monkeypatch, veri)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.multiselect                                          # katalog listesi ana sayfada yok
    assert [t.key for t in at.text_input] == ["yon_ara"]               # Paket 34: yalnız katlanmış aramada
    assert [e.label for e in _acilirlar(at)] == ["Test ara"] and not _acilirlar(at)[0].proto.expanded
    assert any(m.value == f"**{_NHE} · Ön test — 6 sporcunun 2'si ölçüldü, sıradaki: Ali Yılmaz (Deney)**"
               for m in at.markdown)
    assert [x.value for x in at.caption if x.value.startswith("Neden: ")] == ["Neden: başlanmış çalışma, 4 sporcu kaldı"]
    etiket = [b.label for b in at.button]
    assert "Devam et" in etiket and "Başka bir test seç →" in etiket
    assert sum(e.startswith("Ya da: ") for e in etiket) <= 1
    at.button(key="yon::devam").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["sayfa"] == "Test Oturumu"
    assert at.radio(key="ot_kaynak").value == "Çalışma"
    assert at.selectbox(key="ot_calisma").value == _NHE
    assert at.selectbox(key=f"ot_zaman::{_NHE}").value == "Ön test"
    at.button(key="ot_ana").click().run()                       # Paket 38b: sporcular Adım 2'de
    assert at.multiselect(key=f"ot_c_sporcular::{_NHE}::Deney").value == ["Ali Yılmaz"]


def test_40f_test_uygulada_iz(tmp_path, monkeypatch, app):
    """'Başka bir test seç' → Test Uygula; seçili testin yeri üstte (📍 …)."""
    import pandas as _pd

    def veri(d):
        _pd.DataFrame({"Ad": ["Ali"], "Soyad": ["Yılmaz"], "Yaş": [25], "Spor Dalı": ["Golf"], "Cinsiyet": ["Erkek"],
                       "Boy (cm)": [175], "Kilo (kg)": [70]}).to_excel(d / "sporcular.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    assert not at.exception, [e.value for e in at.exception]
    assert any(m.value == "**Önerecek bir şey yok.**" for m in at.markdown)
    at.button(key="yon::baska").click().run()
    assert at.session_state["sayfa"] == "Test Uygula"
    iz = [c.value for c in at.caption if c.value.startswith("📍 ")]
    assert len(iz) == 1 and " › " in iz[0]



# ════════════════════════════════════════════════════════════
# 53. Paket 38p-1: branş eşleştirmesinde "belirgin fark yok" (yayılım eşiği)
# ════════════════════════════════════════════════════════════
_DEMO = r"C:\Users\ertug\Desktop\Olcut_Demo"


def _sahte_fsc(n=11):
    A = _modul("olcut.analiz")
    return {"degerler": {k: {"deger": 1.0, "test_yasi": 10} for k in A.ESLESTIRME_DEGISKENLERI[:n]}}


def _uzakliklar(monkeypatch, degerler):
    """grup_uzakliklari'nı verilen uzaklıklarla değiştirir (eşik ve pencere kuralını yalın sınamak için)."""
    A = _modul("olcut.analiz")
    monkeypatch.setattr(A, "grup_uzakliklari", lambda d: {g: (u, {}) for g, u in degerler.items()})
    return A.brans_grubu_eslestir(_sahte_fsc(), 10)


def test_53a_esik_simulasyonu_kayitla_ayni():
    """araclar/esik_simulasyonu.py çıktısı veri/brans_profilleri.py'deki tabloyla birebir; eşik 0,10."""
    import importlib.util
    A, B = _modul("olcut.analiz"), _modul("veri.brans_profilleri")
    assert A.ESLESTIRME_AYIRT_ESIGI == 0.10
    yol = os.path.join(os.path.dirname(DOSYA), "araclar", "esik_simulasyonu.py")
    spec = importlib.util.spec_from_file_location("esik_simulasyonu", yol)
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    tablo, sans, esik_alti = E.simule()
    kayit = B.ESLESTIRME_YAYILIM_SIMULASYONU
    assert {k: v[0] for k, v in tablo.items()} == kayit["dilimler"]
    assert {k: v[1] for k, v in tablo.items()} == kayit["pay"]
    assert sans == kayit["sans"] and esik_alti == kayit["esik_alti"]


def test_53b_esik_tam_degerde_ayirt_edilebilir_ve_pencere(monkeypatch):
    """yayılım < 0,10 → ayırt edilemez (pencere boş); tam 0,10 → ayırt edilebilir; pencere ilk 3 + 3. ile eşitler."""
    A = _modul("olcut.analiz")
    gr = list(_modul("veri.brans_profilleri").BRANS_GRUBU_PROFILLERI["degerler"])
    e = _uzakliklar(monkeypatch, dict(zip(gr, (1.00, 1.02, 1.04, 1.05, 1.07, 1.099))))
    assert e["ayirt_edilemez"] and A.fiziksel_pencere(e) == [] and abs(e["yayilim"] - 0.099) < 1e-12
    e = _uzakliklar(monkeypatch, dict(zip(gr, (0.90, 0.95, 0.97, 0.98, 0.99, 1.00))))   # tam 0,10
    assert not e["ayirt_edilemez"] and len(A.fiziksel_pencere(e)) == 3
    e = _uzakliklar(monkeypatch, dict(zip(gr, (0.50, 0.60, 0.701, 0.704, 0.70, 0.90))))  # 3. ile iki ondalıkta eşitler
    assert sorted(A.fiziksel_pencere(e)) == sorted(gr[:5]) and e["pencere"][:2] == gr[:2]
    pen = A.ilgi_fiziksel_pencereler(_uzakliklar(monkeypatch, dict(zip(gr, (1, 1.01, 1.02, 1.03, 1.04, 1.05)))),
                                     {gr[0]: 4.5, gr[1]: 2.0})
    assert pen["fiziksel"] == [] and pen["kesisim"] == [] and pen["fiziksel_ayirt_edilemez"] is True
    assert pen["seviyor"] == [gr[0]] and pen["yalniz_fiziksel"] == []


def _demo_rapor(ad):
    if not os.path.exists(os.path.join(_DEMO, "sporcular.xlsx")):
        pytest.skip("Olcut_Demo yok")
    import shutil, tempfile
    d = tempfile.mkdtemp()
    for f in ("sporcular.xlsx", "test_sonuclari.xlsx", "ilgi_anketi.xlsx"):
        shutil.copy(os.path.join(_DEMO, f), d)
    eski = os.getcwd()
    os.chdir(d)
    try:
        return _modul("olcut.analiz").rapor_verisi(ad)
    finally:
        os.chdir(eski)


def test_53c_demo_cocuklari_yayilim():
    """Demo: Kaan ayırt edilemez; Ali, Ece, Can, Nisa, Burak ayırt edilebilir (her biri farklı bir gruba yakın)."""
    assert _demo_rapor("Kaan Demo")["esl"]["ayirt_edilemez"] is True
    for ad in ("Ali", "Ece", "Can", "Nisa", "Burak"):
        e = _demo_rapor(f"{ad} Demo")["esl"]
        assert e["uygun"] and not e["ayirt_edilemez"] and e["yayilim"] >= 0.10, ad


def test_53d_ayirt_edilemezde_veli_raporunda_fiziksel_grup_adi_yok(app):
    """Ayırt edilemez: fiziksel pencerede grup adı yok, verilen metin; raporda geçen her grup adı ilgi anketinden;
    özet cümle (sevdiği grup var / yok). Antrenör: yayılım satırı, eşik notu, simülasyon tablosu."""
    R = _modul("olcut.raporlar")
    gruplar = list(_modul("veri.brans_profilleri").BRANS_GRUBU_PROFILLERI["gruplar"])
    v = _demo_rapor("Kaan Demo")
    h = app["veli_raporu_html"](v)
    fiz = h.split("Fiziksel özellikleri bu gruplara yakın")[1].split("</div>")[0]
    assert R.VELI_FIZIKSEL_AYIRT_EDILEMEZ in fiz and not [g for g in gruplar if g in fiz]
    pencereler = h.split("İki pencere")[1].split('class="veli-sonuc')[0].split("<h2>")[0]
    assert {g for g in gruplar if g in pencereler} <= set(v["pen"]["seviyor"])
    assert R.VELI_OZET_AYIRT_EDILEMEZ_SEVIYOR.format(grup=", ".join(v["pen"]["seviyor"])) in h
    v2 = dict(v, pen=dict(v["pen"], seviyor=[], kesisim=[], yalniz_ilgi=[]))
    assert R.VELI_OZET_AYIRT_EDILEMEZ in app["veli_raporu_html"](v2)
    a = app["antrenor_raporu_html"](v)
    assert "Yayılım (en uzak − en yakın grup): 0,05. Eşik 0,10." in a and R.ANTRENOR_AYIRT_EDILEMEZ in a
    assert "Doğru grup pencerede" in a
    ali = _demo_rapor("Ali Demo")
    ah = app["antrenor_raporu_html"](ali)
    assert "Eşik 0,10." in ah and R.ANTRENOR_AYIRT_EDILEMEZ not in ah
    assert R.VELI_FIZIKSEL_AYIRT_EDILEMEZ not in app["veli_raporu_html"](ali)



