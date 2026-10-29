import streamlit as st
import inspect
import pandas as pd
import os
import re
import collections
from io import BytesIO
from datetime import date
import html as _html

# ════════════════════════════════════════════════════════════
# GÖRSEL SİSTEM (Paket 11) — TÜM renk, yazı ve boşluk kararları BURADA.
# Sayfalar, sonuç kartı, grafikler, raporlar ve .streamlit/config.toml
# yalnızca bu simgelerden beslenir; başka yerde renk kodu yazılmaz.
# Paket 34: iki palet (açık / koyu). Hangi paletin kullanıldığını YALNIZ palet(tema) söyler; kod RENK'e
# doğrudan bakmaz. Uygulama içindeki HTML/SVG renkleri CSS değişkeni (yedekli) olarak yazılır, tarayıcı temaya
# göre çözer; Python tarafı temayı bilmek zorunda kalmaz.
# ════════════════════════════════════════════════════════════
from olcut.tema import (   # Bölme Aşama 2: olcut/tema.py
    UYGULAMA_ADI, UYGULAMA_ALT, RENK, RENK_KOYU, FIGUR_KATMANI, FIGUR_DERINLIK_OPAKLIK, YAZI_AILESI, YAZI,
    BOSLUK, b, NORM_SKALASI, NORM_SKALASI_KOYU, KATEGORI_ESDEGER, NOTR_SKALA, NOTR_SIRA, BILINMEYEN_SKALA,
    SERI_RENKLERI, RAPOR_VURGU, NOTR_SKALA_KOYU, BILINMEYEN_SKALA_KOYU, SERI_RENKLERI_KOYU, RAPOR_VURGU_KOYU,
    TEMALAR, palet, _css_degiskenleri, TG_DEGISKENLERI, renk_css, tg_renk, _norm_css, tema_degiskenleri_css,
    GRAFIK_YUVALARI, _grafik_yuvasi_renkleri, _grafik_sira_renkleri, grafik_renk, grafik_norm_renk,
    kategori_bilgisi, kategori_rengi, kategori_rozeti, seviye_olcer, _AYRILMA_EKI, yuzde_ayrilma, _sayi_goster,
    sonuc_karti_html, logo_svg, logo_veri_url, ACILIS_TANIM, kimlik_html, kart_izgarasi_html, BILESEN_CSS,
    TEMA_CSS, tema_toml, grafik_duzeni, config_toml_yaz, tasarimi_uygula)


from olcut.ortak import (   # Bölme Aşama 2: olcut/ortak.py
    _desteklenen, _TR_KUCUK, _TR_BUYUK, _TR_BUYUT, _TR_KUCULT, _sozcuk_bicimi, ad_bicimi, _girildi, DOGUM_KOLON,
    tarih_coz, dogum_ceyregi, tam_yas, _yas_degeri, _e, _sayi, _tarih_gunu, guvenli_float,
    METIN_DEGISKEN_KALIBI, AYAR_DOSYA, ayar_oku, ayar_yaz, _tablo_guvenli, tablo_oku, _dt_simdi, NOT_CIPLERI,
    not_metni, not_coz)


def coklu_secim(etiket, secenekler, *, tumunu_sec=False, **k):
    """
    st.multiselect, Türkçe (Paket 38a): yer tutucu "Seçiniz"; Streamlit'in İngilizce "Select all" seçeneği kapalı,
    gerekiyorsa üstte "Tümünü seç" düğmesi (key verilmişse).
    """
    secenekler = list(secenekler)
    if tumunu_sec and k.get("key") and secenekler:
        st.button("Tümünü seç", type="tertiary", key=f"tumu::{k['key']}",
                  on_click=lambda: st.session_state.__setitem__(k["key"], list(secenekler)))
    return st.multiselect(etiket, secenekler, **{**_desteklenen(st.multiselect, placeholder="Seçiniz",
                                                                 select_all=False), **k})


st.set_page_config(page_title=UYGULAMA_ADI, page_icon=logo_veri_url(), layout="wide")
tasarimi_uygula()
st.sidebar.markdown(kimlik_html(), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TEST VERİTABANI (Protokol + Kaynak + Değişkenler)
# ════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════
# NORMATİF DEĞERLER VERİTABANI
# Format: test_değişkeni → cinsiyet → seviye → (min, max)
# dusuk_iyi=True → düşük değer daha iyidir (sprint, SJFT vb.)
# ════════════════════════════════════════════════════════════
from veri.normlar_kategorik import (
    ORNEKLEM_KAYNAK_AYDOS_2004, ORNEKLEM_KUNYE_AYDOS_2004, _AYDOS_2004, ORNEKLEM_KAYNAK_MORASSUTTI_2025,
    ORNEKLEM_KUNYE_MORASSUTTI_2025, NORMATIF_TEST)


# ════════════════════════════════════════════════════════════
# KADEME 2 — ÖRNEKLEM KARŞILAŞTIRMASI (Paket 35). YÜZDELİK NORM DEĞİL.
# Aydos, Pepe ve Karakuş (2004): n=77 ERKEK, 18-30 yaş, üniversite kulüp sporcusu (milli takım değil),
# branş başına n=10-15. Değer örneklem ortalaması ± SD'dir: bant, kategori ya da eşik türetilmez; arayüzde
# "norm" değil "örneklem" denir. Yalnız 'Erkek' tanımlıdır — 'Kadın' açılmaz, kadına erkek değeri düşmez
# (genel normdaki Erkek'e düşme kuralı örneklem kaydında işlemez). 18 yaş altında referans gösterilmez
# (yas_alt). Kapsam yalnız "1RM Squat (Arka Çömelme)" ve "1RM Bench Press" (NORMATIF_KAPSAM).
# Künye: çalışma standart 1RM protokolü tarif etmez ("kaldırdığı maksimal ağırlık"; 10 dk hafif ağırlıkla
# ısınma); squat derinliği diz açısı 90°'yi geçene kadar.
# ════════════════════════════════════════════════════════════


from olcut.norm import (   # Bölme Aşama 2: olcut/norm.py
    _aydos_branslari, NORMATIF, ORNEKLEM_SPOR_DALI, ROLATIF_KUVVET, NORM_YOK_METNI, NORMSUZ_TESTLER,
    TURETILEN_DEGISKENLER, SARGENT_DENEMELER, ORNEKLEM_DISI_METNI, normatif_test_degerlendir, NORMATIF_YAS,
    yas_persentil_bul, _STANDART_NORMAL, persentil_sirasi, yas_z_skoru, bant_metni, z_durum_notu, sifir_gecerli,
    ktk3_toplamlari, BILESIK_MAKS_GUN, bilesik_z_hesapla, sporcu_z_profili, tsyt_hucre, DEGISKEN_YONU,
    degisken_yonu, SAYIM_DUSUK_IYI, _yaprak_testler, _COCUK_BATARYA_TESTLERI, NORMATIF_KAPSAM, orneklem_uygun,
    orneklem_bransi, orneklem_karsilastir, _orneklem_sayi, orneklem_notlari, orneklem_disi_metni,
    orneklem_tablosu, normatif_degerlendir, SPORCU_DOSYA, OTURUM_ADI_KOLON, META_KOLONLAR, TEST_DOSYA,
    turetilmis_degerler)


# ════════════════════════════════════════════════════════════
# TESTE ÖZGÜ KATEGORİK NORMATİF DEĞERLER
# Format: "Test Adı › Değişken" → cinsiyet → kategori → (min, max)
# Jenerik değişken adlarının (Deneme 1 (cm) vb.) testler arası
# karışmasını engeller. NORMATIF_YAS'tan sonra, NORMATIF'ten önce bakılır.
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# YAŞA GÖRE EŞİK (KRİTER) NORMLARI — FitnessGram Sağlıklı Uygunluk Zonu (HFZ)
# Format: "Test Adı › Değişken" → yaş → cinsiyet → (alt, tavan) KAYNAĞIN BİRİMİYLE (inç ya da tekrar).
# tavan = ölçümün tavanı (ör. Trunk Lift 12 inç), BAŞARISIZLIK EŞİĞİ DEĞİL: üstündeki değer tavana kırpılır
# ve tavandaki değerle aynı kategoriyi alır. Tavanı olmayan ölçümde None.
# Persentil değildir: değer eşiğin üstündeyse "Sağlıklı Uygunluk Zonu", altındaysa "Gelişim Gerekli".
# NORMATIF_YAS persentil tablosudur (Z skoru, P5-P95 bantları); eşik orada tutulmaz.
# TEK KAYNAK: protokol metnindeki HFZ bölümü bu tablodan üretilir (_katalog_hfz_ekle) — elle yazılmaz.
# Değerler: The Cooper Institute, FitnessGram HFZ tabloları (Test Administration Manual 4. baskı, Tablo 9.1-9.2;
# alt sınırlar Healthy Fitness Zone Standards v10 ile aynı). 17 = "17+" satırı. üst None = alt sınırın üstü HFZ.
# ════════════════════════════════════════════════════════════
from olcut.esik import (   # Bölme Aşama 2: olcut/esik.py
    _hfz_tablo, _HFZ_KAYNAK, _HFZ_BACK_SAVER, NORMATIF_ESIK_YAS, HFZ_KATEGORI, _hfz_cm, esik_degerlendir,
    _hfz_deger_metni, hfz_metni, _katalog_hfz_ekle)


from olcut.katalog_islemleri import (   # Bölme Aşama 2: olcut/katalog_islemleri.py
    TEST_KATALOGU, BOLUM_BASLIKLARI, _BOLUM_SONU, _uygulama_araligi, protokol_formatla, protokol_ozet_cikar,
    YON_BATARYA_KATEGORILERI, YON_BATARYA_DISI, YON_BATARYA_KISA, katalog_testleri, katalog_bataryalari,
    batarya_kisa, test_kisa, batarya_yas_araligi, TEST_TAKMA_AD, kanonik_test, test_tablosu_duzelt,
    test_raflari, test_izi_parcalari, test_izi, test_yolu, test_bilgisi, TEST_BILESENLERI, TEST_NITELIKLERI,
    TEST_NITELIK_KURALLARI, test_niteligi, test_bileseni, test_etiketli, sira_uyarilari, TEST_ETIKET_KURALLARI,
    test_etiketleri, _ARA_HARF, ara_katla, _kelime_eslesir, TEST_ARAMA_DURAK, TEST_ARAMA_KISA, _bitisik_eslesir,
    arama_branslari, _brans_gecer, arama_brans_cezasi, test_ara, CALISMA_ANAHTAR, ONERI_IZ_SINIRI,
    NITELIK_KARTLARI, NITELIK_DIGER, NITELIK_KARTI, nitelik_karti, nitelik_testleri)


# ════════════════════════════════════════════════════════════
# YAŞ BAZLI NORMATİF DEĞERLER (PERSENTİL SİSTEMİ)
# Kaynak: Tomkinson et al. (2018) BJSM — 2.779.165 Eurofit performansı
# Format: "Test Adı › Değişken" → yaş → cinsiyet → persentiller
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# TSYT NORMLARI (Paket 9) — otomatik üretildi; ELLE DÜZENLEMEYİN
# Kaynak: Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3.
# 55 tablo (11 ölçüm × 7-11 yaş), her tabloda erkek/kadın × 4 doğum çeyreği × 19 persentil.
# Okuma: pdftotext -layout ve -raw ile iki bağımsız ayrıştırma, 8.360 değer birebir aynı; bir tablo
# (9.4.19) sayfa görüntüsüyle karşılaştırıldı. 440 sütunun tümü tekdüze; ortalamalar P25-P75 içinde.
# Saklama: ham değer sırası (P5 = en küçük değer). Kitap persentilleri performans yönünde verir
# ("95" = en iyi); düşük-iyi testlerde (çeviklik, 20 m) ham P(100-k) = kitabın k satırı.
# 'ceyrekler': {yaş: {cinsiyet: {çeyrek: bantlar}}} — 1. çeyrek = Ocak-Mart doğumlu (bkz. tsyt_hucre).
# 'yaslar': dört çeyreğin n ağırlıklı ortalaması (doğum tarihi bilinmediğinde; ekranda belirtilir).
# 'ceyrek_n': ağırlıklar — kitabın frekans tablosundaki 'Toplam' satırı (başlıktaki n'de 9.1.7'de yazım
# hatası var: 10.470 / frekans 20.470).
# ════════════════════════════════════════════════════════════
from veri.normlar_tsyt import TSYT_KAYNAK, TSYT_NORMLARI   # Bölme Aşama 1: veri/normlar_tsyt.py



# ════════════════════════════════════════════════════════════
# Z-SKOR MOTORU (Paket 3) — persentil tabanlı
# ------------------------------------------------------------
# Ham skordan (değer − ortalama) / SD ile Z ALINMAZ: yaş bazlı normlar
# yalnızca persentil olarak verilir ve çoğu dağılım normal değildir
# (ör. KTK3+ göz-el koordinasyonunda 6-8 yaşta taban etkisi; 6 yaş kızda
# P5 = P25 = P50 = 0). Bunun yerine:
#   1) Değerin persentil sırası, bantlar arasında doğrusal ara değerle
#      bulunur (en alt bandın altı ve en üst bandın üstü sınırlanır).
#   2) Z = ters normal(persentil). Bu bir sıra dönüşümüdür; çarpıklıktan
#      etkilenmez.
# Performans yönü: "düşük daha iyi" testlerde Z'nin işareti çevrilir;
# böylece her testte + = akranlarından iyi. Antropometrik (nötr) ölçüler
# tanımlayıcıdır, işareti çevrilmez ve bileşik skorlara girmez.
# ════════════════════════════════════════════════════════════
from statistics import NormalDist



from veri.brans_profilleri import BILESIK_Z, BRANS_GRUBU_PROFILLERI   # Bölme Aşama 1: veri/brans_profilleri.py


# ════════════════════════════════════════════════════════════
# BRANŞ GRUBU PROFİLLERİ (Paket 4) — Opstoel ve ark. (2015)
# ------------------------------------------------------------
# Kaynak: Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B.,
# Philippaerts, R., Visscher, C., & Lenoir, M. (2015). PLoS ONE, 10(5), e0126282.
# Tablo 1-3, grup satırları (ortalama, SD). Örneklem: 620 Flaman çocuk, 9-11 yaş
# (10.30 ± 0.88), 347 erkek / 273 kız; değerler cinsiyet ve yaş KARIŞIK grup
# ortalamalarıdır. Analizde kullanılan 6 grup alındı (Atletizm ve Diğer
# sporlar makalede yalnızca betimsel).
# Doğrulama: (1) PDF metninden grup-satır okuması, (2) PDF metninden değişken-sütun
# okuması, (3) makalenin tablo görsellerinden okuma — 102 hücrenin üçünde de
# birebir aynı; ek olarak her çok branşlı grubun ortalaması, branş satırlarının
# n ağırlıklı ortalamasıyla 17 değişkende yuvarlama payı içinde tutuyor.
# ════════════════════════════════════════════════════════════


def sporcu_fsc_profili(df_test, sporcu):
    """
    Sporcunun Opstoel (2015) değişkenlerine karşılık gelen ham değerleri.
    Her eşleşen test için EN SON kayıt kullanılır; boy/kilo sporcu profilinden gelir.
    Dönen: {"degerler": {kod: {"deger", "tarih", "kaynak"}}, "eksik": [kod], "eslesmeyen": [kod]}
    Paket 5'teki branş grubu eşleştirmesi bu fonksiyonun çıktısını kullanır.
    """
    tanim = BRANS_GRUBU_PROFILLERI["degiskenler"]
    sonuc = {"degerler": {}, "eksik": [], "eslesmeyen": [k for k, t in tanim.items() if not t["eslesme"]]}

    bilgi = {}
    if os.path.exists(SPORCU_DOSYA):
        df_sp = pd.read_excel(SPORCU_DOSYA)
        esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
        if not esl.empty:
            bilgi = esl.iloc[0].to_dict()

    df_s = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" in df_s.columns:
        df_s = df_s.sort_values("Tarih_dt", na_position="first")

    for kod, t in tanim.items():
        e = t["eslesme"]
        if not e:
            continue
        if e["kaynak"] in ("profil", "profil_vki"):
            boy = guvenli_float(bilgi.get("Boy (cm)", 0)) if _girildi(bilgi.get("Boy (cm)")) else 0
            kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
            if e["kaynak"] == "profil":
                v = boy if e["alan"] == "Boy (cm)" else kilo
            else:
                v = round(kilo / (boy / 100) ** 2, 2) if boy > 0 and kilo > 0 else 0
            if v > 0:
                sonuc["degerler"][kod] = {"deger": v, "tarih": None, "kaynak": "Sporcu profili"}
            else:
                sonuc["eksik"].append(kod)
            continue

        son = None
        for _, satir in df_s[df_s["Test"] == e["test"]].iterrows():
            vals = satir.to_dict()
            for k_t, v_t in ktk3_toplamlari(e["test"], vals).items():
                if not _girildi(vals.get(k_t)):
                    vals[k_t] = v_t
            sayilar = []
            for d in e["degiskenler"]:
                if _girildi(vals.get(d)):
                    try:
                        sayilar.append(float(vals.get(d)))
                    except (TypeError, ValueError):
                        pass
            if not sayilar:
                continue
            v = sayilar[0] if e["birlestir"] == "tek" else max(sayilar)
            test_yasi = vals.get("Test Yaşı")
            son = {"deger": v, "tarih": satir.get("Tarih", ""), "kaynak": e["test"],
                   "test_yasi": guvenli_float(test_yasi) if _girildi(test_yasi) else None}
        if son is None:
            sonuc["eksik"].append(kod)
        else:
            sonuc["degerler"][kod] = son
    return sonuc


# ════════════════════════════════════════════════════════════
# BRANŞ GRUBU EŞLEŞTİRMESİ (Paket 5)
# ------------------------------------------------------------
# Yöntem: her performans değişkeninde (çocuk − grup ortalaması) / havuzlanmış
# grup içi SD (altı grubun ortak SD'si); her grup için bu standart farkların
# karelerinin ortalamasının karekökü (ortalama standart uzaklık).
# Küçük uzaklık = profil o gruba yakın.
# Neden havuzlanmış SD: her grubun kendi SD'siyle bölmek, SD'si büyük grupları
# (ör. jimnastik) sistematik olarak "yakın" gösteriyordu — simülasyonda top
# sporlarından gelen çocukların çoğu jimnastiğe düşüyordu.
# Sınırlar (ekranda her zaman yazılır):
#  • Opstoel örneklemi 9-11 yaş: bu yaş dışında karşılaştırma yapılmaz.
#  • Grup değerleri erkek ve kız karışık; grupların cinsiyet dağılımı
#    yayımlanmadığı için cinsiyet düzeltilemez.
#  • Opstoel'in diskriminant fonksiyon katsayıları yayımlanmadı; bu yöntem
#    onların sınıflayıcısı değildir, doğruluğu ayrıca test edilmedi.
#  • Antropometri (boy, kilo, VKİ, oturma yüksekliği) eşleştirmeye girmez,
#    yalnızca tanımlayıcı gösterilir (sabit karar 7).
# ════════════════════════════════════════════════════════════
ESLESTIRME_YAS_ARALIGI = (9, 11)
ESLESTIRME_EN_AZ_DEGISKEN = 6
ESLESTIRME_DEGISKENLERI = [k for k, t in BRANS_GRUBU_PROFILLERI["degiskenler"].items()
                           if t["tur"] != "antropometri" and t["eslesme"]]


def _havuz_sd(kod):
    """Altı grubun grup içi SD'lerinin n ağırlıklı havuzu."""
    gruplar = BRANS_GRUBU_PROFILLERI["gruplar"]
    pay = sum((gruplar[g]["n"] - 1) * BRANS_GRUBU_PROFILLERI["degerler"][g][kod][1] ** 2 for g in gruplar)
    payda = sum(gruplar[g]["n"] - 1 for g in gruplar)
    return (pay / payda) ** 0.5


ESLESTIRME_HAVUZ_SD = {k: round(_havuz_sd(k), 3) for k in ESLESTIRME_DEGISKENLERI}

# Yöntemin beklenen ayırt ediciliği (simülasyon, 6 × 3000 sanal çocuk): çocuklar
# kendi grubunun ortalama ve SD'sinden normal ve bağımsız dağılımla üretildi;
# 11 değişkenin tamamı kullanıldı. Değişkenler arası korelasyon bilinmediği için
# gerçek doğruluk farklı olabilir.
ESLESTIRME_SIMULASYON = {"ilk_sira": 29, "ilk_uc": 67, "sans_ilk": 17, "sans_ilk_uc": 50}

from veri.metinler import (   # Bölme Aşama 1: veri/metinler.py
    GUVEN_DUZEYLERI, ILGI_KAYNAKLARI, ILGI_MADDELERI, VELI_TEST_GRUBU, VELI_YORUMLARI, KAYNAKCA, DUNYA_REKORU,
    ACIKLAMALAR, TERIM_SOZLUGU, TERIM_ARAMA)

# PQ ve MQ açıklaması tek kaynakta: ACIKLAMALAR["PQ"], ACIKLAMALAR["MQ"] (Paket 8).


def brans_grubu_eslestir(fsc_profil, sporcu_yas):
    """
    Dönen: {"uygun": bool, "neden": str|None, "siralama": [(grup, uzaklik)],
            "kullanilan": [kod], "dislanan_yas": [kod], "katki": {grup: {kod: z}}}
    """
    sonuc = {"uygun": False, "neden": None, "siralama": [], "kullanilan": [],
             "dislanan_yas": [], "katki": {}}
    try:
        yas = float(sporcu_yas)
    except (TypeError, ValueError):
        sonuc["neden"] = "Sporcu profilinde yaş yok."
        return sonuc
    alt, ust = ESLESTIRME_YAS_ARALIGI
    if not (alt <= int(yas) <= ust):
        sonuc["neden"] = (f"Karşılaştırma yapılamaz: branş grubu profilleri {alt}-{ust} yaş çocuklardan "
                          f"elde edildi (Opstoel ve ark., 2015); sporcu {int(yas)} yaşında.")
        return sonuc

    degerler = {}
    for kod in ESLESTIRME_DEGISKENLERI:
        d = fsc_profil["degerler"].get(kod)
        if not d:
            continue
        ty = d.get("test_yasi")
        if ty is not None and not (alt <= int(ty) <= ust):
            sonuc["dislanan_yas"].append(kod)   # ölçüm 9-11 yaş dışında yapılmış
            continue
        degerler[kod] = d["deger"]
    sonuc["kullanilan"] = list(degerler)
    if len(degerler) < ESLESTIRME_EN_AZ_DEGISKEN:
        sonuc["neden"] = (f"Karşılaştırma için en az {ESLESTIRME_EN_AZ_DEGISKEN} performans testi gerekli; "
                          f"şu an {len(degerler)} test var.")
        return sonuc

    for grup, tablo in BRANS_GRUBU_PROFILLERI["degerler"].items():
        zler = {}
        for kod, x in degerler.items():
            ort = tablo[kod][0]
            z = (x - ort) / ESLESTIRME_HAVUZ_SD[kod]
            # Yön: + = gruptan iyi (düşük-iyi değişkenlerde işaret çevrilir); uzaklığı etkilemez
            if BRANS_GRUBU_PROFILLERI["degiskenler"][kod]["dusuk_iyi"]:
                z = -z
            zler[kod] = round(z, 2)
        uzaklik = (sum(z * z for z in zler.values()) / len(zler)) ** 0.5
        sonuc["siralama"].append((grup, round(uzaklik, 2)))
        sonuc["katki"][grup] = zler
    sonuc["siralama"].sort(key=lambda g: g[1])
    sonuc["uygun"] = True
    return sonuc


# ════════════════════════════════════════════════════════════
# İLGİ ANKETİ (Paket 6) — UYGULAMANIN KENDİ ANKETİ
# ------------------------------------------------------------
# Bu anket Flaman Spor Pusulası'nın "I LIKE" aracı DEĞİLDİR. I LIKE'ın
# soruları, soru sayısı ve puanlaması yayımlanmamış; araç lisanslı bir web
# uygulaması (SportaMundi / Sport Vlaanderen).
# Yapı: altı branş grubunun her biri için, o grubun hareket ve beceri
# içeriğini anlatan 4 madde (madde havuzu: ILGI_KAYNAKLARI'ndaki hakemli
# kaynakların taranmasıyla). 5'li yüz ölçeği + "bilmiyorum / hiç yapmadım".
# Grup ilgi puanı = yanıtlanan maddelerin ortalaması (en az 2 madde).
# Madde kodları "I2-" önekli: sürüm 1'in "I-" kodlu 12 maddesi farklı anlamdaydı;
# kod yeniden kullanılmadı (sabit karar: adlar veri anahtarıdır). Sürüm 1 kayıtları
# yeni puanlamaya girmez; anketin yeniden doldurulması gerekir.
# İlgi ve fiziksel profil TEK SKORDA BİRLEŞTİRİLMEZ (sabit karar 4).
# ════════════════════════════════════════════════════════════
ILGI_DOSYA = "ilgi_anketi.xlsx"
ILGI_ANKET_ADI = "Uygulamanın kendi ilgi anketi (sürüm 2, 24 madde)"
ILGI_UYARI = ("Bu, uygulamanın kendi anketidir; Flaman Spor Pusulası'nın doğrulanmış I LIKE aracı "
              "değildir. Geçerlik ve güvenirlik çalışması henüz yapılmamıştır.")
ILGI_OLCEK = {1: "😢 Hiç sevmiyorum", 2: "🙁 Pek sevmiyorum", 3: "😐 Kararsızım",
              4: "🙂 Seviyorum", 5: "😄 Çok seviyorum", 0: "❔ Bilmiyorum / hiç yapmadım"}
ILGI_EN_AZ_MADDE = 2      # grup puanı için en az bu kadar madde yanıtlanmalı
ILGI_SEVIYOR_ESIGI = 3.5  # bu ve üstü "seviyor" penceresine girer

ILGI_TARANAN_SAYISI = 14   # özeti okunan hakemli kaynak (Opstoel 2015 hariç)

ILGI_TERCIHLERI = [
    ("T-TAKIM", "Takımla oynamak", "Tek başına yapmak"),
    ("T-YER", "İçeride (salonda)", "Dışarıda (açık havada)"),
    ("T-TEMAS", "Rakiple temaslı", "Rakibe dokunmadan"),
    ("T-MUZIK", "Müzikle", "Müziksiz"),
]

ILGI_HAKKINDA = (
    "**Bu anket hakkında**\n\n"
    "Bu anketin maddeleri bu uygulama için yazılmıştır; doğrulanmış bir ölçek değildir.\n\n"
    "Maddeler, Opstoel ve ark. (2015) tarafından tanımlanan altı branş grubunun hareket içeriği esas "
    f"alınarak, {ILGI_TARANAN_SAYISI} hakemli kaynağın taranmasıyla oluşturulan bir madde havuzundan "
    "seçilmiştir. Hazırlık yapay zeka desteğiyle yapılmış, araştırmacı tarafından gözden geçirilmiştir.\n\n"
    "Geçerlik ve güvenirlik çalışması henüz yapılmamıştır. Uygulama üzerinden toplanacak verilerle madde "
    "analizi, test–tekrar test güvenirliği ve anketin branş seçimiyle ilişkisi incelenecektir. Bu çalışma "
    "tamamlanana kadar anketin çıktıları bağlayıcı bir değerlendirme değil, yönlendirici bilgi olarak ele "
    "alınmalıdır.\n\n"
    "Çalışma Prof. Dr. Ömer Şenel ve Prof. Dr. Cengiz Akarçeşme danışmanlığında yürütülmektedir."
)


def ilgi_son_anket(sporcu):
    """Sporcunun en son ilgi anketi kaydı (sözlük) ya da None."""
    if not os.path.exists(ILGI_DOSYA):
        return None
    df_i = pd.read_excel(ILGI_DOSYA)
    df_i = df_i[df_i["Sporcu"] == sporcu]
    if df_i.empty:
        return None
    df_i = df_i.assign(_t=pd.to_datetime(df_i["Tarih"], format="%d.%m.%Y", errors="coerce"))
    return df_i.sort_values("_t", na_position="first").iloc[-1].to_dict()


def ilgi_grup_puanlari(kayit):
    """Grup başına ilgi puanı (1-5) ya da bilinmiyorsa None. 0 = bilmiyorum, ortalamaya girmez."""
    puanlar = {}
    for grup, maddeler in ILGI_MADDELERI.items():
        yanitlar = []
        for kod, _, _ in maddeler:
            v = kayit.get(kod) if kayit else None
            try:
                v = int(float(v))
            except (TypeError, ValueError):
                continue
            if 1 <= v <= 5:
                yanitlar.append(v)
        puanlar[grup] = (round(sum(yanitlar) / len(yanitlar), 1)
                         if len(yanitlar) >= ILGI_EN_AZ_MADDE else None)
    return puanlar


def ilgi_etiketi(p):
    if p is None:
        return "Bilinmiyor"
    if p >= 4.5:
        return "Çok seviyor"
    if p >= 3.5:
        return "Seviyor"
    if p >= 2.5:
        return "Kararsız"
    return "Pek sevmiyor"


def ilgi_fiziksel_pencereler(esl, ilgi_puanlari):
    """
    İlgi ve fiziksel profil AYRI pencereler olarak döner; tek skor üretilmez (sabit karar 4).
    Dönen: {"seviyor": [grup], "fiziksel": [grup], "kesisim": [grup],
            "yalniz_ilgi": [grup], "yalniz_fiziksel": [grup], "bilinmeyen": [grup]}
    """
    seviyor = sorted(g for g, p in ilgi_puanlari.items() if p is not None and p >= ILGI_SEVIYOR_ESIGI)
    fiziksel = sorted(g for g, _ in esl["siralama"][:3]) if esl and esl.get("uygun") else []
    kesisim = sorted(set(seviyor) & set(fiziksel))
    return {
        "seviyor": seviyor, "fiziksel": fiziksel, "kesisim": kesisim,
        "yalniz_ilgi": sorted(set(seviyor) - set(fiziksel)),
        "yalniz_fiziksel": sorted(set(fiziksel) - set(seviyor)),
        "bilinmeyen": sorted(g for g, p in ilgi_puanlari.items() if p is None),
    }


# ════════════════════════════════════════════════════════════
# PAKET 7 — PANEL ARAYÜZÜ, VELİ RAPORU, ANTRENÖR RAPORU
# ------------------------------------------------------------
# (1) Haftalık antrenman süresi sporcu profiline kaydedilir: güven düzeyini
#     belirleyen tek değişken bu; raporda neye dayandığı (değer + kayıt tarihi)
#     yazılır.
# (2) İlgi anketi sporcu girişi akışındadır; test kaydından bağımsız doldurulur.
# (3) Branş grubu profili radara ikinci katman olarak biner: grup ortalaması,
#     sporcunun kendi Z'sinin geldiği norm tablosundan (aynı test, aynı yaş,
#     aynı cinsiyet hücresi) geçirilerek Z'ye çevrilir. Normu olmayan, protokolü
#     eşleşmeyen ya da antropometrik değişkenler radara girmez.
# ════════════════════════════════════════════════════════════
import html as _html

ANTRENMAN_KOLON = "Haftalık Antrenman"
ANTRENMAN_TARIH_KOLON = "Antrenman Bilgisi Tarihi"
ANTRENMAN_SECENEKLERI = ["Bilinmiyor"] + list(GUVEN_DUZEYLERI.keys())
ANTRENMAN_YARDIM = ("Haftalık organize (kulüp/okul takımı) antrenman süresi. Branşa yönlendirmedeki güven düzeyi "
                    "yalnızca buna göre belirlenir (Opstoel ve ark., 2015).")


def sporcu_profil_bilgisi(sporcu):
    """sporcular.xlsx'teki satır (sözlük) ya da boş sözlük."""
    if not os.path.exists(SPORCU_DOSYA):
        return {}
    df_sp = pd.read_excel(SPORCU_DOSYA)
    esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
    return esl.iloc[0].to_dict() if not esl.empty else {}


def sporcu_antrenman(bilgi):
    """(seçenek, kayıt tarihi metni) — kayıt yoksa ("Bilinmiyor", "")."""
    v = bilgi.get(ANTRENMAN_KOLON)
    v = str(v).strip() if _girildi(v) else "Bilinmiyor"
    if v not in ANTRENMAN_SECENEKLERI:
        v = "Bilinmiyor"
    t = bilgi.get(ANTRENMAN_TARIH_KOLON)
    return v, (str(t).strip() if _girildi(t) else "")


def sporcu_antrenman_kaydet(sporcu, secenek):
    """Profildeki haftalık antrenman süresini ve kayıt tarihini günceller. Başarılıysa True."""
    if not os.path.exists(SPORCU_DOSYA):
        return False
    df_sp = pd.read_excel(SPORCU_DOSYA)
    maske = df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu
    if not maske.any():
        return False
    for kolon in (ANTRENMAN_KOLON, ANTRENMAN_TARIH_KOLON):
        if kolon not in df_sp.columns:
            df_sp[kolon] = ""
        df_sp[kolon] = df_sp[kolon].astype(object)
    df_sp.loc[maske, ANTRENMAN_KOLON] = secenek
    df_sp.loc[maske, ANTRENMAN_TARIH_KOLON] = date.today().strftime("%d.%m.%Y")
    df_sp.to_excel(SPORCU_DOSYA, index=False)
    return True


def ilgi_anketi_formu(sporcu):
    """İlgi anketi formu (Sporcu Girişi akışında). Kaydedilen ya da en son kayıt döner."""
    ilgi_kayit = ilgi_son_anket(sporcu)
    with st.expander("ℹ️ Bu anket hakkında"):
        st.markdown(ILGI_HAKKINDA)
        st.caption("Madde havuzunun kaynakları:")
        for k_kod, k_metin in ILGI_KAYNAKLARI.items():
            st.caption(f"[{k_kod}] {k_metin}")
    if ilgi_kayit:
        st.caption(f"Son anket: {ilgi_kayit.get('Tarih', '')} — yeni yanıtlar yeni kayıt olarak eklenir; "
                   "raporlar en son kaydı kullanır.")
    st.warning("⚠️ " + ILGI_UYARI)
    st.caption("Çocuk soruları kendisi yanıtlar; okuyamıyorsa yetişkin soruyu okur ama yanıtı "
               "yönlendirmez. Bir etkinliği hiç yapmadıysa \"Bilmiyorum / hiç yapmadım\" seçilir.")
    with st.form(key=f"ilgi_form_{sporcu}"):
        ilgi_tarih = st.date_input("Anket tarihi", value=date.today(), key=f"ilgi_tarih_{sporcu}")
        yeni = {}
        st.markdown("**Bunu yapmayı ne kadar seversin?**")
        # Maddeler gruplara göre değil, karışık sırayla sorulur (grup etkisini azaltmak için)
        tum_maddeler = [m for grup_m in ILGI_MADDELERI.values() for m in grup_m]
        sira_m = [tum_maddeler[(i * 7) % len(tum_maddeler)] for i in range(len(tum_maddeler))]
        for kod, metin, _ in sira_m:
            onceki = ilgi_kayit.get(kod) if ilgi_kayit else None
            try:
                onceki = int(float(onceki))
            except (TypeError, ValueError):
                onceki = 0
            secenekler = [1, 2, 3, 4, 5, 0]
            yeni[kod] = st.radio(metin, secenekler,
                                 index=secenekler.index(onceki) if onceki in secenekler else 5,
                                 format_func=lambda x: ILGI_OLCEK[x], horizontal=True,
                                 key=f"{kod}_{sporcu}")
        st.markdown("**Hangisini daha çok seversin?** (yalnızca bilgi için, puana girmez)")
        for kod, a_secenek, b_secenek in ILGI_TERCIHLERI:
            tercih_ops = [a_secenek, "İkisi de / fark etmez", b_secenek]
            onceki_t = ilgi_kayit.get(kod) if ilgi_kayit else None
            yeni[kod] = st.radio(f"{a_secenek} mi, {b_secenek.lower()} mı?", tercih_ops,
                                 index=tercih_ops.index(onceki_t) if onceki_t in tercih_ops else 1,
                                 horizontal=True, key=f"{kod}_{sporcu}")
        if st.form_submit_button("💾 Anketi kaydet"):
            kayit_i = {"Sporcu": sporcu, "Tarih": ilgi_tarih.strftime("%d.%m.%Y"),
                       "Anket": ILGI_ANKET_ADI, **yeni}
            if os.path.exists(ILGI_DOSYA):
                df_i_tum = pd.concat([pd.read_excel(ILGI_DOSYA), pd.DataFrame([kayit_i])], ignore_index=True)
            else:
                df_i_tum = pd.DataFrame([kayit_i])
            df_i_tum.to_excel(ILGI_DOSYA, index=False)
            st.success("✅ İlgi anketi kaydedildi.")
            ilgi_kayit = kayit_i
    return ilgi_kayit


# ── Branş grubu katmanı: hangi Opstoel değişkeni hangi norm tablosundan Z'ye çevrilir ──
def _grup_radar_norm_anahtari(kod):
    """(test, norm değişkeni) ya da (None, neden). Eşleştirme Paket 4 kuralıyla aynıdır."""
    t = BRANS_GRUBU_PROFILLERI["degiskenler"][kod]
    if t["tur"] == "antropometri":
        return None, "antropometrik — tanımlayıcı veri, performans radarına girmez"
    e = t["eslesme"]
    if not e:
        return None, "protokol eşleşmedi"
    anahtarlar = [f"{e['test']} › {d}" for d in e["degiskenler"] if f"{e['test']} › {d}" in NORMATIF_YAS]
    if not anahtarlar:
        return None, "yaş/cinsiyet normu yok"
    ilk = NORMATIF_YAS[anahtarlar[0]]["yaslar"]
    if any(NORMATIF_YAS[a]["yaslar"] != ilk for a in anahtarlar[1:]):
        return None, "denemelerin normları birbirinden farklı"
    return (e["test"], anahtarlar[0].split(" › ", 1)[1]), None


GRUP_RADAR_ESLESME = {k: _grup_radar_norm_anahtari(k) for k in BRANS_GRUBU_PROFILLERI["degiskenler"]}
GRUP_RENKLERI = palet("acik")["seri"]          # rapor radarı (kâğıt: açık palet); uygulama grafiği grafik_renk()


def grup_radar_katmani(df_test, sporcu, gruplar):
    """
    Radarın ortak eksenleri: sporcunun Z'si ve seçilen grupların Z'si aynı norm hücresinden.
    Dönen: {"uygun", "neden", "eksenler": [{kod, ad, test, degisken, yas, deger, z, persentil,
            durum, gruplar: {grup: {ort, z, persentil, durum}}}], "cikarilan": [(ad, neden)],
            "cinsiyet"}
    """
    tanim = BRANS_GRUBU_PROFILLERI["degiskenler"]
    sonuc = {"uygun": False, "neden": None, "eksenler": [], "cikarilan": [], "cinsiyet": ""}
    bilgi = sporcu_profil_bilgisi(sporcu)
    cins = str(bilgi.get("Cinsiyet", "")).strip()
    sonuc["cinsiyet"] = cins
    if cins not in ("Erkek", "Kadın"):
        sonuc["neden"] = "Sporcu profilinde cinsiyet yok."
        return sonuc
    alt, ust = ESLESTIRME_YAS_ARALIGI
    try:
        profil_yas = int(float(bilgi.get("Yaş")))
    except (TypeError, ValueError):
        profil_yas = None
    if profil_yas is not None and not (alt <= profil_yas <= ust):
        sonuc["neden"] = (f"branş grubu profilleri {alt}-{ust} yaş çocuklardan elde edildi (Opstoel ve ark., 2015); "
                          f"sporcu {profil_yas} yaşında.")
        return sonuc
    fsc = sporcu_fsc_profili(df_test, sporcu)
    for kod, (anahtar, neden) in GRUP_RADAR_ESLESME.items():
        ad = tanim[kod]["ad"]
        if tanim[kod]["tur"] == "antropometri":
            continue   # tek satırlık notla belirtilir
        if anahtar is None:
            sonuc["cikarilan"].append((ad, neden))
            continue
        d = fsc["degerler"].get(kod)
        if not d:
            sonuc["cikarilan"].append((ad, "sporcuda ölçüm yok"))
            continue
        yas = d.get("test_yasi")
        if yas is None and _girildi(bilgi.get("Yaş")):
            yas = guvenli_float(bilgi.get("Yaş"))
        if yas is None or not (alt <= int(yas) <= ust):
            sonuc["cikarilan"].append((ad, f"ölçüm {alt}-{ust} yaş dışında (grup profilleri {alt}-{ust} yaş)"))
            continue
        test, degisken = anahtar
        zs = yas_z_skoru(test, degisken, yas, cins, d["deger"])
        if not zs or zs["z_performans"] is None:
            sonuc["cikarilan"].append((ad, "sporcunun değeri Z'ye çevrilemedi"))
            continue
        gz_hepsi, cevrilemedi = {}, False
        for g in gruplar:
            ort = BRANS_GRUBU_PROFILLERI["degerler"][g][kod][0]
            gz = yas_z_skoru(test, degisken, yas, cins, ort)
            if not gz or gz["z_performans"] is None:
                cevrilemedi = True
                break
            gz_hepsi[g] = {"ort": ort, "z": gz["z_performans"], "persentil": gz["persentil_performans"], "durum": gz["durum"]}
        if cevrilemedi:
            sonuc["cikarilan"].append((ad, "grup ortalaması Z'ye çevrilemedi"))
            continue
        sonuc["eksenler"].append({"kod": kod, "ad": ad, "test": test, "degisken": degisken, "yas": int(yas),
                                  "deger": d["deger"], "z": zs["z_performans"], "persentil": zs["persentil_performans"],
                                  "durum": zs["durum"], "kullanilan_yas": zs["kullanilan_yas"],
                                  "gruplar": gz_hepsi})
    if len(sonuc["eksenler"]) < 3:
        sonuc["neden"] = (f"Grup katmanı için sporcuda ve grupta ortak, Z'ye çevrilebilen en az 3 değişken gerekli; "
                          f"şu an {len(sonuc['eksenler'])}.")
        return sonuc
    sonuc["uygun"] = True
    return sonuc


GRUP_KATMANI_NOTU = (
    "Grup çizgileri, Opstoel ve ark. (2015) grup ortalamasının sporcunun kendi norm hücresindeki (aynı test, "
    "aynı yaş, aynı cinsiyet) Z'sidir; yani \"o gruptaki ortalama bir çocuk bu sporcunun akranları arasında "
    "nerede durur\". Grup ortalamaları erkek-kız karışık olduğundan cinsiyet farkı düzeltilmemiştir. "
    "Ortalamanın Z'si, grup üyelerinin Z'lerinin ortalamasıyla aynı şey değildir.")


# Raporlar (veli/antrenör, yazdırılır, dosya olarak verilir) bağımsız belgedir: tema yok, her zaman açık palet.
_RAPOR_RENK = palet("acik")["renk"]
_RAPOR_VURGU = palet("acik")["vurgu"]


# ── Rapor için bağımsız SVG radar (internet ve ek paket gerektirmez) ──
def radar_svg(eksenler, katmanlar, aralik=(-3, 3)):
    """
    eksenler: [etiket]; katmanlar: [(ad, [z], renk, kesikli)] — z değerleri aralığa sınırlanır.
    Kendi başına SVG (internet ve ek paket gerektirmez); yazdırmada da aynı görünür.
    """
    import math
    n = len(eksenler)
    gen, yuk = 760, 600
    cx, cy = gen / 2, 285
    r_max = 205
    lo, hi = aralik

    def nokta(i, z, r_ek=0.0):
        z = max(lo, min(hi, z))
        r = (z - lo) / (hi - lo) * r_max + r_ek
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * math.cos(a), cy + r * math.sin(a)

    parcalar = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {gen} {yuk}" width="100%" '
                f'style="max-width:{gen}px" role="img" aria-label="Z profili radarı" '
                f'font-family=\'{YAZI_AILESI.replace(chr(34), "")}\'>']
    for z in range(lo, hi + 1):
        if z == lo:
            continue
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (nokta(i, z) for i in range(n)))
        stil = (f'stroke="{_RAPOR_RENK["ikincil"]}" stroke-width="2"' if z == 0
                else f'stroke="{_RAPOR_RENK["cizgi"]}" stroke-width="1"')
        parcalar.append(f'<polygon points="{pts}" fill="none" {stil}/>')
    for i in range(n):
        x, y = nokta(i, hi)
        parcalar.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{_RAPOR_RENK["cizgi"]}"/>')
    for ad, zler, renk, kesikli in katmanlar:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (nokta(i, z) for i, z in enumerate(zler)))
        dolgu = 'fill="none"' if kesikli else f'fill="{renk}" fill-opacity="0.13"'
        cizgi = ' stroke-dasharray="7 4"' if kesikli else ""
        parcalar.append(f'<polygon points="{pts}" {dolgu} stroke="{renk}" stroke-width="2.4"{cizgi}/>')
        if not kesikli:
            for i, z in enumerate(zler):
                x, y = nokta(i, z)
                parcalar.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.8" fill="{renk}"/>')
    # Ölçek etiketleri: ilk eksenin hemen sağında, beyaz zeminli
    for z in (-2, 0, 2):
        x, y = nokta(0, z)
        et = "0 = akran ort." if z == 0 else f"{z:+d}"
        parcalar.append(f'<text x="{x + 5:.1f}" y="{y + 4:.1f}" font-size="10.5" fill="{_RAPOR_RENK["ikincil"]}" '
                        f'stroke="{_RAPOR_RENK["yuzey"]}" stroke-width="3" paint-order="stroke">{et}</text>')
    for i, et in enumerate(eksenler):
        lx, ly = nokta(i, hi, r_ek=16)
        anchor = "middle" if abs(lx - cx) < 25 else ("start" if lx > cx else "end")
        satirlar, satir = [], ""
        for k in str(et).split():
            if satir and len(satir) + len(k) + 1 > 24:
                satirlar.append(satir)
                satir = k
            else:
                satir = f"{satir} {k}".strip()
        satirlar.append(satir)
        if ly < cy - r_max * 0.8:
            ly -= 12 * (len(satirlar) - 1)      # üstteki etiket yukarı doğru büyür
        elif abs(ly - cy) <= r_max * 0.8:
            ly -= 6 * (len(satirlar) - 1)       # yandaki etiket ortalanır
        for j, s_ in enumerate(satirlar):
            parcalar.append(f'<text x="{lx:.1f}" y="{ly + 4 + j * 13:.1f}" font-size="11.5" fill="{_RAPOR_RENK["murekkep"]}" '
                            f'text-anchor="{anchor}">{_html.escape(s_)}</text>')
    lx = 20
    for ad, _, renk, kesikli in katmanlar:
        cizgi = ' stroke-dasharray="7 4"' if kesikli else ""
        parcalar.append(f'<line x1="{lx}" y1="{yuk - 18}" x2="{lx + 28}" y2="{yuk - 18}" stroke="{renk}" '
                        f'stroke-width="3"{cizgi}/>')
        parcalar.append(f'<text x="{lx + 34}" y="{yuk - 14}" font-size="12" fill="{_RAPOR_RENK["murekkep"]}">{_html.escape(ad)}</text>')
        lx += 52 + 7 * len(ad)
    parcalar.append("</svg>")
    return "".join(parcalar)


# ── Rapor verisi ──
def _kisa_kaynak(kaynak):
    ilk = str(kaynak).split("\n")[0].strip()
    m = re.match(r"^(.*?\(\d{4}[a-z]?\))", ilk)
    return m.group(1) if m else ilk[:80]


def z_satiri_karti(r, zb, teknik=False, not_metni=None):
    """sporcu_z_profili satırını TEK sonuç kartına çevirir (Sonuçlar sayfası ve antrenör raporu)."""
    norm = NORMATIF_YAS.get(f"{r['Test']} › {r['Değişken']}", {})
    notr = r["Tür"] != "Performans"
    kaynak = _kisa_kaynak(zb.get("kaynak", "")) + (f" · {zb['tablo']}" if zb.get("tablo") else "")
    kaynak += f" · {r['Norm yaşı']} yaş normu · ölçüm {r['Tarih']}"
    ek = ""
    if teknik:
        z_m = f"Z {r['Z']:+.2f}" + (" (nötr)" if notr else "") if r.get("Z") is not None else "Z —"
        ham = zb.get("persentil")
        ek = z_m + (f" · ham persentil P{ham:.0f}" if ham is not None else "")
        if not_metni:
            not_metni = re.sub(r" \(Z [+\-−]?\d+\.\d+\)", "", not_metni)   # Z zaten teknik satırda
    return sonuc_karti_html(f"{r['Test']} — {r['Değişken']}", r["Değer"], norm.get("birim", ""),
                            r.get("Kategori") or None, notr=notr, persentil=r.get("Performans persentili"),
                            kaynak=kaynak, notlar=[not_metni if not_metni is not None else r.get("Not", "")],
                            ek=ek)


def _brans_ornekleri(grup):
    """Opstoel grubundaki branşlar, sayılar çıkarılarak (ör. 'basketbol, korfbol, futbol, voleybol')."""
    adlar = re.sub(r"\s*\(\d+\)", "", BRANS_GRUBU_PROFILLERI["gruplar"][grup]["branslar"]).split(", ")
    return ", ".join(a for a in adlar if not a.startswith("diğer"))


# ════════════════════════════════════════════════════════════
# GRUP İÇİ KONUM VE GELİŞİM (Paket 36). Veri yalnız test_sonuclari.xlsx (+ cinsiyet/yaş için sporcular.xlsx).
# Koruma kuralları: n her zaman görünür; n < GRUP_KONUM_YUZDELIK_N iken yüzdelik/sıralama sözcüğü yok (yalnız
# ortalamanın altı/üstü ve konum şeridi); havuz kanonik test adıyla, aynı değişken (aynı birim), aynı cinsiyet ve
# aynı 2 yıllık yaş bandı; sporcunun kendisi havuzda kalır ve vurgulanır; başka sporcuların adı hiçbir çıktıda yok.
# ════════════════════════════════════════════════════════════
GRUP_KONUM_YUZDELIK_N = 20          # n ≥ 20: yüzdelik gösterilebilir
GRUP_KONUM_BANT_YIL = 2             # yaş bandı genişliği (yıl)
KENDI_DEGISIM_YASI = 16             # bu yaşın altında pencerenin varsayılan görünümü "Kendi değişimin"
VELI_KONUM_EN_AZ_YAS = 11           # veli raporunda konum bölümü: yaş ≥ 11 ve n ≥ GRUP_KONUM_YUZDELIK_N
VELI_KONUM_METNI = ("Bu değer aynı yaş bandı ve cinsiyetteki n={n} çocuğun ölçümleriyle karşılaştırılmıştır; gelişim "
                    "hızı bireyler arasında farklıdır, tek ölçüm sporcu yeteneğini belirlemez.")
KONUM_YETERSIZ_METNI = "Yeterli karşılaştırma verisi yok."
# Paket 37: veli raporunda çeyrek/yüzdelik/sıra dili yok. Havuzun P10–P90 aralığı ("çocukların çoğu", ~%80'i) ve
# çocuğun bu aralığa göre yeri anlatılır. P10/P90: sıralı değerlerde doğrusal ara değer (numpy "linear" ile aynı).
VELI_ARALIK_YUZDELIK = (10, 90)
# Paket 38b: özne cinsiyetli ("Bu yaştaki erkek çocukların çoğu …"); yetişkinde "sporcuların". Yer cümlesi kısa;
# altında her zaman aynı not (aralık dışı bir sorun değildir).
VELI_ARALIK_METNI = "Bu yaştaki {kim} çoğu {a}–{b} {birim} arasında."
VELI_ARALIK_KIM = {("Erkek", False): "erkek çocukların", ("Kadın", False): "kız çocukların",
                   ("Erkek", True): "erkek sporcuların", ("Kadın", True): "kadın sporcuların"}
VELI_ARALIK_YERI = {"icinde": "{ad} bu aralığın içinde.",
                    "altinda": "{ad} bu aralığın biraz altında.",
                    "ustunde": "{ad} bu aralığın biraz üstünde.",
                    "altinda_belirgin": "{ad} bu aralığın belirgin şekilde altında.",
                    "ustunde_belirgin": "{ad} bu aralığın belirgin şekilde üstünde.",
                    "altinda_cok": "{ad} bu aralığın çok altında.",
                    "ustunde_cok": "{ad} bu aralığın çok üstünde."}
# Paket 38f: sapmanın büyüklüğü. P10–P90 normal dağılımda ±1,2816 SD'dir; bant genişliğinden SD tahmin edilir ve
# değerin yaklaşık z'si bulunur. |z| > 1,96 (dışarıda kalan ~%5) "belirgin şekilde"; |z| > 3 (~%0,3) "çok" ve
# "Değer doğru mu?" uyarısı (yargı değil, ölçüm/kayıt denetimi çağrısı).
VELI_SAPMA_Z = (1.96, 3.0)
VELI_DOGRU_MU_BASLIK = "Değer doğru mu?"
VELI_DOGRU_MU = ("Bu sonuç aralıktan çok uzak; ölçüm ya da kayıt hatası olabilir. Değeri antrenörle birlikte "
                 "kontrol edin.")
VELI_ARALIK_NOTU ="Aralığın dışında olmak bir sorun anlamına gelmez."
VELI_YASIT_BASLIK = "Yaşıtlarına göre nerede?"
YETISKIN_YAS = 18                    # bu yaştan itibaren veli raporu "Çocuğunuz…" yerine "Sporcu…" der
# Yetişkin sporcuda hitap: "Çocuğunuzun …" → "Sporcunun …" (yalnız hitap biçimleri; araştırma tanımı değişmez)
VELI_YETISKIN_HITAP = (("Çocuğunuzun", "Sporcunun"), ("çocuğunuzun", "sporcunun"), ("Çocuğunuzla", "Sporcuyla"),
                       ("çocuğunuzla", "sporcuyla"), ("Çocuğunuzu", "Sporcuyu"), ("çocuğunuzu", "sporcuyu"),
                       ("Çocuğunuza", "Sporcuya"), ("çocuğunuza", "sporcuya"), ("Çocuğunuz", "Sporcu"),
                       ("çocuğunuz", "sporcu"), ("çocuğun ölçümleriyle", "sporcunun ölçümleriyle"))
# Paket 38f: yetişkinde raporun kendi cümleleri (çocuk/büyüme dili). Araştırma tanımları ("9-11 yaş çocuklar",
# "620 çocukla") değişmez.
VELI_YETISKIN_IFADE = (
    ("aynı yaş ve cinsiyetteki çocuklar için", "aynı yaş ve cinsiyetteki sporcular için"),
    ("Koyu bant çocukların çoğunun", "Koyu bant sporcuların çoğunun"),
    ("hangi spor gruplarındaki çocuklara benzediğini", "hangi spor gruplarına benzediğini"),
    ("Bu yaşta fiziksel özellikler antrenmanla ve büyümeyle hızla değişir", "Fiziksel özellikler antrenmanla değişir"),
    ("Bu yaşta birden fazla sporu denemek önerilir.", "Birden fazla sporu denemek önerilir."),
)


def yetiskin_mi(bilgi):
    """Profil yaşı ≥ YETISKIN_YAS ise True (veli raporunda hitap 'Sporcu…')."""
    y = _yas_degeri((bilgi or {}).get("Yaş"))
    return y is not None and y >= YETISKIN_YAS


def veli_hitabi(metin, yetiskin):
    """Yetişkin sporcuda 'Çocuğunuz…' hitabını 'Sporcu…' yapar; çocukta metin aynen kalır."""
    if not yetiskin:
        return metin
    for eski, yeni in VELI_YETISKIN_HITAP + VELI_YETISKIN_IFADE:
        metin = metin.replace(eski, yeni)
    return metin


def _dogrusal_yuzdelik(sirali, p):
    """Sıralı değerlerin p. yüzdelik değeri — doğrusal ara değer (numpy.percentile varsayılanı)."""
    if not sirali:
        return None
    h = (len(sirali) - 1) * p / 100
    a = int(h)
    return sirali[a] + (sirali[min(a + 1, len(sirali) - 1)] - sirali[a]) * (h - a)


def _konum_sayi(x):
    """Ekran ve rapor sayısı: en çok 2 ondalık, Türkçe virgül (4.1 → "4,1", -0.2 → "-0,2")."""
    return f"{round(float(x), 2):g}".replace(".", ",")


# Paket 38a: parantez içi YALNIZ bilinen birimse birim sayılır; "(1 dk)", "(30 sn)" gibi süre belirten parantezler
# başlığa aittir (birim boş). Sayım değişkenlerinde kısa sözcük: "Düşme Sayısı" → "düşme", "Tekrar" → "tekrar".
BILINEN_BIRIMLER = frozenset({"cm", "kg", "sn", "dk", "kg/kg", "%", "W", "m", "m/sn", "bpm", "tekrar", "adet",
                              "m/s", "ms", "W/kg", "N/kg", "ml/kg/min", "km/sa", "N", "Nm"})
SAYIM_BIRIMLERI = (("düşme", "düşme"), ("tekrar", "tekrar"), ("atış", "atış"))


def _birim(degisken, test=None):
    """Birim: test verilirse önce normun kendi 'birim' alanı; yoksa değişken adındaki bilinen birim ya da sayım sözcüğü."""
    if test is not None:
        anahtar = f"{kanonik_test(test)} › {degisken}"
        for sozluk in (NORMATIF_YAS, NORMATIF_TEST, NORMATIF_ESIK_YAS):
            b_ = str((sozluk.get(anahtar) or {}).get("birim", "") or "").strip()
            if b_:
                return b_
    m = re.search(r"\(([^()]*)\)\s*$", str(degisken))
    if m and m.group(1).strip() in BILINEN_BIRIMLER:
        return m.group(1).strip()
    ad = str(degisken).lower()
    for anahtar, birim in SAYIM_BIRIMLERI:
        if anahtar in ad:
            return birim
    return ""


def _olcum_satirlari(df_test, test, degisken):
    """(Sporcu, tarih, değer, test yaşı) — kanonik test adıyla; sayısal olmayan değer atılır."""
    if df_test is None or df_test.empty or degisken not in df_test.columns:
        return pd.DataFrame(columns=["Sporcu", "Tarih_dt", "Deger", "Test Yaşı"])
    d = df_test[df_test["Test"].map(kanonik_test) == kanonik_test(test)].copy()
    d["Deger"] = pd.to_numeric(d[degisken], errors="coerce")
    if "Tarih_dt" not in d.columns:
        d["Tarih_dt"] = pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce")
    if "Test Yaşı" not in d.columns:
        d["Test Yaşı"] = None
    return d.dropna(subset=["Deger"]).sort_values("Tarih_dt")[["Sporcu", "Tarih_dt", "Deger", "Test Yaşı"]]


def gelisim_ozeti(df_test, sporcu, test, degisken):
    """
    Aynı sporcunun aynı testteki ölçümleri (zaman sırası) ve son ölçümün öncekine göre farkı (mutlak, %).
    iyi_yonde: yön biliniyorsa True/False (süre testlerinde azalma iyi), değilse None. Tek ölçüm: ilk=True.
    """
    d = _olcum_satirlari(df_test, test, degisken)
    d = d[d["Sporcu"] == sporcu]
    olc = [(t.strftime("%d.%m.%Y") if pd.notna(t) else "", float(v)) for t, v in zip(d["Tarih_dt"], d["Deger"])]
    o = {"test": kanonik_test(test), "degisken": degisken, "birim": _birim(degisken, test), "olcumler": olc,
         "yon": degisken_yonu(test, degisken), "ilk": len(olc) == 1, "fark": None, "yuzde": None, "iyi_yonde": None}
    if len(olc) >= 2:
        onceki, son = olc[-2][1], olc[-1][1]
        o["fark"] = round(son - onceki, 2)
        o["yuzde"] = round((son - onceki) / abs(onceki) * 100, 1) if onceki else None
        if o["yon"] is not None and o["fark"] != 0:
            o["iyi_yonde"] = (o["fark"] < 0) if o["yon"] else (o["fark"] > 0)
    return o


# Paket 38c: veli/antrenör "Kendi gelişimi" test başına çalışır. Bir testin ANA SONUCU: "En İyi" değişkeni; yoksa
# deneme değişkenlerinin kayıt içindeki en iyisi (yön tanımına göre); yoksa tek değişken. Bunların hiçbiri yoksa test
# ÇOK BİLEŞENLİDİR (ör. NHT sağ/sol kuvvet): veli raporunda tek satır özet, ham bileşenler antrenör raporunda.
# Neden: değişken başına çalışınca, ikinci oturumda yalnız Deneme 1 girilen bir testin Deneme 2'si "ilk ölçüm"
# tablosunda eski değeriyle kalıyordu (aynı test raporda iki farklı değerle).
_DENEME_KALIBI = re.compile(r"(^|— )Deneme \d")


def ana_sonuc_tanimi(test, degiskenler):
    """("eniyi", d) | ("deneme", [d…]) | ("tek", d) | None (çok bileşenli). Rölatif değer (kayıtlı kilodan
    hesaplanan) başka değişken varken bileşen sayılmaz: "1RM Squat (kg)" + "Rölatif Squat (kg/kg)" → tek."""
    ds = [d for d in degiskenler if not str(d).startswith("Rölatif")] or list(degiskenler)
    en_iyi = [d for d in ds if "En İyi" in d]
    if en_iyi:
        return ("eniyi", en_iyi[0])
    deneme = [d for d in ds if _DENEME_KALIBI.search(d)]
    if deneme and len(deneme) == len(ds):
        return ("deneme", deneme)
    if len(ds) == 1:
        return ("tek", ds[0])
    return None


def _sonuc_degiskenleri(g):
    return [c for c in g.columns if c not in META_KOLONLAR and not METIN_DEGISKEN_KALIBI.search(str(c))
            and pd.to_numeric(g[c], errors="coerce").notna().any()]


def test_sonuc_serisi(g, test):
    """
    Tek testin kayıtları (aynı sporcu) → ana sonuç serisi {test, degisken, birim, olcumler, yon, ilk, fark, yuzde,
    iyi_yonde, tur}; çok bileşenliyse {"tur": "bilesik", test, degiskenler, son_tarih, olcum_sayisi}.
    Aynı gün iki kayıt varsa son kayıt sayılır.
    """
    g = g.sort_values("Tarih_dt") if "Tarih_dt" in g.columns else g
    ds = _sonuc_degiskenleri(g)
    tanim = ana_sonuc_tanimi(test, ds)
    tarihler = [t.strftime("%d.%m.%Y") if pd.notna(t) else str(s) for t, s in
                zip(g.get("Tarih_dt", pd.Series([pd.NaT] * len(g))), g["Tarih"])]
    if tanim is None:
        dolu = [tr for tr, (_, r) in zip(tarihler, g.iterrows()) if any(_girildi(r.get(d)) for d in ds)]
        return {"tur": "bilesik", "test": kanonik_test(test), "degiskenler": ds,
                "son_tarih": dolu[-1] if dolu else "", "olcum_sayisi": len(dict.fromkeys(dolu))}
    tur, d = tanim
    yon = degisken_yonu(test, d if tur != "deneme" else d[0])
    olc = {}
    for tr, (_, r) in zip(tarihler, g.iterrows()):
        if tur == "deneme":
            vs = [float(x) for x in pd.to_numeric(pd.Series([r.get(x) for x in d]), errors="coerce").dropna()]
            if not vs:
                continue
            v = min(vs) if yon is True else max(vs)
        else:
            v = pd.to_numeric(pd.Series([r.get(d)]), errors="coerce").iloc[0]
            if pd.isna(v):
                continue
            v = float(v)
        olc[tr] = v                                         # aynı gün: son kayıt
    birim_kaynagi = d[0] if tur == "deneme" else d
    etiket = (f"En iyi deneme ({_birim(birim_kaynagi)})" if _birim(birim_kaynagi) else "En iyi deneme") \
        if tur == "deneme" else d
    liste = list(olc.items())
    o = {"tur": tur, "test": kanonik_test(test), "degisken": etiket, "birim": _birim(birim_kaynagi, test),
         "olcumler": liste, "yon": yon, "ilk": len(liste) == 1, "fark": None, "yuzde": None, "iyi_yonde": None}
    if len(liste) >= 2:
        onceki, son = liste[-2][1], liste[-1][1]
        o["fark"] = round(son - onceki, 2)
        o["yuzde"] = round((son - onceki) / abs(onceki) * 100, 1) if onceki else None
        if yon is not None and o["fark"] != 0:
            o["iyi_yonde"] = (o["fark"] < 0) if yon else (o["fark"] > 0)
    return o


def test_gelisim_ozetleri(df_test, sporcu):
    """Sporcunun her testi için test_sonuc_serisi (ana sonuçlu ve çok bileşenli olanlar ayrı 'tur' ile)."""
    if df_test is None or df_test.empty:
        return []
    d = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" not in d.columns:
        d = d.assign(Tarih_dt=pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce"))
    sonuc = []
    for test, g in d.groupby(d["Test"].map(kanonik_test), sort=True):
        s = test_sonuc_serisi(g, test)
        if s.get("tur") == "bilesik" and not s["degiskenler"]:
            continue
        if s.get("tur") != "bilesik" and not s["olcumler"]:
            continue
        sonuc.append(s)
    return sonuc


def _profil_haritasi(df_sp):
    if df_sp is None or df_sp.empty or not {"Ad", "Soyad"} <= set(df_sp.columns):
        return {}
    return {f"{a} {s}": r for (a, s), r in zip(zip(df_sp["Ad"].astype(str), df_sp["Soyad"].astype(str)),
                                                  df_sp.to_dict("records"))}


def grup_ici_konum(df_test, df_sp, sporcu, test, degisken):
    """
    Sporcunun son ölçümünün, aynı testi yapan aynı cinsiyet ve aynı 2 yıllık yaş bandındaki sporcuların SON
    ölçümleri arasındaki yeri. Her sporcu havuzda bir kez; sporcunun kendisi havuzda (vurgulanır). Havuz yalnız
    kendisiyse durum "yetersiz". n ≥ GRUP_KONUM_YUZDELIK_N ise performans yönünde yüzdelik ve çeyrek bandı.
    """
    prof = _profil_haritasi(df_sp)
    d = _olcum_satirlari(df_test, test, degisken)
    yetersiz = {"durum": "yetersiz", "n": 0, "metin": KONUM_YETERSIZ_METNI, "degisken": degisken,
                "test": kanonik_test(test), "birim": _birim(degisken, test)}
    kendi = d[d["Sporcu"] == sporcu]
    cins = str(prof.get(sporcu, {}).get("Cinsiyet", "")).strip()
    if kendi.empty or cins not in ("Erkek", "Kadın"):
        return yetersiz
    son = kendi.iloc[-1]
    yas = _yas_degeri(son["Test Yaşı"]) or _yas_degeri(prof.get(sporcu, {}).get("Yaş"))
    if yas is None:
        return yetersiz
    bas = int(yas) // GRUP_KONUM_BANT_YIL * GRUP_KONUM_BANT_YIL
    bant = (bas, bas + GRUP_KONUM_BANT_YIL - 1)
    havuz = {}
    for _, r in d.iterrows():
        p = prof.get(r["Sporcu"], {})
        y = _yas_degeri(r["Test Yaşı"]) or _yas_degeri(p.get("Yaş"))
        if str(p.get("Cinsiyet", "")).strip() != cins or y is None or not bant[0] <= int(y) <= bant[1]:
            continue
        havuz[r["Sporcu"]] = float(r["Deger"])                    # tarih sırasıyla: son ölçüm kalır
    if sporcu not in havuz or len(havuz) < 2:
        return {**yetersiz, "n": len(havuz), "cinsiyet": cins, "bant": bant}
    deger, degerler = havuz[sporcu], sorted(havuz.values())
    ort = sum(degerler) / len(degerler)
    yon = degisken_yonu(test, degisken)
    k = {"durum": "tamam", "n": len(degerler), "deger": deger, "ortalama": round(ort, 2), "degerler": degerler,
         "cinsiyet": cins, "bant": bant, "yas": yas, "yon": yon, "test": kanonik_test(test), "degisken": degisken,
         "birim": _birim(degisken, test), "taraf": ("üstü" if deger > ort else "altı" if deger < ort else "ortası"),
         "yuzdelik": None, "ceyrek": None,
         "p10": _dogrusal_yuzdelik(degerler, VELI_ARALIK_YUZDELIK[0]),          # Paket 37: veli aralığı
         "p90": _dogrusal_yuzdelik(degerler, VELI_ARALIK_YUZDELIK[1])}
    if k["n"] >= GRUP_KONUM_YUZDELIK_N and yon is not None:
        digerleri = list(degerler)
        digerleri.remove(deger)
        iyi = lambda a, b: (a < b) if yon else (a > b)
        alt = sum(1 for x in digerleri if iyi(deger, x)) + 0.5 * sum(1 for x in digerleri if x == deger)
        k["yuzdelik"] = round(alt / len(digerleri) * 100)
        k["ceyrek"] = ("grubun alt çeyreği" if k["yuzdelik"] < 25 else
                       "grubun üst çeyreği" if k["yuzdelik"] > 75 else "grubun orta yarısı")
    return k


def konum_metinleri(k):
    """Pencere ve antrenör raporu metni. n < 20: yüzdelik/sıralama sözcüğü YOK (yalnız ortalamanın altı/üstü)."""
    if k.get("durum") != "tamam":
        return [f"n = {k.get('n', 0)}", KONUM_YETERSIZ_METNI]
    b = k["birim"]
    m = [f"n = {k['n']}",
         f"Havuz: {k['cinsiyet'].lower()}, {k['bant'][0]}-{k['bant'][1]} yaş, {k['test']} — {k['degisken']}",
         f"Değer {_konum_sayi(k['deger'])} {b} · grup ortalaması {_konum_sayi(k['ortalama'])} {b} · ortalamanın {k['taraf']}"]
    if k["yon"] is True:
        m.append("Bu testte düşük değer daha iyidir.")
    elif k["yon"] is None:
        m.append("Bu ölçümün iyi yönü tanımlı değil (tanımlayıcı ölçü).")
    if k.get("yuzdelik") is not None:
        m.append(f"Grup içi yüzdelik ≈ {k['yuzdelik']} ({k['ceyrek']}).")
    return m


def konum_seridi_svg(k, renk=None):
    """
    Konum şeridi: havuzdaki değerler (isimsiz noktalar), ortalama çizgisi, sporcunun değeri vurgulu. renk: {ad: renk}
    (uygulamada renk_css, raporda açık paletin düz tonları — saydam renk yok).
    """
    if k.get("durum") != "tamam":
        return ""
    r = renk or {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}
    en, en_b = min(k["degerler"]), max(k["degerler"])
    aralik = (en_b - en) or 1.0
    x = lambda v: 12 + (v - en) / aralik * 296
    p = [f'<svg viewBox="0 0 320 40" width="320" height="40" role="img" aria-label="Konum şeridi">',
         f'<line x1="12" y1="22" x2="308" y2="22" stroke="{r["cizgi"]}" stroke-width="2"/>']
    p += [f'<circle cx="{x(v):.1f}" cy="22" r="3" fill="{r["ikincil"]}"/>' for v in k["degerler"]]
    p.append(f'<line x1="{x(k["ortalama"]):.1f}" y1="12" x2="{x(k["ortalama"]):.1f}" y2="32" stroke="{r["murekkep"]}" '
             f'stroke-width="1.5"/>')
    p.append(f'<circle cx="{x(k["deger"]):.1f}" cy="22" r="6" fill="{r["ana"]}"/></svg>')
    return "".join(p)


def rapor_konum_degiskenleri(df_test, sporcu):
    """Sporcunun testleri × sonuç değişkenleri (sayısal). Testte "En İyi" türü hesaplanan değişken varsa yalnız o."""
    if df_test is None or df_test.empty:
        return []
    d = df_test[df_test["Sporcu"] == sporcu]
    cift = []
    for test, g in d.groupby(d["Test"].map(kanonik_test)):
        sayisal = [c for c in g.columns if c not in META_KOLONLAR and pd.to_numeric(g[c], errors="coerce").notna().any()]
        en_iyi = [c for c in sayisal if "En İyi" in c]
        cift += [(test, c) for c in (en_iyi or sayisal)]
    return cift


def rapor_verisi(sporcu):
    """Veli ve antrenör raporunun ortak verisi. Test kaydı olmayan sporcu için de çalışır."""
    bilgi = sporcu_profil_bilgisi(sporcu)
    if os.path.exists(TEST_DOSYA):
        df_test = test_tablosu_duzelt(pd.read_excel(TEST_DOSYA))
    else:
        df_test = pd.DataFrame(columns=["Sporcu", "Test", "Tarih"])
    df_test["Tarih_dt"] = pd.to_datetime(df_test["Tarih"], format="%d.%m.%Y", errors="coerce")
    df_s = df_test[df_test["Sporcu"] == sporcu]

    zp = sporcu_z_profili(df_test, sporcu)
    fsc = sporcu_fsc_profili(df_test, sporcu)
    esl = brans_grubu_eslestir(fsc, bilgi.get("Yaş"))
    ilgi = ilgi_son_anket(sporcu)
    puan = ilgi_grup_puanlari(ilgi) if ilgi else {}
    pen = ilgi_fiziksel_pencereler(esl, puan) if ilgi else None
    hacim, hacim_tarih = sporcu_antrenman(bilgi)
    fiziksel_uc = sorted(g for g, _ in esl["siralama"][:3]) if esl["uygun"] else []
    katman = grup_radar_katmani(df_test, sporcu, fiziksel_uc) if fiziksel_uc else None
    bilesikler = {ad: bilesik_z_hesapla(ad, zp["z_sozlugu"]) for ad in BILESIK_Z} if not zp["hata"] else {}

    # Kayıtlı testler: son tarih ve ölçüm sayısı
    testler = []
    for test_adi, grp in df_s.groupby("Test"):
        t_son = grp["Tarih_dt"].max()
        testler.append({"Test": test_adi, "Ölçüm sayısı": len(grp),
                        "Son ölçüm": t_son.strftime("%d.%m.%Y") if pd.notna(t_son) else str(grp["Tarih"].iloc[-1])})
    normlu_testler = {r["Test"] for r in zp["satirlar"]}
    normsuz = sorted(t["Test"] for t in testler if t["Test"] not in normlu_testler)
    tarihler = df_s["Tarih_dt"].dropna()
    tarih_araligi = ((tarihler.min().strftime("%d.%m.%Y"), tarihler.max().strftime("%d.%m.%Y"))
                     if not tarihler.empty else None)

    # Sınır durumları (antrenör raporu)
    sinirlar = []
    cins = str(bilgi.get("Cinsiyet", "")).strip()
    for (test_z, degisken_z), zbilgi in zp["z_sozlugu"].items():
        etiket = f"{test_z} — {degisken_z}"
        if zbilgi.get("durum") in ("alt_sinir", "ust_sinir", "esit_bant"):
            z_s = zbilgi.get("z_performans")
            ek = f" (Z {z_s:+.2f})" if z_s is not None and zbilgi.get("durum") != "esit_bant" else ""
            sinirlar.append((etiket, zbilgi.get("durum_notu", "") + ek))
        if zbilgi.get("yas_notu"):
            sinirlar.append((etiket, str(zbilgi["yas_notu"]).replace("⚠️ ", "")
                             + " (yaş aralığı dışı norm kullanımı)"))
        elif zbilgi.get("yas") is not None and zbilgi.get("kullanilan_yas") is not None \
                and int(zbilgi["yas"]) != int(zbilgi["kullanilan_yas"]):
            sinirlar.append((etiket, f"{int(zbilgi['yas'])} yaş için norm satırı yok — en yakın "
                                     f"{zbilgi['kullanilan_yas']} yaş normu kullanıldı"))
        if zbilgi.get("ceyrek_notu") and "ortalama" in zbilgi["ceyrek_notu"]:
            sinirlar.append((etiket, zbilgi["ceyrek_notu"]))
        if not zbilgi.get("cins_norm_var", True):
            sinirlar.append((etiket, f"{cins} normu yok — erkek normu kullanıldı"))
    for ad_b, bz in bilesikler.items():
        for n_b in bz.get("notlar", []):
            sinirlar.append((ad_b, n_b + " Testin kendi Z'si tabloda ve radarda duruyor."))
    if zp["eski_yas"]:
        sinirlar.append(("Eski kayıtlar", "Test günündeki yaş kaydedilmemiş; profildeki güncel yaş kullanıldı."))
    for kod in esl.get("dislanan_yas", []):
        sinirlar.append((BRANS_GRUBU_PROFILLERI["degiskenler"][kod]["ad"],
                         "9-11 yaş dışında ölçüldüğü için branş eşleştirmesine girmedi"))

    kaynaklar = sorted({str(z.get("kaynak", "")).split("\n")[0].strip()
                        for z in zp["z_sozlugu"].values() if z.get("kaynak")})
    # Paket 36: kendi gelişimi ve grup içi konum (başka sporcuların adı veride tutulmaz)
    df_sp_r = pd.read_excel(SPORCU_DOSYA) if os.path.exists(SPORCU_DOSYA) else pd.DataFrame()
    ciftler = rapor_konum_degiskenleri(df_test, sporcu)
    gelisim = [gelisim_ozeti(df_test, sporcu, t, d_) for t, d_ in ciftler]
    konum = [grup_ici_konum(df_test, df_sp_r, sporcu, t, d_) for t, d_ in ciftler]
    gelisim_test = test_gelisim_ozetleri(df_test, sporcu)                 # Paket 38c: test başına
    return {"sporcu": sporcu, "bilgi": bilgi, "zp": zp, "fsc": fsc, "esl": esl, "ilgi": ilgi, "puan": puan,
            "pen": pen, "hacim": hacim, "hacim_tarih": hacim_tarih, "fiziksel_uc": fiziksel_uc,
            "katman": katman, "bilesikler": bilesikler, "testler": testler, "normsuz": normsuz,
            "tarih_araligi": tarih_araligi, "sinirlar": sinirlar, "kaynaklar": kaynaklar,
            "gelisim": gelisim, "gelisim_test": gelisim_test, "konum": konum, "rapor_tarihi": date.today().strftime("%d.%m.%Y")}


RAPOR_CSS = f"""
<style>
  :root {{ --ink:{_RAPOR_RENK["murekkep"]}; --muted:{_RAPOR_RENK["ikincil"]}; --line:{_RAPOR_RENK["cizgi"]}; --soft:{_RAPOR_RENK["zemin"]};
          --accent:{_RAPOR_RENK["ana"]}; --love:{_RAPOR_VURGU["sevgi"]}; --phys:{_RAPOR_VURGU["fiziksel"]};
          --star:{_RAPOR_VURGU["yildiz"]}; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: {YAZI_AILESI};
         color: var(--ink); background:{_RAPOR_RENK["yuzey"]}; margin:0; padding:24px; line-height:1.5; font-size:14px; }}
  .sayfa {{ max-width: 820px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  h2 {{ font-size: 16px; margin: 26px 0 8px; padding-bottom:4px; border-bottom: 2px solid var(--line); }}
  h3 {{ font-size: 14px; margin: 14px 0 6px; }}
  .alt {{ color: var(--muted); font-size: 12.5px; }}
  .iki {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  .kutu {{ border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; background: var(--soft); }}
  .kutu.sev {{ border-top: 4px solid var(--love); }}
  .kutu.fiz {{ border-top: 4px solid var(--phys); }}
  .kutu ul {{ margin: 6px 0 0; padding-left: 18px; }}
  .kesisim {{ border: 2px solid var(--star); background: {_RAPOR_VURGU["yildiz_zemin"]}; border-radius: 10px; padding: 12px 14px; margin-top: 12px; }}
  .not {{ border-left: 4px solid var(--accent); background: {_RAPOR_VURGU["not_zemin"]}; padding: 10px 12px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
  .uyari {{ border-left: 4px solid {_RAPOR_VURGU["uyari"]}; background: {_RAPOR_VURGU["uyari_zemin"]}; padding: 10px 12px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
  .tablo {{ overflow-x: auto; margin: 6px 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12.5px; }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 5px 6px; text-align: left; vertical-align: top; }}
  th {{ background: var(--soft); font-weight: 600; }}
  td.sayi {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .yildiz {{ color: var(--star); font-weight: 700; }}
  .radar {{ text-align: center; margin: 8px 0; }}
  .kucuk {{ font-size: 11.5px; color: var(--muted); }}
  body.veli {{ border-top: {b(0.75)} solid var(--accent); }}
  .veli-grup {{ display: flex; align-items: center; gap: {b(1)}; margin-top: {b(3)}; }}
  .kutu .veli-grup {{ margin-top: {b(0.75)}; }}
  .veli-satir {{ display: grid; grid-template-columns: 300px 1fr; gap: {b(2)}; align-items: center; margin: 0 0 {b(1.5)}; }}
  .veli-satir .sp-kart {{ margin: 0; }}
  .veli-yorum {{ margin: 0; }}
  .veli-aralik {{ border: 1px solid {_RAPOR_RENK["cizgi"]}; border-radius: 10px; padding: 10px 14px; margin: 0 0 {b(1.5)};
                 break-inside: avoid; }}
  .veli-aralik h4 {{ margin: 0 0 2px; font-size: 15px; }}
  .veli-aralik p {{ margin: 4px 0; }}
  .veli-deger {{ font-size: 16px; }}
  .veli-durum {{ margin: {b(0.5)} 0 {b(1.5)}; color: var(--muted); }}
  .veli-son {{ margin: {b(3)} 0 0; padding: {b(2)}; border: 1px solid var(--line); border-radius: {b(1)};
               background: var(--soft); font-weight: 600; }}
  @media (max-width: 640px) {{ .iki {{ grid-template-columns: 1fr; }} .veli-satir {{ grid-template-columns: 1fr; gap: {b(1)}; }} body {{ padding: 14px; }} }}
  @media print {{ body {{ padding: 0; }} h2 {{ break-after: avoid; }} .kutu, .kesisim, table {{ break-inside: avoid; }} }}
{BILESEN_CSS}
</style>
"""


def _tablolari_sar(metin):
    """Dar ekranda tablolar sayfayı taşırmasın: yatay kaydırılabilir kapsayıcı."""
    return metin.replace("<table>", '<div class="tablo"><table>').replace("</table>", "</table></div>")


# ════════════════════════════════════════════════════════════
# VELİ RAPORU YORUMLARI (Paket 12) — ŞABLONLU, serbest metin YOK.
# Kurallar: (1) çocuğu değil sonucu tarif et; (2) gelecek yordaması yok;
# (3) düşük sonuç = gelişim alanı; (4) tek testten genel sonuç çıkarma.
# Z, persentil, norm kaynağı ve sınır notları veli raporunda geçmez.
# Cümleler: 6 kategori × 4 test grubu = 24 şablon (VELI_YORUMLARI). Denetim
# her şablonu yasak sözcüklere ve yapıya karşı tek tek kontrol eder.
# ════════════════════════════════════════════════════════════
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
            f'{konum_seridi_veli_svg(k, renk)}<p class="kucuk">{_e(VELI_ARALIK_NOTU)}</p></div>')


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


# ════════════════════════════════════════════════════════════
# KAYNAKÇA — uygulamadaki tüm kaynaklar, indeks durumuna göre
# ------------------------------------------------------------
# Sınıflandırma dayanağı: SCImago Journal Rank (SJR) 2025 yılı verisi, "SJR Best
# Quartile" (derginin kategorileri içindeki en iyi çeyreği). Veri: SCImago'nun
# yıllık dışa aktarımlarını derleyen sjrdata (Kashnitsky, v1.0.25, Haziran 2026);
# Archives of Budo SCImago sitesinde kontrol edildi (2025: SJR 0.369, Q3).
# Dergi adı listede eşleşmezse tahmin edilmez: "Belirlenemedi".
# Aynı eserin farklı yazımları (kısa/uzun künye) tek kayıt sayıldı.
# ════════════════════════════════════════════════════════════
KAYNAKCA_DAYANAK = ("SCImago Journal Rank (SJR) 2025 — derginin kategorileri içindeki en iyi çeyrek (SJR Best "
                    "Quartile). Veri: SCImago yıllık dışa aktarımlarını derleyen sjrdata paketi (v1.0.25, Haziran 2026). "
                    "Sınıflandırma tarihi: 14.10.2026.")
KAYNAKCA_SINIFLAR = ["Q1", "Q2", "Q3/Q4", "Scopus (çeyreklik dışı)", "İndekslenmeyen", "Belirlenemedi"]


# ════════════════════════════════════════════════════════════
# DÜNYA VE OLİMPİYAT REKORLARI
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# GENEL NORM KAPSAMI
# Bazı değişken adları birden fazla testte ortaktır. Burada listelenen
# değişkenlerin NORMATIF'teki bantları yalnızca koşulu sağlayan testlere
# uygulanır; diğer testlerde "norm yok" sayılır (protokol eşleşmesi kuralı).
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# TEKNİK TERİM SÖZLÜĞÜ
# Orijinal terim korunur, Türkçe karşılık parantez içinde eklenir
# ════════════════════════════════════════════════════════════


def terimleri_bul(*metinler):
    """Metinlerde geçen terimler (ACIKLAMALAR'daki adlarıyla, tekrarsız)."""
    birlesik = " ".join(str(m) for m in metinler if m)
    return [t for t, kalip in TERIM_ARAMA.items() if re.search(kalip, birlesik)]


def terim_metni(terimler):
    return "\n\n".join(f"**{t}:** {ACIKLAMALAR[t]}" for t in terimler)


def ac_dugmesi(terimler, etiket="ⓘ Bu bölümdeki terimler"):
    """
    Tıklanınca açılan kısa açıklama (telefonda da çalışır). st.popover yoksa st.expander.
    Tek kaynak: ACIKLAMALAR. Bilinmeyen terim KeyError verir (otomatik denetim yakalar).
    """
    terimler = [terimler] if isinstance(terimler, str) else list(dict.fromkeys(terimler))
    if not terimler:
        return
    metin = terim_metni(terimler)
    if hasattr(st, "popover"):
        with st.popover(etiket):
            st.markdown(metin)
    else:
        with st.expander(etiket):
            st.markdown(metin)


def bolum_terimleri(terimler):
    """Bölüm başına TEK düğme: 'ⓘ Bu bölümdeki terimler' (her yerde tıklama; telefonda hover yok)."""
    ac_dugmesi(terimler, "ⓘ Bu ne demek?")                       # Paket 38a: tek dokunuş, sade dil


def _hover_metni(terimler):
    terimler = [terimler] if isinstance(terimler, str) else list(terimler)
    return "\n\n".join(f"{t}: {ACIKLAMALAR[t]}" for t in terimler)


def baslik_ac(metin, terimler, seviye="subheader"):
    """
    Başlık; masaüstünde fareyle üzerine gelince aynı açıklama (title). Düğme koymaz —
    tıklanabilir açıklama bölümün 'ⓘ Bu bölümdeki terimler' düğmesindedir.
    seviye: 'header' (##), 'subheader' (###) ya da markdown önekleri ('####', '######').
    """
    st.markdown(baslik_html(metin, terimler, seviye), unsafe_allow_html=True)


def baslik_html(metin, terimler, seviye="subheader"):
    """
    baslik_ac'ın ürettiği markdown. title içinde satır sonu OLMAMALI: boş satır markdown'da
    paragraf açar ve <span> yarıda kalır (Paket 11'de bulunan hata: birden çok terimli başlıkta
    açıklama metni ham HTML olarak başlık yerine basılıyordu). Satır sonları &#10; olarak yazılır.
    """
    onek = {"header": "##", "subheader": "###"}.get(seviye, seviye)
    baslik = _html.escape(_hover_metni(terimler), quote=True).replace("\n", "&#10;")
    return (f'{onek} <span title="{baslik}" style="text-decoration: underline dotted; '
            f'text-decoration-thickness: 1px; text-underline-offset: 5px; cursor: help;">'
            f'{_html.escape(metin)}</span>')


def sutun_yardimi(sutun_terim):
    """st.dataframe column_config: sütun başlığına (masaüstünde üzerine gelince) aynı açıklama."""
    try:
        return {s: st.column_config.Column(help=ACIKLAMALAR[t]) for s, t in sutun_terim.items()}
    except AttributeError:
        return None


# ════════════════════════════════════════════════════════════
# PAKET 10 — TEST OTURUMU, SPORCU GRUBU, MAKULLÜK KONTROLÜ
# ------------------------------------------------------------
# Kayıt biçimi TEK yerde üretilir (test_kaydi_olustur): tekli giriş ve toplu giriş aynı
# fonksiyonu çağırır; otomatik denetim bunu doğrular.
# Makullük: girilen değer, yaş/cinsiyet normunun P1-P99 aralığı dışındaysa kaydetmeden önce
# uyarılır; kullanıcı onaylarsa kaydedilir (engellemez). Normu olmayan değişkende kontrol yok.
# ════════════════════════════════════════════════════════════
GRUP_KOLON = "Grup/Sınıf"
OTURUM_KOLONLARI = ["Oturum", "Yer", "Uygulayıcı"]
TOPLU_GIRIS_DISI = {"Special Wrestling Fitness Test (SWFT)"}   # özel giriş ekranı olan test


def deger_metni(v):
    """Toplu girişteki sayıyı tekli girişin yazdığı biçime çevirir (\"17\", \"18.5\"); boşsa \"\"."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(v, (int, float)):
        f = float(v)
        return str(int(f)) if f.is_integer() else repr(round(f, 4))
    return str(v).strip()


def test_kaydi_olustur(sporcu, sporcu_satir, kategori, batarya, brans, test_adi, tarih, degerler,
                       hesaplanan, notlar="", oturum=None):
    """
    test_sonuclari.xlsx'e yazılacak TEK kayıt. Tekli giriş ve Test Oturumu bu fonksiyonu kullanır.
    oturum: {"kimlik", "yer", "uygulayici"} ya da None (tekli giriş — alanlar boş yazılır).
    """
    oturum = oturum or {}
    kayit = {
        "Sporcu": sporcu,
        "Kategori": kategori,
        "Batarya": batarya,
        "Branş": brans if brans else "-",
        "Test": kanonik_test(test_adi),          # takma ad asıl adla yazılır (Paket 27)
        "Tarih": tarih.strftime("%d.%m.%Y"),
        "Notlar": notlar or "",
        "Oturum": oturum.get("kimlik", ""),
        "Yer": oturum.get("yer", ""),
        "Uygulayıcı": oturum.get("uygulayici", ""),
    }
    kayit.update(degerler)
    profil_yas = sporcu_satir.get("Yaş") if hasattr(sporcu_satir, "get") else None
    # Test günündeki yaş: Z/persentil sonradan doğru yaş normuyla hesaplansın
    kayit["Test Yaşı"] = tam_yas(sporcu_satir.get(DOGUM_KOLON), tarih) or profil_yas
    # Otomatik hesaplanan sayısal değerler de kaydedilir (ör. KTK3+ toplamları)
    for k_h, v_h in hesaplanan.items():
        if k_h not in kayit and isinstance(v_h, (int, float)):
            kayit[k_h] = v_h
    return kayit


def kayitlari_yaz(kayitlar):
    """Kayıtları test dosyasına ekler."""
    if not kayitlar:
        return
    yeni = pd.DataFrame(kayitlar)
    if os.path.exists(TEST_DOSYA):
        df_eski = pd.read_excel(TEST_DOSYA)
        yeni = pd.concat([df_eski, yeni], ignore_index=True)
    yeni.to_excel(TEST_DOSYA, index=False)


# ── Makullük sınırları ──
def makul_aralik_bantlardan(bantlar):
    """
    Persentil bantlarından (P5…P95, P20…P80 ya da 19 persentil) yaklaşık P1 ve P99.
    Normlar P1/P99 vermez; alt ve üst kuyruk ayrı ayrı normal yaklaşımla uzatılır:
      medyan = P50 (yoksa iki komşu bandın doğrusal ara değeri)
      SS_alt = (medyan − en alt bant) / |z(en alt)|,  SS_üst = (en üst bant − medyan) / z(en üst)
      P1 = medyan − 2.326·SS_alt,  P99 = medyan + 2.326·SS_üst
    Çarpık dağılımlarda iki kuyruk ayrı uzadığı için simetrik bir aralıktan daha gerçekçidir.
    Dönen: (p1, p99) ya da None.
    """
    try:
        noktalar = sorted((int(k[1:]), float(v)) for k, v in bantlar.items()
                          if str(k).startswith("P") and str(k)[1:].isdigit())
    except (TypeError, ValueError):
        return None
    if len(noktalar) < 2:
        return None
    ps = [p for p, _ in noktalar]
    vs = [v for _, v in noktalar]
    if 50 in ps:
        medyan = vs[ps.index(50)]
    else:
        alt_i = max(i for i, p in enumerate(ps) if p < 50) if any(p < 50 for p in ps) else 0
        ust_i = min(i for i, p in enumerate(ps) if p > 50) if any(p > 50 for p in ps) else len(ps) - 1
        p_a, p_u = ps[alt_i], ps[ust_i]
        medyan = vs[alt_i] + (vs[ust_i] - vs[alt_i]) * ((50 - p_a) / (p_u - p_a) if p_u != p_a else 0)
    z_alt = _STANDART_NORMAL.inv_cdf(ps[0] / 100)
    z_ust = _STANDART_NORMAL.inv_cdf(ps[-1] / 100)
    z99 = _STANDART_NORMAL.inv_cdf(0.99)
    ss_alt = max(medyan - vs[0], 0) / abs(z_alt) if z_alt < 0 else 0
    ss_ust = max(vs[-1] - medyan, 0) / z_ust if z_ust > 0 else 0
    p1 = min(medyan - z99 * ss_alt, vs[0])
    p99 = max(medyan + z99 * ss_ust, vs[-1])
    return p1, p99


def makul_aralik(test_adi, degisken, yas, cinsiyet, dogum=None, tarih=None):
    """Bu sporcunun norm hücresinde yaklaşık P1-P99. Normu yoksa None."""
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_YAS or cinsiyet not in ("Erkek", "Kadın"):
        return None
    norm = NORMATIF_YAS[anahtar]
    ornek = next(iter(norm["yaslar"].values())).get(cinsiyet) or {}
    ys = yas_persentil_bul(test_adi, degisken, yas, cinsiyet, ornek.get("P50", 0) or 0, dogum, tarih)
    if not ys or ys.get("yas_notu"):
        return None   # yaş normun aralığı dışında: başka yaşın normuyla makullük denetlenmez (Paket 11)
    sinir = makul_aralik_bantlardan(ys["bantlar"])
    if not sinir:
        return None
    kim = "kız" if cinsiyet == "Kadın" and ys["kullanilan_yas"] < 18 else cinsiyet.lower()
    hucre = f"{ys['kullanilan_yas']} yaş {kim}" + (f" ({ys['ceyrek']}. doğum çeyreği)" if ys.get("ceyrek") else "")
    return {"alt": sinir[0], "ust": sinir[1], "hucre": hucre, "birim": ys.get("birim") or norm.get("birim", "")}


def _sayi_kisa(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if abs(x) < 1000 else f"{x:.0f}"


def makullukte_uyarilar(test_adi, degerler, yas, cinsiyet, dogum=None, tarih=None, etiket=""):
    """Norm aralığı (≈P1-P99) dışındaki değerler için uyarı metinleri. Normu olmayanlar atlanır."""
    uyarilar = []
    for degisken, v in degerler.items():
        if not _girildi(v):
            continue
        try:
            x = float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            continue
        if x == 0 and not sifir_gecerli(test_adi, degisken):
            continue
        ar = makul_aralik(test_adi, degisken, yas, cinsiyet, dogum, tarih)
        if not ar or ar["alt"] <= x <= ar["ust"]:
            continue
        on = f"{etiket}: " if etiket else ""
        uyarilar.append(f"{on}{test_adi} — {degisken} = {_sayi_kisa(x)} {ar['birim']}: {ar['hucre']} için olağandışı "
                        f"(beklenen ≈ {_sayi_kisa(ar['alt'])}–{_sayi_kisa(ar['ust'])} {ar['birim']}, P1–P99). "
                        f"Emin misiniz?")
    return uyarilar


# Profildeki boy ve kilo için norm: TSYT (7-11 yaş). Başka yaşta norm olmadığı için kontrol yok.
PROFIL_MAKULLUK = {"Boy (cm)": ("Boy ve Vücut Ağırlığı (TSYT)", "Boy (cm)"),
                   "Kilo (kg)": ("Boy ve Vücut Ağırlığı (TSYT)", "Vücut Ağırlığı (kg)")}


# Paket 38a: yeni sporcu formu boş açılır (varsayılan sayı yok); bu alt sınırların altı kaydedilmez.
SPORCU_FORM_ALT_SINIR = {"Yaş": 4, "Boy (cm)": 80, "Kilo (kg)": 10}
SPORCU_FORM_ALANLARI = ("sg_ad", "sg_soyad", "sg_yas", "sg_boy", "sg_kilo", "sg_grup", "sg_dogum_var", "sg_dogum")


def sporcu_form_hatalari(yas, boy, kilo):
    """Alan → Türkçe hata. Boş alan "giriniz", alt sınırın altı açıklamalı. Boş sözlük: kayıt yapılabilir."""
    h = {}
    for alan, deger, bos, kucuk in (("Yaş", yas, "Yaşı giriniz.", "Yaş 4'ten küçük olamaz."),
                                    ("Boy (cm)", boy, "Boyu giriniz (cm).", "Boy 80 cm'den kısa olamaz."),
                                    ("Kilo (kg)", kilo, "Kiloyu giriniz (kg).", "Kilo 10 kg'dan az olamaz.")):
        if deger is None:
            h[alan] = bos
        elif float(deger) < SPORCU_FORM_ALT_SINIR[alan]:
            h[alan] = kucuk
    return h


def _sporcu_formunu_temizle():
    """'Başka sporcu ekle': formun alanlarını boşaltır."""
    for k in SPORCU_FORM_ALANLARI:
        st.session_state.pop(k, None)


def profil_uyarilari(boy, kilo, yas, cinsiyet, dogum=None, ad=""):
    uyarilar = []
    for alan, deger in (("Boy (cm)", boy), ("Kilo (kg)", kilo)):
        test_adi, degisken = PROFIL_MAKULLUK[alan]
        for u in makullukte_uyarilar(test_adi, {degisken: deger}, yas, cinsiyet, dogum, date.today()):
            uyarilar.append(u.replace(f"{test_adi} — {degisken}", alan))
    yas_dogumdan = tam_yas(dogum, date.today()) if dogum else None
    try:
        if yas_dogumdan is not None and yas not in (None, "") and int(float(yas)) != yas_dogumdan:
            uyarilar.append(f"Yaş {int(float(yas))} girildi ama doğum tarihine göre {yas_dogumdan} — biri yanlış olabilir.")
    except (TypeError, ValueError):
        pass
    try:
        if boy and kilo and float(boy) > 0 and abs(float(boy) - float(kilo)) < 0.01:
            uyarilar.append(f"Boy ve kilo aynı sayı ({_sayi_kisa(float(boy))}) — biri yanlış alana yazılmış olabilir.")
    except (TypeError, ValueError):
        pass
    return [f"{ad}: {u}" if ad else u for u in uyarilar]


# ── Test oturumu ──
def oturum_sutunu(test_adi, degisken):
    return f"{test_adi} › {degisken}"


def oturum_kayitlari(tablo, sporcu_bilgileri, testler, kategori, batarya, brans, tarih, oturum, yollar=None):
    """
    Toplu giriş tablosunu kayıtlara çevirir. Satır = sporcu ("Sporcu" sütunu), sütun = "Test › Değişken".
    Boş hücreler kaydedilmez; bir sporcunun bir testte en az bir dolu hücresi varsa o test kaydedilir
    (kısmi kayıt normaldir). Streamlit çağrısı yoktur.
    testler: {test_adi: [değişkenler]}; sporcu_bilgileri: {sporcu: profil satırı (dict)}.
    yollar: {test_adi: (kategori, batarya, branş)} — testler farklı kategorilerden seçildiyse (Paket 27).
    Dönen: (kayitlar, uyarilar) — uyarilar makullük ve hesaplama uyarılarıdır.
    """
    kayitlar, uyarilar = [], []
    for _, satir in tablo.iterrows():
        sporcu = satir["Sporcu"]
        bilgi = sporcu_bilgileri.get(sporcu, {})
        kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
        cins = str(bilgi.get("Cinsiyet", "")).strip()
        yas = tam_yas(bilgi.get(DOGUM_KOLON), tarih) or bilgi.get("Yaş")
        for test_adi, degiskenler in testler.items():
            degerler = {d: deger_metni(satir.get(oturum_sutunu(test_adi, d))) for d in degiskenler}
            if not any(degerler.values()):
                continue
            hesaplanan, h_uyari = turetilmis_degerler(test_adi, degerler, bilgi, kilo)
            uyarilar += [f"{sporcu}: {test_adi} — {u}" for u in h_uyari]
            tum = {**degerler, **{k: v for k, v in hesaplanan.items() if isinstance(v, (int, float))}}
            uyarilar += makullukte_uyarilar(test_adi, tum, yas, cins, bilgi.get(DOGUM_KOLON), tarih, sporcu)
            kat_, bat_, br_ = (yollar or {}).get(test_adi, (kategori, batarya, brans))
            kayitlar.append(test_kaydi_olustur(sporcu, bilgi, kat_, bat_, br_, test_adi, tarih,
                                               degerler, hesaplanan, "", oturum))
    return kayitlar, uyarilar


def oturum_secenekleri(df):
    """{oturum kimliği: etiket} — kayıt sırasının tersi (en yeni önce). Sonuçlar süzgeci ve karşılaştırma ortak."""
    if df is None or "Oturum" not in df.columns:
        return {}
    o = df["Oturum"].fillna("").astype(str).str.strip()
    d = df[(o != "") & (o != "nan")]
    et = {kim: f"{oturum_etiketi(grp.iloc[0])} · {grp['Sporcu'].nunique()} sporcu, {len(grp)} kayıt"
          for kim, grp in d.groupby("Oturum", sort=False)}
    return dict(reversed(list(et.items())))


# Paket 38d: Sporcu Karşılaştırma kapsamı. Bireysel = her sporcunun son ölçümü (eski davranış); Tek oturum = yalnız
# o oturumun ölçümleri; Oturumlar arası = iki oturumda da ölçülen sporcunun iki değeri ve farkı (yön tanımından
# "daha iyi / daha kötü"; yön yoksa yalnız fark). Hesap yok: kayıttaki değerler, oturum içinde son ölçüm.
KARSILASTIRMA_KAPSAMLARI = ("Bireysel", "Tek oturum", "Oturumlar arası")


def oturum_degerleri(df, test, degisken, oturum=None):
    """{sporcu: değer} — testin değişkeni; oturum verilirse yalnız o oturum; sporcu başına son ölçüm."""
    d = df[df["Test"].map(kanonik_test) == kanonik_test(test)].copy()
    if oturum is not None:
        d = d[d["Oturum"].astype(str) == str(oturum)] if "Oturum" in d.columns else d.iloc[0:0]
    if degisken not in d.columns or d.empty:
        return {}
    d["_v"] = pd.to_numeric(d[degisken], errors="coerce")
    if "Tarih_dt" not in d.columns:
        d["Tarih_dt"] = pd.to_datetime(d["Tarih"], format="%d.%m.%Y", errors="coerce")
    d = d.dropna(subset=["_v"]).sort_values("Tarih_dt", na_position="first")
    return {s: float(v) for s, v in d.groupby("Sporcu")["_v"].last().items()}


def oturumlar_arasi_fark(df, test, degisken, once, sonra):
    """İki oturumda da ölçülen sporcular: [{Sporcu, Önceki, Sonraki, Fark, Yorum}] — yorum sözcükle."""
    a = oturum_degerleri(df, test, degisken, once)
    b_ = oturum_degerleri(df, test, degisken, sonra)
    yon = degisken_yonu(test, degisken)
    satir = []
    for s in sorted(set(a) & set(b_)):
        fark = round(b_[s] - a[s], 2)
        if fark == 0:
            yorum = "değişmedi"
        elif yon is None:
            yorum = "arttı" if fark > 0 else "azaldı"
        else:
            yorum = "daha iyi" if ((fark < 0) if yon else (fark > 0)) else "daha kötü"
        satir.append({"Sporcu": s, "Önceki": a[s], "Sonraki": b_[s], "Fark": fark, "Yorum": yorum})
    return satir


def oturum_etiketi(satir):
    """Sonuç filtresinde gösterilecek oturum adı. Paket 38d: kullanıcı ad verdiyse "Ad (tarih)"."""
    ad = str(satir.get(OTURUM_ADI_KOLON, "") or "").strip()
    if ad and ad != "nan":
        return f"{ad} ({satir.get('Tarih', '')})"
    parcalar = [str(satir.get(k, "")) for k in ("Tarih", "Yer", "Batarya")]
    uyg = str(satir.get("Uygulayıcı", "") or "")
    return " — ".join(p for p in parcalar if p and p != "nan") + (f" ({uyg})" if uyg and uyg != "nan" else "")


# ════════════════════════════════════════════════════════════
# TEST GÖRSELLERİ (Paket 13-14) — uygulamanın kendi çizimleri; dışarıdan görsel yok.
# Üç katman:
#   1) ÇİZİM TAKIMI: tuval, zemin, figür iskeleti, çizgi kalınlıkları, yazı boyları (renk tg_renk() → CSS değişkeni)
#   2) HAREKET KİTAPLIĞI (hk_*): ortak hareketler — koşu, dönüşlü koşu, sıçrama, sekme, atma,
#      kavrama, oturarak uzanma, denge, antropometri. Yeni test görseli bunlardan üretilir.
#   3) SAHNELER: her test = bir hareket çağrısı + ekipman + ölçülen büyüklük + en çok üç yazı
#      (üstte başlık, altta not, ölçü okunun ucunda ya da kılavuzla bağlı bir etiket).
# Hareket bir kez oynar ve ÖLÇÜM ANINDA durur (fill="freeze"); döngü yok. Hareket azaltıldığında
# aynı sahnenin son karesi (durağan kopya) gösterilir.
# ════════════════════════════════════════════════════════════
import math as _math
from collections import namedtuple as _namedtuple

from olcut.gorseller.cizim import (   # Bölme Aşama 2: olcut/gorseller/cizim.py
    TG_TUVAL, TG_ZEMIN, TG_KALINLIK, TG_YAZI, TG_BASLIK_YAZI, TG_EN_COK_YAZI, TG_RENK, _TG_BOY, TG_TEMEL_POZ,
    TG_UCLAR, TG_ROL_KATMANI, TG_EN_YAKIN_UC, TG_SERIT_UST, TG_SERIT_ALT, TG_YAZI_PAYI, TG_CIZGI_PAYI, TG_SATIR,
    TG_OLCU_Y, TG_OZEL_ADLAR, _TG_RAKAM, _tg_xml_sekilleri, _tg_xml_kutulari, _tg_yon, tg_eklemler,
    _TG_FIGUR_CIZGILERI, _tg_d, _tg_parcalar, _tg_ara, _tg_kareler, _tg_anim, tg_poz, tg_yerlestir, TgSahne,
    TgHareket, _TG_PARKURLAR, TG_OLCEK, _TG_YOYO_KRITIK, _TG_YOYO2_KRITIK, _TG_WINGATE_KRITIK, _TG_WINGATE,
    _TG_YOYO_IR1, TG_HAREKET_KITAPLIGI, tg_kabugu)


from olcut.gorseller.hareketler import (   # Bölme Aşama 2: olcut/gorseller/hareketler.py
    _hk_kos_pozu, _hk_kos_anahtarlari, hk_duz_kos, hk_donuslu_kos, hk_dikey_sicrama, hk_sicrama_ani,
    hk_yana_sicrama, hk_tek_ayak_sekme, hk_atma, hk_kavrama, hk_oturarak_uzanma, hk_denge, hk_antropometri,
    hk_iz, hk_ikinci_figur, _hk_catmull, hk_kavisli_yol, _hk_paten_pozu, hk_paten, _hk_suplex, _hk_ayna,
    _hk_one_pozlari, _hk_one_devirme, hk_pedal, hk_nordic, hk_dinamometre, hk_iki_uke_atis, hk_uchikomi,
    _HK_GARD, _HK_TEKNIK, hk_vurus, hk_asilma_bukumlu, hk_asilma, hk_yan_adim, _hk_iki_parca, _hk_kollar_hedefe,
    _hk_kol_sec, _hk_yere_koy, _hk_uclari_ayir, _hk_ayir_hepsi, hk_uzun_atlama, hk_mekik, _hk_sinav_pozu,
    hk_sinav, hk_modifiye_barfiks, BENCH_KOL_UST, BENCH_KOL_ALT, BENCH_KAVRAMA, BENCH_ARA_ADIM,
    BARFIKS_ARA_ADIM, _hk_asili_barfiks, hk_bench_press, _hk_comelme_pozu, _hk_aci_yakin, hk_arka_comelme,
    hk_leg_press, _hk_ara_ekle, hk_sargent, hk_govde_kaldirma, hk_flamingo, hk_masa_dokunma, hk_omuz_esneme,
    hk_omuz_rotasyon, hk_top_sektirme, hk_top_yakala, hk_takla, hk_alttan_gec, hk_engel_ustu, hk_egil_al,
    _hk_yerinde, KAYAN_HIZ_ISTASYON, KAYAN_HIZ_GECIS, _hk_hiz_siniri, KAYAN_DURAKLAMA, _hk_hazir_durus,
    _hk_duraklat, KOORDINASYON_ISTASYONLARI, hk_koordinasyon_turu, hk_yana_kayma, hk_skipping, hk_topa_vurus,
    CAMSA_BECERILERI, _hk_tur_toplari, hk_camsa_turu, hk_servis, hk_serbest_stil, hk_split, _hk_iki_bag,
    _hk_oturus, hk_kurek_ergometre, hk_kayak_ergometre, _hk_bar_uzanis, hk_koparma, hk_silkme,
    hk_eggbeater_sicrama, hk_tutus)


from olcut.gorseller.sahneler import (   # Bölme Aşama 2: olcut/gorseller/sahneler.py
    _tg_parabol, _tg_direk, _tg_boy, _tg_oturma, _tg_kulac, _tg_esneklik, _tg_dikey, _tg_kavrama,
    _tg_saglik_topu, _tg_pro_agility, _tg_surat, _tg_koordinasyon_genel, _tg_cember, _tg_koordinasyon,
    _tg_mekik, _tg_geriye_denge, _tg_yana_sicrama, _tg_yana_platform, _tg_goz_el, _tg_tek_ayak,
    _tg_periyot_seridi, _tg_yoyo, _tg_imlec_atis, _tg_swft, _tg_sjft, _tg_gures_mac, _tg_paten_30,
    _tg_paten_6_30, _tg_s_turn, _tg_wingate, _tg_zemin_seridi, _tg_koni, _tg_fotosel, _tg_deneme_seridi,
    _tg_sprint, _tg_hizlanma_profili, _tg_rsa, _tg_list, _tg_30_15, _tg_parkur_bacaklari, _tg_parkur,
    _tg_sicrama_turleri, _tg_nordic, _tg_diz_dinamometre, _tg_minder, _tg_sjft_judo, _tg_ukft, _tg_vurus,
    _tg_mac, _tg_asilma, _tg_yan_adim, _tg_mat, _tg_uzun_atlama, _tg_mekik_kosusu, _tg_otur_uzan,
    _tg_govde_fleksiyonu, _tg_sinav, _tg_modifiye_barfiks, _tg_plaka, _tg_bench_press, _tg_arka_comelme,
    _tg_leg_press, _tg_barfiks, _tg_sargent, _tg_govde_kaldirma, _tg_bukumlu_asilma, _tg_flamingo,
    _tg_plate_tapping, _tg_omuz_esneme, _tg_omuz_rotasyon, _tg_top_sektirme, _tg_top_yakalama, _tg_top_firlatma,
    _tg_capl_genel, _tg_capl_parkur, _tg_tenis_servis, _tg_yuzme, _tg_split, _tg_kurek_ergometre,
    _tg_kayak_ergometre, _tg_halter, _tg_suda_sicrama, TEST_GORSELLERI, TEST_GORSELSIZ, tg_sahne,
    test_gorseli_html, test_gorseli_penceresi)


import functools as _functools



# ════════════════════════════════════════════════════════════
# YÖNLENDİRME EKRANI (Paket 16) — açılışta "Ne yapmak istiyorsunuz?"
# Kural tabanlı: yalnız sporcular.xlsx ve test_sonuclari.xlsx'te ne olduğunu söyler. Dış servis yok, internet
# gerekmez, tahmin/öneri üretmez. Tek kural dışı yönlendirme protokolden gelir: TSYT normları 7-11 yaş içindir.
# ════════════════════════════════════════════════════════════
import json as _json

YON_TSYT = ("Türkiye Sportif Yetenek Modeli (TSYT)", "TSYT Bataryası — 7-11 Yaş (GSB)")
YON_TSYT_YAS = (7, 11)
YON_LISTE_SINIRI = 5                 # ekranda adıyla gösterilen satır; fazlası katlanır
# Yarım batarya eşiği (Paket 32) — üçü birden: testlerin en az yarısı yapılmış, bataryadaki son ölçüm 6 haftadan
# eski değil, bataryanın yas_araligi sporcunun yaşını kapsıyor (aralık None ise bu şart aranmaz).
YON_YARIM_ORAN = 0.5
YON_YARIM_GUN = 42
YON_SUSTUR_ANAHTAR = "yarim_susturulan"   # ayarlar.json: [[sporcu, batarya], …] — "Bu bataryayı bitirmeyeceğim"


def ilgi_eki(ad):
    """Türkçe ilgi eki ('Deniz Aydın' → 'Deniz Aydın’ın', 'Ali Bir' → 'Ali Bir’in', 'Ece' → 'Ece’nin')."""
    ad = str(ad).strip()
    unluler = {"a": "ı", "ı": "ı", "A": "ı", "I": "ı", "e": "i", "i": "i", "E": "i", "İ": "i",
               "o": "u", "u": "u", "O": "u", "U": "u", "ö": "ü", "ü": "ü", "Ö": "ü", "Ü": "ü"}
    son = next((unluler[c] for c in reversed(ad) if c in unluler), "i")
    return f"{ad}’{'n' if ad[-1:] in unluler else ''}{son}n"


def yarim_susturulanlar():
    """Susturulan (sporcu, batarya) çiftleri — ayarlar.json'dan; dosya yoksa/bozuksa boş."""
    v = ayar_oku().get(YON_SUSTUR_ANAHTAR, [])
    return {(str(x[0]), str(x[1])) for x in v if isinstance(x, (list, tuple)) and len(x) == 2} if isinstance(v, list) else set()


def yarim_sustur(sporcu, batarya):
    """"Bu bataryayı bitirmeyeceğim": o sporcu + batarya bir daha yarım sayılmaz (başka sporcuyu etkilemez)."""
    s = yarim_susturulanlar() | {(str(sporcu), str(batarya))}
    ayar_yaz(YON_SUSTUR_ANAHTAR, sorted([list(x) for x in s]))


def yonlendirme_durumu(df_sporcu, df_test, katalog=None, bugun=None, susturulan=()):
    """
    Veride ne var: sporcu sayısı, sonuç sayısı, yarım kalan ve tamamlanan bataryalar (sporcu adıyla).
    Bütün testleri yapılmış batarya tamamdır. Eksik testi olan batarya yalnız ÜÇ şart birden sağlanırsa yarım
    sayılır (Paket 32 — tek test bataryayı "başlatmaz"): testlerin en az yarısı yapılmış; bataryadaki son ölçüm
    YON_YARIM_GUN günden eski değil; bataryanın yas_araligi sporcunun yaşını kapsıyor (None ise aranmaz; yaş ya da
    tarih bilinmiyorsa şart sağlanmış sayılmaz). susturulan: {(sporcu, batarya)} — o çift yarım sayılmaz.
    Tahmin yok: yalnız kayıtlı sonuçlar sayılır.
    """
    bugun = tarih_coz(bugun) or date.today()
    susturulan = {tuple(x) for x in susturulan}
    sp = _tablo_guvenli(df_sporcu, ["Ad", "Soyad", "Yaş"])
    ts = _tablo_guvenli(df_test, ["Sporcu", "Test", "Tarih"])
    adlar, yaslar = [], {}
    for _, r in sp.iterrows():
        ad = f"{'' if pd.isna(r['Ad']) else r['Ad']} {'' if pd.isna(r['Soyad']) else r['Soyad']}".strip()
        if ad and ad not in adlar:
            adlar.append(ad)
            y = tam_yas(r.get(DOGUM_KOLON), bugun)            # doğum tarihi varsa bugünkü yaş, yoksa profil yaşı
            if y is None:
                try:
                    y = None if pd.isna(r["Yaş"]) or str(r["Yaş"]).strip() == "" else int(float(r["Yaş"]))
                except (TypeError, ValueError):
                    y = None
            yaslar[ad] = y
    ts = ts[ts["Sporcu"].astype(str).isin(adlar)] if adlar else ts.iloc[0:0]
    yapilan = {a: set(ts.loc[ts["Sporcu"].astype(str) == a, "Test"].astype(str)) for a in adlar}
    yarim, tamam = [], []
    for (kat, bat), testler in katalog_bataryalari(katalog).items():
        ya = batarya_yas_araligi(kat, bat, katalog)
        for a in adlar:
            if not yapilan[a] & set(testler):
                continue
            eksik = [t for t in testler if t not in yapilan[a]]
            kayit = {"sporcu": a, "kategori": kat, "batarya": bat, "eksik": eksik, "toplam": len(testler)}
            if not eksik:
                tamam.append(kayit)
                continue
            satir = ts[(ts["Sporcu"].astype(str) == a) & ts["Test"].astype(str).isin(testler)]
            tarihler = [d_ for d_ in (tarih_coz(x) for x in satir["Tarih"]) if d_ is not None]
            son = max(tarihler) if tarihler else None
            yas = yaslar.get(a)
            if ((len(testler) - len(eksik)) >= YON_YARIM_ORAN * len(testler)            # a) en az yarısı
                    and son is not None and (bugun - son).days <= YON_YARIM_GUN          # b) son ölçüm ≤ 6 hafta
                    and (ya is None or (yas is not None and ya[0] <= yas <= ya[1]))     # c) yaş aralıkta
                    and (a, bat) not in susturulan):
                yarim.append(dict(kayit, son_olcum=son))
    if not adlar:
        durum = "sporcu_yok"
    elif ts.empty:
        durum = "sonuc_yok"
    else:
        durum = "sonuc_var"
    return {"durum": durum, "sporcular": adlar, "sonuc_sayisi": int(len(ts)),
            "sonucsuz": [a for a in adlar if not yapilan[a]], "yarim": yarim, "tamam": tamam}


def yarim_cumlesi(k):
    """'Deniz Aydın’ın TSYT bataryasında 2 test eksik: 20m Sürat, Mekik Koşusu'"""
    return (f"{ilgi_eki(k['sporcu'])} {batarya_kisa(k['batarya'])} bataryasında {len(k['eksik'])} test eksik: "
            + ", ".join(test_kisa(t, k["batarya"]) for t in k["eksik"]))


def tamam_cumlesi(k):
    return f"{ilgi_eki(k['sporcu'])} {batarya_kisa(k['batarya'])} bataryası tamam ({k['toplam']} test)."


# ════════════════════════════════════════════════════════════
# PAKET 27 — KENDİ TEST SETİNİ KURABİLME
# Kategori test seçimini kilitlemez: kategori ağacı gezinmek içindir; branş hangi testin ÖNERİLECEĞİNİ belirler,
# hangisinin YAPILABİLECEĞİNİ değil. Çalışma (ayarlar.json): ad, sıralı testler, gruplar, ölçüm zamanları, sporcu →
# grup ataması. Sporcu ve test dosyalarının yapısı değişmez.
# ════════════════════════════════════════════════════════════



def calisma_bos(ad=""):
    return {"ad": ad, "testler": [], "gruplar": [], "zamanlar": [], "atamalar": {}, "dokunuldu": ""}


def calismalar_oku():
    """Kayıtlı çalışmalar {ad: çalışma}. Bozuk kayıt atlanır; dosya yoksa boş."""
    ham = ayar_oku().get(CALISMA_ANAHTAR, {})
    out = {}
    if isinstance(ham, dict):
        for ad, c in ham.items():
            if isinstance(c, dict):
                d = calisma_bos(ad)
                for k in ("testler", "gruplar", "zamanlar"):
                    d[k] = [str(x) for x in c.get(k, []) if str(x).strip()]
                d["testler"] = list(dict.fromkeys(kanonik_test(x) for x in d["testler"]))   # eski ad → yeni (Paket 30)
                d["atamalar"] = {str(s): str(g) for s, g in (c.get("atamalar") or {}).items()}
                d["dokunuldu"] = str(c.get("dokunuldu") or "")          # Paket 33: ISO zaman damgası
                out[ad] = d
    return out


def calisma_dogrula(c, katalog=None):
    """Kaydetmeyi ENGELLEYEN sorunlar (ad, test, zaman yok; bilinmeyen test; tanımsız gruba atama)."""
    sorun = []
    if not str(c.get("ad", "")).strip():
        sorun.append("Çalışmanın adı yok.")
    if not c.get("testler"):
        sorun.append("En az bir test seçin.")
    adlar = {t["ad"] for t in katalog_testleri(katalog)}
    sorun += [f"Katalogda olmayan test: {t}" for t in c.get("testler", []) if t not in adlar]
    if len(set(c.get("testler", []))) != len(c.get("testler", [])):
        sorun.append("Aynı test iki kez seçilmiş.")
    if not c.get("zamanlar"):
        sorun.append("En az bir ölçüm zamanı girin (ör. Ön test).")
    gruplar = set(c.get("gruplar", []))
    sorun += [f"{s}: '{g}' grubu tanımlı değil." for s, g in c.get("atamalar", {}).items() if g and g not in gruplar]
    return sorun


def calisma_kaydet(c, eski_ad=None):
    """Çalışmayı ayarlar.json'a yazar (ad değiştiyse eskisi silinir). Sorun varsa yazmaz, sorunları döner."""
    c = {**calisma_bos(), **c}
    c["testler"] = [kanonik_test(t) for t in c["testler"]]
    sorun = calisma_dogrula(c)
    if sorun:
        return sorun
    hepsi = {k: v for k, v in calismalar_oku().items() if k != eski_ad}
    hepsi[c["ad"].strip()] = {**{k: c[k] for k in ("testler", "gruplar", "zamanlar", "atamalar")},
                              "dokunuldu": _dt_simdi().isoformat(timespec="seconds")}
    ayar_yaz(CALISMA_ANAHTAR, hepsi)
    return []


def calisma_dokun(ad):
    """Çalışmayla oturum kaydedilince: "en son dokunulan" çalışma öneride öne geçer (Paket 33)."""
    ham = ayar_oku().get(CALISMA_ANAHTAR, {})
    if isinstance(ham, dict) and isinstance(ham.get(ad), dict):
        ham[ad] = {**ham[ad], "dokunuldu": _dt_simdi().isoformat(timespec="seconds")}
        ayar_yaz(CALISMA_ANAHTAR, ham)


def calisma_sil(ad):
    ayar_yaz(CALISMA_ANAHTAR, {k: v for k, v in calismalar_oku().items() if k != ad})


def calisma_oturum_adi(calisma_adi, zaman):
    """Çalışmayla yapılan oturumda "Oturum" alanına yazılan değer: çalışma · ölçüm zamanı."""
    return f"{calisma_adi} · {zaman}"


def oturum_kimligi(calisma_adi, zaman, simdi):
    """Kaydedilen oturumun "Oturum" değeri: çalışmayla "çalışma · ölçüm zamanı", serbest seçimde "OT-zaman damgası"."""
    if calisma_adi and zaman:
        return calisma_oturum_adi(calisma_adi, zaman)
    return f"OT-{simdi:%Y%m%d-%H%M%S}"


def calisma_sporculari(c, gruplar=None):
    """Çalışmada gruba atanmış sporcular (gruplar verilirse yalnız o gruplar), atama sırasıyla."""
    return [s for s, g in c.get("atamalar", {}).items() if g and (not gruplar or g in gruplar)]


# ════════════════════════════════════════════════════════════
# PAKET 33 — ÖNERİ MOTORU: ana sayfa katalog değil, "şimdi şunu yap"
# Sıra (ilk eşleşen kazanır): 0 aktif çalışma · 1 yarım batarya (Paket 32 eşiği) · 2 yaşa uygun tarama bataryası ·
# 3 dalına özgü batarya (11 yaş altında atlanır; dalın katalogda karşılığı yoksa atlanır) · 4 en eski ölçümü tekrar.
# Kural tabanlı; tahmin yok. Olgunluk (PHV) kestirimi yok: kapı yalnız takvim yaşı. Her önerinin gerekçesi var.
# ════════════════════════════════════════════════════════════
ONERI_BRANS_YASI = 11                 # bu yaşın altında branşa özgü öneri yapılmaz (temel dönem)
ONERI_TARAMA_ONCELIK = (YON_TSYT[1],)  # 7-11 yaş: TSYT önce (aralığı yaşı kapsıyorsa)
# Sporcu Girişi'ndeki spor dalı → katalogdaki branş rafı. Karşılığı olmayan dal (ör. Bisiklet, Golf) burada yok:
# 3. kural o sporcu için atlanır (boş liste gösterilmez). Atletizmde katalog rafı sürat/güç testleridir: yalnız Sprint.
SPOR_DALI_BRANS = {
    "Güreş (Serbest)": "Güreş", "Güreş (Grekoromen)": "Güreş", "Judo": "Judo", "Karate": "Karate",
    "Taekwondo": "Taekwondo", "Kickboks": "Kickboks", "Muay Thai": "Muay Thai", "Boks": "Boks",
    "Jiujitsu (BJJ)": "BJJ (Jiujitsu)", "Sambo": "Sambo", "MMA": "MMA",
    "Futbol": "Futbol", "Basketbol": "Basketbol", "Voleybol": "Voleybol", "Hentbol": "Hentbol", "Rugbi": "Rugby",
    "Buz Hokeyi": "Buz Hokeyi", "Su Topu": "Su Topu",
    "Atletizm (Sprint)": "Atletizm", "Yüzme": "Yüzme", "Kürek": "Kürek", "Kano/Kayak": "Kano/Kayak",
    "Halter": "Halter", "Jimnastik": "Jimnastik", "Tenis": "Tenis", "Masa Tenisi": "Masa Tenisi",
    "Badminton": "Badminton", "Squash": "Squash",
}


def kayit_edilebilir(test):
    """Testin değişkeni var mı (sonucu kaydedilebilir mi)."""
    return bool((test_bilgisi(test) or {}).get("degiskenler"))


def brans_rafi(dal, katalog=None):
    """Spor dalının katalog rafı → (alt, branş, [raftaki test adları]) ya da None."""
    katalog = TEST_KATALOGU if katalog is None else katalog
    b = SPOR_DALI_BRANS.get(str(dal).strip())
    for alt, v in katalog.get("Branşa Özgü Testler", {}).items():
        if not str(alt).startswith("_") and isinstance(v, dict) and isinstance(v.get(b), dict):
            return alt, b, [t for t, tv in v[b].items() if not t.startswith("_") and isinstance(tv, dict)]
    return None


def _sporcu_yasi(r, bugun):
    y = tam_yas(r.get(DOGUM_KOLON), bugun)
    if y is None:
        try:
            v = r.get("Yaş")
            y = None if v is None or pd.isna(v) or str(v).strip() == "" else int(float(v))
        except (TypeError, ValueError):
            y = None
    return y


def sayi_iyelik(n):
    """Rakamla yazılan sayının iyelik eki: 1'i, 2'si, 4'ü, 6'sı, 9'u, 10'u, 20'si, 40'ı, 100'ü, 0'ı."""
    n = int(n)
    birler = {1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}
    onlar = {1: "u", 2: "si", 3: "u", 4: "ı", 5: "si", 6: "ı", 7: "i", 8: "i", 9: "ı"}
    if n == 0:
        ek = "ı"
    elif n % 10:
        ek = birler[n % 10]
    elif n % 100:
        ek = onlar[(n // 10) % 10]
    elif n % 1000:
        ek = "ü"                                          # yüz
    else:
        ek = "i"                                          # bin
    return f"{n}'{ek}"


def _hafta_metni(gun):
    return "bu hafta" if gun < 7 else f"{gun // 7} hafta önce"


def oneri_baglami(df_sporcu, df_test, calismalar=None, bugun=None, susturulan=(), katalog=None):
    """Öneri için bir kez okunan durum: sporcular (yaş, dal, grup), kayıtlar, batarya durumu, çalışmalar."""
    bugun = tarih_coz(bugun) or date.today()
    sp = _tablo_guvenli(df_sporcu, ["Ad", "Soyad", "Yaş"])
    ts = _tablo_guvenli(df_test, ["Sporcu", "Test", "Tarih", "Oturum"])
    ts = ts.assign(Test=ts["Test"].map(lambda t: kanonik_test(t) if isinstance(t, str) else t))
    sporcular = {}
    for _, r in sp.iterrows():
        ad = f"{'' if pd.isna(r['Ad']) else r['Ad']} {'' if pd.isna(r['Soyad']) else r['Soyad']}".strip()
        if ad and ad not in sporcular:
            g = r.get(GRUP_KOLON)
            sporcular[ad] = {"yas": _sporcu_yasi(r, bugun), "dal": str(r.get("Spor Dalı") or "").strip(),
                             "grup": "" if not _girildi(g) else str(g).strip()}
    return {"bugun": bugun, "sporcular": sporcular, "ts": ts, "katalog": katalog,
            "durum": yonlendirme_durumu(df_sporcu, ts, katalog, bugun=bugun, susturulan=susturulan),
            "susturulan": {tuple(x) for x in susturulan},
            "calismalar": calismalar_oku() if calismalar is None else calismalar}


def _yapilan(b, sporcu):
    ts = b["ts"]
    return set(ts.loc[ts["Sporcu"].astype(str) == sporcu, "Test"].astype(str))


def _son_olcum(b, sporcu, testler):
    ts = b["ts"]
    s = ts[(ts["Sporcu"].astype(str) == sporcu) & ts["Test"].astype(str).isin([kanonik_test(t) for t in testler])]
    d = [x for x in (tarih_coz(v) for v in s["Tarih"]) if x is not None]
    return max(d) if d else None


def calisma_durumu(b, ad):
    """
    Çalışmanın sıradaki ölçüm zamanı: atanmış sporculardan kaçı o zamanda ölçüldü, sıradaki kim. Ölçüldü =
    "çalışma · zaman" oturumunda çalışmanın (toplu girilebilen) bütün testleri kayıtlı. Her zaman tamamsa None.
    """
    c = b["calismalar"][ad]
    katilan = [s for s in calisma_sporculari(c) if s in b["sporcular"]]
    if not katilan:
        return None
    gerek = [t for t in c["testler"] if t not in TOPLU_GIRIS_DISI and kayit_edilebilir(t)]
    ts = b["ts"]
    for z in c["zamanlar"]:
        o = ts[ts["Oturum"].astype(str) == calisma_oturum_adi(ad, z)]
        olculen = [s for s in katilan
                   if (set(gerek) <= set(o.loc[o["Sporcu"].astype(str) == s, "Test"].astype(str)) if gerek
                       else (o["Sporcu"].astype(str) == s).any())]
        if len(olculen) < len(katilan):
            kalan = [s for s in katilan if s not in olculen]
            return {"calisma": ad, "zaman": z, "toplam": len(katilan), "olculen": len(olculen), "kalan": kalan,
                    "atamalar": c["atamalar"]}
    return None


def calisma_son_dokunma(b, ad):
    """Damga (kaydetme / oturum) ile çalışmanın oturumlarındaki en yeni test tarihinin büyüğü; sıralama anahtarı."""
    from datetime import datetime as _dt
    adaylar = []
    try:
        adaylar.append(_dt.fromisoformat(b["calismalar"][ad].get("dokunuldu", "")))
    except (TypeError, ValueError):
        pass
    ts = b["ts"]
    o = ts[ts["Oturum"].astype(str).str.startswith(f"{ad} · ")]
    d = [x for x in (tarih_coz(v) for v in o["Tarih"]) if x is not None]
    if d:
        adaylar.append(_dt.combine(max(d), _dt.min.time()))
    return max(adaylar) if adaylar else _dt.min


def _calisma_onerisi(cd, sporcu):
    kalan = len(cd["kalan"])
    return {"kural": 0, "sporcu": sporcu, "calisma": cd["calisma"],
            "baslik": (f"{cd['calisma']} · {cd['zaman']} — {cd['toplam']} sporcunun {sayi_iyelik(cd['olculen'])}"
                       f" ölçüldü, sıradaki: {sporcu}"
                       + (f" ({cd['atamalar'].get(sporcu)})" if cd["atamalar"].get(sporcu) else "")),
            "gerekce": (f"başlanmış çalışma, {kalan} sporcu kaldı" if cd["olculen"]
                        else f"kurulmuş çalışma, henüz ölçüm yok; {kalan} sporcu kaldı"),
            "eylem": {"tur": "calisma", "calisma": cd["calisma"], "zaman": cd["zaman"], "sporcu": sporcu,
                      "grup": cd["atamalar"].get(sporcu, "")}}


def aktif_calismalar(b):
    """Sıradaki ölçümü olan çalışmalar, en son dokunulan önce."""
    out = [cd for cd in (calisma_durumu(b, ad) for ad in b["calismalar"]) if cd]
    return sorted(out, key=lambda cd: calisma_son_dokunma(b, cd["calisma"]), reverse=True)


def calisma_onerileri(b, ad=None):
    """0. kural. ad verilirse yalnız o çalışma; diğer aktif çalışmalar alternatif olarak arkadan gelir."""
    aktif = aktif_calismalar(b)
    if ad is not None:
        aktif = [cd for cd in aktif if cd["calisma"] == ad] + [cd for cd in aktif if cd["calisma"] != ad]
    return [_calisma_onerisi(cd, cd["kalan"][0]) for cd in aktif]


def _tarama_adaylari(b, yas):
    """Yaşı kapsayan (yas_araligi None olmayan) tarama bataryaları; 7-11 için TSYT önce."""
    if yas is None:
        return []
    adaylar = [(k, t) for k, t in katalog_bataryalari(b["katalog"]).items()
               if (lambda ya: ya is not None and ya[0] <= yas <= ya[1])(batarya_yas_araligi(*k, b["katalog"]))]
    return sorted(adaylar, key=lambda x: (x[0][1] not in ONERI_TARAMA_ONCELIK, ))


def sporcu_onerileri(b, sporcu):
    """Bir sporcu için öneriler, kural sırasıyla (ilk eşleşen kazanır; sonrakiler alternatif)."""
    bilgi = b["sporcular"].get(sporcu)
    if bilgi is None:
        return []
    yas, grup = bilgi["yas"], bilgi["grup"]
    yapilan = _yapilan(b, sporcu)
    out = []
    # 0) aktif çalışmada bu sporcunun sırası gelmiş
    for cd in aktif_calismalar(b):
        if sporcu in cd["kalan"]:
            out.append(_calisma_onerisi(cd, sporcu))
    # 1) yarım batarya (Paket 32: üç şart + susturma)
    for k in b["durum"]["yarim"]:
        if k["sporcu"] == sporcu:
            n = len(k["eksik"])
            out.append({"kural": 1, "sporcu": sporcu, "batarya": k["batarya"], "kategori": k["kategori"],
                        "baslik": f"{sporcu} · {batarya_kisa(k['batarya'])} bataryasını tamamla ({n} test)",
                        "gerekce": f"başlanmış batarya, {n} test kaldı",
                        "eylem": {"tur": "oturum", "kategori": k["kategori"], "batarya": k["batarya"],
                                  "testler": list(k["eksik"]), "sporcu": sporcu, "grup": grup}})
    # 2) yaşa uygun tarama bataryası tamamlanmamış
    adaylar = _tarama_adaylari(b, yas)
    tamam_tarama = [k for k, t in adaylar if set(t) <= yapilan]
    yarimdaki = {o["batarya"] for o in out if o["kural"] == 1}
    bekleyen = [] if tamam_tarama else [(k, t) for k, t in adaylar if (sporcu, k[1]) not in b["susturulan"]]
    tarama_bekliyor = bool(bekleyen)                     # yarım (1. kural) olan da tarama bekliyor sayılır
    if any(k[1] in yarimdaki for k, _ in adaylar):
        bekleyen = []                                    # yaşa uygun tarama zaten sürüyor (1. kural): ikinci tarama önerilmez
    if bekleyen:
        (kat, bat), testler = bekleyen[0]
        eksik = [t for t in testler if t not in yapilan]
        ya = batarya_yas_araligi(kat, bat, b["katalog"])
        out.append({"kural": 2, "sporcu": sporcu, "batarya": bat, "kategori": kat,
                    "baslik": (f"{sporcu} · {batarya_kisa(bat)} bataryasını uygula"
                               + (f" ({len(eksik)} test)" if len(eksik) == len(testler)
                                  else f" (kalan {len(eksik)} test)")),
                    "gerekce": f"yaşa uygun norm var: {batarya_kisa(bat)} {ya[0]}-{ya[1]} yaş, sporcu {yas} yaşında",
                    "eylem": {"tur": "oturum", "kategori": kat, "batarya": bat, "testler": eksik,
                              "sporcu": sporcu, "grup": grup}})
    # 3) tarama tamam (ya da yaşa uygun tarama yok) → dalına özgü batarya; 11 yaş altında ve karşılıksız dalda atlanır
    raf = brans_rafi(bilgi["dal"], b["katalog"])
    brans_testleri = []
    if raf:
        alt, brans, raf_testleri = raf
        brans_testleri = [t for t in raf_testleri if kayit_edilebilir(t)]
        eksik = [t for t in brans_testleri if kanonik_test(t) not in yapilan]
        if (yas is not None and yas >= ONERI_BRANS_YASI and not tarama_bekliyor and eksik):
            if all(t in TOPLU_GIRIS_DISI for t in eksik):
                eylem = {"tur": "test_uygula", "sporcu": sporcu, "yol": ("Branşa Özgü Testler", alt, brans),
                         "test": eksik[0]}
            else:
                eylem = {"tur": "oturum", "kategori": "Branşa Özgü Testler", "batarya": alt, "brans": brans,
                         "testler": [t for t in eksik if t not in TOPLU_GIRIS_DISI], "sporcu": sporcu, "grup": grup}
            out.append({"kural": 3, "sporcu": sporcu, "batarya": brans, "kategori": "Branşa Özgü Testler",
                        "baslik": f"{sporcu} · {brans} testleri ({len(eksik)} test)",
                        "gerekce": f"dalına özgü ölçüm: {bilgi['dal']}",
                        "eylem": eylem})
    # 4) hepsi tamam → son ölçümü en eski olanı tekrar
    tekrar = []
    for k in b["durum"]["tamam"]:
        if k["sporcu"] == sporcu:
            testler = katalog_bataryalari(b["katalog"])[(k["kategori"], k["batarya"])]
            tekrar.append((_son_olcum(b, sporcu, testler), batarya_kisa(k["batarya"]),
                           {"tur": "oturum", "kategori": k["kategori"], "batarya": k["batarya"], "testler": testler,
                            "sporcu": sporcu, "grup": grup}))
    if raf and brans_testleri and all(kanonik_test(t) in yapilan for t in brans_testleri):
        tekrar.append((_son_olcum(b, sporcu, brans_testleri), f"{raf[1]} testleri",
                       {"tur": "oturum", "kategori": "Branşa Özgü Testler", "batarya": raf[0], "brans": raf[1],
                        "testler": [t for t in brans_testleri if t not in TOPLU_GIRIS_DISI], "sporcu": sporcu,
                        "grup": grup}))
    for son, ad_, eylem in sorted([x for x in tekrar if x[0] is not None], key=lambda x: x[0]):
        out.append({"kural": 4, "sporcu": sporcu, "batarya": ad_,
                    "baslik": f"{sporcu} · {ad_} — tekrar ölç",
                    "gerekce": f"son ölçüm {_hafta_metni((b['bugun'] - son).days)}",
                    "eylem": eylem})
    return [o for o in out if str(o.get("gerekce", "")).strip()]          # gerekçesiz öneri gösterilmez


def oneri_secenekleri(b):
    """Seçici: aktif çalışmalar ("calisma::ad") ve sporcular ("sporcu::ad"); varsayılan = en öncelikli öneri."""
    calisma = [f"calisma::{cd['calisma']}" for cd in aktif_calismalar(b)]
    sporcu = [f"sporcu::{s}" for s in b["sporcular"]]
    varsayilan = calisma[0] if calisma else None
    if varsayilan is None and sporcu:
        sira = {s: min([o["kural"] for o in sporcu_onerileri(b, s)] or [9]) for s in b["sporcular"]}
        varsayilan = f"sporcu::{min(b['sporcular'], key=lambda s: sira[s])}"
    return calisma + sporcu, varsayilan


def oneriler(b, secim):
    """Seçime göre öneri listesi: ilki ana öneri, ikincisi alternatif."""
    tur, _, ad = str(secim or "").partition("::")
    if tur == "calisma":
        return calisma_onerileri(b, ad)
    if tur == "sporcu":
        return sporcu_onerileri(b, ad)
    return []


# ── H) Görselsiz testlerde boş alan yerine neden ──
def gorselsiz_metni(test_adi):
    """Görseli bilerek olmayan test için ekranda yazılacak cümle; görselli ya da bilinmeyen testte None."""
    neden = TEST_GORSELSIZ.get(kanonik_test(test_adi))
    return f"Bu test için görsel yok — {neden}" if neden else None


# ── Paket 27: sıralı test listesi (↑ ↓) ve çalışma düzenleyici ──
def _sira_tasi(anahtar, i, yon):
    """Sıralı listede i. testi bir yukarı (yon=-1) ya da aşağı (yon=+1) taşır (düğme geri çağrısı)."""
    s = list(st.session_state.get(anahtar, []))
    j = i + yon
    if 0 <= i < len(s) and 0 <= j < len(s):
        s[i], s[j] = s[j], s[i]
        st.session_state[anahtar] = s


def sira_birlestir(onceki, secilenler):
    """Önceki sırayı korur: seçimden çıkanlar düşer, yeni seçilenler sona eklenir."""
    return [t for t in onceki if t in secilenler] + [t for t in secilenler if t not in onceki]


def _sira_cikar(t, kaynaklar):
    """Testi sıralı listeye getiren seçimlerden çıkarır (arama eklemesi, ağaç seçimi; takma adlı raf adı dahil)."""
    for k in kaynaklar:
        if isinstance(st.session_state.get(k), list):
            st.session_state[k] = [x for x in st.session_state[k] if kanonik_test(x) != t]


def _sira_listesi(onek, secilenler, kaynaklar=()):
    """
    Seçilen testleri sıralı gösterir (adın yanında ölçtüğü nitelik); ↑ ↓ ile sıra değişir, ✕ testi çıkarır
    (kaynaklar: testi getiren seçimlerin anahtarları). Sıralı listeyi döner.
    """
    anahtar = f"{onek}::sira"
    sira = sira_birlestir(st.session_state.get(anahtar, []), list(secilenler))
    st.session_state[anahtar] = sira
    for i, t in enumerate(sira):
        c1, c2, c3, c4 = st.columns([10, 1, 1, 1])
        yol_, diger_ = test_izi_parcalari(t)                       # iz çubuğu (Paket 33)
        c1.markdown(f"{i + 1}. {_html.escape(test_etiketli(t))}  \n<span style='font-size:0.8em;opacity:0.75'>"
                    f"📍 {_html.escape(yol_)}" + (f" — ayrıca: {_html.escape(', '.join(diger_[:ONERI_IZ_SINIRI]))}"
                                                 + (f" ve {len(diger_) - ONERI_IZ_SINIRI} rafta daha"
                                                    if len(diger_) > ONERI_IZ_SINIRI else "") if diger_ else "")
                    + "</span>", unsafe_allow_html=True)
        c2.button("↑", key=f"{anahtar}::yukari::{i}", disabled=i == 0, on_click=_sira_tasi, args=(anahtar, i, -1),
                  help="Yukarı taşı")
        c3.button("↓", key=f"{anahtar}::asagi::{i}", disabled=i == len(sira) - 1, on_click=_sira_tasi,
                  args=(anahtar, i, 1), help="Aşağı taşı")
        c4.button("✕", key=f"{anahtar}::cikar::{i}", on_click=_sira_cikar, args=(t, tuple(kaynaklar)),
                  disabled=not kaynaklar, help="Listeden çıkar")
    return list(st.session_state[anahtar])


def _ot_ekle(ad):
    """Arama panelinden "Ekle": test sıralı listeye düşer (kategori ağacındaki seçim değişmez)."""
    ek = list(st.session_state.get("ot::ek", []))
    if kanonik_test(ad) not in ek:
        ek.append(kanonik_test(ad))
    st.session_state["ot::ek"] = ek


def _virgullu(metin):
    return [p.strip() for p in str(metin).split(",") if p.strip()]


def _calisma_duzenleyici(sporcu_adlari):
    """Çalışma kur / düzenle: ad, sıralı testler (aranabilir, kategoriden bağımsız), gruplar, ölçüm zamanları, atama."""
    calismalar = calismalar_oku()
    yeni_etiket = "➕ Yeni çalışma"
    secim = st.selectbox("Çalışma", [yeni_etiket] + list(calismalar), key="cl_secim")
    c = calismalar.get(secim, calisma_bos())
    k = f"cl::{secim}"
    ad = st.text_input("Çalışmanın adı", value=c["ad"], key=f"{k}::ad", placeholder="ör. NHE Tez Çalışması")
    ara = st.text_input("Test ara (kategoriden bağımsız)", key=f"{k}::ara", placeholder="ör. sürat, çeviklik, Nordic")
    bulunan = [t["ad"] for t in test_ara(ara)] if ara.strip() else []
    secenek = list(dict.fromkeys(c["testler"] + st.session_state.get(f"{k}::testler", []) + bulunan))
    secili = coklu_secim("Testler", secenek, default=c["testler"], key=f"{k}::testler", format_func=test_etiketli,
                            help="Arama kutusuna yazın, sonuçlardan seçin; sıra aşağıda düzenlenir.")
    sira = _sira_listesi(k, secili, (f"{k}::testler",)) if secili else []
    g1, g2 = st.columns(2)
    gruplar = _virgullu(g1.text_input("Gruplar (virgülle)", value=", ".join(c["gruplar"]), key=f"{k}::gruplar",
                                      placeholder="ör. Kontrol, Deney"))
    zamanlar = _virgullu(g2.text_input("Ölçüm zamanları (virgülle)", value=", ".join(c["zamanlar"]),
                                       key=f"{k}::zamanlar", placeholder="ör. Ön test, Ara test, Son test"))
    atama = {}
    if gruplar and sporcu_adlari:
        tablo = pd.DataFrame({"Sporcu": list(sporcu_adlari),
                              "Grup": [c["atamalar"].get(s, "") if c["atamalar"].get(s, "") in gruplar else ""
                                       for s in sporcu_adlari]})
        duz = st.data_editor(tablo, hide_index=True, num_rows="fixed", width="stretch",
                             key=f"{k}::atama::{'|'.join(gruplar)}",
                             column_config={"Sporcu": st.column_config.TextColumn("Sporcu", disabled=True),
                                            "Grup": st.column_config.SelectboxColumn("Grup", options=[""] + gruplar)})
        atama = {r["Sporcu"]: r["Grup"] for _, r in duz.iterrows() if isinstance(r["Grup"], str) and r["Grup"]}
    yeni = {"ad": ad.strip(), "testler": sira, "gruplar": gruplar, "zamanlar": zamanlar, "atamalar": atama}
    for u in sira_uyarilari(sira):                                  # bildirir, engellemez
        st.warning(f"Sıra uyarısı: {u}", icon=":material/info:")
    b1, b2 = st.columns(2)
    if b1.button("💾 Çalışmayı kaydet", type="primary", key=f"{k}::kaydet"):
        sorun = calisma_kaydet(yeni, eski_ad=secim if secim in calismalar else None)
        if sorun:
            st.error("Kaydedilmedi:\n\n" + "\n".join(f"- {s}" for s in sorun))
        else:
            st.success(f"✅ '{yeni['ad']}' kaydedildi ({len(sira)} test, {len(zamanlar)} ölçüm zamanı). "
                       "Test Oturumu'nda 'Çalışma' seçeneğiyle kullanılabilir.")
    if secim in calismalar and b2.button("🗑 Çalışmayı sil", key=f"{k}::sil"):
        calisma_sil(secim)
        st.success(f"'{secim}' silindi. Kayıtlı test sonuçları etkilenmez.")


# ── düğme geri çağrıları: hedef sayfanın seçim kutularını önceden doldurur ──
def _git_test_uygula(sporcu=None, yol=None, test=None):
    st.session_state["sayfa"] = "Test Uygula"
    if sporcu:
        st.session_state["tu_sporcu"] = sporcu
    if yol and test:
        kat, alt, brans = yol
        st.session_state["tu_mod"] = "📂 Kategoriye Göre"
        st.session_state["tu_kategori"] = kat
        if alt is not None:
            st.session_state[f"tu_alt::{kat}"] = alt
        if brans is not None:
            st.session_state[f"tu_brans::{kat}::{alt}"] = brans
        st.session_state[f"tu_test::{kat}::{alt}::{brans}"] = test


def _git_oturum(kategori, batarya, testler=None, sporcu=None, grup=None, brans=None):
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ot_adim"] = 1                         # Paket 38b: önerilen seçimler Adım 1'de görünür
    st.session_state["ot_kaynak"] = "Serbest seçim"
    st.session_state["ot_kategori"] = kategori
    st.session_state["ot_batarya"] = batarya
    if brans is not None:
        st.session_state["ot_brans"] = brans
    if testler:
        for k_ in [k_ for k_ in st.session_state if str(k_).startswith("ot_testler_")] + ["ot::ek", "ot::sira"]:
            st.session_state.pop(k_, None)                      # yalnız önerilen testler (Paket 33)
        st.session_state[f"ot_testler_{kategori}_{batarya}_{brans}"] = list(testler)
    if sporcu:
        st.session_state["ot_gruplar"] = [grup or "(Grubu girilmemiş)"]
        st.session_state[f"ot_sporcular_{grup or '(Grubu girilmemiş)'}"] = [sporcu]


def _git_calisma(calisma, zaman, sporcu=None, grup=""):
    """Test Oturumu: çalışma + ölçüm zamanı + (varsa) sporcu seçili açılır."""
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ot_adim"] = 1
    st.session_state["ot_kaynak"] = "Çalışma"
    st.session_state["ot_calisma"] = calisma
    st.session_state[f"ot_zaman::{calisma}"] = zaman
    if sporcu and grup:
        st.session_state[f"ot_c_gruplar::{calisma}"] = [grup]
        st.session_state[f"ot_c_sporcular::{calisma}::{grup}"] = [sporcu]


def _oneri_git(eylem):
    """[Devam et]: önerinin eylemi ilgili sayfayı seçimleri dolu açar."""
    e = dict(eylem)
    tur = e.pop("tur")
    if tur == "calisma":
        _git_calisma(e["calisma"], e["zaman"], e.get("sporcu"), e.get("grup", ""))
    elif tur == "oturum":
        _git_oturum(e["kategori"], e["batarya"], e.get("testler"), e.get("sporcu"), e.get("grup", ""), e.get("brans"))
    elif tur == "test_uygula":
        _git_test_uygula(e.get("sporcu"), e.get("yol"), e.get("test"))


def _git_sonuclar(sporcu):
    st.session_state["sayfa"] = "Sonuçları Görüntüle"
    st.session_state["sonuc_oturum"] = "Tüm kayıtlar"
    st.session_state["sonuc_sporcu"] = sporcu


def konum_sekme_sirasi(yas):
    """16 yaş altında (ya da yaş bilinmezken) varsayılan görünüm kendi değişimi; konum ikinci sekmede."""
    y = _yas_degeri(yas)
    return (["Kendi değişimin", "Grup içi konum"] if y is None or y < KENDI_DEGISIM_YASI
            else ["Grup içi konum", "Kendi değişimin"])


@st.dialog("Grup içi konum ve gelişim", width="large")
def grup_konum_penceresi(sporcu, df_test):
    """Sporcu kartından açılır: test + değişken seçilir; kendi değişimi ve aynı yaş bandı/cinsiyetteki konumu."""
    df_sp = pd.read_excel(SPORCU_DOSYA) if os.path.exists(SPORCU_DOSYA) else pd.DataFrame()
    ciftler = rapor_konum_degiskenleri(df_test, sporcu)
    if not ciftler:
        st.info("Bu sporcunun sayısal test sonucu yok.")
        return
    secim = st.selectbox("Test ve değişken", ciftler, format_func=lambda c: f"{c[0]} — {c[1]}", key="gk_secim")
    test, degisken = secim
    yas = _profil_haritasi(df_sp).get(sporcu, {}).get("Yaş")
    sekmeler = konum_sekme_sirasi(yas)
    gorunum = dict(zip(sekmeler, st.tabs(sekmeler)))
    with gorunum["Kendi değişimin"]:
        o = gelisim_ozeti(df_test, sporcu, test, degisken)
        # Paket 38a: raporlarla aynı kart (gerçek değerli, eksen terslenmez); tek ölçümde ilk ölçüm tablosu
        st.markdown(gelisim_bolumu_html([o], {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}),
                    unsafe_allow_html=True)
    with gorunum["Grup içi konum"]:
        k = grup_ici_konum(df_test, df_sp, sporcu, test, degisken)
        for m in konum_metinleri(k):
            st.markdown(m)
        if k.get("durum") == "tamam":
            st.markdown(konum_seridi_svg(k), unsafe_allow_html=True)
            st.caption("Büyük nokta: bu sporcu · çizgi: grup ortalaması · küçük noktalar: havuzdaki öbür ölçümler "
                       "(isimsiz).")


def ozet_kartlari_html(ogeler):
    """Sonuçlar üstündeki özet kartları: dar ekranda alt alta kayar, uzun değer (tarih) kesilmez."""
    return ('<div class="sp-ozet" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));'
            f'gap:{b(1.5)};margin:{b(1)} 0 {b(2)}">'
            + "".join(f'<div class="sp-kart" style="margin:0;border-left-color:{renk_css("ana")}">'
                      f'<span class="sp-etiket">{_html.escape(str(e))}</span>'
                      f'<div class="sp-deger" style="font-size:1.375rem">{_html.escape(str(d))}</div></div>'
                      for e, d in ogeler) + "</div>")


def sekme_hatasi(hata):
    """Bir sekmenin hatası öbürlerini durdurmaz: sade Türkçe uyarı, teknik iz 'Ayrıntı' açılırında."""
    import traceback as _tb
    st.warning("Bu bölüm şu an gösterilemiyor; öbür sekmeler çalışmaya devam ediyor.", icon=":material/error:")
    with st.expander("Ayrıntı"):
        st.code("".join(_tb.format_exception(type(hata), hata, hata.__traceback__)), language=None)


def _git_rapor(sporcu):
    st.session_state["sayfa"] = "Raporlar"
    st.session_state["rapor_sporcu"] = sporcu


def _gecerli_secim(anahtar, secenekler):
    """Önceden doldurulmuş seçim artık seçeneklerde yoksa bırakılır (kutu varsayılana döner, hata vermez)."""
    if anahtar in st.session_state and st.session_state[anahtar] not in list(secenekler):
        del st.session_state[anahtar]


def _yonlendirme_gizle_degisti():
    ayar_yaz("yonlendirme_gizle", bool(st.session_state.get("yon_gizle")))


def yonlendirme_ekrani():
    """'Ne yapmak istiyorsunuz?' — durum dosyalardan okunur; her düğme ilgili sayfayı seçimleri dolu açar."""
    df_sp = tablo_oku(SPORCU_DOSYA)
    df_ts = test_tablosu_duzelt(tablo_oku(TEST_DOSYA))
    b = oneri_baglami(df_sp, df_ts, susturulan=yarim_susturulanlar())
    st.markdown("#### Ne yapmak istiyorsunuz?")

    if not b["sporcular"]:
        # B) boş durum: tek düğmenin üstünde en fazla üç satır tanıtım; veri gelince görünmez
        st.markdown("Ölçüt, sporcunun test sonucunu yaşına ve cinsiyetine uygun normla karşılaştırır.  \n"
                    "**1.** Sporcu ekle → **2.** Test uygula → **3.** Sonucu gör, rapor al.")
        st.button("İlk sporcuyu ekle", icon=":material/person_add:", type="primary", width="stretch",
                  key="yon::ilk", on_click=_sayfaya_git, args=("Sporcu Girişi",))
    else:
        secenekler, varsayilan = oneri_secenekleri(b)
        _gecerli_secim("yon_secim", secenekler)
        secim = st.selectbox("Kim için?", secenekler, index=secenekler.index(varsayilan), key="yon_secim",
                             format_func=lambda s: ("Çalışma: " if s.startswith("calisma::") else "")
                             + s.partition("::")[2])
        liste = oneriler(b, secim)
        if liste:
            o = liste[0]
            with st.container(border=True):
                st.markdown(f"**{_html.escape(o['baslik'], quote=False)}**")
                st.caption(f"Neden: {o['gerekce']}")
                c1, c2 = st.columns([1, 1], vertical_alignment="center")
                c1.button("Devam et", icon=":material/arrow_forward:", type="primary", width="stretch",
                          key="yon::devam", on_click=_oneri_git, args=(o["eylem"],))
                if o["kural"] == 1:                                    # Paket 32: susturma yarım önerinin yanında
                    c2.button("Bu bataryayı bitirmeyeceğim", key="yon::sustur", icon=":material/do_not_disturb_on:",
                              width="stretch", on_click=yarim_sustur, args=(o["sporcu"], o["batarya"]),
                              help="Bu sporcu için bu batarya bir daha yarım sayılmaz (başka sporcuları etkilemez).")
            if len(liste) > 1:
                a = liste[1]
                st.button(f"Ya da: {a['baslik']}", key="yon::alternatif", type="tertiary",
                          on_click=_oneri_git, args=(a["eylem"],), help=f"Neden: {a['gerekce']}")
        else:
            st.markdown("**Önerecek bir şey yok.**")
        st.button("Başka bir test seç →", key="yon::baska", type="tertiary",
                  on_click=_git_test_uygula, args=(secim.partition("::")[2] if secim.startswith("sporcu::") else None,))
        # Paket 34 E: kapalıyken yalnız başlık; açılınca ad + kategori süzgeci, sonuçlar yol bilgisiyle ve "Uygula"
        with st.expander("Test ara", icon=":material/search:", expanded=False):
            tum = katalog_testleri()
            kategoriler = list(dict.fromkeys(t["kategori"] for t in tum))
            a1, a2 = st.columns([2, 1])
            sorgu = a1.text_input("Test adı", key="yon_ara",
                                  placeholder=f"{len(tum)} test arasında ad ya da nitelik ile ara (ör. Yo-Yo, sürat)")
            kat = a2.selectbox("Kategori", ["Tüm kategoriler"] + kategoriler, key="yon_ara_kat")
            kat = None if kat == "Tüm kategoriler" else kat
            ara_sporcu = secim.partition("::")[2] if secim.startswith("sporcu::") else None
            if sorgu.strip() or kat:
                bulunan = test_ara(sorgu, kat)
                st.caption(f"{len(bulunan)} test bulundu" + (" — ilk 12 gösteriliyor" if len(bulunan) > 12 else ""))
                for i, t in enumerate(bulunan[:12]):
                    c1, c2 = st.columns([3, 1], vertical_alignment="center")
                    c1.markdown(f"{_html.escape(test_etiketli(t['ad']))}  \n<span style='font-size:0.85em'>"
                                f"{_html.escape(' › '.join(p for p in t['yol'] if p))}</span>", unsafe_allow_html=True)
                    c2.button("Uygula", key=f"yon::ara::{i}", width="stretch",
                              on_click=_git_test_uygula, args=(ara_sporcu, t["yol"], t["ad"]))
    st.checkbox("Açılışta bu ekranı gösterme (menüden yine açılır)", key="yon_gizle",
                value=bool(ayar_oku().get("yonlendirme_gizle", False)), on_change=_yonlendirme_gizle_degisti)


# ════════════════════════════════════════════════════════════
# TEST OTURUMU — ADIM ADIM (Paket 38b)
# Testler → Sporcular → Oturum bilgisi → Değerler. Her adımda tek ana düğme (sabit alt çubukta, sağda).
# Değerler iki kipte: SIRADAKİ (ekranda tek sporcu, tek test; telefon/tablet varsayılanı) ve TABLO (bilgisayar).
# Her değişiklik TASLAĞA yazılır (oturum durumu + diskte oturum_taslagi.json); xlsx'e yalnız "Oturumu kaydet".
# Ölçüm sırasında karşılaştırma (norm, yaşıt, sıralama) GÖSTERİLMEZ; olağandışı değer uyarılır, engellenmez.
# Kayıt satırları eski yolla kurulur (oturum_kayitlari → test_kaydi_olustur): hesap ve kayıt biçimi aynı.
# ════════════════════════════════════════════════════════════
OT_ADIMLAR = ("Testler", "Sporcular", "Oturum bilgisi", "Değerler")
OT_KIPLER = ("Sıradaki", "Tablo")
TASLAK_DOSYA = "oturum_taslagi.json"
NOT_DEGISKENI = "Not"                 # tablo kipinde test başına not sütunu: "Test › Not" (xlsx'te "Notlar" alanı)
OT_AYKIRI_SORU = "Bu değer olağan aralığın dışında, doğru mu?"
OT_TASLAK_NOTU = "✓ Taslak otomatik kaydedildi"
OT_KORUNMAYAN = ("ot_g::", "ot_n::", "ot_nm::", "ot_tablo", "ot::ara::", "ot::sira::")
_MOBIL_AJAN = re.compile(r"Mobi|Android|iPhone|iPad|Tablet|Silk|Kindle", re.I)


def varsayilan_kip(ajan):
    """Telefon/tablet tarayıcısı → "Sıradaki"; bilgisayar → "Tablo" (ekran genişliği sunucuya gelmez; tarayıcı kimliği)."""
    return "Sıradaki" if _MOBIL_AJAN.search(str(ajan or "")) else "Tablo"


def _istemci_ajani():
    try:
        return str(st.context.headers.get("User-Agent", "") or "")
    except Exception:
        return ""


def _qp_al(ad):
    try:
        return st.query_params.get(ad)
    except Exception:
        return None


def _qp_ayarla(ad, deger):
    """Adres çubuğu parametresi (sayfa yenilenince taslağa dönmek için); eski sürümde sessizce atlanır."""
    try:
        if deger is None:
            if ad in st.query_params:
                del st.query_params[ad]
        elif st.query_params.get(ad) != deger:
            st.query_params[ad] = deger
    except Exception:
        pass


def taslak_bos(testler, sporcular, bilgi=None):
    return {"surum": 1, "testler": list(testler), "sporcular": list(sporcular), "bilgi": dict(bilgi or {}),
            "degerler": {}, "notlar": {}, "durum": {}, "konum": None, "zaman": ""}


def taslak_birlestir(eski, yeni):
    """Adımlar yeniden geçilince: aynı sporcu × test için girilmiş değer, not ve durum korunur."""
    if not eski:
        return yeni
    testler = set(yeni["testler"])
    ait = lambda sutun: any(sutun.startswith(oturum_sutunu(t, "")) for t in testler)
    for s in yeni["sporcular"]:
        d = {c: v for c, v in (eski.get("degerler", {}).get(s) or {}).items() if ait(c)}
        if d:
            yeni["degerler"][s] = d
        for alan in ("notlar", "durum"):
            x = {t: v for t, v in (eski.get(alan, {}).get(s) or {}).items() if t in testler}
            if x:
                yeni[alan][s] = x
    k = eski.get("konum")
    if k and k[0] in testler and k[1] in yeni["sporcular"]:
        yeni["konum"] = list(k)
    return yeni


def taslak_oku(yol=TASLAK_DOSYA):
    """Diskteki taslak ya da None (yok, bozuk ya da boş)."""
    try:
        with open(yol, encoding="utf-8") as f:
            t = _json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(t, dict) or not t.get("testler") or not t.get("sporcular"):
        return None
    for alan in ("degerler", "notlar", "durum", "bilgi"):
        if not isinstance(t.get(alan), dict):
            t[alan] = {}
    return t


def taslak_yaz(t, yol=TASLAK_DOSYA):
    """Taslağı diske yazar (önce geçici dosya, sonra yer değiştirme: yarım yazılmış dosya kalmaz)."""
    from datetime import datetime as _an
    t["zaman"] = _an.now().strftime("%H:%M:%S")
    gecici = yol + ".yaziliyor"
    try:
        with open(gecici, "w", encoding="utf-8") as f:
            _json.dump(t, f, ensure_ascii=False)
        os.replace(gecici, yol)
        return True
    except OSError:
        return False


def taslak_sil(yol=TASLAK_DOSYA):
    try:
        os.remove(yol)
    except OSError:
        pass


def taslak_deger_sayisi(t):
    return sum(1 for d in (t or {}).get("degerler", {}).values() for v in d.values() if str(v).strip())


def sayi_girdisi(metin):
    """Elle girilen sayı: virgül ya da nokta ondalık ("32,5" = "32.5"). Dönen: (kayıt metni, geçerli mi)."""
    m = str(metin or "").strip().replace(" ", "")
    if not m:
        return "", True
    try:
        f = float(m.replace(",", "."))
    except ValueError:
        return m, False
    if f != f or f in (float("inf"), float("-inf")):
        return m, False
    return deger_metni(f), True


def taslak_tablosu(t, testler, notlu=False):
    """Taslak → toplu giriş tablosu (satır sporcu, sütun "Test › Değişken"; notlu: test başına "Test › Not")."""
    sutunlar = ["Sporcu"]
    for test, ds in testler.items():
        sutunlar += [oturum_sutunu(test, d) for d in ds] + ([oturum_sutunu(test, NOT_DEGISKENI)] if notlu else [])
    satirlar = []
    for s in t["sporcular"]:
        r = {"Sporcu": s}
        dv = t.get("degerler", {}).get(s) or {}
        for test, ds in testler.items():
            for d in ds:
                c = oturum_sutunu(test, d)
                v = dv.get(c, "")
                if METIN_DEGISKEN_KALIBI.search(d):
                    r[c] = str(v or "")
                else:
                    try:
                        r[c] = float(v) if str(v).strip() else float("nan")
                    except ValueError:
                        r[c] = float("nan")
            if notlu:
                r[oturum_sutunu(test, NOT_DEGISKENI)] = not_metni((t.get("notlar", {}).get(s) or {}).get(test))
        satirlar.append(r)
    df = pd.DataFrame(satirlar, columns=sutunlar)
    for test, ds in testler.items():
        for d in ds:
            c = oturum_sutunu(test, d)
            df[c] = df[c].astype("object" if METIN_DEGISKEN_KALIBI.search(d) else "float64")
        if notlu:
            df[oturum_sutunu(test, NOT_DEGISKENI)] = df[oturum_sutunu(test, NOT_DEGISKENI)].astype("object")
    return df


def taslak_duzenleme_tablosu(t, testler):
    """Tablo kipinin düzenleme tablosu: değer hücreleri METİN (boş hücre boş görünür, virgül kabul: "4,52")."""
    sutunlar = ["Sporcu"] + [x for test, ds in testler.items()
                             for x in [oturum_sutunu(test, d) for d in ds] + [oturum_sutunu(test, NOT_DEGISKENI)]]
    satirlar = []
    for s in t["sporcular"]:
        dv = t.get("degerler", {}).get(s) or {}
        r = {"Sporcu": s}
        for test, ds in testler.items():
            for d in ds:
                v = str(dv.get(oturum_sutunu(test, d), "") or "")
                r[oturum_sutunu(test, d)] = v if METIN_DEGISKEN_KALIBI.search(d) else v.replace(".", ",")
            r[oturum_sutunu(test, NOT_DEGISKENI)] = not_metni((t.get("notlar", {}).get(s) or {}).get(test))
        satirlar.append(r)
    return pd.DataFrame(satirlar, columns=sutunlar).astype("object")


def taslak_tablodan(t, tablo, testler):
    """
    Tablo kipinde düzenlenen tabloyu taslağa yazar. Dönen: (değişti mi, geçersiz hücreler [(sporcu, sütun, metin)]).
    Sayı olmayan hücre taslağa yazılmaz. Değer girilen 'gelmedi' sporcu açılır.
    """
    eski = _json.dumps([t.get("degerler"), t.get("notlar"), t.get("durum")], sort_keys=True, ensure_ascii=False)
    gecersiz = []
    for _, r in tablo.iterrows():
        s = r["Sporcu"]
        dv = dict(t["degerler"].get(s) or {})
        for test, ds in testler.items():
            dolu = False
            for d in ds:
                c = oturum_sutunu(test, d)
                ham = r.get(c)
                if METIN_DEGISKEN_KALIBI.search(d):
                    v, gecerli = deger_metni(ham), True
                elif isinstance(ham, (int, float)) and not isinstance(ham, bool):
                    v, gecerli = deger_metni(ham), True
                else:
                    v, gecerli = sayi_girdisi(deger_metni(ham))
                if not gecerli:
                    gecersiz.append((s, c, v))
                    continue
                if v:
                    dv[c], dolu = v, True
                else:
                    dv.pop(c, None)
            nc = oturum_sutunu(test, NOT_DEGISKENI)
            if nc in tablo.columns:
                n = not_coz("" if r.get(nc) is None or (isinstance(r.get(nc), float) and r.get(nc) != r.get(nc))
                            else r.get(nc))
                if n["etiketler"] or n["metin"]:
                    t["notlar"].setdefault(s, {})[test] = n
                else:
                    (t["notlar"].get(s) or {}).pop(test, None)
            if dolu and (t["durum"].get(s) or {}).get(test) == "gelmedi":
                t["durum"][s].pop(test)
        if dv:
            t["degerler"][s] = dv
        else:
            t["degerler"].pop(s, None)
    return eski != _json.dumps([t.get("degerler"), t.get("notlar"), t.get("durum")], sort_keys=True,
                               ensure_ascii=False), gecersiz


def taslak_kayitlari(t, bilgiler, testler, yollar, tarih, ot_bilgi):
    """Taslak → xlsx kayıtları (eski toplu giriş yolu) + test başına not "Notlar" alanına. Dönen (kayıtlar, uyarılar)."""
    kayitlar, uyari = oturum_kayitlari(taslak_tablosu(t, testler), bilgiler, testler, "-", "-", None, tarih, ot_bilgi,
                                       yollar=yollar)
    for k in kayitlar:
        notlar = {kanonik_test(x): n for x, n in (t.get("notlar", {}).get(k["Sporcu"]) or {}).items()}
        k["Notlar"] = not_metni(notlar.get(k["Test"]))
    return kayitlar, uyari


def ot_kuyrugu(t):
    """Test bazlı sıra: aynı test sporcudan sporcuya, sonra sıradaki test."""
    return [(test, s) for test in t["testler"] for s in t["sporcular"]]


def ot_durumu(t, test, sporcu):
    return (t.get("durum", {}).get(sporcu) or {}).get(test)


def ot_ilerleme(t, test):
    """(yapılan ya da gelmedi işaretli sporcu sayısı, toplam) — bu test için."""
    return sum(1 for s in t["sporcular"] if ot_durumu(t, test, s) in ("tamam", "gelmedi")), len(t["sporcular"])


def ot_siradaki(t, sonra=None):
    """Kuyrukta 'sonra'dan sonraki ilk bekleyen (test, sporcu); başa sarar; hepsi bittiyse None."""
    kuyruk = ot_kuyrugu(t)
    bas = kuyruk.index(tuple(sonra)) + 1 if sonra and tuple(sonra) in kuyruk else 0
    for test, s in kuyruk[bas:] + kuyruk[:bas]:
        if ot_durumu(t, test, s) is None:
            return [test, s]
    return None


def ot_hesaplanan(test, degerler, bilgi):
    """Girilen değerlerden otomatik hesaplananlar (ör. sıçrama yüksekliği). Karşılaştırma YOK — yalnız sayı."""
    bilgi = bilgi or {}
    kilo = guvenli_float(bilgi.get("Kilo (kg)", 0)) if _girildi(bilgi.get("Kilo (kg)")) else 0
    try:
        h, _ = turetilmis_degerler(test, {d: v for d, v in degerler.items() if v}, bilgi, kilo)
    except Exception:
        return {}
    return {k: v for k, v in h.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in degerler}


def ot_aykiri_uyarilari(t, bilgiler, testler, tarih, test, sporcu):
    """Tek sporcu × tek test için olağandışı değer ve hesap uyarıları (kayıt engellenmez)."""
    tek = {**t, "sporcular": [sporcu]}
    _, uyari = oturum_kayitlari(taslak_tablosu(tek, {test: testler[test]}), bilgiler, {test: testler[test]},
                                "-", "-", None, tarih, {})
    return uyari


def ot_adim_seridi_html(adim):
    """Adım şeridi: renk + simge + kelime (✓ tamamlandı, ● şu an, ○ sırada); 'Adım N / 4' ilerleme olarak."""
    oge = []
    for i, ad in enumerate(OT_ADIMLAR, 1):
        d = "tamam" if i < adim else ("simdi" if i == adim else "sonra")
        isaret = {"tamam": "✓", "simdi": "●", "sonra": "○"}[d]
        kelime = {"tamam": "tamamlandı", "simdi": "şu an", "sonra": "sırada"}[d]
        oge.append(f'<li class="ot-adim ot-{d}"' + (' aria-current="step"' if d == "simdi" else "")
                   + f'><span aria-hidden="true">{isaret}</span> {i}. {_html.escape(ad)}'
                   f'<span class="ot-gizli"> ({kelime})</span></li>')
    return (f'<nav class="ot-serit" aria-label="Oturum adımları"><p class="ot-sayac" role="progressbar" '
            f'aria-valuenow="{adim}" aria-valuemin="1" aria-valuemax="{len(OT_ADIMLAR)}">Adım {adim} / '
            f'{len(OT_ADIMLAR)}</p><ol>{"".join(oge)}</ol></nav>')


def ot_ilerleme_html(yapilan, toplam, etiket):
    yuzde = round(100 * yapilan / toplam) if toplam else 0
    return (f'<div class="ot-ilerleme" role="progressbar" aria-valuenow="{yapilan}" aria-valuemin="0" '
            f'aria-valuemax="{toplam}" aria-label="{_html.escape(etiket)}"><div class="ot-ilerleme-dolu" '
            f'style="width:{yuzde}%"></div></div><p class="ot-ilerleme-yazi">{_html.escape(etiket)}</p>')


def ot_sira_cipleri_html(t, test, simdiki):
    """Sıra çipleri YALNIZ BİLGİ (tıklanmaz): ✓ yapıldı, ● şu an, ○ kalan, – gelmedi."""
    p = []
    for s in t["sporcular"]:
        d = ot_durumu(t, test, s)
        sinif, isaret, kelime = (("simdi", "●", "şu an") if s == simdiki else
                                 ("tamam", "✓", "yapıldı") if d == "tamam" else
                                 ("gelmedi", "–", "gelmedi") if d == "gelmedi" else ("kalan", "○", "kalan"))
        p.append(f'<li class="ot-cip ot-{sinif}"><span aria-hidden="true">{isaret}</span> {_html.escape(ad_bicimi(s))}'
                 f'<span class="ot-gizli"> ({kelime})</span></li>')
    return f'<ul class="ot-cipler" aria-label="Ölçüm sırası">{"".join(p)}</ul>'


def _ot_durum_koru():
    """Görünmeyen adımın seçimleri silinmesin: Streamlit, o çalışmada çizilmeyen bileşenin durumunu temizler."""
    for k in list(st.session_state.keys()):
        k = str(k)
        if not (k.startswith("ot_") or k.startswith("ot::")) or k.startswith(OT_KORUNMAYAN):
            continue
        v = st.session_state[k]
        if isinstance(v, (list, str, date)) or (isinstance(v, (int, float)) and not isinstance(v, bool)):
            st.session_state[k] = v


def _ot_adim_git(n):
    st.session_state["ot_adim"] = n
    st.session_state.pop("ots::aykiri", None)
    st.session_state.pop("ots::aykiri_tablo", None)


def _ot_tablo_yenile():
    st.session_state["ot_tablo_surum"] = st.session_state.get("ot_tablo_surum", 0) + 1
    st.session_state.pop("ots::aykiri", None)
    st.session_state.pop("ots::aykiri_tablo", None)


def _ot_grup_adlari(df_ot, sporcular):
    g = {(df_ot.loc[df_ot["_ad"] == s, "_grup"].iloc[0] if (df_ot["_ad"] == s).any() else "") or "(Grubu girilmemiş)"
         for s in sporcular}
    return sorted(x for x in g if x != "(Grubu girilmemiş)") + (["(Grubu girilmemiş)"] if "(Grubu girilmemiş)" in g else [])


def _ot_taslak_yukle(t, df_ot):
    """Yarım kalan oturum: seçimler ve değerler geri gelir, Adım 4 açılır."""
    st.session_state["ots::taslak"] = t
    st.session_state["ots::testler"] = list(t["testler"])
    st.session_state["ots::sporcular"] = list(t["sporcular"])
    b_ = t.get("bilgi", {})
    st.session_state["ots::calisma"] = {"ad": b_.get("calisma"), "zaman": b_.get("zaman")}
    st.session_state["ot::ek"] = list(t["testler"])
    st.session_state["ot::sira"] = list(t["testler"])
    try:
        st.session_state["ot_tarih"] = date.fromisoformat(str(b_.get("tarih")))
    except ValueError:
        pass
    st.session_state["ot_yer"] = str(b_.get("yer", "") or "")
    st.session_state["ot_uyg"] = str(b_.get("uygulayan", "") or "")
    st.session_state["ot_ad"] = str(b_.get("ad", "") or "")
    calismalar = calismalar_oku()
    if b_.get("calisma") in calismalar:
        c = calismalar[b_["calisma"]]
        st.session_state["ot_kaynak"] = "Çalışma"
        st.session_state["ot_calisma"] = b_["calisma"]
        st.session_state[f"ot_zaman::{b_['calisma']}"] = b_.get("zaman")
        if c["gruplar"]:
            st.session_state[f"ot_c_gruplar::{b_['calisma']}"] = list(c["gruplar"])
            st.session_state[f"ot_c_sporcular::{b_['calisma']}::{'|'.join(c['gruplar'])}"] = list(t["sporcular"])
    else:
        st.session_state["ot_kaynak"] = "Serbest seçim"
        gruplar = _ot_grup_adlari(df_ot, t["sporcular"])
        st.session_state["ot_gruplar"] = gruplar
        st.session_state[f"ot_sporcular_{'|'.join(gruplar)}"] = list(t["sporcular"])
    st.session_state["ot_adim"] = 4
    _ot_tablo_yenile()


def _ot_taslak_temizle():
    taslak_sil()
    st.session_state["ots::taslak"] = None
    st.session_state["ots::taslak_sorma"] = True
    for k in [k for k in st.session_state if str(k).startswith(("ot_g::", "ot_n::", "ot_nm::"))]:
        st.session_state.pop(k, None)
    _qp_ayarla("taslak", None)


def _ot_degerlere_gec():
    """Adım 3 → 4: seçimlerden taslak kurulur (önceki taslağın aynı sporcu × test değerleri korunur) ve diske yazılır."""
    c = st.session_state.get("ots::calisma") or {}
    tarih = st.session_state.get("ot_tarih") or date.today()
    bilgi = {"tarih": tarih.isoformat(), "yer": str(st.session_state.get("ot_yer", "") or "").strip(),
             "uygulayan": str(st.session_state.get("ot_uyg", "") or "").strip(),
             "ad": str(st.session_state.get("ot_ad", "") or "").strip(),          # Paket 38d
             "calisma": c.get("ad"), "zaman": c.get("zaman")}
    yeni = taslak_birlestir(st.session_state.get("ots::taslak"),
                            taslak_bos(st.session_state.get("ots::testler", []),
                                       st.session_state.get("ots::sporcular", []), bilgi))
    st.session_state["ots::taslak"] = yeni
    taslak_yaz(yeni)
    st.session_state["ot_adim"] = 4
    _ot_tablo_yenile()


def _ot_deger_cb(test, sporcu, sutun, anahtar, sayisal):
    """Sıradaki kipinde her alan değişiminde: değer taslağa ve diske (geçersiz sayı yazılmaz, alanın altında uyarı)."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    ham = st.session_state.get(anahtar, "")
    v, gecerli = sayi_girdisi(ham) if sayisal else (str(ham or "").strip(), True)
    hatalar = st.session_state.setdefault("ots::hatalar", {})
    if not gecerli:
        hatalar[anahtar] = True
        return
    hatalar.pop(anahtar, None)
    dv = t["degerler"].setdefault(sporcu, {})
    if v:
        dv[sutun] = v
        if ot_durumu(t, test, sporcu) == "gelmedi":
            t["durum"][sporcu].pop(test)
    else:
        dv.pop(sutun, None)
        if not dv:
            t["degerler"].pop(sporcu, None)
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_not_cb(test, sporcu, anahtar_cip, anahtar_metin):
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    cip = st.session_state.get(anahtar_cip) or []
    n = {"etiketler": [c for c in NOT_CIPLERI if c in cip],
         "metin": str(st.session_state.get(anahtar_metin, "") or "").strip()}
    if n["etiketler"] or n["metin"]:
        t["notlar"].setdefault(sporcu, {})[test] = n
    else:
        (t["notlar"].get(sporcu) or {}).pop(test, None)
    taslak_yaz(t)


def _ot_tamamla(t, test, sporcu):
    t["durum"].setdefault(sporcu, {})[test] = "tamam"
    t["konum"] = ot_siradaki(t, (test, sporcu))
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_sonraki_cb(test, sporcu, bilgiler, testler, tarih):
    """'Kaydet ve sıradaki →': boş/geçersiz alan varsa uyarı; olağandışı değer varsa sorar; yoksa sıradakine geçer."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    onek = f"ot_g::{sporcu}::{oturum_sutunu(test, '')}"
    if any(str(k).startswith(onek) for k in st.session_state.get("ots::hatalar", {})):
        st.session_state["ots::mesaj"] = "Sayı olmayan alanı düzeltin (virgül ya da nokta kullanılabilir)."
        return
    dv = t["degerler"].get(sporcu) or {}
    if not any(dv.get(oturum_sutunu(test, d)) for d in testler[test]):
        st.session_state["ots::mesaj"] = "Değer girin ya da 'Atla (gelmedi)' seçin."
        return
    uy = ot_aykiri_uyarilari(t, bilgiler, testler, tarih, test, sporcu)
    if uy:
        st.session_state["ots::aykiri"] = {"anahtar": [test, sporcu], "uyarilar": uy}
        return
    _ot_tamamla(t, test, sporcu)


def _ot_onayla_cb(test, sporcu):
    t = st.session_state.get("ots::taslak")
    if t:
        _ot_tamamla(t, test, sporcu)


def _ot_atla_cb(test, sporcu):
    """'Atla (gelmedi)': bu sporcunun bu testteki değerleri silinir, gelmedi işaretlenir; kayıt yazılmaz."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    dv = t["degerler"].get(sporcu) or {}
    for c in [c for c in dv if c.startswith(oturum_sutunu(test, ""))]:
        dv.pop(c)
        st.session_state.pop(f"ot_g::{sporcu}::{c}", None)
    if not dv:
        t["degerler"].pop(sporcu, None)
    t["durum"].setdefault(sporcu, {})[test] = "gelmedi"
    t["konum"] = ot_siradaki(t, (test, sporcu))
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_geri_al_cb(test, sporcu):
    """'Geri al': bir önceki sporcuya döner ve onun onayını kaldırır (değerleri durur, düzeltilebilir)."""
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    kuyruk = ot_kuyrugu(t)
    i = kuyruk.index((test, sporcu)) if (test, sporcu) in kuyruk else len(kuyruk)
    if i == 0:
        return
    pt, ps = kuyruk[i - 1]
    (t["durum"].get(ps) or {}).pop(pt, None)
    t["konum"] = [pt, ps]
    st.session_state.pop("ots::aykiri", None)
    taslak_yaz(t)


def _ot_kaydet_cb(bilgiler, testler, yollar, tarih, onayli):
    """'Oturumu kaydet': olağandışı değer varsa (onaysız) önce sorar; sonra xlsx'e yazar ve taslağı siler."""
    from datetime import datetime as _simdi
    t = st.session_state.get("ots::taslak")
    if not t:
        return
    b_ = t.get("bilgi", {})
    ot_bilgi = {"kimlik": "", "yer": b_.get("yer", ""), "uygulayici": b_.get("uygulayan", "")}
    kayitlar, uyari = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, ot_bilgi)
    if not kayitlar:
        st.session_state["ots::mesaj"] = "Kaydedilecek değer yok."
        return
    if uyari and not onayli:
        st.session_state["ots::aykiri_tablo"] = uyari
        return
    ot_calisma_ad, ot_zaman = b_.get("calisma"), b_.get("zaman")
    ot_calisma = calismalar_oku().get(ot_calisma_ad) if ot_calisma_ad else None
    kimlik = oturum_kimligi(ot_calisma_ad if ot_calisma is not None else None, ot_zaman, _simdi.now())
    for k in kayitlar:
        k["Oturum"] = kimlik
        k[OTURUM_ADI_KOLON] = str(b_.get("ad", "") or "").strip()      # Paket 38d: eski dosyada sütun oluşur
    kayitlari_yaz(kayitlar)
    if ot_calisma is not None:
        calisma_dokun(ot_calisma_ad)                   # öneride "en son dokunulan" (Paket 33)
    dolu_sporcu = len({k["Sporcu"] for k in kayitlar})
    _ot_taslak_temizle()
    st.session_state.pop("ots::taslak_sorma", None)
    st.session_state.pop("ots::aykiri_tablo", None)
    st.session_state["ots::sonuc"] = (f"✅ {len(kayitlar)} test kaydı yazıldı ({dolu_sporcu} sporcu). Oturum: {kimlik}. "
                                      "Norm karşılaştırması ve yorum Sonuçları Görüntüle sayfasında.")
    st.session_state["ot_adim"] = 1


def test_norm_var_mi(ad):
    """Adım 1 işareti: testin normu ("norm"), yalnız örneklem karşılaştırması ("orneklem") ya da None."""
    ad = kanonik_test(ad)
    ds = (test_bilgisi(ad) or {}).get("degiskenler", [])
    if ad in NORMATIF_TEST or any(f"{ad} › {x}" in NORMATIF_YAS or f"{ad} › {x}" in NORMATIF_ESIK_YAS for x in ds):
        return "norm"
    nd = [x for x in ds if x in NORMATIF and (x not in NORMATIF_KAPSAM or NORMATIF_KAPSAM[x](ad))]
    if not nd:
        return None
    return "orneklem" if all(NORMATIF[x].get("tur") == "orneklem" for x in nd) else "norm"


NORM_ISARETI = {"norm": "✓ norm var", "orneklem": "✓ örneklem karşılaştırması", None: "○ norm yok"}


def _bant_ortancasi(bantlar):
    """P50; yoksa P50'yi çevreleyen iki yüzdeliğin doğrusal ara değeri; hesaplanamazsa None."""
    try:
        nok = sorted((int(k[1:]), float(v)) for k, v in (bantlar or {}).items()
                     if str(k).startswith("P") and str(k)[1:].isdigit())
    except (TypeError, ValueError):
        return None
    d = dict(nok)
    if 50 in d:
        return d[50]
    alt = [(q, v) for q, v in nok if q < 50]
    ust = [(q, v) for q, v in nok if q > 50]
    if not alt or not ust:
        return None
    (q0, v0), (q1, v1) = alt[-1], ust[0]
    return v0 + (v1 - v0) * (50 - q0) / (q1 - q0)


def ot_ornek_deger(test, degisken, bilgi):
    """
    Sayı kutusunun örneği (Paket 38c): testin yaş normunun bu sporcunun yaşı ve cinsiyetindeki ortancası
    ("ör. 1,9", "ör. 150"). Normu yoksa ya da yaş/cinsiyet bilinmiyorsa "" — genel bir örnek yazılmaz.
    """
    bilgi = bilgi or {}
    cins = str(bilgi.get("Cinsiyet", "") or "").strip()
    yas = tam_yas(bilgi.get(DOGUM_KOLON), date.today()) or bilgi.get("Yaş")
    if cins not in ("Erkek", "Kadın") or not _girildi(yas):
        return ""
    try:
        n = yas_persentil_bul(kanonik_test(test), degisken, yas, cins, 0.0, bilgi.get(DOGUM_KOLON), date.today())
    except Exception:
        return ""
    orta = _bant_ortancasi((n or {}).get("bantlar"))
    return "" if orta is None else f"ör. {_aralik_sayi(orta, _birim(degisken, test))}"


def _ot_sayi_klavyesi():
    """inputmode="decimal" (telefonda virgüllü rakam klavyesi): Streamlit metin kutusunda bu ayar yok; küçük betik
    yalnız büyük sayı alanlarına ekler. Betik çalışmazsa giriş yine çalışır (virgül/nokta kabul edilir)."""
    try:
        betik = ("<script>(function(){var d=window.parent.document;function k(){d.querySelectorAll("
                      "'.st-key-ot-sayilar input').forEach(function(i){if(i.getAttribute('inputmode')!=='decimal')"
                      "{i.setAttribute('inputmode','decimal');}});}k();new MutationObserver(k).observe(d.body,"
                      "{childList:true,subtree:true});})();</script>")
        with st.container(key="ot-betik"):                       # Paket 38c: çerçeve yer kaplamaz, çizgi bırakmaz
            if hasattr(st, "iframe"):
                st.iframe(betik, height=1)
            else:
                import streamlit.components.v1 as _bilesen
                _bilesen.html(betik, height=0)
    except Exception:
        pass


def _ot_adim_testler(df_ot):
    """Adım 1 — Testler (kategori ağacı, arama ya da kayıtlı Çalışma). Seçilen sıra ots::testler'e."""
    calismalar = calismalar_oku()
    with st.expander("Çalışmalar — kur / düzenle (ör. tez: gruplar, ölçüm zamanları, sıralı testler)"):
        _calisma_duzenleyici(df_ot["_ad"].tolist())
    ot_kaynak = st.radio("Test kaynağı", ["Serbest seçim", "Çalışma"], horizontal=True, key="ot_kaynak",
                         help="Serbest seçim: kategori ağacından ya da aramadan, sporcunun branşından bağımsız. "
                              "Çalışma: kayıtlı test listesi kayıtlı sırasıyla gelir.")
    ot_calisma, ot_calisma_ad, ot_zaman = None, None, None
    if ot_kaynak == "Çalışma":
        if not calismalar:
            st.info("Kayıtlı çalışma yok. Yukarıdaki 'Çalışmalar' bölümünden bir çalışma kurun.")
            ot_sira = []
        else:
            c1, c2 = st.columns(2)
            ot_calisma_ad = c1.selectbox("Çalışma", list(calismalar), key="ot_calisma")
            ot_calisma = calismalar[ot_calisma_ad]
            ot_zaman = c2.selectbox("Ölçüm zamanı", ot_calisma["zamanlar"], key=f"ot_zaman::{ot_calisma_ad}")
            ot_sira = list(ot_calisma["testler"])
            st.caption("Testler kayıtlı sırayla: " + " → ".join(ot_sira))
            for t_ in ot_sira:                                   # iz çubuğu (Paket 33)
                st.caption(f"📍 {test_izi(t_)}")
            st.caption(f"Oturum alanına yazılacak: **{calisma_oturum_adi(ot_calisma_ad, ot_zaman)}**")
    else:
        agac_anahtarlari = [k_ for k_, v_ in st.session_state.items()
                            if str(k_).startswith("ot_testler_") and isinstance(v_, list)]
        secili_simdi = {kanonik_test(t) for k_ in agac_anahtarlari for t in st.session_state[k_]} | set(
            st.session_state.get("ot::ek", []))
        with st.container(border=True):                      # arama paneli (ana sayfadaki "Test ara" deseni)
            st.markdown("**Test ara**")
            ot_ara = st.text_input("Test adı ya da ölçtüğü nitelik", key="ot_ara",
                                   placeholder="ör. T-testi, sürat, çeviklik, Nordic — yazıp Enter'a basın")
            if ot_ara.strip():
                ot_bulunan = [t for t in test_ara(ot_ara) if t["ad"] not in TOPLU_GIRIS_DISI
                              and (test_bilgisi(t["ad"]) or {}).get("degiskenler")]
                st.caption(f"{len(ot_bulunan)} test bulundu" + (" — ilk 12 gösteriliyor" if len(ot_bulunan) > 12 else ""))
                for i, t in enumerate(ot_bulunan[:12]):
                    c1, c2 = st.columns([4, 1], vertical_alignment="center")
                    diger = [r[2] or r[1] for r in test_raflari(t["ad"]) if r != t["yol"]]
                    c1.markdown(f"{_html.escape(test_etiketli(t['ad']))}  \n<span style='font-size:0.875rem'>"
                                f"{_html.escape(' › '.join(p for p in t['yol'] if p))}"
                                + (f" · ayrıca rafta: {_html.escape(', '.join(dict.fromkeys(diger)))}" if diger else "")
                                + "</span>", unsafe_allow_html=True)
                    c2.button("Eklendi" if t["ad"] in secili_simdi else "Ekle", key=f"ot::ara::ekle::{i}",
                              width="stretch", disabled=t["ad"] in secili_simdi, on_click=_ot_ekle, args=(t["ad"],))
        st.caption("Kategori ağacı gezinmek içindir; testler sporcunun branşından bağımsız seçilir. "
                   "Aramadan ve ağaçtan seçilen testler aşağıdaki sıralı listede birleşir.")
        b1, b2, b3 = st.columns(3)
        with b1:
            ot_kategori = st.selectbox("Kategori", list(TEST_KATALOGU.keys()), key="ot_kategori")
        with b2:
            ot_batarya = st.selectbox("Batarya", [k for k in TEST_KATALOGU[ot_kategori] if not k.startswith("_")],
                                      key="ot_batarya")
        ot_havuz = TEST_KATALOGU[ot_kategori][ot_batarya]
        ot_brans = None
        if ot_kategori == "Branşa Özgü Testler":
            with b3:
                ot_brans = st.selectbox("Branş", [k for k in ot_havuz if not k.startswith("_")], key="ot_brans")
            ot_havuz = ot_havuz[ot_brans]
        ot_test_adlari = [t for t, v in ot_havuz.items() if not t.startswith("_") and isinstance(v, dict)
                          and "degiskenler" in v and t not in TOPLU_GIRIS_DISI]
        if any(t in TOPLU_GIRIS_DISI for t in ot_havuz):
            st.caption("SWFT'nin özel giriş ekranı olduğu için toplu girişte yer almaz; Test Uygula sayfasından girin.")
        _ot_t_key = f"ot_testler_{ot_kategori}_{ot_batarya}_{ot_brans}"     # yönlendirme ekranı doldurabilir
        ot_testler_sec = coklu_secim("Bu oturumda uygulanan testler", ot_test_adlari, key=_ot_t_key, tumunu_sec=True,
                                     format_func=test_etiketli,
                                     help="Bu dalın testleri. Gezinirken hiçbir test kendiliğinden eklenmez; "
                                          "bataryanın tümü için kutudaki seçenekleri seçin.")
        # diğer ağaç düğümlerinden önceden seçilenler de korunur (kategori değiştirince kaybolmasın)
        agac_anahtarlari = [k_ for k_, v_ in st.session_state.items()
                            if str(k_).startswith("ot_testler_") and isinstance(v_, list)]
        agac = [t for k_ in agac_anahtarlari for t in st.session_state[k_]]
        secilen = list(dict.fromkeys(kanonik_test(t) for t in ot_testler_sec + agac
                                     + list(st.session_state.get("ot::ek", []))))
        st.markdown("**Sıralı test listesi** (↑ ↓ sırayı değiştirir, ✕ çıkarır)")
        ot_sira = (_sira_listesi("ot", secilen, tuple(agac_anahtarlari) + ("ot::ek",)) if secilen else [])
    for u in sira_uyarilari(ot_sira):                               # bildirir, engellemez
        st.warning(f"Sıra uyarısı: {u}", icon=":material/info:")
    ot_sira_giris = [t for t in ot_sira if t not in TOPLU_GIRIS_DISI and (test_bilgisi(t) or {}).get("degiskenler")]
    if len(ot_sira_giris) < len(ot_sira):
        st.caption("Özel giriş ekranı olan ya da değişkeni tanımsız testler (ör. SWFT) toplu girişte yer almaz; "
                   "Test Uygula sayfasından girin.")
    for t_ in ot_sira_giris:                                        # ○ / ✓ norm: renkle birlikte simge ve kelime
        st.caption(f"{NORM_ISARETI[test_norm_var_mi(t_)]} — {test_etiketli(t_)}")
    st.session_state["ots::testler"] = ot_sira_giris
    st.session_state["ots::calisma"] = {"ad": ot_calisma_ad if ot_calisma is not None else None, "zaman": ot_zaman}
    return {"etiket": "İleri: Sporcular →", "cb": _ot_adim_git, "args": (2,), "disabled": not ot_sira_giris}


def _ot_adim_sporcular(df_ot):
    """Adım 2 — Sporcular (grup ya da çalışma grubu, tümü seçili gelir). ots::sporcular'a."""
    calismalar = calismalar_oku()
    c = st.session_state.get("ots::calisma") or {}
    ot_calisma_ad = c.get("ad") if st.session_state.get("ot_kaynak") == "Çalışma" else None
    ot_calisma = calismalar.get(ot_calisma_ad) if ot_calisma_ad else None
    if ot_calisma is not None and ot_calisma["gruplar"]:
        _ot_cg_key = f"ot_c_gruplar::{ot_calisma_ad}"
        ot_c_gruplar = coklu_secim("Çalışma grubu", ot_calisma["gruplar"],
                                   default=None if _ot_cg_key in st.session_state else ot_calisma["gruplar"],
                                   key=_ot_cg_key)
        aday = [s for s in calisma_sporculari(ot_calisma, ot_c_gruplar) if s in set(df_ot["_ad"])]
        if not aday:
            st.caption("Bu gruplara atanmış sporcu yok; çalışmadaki atamayı kontrol edin. Bütün sporcular listelendi.")
            aday = df_ot["_ad"].tolist()
        _ot_s_key = f"ot_c_sporcular::{ot_calisma_ad}::{'|'.join(ot_c_gruplar)}"
    else:
        grup_listesi = sorted({g for g in df_ot["_grup"] if g})
        if (df_ot["_grup"] == "").any():
            grup_listesi.append("(Grubu girilmemiş)")
        ot_gruplar = coklu_secim("Grup / Sınıf", grup_listesi,
                                 default=None if "ot_gruplar" in st.session_state else grup_listesi[:1],
                                 key="ot_gruplar")
        aday = df_ot[df_ot["_grup"].map(lambda g: (g or "(Grubu girilmemiş)") in ot_gruplar)]["_ad"].tolist()
        _ot_s_key = f"ot_sporcular_{'|'.join(ot_gruplar)}"
    ot_sporcular = coklu_secim("Sporcular (gruptakilerin tümü seçili gelir)", aday, tumunu_sec=True, format_func=ad_bicimi,
                               default=None if _ot_s_key in st.session_state else aday, key=_ot_s_key)
    st.markdown(f"**{len(ot_sporcular)} sporcu seçili**")
    st.session_state["ots::sporcular"] = list(ot_sporcular)
    return {"etiket": "İleri: Oturum bilgisi →", "cb": _ot_adim_git, "args": (3,), "disabled": not ot_sporcular}


def _ot_adim_bilgi():
    """Adım 3 — Oturum bilgisi: tarih, yer, uygulayan (çalışmada ölçüm zamanı Adım 1'de)."""
    o1, o2, o3 = st.columns(3)
    with o1:
        st.date_input("Tarih", format="DD.MM.YYYY", key="ot_tarih",
                      **({} if "ot_tarih" in st.session_state else {"value": date.today()}))
    with o2:
        st.text_input("Yer", placeholder="ör. Okul spor salonu", key="ot_yer")
    with o3:
        st.text_input("Uygulayan", placeholder="ör. Ertuğrul K.", key="ot_uyg")
    st.text_input("Oturum adı (isteğe bağlı)", key="ot_ad", max_chars=60, placeholder="ör. 6-B Ekim taraması",
                  help="Sonuçlarda ve karşılaştırmada oturum bu adla görünür. Boş kalırsa tarih, yer ve uygulayan.")
    c = st.session_state.get("ots::calisma") or {}
    if c.get("ad") and c.get("zaman"):
        st.caption(f"Oturum alanına yazılacak: **{calisma_oturum_adi(c['ad'], c['zaman'])}**")
    return {"etiket": "İleri: Değerler →", "cb": _ot_degerlere_gec, "args": ()}


def _ot_siradaki_kipi(t, testler, bilgiler, tarih, yollar):
    """Sıradaki kipi: ekranda TEK sporcu, TEK test; büyük alanlar; otomatik değer canlı; karşılaştırma yok."""
    konum = t.get("konum")
    if not konum or konum[0] not in testler or konum[1] not in t["sporcular"] or ot_durumu(t, *konum):
        konum = ot_siradaki(t, konum)
        t["konum"] = konum
    if konum is None:
        gelmedi = sum(1 for s in t["sporcular"] for x in t["testler"] if ot_durumu(t, x, s) == "gelmedi")
        st.success(f"Tüm ölçümler girildi: {taslak_deger_sayisi(t)} değer"
                   + (f", {gelmedi} ölçümde sporcu gelmedi." if gelmedi else "."))
        st.caption("İsterseniz Tablo kipinde hepsini birlikte görüp düzeltebilirsiniz.")
        kayitlar, _ = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, {})
        return {"etiket": f"Oturumu kaydet ({len(kayitlar)} kayıt)", "cb": _ot_kaydet_cb,
                "args": (bilgiler, testler, yollar, tarih, True), "disabled": not kayitlar}
    test, sporcu = konum
    yap, top = ot_ilerleme(t, test)
    st.markdown(f"**Test {t['testler'].index(test) + 1} / {len(t['testler'])} · {_html.escape(test_etiketli(test))}**")
    st.markdown(ot_ilerleme_html(yap, top, f"{yap} / {top} sporcu"), unsafe_allow_html=True)
    sol, sag = st.columns([1, 2])
    with sol:
        st.markdown(ot_sira_cipleri_html(t, test, sporcu), unsafe_allow_html=True)
    with sag:
        st.markdown(f"### {_html.escape(ad_bicimi(sporcu))}")
        dv = t["degerler"].get(sporcu) or {}
        hatalar = st.session_state.get("ots::hatalar", {})

        def alan(d):
            c = oturum_sutunu(test, d)
            anahtar = f"ot_g::{sporcu}::{c}"
            sayisal = not METIN_DEGISKEN_KALIBI.search(d)
            v = str(dv.get(c, "") or "")
            st.text_input(d, key=anahtar, placeholder=ot_ornek_deger(test, d, bilgiler.get(sporcu)) if sayisal else "",
                          help=ACIKLAMALAR.get(d) or None, on_change=_ot_deger_cb,
                          args=(test, sporcu, c, anahtar, sayisal),
                          **({} if anahtar in st.session_state else {"value": v.replace(".", ",") if sayisal else v}))
            if hatalar.get(anahtar):
                st.error("Sayı girin (virgül ya da nokta kullanılabilir). Bu alan taslağa yazılmadı.")

        with st.container(key="ot-sayilar"):
            for d in [d for d in testler[test] if not METIN_DEGISKEN_KALIBI.search(d)]:
                alan(d)
        for d in [d for d in testler[test] if METIN_DEGISKEN_KALIBI.search(d)]:
            alan(d)
        _ot_sayi_klavyesi()
        for k_h, v_h in ot_hesaplanan(test, {d: dv.get(oturum_sutunu(test, d), "") for d in testler[test]},
                                      bilgiler.get(sporcu, {})).items():
            st.markdown(f'<div class="ot-otomatik" role="status"><span class="sp-etiket">{_html.escape(k_h)} · '
                        f'otomatik</span><div class="ot-otomatik-deger">{_html.escape(_konum_sayi(v_h))}</div></div>',
                        unsafe_allow_html=True)
        n = (t["notlar"].get(sporcu) or {}).get(test) or {}
        k_cip, k_not = f"ot_n::{sporcu}::{test}", f"ot_nm::{sporcu}::{test}"
        not_kutusu = st.container(key="ot-not")
        if hasattr(st, "pills"):
            not_kutusu.pills("Not (isteğe bağlı)", list(NOT_CIPLERI), selection_mode="multi", key=k_cip,
                     on_change=_ot_not_cb, args=(test, sporcu, k_cip, k_not),
                     **({} if k_cip in st.session_state else {"default": list(n.get("etiketler", []))}))
        else:
            with not_kutusu:
                coklu_secim("Not (isteğe bağlı)", list(NOT_CIPLERI), key=k_cip, on_change=_ot_not_cb,
                            args=(test, sporcu, k_cip, k_not),
                            **({} if k_cip in st.session_state else {"default": list(n.get("etiketler", []))}))
        st.text_input("Kısa not", key=k_not, placeholder="ör. ikinci denemede kaydı", on_change=_ot_not_cb,
                      args=(test, sporcu, k_cip, k_not),
                      **({} if k_not in st.session_state else {"value": str(n.get("metin", "") or "")}))
        mesaj = st.session_state.pop("ots::mesaj", None)
        if mesaj:
            st.error(mesaj)
        ayk = st.session_state.get("ots::aykiri")
        if ayk and list(ayk["anahtar"]) == [test, sporcu]:
            st.warning("**! Kontrol et** — " + OT_AYKIRI_SORU + "\n\n" + "\n".join(f"- {u}" for u in ayk["uyarilar"]))
            st.button("Düzelt", key="ot_duzelt", on_click=lambda: st.session_state.pop("ots::aykiri", None))
            return {"etiket": "Evet, kaydet", "cb": _ot_onayla_cb, "args": (test, sporcu)}
        g1, g2 = st.columns(2)
        g1.button("← Geri al", key="ot_geri_al", on_click=_ot_geri_al_cb, args=(test, sporcu), width="stretch",
                  disabled=ot_kuyrugu(t).index((test, sporcu)) == 0, help="Bir önceki sporcuya dön ve düzelt")
        g2.button("Atla (gelmedi)", key="ot_atla", on_click=_ot_atla_cb, args=(test, sporcu), width="stretch")
    return {"etiket": "Kaydet ve sıradaki →", "cb": _ot_sonraki_cb, "args": (test, sporcu, bilgiler, testler, tarih)}


def _ot_tablo_kipi(t, testler, bilgiler, tarih, yollar):
    """Tablo kipi: tüm sporcular satır, denemeler sütun (Enter alt hücre, Tab sağ hücre); test başına not sütunu."""
    surum = st.session_state.get("ot_tablo_surum", 0)
    taban = st.session_state.get("ots::tablo_taban")
    if not taban or taban[0] != surum:
        taban = (surum, taslak_duzenleme_tablosu(t, testler))
        st.session_state["ots::tablo_taban"] = taban
    yapilandirma = {"Sporcu": st.column_config.TextColumn("Sporcu", disabled=True)}
    for test, ds in testler.items():
        kisa = test if len(test) <= 26 else test.split(" (")[0].split(" — ")[0][:26]
        for d in ds:
            yardim = f"{test} — {ACIKLAMALAR.get(d, d)}"
            yapilandirma[oturum_sutunu(test, d)] = st.column_config.TextColumn(
                f"{kisa} · {d}", help=yardim + ("" if METIN_DEGISKEN_KALIBI.search(d) else " (virgül ya da nokta: 4,52)"))
        yapilandirma[oturum_sutunu(test, NOT_DEGISKENI)] = st.column_config.TextColumn(
            f"{kisa} · Not", help="Kısa not. Hazır notlar: " + "; ".join(NOT_CIPLERI) + " (noktalı virgülle ayırın).")
    tablo = st.data_editor(taban[1], column_config=yapilandirma, hide_index=True, num_rows="fixed", width="stretch",
                           key=f"ot_tablo::{surum}")
    degisti, gecersiz = taslak_tablodan(t, tablo, testler)
    if degisti:
        taslak_yaz(t)
    if gecersiz:
        st.error("**! Sayı değil** — bu hücreler taslağa yazılmadı:\n\n"
                 + "\n".join(f"- {s_}: {c_.split(' › ', 1)[1]} = “{v_}”" for s_, c_, v_ in gecersiz))
    hes = []
    for s in t["sporcular"]:
        dv = t["degerler"].get(s) or {}
        for test, ds in testler.items():
            h = ot_hesaplanan(test, {d: dv.get(oturum_sutunu(test, d), "") for d in ds}, bilgiler.get(s, {}))
            if h:
                hes.append({"Sporcu": s, "Test": test, **{f"{k} · otomatik": _konum_sayi(v) for k, v in h.items()}})
    if hes:
        st.markdown("**Otomatik hesaplanan** (girilen değerlerden)")
        st.dataframe(pd.DataFrame(hes), hide_index=True, width="stretch")
    kayitlar, _ = taslak_kayitlari(t, bilgiler, testler, yollar, tarih, {})
    st.caption(f"Kaydedilecek: {len(kayitlar)} test kaydı, {len({k['Sporcu'] for k in kayitlar})} sporcu. "
               "Boş hücreler kaydedilmez.")
    mesaj = st.session_state.pop("ots::mesaj", None)
    if mesaj:
        st.error(mesaj)
    ayk = st.session_state.get("ots::aykiri_tablo")
    if ayk:
        st.warning("**! Kontrol et** — " + OT_AYKIRI_SORU + "\n\n" + "\n".join(f"- {u}" for u in ayk))
        st.button("Düzelt", key="ot_duzelt_t", on_click=lambda: st.session_state.pop("ots::aykiri_tablo", None))
        return {"etiket": "Evet, kaydet", "cb": _ot_kaydet_cb, "args": (bilgiler, testler, yollar, tarih, True)}
    return {"etiket": "Oturumu kaydet", "cb": _ot_kaydet_cb, "args": (bilgiler, testler, yollar, tarih, False),
            "disabled": not kayitlar}


def _ot_ozet_satirlari(adim, t):
    """Tamamlanan adımlar: tek satır özet + 'Düzenle' (her adımda geri dönüş)."""
    testler = (t or {}).get("testler") if adim == 4 else st.session_state.get("ots::testler", [])
    sporcular = (t or {}).get("sporcular") if adim == 4 else st.session_state.get("ots::sporcular", [])
    kisalt = lambda xs: ", ".join(ad_bicimi(x) for x in xs[:3]) + (f" ve {len(xs) - 3} daha" if len(xs) > 3 else "")
    tarih = st.session_state.get("ot_tarih") or date.today()
    ozet = {1: f"{len(testler or [])} test: {kisalt(list(testler or []))}",
            2: f"{len(sporcular or [])} sporcu: {kisalt(list(sporcular or []))}",
            3: " · ".join(x for x in (str(st.session_state.get("ot_ad", "") or "").strip(),
                                       tarih.strftime("%d.%m.%Y"), str(st.session_state.get("ot_yer", "") or "").strip(),
                                       str(st.session_state.get("ot_uyg", "") or "").strip()) if x)}
    for i in range(1, adim):
        c1, c2 = st.columns([5, 1], vertical_alignment="center")
        c1.markdown(f"✓ **{i}. {OT_ADIMLAR[i - 1]}** — {_html.escape(ozet[i])}")
        c2.button("Düzenle", key=f"ot_duzenle::{i}", on_click=_ot_adim_git, args=(i,), width="stretch")


def _ot_alt_cubuk(adim, ana, t):
    """Sabit alt çubuk: '← Geri' · 'N sporcu · M test · K değer' · tek ana düğme (sağda, ≥ 48 px)."""
    n_s = len((t or {}).get("sporcular") or []) if adim == 4 else len(st.session_state.get("ots::sporcular", []) or [])
    n_t = len((t or {}).get("testler") or []) if adim == 4 else len(st.session_state.get("ots::testler", []) or [])
    with st.container(key="ot-altcubuk"):
        c1, c2, c3 = st.columns([1, 2, 1.6], vertical_alignment="center")
        if adim > 1:
            c1.button("← Geri", key="ot_geri", on_click=_ot_adim_git, args=(adim - 1,), width="stretch")
        c2.markdown(f'<p class="ot-ozet">{n_s} sporcu · {n_t} test · {taslak_deger_sayisi(t) if adim == 4 else 0} '
                    f'değer</p>', unsafe_allow_html=True)
        if ana:
            with c3.container(key="ot-ana"):
                st.button(ana["etiket"], key="ot_ana", type="primary", width="stretch", on_click=ana["cb"],
                          args=tuple(ana.get("args", ())), disabled=bool(ana.get("disabled", False)))


def test_oturumu_sayfasi():
    """Test Oturumu (Paket 38b): 4 adım; değerler Sıradaki ya da Tablo kipinde; taslak her değişiklikte diske."""
    _ot_durum_koru()
    st.header("Test Oturumu — Toplu Giriş")
    st.caption("Testleri seç → sporcuları seç → tarih, yer ve uygulayanı gir → değerleri gir → tek düğmeyle kaydet. "
               "Ölçüm sırasında karşılaştırma gösterilmez; norm özeti kayıttan sonra Sonuçlar sayfasındadır.")
    bolum_terimleri(["Olağandışı değer (P1–P99)", "Norm", "Doğum çeyreği"])
    if not os.path.exists(SPORCU_DOSYA):
        st.info("Önce Sporcu Girişi sayfasından sporcu ekleyin.")
        return
    df_ot = pd.read_excel(SPORCU_DOSYA)
    df_ot["_ad"] = df_ot["Ad"].astype(str) + " " + df_ot["Soyad"].astype(str)
    if GRUP_KOLON not in df_ot.columns:
        df_ot[GRUP_KOLON] = ""
    df_ot["_grup"] = df_ot[GRUP_KOLON].map(lambda g: "" if not _girildi(g) else str(g).strip())
    bilgiler = {r["_ad"]: r.to_dict() for _, r in df_ot.iterrows()}
    sonuc = st.session_state.pop("ots::sonuc", None)
    if sonuc:
        st.success(sonuc)
        st.button("Sonuçları gör →", key="ot_sonuca", on_click=_sayfaya_git, args=("Sonuçları Görüntüle",))

    t = st.session_state.get("ots::taslak")
    if t is None and not st.session_state.get("ots::taslak_sorma"):
        disk = taslak_oku()
        if disk:
            if st.session_state.pop("ots::otomatik", False):        # sayfa yenilendi: doğrudan kaldığı yerden
                _ot_taslak_yukle(disk, df_ot)
                t = disk
            else:
                with st.container(border=True):
                    tarih_ = str(disk.get("bilgi", {}).get("tarih", ""))
                    st.markdown(f"**Yarım kalan oturum var.** {'.'.join(reversed(tarih_.split('-')))} · "
                                f"{len(disk['sporcular'])} sporcu · {len(disk['testler'])} test · "
                                f"{taslak_deger_sayisi(disk)} değer girildi"
                                + (f" (son kayıt {disk['zaman']})" if disk.get("zaman") else "") + ".")
                    d1, d2 = st.columns(2)
                    with d1.container(key="ot-taslak-devam"):
                        st.button("Devam et", type="primary", key="ot_taslak_devam", width="stretch",
                                  on_click=_ot_taslak_yukle, args=(disk, df_ot))
                    d2.button("Taslağı sil, yeni oturum", key="ot_taslak_sil", width="stretch",
                              on_click=_ot_taslak_temizle)
                return
    adim = int(st.session_state.get("ot_adim", 1))
    if adim == 4 and not t:
        adim = 3
    st.markdown(ot_adim_seridi_html(adim), unsafe_allow_html=True)
    _ot_ozet_satirlari(adim, t)
    st.markdown(f"##### {adim}. {OT_ADIMLAR[adim - 1]}")
    if adim == 1:
        ana = _ot_adim_testler(df_ot)
    elif adim == 2:
        ana = _ot_adim_sporcular(df_ot)
    elif adim == 3:
        ana = _ot_adim_bilgi()
    else:
        _qp_ayarla("taslak", "1")                                   # yenilenirse taslağa dön
        testler = {x: list(test_bilgisi(x)["degiskenler"]) for x in t["testler"]
                   if (test_bilgisi(x) or {}).get("degiskenler")}
        yollar = {x: test_yolu(x) for x in testler}
        try:
            tarih = date.fromisoformat(str(t.get("bilgi", {}).get("tarih")))
        except ValueError:
            tarih = date.today()
        st.radio("Giriş kipi", OT_KIPLER, horizontal=True, key="ot_kip", on_change=_ot_tablo_yenile,
                 help="Sıradaki: ekranda tek sporcu ve tek test (telefon/tablet). Tablo: tüm sporcular satır, "
                      "denemeler sütun (bilgisayar). Varsayılan cihaza göre gelir; buradan değiştirilebilir.",
                 **({} if "ot_kip" in st.session_state
                    else {"index": OT_KIPLER.index(varsayilan_kip(_istemci_ajani()))}))
        ana = (_ot_siradaki_kipi if st.session_state.get("ot_kip") == "Sıradaki" else _ot_tablo_kipi)(
            t, testler, bilgiler, tarih, yollar)
        st.caption(f"{OT_TASLAK_NOTU}" + (f" ({t['zaman']})" if t.get("zaman") else "")
                   + ". Kaydet'e basılana kadar sonuç dosyasına yazılmaz.")
    _ot_alt_cubuk(adim, ana, t)


# ════════════════════════════════════════════════════════════
# NİTELİĞE GÖRE TEST BUL (Paket 38b)
# Kullanıcıya 9 sade ad; her ad bir ya da iki iç niteliği kapsar ("Kas dayanıklılığı" = kuvvette devamlılık +
# anaerobik). test_niteligi / test_bileseni ve sıra uyarısı DEĞİŞMEZ — yalnız görünen etiket ve gruplama.
# Niteliği olmayan testler (anket, adım sayısı, çok bileşenli batarya, EMG) "Diğer" kartında; kaybolmaz.
# ════════════════════════════════════════════════════════════


def _nitelik_testi_sec(ad):
    """Test seçildi → Test Oturumu Adım 2 (sporcular); sıralı listede yalnız bu test."""
    for k_ in [k for k in st.session_state if str(k).startswith("ot_testler_")] + ["ot::ek", "ot::sira"]:
        st.session_state.pop(k_, None)
    st.session_state["ot_kaynak"] = "Serbest seçim"
    st.session_state["ot::ek"] = [kanonik_test(ad)]
    st.session_state["ot::sira"] = [kanonik_test(ad)]
    st.session_state["ots::testler"] = [kanonik_test(ad)]
    st.session_state["ots::calisma"] = {"ad": None, "zaman": None}
    st.session_state["ot_adim"] = 2
    st.session_state["sayfa"] = "Test Oturumu"


def nitelik_sayfasi():
    st.header("Niteliğe göre test bul")
    st.caption("Ölçmek istediğiniz niteliği seçin; o niteliğin testleri listelenir. Bir testi seçince Test Oturumu "
               "sporcu seçimiyle (Adım 2) açılır.")
    kartlar = [k for k, _ in NITELIK_KARTLARI] + ([NITELIK_DIGER] if nitelik_testleri(NITELIK_DIGER) else [])
    secili = st.session_state.get("nt_kart")
    for bas in range(0, len(kartlar), 3):
        cols = st.columns(3)
        for i, (c, k) in enumerate(zip(cols, kartlar[bas:bas + 3])):
            with c.container(key=f"nt-kart-{bas + i}"):
                st.button(f"{'✓ ' if k == secili else ''}{k} · {len(nitelik_testleri(k))} test", key=f"nt::{k}",
                          width="stretch", on_click=lambda k_=k: st.session_state.__setitem__("nt_kart", k_))
    if not secili:
        return
    liste = nitelik_testleri(secili)
    st.markdown(f"#### {secili} — {len(liste)} test")
    if secili == "Kas dayanıklılığı":
        st.caption("Kuvvette devamlılık (ör. şınav, mekik, barfiks) ve anaerobik dayanıklılık (ör. Wingate, RSA) testleri.")
    elif secili == NITELIK_DIGER:
        st.caption("Tek bir niteliğe bağlanmayan testler: anketler, adım sayısı, çok bileşenli bataryalar, EMG.")
    ara = st.text_input("Bu kartta ara", key="nt_ara", placeholder="ör. Yo-Yo, 20m, Wingate")
    if ara.strip():
        liste = [t for t in liste if ara_katla(ara) in ara_katla(t["ad"])]
        st.caption(f"{len(liste)} test bulundu")
    for i, t in enumerate(liste):
        c1, c2 = st.columns([4, 1.3], vertical_alignment="center")
        c1.markdown(f"{_html.escape(t['ad'])}  \n<span style='font-size:0.875rem'>"
                    f"{_html.escape(' › '.join(p for p in t['yol'] if p))}</span>", unsafe_allow_html=True)
        toplu = t["ad"] not in TOPLU_GIRIS_DISI and (test_bilgisi(t["ad"]) or {}).get("degiskenler")
        if toplu:
            c2.button("Seç", key=f"nt::sec::{i}", width="stretch", on_click=_nitelik_testi_sec, args=(t["ad"],),
                      help="Test Oturumu'nda sporcu seçimine geç")
        else:
            c2.button("Test Uygula →", key=f"nt::uygula::{i}", width="stretch", on_click=_git_test_uygula,
                      args=(None, t["yol"], t["ad"]), help="Bu testin özel giriş ekranı var")


# ════════════════════════════════════════════════════════════
# SONUÇLAR — TEK SPORCU: DÖRT SORU KARTI (Paket 38b)
# Nasıl gelişiyor? · Yaşıtlarına göre nerede? · Güçlü ve geliştirilecek yönler · Hangi branşa uygun?
# Hesaplar mevcut işlevlerden (gelisim_ozeti, grup_ici_konum, sporcu_z_profili, brans_grubu_eslestir); yeni eşik
# yok: nitelik düzeyi normatif seviyeden (_veli_duzeyi: 5-6 güçlü, 3-4 orta, 1-2 geliştir), yaşıt kartı veli
# kartının koşullarıyla (yaş ≥ 11, n ≥ 20, yön tanımlı, vücut ölçüsü değil). Her kart kendi try/except'inde.
# 7 sekmeli ayrıntılı görünüm "Ayrıntılı analiz" anahtarıyla açılır (tüm sporcularda varsayılan).
# ════════════════════════════════════════════════════════════
BRANS_EN_AZ_NITELIK = 5
SONUC_YASIT_METNI = "Aynı yaş bandı ve cinsiyetteki {n} sporcunun çoğu {a}–{b} {birim} arasında."
NITELIK_DURUM_ETIKETI = {"ust": ("✓", "güçlü"), "orta": ("≈", "orta"), "alt": ("!", "geliştir")}
NITELIK_NOTU = "Yön göstericidir, tanı değil."


def sonuc_kart_gorunumu():
    """Tek sporcu seçili ve 'Ayrıntılı analiz' kapalı → dört soru kartı."""
    s = st.session_state.get("sonuc_sporcu")
    return (os.path.exists(TEST_DOSYA) and s not in (None, "Tüm Sporcuları Göster")
            and not st.session_state.get("sonuc_ayrintili", False))


def sonuc_suzgecleri(df_test):
    """Oturum ve sporcu süzgeci (ayrıntılı görünümle aynı anahtarlar: sonuc_oturum, sonuc_sporcu)."""
    if "Oturum" in df_test.columns:
        _ot_deger = df_test["Oturum"].fillna("").astype(str).str.strip()
        df_oturumlu = df_test[(_ot_deger != "") & (_ot_deger != "nan")]
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
    return df_test, st.selectbox("Sporcu Filtrele", sporcular, key="sonuc_sporcu", format_func=ad_bicimi)


def notlu_olcum_sayisi(df):
    if "Notlar" not in df.columns:
        return 0
    n = df["Notlar"].fillna("").astype(str).str.strip()
    return int(((n != "") & (n != "nan")).sum())


def sporcu_ozet_kutulari(df_s, ozetler):
    """Dört özet kutusu: Test, Ölçüm, Gelişen test (son iki ölçüm iyi yönde), Not düşülen ölçüm."""
    gelisen = len({o["test"] for o in ozetler if o.get("iyi_yonde") is True})
    return [("Test", df_s["Test"].nunique()), ("Ölçüm", len(df_s)), ("Gelişen test", gelisen),
            ("Not düşülen ölçüm", notlu_olcum_sayisi(df_s))]


def varsayilan_gelisim_cifti(ozetler):
    """Kart 1'in ilk açılan testi: en çok ölçümü olan, eşitse son ölçümü en yeni olan."""
    def anahtar(o):
        t = _tarih_gunu(o["olcumler"][-1][0]) if o["olcumler"] else None
        return (len(o["olcumler"]), t or date.min)
    return max(range(len(ozetler)), key=lambda i: anahtar(ozetler[i])) if ozetler else None


def yon_oku(o):
    """Son iki ölçüm farkının oku: ▲ arttı, ▼ azaldı, = değişmedi (iyi/kötü sözle söylenir, renkle değil)."""
    if o.get("fark") is None:
        return ""
    return "▲" if o["fark"] > 0 else ("▼" if o["fark"] < 0 else "=")


def sonuc_karti_cumlesi(o):
    """Antrenör sonuç kartı (Paket 38c): "7 cm arttı — daha iyi" / "1 düşme arttı — daha kötü"; yön yoksa yalnız değişim."""
    m = gelisim_metni(o)
    return m.replace(" — bir önceki ölçümden düşük", " — daha kötü")


def yasit_karti_metni(k, ad):
    return (SONUC_YASIT_METNI.format(n=k["n"], a=_aralik_sayi(k["p10"], k["birim"]), b=_aralik_sayi(k["p90"], k["birim"]),
                                     birim=k["birim"]).replace("  ", " ")
            + " " + VELI_ARALIK_YERI[veli_aralik_yeri(k)].format(ad=ad))


def yasit_yetersiz_nedeni(k):
    """Yaşıt kartı gösterilemiyorsa kısa neden (veli kartının koşulları)."""
    if k.get("durum") != "tamam":
        return f"Aynı yaş bandı ve cinsiyette yeterli ölçüm yok (n = {k.get('n', 0)})."
    if test_niteligi(k["test"]) == "antropometri":
        return "Vücut ölçülerinde yaşıt karşılaştırması gösterilmez."
    if k.get("yas") is None or k["yas"] < VELI_KONUM_EN_AZ_YAS:
        return f"{VELI_KONUM_EN_AZ_YAS} yaş altında yaşıt karşılaştırması gösterilmez."
    if k["n"] < GRUP_KONUM_YUZDELIK_N:
        return f"En az {GRUP_KONUM_YUZDELIK_N} sporcu gerekir; şu an n = {k['n']}."
    if k.get("yon") is None:
        return "Bu ölçünün iyi yönü tanımlı değil."
    return ""


def nitelik_durumlari(zp):
    """
    Nitelik başına normatif seviye (1-6) ortalaması: her testten en iyi değişkeni (veli özetindeki gibi), vücut
    ölçüleri ve niteliksiz testler dışarıda. Düzey _veli_duzeyi ile (yeni eşik yok).
    """
    gruplar = {}
    for r in (zp or {}).get("satirlar", []):
        if r.get("Tür") != "Performans" or not r.get("Kategori"):
            continue
        sev = kategori_bilgisi(r["Kategori"])["seviye"]
        kart = nitelik_karti(r["Test"])
        if sev is None or kart in (NITELIK_DIGER, "Vücut ölçüleri"):
            continue
        g = gruplar.setdefault(kart, {})
        g[r["Test"]] = max(g.get(r["Test"], 0), sev)
    sonuc = []
    for kart, _ in NITELIK_KARTLARI:
        if kart in gruplar:
            s = list(gruplar[kart].values())
            ort = sum(s) / len(s)
            sonuc.append({"nitelik": kart, "seviye": round(ort, 1), "test_sayisi": len(s), "durum": _veli_duzeyi(ort)})
    return sonuc


def nitelik_cubuklari_html(durumlar):
    """Yatay çubuklar; renge ek olarak simge ve kelime (✓ güçlü, ≈ orta, ! geliştir)."""
    p = ['<div class="sk-cubuklar">']
    for d in durumlar:
        isaret, kelime = NITELIK_DURUM_ETIKETI[d["durum"]]
        sev = max(1, min(6, round(d["seviye"])))
        k = kategori_bilgisi(next(a for a, s_, *_ in palet("acik")["norm"] if s_ == sev))
        renk = k["zemin"] if sev != 1 else k["yazi"]
        aciklama = f"{d['nitelik']}: {kelime} (ortalama seviye {_konum_sayi(d['seviye'])} / 6, {d['test_sayisi']} test)"
        p.append(f'<div class="sk-cubuk" role="img" aria-label="{_html.escape(aciklama)}" '
                 f'style="display:grid;grid-template-columns:minmax(110px,1fr) 2fr auto;gap:10px;align-items:center;'
                 f'margin:6px 0;font-size:14px"><span>{_html.escape(d["nitelik"])}</span>'
                 f'<span style="background:{renk_css("cizgi")};border-radius:6px;height:14px;display:block">'
                 f'<span style="display:block;height:14px;border-radius:6px;width:{d["seviye"] / 6 * 100:.0f}%;'
                 f'background:{renk}"></span></span><b>{isaret} {kelime}</b></div>')
    p.append("</div>")
    return "".join(p)


def excel_verisi(dataframe):
    """Sonuç tablosunu sütun genişlikleri ayarlı .xlsx olarak döner."""
    buffer = BytesIO()
    cols = [k for k in dataframe.columns if k != "Tarih_dt"]
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe[cols].to_excel(writer, index=False, sheet_name="Sonuçlar")
        ws = writer.sheets["Sonuçlar"]
        for i, kolon in enumerate(cols, start=1):
            uz = [len(str(x)) for x in dataframe[kolon].tolist()]
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = max(max(uz) if uz else 0, len(str(kolon))) + 4
    return buffer.getvalue()


def kart_hatasi(hata):
    """Bir kartın hatası öbürlerini durdurmaz: sade Türkçe uyarı, teknik iz 'Ayrıntı' açılırında."""
    import traceback as _tb
    st.warning("Bu kart şu an gösterilemiyor; öbür kartlar çalışmaya devam ediyor.", icon=":material/error:")
    with st.expander("Ayrıntı"):
        st.code("".join(_tb.format_exception(type(hata), hata, hata.__traceback__)), language=None)


@st.dialog("Tüm testlerin gelişimi", width="large")
def tum_gelisim_penceresi(sporcu, df_test):
    ozetler = [gelisim_ozeti(df_test, sporcu, t, d) for t, d in rapor_konum_degiskenleri(df_test, sporcu)]
    if not ozetler:
        st.info("Bu sporcunun sayısal sonucu yok.")
        return
    st.markdown(gelisim_bolumu_html(ozetler, {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}),
                unsafe_allow_html=True)


def _nitelik_kartina_git(kart):
    st.session_state["nt_kart"] = kart
    st.session_state["sayfa"] = "Niteliğe göre test bul"


def sonuclar_sporcu_sayfasi():
    """Tek sporcu: sporcu kartı, dört özet kutusu, dört soru kartı, en altta kapalı 'Tüm kayıtlar'."""
    st.header("Test Sonuçları ve Analiz")
    df_tum = test_tablosu_duzelt(pd.read_excel(TEST_DOSYA))
    df_tum["Tarih_dt"] = pd.to_datetime(df_tum["Tarih"], format="%d.%m.%Y", errors="coerce")
    df_test, filtre = sonuc_suzgecleri(df_tum)
    if filtre == "Tüm Sporcuları Göster":           # seçim artık geçersiz: ayrıntılı görünüme dön
        st.rerun()
    st.toggle("Ayrıntılı analiz (7 sekme)", key="sonuc_ayrintili",
              help="Veri tablosu, trend, karşılaştırma, normatif konum, profil, Z-skor ve branşa yönlendirme sekmeleri.")
    df_s = df_test[df_test["Sporcu"] == filtre]
    renk = {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}
    kp = sporcu_profil_bilgisi(filtre)
    ad = ad_bicimi(str(kp.get("Ad", "") or "").strip() or filtre)
    ciftler = rapor_konum_degiskenleri(df_test, filtre)
    ozetler = [gelisim_ozeti(df_test, filtre, t, d) for t, d in ciftler]

    with st.container(border=True):                 # sporcu kartı
        son_t = df_s["Tarih_dt"].max()
        alanlar = [("Yaş", kp.get("Yaş")), ("Cinsiyet", kp.get("Cinsiyet")), ("Kilo", kp.get("Kilo (kg)")),
                   ("Grup", kp.get(GRUP_KOLON))]
        bilgi = " · ".join(f"{e}: {_sayi_kisa(v) if isinstance(v, float) else v}{' kg' if e == 'Kilo' else ''}"
                           for e, v in alanlar if _girildi(v))
        c1, c2, c3 = st.columns([2.4, 1.2, 1.4], vertical_alignment="center")
        c1.markdown(f"### {_html.escape(ad_bicimi(filtre))}\n{_html.escape(bilgi)}  \n{df_s['Test'].nunique()} test · "
                    f"{len(df_s)} kayıt · son ölçüm {son_t.strftime('%d.%m.%Y') if pd.notna(son_t) else '—'}")
        if c2.button("Grup içi konum", icon=":material/groups:", key="gk_ac", width="stretch"):
            grup_konum_penceresi(filtre, df_tum)
        c3.button("Veli raporu (PDF)", icon=":material/description:", key="sk_veli", width="stretch",
                  on_click=_git_rapor, args=(filtre,),
                  help="Raporlar sayfasında açılır; tarayıcıda Yazdır → PDF olarak kaydedin.")
    st.markdown(ozet_kartlari_html(sporcu_ozet_kutulari(df_s, ozetler)), unsafe_allow_html=True)

    secim = None
    if ciftler:
        anahtarlar = [f"{t} › {d}" for t, d in ciftler]
        _gecerli_secim("sk_test", anahtarlar)
        secim_k = st.selectbox("Kartlardaki test", anahtarlar, key="sk_test",
                               format_func=lambda k: test_degisken_etiketi(*k.split(" › ", 1)),
                               **({} if "sk_test" in st.session_state
                                  else {"index": varsayilan_gelisim_cifti(ozetler)}))
        secim = anahtarlar.index(secim_k)

    ust = st.columns(2)
    alt = st.columns(2)
    with ust[0].container(border=True):             # 1 · Nasıl gelişiyor?
        try:
            st.markdown("#### Nasıl gelişiyor?")
            if secim is None:
                st.info("Bu sporcunun sayısal sonucu yok.")
            else:
                o = ozetler[secim]
                t_son, v_son = o["olcumler"][-1]
                st.markdown(f"Son değer: **{_konum_sayi(v_son)}{(' ' + o['birim']) if o['birim'] else ''}** ({t_son})")
                if len(o["olcumler"]) >= 2:
                    st.markdown(f"**{yon_oku(o)} {_html.escape(sonuc_karti_cumlesi(o))}**")
                    st.markdown(_gelisim_grafik_svg(o, renk), unsafe_allow_html=True)
                else:
                    st.caption("İlk ölçüm; gelişim ikinci ölçümle görünür.")
            if ciftler:
                if st.button("Tüm testlerin gelişimi →", key="sk_tum_gelisim", type="tertiary"):
                    tum_gelisim_penceresi(filtre, df_test)
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with ust[1].container(border=True):             # 2 · Yaşıtlarına göre nerede?
        try:
            st.markdown("#### Yaşıtlarına göre nerede?")
            k = (grup_ici_konum(df_tum, pd.read_excel(SPORCU_DOSYA) if os.path.exists(SPORCU_DOSYA) else pd.DataFrame(),
                                filtre, *ciftler[secim]) if secim is not None else {"durum": "yetersiz", "n": 0})
            if veli_konum_uygun(k):
                st.markdown(yasit_karti_metni(k, ad))
                st.markdown(konum_seridi_veli_svg(k, renk), unsafe_allow_html=True)
                st.caption(f"Antrenör notu: yüzdelik ≈ P{k['yuzdelik']} · n = {k['n']}" if k.get("yuzdelik") is not None
                           else f"Antrenör notu: n = {k['n']}")
            else:
                st.markdown("**Karşılaştırma için yeterli veri yok.**")
                neden = yasit_yetersiz_nedeni(k)
                if neden:
                    st.caption(neden)
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with alt[0].container(border=True):             # 3 · Güçlü ve geliştirilecek yönler
        try:
            st.markdown("#### Güçlü ve geliştirilecek yönler")
            durumlar = nitelik_durumlari(sporcu_z_profili(df_test, filtre))
            if durumlar:
                st.markdown(nitelik_cubuklari_html(durumlar), unsafe_allow_html=True)
                st.caption(NITELIK_NOTU + " Çubuk: o nitelikteki testlerin normatif seviye ortalaması (1-6).")
            else:
                st.info("Normla karşılaştırılan performans testi yok.")
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with alt[1].container(border=True):             # 4 · Hangi branşa uygun?
        try:
            st.markdown("#### Hangi branşa uygun?")
            kapsanan = sorted({nitelik_karti(t) for t in df_s["Test"].unique()} - {NITELIK_DIGER})
            if len(kapsanan) < BRANS_EN_AZ_NITELIK:
                st.markdown(f'<div style="border:2px dashed {renk_css("cizgi")};border-radius:10px;padding:12px 14px;'
                            f'font-size:14px">En az {BRANS_EN_AZ_NITELIK} farklı niteliği kapsayan test gerekir; '
                            f'şu an {len(kapsanan)} nitelik var.</div>', unsafe_allow_html=True)
                if st.toggle("Eksik testleri öner", key="sk_eksik"):
                    for kart in [k_ for k_, _ in NITELIK_KARTLARI if k_ not in kapsanan]:
                        st.button(f"{kart} testleri →", key=f"sk_eksik::{kart}", type="tertiary",
                                  on_click=_nitelik_kartina_git, args=(kart,))
            else:
                fsc = sporcu_fsc_profili(df_tum, filtre)
                esl = brans_grubu_eslestir(fsc, kp.get("Yaş"))
                if esl["uygun"]:
                    st.markdown("Fiziksel profili bu gruplara yakın (sıra yok): **"
                                + ", ".join(sorted(g for g, _ in esl["siralama"][:3])) + "**")
                    st.caption("Bilgilendiricidir, eleyici değildir; ilgi ve antrenman süresiyle birlikte okunur.")
                else:
                    st.info(esl.get("neden") or "Branş eşleştirmesi yapılamadı.")
                st.button("Ayrıntı: Branşa Yönlendirme →", key="sk_brans", type="tertiary",
                          on_click=lambda: st.session_state.__setitem__("sonuc_ayrintili", True))
        except Exception as _kart_h:
            kart_hatasi(_kart_h)

    with st.expander("Tüm kayıtlar", icon=":material/table_rows:", expanded=False):
        _tum_kolon = [k_ for k_ in df_s.columns if k_ != "Tarih_dt"]
        st.dataframe(df_s[[k_ for k_ in _tum_kolon if k_ not in ("Kategori", "Batarya")]], width="stretch")
        dosya_adi = re.sub(r"[^\w]+", "_", filtre).strip("_") + "_sonuclar.xlsx"
        st.download_button("⬇️ Excel (.xlsx) İndir", excel_verisi(df_s), key="sk_excel", file_name=dosya_adi,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ════════════════════════════════════════════════════════════
# YAN MENÜ
# ════════════════════════════════════════════════════════════
SAYFALAR = ["Ana Sayfa", "Sporcu Girişi", "Niteliğe göre test bul", "Test Uygula", "Test Oturumu",
            "Sonuçları Görüntüle", "Raporlar", "Kaynakça"]


def _sayfaya_git(hedef):
    st.session_state["sayfa"] = hedef


# Paket 38b: değer girilirken sayfa yenilendiyse (adreste ?taslak=1 ve diskte taslak) kaldığı yere döner
if "sayfa" not in st.session_state and _qp_al("taslak") == "1" and taslak_oku():
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ots::otomatik"] = True
# "Açılışta bu ekranı gösterme" seçiliyse oturumun ilk açılışı doğrudan iş sayfasına (menü aynen kalır)
if "sayfa" not in st.session_state and ayar_oku().get("yonlendirme_gizle"):
    st.session_state["sayfa"] = "Test Uygula" if os.path.exists(SPORCU_DOSYA) else "Sporcu Girişi"
sayfa = st.sidebar.selectbox("Menü", SAYFALAR, key="sayfa")
if sayfa != "Test Oturumu":
    _qp_ayarla("taslak", None)

# ── SAYFA 1: SPORCU GİRİŞİ ──
if sayfa == "Niteliğe göre test bul":
    nitelik_sayfasi()

elif sayfa == "Ana Sayfa":
    # ── AÇILIŞ EKRANI (Paket 13) ──
    st.markdown(f'<div class="sp-acilis">{logo_svg(72)}<div><h1>{_html.escape(UYGULAMA_ADI)}</h1>'
                f'<p>{_html.escape(ACILIS_TANIM)}</p></div></div>', unsafe_allow_html=True)
    yonlendirme_ekrani()

elif sayfa == "Sporcu Girişi":
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

# ── SAYFA 2: TEST UYGULA ──
elif sayfa == "Test Uygula":
    # Hiyerarşi (Paket 11): seçim → [giriş | normatif sonuç] yan yana → kaydet;
    # protokol ve kaynak katlanmış; rekor ve teknik ayrıntı en altta.
    st.header("Test Uygula")

    if not os.path.exists(SPORCU_DOSYA):
        st.error("Sistemde sporcu bulunamadı. Lütfen önce 'Sporcu Girişi' yapın.")
    else:
        df_sporcu = pd.read_excel(SPORCU_DOSYA)
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
                st.stop()
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
                tekli_test_yasi, sporcu_cinsiyet, sporcu_satir.get(DOGUM_KOLON), test_tarihi)
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

# ── SAYFA: TEST OTURUMU — toplu giriş (Paket 10) ──
elif sayfa == "Test Oturumu":
    test_oturumu_sayfasi()                       # Paket 38b: Testler → Sporcular → Oturum bilgisi → Değerler

# ── SAYFA 3: SONUÇLARI GÖRÜNTÜLE ──
elif sayfa == "Sonuçları Görüntüle" and sonuc_kart_gorunumu():
    sonuclar_sporcu_sayfasi()                    # Paket 38b: tek sporcu → dört soru kartı

elif sayfa == "Sonuçları Görüntüle":
    st.header("Test Sonuçları ve Analiz")

    if not os.path.exists(TEST_DOSYA):
        st.info("Kaydedilmiş test sonucu yok.")
    else:
        df_test = test_tablosu_duzelt(pd.read_excel(TEST_DOSYA))     # takma adlı kayıt asıl adla (Paket 27)

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
                    grup_konum_penceresi(filtre, test_tablosu_duzelt(pd.read_excel(TEST_DOSYA)))

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

        # ══ SEKME 3: SPORCU KARŞILAŞTIRMA ══
        with sekme3:
            try:
                st.subheader("Sporcular Arası Karşılaştırma")
                import plotly.graph_objects as go
                df_kars_tum = test_tablosu_duzelt(pd.read_excel(TEST_DOSYA))      # oturumlar arası: süzgeçsiz
                df_kars_tum["Tarih_dt"] = pd.to_datetime(df_kars_tum["Tarih"], format="%d.%m.%Y", errors="coerce")
                kars_oturumlar = oturum_secenekleri(df_kars_tum)
                kapsam = st.radio("Kapsam", KARSILASTIRMA_KAPSAMLARI, horizontal=True, key="kars_kapsam",
                                  help="Bireysel: her sporcunun son ölçümü. Tek oturum: yalnız seçilen oturum. "
                                       "Oturumlar arası: iki oturumda da ölçülen sporcuların farkı.")
                if kapsam != "Bireysel" and not kars_oturumlar:
                    st.info("Kayıtlarda oturum yok; oturum kapsamı için Test Oturumu sayfasından giriş yapın.")
                    kapsam = "Bireysel"
                kars_kaynak = df_test if kapsam == "Bireysel" else df_kars_tum
                k1, k2 = st.columns(2)
                with k1:
                    kars_test = st.selectbox("Test", sorted(kars_kaynak["Test"].unique().tolist()), key="kars_test")
                sayisal_kars = [k for k in kars_kaynak.columns if k not in META_KOLONLAR
                                and pd.to_numeric(kars_kaynak.loc[kars_kaynak["Test"] == kars_test, k],
                                                  errors="coerce").notna().any()]
                with k2:
                    kars_kolon = st.selectbox("Değişken", sayisal_kars if sayisal_kars else ["—"], key="kars_kolon")
                oturum_listesi = list(kars_oturumlar)
                if kapsam == "Tek oturum":
                    _gecerli_secim("kars_oturum", oturum_listesi)
                    on = st.session_state.get("sonuc_oturum")                  # Sonuçlar süzgeciyle aynı oturum
                    kars_oturum = st.selectbox("Oturum", oturum_listesi, format_func=kars_oturumlar.get,
                                               key="kars_oturum", **({} if "kars_oturum" in st.session_state else
                                                                     {"index": oturum_listesi.index(on) if on in oturum_listesi else 0}))
                elif kapsam == "Oturumlar arası":
                    o1, o2 = st.columns(2)
                    _gecerli_secim("kars_once", oturum_listesi)
                    _gecerli_secim("kars_sonra", oturum_listesi)
                    kars_sonra = o2.selectbox("Sonraki oturum", oturum_listesi, format_func=kars_oturumlar.get,
                                              key="kars_sonra")
                    kars_once = o1.selectbox("Önceki oturum", oturum_listesi, format_func=kars_oturumlar.get,
                                             key="kars_once", **({} if "kars_once" in st.session_state else
                                                                 {"index": min(1, len(oturum_listesi) - 1)}))

                if not sayisal_kars or kars_kolon == "—":
                    st.info("Bu test için sayısal değişken bulunamadı.")
                elif kapsam == "Oturumlar arası":
                    satirlar = oturumlar_arasi_fark(df_kars_tum, kars_test, kars_kolon, kars_once, kars_sonra)
                    if kars_once == kars_sonra:
                        st.info("Farklı iki oturum seçin.")
                    elif not satirlar:
                        st.info("İki oturumda da bu testi yapan sporcu yok.")
                    else:
                        tablo = pd.DataFrame(satirlar)
                        tablo["Sporcu"] = tablo["Sporcu"].map(ad_bicimi)
                        st.dataframe(tablo, hide_index=True, width="stretch",
                                     column_config={"Fark": st.column_config.NumberColumn("Fark", format="%+.2f")})
                        isaret = {"daha iyi": "✓", "daha kötü": "!", "değişmedi": "=", "arttı": "▲", "azaldı": "▼"}
                        fig2 = go.Figure(go.Bar(
                            y=tablo["Sporcu"], x=tablo["Fark"], orientation="h",
                            text=[f"{isaret[y]} {f:+.2f} {y}".replace(".", ",") for f, y in zip(tablo["Fark"], tablo["Yorum"])],
                            textposition="outside", cliponaxis=False,
                            marker_color=[grafik_renk("ana") if y == "daha iyi" else grafik_renk("ikincil")
                                          for y in tablo["Yorum"]]))
                        _m = max(0.01, float(tablo["Fark"].abs().max()))
                        fig2.update_layout(title=f"{kars_test} — {kars_kolon}: oturumlar arası fark",
                                           xaxis=dict(title="Fark (sonraki − önceki)", range=[-2.2 * _m, 2.2 * _m],
                                                      zeroline=True),
                                           height=max(260, 46 * len(tablo) + 120), **grafik_duzeni())
                        st.plotly_chart(fig2, width="stretch")
                        st.caption("Fark = sonraki − önceki. Yön sözcükle yazılır (✓ daha iyi, ! daha kötü); "
                                   "yön tanımsız ölçüde yalnız ▲ arttı / ▼ azaldı.")
                else:
                    degerler = oturum_degerleri(kars_kaynak, kars_test, kars_kolon,
                                                kars_oturum if kapsam == "Tek oturum" else None)
                    if not degerler:
                        st.info("Bu test için karşılaştırılacak veri yok.")
                    else:
                        df_kars_son = pd.DataFrame(sorted(degerler.items(), key=lambda x: -x[1]),
                                                   columns=["Sporcu", kars_kolon])
                        renkler = [grafik_renk("ikincil") if s != filtre else grafik_renk("ana")
                                   for s in df_kars_son["Sporcu"]]
                        fig2 = go.Figure(go.Bar(
                            x=df_kars_son["Sporcu"].map(ad_bicimi),
                            y=df_kars_son[kars_kolon],
                            text=df_kars_son[kars_kolon].round(2),
                            textposition="outside",
                            marker_color=renkler,
                        ))
                        fig2.update_layout(
                            title=f"{kars_test} — {kars_kolon} Karşılaştırması"
                                  + (f" · {kars_oturumlar.get(kars_oturum, '')}" if kapsam == "Tek oturum" else ""),
                            xaxis_title="Sporcu",
                            yaxis_title=kars_kolon,
                            **grafik_duzeni(),
                        )
                        st.plotly_chart(fig2, width="stretch")
                        st.caption("Mavi: seçili sporcu · gri: diğer sporcular")
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
                if os.path.exists(SPORCU_DOSYA):
                    df_sp = pd.read_excel(SPORCU_DOSYA)
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
                    if esl["uygun"]:
                        for g in pen["fiziksel"] if pen else sorted(x for x, _ in esl["siralama"][:3]):
                            isaret = " ★" if pen and g in pen["kesisim"] else ""
                            st.markdown(f"- **{g}**{isaret}")
                        st.caption("Sırasız; bilgilendiricidir, eleyici değildir.")
                    else:
                        st.caption(esl["neden"] or "Fiziksel karşılaştırma yapılamadı.")

                if pen:
                    if pen["kesisim"]:
                        st.success("★ **Hem seviyor hem fiziksel profili yakın:** " + ", ".join(pen["kesisim"])
                                   + ". Bu, en güçlü işarettir; bu grupların sporlarını denemek iyi bir başlangıçtır.")
                    if pen["yalniz_ilgi"] and esl["uygun"]:
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
                             "Fiziksel profil yakın üçte": ("Evet" if g in pen["fiziksel"] else
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
                else:
                    sira = esl["siralama"]
                    ilk_uc = sorted(g for g, _ in sira[:3])   # bilinçli olarak sırasız (alfabetik)
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


# ── SAYFA: RAPORLAR (Paket 7) ──
elif sayfa == "Raporlar":
    def rapor_goster(html_metin, yukseklik):
        """Yeni Streamlit'te st.iframe; eski sürümlerde components.html (2026'da kaldırılıyor)."""
        if hasattr(st, "iframe"):
            st.iframe(html_metin, height=yukseklik)
        else:
            import streamlit.components.v1 as components
            components.html(html_metin, height=yukseklik, scrolling=True)

    st.header("Raporlar")
    st.caption("Veli raporu sade dille yazılır; Z, persentil ve uzaklık sayısı içermez. Antrenör raporu tekniktir. "
               "İkisi de indirilebilir HTML'dir: tarayıcıda açıp Yazdır → PDF olarak kaydedilebilir.")
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
        dosya_on_ek = re.sub(r"[^\w]+", "_", r_sporcu).strip("_")
        r1, r2 = st.tabs(["Veli raporu", "Antrenör raporu"])
        with r1:
            veli_html = veli_raporu_html(r_veri)
            st.download_button("⬇️ Veli raporunu indir (HTML)", veli_html.encode("utf-8"),
                               file_name=f"{dosya_on_ek}_veli_raporu.html", mime="text/html", key="veli_indir")
            rapor_goster(veli_html, 1300 + 130 * veli_html.count('class="veli-satir"'))
        with r2:
            ant_html = antrenor_raporu_html(r_veri)
            st.download_button("⬇️ Antrenör raporunu indir (HTML)", ant_html.encode("utf-8"),
                               file_name=f"{dosya_on_ek}_antrenor_raporu.html", mime="text/html", key="ant_indir")
            rapor_goster(ant_html, 1400)

# ── SAYFA 4: KAYNAKÇA ──
elif sayfa == "Kaynakça":
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
