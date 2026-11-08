"""
Ölçüt test takımı ortak yapılandırması, fikstürler (kaynak, agac, uyg_agac, app) ve paylaşılan yardımcılar.
"""
import ast
import collections
import glob
import math
import os
import re
import sys
import types

import pytest

KLASOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KLASOR not in sys.path:
    sys.path.insert(0, KLASOR)
if os.path.join(KLASOR, "araclar") not in sys.path:
    sys.path.insert(0, os.path.join(KLASOR, "araclar"))


def _dosya_bul():
    ortam = os.environ.get("UYGULAMA")
    if ortam:
        yol = ortam if os.path.isabs(ortam) else os.path.join(KLASOR, ortam)
        if not os.path.exists(yol):
            raise FileNotFoundError(f"UYGULAMA ile verilen dosya yok: {yol}")
        return yol
    varsayilan = os.path.join(KLASOR, "uygulama.py")
    if os.path.exists(varsayilan):
        return varsayilan
    adaylar = [p for p in glob.glob(os.path.join(KLASOR, "uygulama*.py"))]
    if not adaylar:
        raise FileNotFoundError("Klasörde uygulama.py ya da uygulama*.py bulunamadı.")
    return max(adaylar, key=os.path.getmtime)


DOSYA = _dosya_bul()


class _StKukla:
    """Modül düzeyinde st.xxx(...) çağrısı varsa çalışmasın diye: her şey None döner."""
    def __getattr__(self, ad):
        return self

    def __call__(self, *a, **k):
        return None


def _kaynak_dosyalari(veri=True):
    """
    Bölme Aşama 1-2: uygulama.py + olcut/**/*.py (+ veri/*.py). Kaynak taraması (renk kodu, emoji, tekrarlanan
    anahtar, ağ kitaplığı…) taşınan kodu ve veriyi de görsün. Sıra: uygulama.py, olcut (yol sırasıyla), veri.
    """
    kok = os.path.dirname(DOSYA)
    yollar = [DOSYA]
    for alt in ("olcut",) + (("veri",) if veri else ()):
        for d, _, ds in sorted(os.walk(os.path.join(kok, alt))):
            yollar += [os.path.join(d, x) for x in sorted(ds) if x.endswith(".py")]
    return yollar


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="session")
def kaynak():
    return "\n".join(_oku(y) for y in _kaynak_dosyalari())


@pytest.fixture(scope="session")
def agac():
    """Birleşik ağaç: her dosya ayrı ayrıştırılır, gövdeler sırayla birleştirilir."""
    return ast.Module(body=[d for y in _kaynak_dosyalari() for d in ast.parse(_oku(y)).body], type_ignores=[])


@pytest.fixture(scope="session")
def uyg_agac():
    """Yalnız uygulama.py — app fikstürü bunu çalıştırır."""
    return ast.parse(_oku(DOSYA))


_VERI_MODULLERI = (
    "veri.normlar_kategorik",
    "veri.normlar_tsyt",
    "veri.brans_profilleri",
    "veri.metinler",
)

_OLCUT_MODULLERI = (
    "olcut.ortak",
    "olcut.tema",
    "olcut.esik",
    "olcut.katalog_islemleri",
    "olcut.gorseller.cizim",
    "olcut.gorseller.hareketler",
    "olcut.gorseller.sahneler",
    "olcut.norm",
    "olcut.analiz",
    "olcut.kayit",
    "olcut.raporlar",
    "olcut.oneri",
    "olcut.bilesenler",
    "olcut.sayfalar.ana_sayfa",
    "olcut.sayfalar.test_oturumu",
    "olcut.sayfalar.nitelik",
    "olcut.sayfalar.sonuclar",
)


def _modulleri_yukle(kl, ns):
    import importlib
    if not os.path.isdir(os.path.join(kl, "olcut")):
        return
    if kl not in sys.path:
        sys.path.insert(0, kl)
    ns.setdefault("_math", math)
    for m_ad in _VERI_MODULLERI + _OLCUT_MODULLERI:
        yol = os.path.join(kl, *m_ad.split(".")) + ".py"
        if not os.path.exists(yol):
            continue
        mod = importlib.import_module(m_ad)
        m_agac = ast.parse(_oku(yol))
        for d in m_agac.body:
            adlar = (
                [d.name]
                if isinstance(d, (ast.FunctionDef, ast.ClassDef))
                else [t.id for t in d.targets if isinstance(t, ast.Name)]
                if isinstance(d, ast.Assign)
                else []
            )
            for ad in adlar:
                if hasattr(mod, ad):
                    ns[ad] = getattr(mod, ad)


@pytest.fixture(scope="session")
def app(uyg_agac):
    """Modül düzeyindeki tanımları Streamlit'siz bir ad alanında çalıştırır."""
    g = {"__name__": "uygulama_denetim", "st": _StKukla()}
    _modulleri_yukle(os.path.dirname(DOSYA), g)
    atlanan = []
    for dugum in uyg_agac.body:
        if isinstance(dugum, ast.Import):
            if any(a.name.split(".")[0] in ("streamlit", "plotly") for a in dugum.names):
                continue
        elif isinstance(dugum, ast.ImportFrom):
            if (dugum.module or "").split(".")[0] in ("streamlit", "plotly"):
                continue
        elif not isinstance(dugum, (ast.FunctionDef, ast.Assign, ast.AnnAssign, ast.ClassDef)):
            continue
        try:
            exec(compile(ast.Module(body=[dugum], type_ignores=[]), DOSYA, "exec"), g)
        except Exception as hata:
            atlanan.append((dugum.lineno, repr(hata)[:120]))
    g["_atlanan"] = atlanan
    return g


_AYRAC = "\x1f"


def _testler(katalog):
    """(yol, tanım) — katalogdaki her test. '_' ile başlayan anahtarlar (ör. _kunye) test değildir."""
    for ad, deger in katalog.items():
        if str(ad).startswith("_") or not isinstance(deger, dict):
            continue
        if any(a in deger for a in ("protokol", "kaynak", "degiskenler")):
            yield ad, deger
        elif deger and all(isinstance(v, dict) for k, v in deger.items() if not str(k).startswith("_")):
            for alt_ad, alt in _testler(deger):
                yield f"{ad}{_AYRAC}{alt_ad}", alt
        else:
            yield ad, deger


def _test_adi(yol):
    return yol.split(_AYRAC)[-1]


def _ozet(liste, n=15):
    liste = list(liste)
    ek = f"\n  … ve {len(liste) - n} tane daha" if len(liste) > n else ""
    return "\n  " + "\n  ".join(str(x) for x in liste[:n]) + ek


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

ZORUNLU_TERIMLER = [
    "Z skoru", "Persentil", "Performans persentili", "P5 / P95", "Norm", "Düşük-iyi test", "MQ", "PQ", "Ortalama Z",
    "Havuzlanmış standart sapma", "Ortalama standart uzaklık", "Güven düzeyi", "Taban / tavan etkisi",
    "Sınır değer (P5 altı / P95 üstü)", "HFZ", "VKİ", "Asimetri indeksi", "VO2max",
    "Reaktif kuvvet indeksi", "Nötr (tanımlayıcı) ölçüm", "Doğum çeyreği",
]

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

def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _parlaklik(h):
    r, g, b = (_lin(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def _L(h):
    y = _parlaklik(h)
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16

def _kontrast(a, b):
    x, y = sorted((_parlaklik(a), _parlaklik(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)

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

def app_teknik_kaliplari():
    return VELI_TEKNIK

def _gorsel_testleri(app):
    K = app["TEST_KATALOGU"]
    tsyt = [t for t in K["Türkiye Sportif Yetenek Modeli (TSYT)"]["TSYT Bataryası — 7-11 Yaş (GSB)"] if t != "_kunye"]
    ktk = [t for t in K["Çocuk ve Genç Fiziksel Uygunluk Bataryaları"]["KTK3+ Motor Koordinasyon Test Bataryası"]
           if t != "_kunye"]
    return tsyt, ktk

def _svgler(app, ad):
    html = app["test_gorseli_html"](ad)
    return re.findall(r"<svg\b.*?</svg>", html, flags=re.S)

_FIGUR_PARCALARI = [("parmak1", "ayak1"), ("ayak1", "diz1"), ("diz1", "kok_b1"), ("parmak2", "ayak2"), ("ayak2", "diz2"),
                    ("diz2", "kok_b2"), ("kalca", "boyun"), ("el1", "dirsek1"), ("dirsek1", "kok_k1"),
                    ("el2", "dirsek2"), ("dirsek2", "kok_k2")]

def _parca_kutuda(a, b, k, pay=0.0):
    for i in range(41):
        t = i / 40
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if k[0] - pay <= x <= k[2] + pay and k[1] - pay <= y <= k[3] + pay:
            return True
    return False

def _sahneler_tekil(app):
    """
    Her farklı sahne bir kez: aynı fonksiyon aynı bağımsız değişkenlerle iki testte kullanılıyorsa biri yeter.
    Değişkeni farklı olan (ör. branş adı başlıkta, mesafe etikette) ayrı denetlenir — yazı genişliği değişir.
    (ad, sahne fonksiyonunun adı) döner.
    """
    gorulen, liste = set(), []
    for ad, (f, _) in app["TEST_GORSELLERI"].items():
        anahtar = (getattr(f, "func", f).__name__, repr(getattr(f, "args", ())), repr(getattr(f, "keywords", {})))
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        liste.append((ad, anahtar[0]))
    return liste

def _sayilar(metin):
    out = set()
    for s_ in re.findall(r"\d+(?:[.,]\d+)?", metin):
        v = float(s_.replace(",", "."))
        out.add(str(int(v)) if v == int(v) else f"{v:g}")
    return out

def _kutu_araligi(a, b):
    """İki kutu arasındaki boşluk (eksenlerden birinde ayrılık; üst üste ise negatif)."""
    return max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])

def _nokta_kutu(px, py, k):
    """Noktanın dikdörtgene uzaklığı (içindeyse 0)."""
    dx = max(k[0] - px, 0, px - k[2])
    dy = max(k[1] - py, 0, py - k[3])
    return (dx * dx + dy * dy) ** 0.5

def _nokta_parca(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    uz = vx * vx + vy * vy
    t = 0.0 if uz == 0 else max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / uz))
    return ((px - x1 - t * vx) ** 2 + (py - y1 - t * vy) ** 2) ** 0.5

def _kutu_parca(k, x1, y1, x2, y2):
    """Dikdörtgen ile doğru parçası arası en kısa uzaklık (kesişiyorsa 0)."""
    for i in range(21):                                   # parça kutunun içinden geçiyor mu
        t = i / 20
        if _nokta_kutu(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, k) == 0:
            return 0.0
    koseler = [(k[0], k[1]), (k[2], k[1]), (k[2], k[3]), (k[0], k[3])]
    return min([_nokta_kutu(x1, y1, k), _nokta_kutu(x2, y2, k)]
               + [_nokta_parca(cx, cy, x1, y1, x2, y2) for cx, cy in koseler])

def _yazi_cizgi_uzakligi(k, sekil):
    """Yazı kutusu ↔ çizilmiş şekil: çizginin kendi kalınlığı düşülür (çizginin kenarına uzaklık)."""
    tur = sekil[0]
    if tur == "cizgi":
        return _kutu_parca(k, *sekil[1:5]) - sekil[5]
    if tur == "disk":
        return _nokta_kutu(sekil[1], sekil[2], k) - sekil[3]
    return max(sekil[1] - k[2], k[0] - sekil[3], sekil[2] - k[3], k[1] - sekil[4], 0.0)

def _tsyt_testleri(app):
    return app["katalog_bataryalari"]()[app["YON_TSYT"]]

def _apptest(tmp_path, monkeypatch, hazirla):
    st_test = pytest.importorskip("streamlit.testing.v1")
    try:
        from streamlit.testing.v1.element_tree import ButtonGroup as _BG
        if not getattr(_BG, "_olcut_uyumlu", False):
            _eski_indices = _BG.indices.fget

            def _uyumlu_indices(self):
                try:
                    return _eski_indices(self)
                except ValueError:
                    degerler = self.value if isinstance(self.value, (list, tuple)) else ([self.value] if self.value is not None else [])
                    return [self.options.index(self.format_func(v)) for v in degerler]

            _BG.indices = property(_uyumlu_indices)
            _BG._olcut_uyumlu = True
    except Exception:
        pass
    import importlib.util as _ilu
    import streamlit as _st
    from streamlit.delta_generator import DeltaGenerator as _DG

    class _PlotlyKukla:
        __path__ = []
        __spec__ = None

        def __getattr__(self, _ad):
            return self

        def __call__(self, *a, **k):
            return self

    try:
        _plotly_var = not isinstance(sys.modules.get("plotly"), _PlotlyKukla) and _ilu.find_spec("plotly") is not None
    except Exception:
        _plotly_var = False
    if not _plotly_var:
        for _m in ("plotly", "plotly.graph_objects", "plotly.express", "plotly.io"):
            sys.modules.setdefault(_m, _PlotlyKukla())
        monkeypatch.setattr(_DG, "plotly_chart", lambda *a, **k: None, raising=False)
        monkeypatch.setattr(_st, "plotly_chart", lambda *a, **k: None, raising=False)
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

_P17_TESTLER = [
    "Yo-Yo IR1 (Futbol)", "Yo-Yo IR2 (Futbol)", "RSA Testi (Repeated Sprint Ability)",
    "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)", "Nordic Hamstring Kuvvet Testi (NHT)",
    "Loughborough İntermittent Shuttle Test (LIST)", "Illinois Çeviklik Testi",
    "NBA Lane Agility Testi", "NBA 3/4 Saha Sprint Testi", "Dikey Sıçrama - Basketbol (CMJ + SJ)", "Yo-Yo IR1 (Basketbol)",
    "Dikey Sıçrama - Voleybol (CMJ + SJ + DJ)", "20m Sprint - Voleybol", "Voleybol Çeviklik Testi (VAT)", "Yo-Yo IR1 (Voleybol)",
    "Yo-Yo IR1 (Hentbol)", "Hentbol Çeviklik ve Sprint Testi", "Dikey Sıçrama (Hentbol)",
    "10m Sprint", "20m Sprint", "100m Sprint", "200m Sprint", "Sprint Hızlanma Profili (10-20-30m)",
    "400m Sprint", "30-15 İntermittent Fitness Test (30-15 IFT)", "Atletik Güç Testi Bataryası",
]

_P18_TESTLER = [
    "Special Judo Fitness Test (SJFT)", "Judo Fiziksel Uygunluk Testi (JPFT)", "Uchi-Komi Fitness Test (UKFT)",
    "Yo-Yo IR1 (Judo)", "Taekwondo Spesifik Aerobik Test (TSAT)", "Taekwondo Çeviklik ve Hız Testi",
    "Yo-Yo IR1 (Taekwondo)", "Karate Spesifik Dayanıklılık Testi (KSDT)", "Karate Çeviklik Testi (KAT)",
    "Yo-Yo IR1 (Karate)", "Muay Thai Spesifik Dayanıklılık Testi (MTSDT)", "Wingate (Muay Thai)",
    "Yo-Yo IR1 (Muay Thai)", "MMA Spesifik Kondisyon Testi (MMA-SCT)", "MMA Fiziksel Uygunluk Bataryası",
    "Wingate (MMA)", "BJJ Spesifik Dayanıklılık Testi (BJJSFT)", "BJJ Kavrama Kuvveti ve Dayanıklılığı",
    "Yo-Yo IR1 (BJJ)", "Kickboks Spesifik Kondisyon Testi (KSKT)", "Wingate (Kickboks)",
    "Boks Spesifik Dayanıklılık Testi", "Yo-Yo IR1 (Boks)", "Sambo Spesifik Fitness Testi (SSFT)",
    "El Kavrama ve Kurtka Kavrama (Sambo)",
]

_P18_BATARYA = ["Judo Fiziksel Uygunluk Testi (JPFT)", "MMA Fiziksel Uygunluk Bataryası"]

_P19_TESTLER = [
    'Flamingo Denge Testi',
    'Plate Tapping (Disk Dokunma) Testi',
    'Otur-Uzan (Sit and Reach) Testi',
    'Durarak Uzun Atlama',
    'El Kavrama Kuvveti (Eurofit)',
    'Asılı Durma - Bükümlü Kol (Bent Arm Hang)',
    'Mekik (Sit-Up) Testi - 30sn',
    '10x5m Mekik Koşusu (Shuttle Run)',
    '20m Mekik Koşusu (Eurofit/Léger)',
    'PACER (20m Mekik Koşusu)',
    'Push-Up (Şınav) Testi',
    'Modified Pull-Up Testi',
    'Curl-Up (Kademeli Mekik) Testi',
    'Trunk Lift (Gövde Kaldırma) Testi',
    'Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)',
    'Shoulder Stretch (Omuz Esnekliği) Testi',
    '1 Mil Yürüyüş/Koşu Testi',
    'Curl-Up (Mekik) Testi',
    'PACER Testi',
    'Push-Up Testi',
    'Trunk Lift Testi',
    'Back-Saver Sit and Reach',
    'Shoulder Stretch Testi',
    'CAPL Engel Parkuru (Motor Beceri)',
    'CAPL Duran Uzun Atlama (Fiziksel Uygunluk)',
    'CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)',
    '20m Mekik Koşusu (ALPHA)',
    'El Kavrama Kuvveti (ALPHA)',
    'Durarak Uzun Atlama (ALPHA)',
    '4x10m Mekik Koşusu (ALPHA)',
    'Back-Saver Sit and Reach (ALPHA)',
    'Plate Tapping (El Plakası Vurma)',
    'Durarak Uzun Atlama (PREFIT)',
    '20m Mekik Koşusu (PREFIT)',
    'El Kavrama Kuvveti (PREFIT)',
    '4x10m Mekik Koşusu (PREFIT)',
    'Flamingo Denge Testi (PREFIT)',
    '50m Sprint',
    'Mekik Koşusu (50m × 8)',
    'Durarak Uzun Atlama (CNPFM)',
    'Otur-Uzan Testi (CNPFM)',
    '1000m Koşusu - Erkek / 800m Koşusu - Kadın (CNPFM)',
    'Mekik (Sit-Up) 1 Dakika (CNPFM)',
    'Yana Sıçrama (KMS)',
    'Balans (Denge) Testi (KMS)',
    'Top Yakalama Testi (KMS)',
    '20m Sprint (KMS)',
    '20m Sprint (Latorre)',
    'Durarak Uzun Atlama (Latorre)',
    'El Kavrama Kuvveti (Latorre)',
    'Tek Ayak Denge Testi (Latorre)',
    'Top Fırlatma Testi (Latorre)',
    'Top Sektirme — Alternatif El (BOT-2)',
    'Omuz Rotasyon Testi (Sopa/İp)',
    'Diz Üstü Şınav — 30 sn (BOT-2)',
    'Oturma Yüksekliği',
    'Ghost Drill (Squash Çeviklik Testi)',
]

_P19_GORSELSIZ = [
    'Vücut Kompozisyonu - Deri Kıvrımı',
    'Vücut Kompozisyonu (PYFP)',
    'Vücut Kompozisyonu (PREFIT)',
    'Vücut Kompozisyonu (CNPFM)',
    'Vücut Kompozisyonu (Latorre)',
    'Bel Çevresi ve VKİ (Vücut Kompozisyonu)',
    'CAPL Günlük Adım Sayısı (Günlük Davranış)',
    'CAPL Motivasyon ve Güven Anketi',
]

def _figur_keytimes(app, ad):
    """Sahnenin figür yolu (d) animasyonlarının keyTimes listeleri."""
    svg = app["tg_sahne"](ad).svg(True, ad)
    return [[float(x) for x in kt.split(";")]
            for kt in re.findall(r'<animate attributeName="d" values="[^"]*" keyTimes="([^"]+)"', svg)]

_HFZ_BOLUMU = re.compile(r"^\*\*HFZ[^\n]*\n(?:- [^\n]*\n?)*", re.M)

def _hfz_bolumleri(metin):
    """Protokoldeki HFZ başlıklı bölümler (başlık satırı + altındaki madde satırları)."""
    return [m.group(0) for m in _HFZ_BOLUMU.finditer(metin)]

_KOORD = "Koordinasyon Parkuru (TSYT)"

_CAMSA = "CAPL Engel Parkuru (Motor Beceri)"

def _katalog_testi(app, ad):
    def gez(d):
        for k, v in d.items():
            if isinstance(v, dict):
                if k == ad and "protokol" in v:
                    return v
                r = gez(v)
                if r:
                    return r
    t = gez(app["TEST_KATALOGU"])
    assert t, ad
    return t

def _rozet_top(app, tur):
    d = app["_TG_PARKURLAR"][tur]
    P = app["_tg_zemin_seridi"](d["x0"], *d["olcek"])
    return [P(*d["yol"][i]) for i in d["donus"]]

def _ara_deger(seq, t):
    """[(t, a, b, ...)] dizisinde t anındaki doğrusal ara değer (SVG ile aynı: kareler arası doğrusal)."""
    for a, b in zip(seq, seq[1:]):
        if a[0] <= t <= b[0]:
            f = 0 if b[0] == a[0] else (t - a[0]) / (b[0] - a[0])
            return [x + (y - x) * f for x, y in zip(a[1:], b[1:])]
    return list(seq[-1][1:]) if t >= seq[-1][0] else list(seq[0][1:])

_NHT_G = "Nordic Hamstring Kuvvet Testi — Genel (NHT)"

def _test_oturumu_kaynagi(kaynak):
    """
    Test Oturumu sayfasının kaynağı. Paket 38b gövdeyi 'elif sayfa == "Test Oturumu":' bloğundan
    test_oturumu_sayfasi() ve _ot_* adım fonksiyonlarına taşıdı; bunlar dosyadaki sırayla birleştirilir.
    """
    return "\n".join(ast.get_source_segment(kaynak, d) for d in ast.parse(kaynak).body
                     if isinstance(d, ast.FunctionDef) and (d.name == "test_oturumu_sayfasi" or d.name.startswith("_ot_")))

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

_PALET_ADLARI = ("RENK", "NORM_SKALASI", "NOTR_SKALA", "BILINMEYEN_SKALA", "SERI_RENKLERI", "RAPOR_VURGU")

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

_P34_NORMATIF = {
    '100m Sprint (sn)', '10m Sprint (sn)', '200m Sprint (sn)', '20m Sprint (sn)', '30m Sprint En İyi (sn)',
    '400m Sprint (sn)', 'Asimetri İndeksi (%)', 'Askıda Kol Bükme (sn)', 'CMJ En İyi (cm)', 'Düşme Sayısı (1 dk)',
    'Düşme Sayısı (30 sn)', 'H:K Oranı Dom. (%)', 'H:K Oranı N-Dom. (%)', 'Illinois Çeviklik En İyi (sn)', 'Pik Güç (W)',
    'SJFT İndeksi', 'SWFT Index', 'Sağ Bacak (N/kg)', 'Sağ El (kg)', 'Sol Bacak (N/kg)', 'Sol El (kg)',
    'Tamamlanan Mesafe (m)', 'Tekrar Sayısı (30sn)', 'VO2max Tahmini (ml/kg/min)', 'Vücut Yağ % (Tahmini)'}

_P35_AYDOS = {"Halter": (10, 2.897, 0.196, 1.453, 0.106), "Güreş": (11, 1.915, 0.360, 1.301, 0.210),
              "Boks": (10, 1.827, 0.376, 1.178, 0.145), "Judo": (10, 1.606, 0.305, 1.273, 0.241),
              "Basketbol": (10, 1.566, 0.325, 1.027, 0.145), "Futbol": (15, 1.405, 0.304, 1.089, 0.228),
              "Voleybol": (11, 1.307, 0.171, 1.015, 0.185)}

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

def _p38f_satir(test, deg, deger, p, kategori="Çok Düşük"):
    return {"Test": test, "Değişken": deg, "Değer": deger, "Tarih": "29.07.2026", "Tür": "Performans",
            "Kategori": kategori, "Performans persentili": p}

_VERI_KLASOR = os.path.join(os.path.dirname(DOSYA), "veri")

_VERI_SERBEST = (ast.Constant, ast.Dict, ast.List, ast.Tuple, ast.Set, ast.Load)

def _veri_modulleri():
    if not os.path.isdir(_VERI_KLASOR):
        return []
    return sorted(os.path.join(_VERI_KLASOR, d) for d in os.listdir(_VERI_KLASOR)
                  if d.endswith(".py") and d != "__init__.py")

_OLCUT_KATMAN = ["ortak", "disa_aktarma", "tema", "esik", "katalog_islemleri", "gorseller.cizim", "gorseller.hareketler",
                 "gorseller.sahneler", "norm", "analiz", "kayit", "duzeltme", "kulup", "raporlar", "oneri", "karsilastirma", "kulup_raporu", "bilesenler", "sayfalar"]

def _olcut_katmani(modul):
    ad = modul[len("olcut."):]
    return next((i for i, k in enumerate(_OLCUT_KATMAN) if ad == k or ad.startswith(k + ".")), None)

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

def _kars_df(tmp_path, monkeypatch):
    import pandas as _pd
    monkeypatch.chdir(tmp_path)
    _p38g_veri(tmp_path)
    return _pd.read_excel(tmp_path / "test_sonuclari.xlsx")

def _p38j_noktali_oturumlar(d):
    """_p38g_veri, oturum adları " · " içerir (demo verisindeki gibi)."""
    import pandas as _pd
    _p38g_veri(d)
    t = _pd.read_excel(d / "test_sonuclari.xlsx")
    t["Oturum"] = t["Oturum"].map({"S1": "Demo · Ön Test", "S2": "Demo · Son Test"})
    t.to_excel(d / "test_sonuclari.xlsx", index=False)

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

_DEMO = r"C:\Users\ertug\Desktop\Olcut_Demo"

def _sahte_fsc(n=11):
    A = _modul("olcut.analiz")
    return {"degerler": {k: {"deger": 1.0, "test_yasi": 10} for k in A.ESLESTIRME_DEGISKENLERI[:n]}}

def _uzakliklar(monkeypatch, degerler):
    """grup_uzakliklari'nı verilen uzaklıklarla değiştirir (eşik ve pencere kuralını yalın sınamak için)."""
    A = _modul("olcut.analiz")
    monkeypatch.setattr(A, "grup_uzakliklari", lambda d: {g: (u, {}) for g, u in degerler.items()})
    return A.brans_grubu_eslestir(_sahte_fsc(), 10)

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


__all__ = [k for k in globals() if not k.startswith("__")]

