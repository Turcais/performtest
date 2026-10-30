"""
Ölçüt (sporcu performans uygulaması) — otomatik denetim (Paket 8; Paket 11-18 ile genişletildi)
=========================================================================================

Bugüne kadar her sürümde elle yapılan denetimlerin kalıcı hali. Her kontrol daha
önce gerçek bir hata yakalamış bir kontroldür (açıklamalar test fonksiyonlarında).

ÇALIŞTIRMA
----------
    python -m pytest test_uygulama.py -v

Dosya yanındaki `uygulama.py`'yi denetler. Başka bir dosyayı denetlemek için:

    Windows (PowerShell):  $env:UYGULAMA="uygulama (61).py"; python -m pytest test_uygulama.py -v
    macOS / Linux:         UYGULAMA="uygulama (61).py" python -m pytest test_uygulama.py -v

`uygulama.py` yoksa ve UYGULAMA da verilmemişse, klasördeki en yeni
"uygulama*.py" dosyası denetlenir (ekranın başında hangisi olduğu yazılır).

Gereken paketler: pytest ve pandas (pip install pytest pandas).

NASIL ÇALIŞIR
-------------
Uygulama içe aktarılmaz ve Streamlit çalıştırılmaz. Dosya `ast` ile okunur;
yalnızca modül düzeyindeki içe aktarmalar (streamlit ve plotly hariç), sabitler
(sözlükler, listeler) ve fonksiyon tanımları ayrı bir ad alanında çalıştırılır.
Sayfa kodu (if sayfa == ...) hiç çalışmaz; dosya okunmaz, yazılmaz.
"""
import ast
import collections
import glob
import math
import os
import re
import types

import pytest

KLASOR = os.path.dirname(os.path.abspath(__file__))


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
print(f"\nDenetlenen dosya: {DOSYA}")


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


@pytest.fixture(scope="module")
def kaynak():
    return "\n".join(_oku(y) for y in _kaynak_dosyalari())


@pytest.fixture(scope="module")
def agac():
    """Birleşik ağaç: her dosya ayrı ayrıştırılır, gövdeler sırayla birleştirilir."""
    return ast.Module(body=[d for y in _kaynak_dosyalari() for d in ast.parse(_oku(y)).body], type_ignores=[])


@pytest.fixture(scope="module")
def uyg_agac():
    """Yalnız uygulama.py — app fikstürü bunu çalıştırır (içe aktarmalar taşınan modülleri getirir)."""
    return ast.parse(_oku(DOSYA))


@pytest.fixture(scope="module")
def app(uyg_agac):
    agac = uyg_agac
    """Modül düzeyindeki tanımları Streamlit'siz bir ad alanında çalıştırır."""
    g = {"__name__": "uygulama_denetim", "st": _StKukla()}
    atlanan = []
    for dugum in agac.body:
        if isinstance(dugum, ast.Import):
            if any(a.name.split(".")[0] in ("streamlit", "plotly") for a in dugum.names):
                continue
        elif isinstance(dugum, ast.ImportFrom):
            if (dugum.module or "").split(".")[0] in ("streamlit", "plotly"):
                continue
        elif not isinstance(dugum, (ast.FunctionDef, ast.Assign, ast.AnnAssign, ast.ClassDef)):
            continue   # if/for/ifade: sayfa kodu — çalıştırılmaz
        try:
            exec(compile(ast.Module(body=[dugum], type_ignores=[]), DOSYA, "exec"), g)
        except Exception as hata:   # ör. st'ye bağlı bir atama — denetim için gerekmez
            atlanan.append((dugum.lineno, repr(hata)[:120]))
    g["_atlanan"] = atlanan
    return g


_AYRAC = "\x1f"   # yol ayracı: test adında geçmeyen karakter ("1000m … / 800m …" gibi adlarda " / " geçer)


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
            yield ad, deger   # yaprak ama test alanları yok — kontrol 3 yakalar


def _test_adi(yol):
    return yol.split(_AYRAC)[-1]


def _ozet(liste, n=15):
    liste = list(liste)
    ek = f"\n  … ve {len(liste) - n} tane daha" if len(liste) > n else ""
    return "\n  " + "\n  ".join(str(x) for x in liste[:n]) + ek


# ════════════════════════════════════════════════════════════
# 1. Sözdizimi
# ════════════════════════════════════════════════════════════
def test_01_sozdizimi(kaynak):
    """Dosya hatasız ayrıştırılıyor."""
    try:
        ast.parse(kaynak)
    except SyntaxError as hata:
        pytest.fail(f"Sözdizimi hatası: satır {hata.lineno}: {hata.msg}")


# ════════════════════════════════════════════════════════════
# 2. Tekrarlanan sözlük anahtarı
# (12 tekrar bulunmuştu; Trunk Lift notu ve Yo-Yo üst sınırı böyle kaybolmuştu:
#  Python'da aynı anahtar ikinci kez yazılınca ilki sessizce silinir.)
# ════════════════════════════════════════════════════════════
def test_02_tekrarlanan_anahtar_yok(agac):
    sorunlar = []
    for dugum in agac.body:
        if not isinstance(dugum, (ast.Assign, ast.AnnAssign)):
            continue
        hedef = ast.unparse(dugum.targets[0] if isinstance(dugum, ast.Assign) else dugum.target)
        for d in ast.walk(dugum):
            if not isinstance(d, ast.Dict):
                continue
            satirlar = collections.defaultdict(list)
            for k in d.keys:
                if isinstance(k, ast.Constant):
                    satirlar[k.value].append(k.lineno)
            for anahtar, sat in satirlar.items():
                if len(sat) > 1:
                    sorunlar.append(f"{hedef}: {anahtar!r} — satırlar {sat}")
    assert not sorunlar, "Tekrarlanan anahtar (ilk tanım sessizce kaybolur):" + _ozet(sorunlar)


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
# 17. Görsel sistem (Paket 11)
# ════════════════════════════════════════════════════════════
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


def test_17a_normatif_skala_gri_tonlamada_ayirt_edilir(app):
    """
    Renk körlüğü: skala yalnızca kırmızı-yeşil farkına dayanmasın. Gri tonlamada (yalnız açıklık)
    kategoriler sıralı ve ayırt edilebilir olmalı: Üstün en koyu, Çok Düşük en açık, komşular arası
    L* farkı ≥ 10. Rozet yazısı her kategoride okunur olmalı (kontrast ≥ 4.5:1, WCAG AA).
    """
    skala = app["NORM_SKALASI"]
    assert [k for k, *_ in skala] == ["Üstün", "İyi", "Ortalama Üstü", "Ortalama Altı", "Düşük", "Çok Düşük"]
    assert [s for _, s, _, _ in skala] == [6, 5, 4, 3, 2, 1]
    L = [_L(z) for _, _, z, _ in skala]
    sorunlar = [f"{skala[i][0]} → {skala[i + 1][0]}: ΔL* = {L[i + 1] - L[i]:.1f}" for i in range(5)
                if L[i + 1] - L[i] < 10]
    sorunlar += [f"{k}: yazı/zemin kontrastı {_kontrast(z, y):.2f}" for k, _, z, y in skala if _kontrast(z, y) < 4.5]
    assert not sorunlar, "Skala gri tonlamada ayırt edilemiyor ya da yazı okunmuyor:" + _ozet(sorunlar)


def test_17b_her_norm_kategorisi_skalada(app):
    """Uygulamadaki her norm kategorisi (yaş persentili, DMT, kategorik normlar, nötr) skalaya oturmalı."""
    adlar = {"Üstün", "İyi", "Ortalama Üstü", "Ortalama", "Ortalama Altı", "Düşük", "Çok Düşük"}
    for sozluk in (app["NORMATIF"], app["NORMATIF_TEST"]):
        for norm in sozluk.values():
            if norm.get("tur") == "orneklem":          # Kademe 2 (Paket 35): ort ± SD, kategori yok
                continue
            for anahtar, deger in norm.items():
                if anahtar in ("Erkek", "Kadın") and isinstance(deger, dict):
                    adlar |= set(deger)
            for brans in norm.get("branslar", {}).values():
                for c in ("Erkek", "Kadın"):
                    adlar |= set(brans.get(c, {}))
    eksik = sorted(a for a in adlar if app["kategori_bilgisi"](a)["seviye"] is None)
    eksik += [f"nötr: {a}" for a in app["NOTR_SIRA"] if app["kategori_bilgisi"](a, notr=True)["seviye"] is None]
    assert not eksik, "Skalada karşılığı olmayan kategori:" + _ozet(eksik)


def test_17c_emoji_daire_yok_renk_skaladan(app, kaynak):
    """Emoji daire (🟢🔵🟡🟠⚪) platforma göre değişir, biçimlenmez: kategori rengi yalnız NORM_SKALASI'ndan gelir."""
    bulunan = [e for e in "🟢🔵🟡🟠⚪" if e in kaynak]
    assert not bulunan, f"Emoji daire hâlâ kullanılıyor: {bulunan}"
    ys = app["yas_persentil_bul"]("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)", 10, "Erkek", 141)
    assert ys and ys["renk"].startswith("#"), ys
    skala_renkleri = {z for _, _, z, _ in app["NORM_SKALASI"]} | {app["NOTR_SKALA"]["zemin"]}
    assert ys["renk"] in skala_renkleri


def test_17d_renk_kodu_yalniz_gorsel_sistemde(kaynak):
    """
    'Önce sistem': renk kodu (#RRGGBB) yalnız dosyanın başındaki GÖRSEL SİSTEM bloğunda yazılır;
    sayfalar, grafikler ve raporlar RENK / NORM_SKALASI simgelerinden beslenir. (Paket 11 öncesi
    grafikler koyu tema için beyaz yazıyla sabitlenmişti; açık temada görünmez oluyordu.)
    """
    kalip = re.compile(r"#[0-9A-Fa-f]{6}\b|[\"']#[0-9A-Fa-f]{3}[\"']")
    tema = os.path.join(os.path.dirname(DOSYA), "olcut", "tema.py")
    disarida = []
    for yol in _kaynak_dosyalari():                       # Bölme Aşama 2: görsel sistem = olcut/tema.py
        if os.path.exists(tema) and os.path.samefile(yol, tema):
            continue
        satirlar = _oku(yol).split("\n")
        bas = son = -1
        if yol == DOSYA and not os.path.exists(tema):
            bas = next(i for i, l in enumerate(satirlar) if "GÖRSEL SİSTEM (Paket 11)" in l)
            son = next(i for i, l in enumerate(satirlar) if l.startswith("def tasarimi_uygula"))
        disarida += [f"{os.path.basename(yol)} satır {i + 1}: {l.strip()[:80]}" for i, l in enumerate(satirlar)
                     if not (bas <= i <= son) and kalip.search(l)]
    assert not disarida, "Görsel sistem dışında renk kodu:" + _ozet(disarida)


def test_17e_config_toml_simgelerden(app):
    """.streamlit/config.toml simgelerden üretilir; yanında bir kopya varsa onunla birebir aynı olmalı."""
    import tomllib
    metin = app["tema_toml"]()
    tema = tomllib.loads(metin)["theme"]
    for bolum, ad in (("light", "acik"), ("dark", "koyu")):           # Paket 34: renkler iki bölümde
        R, T = app["palet"](ad)["renk"], tema[bolum]
        assert T["primaryColor"] == R["ana"] and T["backgroundColor"] == R["zemin"]
        assert T["textColor"] == R["murekkep"] and T["borderColor"] == R["cizgi"]
    for yol in (os.path.join(KLASOR, ".streamlit", "config.toml"), os.path.join(KLASOR, "config.toml")):
        if os.path.exists(yol):
            with open(yol, encoding="utf-8") as f:
                assert f.read() == metin, f"{yol} simgelerle uyuşmuyor: uygulamayı açınca yeniden yazılır, silin."


def test_17f_sonuc_karti_tek_bilesen(app, agac):
    """
    Sonuç her yerde aynı kartla gösterilir: değer + birim, performans persentili, kategori, kaynak.
    Kategori adı her zaman kartın içinde yazılı (renk tek başına anlam taşımaz). Veli dili (sade=True)
    persentil göstermez. Sayfa kodunda kategoriyi st.metric ile basan eski yol kalmamalı.
    """
    kart = app["sonuc_karti_html"]
    for k, *_ in app["NORM_SKALASI"]:
        h = kart("Sağ El (kg)", 19, "kg", k, persentil=71, kaynak="GSB (2023)")
        for parca in (k, "19", "kg", "P71", "GSB (2023)", "seviye"):
            assert parca in h, (k, parca)
    assert "P71" not in kart("x", 1, "", "İyi", persentil=71, sade=True)
    notr = kart("Boy (cm)", 141, "cm", "Yüksek", notr=True, persentil=80)
    assert app["NOTR_SKALA"]["zemin"] in notr and "konum" in notr
    metrikte = [ast.unparse(d)[:90] for d in ast.walk(agac) if isinstance(d, ast.Call)
                and isinstance(d.func, ast.Attribute) and d.func.attr == "metric" and "kategori" in ast.unparse(d)]
    assert not metrikte, "Kategori hâlâ st.metric ile gösteriliyor:" + _ozet(metrikte)
    cagri = collections.Counter(d.func.id for d in ast.walk(agac) if isinstance(d, ast.Call)
                                and isinstance(d.func, ast.Name))
    assert cagri["sonuc_karti_html"] >= 2 and cagri["z_satiri_karti"] >= 2, cagri


def test_17g_cok_terimli_baslik_bozulmaz(app):
    """
    Paket 11'de bulunan hata: fare-üzeri açıklamasında birden çok terim varken araya giren boş satır
    markdown'da paragraf açıyor, <span> yarıda kalıyor ve açıklama ham HTML olarak başlık yerine basılıyordu.
    """
    h = app["baslik_html"]("Yaşa Göre Persentil", ["Performans persentili", "P5 / P95", "Z skoru", "Norm"])
    assert "\n" not in h and h.count("<span") == 1 and h.endswith("</span>")


def test_17h_yuzde_eki_turkce(app):
    """'%3'ünden', '%62'sinden' — 'akranlarının ~%3'inden iyi' gibi yanlış ek kalmasın."""
    beklenen = {3: "%3'ünden", 5: "%5'inden", 6: "%6'sından", 9: "%9'undan", 10: "%10'undan",
                40: "%40'ından", 50: "%50'sinden", 62: "%62'sinden", 71: "%71'inden", 90: "%90'ından",
                100: "%100'ünden"}
    yanlis = {n: app["yuzde_ayrilma"](n) for n in beklenen if app["yuzde_ayrilma"](n) != beklenen[n]}
    assert not yanlis, yanlis


def test_17i_norm_disi_yasta_makullük_yok(app):
    """
    3 yaşındaki bir çocuğun boyu 7 yaş normuyla 'olağandışı' ilan ediliyordu (boş formun varsayılanı).
    Yaş normun aralığı dışındaysa makullük denetlenmez — normu olmayan testteki kuralın aynısı.
    """
    assert app["makul_aralik"]("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)", 3, "Erkek") is None
    assert app["makul_aralik"]("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)", 9, "Erkek") is not None


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
# 19. Test görselleri (Paket 13): tek çizim takımı, kendi çizimimiz, bir kez oynar
# ════════════════════════════════════════════════════════════
def _gorsel_testleri(app):
    K = app["TEST_KATALOGU"]
    tsyt = [t for t in K["Türkiye Sportif Yetenek Modeli (TSYT)"]["TSYT Bataryası — 7-11 Yaş (GSB)"] if t != "_kunye"]
    ktk = [t for t in K["Çocuk ve Genç Fiziksel Uygunluk Bataryaları"]["KTK3+ Motor Koordinasyon Test Bataryası"]
           if t != "_kunye"]
    return tsyt, ktk


def _svgler(app, ad):
    html = app["test_gorseli_html"](ad)
    return re.findall(r"<svg\b.*?</svg>", html, flags=re.S)


def test_19a_kapsam_tsyt_11_ktk3_5(app):
    """Kapsam: TSYT bataryasının 11 testi ve KTK3+'ın 5 testi — her birinin görseli ve kritik ayrıntı cümlesi var."""
    tsyt, ktk = _gorsel_testleri(app)
    assert len(tsyt) == 11 and len(ktk) == 5, (len(tsyt), len(ktk))
    gorsel = app["TEST_GORSELLERI"]
    katalog = {_test_adi(y) for y, _ in _testler(app["TEST_KATALOGU"])}
    eksik = [t for t in tsyt + ktk if t not in gorsel]
    fazla = [t for t in gorsel if t not in katalog]
    kisa = [t for t, (_, kritik) in gorsel.items() if len(kritik) < 30]
    assert not (eksik or fazla or kisa), f"görseli yok: {eksik} · katalogda yok: {fazla} · kritik cümle eksik: {kisa}"


def test_19b_ayni_tuval_ayni_zemin_ayni_kalinlik(app):
    """
    Tek çizim takımı: her görsel aynı tuvalde (viewBox), aynı zemin çizgisiyle; çizgi kalınlıkları
    yalnız TG_KALINLIK'tan (figür, ölçeğe göre). Dışarıdan görsel yok (image/href/url/base64).
    """
    w, h = app["TG_TUVAL"]
    zemin = app["TG_ZEMIN"]
    kal = app["TG_KALINLIK"]
    katman = [k["incelik"] for k in app["FIGUR_KATMANI"].values()]   # figür: üç kademe × katman inceliği
    izinli = ({float(v) for v in kal.values()}
              | {round(kal[p] * k * i, 2) for p in ("figur", "govde") for k in (0.7, 0.8, 1.0) for i in katman})
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        for svg in _svgler(app, ad):
            if f'viewBox="0 0 {w} {h}"' not in svg:
                sorunlar.append(f"{ad}: farklı tuval")
            if f'y1="{zemin}" x2="{w - 6}" y2="{zemin}"' not in svg:
                sorunlar.append(f"{ad}: ortak zemin çizgisi yok")
            for k in set(re.findall(r'stroke-width="([0-9.]+)"', svg)):
                if float(k) not in izinli:
                    sorunlar.append(f"{ad}: takım dışı çizgi kalınlığı {k}")
            if re.search(r"<image|href=|url\(|base64", svg):
                sorunlar.append(f"{ad}: dışarıdan görsel/bağlantı")
    assert not sorunlar, "Görsel takım dışına çıkıyor:" + _ozet(sorunlar)


def test_19c_renkler_gorsel_sistemden(app):
    """Görsellerdeki her renk RENK simgelerinden (GÖRSEL SİSTEM bloğu); renk adı (white/red…) da yok."""
    izinli = {v.lower() for v in app["RENK"].values()}
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        for svg in _svgler(app, ad):
            for r in set(re.findall(r"#[0-9a-fA-F]{3,6}\b", svg)):
                if r.lower() not in izinli:
                    sorunlar.append(f"{ad}: {r}")
            cizim = re.sub(r"<animate[^>]*>", "", svg)   # animasyonun fill="freeze"i renk değildir
            for r in set(re.findall(r'(?:fill|stroke)="([a-z]+)"', cizim)):
                if r != "none":
                    sorunlar.append(f"{ad}: renk adı {r}")
    assert not sorunlar, "Görselde GÖRSEL SİSTEM dışı renk:" + _ozet(sorunlar)


def test_19d_bir_kez_oynar_son_pozda_durur(app):
    """
    Hareket bir kez oynar ve son pozda durur: her animasyon fill="freeze", döngü (repeatCount/indefinite) yok.
    Durağan kopya (prefers-reduced-motion) hiç animasyon içermez ve CSS onu hareket azaltıldığında gösterir.
    """
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        hareketli, duragan = _svgler(app, ad)
        anim = re.findall(r"<animate(?:Transform)?\b[^>]*>", hareketli)
        if not anim:
            sorunlar.append(f"{ad}: hareket yok")
        sorunlar += [f"{ad}: freeze yok" for a in anim if 'fill="freeze"' not in a]
        if re.search(r"repeatCount|indefinite|repeatDur", hareketli):
            sorunlar.append(f"{ad}: döngü")
        if "<animate" in duragan:
            sorunlar.append(f"{ad}: durağan kopyada hareket")
    css = app["TEMA_CSS"]
    assert "prefers-reduced-motion: reduce" in css and ".tg-hareketli {{ display:none; }}".replace("{{", "{").replace("}}", "}") in css
    assert not sorunlar, _ozet(sorunlar)



def test_19e_figur_her_karede_tuvalde(app):
    """Hareketin hiçbir karesinde figür tuvalin dışına taşmaz (Paket 13'te sürat ve sıçramada taşıyordu)."""
    w, h = app["TG_TUVAL"]
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        hareketli = _svgler(app, ad)[0]
        for degerler in re.findall(r'attributeName="d" values="([^"]+)"', hareketli):
            for x, y in re.findall(r"(-?[\d.]+),(-?[\d.]+)", degerler):
                if not (2 <= float(x) <= w - 2 and 2 <= float(y) <= h - 2):
                    sorunlar.append(f"{ad}: ({x}, {y})")
                    break
    assert not sorunlar, "Figür tuvalden taşıyor:" + _ozet(sorunlar)

# ════════════════════════════════════════════════════════════
# 20. Test görsellerinin kalitesi (Paket 14)
# ════════════════════════════════════════════════════════════
def test_20a_son_karede_uzuv_uclari_ayrik(app):
    """Figür tek çubuk gibi görünmesin: son karede eller ve ayaklar birbirine 3 birimden yakın değil."""
    import math as _m
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        e = app["tg_sahne"](ad).son_eklemler
        uclar = [(u, e[u]) for u in app["TG_UCLAR"]]
        for i, (a, p) in enumerate(uclar):
            for b, q in uclar[i + 1:]:
                if _m.dist(p, q) < app["TG_EN_YAKIN_UC"]:
                    sorunlar.append(f"{ad}: {a}–{b} {_m.dist(p, q):.1f} birim")
    assert not sorunlar, "Uzuv uçları üst üste:" + _ozet(sorunlar)


def test_20b_sahne_basina_en_cok_uc_yazi(app):
    """
    Sahne başına en çok üç yazı (başlık, not, ölçü/işaret etiketi); yazılar yalnız bu üç yoldan girer. Aynı yuvada
    nöbetleşe görünen yazılar (data-yuva, Paket 25: istasyon adı başlık yerinde) tek yazı sayılır.
    """
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        S = app["tg_sahne"](ad)
        for svg, K in ((S.svg(True, ad), S), (S.svg(False, ad), S.duragan or S)):   # ayrı durağan sahne (Paket 21)
            yuvalar = re.findall(r'<text data-yuva="([^"]+)"', svg)
            n = svg.count("<text") - len(yuvalar) + len(set(yuvalar))
            if n > app["TG_EN_COK_YAZI"]:
                sorunlar.append(f"{ad}: {n} yazı")
            if n != K.yazi_sayisi:
                sorunlar.append(f"{ad}: başlık/not/ölçü dışından yazı girmiş")
    assert not sorunlar, _ozet(sorunlar)


def test_20c_her_eklem_tuvalde(app):
    """Hareketin her karesinde her eklem tuvalin içinde (0 ≤ x ≤ 260, 0 ≤ y ≤ 140)."""
    w, h = app["TG_TUVAL"]
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        for kare in app["tg_sahne"](ad).tum_eklemler:
            disari = [k for k, (x, y) in kare.items() if not (0 <= x <= w and 0 <= y <= h)]
            if disari:
                sorunlar.append(f"{ad}: {disari[0]} {kare[disari[0]]}")
                break
    assert not sorunlar, "Eklem tuval dışında:" + _ozet(sorunlar)


def test_20d_animasyonda_sabit_renk_yok(app):
    """Animasyon öğelerinde (<animate…>) renk kodu yok: renk yalnız çizim öğesinde, simgelerden."""
    sorunlar = [ad for ad in app["TEST_GORSELLERI"]
                if any("#" in a for a in re.findall(r"<animate(?:Transform)?\b[^>]*>", _svgler(app, ad)[0]))]
    assert not sorunlar, sorunlar


def test_20e_olcu_oku_sifir_uzunlukta_degil(app):
    """Ölçü oku olan her sahnede okun uzunluğu > 0 (sıfır uzunlukta ölçü çizgisi kalmasın)."""
    import math as _m
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        for x1, y1, x2, y2 in app["tg_sahne"](ad).olculer:
            if _m.hypot(x2 - x1, y2 - y1) <= 0.5:
                sorunlar.append(f"{ad}: ({x1}, {y1})–({x2}, {y2})")
    assert not sorunlar, _ozet(sorunlar)


def test_20f_sahne_hareketi_kitapliktan_alir(app, agac):
    """
    Kitaplık sınırı: her sahne fonksiyonu bir hareket kitaplığı fonksiyonu (hk_*) çağırır ve pozu kendisi
    kurmaz (tg_poz / tg_yerlestir / poz sözlüğü yok). Kalan testlerin görselleri bu sınırla üretilecek.
    """
    sahneler = {getattr(f, "func", f).__name__ for f, _ in app["TEST_GORSELLERI"].values()}
    kitaplik = set(app["TG_HAREKET_KITAPLIGI"])
    fonks = {d.name: d for d in agac.body if isinstance(d, ast.FunctionDef)}

    def cagrilar(ad, gorulen=()):
        """Sahnenin ve çağırdığı _tg_ yardımcılarının çağrıları (ortak sahne yardımcıları da sayılır)."""
        c = {k.func.id for k in ast.walk(fonks[ad]) if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)}
        for alt in [x for x in c if x.startswith("_tg_") and x in fonks and x not in gorulen and x != ad]:
            c |= cagrilar(alt, gorulen + (ad,))
        return c
    sorunlar = []
    for d in agac.body:
        if isinstance(d, ast.FunctionDef) and d.name in sahneler:
            cagri = cagrilar(d.name)
            if not cagri & kitaplik:
                sorunlar.append(f"{d.name}: hareket kitaplığını çağırmıyor")
            if cagri & {"tg_poz", "tg_yerlestir", "tg_eklemler"}:
                sorunlar.append(f"{d.name}: pozu kendisi kuruyor ({sorted(cagri & {'tg_poz', 'tg_yerlestir', 'tg_eklemler'})})")
    eksik = [k for k in kitaplik if k not in app]
    assert not sorunlar and not eksik, _ozet(sorunlar + [f"tanımsız: {k}" for k in eksik])


def test_20g_son_kare_olcum_ani(app):
    """Durağan poz ölçüm anıdır: dikey sıçrama tepede (ayaklar yerden yukarıda), sağlık topu bırakma pozunda."""
    h = app["hk_dikey_sicrama"](118)
    e = app["tg_eklemler"](h.anahtarlar[-1][1])
    assert max(e["ayak1"][1], e["ayak2"][1]) <= app["TG_ZEMIN"] - 8, "dikey sıçrama son karesi tepede değil"
    a = app["hk_atma"](72, "geriye", yon=-1)
    birak = [p for t, p in a.anahtarlar if abs(t - a.olay["birakma_t"]) < 1e-9][0]
    assert a.anahtarlar[-1][1] == birak, "sağlık topu son karesi bırakma pozu değil"
    k = app["hk_kavrama"](118)
    assert k.anahtarlar[-1][1]["o1"] > k.anahtarlar[-2][1]["o1"], "kavrama son karesi sıkma anı değil"


# ════════════════════════════════════════════════════════════
# 21. Görsel ayrıntı denetimi (Paket 14 düzeltmeleri + Paket 15 branş görselleri)
# ════════════════════════════════════════════════════════════
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


def test_21a_brans_kapsami_ve_yoyo_tek_sahne(app):
    """
    Paket 15: Güreş (Yo-Yo IR1, SWFT, Modified SJFT, 6 dk maç) ve Buz Hokeyi (30 m paten, 6 m + 30 m, S-Turn)
    görselli; NHL/NHLTM Off-Ice bir batarya olduğu için görselsiz. 16 Yo-Yo IR1 testi aynı sahneyi kullanır,
    branş adı yalnız başlıkta geçer (sahnenin geri kalanı birebir aynı).
    """
    g = app["TEST_GORSELLERI"]
    gerekli = ["Yo-Yo IR1 (Güreş)", "Special Wrestling Fitness Test (SWFT)", "Modified SJFT (Güreş için)",
               "Simulated Wrestling Match (6 dk)", "30m Paten Hızı", "Hızlanma Paten Testi (6m + 30m)", "S-Turn Testi"]
    assert all(t in g for t in gerekli), [t for t in gerekli if t not in g]
    assert "NHL/NHLTM Off-Ice Testleri" not in g
    yoyo = [t for t in g if t.startswith("Yo-Yo IR1 (")]
    assert len(yoyo) == 16, len(yoyo)
    assert {getattr(g[t][0], "func", g[t][0]).__name__ for t in yoyo} == {"_tg_yoyo"}

    def bassiz(t):
        return re.sub(r'<text[^>]*font-size="9\.5"[^>]*>.*?</text>', "", app["tg_sahne"](t).svg(False, ""))
    for t in yoyo:
        brans = t[len("Yo-Yo IR1 ("):-1]
        sahne = app["tg_sahne"](t)
        baslik = sahne.yazi_kutulari[0][4] if sahne.yazi_kutulari else ""
        if brans != "Genel":
            assert brans in baslik, (t, baslik)
        assert bassiz(t) == bassiz("Yo-Yo IR1 (Genel)"), f"{t}: başlık dışında farklı"


def test_21b_yazi_cakismasi_yok(app):
    """
    Etiket çakışması: hiçbir yazı başka bir yazıyla, bir ölçü okuyla ya da (son karede) bir figürle çakışmaz;
    her yazı tuvalin içindedir. Yazı kutusu genişliği yaklaşık tahmindir (TgSahne.genislik).
    """
    w, h = app["TG_TUVAL"]
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        K = S.yazi_kutulari
        for i, a in enumerate(K):
            if a[0] < 0 or a[2] > w or a[1] < 0 or a[3] > h:
                sorunlar.append(f"{ad}: '{a[4]}' tuvalden taşıyor")
            for b in K[i + 1:]:
                if not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]):
                    sorunlar.append(f"{ad}: '{a[4]}' ile '{b[4]}' üst üste")
            for o in S.olcu_kayit:
                x1, y1, x2, y2 = o["uc"]
                if _parca_kutuda((x1, y1), (x2, y2), a):
                    sorunlar.append(f"{ad}: '{a[4]}' ölçü okunun üstünde")
            for f in S.figurler:
                if any(_parca_kutuda(f["son"][p], f["son"][q], a, pay=1.2) for p, q in _FIGUR_PARCALARI):
                    sorunlar.append(f"{ad}: '{a[4]}' figürün üstünde")
    assert not sorunlar, "Yazı çakışması:" + _ozet(sorunlar)


def test_21c_olcu_oku_etiketli_ve_olcege_uygun(app):
    """
    Ölçü oku: etiketsiz ok yalnız etiketli bir okun eşi olabilir (aynı uzunlukta). Ölçek tablosu: protokol mesafesi
    taşıyan her ok (metre) TG_OLCEK'teki ölçekle çizilir (±1,5 birim); bu okları kullanan her sahne tabloda yer alır.
    """
    import math as _m
    olcek = app["TG_OLCEK"]
    sorunlar = []
    for ad, fn in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        for o in S.olcu_kayit:
            uz = _m.hypot(o["uc"][2] - o["uc"][0], o["uc"][3] - o["uc"][1])
            if not o["etiket"]:
                es = S.olcu_kayit[o["es"]] if o["es"] is not None else None
                if es is None or not es["etiket"]:
                    sorunlar.append(f"{ad}: etiketsiz ölçü oku")
                elif abs(_m.hypot(es["uc"][2] - es["uc"][0], es["uc"][3] - es["uc"][1]) - uz) > 1.0:
                    sorunlar.append(f"{ad}: eş ok farklı uzunlukta")
            if o["metre"] is not None:
                if fn not in olcek:
                    sorunlar.append(f"{ad}: ölçek tablosunda yok ({fn})")
                elif abs(uz - o["metre"] * olcek[fn][0]) > 1.5:
                    sorunlar.append(f"{ad}: {o['metre']} m = {uz:.1f} birim, ölçek {o['metre'] * olcek[fn][0]:.1f} diyor")
    bos = [k for k in olcek if not k.startswith("_tg_")]
    assert not sorunlar and not bos, "Ölçü oku / ölçek:" + _ozet(sorunlar + bos)


def test_21d_figur_katmanlari_tek_anlamli(app):
    """
    Gri tek anlam taşır (Paket 18, GÖRSEL SİSTEM → FIGUR_KATMANI): her figür çizgisi bir katmana bağlı ve
    o katmanın kodunu taşır — ölçülen: mürekkep, tam opak; ikinci kişi: AYRI RENK (RENK["ikinci"]), ince;
    önceki an: mürekkep, çok soluk, belirgin ince ve kesik. Uzak uzuv (derinlik) yalnız opaklığı
    FIGUR_DERINLIK_OPAKLIK ile çarpar, rengi ve kalınlığı değiştirmez. İkinci kişinin rengi başka hiçbir şeyde yok.
    """
    K, R = app["FIGUR_KATMANI"], app["RENK"]
    tg = app["tg_renk"]                                   # Paket 34: renk yedekli CSS değişkeni
    d = app["FIGUR_DERINLIK_OPAKLIK"]
    assert len({k["renk"] for k in K.values()}) == 2 and K["ikinci_kisi"]["renk"] != K["olculen"]["renk"]
    assert K["onceki_an"]["opaklik"] < d < 1 and K["onceki_an"]["incelik"] < K["ikinci_kisi"]["incelik"] < 1
    assert K["onceki_an"]["kesik"] and not K["olculen"]["kesik"] and not K["ikinci_kisi"]["kesik"]
    sorunlar, ikinci_kisili = [], 0
    for ad, _ in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        svg = S.svg(False, ad)
        if any(f["rol"] == "partner" for f in S.figurler):
            ikinci_kisili += 1
            if [f["rol"] for f in S.figurler].count("olculen") != 1:
                sorunlar.append(f"{ad}: ikinci kişili sahnede ölçülen sporcu tek değil")
        kalin = {}
        for etiket in re.findall(r'<(?:path|circle)\b[^>]*data-katman="[^"]+"[^>]*>', svg):
            k = re.search(r'data-katman="([^"]+)"', etiket).group(1)
            renk = re.search(r'(?:stroke|fill)="(var\(--tg-[a-z]+, #[0-9A-Fa-f]{6}\))"',
                             etiket.replace('fill="none" ', "")).group(1)
            op = float((re.search(r'(?:stroke|fill)-opacity="([\d.]+)"', etiket) or [None, "1"])[1])
            beklenen = K[k]["opaklik"] * (d if 'data-derinlik="1"' in etiket else 1)
            if renk != tg(K[k]["renk"]) or abs(op - beklenen) > 1e-3:
                sorunlar.append(f"{ad}: {k} kodu bozuk (renk {renk}, opaklık {op})")
            if ("stroke-dasharray" in etiket) != bool(K[k]["kesik"]) and "<path" in etiket:
                sorunlar.append(f"{ad}: {k} kesik çizgi kuralı bozuk")
            w = re.search(r'stroke-width="([\d.]+)"', etiket)
            if w:
                kalin.setdefault(k, set()).add(float(w.group(1)))
        if "olculen" in kalin and "onceki_an" in kalin and max(kalin["onceki_an"]) >= min(kalin["olculen"]):
            sorunlar.append(f"{ad}: önceki an ölçülenden ince değil")
        disari = re.sub(r'<(?:path|circle)\b[^>]*data-katman="ikinci_kisi"[^>]*>', "", svg)
        if "--tg-ikinci," in disari or R["ikinci"].lower() in disari.lower():
            sorunlar.append(f"{ad}: ikinci kişi rengi başka bir şeyde kullanılmış")
    assert ikinci_kisili >= 5, f"ikinci kişili sahne sayısı {ikinci_kisili}"
    assert not sorunlar, "Figür katmanı:" + _ozet(sorunlar)


def _sayilar(metin):
    out = set()
    for s_ in re.findall(r"\d+(?:[.,]\d+)?", metin):
        v = float(s_.replace(",", "."))
        out.add(str(int(v)) if v == int(v) else f"{v:g}")
    return out


def test_21e_etiket_sayilari_protokolde_var(app):
    """
    Protokol uyumu: görsel etiketlerindeki her sayı (süre, tekrar, mesafe) o testin protokol metninde geçer —
    yuvarlanmış ya da uydurulmuş sayı yok. 'Standart Yo-Yo IR1 protokolü' diyen testlerde standart metin de okunur;
    'FitnessGram → X ile aynı protokol' diyen testlerde (PYFP, CAPL) X'in metni de okunur.
    """
    protokol = {}
    for y, t in _testler(app["TEST_KATALOGU"]):   # aynı adlı testler (FitnessGram ve PYFP Modified Pull-Up): metinler birleşir
        protokol[_test_adi(y)] = protokol.get(_test_adi(y), "") + t.get("protokol", "")
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        metin = protokol.get(ad, "")
        if ad.startswith("Yo-Yo IR"):        # IR2 protokolü "IR1 ile aynı format" der: standart metinler de okunur
            metin += protokol.get("Yo-Yo IR1 (Genel)", "") + protokol.get("Yo-Yo IR2 (Genel)", "")
        for ref in re.findall(r"FitnessGram → (.+?) ile aynı protokol", metin):   # PYFP/CAPL: başvurulan metin de okunur
            metin += protokol.get(ref.strip(), "")
        izinli = _sayilar(metin)
        for k in app["tg_sahne"](ad).yazi_kutulari:
            fazla = _sayilar(k[4]) - izinli
            if fazla:
                sorunlar.append(f"{ad}: '{k[4]}' → protokolde yok: {sorted(fazla)}")
    assert not sorunlar, "Etiket protokolle çelişiyor:" + _ozet(sorunlar)


def test_21f_kitaplik_yetenekleri(app):
    """Yeni yetenekler genel çalışır: kavisli yol verilen noktalardan geçer (S ve köşe), paten öne eğik
    ve iten bacak geride, ikinci figür rol taşır, güreş atışında eller mankenin kalçasına temas eder."""
    import math as _m
    noktalar = [(20, 100), (60, 80), (100, 110), (140, 80)]
    for yumusak in (True, False):
        yol = app["hk_kavisli_yol"](noktalar, yumusak=yumusak).olay["yol"]
        for n in noktalar:
            assert min(_m.dist(n, y) for y in yol) < 0.5, (yumusak, n)
    kose = app["hk_kavisli_yol"]([(20, 100), (120, 100), (120, 60)], yumusak=False)
    assert len(kose.olay["yol"]) == 3
    pat = app["hk_paten"](30, 200).anahtarlar[-1][1]
    assert pat["g"] >= 30 and min(pat["u1"], pat["u2"]) <= -40, pat
    assert app["hk_ikinci_figur"](app["hk_tutus"](100)).olay["rol"] == "partner"
    el, kalca = app["hk_atma"](128, "suplex").olay["temas"]
    assert _m.dist(el, kalca) < 8, (el, kalca)


# ════════════════════════════════════════════════════════════
# 22. Yazı yerleşimi ve ölçü doğruluğu (Paket 16) — bütün sahnelere ve sonraki testlere genel kural
# ════════════════════════════════════════════════════════════
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


def test_22a_yazi_figur_ve_esyadan_uzak(app):
    """
    Hiçbir yazı, figürün (son kare) ya da eşyanın EN YAKIN ÇİZGİSİNE 6 birimden yakın değil (Paket 17).
    Sınır kutusuyla değil gerçek çizgiyle ölçülür: yere serilmiş figürün boş köşesine düşen yazı sahte hata vermez.
    """
    pay = app["TG_CIZGI_PAYI"]
    assert pay == 6
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        cizim = [g[1:] for g in S.cizim_sekilleri if g[0] in ("esya", "figur")]
        assert any(g[0] == "figur" for g in S.cizim_sekilleri), f"{ad}: figür çizgisi kaydı yok"
        for y in S.yazi_kutulari:
            en = min((( _yazi_cizgi_uzakligi(y, g), g[0]) for g in cizim), default=(99, ""))
            if en[0] < pay - 1e-6:
                sorunlar.append(f"{ad}: '{y[4]}' ↔ {en[1]} ({en[0]:.1f} birim)")
    assert not sorunlar, "Yazı çizgiye yakın:" + _ozet(sorunlar)


def test_22b_yazi_seritleri(app):
    """
    Üst şerit y ∈ [0, 16] yalnız başlık, alt şerit y ∈ [128, 140] yalnız not; ölçü/işaret etiketi çizim alanında
    ve tuval kenarından ≥ 4 birim içeride. Hiçbir çizim öğesi (eşya, ok, kılavuz, figürün bütün kareleri) şeritlere girmez.
    """
    ust, alt, pay = app["TG_SERIT_UST"], app["TG_SERIT_ALT"], app["TG_YAZI_PAYI"]
    w, h = app["TG_TUVAL"]
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        yerler = [k[6] for k in S.yazi_kutulari]
        if yerler.count("baslik") != 1 or yerler.count("not") > 1:
            sorunlar.append(f"{ad}: başlık/not sayısı {yerler}")
        for x0, y0, x1, y1, metin, _, yer in S.yazi_kutulari:
            aralik = {"baslik": (0, ust), "not": (alt, h)}.get(yer, (ust, alt))
            if not (aralik[0] <= y0 and y1 <= aralik[1]):
                sorunlar.append(f"{ad}: {yer} '{metin}' y {y0:.1f}–{y1:.1f} şeridin dışında")
            if x0 < pay or x1 > w - pay:
                sorunlar.append(f"{ad}: '{metin}' kenara {min(x0, w - x1):.1f} birim")
        for k in S.cizim_kutulari + [(*a, "figür (bütün kareler)") for a in S.figur_alani]:
            if k[1] < ust - 1e-6 or k[3] > alt + 1e-6:
                sorunlar.append(f"{ad}: {k[4]} şeride giriyor (y {k[1]:.1f}–{k[3]:.1f})")
    assert not sorunlar, "Şerit ihlali:" + _ozet(sorunlar)


def test_22c_satir_araligi(app):
    """Alt alta iki yazının (yatayda örtüşen) taban farkı ≥ 11 birim."""
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        K = app["tg_sahne"](ad).yazi_kutulari
        for i, a in enumerate(K):
            for b in K[i + 1:]:
                if a[0] < b[2] and b[0] < a[2] and abs(a[5] - b[5]) < app["TG_SATIR"]:
                    sorunlar.append(f"{ad}: '{a[4]}' / '{b[4]}' taban farkı {abs(a[5] - b[5]):.1f}")
    assert not sorunlar, _ozet(sorunlar)


def test_22d_etiket_buyuk_harfle_baslar(app):
    """
    Her etiket büyük harf, rakam ya da özel adla başlar (Türkçe: yalnız cümle başı ve özel adlar; birimler küçük).
    Büyük harfler metne elle yazılır: kaynakta dönüştürme işlevi yok (İngilizce kuralı 'i' → 'I' yapar).
    """
    sorunlar = []
    for ad in app["TEST_GORSELLERI"]:
        for k in app["tg_sahne"](ad).yazi_kutulari:
            m = k[4]
            if not (m[:1].isdigit() or (m[:1].isalpha() and m[:1] == m[:1].upper() and m[:1] != m[:1].lower())
                    or m.startswith(app["TG_OZEL_ADLAR"])):
                sorunlar.append(f"{ad}: '{m}'")
    assert not sorunlar, "Küçük harfle başlayan etiket:" + _ozet(sorunlar)


def test_22e_kaynakta_harf_donusturme_yok(kaynak):
    """.capitalize( .title( .upper( kaynakta geçmez (Türkçe i/İ kuralını bozar)."""
    bulunan = [y for y in (".capitalize(", ".title(", ".upper(") if y in kaynak]
    assert not bulunan, bulunan


def test_22f_olcu_oku_son_kareden(app):
    """
    Ölçü okunun gösterdiği değer, son karedeki ilgili eklemle ≤ 2 birim uyuşur (ör. dikey sıçrama: okun ucu
    tepedeki en alt ayak noktası; boy: başın tepesi; kulaç: el uçları). Bu sahnelerde bağlı ok zorunludur.
    """
    zorunlu = {"_tg_boy", "_tg_oturma", "_tg_kulac", "_tg_dikey", "_tg_goz_el"}
    sorunlar, bagli = [], set()
    for ad, fn in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        e = S.son_eklemler
        for o in S.olcu_kayit:
            for uc, eksen, eklemler, kural in o["bag"]:
                i = {"x": 0, "y": 1}[eksen]
                beklenen = (min if kural == "min" else max)(e[k][i] for k in eklemler)
                deger = o["uc"][2 * uc + i]
                bagli.add(fn)
                if abs(deger - beklenen) > 2:
                    sorunlar.append(f"{ad}: '{o['etiket']}' ucu {deger:.1f}, eklem {beklenen:.1f}")
    eksik = sorted(zorunlu - bagli)
    assert not sorunlar and not eksik, f"Ölçü oku eklemle uyuşmuyor: {_ozet(sorunlar)} · bağsız: {eksik}"


def test_22g_sureli_testlerde_zaman_seridi(app):
    """Süreli testler protokolün aralık yapısını tek şeritte gösterir (Paket 16: yaygınlaştırma)."""
    sureli = ["Yana Sıçrama (Jumping Sideways)", "Yana Platform Değiştirme (Moving Sideways)",
              "Göz-El Koordinasyonu (Duvara Atıp Yakalama)", "Special Wrestling Fitness Test (SWFT)",
              "Modified SJFT (Güreş için)", "Simulated Wrestling Match (6 dk)", "Wingate 30sn Bisiklet Testi"]
    sureli += [t for t in app["TEST_GORSELLERI"] if t.startswith(("Yo-Yo IR1 (", "Wingate"))]
    eksik = [t for t in sureli if t not in app["TEST_GORSELLERI"] or not app["tg_sahne"](t).zaman_seritleri]
    assert not eksik, eksik


def test_22h_swft_ve_sjft_ayrisir(app):
    """
    SWFT ile Modified SJFT aynı çizim değil: ölçülen şey (toplam atış sayacı ↔ periyot başına sayaç) ve figürün
    hareketi (suplex: geriye köprü ↔ öne devirme) farklı. Sayaç yedi bölmeli rakamdır, yazı öğesi değil.
    """
    sw = app["tg_sahne"]("Special Wrestling Fitness Test (SWFT)")
    sj = app["tg_sahne"]("Modified SJFT (Güreş için)")
    assert len(sw.sayaclar) == 1 and len(sj.sayaclar) == 3, (len(sw.sayaclar), len(sj.sayaclar))
    a, b = sw.son_eklemler, sj.son_eklemler
    # suplex sonu: gövde geriye gerili (baş kalçanın gerisinde değil, yukarıda); öne devirme: gövde öne eğik
    egim = lambda e: (e["boyun"][0] - e["kalca"][0], e["kalca"][1] - e["boyun"][1])
    (dx1, dy1), (dx2, dy2) = egim(a), egim(b)
    assert dy1 > 20 and dy2 < dy1 - 8, ("gövde eğimleri ayrışmıyor", egim(a), egim(b))
    assert sw.svg(False, "") != sj.svg(False, "")


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
        assert [b.label for b in at.main.button if b.key != "alt_hakkinda"
                and not (b.key or "").startswith("ust-menu-")] == ["İlk sporcuyu ekle"]
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
# 24. Branş görselleri 2. parti (Paket 17): Futbol, Voleybol, Basketbol, Hentbol, Atletizm
# ════════════════════════════════════════════════════════════
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


def test_24a_ikinci_parti_kapsami(app):
    """
    26 testin 25'i görselli; Atletik Güç Testi Bataryası dört ayrı hareket (CMJ, SJ, üçlü atlama, medisin topu)
    olduğu için tek sahneye sığmaz — görselsiz kalır. Halter dikey sıçrama ve Yo-Yo IR2 (Genel) de aynı sahnelerle.
    """
    g = app["TEST_GORSELLERI"]
    katalog = {_test_adi(y) for y, _ in _testler(app["TEST_KATALOGU"])}
    assert len(_P17_TESTLER) == 26 and all(t in katalog for t in _P17_TESTLER)
    eksik = [t for t in _P17_TESTLER if t not in g and t != "Atletik Güç Testi Bataryası"]
    assert not eksik, eksik
    assert "Atletik Güç Testi Bataryası" not in g
    assert "Dikey Sıçrama ve CMJ (Halter)" in g and "Yo-Yo IR2 (Genel)" in g


def test_24b_test_ara_turkce_i(app):
    """Test ara: İngilizce klavyede büyük I ile yazılan Türkçe İ'yi bulur (ve tersi)."""
    ara = app["test_ara"]
    hedef = "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)"
    for sorgu in ("IZOMETRIK", "İZOMETRİK", "izometrik", "Izometrik"):
        assert any(t["ad"] == hedef for t in ara(sorgu)), sorgu
    for sorgu in ("ILLINOIS", "İLLİNOİS", "illinois"):
        assert any(t["ad"] == "Illinois Çeviklik Testi" for t in ara(sorgu)), sorgu


def test_24c_yoyo_ir2_farki_yalniz_etikette(app):
    """Yo-Yo IR2 aynı sahne; fark yalnız notta (başlangıç hızı 13 km/h, protokoldeki 10 sn dinlenme)."""
    def notsuz(t):
        return re.sub(r"<text[^>]*>[^<]*</text>", "", app["tg_sahne"](t).svg(False, ""))
    assert notsuz("Yo-Yo IR2 (Futbol)") == notsuz("Yo-Yo IR1 (Futbol)")
    ir2 = [k[4] for k in app["tg_sahne"]("Yo-Yo IR2 (Futbol)").yazi_kutulari if k[6] == "not"][0]
    ir1 = [k[4] for k in app["tg_sahne"]("Yo-Yo IR1 (Futbol)").yazi_kutulari if k[6] == "not"][0]
    assert "13 km/h" in ir2 and "10 sn" in ir2 and ir1 != ir2


def test_24d_zaman_seridi_yaygin(app):
    """Süresi ya da tekrar yapısı olan her testte zaman çubuğu: RSA, LIST, 30-15 IFT, bütün Yo-Yo'lar, Wingate, sprintler."""
    g = app["TEST_GORSELLERI"]
    gerekli = [t for t in g if t.startswith(("Yo-Yo", "Wingate"))] + [
        "RSA Testi (Repeated Sprint Ability)", "Loughborough İntermittent Shuttle Test (LIST)",
        "30-15 İntermittent Fitness Test (30-15 IFT)", "Sprint Hızlanma Profili (10-20-30m)",
        "10m Sprint", "20m Sprint", "100m Sprint", "200m Sprint", "400m Sprint", "NBA 3/4 Saha Sprint Testi",
        "20m Sprint - Voleybol"]
    eksik = [t for t in gerekli if not app["tg_sahne"](t).zaman_seritleri]
    assert not eksik, eksik
    # 30-15 IFT: koşu blokları aşama aşama yükselir (artımlı hız); Yo-Yo'da koşu blokları kısalır
    svg = app["tg_sahne"]("30-15 İntermittent Fitness Test (30-15 IFT)").svg(False, "")
    dolu = app["TG_RENK"]["olcu"]
    yuk = [float(h) for h in re.findall(rf'<rect x="[\d.]+" y="[\d.]+" width="18\.0" height="([\d.]+)" rx="1" fill="{re.escape(dolu)}"', svg)]
    assert len(yuk) == 5 and yuk == sorted(yuk) and yuk[0] < yuk[-1], yuk


def test_24e_cmj_sj_dj_ayrisir(app):
    """
    Paket 18: durağan kare her varyantın AYIRT EDİCİ ANI — CMJ ön-çömelmenin dibi (SJ'nin 90°'sinden derin),
    SJ 90° statik çömelme (başta da sonda da aynı yükseklikte, ön-çömelme yok), DJ kutudan düşüş (havada, kutunun
    önünde, kutu üstü ile zemin arası). Eller kalçada. Sahnede varyant sayısı kadar figür, iz yok; başlıktaki
    varyant sayısı figür sayısına eşit.
    """
    import math as _m
    a = app["hk_sicrama_ani"]
    e = app["tg_eklemler"]

    def diz_acisi(p):
        q = e(p)
        u = _m.atan2(q["kalca"][0] - q["diz1"][0], q["kalca"][1] - q["diz1"][1])
        b = _m.atan2(q["ayak1"][0] - q["diz1"][0], q["ayak1"][1] - q["diz1"][1])
        return abs(_m.degrees(u - b)) % 360
    cmj, sj = a(80, "cmj", s=0.7), a(80, "sj", s=0.7)
    dj = a(175, "dj", s=0.7, kutu=(162, 186, 10.7))
    assert diz_acisi(cmj.anahtarlar[-1][1]) < diz_acisi(sj.anahtarlar[-1][1]) - 15, "CMJ dibi SJ'den derin değil"
    assert abs(diz_acisi(sj.anahtarlar[-1][1]) - 90) < 6, "SJ 90° değil"
    assert abs(sj.anahtarlar[0][1]["hy"] - sj.anahtarlar[-1][1]["hy"]) < 0.5, "SJ'de ön-çömelme var"
    assert e(cmj.anahtarlar[0][1])["diz1"][1] - e(cmj.anahtarlar[0][1])["kalca"][1] > 12, "CMJ ayakta başlamıyor"
    son = e(dj.anahtarlar[-1][1])
    ayak = max(son["ayak1"][1], son["ayak2"][1], son["parmak1"][1], son["parmak2"][1])
    assert app["TG_ZEMIN"] - 10.7 < ayak < app["TG_ZEMIN"] - 1 and min(son["ayak1"][0], son["ayak2"][0]) > 186, "DJ düşüş anı değil"
    for h in (cmj, sj, dj):
        q = e(h.anahtarlar[-1][1])
        assert _m.dist(q["el1"], q["kalca"]) < 10, "eller kalçada değil"
    for ad in [t_ for t_ in app["TEST_GORSELLERI"] if t_.startswith("Dikey Sıçrama") and "TSYT" not in t_
               and "Suda" not in t_]:                              # suda sıçrama ayrı test (Paket 24)
        S = app["tg_sahne"](ad)
        baslik = [k[4] for k in S.yazi_kutulari if k[6] == "baslik"][0]
        varyant = sum(v in baslik for v in ("CMJ", "SJ", "DJ"))
        roller = [f["rol"] for f in S.figurler]
        assert roller.count("olculen") == varyant == len(roller), (ad, varyant, roller)


def test_24f_nordic_ve_dinamometre(app):
    """Nordic: diz her karede aynı noktada, gövde öne iner; dinamometre: kol ucu kavalı izler, 90° → 45° biter."""
    import math as _m
    e = app["tg_eklemler"]
    h = app["hk_nordic"](124, 108, s=0.9)
    dizler = [e(p)["diz1"] for _, p in h.anahtarlar]
    assert all(_m.dist(d, dizler[0]) < 0.6 for d in dizler), "diz sabit değil"
    assert h.anahtarlar[0][1]["g"] == 0 and h.anahtarlar[-1][1]["g"] >= 45
    d = app["hk_dinamometre"](96, 72)
    assert d.anahtarlar[0][1]["b1"] == 0 and d.anahtarlar[-1][1]["b1"] == 45
    son = e(d.anahtarlar[-1][1])["ayak1"]
    assert _m.dist(d.olay["ayak_yolu"][-1][1:], son) < 0.6 and _m.dist(d.olay["diz"], e(d.anahtarlar[-1][1])["diz1"]) < 0.6
    assert re.search(r'<line [^>]*><animate attributeName="x2"', app["tg_sahne"](
        "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)").svg(True, ""))


# ════════════════════════════════════════════════════════════
# 25. Paket 18: görsel kodlar, yandan görünüşte parkur, mücadele sporları (3. parti)
# ════════════════════════════════════════════════════════════
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


def test_25a_ucuncu_parti_kapsami(app):
    """25 testin 23'ü görselli; JPFT ve MMA Fiziksel Uygunluk Bataryası çok bileşenli bataryadır — görselsiz."""
    g = app["TEST_GORSELLERI"]
    katalog = {_test_adi(y) for y, _ in _testler(app["TEST_KATALOGU"])}
    assert len(_P18_TESTLER) == 25 and all(t in katalog for t in _P18_TESTLER)
    eksik = [t for t in _P18_TESTLER if t not in g and t not in _P18_BATARYA]
    assert not eksik and not [t for t in _P18_BATARYA if t in g], eksik
    assert "Masa Tenisi Reaksiyon ve Çeviklik Testi" in g


def test_25b_figur_katmani_gorsel_sistemde(kaynak, app):
    """Katman kuralı GÖRSEL SİSTEM bloğunda tanımlı; her figür rolü bir katmana bağlı."""
    satir = kaynak.split("\n")
    son = next(i for i, l in enumerate(satir) if l.startswith("def tasarimi_uygula"))
    tanim = [i for i, l in enumerate(satir) if l.startswith(("FIGUR_KATMANI", "FIGUR_DERINLIK_OPAKLIK"))]
    assert len(tanim) == 2 and all(i < son for i in tanim), tanim
    assert set(app["TG_ROL_KATMANI"].values()) == set(app["FIGUR_KATMANI"])


def test_25c_parkur_yandan_gorunus(app):
    """
    Perspektif saha yok (Paket 18): iki boyutlu güzergâhlar yandan görünüşte, zemin çizgisinin hemen gerisindeki
    ince şeritte (≤ 16 birim); sahada eğik (paralelkenar) kenar çizilmez.
    """
    assert "_tg_saha" not in app
    for ad in ["Illinois Çeviklik Testi", "Voleybol Çeviklik Testi (VAT)", "NBA Lane Agility Testi",
               "Hentbol Çeviklik ve Sprint Testi", "Karate Çeviklik Testi (KAT)", "Taekwondo Çeviklik ve Hız Testi"]:
        svg = app["tg_sahne"](ad).svg(False, "")
        yol = re.findall(r'<path d="([^"]+)"[^>]*stroke-dasharray="3 2"', svg)
        assert yol, ad
        ys = [float(y) for d in yol for _, y in re.findall(r"(-?[\d.]+),(-?[\d.]+)", d)]
        assert min(ys) >= app["TG_ZEMIN"] - 16 and max(ys) <= app["TG_ZEMIN"], (ad, min(ys), max(ys))


def test_25d_vurus_parametreleri(app):
    """Tekme protokolleri tek çizim: teknik dizisi, hedef (torba var/yok) ve tempo (şerit) parametreyle ayrışır."""
    v = app["hk_vurus"]
    e = app["tg_eklemler"]
    dollyo = e(v(150, ["dollyo"], s=0.75).anahtarlar[-1][1])
    rh = e(v(150, ["roundhouse"], s=0.75).anahtarlar[-1][1])
    cross = e(v(150, ["cross"], s=0.75).anahtarlar[-1][1])
    assert dollyo["ayak2"][1] < rh["ayak2"][1] - 8, "dollyo yüksek, roundhouse orta değil"
    assert max(cross["ayak1"][1], cross["ayak2"][1]) > app["TG_ZEMIN"] - 2 and cross["el2"][0] > cross["boyun"][0] + 15
    torbali = {"Muay Thai Spesifik Dayanıklılık Testi (MTSDT)", "Kickboks Spesifik Kondisyon Testi (KSKT)",
               "Boks Spesifik Dayanıklılık Testi"}
    serit = set()
    for ad in torbali | {"Taekwondo Spesifik Aerobik Test (TSAT)", "Karate Spesifik Dayanıklılık Testi (KSDT)"}:
        S = app["tg_sahne"](ad)
        torba = bool(re.search(r'<rect [^>]*width="14\.0" height="66\.0"', S.svg(False, "")))
        assert torba == (ad in torbali), ad
        assert len(S.sayaclar) == 1 and S.zaman_seritleri, ad
        serit.add(re.sub(r"<(?!rect)[^>]*>", "", S.svg(False, "")).count("<rect"))
    assert len(serit) >= 3, "tempo (şerit) branşlar arasında ayrışmıyor"


def test_25e_judo_ve_kavrama(app):
    """
    Judo SJFT: iki uke (ikinci kişi), üç periyotta birer atış, periyot sayaçları. UKFT: atış yok — uke ayakta
    kalır, son kare giriş anı. Kavrama: sporcu asılı (ayaklar yerden kesik), süre kronometre simgesiyle (Paket 19).
    """
    S = app["tg_sahne"]("Special Judo Fitness Test (SJFT)")
    roller = [f["rol"] for f in S.figurler]
    assert roller.count("partner") == 2 and roller.count("olculen") == 1 and len(S.sayaclar) == 3
    e = app["tg_eklemler"]
    u = app["hk_uchikomi"](140, s=0.8)
    uke = e(u.olay["partner"].anahtarlar[-1][1])
    assert uke["bas"][1] < uke["kalca"][1] - 20, "UKFT'de uke devrilmiş"
    assert u.anahtarlar[-1][1].get("yon", 1) == -1, "UKFT son kare giriş değil"
    a = app["hk_asilma"](110, 34, s=0.75)
    son = e(a.anahtarlar[-1][1])
    assert max(son["ayak1"][1], son["ayak2"][1], son["parmak1"][1], son["parmak2"][1]) < app["TG_ZEMIN"] - 6
    assert abs(son["el1"][1] - 34) < 1
    K = app["tg_sahne"]("BJJ Kavrama Kuvveti ve Dayanıklılığı")
    assert K.kronometreler and not K.sayaclar, "süre ölçümü kronometre simgesiyle gösterilmeli (Paket 19)"


def test_25f_mesafe_oku_zeminde(app):
    """RSA ve 30-15 IFT'de mesafe oku havada değil, zemin şeridinde (TG_OLCU_Y)."""
    for ad in ("RSA Testi (Repeated Sprint Ability)", "30-15 İntermittent Fitness Test (30-15 IFT)"):
        oklar = [o for o in app["tg_sahne"](ad).olcu_kayit if o["metre"]]
        assert oklar and all(o["uc"][1] == o["uc"][3] == app["TG_OLCU_Y"] for o in oklar), ad


# ════════════════════════════════════════════════════════════
# Yükleyici sağlığı: denetimin kendisi eksik çalışmasın
# ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
# 26. Dördüncü parti: çocuk ve genç bataryaları, tek sayaç, numaralı parkur (Paket 19)
# ════════════════════════════════════════════════════════════
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


def test_26a_dorduncu_parti_kapsami(app):
    """Paket 19: çocuk ve genç bataryalarından 56 test + Ghost Drill görselli; vücut kompozisyonu, adım sayısı ve anket
    (8 test) bir hareket değil, ölçüm ya da form — görselsiz."""
    g = app["TEST_GORSELLERI"]
    katalog = {_test_adi(y) for y, _ in _testler(app["TEST_KATALOGU"])}
    assert len(_P19_TESTLER) == 57 and len(_P19_GORSELSIZ) == 8
    assert all(t in katalog for t in _P19_TESTLER + _P19_GORSELSIZ), [t for t in _P19_TESTLER + _P19_GORSELSIZ if t not in katalog]
    assert not [t for t in _P19_TESTLER if t not in g] and not [t for t in _P19_GORSELSIZ if t in g]


def test_26b_sayac_tek_bicim(app, kaynak):
    """Sayaç tek biçim: çetele (çizgi), rakam yok; süre ölçümü kronometre simgesi. Hiçbir sahne sayaçta değer göstermez."""
    assert "basamak" not in kaynak.split("def sayac(")[1].split("def kronometre(")[0]
    for ad in app["TEST_GORSELLERI"]:
        S = app["tg_sahne"](ad)
        for x0, y0, x1, y1 in S.sayaclar:
            assert not [k for k in S.yazi_kutulari if k[0] < x1 and k[2] > x0 and k[1] < y1 and k[3] > y0], ad
    K = app["tg_sahne"]("Asılı Durma - Bükümlü Kol (Bent Arm Hang)")
    assert K.kronometreler and not K.sayaclar
    F = app["tg_sahne"]("Flamingo Denge Testi")
    assert len(F.sayaclar) == 1


def test_26c_tekme_hedefi_yuksekligi(app):
    """TSAT ve KSDT'de ayaklı ped var; yüksekliği son tekniğin erişiminden — TSAT (dollyo: baş) KSDT'den (geri: gövde) yüksek."""
    t = [h for h in app["tg_sahne"]("Taekwondo Spesifik Aerobik Test (TSAT)").hedefler if h[0] == "ped"]
    k = [h for h in app["tg_sahne"]("Karate Spesifik Dayanıklılık Testi (KSDT)").hedefler if h[0] == "ped"]
    assert t and k and t[0][2] < k[0][2] - 5, (t, k)


def test_26d_parkur_donus_numaralari(app):
    """Çok dönüşlü parkurlarda dönüş noktaları 1..n sırayla numaralı (Paket 19); n parkur tanımındaki dönüş sayısı."""
    beklenen = {"Illinois Çeviklik Testi": 5, "Hentbol Çeviklik ve Sprint Testi": 5, "Voleybol Çeviklik Testi (VAT)": 4,
                "NBA Lane Agility Testi": 4, "Karate Çeviklik Testi (KAT)": 4, "Ghost Drill (Squash Çeviklik Testi)": 6,
                "T-Testi (Çeviklik)": 4, "Spider Test (Tenis Çeviklik Testi)": 5}
    for ad, n in beklenen.items():
        S = app["tg_sahne"](ad)
        assert [k[0] for k in S.numaralar] == list(range(1, n + 1)), (ad, S.numaralar)
        assert all(app["TG_SERIT_UST"] < k[2] < app["TG_SERIT_ALT"] for k in S.numaralar), ad
    assert [k[0] for k in app["tg_sahne"]("CAPL Engel Parkuru (Motor Beceri)").numaralar] == list(range(1, 8))   # CAMSA (Paket 22)


def test_26e_back_saver_tek_bacak(app):
    """Back-Saver: yakın bacak düz ve kutuda, uzak bacak dizden bükülü ve ayak tabanı yerde; Eurofit'te iki bacak düz."""
    import math as _m
    for ad, tek in (("Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)", True), ("Otur-Uzan (Sit and Reach) Testi", False)):
        e = app["tg_sahne"](ad).son_eklemler
        aci = lambda k, d, a: _m.degrees(_m.atan2(*(_m.dist(e[k], e[d]), 1))) if False else (
            _m.dist(e[k], e[a]) / (_m.dist(e[k], e[d]) + _m.dist(e[d], e[a])))
        assert aci("kalca", "diz1", "ayak1") > 0.99, ad              # yakın bacak düz
        if tek:
            assert aci("kalca", "diz2", "ayak2") < 0.85, "uzak diz bükük değil"
            assert abs(max(e["ayak2"][1], e["parmak2"][1]) - app["TG_ZEMIN"]) < 1.5, "uzak ayak yerde değil"
        else:
            assert aci("kalca", "diz2", "ayak2") > 0.99


def test_26f_esneklik_sifir_noktasi_protokolden(app):
    """Her otur-uzan varyantında sıfır ile ayak tabanı arası ok, varyantın KENDİ protokol değerinde ve ölçekle tutarlı:
    Eurofit 15 cm, FitnessGram / PYFP / ALPHA Back-Saver 22,9 cm; CNPFM'de ok yok, sıfır ayak tabanında işaretli."""
    m = app["TG_OLCEK"]["_tg_otur_uzan"][0]
    beklenen = {"Otur-Uzan (Sit and Reach) Testi": 0.15, "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)": 0.229,
                "Back-Saver Sit and Reach": 0.229, "Back-Saver Sit and Reach (ALPHA)": 0.229, "Otur-Uzan Testi (CNPFM)": None}
    for ad, metre in beklenen.items():
        S = app["tg_sahne"](ad)
        oklar = [o for o in S.olcu_kayit if o["metre"]]
        if metre is None:
            assert not oklar and any("Sıfır" in k[4] for k in S.yazi_kutulari), ad
            continue
        assert len(oklar) == 1 and abs(oklar[0]["metre"] - metre) < 1e-9, (ad, oklar)
        x1, _, x2, _ = oklar[0]["uc"]
        assert abs(abs(x2 - x1) - metre * m) < 0.5, ad
        assert f"{metre * 100:g}".replace(".", ",") in oklar[0]["etiket"], ad
    assert app["TEST_GORSELLERI"]["Esneklik (Uzan Eriş) — TSYT"][0] is app["_tg_esneklik"], "TSYT varsayılan kabul edilmemeli"


def test_26g_uygunluk_hareketleri(app):
    """Yeni hareketler: uzun atlamada ok topuğa; şınavda eller ve destek yerde; curl-up'ta parmaklar ileri kayar;
    flamingo denge kaybında serbest ayak yere değer; top yakalamada top çocuğun elinde biter."""
    import math as _m
    e = app["tg_eklemler"]; Z = app["TG_ZEMIN"]
    u = app["hk_uzun_atlama"](60, 90, s=0.8)
    son = e(u.anahtarlar[-1][1])
    assert abs(min(son["ayak1"][0], son["ayak2"][0]) - u.olay["topuk_x"]) < 1
    for diz in (False, True):
        p = e(app["hk_sinav"](130, s=0.8, diz=diz).anahtarlar[-1][1])
        assert abs(max(p["el1"][1], p["el2"][1]) - Z) < 1.5
        destek = ("diz1",) if diz else ("parmak1", "parmak2")
        assert abs(max(p[k][1] for k in destek) - Z) < 1.5, diz
    yol = app["hk_mekik"](130, "curlup", s=0.8).olay["el_yolu"]
    assert yol[1][0] - yol[0][0] > 1.5          # şerit 4,5 / 11,5 cm: figür ölçeğinde birkaç birim
    f = app["hk_flamingo"](130, s=0.8)
    an = dict(f.anahtarlar)
    kayip = e(an[f.olay["kayip_t"]])
    assert abs(max(kayip["ayak2"][1], kayip["parmak2"][1]) - Z) < 1.5
    t = app["hk_top_yakala"](90, 170)
    c = e(t.anahtarlar[-1][1])
    assert _m.dist(t.olay["top_yolu"][-1][1:], c["el1"]) < 1 and t.olay["atan"].olay["rol"] == "partner"


# ════════════════════════════════════════════════════════════
# 27. Animasyon zamanlaması ve FitnessGram HFZ (Paket 20)
# ════════════════════════════════════════════════════════════
def _figur_keytimes(app, ad):
    """Sahnenin figür yolu (d) animasyonlarının keyTimes listeleri."""
    svg = app["tg_sahne"](ad).svg(True, ad)
    return [[float(x) for x in kt.split(";")]
            for kt in re.findall(r'<animate attributeName="d" values="[^"]*" keyTimes="([^"]+)"', svg)]


def test_27a_animasyon_zamani_bastan_baslar(app):
    """
    Figürün d animasyonu zamanın başından başlar ve karelere yayılır: keyTimes ilk değeri ≤ 0,02, karelerin en az
    %40'ı ilk yarıda (≤ 0,5). Paket 20'ye dek çok ayaklı koşularda bütün kareler son ayağın penceresine yığılıyordu
    (10x5 m: keyTimes 0,9'da başlıyordu); durağan kopya doğru olduğu için başka hiçbir denetim görmedi.
    """
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        listeler = _figur_keytimes(app, ad)
        assert listeler, f"{ad}: figür animasyonu yok"
        for t in listeler:
            ilk_yari = sum(x <= 0.5 for x in t) / len(t)
            if t[0] > 0.02 or ilk_yari < 0.4:
                sorunlar.append(f"{ad}: keyTimes {t[0]:.3f}'te başlıyor, ilk yarıda %{100 * ilk_yari:.0f}")
                break
    assert not sorunlar, "Animasyon zamanı yığılmış:" + _ozet(sorunlar)


def test_27b_donuslu_kos_zaman_penceresi(app):
    """hk_donuslu_kos: her ayak kendi aralığında; bütün hareket verilen [t0, t1] penceresini kaplar."""
    for duraklar in ([30, 200, 34], [30, 200] * 5 + [34]):
        an = [t for t, _ in app["hk_donuslu_kos"](duraklar, dokun=True).anahtarlar]
        assert an[0] <= 0.02 and abs(an[-1] - 1.0) < 1e-9 and an == sorted(an), (len(duraklar), an[:3])
        ayak = len(duraklar) - 1
        assert sum(t <= 1 / ayak for t in an) >= 2, "ilk ayak kendi penceresinde değil"
    an = [t for t, _ in app["hk_donuslu_kos"]([30, 200, 34], t0=0.2, t1=0.6).anahtarlar]
    assert abs(an[0] - 0.2) < 0.02 and abs(an[-1] - 0.6) < 1e-9


_HFZ_BOLUMU = re.compile(r"^\*\*HFZ[^\n]*\n(?:- [^\n]*\n?)*", re.M)


def _hfz_bolumleri(metin):
    """Protokoldeki HFZ başlıklı bölümler (başlık satırı + altındaki madde satırları)."""
    return [m.group(0) for m in _HFZ_BOLUMU.finditer(metin)]


def test_27c_hfz_protokol_ve_norm_tek_kaynak(app):
    """
    HFZ eşiği olan her testte protokol metni ile normatif girdi aynı şeyi söyler (Paket 20):
    - protokolde sayılı bir HFZ bölümü varsa o testin NORMATIF_ESIK_YAS girdisi vardır;
    - bölüm tablodan üretilen metnin aynısıdır (sayı, birim, yaş grupları);
    - tablo yaşa göre değişiyorsa metin yaş gruplarını verir; tek bant yazılmışsa test düşer.
    Sayısız not ("eşik girilmedi") serbesttir.
    """
    esik = app["NORMATIF_ESIK_YAS"]
    esikli_testler = {k.split(" › ")[0] for k in esik}
    sorunlar = []
    for yol, t in _testler(app["TEST_KATALOGU"]):
        ad = _test_adi(yol)
        bolumler = [b for b in _hfz_bolumleri(t.get("protokol", "")) if re.search(r"\d", b)]
        if not bolumler and ad not in esikli_testler:
            continue
        if ad not in esikli_testler:
            sorunlar.append(f"{ad}: protokolde sayılı HFZ var, NORMATIF_ESIK_YAS'ta yok → {bolumler[0][:60]!r}")
            continue
        beklenen = app["hfz_metni"](ad).strip()
        if [b.strip() for b in bolumler] != [beklenen]:
            sorunlar.append(f"{ad}: protokoldeki HFZ tablodan farklı → {[b[:80] for b in bolumler]}")
        for k, n in esik.items():
            if k.split(" › ")[0] != ad:
                continue
            for cins in ("Erkek", "Kadın"):
                degerler = {n["yaslar"][y][cins] for y in n["yaslar"]}
                if len(degerler) > 1 and beklenen.count("yaş") < 2:
                    sorunlar.append(f"{ad}: eşik yaşa göre değişiyor, metin yaş ayırmıyor")
    assert not sorunlar, "HFZ protokol–norm çelişkisi:" + _ozet(sorunlar)


def test_27d_fitnessgram_hfz_degerleri(app):
    """
    FitnessGram HFZ (Cooper Institute tabloları) — bilinen hücreler. Trunk Lift: 5-9 yaş 6-12 inç (15,2-30,5 cm),
    10+ 9-12 inç (22,9-30,5 cm), iki cinsiyet aynı. Ölçüm yerden ÇENEYE (göz hizasındaki işaret ölçüm noktası değil).
    """
    f = app["esik_degerlendir"]
    TL, CU, PU, MP = ("Trunk Lift (Gövde Kaldırma) Testi", "Curl-Up (Kademeli Mekik) Testi",
                      "Push-Up (Şınav) Testi", "Modified Pull-Up Testi")
    BS = "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)"
    beklenen = [(TL, "En İyi Kaldırma (cm)", 7, "Erkek", (15.2, 30.5)), (TL, "En İyi Kaldırma (cm)", 9, "Kadın", (15.2, 30.5)),
                (TL, "En İyi Kaldırma (cm)", 10, "Kadın", (22.9, 30.5)), (TL, "En İyi Kaldırma (cm)", 17, "Erkek", (22.9, 30.5)),
                (CU, "Tekrar Sayısı", 7, "Erkek", (4, None)), (CU, "Tekrar Sayısı", 13, "Erkek", (21, None)),
                (CU, "Tekrar Sayısı", 13, "Kadın", (18, None)), (PU, "Tekrar Sayısı", 11, "Erkek", (8, None)),
                (PU, "Tekrar Sayısı", 11, "Kadın", (7, None)), (MP, "Tekrar Sayısı", 17, "Erkek", (14, None)),
                (MP, "Tekrar Sayısı", 9, "Kadın", (4, None)), (BS, "Sağ Bacak - En İyi (cm)", 10, "Kadın", (22.9, None)),
                (BS, "Sol Bacak - En İyi (cm)", 11, "Kadın", (25.4, None)), (BS, "Sağ Bacak - En İyi (cm)", 15, "Kadın", (30.5, None)),
                (BS, "Sağ Bacak - En İyi (cm)", 9, "Erkek", (20.3, None))]
    for test, deg, yas, cins, esik in beklenen:
        r = f(test, deg, 0, yas, cins)
        assert r and r["esik"] == esik, (test, yas, cins, r and r["esik"])
    assert f(TL, "En İyi Kaldırma (cm)", 20, 8, "Erkek")["kategori"] == "Sağlıklı Uygunluk Zonu"
    assert f(TL, "En İyi Kaldırma (cm)", 20, 10, "Erkek")["kategori"] == "Gelişim Gerekli"
    p = [t for y, t in _testler(app["TEST_KATALOGU"]) if _test_adi(y) == TL][0]["protokol"].lower()
    assert "çeneye" in p and "gözbebeğine" not in p, "Trunk Lift ölçüm noktası çene olmalı"
    S = app["tg_sahne"](TL)
    assert any(("cene",) == b[2] for o in S.olcu_kayit for b in o["bag"]), "Trunk Lift oku çeneye bağlı değil"
    assert all("göz" not in k[4].lower() for k in S.yazi_kutulari)
    h = app["hk_modifiye_barfiks"](206, s=0.85)          # Modified Pull-Up: çene bardan 7-8 inç aşağıdaki bandın üstünde
    bant_y = h.olay["bar"][1] + 0.19 * app["TG_OLCEK"]["_tg_modifiye_barfiks"][0]
    assert app["tg_eklemler"](h.anahtarlar[-1][1])["cene"][1] < bant_y, "çene elastik bandın üstüne çıkmıyor"


def test_27e_tek_bantli_fitnessgram_normu_yok(app):
    """FitnessGram/Cooper kaynaklı tek bantlı (yaşsız) norm kalmadı; yetişkin VO2max bantları çocuk testlerine uygulanmaz."""
    for sozluk in ("NORMATIF", "NORMATIF_TEST"):
        tek = [k for k, n in app[sozluk].items() if re.search(r"FitnessGram|Cooper Institute", str(n.get("kaynak", "")))]
        assert not tek, f"{sozluk}: {tek}"
    kapsam = app["NORMATIF_KAPSAM"]["VO2max Tahmini (ml/kg/min)"]
    for t in ("PACER (20m Mekik Koşusu)", "1 Mil Yürüyüş/Koşu Testi", "20m Mekik Koşusu (ALPHA)", "PACER Testi"):
        assert not kapsam(t), t
    assert kapsam("Yo-Yo IR1 (Futbol)")


def test_27f_esik_tavani_basarisizlik_degil(app):
    """
    Eşik normunda üst sınır ölçümün TAVANIDIR (Trunk Lift 12 inç = 30,5 cm), başarısızlık eşiği değil: tavanın
    üstündeki değer tavana kırpılır ve tavandaki değerle aynı kategoriyi alır. Tavanı olan bütün eşik normlarına,
    her yaş ve cinsiyette uygulanır.
    """
    f, sorunlar = app["esik_degerlendir"], []
    for anahtar, norm in app["NORMATIF_ESIK_YAS"].items():
        test, deg = anahtar.split(" › ")
        for yas in norm["yaslar"]:
            for cins in ("Erkek", "Kadın"):
                alt, tavan = f(test, deg, 0, yas, cins)["esik"]
                if tavan is None:
                    continue
                k_tavan = f(test, deg, tavan, yas, cins)["kategori"]
                for ustu in (tavan + 0.1, tavan + 2.5, tavan * 2):
                    if f(test, deg, ustu, yas, cins)["kategori"] != k_tavan:
                        sorunlar.append(f"{anahtar}, {yas} yaş {cins}: {ustu:g} → tavandaki ({tavan:g}) ile farklı")
    assert not sorunlar, "Tavan başarısızlık eşiği gibi davranıyor:" + _ozet(sorunlar)
    TL = ("Trunk Lift (Gövde Kaldırma) Testi", "En İyi Kaldırma (cm)")
    for deger in (30.5, 31, 33):
        assert f(*TL, deger, 10, "Erkek")["kategori"] == "Sağlıklı Uygunluk Zonu", deger


# ════════════════════════════════════════════════════════════
# 28. Koordinasyon Parkuru — kayan sahne (Paket 21)
# ════════════════════════════════════════════════════════════
_KOORD = "Koordinasyon Parkuru (TSYT)"
_CAMSA = "CAPL Engel Parkuru (Motor Beceri)"


def test_28a_koordinasyon_sirasi_protokolden(app):
    """Turdaki dokuz istasyon, protokolün 2-10. adımlarıyla aynı adlar ve aynı sırada; numara rozetleri 1-9 sırayla."""
    p = [t for y, t in _testler(app["TEST_KATALOGU"]) if _test_adi(y) == _KOORD][0]["protokol"]
    adimlar = re.findall(r"^(\d+)\. \*\*([^*:]+):\*\*", p, re.M)
    protokol = [ad.strip() for no, ad in adimlar if 2 <= int(no) <= 10]
    assert len(protokol) == 9, protokol
    h = app["hk_koordinasyon_turu"]()
    assert list(h.olay["istasyon_adlari"]) == protokol == list(app["KOORDINASYON_ISTASYONLARI"])
    zaman = h.olay["istasyonlar"]
    assert [n for n, _, _ in zaman] == list(range(1, 10))
    assert all(a < b <= c for (_, a, b), (_, c, _) in zip(zaman, zaman[1:])), "istasyon aralıkları sıralı değil"
    S = app["tg_sahne"](_KOORD)
    assert [n for n, _, _ in S.numaralar] == list(range(1, 10))
    assert [n for n, _, _ in S.duragan.numaralar] == list(range(1, 10))


def test_28b_kayan_sahne_ve_sabit_katman(app):
    """
    Parkur tuvalden geniş ve bir grup olarak kayar; yazılar, numara ve süreölçer sabit katmanda (kayan grubun içinde
    yazı yok). Kayan grup tuvalin her yerinden geçebileceği için her kayan kutu her yazıdan dikeyde ≥ 6 birim uzak.
    Figür tuvalin ortasına yakın kalır. Durağan kopya BİLEREK ayrı kompozisyon (genel görünüm).
    """
    S = app["tg_sahne"](_KOORD)
    assert S.kayan_kutular and max(k[2] for k in S.kayan_kutular) - min(k[0] for k in S.kayan_kutular) > 3 * app["TG_TUVAL"][0]
    svg = S.svg(True, "")
    for grup in re.findall(r'<g transform="translate\([^)]*\)"><animateTransform[^>]*type="translate".*?</g>', svg, re.S):
        assert "<text" not in grup, "yazı kayan grubun içinde"
    pay = app["TG_CIZGI_PAYI"]
    for y in S.yazi_kutulari:
        for k in S.kayan_kutular:
            assert max(k[1] - y[3], y[1] - k[3]) >= pay, (y[4], k)
    xs = [e["kalca"][0] for e in S.tum_eklemler]
    assert max(xs) - min(xs) < 1 and 80 < xs[0] < 180, "figür sabit değil"
    assert S.duragan is not None and S.svg(False, "") == S.duragan.svg(False, "")
    assert S.svg(False, "") != re.sub(r"<animate[^>]*/>", "", svg), "durağan kopya genel görünüm olmalı"
    assert S.sure >= 8, S.sure      # süre hız sınırından çıkar (Paket 22, test_29b)


def test_28c_genel_gorunum_yerlesim_kurallari(app):
    """Durağan genel görünüm de bütün yerleşim kurallarından geçer (yazı çakışması, şerit, çizgi payı, satır)."""
    yerine = dict(app)
    yerine["tg_sahne"] = lambda ad: app["tg_sahne"](ad).duragan
    yerine["TEST_GORSELLERI"] = {ad: app["TEST_GORSELLERI"][ad] for ad in (_KOORD, _CAMSA)}
    for test in (test_21b_yazi_cakismasi_yok, test_22a_yazi_figur_ve_esyadan_uzak, test_22b_yazi_seritleri,
                 test_22c_satir_araligi, test_22d_etiket_buyuk_harfle_baslar):
        test(yerine)


def test_28d_koordinasyon_pozlari(app):
    """
    Dört yeni poz: takla — büzük gövde kayan sahnede grupça 360° döner (dönüş 1. istasyonun içinde);
    altından geçişte baş engelin altında; üstünden geçişte öndeki ayak engelin üstünde; eğilip almada el yerde.
    """
    m, Z = app["TG_OLCEK"]["_tg_koordinasyon"][0], app["TG_ZEMIN"]
    for h_m in (0.8, 1.3):
        assert app["hk_alttan_gec"](100, h_m * m, s=0.7).olay["bas_ust_en_yuksek"] > Z - h_m * m
    assert app["hk_engel_ustu"](100, 0.4 * m, s=0.7).olay["ayak_en_alt_ustte"] > 0.4 * m
    el = app["hk_egil_al"](100, s=0.7).olay["el"]
    assert Z - 4 < el[1] <= Z
    h = app["hk_koordinasyon_turu"]()
    t0, t1, _, _ = h.olay["donus"]
    _, a, b = h.olay["istasyonlar"][0]
    assert a <= t0 < t1 <= b
    svg = app["tg_sahne"](_KOORD).svg(True, "")
    assert re.search(r'type="rotate" values="0 [\d.]+ [\d.]+;0 [\d.]+ [\d.]+;360', svg), "takla dönüşü yok"


# ════════════════════════════════════════════════════════════
# 29. Takla, kayan sahne hızı, CAMSA (Paket 22)
# ════════════════════════════════════════════════════════════
def test_29a_donuste_zemin_ve_uzuv_uclari(app):
    """
    Dönüş (donus) kullanılan her sahnede, dönüş aralığındaki her karede figür döndürülmüş hâliyle zemin çizgisinin
    altına inmez (eklemler ve baş çemberi) ve hiçbir iki uzuv ucu 3 birimden yakın değildir. Paket 22'ye dek
    takla merkezi eklem ortalamasıydı: figür 10,7 birim gömülüyor, büzük poz düğüm gibi görünüyordu.
    """
    import math as _m
    Z, U, en_az = app["TG_ZEMIN"], app["TG_UCLAR"], app["TG_EN_YAKIN_UC"]
    sorunlar, sayi = [], 0
    for ad, _ in _sahneler_tekil(app):
        for d in app["tg_sahne"](ad).donusler:
            sayi += 1
            assert d["kareler"], ad
            for t, e in d["kareler"]:
                a = _m.radians(360 * (t - d["t0"]) / ((d["t1"] - d["t0"]) or 1))

                def don(p):
                    x, y = p[0] - d["cx"], p[1] - d["cy"]
                    return d["cx"] + x * _m.cos(a) - y * _m.sin(a), d["cy"] + x * _m.sin(a) + y * _m.cos(a)
                alt = max([don(p)[1] for p in e.values()] + [don(e["bas"])[1] + d["bas_r"]])
                if alt > Z + 1e-6:
                    sorunlar.append(f"{ad}: t={t:.3f} en alt nokta {alt:.1f} (zemin {Z})")
                yakin = min(_m.dist(e[p], e[q]) for i, p in enumerate(U) for q in U[i + 1:])
                if yakin < en_az:
                    sorunlar.append(f"{ad}: t={t:.3f} uzuv uçları {yakin:.1f} birim")
    assert sayi, "dönüşlü sahne yok"
    assert not sorunlar, "Dönüşte zemin/uzuv sorunu:" + _ozet(sorunlar[:12])


def test_29b_kayan_sahne_hiz_siniri(app):
    """
    Kayan sahnede parkurun kayma hızı hiçbir anda KAYAN_HIZ_GECIS'i, bir istasyon/beceri yapılırken
    KAYAN_HIZ_ISTASYON'u geçmez (Paket 22: 90/156; Paket 23: 130/225 birim/sn — sınırlar uygulamadan okunur).
    """
    kayanlar = [ad for ad in app["TEST_GORSELLERI"] if app["tg_sahne"](ad).duragan is not None]
    assert set(kayanlar) >= {_KOORD, _CAMSA}, kayanlar
    sorunlar = []
    for ad in kayanlar:
        S = app["tg_sahne"](ad)
        assert S.istasyon_araliklari, f"{ad}: istasyon aralıkları kayıtlı değil"
        kayma = S.parkur_kaymasi
        assert kayma and [(t, d) for t, d, _ in S.kaymalar[0]] == [(t, d) for t, d in kayma], f"{ad}: parkur kayması"
        for (ta, da), (tb, db) in zip(kayma, kayma[1:]):
            if tb <= ta:
                continue
            v = abs(db - da) / ((tb - ta) * S.sure)
            orta = (ta + tb) / 2
            sinir = (app["KAYAN_HIZ_ISTASYON"] if any(a <= orta <= b for a, b in S.istasyon_araliklari)
                     else app["KAYAN_HIZ_GECIS"])
            if v > sinir + 0.5:
                sorunlar.append(f"{ad}: t={orta:.3f} kayma {v:.0f} birim/sn > {sinir}")
    assert not sorunlar, "Kayma çok hızlı:" + _ozet(sorunlar[:12])


def test_29c_camsa_protokolu(app):
    """
    CAPL-2 motor beceri testi CAMSA'dır: yedi beceri sabit sırayla (çift ayak sıçrama, yana kayma, top yakalama,
    hedefe atış, skipping 5 m, tek ayak sekme, topa vuruş); beceri 0-14 + süre 1-14 = toplam 1-28. Denge tahtası ve
    atlama ipi bu testte yok; eski "Teknik Beceri Puanı (1-10)" hiçbir yerde kalmadı.
    """
    t = [x for y, x in _testler(app["TEST_KATALOGU"]) if _test_adi(y) == _CAMSA][0]
    p = t["protokol"]
    adimlar = [ad.strip() for no, ad in re.findall(r"^(\d+)\. \*\*([^*:]+):\*\*", p, re.M) if 2 <= int(no) <= 8]
    assert adimlar == list(app["CAMSA_BECERILERI"]) == app["hk_camsa_turu"]().olay["beceri_adlari"], adimlar
    for parca in ("0–14", "1–14", "1–28", "5 m", "Üç çember", "Altı çember", "iki koninin arasından"):
        assert parca.lower() in p.lower(), parca
    ekipman = re.search(r"\*\*Ekipman:\*\*([^\n]*)", p).group(1).lower()
    assert "denge tahtası" not in ekipman and "atlama ipi" not in ekipman, ekipman
    assert "Beceri Puanı (0-14)" in t["degiskenler"] and "Süre Puanı (1-14)" in t["degiskenler"]
    assert not [k for k in list(app["NORMATIF"]) + list(app["NORMATIF_TEST"]) + list(app["NORMATIF_YAS"]) if "Teknik Beceri" in k]
    assert "Teknik Beceri Puanı (1-10)" not in str(t["degiskenler"])


def test_29d_camsa_kayan_sahne(app):
    """
    CAMSA kayan sahnede: beceri numaraları 1-7 sırayla (durağan genel görünümde de), kayan grupta yazı yok, figür
    sabit; topu atan uygulayıcı parkurun içinde ikinci kişi katmanında; süreölçer vuruşta durur.
    """
    S = app["tg_sahne"](_CAMSA)
    assert [n for n, _, _ in S.numaralar] == list(range(1, 8)) == [n for n, _, _ in S.duragan.numaralar]
    svg = S.svg(True, "")
    gruplar = re.findall(r'<g transform="translate\([^)]*\)"><animateTransform[^>]*type="translate".*?</g>', svg, re.S)
    parkur = max(gruplar, key=len)
    assert "<text" not in parkur and 'data-katman="ikinci_kisi"' in parkur
    xs = [e["kalca"][0] for e in S.tum_eklemler]
    assert max(xs) - min(xs) < 1
    h = app["hk_camsa_turu"]()
    t_bitis = h.olay["bitis_t"]
    kron = re.search(r'type="rotate" values="0 [^"]*;720 [^"]*;720 [^"]*" keyTimes="0;([\d.]+);([\d.]+);1"', svg)
    assert kron and abs(float(kron.group(2)) - t_bitis) < 1e-3, "süreölçer vuruşta durmuyor"
    assert S.svg(False, "") == S.duragan.svg(False, "")


# ── Paket 23 ──
def test_30a_kayma_hizi_sabitleri(app):
    """Kayma hızı sınırı 130 (istasyon) / 225 (geçiş) birim/sn; turlar buna göre kısalır (≈ 14,2 ve 7,4 sn)."""
    assert app["KAYAN_HIZ_ISTASYON"] == 130.0 and app["KAYAN_HIZ_GECIS"] == 225.0
    d = app["KAYAN_DURAKLAMA"]                             # Paket 25: her istasyon başında duraklama
    assert abs(app["hk_koordinasyon_turu"]().olay["sure"] - (14.2 + 9 * d)) < 0.3
    assert abs(app["hk_camsa_turu"]().olay["sure"] - (7.4 + 7 * d)) < 0.3


def test_30b_t_testi_standart_sira(app):
    """
    T-testi: A → B → C → D → B → A (Semenick 1990; Pauole ve ark. 2000). D'den C'ye dönüş yok; KAT ve tenis
    T-testi aynı parkuru, aynı sırayı gösterir; protokol metinlerinde eski sıra kalmaz.
    """
    p = app["_TG_PARKURLAR"]["t_testi"]
    assert p["yol"] == [(4.57, 0), (4.57, 9.14), (0, 9.14), (9.14, 9.14), (4.57, 9.14), (4.57, 0)]
    assert tuple(p["donus"]) == (1, 2, 3, 4)
    for ad in ("Karate Çeviklik Testi (KAT)", "T-Testi (Çeviklik)"):
        assert "D → C" not in app["TEST_GORSELLERI"][ad][1] + str(app["TEST_GORSELLERI"][ad][0].args) and "A → B → C → D → B → A" in app["TEST_GORSELLERI"][ad][1] + str(app["TEST_GORSELLERI"][ad][0].args)
        pr = _katalog_testi(app, ad)["protokol"]
        assert "C→D→C" not in pr and "D'den C'ye" not in pr, ad


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


def test_30c_spider_guzergahi(app):
    """
    Spider: başlangıç karesi arka çizginin gerisinde ortada; 5 top sağdan başlayarak sırayla, her biri kareye
    geri getirilir (her top arasında kareye dönüş); topa dokunuşlar 1-5 numaralı.
    """
    p = app["_TG_PARKURLAR"]["spider"]
    yol = p["yol"]
    kare = yol[0]
    assert kare[1] < 0 and abs(kare[0] - 8.23 / 2) < 1e-6
    assert yol[::2] == [kare] * 6, "her toptan sonra kareye dönülmeli"
    toplar = yol[1::2]
    assert len(toplar) == 5 and toplar[0][0] > kare[0], "sağdan başlanır"
    assert tuple(p["dokun"]) == (1, 3, 5, 7, 9)
    S = app["tg_sahne"]("Spider Test (Tenis Çeviklik Testi)")
    assert [n for n, _, _ in S.numaralar] == [1, 2, 3, 4, 5]


def test_30d_dogrulanamayan_degerler_isaretli(app):
    """
    Kaynakla doğrulanamayan değerler 'doğrulanamadı' notuyla kalır, norm olarak gösterilmez (Paket 23):
    Spider, servis, T-30, tenis T-testi eşikleri; CSS dinlenme süresi; BAT protokolü; esneklik profili yöntemi.
    """
    for ad in ("Spider Test (Tenis Çeviklik Testi)", "Tenis Servis Hızı ve İsabeti", "T-30 Yüzme Testi",
               "T-Testi (Çeviklik)", "Critical Swimming Speed (CSS) Testi",
               "Badminton Spesifik Çeviklik Testi (BAT)", "Jimnastik Esneklik Profili"):
        pr = _katalog_testi(app, ad)["protokol"]
        assert "doğrulanamadı" in pr, ad
        assert "**Normatif" not in pr, ad
    assert "Spider Test (Tenis Çeviklik Testi)" not in app["NORMATIF_TEST"]
    t30 = _katalog_testi(app, "T-30 Yüzme Testi")
    assert "Olbrecht" in t30["kaynak"] and "1800" in t30["protokol"]
    h, _ = app["turetilmis_degerler"]("T-30 Yüzme Testi", {"Toplam Mesafe (m)": "2160"}, None, 70)
    assert h["T-30 Hızı (m/sn)"] == 1.2
    assert "BAT" not in " ".join(app["TEST_GORSELLERI"]), "BAT protokolü doğrulanmadan görsel konmaz"


def test_30e_gorselsiz_katalog(app):
    """
    Bilerek görselsiz testler açıkça işaretli: her ad katalogda var, hiçbiri TEST_GORSELLERI'nde değil; her
    birinin nedeni yazılı. Vücut kompozisyonu, CAPL adım/anket, laboratuvar ölçümleri ve bataryalar burada.
    """
    Z = app["TEST_GORSELSIZ"]
    for ad, neden in Z.items():
        _katalog_testi(app, ad)
        assert neden and ad not in app["TEST_GORSELLERI"], ad
    nedenler = " ".join(Z.values())
    assert sum("vücut kompozisyonu" in n for n in Z.values()) >= 6
    assert "anket" in nedenler and "pedometre" in nedenler and "laboratuvar" in nedenler and "batarya" in nedenler
    for ad in ("VO2max Direkt Ölçüm (Ergospirometri)", "Laktat Eşiği Testi", "Kardiyopulmoner Egzersiz Testi (CPET)",
               "İzokinetik Kuvvet Testi", "EMG Tabanlı Kas Aktivasyonu", "DEXA (Dual-Energy X-ray Absorptiometry)",
               "Force-Velocity Profili (F-V)", "Rate of Force Development (RFD) Ölçümü",
               "Kuru Kara Testleri (Dry-Land) — Yüzme", "Jimnastik Fiziksel Uygunluk Testi (GFT)"):
        assert ad in Z, ad


def test_30f_yuzme_su_cizgisi(app):
    """
    Yüzme: su çizgisi zeminle aynı kalınlıkta ikinci yatay çizgi; yüzücünün kalçası her karede su çizgisinde;
    öne dönen kol (toparlanma) suyun üstünden geçer. CSS ve T-30 aynı çizimi kullanır, etiketleri farklıdır.
    """
    h = app["hk_serbest_stil"](54, 200, 72, s=0.75)
    su = h.olay["su_y"]
    k = app["TG_KALINLIK"]["zemin"]
    for ad in ("Critical Swimming Speed (CSS) Testi", "T-30 Yüzme Testi"):
        S = app["tg_sahne"](ad)
        svg = S.svg(False, "")
        assert re.search(rf'<line x1="14(\.0)?" y1="{su}(\.0)?" x2="246(\.0)?" y2="{su}(\.0)?"[^>]*stroke-width="{k}"', svg), ad
        assert all(abs(e["kalca"][1] - su) < 7 for e in S.tum_eklemler), ad      # gövde su çizgisinde (çırpışla ±)
    css, t30 = (app["TEST_GORSELLERI"][a][0] for a in ("Critical Swimming Speed (CSS) Testi", "T-30 Yüzme Testi"))
    assert css.func is t30.func and css.args != t30.args
    ust, sorunlar = 0, []
    kareler = [(t, app["tg_eklemler"](p)) for t, p in app["_tg_kareler"](h.anahtarlar)]
    for (ta, ea), (tb, eb) in zip(kareler, kareler[1:]):
        for el, om in (("el1", "boyun"), ("el2", "boyun")):
            ileri = (eb[el][0] - eb[om][0]) - (ea[el][0] - ea[om][0])      # el omza göre öne (yüzüş yönü +x)
            if ileri > 0.5:
                ust += 1
                if max(ea[el][1], eb[el][1]) > su + 1:
                    sorunlar.append(f"t={tb:.3f} {el} öne dönerken su altında")
    assert ust and not sorunlar, "toparlanma suyun üstünden geçmeli:" + _ozet(sorunlar[:8])


def test_30g_yeni_hareketler(app):
    """
    Servis: top elden çıkar, vuruş anında raket başı temas noktasına yakın; split: son karede kasık zeminden
    `uzaklik` kadar yukarıda (0 = tam split), ölçü oku kalçaya bağlı. Hepsi kitaplıkta.
    """
    for ad in ("hk_servis", "hk_serbest_stil", "hk_split"):
        assert ad in app["TG_HAREKET_KITAPLIGI"], ad
    h = app["hk_servis"](40, s=0.75)
    tv = h.olay["vurus_t"]
    rx, ry = min(((x, y) for t, x, y in h.olay["raket"] if abs(t - tv) < 1e-6), default=(None, None))
    assert rx is not None and app["_math"].dist((rx, ry), h.olay["temas"]) < 12
    assert h.olay["tutan_el"][1] > h.olay["atan_el"][1], "top önce elde, sonra yukarı atılır"
    bx, by = app["hk_servis"](36, s=0.75).olay["tutan_el"]
    assert f'cx="{bx:.1f}" cy="{by:.1f}" r="2.0"' in app["tg_sahne"]("Tenis Servis Hızı ve İsabeti").svg(True, ""), \
        "sahnede top başta tutan elde değil"
    for u in (0, 10, 20):
        hs = app["hk_split"](120, s=0.85, uzaklik=u)
        assert abs((app["TG_ZEMIN"] - hs.olay["kasik"][1]) - u) < 1.5, u


# ── Paket 24 ──
def test_31a_servis_temas_aninda_donar(app):
    """
    Tenis servisi: son anahtar TEMAS anıdır (raket yukarıda, top temasta); vuruş sonrası kare yok. Top sahnede
    temas noktasında kalır; hız oku ve radarın kesik ışını son karede görünür.
    """
    import math as _m
    h = app["hk_servis"](36, s=0.75)
    assert h.olay["vurus_t"] == 1.0 and h.anahtarlar[-1][0] == 1.0
    e = app["tg_eklemler"](h.anahtarlar[-1][1])
    assert e["el1"][1] < e["bas_ust"][1], "son karede raket kolu yukarıda değil"
    t, rx, ry = h.olay["raket"][-1]
    assert t == 1.0 and _m.dist((rx, ry), h.olay["temas"]) < 12
    S = app["tg_sahne"]("Tenis Servis Hızı ve İsabeti")
    (bx, by), (tx, ty) = h.olay["tutan_el"], h.olay["temas"]
    assert any(abs(k[-1][1] - (tx - bx)) < 0.2 and abs(k[-1][2] - (ty - by)) < 0.2 for k in S.kaymalar), \
        "top son karede temas noktasında değil"
    svg = S.svg(True, "")
    i = svg.find('<path d="M22,')
    assert i > 0, "radar ışını yok"
    kt = [float(v) for v in re.findall(r'keyTimes="([^"]+)"', svg[max(0, i - 400):i])[-1].split(";")]
    assert kt == sorted(kt) and max(kt) <= 1 and kt[1] < 1, "radar ışını animasyonda belirmiyor"


def test_31b_yuzme_kulac_ortasi(app):
    """
    Yüzme: son kare kulaç ortası — yakın kol suda (el su çizgisinin altında, omuzun gerisinde çekişte), uzak
    kol suyun üstünde ve önde. Havuzda su açık dolguyla görünür.
    """
    h = app["hk_serbest_stil"](54, 200, 72, s=0.75)
    e = app["tg_eklemler"](h.anahtarlar[-1][1])
    su = h.olay["su_y"]
    assert e["el1"][1] > su + 4, "yakın kol suda çekişte değil"
    assert e["el2"][1] < su - 4 and e["el2"][0] > e["boyun"][0], "uzak kol suyun üstünde önde değil"
    for ad in ("T-30 Yüzme Testi", "Su Topu Spesifik Aerobik Test (WPOAT)"):
        assert re.search(r'<rect x="14" y="72"[^>]*fill-opacity', app["tg_sahne"](ad).svg(False, "")), ad


def _rozet_top(app, tur):
    d = app["_TG_PARKURLAR"][tur]
    P = app["_tg_zemin_seridi"](d["x0"], *d["olcek"])
    return [P(*d["yol"][i]) for i in d["donus"]]


def test_31c_tek_bacak_ve_ayrik_rozet(app):
    """
    Spider ve SIST: rozetler üst üste binmez (merkezler arası > iki yarıçap) ve her rozet KENDİ hedefinin
    yanındadır (en yakın hedef odur). Aynı anda yalnız o anki gidiş-dönüş çizilir: bacak aralıkları ardışık,
    örtüşmez, sonuncusu sona kadar kalır; tek bir sürekli güzergâh çizgisi yoktur.
    """
    import math as _m
    for ad, tur in (("Spider Test (Tenis Çeviklik Testi)", "spider"), ("Squash Artımlı Mekik Testi (SIST)", "sist")):
        S = app["tg_sahne"](ad)
        hedef = _rozet_top(app, tur)
        rozet = [(x, y) for _, x, y in S.numaralar]
        assert len(rozet) == len(hedef)
        for i, p in enumerate(rozet):
            for q in rozet[i + 1:]:
                assert _m.dist(p, q) > 12, (ad, p, q)          # 2 × yarıçap + belirgin boşluk (eski sütun: 10)
            yakin = min(range(len(hedef)), key=lambda j: _m.dist(p, hedef[j]))
            assert yakin == i and _m.dist(p, hedef[i]) < 16, (ad, i + 1)
        b = S.bacaklar
        assert len(b) == len(hedef) and b[0][0] == 0 and b[-1][1] == 1.0, (ad, b)
        assert all(abs(x[1] - y[0]) < 1e-9 for x, y in zip(b, b[1:])), (ad, b)
        assert app["_TG_PARKURLAR"][tur].get("tek_tek")


def test_31d_besinci_parti_protokolleri(app):
    """
    5. parti protokolleri kaynakla karşılaştırıldı: doğrulanamayan eşikler norm olarak gösterilmez ("doğrulanamadı"
    notu), bulunamayan künyeler çıkarıldı, doğrulanan ayrıntılar (SIST kademesi, 6 dk düzeni, RLMSP yapısı) metinde.
    """
    notlu = ["Koparma (Snatch) / Silkme (Clean & Jerk) 1RM", "2000m Kürek Ergometre Testi",
             "200m Ergometre Testi (Kano/Kayak)", "500m Ergometre Testi (Kano/Kayak)",
             "1000m Ergometre Testi (Kano/Kayak)", "Rugby League Match Simulation Protocol (RLMSP)",
             "NFL Combine Testleri", "Rugby Union Fitness Test Bataryası", "Su Topu Spesifik Aerobik Test (WPOAT)",
             "Dikey Sıçrama - Suda (Su Topu)", "Squash Artımlı Mekik Testi (SIST)"]
    for ad in notlu + ["6 Dakika Kürek Ergometre Testi"]:
        t = _katalog_testi(app, ad)
        assert "**Normatif" not in t["protokol"], ad
        if ad in notlu:
            assert "doğrulanamadı" in t["protokol"], ad
        assert not any(k in t["kaynak"] for k in ("Malcolm", "Cuthbert", "Erzurum")), ad
    sist = _katalog_testi(app, "Squash Artımlı Mekik Testi (SIST)")
    assert "14 hareket" in sist["protokol"] and "1 dakika" in sist["protokol"] and "41-53" in sist["kaynak"]
    assert "111–114" in _katalog_testi(app, "6 Dakika Kürek Ergometre Testi")["protokol"]
    rl = _katalog_testi(app, "Rugby League Match Simulation Protocol (RLMSP)")
    assert "31(1), 48-57" in rl["kaynak"] and "5 devre × 10 dk (toplam 50 dk)\" yapısı" in rl["protokol"]


def test_31e_besinci_parti_kapsami(app):
    """
    12 test: dokuzu görselli (kürek iki test, kano üç test aynı çizim — fark etikette; WPOAT yüzme çizimini
    paylaşır; SIST parkurda), üçü (RLMSP, NFL Combine, Rugby Union) bilerek görselsiz.
    """
    G, Z = app["TEST_GORSELLERI"], app["TEST_GORSELSIZ"]
    gorselli = {"2000m Kürek Ergometre Testi": "_tg_kurek_ergometre", "6 Dakika Kürek Ergometre Testi": "_tg_kurek_ergometre",
                "200m Ergometre Testi (Kano/Kayak)": "_tg_kayak_ergometre", "500m Ergometre Testi (Kano/Kayak)": "_tg_kayak_ergometre",
                "1000m Ergometre Testi (Kano/Kayak)": "_tg_kayak_ergometre",
                "Koparma (Snatch) / Silkme (Clean & Jerk) 1RM": "_tg_halter",
                "Squash Artımlı Mekik Testi (SIST)": "_tg_parkur", "Su Topu Spesifik Aerobik Test (WPOAT)": "_tg_yuzme",
                "Dikey Sıçrama - Suda (Su Topu)": "_tg_suda_sicrama"}
    for ad, f in gorselli.items():
        assert G[ad][0].func.__name__ == f, ad
    assert G["2000m Kürek Ergometre Testi"][0].args != G["6 Dakika Kürek Ergometre Testi"][0].args
    assert len({G[a][0].args for a in gorselli if "Kano" in a}) == 3
    for ad in ("Rugby League Match Simulation Protocol (RLMSP)", "NFL Combine Testleri", "Rugby Union Fitness Test Bataryası"):
        assert ad in Z and ad not in G, ad


def test_31f_besinci_parti_hareketleri(app):
    """
    Kürek: ayaklar her karede ayaklıkta, son kare bitiş (koltuk en geride, bacaklar gergin). Kano/kayak: son kare
    yakalama (yakın el aşağıda-önde). Koparma: bar yerden (plaka zemine değer) baş üstüne; silkme: makas + bar baş
    üstünde. Suda sıçrama: tepede el suyun üstünde, kalça suyun altında.
    """
    import math as _m
    e = app["tg_eklemler"]
    Z = app["TG_ZEMIN"]
    k = app["hk_kurek_ergometre"](172, s=0.9)
    for _, p in app["_tg_kareler"](k.anahtarlar):
        assert _m.dist(e(p)["ayak1"], k.olay["ayaklik"]) < 1.5
    hx = [p["hx"] for _, p in k.anahtarlar]
    assert hx[-1] == min(hx) and _m.dist(e(k.anahtarlar[-1][1])["kalca"], k.olay["ayaklik"]) > 0.95 * 45 * 0.9
    y = app["hk_kayak_ergometre"](96, s=0.9)
    q = e(y.anahtarlar[-1][1])
    assert q["el1"][1] > q["el2"][1] + 15 and q["el1"][0] > q["boyun"][0]
    assert len(y.olay["kurek"][-1]) == 5
    kp = app["hk_koparma"](78, s=0.6)
    assert abs(kp.olay["bar"][0][2] - (Z - kp.olay["plaka"])) < 1.5, "bar yerde başlamıyor"
    q = e(kp.anahtarlar[-1][1])
    assert kp.olay["bar"][-1][2] < q["bas_ust"][1] and q["kalca"][1] > Z - 30, "koparma karşılaması değil"
    sk = app["hk_silkme"](182, s=0.6)
    q = e(sk.anahtarlar[-1][1])
    assert sk.olay["bar"][-1][2] < q["bas_ust"][1] and abs(q["ayak1"][0] - q["ayak2"][0]) > 15, "silkme makası değil"
    eg = app["hk_eggbeater_sicrama"](120, 76, s=0.6)
    q = e(eg.anahtarlar[-1][1])
    assert q["el1"][1] < 76 - 20 and q["kalca"][1] > 76
    b = [p["b1"] for _, p in eg.anahtarlar[:4]]
    assert len(set(b)) > 1, "eggbeater bacakları çırpmıyor"


# ── Paket 25 ──
def _ara_deger(seq, t):
    """[(t, a, b, ...)] dizisinde t anındaki doğrusal ara değer (SVG ile aynı: kareler arası doğrusal)."""
    for a, b in zip(seq, seq[1:]):
        if a[0] <= t <= b[0]:
            f = 0 if b[0] == a[0] else (t - a[0]) / (b[0] - a[0])
            return [x + (y - x) * f for x, y in zip(a[1:], b[1:])]
    return list(seq[-1][1:]) if t >= seq[-1][0] else list(seq[0][1:])


def test_32a_cubuk_basi_kesmez(app):
    """
    cubuk / cubuk_iki ile çizilen hiçbir öğe (kürek sapı, zincir, dinamometre kolu) HİÇBİR karede bir figürün baş
    çemberinin içinden geçmez (Paket 25: kayak küreği başın 4,4 birim içinden geçiyordu). Çubuk ve baş aynı zaman
    çizelgesinde, kareler arası doğrusal (SVG gibi) karşılaştırılır.
    """
    import math as _m

    def parca(px, py, x1, y1, x2, y2):
        vx, vy = x2 - x1, y2 - y1
        u = vx * vx + vy * vy
        t = 0 if u == 0 else max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / u))
        return _m.hypot(px - x1 - t * vx, py - y1 - t * vy)
    sorunlar, sayi = [], 0
    for ad, _ in _sahneler_tekil(app):
        S = app["tg_sahne"](ad)
        for c in S.cubuklar:
            sayi += 1
            for f in S.figurler:
                bas = [(t, *e["bas"]) for t, e in f["kareler"]]
                zam = sorted({k[0] for k in c} | {k[0] for k in bas})
                en = min((parca(*_ara_deger(bas, t), *_ara_deger(c, t)), t) for t in zam)
                if en[0] < f["bas_r"]:
                    sorunlar.append(f"{ad}: t={en[1]:.3f} çubuk baş merkezine {en[0]:.1f} (yarıçap {f['bas_r']:.1f})")
    assert sayi >= 4, sayi
    assert not sorunlar, "Çubuk başın içinden geçiyor:" + _ozet(sorunlar)


def test_32b_uzak_el_gorunur(app):
    """
    Son karede HER ölçülen figürün (yalnız sahnedeki son figür değil) uzuv uçları ayrık; halter (koparma ve
    silkme) ve kürek ergometresinde iki el en az 4,5 birim ayrı — uzak kol yakınınkinin altında kaybolmaz.
    """
    import math as _m
    sorunlar = []
    for ad, _ in _sahneler_tekil(app):
        for f in app["tg_sahne"](ad).figurler:
            if f["rol"] != "olculen":
                continue
            e = f["son"]
            for i, a in enumerate(app["TG_UCLAR"]):
                for b in app["TG_UCLAR"][i + 1:]:
                    if _m.dist(e[a], e[b]) < app["TG_EN_YAKIN_UC"]:
                        sorunlar.append(f"{ad}: {a}–{b} {_m.dist(e[a], e[b]):.1f}")
    for ad in ("Koparma (Snatch) / Silkme (Clean & Jerk) 1RM", "2000m Kürek Ergometre Testi"):
        for f in app["tg_sahne"](ad).figurler:
            d = _m.dist(f["son"]["el1"], f["son"]["el2"])
            if d < 4.5:
                sorunlar.append(f"{ad}: eller {d:.1f}")
    assert not sorunlar, "Uzuv uçları üst üste:" + _ozet(sorunlar)


def test_32c_aciktaki_test_kalmadi(app):
    """
    Katalogdaki her test ya görselli (TEST_GORSELLERI) ya da bilerek görselsiz (TEST_GORSELSIZ, nedenli); ikisi
    birden olamaz, hiçbiri açıkta kalmaz. Yeni eklenen test bu denetimi kırar ve kararı ister.
    """
    def adlar(d):
        for k, v in d.items():
            if str(k).startswith("_") or not isinstance(v, dict):
                continue
            if "protokol" in v:
                yield k
            else:
                yield from adlar(v)
    katalog = set(adlar(app["TEST_KATALOGU"]))
    G, Z = set(app["TEST_GORSELLERI"]), set(app["TEST_GORSELSIZ"])
    assert not (G & Z), sorted(G & Z)
    acik = sorted(katalog - G - Z)
    assert not acik, f"Açıkta {len(acik)} test: {acik}"
    assert "NHL/NHLTM Off-Ice Testleri" in Z


def test_32d_kayan_tur_ritmi(app):
    """
    Koordinasyon ve CAMSA turunda ritim (Paket 25): her istasyon penceresinin ilk 0,4 sn'sinde parkur kayması
    ~0 (duraklama); istasyon adı başlık yuvasında YALNIZ kendi penceresinde görünür, pencere dışında başlık;
    yuvadaki yazılar tek yazı sayılır, aynı anda en çok 3 yazı.
    """
    for ad, adlar_ in ((_KOORD, "istasyon_adlari"), (_CAMSA, "beceri_adlari")):
        S = app["tg_sahne"](ad)
        h = app["hk_koordinasyon_turu"]() if ad == _KOORD else app["hk_camsa_turu"]()
        pencere = h.olay["istasyonlar" if ad == _KOORD else "beceriler"]
        kayma = [(t, d) for t, d in S.parkur_kaymasi]
        for _, t0, t1 in pencere:
            tb = t0 + 0.4 / S.sure
            assert tb < t1
            d0, d1 = _ara_deger(kayma, t0)[0], _ara_deger(kayma, tb)[0]
            assert abs(d1 - d0) < 0.3, (ad, t0, d1 - d0)
        y = S.yuva
        assert [m for m, _, _ in y["pencereler"]] == h.olay[adlar_]
        assert [(a, b) for _, a, b in y["pencereler"]] == [(a, b) for _, a, b in pencere]
        svg = S.svg(True, ad)
        for metin, a, b in y["pencereler"]:
            i = svg.find(f">{metin}</text>")
            kt = re.findall(r'<g opacity="0"><animate attributeName="opacity" values="([^"]+)" keyTimes="([^"]+)"',
                            svg[:i])[-1]
            assert kt[0] == "0;1;0" and [round(float(x), 4) for x in kt[1].split(";")] == [0.0, round(a, 4), round(b, 4)], (ad, metin, kt)
        assert svg.count('data-yuva="baslik"') == len(y["pencereler"]) + 1
        yuvasiz = svg.count("<text") - svg.count('data-yuva="baslik"')
        assert yuvasiz + 1 <= app["TG_EN_COK_YAZI"]
    assert abs(app["hk_koordinasyon_turu"]().olay["sure"] - 18.7) < 0.3


# ── Paket 26 ──
def test_33a_duraklamada_iki_ayak_yerde(app):
    """
    Kayan turda her duraklamanın ortasında figürün iki ayağı da zeminde (bilekler TG_ZEMIN'den ≤ 1,5 birim): koşu
    ortasındaki poz donmuş görünmez (Paket 26: Koordinasyon 9/9, CAMSA 6/7 duraklamada bir ayak 12,4 birim havadaydı).
    Zaten iki ayağı yerde olan poz değişmez.
    """
    Z, E, d = app["TG_ZEMIN"], app["tg_eklemler"], app["KAYAN_DURAKLAMA"]
    for f, k in ((app["hk_koordinasyon_turu"], "istasyonlar"), (app["hk_camsa_turu"], "beceriler")):
        h = f()
        kareler = app["_tg_kareler"](h.anahtarlar)
        for n, t0, _ in h.olay[k]:
            for oran in (0.4, 0.5, 0.6):
                tm = t0 + d * oran / h.olay["sure"]
                _, p = min(kareler, key=lambda q: abs(q[0] - tm))
                e = E(p)
                y = max(Z - e["ayak1"][1], Z - e["ayak2"][1])
                assert y <= 1.5, (k, n, oran, round(y, 1))
    yerde = app["tg_poz"](100, s=0.7)
    assert app["_hk_hazir_durus"](yerde) is yerde
    havada = dict(app["tg_poz"](100, s=0.7, g=20, u1=80, b1=-60, k1=40), hy=Z - 60)   # sıçrama ortası gibi
    q = app["_hk_hazir_durus"](havada)
    e = E(q)
    assert max(Z - e["ayak1"][1], Z - e["ayak2"][1]) <= 1.5 and q["g"] == 20 and q["k1"] == 40 and q["hx"] == 100


def test_33b_koordinasyon_engel_altinda_bas(app):
    """
    Koordinasyon 3. istasyon: gövde direkler arasındayken (|kalça_x − engel_x| ≤ 6, dünya koordinatında) başın
    tepesi her karede kirişin altında (bas_ust y > kiriş y). Doğrulma gövde direklerin dışına çıktıktan sonra başlar
    (Paket 26: dönüşte baş kirişin 6 birim üstüne çıkıyordu). Top yine çembere bırakılır.
    """
    h = app["hk_koordinasyon_turu"]()
    o, Z = h.olay, app["TG_ZEMIN"]
    ex, eh = o["ekipman"]["engel_ust"]
    kiris = Z - eh
    _, a, b = [q for q in o["istasyonlar"] if q[0] == 3][0]

    def dx(t):
        return _ara_deger([(tt, d) for tt, d in o["kayma"]], t)[0]
    gecis = 0
    for t, p in app["_tg_kareler"](h.anahtarlar):
        if a <= t <= b:
            e = app["tg_eklemler"](p)
            if abs(e["kalca"][0] - dx(t) - ex) <= 6:
                gecis += 1
                assert e["bas_ust"][1] > kiris, (round(t * o["sure"], 2), round(kiris - e["bas_ust"][1], 1))
    assert gecis >= 3


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
# 41. Paket 34 — koyu tema: iki palet, tek yardımcı, CSS değişkenli görseller, Plotly yuvaları, katlanmış arama
# ════════════════════════════════════════════════════════════
_PALET_ADLARI = ("RENK", "NORM_SKALASI", "NOTR_SKALA", "BILINMEYEN_SKALA", "SERI_RENKLERI", "RAPOR_VURGU")


def test_41a_iki_palet_tek_yardimci(app, agac):
    """Her açık simgenin koyu karşılığı aynı yapıda; palet sabitlerine palet() dışında hiçbir kod bakmaz."""
    for ad in _PALET_ADLARI:
        a, k = app[ad], app[ad + "_KOYU"]
        if isinstance(a, dict):
            assert set(a) == set(k), ad
        else:
            assert len(a) == len(k), ad
    assert [x[:2] for x in app["NORM_SKALASI_KOYU"]] == [x[:2] for x in app["NORM_SKALASI"]]
    assert app["palet"]("koyu")["renk"] is app["RENK_KOYU"] and app["palet"]()["renk"] is app["RENK"]
    with pytest.raises(ValueError):
        app["palet"]("mavi")
    adlar = set(_PALET_ADLARI) | {a + "_KOYU" for a in _PALET_ADLARI}
    palet_fn = next(d for d in agac.body if isinstance(d, ast.FunctionDef) and d.name == "palet")
    icerde = {id(n) for n in ast.walk(palet_fn)}
    disarida = sorted({f"satır {n.lineno}: {n.id}" for n in ast.walk(agac)
                       if isinstance(n, ast.Name) and n.id in adlar and isinstance(n.ctx, ast.Load) and id(n) not in icerde})
    assert not disarida, "Palet sabitine doğrudan bakan kod:" + _ozet(disarida)


def test_41b_norm_skalasi_iki_temada_okunur(app):
    """Altı kategori × iki tema = 12 yazı/zemin kontrastı ≥ 4.5:1; koyu skalada da komşular arası ΔL* ≥ 10."""
    oranlar = {}
    for tema in ("acik", "koyu"):
        for k, sev, z, y in app["palet"](tema)["norm"]:
            oranlar[(tema, k)] = round(_kontrast(z, y), 2)
            b = app["kategori_bilgisi"](k, tema=tema)
            assert (b["zemin"], b["yazi"]) == (z, y)
    assert len(oranlar) == 12
    dusuk = {k: v for k, v in oranlar.items() if v < 4.5}
    assert not dusuk, dusuk
    L = [_L(z) for _, _, z, _ in app["NORM_SKALASI_KOYU"]]      # koyu zeminde Üstün en açık
    assert all(L[i] - L[i + 1] >= 10 for i in range(5)), L
    print("\nKontrast (yazı/zemin):", oranlar)


def test_41c_config_toml_iki_bolum_ve_yedek(app, tmp_path):
    """[theme] ortak + [theme.light] + [theme.dark]; yalnız [theme]'de geçerli anahtarlar alt bölümde yok. Varsa
    üzerine yazılır, eskisi config.toml.yedek; aynıysa dokunulmaz."""
    import tomllib
    t = tomllib.loads(app["tema_toml"]())["theme"]
    yalniz_ust = {"base", "fontFaces", "baseFontSize", "baseFontWeight", "metricValueFontSize",
                  "metricValueFontWeight", "showSidebarBorder"}
    assert set(t) >= {"light", "dark", "baseFontSize", "showSidebarBorder"}
    for b, tema in (("light", "acik"), ("dark", "koyu")):
        assert not (set(t[b]) & yalniz_ust), (b, set(t[b]) & yalniz_ust)
        assert t[b]["backgroundColor"] == app["palet"](tema)["renk"]["zemin"]
    yaz = app["config_toml_yaz"]
    d = tmp_path / ".streamlit"
    assert yaz(str(d)) == "yazildi" and not (d / "config.toml.yedek").exists()
    assert yaz(str(d)) == "ayni"
    (d / "config.toml").write_text('[theme]\nbase = "light"\n', encoding="utf-8")
    assert yaz(str(d)) == "yazildi"
    assert (d / "config.toml.yedek").read_text(encoding="utf-8") == '[theme]\nbase = "light"\n'
    assert (d / "config.toml").read_text(encoding="utf-8") == app["tema_toml"]()


def test_41c2_grafik_renkleri_surume_gore(app):
    """Paket 38h: grafik renkleri kurulu Streamlit'in tanıdığı bölüme yazılır (1.58: yalnız [theme]; light/dark
    altında yazılırsa açılışta 'not a valid config option' uyarısı ve varsayılan palet). Kurulu sürümün tanımadığı
    hiçbir theme anahtarı üretilmez."""
    import tomllib
    from streamlit import config as cfg
    gecerli = set(cfg.get_config_options())

    def anahtarlar(d, on="theme"):
        for k, v in d.items():
            yield from (anahtarlar(v, f"{on}.{k}") if isinstance(v, dict) else [f"{on}.{k}"])
    kurulu = tomllib.loads(app["tema_toml"]())["theme"]
    assert set(anahtarlar(kurulu)) <= gecerli, set(anahtarlar(kurulu)) - gecerli

    ortak = tomllib.loads(app["tema_toml"]("ortak"))["theme"]
    assert len(ortak["chartCategoricalColors"]) == 10 and len(ortak["chartSequentialColors"]) == 10
    assert all("chartCategoricalColors" not in ortak[b] for b in ("light", "dark"))
    zeminler = [app["palet"](t)["renk"]["zemin"] for t in ("acik", "koyu")]
    # marka yuvaları (ana, ikincil, seriler) iki zeminde de ≥ 3:1 (grafik ögesi)
    for i in (0, 1, 4, 5, 6):
        r = ortak["chartCategoricalColors"][i]
        assert all(_kontrast(r, z) >= 3 for z in zeminler), (i, r)

    tema = tomllib.loads(app["tema_toml"]("tema"))["theme"]
    assert "chartCategoricalColors" not in tema
    for b, t in (("light", "acik"), ("dark", "koyu")):
        assert tema[b]["chartCategoricalColors"] == app["_grafik_yuvasi_renkleri"](t)
        assert len(tema[b]["chartSequentialColors"]) == 10

    yok = app["tema_toml"](None)
    assert "chart" not in yok


def test_41d_gorseller_css_degiskeni_yedekli(app):
    """166 sahnenin (Paket 35: 160 + 6) hareketli ve durağan kopyasında hiçbir fill/stroke "#" ile başlamaz; her renk altı
    --tg-* değişkeninden biri ve açık yedeği var (tanımsız bağlamda figür görünür)."""
    G = app["TEST_GORSELLERI"]
    assert len(G) == 167   # Paket 35c: + Sargent görseli
    acik = app["palet"]("acik")["renk"]
    izinli = {f"var(--tg-{a}, {acik[a]})" for a in app["TG_DEGISKENLERI"]}     # yedek = açık paletin rengi
    assert {app["tg_renk"](a) for a in app["TG_DEGISKENLERI"]} == izinli and len(izinli) == 6
    sorun = []
    for ad in G:
        for hareketli in (True, False):
            svg = app["tg_sahne"](ad).svg(hareketli, ad)
            for attr, v in re.findall(r'\b(fill|stroke)="([^"]*)"', svg):
                if v.startswith("#"):
                    sorun.append(f"{ad} ({'hareketli' if hareketli else 'durağan'}): {attr}={v}")
                elif v.startswith("var(") and v not in izinli:
                    sorun.append(f"{ad}: yedeksiz/bilinmeyen değişken {v}")
            if re.search(r'style="[^"]*(?:fill|stroke)\s*:\s*#', svg):
                sorun.append(f"{ad}: style içinde hex")
    assert not sorun, "Görselde sabit renk:" + _ozet(sorun)


def test_41e_tema_css_iki_tema_degiskenleri(app):
    """TEMA_CSS: :root açık; prefers-color-scheme koyu; Streamlit'in tema seçimi (color-scheme → light-dark())."""
    css = app["TEMA_CSS"]
    acik, koyu = app["palet"]("acik")["renk"], app["palet"]("koyu")["renk"]
    kok = re.search(r":root \{([^}]*)\}", css).group(1)
    medya = re.search(r"@media \(prefers-color-scheme: dark\) \{ :root \{([^}]*)\}", css).group(1)
    secici = re.search(r'\[data-testid="stApp"\] \{([^}]*)\}', css).group(1)
    for a in app["TG_DEGISKENLERI"]:
        assert f"--tg-{a}:{acik[a]};" in kok and f"--tg-{a}:{koyu[a]};" in medya, a
        assert f"--tg-{a}:light-dark({acik[a]}, {koyu[a]})" in secici, a
    assert "@supports (color: light-dark(" in css
    for k, sev, z, y in app["palet"]("koyu")["norm"]:
        assert f"--sp-norm-{sev}-zemin:{z};" in medya and f"--sp-norm-{sev}-yazi:{y};" in medya
    # sayfa bileşenleri de değişkenden: rozet, kart, ölçer
    roz = app["kategori_rozeti"]("Üstün")
    assert "var(--sp-norm-6-zemin, " in roz and "var(--sp-norm-6-yazi, " in roz
    assert "var(--sp-yuzey, " in app["BILESEN_CSS"] and "var(--tg-yuzey, " in app["BILESEN_CSS"]


def test_41f_plotly_tema_yuvalari(app, agac):
    """Plotly renkleri Streamlit'in tema yuvaları (#000001…): tarayıcı o anki temanın rengini koyar; Python'da yazı
    rengi verilmez."""
    gr = app["grafik_renk"]
    assert gr("ana") == "#000001" and gr("ikincil") == "#000002"
    # Paket 38h: yazı ve çizgi Streamlit'in kendi tema grileri (tek paletli sürümde de iki temada doğru)
    assert gr("murekkep") == "#000037" and gr("cizgi") == "#000035"
    with pytest.raises(ValueError):
        gr("yok")
    # Paket 35d: saydamlık parametresi kaldırıldı (8 haneli #RRGGBBAA eski Plotly'de reddediliyor); hep 6 hane
    assert all(re.fullmatch(r"#\d{6}", gr(y)) for y in app["GRAFIK_YUVALARI"])
    with pytest.raises(TypeError):
        gr("ana", 0.15)
    assert app["grafik_norm_renk"]("Üstün") == "#000016" and app["grafik_norm_renk"]("Çok Düşük") == "#000011"
    d = app["grafik_duzeni"]()
    # Paket 38b: zemin rengi verilmez (rgba yok); Streamlit teması grafiğin zeminini sayfayla eşler
    assert "color" not in d["font"] and "paper_bgcolor" not in d and "plot_bgcolor" not in d
    assert "rgba" not in repr(d)
    cagri = [n for n in ast.walk(agac) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr in ("update_layout", "add_trace", "add_shape", "add_annotation", "add_vline")]
    sorun = [ast.unparse(n)[:80] for n in cagri if re.search(r'font=dict\(color=|\bRENK\b', ast.unparse(n))
             and "add_annotation" not in ast.unparse(n)]
    assert not sorun, sorun
    assert sum("grafik_duzeni" in ast.unparse(n) for n in cagri) == 6   # Paket 38d: + oturumlar arası fark


def test_41g_ana_sayfa_katlanmis_arama(tmp_path, monkeypatch, app):
    """Öneri kartının altında KAPALI 'Test ara'; açılınca ad + kategori, sonuçlar yol bilgisiyle ve 'Uygula'."""
    import pandas as _pd

    def veri(d):
        _pd.DataFrame({"Ad": ["Ali"], "Soyad": ["Yılmaz"], "Yaş": [10], "Cinsiyet": ["Erkek"]}).to_excel(
            d / "sporcular.xlsx", index=False)
    at = _apptest(tmp_path, monkeypatch, veri)
    assert not at.exception, [e.value for e in at.exception]
    assert [e.label for e in _acilirlar(at)] == ["Test ara"] and not _acilirlar(at)[0].proto.expanded
    assert not [b for b in at.button if b.label == "Uygula"]            # sorgu yokken liste yok
    at.text_input(key="yon_ara").input("yo-yo").run()
    assert [b.label for b in at.button].count("Uygula") == 2
    assert any("Laboratuvar ve Fizyolojik Testler › " in m.value for m in at.markdown)
    at.button(key="yon::ara::0").click().run()
    assert at.session_state["sayfa"] == "Test Uygula" and at.session_state["tu_sporcu"] == "Ali Yılmaz"


def test_00_yukleyici_gerekli_tanimlari_buldu(app):
    gerekli = ["TEST_KATALOGU", "NORMATIF_YAS", "NORMATIF_TEST", "NORMATIF", "BOLUM_BASLIKLARI",
               "protokol_formatla", "protokol_ozet_cikar", "_uygulama_araligi", "yas_z_skoru",
               "brans_grubu_eslestir", "BRANS_GRUBU_PROFILLERI", "ESLESTIRME_DEGISKENLERI",
               "KAYNAKCA", "KAYNAKCA_SINIFLAR"]
    eksik = [ad for ad in gerekli if ad not in app]
    assert not eksik, (f"Denetim için gerekli tanımlar yüklenemedi: {eksik}. "
                       f"Atlanan modül düzeyi satırlar: {app['_atlanan'][:5]}")


def test_00b_modul_duzeyinde_gizli_degisiklik_yok(agac):
    """
    Denetim yalnızca atamaları ve fonksiyonları çalıştırır. Modül düzeyinde 'SOZLUK.update(...)' gibi
    bir ifade, uygulamada çalışır ama denetimde görünmez (TSYT normları bir kez böyle gözden kaçtı).
    Bu tür değişiklikler atama olarak yazılmalı: SOZLUK = {**SOZLUK, **EK}.
    """
    sorunlar = []
    for dugum in agac.body:
        if (isinstance(dugum, ast.Expr) and isinstance(dugum.value, ast.Call)
                and isinstance(dugum.value.func, ast.Attribute)
                and dugum.value.func.attr in ("update", "append", "extend", "insert", "setdefault", "pop")
                and isinstance(dugum.value.func.value, ast.Name) and dugum.value.func.value.id.isupper()):
            sorunlar.append(f"satır {dugum.lineno}: {ast.unparse(dugum)[:80]}")
    assert not sorunlar, "Denetimin göremediği modül düzeyi değişiklik:" + _ozet(sorunlar)


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
# 44. Bölme Aşama 1: veri/ modülleri yalnız sabit değer
# ════════════════════════════════════════════════════════════
_VERI_KLASOR = os.path.join(os.path.dirname(DOSYA), "veri")
_VERI_SERBEST = (ast.Constant, ast.Dict, ast.List, ast.Tuple, ast.Set, ast.Load)


def _veri_modulleri():
    if not os.path.isdir(_VERI_KLASOR):
        return []
    return sorted(os.path.join(_VERI_KLASOR, d) for d in os.listdir(_VERI_KLASOR)
                  if d.endswith(".py") and d != "__init__.py")


def test_44a_veri_modulleri_yalniz_sabit(agac):
    """
    veri/*.py: modül düzeyinde yalnız açıklama ve atama; değerlerde yalnız sabit, sözlük, liste, demet, küme,
    eksi sayı, metin birleştirme (+) ve AYNI modülde daha önce tanımlanmış ad (ör. TSYT_KAYNAK + "…").
    Çağrı, lambda, içe aktarma, f-string yok. Uygulama her modülü içe aktarır ve hiçbir veri adını yeniden
    literal olarak tanımlamaz (iki kopya olmasın).
    """
    sorun, tum_adlar = [], {}
    for yol in _veri_modulleri():
        m = ast.parse(open(yol, encoding="utf-8").read())
        tanimli = set()
        for i, d in enumerate(m.body):
            if i == 0 and isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant):
                continue
            if not (isinstance(d, ast.Assign) and len(d.targets) == 1 and isinstance(d.targets[0], ast.Name)):
                sorun.append(f"{os.path.basename(yol)}:{d.lineno} atama değil ({type(d).__name__})")
                continue
            for x in ast.walk(d.value):
                if isinstance(x, _VERI_SERBEST):
                    continue
                if isinstance(x, ast.UnaryOp) and isinstance(x.op, ast.USub) and isinstance(x.operand, ast.Constant):
                    continue
                if isinstance(x, ast.USub) or isinstance(x, ast.Add):
                    continue
                if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Add):
                    continue
                if isinstance(x, ast.Name) and x.id in tanimli:
                    continue
                sorun.append(f"{os.path.basename(yol)}:{x.lineno} izin verilmeyen {type(x).__name__}")
            tanimli.add(d.targets[0].id)
        tum_adlar[os.path.basename(yol)[:-3]] = tanimli
    assert not sorun, sorun
    ice = {(d.module, a.name) for d in agac.body if isinstance(d, ast.ImportFrom) and (d.module or "").startswith("veri.")
           for a in d.names}
    for modul, adlar in tum_adlar.items():
        assert any(m == f"veri.{modul}" for m, _ in ice), f"veri/{modul}.py içe aktarılmıyor"
    kod = [d for y in _kaynak_dosyalari(veri=False) for d in ast.parse(_oku(y)).body]   # uygulama + olcut
    literal = {d.targets[0].id for d in kod if isinstance(d, ast.Assign) and len(d.targets) == 1
               and isinstance(d.targets[0], ast.Name) and isinstance(d.value, (ast.Dict, ast.List, ast.Tuple, ast.Constant))
               and not any(isinstance(x, (ast.Name, ast.Call)) for x in ast.walk(d.value))}   # {**X, …} literal değil
    iki_kez = sorted(literal & set().union(*tum_adlar.values())) if tum_adlar else []
    assert not iki_kez, f"Hem veri/ hem uygulama.py'de literal: {iki_kez}"


# ════════════════════════════════════════════════════════════
# 45. Bölme Aşama 2: olcut/ paketinin katman sırası (döngüsel bağımlılık yok)
# ════════════════════════════════════════════════════════════
_OLCUT_KATMAN = ["ortak", "disa_aktarma", "tema", "esik", "katalog_islemleri", "gorseller.cizim", "gorseller.hareketler",
                 "gorseller.sahneler", "norm", "analiz", "kayit", "raporlar", "oneri", "karsilastirma", "bilesenler", "sayfalar"]


def _olcut_katmani(modul):
    ad = modul[len("olcut."):]
    return next((i for i, k in enumerate(_OLCUT_KATMAN) if ad == k or ad.startswith(k + ".")), None)


def test_45a_olcut_katman_sirasi():
    """
    Her olcut modülü yalnız kendinden AŞAĞIDAKİ katmanları içe aktarır (sayfalar birbirini içe aktarmaz);
    hiçbir modül uygulama.py'yi içe aktarmaz. Yeni bir modül önce _OLCUT_KATMAN'a yazılmalı.
    """
    kok = os.path.dirname(DOSYA)
    sorun = []
    for yol in _kaynak_dosyalari(veri=False)[1:]:
        goreli = os.path.relpath(yol, kok)[:-3].replace(os.sep, ".")
        modul = goreli[:-len(".__init__")] if goreli.endswith(".__init__") else goreli
        if modul in ("olcut", "olcut.gorseller", "olcut.sayfalar"):
            continue
        ben = _olcut_katmani(modul)
        if ben is None:
            sorun.append(f"{modul}: _OLCUT_KATMAN'da yok")
            continue
        for d in ast.walk(ast.parse(_oku(yol))):
            hedefler = ([a.name for a in d.names] if isinstance(d, ast.Import)
                        else [d.module or ""] if isinstance(d, ast.ImportFrom) else [])
            for h in hedefler:
                if h.split(".")[0] == "uygulama":
                    sorun.append(f"{modul}: uygulama'yı içe aktarıyor")
                elif h.startswith("olcut."):
                    o = _olcut_katmani(h)
                    if o is None or o >= ben:
                        sorun.append(f"{modul} → {h}: katman sırasına aykırı")
    assert not sorun, sorun



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
    assert [t.label for t in at.tabs] == ["Sporcular arası", "Oturumlar arası"]
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
        ilk_dugme = next(c for c in sira if type(c).__name__ == "Button")
        assert ilk_dugme.key == beklenen[0], sayfa                       # menü ana alanın en üstünde
        assert getattr(sira[-1], "key", None) == "alt_hakkinda" or M.ALT_BILGI_METNI in str(
            getattr(sira[-1], "value", "")), sayfa                        # alt bilgi en sonda
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
    assert "ot_geri" in anahtar and anahtar.index("ot_geri") < alt and anahtar.index("ust-menu-ana-sayfa") == min(
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
