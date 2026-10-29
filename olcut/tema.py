"""
Görsel sistem (Paket 11): renk, yazı ve boşluk kararlarının tek kaynağı — açık/koyu palet, CSS değişkenleri,
Plotly tema yuvaları (grafik_renk), kategori rozetleri, logo, Streamlit config.toml ve tasarimi_uygula.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import os
import streamlit as st


UYGULAMA_ADI = "Ölçüt"                                   # Paket 11 kimlik kararı (Ertuğrul, 15.10.2026)


UYGULAMA_ALT = "Sporcu performansı · yaşa ve cinsiyete göre karşılaştırma"


# ── Renk simgeleri — açık tema ──
RENK = {
    "murekkep": "#1B2430",   # gövde metni, başlıklar
    "ikincil":  "#5A6472",   # açıklama, etiket, kaynak satırı
    "zemin":    "#F6F5F1",   # sayfa arka planı (sıcak kâğıt)
    "yuzey":    "#FFFFFF",   # kart, giriş alanı, kenar çubuğu
    "cizgi":    "#DEDBD2",   # kenarlık, ayırıcı, ölçerin boş dilimi
    "ana":      "#1D4E89",   # düğme, bağlantı, seçili öğe, grafik serisi
    "ikinci":   "#9A5B3F",   # test görsellerinde İKİNCİ KİŞİ (partner, manken, rakip, uke) — yalnız bu anlamda
}


# ── Koyu tema karşılıkları (Paket 34) — aynı anlamlar; metin/zemin ≥ 4.5:1 ──
RENK_KOYU = {
    "murekkep": "#E4E7EB",   # zeminde 14.6:1
    "ikincil":  "#A7B0BC",   # zeminde 8.3:1
    "zemin":    "#12161C",
    "yuzey":    "#1B2129",
    "cizgi":    "#353D49",
    "ana":      "#5590D6",   # bağlantı zeminde 5.5:1, yüzeyde 4.9:1
    "ikinci":   "#D6926F",
}


# ── Test görsellerinde figür katmanları (Paket 18): her görsel kod TEK anlam taşır ──
# Aynı soluk gri üç ayrı şey için kullanılıyordu (uzak uzuv, ikinci kişi, önceki an). Artık üç ayrı kod var:
#   derinlik    — aynı kişinin uzaktaki kolu/bacağı: AYNI renk, opaklık FIGUR_DERINLIK_OPAKLIK, aynı kalınlık.
#   ikinci_kisi — partner, manken, rakip, uke: AYRI RENK TONU (RENK["ikinci"]), tam opak, biraz ince.
#   onceki_an   — aynı sporcunun daha önceki pozu (iz): aynı renk, çok soluk, belirgin ince ve kesik çizgi.
# Bütün sahneler bu tabloyu kullanır; sahne içinde opaklık/kalınlık/renk elle verilmez.
FIGUR_KATMANI = {
    "olculen":     {"renk": "murekkep", "opaklik": 1.0, "incelik": 1.0, "kesik": None},
    "ikinci_kisi": {"renk": "ikinci",   "opaklik": 1.0, "incelik": 0.8, "kesik": None},
    "onceki_an":   {"renk": "murekkep", "opaklik": 0.25, "incelik": 0.5, "kesik": "2 2"},
}


FIGUR_DERINLIK_OPAKLIK = 0.45   # uzak uzuv (her katmanda katmanın kendi opaklığıyla çarpılır)


# ── Yazı ölçeği (4 kademe) ──
YAZI_AILESI = '"Source Sans 3", "Source Sans Pro", "Segoe UI", system-ui, -apple-system, sans-serif'


YAZI = {                       # (boyut, kalınlık)
    "baslik":    ("1.75rem", 700),    # sayfa başlığı
    "altbaslik": ("1.25rem", 600),    # bölüm başlığı
    "govde":     ("1rem", 400),       # metin, giriş
    "etiket":    ("0.875rem", 600),   # alan adı, kaynak, rozet — Paket 38a: en küçük metin 14 px
}


# ── Boşluk birimi: her aralık bunun katı ──
BOSLUK = 8  # px


def b(n):
    """n boşluk birimi (CSS uzunluğu)."""
    return f"{n * BOSLUK}px"


# ── Normatif renk skalası (6 kategori) ──
# Koyudan açığa: Üstün en koyu, Çok Düşük en açık. Renk tek başına anlam taşımaz:
# kategori adı her zaman yazılır ve 6 dilimli ölçer seviyeyi ayrıca gösterir.
# Doğrulama (Paket 11): gri tonlamada komşu kategoriler arası ΔE ≥ 11, L* tekdüze artar
# (25 → 38 → 49 → 66 → 76 → 90); döteranopi/protanopi/tritanopi simülasyonunda sıra korunur;
# her rozette yazı/zemin kontrastı ≥ 4.5:1 (WCAG AA).
NORM_SKALASI = [   # (kategori, seviye 6 = en iyi, zemin, yazı)
    ("Üstün",         6, "#0A4433", "#FFFFFF"),
    ("İyi",           5, "#1F6646", "#FFFFFF"),
    ("Ortalama Üstü", 4, "#468343", "#FFFFFF"),
    ("Ortalama Altı", 3, "#B89E35", "#1F1806"),
    ("Düşük",         2, "#EFAE80", "#3D1F0C"),
    ("Çok Düşük",     1, "#FCDCD6", "#8A2318"),
]


# Koyu zeminde öne çıkan açık renktir: sıra tersine döner (Üstün en açık, Çok Düşük en koyu), tonlar aynı aileden.
# L* 86 → 74 → 62 → 51.6 → 39 → 26 (komşular arası ≥ 10); her rozette yazı/zemin ≥ 4.5:1.
NORM_SKALASI_KOYU = [
    ("Üstün",         6, "#7AECCA", "#04261A"),
    ("İyi",           5, "#53CB95", "#03190F"),
    ("Ortalama Üstü", 4, "#45AA41", "#071406"),
    ("Ortalama Altı", 3, "#8E7A28", "#0D0A01"),
    ("Düşük",         2, "#924712", "#FCE9DD"),
    ("Çok Düşük",     1, "#781A09", "#FCDCD6"),
]


# Başka norm sistemlerinin kategori adları aynı skalaya oturur (renk = performans düzeyi):
KATEGORI_ESDEGER = {"Ortalama": "Ortalama Üstü",      # Alman DMT, P40-P60
                    "Mükemmel": "Üstün", "Orta": "Ortalama Üstü", "Zayıf": "Düşük",
                    # FitnessGram kriter normu (Paket 20): iki bölge, renk skaladan
                    "Sağlıklı Uygunluk Zonu": "İyi", "Gelişim Gerekli": "Düşük"}


# Antropometrik (nötr) ölçüler iyi/kötü değildir: tek nötr renk, ölçerde yalnızca konum.
NOTR_SKALA = {"zemin": "#E6EAF0", "yazi": "#26334A", "isaret": "#55657D"}


NOTR_SIRA = ["Çok Düşük", "Düşük", "Ortalama (alt yarı)", "Ortalama (üst yarı)", "Yüksek", "Çok Yüksek"]


BILINMEYEN_SKALA = {"zemin": "#ECEBE6", "yazi": "#3B4350"}


# ── Veri serisi ve rapor vurguları (kategori skalasıyla karışmayan tonlar) ──
SERI_RENKLERI = ["#C2621B", "#6E4A9E", "#2B7A8C"]   # branş grubu katmanları (radar)


RAPOR_VURGU = {"sevgi": "#B4547A", "fiziksel": "#2B7A8C", "yildiz": "#A86B12",
               "yildiz_zemin": "#FBF3E2", "not_zemin": "#EDF2F8", "uyari": "#B5531C", "uyari_zemin": "#FBEFE6"}


NOTR_SKALA_KOYU = {"zemin": "#2A3546", "yazi": "#D7E0EC", "isaret": "#8DA2BF"}


BILINMEYEN_SKALA_KOYU = {"zemin": "#2B2F36", "yazi": "#D2D6DC"}


SERI_RENKLERI_KOYU = ["#E0894A", "#A98AD6", "#4FB4C7"]


RAPOR_VURGU_KOYU = {"sevgi": "#D97FA3", "fiziksel": "#4FB4C7", "yildiz": "#D9A441",
                    "yildiz_zemin": "#33291A", "not_zemin": "#1C2633", "uyari": "#E08A55", "uyari_zemin": "#36241A"}


TEMALAR = ("acik", "koyu")


def palet(tema="acik"):
    """
    TEK YARDIMCI: hangi paletin kullanıldığı. {"renk", "norm", "notr", "bilinmeyen", "seri", "vurgu"}.
    Uygulama içi HTML/SVG temayı bilmez: renk_css() / tg_renk() CSS değişkeni yazar (yedeği açık palet);
    raporlar kâğıda basılan bağımsız belge olduğu için palet("acik") kullanır; grafikler grafik_renk() ile
    Streamlit'in tema yuvalarına bağlanır. Üçü de buradan beslenir.
    """
    if tema not in TEMALAR:
        raise ValueError(f"Bilinmeyen tema: {tema}")
    k = tema == "koyu"
    return {"renk": RENK_KOYU if k else RENK, "norm": NORM_SKALASI_KOYU if k else NORM_SKALASI,
            "notr": NOTR_SKALA_KOYU if k else NOTR_SKALA, "bilinmeyen": BILINMEYEN_SKALA_KOYU if k else BILINMEYEN_SKALA,
            "seri": SERI_RENKLERI_KOYU if k else SERI_RENKLERI, "vurgu": RAPOR_VURGU_KOYU if k else RAPOR_VURGU}


def _css_degiskenleri(tema):
    """Bir temanın CSS değişkenleri {ad: değer}: --sp-* (sayfa bileşenleri), --tg-* (test görselleri)."""
    p = palet(tema)
    d = {f"--sp-{a}": v for a, v in p["renk"].items()}
    for _, sev, zemin, yazi in p["norm"]:
        d[f"--sp-norm-{sev}-zemin"], d[f"--sp-norm-{sev}-yazi"] = zemin, yazi
    d.update({f"--sp-notr-{a}": v for a, v in p["notr"].items()})
    d.update({f"--sp-bilinmeyen-{a}": v for a, v in p["bilinmeyen"].items()})
    d.update({f"--tg-{a}": p["renk"][a] for a in TG_DEGISKENLERI})
    return d


TG_DEGISKENLERI = ("murekkep", "yuzey", "ana", "cizgi", "ikincil", "ikinci")   # test görsellerinin altı rengi


def renk_css(ad):
    """Sayfa bileşeni rengi: var(--sp-ad, açık yedek) — tarayıcı temaya göre çözer."""
    return f"var(--sp-{ad}, {palet('acik')['renk'][ad]})"


def tg_renk(ad):
    """Test görseli rengi: var(--tg-ad, açık yedek). Değişken tanımsızsa (rapor, dışa aktarım) figür yine görünür."""
    return f"var(--tg-{ad}, {palet('acik')['renk'][ad]})"


def _norm_css(seviye, parca, yedek):
    return f"var(--sp-norm-{seviye}-{parca}, {yedek})"


def tema_degiskenleri_css():
    """
    :root'ta iki temanın değişkenleri: varsayılan açık; sistem koyuysa (prefers-color-scheme) koyu; Streamlit'in
    seçtiği tema her şeyin önünde — Streamlit uygulama kabuğuna color-scheme yazar, light-dark() onu izler.
    """
    acik, koyu = _css_degiskenleri("acik"), _css_degiskenleri("koyu")
    satir = lambda d: " ".join(f"{k}:{v};" for k, v in d.items())
    secici = "; ".join(f"{k}:light-dark({acik[k]}, {koyu[k]})" for k in acik) + ";"
    return (f":root {{ {satir(acik)} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root {{ {satir(koyu)} }} }}\n"
            f'@supports (color: light-dark(#000, #fff)) {{ [data-testid="stApp"] {{ {secici} }} }}\n')


# ── Grafik renk yuvaları (Paket 34): Streamlit, Plotly şekline gömülü "#000001"… yer tutucularını tarayıcıda o
# anki temanın chartCategoricalColors / chartSequentialColors değeriyle değiştirir. Yuvaların dolduğu yer
# config.toml'un [theme.light] / [theme.dark] bölümleridir (tema_toml); Python tarafı temayı bilmez.
GRAFIK_YUVALARI = ("ana", "ikincil", "murekkep", "cizgi", "seri0", "seri1", "seri2")


def _grafik_yuvasi_renkleri(tema):
    """10 kategorik yuva (Streamlit onu bekler): adlı 7 yuva + "ikinci" + iki seri (varsayılan renk sırası için)."""
    p = palet(tema)
    adli = [p["renk"][a] if a in p["renk"] else p["seri"][int(a[-1])] for a in GRAFIK_YUVALARI]
    return adli + [p["renk"]["ikinci"], p["seri"][0], p["seri"][1]]


def _grafik_sira_renkleri(tema):
    """10'lu sıralı yuva: 1-6 normatif seviye zeminleri (Çok Düşük → Üstün), kalan 4 yuva Üstün."""
    z = [zemin for _, _, zemin, _ in sorted(palet(tema)["norm"], key=lambda x: x[1])]
    return z + [z[-1]] * 4


def grafik_renk(ad):
    """
    Plotly rengi: temanın kategorik yuvası (ör. "ana" → "#000001"), HER ZAMAN 6 haneli. Paket 35d: 8 haneli
    (#RRGGBBAA) çıktı kaldırıldı — eski Plotly doğrulayıcısı reddediyor (ValueError, fillcolor). Saydamlık iz
    düzeyinde opacity ile verilir; rgba() kullanılmaz (Streamlit yalnız "#00000N" yer tutucusunu temaya çevirir).
    """
    return f"#{GRAFIK_YUVALARI.index(ad) + 1:06d}"


def grafik_norm_renk(kategori):
    """Normatif kategorinin Plotly rengi: temanın sıralı yuvası (seviye 1 → 1. yuva)."""
    sev = kategori_bilgisi(kategori)["seviye"]
    return f"#{10 + sev:06d}" if sev else grafik_renk("cizgi")


def kategori_bilgisi(kategori, notr=False, tema=None):
    """
    Kategori → {seviye (1-6 ya da None), zemin, yazi, notr}. Tek kaynak: palet()["norm"].
    tema=None: CSS değişkeni (uygulamada temayı izler, değişken yoksa açık yedek); "acik"/"koyu": o paletin hex'i.
    """
    p = palet(tema or "acik")
    c = (lambda d, h: h) if tema else (lambda d, h: f"var(--sp-{d}, {h})")
    if notr:
        sev = NOTR_SIRA.index(kategori) + 1 if kategori in NOTR_SIRA else None
        return {"seviye": sev, "zemin": c("notr-zemin", p["notr"]["zemin"]),
                "yazi": c("notr-yazi", p["notr"]["yazi"]), "notr": True}
    ad = KATEGORI_ESDEGER.get(kategori, kategori)
    for k, sev, zemin, yazi in p["norm"]:
        if k == ad:
            return {"seviye": sev, "zemin": c(f"norm-{sev}-zemin", zemin), "yazi": c(f"norm-{sev}-yazi", yazi),
                    "notr": False}
    return {"seviye": None, "zemin": c("bilinmeyen-zemin", p["bilinmeyen"]["zemin"]),
            "yazi": c("bilinmeyen-yazi", p["bilinmeyen"]["yazi"]), "notr": False}


def kategori_rengi(kategori, notr=False, tema="acik"):
    """Kategorinin zemin rengi (hex) — sonuç kayıtlarında ve dışa aktarımda."""
    return kategori_bilgisi(kategori, notr, tema)["zemin"]


def kategori_rozeti(kategori, notr=False):
    """Renkli rozet; kategori adı her zaman içinde yazılı."""
    k = kategori_bilgisi(kategori, notr)
    return (f'<span class="sp-rozet" style="background:{k["zemin"]};color:{k["yazi"]}">'
            f'{_html.escape(str(kategori))}</span>')


def seviye_olcer(kategori, notr=False):
    """6 dilimli ölçer: performansta soldan dolan çubuk, nötr ölçüde yalnızca konum işareti."""
    k = kategori_bilgisi(kategori, notr)
    if k["seviye"] is None:
        return ""
    dilimler = []
    for i in range(1, 7):
        if k["notr"]:
            renk = renk_css("cizgi") if i != k["seviye"] else f"var(--sp-notr-isaret, {palet()['notr']['isaret']})"
        else:   # en soluk kategorinin zemini yüzeyde kaybolur: o kategoride yazı rengi
            renk = (k["zemin"] if k["seviye"] != 1 else k["yazi"]) if i <= k["seviye"] else renk_css("cizgi")
        dilimler.append(f'<i style="background:{renk}"></i>')
    aria = f"konum {k['seviye']}/6" if k["notr"] else f"seviye {k['seviye']}/6"
    return (f'<span class="sp-olcer" role="progressbar" aria-valuenow="{k["seviye"]}" aria-valuemin="1" '
            f'aria-valuemax="6" aria-label="{aria}" title="{aria}">{"".join(dilimler)}</span>')


_AYRILMA_EKI = {1: "inden", 2: "sinden", 3: "ünden", 4: "ünden", 5: "inden", 6: "sından", 7: "sinden",
                8: "inden", 9: "undan", 10: "undan", 20: "sinden", 30: "undan", 40: "ından", 50: "sinden",
                60: "ından", 70: "inden", 80: "inden", 90: "ından", 0: "ından", 100: "ünden"}


def yuzde_ayrilma(n):
    """'%3'ünden', '%62'sinden', '%40'ından' — Türkçe ünlü uyumuyla (sayının okunuşuna göre)."""
    n = int(n)
    anahtar = 100 if n == 100 else (n % 10 if n % 10 else (n if n else 0))
    return f"%{n}'{_AYRILMA_EKI[anahtar]}"


def _sayi_goster(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return _html.escape(str(x))
    return f"{f:.2f}".rstrip("0").rstrip(".") if abs(f - round(f)) > 1e-9 else f"{f:.0f}"


def sonuc_karti_html(ad, deger, birim="", kategori=None, notr=False, persentil=None, kaynak="",
                     notlar=(), ek="", sade=False):
    """
    TEK SONUÇ KARTI — uygulamada ve raporlarda bir ölçüm sonucu yalnızca bununla gösterilir.
    ad: değişken adı · deger + birim · kategori (rozet + ölçer) · persentil: performans
    persentili (sade=True ise gösterilmez: veli dili) · kaynak: kısa norm dayanağı ·
    notlar: kartta kalması gereken uyarılar · ek: teknik satır (antrenör raporu).
    """
    k = kategori_bilgisi(kategori, notr) if kategori else None
    serit = k["zemin"] if k and k["seviye"] else renk_css("cizgi")
    if k and not notr and k["seviye"] == 1:
        serit = k["yazi"]                # en soluk zeminde şerit görünür kalsın
    p = [f'<div class="sp-kart" style="border-left-color:{serit}">']
    p.append(f'<div class="sp-kart-ust"><span class="sp-etiket">{_html.escape(str(ad))}</span>'
             f'{seviye_olcer(kategori, notr) if kategori else ""}</div>')
    p.append(f'<div class="sp-deger">{_sayi_goster(deger)}'
             f'{f"<span class=sp-birim>{_html.escape(str(birim))}</span>" if birim else ""}</div>')
    alt = []
    if kategori:
        alt.append(kategori_rozeti(kategori, notr))
    if persentil is not None and not sade:
        p_i = int(round(float(persentil)))
        yorum = (f"akranlarının ~{yuzde_ayrilma(p_i)} yüksek" if notr else f"akranlarının ~{yuzde_ayrilma(p_i)} iyi")
        alt.append(f'<span class="sp-pers" title="Performans persentili">P{p_i} · {yorum}</span>')
    if alt:
        p.append(f'<div class="sp-kart-alt">{"".join(alt)}</div>')
    for n in notlar:
        if n:
            p.append(f'<div class="sp-not">{_html.escape(str(n))}</div>')
    if ek:
        p.append(f'<div class="sp-ek">{_html.escape(str(ek))}</div>')
    if kaynak:
        p.append(f'<div class="sp-kaynak">{_html.escape(str(kaynak))}</div>')
    p.append("</div>")
    return "".join(p)


def logo_svg(boyut=40, tema=None):
    """
    Ölçüt simgesi: normatif skalanın 6 rengi, soldan sağa yükselen 6 çubuk (en soluktan en güçlüye).
    tema=None: CSS değişkeni (uygulamada temayı izler); "acik"/"koyu": hex (favicon gibi bağımsız görüntü).
    """
    seviyeler = [kategori_bilgisi(k, tema=tema) for k in ("Çok Düşük", "Düşük", "Ortalama Altı", "Ortalama Üstü",
                                                            "İyi", "Üstün")]
    renkler = [s["yazi"] if s["seviye"] == 1 else s["zemin"] for s in seviyeler]   # en soluk zemin kaybolmasın
    yuzey, cizgi = ((palet(tema)["renk"]["yuzey"], palet(tema)["renk"]["cizgi"]) if tema
                    else (renk_css("yuzey"), renk_css("cizgi")))
    cubuklar = []
    for i, renk in enumerate(renkler):
        h = 8 + i * 5.6
        cubuklar.append(f'<rect x="{6.5 + i * 6}" y="{41 - h:.1f}" width="4" height="{h:.1f}" rx="1.2" fill="{renk}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{boyut}" height="{boyut}" viewBox="0 0 48 48" '
            f'role="img" aria-label="{UYGULAMA_ADI}">'
            f'<rect x="0.5" y="0.5" width="47" height="47" rx="10" fill="{yuzey}" stroke="{cizgi}"/>'
            f'{"".join(cubuklar)}</svg>')


def logo_veri_url():
    import base64
    return "data:image/svg+xml;base64," + base64.b64encode(logo_svg(64, tema="acik").encode("utf-8")).decode("ascii")


ACILIS_TANIM = ("Çocukların ve sporcuların test sonuçlarını, aynı yaş ve cinsiyetteki akranlarının "
                "sonuçlarıyla karşılaştırır.")


def kimlik_html():
    return (f'<div class="sp-kimlik">{logo_svg(44)}<div><b>{_html.escape(UYGULAMA_ADI)}</b>'
            f'<span>{_html.escape(UYGULAMA_ALT)}</span></div></div>')


def kart_izgarasi_html(kartlar):
    return f'<div class="sp-izgara">{"".join(kartlar)}</div>'


# ── Ortak bileşen CSS'i (uygulama + raporlar aynı dosyadan) ──
BILESEN_CSS = f"""
.sp-kart {{ background:{renk_css("yuzey")}; border:1px solid {renk_css("cizgi")}; border-left:{b(0.75)} solid;
           border-radius:{b(1)}; padding:{b(1.5)} {b(2)}; margin:0 0 {b(1.5)}; color:{renk_css("murekkep")};
           break-inside:avoid; }}
.sp-kart-ust {{ display:flex; justify-content:space-between; align-items:center; gap:{b(1)}; }}
.sp-etiket {{ font-size:{YAZI["etiket"][0]}; font-weight:{YAZI["etiket"][1]}; color:{renk_css("ikincil")};
             letter-spacing:.01em; }}
.sp-deger {{ font-size:{YAZI["baslik"][0]}; font-weight:{YAZI["baslik"][1]}; line-height:1.15;
            margin:{b(0.5)} 0 {b(1)}; font-variant-numeric:tabular-nums; }}
.sp-birim {{ font-size:{YAZI["govde"][0]}; font-weight:400; color:{renk_css("ikincil")}; margin-left:{b(0.5)}; }}
.sp-kart-alt {{ display:flex; flex-wrap:wrap; align-items:center; gap:{b(1)}; }}
.sp-rozet {{ display:inline-block; font-size:{YAZI["etiket"][0]}; font-weight:700; line-height:1;
            padding:{b(0.625)} {b(1.25)}; border-radius:999px; white-space:nowrap; }}
.sp-pers {{ font-size:{YAZI["etiket"][0]}; color:{renk_css("ikincil")}; font-variant-numeric:tabular-nums; }}
.sp-olcer {{ display:inline-flex; gap:3px; flex:none; }}
.sp-olcer i {{ display:block; width:{b(1.25)}; height:{b(1)}; border-radius:2px; }}
.sp-not {{ font-size:{YAZI["etiket"][0]}; color:{renk_css("murekkep")}; background:{renk_css("zemin")};
          border-radius:{b(0.5)}; padding:{b(0.5)} {b(1)}; margin-top:{b(1)}; }}
.sp-ek {{ font-size:{YAZI["etiket"][0]}; color:{renk_css("ikincil")}; margin-top:{b(1)};
         font-variant-numeric:tabular-nums; }}
.sp-kaynak {{ font-size:{YAZI["etiket"][0]}; font-weight:400; color:{renk_css("ikincil")}; margin-top:{b(1)};
             border-top:1px solid {renk_css("cizgi")}; padding-top:{b(0.75)}; }}
.sp-izgara {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:{b(1.5)}; }}
.sp-izgara .sp-kart {{ margin:0; }}
.sp-kimlik {{ display:flex; align-items:center; gap:{b(1.5)}; margin:0 0 {b(2)}; }}
.sp-kimlik b {{ display:block; font-size:{YAZI["altbaslik"][0]}; font-weight:700; color:{renk_css("murekkep")};
               line-height:1.1; }}
.sp-kimlik span {{ display:block; font-size:{YAZI["etiket"][0]}; color:{renk_css("ikincil")}; margin-top:2px; }}
.tg-kap {{ display:block; background:{tg_renk("yuzey")}; border:1px solid {renk_css("cizgi")}; border-radius:{b(1)}; padding:{b(0.5)}; }}
.tg-svg {{ display:block; height:140px; width:auto; max-width:100%; margin:0 auto; }}
.tg-svg.tg-buyuk {{ height:auto; width:100%; max-width:720px; }}
.tg-duragan {{ display:none; }}
@media (prefers-reduced-motion: reduce) {{ .tg-hareketli {{ display:none; }} .tg-duragan {{ display:block; }} }}
.sp-acilis {{ display:flex; align-items:center; gap:{b(2.5)}; margin:{b(2)} 0 {b(1)}; }}
.sp-acilis h1 {{ margin:0 !important; padding:0 !important; }}
.sp-acilis p {{ margin:{b(0.5)} 0 0; color:{renk_css("ikincil")}; font-size:{YAZI["govde"][0]}; max-width:560px; }}
.sp-lejant {{ display:flex; flex-wrap:wrap; gap:{b(0.75)}; align-items:center; margin:{b(0.5)} 0 {b(1.5)}; }}
[class*="st-key-kars-sutun"] [data-testid="stCheckbox"] label {{ min-height:44px; align-items:center; }}
[class*="st-key-kars-sutun"] button {{ min-height:44px; }}
.kars-pasif {{ border:2px dashed {renk_css("cizgi")}; border-radius:{b(1)}; padding:{b(3)} {b(2)}; text-align:center;
              color:{renk_css("ikincil")}; font-size:{YAZI["govde"][0]}; }}
"""


# ── Uygulama kabuğu CSS'i (yalnız Streamlit) ──
TEMA_CSS = f"""
<style>
{tema_degiskenleri_css()}html, body, [data-testid="stAppViewContainer"] {{ font-family:{YAZI_AILESI}; }}
[data-testid="stMainBlockContainer"] {{ padding-top:{b(4)}; padding-bottom:{b(8)}; max-width:1240px; }}
h1, h2 {{ font-size:{YAZI["baslik"][0]} !important; font-weight:{YAZI["baslik"][1]} !important;
         color:{renk_css("murekkep")}; letter-spacing:-0.01em; }}
h3 {{ font-size:{YAZI["altbaslik"][0]} !important; font-weight:{YAZI["altbaslik"][1]} !important; }}
h4, h5, h6 {{ font-size:{YAZI["govde"][0]} !important; font-weight:{YAZI["altbaslik"][1]} !important; }}
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {{ color:{renk_css("ikincil")}; }}
[data-testid="stWidgetLabel"] p {{ font-size:{YAZI["etiket"][0]}; font-weight:{YAZI["etiket"][1]}; }}
[data-testid="stMetricValue"] {{ font-variant-numeric:tabular-nums; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {{ font-size:{YAZI["govde"][0]}; font-variant-numeric:tabular-nums; }}
[data-testid="stExpander"] details {{ border-color:{renk_css("cizgi")}; background:{renk_css("yuzey")}; }}
[data-testid="stSidebar"] {{ border-right:1px solid {renk_css("cizgi")}; }}
hr {{ border-color:{renk_css("cizgi")} !important; margin:{b(2)} 0 !important; }}
.sp-bolum {{ font-size:{YAZI["etiket"][0]}; font-weight:{YAZI["etiket"][1]}; color:{renk_css("ikincil")};
            letter-spacing:.06em; margin:{b(1)} 0 {b(1)}; }}
/* Paket 38a — erişilebilirlik: Deploy menüsü yok; düğmeler ≥ 44 px; klavye odağı görünür; en küçük yazı 14 px */
[data-testid="stAppDeployButton"], [data-testid="stDeployButton"] {{ display:none !important; }}
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button, [data-testid="stPopover"] button,
[data-testid="stFormSubmitButton"] button {{ min-height:44px; min-width:44px; }}
*:focus-visible {{ outline:3px solid {renk_css("ana")} !important; outline-offset:2px; }}
/* Paket 38d: metin/sayı/tarih kutusu ve açılır listede odak çerçevesi DIŞ kutuda (tek çerçeve); içteki input,
   tarih parçası ya da düğme ikinci çerçeve çizmez. Streamlit'in yeni (react-aria) ve eski (baseweb) yapısı birlikte. */
:is([data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stDateInputField"],
    [data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [role="group"],
    [data-testid="stMultiSelect"] [role="group"], [data-baseweb="input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div) :focus-visible {{ outline:none !important; }}
:is([data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stDateInputField"],
    [data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [role="group"],
    [data-testid="stMultiSelect"] [role="group"], [data-baseweb="input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div):has(:focus-visible) {{ outline:3px solid {renk_css("ana")} !important;
    outline-offset:2px; }}
[data-testid="stCaptionContainer"], [data-testid="stTooltipContent"], [data-testid="stMarkdownContainer"] small
{{ font-size:{YAZI["etiket"][0]}; }}
/* Paket 38b — Test Oturumu: adım şeridi, ilerleme, sıra çipleri, büyük sayı alanı, sabit alt çubuk */
.ot-gizli {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }}
.ot-serit {{ margin:0 0 {b(2)}; }}
.ot-serit ol {{ display:flex; flex-wrap:wrap; gap:{b(1)}; list-style:none; padding:0; margin:{b(1)} 0 0; }}
.ot-adim {{ font-size:{YAZI["govde"][0]}; padding:6px 18px 6px 14px !important; border-radius:999px; min-height:44px;
           display:flex; align-items:center; gap:6px; border:1px solid {renk_css("cizgi")}; white-space:nowrap;
           position:relative; margin:0 !important; flex:0 0 auto; overflow:visible;
           color:{renk_css("murekkep")}; background:{renk_css("yuzey")}; }}
.ot-adim.ot-simdi {{ border:2px solid {renk_css("ana")}; font-weight:700; }}
.ot-adim.ot-sonra {{ color:{renk_css("ikincil")}; }}
.ot-sayac {{ font-size:{YAZI["etiket"][0]}; font-weight:700; color:{renk_css("ikincil")}; margin:0; }}
.ot-ilerleme {{ height:12px; border-radius:6px; background:{renk_css("cizgi")}; overflow:hidden; }}
.ot-ilerleme-dolu {{ height:100%; background:{renk_css("ana")}; }}
.ot-ilerleme-yazi {{ font-size:{YAZI["govde"][0]}; font-weight:700; margin:6px 0 {b(1.5)}; }}
.ot-cipler {{ list-style:none; padding:0; margin:0; display:flex; flex-wrap:wrap; gap:6px; }}
.ot-cip {{ font-size:{YAZI["etiket"][0]}; padding:6px 12px !important; border-radius:8px; border:1px solid {renk_css("cizgi")};
          color:{renk_css("murekkep")}; margin:0 !important; white-space:nowrap; position:relative; flex:0 0 auto; }}
.ot-cip.ot-simdi {{ border:2px solid {renk_css("ana")}; font-weight:700; }}
.ot-cip.ot-kalan, .ot-cip.ot-gelmedi {{ color:{renk_css("ikincil")}; }}
.ot-otomatik {{ border:1px dashed {renk_css("ana")}; border-radius:{b(1)}; padding:{b(1)} {b(1.5)}; margin:{b(1)} 0; }}
.ot-otomatik-deger {{ font-size:1.75rem; font-weight:700; font-variant-numeric:tabular-nums; }}
.st-key-ot-sayilar [data-baseweb="input"] {{ height:56px; min-height:56px; }}
.st-key-ot-sayilar [data-baseweb="base-input"] {{ height:100%; }}
.st-key-ot-sayilar input {{ height:100% !important; min-height:56px; font-size:22px !important; line-height:1.25;
                           padding-top:0 !important; padding-bottom:0 !important; box-sizing:border-box; }}
[data-testid="InputInstructions"] {{ display:none !important; }}
.st-key-ot-betik {{ position:absolute !important; width:0 !important; height:0 !important; overflow:hidden !important;
                   margin:0 !important; padding:0 !important; border:0 !important; }}
.st-key-ot-sayilar [data-testid="stWidgetLabel"] p {{ font-size:1rem; }}
.st-key-ot-not [data-testid="stButtonGroup"] > div {{ flex-wrap:wrap !important; overflow-x:visible !important;
                                                      row-gap:6px; }}
.ot-ozet {{ margin:0; font-size:{YAZI["govde"][0]}; font-weight:600; }}
.st-key-ot-altcubuk {{ position:sticky; bottom:0; z-index:20; background:{renk_css("zemin")};
                      border-top:1px solid {renk_css("cizgi")}; padding:{b(1)} 0; margin-top:{b(2)}; }}
.st-key-ot-altcubuk [data-testid="stHorizontalBlock"] {{ flex-wrap:nowrap !important; }}
.st-key-ot-altcubuk [data-testid="stColumn"] {{ min-width:0 !important; width:auto !important; flex:1 1 0 !important; }}
.st-key-ot-ana button, .st-key-ot-taslak-devam button {{ min-height:48px; font-weight:700; }}
[class*="st-key-nt-kart"] button {{ min-height:64px; }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation:none !important;
    transition:none !important; scroll-behavior:auto !important; }} }}
{BILESEN_CSS}
</style>
"""


def tema_toml():
    """
    .streamlit/config.toml içeriği — yalnızca simgelerden üretilir (denetim eşitliği kontrol eder). Paket 34:
    [theme] ortak (yazı, köşe, kenarlık; base, baseFontSize, showSidebarBorder yalnız burada geçerli),
    [theme.light] ve [theme.dark] renkler. Kullanıcı Streamlit menüsünden ya da sistem ayarından seçer.
    """
    def renkler(tema):
        r = palet(tema)["renk"]
        return [
            f'primaryColor = "{r["ana"]}"',
            f'backgroundColor = "{r["zemin"]}"',
            f'secondaryBackgroundColor = "{r["yuzey"]}"',
            f'textColor = "{r["murekkep"]}"',
            f'linkColor = "{r["ana"]}"',
            f'borderColor = "{r["cizgi"]}"',
            f'dataframeBorderColor = "{r["cizgi"]}"',
            "chartCategoricalColors = [" + ", ".join(f'"{c}"' for c in _grafik_yuvasi_renkleri(tema)) + "]",
            "chartSequentialColors = [" + ", ".join(f'"{c}"' for c in _grafik_sira_renkleri(tema)) + "]",
        ]
    return "\n".join([
        "# Bu dosya uygulamanın GÖRSEL SİSTEM simgelerinden üretildi (Paket 11, 34). Elle değiştirmeyin;",
        "# renk/yazı değişikliği uygulama dosyasının başındaki RENK / RENK_KOYU / YAZI simgelerinde yapılır.",
        "[theme]",
        "showWidgetBorder = true",
        "showSidebarBorder = true",
        f'baseRadius = "{b(1)}"',
        'font = "sans-serif"',
        f'baseFontSize = {int(16 * float(YAZI["govde"][0].rstrip("rem")))}',
        f'headingFontSizes = ["{YAZI["baslik"][0]}", "{YAZI["baslik"][0]}", "{YAZI["altbaslik"][0]}", '
        f'"{YAZI["govde"][0]}", "{YAZI["govde"][0]}", "{YAZI["govde"][0]}"]',
        f'headingFontWeights = [{YAZI["baslik"][1]}, {YAZI["baslik"][1]}, {YAZI["altbaslik"][1]}, '
        f'{YAZI["altbaslik"][1]}, {YAZI["altbaslik"][1]}, {YAZI["altbaslik"][1]}]',
        "",
        "[theme.light]",
        *renkler("acik"),
        "",
        "[theme.dark]",
        *renkler("koyu"),
        "",
    ])


def grafik_duzeni(**ek):
    """
    Plotly ortak düzeni (Paket 34): yazı ailesi simgeden, YAZI RENGİ VERİLMEZ — Streamlit'in grafik teması o anki
    temanın yazı rengini koyar. Seri renkleri grafik_renk() yuvalarından (colorway).
    Paket 38b: zemin rengi VERİLMEZ (rgba yok) — Streamlit teması grafiğin zeminini sayfanın zeminiyle eşler.
    st.context.theme.type'a güvenilmez (tema değişirken yanlış olabilir).
    """
    d = dict(font=dict(family=YAZI_AILESI), colorway=[grafik_renk(a) for a in GRAFIK_YUVALARI])
    d.update(ek)
    return d


def config_toml_yaz(klasor=".streamlit"):
    """
    config.toml'u simgelerden yazar. Dosya VARSA ve farklıysa üzerine yazar (eski tek temalı dosya kalırsa koyu
    tema hiç çalışmaz); yazmadan önce eskisini config.toml.yedek olarak bırakır. Aynıysa dokunmaz.
    Döner: "yazildi" | "ayni" | "hata".
    """
    yol = os.path.join(klasor, "config.toml")
    yeni = tema_toml()
    try:
        eski = None
        if os.path.exists(yol):
            with open(yol, encoding="utf-8") as f:
                eski = f.read()
        if eski == yeni:
            return "ayni"
        os.makedirs(klasor, exist_ok=True)
        if eski is not None:
            with open(yol + ".yedek", "w", encoding="utf-8") as f:
                f.write(eski)
        with open(yol, "w", encoding="utf-8") as f:
            f.write(yeni)
        return "yazildi"
    except OSError:
        return "hata"


def tasarimi_uygula():
    """CSS'i sayfaya basar; config.toml'u simgelerden yazar (tema bir sonraki açılışta etkinleşir)."""
    st.markdown(TEMA_CSS, unsafe_allow_html=True)
    config_toml_yaz()          # yazılamıyorsa CSS yine uygulanır
