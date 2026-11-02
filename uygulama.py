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


from olcut.ortak import (
    veri_yolu,   # Bölme Aşama 2: olcut/ortak.py
    _desteklenen, _TR_KUCUK, _TR_BUYUK, _TR_BUYUT, _TR_KUCULT, _sozcuk_bicimi, ad_bicimi, _girildi, DOGUM_KOLON,
    tarih_coz, dogum_ceyregi, tam_yas, _yas_degeri, _e, _sayi, _tarih_gunu, guvenli_float,
    METIN_DEGISKEN_KALIBI, AYAR_DOSYA, ayar_oku, ayar_yaz, _tablo_guvenli, tablo_oku, _dt_simdi, NOT_CIPLERI,
    not_metni, not_coz)


from olcut.bilesenler import (   # Bölme Aşama 2: olcut/bilesenler.py
    coklu_secim, ilgi_anketi_formu, terimleri_bul, terim_metni, ac_dugmesi, bolum_terimleri, _hover_metni,
    baslik_ac, baslik_html, sutun_yardimi, _sira_tasi, _sira_cikar, _sira_listesi, _ot_ekle,
    _calisma_duzenleyici, _git_test_uygula, _git_oturum, _git_calisma, _oneri_git, _git_sonuclar,
    grup_konum_penceresi, sekme_hatasi, _git_rapor, _gecerli_secim, _nitelik_testi_sec, _nitelik_kartina_git,
    _sayfaya_git)


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


from olcut.analiz import (   # Bölme Aşama 2: olcut/analiz.py
    sporcu_fsc_profili, ESLESTIRME_YAS_ARALIGI, ESLESTIRME_EN_AZ_DEGISKEN, ESLESTIRME_DEGISKENLERI, _havuz_sd,
    ESLESTIRME_HAVUZ_SD, ESLESTIRME_SIMULASYON, brans_grubu_eslestir, ILGI_DOSYA, ILGI_ANKET_ADI, ILGI_UYARI,
    ILGI_OLCEK, ILGI_EN_AZ_MADDE, ILGI_SEVIYOR_ESIGI, ILGI_TARANAN_SAYISI, ILGI_TERCIHLERI, ILGI_HAKKINDA,
    ilgi_son_anket, ilgi_grup_puanlari, ilgi_etiketi, ilgi_fiziksel_pencereler, ANTRENMAN_KOLON,
    ANTRENMAN_TARIH_KOLON, ANTRENMAN_SECENEKLERI, ANTRENMAN_YARDIM, sporcu_profil_bilgisi, sporcu_antrenman,
    sporcu_antrenman_kaydet, _grup_radar_norm_anahtari, GRUP_RADAR_ESLESME, GRUP_RENKLERI, grup_radar_katmani,
    GRUP_KATMANI_NOTU, _RAPOR_RENK, _RAPOR_VURGU, radar_svg, _kisa_kaynak, z_satiri_karti, _brans_ornekleri,
    GRUP_KONUM_YUZDELIK_N, GRUP_KONUM_BANT_YIL, KENDI_DEGISIM_YASI, VELI_KONUM_EN_AZ_YAS, VELI_KONUM_METNI,
    KONUM_YETERSIZ_METNI, VELI_ARALIK_YUZDELIK, VELI_ARALIK_METNI, VELI_ARALIK_KIM, VELI_ARALIK_YERI,
    VELI_SAPMA_Z, VELI_DOGRU_MU_BASLIK, VELI_DOGRU_MU, VELI_ARALIK_NOTU, VELI_YASIT_BASLIK, YETISKIN_YAS,
    VELI_YETISKIN_HITAP, VELI_YETISKIN_IFADE, yetiskin_mi, veli_hitabi, _dogrusal_yuzdelik, _konum_sayi,
    BILINEN_BIRIMLER, SAYIM_BIRIMLERI, _birim, _olcum_satirlari, gelisim_ozeti, _DENEME_KALIBI,
    ana_sonuc_tanimi, _sonuc_degiskenleri, test_sonuc_serisi, test_gelisim_ozetleri, _profil_haritasi,
    grup_ici_konum, konum_metinleri, konum_seridi_svg, rapor_konum_degiskenleri, rapor_verisi, RAPOR_CSS,
    _tablolari_sar)


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


from veri.metinler import (   # Bölme Aşama 1: veri/metinler.py
    GUVEN_DUZEYLERI, ILGI_KAYNAKLARI, ILGI_MADDELERI, VELI_TEST_GRUBU, VELI_YORUMLARI, KAYNAKCA, DUNYA_REKORU,
    ACIKLAMALAR, TERIM_SOZLUGU, TERIM_ARAMA)

# PQ ve MQ açıklaması tek kaynakta: ACIKLAMALAR["PQ"], ACIKLAMALAR["MQ"] (Paket 8).


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



# ════════════════════════════════════════════════════════════
# GRUP İÇİ KONUM VE GELİŞİM (Paket 36). Veri yalnız test_sonuclari.xlsx (+ cinsiyet/yaş için sporcular.xlsx).
# Koruma kuralları: n her zaman görünür; n < GRUP_KONUM_YUZDELIK_N iken yüzdelik/sıralama sözcüğü yok (yalnız
# ortalamanın altı/üstü ve konum şeridi); havuz kanonik test adıyla, aynı değişken (aynı birim), aynı cinsiyet ve
# aynı 2 yıllık yaş bandı; sporcunun kendisi havuzda kalır ve vurgulanır; başka sporcuların adı hiçbir çıktıda yok.
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# VELİ RAPORU YORUMLARI (Paket 12) — ŞABLONLU, serbest metin YOK.
# Kurallar: (1) çocuğu değil sonucu tarif et; (2) gelecek yordaması yok;
# (3) düşük sonuç = gelişim alanı; (4) tek testten genel sonuç çıkarma.
# Z, persentil, norm kaynağı ve sınır notları veli raporunda geçmez.
# Cümleler: 6 kategori × 4 test grubu = 24 şablon (VELI_YORUMLARI). Denetim
# her şablonu yasak sözcüklere ve yapıya karşı tek tek kontrol eder.
# ════════════════════════════════════════════════════════════
from olcut.raporlar import (   # Bölme Aşama 2: olcut/raporlar.py
    VELI_GRUPLARI, VELI_DISARIDA, VELI_DISARIDA_NOTU, VELI_GRUP_DUZEY, VELI_GRUP_TEK_TEST, VELI_GRUP_TEST_YOK,
    VELI_SON_PARAGRAF, _VELI_SIMGE_YOLLARI, veli_grup_simgesi, veli_yorumu, _veli_duzeyi, veli_grup_durumu,
    VELI_ARALIK_Z, VELI_YER_ISARETI, VELI_YER_SIRASI, VELI_YAKLASIK_NOTU, VELI_SONUC_GIRIS, norm_araligi,
    veli_aralik_cumlesi, veli_sonuc_kutusu_html, veli_grup_aralik_durumu, veli_en_iyi_satir, veli_test_ozeti,
    veli_kutu_testleri, veli_sonuclari_html, TR_AY_KISA, _gelisim_grafik_svg, _tarih_konumlari, _etiket_secimi,
    _yon_isareti, gelisim_metni, BIRIM_EKLERI, sure_metni, ilerleme_cumlesi, test_degisken_etiketi,
    gelisim_karti_html, ilk_olcum_tablosu_html, gelisim_bolumu_html, VELI_BILESIK_OZET, VELI_BILESIK_NOTU,
    veli_bilesik_satiri, veli_bolumleri, veli_gelisim_html, veli_konum_uygun, _aralik_sayi, veli_aralik_yeri,
    veli_aralik_konumu, konum_seridi_veli_svg, veli_konum_metni, veli_konum_html, veli_raporu_html,
    RAPOR_TERIMLERI, antrenor_raporu_html, KAYNAKCA_DAYANAK, KAYNAKCA_SINIFLAR)


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


# ════════════════════════════════════════════════════════════
# PAKET 10 — TEST OTURUMU, SPORCU GRUBU, MAKULLÜK KONTROLÜ
# ------------------------------------------------------------
# Kayıt biçimi TEK yerde üretilir (test_kaydi_olustur): tekli giriş ve toplu giriş aynı
# fonksiyonu çağırır; otomatik denetim bunu doğrular.
# Makullük: girilen değer, yaş/cinsiyet normunun P1-P99 aralığı dışındaysa kaydetmeden önce
# uyarılır; kullanıcı onaylarsa kaydedilir (engellemez). Normu olmayan değişkende kontrol yok.
# ════════════════════════════════════════════════════════════
from olcut.kayit import (   # Bölme Aşama 2: olcut/kayit.py
    GRUP_KOLON, OTURUM_KOLONLARI, TOPLU_GIRIS_DISI, deger_metni, test_kaydi_olustur, kayitlari_yaz,
    makul_aralik_bantlardan, makul_aralik, _sayi_kisa, makullukte_uyarilar, PROFIL_MAKULLUK,
    SPORCU_FORM_ALT_SINIR, SPORCU_FORM_ALANLARI, sporcu_form_hatalari, _sporcu_formunu_temizle,
    profil_uyarilari, oturum_sutunu, oturum_kayitlari, oturum_secenekleri,
    oturum_degerleri, oturumlar_arasi_fark, oturum_etiketi, calisma_bos, calismalar_oku, calisma_dogrula,
    calisma_kaydet, calisma_dokun, calisma_sil, calisma_oturum_adi, oturum_kimligi, calisma_sporculari)


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

from olcut.oneri import (   # Bölme Aşama 2: olcut/oneri.py
    YON_TSYT, YON_TSYT_YAS, YON_LISTE_SINIRI, YON_YARIM_ORAN, YON_YARIM_GUN, YON_SUSTUR_ANAHTAR, ilgi_eki,
    yarim_susturulanlar, yarim_sustur, yonlendirme_durumu, yarim_cumlesi, tamam_cumlesi, ONERI_BRANS_YASI,
    ONERI_TARAMA_ONCELIK, SPOR_DALI_BRANS, kayit_edilebilir, brans_rafi, _sporcu_yasi, sayi_iyelik,
    _hafta_metni, oneri_baglami, _yapilan, _son_olcum, calisma_durumu, calisma_son_dokunma, _calisma_onerisi,
    aktif_calismalar, calisma_onerileri, _tarama_adaylari, sporcu_onerileri, oneri_secenekleri, oneriler,
    gorselsiz_metni, sira_birlestir, _virgullu, konum_sekme_sirasi, ozet_kartlari_html)


# ════════════════════════════════════════════════════════════
# PAKET 27 — KENDİ TEST SETİNİ KURABİLME
# Kategori test seçimini kilitlemez: kategori ağacı gezinmek içindir; branş hangi testin ÖNERİLECEĞİNİ belirler,
# hangisinin YAPILABİLECEĞİNİ değil. Çalışma (ayarlar.json): ad, sıralı testler, gruplar, ölçüm zamanları, sporcu →
# grup ataması. Sporcu ve test dosyalarının yapısı değişmez.
# ════════════════════════════════════════════════════════════



# ════════════════════════════════════════════════════════════
# PAKET 33 — ÖNERİ MOTORU: ana sayfa katalog değil, "şimdi şunu yap"
# Sıra (ilk eşleşen kazanır): 0 aktif çalışma · 1 yarım batarya (Paket 32 eşiği) · 2 yaşa uygun tarama bataryası ·
# 3 dalına özgü batarya (11 yaş altında atlanır; dalın katalogda karşılığı yoksa atlanır) · 4 en eski ölçümü tekrar.
# Kural tabanlı; tahmin yok. Olgunluk (PHV) kestirimi yok: kapı yalnız takvim yaşı. Her önerinin gerekçesi var.
# ════════════════════════════════════════════════════════════


from olcut.sayfalar.ana_sayfa import _yonlendirme_gizle_degisti, yonlendirme_ekrani   # Bölme Aşama 2: olcut/sayfalar/ana_sayfa.py


# ════════════════════════════════════════════════════════════
# TEST OTURUMU — ADIM ADIM (Paket 38b)
# Testler → Sporcular → Oturum bilgisi → Değerler. Her adımda tek ana düğme (sabit alt çubukta, sağda).
# Değerler iki kipte: SIRADAKİ (ekranda tek sporcu, tek test; telefon/tablet varsayılanı) ve TABLO (bilgisayar).
# Her değişiklik TASLAĞA yazılır (oturum durumu + diskte oturum_taslagi.json); xlsx'e yalnız "Oturumu kaydet".
# Ölçüm sırasında karşılaştırma (norm, yaşıt, sıralama) GÖSTERİLMEZ; olağandışı değer uyarılır, engellenmez.
# Kayıt satırları eski yolla kurulur (oturum_kayitlari → test_kaydi_olustur): hesap ve kayıt biçimi aynı.
# ════════════════════════════════════════════════════════════
from olcut.sayfalar.test_oturumu import (   # Bölme Aşama 2: olcut/sayfalar/test_oturumu.py
    OT_ADIMLAR, OT_KIPLER, TASLAK_DOSYA, NOT_DEGISKENI, OT_AYKIRI_SORU, OT_TASLAK_NOTU, OT_KORUNMAYAN,
    _MOBIL_AJAN, varsayilan_kip, _istemci_ajani, _qp_al, _qp_ayarla, taslak_bos, taslak_birlestir, taslak_oku,
    taslak_yaz, taslak_sil, taslak_deger_sayisi, sayi_girdisi, taslak_tablosu, taslak_duzenleme_tablosu,
    taslak_tablodan, taslak_kayitlari, ot_kuyrugu, ot_durumu, ot_ilerleme, ot_siradaki, ot_hesaplanan,
    ot_aykiri_uyarilari, ot_adim_seridi_html, ot_ilerleme_html, ot_sira_cipleri_html, _ot_durum_koru,
    _ot_adim_git, _ot_tablo_yenile, _ot_grup_adlari, _ot_taslak_yukle, _ot_taslak_temizle, _ot_degerlere_gec,
    _ot_deger_cb, _ot_not_cb, _ot_tamamla, _ot_sonraki_cb, _ot_onayla_cb, _ot_atla_cb, _ot_geri_al_cb,
    _ot_kaydet_cb, test_norm_var_mi, NORM_ISARETI, _bant_ortancasi, ot_ornek_deger, _ot_sayi_klavyesi,
    _ot_adim_testler, _ot_adim_sporcular, _ot_adim_bilgi, _ot_siradaki_kipi, _ot_tablo_kipi, _ot_ozet_satirlari,
    _ot_alt_cubuk, test_oturumu_sayfasi)


# ════════════════════════════════════════════════════════════
# NİTELİĞE GÖRE TEST BUL (Paket 38b)
# Kullanıcıya 9 sade ad; her ad bir ya da iki iç niteliği kapsar ("Kas dayanıklılığı" = kuvvette devamlılık +
# anaerobik). test_niteligi / test_bileseni ve sıra uyarısı DEĞİŞMEZ — yalnız görünen etiket ve gruplama.
# Niteliği olmayan testler (anket, adım sayısı, çok bileşenli batarya, EMG) "Diğer" kartında; kaybolmaz.
# ════════════════════════════════════════════════════════════


from olcut.sayfalar.nitelik import nitelik_sayfasi   # Bölme Aşama 2: olcut/sayfalar/nitelik.py


# ════════════════════════════════════════════════════════════
# SONUÇLAR — TEK SPORCU: DÖRT SORU KARTI (Paket 38b)
# Nasıl gelişiyor? · Yaşıtlarına göre nerede? · Güçlü ve geliştirilecek yönler · Hangi branşa uygun?
# Hesaplar mevcut işlevlerden (gelisim_ozeti, grup_ici_konum, sporcu_z_profili, brans_grubu_eslestir); yeni eşik
# yok: nitelik düzeyi normatif seviyeden (_veli_duzeyi: 5-6 güçlü, 3-4 orta, 1-2 geliştir), yaşıt kartı veli
# kartının koşullarıyla (yaş ≥ 11, n ≥ 20, yön tanımlı, vücut ölçüsü değil). Her kart kendi try/except'inde.
# 7 sekmeli ayrıntılı görünüm "Ayrıntılı analiz" anahtarıyla açılır (tüm sporcularda varsayılan).
# ════════════════════════════════════════════════════════════
from olcut.sayfalar.sonuclar import (   # Bölme Aşama 2: olcut/sayfalar/sonuclar.py
    BRANS_EN_AZ_NITELIK, SONUC_YASIT_METNI, NITELIK_DURUM_ETIKETI, NITELIK_NOTU, sonuc_kart_gorunumu,
    sonuc_suzgecleri, notlu_olcum_sayisi, sporcu_ozet_kutulari, varsayilan_gelisim_cifti, yon_oku,
    sonuc_karti_cumlesi, yasit_karti_metni, yasit_yetersiz_nedeni, nitelik_durumlari, nitelik_cubuklari_html,
    excel_verisi, kart_hatasi, tum_gelisim_penceresi, sonuclar_sporcu_sayfasi)


# ════════════════════════════════════════════════════════════
# YAN MENÜ
# ════════════════════════════════════════════════════════════
SAYFALAR = ["Ana Sayfa", "Sporcu Girişi", "Niteliğe göre test bul", "Test Uygula", "Test Oturumu",
            "Sonuçları Görüntüle", "Raporlar", "Kaynakça", "Hakkında", "Kulüpler"]
UST_MENU = ["Ana Sayfa", "Raporlar", "Kaynakça", "Hakkında"]          # Paket 38k: üstte, site menüsü gibi
IKINCIL_SAYFALAR = ["Kulüpler"]                                        # Paket 38n: alt bilgiden (Hakkında'nın yanı)
YAN_MENU = [s_ for s_ in SAYFALAR if s_ not in UST_MENU + IKINCIL_SAYFALAR]   # sol menüde iş sayfaları

# Paket 38n: çalışma alanı (Genel ya da kulupler/<kod>/) — her veri okumasından ÖNCE doğrulanır
from olcut.bilesenler import calisma_alani_dogrula
calisma_alani_dogrula()


# Paket 38b: değer girilirken sayfa yenilendiyse (adreste ?taslak=1 ve diskte taslak) kaldığı yere döner
if "sayfa" not in st.session_state and _qp_al("taslak") == "1" and taslak_oku():
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ots::otomatik"] = True
# "Açılışta bu ekranı gösterme" seçiliyse oturumun ilk açılışı doğrudan iş sayfasına (menü aynen kalır)
if "sayfa" not in st.session_state and ayar_oku().get("yonlendirme_gizle"):
    st.session_state["sayfa"] = "Test Uygula" if os.path.exists(veri_yolu(SPORCU_DOSYA)) else "Sporcu Girişi"
from olcut.bilesenler import alt_bilgi, bugun_karti, ust_menu, yan_menu   # 38k: üst menü, alt bilgi; 38l: yan
from olcut.sayfalar.hakkinda import hakkinda_sayfasi                  # Paket 38k: olcut/sayfalar/hakkinda.py
from olcut.sayfalar.kulupler import kulupler_sayfasi                  # Paket 38n: olcut/sayfalar/kulupler.py
# Paket 38k: "sayfa" yönlendirme durumu (artık bir seçicinin anahtarı değil); sol menü yalnız iş sayfaları
if st.session_state.get("sayfa") not in SAYFALAR:
    st.session_state["sayfa"] = "Ana Sayfa"
sayfa = st.session_state["sayfa"]
yan_menu(sayfa, YAN_MENU)                                             # Paket 38l: iş sayfaları alt alta
_taslak = taslak_oku()
bugun_karti(sayfa, taslak_deger_sayisi(_taslak) if _taslak else None)  # Paket 38l: kısa durum + taslağa dön
if sayfa != "Test Oturumu":
    _qp_ayarla("taslak", None)
ust_menu(sayfa, UST_MENU)

from olcut.sayfalar.sporcu_girisi import sporcu_girisi_sayfasi   # Bölme Aşama 2: olcut/sayfalar/sporcu_girisi.py


from olcut.sayfalar.test_uygula import test_uygula_sayfasi   # Bölme Aşama 2: olcut/sayfalar/test_uygula.py


from olcut.sayfalar.sonuclar_genel import sonuclari_goruntule_sayfasi   # Bölme Aşama 2: olcut/sayfalar/sonuclar_genel.py
from olcut.sayfalar.karsilastirma import karsilastirma_sayfasi   # Paket 38g: olcut/sayfalar/karsilastirma.py
from olcut.sayfalar.kayit_duzelt import kayit_duzelt_sayfasi    # Paket 38s: olcut/sayfalar/kayit_duzelt.py
from olcut.bilesenler import SONUC_BOLUMLERI, _karsilastirmaya_git, sonuc_bolumu_secici   # Paket 38g
from olcut.kayit import ONCEKI_KAT, normsuz_uyarilar, onceki_olcumler   # Paket 38g: normsuz olağandışı değer


from olcut.sayfalar.raporlar import raporlar_sayfasi, kaynakca_sayfasi   # Bölme Aşama 2: olcut/sayfalar/raporlar.py


if sayfa == "Niteliğe göre test bul":
    nitelik_sayfasi()

elif sayfa == "Ana Sayfa":
    # ── AÇILIŞ EKRANI (Paket 13) ──
    st.markdown(f'<div class="sp-acilis">{logo_svg(72)}<div><h1>{_html.escape(UYGULAMA_ADI)}</h1>'
                f'<p>{_html.escape(ACILIS_TANIM)}</p></div></div>', unsafe_allow_html=True)
    yonlendirme_ekrani()

elif sayfa == "Sporcu Girişi":
    sporcu_girisi_sayfasi()

# ── SAYFA 2: TEST UYGULA ──
elif sayfa == "Test Uygula":
    test_uygula_sayfasi()

# ── SAYFA: TEST OTURUMU — toplu giriş (Paket 10) ──
elif sayfa == "Test Oturumu":
    test_oturumu_sayfasi()                       # Paket 38b: Testler → Sporcular → Oturum bilgisi → Değerler

# ── SAYFA 3: SONUÇLARI GÖRÜNTÜLE ──
elif sayfa == "Sonuçları Görüntüle":
    _bolum = sonuc_bolumu_secici()
    if _bolum == "Karşılaştırma":                    # Paket 38g: üst düzey bölüm (Sporcular / Oturumlar arası)
        karsilastirma_sayfasi()
    elif _bolum == "Kayıt düzelt":                   # Paket 38s
        kayit_duzelt_sayfasi()
    elif sonuc_kart_gorunumu():
        sonuclar_sporcu_sayfasi()                    # Paket 38b: tek sporcu → dört soru kartı
    else:
        sonuclari_goruntule_sayfasi()


# ── SAYFA: RAPORLAR (Paket 7) ──
elif sayfa == "Raporlar":
    raporlar_sayfasi()

# ── SAYFA 4: KAYNAKÇA ──
elif sayfa == "Kaynakça":
    kaynakca_sayfasi()

# ── HAKKINDA (Paket 38k) ──
elif sayfa == "Hakkında":
    hakkinda_sayfasi()

# ── KULÜPLER (Paket 38n) ──
elif sayfa == "Kulüpler":
    kulupler_sayfasi()

alt_bilgi(sayfa)                                 # Paket 38k: her sayfanın en altında (raporlara girmez)
