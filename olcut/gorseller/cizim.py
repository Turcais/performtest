"""
Test görselleri — çizim motoru (Paket 13-14): TgSahne (SVG sahne, animasyon kareleri, yazı kutuları), figür ve
eklem yardımcıları, renk/ölçek sabitleri. Uygulamanın kendi çizimleri; dışarıdan görsel yok.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import math as _math
import re
import streamlit as st
from collections import namedtuple as _namedtuple
from olcut.tema import FIGUR_DERINLIK_OPAKLIK, FIGUR_KATMANI, YAZI_AILESI, tg_renk


# ── 1) ÇİZİM TAKIMI ──
TG_TUVAL = (260, 140)        # viewBox genişlik × yükseklik — her görsel bununla çizilir


TG_ZEMIN = 116               # zemin çizgisinin y'si (altında ölçü okları için şerit: 116-128)


TG_KALINLIK = {"figur": 3.2, "govde": 4.0, "esya": 2.0, "olcu": 1.6, "zemin": 1.5, "vurgu": 4.0, "kilavuz": 0.8}


TG_YAZI = 8.5                # not ve ölçü etiketi


TG_BASLIK_YAZI = 9.5         # üst başlık (kalın)


TG_EN_COK_YAZI = 3           # sahne başına yazı sınırı


# Paket 34: renk hex değil yedekli CSS değişkeni — var(--tg-murekkep, <açık yedek>) … Değişkenler TEMA_CSS'te iki tema
# için tanımlı; tanımsız kaldığı bağlamda (rapor, dışa aktarım) yedek açık renk çizilir, figür kaybolmaz.
TG_RENK = {"figur": tg_renk("murekkep"), "esya": tg_renk("ikincil"), "olcu": tg_renk("ana"),
           "zemin": tg_renk("ikincil"), "dolgu": tg_renk("cizgi"), "yuzey": tg_renk("yuzey")}


# Çocuk figürünün parça uzunlukları (tuval biriminde; ayakta boy ≈ 92)
_TG_BOY = {"govde": 30, "boyun": 9, "bas": 6.5, "uyluk": 22, "baldir": 23, "ust": 16, "on": 15, "ayak": 6,
           "omuz": 2.0, "kalca": 2.0}


# Ayakta temel poz: uzuvlar ayrışık (yakın/uzak bacak ve kol üst üste binmez). Her poz bundan türer.
# Bacak açıları ayak bilekleri arası ≥ 3 birim olacak biçimde seçildi (u1=4/b1=-3/u2=-5/b2=2 ile 1,4 kalıyordu).
TG_TEMEL_POZ = {"g": 0, "u1": 7, "b1": -1, "u2": -6, "b2": 0, "k1": 9, "o1": 7, "k2": -8, "o2": -6,
                "a1": 90, "a2": 90}


TG_UCLAR = ("el1", "el2", "ayak1", "ayak2")   # uzuv uçları (örtüşme denetimi)


# Figür rolü → GÖRSEL SİSTEM'deki katman (FIGUR_KATMANI): renk, opaklık, kalınlık ve kesik çizgi oradan gelir
TG_ROL_KATMANI = {"olculen": "olculen", "partner": "ikinci_kisi", "iz": "onceki_an"}


TG_EN_YAKIN_UC = 3.0


# Yazı yerleşimi (Paket 16): üst ve alt şerit yalnız yazıya ait; çizim bu şeritlere girmez.
TG_SERIT_UST = 16            # üst şerit y ∈ [0, 16]: başlık


TG_SERIT_ALT = 128           # alt şerit y ∈ [128, 140]: not


TG_YAZI_PAYI = 4             # etiket tuval kenarından en az


TG_CIZGI_PAYI = 6            # yazı kutusu ↔ en yakın figür/eşya çizgisi en az (Paket 17: kutu değil gerçek çizgi)


TG_SATIR = 11                # alt alta iki yazının taban farkı en az (8,5 punto için)


TG_OLCU_Y = 121              # zemin üstü mesafe okları: zemin çizgisinin altında, alt şeritten (128) önce


# Büyük harf kuralı: etiket büyük harf, rakam ya da özel adla başlar (özel ad kendi yazımını korur).
# Büyük harfler etiket metnine elle yazılır — dönüştürme işlevi kullanılmaz (Türkçe i/İ kuralı).
TG_OZEL_ADLAR = ("TSYT", "KTK3+", "Yo-Yo", "Pro Agility", "SWFT", "SJFT", "NBA", "Borg", "Wingate")


# Yedi bölmeli rakam bölmeleri (a üst, b sağ üst, c sağ alt, d alt, e sol alt, f sol üst, g orta) — yalnız sıra
# numarası rozetinde kullanılır; sayaç rakam göstermez (Paket 19)
_TG_RAKAM = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
             8: "abcdefg", 9: "abcdfg"}


def _tg_xml_sekilleri(xml, dx=0.0, dy=0.0):
    """
    Çizim xml'indeki şekillerin geometrisi (denetim: yazının EN YAKIN ÇİZGİYE uzaklığı). Yazı dışarıda.
    ("cizgi", x1, y1, x2, y2, yarı_kalınlık) — çizgi, dikdörtgen kenarı, yol parçası;
    ("disk", cx, cy, r) — dolu daire/elips (yarıçap çizgi payıyla); ("alan", x0, y0, x1, y1) — dolu dikdörtgen.
    """
    xml = re.sub(r"<text\b.*?</text>", "", xml, flags=re.S)
    sekiller = []
    for ad, govde in re.findall(r"<(line|rect|circle|ellipse|path)\b([^>]*)>", xml):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', govde))
        f = lambda n: float(a.get(n, 0) or 0)
        k = f("stroke-width") / 2 if a.get("stroke", "none") != "none" else 0.0
        dolu = a.get("fill", "black") != "none"
        if ad == "line":
            sekiller.append(("cizgi", f("x1") + dx, f("y1") + dy, f("x2") + dx, f("y2") + dy, k))
        elif ad == "rect":
            x0, y0, x1, y1 = f("x") + dx, f("y") + dy, f("x") + f("width") + dx, f("y") + f("height") + dy
            if dolu:
                sekiller.append(("alan", x0 - k, y0 - k, x1 + k, y1 + k))
            else:
                sekiller += [("cizgi", x0, y0, x1, y0, k), ("cizgi", x1, y0, x1, y1, k),
                             ("cizgi", x1, y1, x0, y1, k), ("cizgi", x0, y1, x0, y0, k)]
        elif ad == "circle":
            sekiller.append(("disk", f("cx") + dx, f("cy") + dy, f("r") + k))
        elif ad == "ellipse":                          # elips: 24 parçalı çevre
            cx, cy, rx, ry = f("cx") + dx, f("cy") + dy, f("rx"), f("ry")
            n = [(cx + rx * _math.cos(i * _math.pi / 12), cy + ry * _math.sin(i * _math.pi / 12)) for i in range(25)]
            sekiller += [("cizgi", *a_, *b_, k) for a_, b_ in zip(n, n[1:])]
        else:
            noktalar, cx, cy, kip, sayilar = [], 0.0, 0.0, "M", []
            for parca in re.findall(r"[MLQqlmz]|-?\d+(?:\.\d+)?", a.get("d", "")):
                if parca.isalpha():
                    if parca == "z" and noktalar:
                        noktalar.append(noktalar[0])
                    kip, sayilar = parca, []
                    continue
                sayilar.append(float(parca))
                gerek = 4 if kip in "Qq" else 2
                if len(sayilar) == gerek:
                    goreli = kip.islower()
                    p = [(sayilar[i] + (cx if goreli else 0), sayilar[i + 1] + (cy if goreli else 0)) for i in range(0, gerek, 2)]
                    noktalar += p
                    cx, cy = p[-1]
                    sayilar = []
            sekiller += [("cizgi", x1 + dx, y1 + dy, x2 + dx, y2 + dy, k)
                         for (x1, y1), (x2, y2) in zip(noktalar, noktalar[1:])]
    return sekiller


def _tg_xml_kutulari(xml, dx=0.0, dy=0.0):
    """Çizim xml'indeki şekillerin sınır kutuları (çizgi kalınlığı dahil); yazı dışarıda. Denetim içindir."""
    xml = re.sub(r"<text\b.*?</text>", "", xml, flags=re.S)
    kutular = []
    for ad, govde in re.findall(r"<(line|rect|circle|ellipse|path)\b([^>]*)>", xml):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', govde))
        f = lambda n: float(a.get(n, 0) or 0)
        k = f("stroke-width") / 2 if a.get("stroke", "none") != "none" else 0.0
        if ad == "line":
            xs, ys = [f("x1"), f("x2")], [f("y1"), f("y2")]
        elif ad == "rect":
            xs, ys = [f("x"), f("x") + f("width")], [f("y"), f("y") + f("height")]
        elif ad == "circle":
            xs, ys = [f("cx") - f("r"), f("cx") + f("r")], [f("cy") - f("r"), f("cy") + f("r")]
        elif ad == "ellipse":
            xs, ys = [f("cx") - f("rx"), f("cx") + f("rx")], [f("cy") - f("ry"), f("cy") + f("ry")]
        else:
            xs, ys, cx, cy, kip = [], [], 0.0, 0.0, "M"
            sayilar = []
            for parca in re.findall(r"[MLQqlmz]|-?\d+(?:\.\d+)?", a.get("d", "")):
                if parca.isalpha():
                    kip, sayilar = parca, []
                    continue
                sayilar.append(float(parca))
                gerek = 4 if kip in "Qq" else 2
                if len(sayilar) == gerek:
                    goreli = kip.islower()
                    noktalar = [(sayilar[i] + (cx if goreli else 0), sayilar[i + 1] + (cy if goreli else 0))
                                for i in range(0, gerek, 2)]
                    for x, y in noktalar:
                        xs.append(x)
                        ys.append(y)
                    cx, cy = noktalar[-1]
                    sayilar = []
            if not xs:
                continue
        kutular.append((min(xs) - k + dx, min(ys) - k + dy, max(xs) + k + dx, max(ys) + k + dy))
    return kutular


def _tg_yon(aci):
    """Aşağıdan ölçülen açı (derece, + = ileri/+x) → birim vektör (SVG: y aşağı)."""
    r = _math.radians(aci)
    return _math.sin(r), _math.cos(r)


def tg_eklemler(p):
    """
    Poz → eklem noktaları. p: hx, hy (kalça), g (gövde eğimi, + ileri), u/b (uyluk/baldır), k/o (üst kol/ön kol)
    1 = yakın, 2 = uzak; a1/a2 ayak açısı (90 = ileri); yon (+1 sağa, −1 sola bakar); s ölçek; cephe (önden).
    """
    s, yon = p.get("s", 1.0), p.get("yon", 1)
    L = {k: v * s for k, v in _TG_BOY.items()}
    hx, hy = p["hx"], p["hy"]

    def uc(x, y, aci, uz):
        dx, dy = _tg_yon(aci)
        return x + yon * dx * uz, y + dy * uz

    g = _math.radians(p.get("g", 0))
    ux, uy = yon * _math.sin(g), -_math.cos(g)          # gövde doğrultusu (yukarı)
    px, py = -uy, ux                                    # gövdeye dik (omuz/kalça çizgisi)
    boyun = (hx + ux * L["govde"], hy + uy * L["govde"])
    bas = (boyun[0] + ux * L["boyun"], boyun[1] + uy * L["boyun"])
    e = {"kalca": (hx, hy), "boyun": boyun, "bas": bas,
         "bas_ust": (bas[0] + ux * L["bas"], bas[1] + uy * L["bas"]),     # başın tepesi (ölçü bağı için)
         # çene: baş çemberinde yüzün baktığı yanın altı (yüz = gövdeye dik, yon yönünde) — ölçü bağı için
         "cene": (bas[0] + (0.6 * -uy - 0.8 * ux) * L["bas"], bas[1] + (0.6 * ux - 0.8 * uy) * L["bas"]),
         "omuz_a": (boyun[0] + px * L["omuz"], boyun[1] + py * L["omuz"]),
         "omuz_b": (boyun[0] - px * L["omuz"], boyun[1] - py * L["omuz"]),
         "kalca_a": (hx + px * L["kalca"], hy + py * L["kalca"]),
         "kalca_b": (hx - px * L["kalca"], hy - py * L["kalca"])}
    on = p.get("cephe", False)
    for i, isaret in (("1", 1), ("2", -1)):
        kok_b = e["kalca_a" if isaret > 0 else "kalca_b"] if on else (hx, hy)
        kok_k = e["omuz_a" if isaret > 0 else "omuz_b"] if on else boyun
        diz = uc(*kok_b, p.get("u" + i, 0), L["uyluk"])
        ayak = uc(*diz, p.get("b" + i, 0), L["baldir"])
        e["kok_b" + i], e["kok_k" + i] = kok_b, kok_k
        e["diz" + i], e["ayak" + i] = diz, ayak
        e["parmak" + i] = uc(*ayak, p.get("a" + i, 90), L["ayak"])
        dirsek = uc(*kok_k, p.get("k" + i, 0), L["ust"])
        e["dirsek" + i], e["el" + i] = dirsek, uc(*dirsek, p.get("o" + i, 0), L["on"])
    return e


# Figürün son karesindeki çizgi parçaları (yazı ↔ en yakın çizgi denetimi; çizim _tg_parcalar ile aynı)
_TG_FIGUR_CIZGILERI = [("parmak1", "ayak1"), ("ayak1", "diz1"), ("diz1", "kok_b1"), ("parmak2", "ayak2"),
                       ("ayak2", "diz2"), ("diz2", "kok_b2"), ("kalca", "boyun"), ("el1", "dirsek1"),
                       ("dirsek1", "kok_k1"), ("el2", "dirsek2"), ("dirsek2", "kok_k2"),
                       ("omuz_a", "omuz_b"), ("kalca_a", "kalca_b")]


def _tg_d(noktalar):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in noktalar)


def _tg_parcalar(e):
    """Figür parçaları: uzak uzuvlar soluk; gövde kalın; omuz ve kalça kısa çizgi."""
    return {
        "bacak2": _tg_d([e["parmak2"], e["ayak2"], e["diz2"], e["kok_b2"]]),
        "kol2": _tg_d([e["el2"], e["dirsek2"], e["kok_k2"]]),
        "govde": _tg_d([e["kalca"], e["boyun"]]),
        "kusak": _tg_d([e["omuz_a"], e["omuz_b"]]) + " " + _tg_d([e["kalca_a"], e["kalca_b"]]),
        "bacak1": _tg_d([e["parmak1"], e["ayak1"], e["diz1"], e["kok_b1"]]),
        "kol1": _tg_d([e["el1"], e["dirsek1"], e["kok_k1"]]),
    }


def _tg_ara(p0, p1, f):
    """İki poz arasında açı/konum ara değeri (uzuv boyu korunur)."""
    sonuc = dict(p1)
    for k, v in p1.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and k in p0 and k != "yon":
            sonuc[k] = p0[k] + (v - p0[k]) * f
    if f < 0.5:
        sonuc["yon"] = p0.get("yon", 1)
    return sonuc


def _tg_kareler(anahtarlar, adim=6):
    """[(t, poz)] → sık kareler: SMIL doğrusal ara değerde uzuvlar kısalmasın."""
    kareler = []

    def taban(p):
        e = tg_eklemler(p)
        return max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))
    for (t0, p0), (t1, p1) in zip(anahtarlar, anahtarlar[1:]):
        z0, z1 = taban(p0), taban(p1)
        for j in range(adim):
            f = j / adim
            q = _tg_ara(p0, p1, f * f * (3 - 2 * f))
            if abs(z0 - z1) < 0.5:                    # iki anahtar aynı zeminde: ara karede de o zeminde
                q = dict(q, hy=q["hy"] + (z0 - taban(q)))
            elif taban(q) > max(z0, z1):              # zemine gömülmez
                q = dict(q, hy=q["hy"] + (max(z0, z1) - taban(q)))
            kareler.append((t0 + (t1 - t0) * f, q))
    kareler.append(anahtarlar[-1])
    return kareler


def _tg_anim(nitelik, degerler, zamanlar, sure):
    kt = ";".join(f"{t:.4f}" for t in zamanlar)
    return (f'<animate attributeName="{nitelik}" values="{";".join(degerler)}" keyTimes="{kt}" '
            f'dur="{sure}s" begin="0s" fill="freeze" calcMode="linear"/>')


def tg_poz(hx, **k):
    """Temel pozdan türeyen poz (ayakta; kalça yüksekliği ölçeğe göre)."""
    s = k.get("s", 1.0)
    p = {"hx": hx, "hy": TG_ZEMIN - (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s, **TG_TEMEL_POZ}
    p.update(k)
    return p


def tg_yerlestir(p, ayak_x=None, bacak="1", zemin=None):
    """Pozu zemine oturtur: en alttaki ayak noktası (bilek ya da parmak) zemine değer; ayak_x verilirse o ayak bu x'e gelir."""
    zemin = TG_ZEMIN if zemin is None else zemin
    e = tg_eklemler(p)
    q = dict(p, hy=p["hy"] + (zemin - max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))))
    if ayak_x is not None:
        q["hx"] = p["hx"] + (ayak_x - e["ayak" + bacak][0])
    return q


class TgSahne:
    """Tek tuvalde bir test sahnesi. Her öğe hem hareketli hem durağan (son kare) olarak üretilir."""

    def __init__(self, sure=3.0):
        self.sure = sure
        self.ogeler = []          # (hareketli_xml, duragan_xml)
        self.yazi_sayisi = 0
        self.olculer = []         # ölçü okları (x1, y1, x2, y2) — denetim uzunluk > 0 ister
        self.cubuklar = []        # çubuk / çubuk_iki: [(t, x1, y1, x2, y2)] her karede (Paket 25 denetimi)
        self.son_eklemler = None  # ÖLÇÜLEN figürün son karedeki eklemleri — denetim uç mesafesine bakar
        self.tum_eklemler = []    # her figürün her karedeki eklemleri — denetim tuval sınırına bakar
        self.yazi_kutulari = []   # (x0, y0, x1, y1, metin) — denetim çakışmaya bakar
        self.olcu_kayit = []      # {"uc": (x1, y1, x2, y2), "etiket", "metre", "es"} — ölçek ve etiket denetimi
        self.figurler = []        # {"rol", "opaklik", "son"} — ikinci figür denetimi
        self.cizim_sekilleri = [] # (tur, şekil…) son kare geometrisi — yazı ↔ en yakın çizgi denetimi
        self.cizim_kutulari = []  # (x0, y0, x1, y1, tur) son kare: tur "esya" | "figur" | "isaret" (ok, kılavuz, iz)
        self.figur_alani = []     # (x0, y0, x1, y1) figürün bütün karelerdeki alanı — şerit denetimi
        self.zaman_seritleri = [] # periyot şeritleri (x0, x1, y) — süreli testler
        self.sayaclar = []        # sayaç kutuları (x0, y0, x1, y1)
        self.kronometreler = []   # süreölçer simgeleri (x0, y0, x1, y1)
        self.numaralar = []       # sıra numarası rozetleri (n, x, y)
        self.hedefler = []        # vuruş hedefleri (tür, merkez_x, merkez_y)
        # Paket 21: durağan kopya ayrı bir sahne olabilir (kayan tur — Koordinasyon Parkuru). None: durağan = son kare
        self.duragan = None
        self.kayan_kutular = []   # kaydir ile ötelenen öğelerin kutuları (y aralığı; x kaydığı için her yere uğrayabilir)
        self.kaymalar = []        # kaydir anahtarları [(t, dx, dy)] — kayan sahnede hız denetimi
        self.istasyon_araliklari = []   # kayan turda beceri/istasyon pencereleri [(t0, t1)] (0-1)
        self.parkur_kaymasi = []  # kayan turda parkurun kayması [(t, dx)] (tuval x = dünya x + dx) — hız denetimi
        self.donusler = []        # figür grubu dönüşleri: {"t0", "t1", "cx", "cy", "bas_r", "kareler": [(t, eklemler)]}

    def _kaydet(self, xml, tur, dx=0.0, dy=0.0):
        self.cizim_kutulari += [(*k, tur) for k in _tg_xml_kutulari(xml, dx, dy)]
        self.cizim_sekilleri += [(tur, *g) for g in _tg_xml_sekilleri(xml, dx, dy)]

    # ── çizim yardımcıları (renk ve kalınlık yalnız takımdan) ──
    def esya(self, xml, tur="esya"):
        self._kaydet(xml, tur)
        self.ogeler.append((xml, xml))

    def cizgi(self, x1, y1, x2, y2, tur="esya", kesik=False, ok=False):
        """ok=True: iki uçta ok başı; ok="son": yalnız (x2, y2) ucunda."""
        r, k = TG_RENK[tur if tur in TG_RENK else "olcu"], TG_KALINLIK[tur]
        da = ' stroke-dasharray="4 3"' if kesik else (' stroke-dasharray="2 2"' if tur == "kilavuz" else "")
        xml = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{r}" '
               f'stroke-width="{k}" stroke-linecap="round"{da}/>')
        if ok:
            uz = _math.hypot(x2 - x1, y2 - y1) or 1
            ux, uy = (x2 - x1) / uz, (y2 - y1) / uz
            for (qx, qy, sx) in ((x2, y2, 1), (x1, y1, -1))[:1 if ok == "son" else 2]:
                bx, by = qx - sx * ux * 5, qy - sx * uy * 5
                xml += (f'<path d="M{qx:.1f},{qy:.1f} L{bx - uy * 2.2:.1f},{by + ux * 2.2:.1f} '
                        f'L{bx + uy * 2.2:.1f},{by - ux * 2.2:.1f} z" fill="{r}"/>')
        return xml

    def kutu(self, x, y, w, h, dolgu="dolgu", rx=1.5):
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                f'fill="{TG_RENK[dolgu]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')

    def nokta(self, x, y, r=3.2, dolu=False):
        dolgu = TG_RENK["olcu"] if dolu else "none"
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{dolgu}" stroke="{TG_RENK["olcu"]}" '
                f'stroke-width="{TG_KALINLIK["olcu"]}"/>')

    @staticmethod
    def genislik(metin, boy=TG_YAZI):
        """Yazının tuval birimindeki yaklaşık genişliği (yerleşim ve denetim için)."""
        return len(metin) * boy * 0.56

    def _yazi(self, x, y, metin, boy=TG_YAZI, hiza="middle", kalin=False, yer="etiket"):
        self.yazi_sayisi += 1
        w = self.genislik(metin, boy)
        x0 = x - w / 2 if hiza == "middle" else (x if hiza == "start" else x - w)
        self.yazi_kutulari.append((x0, y - boy * 0.72, x0 + w, y + boy * 0.22, metin, y, yer))   # taban, yer: baslik/not/etiket
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{boy}" fill="{TG_RENK["olcu"]}" '
                f'text-anchor="{hiza}"{" font-weight=\'600\'" if kalin else ""}>{_html.escape(metin)}</text>')

    # ── üç yazı yeri: başlık, not, ölçü/işaret etiketi ──
    def baslik(self, metin, t=0.0):
        """Üst şerit (y ∈ [0, 16])."""
        self.belir(self._yazi(TG_TUVAL[0] / 2, 11, metin, TG_BASLIK_YAZI, kalin=True, yer="baslik"), t, tur="isaret")

    def baslik_nobet(self, varsayilan, pencereler):
        """
        Başlık yuvasında nöbetleşe yazı (Paket 25): `varsayilan` pencereler dışında, her (metin, t0, t1)
        penceresinde onun yerine `metin` görünür; pencere bitince başlık geri gelir. Yeni yazı yeri açmaz: yazı
        sayısında ve yerleşim denetiminde TEK yazıdır (en geniş metnin kutusu). self.yuva: denetim için kayıt.
        """
        sayi, k0 = self.yazi_sayisi, len(self.yazi_kutulari)
        xml = [self._yazi(TG_TUVAL[0] / 2, 11, m, TG_BASLIK_YAZI, kalin=True, yer="baslik")
               .replace("<text ", '<text data-yuva="baslik" ', 1)
               for m in [varsayilan] + [p[0] for p in pencereler]]
        kutular = self.yazi_kutulari[k0:]
        del self.yazi_kutulari[k0:]
        self.yazi_kutulari.append(max(kutular, key=lambda k: k[2] - k[0]))
        self.yazi_sayisi = sayi + 1
        self.yuva = {"varsayilan": varsayilan, "pencereler": [tuple(p) for p in pencereler]}
        araliklar = sorted((a, b) for _, a, b in pencereler)
        disari, t = [], 0.0
        for a, b in araliklar:
            if a > t + 1e-9:
                disari.append((t, a))
            t = max(t, b)
        if t < 1 - 1e-9:
            disari.append((t, 1.0))
        for parca, ara in [(xml[0], disari)] + [(x, [(a, b)]) for x, (_, a, b) in zip(xml[1:], pencereler)]:
            self._nobet(parca, ara)

    def _nobet(self, xml, araliklar):
        """xml yalnız araliklar [(t0, t1)] içinde görünür (kesikli opaklık); durağan kopyada sonda görünüyorsa var."""
        zam, deg = [0.0], ["1" if araliklar and araliklar[0][0] <= 1e-9 else "0"]
        for a, b in araliklar:
            if a > 1e-9:
                zam.append(a)
                deg.append("1")
            if b < 1 - 1e-9:
                zam.append(b)
                deg.append("0")
        self._kaydet(xml, "isaret")
        a = _tg_anim("opacity", deg, zam, self.sure).replace('calcMode="linear"', 'calcMode="discrete"')
        sonda = bool(araliklar) and araliklar[-1][1] >= 1 - 1e-9
        self.ogeler.append((f'<g opacity="{deg[0]}">{a}{xml}</g>', xml if sonda else ""))

    def not_(self, metin, t=0.0):
        """Alt şerit (y ∈ [128, 140])."""
        self.belir(self._yazi(TG_TUVAL[0] / 2, 137.5, metin, yer="not"), t, tur="isaret")

    def olcu(self, x1, y1, x2, y2, etiket=None, uc="son", t=0.0, kilavuzlar=(), metre=None, es=None, bag=(),
             etiket_yer="uc", etiket_dx=0):
        """
        Ölçü oku (iki uçlu) + etiket okun bir ucunda. kilavuzlar: [(x1, y1, x2, y2)] kesik kılavuzlar.
        metre: protokoldeki mesafe (ölçek tablosuyla karşılaştırılır). es: etiketsiz ok yalnız etiketli bir
        okun simetrik eşi olabilir (o okun sırası).
        etiket_yer: "uc" (yatay ok: ucun yanında) ya da "orta" (okun ortasında, üstte; etiket_dx ile kaydırılır —
        figür/eşya payı için). Dikey okta etiket ("sol" verilirse solda)
        her zaman okun yanında, ortadadır (sağda; sığmazsa solda).
        bag: [(uç, eksen, eklemler, kural)] — okun bir ucu ölçülen figürün son karesindeki eklemden gelir
        (ör. (1, "y", ("ayak1", "ayak2"), "max") = ikinci ucun y'si en alttaki ayak). Denetim ≤ 2 birim ister.
        """
        self.olculer.append((x1, y1, x2, y2))
        self.olcu_kayit.append({"uc": (x1, y1, x2, y2), "etiket": etiket, "metre": metre, "es": es,
                                "bag": tuple(bag)})
        xml = "".join(self.cizgi(*k, tur="olcu", kesik=True) for k in kilavuzlar)
        xml += self.cizgi(x1, y1, x2, y2, "olcu", ok=True)
        if etiket:
            qx, qy, rx, ry = (x2, y2, x1, y1) if uc == "son" else (x1, y1, x2, y2)
            w = self.genislik(etiket)
            if abs(qx - rx) >= abs(qy - ry) and etiket_yer == "orta":
                xml += self._yazi((x1 + x2) / 2 + etiket_dx, (y1 + y2) / 2 - 5, etiket, kalin=True)
            elif abs(qx - rx) >= abs(qy - ry):      # yatay ok: etiket ucun yanında; sığmazsa ucun üstünde
                sag = qx > rx
                taban = min(qy + 3, TG_SERIT_ALT - 2)
                if (sag and qx + 11 + w <= TG_TUVAL[0] - TG_YAZI_PAYI) or (not sag and qx - 11 - w >= TG_YAZI_PAYI):
                    xml += self._yazi(qx + (11 if sag else -11), taban, etiket, hiza="start" if sag else "end", kalin=True)
                else:
                    xml += self._yazi(qx, qy - 5, etiket, hiza="end" if sag else "start", kalin=True)
            else:                                    # dikey ok: etiket okun yanında, ortada
                orta_y = (y1 + y2) / 2 + 3
                if etiket_yer != "sol" and x1 + 7 + w <= TG_TUVAL[0] - TG_YAZI_PAYI:
                    xml += self._yazi(x1 + 7, orta_y, etiket, hiza="start", kalin=True)
                else:
                    xml += self._yazi(x1 - 7, orta_y, etiket, hiza="end", kalin=True)
        self.belir(xml, t, tur="isaret")

    def isaret(self, etiket, hedef, yazi_xy, hiza="middle", t=0.0):
        """Etiket, ince kesik kılavuzla gösterdiği noktaya bağlı (serbest yazı yok)."""
        hx_, hy_ = hedef
        yx, yy = yazi_xy
        w = self.genislik(etiket)
        if hiza == "start":
            yx = min(yx, TG_TUVAL[0] - TG_YAZI_PAYI - w)
        elif hiza == "end":
            yx = max(yx, TG_YAZI_PAYI + w)
        bag_y = yy + 3 if hy_ > yy else yy - 9
        xml = (self.cizgi(yx, bag_y, hx_, hy_, "kilavuz") + self.nokta(hx_, hy_, 1.8, dolu=True)
               + self._yazi(yx, yy, etiket, hiza=hiza, kalin=True))
        self.belir(xml, t, tur="isaret")

    # ── zamanlı öğeler ──
    def belir(self, xml, t, t2=None, tur="esya"):
        """xml grubu t anında (0-1) belirir ve kalır; t = 0 ise baştan görünür."""
        if t <= 0:
            self.esya(xml, tur)
            return
        self._kaydet(xml, tur)
        t2 = min(1.0, t + 0.06) if t2 is None else t2
        a = _tg_anim("opacity", ["0", "0", "1", "1"], [0, t, t2, 1], self.sure)
        self.ogeler.append((f'<g opacity="1">{a}{xml}</g>', f"<g>{xml}</g>"))

    def goster(self, xml, t0, t1=None, tur="esya"):
        """xml grubu [t0, t1) aralığında görünür (t1 yoksa sona kadar). Durağan kopyada yalnız sonda görünen kalır."""
        if t1 is None or t1 >= 1:
            self.belir(xml, t0, min(1.0, t0 + 1e-3) if t0 > 0 else None, tur)
            return
        self._kaydet(xml, tur)
        deg, zam = (["1", "0", "0"], [0, t1, 1]) if t0 <= 0 else (["0", "1", "0", "0"], [0, t0, t1, 1])
        a = _tg_anim("opacity", deg, zam, self.sure).replace('calcMode="linear"', 'calcMode="discrete"')
        self.ogeler.append((f'<g opacity="0">{a}{xml}</g>', ""))

    def sayac(self, x, y, anlar, boy=16):
        """
        Sayaç — TEK biçim (Paket 19): kutu içinde çetele. anlar'daki her anda bir çizgi belirir (beşincisi dördünü
        çapraz keser). Rakam yazmaz: çizilen çetele sayılan şeyi gösterir, sonucun kendisi değildir.
        Döndürür: kutunun (x0, y0, x1, y1).
        """
        n = len(anlar)
        ara = 3.4
        grup = [min(5, n - 5 * g) for g in range((n + 4) // 5)] or [0]
        gen = 6 + sum(min(k, 4) * ara + 4 for k in grup)
        yuk = boy
        self.esya(self.kutu(x, y, gen, yuk, dolgu="yuzey", rx=1.5))
        kal = TG_KALINLIK["olcu"]
        cx, i = x + 5, 0
        for g, k in enumerate(grup):
            gx = cx
            for j in range(k):
                if j < 4:
                    xml = self.cizgi(cx + j * ara, y + 4, cx + j * ara, y + yuk - 4, "olcu")
                else:                                       # beşinci: dördünü çapraz keser
                    xml = self.cizgi(gx - 1.5, y + yuk - 5, gx + 3 * ara + 1.5, y + 5, "olcu")
                self.belir(xml, anlar[i], min(1.0, anlar[i] + 1e-3), tur="isaret")
                i += 1
            cx += min(k, 4) * ara + 4
        self.sayaclar.append((x, y, x + gen, y + yuk))
        return x, y, x + gen, y + yuk

    def kronometre(self, cx, cy, t0=0.0, r=8, t1=None):
        """
        Süre ölçümü simgesi: kadran + düğme; ibre t0'dan sonra döner, t1 verilirse o anda durur (ör. CAMSA: vuruş).
        Rakam yok (değer gösterilmez).
        """
        kal = TG_KALINLIK["olcu"]
        self.esya(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["olcu"]}" '
                  f'stroke-width="{kal}"/>' + self.cizgi(cx, cy - r - 3, cx, cy - r, "olcu")
                  + self.cizgi(cx - 2.5, cy - r - 3, cx + 2.5, cy - r - 3, "olcu"))
        ibre = self.cizgi(cx, cy, cx, cy - r + 2, "olcu")
        m = f"{cx:.1f} {cy:.1f}"
        if t1 is None:
            an = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};720 {m}" '
                  f'keyTimes="0;{t0:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        else:
            an = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};720 {m};720 {m}" '
                  f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        self._kaydet(ibre, "isaret")
        self.ogeler.append((f'<g>{an}{ibre}</g>', f'<g transform="rotate(300 {cx:.1f} {cy:.1f})">{ibre}</g>'))
        self.kronometreler.append((cx - r, cy - r - 3, cx + r, cy + r))
        return cx - r, cy - r - 3, cx + r, cy + r

    def figur_xml(self, e, rol="partner", s=1.0, cephe=False):
        """
        Tek pozluk figürün DURAĞAN çizimi (animasyonsuz), figur() ile aynı katman ve kalınlık kuralları. Kayan
        parkurun içine konur (ör. CAMSA'da topu atan uygulayıcı); sahneye kendisi eklenmez, figür sayılmaz.
        """
        katman_adi = TG_ROL_KATMANI[rol]
        katman = FIGUR_KATMANI[katman_adi]
        renk, opak = tg_renk(katman["renk"]), katman["opaklik"]
        kademe = 1.0 if s >= 0.9 else (0.8 if s >= 0.75 else 0.7)
        olcek = kademe * katman["incelik"]
        kesik = f' stroke-dasharray="{katman["kesik"]}"' if katman["kesik"] else ""
        parca = _tg_parcalar(e)
        xml = ""
        for ad in ("bacak2", "kol2", "govde", "kusak", "bacak1", "kol1"):
            kal = TG_KALINLIK["govde" if ad == "govde" else "figur"] * olcek
            uzak = not (cephe or ad in ("govde", "kusak", "bacak1", "kol1"))
            o = round(opak * (FIGUR_DERINLIK_OPAKLIK if uzak else 1.0), 3)
            soluk = f' stroke-opacity="{o}"' if o < 1 else ""
            xml += (f'<path d="{parca[ad]}" fill="none" stroke="{renk}" stroke-width="{kal:.2f}" stroke-linecap="round" '
                    f'stroke-linejoin="round"{soluk}{kesik} data-katman="{katman_adi}"'
                    + (' data-derinlik="1"' if uzak else "") + "/>")
        bx, by = e["bas"]
        xml += (f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{_TG_BOY["bas"] * s:.1f}" fill="{renk}" data-katman="{katman_adi}"'
                + (f' fill-opacity="{opak}"' if opak < 1 else "") + "/>")
        return xml

    @property
    def bacaklar(self):
        """Tek tek çizilen gidiş-dönüşlerin görünme aralıkları [(t0, t1)] (Spider, Paket 24)."""
        if not hasattr(self, "_bacaklar"):
            self._bacaklar = []
        return self._bacaklar

    def numara(self, x, y, n, t=0.0, t_bitis=None):
        """
        Sıra numarası rozeti (çok dönüşlü parkur): küçük halka içinde çizilmiş rakam — yazı öğesi değildir.
        Sayaçtan ayrı bir şeydir: bir değer değil, sırayı gösterir.
        """
        r, h, w = 4.6, 4.8, 2.6
        xml = (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["olcu"]}" '
               f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
        ox, oy = x - w / 2, y - h / 2
        u = {"a": (0, 0, w, 0), "b": (w, 0, w, h / 2), "c": (w, h / 2, w, h), "d": (0, h, w, h),
             "e": (0, h / 2, 0, h), "f": (0, 0, 0, h / 2), "g": (0, h / 2, w, h / 2)}
        for b in _TG_RAKAM[n % 10]:
            x1, y1, x2, y2 = u[b]
            xml += (f'<line x1="{ox + x1:.1f}" y1="{oy + y1:.1f}" x2="{ox + x2:.1f}" y2="{oy + y2:.1f}" '
                    f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-linecap="round"/>')
        if t_bitis is None:
            self.belir(xml, t, tur="isaret")
        else:                                   # kayan turda o anki istasyonun numarası (yalnız o aralıkta)
            self.goster(xml, t, t_bitis, tur="isaret")
        self.numaralar.append((n, x, y))

    def kaydir(self, xml, anahtarlar, tur="esya"):
        """xml grubunu [(t, dx, dy)] boyunca öteler; son konumda durur."""
        self._kaydet(xml, tur, anahtarlar[-1][1], anahtarlar[-1][2])
        self.kaymalar.append(list(anahtarlar))
        dys = [dy for _, _, dy in anahtarlar]
        self.kayan_kutular += [(x0, y0 + min(dys), x1, y1 + max(dys)) for x0, y0, x1, y1 in _tg_xml_kutulari(xml, 0, 0)]
        kt = ";".join(f"{t:.4f}" for t, _, _ in anahtarlar)
        deg = [f"{dx:.1f} {dy:.1f}" for _, dx, dy in anahtarlar]
        a = (f'<animateTransform attributeName="transform" type="translate" values="{";".join(deg)}" '
             f'keyTimes="{kt}" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        self.ogeler.append((f'<g transform="translate({deg[-1]})">{a}{xml}</g>',
                            f'<g transform="translate({deg[-1]})">{xml}</g>'))

    def top(self, yol, r=4.0, iz=False):
        """yol: [(t, x, y)] — top bu noktalardan geçer ve son noktada kalır. iz=True: uçuş izi kesik çizgi."""
        x0, y0 = yol[0][1], yol[0][2]
        anahtar = [(0.0, 0.0, 0.0)]
        for t, x, y in yol:
            if t > anahtar[-1][0] + 1e-6:
                anahtar.append((t, x - x0, y - y0))
        if anahtar[-1][0] < 1:
            anahtar.append((1.0, anahtar[-1][1], anahtar[-1][2]))
        self.kaydir(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{r}" fill="{TG_RENK["olcu"]}"/>', anahtar)

    def figur(self, hareket, donus=None):
        """
        Hareket kitaplığından gelen [(t, poz)] anahtarlarıyla figür; son karede durur.
        hareket.olay["rol"] == "partner" (hk_ikinci_figur): daha ince ve soluk çizilir — ölçülen belli olsun.
        """
        anahtarlar = hareket.anahtarlar if hasattr(hareket, "anahtarlar") else hareket
        rol = (hareket.olay.get("rol") if hasattr(hareket, "olay") else None) or "olculen"
        partner = rol in ("partner", "iz")          # iz: aynı sporcunun başlangıç pozu, daha da soluk (Paket 17)
        kareler = _tg_kareler(anahtarlar)
        zam = [t for t, _ in kareler]
        eklemler = [tg_eklemler(p) for _, p in kareler]
        self.tum_eklemler += eklemler
        if not partner:
            self.son_eklemler = eklemler[-1]
        katman_adi = TG_ROL_KATMANI[rol]
        katman = FIGUR_KATMANI[katman_adi]
        opak = katman["opaklik"]
        renk = tg_renk(katman["renk"])
        self.figurler.append({"rol": rol, "opaklik": opak, "son": eklemler[-1],
                              "kareler": list(zip(zam, eklemler)),
                              "bas_r": _TG_BOY["bas"] * anahtarlar[-1][1].get("s", 1.0)})
        s_ = anahtarlar[-1][1].get("s", 1.0)
        pay = TG_KALINLIK["govde"] * max(s_, 0.7) / 2

        def alan(e):
            xs = [p[0] for k, p in e.items()] + [e["bas"][0] - _TG_BOY["bas"] * s_, e["bas"][0] + _TG_BOY["bas"] * s_]
            ys = [p[1] for k, p in e.items()] + [e["bas"][1] - _TG_BOY["bas"] * s_, e["bas"][1] + _TG_BOY["bas"] * s_]
            return min(xs) - pay, min(ys) - pay, max(xs) + pay, max(ys) + pay
        self.cizim_kutulari.append((*alan(eklemler[-1]), "figur"))
        son = eklemler[-1]
        for a, b in _TG_FIGUR_CIZGILERI:
            self.cizim_sekilleri.append(("figur", "cizgi", *son[a], *son[b], TG_KALINLIK["figur"] * (1.0 if s_ >= 0.9 else (0.8 if s_ >= 0.75 else 0.7)) / 2))
        self.cizim_sekilleri.append(("figur", "disk", *son["bas"], _TG_BOY["bas"] * s_))
        tum = [alan(e) for e in eklemler]
        self.figur_alani.append((min(a[0] for a in tum), min(a[1] for a in tum),
                                 max(a[2] for a in tum), max(a[3] for a in tum)))
        parcalar = [_tg_parcalar(e) for e in eklemler]
        cephe = anahtarlar[-1][1].get("cephe", False)
        s = anahtarlar[-1][1].get("s", 1.0)
        kademe = 1.0 if s >= 0.9 else (0.8 if s >= 0.75 else 0.7)    # kalınlık yalnız üç kademede (takım)
        olcek = kademe * katman["incelik"]
        kesik = f' stroke-dasharray="{katman["kesik"]}"' if katman["kesik"] else ""
        hareketli, duragan = [], []
        for ad in ("bacak2", "kol2", "govde", "kusak", "bacak1", "kol1"):
            kal = TG_KALINLIK["govde" if ad == "govde" else "figur"] * olcek
            uzak = not (cephe or ad in ("govde", "kusak", "bacak1", "kol1"))
            o = round(opak * (FIGUR_DERINLIK_OPAKLIK if uzak else 1.0), 3)
            soluk = f' stroke-opacity="{o}"' if o < 1 else ""
            ortak = (f'fill="none" stroke="{renk}" stroke-width="{kal:.2f}" stroke-linecap="round" '
                     f'stroke-linejoin="round"{soluk}{kesik} data-katman="{katman_adi}"'
                     + (' data-derinlik="1"' if uzak else ""))
            son = parcalar[-1][ad]
            hareketli.append(f'<path d="{son}" {ortak}>{_tg_anim("d", [pp[ad] for pp in parcalar], zam, self.sure)}</path>')
            duragan.append(f'<path d="{son}" {ortak}/>')
        r = _TG_BOY["bas"] * s
        bx, by = eklemler[-1]["bas"]
        ortak = (f'r="{r:.1f}" fill="{renk}" data-katman="{katman_adi}"'
                 + (f' fill-opacity="{opak}"' if opak < 1 else ""))
        ax = _tg_anim("cx", [f"{e['bas'][0]:.1f}" for e in eklemler], zam, self.sure)
        ay = _tg_anim("cy", [f"{e['bas'][1]:.1f}" for e in eklemler], zam, self.sure)
        hareketli.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" {ortak}>{ax}{ay}</circle>')
        duragan.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" {ortak}/>')
        if donus:      # (t0, t1, cx, cy): figür grubu bu aralıkta (cx, cy) çevresinde 360° döner (öne takla)
            t0, t1, cx, cy = donus
            m = f"{cx:.1f} {cy:.1f}"
            rot = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};360 {m};360 {m}" '
                   f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
            hareketli = [f"<g>{rot}"] + hareketli + ["</g>"]
            self.donusler.append({"t0": t0, "t1": t1, "cx": cx, "cy": cy, "bas_r": _TG_BOY["bas"] * s,
                                  "kareler": [(t, e) for t, e in zip(zam, eklemler) if t0 - 1e-9 <= t <= t1 + 1e-9]})
        self.ogeler.append(("".join(hareketli), "".join(duragan)))
        return eklemler[-1]

    def cubuk(self, x1, y1, yol, tur="esya", kalinlik="vurgu"):
        """(x1, y1)'de sabit, öbür ucu yol [(t, x, y)] boyunca giden çubuk (ör. dinamometre kolu; ince: zincir)."""
        zam = [t for t, _, _ in yol]
        ax = _tg_anim("x2", [f"{x:.1f}" for _, x, _ in yol], zam, self.sure)
        ay = _tg_anim("y2", [f"{y:.1f}" for _, _, y in yol], zam, self.sure)
        _, xs, ys = yol[-1]
        ortak = (f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{xs:.1f}" y2="{ys:.1f}" stroke="{TG_RENK["esya"]}" '
                 f'stroke-width="{TG_KALINLIK[kalinlik]}" stroke-linecap="round"')
        self._kaydet(f"<line {ortak}/>", tur)
        self.ogeler.append((f"<line {ortak}>{ax}{ay}</line>", f"<line {ortak}/>"))
        self.cubuklar.append([(t, x1, y1, x, y) for t, x, y in yol])

    def cubuk_iki(self, yol, tur="esya", kalinlik="esya"):
        """İki ucu da hareketli çubuk: yol [(t, x1, y1, x2, y2)] (ör. çift palalı kürek sapı). Son karede durur."""
        zam = [k[0] for k in yol]
        anim = "".join(_tg_anim(ad, [f"{k[i]:.1f}" for k in yol], zam, self.sure)
                       for i, ad in ((1, "x1"), (2, "y1"), (3, "x2"), (4, "y2")))
        _, a, b, c, d = yol[-1]
        ortak = (f'x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{TG_RENK["esya"]}" '
                 f'stroke-width="{TG_KALINLIK[kalinlik]}" stroke-linecap="round"')
        self._kaydet(f"<line {ortak}/>", tur)
        self.ogeler.append((f"<line {ortak}>{anim}</line>", f"<line {ortak}/>"))
        self.cubuklar.append([tuple(k) for k in yol])

    def yol(self, noktalar, t=0.0):
        """Güzergâh: ince kesik çizgi (hk_kavisli_yol'un olay["yol"] noktaları)."""
        d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(noktalar))
        self.belir(f'<path d="{d}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
                   f'stroke-dasharray="3 2" stroke-linecap="round"/>', t, tur="isaret")

    def svg(self, hareketli=True, etiket="", sinif="tg-svg"):
        if not hareketli and self.duragan is not None:       # bilerek farklı durağan kompozisyon (Paket 21)
            return self.duragan.svg(False, etiket, sinif)
        w, h = TG_TUVAL
        zemin = (f'<line x1="6" y1="{TG_ZEMIN}" x2="{w - 6}" y2="{TG_ZEMIN}" stroke="{TG_RENK["zemin"]}" '
                 f'stroke-width="{TG_KALINLIK["zemin"]}" stroke-linecap="round"/>')
        ic = "".join(a if hareketli else d for a, d in self.ogeler)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" class="{sinif}" role="img" '
                f'aria-label="{_html.escape(etiket)}" font-family="{_html.escape(YAZI_AILESI.replace(chr(34), ""))}">'
                f'<title>{_html.escape(etiket)}</title>{zemin}{ic}</svg>')


# ── 2) HAREKET KİTAPLIĞI ──
# Her fonksiyon TgHareket döndürür: anahtarlar [(t, poz)] (son anahtar = ölçüm anı) ve olay
# (ölçüm için gereken noktalar/zamanlar: ör. tepe yüksekliği, topun bırakıldığı an ve el konumu).
TgHareket = _namedtuple("TgHareket", ["anahtarlar", "olay"])


# Çeviklik parkurları (metre). Yan eksen zemin boyunca, derinlik zeminin gerisinde ince şeritte (sz küçük);
# dönüş noktaları işaretli, sıralama başlıkta. olcek = (1 m yan eksende kaç birim, 1 m derinlikte kaç birim).
_TG_PARKURLAR = {
    # Illinois: 10 × 5 m, 8 koni (4 köşe + ortada 3,3 m arayla 4); yüzüstü başla, zigzag + slalom (~60 m)
    "illinois": dict(olcek=(17, 2.6), x0=58, s=0.62,
                     koniler=[(0, 0), (10, 0), (0, 5), (10, 5), (0, 2.5), (3.3, 2.5), (6.6, 2.5), (10, 2.5)],
                     yol=[(0, 0.4), (10, 0.4), (0, 2.5), (1.65, 3.3), (4.95, 1.7), (8.25, 3.3), (10, 2.5),
                          (8.25, 1.7), (4.95, 3.3), (1.65, 1.7), (0, 2.5), (10, 4.6), (0, 4.6)],
                     baslangic="yuzustu", dokun=(), donus=(1, 2, 6, 10, 11)),
    # Voleybol (VAT): 9 m yan, 18 m derinlik; ortadan sol ön → sağ ön → sağ arka → sol arka → orta, köşede dokun
    "vat": dict(olcek=(18, 0.75), x0=50, s=0.62,
                koniler=[(0, 0), (9, 0), (9, 18), (0, 18)],
                yol=[(4.5, 9), (0, 0), (9, 0), (9, 18), (0, 18), (4.5, 9)],
                baslangic=None, dokun=(1, 2, 3, 4), donus=(1, 2, 3, 4)),
    # NBA Lane: boya alanı 4,9 m yan × 5,8 m derinlik (koni yok); aşağı → sol → yukarı → sağ → aşağı
    "nba_lane": dict(olcek=(28, 2.4), x0=62, s=0.62, koniler=[],
                     yol=[(4.9, 5.8), (4.9, 0), (0, 0), (0, 5.8), (4.9, 5.8), (4.9, 0)],
                     baslangic=None, dokun=(), donus=(1, 2, 3, 4)),
    # T-testi (Karate KAT, Taekwondo): A başlangıç; B 9,14 m ileride; C ve D B'nin 4,57 m solu/sağı
    "t_testi": dict(olcek=(18, 1.5), x0=48, s=0.62,
                    koniler=[(4.57, 0), (4.57, 9.14), (0, 9.14), (9.14, 9.14)],
                    yol=[(4.57, 0), (4.57, 9.14), (0, 9.14), (9.14, 9.14), (4.57, 9.14), (4.57, 0)],
                    baslangic=None, dokun=(), donus=(1, 2, 3, 4)),          # A→B→C→D→B→A (Semenick 1990)
    # Spider (tenis): tekler kortu 8,23 m; arka çizginin gerisinden 5 topa sırayla, sağdan; her top kareye
    "spider": dict(olcek=(19, 2.0), x0=52, s=0.6, koniler=[],
                   yol=[(4.115, -0.4), (8.23, 0), (4.115, -0.4), (8.23, 5.49), (4.115, -0.4), (4.115, 11.89),
                        (4.115, -0.4), (0, 5.49), (4.115, -0.4), (0, 0), (4.115, -0.4)],
                   baslangic=None, dokun=(1, 3, 5, 7, 9), donus=(1, 3, 5, 7, 9),
                   tek_tek=True,                                  # yalnız o anki gidiş-dönüş çizilir (Paket 24)
                   rozet=[(9, -3), (9, -8), (-13, -6), (-9, -8), (-9, -3)]),   # her rozet kendi topunun dış yanında
    # Squash SIST (Wilkinson ve ark., 2009): kort 6,4 m eni; derinlik arka duvardan (ön duvar 9,75 m); T'den
    # sinyalin gösterdiği köşeye, ayak hedefte, T'ye dönüş. Köşe sırası sinyale göredir — çizimdeki sıra örnektir.
    "sist": dict(olcek=(24, 2.0), x0=54, s=0.6, koniler=[],
                 yol=[(3.2, 4.31), (0, 9.75), (3.2, 4.31), (6.4, 0), (3.2, 4.31), (6.4, 9.75), (3.2, 4.31),
                      (0, 0), (3.2, 4.31)],
                 baslangic=None, dokun=(), donus=(1, 3, 5, 7), tek_tek=True,
                 rozet=[(-9, -6), (9, -3), (9, -6), (-9, -3)]),
    # Ghost Drill (Squash): kort 6,4 m × 9,75 m; T noktasından 6 köşeye sırayla, her köşeden T'ye; köşede raketle duvar
    "ghost": dict(olcek=(26, 1.3), x0=48, s=0.62, koniler=[],
                  yol=[(3.2, 4.3), (0.5, 9.2), (3.2, 4.3), (5.9, 9.2), (3.2, 4.3), (0.5, 4.9), (3.2, 4.3),
                       (5.9, 4.9), (3.2, 4.3), (0.5, 0.6), (3.2, 4.3), (5.9, 0.6), (3.2, 4.3)],
                  baslangic=None, dokun=(1, 3, 5, 7, 9, 11), donus=(1, 3, 5, 7, 9, 11)),
}


# Ölçek tablosu: sahne → (1 m kaç tuval birimi, açıklama). Protokoldeki mesafe okları bu ölçekle çizilir;
# figür (≈ 1,35 m çocuk ≈ 92 birim) ile mesafe ölçeği aynı değilse "şematik" yazılır.
TG_OLCEK = {
    "_tg_surat": (9.5, "şematik: 20 m tuvale sığsın diye figürden küçük ölçek"),
    "_tg_pro_agility": (75 / 4.57, "şematik"),
    "_tg_mekik": (10.0, "şematik"),
    "_tg_goz_el": (46.0, "figürle aynı ölçek (0,66 ölçekli çocuk: 1,32 m ≈ 61 birim)"),
    "_tg_yoyo": (8.0, "şematik"),
    "_tg_paten_30": (6.2, "şematik"),
    "_tg_paten_6_30": (6.2, "şematik"),
    "_tg_s_turn": (12.0, "şematik, yandan: buz yüzeyi zemin çizgisinin gerisinde ince şerit"),
    # Paket 17 — düz sprintte (_tg_sprint) ok şematiktir: 10 m'den 400 m'ye aynı boy, mesafe etikette
    "_tg_hizlanma_profili": (6.4, "şematik"),
    "_tg_rsa": (6.4, "şematik"),
    "_tg_list": (10.0, "şematik"),
    "_tg_30_15": (5.0, "şematik"),
    "_tg_sjft_judo": (23.0, "şematik: iki uke arası 6 m"),
    "_tg_modifiye_barfiks": (30.4, "figürle aynı ölçek (0,85 ölçekli figür; elastik bant bardan 19 cm aşağıda)"),
    "_tg_otur_uzan": (68.0, "şematik: sıfır ile ayak tabanı arası okunsun diye cetvel figürden büyük ölçekte"),
    "_tg_flamingo": (58.0, "figürle aynı ölçek (0,85 ölçekli çocuk)"),
    "_tg_plate_tapping": (61.5, "figürle aynı ölçek (0,9 ölçekli çocuk)"),
    "_tg_top_yakalama": (58.0, "figürle aynı ölçek (0,7 ölçekli çocuk, 3-6 yaş)"),
    "_tg_yan_adim": (25.0, "şematik"),
    "_tg_sicrama_turleri": (35.8, "figürle aynı ölçek (yetişkin ≈ 1,8 m ≈ 64 birim)"),
    "_tg_tenis_servis": (11.0, "şematik: arka çizgiden servis karesine (11,89 + 6,40 m) tuvale sığsın; figür ölçeksiz"),
    "_tg_capl_parkur": (34.5, "figürle aynı ölçek; yalnız skipping 5 m protokolde, öbür aralıklar şematik"),
    "_tg_koordinasyon": (34.5, "figürle aynı ölçek (0,7 ölçekli çocuk ≈ 1,3 m ≈ 45 birim); kayan sahne"),
}


_TG_YOYO_KRITIK = ("20 m çift yön koşu, bip sesiyle artan hız; her turda 10 sn aktif dinlenme (5 m gidip gelme); "
                   "2 kez üst üste bipe yetişemeyen testi bitirir.")


_TG_YOYO2_KRITIK = ("IR1 ile aynı 20 m çift yön format ve 10 sn aktif dinlenme; başlangıç hızı daha yüksek (13 km/h); "
                    "2 kez üst üste bipe yetişemeyen bitirir.")


_TG_WINGATE_KRITIK = ("Ergometrede oturarak, vücut ağırlığının %7,5'i dirençle 30 sn maksimal pedal çevirme; "
                      "pik güç, ortalama güç ve yorgunluk indeksi hesaplanır.")


_TG_WINGATE = {"Wingate 30sn Bisiklet Testi": "", "Wingate (Muay Thai)": "Muay Thai", "Wingate (MMA)": "MMA",
               "Wingate (Kickboks)": "Kickboks"}


_TG_YOYO_IR1 = ["Güreş", "Judo", "Tenis", "Muay Thai", "BJJ", "Badminton", "Masa Tenisi", "Squash", "Karate",
                "Taekwondo", "Boks", "Futbol", "Basketbol", "Voleybol", "Hentbol", "Genel"]


# Hangi sahne hangi hareketi kullanıyor (sonraki testler için kitaplık haritası; denetim de bakar)
TG_HAREKET_KITAPLIGI = ("hk_duz_kos", "hk_donuslu_kos", "hk_dikey_sicrama", "hk_yana_sicrama", "hk_tek_ayak_sekme",
                        "hk_ikinci_figur", "hk_kavisli_yol", "hk_paten", "hk_tutus", "hk_pedal",
                        "hk_nordic", "hk_dinamometre", "hk_iz", "hk_sicrama_ani",
                        "hk_iki_uke_atis", "hk_uchikomi", "hk_vurus", "hk_asilma", "hk_yan_adim",
                        "hk_uzun_atlama", "hk_mekik", "hk_sinav", "hk_modifiye_barfiks", "hk_govde_kaldirma",
                        "hk_flamingo", "hk_masa_dokunma", "hk_omuz_esneme", "hk_omuz_rotasyon", "hk_top_sektirme",
                        "hk_top_yakala", "hk_asilma_bukumlu",
                        "hk_atma", "hk_kavrama", "hk_oturarak_uzanma", "hk_denge", "hk_antropometri",
                        "hk_takla", "hk_alttan_gec", "hk_engel_ustu", "hk_egil_al", "hk_koordinasyon_turu",
                        "hk_yana_kayma", "hk_skipping", "hk_topa_vurus", "hk_camsa_turu",
                        "hk_servis", "hk_serbest_stil", "hk_split",
                        "hk_kurek_ergometre", "hk_kayak_ergometre", "hk_koparma", "hk_silkme", "hk_eggbeater_sicrama",
                        "hk_bench_press", "hk_arka_comelme", "hk_leg_press", "hk_sargent")


def tg_kabugu(anahtar):
    """Gösterilecek görselin anahtarı (test, tekrar sayacı) öncekinden farklıysa kabuğu çevirir."""
    if st.session_state.get("tg_son_anahtar") != anahtar:
        st.session_state["tg_son_anahtar"] = anahtar
        st.session_state["tg_kabuk"] = 1 - st.session_state.get("tg_kabuk", 0)
    return st.session_state.get("tg_kabuk", 0)
