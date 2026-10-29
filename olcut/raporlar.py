"""
Raporlar: veli raporu (sonuç kutuları, aralık dili, gelişim, yaşıtlarına göre konum) ve antrenör raporu HTML'i,
şablonlu yorumlar, şeritler ve gelişim grafikleri.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import collections
import re
from datetime import date
from veri.brans_profilleri import BILESIK_Z, BRANS_GRUBU_PROFILLERI
from veri.metinler import ACIKLAMALAR, GUVEN_DUZEYLERI, VELI_TEST_GRUBU, VELI_YORUMLARI
from olcut.analiz import (
    ESLESTIRME_DEGISKENLERI, ESLESTIRME_EN_AZ_DEGISKEN, ESLESTIRME_SIMULASYON, ESLESTIRME_YAS_ARALIGI,
    GRUP_KATMANI_NOTU, GRUP_KONUM_YUZDELIK_N, GRUP_RENKLERI, ILGI_ANKET_ADI, ILGI_TERCIHLERI, ILGI_UYARI,
    RAPOR_CSS, SAYIM_BIRIMLERI, VELI_ARALIK_KIM, VELI_ARALIK_METNI, VELI_ARALIK_NOTU, VELI_ARALIK_YERI,
    VELI_DOGRU_MU, VELI_DOGRU_MU_BASLIK, VELI_KONUM_EN_AZ_YAS, VELI_KONUM_METNI, VELI_SAPMA_Z,
    VELI_YASIT_BASLIK, _RAPOR_RENK, _brans_ornekleri, _konum_sayi, _tablolari_sar, ilgi_etiketi,
    konum_metinleri, konum_seridi_svg, radar_svg, veli_hitabi, yetiskin_mi, z_satiri_karti)
from olcut.katalog_islemleri import ara_katla, kanonik_test, test_niteligi
from olcut.norm import NORMATIF_YAS, _STANDART_NORMAL
from olcut.ortak import _TR_KUCULT, _e, _girildi, _sayi, _tarih_gunu, ad_bicimi
from olcut.tema import KATEGORI_ESDEGER, kart_izgarasi_html, kategori_bilgisi, kimlik_html, palet


VELI_GRUPLARI = ["Hız ve çabukluk", "Kuvvet", "Esneklik", "Koordinasyon ve denge"]


# Dört başlığa girmeyen performans testleri: dayanıklılık. Veli raporunda yer almaz (antrenör raporunda var).
VELI_DISARIDA = {
    "PACER (20m Mekik Koşusu)", "PACER Testi", "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)",
    "20m Mekik Koşusu (ALPHA)", "20m Mekik Koşusu (PREFIT)", "20m Mekik Koşusu (Eurofit/Léger)",
    "20m Mekik Koşusu (Beep Test)",
}


VELI_DISARIDA_NOTU = ("Dayanıklılık (uzun süreli koşu) testleri bu raporun dört başlığına girmez; "
                      "sonuçları antrenör raporundadır.")


# Grubun genel durumu da şablonla: yalnızca sayım; tek testten genel sonuç çıkarılmaz.
VELI_GRUP_DUZEY = {   # seviye aralığı → ifade
    "ust": "akranlarının çoğundan iyi",
    "orta": "akranlarına yakın",
    "alt": "şu an akranlarının altında",
}


VELI_GRUP_TEK_TEST = ("Bu başlıkta yalnızca bir test yapıldı; tek test, bu başlık hakkında genel bir şey "
                      "söylemek için yeterli değildir.")


VELI_GRUP_TEST_YOK = "Bu başlıkta henüz test yapılmadı."


VELI_SON_PARAGRAF = (
    "Bu sonuçlar, ölçümün yapıldığı günü gösterir; çocuğunuzun gelişimi devam ediyor ve sonuçlar zamanla "
    "değişebilir. Hiçbir sonuç, çocuğunuzun herhangi bir sporu yapmasına engel değildir. Çocuğunuzun ilgi "
    "duyduğu sporu yapması her durumda desteklenmelidir.")


# Dört grup için sade çizgi simgeler (24×24, tek çizgi kalınlığı, renk _RAPOR_RENK["ana"]) — uygulamanın kendi çizimi
_VELI_SIMGE_YOLLARI = {
    "Hız ve çabukluk": "M3 8h7 M2 12h9 M4 16h6 M14 6l6 6-6 6",
    "Kuvvet": "M4 9v6 M7 6.5v11 M17 6.5v11 M20 9v6 M7 12h10",
    "Esneklik": "M5 19c0-8 6-14 14-14 M15.5 3l3.5 2-2 3.5",
    "Koordinasyon ve denge": "M3 14h18 M12 14l-3 6h6z M12 4.5a2.5 2.5 0 1 0 0.01 0",
    "sevdikleri": "M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z",
    "fiziksel": "M12 3.5a2 2 0 1 0 0.01 0 M12 7.5v6 M7.5 10h9 M12 13.5l-3.5 6.5 M12 13.5l3.5 6.5",
}


def veli_grup_simgesi(grup, boyut=22):
    return (f'<svg viewBox="0 0 24 24" width="{boyut}" height="{boyut}" fill="none" stroke="{_RAPOR_RENK["ana"]}" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'<path d="{_VELI_SIMGE_YOLLARI[grup]}"/></svg>')


def veli_yorumu(grup, kategori):
    """Şablondan tek cümle. DMT/kategorik norm adları skaladaki eşdeğerine çevrilir; şablonu yoksa None."""
    return VELI_YORUMLARI.get((grup, KATEGORI_ESDEGER.get(kategori, kategori)))


def _veli_duzeyi(seviye):
    return "ust" if seviye >= 5 else ("orta" if seviye >= 3 else "alt")


def veli_grup_durumu(seviyeler):
    """Grubun genel durumu: kaç testte hangi düzey — yorum değil sayım."""
    if not seviyeler:
        return VELI_GRUP_TEST_YOK
    if len(seviyeler) == 1:
        return VELI_GRUP_TEK_TEST
    sayim = collections.Counter(_veli_duzeyi(s) for s in seviyeler)
    parcalar = [f"{sayim[d]} testte {VELI_GRUP_DUZEY[d]}" for d in ("ust", "orta", "alt") if sayim[d]]
    return (f"Bu başlıkta {len(seviyeler)} test yapıldı: " + ", ".join(parcalar)
            + " bir sonuç aldı. Bu sayım testlerin sonucunu özetler; çocuğunuz hakkında bir yargı değildir.")


# Paket 38c: veli raporundaki sonuçlar sınıf etiketi (Çok Düşük … Üstün) ve "akranlarının …" cümlesi yerine
# yayımlanmış tablonun P10–P90 aralığıyla anlatılır. Tabloda P10 ve P90 varsa doğrudan; yoksa komşu yüzdelikler
# arasında doğrusal ara değer; aralık tablonun dışına düşüyorsa (yalnız P20–P80 olan tablolar) mevcut makullük
# yöntemiyle (medyan ± z·SS, kuyruklar ayrı) tahmin — bu iki durumda metinde "yaklaşık" yazar.
VELI_ARALIK_Z = 1.2816                  # standart normalde P90'ın z değeri (P10 için −)


VELI_YER_ISARETI = {"icinde": ("●", "aralığın içinde"), "ustunde": ("▲", "aralığın biraz üstünde"),
                    "altinda": ("▼", "aralığın biraz altında"),
                    "ustunde_belirgin": ("▲", "aralığın belirgin şekilde üstünde"),
                    "altinda_belirgin": ("▼", "aralığın belirgin şekilde altında"),
                    "ustunde_cok": ("▲", "aralığın çok üstünde"), "altinda_cok": ("▼", "aralığın çok altında")}


VELI_YER_SIRASI = ("icinde", "ustunde", "ustunde_belirgin", "ustunde_cok", "altinda", "altinda_belirgin", "altinda_cok")


VELI_YAKLASIK_NOTU = ("“Yaklaşık” yazan aralıklar, kaynak tablodaki en yakın değerlerden hesaplanmıştır; "
                      "tabloda bu aralık doğrudan verilmemiştir.")


VELI_SONUC_GIRIS = ("Her sonuç, aynı yaş ve cinsiyetteki çocuklar için yayımlanmış değerlerle karşılaştırıldı. "
                    "Koyu bant çocukların çoğunun bulunduğu aralığı, nokta {ad} için ölçülen sonucu gösterir.")


def norm_araligi(bantlar):
    """Yüzdelik bantlarından (P10, P90, kesin_mi). Bant yoksa None."""
    try:
        nok = sorted((int(k[1:]), float(v)) for k, v in (bantlar or {}).items()
                     if str(k).startswith("P") and str(k)[1:].isdigit())
    except (TypeError, ValueError):
        return None
    if len(nok) < 2:
        return None
    d = dict(nok)
    if 10 in d and 90 in d:
        return d[10], d[90], True

    def ara(p):
        alt = [(q, v) for q, v in nok if q < p]
        ust = [(q, v) for q, v in nok if q > p]
        if not alt or not ust:
            return None
        (q0, v0), (q1, v1) = alt[-1], ust[0]
        return v0 + (v1 - v0) * (p - q0) / (q1 - q0)

    a, b = d.get(10, ara(10)), d.get(90, ara(90))
    if a is None or b is None:                      # tablo P10/P90'ı kapsamıyor: kuyruk tahmini
        ps, vs = [p for p, _ in nok], [v for _, v in nok]
        med = d.get(50, ara(50))
        if med is None:
            return None
        z_alt = _STANDART_NORMAL.inv_cdf(ps[0] / 100)
        z_ust = _STANDART_NORMAL.inv_cdf(ps[-1] / 100)
        ss_alt = (med - vs[0]) / abs(z_alt) if z_alt else None
        ss_ust = (vs[-1] - med) / z_ust if z_ust else None
        if a is None and ss_alt is not None:
            a = med - VELI_ARALIK_Z * ss_alt
        if b is None and ss_ust is not None:
            b = med + VELI_ARALIK_Z * ss_ust
        if a is None or b is None:
            return None
    return min(a, b), max(a, b), False


def veli_aralik_cumlesi(cinsiyet, yetiskin, a, b, birim, kesin):
    kim = VELI_ARALIK_KIM.get((cinsiyet, bool(yetiskin)), "sporcuların" if yetiskin else "çocukların")
    return VELI_ARALIK_METNI.format(kim=kim, a=(("" if kesin else "yaklaşık ") + _aralik_sayi(a, birim)),
                                    b=_aralik_sayi(b, birim), birim=birim).replace("  ", " ")


def veli_sonuc_kutusu_html(t, ad, cinsiyet, yetiskin, renk):
    """Tek test kutusu: ad, 'Son ölçüm, tarih', değer + yer (simge ve sözcük), aralık cümlesi, bant, sabit not."""
    k = {"deger": t["deger"], "p10": t["p10"], "p90": t["p90"], "birim": t["birim"]}
    yer = veli_aralik_konumu(k)                      # Paket 38f: biraz / belirgin şekilde / çok
    isaret, kelime = VELI_YER_ISARETI[yer]
    ipucu = ("Bu testte süre kısaldıkça sonuç iyileşir." if t.get("dusuk_iyi") and t["birim"] in ("sn", "dk")
             else "Bu testte daha düşük değer daha iyidir." if t.get("dusuk_iyi") else "")
    dogru_mu = (f'<p class="veli-dogru-mu"><b>⚠ {_e(VELI_DOGRU_MU_BASLIK)}</b> {_e(VELI_DOGRU_MU)}</p>'
                if yer.endswith("_cok") else "")
    return (f'<div class="veli-aralik"><h4>{_e(t["ad"])}</h4>'
            f'<p class="kucuk">Son ölçüm, {_e(t["tarih"])}</p>'
            f'<p class="veli-deger"><b>{_e(_konum_sayi(t["deger"]))}{(" " + _e(t["birim"])) if t["birim"] else ""}</b>'
            f' · <span>{isaret} {_e(kelime)}</span></p>'
            f'<p>{_e(veli_aralik_cumlesi(cinsiyet, yetiskin, t["p10"], t["p90"], t["birim"], t["kesin"]))} '
            f'{_e(VELI_ARALIK_YERI[yer].format(ad=ad))}{(" " + _e(ipucu)) if ipucu else ""}</p>{dogru_mu}'
            f'{konum_seridi_veli_svg(k, renk)}'
            + ("" if dogru_mu else f'<p class="kucuk">{_e(VELI_ARALIK_NOTU)}</p>')   # Paket 38g: uyarı varken not yok
            + '</div>')


def veli_grup_aralik_durumu(yerler):
    """Başlığın özeti — sayım, yargı değil: "3 test yapıldı: 2 testte aralığın içinde, 1 testte biraz üstünde."."""
    if not yerler:
        return VELI_GRUP_TEST_YOK
    if len(yerler) == 1:
        return VELI_GRUP_TEK_TEST
    s = collections.Counter(yerler)
    return (f"Bu başlıkta {len(yerler)} test yapıldı: "            # Paket 38f: derece de sayılır
            + ", ".join(f"{s[y]} testte {VELI_YER_ISARETI[y][1]}" for y in VELI_YER_SIRASI if s[y]) + ".")


def veli_en_iyi_satir(test, adaylar):
    """
    Paket 38f: bir testin veli kutusundaki tek sonucu. adaylar: [(persentil, satır, seviye)], aynı gün.
    (1) "En İyi …" değişkeni varsa o; (2) yoksa denemeler (Deneme 1/2/3) arasında HAM değer ve test yönü (düşük
    iyi → en küçük), eşitlikte yüksek persentil; (3) öbür çoklu değişkenlerde (sağ/sol) en yüksek persentil.
    Persentil tablonun ucunda (P5/P95) sabitlendiğinde denemeler eşit görünür; o zaman ilk deneme seçiliyordu.
    """
    en_iyi = [a for a in adaylar if str(a[1]["Değişken"]).startswith("En İyi")]
    if en_iyi:
        return max(en_iyi, key=lambda a: a[0])
    denemeler = []
    for a in adaylar:
        if "Deneme" in str(a[1]["Değişken"]):
            try:
                denemeler.append((float(a[1]["Değer"]), a))
            except (TypeError, ValueError):
                pass
    if denemeler:
        dusuk = bool(NORMATIF_YAS.get(f"{test} › {denemeler[0][1][1]['Değişken']}", {}).get("dusuk_iyi"))
        return max(denemeler, key=lambda d: (-d[0] if dusuk else d[0], d[1][0]))[1]
    return max(adaylar, key=lambda a: a[0])            # eşitlikte ilk (önceki davranış)


def veli_test_ozeti(zp):
    """
    sporcu_z_profili → dört başlık. Her test bir kart: birden çok değişkeni olan testte (deneme 1/2,
    sağ/sol) en iyi sonuç alınır. Nötr (vücut ölçüsü) ve dışarıda bırakılan testler girmez.
    Dönen: {grup: {"testler": [{ad, deger, birim, kategori, seviye, yorum}], "durum": cümle}},
           ve "_disarida": dayanıklılık testi var mı.
    """
    secim = {}
    disarida = False
    # Paket 38c: her test yalnız SON ölçüm gününden (farklı günlerin denemeleri karışmaz); tarih kutuda yazılır
    _gun = lambda s: _tarih_gunu(s) or date.min
    son_gun = {}
    for r in zp.get("satirlar", []):
        son_gun[r["Test"]] = max(son_gun.get(r["Test"], date.min), _gun(r.get("Tarih", "")))
    for r in zp.get("satirlar", []):
        if r.get("Tür") != "Performans":
            continue
        if _gun(r.get("Tarih", "")) != son_gun.get(r["Test"]):
            continue
        if r["Test"] in VELI_DISARIDA:
            disarida = True
            continue
        if r["Test"] not in VELI_TEST_GRUBU or not r.get("Kategori"):
            continue
        sev = kategori_bilgisi(r["Kategori"])["seviye"]
        if sev is None:
            continue
        p = r.get("Performans persentili")
        p = -1 if p is None else p
        secim.setdefault(r["Test"], []).append((p, r, sev))
    secim = {test: veli_en_iyi_satir(test, adaylar) for test, adaylar in secim.items()}
    ozet = {g: {"testler": [], "durum": ""} for g in VELI_GRUPLARI}
    for test, (_, r, sev) in sorted(secim.items()):
        grup, ad = VELI_TEST_GRUBU[test]
        degiskenler = [x["Değişken"] for x in zp["satirlar"] if x["Test"] == test]
        if any("Deneme" in d for d in degiskenler) and len(degiskenler) > 1:
            ad += " (en iyi deneme)"
        elif any(d.startswith("Sağ") for d in degiskenler) and len(degiskenler) > 1:
            ad += " (sağ el)" if r["Değişken"].startswith("Sağ El") else (
                " (sol el)" if r["Değişken"].startswith("Sol El") else (
                    " (sağ bacak)" if r["Değişken"].startswith("Sağ") else " (sol bacak)"))
        birim = NORMATIF_YAS.get(f"{test} › {r['Değişken']}", {}).get("birim", "")
        zb = (zp.get("z_sozlugu") or {}).get((test, r["Değişken"]), {})
        ar = norm_araligi(zb.get("bantlar"))
        ozet[grup]["testler"].append({"ad": ad, "deger": r["Değer"], "birim": birim, "kategori": r["Kategori"],
                                      "seviye": sev, "yorum": veli_yorumu(grup, r["Kategori"]),
                                      "test": test, "tarih": r.get("Tarih", ""),
                                      "p10": ar[0] if ar else None, "p90": ar[1] if ar else None,
                                      "kesin": ar[2] if ar else None,
                                      "dusuk_iyi": bool(NORMATIF_YAS.get(f"{test} › {r['Değişken']}", {}).get("dusuk_iyi"))})
    for g in VELI_GRUPLARI:
        ozet[g]["durum"] = veli_grup_durumu([t["seviye"] for t in ozet[g]["testler"]])
    ozet["_disarida"] = disarida
    return ozet


def veli_kutu_testleri(zp):
    """Veli sonuç kutularında görünen testler (kanonik ad) — öbür bölümler bunları yinelemez."""
    oz = veli_test_ozeti(zp or {})
    return {kanonik_test(t["test"]) for g in VELI_GRUPLARI for t in oz[g]["testler"] if t.get("p10") is not None}


def veli_sonuclari_html(zp, bilgi=None):
    """
    Veli raporunun sonuç bölümü (Paket 38c): dört başlık; her test SON ölçümüyle, yayımlanmış tablonun P10–P90
    aralığı ve çocuğun bu aralığa göre yeri (simge + sözcük + bant). Sınıf etiketi ve yargı cümlesi yok.
    """
    bilgi = bilgi or {}
    yetiskin = yetiskin_mi(bilgi)
    ad = ad_bicimi(str(bilgi.get("Ad", "") or "").strip()) or ("Sporcu" if yetiskin else "Çocuğunuz")
    cins = str(bilgi.get("Cinsiyet", "") or "").strip()
    renk = palet("acik")["renk"]
    ozet = veli_test_ozeti(zp)
    p = ["<h2>Test sonuçları</h2>"]
    gosterilen = {g: [t for t in ozet[g]["testler"] if t.get("p10") is not None] for g in VELI_GRUPLARI}
    if not any(gosterilen.values()):
        p.append("<p>Henüz bu dört başlığa giren bir test sonucu yok.</p>")
    else:
        p.append(f'<p class="kucuk">{_e(VELI_SONUC_GIRIS.format(ad=ad))}</p>')
        for g in VELI_GRUPLARI:
            p.append(f'<h3 class="veli-grup">{veli_grup_simgesi(g)}<span>{_e(g)}</span></h3>'
                     f'<p class="veli-durum">{_e(veli_grup_aralik_durumu([veli_aralik_konumu({"deger": t["deger"], "p10": t["p10"], "p90": t["p90"]}) for t in gosterilen[g]]))}</p>')
            for t in gosterilen[g]:
                p.append(veli_sonuc_kutusu_html(t, ad, cins, yetiskin, renk))
        if any(not t["kesin"] for ts in gosterilen.values() for t in ts):
            p.append(f'<p class="kucuk">{_e(VELI_YAKLASIK_NOTU)}</p>')
    if ozet["_disarida"]:
        p.append(f'<p class="kucuk">{_e(VELI_DISARIDA_NOTU)}</p>')
    return "".join(p)


TR_AY_KISA = ("Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara")


def _gelisim_grafik_svg(o, renk):
    """
    Gerçek değerli mini grafik: eksen TERSLENMEZ (büyük değer yukarıda); her noktada değer, altında ay etiketi;
    düz ton (saydam renk yok). renk: {ad: renk} — raporda açık palet, uygulamada CSS değişkeni.
    """
    ys = [v for _, v in o["olcumler"]]
    if len(ys) < 2:
        return ""
    en, en_b = min(ys), max(ys)
    ar = (en_b - en) or 1.0
    gen, yuk = 260, 120
    nok = [(30 + x * 200, 92 - (y - en) / ar * 56) for x, y in zip(_tarih_konumlari(o["olcumler"]), ys)]
    goster = _etiket_secimi([a for a, _ in nok])
    p = [f'<svg viewBox="0 0 {gen} {yuk}" width="{gen}" height="{yuk}" role="img" '
         f'aria-label="{_e(o["test"])} gelişim grafiği" style="max-width:100%;height:auto">',
         f'<line x1="20" y1="100" x2="{gen - 20}" y2="100" stroke="{renk["cizgi"]}" stroke-width="1"/>',
         f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in nok)}" fill="none" stroke="{renk["ana"]}" '
         f'stroke-width="2.5"/>']
    goster_n = {nok[i] for i in goster}
    for (a, b), (t, y) in zip(nok, o["olcumler"]):
        ay = ""
        try:
            ay = f"{TR_AY_KISA[int(t[3:5]) - 1]} {t[8:10]}"
        except (ValueError, IndexError):
            pass
        p.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4" fill="{renk["ana"]}"/>')
        if (a, b) in goster_n:
            p.append(f'<text x="{a:.1f}" y="{b - 9:.1f}" text-anchor="middle" font-size="14" fill="{renk["murekkep"]}">'
                     f'{_e(_konum_sayi(y))}</text>'
                     f'<text x="{a:.1f}" y="116" text-anchor="middle" font-size="14" fill="{renk["ikincil"]}">'
                     f'{_e(ay)}</text>')
    p.append("</svg>")
    return "".join(p)


def _tarih_konumlari(olcumler):
    """
    Paket 38b: x konumu GERÇEK TARİHE orantılı (0…1). Tarih okunamazsa ya da hepsi aynı günse eşit aralık.
    """
    gunler = [_tarih_gunu(t) for t, _ in olcumler]
    n = len(olcumler)
    if None in gunler or gunler[-1] == gunler[0]:
        return [i / (n - 1) for i in range(n)]
    top = (gunler[-1] - gunler[0]).days
    return [(g - gunler[0]).days / top for g in gunler]


def _etiket_secimi(xler, aralik=34):
    """Yakın noktalarda değer/ay etiketi üst üste binmesin: son nokta her zaman, öncekiler en az 'aralik' uzakta."""
    secili, son = set(), None
    for i in range(len(xler) - 1, -1, -1):
        if son is None or son - xler[i] >= aralik:
            secili.add(i)
            son = xler[i]
    return secili


def _yon_isareti(o):
    """Son satırın yön işareti: ✓ daha iyi; yön tanımsız ya da ters yönde ▲ arttı / ▼ azaldı; = değişmedi."""
    if not o["fark"]:
        return "="
    if o["iyi_yonde"] is True:
        return "✓"
    return "▲" if o["fark"] > 0 else "▼"


def gelisim_metni(o):
    """
    Sade cümle — işaret ve % yok: "7 cm arttı — daha iyi", "2 düşme azaldı — daha iyi", "0,4 sn kısaldı — daha iyi";
    ters yönde "… — bir önceki ölçümden düşük"; yön tanımsızsa yalnız "7 cm arttı". Tek ölçüm: "İlk ölçüm."
    """
    if o["ilk"]:
        return "İlk ölçüm."
    if o["fark"] is None:
        return ""
    if o["fark"] == 0:
        return "Değişmedi"
    zaman = o["birim"] in ("sn", "dk")
    fiil = ("kısaldı" if o["fark"] < 0 else "uzadı") if zaman else ("azaldı" if o["fark"] < 0 else "arttı")
    m = " ".join(x for x in (_konum_sayi(abs(o["fark"])), o["birim"], fiil) if x)
    return m + {True: " — daha iyi", False: " — bir önceki ölçümden düşük", None: ""}[o["iyi_yonde"]]


# Paket 38b: veli kartının cümlesi ilk → son ölçüm, süreyle: "4 ayda 16 cm ilerledi: 132 cm'den 148 cm'ye."
# Ek, birimin okunuşuna göre (santimetre'den, kilogram'dan, saniye'den); eki bilinmeyen birimde ok gösterimi.
BIRIM_EKLERI = {"cm": ("'den", "'ye"), "m": ("'den", "'ye"), "sn": ("'den", "'ye"), "kg": ("'dan", "'a"),
                "dk": ("'dan", "'ya"), "W": ("'tan", "'a"), "tekrar": ("dan", "a"), "düşme": ("den", "ye"),
                "atış": ("tan", "a")}


def sure_metni(t0, t1):
    """İki tarih arası: "12 günde", "4 ayda", "2 yılda" (ay ≈ 30,44 gün; 24 ay ve üstü yıl)."""
    g0, g1 = _tarih_gunu(t0), _tarih_gunu(t1)
    if g0 is None or g1 is None:
        return ""
    gun = (g1 - g0).days
    if gun < 31:
        return f"{gun} günde"
    ay = round(gun / 30.44)
    return f"{ay} ayda" if ay < 24 else f"{round(gun / 365.25)} yılda"


def ilerleme_cumlesi(o):
    """
    Veli kartı (Paket 38b): ilk ve son ölçüm, aradaki süre. İyi yönde "ilerledi" (düşük-iyi testte "kısaldı"/"azaldı");
    yön tanımsızsa "arttı/azaldı";
    ters yönde olumsuz sözcük yok ("… değişti"); fark yoksa "değişmedi". Tek ölçümde "İlk ölçüm."
    """
    olc = o.get("olcumler") or []
    if len(olc) < 2:
        return "İlk ölçüm."
    (t0, a), (t1, b_) = olc[0], olc[-1]
    birim = o.get("birim", "")
    sure = sure_metni(t0, t1)
    ek = BIRIM_EKLERI.get(birim)
    if ek:
        aralik = f"{_konum_sayi(a)} {birim}{ek[0]} {_konum_sayi(b_)} {birim}{ek[1]}"
    else:
        aralik = f"({_konum_sayi(a)} → {_konum_sayi(b_)}{(' ' + birim) if birim else ''})"
    fark = round(b_ - a, 2)
    bas = (sure + " ") if sure else ""
    if fark == 0:
        return f"{bas}{'değişmedi' if bas else 'Değişmedi'}: {_konum_sayi(b_)}{(' ' + birim) if birim else ''}."
    yon = o.get("yon")
    iyi = None if yon is None else ((fark < 0) if yon else (fark > 0))
    miktar = " ".join(x for x in (_konum_sayi(abs(fark)), birim) if x)
    if iyi is True:                          # yüksek iyi: "ilerledi"; düşük iyi: "kısaldı" (süre) / "azaldı"
        govde = f"{miktar} {('kısaldı' if birim in ('sn', 'dk') else 'azaldı') if yon else 'ilerledi'}"
    elif iyi is None:
        govde = f"{miktar} {'arttı' if fark > 0 else 'azaldı'}"
    else:
        return f"{bas}{aralik if ek else aralik.strip('()')} değişti.".replace("  ", " ")
    return f"{bas}{govde}{': ' if ek else ' '}{aralik}."


def test_degisken_etiketi(test, degisken):
    """Test adı ile değişken adı aynıysa (birim parantezi hariç, ya da değişken test adında geçiyorsa) yalnız test."""
    kok = re.sub(r"\s*\([^()]*\)\s*$", "", str(degisken)).strip()
    if kok and ara_katla(kok) in ara_katla(test):
        return str(test)
    return f"{test} — {degisken}"


def gelisim_karti_html(o, renk, cumle=None):
    """≥ 2 ölçüm: solda Tarih | Sonuç (alt alta; son satırda yön işareti), sağda mini grafik, altında sade cümle.
    cumle: verilirse (veli kartı) o cümle; yoksa son iki ölçümün farkı (gelisim_metni)."""
    b = o["birim"]
    satir = []
    for i, (t, y) in enumerate(o["olcumler"]):
        isaret = f' <span aria-label="yön">{_yon_isareti(o)}</span>' if i == len(o["olcumler"]) - 1 else ""
        satir.append(f'<tr><td>{_e(t)}</td><td class="sayi">{_e(_konum_sayi(y))}{(" " + _e(b)) if b else ""}{isaret}</td></tr>')
    return (f'<div class="gelisim-kart" style="border:1px solid {renk["cizgi"]};border-radius:10px;padding:12px 14px;'
            f'margin:10px 0"><h3 style="margin:0 0 8px">{_e(o["test"])} — {_e(o["degisken"])}</h3>'
            f'<div style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start">'
            f'<table style="flex:1 1 200px;min-width:200px;font-size:14px"><tr><th>Tarih</th><th>Sonuç</th></tr>'
            f'{"".join(satir)}</table><div style="flex:1 1 260px">{_gelisim_grafik_svg(o, renk)}</div></div>'
            f'<p style="margin:8px 0 0;font-size:14px">{_e(cumle if cumle is not None else gelisim_metni(o))}</p></div>')


def ilk_olcum_tablosu_html(sat):
    """Tek ölçümlü testler TEK tabloda: Test | Sonuç | Tarih."""
    if not sat:
        return ""
    return ('<h3>İlk ölçümü yapılan testler</h3><table class="ilk-olcum" style="font-size:14px">'
            '<tr><th>Test</th><th>Sonuç</th><th>Tarih</th></tr>'
            + "".join(f'<tr><td>{_e(test_degisken_etiketi(o["test"], o["degisken"]))}</td><td class="sayi">'
                      f'{_e(_konum_sayi(o["olcumler"][0][1]))}{(" " + _e(o["birim"])) if o["birim"] else ""}</td>'
                      f'<td>{_e(o["olcumler"][0][0])}</td></tr>' for o in sat) + "</table>")


def gelisim_bolumu_html(liste, renk, veli=False):
    """Kartlar (≥ 2 ölçüm) + tek ölçümlüler için tek tablo. veli=True: kart cümlesi ilk → son (ilerleme_cumlesi)."""
    coklu = [o for o in liste if len(o["olcumler"]) >= 2]
    tek = [o for o in liste if len(o["olcumler"]) == 1]
    return ("".join(gelisim_karti_html(o, renk, ilerleme_cumlesi(o) if veli else None) for o in coklu)
            + ilk_olcum_tablosu_html(tek))


# Paket 38c: çok bileşenli testlerin veli raporundaki tek satırı (bilinen testler); öbürleri genel özet
VELI_BILESIK_OZET = {
    "Nordic Hamstring Kuvvet Testi (NHT)": "Nordic Hamstring: sağ/sol bacak kuvveti ve denge",
    "Nordic Hamstring Kuvvet Testi — Genel (NHT)": "Nordic Hamstring: sağ/sol bacak kuvveti ve denge",
}


VELI_BILESIK_NOTU = "Ayrıntılı bileşenler antrenör raporundadır."


def veli_bilesik_satiri(s):
    """Çok bileşenli test → tek satır: bilinen testte hazır özet; 2-3 bileşende adları ("son seviye ve son tekrar");
    daha fazlasında bileşen sayısı. Değerler antrenör raporunda."""
    if s["test"] in VELI_BILESIK_OZET:
        return VELI_BILESIK_OZET[s["test"]]
    adlar = [re.sub(r"\s*\([^()]*\)\s*$", "", str(d)).strip().translate(_TR_KUCULT)
             for d in s["degiskenler"] if not str(d).startswith("Rölatif")]
    if 2 <= len(adlar) <= 3:
        return f"{s['test']}: {', '.join(adlar[:-1])} ve {adlar[-1]}"
    return f"{s['test']}: {len(adlar)} bileşenli ölçüm"


def veli_bolumleri(v, haric=()):
    """
    Veli raporunda her test TEK seviye yerinde: sonuç kutusu (haric) > tek ölçüm tablosu > çok bileşenli satırı.
    Kendi gelişimi kartı yalnız ≥ 2 ölçüm günü olan ana sonuçlu testlerde (son değeri kutudakiyle aynı gün).
    Dönen: {"kart": [...], "tek": [...], "bilesik": [...]} — vücut ölçüleri girmez.
    """
    haric = {kanonik_test(t) for t in haric}
    tum = [s for s in v.get("gelisim_test", []) if test_niteligi(s["test"]) != "antropometri"]
    return {"kart": [s for s in tum if s["tur"] != "bilesik" and len(s["olcumler"]) >= 2],
            "tek": [s for s in tum if s["tur"] != "bilesik" and len(s["olcumler"]) == 1 and s["test"] not in haric],
            "bilesik": [s for s in tum if s["tur"] == "bilesik" and s["test"] not in haric]}


def veli_gelisim_html(v, haric=()):
    """Veli raporu 'Kendi gelişimi' (kâğıt, açık palet): kartlar + ilk ölçüm tablosu + çok bileşenli satırlar."""
    b_ = veli_bolumleri(v, haric)
    if not (b_["kart"] or b_["tek"] or b_["bilesik"]):
        return ""
    p = ["<h2>Kendi gelişimi</h2>",
         '<p class="kucuk">Her test, çocuğunuzun kendi önceki ölçümleriyle karşılaştırıldı.</p>',
         gelisim_bolumu_html(b_["kart"] + b_["tek"], palet("acik")["renk"], veli=True)]
    if b_["bilesik"]:
        p.append('<h3>Birden çok bileşeni olan testler</h3><table class="bilesik" style="font-size:14px">'
                 '<tr><th>Test</th><th>Son ölçüm</th></tr>'
                 + "".join(f'<tr><td>{_e(veli_bilesik_satiri(s))}</td><td>{_e(s["son_tarih"])}</td></tr>'
                           for s in b_["bilesik"]) + "</table>"
                 f'<p class="kucuk">{_e(VELI_BILESIK_NOTU)}</p>')
    return "".join(p)


def veli_konum_uygun(k):
    """Veli raporunda konum: yaş ≥ 11, n ≥ 20, yön tanımlı (nötr ölçü değil), vücut ölçüsü değil."""
    return (k.get("durum") == "tamam" and k.get("yon") is not None and k.get("p10") is not None
            and k["n"] >= GRUP_KONUM_YUZDELIK_N
            and k.get("yas") is not None and k["yas"] >= VELI_KONUM_EN_AZ_YAS
            and test_niteligi(k["test"]) != "antropometri")


def _aralik_sayi(x, birim):
    """Veli aralığı (Paket 38a): cm ve kg tam sayı ("105–143 cm"), sn bir ondalık, öbürleri en çok bir ondalık."""
    if birim in ("cm", "kg") or birim in {b_ for _, b_ in SAYIM_BIRIMLERI} | {"adet"}:   # Paket 38c: sayım tam
        return str(int(round(float(x))))
    if birim == "sn":
        return f"{float(x):.1f}".replace(".", ",")
    return f"{round(float(x), 1):g}".replace(".", ",")


def veli_aralik_yeri(k):
    """Çocuğun değeri havuzun P10–P90 aralığına göre: "altinda" / "icinde" / "ustunde"."""
    return "altinda" if k["deger"] < k["p10"] else ("ustunde" if k["deger"] > k["p90"] else "icinde")


def veli_aralik_konumu(k):
    """
    Paket 38f: yer + sapmanın büyüklüğü — "icinde", "ustunde"/"altinda" (biraz), "…_belirgin", "…_cok".
    SD, P10–P90 bandından tahmin edilir (bant = 2 × 1,2816 SD); eşikler VELI_SAPMA_Z.
    """
    yer = veli_aralik_yeri(k)
    genislik = k["p90"] - k["p10"]
    if yer == "icinde" or not genislik or genislik <= 0:
        return yer
    sd = genislik / (2 * VELI_ARALIK_Z)
    uzaklik = (k["deger"] - k["p90"]) if yer == "ustunde" else (k["p10"] - k["deger"])
    z = VELI_ARALIK_Z + uzaklik / sd
    if z > VELI_SAPMA_Z[1]:
        return f"{yer}_cok"
    if z > VELI_SAPMA_Z[0]:
        return f"{yer}_belirgin"
    return yer


def konum_seridi_veli_svg(k, renk):
    """
    Veli sürümü şerit: yalnız P10–P90 bandı (açık palet, düz ton) ve çocuğun yeri tek işaret. Havuzdaki öbür
    değerler ÇİZİLMEZ (başka çocuk görünmez). Ölçek bandı ve çocuğun değerini kapsar.
    """
    a, b, d = k["p10"], k["p90"], k["deger"]
    en, en_b = min(a, d), max(b, d)
    pay = ((en_b - en) or 1.0) * 0.15
    en, en_b = en - pay, en_b + pay
    x = lambda v_: 12 + (v_ - en) / (en_b - en) * 296
    xa, xb = x(a), x(b)
    ya, yb = ("end", "start") if xb - xa < 48 else ("middle", "middle")   # yakın uçlar: yazılar dışa doğru
    birim = k.get("birim", "")
    return (f'<svg viewBox="0 0 320 58" width="320" height="58" role="img" '
            f'aria-label="Aralık şeridi: {_e(_aralik_sayi(a, birim))}–{_e(_aralik_sayi(b, birim))} {_e(birim)}">'
            f'<line x1="12" y1="22" x2="308" y2="22" stroke="{renk["cizgi"]}" stroke-width="2"/>'
            f'<rect x="{xa:.1f}" y="14" width="{xb - xa:.1f}" height="16" rx="3" fill="{renk["cizgi"]}"/>'
            f'<circle cx="{x(d):.1f}" cy="22" r="6" fill="{renk["ana"]}"/>'
            f'<text x="{xa:.1f}" y="50" text-anchor="{ya}" font-size="14" fill="{renk["murekkep"]}">'
            f'{_e(_aralik_sayi(a, birim))}</text>'
            f'<text x="{xb:.1f}" y="50" text-anchor="{yb}" font-size="14" fill="{renk["murekkep"]}">'
            f'{_e(_aralik_sayi(b, birim))}</text></svg>')


def veli_konum_metni(k, ad, yetiskin=False):
    """İki cümle: aralık ("Bu yaştaki erkek çocukların çoğu A–B birim arasında") ve yeri. Çeyrek/yüzdelik/sıra yok."""
    kim = VELI_ARALIK_KIM.get((k.get("cinsiyet"), bool(yetiskin)), "sporcuların" if yetiskin else "çocukların")
    yer = veli_aralik_konumu(k)                      # Paket 38f: biraz / belirgin şekilde / çok (+ doğru mu?)
    return (VELI_ARALIK_METNI.format(kim=kim, a=_aralik_sayi(k["p10"], k["birim"]),
                                     b=_aralik_sayi(k["p90"], k["birim"]), birim=k["birim"]).replace("  ", " ")
            + " " + VELI_ARALIK_YERI[yer].format(ad=ad)
            + (f" {VELI_DOGRU_MU_BASLIK} {VELI_DOGRU_MU}" if yer.endswith("_cok") else ""))


def veli_konum_html(v, haric=()):
    """Veli raporu 'Yaşıtlarına göre nerede?': şartı sağlayan, sonuç kutusunda OLMAYAN testler; başka çocuk adı yok."""
    haric = {kanonik_test(t) for t in haric}
    sat = [k for k in v.get("konum", []) if veli_konum_uygun(k) and kanonik_test(k["test"]) not in haric]
    if not sat:
        return ""                                   # bölüm yok (boş başlık da yok)
    renk = palet("acik")["renk"]
    yetiskin = yetiskin_mi(v.get("bilgi"))
    ad = ad_bicimi(str((v.get("bilgi") or {}).get("Ad", "") or "").strip()) or ("Sporcu" if yetiskin else "Çocuğunuz")
    p = [f"<h2>{_e(VELI_YASIT_BASLIK)}</h2>"]
    for k in sat:
        p.append(f'<div class="veli-konum"><h3>{_e(test_degisken_etiketi(k["test"], k["degisken"]))}</h3>'
                 f'<p>{_e(veli_konum_metni(k, ad, yetiskin))}</p>{konum_seridi_veli_svg(k, renk)}'
                 f'<p>{_e(VELI_ARALIK_NOTU)}</p>'
                 f'<p class="kucuk">{_e(VELI_KONUM_METNI.format(n=k["n"]))}</p></div>')
    return "".join(p)


def veli_raporu_html(v):
    """Sade dil; Z, persentil, uzaklık sayısı yok."""
    b = v["bilgi"]
    ad = _e(ad_bicimi(f"{b.get('Ad', '')} {b.get('Soyad', '')}".strip() or v["sporcu"]))
    esl, pen, puan = v["esl"], v["pen"], v["puan"]
    p = [f'<!doctype html><html lang="tr"><head><meta charset="utf-8">'
         f'<meta name="viewport" content="width=device-width, initial-scale=1">'
         f'<title>Veli raporu — {ad}</title>{RAPOR_CSS}</head><body class="veli">'
         f'<div class="sayfa">{kimlik_html()}']
    p.append(f"<h1>{ad} — Spor yönlendirme bilgisi</h1>")
    olcum = (f"Ölçümler: {v['tarih_araligi'][0]} – {v['tarih_araligi'][1]}" if v["tarih_araligi"]
             else "Henüz fiziksel ölçüm yok")
    anket = f"İlgi anketi: {_e(v['ilgi'].get('Tarih', ''))}" if v["ilgi"] else "İlgi anketi henüz doldurulmadı"
    p.append(f'<div class="alt">Rapor tarihi: {v["rapor_tarihi"]} · {olcum} · {anket}</div>')
    p.append('<p>Bu sayfa iki şeyi ayrı ayrı gösterir: çocuğunuzun hangi etkinlikleri sevdiğini ve '
             'fiziksel özelliklerinin hangi spor gruplarındaki çocuklara benzediğini. İkisi tek bir puanda '
             'birleştirilmez. Bu bir karar değil, konuşmayı başlatacak bir bilgidir.</p>')

    p.append('<h2>İki pencere</h2><div class="iki">')
    # Pencere 1: sevdikleri
    p.append(f'<div class="kutu sev"><h3 class="veli-grup">{veli_grup_simgesi("sevdikleri")}<span>Sevdiği etkinlikler</span></h3>')
    if not v["ilgi"]:
        p.append('<p>İlgi anketi henüz doldurulmadı.</p>')
    elif pen["seviyor"]:
        p.append("<ul>" + "".join(
            f'<li><b>{_e(g)}</b>{" <span class=yildiz>★</span>" if g in pen["kesisim"] else ""}'
            f' — {_e(ilgi_etiketi(puan.get(g)).lower())}<br><span class="kucuk">ör. {_e(_brans_ornekleri(g))}</span></li>'
            for g in pen["seviyor"]) + "</ul>")
    else:
        p.append('<p>Ankette belirgin bir tercih çıkmadı.</p>')
    p.append("</div>")
    # Pencere 2: fiziksel
    p.append(f'<div class="kutu fiz"><h3 class="veli-grup">{veli_grup_simgesi("fiziksel")}<span>Fiziksel özellikleri bu gruplara yakın</span></h3>')
    if esl["uygun"]:
        p.append("<ul>" + "".join(
            f'<li><b>{_e(g)}</b>{" <span class=yildiz>★</span>" if pen and g in pen["kesisim"] else ""}'
            f'<br><span class="kucuk">ör. {_e(_brans_ornekleri(g))}</span></li>' for g in v["fiziksel_uc"]) + "</ul>")
        p.append('<p class="kucuk">Sıra yoktur; üç grup arasında bir öncelik yoktur.</p>')
    else:
        try:
            yas_i = int(float(b.get("Yaş")))
        except (TypeError, ValueError):
            yas_i = None
        if yas_i is not None and not (ESLESTIRME_YAS_ARALIGI[0] <= yas_i <= ESLESTIRME_YAS_ARALIGI[1]):
            neden = "Bu karşılaştırma yalnızca 9-11 yaş çocuklar için yapılabiliyor."
        elif yas_i is None:
            neden = "Profilde yaş bilgisi olmadığı için karşılaştırma yapılamadı."
        else:
            neden = (f"Karşılaştırma için en az {ESLESTIRME_EN_AZ_DEGISKEN} ölçüm gerekiyor; şu an "
                     f"{len(esl['kullanilan'])} ölçüm var.")
        p.append(f"<p>{_e(neden)}</p>")
    p.append("</div></div>")

    if pen and pen["kesisim"]:
        p.append(f'<div class="kesisim"><span class="yildiz">★</span> <b>Hem seviyor hem fiziksel özellikleri '
                 f'yakın:</b> {_e(", ".join(pen["kesisim"]))}. Bu, en güçlü işarettir; bu gruplardaki sporları '
                 f'denemek iyi bir başlangıç olabilir.</div>')
    if pen and esl["uygun"]:
        if pen["yalniz_ilgi"]:
            p.append(f'<div class="not">Çocuğunuz <b>{_e(", ".join(pen["yalniz_ilgi"]))}</b> grubundaki etkinlikleri '
                     f'seviyor; fiziksel özellikleri ise daha çok başka gruplara benziyor. Sevdiği sporu yapması '
                     f'önemlidir: sevilen spor daha uzun süre sürdürülür. Fiziksel özellikler antrenmanla değişir.</div>')
        elif pen["yalniz_fiziksel"] and pen["seviyor"]:
            p.append(f'<div class="not">Fiziksel özellikleri <b>{_e(", ".join(pen["yalniz_fiziksel"]))}</b> grubuna da '
                     f'benziyor, ama ankette bu grubu sevdiğini belirtmedi. Bu yalnızca bilgidir; çocuğunuzu '
                     f'istemediği bir spora yönlendirmek için bir gerekçe değildir.</div>')
        elif pen["yalniz_fiziksel"]:
            p.append('<div class="not">Ankette belirgin bir ilgi çıkmadı. Fiziksel olarak benzediği gruplardaki '
                     'sporları birkaç kez denemek, neyi sevdiğini görmek için iyi bir yoldur.</div>')
    if pen and pen["bilinmeyen"]:
        p.append(f'<p class="kucuk">Henüz bilmediği ya da yeterince yanıtlamadığı gruplar: '
                 f'{_e(", ".join(pen["bilinmeyen"]))}. Bu sporları denemek ilgisini öğrenmenin en iyi yoludur.</p>')

    kutuda = veli_kutu_testleri(v.get("zp") or {})  # Paket 38c: her test tek seviye yerinde
    p.append(veli_sonuclari_html(v.get("zp") or {}, b))
    p.append(veli_gelisim_html(v, kutuda))          # Paket 36: önce kendi gelişimi,
    p.append(veli_konum_html(v, kutuda))            # sonra (şartlar sağlanırsa) grup içindeki konum

    p.append("<h2>Bu bilgiyi okurken</h2>")
    p.append('<div class="uyari"><b>Fiziksel karşılaştırma eleyici değildir.</b> Çocuğunuzun fiziksel '
             'özelliklerinin bir gruba benzememesi, o sporu yapamayacağı ya da o sporda başarılı olamayacağı '
             'anlamına gelmez. Bu yaşta fiziksel özellikler antrenmanla ve büyümeyle hızla değişir; spor '
             'grupları da fiziksel olarak birbirine çok yakındır.</div>')
    if v["hacim"] == "Haftada 5 saat ve üzeri":
        guven = ("Çocuğunuz haftada 5 saat ve üzeri antrenman yapıyor. Araştırmada bu düzeyde antrenman yapan "
                 "çocuklarda fiziksel özellikler spor gruplarını daha iyi ayırt etti.")
    elif v["hacim"] == "Bilinmiyor":
        guven = ("Haftalık antrenman süresi kayıtlı olmadığı için fiziksel karşılaştırmanın ne kadar güvenilir "
                 "olduğu söylenemez. Araştırmada bu karşılaştırma yalnızca haftada 5 saat ve üzeri antrenman "
                 "yapan çocuklarda güvenilir çıktı.")
    else:
        guven = ("Haftada 5 saatten az antrenman yapan çocuklarda fiziksel özellikler spor gruplarını birbirinden "
                 "pek ayırmıyor. Bu yüzden fiziksel karşılaştırmayı yalnızca fikir verici olarak okuyun.")
    if esl["uygun"]:
        p.append(f'<div class="not">{guven}</div>')
    p.append('<div class="uyari"><b>İlgi anketi henüz doğrulanmamıştır.</b> Anket bu uygulama için hazırlanmıştır; '
             'bilimsel geçerlik ve güvenirlik çalışması henüz yapılmamıştır. Sonuçlar bir değerlendirme değil, '
             'çocuğunuzla konuşmak için bir başlangıç noktasıdır.</div>')
    p.append('<p>Bu yaşta birden fazla sporu denemek önerilir. Hangi sporda devam edeceğine karar verirken '
             'çocuğunuzun isteği en önemli bilgidir.</p>')
    p.append('<p class="kucuk">Fiziksel karşılaştırma, Belçika\'da 9-11 yaşında 620 çocukla yapılan bir '
             'araştırmadaki altı spor grubuna göre yapılmıştır (Opstoel ve ark., 2015).</p>')
    p.append(f'<div class="veli-son">{_e(VELI_SON_PARAGRAF)}</div>')   # sabit, her raporun son paragrafı
    p.append("</div></body></html>")
    return veli_hitabi("".join(p), yetiskin_mi(b))                 # Paket 38b: yetişkinde "Sporcunun …"


RAPOR_TERIMLERI = ["Z skoru", "Performans persentili", "Persentil", "P5 / P95", "Sınır değer (P5 altı / P95 üstü)", "Norm",
                   "Düşük-iyi test", "Nötr (tanımlayıcı) ölçüm", "Taban / tavan etkisi", "Doğum çeyreği",
                   "Ortalama Z", "Güven düzeyi", "Ortalama standart uzaklık", "Havuzlanmış standart sapma",
                   "Branş grubu katmanı"]


def antrenor_raporu_html(v):
    """Teknik rapor: persentil, Z, radar, eksikler, tarihler, güven ve dayanağı, normlar, sınır durumları."""
    b, zp, esl, fsc = v["bilgi"], v["zp"], v["esl"], v["fsc"]
    tanim = BRANS_GRUBU_PROFILLERI["degiskenler"]
    ad = _e(ad_bicimi(f"{b.get('Ad', '')} {b.get('Soyad', '')}".strip() or v["sporcu"]))
    p = [f'<!doctype html><html lang="tr"><head><meta charset="utf-8">'
         f'<meta name="viewport" content="width=device-width, initial-scale=1">'
         f'<title>Antrenör raporu — {ad}</title>{RAPOR_CSS}</head><body><div class="sayfa">{kimlik_html()}']
    p.append(f"<h1>{ad} — Antrenör raporu</h1>")
    boy, kilo = b.get("Boy (cm)"), b.get("Kilo (kg)")
    p.append(f'<div class="alt">Rapor tarihi: {v["rapor_tarihi"]} · Yaş (profil): {_e(b.get("Yaş", "—"))} · '
             f'Cinsiyet: {_e(b.get("Cinsiyet", "—"))} · Branş: {_e(b.get("Spor Dalı", "—"))} · '
             f'Boy: {_e(boy)} cm · Kilo: {_e(kilo)} kg</div>')

    # 1. Güven düzeyi
    p.append("<h2>1. Güven düzeyi ve dayanağı</h2>")
    kayit = f" (profile kayıt: {_e(v['hacim_tarih'])})" if v["hacim_tarih"] else ""
    p.append(f"<p><b>Haftalık organize antrenman:</b> {_e(v['hacim'])}{kayit}.</p>")
    if v["hacim"] in GUVEN_DUZEYLERI:
        g = GUVEN_DUZEYLERI[v["hacim"]]
        p.append(f'<div class="{"not" if g["anlamli"] else "uyari"}">{_e(g["metin"])}</div>')
    else:
        p.append('<div class="uyari">Antrenman süresi kayıtlı değil; güven düzeyi belirlenemez. Opstoel ve ark. '
                 '(2015): doğru sınıflama 5+ saat %85.2 (n=81), 1-5 saat %48.8 (n=252), ≤1 saat %48.4 (n=184).</div>')
    p.append('<p class="kucuk">Dayanak: Opstoel ve ark. (2015) diskriminant modeli. Uygulamadaki eşleştirme '
             'onların modeli değildir (katsayılar yayımlanmadı); havuzlanmış grup içi SD ile ortalama standart '
             f'uzaklık. Simülasyon: doğru grup %{ESLESTIRME_SIMULASYON["ilk_sira"]} ilk sırada, '
             f'%{ESLESTIRME_SIMULASYON["ilk_uc"]} ilk üçte (şans %{ESLESTIRME_SIMULASYON["sans_ilk"]} / '
             f'%{ESLESTIRME_SIMULASYON["sans_ilk_uc"]}).</p>')

    # 2. Test test persentil ve Z
    p.append("<h2>2. Test sonuçları — yaş/cinsiyet persentili ve Z</h2>")
    if zp["hata"]:
        p.append(f'<div class="uyari">{_e(zp["hata"])}</div>')
    elif not zp["satirlar"]:
        p.append("<p>Yaş bazlı normu olan test kaydı yok.</p>")
    else:
        kartlar_r = []
        for r in sorted(zp["satirlar"], key=lambda r: (r["Tür"] != "Performans", r["Test"], r["Değişken"])):
            zb = zp["z_sozlugu"].get((r["Test"], r["Değişken"]), {})
            etiket_r = f"{r['Test']} — {r['Değişken']}"
            not_r = " · ".join(n_s for a_s, n_s in v["sinirlar"] if a_s == etiket_r) or r["Not"]
            yas_t = zb.get("yas")
            if yas_t is not None and int(yas_t) != int(r["Norm yaşı"]):
                not_r = (not_r + " · " if not_r else "") + f"test yaşı {int(yas_t)}"
            kartlar_r.append(z_satiri_karti(r, zb, teknik=True, not_metni=not_r))
        p.append(kart_izgarasi_html(kartlar_r))
        p.append('<p class="kucuk">Z persentil sırasından türetilir (Z = ters normal(persentil)); performans '
                 'yönlü (+ = akranlarından iyi). Antropometrik ölçüler nötrdür, iyi/kötü yorumu yapılmaz. '
                 'P5–P95 bantlı normlarda Z en fazla ±1.64, P20–P80 bantlılarda ±0.84.</p>')
        for ad_b, bz in v["bilesikler"].items():
            if bz["deger"] is None:
                p.append(f"<p><b>{_e(ad_b)}:</b> hesaplanmadı — eksik: {_e(', '.join(bz['eksik']))}.</p>")
            else:
                ek = f" ({bz['bilesen_sayisi']} test)" if bz["dislanan"] else ""
                p.append(f"<p><b>{_e(ad_b)}{ek}:</b> {_sayi(bz['deger'], 2, True)}. "
                         f"<span class=kucuk>{_e(BILESIK_Z[ad_b]['aciklama'])}</span></p>")

    # 3. Sınır durumları
    p.append("<h2>3. Sınır durumları</h2>")
    if v["sinirlar"]:
        p.append("<table><tr><th>Ölçüm</th><th>Durum</th></tr>" + "".join(
            f"<tr><td>{_e(a)}</td><td>{_e(n)}</td></tr>" for a, n in v["sinirlar"]) + "</table>")
    else:
        p.append("<p>Sınır durumu yok: hiçbir değer bant dışında değil, tüm normlar sporcunun yaşında ve "
                 "cinsiyetinde mevcut, bileşikten çıkarılan test yok.</p>")

    # 4. Radar
    p.append("<h2>4. Radar — Z profili</h2>")
    perf = [r for r in zp["satirlar"] if r["Tür"] == "Performans"] if not zp["hata"] else []
    if len(perf) >= 3:
        eks = [f"{r['Test'].split(' (')[0]} — {r['Değişken']}" for r in perf]
        p.append('<div class="radar">' + radar_svg(eks, [(v["sporcu"], [r["Z"] for r in perf], _RAPOR_RENK["ana"], False)])
                 + "</div>")
        p.append('<p class="kucuk">Kalın halka Z = 0 (akran ortalaması). Değerler ±3 aralığına sınırlıdır.</p>')
    else:
        p.append(f"<p>Radar için normu olan en az 3 performans testi gerekli (şu an {len(perf)}).</p>")
    k = v["katman"]
    if k and k["uygun"]:
        p.append("<h3>Branş grubu katmanı (fiziksel profilin yakın olduğu üç grup)</h3>")
        eks = [e["ad"] for e in k["eksenler"]]
        katmanlar = [(v["sporcu"], [e["z"] for e in k["eksenler"]], _RAPOR_RENK["ana"], False)]
        for i, g in enumerate(v["fiziksel_uc"]):
            katmanlar.append((g, [e["gruplar"][g]["z"] for e in k["eksenler"]], GRUP_RENKLERI[i % 3], True))
        p.append('<div class="radar">' + radar_svg(eks, katmanlar) + "</div>")
        p.append("<table><tr><th>Değişken</th><th>Sporcu (değer / Z)</th>" +
                 "".join(f"<th>{_e(g)} (ort. / Z)</th>" for g in v["fiziksel_uc"]) + "</tr>")
        for e in k["eksenler"]:
            p.append(f"<tr><td>{_e(e['ad'])}</td><td class=sayi>{_e(e['deger'])} / {_sayi(e['z'], 2, True)}</td>" +
                     "".join(f"<td class=sayi>{_e(e['gruplar'][g]['ort'])} / {_sayi(e['gruplar'][g]['z'], 2, True)}</td>"
                             for g in v["fiziksel_uc"]) + "</tr>")
        p.append("</table>")
        p.append(f'<p class="kucuk">{_e(GRUP_KATMANI_NOTU)} Radardan çıkarılan değişkenler: '
                 + _e("; ".join(f"{a} ({n})" for a, n in k["cikarilan"]))
                 + "; boy, kilo, VKİ, oturma yüksekliği (antropometrik).</p>")
    elif k:
        p.append(f'<p class="kucuk">Grup katmanı çizilmedi: {_e(k["neden"])}</p>')

    # 5. Branşa yönlendirme
    p.append("<h2>5. Branşa yönlendirme</h2>")
    p.append('<div class="iki"><div class="kutu sev"><h3>İlgi (anket)</h3>')
    if v["ilgi"]:
        p.append(f'<p class="kucuk">{_e(ILGI_ANKET_ADI)} · {_e(v["ilgi"].get("Tarih", ""))}</p><table>'
                 "<tr><th>Grup</th><th>Ortalama (1-5)</th><th>Etiket</th></tr>" + "".join(
                     f"<tr><td>{_e(g)}{' <span class=yildiz>★</span>' if v['pen'] and g in v['pen']['kesisim'] else ''}</td>"
                     f"<td class=sayi>{_sayi(v['puan'].get(g), 1) if v['puan'].get(g) is not None else '—'}</td>"
                     f"<td>{_e(ilgi_etiketi(v['puan'].get(g)))}</td></tr>"
                     for g in BRANS_GRUBU_PROFILLERI["gruplar"]) + "</table>")
        tercihler = [str(v["ilgi"].get(kd)) for kd, _, _ in ILGI_TERCIHLERI
                     if _girildi(v["ilgi"].get(kd)) and v["ilgi"].get(kd) != "İkisi de / fark etmez"]
        if tercihler:
            p.append(f'<p class="kucuk">Tercihleri: {_e(" · ".join(tercihler))}</p>')
    else:
        p.append("<p>Anket yok.</p>")
    p.append('</div><div class="kutu fiz"><h3>Fiziksel profil (sırasız ilk üç)</h3>')
    if esl["uygun"]:
        p.append("<p>" + " · ".join(f"<b>{_e(g)}</b>" for g in v["fiziksel_uc"]) + "</p>")
        p.append("<table><tr><th>Grup</th><th>Ort. standart uzaklık</th></tr>" + "".join(
            f"<tr><td>{_e(g)}</td><td class=sayi>{float(u):.2f}</td></tr>" for g, u in esl["siralama"]) + "</table>")
        p.append('<p class="kucuk">Uzaklık farkları yorumlanmamalı: grup merkezleri arası 0.11-0.20 standart birim. '
                 f'{len(esl["kullanilan"])} değişken kullanıldı.</p>')
    else:
        p.append(f"<p>{_e(esl['neden'])}</p>")
    p.append("</div></div>")
    if v["pen"] and v["pen"]["kesisim"]:
        p.append(f'<div class="kesisim"><span class="yildiz">★</span> Kesişim: {_e(", ".join(v["pen"]["kesisim"]))}</div>')
    p.append('<p class="kucuk">İlgi ve fiziksel profil tek skorda birleştirilmez. Fiziksel profil bilgilendiricidir, '
             'eleyici değildir. Grup değerleri erkek-kız karışık; cinsiyet düzeltilemedi. ' + _e(ILGI_UYARI) + "</p>")

    # 6. Eksik testler ve ölçüm tarihleri
    p.append("<h2>6. Eksik testler ve ölçüm tarihleri</h2>")
    eksik_esl = [tanim[kd]["ad"] for kd in fsc["eksik"] if kd in ESLESTIRME_DEGISKENLERI]
    p.append("<table><tr><th>Ne için</th><th>Eksik</th></tr>")
    p.append(f"<tr><td>Branş eşleştirmesi (11 performans değişkeni)</td><td>{_e(', '.join(eksik_esl) or 'yok')}</td></tr>")
    for ad_b, bz in v["bilesikler"].items():
        p.append(f"<tr><td>{_e(ad_b)}</td><td>{_e(', '.join(bz['eksik']) or 'yok')}</td></tr>")
    p.append(f"<tr><td>Eşleştirmeye hiç girmeyen (protokol eşleşmedi)</td>"
             f"<td>{_e(', '.join(tanim[kd]['ad'] for kd in fsc['eslesmeyen']))}</td></tr>")
    p.append(f"<tr><td>Kayıtlı ama yaş normu olmayan testler</td><td>{_e(', '.join(v['normsuz']) or 'yok')}</td></tr>")
    p.append("</table>")
    if v["testler"]:
        p.append("<table><tr><th>Kayıtlı test</th><th>Ölçüm sayısı</th><th>Son ölçüm</th></tr>" + "".join(
            f"<tr><td>{_e(t['Test'])}</td><td class=sayi>{t['Ölçüm sayısı']}</td><td>{_e(t['Son ölçüm'])}</td></tr>"
            for t in sorted(v["testler"], key=lambda t: t["Test"])) + "</table>")
    else:
        p.append("<p>Kayıtlı test yok.</p>")

    # Paket 36: kendi gelişimi ve grup içi konum (başka sporcuların adı yok; n < 20 iken yüzdelik yok)
    if v.get("gelisim"):
        p.append("<h2>Kendi gelişimi ve grup içi konum</h2>")
        renk = palet("acik")["renk"]
        bilesik = {s["test"] for s in v.get("gelisim_test", []) if s["tur"] == "bilesik"}
        liste = ([s for s in v.get("gelisim_test", []) if s["tur"] != "bilesik"]
                 + [o for o in v["gelisim"] if kanonik_test(o["test"]) in bilesik])   # Paket 38c
        p.append(gelisim_bolumu_html(liste, renk))                  # Paket 38a: kartlar + ilk ölçüm tablosu
        p.append("<h3>Grup içi konum</h3>")
        for k in v.get("konum", []):
            p.append(f'<p class=kucuk><b>{_e(k["test"])} — {_e(k["degisken"])}:</b> '
                     + " · ".join(_e(m) for m in konum_metinleri(k)) + "</p>" + konum_seridi_svg(k, renk))

    # 7. Kaynaklar
    p.append("<h2>7. Kullanılan norm kaynakları</h2><ul>")
    for kyn in v["kaynaklar"]:
        p.append(f"<li class=kucuk>{_e(kyn)}</li>")
    p.append(f"<li class=kucuk>{_e(BRANS_GRUBU_PROFILLERI['kaynak'])}</li>")
    p.append("</ul>")

    # 8. Terimler — uygulamadaki ⓘ açıklamalarıyla aynı kaynak (ACIKLAMALAR)
    p.append("<h2>8. Terimler</h2>")
    for t in RAPOR_TERIMLERI:
        p.append(f"<p class=kucuk><b>{_e(t)}:</b> {_e(ACIKLAMALAR[t])}</p>")
    p.append("</div></body></html>")
    return _tablolari_sar("".join(p))


KAYNAKCA_DAYANAK = ("SCImago Journal Rank (SJR) 2025 — derginin kategorileri içindeki en iyi çeyrek (SJR Best "
                    "Quartile). Veri: SCImago yıllık dışa aktarımlarını derleyen sjrdata paketi (v1.0.25, Haziran 2026). "
                    "Sınıflandırma tarihi: 14.10.2026.")


KAYNAKCA_SINIFLAR = ["Q1", "Q2", "Q3/Q4", "Scopus (çeyreklik dışı)", "İndekslenmeyen", "Belirlenemedi"]
