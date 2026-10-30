"""
Sonuçları Görüntüle — ayrıntılı genel görünüm: tablo, grafikler, radar, Excel (karşılaştırma: Paket 38g ayrı bölüm).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import os
import pandas as pd
import streamlit as st
from io import BytesIO
from veri.brans_profilleri import BILESIK_Z, BRANS_GRUBU_PROFILLERI
from veri.metinler import ACIKLAMALAR, GUVEN_DUZEYLERI
from olcut.raporlar import (
    ANTRENOR_AYIRT_EDILEMEZ, ANTRENOR_YAYILIM_SATIRI, ANTRENOR_YAYILIM_YONTEMI, VELI_FIZIKSEL_AYIRT_EDILEMEZ,
    VELI_OZET_AYIRT_EDILEMEZ, VELI_OZET_AYIRT_EDILEMEZ_SEVIYOR, yayilim_simulasyon_tablosu)
from olcut.analiz import (
    ESLESTIRME_AYIRT_ESIGI, fiziksel_pencere, ANTRENMAN_SECENEKLERI, ANTRENMAN_YARDIM, ESLESTIRME_DEGISKENLERI, ESLESTIRME_SIMULASYON, GRUP_KATMANI_NOTU,
    ILGI_ANKET_ADI, ILGI_HAKKINDA, ILGI_TERCIHLERI, ILGI_UYARI, brans_grubu_eslestir, grup_radar_katmani,
    ilgi_etiketi, ilgi_fiziksel_pencereler, ilgi_grup_puanlari, ilgi_son_anket, sporcu_antrenman,
    sporcu_antrenman_kaydet, sporcu_fsc_profili, sporcu_profil_bilgisi, z_satiri_karti)
from olcut.bilesenler import (
    _gecerli_secim, _karsilastirmaya_git, baslik_ac, bolum_terimleri, coklu_secim, grup_konum_penceresi, sekme_hatasi, sutun_yardimi)
from olcut.katalog_islemleri import test_tablosu_duzelt
from olcut.kayit import oturum_secenekleri
from olcut.norm import (
    BILESIK_MAKS_GUN, META_KOLONLAR, NORMATIF, SPORCU_DOSYA, TEST_DOSYA, bilesik_z_hesapla,
    normatif_degerlendir, orneklem_disi_metni, orneklem_notlari, orneklem_tablosu, sporcu_z_profili)
from olcut.oneri import ozet_kartlari_html
from olcut.ortak import ad_bicimi, veri_yolu
from olcut.tema import _sayi_goster, grafik_duzeni, grafik_norm_renk, grafik_renk, kart_izgarasi_html


def sonuclari_goruntule_sayfasi():
    """Sonuçları Görüntüle sayfası (Bölme Aşama 2: satır içi dal fonksiyona sarıldı)."""
    st.header("Test Sonuçları ve Analiz")

    if not os.path.exists(veri_yolu(TEST_DOSYA)):
        st.info("Kaydedilmiş test sonucu yok.")
    else:
        df_test = test_tablosu_duzelt(pd.read_excel(veri_yolu(TEST_DOSYA)))     # takma adlı kayıt asıl adla (Paket 27)

        # Tarih sütununu datetime'a çevir
        try:
            df_test["Tarih_dt"] = pd.to_datetime(df_test["Tarih"], format="%d.%m.%Y", errors="coerce")
        except Exception:
            df_test["Tarih_dt"] = pd.NaT

        # ── Test oturumu filtresi (Paket 10): "şu tarihteki taramanın sonuçları" ──
        if "Oturum" in df_test.columns:
            _ot_deger = df_test["Oturum"].fillna("").astype(str).str.strip()
            df_oturumlu = df_test[(_ot_deger != "") & (_ot_deger != "nan")]       # OT-… ve "Çalışma · zaman"
            if not df_oturumlu.empty:
                ot_etiket = oturum_secenekleri(df_oturumlu)                     # Paket 38d: ortak liste
                _gecerli_secim("sonuc_oturum", ["Tüm kayıtlar"] + list(ot_etiket))
                ot_secim = st.selectbox("Test oturumu", ["Tüm kayıtlar"] + list(ot_etiket),
                                        format_func=lambda k: k if k == "Tüm kayıtlar" else ot_etiket[k],
                                        key="sonuc_oturum")
                if ot_secim != "Tüm kayıtlar":
                    df_test = df_test[df_test["Oturum"] == ot_secim]

        sporcular = ["Tüm Sporcuları Göster"] + sorted(df_test["Sporcu"].unique().tolist())
        _gecerli_secim("sonuc_sporcu", sporcular)
        filtre = st.selectbox("Sporcu Filtrele", sporcular, key="sonuc_sporcu", format_func=ad_bicimi)

        df_filtre = df_test if filtre == "Tüm Sporcuları Göster" else df_test[df_test["Sporcu"] == filtre]
        if filtre != "Tüm Sporcuları Göster":                      # Paket 36: sporcu kartı → küçük pencere
            st.toggle("Ayrıntılı analiz (7 sekme)", key="sonuc_ayrintili",          # Paket 38b: kapat → kartlar
                      help="Kapatınca bu sporcu için dört soru kartı görünür.")
            with st.container(border=True):
                _kp = sporcu_profil_bilgisi(filtre)
                c_k1, c_k2 = st.columns([3, 1], vertical_alignment="center")
                c_k1.markdown(f"**{_html.escape(filtre)}** · {_html.escape(str(_kp.get('Yaş', '—')))} yaş · "
                              f"{_html.escape(str(_kp.get('Cinsiyet', '—')))} · "
                              f"{df_filtre['Test'].nunique()} test, {len(df_filtre)} kayıt")
                if c_k2.button("Grup içi konum", icon=":material/groups:", key="gk_ac", width="stretch"):
                    grup_konum_penceresi(filtre, test_tablosu_duzelt(pd.read_excel(veri_yolu(TEST_DOSYA))))

        # ── Paket 38a: özet kartları ──
        _son_t = df_filtre["Tarih_dt"].max() if "Tarih_dt" in df_filtre.columns else pd.NaT
        st.markdown(ozet_kartlari_html([("Sporcu", df_filtre["Sporcu"].nunique()), ("Test", df_filtre["Test"].nunique()),
                                        ("Son ölçüm", _son_t.strftime("%d.%m.%Y") if pd.notna(_son_t) else "—"),
                                        ("Kayıt", len(df_filtre))]), unsafe_allow_html=True)

        # ── Sekmeler (Paket 38a: Performans Trendi ilk/varsayılan) ──
        sekme2, sekme1, sekme3, sekme4, sekme5, sekme6, sekme7 = st.tabs([
            "Performans Trendi",
            "Veri Tablosu",
            "Sporcu Karşılaştırma",
            "Normatif Konum",
            "Performans Profili",
            "Z-Skor Profili",
            "Branşa Yönlendirme"
        ])

        # ══ SEKME 1: VERİ TABLOSU ══
        with sekme1:
            try:
                _tum_kolon = [k for k in df_filtre.columns if k != "Tarih_dt"]
                gorun_kolonlar = coklu_secim("Gösterilecek sütunlar", _tum_kolon, key="vt_sutunlar",
                                             default=None if "vt_sutunlar" in st.session_state else
                                             [k for k in _tum_kolon if k not in ("Kategori", "Batarya")]) or _tum_kolon
                st.dataframe(df_filtre[gorun_kolonlar], width="stretch")

                def excel_indir_hazirla(dataframe):
                    buffer = BytesIO()
                    cols = [k for k in dataframe.columns if k != "Tarih_dt"]
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        dataframe[cols].to_excel(writer, index=False, sheet_name="Sonuçlar")
                        worksheet = writer.sheets["Sonuçlar"]
                        for i, kolon in enumerate(cols, start=1):
                            uzunluklar = [len(str(d)) for d in dataframe[kolon].tolist()]
                            en_uzun = max(max(uzunluklar) if uzunluklar else 0, len(str(kolon)))
                            worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = en_uzun + 4
                    return buffer.getvalue()

                excel_verisi = excel_indir_hazirla(df_filtre)
                st.download_button(
                    label="⬇️ Excel (.xlsx) İndir",
                    data=excel_verisi,
                    file_name="sonuclar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 2: PERFORMANS TRENDİ ══
        with sekme2:
            try:
                st.subheader("Zaman İçinde Performans Değişimi")

                sayisal_kolonlar = []
                for k in df_filtre.columns:
                    if k not in META_KOLONLAR:
                        try:
                            sayisal = pd.to_numeric(df_filtre[k], errors="coerce")
                            if sayisal.notna().sum() > 0:
                                sayisal_kolonlar.append(k)
                        except Exception:
                            pass

                if not sayisal_kolonlar:
                    st.info("Trend grafiği için sayısal veri bulunamadı.")
                else:
                    t1, t2, t3 = st.columns(3)
                    with t1:
                        trend_sporcu = st.selectbox(
                            "Sporcu",
                            sorted(df_test["Sporcu"].unique().tolist()),
                            key="trend_sporcu", format_func=ad_bicimi
                        )
                    with t2:
                        trend_test = st.selectbox(
                            "Test",
                            sorted(df_test["Test"].unique().tolist()),
                            key="trend_test"
                        )
                    with t3:
                        trend_kolon = st.selectbox(
                            "Değişken",
                            sayisal_kolonlar,
                            key="trend_kolon"
                        )

                    df_trend = df_test[
                        (df_test["Sporcu"] == trend_sporcu) &
                        (df_test["Test"] == trend_test)
                    ].copy()
                    df_trend[trend_kolon] = pd.to_numeric(df_trend[trend_kolon], errors="coerce")
                    df_trend = df_trend.dropna(subset=["Tarih_dt", trend_kolon]).sort_values("Tarih_dt")

                    if df_trend.empty:
                        st.info("Bu sporcu ve test için yeterli veri yok.")
                    else:
                        import plotly.graph_objects as go
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_trend["Tarih_dt"],
                            y=df_trend[trend_kolon],
                            mode="lines+markers+text",
                            text=df_trend[trend_kolon].round(2).astype(str),
                            textposition="top center",
                            line=dict(color=grafik_renk("ana"), width=2),
                            marker=dict(size=10, color=grafik_renk("ana")),
                            name=trend_kolon
                        ))

                        # Trend çizgisi (2+ nokta varsa)
                        if len(df_trend) >= 2:
                            import numpy as np
                            x_num = np.arange(len(df_trend))
                            y_vals = df_trend[trend_kolon].values
                            try:
                                z = np.polyfit(x_num, y_vals, 1)
                                p = np.poly1d(z)
                                fig.add_trace(go.Scatter(
                                    x=df_trend["Tarih_dt"],
                                    y=p(x_num),
                                    mode="lines",
                                    line=dict(color=grafik_renk("ikincil"), width=1, dash="dash"),
                                    name="Trend"
                                ))
                            except Exception:
                                pass

                        fig.update_layout(
                            title=f"{trend_sporcu} — {trend_test} — {trend_kolon}",
                            xaxis_title="Tarih",
                            yaxis_title=trend_kolon,
                            hovermode="x unified",
                            **grafik_duzeni()
                        )
                        st.plotly_chart(fig, width="stretch")

                        # Özet istatistikler
                        col_a, col_b, col_c, col_d = st.columns(4)
                        col_a.metric("İlk Ölçüm", round(df_trend[trend_kolon].iloc[0], 2))
                        col_b.metric("Son Ölçüm", round(df_trend[trend_kolon].iloc[-1], 2))
                        degisim = round(df_trend[trend_kolon].iloc[-1] - df_trend[trend_kolon].iloc[0], 2)
                        col_c.metric("Değişim", degisim, delta=str(degisim))
                        col_d.metric("Ölçüm Sayısı", len(df_trend))
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 3: SPORCU KARŞILAŞTIRMA — Paket 38g: sayfanın üstündeki "Karşılaştırma" bölümüne taşındı ══
        with sekme3:
            try:
                st.subheader("Sporcular ve oturumlar arası karşılaştırma")
                st.markdown("Karşılaştırma artık bu sayfanın üstündeki **Karşılaştırma** bölümünde: iki sporcu grubu "
                            "(Sporcular arası) ya da önce / sonra oturumları (Oturumlar arası).")
                st.button("Karşılaştırmayı aç", key="kars_ac", icon=":material/compare_arrows:", type="primary",
                          on_click=_karsilastirmaya_git)
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 4: NORMATİF KONUM ══
        with sekme4:
            try:
                baslik_ac("Normatif Bantlar İçinde Konumlanma", ["Norm", "Düşük-iyi test"])
                bolum_terimleri(["Norm", "Düşük-iyi test"])

                norm_sporcular = sorted(df_test["Sporcu"].unique().tolist())
                n1, n2, n3 = st.columns(3)
                with n1:
                    norm_sporcu = st.selectbox("Sporcu", norm_sporcular, key="norm_sporcu", format_func=ad_bicimi)
                with n2:
                    norm_test = st.selectbox("Test", sorted(df_test["Test"].unique().tolist()), key="norm_test")

                df_norm_sporcu = df_test[(df_test["Sporcu"] == norm_sporcu) & (df_test["Test"] == norm_test)]

                # Sporcu profilinden cinsiyet ve branş al
                sporcu_bilgi = {}
                if os.path.exists(veri_yolu(SPORCU_DOSYA)):
                    df_sp = pd.read_excel(veri_yolu(SPORCU_DOSYA))
                    eslesme = df_sp[df_sp["Ad"] + " " + df_sp["Soyad"] == norm_sporcu]
                    if not eslesme.empty:
                        sporcu_bilgi = eslesme.iloc[0].to_dict()

                norm_cinsiyet = str(sporcu_bilgi.get("Cinsiyet", "Erkek"))
                norm_spor = str(sporcu_bilgi.get("Spor Dalı", "Genel/Yok"))

                norm_degiskenler = [k for k in NORMATIF.keys()]
                with n3:
                    norm_degisken = st.selectbox("Değişken", norm_degiskenler, key="norm_deg")

                # Son ölçümü al
                df_norm_filtre = df_norm_sporcu.copy()
                if norm_degisken in df_norm_filtre.columns:
                    df_norm_filtre[norm_degisken] = pd.to_numeric(df_norm_filtre[norm_degisken], errors="coerce")
                    df_norm_filtre = df_norm_filtre.dropna(subset=[norm_degisken])

                if df_norm_filtre.empty or norm_degisken not in df_norm_filtre.columns:
                    st.info("Bu test ve değişken için veri bulunamadı.")
                else:
                    son_deger = float(df_norm_filtre[norm_degisken].iloc[-1])
                    _yas_s = (pd.to_numeric(df_norm_filtre["Test Yaşı"], errors="coerce").iloc[-1]
                              if "Test Yaşı" in df_norm_filtre.columns else None)
                    if _yas_s is None or pd.isna(_yas_s):
                        _yas_s = sporcu_bilgi.get("Yaş")
                    norm_bilgi = normatif_degerlendir(norm_degisken, son_deger, norm_cinsiyet, norm_spor, norm_test, yas=_yas_s)

                    if norm_bilgi and norm_bilgi.get("tur") == "orneklem":     # Kademe 2 (Paket 35): bant yok
                        st.markdown(f"**{norm_sporcu} — {norm_degisken}: {_sayi_goster(son_deger)} {norm_bilgi['birim']}**")
                        for _n in orneklem_notlari(norm_bilgi, _yas_s):
                            st.caption(_n)
                        st.markdown(orneklem_tablosu(norm_bilgi))
                    elif norm_bilgi:
                        # Normatif bantları al
                        norm_data = NORMATIF[norm_degisken]
                        brans_norm = norm_data.get("branslar", {})
                        cinsiyet_normu = None
                        for brans_adi, brans_veri in brans_norm.items():
                            if brans_adi in norm_spor or norm_spor in brans_adi:
                                cinsiyet_normu = brans_veri.get(norm_cinsiyet)
                                break
                        if cinsiyet_normu is None:
                            cinsiyet_normu = norm_data.get(norm_cinsiyet) or norm_data.get("Erkek", {})

                        import plotly.graph_objects as go
                        bant_renkleri = {k: grafik_norm_renk(k) for k in ("Mükemmel", "İyi", "Orta", "Zayıf")}
                        fig3 = go.Figure()
                        dusuk_iyi = norm_bilgi.get("dusuk_iyi", False)
                        siralama = ["Zayıf", "Orta", "İyi", "Mükemmel"] if not dusuk_iyi else ["Mükemmel", "İyi", "Orta", "Zayıf"]

                        for kat in siralama:
                            if kat in cinsiyet_normu:
                                alt, ust = cinsiyet_normu[kat]
                                goster_ust = ust if ust < 99999 else son_deger * 1.3
                                goster_alt = alt if alt > -99999 else son_deger * 0.7
                                fig3.add_shape(
                                    type="rect",
                                    x0=0, x1=1,
                                    y0=goster_alt, y1=goster_ust,
                                    fillcolor=bant_renkleri.get(kat, grafik_renk("cizgi")),
                                    opacity=0.3,
                                    line_width=0,
                                    layer="below"
                                )
                                fig3.add_annotation(
                                    x=0.05, y=(goster_alt + goster_ust) / 2,
                                    text=kat, showarrow=False,
                                    font=dict(size=12, color=grafik_renk("murekkep")),
                                    xanchor="left"
                                )

                        # Sporcu değeri
                        fig3.add_shape(
                            type="line",
                            x0=0, x1=1, y0=son_deger, y1=son_deger,
                            line=dict(color=grafik_renk("murekkep"), width=3, dash="solid")
                        )
                        fig3.add_annotation(
                            x=0.95, y=son_deger,
                            text=f"  {son_deger}  ({norm_bilgi['kategori']})",
                            showarrow=False, font=dict(size=13, color=grafik_renk("murekkep")),
                            xanchor="left"
                        )
                        fig3.update_layout(
                            title=f"{norm_sporcu} — {norm_degisken}",
                            xaxis=dict(showticklabels=False, showgrid=False),
                            yaxis_title=norm_degisken,
                            **grafik_duzeni(),
                            height=350
                        )
                        st.plotly_chart(fig3, width="stretch")
                        st.caption(f"Kaynak: {norm_bilgi['kaynak']}")
                    elif NORMATIF[norm_degisken].get("tur") == "orneklem":
                        st.info(orneklem_disi_metni(norm_degisken))
                    else:
                        st.info("Bu değişken için normatif bant tanımlanmamış.")
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 5: PERFORMANS PROFİLİ (RADAR, Z tabanlı) ══
        with sekme5:
            try:
                baslik_ac("Çok Boyutlu Performans Profili",
                          ["Z skoru", "Sınır değer (P5 altı / P95 üstü)", "Düşük-iyi test", "Branş grubu katmanı"])
                bolum_terimleri(["Z skoru", "Performans persentili", "Sınır değer (P5 altı / P95 üstü)", "Düşük-iyi test",
                                 "Branş grubu katmanı"])
                st.caption(
                    "Her eksen bir test: sporcunun en son ölçümünün yaş/cinsiyet normuna göre Z skoru "
                    "(persentil sırasından). Farklı birimler (adım, saniye, cm) Z ile ortak eksene taşınır. "
                    "Kalın halka Z = 0, yani akran ortalaması; dışarısı akranlarından iyi, içerisi zayıf. "
                    "Yalnızca yaş bazlı persentil normu olan performans testleri gösterilir."
                )

                radar_sporcu = st.selectbox(
                    "Sporcu",
                    sorted(df_test["Sporcu"].unique().tolist()),
                    key="radar_sporcu", format_func=ad_bicimi
                )
                radar_profil = sporcu_z_profili(df_test, radar_sporcu)
                radar_satirlar = [r for r in radar_profil["satirlar"] if r["Tür"] == "Performans"]

                # ── İkinci katman: branş grubu profili, aynı norm tablolarından Z'ye çevrilmiş (Paket 7) ──
                radar_gruplar = coklu_secim(
                    "Branş grubu katmanı (Opstoel ve ark., 2015; en fazla 3 grup)",
                    list(BRANS_GRUBU_PROFILLERI["gruplar"].keys()), max_selections=3, key=f"radar_grup_{radar_sporcu}",
                    help="Grup ortalaması, sporcunun Z'sinin geldiği norm hücresinden (aynı test, yaş, cinsiyet) "
                         "geçirilerek Z'ye çevrilir. Çevrilemeyen değişken radarda gösterilmez.")
                radar_katman = grup_radar_katmani(df_test, radar_sporcu, radar_gruplar) if radar_gruplar else None
                if radar_katman and not radar_katman["uygun"]:
                    st.info("Grup katmanı çizilemedi: " + (radar_katman["neden"] or ""))
                    radar_katman = None
                if radar_katman:
                    # Katman açıkken eksenler, hem sporcuda hem grupta Z'si olan Opstoel değişkenleridir.
                    radar_satirlar = [{"Test": e["ad"], "Değişken": BRANS_GRUBU_PROFILLERI["degiskenler"][e["kod"]]["birim"],
                                       "Z": e["z"], "Değer": e["deger"], "Performans persentili": e["persentil"]}
                                      for e in radar_katman["eksenler"]]

                if radar_profil["hata"]:
                    st.warning(radar_profil["hata"])
                elif len(radar_satirlar) < 3:
                    st.info("Radar için yaş bazlı normu olan en az 3 performans testi gerekli "
                            f"(şu an {len(radar_satirlar)}). Ayrıntı için Z-Skor Profili sekmesine bakın.")
                else:
                    import plotly.graph_objects as go
                    RADAR_ARALIK = (-3, 3)
                    def _sar(metin, genislik=24):
                        """Etiketi kelime sınırından satırlara böler (kelime ortasından kesmez)."""
                        satirlar_e, satir_e = [], ""
                        for kelime in metin.split():
                            if satir_e and len(satir_e) + 1 + len(kelime) > genislik:
                                satirlar_e.append(satir_e)
                                satir_e = kelime
                            else:
                                satir_e = f"{satir_e} {kelime}".strip()
                        if satir_e:
                            satirlar_e.append(satir_e)
                        return "<br>".join(satirlar_e)

                    # Test adındaki parantezli İngilizce karşılık eksende gösterilmez (tabloda tam ad var)
                    eksenler = [_sar(r["Test"].split(" (")[0]) + "<br><i>" + _sar(r["Değişken"]) + "</i>"
                                for r in radar_satirlar]
                    z_degerleri = [max(RADAR_ARALIK[0], min(RADAR_ARALIK[1], r["Z"])) for r in radar_satirlar]

                    fig4 = go.Figure()
                    # Akran ortalaması halkası (Z = 0)
                    fig4.add_trace(go.Scatterpolar(
                        r=[0] * (len(eksenler) + 1),
                        theta=eksenler + [eksenler[0]],
                        mode="lines",
                        line=dict(color=grafik_renk("ikincil"), width=3),
                        name="Akran ortalaması (Z = 0)",
                        hoverinfo="skip",
                    ))
                    # Paket 35d: sporcunun alanı ayrı dolgu izi — renk tema yuvasından (6 haneli), saydamlık iz opacity'si
                    fig4.add_trace(go.Scatterpolar(
                        r=z_degerleri + [z_degerleri[0]],
                        theta=eksenler + [eksenler[0]],
                        fill="toself", fillcolor=grafik_renk("ana"), opacity=0.15, mode="none",
                        showlegend=False, hoverinfo="skip",
                    ))
                    fig4.add_trace(go.Scatterpolar(
                        r=z_degerleri + [z_degerleri[0]],
                        theta=eksenler + [eksenler[0]],
                        mode="lines+markers",
                        line=dict(color=grafik_renk("ana"), width=2),
                        marker=dict(size=7, color=grafik_renk("ana")),
                        name=radar_sporcu,
                        customdata=[[r["Değer"], r["Performans persentili"]] for r in radar_satirlar] +
                                   [[radar_satirlar[0]["Değer"], radar_satirlar[0]["Performans persentili"]]],
                        hovertemplate="%{theta}<br>Z = %{r:+.2f}<br>Değer: %{customdata[0]}"
                                      "<br>Persentil ≈ P%{customdata[1]:.0f}<extra></extra>",
                    ))
                    if radar_katman:
                        for g_i, g_ad in enumerate(radar_gruplar):
                            gz = [max(RADAR_ARALIK[0], min(RADAR_ARALIK[1], e["gruplar"][g_ad]["z"]))
                                  for e in radar_katman["eksenler"]]
                            g_cd = [[e["gruplar"][g_ad]["ort"], e["gruplar"][g_ad]["persentil"]]
                                    for e in radar_katman["eksenler"]]
                            fig4.add_trace(go.Scatterpolar(
                                r=gz + [gz[0]], theta=eksenler + [eksenler[0]], mode="lines",
                                line=dict(color=grafik_renk(f"seri{g_i % 3}"), width=2, dash="dash"),
                                name=f"{g_ad} (grup ortalaması)", customdata=g_cd + [g_cd[0]],
                                hovertemplate="%{theta}<br>Grup Z = %{r:+.2f}<br>Grup ortalaması: %{customdata[0]}"
                                              "<br>Persentil ≈ P%{customdata[1]:.0f}<extra></extra>",
                            ))
                    fig4.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True, range=list(RADAR_ARALIK),
                                tickvals=[-3, -2, -1, 0, 1, 2, 3],
                                ticktext=["−3", "−2", "−1", "0 (akran ort.)", "+1", "+2", "+3"],
                                tickfont=dict(size=10, color=grafik_renk("ikincil")),
                                gridcolor=grafik_renk("cizgi")
                            ),
                            angularaxis=dict(
                                tickfont=dict(size=10, color=grafik_renk("murekkep")),
                                gridcolor=grafik_renk("cizgi")
                            )
                        ),
                        **grafik_duzeni(),
                        title=f"{radar_sporcu} — Performans Profili (Z, −3 / +3)",
                        showlegend=True,
                        legend=dict(orientation="h", y=-0.12),
                        height=560
                    )
                    st.plotly_chart(fig4, width="stretch")
                    st.caption("Not: P5–P95 bantlı normlarda Z en fazla ±1.64'tür (bant dışı değerler sınırda "
                               "tutulur); P20–P80 bantlı normlarda ±0.84. Bu yüzden ±3'e yaklaşan değer görülmez. "
                               "Değerler ve persentiller Z-Skor Profili sekmesindedir.")
                    if radar_katman:
                        st.caption("🔀 Grup katmanı açık: eksenler hem sporcuda hem grupta Z'si olan değişkenlerdir; "
                                   "sporcunun değeri o testin en iyi denemesidir. " + GRUP_KATMANI_NOTU)
                        st.caption("Radardan çıkarılan değişkenler: "
                                   + "; ".join(f"{a} ({n})" for a, n in radar_katman["cikarilan"])
                                   + "; boy, kilo, VKİ, oturma yüksekliği (antropometrik).")
                        st.dataframe(pd.DataFrame([
                            {"Değişken": e["ad"], "Sporcu": e["deger"], "Sporcu Z": e["z"],
                             **{f"{g} ort.": e["gruplar"][g]["ort"] for g in radar_gruplar},
                             **{f"{g} Z": e["gruplar"][g]["z"] for g in radar_gruplar},
                             "Norm hücresi": f"{e['kullanilan_yas']} yaş {radar_katman['cinsiyet'].lower()}"}
                            for e in radar_katman["eksenler"]]), width="stretch", hide_index=True)
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 6: Z-SKOR PROFİLİ (persentil tabanlı) ══
        with sekme6:
            try:
                baslik_ac("Z-Skor Profili", ["Z skoru", "Performans persentili"])
                bolum_terimleri(["Z skoru", "Performans persentili", "Sınır değer (P5 altı / P95 üstü)",
                                 "Taban / tavan etkisi", "Nötr (tanımlayıcı) ölçüm", "Doğum çeyreği",
                                 "Ortalama Z", "MQ", "PQ"])
                st.caption(
                    "Her testin en son ölçümü, sporcunun yaşına ve cinsiyetine göre persentil sırasına "
                    "çevrilir; Z = ters normal(persentil). Ham skordan ortalama/SD ile Z alınmaz, çünkü "
                    "normlar persentil olarak verilir ve çoğu dağılım çarpıktır. Yalnızca yaş bazlı "
                    "persentil normu olan testler listelenir. + = akranlarından iyi."
                )

                z_sporcu = st.selectbox("Sporcu", sorted(df_test["Sporcu"].unique().tolist()), key="z_sporcu", format_func=ad_bicimi)

                z_profil = sporcu_z_profili(df_test, z_sporcu)
                if z_profil["hata"]:
                    st.warning(z_profil["hata"])
                else:
                    satirlar = z_profil["satirlar"]
                    z_sozlugu = z_profil["z_sozlugu"]
                    eski_yas_kullanildi = z_profil["eski_yas"]
                    if not satirlar:
                        st.info("Bu sporcunun yaş bazlı persentil normu olan bir test kaydı yok.")
                    else:
                        df_zt = pd.DataFrame(satirlar)
                        sirali_z = sorted(satirlar, key=lambda r: (r["Tür"] != "Performans", r["Test"], r["Değişken"]))
                        st.markdown(kart_izgarasi_html(
                            [z_satiri_karti(r, z_sozlugu.get((r["Test"], r["Değişken"]), {})) for r in sirali_z]),
                            unsafe_allow_html=True)
                        with st.expander("Tablo görünümü (Z ve not sütunlarıyla)", icon=":material/table_rows:"):
                            st.dataframe(df_zt, width="stretch", hide_index=True,
                                         column_config=sutun_yardimi({"Performans persentili": "Performans persentili", "Z": "Z skoru"}))
                        if eski_yas_kullanildi:
                            st.caption("ℹ️ Bazı eski kayıtlarda test günündeki yaş kaydedilmemiş; bu kayıtlarda "
                                       "profildeki güncel yaş kullanıldı. Yeni kayıtlar test günündeki yaşı saklar.")

                        df_perf = df_zt[df_zt["Tür"] == "Performans"]
                        if not df_perf.empty:
                            import plotly.graph_objects as go
                            etiketler = [f"{t[:32]} — {d[:22]}" for t, d in zip(df_perf["Test"], df_perf["Değişken"])]
                            fig_z = go.Figure(go.Bar(
                                x=df_perf["Z"], y=etiketler, orientation="h",
                                marker_color=grafik_renk("ana"),
                                text=[f"{z:+.2f}" for z in df_perf["Z"]], textposition="outside",
                                hovertemplate="%{y}<br>Z = %{x:+.2f}<extra></extra>",
                            ))
                            for x_ref, stil in ((0, "solid"), (-1, "dot"), (1, "dot")):
                                fig_z.add_vline(x=x_ref, line_dash=stil, line_color=grafik_renk("ikincil"), line_width=1)
                            fig_z.update_layout(
                                xaxis=dict(range=[-2.2, 2.2], title="Z (performans yönlü)", zeroline=False),
                                yaxis=dict(autorange="reversed"),
                                height=max(260, 46 * len(df_perf) + 80),
                                margin=dict(l=10, r=40, t=30, b=40),
                                **grafik_duzeni(),
                                showlegend=False,
                            )
                            st.plotly_chart(fig_z, width="stretch")
                            st.caption("Noktalı çizgiler ±1 Z (≈ P16 ve P84). P5–P95 bantlı normlarda Z en fazla "
                                       "±1.64'tür; bant dışı değerler sınırda tutulur.")

                        # ── Bileşik skorlar ──
                        for ad_b, tanim_b in BILESIK_Z.items():
                            bz = bilesik_z_hesapla(ad_b, z_sozlugu)
                            baslik_ac(ad_b, ["Ortalama Z", "MQ", "PQ", "Taban / tavan etkisi"], "####")
                            if bz["deger"] is None:
                                eksik_ad = ", ".join(bz["eksik"])
                                st.info(f"Hesaplanmadı — eksik test: {eksik_ad}")
                            else:
                                etiket_b = ad_b if not bz["dislanan"] else f"{ad_b} ({bz['bilesen_sayisi']} test)"
                                st.metric(etiket_b, f"{bz['deger']:+.2f}", help=ACIKLAMALAR["Ortalama Z"])
                                for not_b in bz["notlar"]:
                                    st.info(f"ℹ️ {not_b} Testin kendi Z'si tabloda ve radarda gösterilmeye devam eder.")
                                if bz["tarih_farki_gun"] is not None and bz["tarih_farki_gun"] > BILESIK_MAKS_GUN:
                                    st.warning(f"Bileşen ölçümleri arasında {bz['tarih_farki_gun']} gün var "
                                               f"(önerilen en fazla {BILESIK_MAKS_GUN}). Bileşik skor farklı "
                                               f"dönemlerin karışımı olabilir.")
                            st.caption(tanim_b["aciklama"] + " Ortalama Z bir persentile çevrilmez: bileşenler "
                                       "arasındaki korelasyon bilinmediği için ortalamanın dağılımı bilinmiyor.")
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)

        # ══ SEKME 7: BRANŞA YÖNLENDİRME (Paket 5) ══
        with sekme7:
            try:
                baslik_ac("Branşa Yönlendirme", ["Güven düzeyi", "Ortalama standart uzaklık"])
                bolum_terimleri(["Güven düzeyi", "Ortalama standart uzaklık", "Havuzlanmış standart sapma",
                                 "Nötr (tanımlayıcı) ölçüm", "PQ", "MQ"])
                st.caption(
                    "İki bilgi ayrı ayrı gösterilir: çocuğun ilgisi (anket) ve fiziksel profili (Flaman Spor "
                    "Pusulası çalışmasındaki altı branş grubunun profilleriyle karşılaştırma; Opstoel ve ark., 2015; "
                    "9-11 yaş). Tek bir puanda birleştirilmez. Çıktı bir yönlendirmedir, karar değildir."
                )
                y1, y2 = st.columns(2)
                with y1:
                    yon_sporcu = st.selectbox("Sporcu", sorted(df_test["Sporcu"].unique().tolist()), key="yon_sporcu", format_func=ad_bicimi)
                yon_bilgi = sporcu_profil_bilgisi(yon_sporcu)
                kayitli_hacim, kayitli_hacim_tarih = sporcu_antrenman(yon_bilgi)
                with y2:
                    yon_hacim = st.selectbox(
                        "Haftalık organize antrenman süresi",
                        ANTRENMAN_SECENEKLERI,
                        index=ANTRENMAN_SECENEKLERI.index(kayitli_hacim),
                        key=f"yon_hacim_{yon_sporcu}",
                        help=ANTRENMAN_YARDIM + " Sporcu profilinde saklanır.",
                    )
                    if yon_hacim != kayitli_hacim:
                        if st.button("💾 Profile kaydet", key=f"hacim_kaydet_{yon_sporcu}"):
                            if sporcu_antrenman_kaydet(yon_sporcu, yon_hacim):
                                st.success("Antrenman süresi profile kaydedildi.")
                                st.rerun()
                            else:
                                st.error("Sporcu profili bulunamadı; kaydedilemedi.")
                        st.caption("⚠️ Bu seçim henüz kaydedilmedi; raporlar profildeki değeri kullanır.")
                    elif kayitli_hacim_tarih:
                        st.caption(f"Profilde kayıtlı ({kayitli_hacim_tarih}).")
                    elif kayitli_hacim == "Bilinmiyor":
                        st.caption("Profilde kayıtlı değil.")

                fsc = sporcu_fsc_profili(df_test, yon_sporcu)
                esl = brans_grubu_eslestir(fsc, yon_bilgi.get("Yaş"))
                tanimlar = BRANS_GRUBU_PROFILLERI["degiskenler"]

                # ══ İLGİ ANKETİ (Paket 6) — form Sporcu Girişi sayfasında (Paket 7) ══
                ilgi_kayit = ilgi_son_anket(yon_sporcu)
                with st.expander("ℹ️ Bu anket hakkında"):
                    st.markdown(ILGI_HAKKINDA)
                if not ilgi_kayit:
                    st.caption("İlgi anketi Sporcu Girişi sayfasından doldurulur (testlerden bağımsız).")
                ilgi_puan = ilgi_grup_puanlari(ilgi_kayit) if ilgi_kayit else {}

                # ══ İKİ AYRI PENCERE (sabit karar 4: tek skorda birleştirilmez) ══
                st.markdown("##### İlgi ve fiziksel profil")
                st.caption("İki bilgi ayrı ayrı gösterilir ve tek bir puana çevrilmez. İkisinin örtüştüğü gruplar en "
                           "güçlü işarettir; ayrıştıkları yer de çocuk hakkında bilgi verir.")
                if not ilgi_kayit:
                    st.info("İlgi anketi henüz doldurulmadı. Aşağıdaki fiziksel profil tek başına bir öneri değildir; "
                            "yalnızca bilgilendiricidir.")
                pen = ilgi_fiziksel_pencereler(esl, ilgi_puan) if ilgi_kayit else None
                p1, p2 = st.columns(2)
                with p1:
                    st.markdown("**💛 Bunları seviyor** (ilgi anketi)")
                    if not ilgi_kayit:
                        st.caption("Anket yok.")
                    elif pen["seviyor"]:
                        for g in pen["seviyor"]:
                            isaret = " ★" if g in pen["kesisim"] else ""
                            st.markdown(f"- **{g}**{isaret} — {ilgi_etiketi(ilgi_puan[g]).lower()}")
                    else:
                        st.caption("Belirgin bir tercih çıkmadı (hiçbir grupta ortalama \"seviyorum\" düzeyine ulaşmadı).")
                with p2:
                    st.markdown("**🏃 Fiziksel profili bu gruplara yakın** (eşleştirme)")
                    if esl["uygun"] and esl.get("ayirt_edilemez"):        # Paket 38p: grup adı yok
                        st.markdown(VELI_FIZIKSEL_AYIRT_EDILEMEZ)
                    elif esl["uygun"]:
                        for g in pen["fiziksel"] if pen else fiziksel_pencere(esl):
                            isaret = " ★" if pen and g in pen["kesisim"] else ""
                            st.markdown(f"- **{g}**{isaret}")
                        st.caption("Sırasız; bilgilendiricidir, eleyici değildir.")
                    else:
                        st.caption(esl["neden"] or "Fiziksel karşılaştırma yapılamadı.")

                if pen:
                    if pen["kesisim"]:
                        st.success("★ **Hem seviyor hem fiziksel profili yakın:** " + ", ".join(pen["kesisim"])
                                   + ". Bu, en güçlü işarettir; bu grupların sporlarını denemek iyi bir başlangıçtır.")
                    if esl["uygun"] and esl.get("ayirt_edilemez"):        # Paket 38p: veli raporuyla aynı dil
                        st.info(VELI_OZET_AYIRT_EDILEMEZ_SEVIYOR.format(grup=", ".join(pen["seviyor"]))
                                if pen["seviyor"] else VELI_OZET_AYIRT_EDILEMEZ)
                    elif pen["yalniz_ilgi"] and esl["uygun"]:
                        st.info("**Ayrışma:** " + ", ".join(pen["yalniz_ilgi"]) + " grubunu seviyor; fiziksel profili ise "
                                + (", ".join(pen["yalniz_fiziksel"]) + " gruplarına" if pen["yalniz_fiziksel"] else "başka gruplara") + " daha yakın. İkisi de bilgidir: "
                                "sevdiği spor uzun süre devam etmesini kolaylaştırabilir; fiziksel profil ise yalnızca "
                                "bugünkü fiziksel özelliklerini gösterir ve antrenmanla değişir. Fiziksel profil, sevdiği "
                                "sporu yapmasına engel değildir.")
                    elif pen["yalniz_fiziksel"] and not pen["seviyor"] and esl["uygun"]:
                        st.info("Fiziksel profili " + ", ".join(pen["yalniz_fiziksel"]) + " gruplarına yakın, ama ankette "
                                "belirgin bir ilgi çıkmadı. Bu sporları birkaç kez denemesi, ilgisini görmek için iyi bir yoldur.")
                    elif pen["yalniz_fiziksel"] and esl["uygun"]:
                        durum = [f"{g} ({'ilgisi bilinmiyor' if ilgi_puan.get(g) is None else ilgi_etiketi(ilgi_puan[g]).lower()})"
                                 for g in pen["yalniz_fiziksel"]]
                        st.info("**Ayrışma:** fiziksel profili " + ", ".join(durum) + " grubuna da yakın, ama ankette bu "
                                "grubu \"seviyorum\" düzeyinde işaretlemedi. Bu yalnızca bilgidir; çocuğun istemediği bir "
                                "spora yönlendirme gerekçesi değildir.")
                    if pen["bilinmeyen"]:
                        st.caption("İlgisi bilinmeyen gruplar (yeterli madde yanıtlanmadı ya da \"hiç yapmadım\"): "
                                   + ", ".join(pen["bilinmeyen"]) + ". Bu sporları denemek, ilgisini öğrenmenin en iyi yoludur.")
                    ozet = [{"Grup": g, "İlgi (anket)": ilgi_etiketi(ilgi_puan.get(g)),
                             "İlgi ortalaması (1-5)": ilgi_puan.get(g),
                             "Fiziksel profil yakın üçte": ("Ayırt edilemiyor" if pen["fiziksel_ayirt_edilemez"] else
                                                            "Evet" if g in pen["fiziksel"] else
                                                            ("—" if esl["uygun"] else "Bilgi yok"))}
                            for g in BRANS_GRUBU_PROFILLERI["gruplar"]]
                    st.dataframe(pd.DataFrame(ozet), width="stretch", hide_index=True)
                    tercihler = [ilgi_kayit.get(k) for k, a, b in ILGI_TERCIHLERI
                                 if ilgi_kayit.get(k) and ilgi_kayit.get(k) != "İkisi de / fark etmez"]
                    if tercihler:
                        st.caption("Tercihleri: " + " · ".join(str(t) for t in tercihler))
                    st.caption(f"Anket: {ILGI_ANKET_ADI} ({ilgi_kayit.get('Tarih', '')}). {ILGI_UYARI}")

                st.markdown("---")
                st.markdown("##### Fiziksel profil (bilgilendirici, eleyici değil)")
                st.caption("Fiziksel profilin bir gruba uzak görünmesi, çocuğun o sporu yapamayacağı anlamına gelmez. "
                           "9-11 yaşta performans antrenmanla hızla değişir ve branş grupları fiziksel olarak "
                           "birbirine çok yakındır.")

                # ── Güven düzeyi: her zaman gösterilir (sabit karar 3) ──
                baslik_ac("Fiziksel profilin güven düzeyi", ["Güven düzeyi"], "######")
                if yon_hacim == "Bilinmiyor":
                    st.warning("Antrenman süresi seçilmedi. Opstoel ve ark. (2015) sonuçlarına göre profil, branşı "
                               "yalnızca haftada 5 saat ve üzeri antrenman yapan çocuklarda güvenilir biçimde "
                               "ayırt etti (%85.2); 1-5 saatte %48.8, 1 saat ve altında %48.4 — tesadüf düzeyine yakın.")
                else:
                    g_d = GUVEN_DUZEYLERI[yon_hacim]
                    (st.success if g_d["anlamli"] else st.warning)(g_d["metin"])
                st.caption("Bu oranlar Opstoel'in kendi diskriminant modeline aittir. Buradaki uzaklık yöntemi daha "
                           "basittir (model katsayıları yayımlanmadı) ve doğruluğu ayrıca test edilmedi.")

                if not esl["uygun"]:
                    st.info(esl["neden"])
                elif esl.get("ayirt_edilemez"):                        # Paket 38p
                    st.info(ANTRENOR_YAYILIM_SATIRI.format(x=f"{esl['yayilim']:.2f}".replace(".", ","),
                                                           esik=f"{ESLESTIRME_AYIRT_ESIGI:.2f}".replace(".", ","))
                            + " " + ANTRENOR_AYIRT_EDILEMEZ)
                    st.caption(ANTRENOR_YAYILIM_YONTEMI)
                    st.markdown(yayilim_simulasyon_tablosu(), unsafe_allow_html=True)
                else:
                    sira = esl["siralama"]
                    ilk_uc = fiziksel_pencere(esl)   # bilinçli olarak sırasız (alfabetik); 38p: + eşit uzaklıktakiler
                    baslik_ac("Fiziksel profilin biraz daha yakın olduğu gruplar",
                              ["Ortalama standart uzaklık", "Havuzlanmış standart sapma"], "######")
                    st.markdown(
                        " · ".join(f"**{g}**" for g in ilk_uc) + "  \n"
                        "Bu üç grup **sırasız** gösterilir: aralarında bir öncelik yoktur. Profil bu gruplara diğer "
                        "üçünden biraz daha yakındır; bu tek başına bir öneri ya da eleme değildir. Bu yaşta birden "
                        "fazla sporu denemek önerilir."
                    )
                    sim = ESLESTIRME_SIMULASYON
                    st.caption(
                        "Neden sıra yok: grupların ortalama profilleri birbirine çok yakın (grup merkezleri arası "
                        "0.11-0.20 standart birim). Bir çocuk bir grubun tam ortalamasında olsa bile ikinci grup ancak "
                        f"bu kadar geride kalır. Simülasyonda gerçek grup %{sim['ilk_uc']} oranında bu üç içinde çıktı "
                        f"(şans %{sim['sans_ilk_uc']}); ilk sırada çıkma oranı yalnızca %{sim['ilk_sira']} "
                        f"(şans %{sim['sans_ilk']})."
                    )

                    # ── Değişken tablosu (sporcu ve altı grubun ortalaması, sabit sıra) ──
                    gruplar_sabit = list(BRANS_GRUBU_PROFILLERI["degerler"].keys())
                    satirlar_y = []
                    for kod in esl["kullanilan"]:
                        t = tanimlar[kod]
                        satir_y = {"Değişken": t["ad"], "Birim": t["birim"],
                                   "Yön": "düşük iyi" if t["dusuk_iyi"] else "yüksek iyi",
                                   "Sporcu": fsc["degerler"][kod]["deger"]}
                        for grup in gruplar_sabit:
                            satir_y[grup] = BRANS_GRUBU_PROFILLERI["degerler"][grup][kod][0]
                        satirlar_y.append(satir_y)
                    st.dataframe(pd.DataFrame(satirlar_y), width="stretch", hide_index=True)
                    st.caption(f"{len(esl['kullanilan'])} performans değişkeni kullanıldı. Grup sütunları grup "
                               "ortalamalarıdır (Opstoel ve ark., 2015).")

                    with st.expander("Teknik ayrıntı: uzaklık değerleri (antrenör için — veliye gösterilmemeli)"):
                        st.warning("Bu sayıların arasındaki farklar YORUMLANMAMALIDIR. Gruplar birbirine 0.11-0.20 "
                                   "standart birim uzaklıkta olduğundan, 0.1-0.2'lik farklar ölçüm hatası ve "
                                   "günlük değişkenlik içinde kalır; sıralama bir kesinlik göstermez.")
                        st.dataframe(pd.DataFrame([{"Grup": g, "Ortalama standart uzaklık": u} for g, u in sira]),
                                     width="stretch", hide_index=True,
                                     column_config=sutun_yardimi({"Ortalama standart uzaklık": "Ortalama standart uzaklık"}))

                # ── Eksikler ve sınırlar ──
                eksik_ad = [tanimlar[k]["ad"] for k in fsc["eksik"] if k in ESLESTIRME_DEGISKENLERI]
                if eksik_ad:
                    st.caption("Kaydı olmayan testler: " + ", ".join(eksik_ad) + ".")
                if esl["dislanan_yas"]:
                    st.caption("9-11 yaş dışında yapıldığı için kullanılmayan ölçümler: "
                               + ", ".join(tanimlar[k]["ad"] for k in esl["dislanan_yas"]) + ".")
                st.caption("Eşleştirmeye girmeyenler: "
                           + ", ".join(f"{tanimlar[k]['ad']} (protokol eşleşmedi)" for k in fsc["eslesmeyen"])
                           + "; boy, kilo, VKİ ve oturma yüksekliği (antropometrik — tanımlayıcı veri).")
                st.info("ℹ️ Grup ortalamaları erkek ve kızların karışımıdır; grupların cinsiyet dağılımı "
                        "yayımlanmadığı için cinsiyet düzeltilemedi. Örneğin kızlar otur-uzanda genellikle daha "
                        "yüksek skor alır; bu, bir kızın profilini dans veya jimnastiğe yaklaştırabilir.")

                antrop = [(tanimlar[k]["ad"], fsc["degerler"][k]["deger"], tanimlar[k]["birim"])
                          for k in tanimlar if tanimlar[k]["tur"] == "antropometri" and k in fsc["degerler"]]
                if antrop:
                    with st.expander("Antropometrik bilgiler (eşleştirmeye girmez)"):
                        for ad_a, v_a, b_a in antrop:
                            st.caption(f"{ad_a}: {v_a} {b_a}")

                with st.expander("Yöntem ve kaynak"):
                    st.markdown(
                        "Her performans değişkeninde (sporcu − grup ortalaması) / havuzlanmış grup içi SD hesaplanır "
                        "(altı grubun ortak SD'si; her grubun kendi SD'si kullanılsaydı SD'si büyük gruplar "
                        "sistematik olarak yakın görünürdü). Her grup için bu farkların karelerinin ortalamasının "
                        "karekökü alınır; en küçük uzaklık, profilin en çok benzediği gruptur.\n\n"
                        f"Simülasyon (6 × 3000 sanal çocuk, değişkenler bağımsız ve normal varsayıldı): gerçek grup "
                        f"%{ESLESTIRME_SIMULASYON['ilk_sira']} ilk sırada, %{ESLESTIRME_SIMULASYON['ilk_uc']} ilk üçte.\n\n"
                        f"Kaynak: {BRANS_GRUBU_PROFILLERI['kaynak']}\n\n"
                        f"Örneklem: {BRANS_GRUBU_PROFILLERI['orneklem']}."
                    )
            except Exception as _sekme_h:          # Paket 38a: bir sekmenin hatası öbürlerini durdurmaz
                sekme_hatasi(_sekme_h)
