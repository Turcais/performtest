"""
PerformTest — Biyomekanik 3B/Vektör Atletik Sahne ve Animasyon Motoru (`svg_sahne_motoru.py`).

Özellikler:
- Her sahneye özel benzersiz `<defs>` kimlikleri (`{sahne_id}-*`) ile sekme/modal arası ID çakışmasını önler.
- "Cin Ali" (çöp adam) yerine yuvarlatılmış eklem kapaklı, bağımsız uyluk/baldır/kol kas segmentli,
  kesişmeyen şort/pelvis yapılı ve doğru yüz/bakış yönlü (`ux, uy` ve `fx, fy` ortogonal bazlı) anatomik sporcu.
- Ekipman (`kaydir`, `top`, `cubuk`) ve sporcu anahtar kareleri arasında %100 senkronize zamanlama (`S.sure`).
- Ölçü okları ve etiketlerin (`Boy (cm)`, `Sıçrama yüksekliği`, `Mesafe (cm)` vb.) kaybolmasını önleyen
  sürekli görünür yüksek kontrastlı rozet (pill) etiketler.
"""
import html as _html
import math as _math
import re
import uuid
from typing import Any

from olcut.gorseller import TEST_GORSELLERI, TEST_GORSELSIZ
from olcut.gorseller.cizim import TG_TUVAL, TG_ZEMIN


def _birim_vektor(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float, float]:
    dx, dy = x2 - x1, y2 - y1
    boy = _math.hypot(dx, dy)
    if boy < 1e-4:
        return 0.0, -1.0, 1.0, 0.0, 0.0
    ux, uy = dx / boy, dy / boy
    nx, ny = -uy, ux
    return ux, uy, nx, ny, boy


def _uzuv_kapsul_d(
    p1: tuple[float, float],
    p2: tuple[float, float],
    r1: float,
    r2: float,
    sisme_sag: float = 0.0,
    sisme_sol: float = 0.0,
    bas_oran: float = 0.0,
    bit_oran: float = 1.0,
) -> str:
    """
    İki eklem noktası arasında sabit 12 köşeli, yuvarlatılmış uçlu, asimetrik kas kavislendirmeli
    kapalı SVG yolu üretir. Sabit köşe sayısı sayesinde SMIL `<animate attributeName="d">`
    tüm kareler arasında pürüzsüz geçiş yapar.
    """
    x1, y1 = p1
    x2, y2 = p2
    if bas_oran > 0.0 or bit_oran < 1.0:
        bx = x1 + (x2 - x1) * bas_oran
        by = y1 + (y2 - y1) * bas_oran
        ex = x1 + (x2 - x1) * bit_oran
        ey = y1 + (y2 - y1) * bit_oran
        x1, y1, x2, y2 = bx, by, ex, ey

    ux, uy, nx, ny, _ = _birim_vektor(x1, y1, x2, y2)
    q1x, q1y = x1 + (x2 - x1) * 0.33, y1 + (y2 - y1) * 0.33
    mx, my = (x1 + x2) * 0.52, (y1 + y2) * 0.52
    q3x, q3y = x1 + (x2 - x1) * 0.75, y1 + (y2 - y1) * 0.75

    r_q1_sag = r1 * 0.75 + r2 * 0.25 + sisme_sag * 0.85
    r_m_sag = (r1 + r2) * 0.5 + sisme_sag
    r_q3_sag = r1 * 0.25 + r2 * 0.75 + sisme_sag * 0.45

    r_q1_sol = r1 * 0.75 + r2 * 0.25 + sisme_sol * 0.85
    r_m_sol = (r1 + r2) * 0.5 + sisme_sol
    r_q3_sol = r1 * 0.25 + r2 * 0.75 + sisme_sol * 0.45

    pts = [
        (x1 - ux * r1 * 0.65, y1 - uy * r1 * 0.65),
        (x1 + nx * r1, y1 + ny * r1),
        (q1x + nx * r_q1_sag, q1y + ny * r_q1_sag),
        (mx + nx * r_m_sag, my + ny * r_m_sag),
        (q3x + nx * r_q3_sag, q3y + ny * r_q3_sag),
        (x2 + nx * r2, y2 + ny * r2),
        (x2 + ux * r2 * 0.65, y2 + uy * r2 * 0.65),
        (x2 - nx * r2, y2 - ny * r2),
        (q3x - nx * r_q3_sol, q3y - ny * r_q3_sol),
        (mx - nx * r_m_sol, my - ny * r_m_sol),
        (q1x - nx * r_q1_sol, q1y - ny * r_q1_sol),
        (x1 - nx * r1, y1 - ny * r1),
    ]
    return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + " Z"


def _ayakkabi_d(ayak: tuple[float, float], parmak: tuple[float, float], s: float) -> tuple[str, str]:
    """Bilek (`ayak`) ve burun (`parmak`) noktalarından spor ayakkabısı gövdesi ve beyaz alt tabanı üretir."""
    ax, ay = ayak
    px, py = parmak
    ux, uy, nx, ny, boy = _birim_vektor(ax, ay, px, py)
    if boy < 0.8:
        ux, uy, nx, ny = 1.0, 0.0, 0.0, 1.0
    # Taban normali (`nx, ny`) daima zemine (+y) baksın
    if ny < 0:
        nx, ny = -nx, -ny

    ust_pts = [
        (ax - ux * 1.6 * s - nx * 1.9 * s, ay - uy * 1.6 * s - ny * 1.9 * s),
        (ax + ux * 1.4 * s - nx * 2.1 * s, ay + uy * 1.4 * s - ny * 2.1 * s),
        (px + ux * 1.5 * s - nx * 0.6 * s, py + uy * 1.5 * s - ny * 0.6 * s),
        (px + ux * 1.7 * s + nx * 0.7 * s, py + uy * 1.7 * s + ny * 0.7 * s),
        (ax - ux * 1.7 * s + nx * 0.7 * s, ay - uy * 1.7 * s + ny * 0.7 * s),
    ]
    taban_pts = [
        (ax - ux * 1.8 * s + nx * 0.5 * s, ay - uy * 1.8 * s + ny * 0.5 * s),
        (px + ux * 1.8 * s + nx * 0.5 * s, py + uy * 1.8 * s + ny * 0.5 * s),
        (px + ux * 1.6 * s + nx * 1.35 * s, py + uy * 1.6 * s + ny * 1.35 * s),
        (ax - ux * 1.7 * s + nx * 1.35 * s, ay - uy * 1.7 * s + ny * 1.35 * s),
    ]
    ust_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ust_pts) + " Z"
    taban_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in taban_pts) + " Z"
    return ust_d, taban_d


def _bakis_yonu_bul(e: dict[str, tuple[float, float]]) -> float:
    """Ayak burnu (`parmak1 - ayak1`) ve diz/el konumundan sporcunun baktığı yönü (+1 sağ, -1 sol) bulur."""
    dx_ayak = e["parmak1"][0] - e["ayak1"][0]
    if abs(dx_ayak) > 1.2:
        return 1.0 if dx_ayak > 0 else -1.0
    dx_el = (e["el1"][0] + e["el2"][0]) * 0.5 - e["kalca"][0]
    return 1.0 if dx_el >= 0 else -1.0


def _kafa_sac_bant_d(e: dict[str, tuple[float, float]], r_bas: float, yon: float) -> tuple[str, str, str]:
    """
    Gövde doğrultusu (`boyun -> bas_ust`) ve bakış yönü (`yon`) ile ortogonal koordinat sistemi kurar:
    - `(ux, uy)`: Başın tepe (yukarı) birim vektörü
    - `(fx, fy)`: Yüzün baktığı (ileri) birim vektörü
    Böylece saç her zaman başın üst-arkasında, sporcu bandı alında ve göz yüzün ön kısmında yer alır.
    """
    bx, by = e["bas"]
    tx, ty = e["bas_ust"]
    ux, uy, _, _, _ = _birim_vektor(bx, by, tx, ty)
    # (ux, uy) yukarı vektörü iken (örn. 0, -1), ileri vektör: (-yon * uy, yon * ux) -> (+1, 0)
    fx, fy = -yon * uy, yon * ux

    def nokta(ileri: float, yukari: float) -> tuple[float, float]:
        return (bx + (fx * ileri + ux * yukari) * r_bas, by + (fy * ileri + uy * yukari) * r_bas)

    # Anatomik baş ve çene profili (10 noktalı düzgün kafa konturu)
    kafa_pts = [
        nokta(0.0, 1.02),     # tepe
        nokta(0.68, 0.82),    # alın üst
        nokta(0.98, 0.25),    # alın / kaş
        nokta(1.06, -0.10),   # burun ucu
        nokta(0.88, -0.62),   # çene ucu
        nokta(0.25, -0.96),   # çene altı
        nokta(-0.48, -0.88),  # ense kökü
        nokta(-0.92, -0.35),  # arka kafa alt
        nokta(-1.00, 0.35),   # arka kafa üst
        nokta(-0.62, 0.90),   # tepe arka
    ]
    # Modern atletik saç kesimi (yalnızca tepe ve ense üstünde, yüzü kapatmaz — 8 nokta)
    sac_pts = [
        nokta(0.72, 0.72),    # ön perçem ucu
        nokta(0.25, 1.15),    # tepe ön
        nokta(-0.45, 1.12),   # tepe arka
        nokta(-0.98, 0.65),   # arka üst
        nokta(-1.06, 0.05),   # ense üst
        nokta(-0.82, -0.38),  # ense alt
        nokta(-0.55, 0.28),   # kulak arkası
        nokta(0.20, 0.62),    # alın saç çizgisi
    ]
    # Sporcu ter bandı (alın hizasında ince şerit — 4 nokta)
    bant_pts = [
        nokta(-0.88, 0.32),
        nokta(0.88, 0.36),
        nokta(0.82, 0.60),
        nokta(-0.82, 0.56),
    ]
    kafa_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in kafa_pts) + " Z"
    sac_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in sac_pts) + " Z"
    bant_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in bant_pts) + " Z"
    return kafa_d, sac_d, bant_d


def _kare_anatomik_parcalar(e: dict[str, tuple[float, float]], bas_r: float, yon: float) -> dict[str, str]:
    """Tek bir karedeki eklem sözlüğünden (`e`) 18 anatomik vücut katmanının SVG `d` yollarını hesaplar."""
    s = max(0.55, bas_r / 6.5)
    arka_ayk_ust, arka_ayk_taban = _ayakkabi_d(e["ayak2"], e["parmak2"], s * 0.92)
    on_ayk_ust, on_ayk_taban = _ayakkabi_d(e["ayak1"], e["parmak1"], s)
    kafa_d, sac_d, bant_d = _kafa_sac_bant_d(e, bas_r, yon)

    # Kalça-gövde pelvis bloğu (bacaklardan bağımsız olduğu için çömelmede/sıçramada asla burkulmaz)
    kx, ky = e["kalca"]
    bx, by = e["boyun"]
    pelvis_bitis = (kx + (bx - kx) * 0.28, ky + (by - ky) * 0.28)
    pelvis_bas = (kx - (bx - kx) * 0.12, ky - (by - ky) * 0.12)

    return {
        "arka_uyluk": _uzuv_kapsul_d(e["kok_b2"], e["diz2"], 2.65 * s, 1.80 * s, sisme_sag=0.45 * s, sisme_sol=0.25 * s),
        "arka_sort_paca": _uzuv_kapsul_d(e["kok_b2"], e["diz2"], 2.95 * s, 2.45 * s, bas_oran=0.0, bit_oran=0.48),
        "arka_baldir": _uzuv_kapsul_d(e["diz2"], e["ayak2"], 1.75 * s, 1.08 * s, sisme_sag=0.15 * s, sisme_sol=0.42 * s),
        "arka_corap": _uzuv_kapsul_d(e["diz2"], e["ayak2"], 1.32 * s, 1.15 * s, bas_oran=0.65, bit_oran=1.0),
        "arka_ayk_ust": arka_ayk_ust,
        "arka_ayk_taban": arka_ayk_taban,
        "arka_ust_kol": _uzuv_kapsul_d(e["kok_k2"], e["dirsek2"], 1.75 * s, 1.30 * s, sisme_sag=0.22 * s, sisme_sol=0.18 * s),
        "arka_on_kol": _uzuv_kapsul_d(e["dirsek2"], e["el2"], 1.25 * s, 0.92 * s, sisme_sag=0.15 * s, sisme_sol=0.10 * s),
        "boyun": _uzuv_kapsul_d(e["boyun"], e["bas"], 1.55 * s, 1.35 * s),
        "govde_forma": _uzuv_kapsul_d(e["kalca"], e["boyun"], 2.75 * s, 3.45 * s, sisme_sag=0.55 * s, sisme_sol=0.35 * s),
        "pelvis_sort": _uzuv_kapsul_d(pelvis_bas, pelvis_bitis, 2.85 * s, 2.95 * s, sisme_sag=0.25 * s, sisme_sol=0.25 * s),
        "forma_serit": _uzuv_kapsul_d(e["kalca"], e["boyun"], 1.20 * s, 2.30 * s, bas_oran=0.42, bit_oran=0.86),
        "kafa": kafa_d,
        "sac": sac_d,
        "bant": bant_d,
        "on_uyluk": _uzuv_kapsul_d(e["kok_b1"], e["diz1"], 2.80 * s, 1.88 * s, sisme_sag=0.52 * s, sisme_sol=0.30 * s),
        "on_sort_paca": _uzuv_kapsul_d(e["kok_b1"], e["diz1"], 3.10 * s, 2.55 * s, bas_oran=0.0, bit_oran=0.48),
        "on_baldir": _uzuv_kapsul_d(e["diz1"], e["ayak1"], 1.85 * s, 1.12 * s, sisme_sag=0.18 * s, sisme_sol=0.48 * s),
        "on_corap": _uzuv_kapsul_d(e["diz1"], e["ayak1"], 1.38 * s, 1.20 * s, bas_oran=0.65, bit_oran=1.0),
        "on_ayk_ust": on_ayk_ust,
        "on_ayk_taban": on_ayk_taban,
        "on_ust_kol": _uzuv_kapsul_d(e["kok_k1"], e["dirsek1"], 1.92 * s, 1.38 * s, sisme_sag=0.28 * s, sisme_sol=0.20 * s),
        "on_kol_forma": _uzuv_kapsul_d(e["kok_k1"], e["dirsek1"], 2.25 * s, 1.85 * s, bas_oran=0.0, bit_oran=0.46),
        "on_on_kol": _uzuv_kapsul_d(e["dirsek1"], e["el1"], 1.35 * s, 0.96 * s, sisme_sag=0.18 * s, sisme_sol=0.12 * s),
    }


def _cizgi_d(p1: tuple[float, float], p2: tuple[float, float], bas_oran: float = 0.0, bit_oran: float = 1.0) -> str:
    """İki eklem arasında (isteğe bağlı kırpılmış) tek segmentli yol: `M x1,y1 L x2,y2`.
    Yuvarlak uçlu kalın `stroke` ile çizildiğinde pürüzsüz, kesişmeyen bir uzuv oluşturur ve
    tüm karelerde aynı komut yapısına sahip olduğu için SMIL `d` geçişi kusursuzdur."""
    x1, y1 = p1
    x2, y2 = p2
    ax, ay = x1 + (x2 - x1) * bas_oran, y1 + (y2 - y1) * bas_oran
    bx, by = x1 + (x2 - x1) * bit_oran, y1 + (y2 - y1) * bit_oran
    return f"M{ax:.2f},{ay:.2f} L{bx:.2f},{by:.2f}"


def _bas_noktalari(e: dict[str, tuple[float, float]], r: float, yon: float) -> dict[str, tuple[float, float]]:
    """Baş için ortogonal (yukarı `u`, ileri `f`) bazda saç, ter bandı, kulak ve göz noktaları."""
    bx, by = e["bas"]
    ux, uy, _, _, _ = _birim_vektor(e["boyun"][0], e["boyun"][1], bx, by)
    fx, fy = -yon * uy, yon * ux

    def n(ileri: float, yukari: float) -> tuple[float, float]:
        return (bx + (fx * ileri + ux * yukari) * r, by + (fy * ileri + uy * yukari) * r)

    return {
        "sac": n(-0.20, 0.16),
        "bant_a": n(-0.93, 0.40),
        "bant_b": n(0.93, 0.40),
        "kulak": n(-0.12, -0.02),
        "goz": n(0.58, 0.12),
        "burun": n(0.98, -0.05),
    }


def _smil_anim(nitelik: str, degerler: list[str], zamanlar: list[float], sure: float, dongu: bool = True) -> str:
    kt = ";".join(f"{t:.4f}" for t in zamanlar)
    rep = 'repeatCount="indefinite"' if dongu else 'fill="freeze"'
    return (
        f'<animate attributeName="{nitelik}" values="{";".join(degerler)}" '
        f'keyTimes="{kt}" dur="{sure:.2f}s" begin="0s" {rep} calcMode="linear"/>'
    )


def _anatomik_figur_svg(
    sahne_id: str,
    figur_bilgi: dict[str, Any],
    sure: float,
    donus_listesi: list[dict[str, Any]],
    dongu: bool = True,
) -> str:
    """
    `S.figurler` içindeki bir figürü 18 katmanlı anatomik sporcu modeliyle ve sahnedeki
    ekipmanlarla birebir aynı zamanlamada (`sure`, `zamanlar`) üretir.
    """
    rol = figur_bilgi.get("rol", "olculen")
    kareler = figur_bilgi.get("kareler", [])
    if not kareler:
        return ""

    # Ekipmanlarla (kaydir, top, cubuk) %100 senkronize olması için orijinal keyTimes kullanılır
    zamanlar = [round(float(t), 4) for t, _ in kareler]
    eklem_listesi = [e for _, e in kareler]
    bas_r = float(figur_bilgi.get("bas_r", 6.5))
    s = max(0.55, bas_r / 6.5)

    yon_listesi = [_bakis_yonu_bul(e) for e in eklem_listesi]
    # Tek karede yön sıçramasını (ara karelerde ayak düzleşince) önlemek için çoğunluk yönü kullanılır
    yon = 1.0 if sum(yon_listesi) >= 0 else -1.0
    son_e = eklem_listesi[-1]
    r_bas = bas_r * 0.92

    if rol == "iz":
        grup_opaklik = "0.28"
        forma, forma_koyu, sort, ten, ten_koyu, sac, vurgu = (
            "#64748b", "#475569", "#334155", "#94a3b8", "#64748b", "#334155", "#94a3b8")
    elif rol == "partner":
        grup_opaklik = "0.85"
        forma, forma_koyu, sort, ten, ten_koyu, sac, vurgu = (
            "#10b981", "#047857", "#1e293b", "#f1c27d", "#c99a5e", "#3f2a1d", "#a7f3d0")
    else:
        grup_opaklik = "1.0"
        forma, forma_koyu, sort, ten, ten_koyu, sac, vurgu = (
            "#2563eb", "#1e40af", "#0f172a", "#f5c9a0", "#d9a273", "#1f1410", "#38bdf8")

    parca_xml: list[str] = []

    def cizgi(p1: str, p2: str, renk: str, kalinlik: float, bas_o: float = 0.0, bit_o: float = 1.0,
              uc: str = "round") -> None:
        d_list = [_cizgi_d(e[p1], e[p2], bas_o, bit_o) for e in eklem_listesi]
        parca_xml.append(
            f'<path d="{d_list[-1]}" fill="none" stroke="{renk}" stroke-width="{kalinlik * s:.2f}" '
            f'stroke-linecap="{uc}" stroke-linejoin="round">{_smil_anim("d", d_list, zamanlar, sure, dongu)}</path>'
        )

    def daire(nokta_fn, r: float, renk: str, ek: str = "") -> None:
        noktalar = [nokta_fn(e) for e in eklem_listesi]
        cx = [f"{x:.2f}" for x, _ in noktalar]
        cy = [f"{y:.2f}" for _, y in noktalar]
        parca_xml.append(
            f'<circle cx="{cx[-1]}" cy="{cy[-1]}" r="{r:.2f}" fill="{renk}"{ek}>'
            f'{_smil_anim("cx", cx, zamanlar, sure, dongu)}{_smil_anim("cy", cy, zamanlar, sure, dongu)}</circle>'
        )

    def ayakkabi(ayak: str, parmak: str, olcek: float, ust_renk: str, taban_renk: str) -> None:
        ciftler = [_ayakkabi_d(e[ayak], e[parmak], s * olcek) for e in eklem_listesi]
        for idx, renk in ((0, ust_renk), (1, taban_renk)):
            d_list = [c[idx] for c in ciftler]
            parca_xml.append(
                f'<path d="{d_list[-1]}" fill="{renk}" stroke-linejoin="round">'
                f'{_smil_anim("d", d_list, zamanlar, sure, dongu)}</path>'
            )

    # 1. Dinamik zemin gölgesi (sporcu havalandıkça küçülür)
    if rol != "iz":
        golge_cx = [f"{(e['ayak1'][0] + e['ayak2'][0] + e['kalca'][0]) / 3:.1f}" for e in eklem_listesi]
        golge_rx = [
            f"{max(4.5, 11.5 - max(0.0, TG_ZEMIN - max(e['ayak1'][1], e['ayak2'][1])) * 0.22):.1f}"
            for e in eklem_listesi
        ]
        parca_xml.append(
            f'<ellipse cx="{golge_cx[-1]}" cy="{TG_ZEMIN + 1.2:.1f}" rx="{golge_rx[-1]}" ry="1.9" '
            f'fill="rgba(2,6,23,0.45)">'
            f'{_smil_anim("cx", golge_cx, zamanlar, sure, dongu)}'
            f'{_smil_anim("rx", golge_rx, zamanlar, sure, dongu)}'
            f"</ellipse>"
        )

    # 2. Uzak (arka) uzuvlar — koyu tonlu, derinlik hissi
    cizgi("kok_k2", "dirsek2", ten_koyu, 3.3)
    cizgi("dirsek2", "el2", ten_koyu, 2.8)
    daire(lambda e: e["el2"], 1.55 * s, ten_koyu)
    cizgi("kok_b2", "diz2", ten_koyu, 5.0)
    cizgi("diz2", "ayak2", ten_koyu, 3.9)
    if rol != "iz":
        cizgi("diz2", "ayak2", "#cbd5e1", 3.6, 0.62, 1.0, "butt")
        cizgi("kok_b2", "diz2", sort, 6.0, -0.06, 0.5, "round")
    ayakkabi("ayak2", "parmak2", 0.92, "#1e293b", "#cbd5e1")

    # 3. Boyun, gövde (forma) ve şort
    cizgi("boyun", "bas", ten_koyu, 3.6, 0.0, 0.55)
    cizgi("kalca", "boyun", forma, 10.5, 0.04, 0.93)
    if rol != "iz":
        cizgi("kalca", "boyun", forma_koyu, 2.2, 0.15, 0.85, "butt")   # forma yan dikiş şeridi
        cizgi("kalca", "boyun", vurgu, 0.9, 0.18, 0.82, "butt")
    cizgi("kalca", "boyun", sort, 11.0, -0.06, 0.20, "round")

    # 4. Baş: saç (arka-üst), yüz, kulak, göz, ter bandı
    bas_n = [_bas_noktalari(e, r_bas, yon) for e in eklem_listesi]
    sozluk = {id(e): bn for e, bn in zip(eklem_listesi, bas_n)}
    daire(lambda e: sozluk[id(e)]["sac"], r_bas * 1.0, sac)
    daire(lambda e: e["bas"], r_bas, ten, ' stroke="rgba(15,23,42,0.25)" stroke-width="0.35"')
    if rol != "iz":
        daire(lambda e: sozluk[id(e)]["burun"], r_bas * 0.16, ten)
        daire(lambda e: sozluk[id(e)]["kulak"], r_bas * 0.20, ten_koyu)
        daire(lambda e: sozluk[id(e)]["goz"], r_bas * 0.11, "#0f172a")
        bant_d = [
            f"M{b['bant_a'][0]:.2f},{b['bant_a'][1]:.2f} L{b['bant_b'][0]:.2f},{b['bant_b'][1]:.2f}" for b in bas_n
        ]
        parca_xml.append(
            f'<path d="{bant_d[-1]}" fill="none" stroke="{vurgu}" stroke-width="{1.45 * s:.2f}" stroke-linecap="butt">'
            f'{_smil_anim("d", bant_d, zamanlar, sure, dongu)}</path>'
        )

    # 5. Yakın (ön) uzuvlar — açık ton, kas çizgisi vurgulu
    cizgi("kok_b1", "diz1", ten, 5.3)
    cizgi("diz1", "ayak1", ten, 4.1)
    if rol != "iz":
        cizgi("diz1", "ayak1", "#ffffff", 3.8, 0.62, 1.0, "butt")
        cizgi("kok_b1", "diz1", sort, 6.4, -0.06, 0.5, "round")
        cizgi("kok_b1", "diz1", vurgu, 0.7, 0.05, 0.48, "butt")
    ayakkabi("ayak1", "parmak1", 1.0, vurgu if rol == "olculen" else "#334155", "#ffffff")
    cizgi("kok_k1", "dirsek1", ten, 3.5)
    cizgi("dirsek1", "el1", ten, 3.0)
    if rol != "iz":
        cizgi("kok_k1", "dirsek1", forma, 4.6, 0.0, 0.42, "round")   # forma kol ağzı
    daire(lambda e: e["el1"], 1.7 * s, ten)

    # 4. Biyomekanik MoCap Eklem Noktaları (Varsayılan olarak gizli, kullanıcı "🎯 Eklem İzi" ile açar)
    if rol == "olculen":
        for eklem_ad in ("diz1", "ayak1", "kalca", "dirsek1", "el1"):
            ex_list = [f"{e[eklem_ad][0]:.1f}" for e in eklem_listesi]
            ey_list = [f"{e[eklem_ad][1]:.1f}" for e in eklem_listesi]
            parca_xml.append(
                f'<circle class="pt-mocap-node" style="display:none;" cx="{son_e[eklem_ad][0]:.1f}" '
                f'cy="{son_e[eklem_ad][1]:.1f}" r="1.4" fill="#ffffff" stroke="#0284c7" stroke-width="0.8">'
                f'{_smil_anim("cx", ex_list, zamanlar, sure, dongu)}'
                f'{_smil_anim("cy", ey_list, zamanlar, sure, dongu)}'
                f"</circle>"
            )

    ic_xml = "".join(parca_xml)
    if rol == "olculen" and donus_listesi:
        d = donus_listesi[0]
        t0, t1, cx, cy = d["t0"], d["t1"], d["cx"], d["cy"]
        m = f"{cx:.1f} {cy:.1f}"
        rep = 'repeatCount="indefinite"' if dongu else 'fill="freeze"'
        rot = (
            f'<animateTransform attributeName="transform" type="rotate" '
            f'values="0 {m};0 {m};360 {m};360 {m}" '
            f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{sure:.2f}s" begin="0s" {rep}/>'
        )
        ic_xml = f"<g>{rot}{ic_xml}</g>"

    return f'<g class="pt-anatomik-figur" data-rol="{rol}" opacity="{grup_opaklik}">{ic_xml}</g>'


def _sahne_etiketlerini_zenginlestir(xml_parca: str) -> str:
    """
    1) Üst başlık (`y="11.0"`) ve alt not (`y="137.5"`) metinlerini diğer `<g>` etiketlerine dokunmadan
       yalnızca kendi `<text>` düğümleri bazında temizler.
    2) Sahne içi ölçü oklarının (`olcu`, `isaret`) döngü sırasında kaybolmaması için `values="0;0;1;1"`
       opaklık animasyonlarını sürekli görünür (`opacity="1"`) yapar.
    3) Sahne içi ölçü etiketlerinin arkasına yüksek kontrastlı rozet kutusu ekler.
    4) Hareketli ekipmanların (`translate`, `rotate`, `x2`, `y2`) döngüsel oynamasını sağlar.
    """
    # Yalnızca y="11.0" veya y="137.5" olan <text> düğümünü (içinde başka etiket olmayan) kaldır
    xml_parca = re.sub(
        r'<text\b[^>]*\by="(?:11\.0|137\.5)"[^>]*>[^<]*</text>',
        "",
        xml_parca,
    )

    # Ölçü oklarının/etiketlerinin döngüde %95 süre görünmez kalmasını önle:
    # S.belir() tarafından üretilen `<animate attributeName="opacity" values="0;0;1;1".../>` düğümünü kaldır
    xml_parca = re.sub(
        r'<animate attributeName="opacity" values="0;0;1;1"[^/>]*/>',
        "",
        xml_parca,
    )

    # Kalan ölçü etiketlerine arka plan rozet kutusu ekle
    def _etiket_hapla(eslesme: re.Match) -> str:
        tam = eslesme.group(0)
        govde = eslesme.group(1)
        icerik = eslesme.group(2)
        if not icerik.strip():
            return tam
        atrib = dict(re.findall(r'([\w-]+)="([^"]*)"', govde))
        try:
            x = float(atrib.get("x", 0))
            y = float(atrib.get("y", 0))
            boy = float(atrib.get("font-size", 8.5))
        except ValueError:
            return tam
        hiza = atrib.get("text-anchor", "middle")
        metin_duz = _html.unescape(icerik)
        w = max(20.0, len(metin_duz) * boy * 0.57 + 8.0)
        h = boy + 4.6
        rx_kutu = x - w / 2 if hiza == "middle" else (x - 4.0 if hiza == "start" else x - w + 4.0)
        ry_kutu = y - boy * 0.32 - h / 2
        hap = (
            f'<rect x="{rx_kutu:.1f}" y="{ry_kutu:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3.4" '
            f'fill="#0f172a" fill-opacity="0.92" stroke="#38bdf8" stroke-width="0.75"/>'
        )
        yeni_text = re.sub(r'fill="[^"]*"', 'fill="#f8fafc"', tam)
        return hap + yeni_text

    xml_parca = re.sub(r"<text\b([^>]*)>([^<]*)</text>", _etiket_hapla, xml_parca)
    xml_parca = xml_parca.replace('fill="freeze"', 'repeatCount="indefinite"')
    return xml_parca


def _svg_defs_ve_sahne_zemini(sahne_id: str, w: int, h: int) -> str:
    """Her sahneye özel (`{sahne_id}-*`) gradyan tanımları ve PerformTest Tartan Pist/Laboratuvar zemini."""
    cetvel_cizgileri = "".join(
        f'<line x1="{x}" y1="{TG_ZEMIN}" x2="{x}" y2="{TG_ZEMIN + (3.2 if x % 20 == 0 else 1.8)}" '
        f'stroke="rgba(148,163,184,0.45)" stroke-width="0.6"/>'
        for x in range(10, w - 6, 10)
    )
    izgara_yatay = "".join(
        f'<line x1="6" y1="{y}" x2="{w - 6}" y2="{y}" stroke="rgba(148,163,184,0.12)" stroke-width="0.5" stroke-dasharray="2 3"/>'
        for y in (34, 62, 90)
    )
    return f"""
    <defs>
      <linearGradient id="{sahne_id}-arkaplan" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#0f172a"/>
        <stop offset="78%" stop-color="#1e293b"/>
        <stop offset="100%" stop-color="#0f172a"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-pist" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#1e293b"/>
        <stop offset="50%" stop-color="#334155"/>
        <stop offset="100%" stop-color="#1e293b"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-forma-grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#3b82f6"/>
        <stop offset="55%" stop-color="#2563eb"/>
        <stop offset="100%" stop-color="#1d4ed8"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-partner-grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#10b981"/>
        <stop offset="100%" stop-color="#059669"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-iz-grad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#64748b"/>
        <stop offset="100%" stop-color="#475569"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-sort-grad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1e293b"/>
        <stop offset="100%" stop-color="#0f172a"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-ten-grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#fed7aa"/>
        <stop offset="100%" stop-color="#f97316"/>
      </linearGradient>
      <linearGradient id="{sahne_id}-ayakkabi-grad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#0284c7"/>
        <stop offset="100%" stop-color="#38bdf8"/>
      </linearGradient>
    </defs>
    <rect x="0" y="0" width="{w}" height="{h}" rx="8" fill="url(#{sahne_id}-arkaplan)"/>
    {izgara_yatay}
    <rect x="0" y="{TG_ZEMIN}" width="{w}" height="{h - TG_ZEMIN}" rx="2" fill="url(#{sahne_id}-pist)"/>
    <line x1="4" y1="{TG_ZEMIN}" x2="{w - 4}" y2="{TG_ZEMIN}" stroke="#38bdf8" stroke-width="1.5" stroke-opacity="0.9"/>
    {cetvel_cizgileri}
    """


_KOYU_TEMA_RENKLERI = {
    "murekkep": "#e2e8f0",
    "ikincil": "#94a3b8",
    "ana": "#38bdf8",
    "cizgi": "#64748b",
    "yuzey": "#0f172a",
}


def _renk_degiskenlerini_coz(xml: str) -> str:
    """`var(--tg-ad, #yedek)` CSS değişkenlerini koyu sahne için yüksek kontrastlı renklere çevirir
    (yedek hex değerinden bağımsız; böylece cetvel, plaka ve ölçü okları koyu zeminde kaybolmaz)."""
    def degistir(m: re.Match) -> str:
        return _KOYU_TEMA_RENKLERI.get(m.group(1), m.group(2).strip())

    return re.sub(r"var\(--tg-([a-z_]+)\s*,\s*([^)]+)\)", degistir, xml)


# ── Hareket fazı analizi ─────────────────────────────────────────────────────
_FAZ_STILI = {
    "Hazırlık": ("#94a3b8", "◉"),
    "Yüklenme": ("#f59e0b", "▼"),
    "İtiş & Uçuş": ("#22d3ee", "▲"),
    "İniş & Amortisman": ("#a78bfa", "▼"),
    "Hareket": ("#38bdf8", "➜"),
    "Bitiş": ("#34d399", "✓"),
    "Ölçüm Pozisyonu": ("#34d399", "◉"),
}


def _faz_analizi(kareler: list) -> dict[str, Any]:
    """
    Figür karelerinden (kalça yüksekliği, ayak-zemin teması, yatay yer değiştirme) hareket fazlarını
    otomatik çıkarır: Hazırlık → Yüklenme → İtiş & Uçuş → İniş & Amortisman → Bitiş.
    """
    zaman = [float(t) for t, _ in kareler]
    eklem = [e for _, e in kareler]
    ayak_y = [max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2")) for e in eklem]
    kalca_y = [e["kalca"][1] for e in eklem]
    kalca_x = [e["kalca"][0] for e in eklem]
    zemin = max(ayak_y)
    havada = [y < zemin - 1.5 for y in ayak_y]
    yerde_kalca = [ky for ky, h in zip(kalca_y, havada) if not h] or kalca_y
    ayakta = min(yerde_kalca)
    comelme = [(not h) and ky > ayakta + 3.5 for ky, h in zip(kalca_y, havada)]

    ilk_ucus = next((i for i, h in enumerate(havada) if h), None)
    son_ucus = max((i for i, h in enumerate(havada) if h), default=None)
    hareket_var = (max(kalca_x) - min(kalca_x)) > 6

    etiketler: list[str] = []
    for i in range(len(eklem)):
        if havada[i]:
            etiketler.append("İtiş & Uçuş")
        elif comelme[i]:
            once = ilk_ucus is None or i < ilk_ucus
            etiketler.append("Yüklenme" if once else "İniş & Amortisman")
        elif ilk_ucus is None and not any(comelme):
            etiketler.append("Hareket" if hareket_var and 0 < i < len(eklem) - 1 else "Ölçüm Pozisyonu")
        elif (ilk_ucus is not None and i < ilk_ucus) or (ilk_ucus is None and i < comelme.index(True)):
            etiketler.append("Hazırlık")
        else:
            etiketler.append("Bitiş")

    segmentler: list[list] = []
    for t, et in zip(zaman, etiketler):
        if segmentler and segmentler[-1][2] == et:
            continue
        if segmentler:
            segmentler[-1][1] = t
        segmentler.append([t, 1.0, et])
    if segmentler:
        segmentler[-1][1] = 1.0
        segmentler[0][0] = 0.0

    yuklenme_idx = None
    if any(comelme):
        adaylar = [i for i, c in enumerate(comelme) if c and (ilk_ucus is None or i < ilk_ucus)]
        if adaylar:
            yuklenme_idx = max(adaylar, key=lambda i: kalca_y[i])
    tepe_idx = min((i for i, h in enumerate(havada) if h), key=lambda i: kalca_y[i], default=None)

    return {
        "zaman": zaman,
        "eklem": eklem,
        "segmentler": [tuple(s) for s in segmentler],
        "kalkis_t": zaman[ilk_ucus] if ilk_ucus is not None else None,
        "inis_t": zaman[son_ucus + 1] if son_ucus is not None and son_ucus + 1 < len(zaman) else None,
        "inis_idx": son_ucus + 1 if son_ucus is not None and son_ucus + 1 < len(zaman) else None,
        "kalkis_idx": ilk_ucus,
        "yuklenme_idx": yuklenme_idx,
        "tepe_idx": tepe_idx,
        "zemin": zemin,
    }


def _ayrik_gorunurluk(t0: float, t1: float, sure: float, deger: str = "1") -> str:
    """[t0, t1) aralığında görünür, diğer zamanlarda gizli ayrık opaklık animasyonu."""
    if t0 <= 0.0005:
        values, kt = f"{deger};0", f"0;{t1:.4f}"
    elif t1 >= 0.9995:
        values, kt = f"0;{deger}", f"0;{t0:.4f}"
    else:
        values, kt = f"0;{deger};0", f"0;{t0:.4f};{t1:.4f}"
    return (f'<animate attributeName="opacity" values="{values}" keyTimes="{kt}" dur="{sure:.2f}s" '
            f'begin="0s" repeatCount="indefinite" calcMode="discrete"/>')


def _faz_katmani(faz: dict[str, Any], sure: float, w: int, h: int) -> str:
    """Sol üstte senkron faz rozeti + alt kenarda fazlara bölünmüş ilerleme çubuğu ve oynatma imleci."""
    segmentler = faz["segmentler"]
    if not segmentler:
        return ""
    parcalar: list[str] = []
    # Faz rozeti
    for t0, t1, et in segmentler:
        renk, ikon = _FAZ_STILI.get(et, ("#38bdf8", "●"))
        metin = f"{et.upper()}"
        gen = len(metin) * 4.6 + 18.0
        parcalar.append(
            f'<g opacity="{1 if t0 <= 0.0005 else 0}">{_ayrik_gorunurluk(t0, t1, sure)}'
            f'<rect x="8" y="16.5" width="{gen:.1f}" height="13.5" rx="6.75" fill="#090d16" fill-opacity="0.94" '
            f'stroke="{renk}" stroke-width="0.9"/>'
            f'<circle cx="14.5" cy="23.2" r="2.2" fill="{renk}">'
            f'<animate attributeName="opacity" values="0.7;1;0.7" dur="1.2s" repeatCount="indefinite"/></circle>'
            f'<text x="21.0" y="25.8" font-size="7.5" font-weight="800" fill="{renk}" '
            f'font-family="system-ui,-apple-system,Inter,Segoe UI,Roboto,sans-serif" letter-spacing="0.5">{_html.escape(metin)}</text></g>'
        )
    # İlerleme çubuğu
    y_bar = h - 10.5
    x0, x1 = 8.0, w - 8.0
    parcalar.append(f'<rect x="{x0}" y="{y_bar}" width="{x1 - x0}" height="2.2" rx="1.1" fill="#1e293b"/>')
    for t0, t1, et in segmentler:
        renk = _FAZ_STILI.get(et, ("#38bdf8", ""))[0]
        sx = x0 + (x1 - x0) * t0
        sw = max(0.6, (x1 - x0) * (t1 - t0) - 0.6)
        parcalar.append(
            f'<rect x="{sx:.1f}" y="{y_bar}" width="{sw:.1f}" height="2.2" rx="1.1" fill="{renk}" fill-opacity="0.55"/>'
        )
    parcalar.append(
        f'<circle cx="{x0}" cy="{y_bar + 1.1}" r="2.3" fill="#ffffff" stroke="#38bdf8" stroke-width="0.8">'
        f'<animate attributeName="cx" values="{x0};{x1}" dur="{sure:.2f}s" begin="0s" repeatCount="indefinite"/></circle>'
    )
    return f'<g class="pt-faz-katmani">{"".join(parcalar)}</g>'


def _toz_efekti(x: float, y: float, t: float, sure: float) -> str:
    """Kalkış/iniş anında ayak altında genişleyip sönen toz/şok halkası."""
    t = min(max(t, 0.002), 0.95)
    t2 = min(t + 0.14, 0.999)
    tm = max(t - 0.001, 0.001)
    kt = f"0;{tm:.4f};{t:.4f};{t2:.4f};1"
    halkalar = []
    for dx, gecikme_r in ((-1, 1.0), (1, 1.0), (0, 1.35)):
        halkalar.append(
            f'<ellipse cx="{x + dx * 2.5:.1f}" cy="{y - 0.6:.1f}" rx="1" ry="0.8" fill="none" '
            f'stroke="#cbd5e1" stroke-width="0.7" opacity="0">'
            f'<animate attributeName="rx" values="1;1;1;{9 * gecikme_r:.1f};{9 * gecikme_r:.1f}" keyTimes="{kt}" '
            f'dur="{sure:.2f}s" begin="0s" repeatCount="indefinite"/>'
            f'<animate attributeName="ry" values="0.8;0.8;0.8;2.4;2.4" keyTimes="{kt}" '
            f'dur="{sure:.2f}s" begin="0s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;0.75;0;0" keyTimes="{kt}" '
            f'dur="{sure:.2f}s" begin="0s" repeatCount="indefinite"/></ellipse>'
        )
    return "".join(halkalar)


def _iz_hayaleti(sahne_id: str, e: dict, t: float, bas_r: float, sure: float, opaklik: float = 0.22) -> str:
    """Kritik pozun (en derin yüklenme / uçuş tepesi) o an geçildikten sonra beliren soluk izi (onion-skin)."""
    t = min(max(t, 0.002), 0.97)
    ic = _anatomik_figur_svg(sahne_id, {"rol": "iz", "kareler": [(0.0, e), (1.0, e)], "bas_r": bas_r},
                             sure, [], dongu=True)
    kt = f"0;{t:.4f};{min(t + 0.03, 0.99):.4f};0.97;1"
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;0;{opaklik};{opaklik};0" keyTimes="{kt}" '
            f'dur="{sure:.2f}s" begin="0s" repeatCount="indefinite"/>{ic}</g>')


def _ucus_cizgileri(faz: dict[str, Any], sure: float) -> str:
    """Uçuş fazında kalça arkasında beliren hız çizgileri (hareket yönünü ve hızı okutur)."""
    ki, ii = faz["kalkis_idx"], faz["inis_idx"]
    if ki is None or ii is None:
        return ""
    eklem, zaman = faz["eklem"], faz["zaman"]
    t0, t1 = zaman[ki], zaman[ii]
    kare_ara = range(ki, ii + 1)
    dx = eklem[ii]["kalca"][0] - eklem[ki]["kalca"][0]
    yon = 1.0 if dx >= 0 else -1.0
    dikey = abs(dx) < 8
    cizgiler = []
    for j, ofset in enumerate((-4.0, 0.0, 4.0)):
        xs, ys = [], []
        for i in kare_ara:
            kx, ky = eklem[i]["kalca"]
            xs.append(kx + (ofset if dikey else -yon * 9))
            ys.append(ky + (11 if dikey else ofset))
        d_list = []
        for x, y in zip(xs, ys):
            if dikey:
                d_list.append(f"M{x:.1f},{y:.1f} L{x:.1f},{y + 7 + j:.1f}")
            else:
                d_list.append(f"M{x:.1f},{y:.1f} L{x - yon * (7 + j * 2):.1f},{y:.1f}")
        # Uçuş dışındaki zamanlarda ilk/son konumda sabit ve görünmez
        tam_d = [d_list[0]] + d_list + [d_list[-1]]
        tam_t = [0.0] + [zaman[i] for i in kare_ara] + [1.0]
        temiz_t, temiz_d = [], []
        for tt, dd in zip(tam_t, tam_d):
            if temiz_t and tt <= temiz_t[-1]:
                continue
            temiz_t.append(tt)
            temiz_d.append(dd)
        if temiz_t[-1] < 1.0:
            temiz_t.append(1.0)
            temiz_d.append(temiz_d[-1])
        cizgiler.append(
            f'<path d="{temiz_d[0]}" stroke="#7dd3fc" stroke-width="0.7" stroke-linecap="round" opacity="0">'
            f'{_smil_anim("d", temiz_d, temiz_t, sure)}'
            f'{_ayrik_gorunurluk(t0, t1, sure, "0.65")}</path>'
        )
    return "".join(cizgiler)


def _kelimeler(metin: str) -> set[str]:
    return {k for k in re.findall(r"\w+", metin.lower()) if len(k) > 3 and k not in {"testi", "test", "tsyt"}}


def _en_benzer_sahne(test_adi: str) -> str | None:
    """Görseli olmayan bir test için adı en çok ortak anlamlı kelimeyi paylaşan sahneyi döndürür."""
    hedef = _kelimeler(test_adi)
    if not hedef:
        return None
    en_iyi, en_puan = None, 0
    for anahtar in TEST_GORSELLERI:
        puan = len(hedef & _kelimeler(anahtar))
        if puan > en_puan:
            en_iyi, en_puan = anahtar, puan
    return en_iyi if en_puan >= 1 else None


def gelismis_test_sahnesi_uret(b: dict[str, Any], test_adi: str) -> dict[str, Any]:
    """
    Bir test için anatomik sporcu modelli, ekipmanlarla tam senkronize, yüksek okunabilirlikli
    SVG sahneyi ve etkileşimli kontrol çubuğunu üretir.
    """
    bilgi = b["test_bilgisi"](test_adi) or {}
    nitelik = b["test_niteligi"](test_adi) or "Genel"
    protokol_metni = str(bilgi.get("protokol") or bilgi.get("aciklama") or "")
    adimlar_md = b["protokol_ozet_cikar"](protokol_metni) if "protokol_ozet_cikar" in b and protokol_metni else ""

    if test_adi not in TEST_GORSELLERI:
        neden = TEST_GORSELSIZ.get(test_adi, "Bu protokol çok bileşenli veya laboratuvar tabanlıdır.")
        ad_kucuk = test_adi.lower()
        benzer = _en_benzer_sahne(test_adi)
        if benzer:
            yedek_anahtar = benzer
        elif any(k in ad_kucuk for k in ("kompozisyon", "deri", "bia", "dexa", "tartım", "bel çevresi")):
            yedek_anahtar = "Boy ve Vücut Ağırlığı (TSYT)"
        elif any(k in ad_kucuk for k in ("vo2", "laktat", "cpet", "kardiyo")):
            yedek_anahtar = "Wingate 30sn Bisiklet Testi"
        else:
            yedek_anahtar = "Durarak Uzun Atlama"
        sahne_fn, _ = TEST_GORSELLERI[yedek_anahtar]
        kritik_ayrinti = f"Laboratuvar / Çok Bileşenli Protokol ({neden})"
    else:
        sahne_fn, kritik_ayrinti = TEST_GORSELLERI[test_adi]
    S = sahne_fn()

    w, h = TG_TUVAL
    sure = round(float(S.sure), 2)
    sahne_id = f"pt-svg-{uuid.uuid4().hex[:8]}"

    baslik_metni = ""
    not_metni = ""
    for yk in getattr(S, "yazi_kutulari", []):
        if len(yk) >= 7:
            metin, yer = yk[4], yk[6]
            if yer == "baslik" and not baslik_metni:
                baslik_metni = metin
            elif yer == "not" and not not_metni:
                not_metni = metin

    yeni_ogeler: list[str] = []
    figur_indeks = 0
    for har_xml, _ in S.ogeler:
        dogrudan_figur = (
            har_xml.startswith("<path ")
            or har_xml.startswith('<g><animateTransform attributeName="transform" type="rotate"')
        )
        if dogrudan_figur and 'data-katman="' in har_xml and figur_indeks < len(S.figurler):
            fig_bilgi = S.figurler[figur_indeks]
            figur_indeks += 1
            yeni_ogeler.append(_anatomik_figur_svg(sahne_id, fig_bilgi, sure, getattr(S, "donusler", []), dongu=True))
        else:
            temiz = _sahne_etiketlerini_zenginlestir(har_xml)
            if temiz.strip():
                yeni_ogeler.append(temiz)

    defs_ve_zemin = _svg_defs_ve_sahne_zemini(sahne_id, w, h)

    # Hareket fazı analizi (ölçülen sporcu) → faz rozeti, ilerleme çubuğu, iz hayaletleri, toz ve hız çizgileri
    efekt_arka, faz_xml = "", ""
    olculen = next((f for f in S.figurler if f.get("rol", "olculen") == "olculen" and f.get("kareler")), None)
    if olculen:
        try:
            faz = _faz_analizi(olculen["kareler"])
            bas_r_f = float(olculen.get("bas_r", 6.5))
            dondurme_var = bool(getattr(S, "donusler", []))
            parcalar_efekt = []
            if not dondurme_var:
                for idx in (faz["yuklenme_idx"], faz["tepe_idx"]):
                    if idx is not None:
                        parcalar_efekt.append(
                            _iz_hayaleti(sahne_id, faz["eklem"][idx], faz["zaman"][idx], bas_r_f, sure)
                        )
                parcalar_efekt.append(_ucus_cizgileri(faz, sure))
            for idx_ad, t_ad in (("kalkis_idx", "kalkis_t"), ("inis_idx", "inis_t")):
                idx = faz[idx_ad]
                if idx is not None:
                    e_an = faz["eklem"][idx if idx_ad == "inis_idx" else max(idx - 1, 0)]
                    ax = (e_an["ayak1"][0] + e_an["ayak2"][0]) / 2
                    parcalar_efekt.append(_toz_efekti(ax, faz["zemin"], faz[t_ad], sure))
            efekt_arka = "".join(parcalar_efekt)
            faz_xml = _faz_katmani(faz, sure, w, h)
        except (KeyError, ValueError, IndexError):
            efekt_arka, faz_xml = "", ""

    govde_xml = efekt_arka + "".join(yeni_ogeler)
    govde_xml = _renk_degiskenlerini_coz(govde_xml) + faz_xml

    svg_kod = (
        f'<svg id="{sahne_id}" xmlns="http://www.w3.org/2000/svg" viewBox="0 14 {w} {h - 22}" '
        f'style="width:100%;height:auto;display:block;border-radius:12px;" role="img" '
        f'aria-label="{_html.escape(test_adi)}">'
        f"{defs_ve_zemin}{govde_xml}</svg>"
    )

    ust_hud = (
        f'<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;'
        f'background:#0f172a;color:#f8fafc;padding:11px 15px;border-radius:12px 12px 0 0;border-bottom:1px solid #1e293b;">'
        f'<div style="display:flex;align-items:center;gap:9px;">'
        f'<span style="background:linear-gradient(135deg,#2563eb,#06b6d4);color:#fff;padding:3px 9px;border-radius:6px;font-size:11.5px;font-weight:700;">BİYOMEKANİK SAHNE</span>'
        f'<span style="font-weight:700;font-size:14px;color:#f1f5f9;">{_html.escape(baslik_metni or test_adi)}</span>'
        f"</div>"
        f'<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">'
        f'<button type="button" onclick="(function(){{const s=document.getElementById(\'{sahne_id}\');if(s&&s.setCurrentTime)s.setCurrentTime(0);}})()" '
        f'style="background:#1e293b;color:#38bdf8;border:1px solid #334155;padding:4px 9px;border-radius:6px;font-size:11.5px;font-weight:600;cursor:pointer;">↺ Baştan</button>'
        f'<button type="button" onclick="(function(btn){{const s=document.getElementById(\'{sahne_id}\');if(!s)return;const hizlar=[1,0.5,1.5];const etiketler=[\'⚡ 1x Hız\',\'🐢 0.5x Ağır Çekim\',\'🚀 1.5x Hızlı\'];let i=(parseInt(btn.dataset.idx||\'0\')+1)%3;btn.dataset.idx=i;btn.textContent=etiketler[i];const carpan=hizlar[i];s.querySelectorAll(\'animate,animateTransform\').forEach(a=>{{if(!a.dataset.baseDur)a.dataset.baseDur=parseFloat(a.getAttribute(\'dur\'))||{sure};a.setAttribute(\'dur\',(parseFloat(a.dataset.baseDur)/carpan).toFixed(2)+\'s\');}});if(s.setCurrentTime)s.setCurrentTime(0);}})(this)" '
        f'style="background:#1e293b;color:#fcd34d;border:1px solid #334155;padding:4px 9px;border-radius:6px;font-size:11.5px;font-weight:600;cursor:pointer;">⚡ 1x Hız</button>'
        f'<button type="button" onclick="(function(btn){{const s=document.getElementById(\'{sahne_id}\');if(!s)return;if(s.animationsPaused&&s.animationsPaused()){{s.unpauseAnimations();btn.textContent=\'⏸ Duraklat\';}}else if(s.pauseAnimations){{s.pauseAnimations();btn.textContent=\'▶ Oynat\';}}}})(this)" '
        f'style="background:#1e293b;color:#e2e8f0;border:1px solid #334155;padding:4px 9px;border-radius:6px;font-size:11.5px;font-weight:600;cursor:pointer;">⏸ Duraklat</button>'
        f'<button type="button" onclick="(function(){{const s=document.getElementById(\'{sahne_id}\');if(!s)return;s.querySelectorAll(\'.pt-mocap-node\').forEach(n=>n.style.display=n.style.display===\'none\'?\'\':\'none\');}})()" '
        f'style="background:#1e293b;color:#a7f3d0;border:1px solid #334155;padding:4px 9px;border-radius:6px;font-size:11.5px;font-weight:600;cursor:pointer;">🎯 Eklem İzi</button>'
        f"</div></div>"
    )

    alt_hud = (
        f'<div style="background:#0f172a;color:#cbd5e1;padding:10px 15px;border-radius:0 0 12px 12px;border-top:1px solid #1e293b;'
        f'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;font-size:13px;">'
        f'<div><strong style="color:#38bdf8;">📌 Ölçüm Kuralı:</strong> {_html.escape(not_metni or kritik_ayrinti)}</div>'
        f'<div style="color:#94a3b8;font-size:11.5px;">Döngü: {sure} sn · Biyomekanik Vektör Model</div>'
        f"</div>"
    )

    kritik_kutu = (
        f'<div style="margin-top:12px;padding:11px 14px;background:rgba(37,99,235,0.08);border-left:4px solid #2563eb;'
        f'border-radius:0 10px 10px 0;font-size:13.5px;">'
        f"<strong>⚡ Kritik Saha Ayrıntısı:</strong> {_html.escape(kritik_ayrinti)}"
        f"</div>"
        if kritik_ayrinti
        else ""
    )

    adim_satirlari = [
        satir.strip().lstrip("-*0123456789. ")
        for satir in adimlar_md.splitlines()
        if satir.strip()
    ]
    adimlar_html = ""
    if adim_satirlari:
        adim_kartlari = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 11px;border-radius:8px;background:var(--surface-2, #f8fafc);border:1px solid var(--line, #e2e8f0);font-size:13px;">'
            f'<span style="background:#2563eb;color:#fff;width:22px;height:22px;border-radius:6px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:11.5px;flex-shrink:0;">{idx + 1}</span>'
            f'<span>{_html.escape(adim)}</span></div>'
            for idx, adim in enumerate(adim_satirlari[:6])
        )
        adimlar_html = (
            f'<div style="margin-top:12px;">'
            f'<div style="font-size:12px;font-weight:700;text-transform:uppercase;color:var(--muted, #64748b);margin-bottom:6px;">Adım Adım Protokol Uygulaması</div>'
            f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px;">{adim_kartlari}</div>'
            f"</div>"
        )

    tam_html = (
        f'<div class="pt-sahne-kart" style="border-radius:12px;overflow:hidden;box-shadow:0 10px 25px -5px rgba(15,23,42,0.28);">'
        f"{ust_hud}"
        f'<div style="background:#0f172a;padding:8px 12px;">{svg_kod}</div>'
        f"{alt_hud}"
        f"</div>"
        f"{kritik_kutu}"
        f"{adimlar_html}"
    )

    return {
        "test_adi": test_adi,
        "nitelik": nitelik,
        "aciklama": bilgi.get("aciklama", ""),
        "alanlar": bilgi.get("alanlar", []),
        "baslik": baslik_metni,
        "not": not_metni,
        "kritik_ayrinti": kritik_ayrinti,
        "adimlar": adimlar_md,
        "svg_html": tam_html,
    }
