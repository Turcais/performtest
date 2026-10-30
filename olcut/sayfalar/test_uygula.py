"""
Test Uygula sayfası: tek test girişi, protokol, görsel, normatif değerlendirme.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import os
import pandas as pd
import streamlit as st
from datetime import date
from veri.metinler import ACIKLAMALAR, DUNYA_REKORU
from veri.normlar_kategorik import NORMATIF_TEST
from olcut.analiz import _kisa_kaynak, _konum_sayi
from olcut.bilesenler import _gecerli_secim, baslik_ac, bolum_terimleri, terim_metni, terimleri_bul
from olcut.esik import NORMATIF_ESIK_YAS, esik_degerlendir
from olcut.gorseller.cizim import tg_kabugu
from olcut.gorseller.sahneler import TEST_GORSELLERI, test_gorseli_html, test_gorseli_penceresi
from olcut.katalog_islemleri import (
    TEST_KATALOGU, TEST_TAKMA_AD, kanonik_test, protokol_formatla, protokol_ozet_cikar, test_ara, test_bilgisi,
    test_etiketli, test_izi)
from olcut.kayit import kayitlari_yaz, makullukte_uyarilar, onceki_olcumler, test_kaydi_olustur
from olcut.norm import (
    NORMATIF, NORMATIF_KAPSAM, NORMATIF_YAS, NORMSUZ_TESTLER, NORM_YOK_METNI, ROLATIF_KUVVET, SPORCU_DOSYA,
    TURETILEN_DEGISKENLER, bant_metni, normatif_degerlendir, normatif_test_degerlendir, orneklem_disi_metni,
    orneklem_notlari, orneklem_tablosu, orneklem_uygun, sifir_gecerli, turetilmis_degerler, yas_persentil_bul,
    yas_z_skoru, z_durum_notu)
from olcut.oneri import gorselsiz_metni
from olcut.ortak import DOGUM_KOLON, ad_bicimi, guvenli_float, tam_yas, veri_yolu
from olcut.tema import kart_izgarasi_html, sonuc_karti_html


def test_uygula_sayfasi():
    """Test Uygula sayfası (Bölme Aşama 2: satır içi dal fonksiyona sarıldı)."""
    # Hiyerarşi (Paket 11): seçim → [giriş | normatif sonuç] yan yana → kaydet;
    # protokol ve kaynak katlanmış; rekor ve teknik ayrıntı en altta.
    st.header("Test Uygula")

    df_sporcu = pd.read_excel(veri_yolu(SPORCU_DOSYA)) if os.path.exists(veri_yolu(SPORCU_DOSYA)) else None
    if df_sporcu is None or df_sporcu.dropna(how="all").empty:      # Paket 38n: boş dosya (yeni kulüp) da
        st.error("Sistemde sporcu bulunamadı. Lütfen önce 'Sporcu Girişi' yapın.")
    else:
        sporcu_listesi = df_sporcu["Ad"] + " " + df_sporcu["Soyad"]

        # ── 1. Seçim: sporcu, test, tarih ──
        s1, s2 = st.columns([1, 1])
        with s1:
            _gecerli_secim("tu_sporcu", sporcu_listesi)
            secili_sporcu = st.selectbox("Test Edilecek Sporcuyu Seçin", sporcu_listesi, key="tu_sporcu", format_func=ad_bicimi)
        with s2:
            mod = st.radio("Test Arama Modu", ["📂 Kategoriye Göre", "🔍 Tüm Testlerde Ara"], horizontal=True,
                           key="tu_mod")

        sporcu_satir = df_sporcu[df_sporcu["Ad"] + " " + df_sporcu["Soyad"] == secili_sporcu].iloc[0]
        sporcu_kilo = guvenli_float(sporcu_satir.get("Kilo (kg)", 0))
        test_havuzu = None

        if mod == "🔍 Tüm Testlerde Ara":
            tum_testler = {}

            def testleri_topla(d, yol=""):
                for k, v in d.items():
                    if k == "_kunye":
                        continue  # künye meta verisi test değildir
                    if isinstance(v, dict):
                        if "protokol" in v:
                            tum_testler[f"{yol} › {k}".lstrip(" › ")] = v
                        else:
                            testleri_topla(v, f"{yol} › {k}".lstrip(" › "))
            testleri_topla(TEST_KATALOGU)

            col1, col2 = st.columns(2)
            with col1:
                arama = st.text_input("🔍 Test ara (ad ya da ölçtüğü şey: sürat, çeviklik, kuvvet, metre…)")
            filtreli = {}
            for t_ in test_ara(arama):
                filtreli[" › ".join(x for x in t_["yol"] if x) + " › " + t_["ad"]] = tum_testler.get(
                    " › ".join(x for x in t_["yol"] if x) + " › " + t_["ad"])
            filtreli = {k_: v_ for k_, v_ in filtreli.items() if v_ is not None}
            with col2:
                if filtreli:
                    secim = st.selectbox("Test Seçimi", list(filtreli.keys()))
                    test_tarihi = st.date_input("Test Tarihi", value=date.today())
                else:
                    st.warning("Arama sonucu bulunamadı.")
                    secim = None
                    test_tarihi = date.today()
            if not secim:
                return                                   # Paket 38k: st.stop() değil — alt bilgi yine çizilsin
            test_adi = secim.split(" › ")[-1]
            test_bilgi = filtreli[secim]
            kategori = secim.split(" › ")[0]
            alt_kategori = secim.split(" › ")[1] if " › " in secim else ""
            secili_brans = None
        else:
            col1, col2 = st.columns(2)
            with col1:
                # anahtarlar üst seçimi içerir: yönlendirme ekranı bir testi önceden seçebilir, kategori
                # değişince alt seçim geçersiz kalmaz (Paket 16)
                _gecerli_secim("tu_kategori", TEST_KATALOGU)
                kategori = st.selectbox("Test Kategorisi", list(TEST_KATALOGU.keys()), key="tu_kategori")
                _alt_ops = list(TEST_KATALOGU[kategori].keys())
                _gecerli_secim(f"tu_alt::{kategori}", _alt_ops)
                alt_kategori = st.selectbox("Alt Kategori / Batarya", _alt_ops, key=f"tu_alt::{kategori}")
            with col2:
                alt_icerik = TEST_KATALOGU[kategori][alt_kategori]
                if kategori == "Branşa Özgü Testler":
                    _br_ops = [k for k in alt_icerik.keys() if k != "_kunye"]
                    _gecerli_secim(f"tu_brans::{kategori}::{alt_kategori}", _br_ops)
                    secili_brans = st.selectbox("Branş", _br_ops, key=f"tu_brans::{kategori}::{alt_kategori}")
                    test_havuzu = alt_icerik[secili_brans]
                else:
                    secili_brans = None
                    test_havuzu = alt_icerik
                _t_ops = [t for t in test_havuzu.keys() if t != "_kunye"]
                _t_key = f"tu_test::{kategori}::{alt_kategori}::{secili_brans}"
                _gecerli_secim(_t_key, _t_ops)
                test_adi = st.selectbox("Test Seçimi", _t_ops, key=_t_key, format_func=test_etiketli)
                test_tarihi = st.date_input("Test Tarihi", value=date.today())
            test_bilgi = test_havuzu[test_adi]

        _iz_yol = (tuple((secim.split(" › ")[:-1] + [None, None])[:3]) if mod == "🔍 Tüm Testlerde Ara"
                   else (kategori, alt_kategori, secili_brans))
        st.caption(f"📍 {test_izi(test_adi, _iz_yol)}")              # iz çubuğu (Paket 33)
        if test_adi in TEST_TAKMA_AD:                 # aynı test: veri tek adda toplanır (Paket 27)
            st.caption(f"Bu test '{kanonik_test(test_adi)}' ile aynıdır; sonuç o adla kaydedilir.")
            test_adi = kanonik_test(test_adi)
            test_bilgi = test_bilgisi(test_adi)
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        sporcu_spor_dali = str(sporcu_satir.get("Spor Dalı", "Genel/Yok"))
        sporcu_yas = sporcu_satir.get("Yaş", 0)
        tekli_test_yasi = tam_yas(sporcu_satir.get(DOGUM_KOLON), test_tarihi) or sporcu_yas

        st.divider()

        # ── Test görseli (Paket 13): test adının yanında, giriş alanlarının üstünde ──
        if test_adi in TEST_GORSELLERI:
            tg_anahtar = f"tg_n::{test_adi}"
            g_sol, g_sag = st.columns([11, 9], gap="large")
            with g_sol:
                st.subheader(test_adi)
                st.caption(TEST_GORSELLERI[test_adi][1])
                gb1, gb2, gb3 = st.columns(3)
                if gb1.button("Tekrar oynat", icon=":material/replay:", key=f"tg_tekrar::{test_adi}"):
                    st.session_state[tg_anahtar] = st.session_state.get(tg_anahtar, 0) + 1
                    st.session_state["tg_durdur"] = False
                gb3.toggle("Durdur", key="tg_durdur", help="Animasyonu durdurur; ölçüm anının çizimi kalır.")
                if gb2.button("Büyüt · adım adım", icon=":material/open_in_full:", key=f"tg_buyut::{test_adi}"):
                    test_gorseli_penceresi(test_adi, test_bilgi["protokol"])
            with g_sag:
                kabuk = tg_kabugu((test_adi, st.session_state.get(tg_anahtar, 0)))
                st.markdown(test_gorseli_html(test_adi, kabuk=kabuk, duragan=st.session_state.get("tg_durdur", False)),
                            unsafe_allow_html=True)
        elif gorselsiz_metni(test_adi):                 # görselin yeri boş kalmasın: neden yazılır (Paket 27)
            st.subheader(test_adi)
            st.info(gorselsiz_metni(test_adi), icon=":material/hide_image:")

        sol, sag = st.columns([11, 9], gap="large")

        # ── 2a. Giriş (sol) ──
        hesaplanan = {}
        with sol:
            st.subheader("Ölçüm")
            st.caption(f"{secili_sporcu} · test günü {tekli_test_yasi} yaş · {sporcu_cinsiyet} · {test_adi}")

            if test_adi == "Special Wrestling Fitness Test (SWFT)":
                if sporcu_kilo == 0:
                    st.warning("Bu sporcunun kilo bilgisi yok. Manken ağırlığı otomatik önerilemiyor.")
                    manken_auto = 22
                elif sporcu_kilo < 75:
                    manken_auto = 22
                elif sporcu_kilo <= 89.99:
                    manken_auto = 27
                else:
                    manken_auto = 32
                st.info(f"⚖️ Sporcu kilosu: **{sporcu_kilo} kg** → Önerilen manken: **{manken_auto} kg**")
                c_a, c_b = st.columns(2)
                with c_a:
                    p1 = st.number_input("Periyot 1 Atış Sayısı", min_value=0, max_value=50, help=ACIKLAMALAR["Periyot 1 Atış Sayısı"])
                    p2 = st.number_input("Periyot 2 Atış Sayısı", min_value=0, max_value=50, help=ACIKLAMALAR["Periyot 2 Atış Sayısı"])
                    p3 = st.number_input("Periyot 3 Atış Sayısı", min_value=0, max_value=50, help=ACIKLAMALAR["Periyot 3 Atış Sayısı"])
                with c_b:
                    manken_kg = st.number_input("Manken Ağırlığı (kg)", min_value=10, max_value=60, value=manken_auto, help=ACIKLAMALAR["Manken Ağırlığı (kg)"])
                    hr0 = st.number_input("HR0 - Test sonu KAH (bpm)", min_value=0, max_value=250, help=ACIKLAMALAR["HR0 (bpm)"])
                    hr1 = st.number_input("HR1 - 1. dk KAH (bpm)", min_value=0, max_value=250, help=ACIKLAMALAR["HR1-dk (bpm)"])

                tn_throws = p1 + p2 + p3
                tn_bm = round(tn_throws / sporcu_kilo, 3) if sporcu_kilo > 0 else 0
                swft_index = round((hr0 + hr1) / tn_throws * 100, 2) if tn_throws > 0 else 0

                st.markdown("##### Otomatik hesaplanan")
                m1, m2, m3 = st.columns(3)
                m1.metric("Toplam Atış (TnThrows)", tn_throws)
                m2.metric("TnThrows/BM", tn_bm, help="Vücut ağırlığına normalize atış sayısı")
                m3.metric("SWFT Index", swft_index, help="Düşük = daha iyi performans")

                degerler = {
                    "Periyot 1 Atış Sayısı": p1, "Periyot 2 Atış Sayısı": p2, "Periyot 3 Atış Sayısı": p3,
                    "Toplam Atış (TnThrows)": tn_throws, "Manken Ağırlığı (kg)": manken_kg,
                    "HR0 (bpm)": hr0, "HR1-dk (bpm)": hr1, "TnThrows/BM": tn_bm, "SWFT Index": swft_index,
                }
            else:
                degiskenler = test_bilgi["degiskenler"]
                degerler = {}
                cols = st.columns(2)
                for i, deg in enumerate(degiskenler):
                    with cols[i % 2]:
                        degerler[deg] = st.text_input(deg, help=ACIKLAMALAR.get(deg, ""))

                hesaplanan, _uyarilar_h = turetilmis_degerler(test_adi, degerler, sporcu_satir, sporcu_kilo)
                for _u_h in _uyarilar_h:
                    st.warning(_u_h)
                if hesaplanan:
                    terimler_h = terimleri_bul(*hesaplanan.keys())
                    if terimler_h:
                        baslik_ac("Otomatik hesaplanan", terimler_h, "#####")
                    else:
                        st.markdown("##### Otomatik hesaplanan")
                    cols_h = st.columns(min(len(hesaplanan), 3))
                    for i, (k, v) in enumerate(hesaplanan.items()):
                        cols_h[i % len(cols_h)].metric(k, v, help=terim_metni(terimleri_bul(k)) or None)
                    if test_adi in ROLATIF_KUVVET and ROLATIF_KUVVET[test_adi][1] in hesaplanan:   # Paket 36
                        st.caption(f"Hesapta kullanılan kilo: {_konum_sayi(sporcu_kilo)} kg (profil)")
                    degerler.update(hesaplanan)

            notlar = st.text_area("Ek Notlar (Opsiyonel)", height=80)

        # ── Normatif hesap ──
        norm_sonuclar = {}
        yas_sonuclar = {}
        tum_degerler = {**degerler, **hesaplanan}
        for degisken, deger in tum_degerler.items():
            try:
                d = float(deger)
            except (ValueError, TypeError):
                continue
            if d == 0 and not sifir_gecerli(test_adi, degisken):
                continue  # 0 = henüz girilmemiş (0'ın gerçek skor olduğu normlar hariç)
            # 1) Yaş bazlı persentil normu (en öncelikli)
            yas_sonuc = yas_persentil_bul(test_adi, degisken, sporcu_yas, sporcu_cinsiyet, d,
                                          sporcu_satir.get(DOGUM_KOLON), test_tarihi)
            if yas_sonuc:
                yas_sonuclar[degisken] = (d, yas_sonuc)
                continue
            # 1b) Yaşa göre eşik (FitnessGram HFZ, Paket 20)
            esik_sonuc = esik_degerlendir(test_adi, degisken, d, sporcu_yas, sporcu_cinsiyet)
            if esik_sonuc:
                norm_sonuclar[degisken] = (d, esik_sonuc)
                continue
            # 2) Teste özgü kategorik norm
            test_sonuc = normatif_test_degerlendir(test_adi, degisken, d, sporcu_cinsiyet)
            if test_sonuc:
                norm_sonuclar[degisken] = (d, test_sonuc)
                continue
            # 3) Genel değişken bazlı norm (yalnızca benzersiz adlar)
            sonuc = normatif_degerlendir(degisken, d, sporcu_cinsiyet, sporcu_spor_dali, test_adi, yas=tekli_test_yasi)
            if sonuc:
                norm_sonuclar[degisken] = (d, sonuc)

        _aday = list(tum_degerler) + [d for d in ([ROLATIF_KUVVET[test_adi][1]] if test_adi in ROLATIF_KUVVET else [])
                                      + TURETILEN_DEGISKENLER.get(test_adi, []) if d not in tum_degerler]
        _kapsamda = [d for d in _aday if d in NORMATIF and (d not in NORMATIF_KAPSAM or NORMATIF_KAPSAM[d](test_adi))]
        orneklem_disi = [d for d in _kapsamda if NORMATIF[d].get("tur") == "orneklem"
                         and not orneklem_uygun(d, sporcu_cinsiyet, tekli_test_yasi, test_adi)]   # Paket 35
        normatif_olan = [d for d in _kapsamda if d not in orneklem_disi]
        yas_normu_olan = [d for d in tum_degerler
                          if f"{test_adi} › {d}" in NORMATIF_YAS or f"{test_adi} › {d}" in NORMATIF_TEST
                          or f"{test_adi} › {d}" in NORMATIF_ESIK_YAS]

        # ── 2b. Normatif sonuç (sağ, girişin yanında) ──
        teknik = []   # en alttaki teknik ayrıntı için
        with sag:
            st.subheader("Normatif Sonuç")
            terimler_ys = ["Performans persentili", "Norm"]
            if yas_sonuclar or yas_normu_olan:
                terimler_ys += ["P5 / P95", "Z skoru", "Sınır değer (P5 altı / P95 üstü)"]
            if any(y.get("dusuk_iyi") for _, y in list(yas_sonuclar.values()) + list(norm_sonuclar.values())):
                terimler_ys.append("Düşük-iyi test")
            if any(y.get("notr") for _, y in yas_sonuclar.values()):
                terimler_ys.append("Nötr (tanımlayıcı) ölçüm")
            if any(y.get("ceyrek_notu") for _, y in yas_sonuclar.values()):
                terimler_ys.append("Doğum çeyreği")
            terimler_ys += [t for t in terimleri_bul(test_bilgi["protokol"]) if t not in terimler_ys]

            kartlar = []
            for degisken, (deger, ys) in yas_sonuclar.items():
                zs = yas_z_skoru(test_adi, degisken, sporcu_yas, sporcu_cinsiyet, deger,
                                 sporcu_satir.get(DOGUM_KOLON), test_tarihi)
                notlar_k = [z_durum_notu(zs) if zs else None, ys.get("yas_notu")]
                if ys.get("ceyrek_notu") and not ys.get("ceyrek"):
                    notlar_k.append(ys["ceyrek_notu"])        # "çeyrek bilinmiyor" ekranda kalır
                kaynak_k = _kisa_kaynak(ys["kaynak"]) + (f" · {ys['tablo']}" if ys.get("tablo") else "")
                kaynak_k += f" · {ys['kullanilan_yas']} yaş {sporcu_cinsiyet.lower()}"
                kartlar.append(sonuc_karti_html(
                    degisken, deger, ys["birim"], ys["kategori"], notr=ys.get("notr", False),
                    persentil=zs["persentil_performans"] if zs else None, kaynak=kaynak_k, notlar=notlar_k))
                teknik.append((degisken, ys, zs))
            for degisken, (deger, sonuc) in norm_sonuclar.items():
                if sonuc.get("tur") == "orneklem":      # Kademe 2 (Paket 35): kategori yok, örneklem ort ± SD
                    kartlar.append(sonuc_karti_html(
                        degisken, deger, sonuc["birim"], None,
                        kaynak=f"{_kisa_kaynak(sonuc['kaynak'])} · örneklem karşılaştırması · {sporcu_cinsiyet.lower()}",
                        notlar=orneklem_notlari(sonuc, tekli_test_yasi)))
                    continue
                if "esik" in sonuc:                     # yaşa göre eşik (HFZ): hangi yaş satırı, eşik kaç
                    alt, ust = sonuc["esik"]
                    sinir = (f"≥ {alt:g}" if ust is None else f"{alt:g}–{ust:g}").replace(".", ",")
                    kartlar.append(sonuc_karti_html(
                        degisken, deger, sonuc["birim"], sonuc["kategori"],
                        kaynak=(f"{_kisa_kaynak(sonuc['kaynak'])} · {sonuc['olcut']} {sinir} {sonuc['birim']} · "
                                f"{sonuc['kullanilan_yas']} yaş {sporcu_cinsiyet.lower()}"),
                        notlar=[sonuc.get("yas_notu")]))
                    continue
                brans_k = (f"{sporcu_spor_dali} branş normu" if sporcu_spor_dali != "Genel/Yok" else "genel norm")
                kartlar.append(sonuc_karti_html(
                    degisken, deger, "", sonuc["kategori"],
                    kaynak=f"{_kisa_kaynak(sonuc['kaynak'])} · {brans_k} · {sporcu_cinsiyet.lower()}"))

            if kartlar:
                st.markdown(kart_izgarasi_html(kartlar), unsafe_allow_html=True)
                for _o_d, (_o_v, _o_s) in norm_sonuclar.items():          # Kademe 2: örneklem satırları (Paket 35)
                    if _o_s.get("tur") == "orneklem":
                        with st.expander(f"Örneklem değerleri — {_o_d}", icon=":material/table_rows:"):
                            st.markdown(orneklem_tablosu(_o_s))
            elif normatif_olan and all(NORMATIF.get(d, {}).get("tur") == "orneklem" for d in normatif_olan) \
                    and not yas_normu_olan:
                st.info("Değer girildiğinde sonuç hesaplanır ve örneklem ortalamasıyla yan yana görünür "
                        "(yüzdelik norm değil)." + (" Rölatif değer kayıtlı vücut ağırlığından hesaplanır."
                                                    if test_adi in ROLATIF_KUVVET else ""))
            elif normatif_olan or yas_normu_olan:
                st.info("Değer girildiğinde sonuç burada, yaşa ve cinsiyete göre normla birlikte görünür.")
            elif orneklem_disi:
                st.info(orneklem_disi_metni(orneklem_disi[0]))
            elif test_adi in NORMSUZ_TESTLER:
                st.info(NORM_YOK_METNI, icon=":material/radio_button_unchecked:")       # ○ norm yok
            else:
                st.info("Bu test için normatif değerlendirme henüz mevcut değil. İlgili literatür "
                        "bulunduğunda eklenecektir.")
            bolum_terimleri(terimler_ys)

        # ── 2c. Kaydet (sol, girişin altında) ──
        with sol:
            with st.expander("Oturum bilgisi (isteğe bağlı)"):
                o1, o2 = st.columns(2)
                with o1:
                    tekli_yer = st.text_input("Yer", key="tekli_yer")
                with o2:
                    tekli_uyg = st.text_input("Uygulayan", key="tekli_uygulayici")

            # Makullük kontrolü: norm P1-P99 dışı değer → uyar, onaylanırsa kaydet
            tekli_uyari = makullukte_uyarilar(
                test_adi, {**degerler, **{k: v for k, v in hesaplanan.items() if isinstance(v, (int, float))}},
                tekli_test_yasi, sporcu_cinsiyet, sporcu_satir.get(DOGUM_KOLON), test_tarihi,
                onceki=onceki_olcumler(secili_sporcu, test_adi, test_tarihi))      # Paket 38g: normsuzda da uyarı
            tekli_onay = True
            if tekli_uyari:
                for u in tekli_uyari:
                    st.warning("⚠️ " + u)
                tekli_onay = st.checkbox("Değerleri kontrol ettim, doğru — yine de kaydet", key="tekli_onay")

            if st.button("Test Sonucunu Veritabanına Kaydet", disabled=not tekli_onay, type="primary"):
                kayit = test_kaydi_olustur(
                    secili_sporcu, sporcu_satir, kategori, alt_kategori, secili_brans, test_adi, test_tarihi,
                    degerler, hesaplanan, notlar,
                    {"kimlik": "", "yer": tekli_yer.strip(), "uygulayici": tekli_uyg.strip()})
                kayitlari_yaz([kayit])
                st.success("✅ Test sonucu başarıyla kaydedildi!")

        # ── 3. Test hakkında (katlanmış) ──
        st.divider()
        st.markdown('<div class="sp-bolum">TEST HAKKINDA</div>', unsafe_allow_html=True)
        with st.expander("Sahada nasıl uygularsın? (sade özet)", icon=":material/sports:"):
            st.markdown(protokol_ozet_cikar(test_bilgi["protokol"]))
        with st.expander("Akademik protokol ve kaynaklar", icon=":material/menu_book:"):
            st.markdown(protokol_formatla(test_bilgi["protokol"]))
            st.markdown("---")
            st.markdown("**Kaynaklar (APA):**")
            st.text(test_bilgi["kaynak"])
        kunye = test_havuzu.get("_kunye") if test_havuzu else None
        if kunye and isinstance(kunye, dict) and any(k_ != "yas_araligi" for k_ in kunye):
            with st.expander(f"Batarya künyesi — {alt_kategori}", icon=":material/info:"):
                k1, k2 = st.columns(2)
                with k1:
                    st.markdown(f"**Geliştiren:** {kunye.get('gelistiren', '-')}")
                    st.markdown(f"**Ülke/Bölge:** {kunye.get('ulke', '-')}")
                    st.markdown(f"**Yıl:** {kunye.get('yil', '-')}")
                with k2:
                    st.markdown(f"**Hedef Yaş Grubu:** {kunye.get('hedef_yas', '-')}")
                    if kunye.get("yas_araligi"):
                        st.caption(f"Yönlendirmede kullanılan yaş aralığı: {kunye['yas_araligi'][0]}-"
                                   f"{kunye['yas_araligi'][1]}")
                    st.markdown(f"**Kullanım Yaygınlığı:** {kunye.get('yayginlik', '-')}")

        # ── 4. Rekor ve teknik ayrıntı (en altta) ──
        rekor_satirlar = []
        for degisken in tum_degerler:
            if degisken in DUNYA_REKORU:
                r = DUNYA_REKORU[degisken]
                if sporcu_cinsiyet in r:
                    rd = r[sporcu_cinsiyet]
                    rekor_satirlar.append(
                        f"**{degisken}** Dünya Rekoru ({sporcu_cinsiyet}): "
                        f"**{rd['deger']}** — {rd['sahibi']} ({rd['yil']})"
                        + (f" | Olimpiyat: **{r.get('olimpiyat_' + sporcu_cinsiyet.lower(), {}).get('deger', '')}**"
                           if 'olimpiyat_' + sporcu_cinsiyet.lower() in r else ""))
        if teknik or norm_sonuclar or rekor_satirlar:
            st.markdown('<div class="sp-bolum">TEKNİK AYRINTI</div>', unsafe_allow_html=True)
        if teknik:
            with st.expander("Persentil bantları, Z ve norm hücresi", icon=":material/table_chart:"):
                ilk = teknik[0][1]
                st.caption(f"Norm yaşı: {ilk['kullanilan_yas']} | Cinsiyet: {sporcu_cinsiyet} | n = {ilk['n']}")
                for degisken, ys, zs in teknik:
                    if ys.get("notr"):
                        ok = "antropometrik ölçü — iyi/kötü değil, akranlara göre konum"
                    else:
                        ok = "↓ düşük daha iyi" if ys["dusuk_iyi"] else "↑ yüksek daha iyi"
                    st.markdown(f"**{degisken}** ({ok})")
                    st.caption(bant_metni(ys["bantlar"], ys["dusuk_iyi"] and not ys.get("notr")))
                    if zs:
                        if zs["notr"]:
                            st.caption(f"Persentil ≈ P{zs['persentil_performans']:.0f} · Z = {zs['z']:+.2f} "
                                       f"(tanımlayıcı; bileşik skorlara girmez)")
                        else:
                            yon = " — süre/az olan iyi, işaret çevrildi" if zs["dusuk_iyi"] else ""
                            st.caption(f"Performans persentili ≈ P{zs['persentil_performans']:.0f} · "
                                       f"Z = {zs['z_performans']:+.2f} (+ = akranlarından iyi{yon})")
                    if ys.get("ceyrek_notu"):
                        st.caption(("ℹ️ " if ys.get("ceyrek") else "⚠️ ") + ys["ceyrek_notu"]
                                   + (f" — {ys['tablo']}" if ys.get("tablo") else ""))
                st.markdown("**Persentil kaynakları**")
                for k in sorted({y["kaynak"] for _, y, _ in teknik if y["kaynak"]}):
                    st.caption(k)
        _kat_k = sorted({s["kaynak"] for _, s in norm_sonuclar.values() if s["kaynak"] and s.get("tur") != "orneklem"})
        _orn_k = sorted({s["kaynak"] for _, s in norm_sonuclar.values() if s.get("tur") == "orneklem"})
        if _kat_k:
            with st.expander("Kategorik norm kaynakları", icon=":material/table_chart:"):
                for k in _kat_k:
                    st.caption(k)
        if _orn_k:                                  # Kademe 2 (Paket 35): norm değil, örneklem
            with st.expander("Örneklem kaynağı (Kademe 2 — yüzdelik norm değil)", icon=":material/table_chart:"):
                for k in _orn_k:
                    st.caption(k)
                for ku in {str(s.get("kunye")): s.get("kunye") for _, s in norm_sonuclar.values()
                           if s.get("tur") == "orneklem" and s.get("kunye")}.values():
                    st.caption(f"Örneklem: {ku['orneklem']}. {ku['protokol']}")
                    for _ek in ("not", "dogrulama"):                      # Paket 36
                        if ku.get(_ek):
                            st.caption(ku[_ek])
        if rekor_satirlar:
            with st.expander("Dünya ve olimpiyat rekorları", icon=":material/emoji_events:"):
                for satir in rekor_satirlar:
                    st.markdown(satir)
