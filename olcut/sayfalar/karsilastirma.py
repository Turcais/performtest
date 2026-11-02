"""
Karşılaştırma ekranı (Paket 38g): Sonuçlar sayfasının üstündeki "Karşılaştırma" bölümü. İki sekme:
"Sporcular arası" (iki sporcu grubu A / B) ve "Oturumlar arası" (önce / sonra oturum kümeleri).
Her sekmede iki seçim sütunu (onay kutusu, arama, Tümünü seç / Temizle), "Karşılaştır" düğmesi; basılana kadar sonuç
bölümü pasif, seçim değişirse sonuç "eski" diye işaretlenir. Hesap: olcut/karsilastirma.py.
"""
import os
import pandas as pd
import streamlit as st
from olcut.bilesenler import coklu_secim
from olcut.disa_aktarma import guvenli_dosya_adi, tablo_csv, tablo_xlsx, tarih_eki
from olcut.karsilastirma import (
    KARS_ISTATISTIK_EN_AZ_N, KARS_KARISIK_UYARI, KARS_KUCUK_NOTU, KARS_YUZDELIK_YOK_NOTU, csv_ile_istatistik, etki_metni,
    grup_ozeti_disa, istatistik_disa, karisik_mi, ortak_testler, oturum_adlari, oturum_etiketleri, oturum_testleri,
    oturumlar_arasi, oturumlar_arasi_disa, sayisal_degiskenler, sporcu_ozellikleri, sporcular_arasi,
    sporcular_arasi_disa, wilcoxon_isaretli_sira, KULUPLER_ARASI_EN_AZ_N, degisen_yetersiz_metni, kulupler_arasi, normlu_degisken,
    p_metni)
from olcut.kulup import karsilastirma_katilimcilari, kulup_verisi
from olcut.katalog_islemleri import ara_katla, test_tablosu_duzelt
from olcut.norm import TEST_DOSYA
from olcut.ortak import ad_bicimi, aktif_kulup, veri_yolu
from olcut.tema import grafik_duzeni, grafik_renk

KARS_PASIF_IPUCU = "Önce sporcuları seçip Karşılaştır'a basın."
KARS_PASIF_IPUCU_OTURUM = "Önce oturumları seçip Karşılaştır'a basın."
KARS_ESKI_NOTU = "Seçim değişti; aşağıdaki sonuç eski. Güncellemek için yeniden Karşılaştır'a basın."
KARS_TUM_OTURUMLAR = "Tüm oturumlar"


def _sayi(x, basamak=2):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{x:.{basamak}f}".rstrip("0").rstrip(".").replace(".", ",")


def indirme_dugmeleri(sayfalar, csv_tablosu, tur, onek):
    """Paket 38i: sonuç tablosunu Excel (sayfalar) ve CSV olarak indirme; dosya adı Karsilastirma_<tur>_<GGAAYYYY>."""
    ad = guvenli_dosya_adi("Karsilastirma", tur, tarih_eki())
    c1, c2 = st.columns(2)
    c1.download_button("Tabloyu Excel olarak indir", tablo_xlsx(sayfalar), file_name=f"{ad}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key=f"{onek}_xlsx", icon=":material/table_view:", width="stretch")
    c2.download_button("CSV olarak indir", tablo_csv(csv_tablosu), file_name=f"{ad}.csv", mime="text/csv",
                       key=f"{onek}_csv", icon=":material/download:", width="stretch")


# ── seçim sütunu ──
def _secim(onek):
    return st.session_state.setdefault(f"{onek}::secim", [])


def _kutu_degisti(onek, kimlik):
    s = _secim(onek)
    if st.session_state.get(f"{onek}::k::{kimlik}"):
        if kimlik not in s:
            s.append(kimlik)
    elif kimlik in s:
        s.remove(kimlik)


def _hepsi(onek, kimlikler, deger):
    s = _secim(onek)
    for k in kimlikler:
        if deger and k not in s:
            s.append(k)
        if not deger and k in s:
            s.remove(k)
        st.session_state[f"{onek}::k::{k}"] = deger


def secim_sutunu(baslik, secenekler, onek, aciklama=""):
    """
    secenekler: {kimlik: etiket}. Onay kutulu çoklu seçim; arama kutusu yalnız görünümü süzer (gizlenen seçim kalır).
    Seçim {onek}::secim listesinde tutulur. Dönen: seçili kimlikler (seçenek sırasıyla).
    """
    secili = _secim(onek)
    secili[:] = [k for k in secili if k in secenekler]
    with st.container(border=True, key=f"kars-sutun-{onek}"):
        st.markdown(f"**{baslik}**")
        if aciklama:
            st.caption(aciklama)
        ara = st.text_input("Ara", key=f"{onek}::ara", placeholder="Ada göre ara", label_visibility="collapsed")
        q = ara_katla(ara.strip()) if ara.strip() else ""
        gorunen = [k for k, et in secenekler.items() if not q or q in ara_katla(et)]
        b1, b2 = st.columns(2)
        b1.button("Tümünü seç", key=f"{onek}::hepsi", on_click=_hepsi, args=(onek, gorunen, True), width="stretch",
                  help="Görünen (aramaya uyan) satırların hepsini seçer")
        b2.button("Temizle", key=f"{onek}::temizle", on_click=_hepsi, args=(onek, list(secenekler), False),
                  width="stretch")
        with st.container(height=300):
            if not gorunen:
                st.caption("Aramaya uyan yok.")
            for k in gorunen:
                st.checkbox(secenekler[k], key=f"{onek}::k::{k}", on_change=_kutu_degisti, args=(onek, k),
                            **({} if f"{onek}::k::{k}" in st.session_state else {"value": k in secili}))
        st.caption(f"{len(secili)} seçili")
    return [k for k in secenekler if k in secili]


def _pasif(ipucu):
    st.markdown(f'<div class="kars-pasif">{ipucu}</div>', unsafe_allow_html=True)


def _durum(anahtar, parametre):
    """Saklanan karşılaştırma parametresi (None: henüz basılmadı) ve eski mi."""
    saklanan = st.session_state.get(anahtar)
    return saklanan, (saklanan is not None and saklanan != parametre)


def _sakla(anahtar, parametre):
    st.session_state[anahtar] = parametre


# ── Sporcular arası ──
def _sporcular_arasi(df):
    sporcular = sorted(df["Sporcu"].dropna().astype(str).unique().tolist())
    etiket = {s: ad_bicimi(s) for s in sporcular}
    c1, c2 = st.columns(2)
    with c1:
        grup_a = secim_sutunu("Sporcu seç — Grup A", etiket, "ksa_a")
    with c2:
        grup_b = secim_sutunu("Sporcu seç — Grup B", etiket, "ksa_b",
                              "Boş bırakılırsa karşılaştırma yalnız A'daki sporcular arasında yapılır.")
    ikisi = [s for s in grup_a if s in grup_b]
    if ikisi:
        st.warning("Aynı sporcu iki grupta da seçili: " + ", ".join(etiket[s] for s in ikisi)
                   + ". Bu sporcu iki grubun ortalamasına da girer.", icon=":material/info:")
    ot = oturum_etiketleri(df)
    ot_secim = coklu_secim("Oturum", [KARS_TUM_OTURUMLAR] + list(ot), key="ksa_oturum",
                           format_func=lambda k: k if k == KARS_TUM_OTURUMLAR else ot[k],
                           **({} if "ksa_oturum" in st.session_state else {"default": [KARS_TUM_OTURUMLAR]}))
    oturumlar = None if (not ot_secim or KARS_TUM_OTURUMLAR in ot_secim) else tuple(ot_secim)
    df_o = df if oturumlar is None else df[df["Oturum"].astype(str).isin(oturumlar)]
    secili = list(dict.fromkeys(grup_a + grup_b))
    testler = ortak_testler(df_o, secili)
    t1, t2 = st.columns(2)
    test = t1.selectbox("Test (seçilenlerin ortak testleri)", testler or ["—"], key="ksa_test",
                        disabled=not testler)
    degiskenler = sayisal_degiskenler(df_o, test) if testler else []
    degisken = t2.selectbox("Değişken", degiskenler or ["—"], key="ksa_degisken", disabled=not degiskenler)
    if secili and not testler:
        st.caption("Seçilen sporcuların hepsinin yaptığı bir test yok.")
    karisik = bool(secili) and karisik_mi(sporcu_ozellikleri(secili))
    z = st.toggle("Z-skoru da göster (yaşa ve cinsiyete göre norm)", key="ksa_z",
                  help="Karışık yaş/cinsiyette ham değer yanında norm tablosuna göre Z. Normu olmayanda —.") \
        if karisik else False
    parametre = {"A": tuple(grup_a), "B": tuple(grup_b), "oturum": oturumlar, "test": test, "degisken": degisken,
                 "z": bool(z)}
    hazir = bool(grup_a) and bool(testler) and bool(degiskenler)
    st.button("Karşılaştır", type="primary", key="ksa_karsilastir", disabled=not hazir, on_click=_sakla,
              args=("ksa::sonuc", parametre), help=None if hazir else "Grup A'dan en az bir sporcu ve bir test seçin.")
    saklanan, eski = _durum("ksa::sonuc", parametre)
    with st.container(border=True, key="kars-sonuc-ksa"):
        if saklanan is None:
            _pasif(KARS_PASIF_IPUCU)
            return
        if eski:
            st.info(KARS_ESKI_NOTU, icon=":material/history:")
        _sporcular_arasi_sonuc(df, saklanan, etiket)


def _sporcular_arasi_sonuc(df, p, etiket):
    import plotly.graph_objects as go
    r = sporcular_arasi(df, p["test"], p["degisken"], p["A"], p["B"], p["oturum"], z=p["z"])
    st.markdown(f"**{p['test']} — {p['degisken']}**" + (f" ({r['birim']})" if r["birim"] else ""))
    if r["karisik"]:
        st.warning(KARS_KARISIK_UYARI + ("" if p["z"] else " Z-skoru için yukarıdaki düğmeyi açabilirsiniz."),
                   icon=":material/warning:")
    if r["kucuk"]:
        st.info(KARS_KUCUK_NOTU, icon=":material/child_care:")
    if r["olcumsuz"]:
        st.caption("Bu test/değişkende ölçümü olmayan: " + ", ".join(etiket.get(s, s) for s in r["olcumsuz"]))
    if not r["satirlar"]:
        st.info("Seçilenlerin bu değişkende ölçümü yok.")
        return
    tablo = pd.DataFrame(r["satirlar"])
    tablo["Sporcu"] = tablo["Sporcu"].map(ad_bicimi)
    st.dataframe(tablo, hide_index=True, width="stretch",
                 column_config={"Değer": st.column_config.NumberColumn("Değer", format="%.2f"),
                                "Yaş": st.column_config.NumberColumn("Yaş", format="%d")})
    for grup, oz in r["ozet"].items():
        ad = f"Grup {grup}"
        if not oz.get("n"):
            st.caption(f"{ad}: ölçüm yok.")
            continue
        metin = (f"**{ad}** · n = {oz['n']} · ortalama {_sayi(oz['ortalama'])} {r['birim']} · aralık "
                 f"{_sayi(oz['en_kucuk'])}–{_sayi(oz['en_buyuk'])} {r['birim']}")
        if oz.get("p25") is not None:
            metin += f" · çeyrekler (P25–P75) {_sayi(oz['p25'])}–{_sayi(oz['p75'])}"
        st.markdown(metin)
    if any(oz.get("n") and oz.get("p25") is None for oz in r["ozet"].values()):
        st.caption(KARS_YUZDELIK_YOK_NOTU)
    renk = {"A": grafik_renk("ana"), "B": grafik_renk("ikincil")}
    fig = go.Figure()
    for grup in ("A", "B"):
        g = tablo[tablo["Grup"] == grup]
        if g.empty:
            continue
        fig.add_trace(go.Bar(x=[f"{grup} · {s}" for s in g["Sporcu"]], y=g["Değer"], name=f"Grup {grup}",
                             marker_color=renk[grup], text=[f"{grup} · {_sayi(v)}" for v in g["Değer"]],
                             textposition="outside", cliponaxis=False))
        oz = r["ozet"].get(grup) or {}
        if oz.get("n"):
            fig.add_hline(y=oz["ortalama"], line_dash="dash" if grup == "A" else "dot", line_color=renk[grup],
                          annotation_text=f"Grup {grup} ortalaması {_sayi(oz['ortalama'])}",
                          annotation_position="top left" if grup == "A" else "bottom right")
    fig.update_layout(title=f"{p['test']} — {p['degisken']}", yaxis_title=r["birim"] or p["degisken"],
                      showlegend=True, **grafik_duzeni())
    st.plotly_chart(fig, width="stretch")
    st.caption("Grup harfi her çubuğun üstünde yazılıdır; kesikli çizgi A, noktalı çizgi B ortalaması."
               + ("" if r["kucuk"] else " Sıra testin yönüne göredir (en iyi önce)."))
    disa = sporcular_arasi_disa(df, r, p["test"], p["degisken"], p["oturum"])
    indirme_dugmeleri({"Sonuçlar": disa, "Grup özeti": grup_ozeti_disa(r)}, disa, "sporcular", "ksa_indir")


# ── Oturumlar arası ──
def _oturumlar_arasi(df):
    ot = oturum_etiketleri(df)
    if not ot:
        st.info("Kayıtlarda oturum yok; oturumlar arası karşılaştırma için Test Oturumu sayfasından giriş yapın.")
        return
    c1, c2 = st.columns(2)
    with c1:
        sol = secim_sutunu("Oturum seç — Önce", ot, "koa_once")
    with c2:
        sag = secim_sutunu("Oturum seç — Sonra", ot, "koa_sonra")
    ikisi = [o for o in sol if o in sag]
    if ikisi:
        st.warning("Aynı oturum iki tarafta da seçili: " + ", ".join(ot[o] for o in ikisi)
                   + ". Önce ve Sonra farklı oturumlar olmalı.", icon=":material/info:")
    testler = oturum_testleri(df, sol, sag)
    t1, t2 = st.columns(2)
    test = t1.selectbox("Test (iki tarafta da ölçülen)", testler or ["—"], key="koa_test", disabled=not testler)
    degiskenler = sayisal_degiskenler(df, test) if testler else []
    degisken = t2.selectbox("Değişken", degiskenler or ["—"], key="koa_degisken", disabled=not degiskenler)
    ist = st.checkbox("İstatistik göster", key="koa_ist", value=False,
                      help=f"n ≥ {KARS_ISTATISTIK_EN_AZ_N}: Wilcoxon işaretli sıra testi ve etki büyüklüğü.")
    parametre = {"sol": tuple(sol), "sag": tuple(sag), "test": test, "degisken": degisken, "ist": bool(ist)}
    hazir = bool(sol) and bool(sag) and bool(testler) and bool(degiskenler) and not ikisi
    st.button("Karşılaştır", type="primary", key="koa_karsilastir", disabled=not hazir, on_click=_sakla,
              args=("koa::sonuc", parametre),
              help=None if hazir else "İki tarafta da (farklı) en az bir oturum ve ortak bir test seçin.")
    saklanan, eski = _durum("koa::sonuc", parametre)
    with st.container(border=True, key="kars-sonuc-koa"):
        if saklanan is None:
            _pasif(KARS_PASIF_IPUCU_OTURUM)
            return
        if eski:
            st.info(KARS_ESKI_NOTU, icon=":material/history:")
        _oturumlar_arasi_sonuc(df, saklanan)


def _oturumlar_arasi_sonuc(df, p):
    import plotly.graph_objects as go
    r = oturumlar_arasi(df, p["test"], p["degisken"], p["sol"], p["sag"])
    st.markdown(f"**{p['test']} — {p['degisken']}**" + (f" ({r['birim']})" if r["birim"] else ""))
    if r["kucuk"]:
        st.info(KARS_KUCUK_NOTU, icon=":material/child_care:")
    if not r["satirlar"]:
        st.info("İki tarafta da bu değişkende ölçümü olan sporcu yok.")
        return
    tablo = pd.DataFrame(r["satirlar"])
    tablo["Sporcu"] = tablo["Sporcu"].map(ad_bicimi)
    st.dataframe(tablo[["Sporcu", "Yaş", "Önce", "Sonra", "Fark", "Yön"]], hide_index=True, width="stretch",
                 column_config={"Fark": st.column_config.NumberColumn("Fark", format="%+.2f"),
                                "Yaş": st.column_config.NumberColumn("Yaş", format="%d")})
    fig = go.Figure(go.Bar(
        y=tablo["Sporcu"], x=tablo["Fark"], orientation="h",
        text=[f"{y} ({_sayi(f)})" for f, y in zip(tablo["Fark"], tablo["Yön"])], textposition="outside",
        cliponaxis=False,
        marker_color=[grafik_renk("ana") if y == "daha iyi" else grafik_renk("ikincil") for y in tablo["Yorum"]]))
    _m = max(0.01, float(tablo["Fark"].abs().max()))
    fig.update_layout(title=f"{p['test']} — {p['degisken']}: oturumlar arası fark",
                      xaxis=dict(title="Fark (sonra − önce)", range=[-2.2 * _m, 2.2 * _m], zeroline=True),
                      height=max(260, 46 * len(tablo) + 120), **grafik_duzeni())
    st.plotly_chart(fig, width="stretch")
    st.caption("Fark = sonra − önce. Yön sözcükle yazılır (✓ daha iyi, ! daha kötü; 11 yaş altında ve yönü "
               "tanımsız ölçüde yalnız ▲ arttı / ▼ azaldı); renk tek başına anlam taşımaz.")
    ort = tablo["Fark"].mean()
    st.markdown(f"Ortalama fark {_sayi(ort)} {r['birim']} · n = {len(tablo)} sporcu")
    w = wilcoxon_isaretli_sira(tablo["Fark"].tolist()) if p["ist"] else None
    if p["ist"]:
        if w.get("yetersiz"):
            st.caption("D" + degisen_yetersiz_metni(w)[1:] + "; istatistik testi yapılmadı (sıfır farklar "
                       "sayılmaz).")                          # "değişen…" → "Değişen…" (.capitalize Türkçe i/İ'yi bozar)
        else:
            st.markdown(f"**Wilcoxon işaretli sıra testi** ({w['yontem']}): n = {w['n']}, W = {_sayi(w['w'])}, "
                        f"{p_metni(w['p'])} · etki büyüklüğü (eşleştirilmiş sıra-iki serili) r = "
                        f"{_sayi(w['r'])} ({etki_metni(w['r'])})")
            st.caption("Sıfır farklar testten çıkarılır. r > 0: sonra değerleri büyük; testin iyi yönü için "
                       "tablodaki Yön sütununa bakın.")
    disa = oturumlar_arasi_disa(r, p["test"], p["degisken"], oturum_adlari(df, p["sol"]),
                                oturum_adlari(df, p["sag"]))
    indirme_dugmeleri({"Sonuçlar": disa, "İstatistik": istatistik_disa(w)}, csv_ile_istatistik(disa, w),
                      "oturumlar", "koa_indir")


# ── Kulüpler arası (Paket 38o) ──
KARS_KULUP_ACIKLAMA = (f"Yalnız toplu değerler: her kulüpte sporcu başına son ölçüm, yaş bandı × cinsiyet hücresinde "
                       f"sporcu sayısı ve ortalama. {KULUPLER_ARASI_EN_AZ_N}'dan az sporcu olan hücrede değer "
                       "gösterilmez; en küçük ve en büyük değer hiç gösterilmez (tek bir sporcunun değeridir); çeyrekler "
                       "yalnız 20 ve üstü sporcuda. Satırlar kulübe göre dizilir, başarıya göre sıralanmaz. Sporcu adı "
                       "yoktur; yalnız kulüp bilgilerinde karşılaştırmaya onay vermiş kulüpler katılır.")
KARS_KULUP_PASIF = "Test ve değişkeni seçip Karşılaştır'a basın."
KARS_KULUP_YAS_NOTU = ("Bant içinde yaş dağılımı kulüpten kulübe değişir; ham ortalamaları ortalama yaşla birlikte "
                       "okuyun.")


def kulup_etiketleri(katilan, aktif):
    """Seçili kulüp adıyla, ötekiler kod sırasıyla 'Kulüp 1, 2…' (başka kulübün adı görünmez)."""
    etiket, i = {}, 1
    if aktif in katilan:
        etiket[aktif] = katilan[aktif]["ad"]
    for kod in sorted(katilan):
        if kod != aktif:
            etiket[kod], i = f"Kulüp {i}", i + 1
    return etiket


def _kulupler_arasi():
    st.caption(KARS_KULUP_ACIKLAMA)
    katilan, aktif = karsilastirma_katilimcilari(), aktif_kulup()
    if aktif and aktif not in katilan:
        st.info("Bu kulüp kulüpler arası karşılaştırmaya onay vermemiş; ötekilerin değerleri de gösterilmez. Onay, "
                "Kulüpler sayfasında kulüp bilgilerinden verilir.", icon=":material/lock:")
        return
    if len(katilan) < 2:
        st.info(f"Kulüpler arası karşılaştırma için en az iki kulübün onayı gerekli (şu an {len(katilan)}). Onay, "
                "Kulüpler sayfasında kulüp bilgilerinden verilir.", icon=":material/info:")
        return
    etiket = kulup_etiketleri(katilan, aktif)
    veriler = [(etiket[k], *kulup_verisi(k)) for k in etiket]
    sayim = {}
    for _, _, df_t in veriler:
        for t in (set(df_t["Test"].dropna().astype(str)) if not df_t.empty and "Test" in df_t.columns else set()):
            sayim[t] = sayim.get(t, 0) + 1
    testler = sorted(t for t, n in sayim.items() if n >= 2)
    if not testler:
        st.info("Onaylı kulüplerin en az ikisinde ölçülmüş ortak bir test yok.")
        return
    st.caption("Katılan kulüpler: " + ", ".join(etiket.values()))
    tum = pd.concat([d for _, _, d in veriler if not d.empty], ignore_index=True)
    t1, t2 = st.columns(2)
    test = t1.selectbox("Test (en az iki kulüpte ölçülen)", testler, key="kka_test")
    degiskenler = sayisal_degiskenler(tum, test)
    degisken = t2.selectbox("Değişken", degiskenler or ["—"], key="kka_degisken", disabled=not degiskenler)
    z = (st.checkbox("Z-skoru ile göster", key="kka_z",
                     help="Her sporcunun Z'si değerin ölçüldüğü günkü yaşa ve cinsiyete göre normdan; hücrede Z'lerin "
                          f"ortalaması (en az {KULUPLER_ARASI_EN_AZ_N} sporcu).")
         if degiskenler and normlu_degisken(test, degisken) else False)
    parametre = {"test": test, "degisken": degisken, "kulupler": tuple(etiket), "z": bool(z)}
    st.button("Karşılaştır", type="primary", key="kka_karsilastir", disabled=not degiskenler, on_click=_sakla,
              args=("kka::sonuc", parametre))
    saklanan, eski = _durum("kka::sonuc", parametre)
    with st.container(border=True, key="kars-sonuc-kka"):
        if saklanan is None:
            _pasif(KARS_KULUP_PASIF)
            return
        if eski:
            st.info(KARS_ESKI_NOTU, icon=":material/history:")
        r = kulupler_arasi(veriler, saklanan["test"], saklanan["degisken"], z=saklanan.get("z", False))
        st.markdown(f"**{saklanan['test']} — {saklanan['degisken']}**" + (f" ({r['birim']})" if r["birim"] else ""))
        if not r["satirlar"]:
            st.info("Bu değişkende yaşı ve cinsiyeti bilinen ölçüm yok.")
            return
        st.caption(KARS_KULUP_YAS_NOTU)
        st.dataframe(pd.DataFrame(r["satirlar"]), hide_index=True, width="stretch",
                     column_config={"Ortalama": st.column_config.NumberColumn("Ortalama", format="%.2f"),
                                    "Ort. yaş": st.column_config.NumberColumn("Ort. yaş", format="%.1f"),
                                    "Ort. Z": st.column_config.NumberColumn("Ort. Z", format="%.2f"),
                                    "P25": st.column_config.NumberColumn("P25", format="%.2f"),
                                    "P75": st.column_config.NumberColumn("P75", format="%.2f")})


def karsilastirma_sayfasi():
    """Sonuçlar → Karşılaştırma bölümü: Genel (sporcular arası) / Oturumlar arası / Kulüpler arası (38o)."""
    st.header("Karşılaştırma")
    df = None
    if os.path.exists(veri_yolu(TEST_DOSYA)):
        df = test_tablosu_duzelt(pd.read_excel(veri_yolu(TEST_DOSYA)))
        df["Tarih_dt"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y", errors="coerce")
    s1, s2, s3 = st.tabs(["Genel", "Oturumlar arası", "Kulüpler arası"])
    veri_var = df is not None and not df.empty
    for sekme, ciz in ((s1, _sporcular_arasi), (s2, _oturumlar_arasi)):
        with sekme:
            if veri_var:
                ciz(df)
            else:
                st.info("Kaydedilmiş test sonucu yok.")
    with s3:
        _kulupler_arasi()
