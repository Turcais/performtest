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
    profil_uyarilari, oturum_sutunu, oturum_kayitlari, oturum_secenekleri, KARSILASTIRMA_KAPSAMLARI,
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
