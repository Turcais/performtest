"""
Raporlar (veli ve antrenör raporu) ve Kaynakça sayfaları.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import os
import pandas as pd
import streamlit as st
from veri.metinler import KAYNAKCA
from olcut.analiz import rapor_verisi
from olcut.bilesenler import baslik_ac, bolum_terimleri, coklu_secim
from olcut.disa_aktarma import PDF_YAZDIRMA_ADIMLARI, guvenli_dosya_adi, pdf_cevir, tarih_eki
from olcut.norm import SPORCU_DOSYA
from olcut.ortak import ad_bicimi
from olcut.raporlar import KAYNAKCA_DAYANAK, KAYNAKCA_SINIFLAR, antrenor_raporu_html, veli_raporu_html


@st.cache_data(show_spinner=False, max_entries=16)
def rapor_pdf(html_metin):
    """Rapor HTML'i aynen PDF'e (Paket 38i); çevrilemezse None. Aynı HTML ikinci kez çevrilmez."""
    return pdf_cevir(html_metin)[0]


def rapor_indirme(html_metin, tur, sporcu, onek):
    """
    "PDF olarak indir" (tek tık); çevirici yoksa yazdırmaya hazır HTML + adım adım talimat. HTML her durumda
    indirilebilir. Dosya adı: <Tur>_raporu_<Ad_Soyad>_<GGAAYYYY>; PDF'e ekranda gösterilen HTML'in kendisi girer.
    """
    ad = guvenli_dosya_adi(f"{tur}_raporu", ad_bicimi(sporcu), tarih_eki())
    with st.spinner("PDF hazırlanıyor…"):
        pdf = rapor_pdf(html_metin)
    c1, c2 = st.columns(2)
    if pdf:
        c1.download_button("PDF olarak indir", pdf, file_name=f"{ad}.pdf", mime="application/pdf", type="primary",
                           key=f"{onek}_pdf", icon=":material/picture_as_pdf:", width="stretch")
    c2.download_button("HTML olarak indir" if pdf else "Yazdırmaya hazır HTML indir", html_metin.encode("utf-8"),
                       file_name=f"{ad}.html", mime="text/html", key=onek, icon=":material/download:",
                       type="secondary" if pdf else "primary", width="stretch")
    if not pdf:
        st.info(PDF_YAZDIRMA_ADIMLARI, icon=":material/print:")


def raporlar_sayfasi():
    """Raporlar sayfası (Bölme Aşama 2: satır içi dal fonksiyona sarıldı)."""
    def rapor_goster(html_metin, yukseklik):
        """Yeni Streamlit'te st.iframe; eski sürümlerde components.html (2026'da kaldırılıyor)."""
        if hasattr(st, "iframe"):
            st.iframe(html_metin, height=yukseklik)
        else:
            import streamlit.components.v1 as components
            components.html(html_metin, height=yukseklik, scrolling=True)

    st.header("Raporlar")
    st.caption("Veli raporu sade dille yazılır; Z, persentil ve uzaklık sayısı içermez. Antrenör raporu tekniktir. "
               "İkisi de PDF olarak tek tıkla indirilebilir (A4).")
    if not os.path.exists(SPORCU_DOSYA):
        st.info("Sistemde kayıtlı sporcu yok.")
    else:
        df_r = pd.read_excel(SPORCU_DOSYA)
        r_liste = sorted((df_r["Ad"].astype(str) + " " + df_r["Soyad"].astype(str)).tolist())
        r_sporcu = st.selectbox("Sporcu", r_liste, key="rapor_sporcu", format_func=ad_bicimi)
        r_veri = rapor_verisi(r_sporcu)
        if r_veri["hacim"] == "Bilinmiyor":
            st.warning("Haftalık antrenman süresi profilde kayıtlı değil; raporlarda güven düzeyi "
                       "\"belirlenemedi\" olarak yazılır. Sporcu Girişi sayfasından eklenebilir.")
        if not r_veri["ilgi"]:
            st.info("İlgi anketi doldurulmamış; raporların ilgi penceresi boş kalır. Anket Sporcu Girişi sayfasında.")
        r1, r2 = st.tabs(["Veli raporu", "Antrenör raporu"])
        with r1:
            veli_html = veli_raporu_html(r_veri)
            rapor_indirme(veli_html, "Veli", r_sporcu, "veli_indir")
            rapor_goster(veli_html, 1300 + 130 * veli_html.count('class="veli-satir"'))
        with r2:
            ant_html = antrenor_raporu_html(r_veri)
            rapor_indirme(ant_html, "Antrenor", r_sporcu, "ant_indir")
            rapor_goster(ant_html, 1400)


def kaynakca_sayfasi():
    """Kaynakça sayfası (Bölme Aşama 2: satır içi dal fonksiyona sarıldı)."""
    baslik_ac("Kaynakça", ["SJR çeyreği"], "header")
    bolum_terimleri(["SJR çeyreği"])
    st.caption("Uygulamadaki testlerin, normların ve anketin dayandığı tüm kaynaklar, indeks durumuna göre.")
    st.info("**Sınıflandırmanın dayanağı:** " + KAYNAKCA_DAYANAK + " Kitaplar, kurum kılavuzları ve el kitapları "
            "(ör. Council of Europe, Beltz Test, FitnessGram) dergi olmadığı için \"İndekslenmeyen\" sınıfındadır. "
            "Dergisi listede doğrulanamayan kaynaklar tahmin edilmeden \"Belirlenemedi\" olarak işaretlendi.")
    sayim = {s_: sum(1 for x in KAYNAKCA if x["s"] == s_) for s_ in KAYNAKCA_SINIFLAR}
    dergiler = {}
    for x in KAYNAKCA:
        if x["d"]:
            dergiler[x["d"]] = x["s"]
    k1, k2 = st.columns(2)
    with k1:
        st.metric("Benzersiz kaynak", len(KAYNAKCA))
    with k2:
        st.metric("Farklı dergi adı", len(dergiler))
    st.dataframe(pd.DataFrame([{"Sınıf": s_, "Kaynak": sayim[s_],
                                "Dergi": sum(1 for v in dergiler.values() if v == s_)}
                               for s_ in KAYNAKCA_SINIFLAR]),
                 width="stretch", hide_index=True)
    st.caption("Dergi sayısında bazı dergiler eski ve yeni adıyla iki kez yer alır (ör. Canadian Journal of Applied "
               "Physiology → Applied Physiology, Nutrition and Metabolism); eski adlar bugünkü dergiyle sınıflandı.")
    secili_sinif = coklu_secim("Sınıf filtresi", KAYNAKCA_SINIFLAR, default=KAYNAKCA_SINIFLAR)
    arama = st.text_input("Kaynak ara (yazar, dergi, başlık)")
    for s_ in [x for x in KAYNAKCA_SINIFLAR if x in secili_sinif]:
        liste = [x for x in KAYNAKCA if x["s"] == s_ and (not arama or arama.lower() in (x["k"] + x["d"]).lower())]
        if not liste:
            continue
        with st.expander(f"{s_} — {len(liste)} kaynak", expanded=False):
            for x in liste:
                ek = f" *({x['n']})*" if x["n"] else ""
                st.markdown(f"- {x['k']}{ek}")
