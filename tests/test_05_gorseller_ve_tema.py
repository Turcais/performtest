"""
Görsel sistem (tema.py), açık/koyu paletler, Plotly tema yuvaları, SVG test sahneleri ve animasyonlar.
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

