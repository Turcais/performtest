"""
Sporcu Girişi sayfası: sporcu ekleme/düzenleme, ilgi anketi.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import os
import pandas as pd
import streamlit as st
from datetime import date
from olcut.analiz import (
    ANTRENMAN_KOLON, ANTRENMAN_SECENEKLERI, ANTRENMAN_TARIH_KOLON, ANTRENMAN_YARDIM, sporcu_antrenman)
from olcut.bilesenler import baslik_ac, bolum_terimleri, ilgi_anketi_formu
from olcut.kayit import GRUP_KOLON, _sporcu_formunu_temizle, profil_uyarilari, sporcu_form_hatalari
from olcut.norm import SPORCU_DOSYA
from olcut.ortak import DOGUM_KOLON, ad_bicimi, dogum_ceyregi, tam_yas, tarih_coz


# ── SAYFA 1: SPORCU GİRİŞİ ──
def sporcu_girisi_sayfasi():
    """Sporcu Girişi sayfası (Bölme Aşama 2: satır içi dal fonksiyona sarıldı)."""
    st.header("Sporcu Bilgisi Giriş")
    bolum_terimleri(["Doğum çeyreği", "Güven düzeyi", "VKİ"])

    # Paket 38a: form boş açılır; doğum tarihi biliniyorsa yaş ondan hesaplanır (salt okunur)
    _dogum_bilinen = st.session_state.get("sg_dogum") if st.session_state.get("sg_dogum_var") else None
    _yas_dogumdan = tam_yas(_dogum_bilinen, date.today()) if _dogum_bilinen else None
    if _yas_dogumdan is not None:
        st.session_state["sg_yas"] = _yas_dogumdan
    col1, col2 = st.columns(2)
    with col1:
        ad = st.text_input("Sporcu Adı", key="sg_ad")
        yas = st.number_input("Yaş", min_value=0, max_value=60, step=1, placeholder="ör. 12", key="sg_yas",
                              disabled=_yas_dogumdan is not None,
                              help="Doğum tarihi girilirse yaş otomatik hesaplanır.",
                              **({} if "sg_yas" in st.session_state else {"value": None}))
        spor_dali = st.selectbox("Spor Dalı", [
            "Genel/Yok",
            # Dövüş Sporları
            "Güreş (Serbest)", "Güreş (Grekoromen)", "Judo", "Karate", "Taekwondo",
            "Kickboks", "Muay Thai", "Boks", "Jiujitsu (BJJ)", "Sambo", "MMA",
            # Takım Sporları
            "Futbol", "Basketbol", "Voleybol", "Hentbol", "Rugbi", "Amerikan Futbolu",
            "Buz Hokeyi", "Su Topu", "Beyzbol", "Amerikan Futbolu",
            # Bireysel Sporlar
            "Atletizm (Sprint)", "Atletizm (Orta Mesafe)", "Atletizm (Uzun Mesafe)",
            "Atletizm (Atlama)", "Atletizm (Atma)", "Yüzme", "Bisiklet", "Triatlon",
            "Kürek", "Kano/Kayak", "Halter", "Jimnastik", "Tenis", "Masa Tenisi",
            "Badminton", "Squash", "Golf", "Okçuluk", "Eskrim", "Biatlon",
            "Kayak (Alp)", "Kayak (Nordik)", "Paten", "Boks",
            "Diğer"
        ])
        boy = st.number_input("Boy (cm)", min_value=0, max_value=250, step=1, placeholder="ör. 150", key="sg_boy",
                              **({} if "sg_boy" in st.session_state else {"value": None}))
    with col2:
        soyad = st.text_input("Sporcu Soyadı", key="sg_soyad")
        cinsiyet = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
        derece = st.selectbox("Spor Derecesi", ["Okul Öncesi/Öğrenci", "Rekreasyonel", "Amatör", "Yarı Profesyonel", "Profesyonel", "Milli Sporcu"])
        kilo = st.number_input("Kilo (kg)", min_value=0.0, max_value=200.0, step=0.1, placeholder="ör. 42,5",
                               key="sg_kilo", **({} if "sg_kilo" in st.session_state else {"value": None}))
    grup = st.text_input("Grup / Sınıf", placeholder="ör. 5-A, U14 güreş", key="sg_grup",
                         help="Serbest metin. Test Oturumu'nda sporcular bu gruba göre seçilir.")
    antrenman = st.selectbox("Haftalık organize antrenman süresi", ANTRENMAN_SECENEKLERI,
                             help=ANTRENMAN_YARDIM)
    dogum_var = st.checkbox("Doğum tarihi biliniyor", key="sg_dogum_var",
                            help="Yaşın yanına kaydedilir. Doğum çeyreği ve TSYT norm hücresi buradan hesaplanır.")
    dogum_giris = st.date_input("Doğum Tarihi", min_value=date(1940, 1, 1), max_value=date.today(),
                                format="DD.MM.YYYY", disabled=not dogum_var, key="sg_dogum",
                                **({} if "sg_dogum" in st.session_state else {"value": date(date.today().year - 9, 1, 1)}))

    # Paket 38a: geçersiz ya da boş alan → kayıt yok; uyarı ilgili alanın adıyla, ad-soyad yazılınca ya da
    # değer alt sınırın altındaysa hemen
    form_hata = sporcu_form_hatalari(yas, boy, kilo)
    for alan, mesaj in form_hata.items():
        deger_ = {"Yaş": yas, "Boy (cm)": boy, "Kilo (kg)": kilo}[alan]
        if deger_ is not None or (ad.strip() and soyad.strip()):
            st.error(f"{alan}: {mesaj}", icon=":material/error:")

    # Uyarı, ad-soyad yazılınca başlar: boş formun varsayılan değerleri uyarı üretmesin (Paket 11)
    profil_uyari = (profil_uyarilari(boy, kilo, yas, cinsiyet, dogum_giris if dogum_var else None)
                    if ad.strip() and soyad.strip() and not form_hata else [])
    profil_onay = True
    if profil_uyari:
        for u in profil_uyari:
            st.warning("⚠️ " + u)
        profil_onay = st.checkbox("Değerleri kontrol ettim, doğru", key="profil_onay_yeni")
    if st.button("Sporcu Kaydet", disabled=not profil_onay or bool(form_hata), type="primary", icon=":material/save:"):
        if ad and soyad:
            ad, soyad = ad_bicimi(ad), ad_bicimi(soyad)                 # Paket 38c
            yeni = {"Ad": ad, "Soyad": soyad, "Yaş": yas, "Cinsiyet": cinsiyet,
                    "Spor Dalı": spor_dali, "Derece": derece, "Boy (cm)": boy, "Kilo (kg)": kilo,
                    ANTRENMAN_KOLON: antrenman, GRUP_KOLON: grup.strip(),
                    DOGUM_KOLON: dogum_giris.strftime("%d.%m.%Y") if dogum_var else "",
                    ANTRENMAN_TARIH_KOLON: date.today().strftime("%d.%m.%Y") if antrenman != "Bilinmiyor" else ""}
            if os.path.exists(SPORCU_DOSYA):
                df = pd.read_excel(SPORCU_DOSYA)
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
            else:
                df = pd.DataFrame([yeni])
            df.to_excel(SPORCU_DOSYA, index=False)
            st.session_state["son_kaydedilen_sporcu"] = f"{ad} {soyad}"
            st.success(f"✅ {ad} {soyad} başarıyla kaydedildi! Şimdi aşağıdan ilgi anketini doldurabilirsiniz.")
            st.button("Başka sporcu ekle", icon=":material/person_add:", key="sg_baska",
                      on_click=_sporcu_formunu_temizle)
        else:
            st.warning("Lütfen sporcunun adını ve soyadını giriniz.")

    # ── İlgi anketi: sporcu girişi akışının parçası, test kaydından bağımsız (Paket 7) ──
    if os.path.exists(SPORCU_DOSYA):
        df_ilgi_sp = pd.read_excel(SPORCU_DOSYA)
        ilgi_liste = (df_ilgi_sp["Ad"].astype(str) + " " + df_ilgi_sp["Soyad"].astype(str)).tolist()
        if ilgi_liste:
            st.divider()
            st.subheader("İlgi Anketi")
            st.caption("Testlerden bağımsızdır; sporcu kaydedildikten hemen sonra doldurulabilir. "
                       "Sonuçlar Branşa Yönlendirme sekmesinde ve raporlarda kullanılır.")
            son_k = st.session_state.get("son_kaydedilen_sporcu")
            ilgi_sporcu = st.selectbox("Anketi dolduracak sporcu", ilgi_liste, format_func=ad_bicimi,
                                       index=ilgi_liste.index(son_k) if son_k in ilgi_liste else 0,
                                       key="ilgi_sporcu_sec")
            ilgi_anketi_formu(ilgi_sporcu)

    st.divider()
    baslik_ac("Kayıtlı Sporcular", ["VKİ"])
    if os.path.exists(SPORCU_DOSYA) and not pd.read_excel(SPORCU_DOSYA).empty:      # Paket 38c: boş dosya
        df_goster = pd.read_excel(SPORCU_DOSYA)
        if "Boy (cm)" in df_goster.columns and "Kilo (kg)" in df_goster.columns:
            df_goster["VKİ (kg/m²)"] = df_goster.apply(
                lambda satir: round(satir["Kilo (kg)"] / ((satir["Boy (cm)"] / 100) ** 2), 1)
                if satir["Boy (cm)"] > 0 else None,
                axis=1
            )
        if DOGUM_KOLON in df_goster.columns:
            df_goster["Doğum Çeyreği"] = df_goster[DOGUM_KOLON].map(
                lambda x: f"{dogum_ceyregi(x)}. çeyrek" if dogum_ceyregi(x) else "")
        st.dataframe(df_goster.assign(**{_k: df_goster[_k].map(lambda x: ad_bicimi(x) if isinstance(x, str) else x)
                                        for _k in ("Ad", "Soyad") if _k in df_goster.columns}),   # Paket 38c
                     width="stretch")

        st.divider()
        st.subheader("Sporcu Bilgilerini Düzenle / Sil")

        spor_listesi_duzenle = df_goster["Ad"] + " " + df_goster["Soyad"]
        secili_duzenle = st.selectbox("Düzenlenecek Sporcuyu Seçin", spor_listesi_duzenle, key="duzenle_sec", format_func=ad_bicimi)
        secili_idx = spor_listesi_duzenle[spor_listesi_duzenle == secili_duzenle].index[0]
        secili_satir = df_goster.loc[secili_idx]

        with st.form("duzenle_form"):
            d1, d2 = st.columns(2)
            with d1:
                yeni_ad    = st.text_input("Ad",    value=str(secili_satir.get("Ad", "")))
                yeni_yas   = st.number_input("Yaş", min_value=3, max_value=60, value=int(secili_satir.get("Yaş", 18)))
                tum_sporlar = [
                    "Genel/Yok",
                    "Güreş (Serbest)", "Güreş (Grekoromen)", "Judo", "Karate", "Taekwondo",
                    "Kickboks", "Muay Thai", "Boks", "Jiujitsu (BJJ)", "Sambo", "MMA",
                    "Futbol", "Basketbol", "Voleybol", "Hentbol", "Rugbi",
                    "Buz Hokeyi", "Su Topu", "Beyzbol",
                    "Atletizm (Sprint)", "Atletizm (Orta Mesafe)", "Atletizm (Uzun Mesafe)",
                    "Atletizm (Atlama)", "Atletizm (Atma)", "Yüzme", "Bisiklet", "Triatlon",
                    "Kürek", "Kano/Kayak", "Halter", "Jimnastik", "Tenis", "Masa Tenisi",
                    "Badminton", "Squash", "Golf", "Okçuluk", "Eskrim",
                    "Kayak (Alp)", "Kayak (Nordik)", "Paten", "Diğer"
                ]
                mevcut_spor = str(secili_satir.get("Spor Dalı", "Genel/Yok"))
                spor_idx = tum_sporlar.index(mevcut_spor) if mevcut_spor in tum_sporlar else 0
                yeni_spor  = st.selectbox("Spor Dalı", tum_sporlar, index=spor_idx)
                yeni_boy   = st.number_input("Boy (cm)", min_value=50, max_value=250, value=int(secili_satir.get("Boy (cm)", 170)))
            with d2:
                yeni_soyad  = st.text_input("Soyad", value=str(secili_satir.get("Soyad", "")))
                cin_sec     = ["Erkek", "Kadın"]
                cin_idx     = cin_sec.index(str(secili_satir.get("Cinsiyet", "Erkek"))) if str(secili_satir.get("Cinsiyet", "Erkek")) in cin_sec else 0
                yeni_cin    = st.selectbox("Cinsiyet", cin_sec, index=cin_idx)
                derece_sec  = ["Okul Öncesi/Öğrenci", "Rekreasyonel", "Amatör", "Yarı Profesyonel", "Profesyonel", "Milli Sporcu"]
                der_idx     = derece_sec.index(str(secili_satir.get("Derece", "Amatör"))) if str(secili_satir.get("Derece", "Amatör")) in derece_sec else 0
                yeni_derece = st.selectbox("Spor Derecesi", derece_sec, index=der_idx)
                yeni_kilo   = st.number_input("Kilo (kg)", min_value=10.0, max_value=200.0, step=0.1, value=float(secili_satir.get("Kilo (kg)", 70.0)))
            mevcut_grup = str(secili_satir.get(GRUP_KOLON, "") or "")
            yeni_grup = st.text_input("Grup / Sınıf", value="" if mevcut_grup == "nan" else mevcut_grup)
            mevcut_dogum = tarih_coz(secili_satir.get(DOGUM_KOLON))
            yeni_dogum_var = st.checkbox("Doğum tarihi kayıtlı", value=mevcut_dogum is not None)
            yeni_dogum = st.date_input("Doğum Tarihi", value=mevcut_dogum or date(date.today().year - 9, 1, 1),
                                       min_value=date(1940, 1, 1), max_value=date.today(), format="DD.MM.YYYY",
                                       key="duzenle_dogum")
            mevcut_ant, mevcut_ant_tarih = sporcu_antrenman(secili_satir.to_dict())
            yeni_ant = st.selectbox("Haftalık organize antrenman süresi", ANTRENMAN_SECENEKLERI,
                                    index=ANTRENMAN_SECENEKLERI.index(mevcut_ant), help=ANTRENMAN_YARDIM)
            if mevcut_ant_tarih:
                st.caption(f"Antrenman bilgisi son kayıt: {mevcut_ant_tarih}")

            duzenle_onay = st.checkbox("Olağandışı değer uyarısı çıkarsa: değerleri kontrol ettim, doğru",
                                       key="profil_onay_duzenle")
            kaydet_btn = st.form_submit_button("💾 Değişiklikleri Kaydet")
            sil_btn    = st.form_submit_button("🗑️ Bu Sporcuyu Sil", type="secondary")

        duzenle_uyari = profil_uyarilari(yeni_boy, yeni_kilo, yeni_yas, yeni_cin,
                                         yeni_dogum if yeni_dogum_var else None) if kaydet_btn else []
        if kaydet_btn and duzenle_uyari and not duzenle_onay:
            for u in duzenle_uyari:
                st.warning("⚠️ " + u)
            st.error("Kaydedilmedi: olağandışı değer var. Değerleri kontrol edin; doğruysa onay kutusunu işaretleyip "
                     "yeniden kaydedin.")
            kaydet_btn = False
        if kaydet_btn:
            df_goster.at[secili_idx, "Ad"]       = yeni_ad
            df_goster.at[secili_idx, "Soyad"]    = yeni_soyad
            df_goster.at[secili_idx, "Yaş"]      = yeni_yas
            df_goster.at[secili_idx, "Cinsiyet"] = yeni_cin
            df_goster.at[secili_idx, "Spor Dalı"]= yeni_spor
            df_goster.at[secili_idx, "Derece"]   = yeni_derece
            df_goster.at[secili_idx, "Boy (cm)"] = yeni_boy
            df_goster.at[secili_idx, "Kilo (kg)"]= yeni_kilo
            for kolon in (ANTRENMAN_KOLON, ANTRENMAN_TARIH_KOLON, DOGUM_KOLON, GRUP_KOLON):
                if kolon not in df_goster.columns:
                    df_goster[kolon] = ""
                df_goster[kolon] = df_goster[kolon].astype(object)
            df_goster.at[secili_idx, DOGUM_KOLON] = yeni_dogum.strftime("%d.%m.%Y") if yeni_dogum_var else ""
            df_goster.at[secili_idx, GRUP_KOLON] = yeni_grup.strip()
            if yeni_ant != mevcut_ant:
                df_goster.at[secili_idx, ANTRENMAN_KOLON] = yeni_ant
                df_goster.at[secili_idx, ANTRENMAN_TARIH_KOLON] = (date.today().strftime("%d.%m.%Y")
                                                                   if yeni_ant != "Bilinmiyor" else "")
            # VKİ sütununu çıkar, orijinal sütunlarla kaydet
            kayit_df = df_goster.drop(columns=["VKİ (kg/m²)", "Doğum Çeyreği"], errors="ignore")
            kayit_df.to_excel(SPORCU_DOSYA, index=False)
            st.success(f"✅ {yeni_ad} {yeni_soyad} bilgileri güncellendi!")
            st.rerun()

        if sil_btn:
            df_goster = df_goster.drop(index=secili_idx).reset_index(drop=True)
            kayit_df  = df_goster.drop(columns=["VKİ (kg/m²)", "Doğum Çeyreği"], errors="ignore")
            kayit_df.to_excel(SPORCU_DOSYA, index=False)
            st.success(f"🗑️ {secili_duzenle} silindi.")
            st.rerun()
    else:
        st.info("Sistemde henüz kayıtlı sporcu bulunmamaktadır.")
