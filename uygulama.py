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
from veri.normlar_kategorik import (   # Bölme Aşama 1: veri/normlar_kategorik.py
    NORMATIF, ORNEKLEM_KAYNAK_AYDOS_2004, ORNEKLEM_KUNYE_AYDOS_2004, _AYDOS_2004,
    ORNEKLEM_KAYNAK_MORASSUTTI_2025, ORNEKLEM_KUNYE_MORASSUTTI_2025, NORMATIF_TEST)


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


def _aydos_branslari(sutun):
    """sutun 2 = squat, 4 = bench press. Yalnız 'Erkek' (örneklem erkek)."""
    return {r[0]: {"Erkek": {"ort": r[sutun], "sd": r[sutun + 1], "n": r[1]}} for r in _AYDOS_2004}


NORMATIF = {**NORMATIF,                       # atama: otomatik denetim de görsün (modül düzeyinde .update yok)
    "Rölatif Squat (kg/kg)": {
        "tur": "orneklem", "birim": "kg/kg", "dusuk_iyi": False, "yas_alt": 18, "orneklem_yas": (18, 30),
        "kaynak": ORNEKLEM_KAYNAK_AYDOS_2004, "kunye": ORNEKLEM_KUNYE_AYDOS_2004, "branslar": _aydos_branslari(2),
    },
    "Rölatif Bench Press (kg/kg)": {
        "tur": "orneklem", "birim": "kg/kg", "dusuk_iyi": False, "yas_alt": 18, "orneklem_yas": (18, 30),
        "kaynak": ORNEKLEM_KAYNAK_AYDOS_2004, "kunye": ORNEKLEM_KUNYE_AYDOS_2004, "branslar": _aydos_branslari(4),
    },
}
NORMATIF = {**NORMATIF,                       # atama: otomatik denetim de görsün (modül düzeyinde .update yok)
    "Sıçrama Yüksekliği — En İyi (cm)": {
        "tur": "orneklem", "birim": "cm", "basamak": 1, "dusuk_iyi": False, "yas_alt": 20, "yas_ust": 29,
        "orneklem_yas": (20, 29), "kaynak": ORNEKLEM_KAYNAK_MORASSUTTI_2025, "kunye": ORNEKLEM_KUNYE_MORASSUTTI_2025,
        "genel_orneklem": "Üniversite öğrencisi (karma düzey)",
        "branslar": {"Üniversite öğrencisi (karma düzey)": {"Erkek": {"ort": 53.0, "sd": 14.0, "n": 422},
                                                             "Kadın": {"ort": 37.0, "sd": 11.0, "n": 538}}},
    },
}
# Profildeki spor dalı → örneklem branşı (tam ad eşleşir; alt gruplar burada). "Amerikan Futbolu" Futbol değildir.
ORNEKLEM_SPOR_DALI = {"Güreş (Serbest)": "Güreş", "Güreş (Grekoromen)": "Güreş"}
# Rölatif kuvvet: test → (girilen mutlak yük, hesaplanan rölatif değer). Rölatif değer kullanıcıdan istenmez.
ROLATIF_KUVVET = {
    "1RM Bench Press": ("1RM Bench Press (kg)", "Rölatif Bench Press (kg/kg)"),
    "1RM Squat (Arka Çömelme)": ("1RM Squat (kg)", "Rölatif Squat (kg/kg)"),
    "1RM Leg Press": ("1RM Leg Press (kg)", "Rölatif Leg Press (kg/kg)"),
}
# Doğrulanmış normu olmayan testler: değerlendirme alanında boş tablo değil bu metin görünür. Uydurma norm yok.
NORM_YOK_METNI = "Bu test için doğrulanmış norm bulunmamaktadır."
NORMSUZ_TESTLER = ("1RM Leg Press", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)",
                   "Şınav (Push-Up) — Maksimum Tekrar (Genel)", "Mekik (Sit-Up) — 1 Dakika (Genel)")
# Paket 36: Sargent normsuz listeden çıktı (Morassutti 2025 örneklemi). Testin hesaplanan değişkenleri — kapsam ve
# "değer girilince" metni için (girişten önce de bilinsin).
TURETILEN_DEGISKENLER = {"Sargent Dikey Sıçrama Testi (Duvar)": ["Sıçrama Yüksekliği — En İyi (cm)"]}
SARGENT_DENEMELER = ("Sıçrama Erişimi — Deneme 1 (cm)", "Sıçrama Erişimi — Deneme 2 (cm)",
                     "Sıçrama Erişimi — Deneme 3 (cm)")
ORNEKLEM_DISI_METNI = ("Bu değerin karşılaştırma örneklemi yalnız 18-30 yaş erkek sporculardan oluşur (Aydos ve ark., "
                       "2004); kadın ve 18 yaş altı sporcu için referans gösterilmez.")


# ════════════════════════════════════════════════════════════
# TESTE ÖZGÜ KATEGORİK NORMATİF DEĞERLER
# Format: "Test Adı › Değişken" → cinsiyet → kategori → (min, max)
# Jenerik değişken adlarının (Deneme 1 (cm) vb.) testler arası
# karışmasını engeller. NORMATIF_YAS'tan sonra, NORMATIF'ten önce bakılır.
# ════════════════════════════════════════════════════════════


def normatif_test_degerlendir(test_adi, degisken, deger, cinsiyet):
    """Teste özgü kategorik normatif değerlendirme."""
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_TEST:
        return None
    norm = NORMATIF_TEST[anahtar]
    cins_normu = norm.get(cinsiyet) or norm.get("Erkek")
    if cins_normu is None:
        return None
    try:
        d = float(deger)
    except (ValueError, TypeError):
        return None
    kategori = "Bilinmiyor"
    for kat, (alt, ust) in cins_normu.items():
        if alt <= d < ust:
            kategori = kat
            break
    renk = kategori_rengi(kategori)
    return {
        "kategori": kategori,
        "renk": renk,
        "kaynak": norm.get("kaynak", ""),
        "dusuk_iyi": norm.get("dusuk_iyi", False),
    }


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
from veri.normlar_yas import NORMATIF_YAS   # Bölme Aşama 1: veri/normlar_yas.py


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
NORMATIF_YAS = {**NORMATIF_YAS, **TSYT_NORMLARI}   # atama: otomatik denetim de görsün



def yas_persentil_bul(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum=None, test_tarihi=None):
    """
    Yaş ve cinsiyete göre persentil kategorisini bulur.
    Dönen: {kategori, renk, persentil_aralik, kaynak, n, bantlar, ceyrek_notu, ...} veya None

    Çeyrek boyutu (Paket 9, TSYT): norm "ceyrekler" içeriyorsa ve doğum + test tarihi biliniyorsa
    hücre = (doğum yılına göre yaş, takvim doğum çeyreği). Bilinmiyorsa dört çeyreğin ortalaması
    ("yaslar") kullanılır ve ceyrek_notu bunu söyler.
    """
    anahtar = f"{test_adi} › {degisken}"
    if anahtar not in NORMATIF_YAS:
        return None

    norm = NORMATIF_YAS[anahtar]
    yaslar = norm["yaslar"]

    try:
        yas = int(float(sporcu_yas))
        d = float(deger)
    except (ValueError, TypeError):
        hucre_y = tsyt_hucre(dogum, test_tarihi) if "ceyrekler" in norm else None
        if hucre_y is None:
            return None
        yas, d = hucre_y[0], None
        try:
            d = float(deger)
        except (ValueError, TypeError):
            return None

    ceyrek, ceyrek_notu = None, None
    if "ceyrekler" in norm:
        hucre = tsyt_hucre(dogum, test_tarihi)
        if hucre:
            yas, ceyrek = hucre   # TSYT tabloları doğum yılına göre yaşla kurulmuş
        else:
            ceyrek_notu = ("Doğum tarihi bilinmediği için dört doğum çeyreğinin ortalaması kullanıldı "
                           "(çocuk sayısıyla ağırlıklı; yaklaşık değer; profil yaşıyla).")

    # En yakın yaş grubunu bul
    mevcut_yaslar = sorted(yaslar.keys())
    if yas < mevcut_yaslar[0]:
        secili_yas = mevcut_yaslar[0]
        yas_notu = f"⚠️ {yas} yaş için norm yok — {secili_yas} yaş normu kullanıldı"
    elif yas > mevcut_yaslar[-1]:
        secili_yas = mevcut_yaslar[-1]
        yas_notu = f"⚠️ {yas} yaş için norm yok — {secili_yas} yaş normu kullanıldı"
    else:
        secili_yas = min(mevcut_yaslar, key=lambda y: abs(y - yas))
        yas_notu = None

    cins_veri = yaslar[secili_yas].get(cinsiyet)
    if cins_veri is None:
        cins_veri = yaslar[secili_yas].get("Erkek")
    if ceyrek is not None:
        cey_tablo = norm["ceyrekler"].get(secili_yas, {}).get(cinsiyet, {})
        if ceyrek in cey_tablo:
            cins_veri = cey_tablo[ceyrek]
            ceyrek_notu = f"TSYT hücresi: {secili_yas} yaş (doğum yılına göre), {ceyrek}. doğum çeyreği"
        else:
            ceyrek_notu = "Bu yaş/cinsiyet için çeyrek tablosu yok — dört çeyreğin ortalaması kullanıldı."
    if cins_veri is None:
        return None
    tum_bantlar = {k: v for k, v in cins_veri.items() if k.startswith("P") and k[1:].isdigit()}
    tablo_no = norm.get("tablolar", {}).get(secili_yas)

    dusuk_iyi = norm.get("dusuk_iyi", False)

    # ── Persentil seti: P5/P25/P50/P75/P95 (varsayilan) veya P20/P40/P60/P80 ──
    if "P20" in cins_veri and "P5" not in cins_veri:
        # Alman DMT / NRW tipi 5 sinifli sistem (sinirlar P20, P40, P60, P80)
        p20, p40, p60, p80 = (cins_veri["P20"], cins_veri["P40"],
                              cins_veri["P60"], cins_veri["P80"])
        bantlar = {"P20": p20, "P40": p40, "P60": p60, "P80": p80}
        if dusuk_iyi:
            if d <= p20:    kategori, aralik = "Üstün", "≥ P80"
            elif d <= p40:  kategori, aralik = "İyi", "P60-P80"
            elif d <= p60:  kategori, aralik = "Ortalama", "P40-P60"
            elif d <= p80:  kategori, aralik = "Ortalama Altı", "P20-P40"
            else:           kategori, aralik = "Düşük", "< P20"
        else:
            if d >= p80:    kategori, aralik = "Üstün", "≥ P80"
            elif d >= p60:  kategori, aralik = "İyi", "P60-P80"
            elif d >= p40:  kategori, aralik = "Ortalama", "P40-P60"
            elif d >= p20:  kategori, aralik = "Ortalama Altı", "P20-P40"
            else:           kategori, aralik = "Düşük", "< P20"
        return {
            "kategori": kategori, "renk": kategori_rengi(kategori), "persentil_aralik": aralik,
            "kaynak": norm.get("kaynak", ""), "n": norm.get("n", ""),
            "birim": norm.get("birim", ""), "yas_notu": yas_notu,
            "kullanilan_yas": secili_yas, "bantlar": bantlar, "dusuk_iyi": dusuk_iyi,
            "ceyrek": ceyrek, "ceyrek_notu": ceyrek_notu, "tablo": tablo_no,
        }

    p5, p25, p50, p75, p95 = (cins_veri["P5"], cins_veri["P25"],
                               cins_veri["P50"], cins_veri["P75"], cins_veri["P95"])

    # Kategori belirle
    if dusuk_iyi:
        if d <= p5:      kategori, aralik = "Üstün", "≥ P95"
        elif d <= p25:   kategori, aralik = "İyi", "P75-P95"
        elif d <= p50:   kategori, aralik = "Ortalama Üstü", "P50-P75"
        elif d <= p75:   kategori, aralik = "Ortalama Altı", "P25-P50"
        elif d <= p95:   kategori, aralik = "Düşük", "P5-P25"
        else:            kategori, aralik = "Çok Düşük", "< P5"
    else:
        if d >= p95:     kategori, aralik = "Üstün", "≥ P95"
        elif d >= p75:   kategori, aralik = "İyi", "P75-P95"
        elif d >= p50:   kategori, aralik = "Ortalama Üstü", "P50-P75"
        elif d >= p25:   kategori, aralik = "Ortalama Altı", "P25-P50"
        elif d >= p5:    kategori, aralik = "Düşük", "P5-P25"
        else:            kategori, aralik = "Çok Düşük", "< P5"

    # Antropometrik (nötr) ölçüler: iyi/kötü değil, akranlara göre konum
    notr = norm.get("notr", False)
    if notr:
        notr_etiket = {
            "≥ P95":   "Çok Yüksek",
            "P75-P95": "Yüksek",
            "P50-P75": "Ortalama (üst yarı)",
            "P25-P50": "Ortalama (alt yarı)",
            "P5-P25":  "Düşük",
            "< P5":    "Çok Düşük",
        }
        kategori = notr_etiket[aralik]

    return {
        "kategori": kategori,
        "renk": kategori_rengi(kategori, notr),
        "persentil_aralik": aralik,
        "kaynak": norm.get("kaynak", ""),
        "n": norm.get("n", ""),
        "birim": norm.get("birim", ""),
        "yas_notu": yas_notu,
        "kullanilan_yas": secili_yas,
        # 19 persentilli tablolarda (TSYT) Z tüm bantlarla hesaplanır; gösterimde 5 ana bant kullanılır
        "bantlar": tum_bantlar if len(tum_bantlar) > 5 else {"P5": p5, "P25": p25, "P50": p50, "P75": p75, "P95": p95},
        "dusuk_iyi": dusuk_iyi,
        "notr": notr,
        "ceyrek": ceyrek, "ceyrek_notu": ceyrek_notu, "tablo": tablo_no,
    }


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

_STANDART_NORMAL = NormalDist()


def persentil_sirasi(bantlar, deger):
    """
    Persentil bantlarından (ör. {"P5":..,"P25":..,...}) değerin persentil
    sırasını bulur. Dönen: (persentil, durum) — durum: None, "alt_sinir",
    "ust_sinir" veya "esit_bant" (değer birden fazla bantla aynı).
    Bantlar ham değer yönünde artan değilse None döner.
    """
    try:
        noktalar = sorted((int(k[1:]), float(v)) for k, v in bantlar.items()
                          if k.startswith("P") and k[1:].isdigit())
        d = float(deger)
    except (TypeError, ValueError):
        return None
    if len(noktalar) < 2:
        return None
    ps = [p for p, _ in noktalar]
    vs = [v for _, v in noktalar]
    if any(vs[i] > vs[i + 1] for i in range(len(vs) - 1)):
        return None  # bant sırası bozuk — veri hatası, uydurma Z üretme

    esit = [p for p, v in noktalar if v == d]
    if len(esit) > 1:
        # Aynı değere birden fazla bant düşüyor (taban/tavan etkisi):
        # bu bantların en altı ile en üstünün ortası kullanılır.
        return (min(esit) + max(esit)) / 2, "esit_bant"
    if d < vs[0]:
        return float(ps[0]), "alt_sinir"
    if d > vs[-1]:
        return float(ps[-1]), "ust_sinir"
    if len(esit) == 1:
        return float(esit[0]), None
    for i in range(len(vs) - 1):
        if vs[i] < d < vs[i + 1]:
            oran = (d - vs[i]) / (vs[i + 1] - vs[i])
            return ps[i] + oran * (ps[i + 1] - ps[i]), None
    return None


def yas_z_skoru(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum=None, test_tarihi=None):
    """
    Yaş/cinsiyet normundan persentil sırası ve Z skoru.
    Dönen sözlük: persentil, z (ham değer yönünde), z_performans
    (+ = iyi; nötr ölçülerde None), durum, notr, yas_notu, kullanilan_yas,
    kaynak, n. Norm yoksa None.
    """
    ys = yas_persentil_bul(test_adi, degisken, sporcu_yas, cinsiyet, deger, dogum, test_tarihi)
    if not ys:
        return None
    sonuc = persentil_sirasi(ys["bantlar"], deger)
    if sonuc is None:
        return None
    persentil, durum = sonuc
    z = _STANDART_NORMAL.inv_cdf(persentil / 100.0)
    notr = bool(ys.get("notr"))
    if notr:
        z_perf = None
    else:
        z_perf = -z if ys.get("dusuk_iyi") else z
    # Performans persentili: her testte büyük = iyi. Düşük-iyi testlerde sıra ters çevrilir
    # (100 − P). Nötr (antropometrik) ölçülerde iyi/kötü olmadığı için ham sıra kalır.
    persentil_perf = persentil if notr or not ys.get("dusuk_iyi") else 100.0 - persentil
    return {
        "persentil": round(persentil, 1),
        "persentil_performans": round(persentil_perf, 1),
        "z": round(z, 2),
        "z_performans": None if z_perf is None else round(z_perf, 2),
        "durum": durum,
        "notr": notr,
        "dusuk_iyi": ys.get("dusuk_iyi", False),
        "yas_notu": ys.get("yas_notu"),
        "kullanilan_yas": ys.get("kullanilan_yas"),
        "kaynak": ys.get("kaynak", ""),
        "n": ys.get("n", ""),
        "birim": ys.get("birim", ""),
        "bantlar": ys["bantlar"],
        "bant_araligi": (min(int(k[1:]) for k in ys["bantlar"]),
                         max(int(k[1:]) for k in ys["bantlar"])),
        "ceyrek": ys.get("ceyrek"), "ceyrek_notu": ys.get("ceyrek_notu"), "tablo": ys.get("tablo"),
        "kategori": ys.get("kategori"), "persentil_aralik": ys.get("persentil_aralik"),
    }


def bant_metni(bantlar, ters):
    """
    Norm bantlarını yazıya döker. ters=True (düşük-iyi test): etiketler performans yönüne
    çevrilir (ham P5 → P95), böylece her testte P95 "en iyi %5'in sınırı" demektir.
    """
    sirali = sorted(((int(k[1:]), v) for k, v in bantlar.items()), key=lambda x: x[0])
    if len(sirali) > 5:   # TSYT: 19 persentil — ekranda 5 ana bant
        sirali = [(p, v) for p, v in sirali if p in (5, 25, 50, 75, 95)]
    parcalar = []
    for p, v in sirali:
        p_g = 100 - p if ters else p
        etiket = f"**P50 (medyan): {v}**" if p_g == 50 else f"P{p_g}: {v}"
        parcalar.append(etiket)
    return " | ".join(parcalar)


def z_durum_notu(zs):
    """Z sonucunun yanında gösterilecek kısa uyarı (performans yönünde yazılır)."""
    alt, ust = zs["bant_araligi"]
    if zs["durum"] in ("alt_sinir", "ust_sinir"):
        if zs.get("notr"):
            uc = f"P{alt} altında" if zs["durum"] == "alt_sinir" else f"P{ust} üstünde"
            return f"{uc} — tablonun dışında; konum sınırda tutuldu"
        iyi_uc = (zs["z_performans"] or 0) > 0
        yuzde = 100 - ust if iyi_uc else alt
        return (f"Akranlarının en {'iyi' if iyi_uc else 'zayıf'} %{yuzde:g}'inin de "
                f"{'üstünde' if iyi_uc else 'altında'} — Z sınırda tutuldu "
                f"(gerçek konum daha {'iyi' if iyi_uc else 'zayıf'} olabilir)")
    if zs["durum"] == "esit_bant":
        return "Değer birden fazla persentil bandına eşit (taban/tavan etkisi) — bu bantların ortası kullanıldı"
    return None


def sifir_gecerli(test_adi, degisken):
    """0 değeri bu normda gerçek bir skor mu? (ör. göz-el koordinasyonunda 0 yakalama)"""
    norm = NORMATIF_YAS.get(f"{test_adi} › {degisken}")
    if not norm:
        return False
    for cinsler in norm["yaslar"].values():
        for bant in cinsler.values():
            if isinstance(bant, dict) and any(
                    isinstance(v, (int, float)) and v <= 0 for v in bant.values()):
                return True
    return False


def ktk3_toplamlari(test_adi, degerler):
    """
    KTK3+ testlerinin norma bağlanan toplam skorları. Hem test ekranında hem
    de eski kayıtlardan Z profili çıkarılırken kullanılır. 0 geçerli bir
    skordur: toplam, alanlardan en az biri doldurulmuşsa hesaplanır.
    """
    def al(k):
        return guvenli_float(degerler.get(k, 0)) if _girildi(degerler.get(k)) else 0.0

    def herhangi(*ks):
        return any(_girildi(degerler.get(k)) for k in ks)

    sonuc = {}
    if test_adi == "Dengede Geriye Yürüme (Balancing Backwards)":
        ks = ["6 cm Kiriş - Toplam Adım", "4.5 cm Kiriş - Toplam Adım", "3 cm Kiriş - Toplam Adım"]
        if herhangi(*ks):
            sonuc["Toplam Adım (maks 72)"] = min(int(sum(al(k) for k in ks)), 72)
    elif test_adi == "Yana Sıçrama (Jumping Sideways)":
        ks = ["Deneme 1 (sıçrama sayısı)", "Deneme 2 (sıçrama sayısı)"]
        if herhangi(*ks):
            sonuc["Toplam Sıçrama (2 deneme)"] = int(sum(al(k) for k in ks))
    elif test_adi == "Yana Platform Değiştirme (Moving Sideways)":
        ks = ["Deneme 1 (puan)", "Deneme 2 (puan)"]
        if herhangi(*ks):
            sonuc["Toplam Puan (2 deneme)"] = int(sum(al(k) for k in ks))
    elif test_adi == "Göz-El Koordinasyonu (Duvara Atıp Yakalama)":
        ks = ["Deneme 1 (yakalama)", "Deneme 2 (yakalama)"]
        if herhangi(*ks):
            sonuc["Toplam Yakalama (2 deneme)"] = int(sum(al(k) for k in ks))
    return sonuc


from veri.brans_profilleri import BILESIK_Z, BRANS_GRUBU_PROFILLERI   # Bölme Aşama 1: veri/brans_profilleri.py
BILESIK_MAKS_GUN = 90  # bileşenler arasında izin verilen en uzun tarih farkı


def bilesik_z_hesapla(ad, z_sozlugu):
    """
    z_sozlugu: {(test, değişken): {"z_performans": .., "tarih": Timestamp/None}}
    Dönen: {"deger", "eksik", "tarih_farki_gun"} — eksik bileşen varsa deger None.
    """
    tanim = BILESIK_Z[ad]
    eksik = [t for t, d in tanim["bilesenler"] if (t, d) not in z_sozlugu
             or z_sozlugu[(t, d)].get("z_performans") is None]
    if eksik:
        return {"deger": None, "eksik": eksik, "tarih_farki_gun": None, "dislanan": [], "notlar": []}

    kullanilan = list(tanim["bilesenler"])
    dislanan, notlar = [], []
    kural = tanim.get("taban_kurali")
    if kural:
        b = kural["bilesen"]
        p50 = (z_sozlugu[b].get("bantlar") or {}).get("P50")
        if p50 is not None and p50 <= kural["p50_esik"]:
            kullanilan.remove(b)
            dislanan.append(b[0])
            hucre = z_sozlugu[b].get("hucre", "")
            notlar.append(kural["not"] + (f" ({hucre} normunda medyan {p50} yakalama)." if hucre else "."))

    zler = [z_sozlugu[b]["z_performans"] for b in kullanilan]
    tarihler = [z_sozlugu[b].get("tarih") for b in tanim["bilesenler"]]
    tarihler = [t for t in tarihler if t is not None and not pd.isna(t)]
    fark = (max(tarihler) - min(tarihler)).days if len(tarihler) >= 2 else None
    return {"deger": round(sum(zler) / len(zler), 2), "eksik": [], "tarih_farki_gun": fark,
            "dislanan": dislanan, "notlar": notlar, "bilesen_sayisi": len(zler)}


def sporcu_z_profili(df_test, sporcu):
    """
    Sporcunun yaş bazlı normu olan her (test, değişken) için EN SON ölçümünün Z skoru.
    Dönen: {"hata": str|None, "satirlar": [..], "z_sozlugu": {..}, "eski_yas": bool}
    Z-Skor Profili sekmesi, radar ve ileride branş eşleştirmesi bu tek kaynağı kullanır.
    """
    bilgi = {}
    if os.path.exists(SPORCU_DOSYA):
        df_sp = pd.read_excel(SPORCU_DOSYA)
        esl = df_sp[df_sp["Ad"].astype(str) + " " + df_sp["Soyad"].astype(str) == sporcu]
        if not esl.empty:
            bilgi = esl.iloc[0].to_dict()
    cinsiyet = str(bilgi.get("Cinsiyet", "")).strip()
    profil_yas = bilgi.get("Yaş")
    sonuc = {"hata": None, "satirlar": [], "z_sozlugu": {}, "eski_yas": False}
    if cinsiyet not in ("Erkek", "Kadın"):
        sonuc["hata"] = "Sporcu profilinde cinsiyet bulunamadı; Z skoru hesaplanamaz."
        return sonuc

    df_s = df_test[df_test["Sporcu"] == sporcu]
    if "Tarih_dt" in df_s.columns:
        df_s = df_s.sort_values("Tarih_dt", na_position="first")

    son_olcum = {}
    for _, satir in df_s.iterrows():
        test_z = satir.get("Test", "")
        vals = satir.to_dict()
        for k_t, v_t in ktk3_toplamlari(test_z, vals).items():
            if not _girildi(vals.get(k_t)):
                vals[k_t] = v_t   # eski kayıtlarda toplam kaydedilmemişti
        yas_z = vals.get("Test Yaşı")
        if not _girildi(yas_z):
            yas_z = profil_yas
            sonuc["eski_yas"] = True
        on_ek = f"{test_z} › "
        for anahtar in NORMATIF_YAS:
            if not anahtar.startswith(on_ek):
                continue
            degisken_z = anahtar[len(on_ek):]
            v = vals.get(degisken_z)
            if not _girildi(v):
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if v == 0 and not sifir_gecerli(test_z, degisken_z):
                continue
            son_olcum[(test_z, degisken_z)] = (v, satir.get("Tarih_dt"), satir.get("Tarih", ""), yas_z)

    for (test_z, degisken_z), (v, tarih_dt, tarih_str, yas_z) in son_olcum.items():
        zs = yas_z_skoru(test_z, degisken_z, yas_z, cinsiyet, v, bilgi.get(DOGUM_KOLON), tarih_dt)
        if not zs:
            continue
        try:
            yas_say = int(float(yas_z))
        except (TypeError, ValueError):
            yas_say = None
        norm_yaslar = NORMATIF_YAS[f"{test_z} › {degisken_z}"]["yaslar"]
        sonuc["z_sozlugu"][(test_z, degisken_z)] = {
            "z_performans": zs["z_performans"], "tarih": tarih_dt,
            "bantlar": zs["bantlar"], "hucre": f"{zs['kullanilan_yas']} yaş {cinsiyet.lower()}",
            # Rapor için (Paket 7): sınır durumları ve norm dayanağı
            "durum": zs["durum"], "durum_notu": z_durum_notu(zs), "yas_notu": zs.get("yas_notu"),
            "persentil": zs["persentil"], "ceyrek_notu": zs.get("ceyrek_notu"), "tablo": zs.get("tablo"),
            "yas": yas_say, "kullanilan_yas": zs["kullanilan_yas"], "kaynak": zs.get("kaynak", ""),
            "cins_norm_var": norm_yaslar.get(zs["kullanilan_yas"], {}).get(cinsiyet) is not None,
        }
        notlar_z = [n for n in (z_durum_notu(zs), zs.get("yas_notu"), zs.get("ceyrek_notu")) if n]
        sonuc["satirlar"].append({
            "Test": test_z,
            "Değişken": degisken_z,
            "Değer": v,
            "Tarih": tarih_str,
            "Norm yaşı": zs["kullanilan_yas"],
            "Performans persentili": zs["persentil_performans"],
            "Kategori": zs.get("kategori", ""),
            "Z": zs["z"] if zs["notr"] else zs["z_performans"],
            "Tür": "Tanımlayıcı (antropometrik)" if zs["notr"] else "Performans",
            "Not": " · ".join(notlar_z),
        })
    return sonuc


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


def tsyt_hucre(dogum, test_tarihi):
    """
    TSYT norm hücresi: (doğum yılına göre yaş, takvim doğum çeyreği). Kitabın tabloları bu tanımla
    tutarlıdır: çeyrekler boyunca ortalamalar kesintisiz bir yaş merdiveni oluşturur
    (ör. 7 yaş 1. çeyrek boy 128.2 < 8 yaş 4. çeyrek 129.5 cm). Doğum ya da test tarihi yoksa None.
    """
    d, t = tarih_coz(dogum), tarih_coz(test_tarihi)
    if d is None or t is None:
        return None
    return t.year - d.year, dogum_ceyregi(d)



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
# Normu olmayan ama yönü tanımdan belli olan hesaplanan değişkenler (norm sözlüklerinde yönü olanlar oradan okunur)
DEGISKEN_YONU = {"En İyi Süre (sn)": True, "En İyi Değer (cm)": False, "Rölatif Bench Press (kg/kg)": False,
                 "Rölatif Squat (kg/kg)": False, "Rölatif Leg Press (kg/kg)": False}


def _konum_sayi(x):
    """Ekran ve rapor sayısı: en çok 2 ondalık, Türkçe virgül (4.1 → "4,1", -0.2 → "-0,2")."""
    return f"{round(float(x), 2):g}".replace(".", ",")


def degisken_yonu(test, degisken):
    """True: düşük değer iyi · False: yüksek değer iyi · None: yön tanımsız (nötr ölçü ya da bilinmiyor)."""
    test = kanonik_test(test)
    anahtar = f"{test} › {degisken}"
    for sozluk in (NORMATIF_YAS, NORMATIF_TEST, NORMATIF_ESIK_YAS):
        n = sozluk.get(anahtar)
        if n is not None:
            return None if n.get("notr") else bool(n.get("dusuk_iyi", False))
    n = NORMATIF.get(degisken)
    if n is not None and (degisken not in NORMATIF_KAPSAM or NORMATIF_KAPSAM[degisken](test)):
        return bool(n.get("dusuk_iyi", False))
    if degisken in DEGISKEN_YONU:
        return DEGISKEN_YONU[degisken]
    return True if SAYIM_DUSUK_IYI.search(str(degisken)) else None       # Paket 38c: düşme/hata sayısı


# Paket 38a: parantez içi YALNIZ bilinen birimse birim sayılır; "(1 dk)", "(30 sn)" gibi süre belirten parantezler
# başlığa aittir (birim boş). Sayım değişkenlerinde kısa sözcük: "Düşme Sayısı" → "düşme", "Tekrar" → "tekrar".
BILINEN_BIRIMLER = frozenset({"cm", "kg", "sn", "dk", "kg/kg", "%", "W", "m", "m/sn", "bpm", "tekrar", "adet",
                              "m/s", "ms", "W/kg", "N/kg", "ml/kg/min", "km/sa", "N", "Nm"})
SAYIM_BIRIMLERI = (("düşme", "düşme"), ("tekrar", "tekrar"), ("atış", "atış"))


# Paket 38c: düşme ya da hata SAYISI: az olan iyidir (normu olmayan sürümlerde de, ör. Latorre tek ayak denge)
SAYIM_DUSUK_IYI = re.compile(r"düşme|hata", re.I)


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
def _yaprak_testler(d):
    for ad, v in d.items():
        if isinstance(v, dict) and "protokol" in v:
            yield ad
        elif isinstance(v, dict):
            yield from _yaprak_testler(v)


_COCUK_BATARYA_TESTLERI = frozenset(_yaprak_testler(TEST_KATALOGU["Çocuk ve Genç Fiziksel Uygunluk Bataryaları"]))
NORMATIF_KAPSAM = {
    # Yo-Yo IR1 bantları (Bangsbo 2008). IR2, Cooper 12 dk ve
    # 6 dk kürek ergometresi de bu değişken adını kullanır — onlara uygulanmaz.
    "Tamamlanan Mesafe (m)": lambda test: test.startswith("Yo-Yo IR1"),
    # VO2max bantları yetişkin (Haugen 2022, Saltin 1967): çocuk ve genç bataryalarının testlerine uygulanmaz.
    # FitnessGram'ın aerobik HFZ'si yaşa ve cinsiyete göre VO2max eşiğidir; tablo girilmedi (Paket 20).
    "VO2max Tahmini (ml/kg/min)": lambda test: test not in _COCUK_BATARYA_TESTLERI,
    # Paket 35: Aydos 2004 örneklemi (Kademe 2) yalnız bu iki testin rölatif değerine; Leg Press ve öbürleri normsuz
    "Rölatif Squat (kg/kg)": lambda test: test == "1RM Squat (Arka Çömelme)",
    "Rölatif Bench Press (kg/kg)": lambda test: test == "1RM Bench Press",
    # Paket 36: Morassutti 2025 örneklemi yalnız Sargent (duvar) sıçrama yüksekliğine
    "Sıçrama Yüksekliği — En İyi (cm)": lambda test: test == "Sargent Dikey Sıçrama Testi (Duvar)",
}


def orneklem_uygun(degisken, cinsiyet, yas, test_adi=None):
    """
    Kademe 2 örneklem karşılaştırması bu sporcuya gösterilebilir mi (Paket 35): değişken kapsamdaki testte, cinsiyet
    örneklemde TANIMLI (Erkek'e düşme yok) ve yaş ≥ yas_alt. Yaş bilinmiyorsa gösterilmez.
    """
    norm = NORMATIF.get(degisken)
    if not norm or norm.get("tur") != "orneklem":
        return False
    kapsam = NORMATIF_KAPSAM.get(degisken)
    if kapsam is not None and (test_adi is None or not kapsam(test_adi)):
        return False
    cinsler = {c for b in norm["branslar"].values() for c in b if c in ("Erkek", "Kadın")}
    if str(cinsiyet).strip() not in cinsler:
        return False
    try:
        y = float(yas)
    except (TypeError, ValueError):
        return False
    if norm.get("yas_ust") is not None and y > norm["yas_ust"]:         # Paket 36 (Aydos'ta yok → aynı)
        return False
    return y == y and y >= norm.get("yas_alt", 0)


def orneklem_bransi(norm, spor_dali):
    """Sporcunun spor dalına karşılık gelen örneklem branşı (tam ad ya da ORNEKLEM_SPOR_DALI); yoksa None."""
    s = str(spor_dali or "").strip()
    b = ORNEKLEM_SPOR_DALI.get(s, s)
    return b if b in norm.get("branslar", {}) else None


def orneklem_karsilastir(degisken, deger, cinsiyet, spor_dali="Genel/Yok", yas=None, test_adi=None):
    """
    Kademe 2: değeri örneklem ortalaması ± SD ile yan yana koyar — kategori, bant, yüzdelik YOK. Branş örneklemde
    varsa fark (değer − ort) ve SD cinsinden fark; yoksa yalnız tüm branş satırları. Uygun değilse None.
    """
    if not orneklem_uygun(degisken, cinsiyet, yas, test_adi):
        return None
    try:
        d = float(deger)
    except (TypeError, ValueError):
        return None
    norm, c = NORMATIF[degisken], str(cinsiyet).strip()
    sonuc = {"tur": "orneklem", "kategori": None, "kaynak": norm["kaynak"], "dusuk_iyi": norm.get("dusuk_iyi", False),
             "birim": norm.get("birim", ""), "kunye": norm.get("kunye", {}), "orneklem_yas": norm.get("orneklem_yas"),
             "deger": d, "brans": orneklem_bransi(norm, spor_dali) or norm.get("genel_orneklem"),
             "basamak": norm.get("basamak", 3),
             "satirlar": [(b, v[c]["n"], v[c]["ort"], v[c]["sd"]) for b, v in norm["branslar"].items() if c in v]}
    if sonuc["brans"] and c in norm["branslar"][sonuc["brans"]]:
        o = norm["branslar"][sonuc["brans"]][c]
        sonuc.update(ort=o["ort"], sd=o["sd"], n=o["n"], fark=round(d - o["ort"], 3),
                     sd_fark=round((d - o["ort"]) / o["sd"], 2))
    return sonuc


def _orneklem_sayi(x, basamak=3):
    return f"{x:.{basamak}f}".replace(".", ",")


def orneklem_notlari(sonuc, yas=None):
    """Kart notları (örneklem dili; kategori sözcüğü yok)."""
    n = []
    if sonuc.get("ort") is not None:
        isaret = "üstünde" if sonuc["fark"] >= 0 else "altında"
        b_ = sonuc.get("basamak", 3)
        n.append(f"{sonuc['brans']} örneklemi (n={sonuc['n']}): {_orneklem_sayi(sonuc['ort'], b_)} ± "
                 f"{_orneklem_sayi(sonuc['sd'], b_)} {sonuc['birim']}")
        n.append(f"Örneklem ortalamasının {_orneklem_sayi(abs(sonuc['fark']), b_)} {sonuc['birim']} "
                 f"({_orneklem_sayi(abs(sonuc['sd_fark']), 1)} SD) {isaret}" if abs(sonuc["fark"]) > 1e-9
                 else "Örneklem ortalamasına eşit")
    else:
        n.append("Sporcunun branşı örneklemde yok; yedi branşın örneklem değerleri tabloda.")
    oy = sonuc.get("orneklem_yas")
    try:
        if oy and yas is not None and float(yas) > oy[1]:
            n.append(f"Örneklem {oy[0]}-{oy[1]} yaş; sporcu {int(float(yas))} yaşında.")
    except (TypeError, ValueError):
        pass
    n.append((sonuc.get("kunye") or {}).get("kart_notu", "Yüzdelik norm değil."))
    return n


def orneklem_disi_metni(degisken):
    """Kapsam dışı (yaş/cinsiyet) açıklaması: örneklemin künyesinden; yoksa Aydos metni (Paket 35)."""
    return (NORMATIF.get(degisken, {}).get("kunye") or {}).get("disi_metni", ORNEKLEM_DISI_METNI)


def orneklem_tablosu(sonuc):
    """Örneklem satırları (markdown); sporcunun branşı kalın."""
    birim = sonuc.get("birim", "")
    satir = [f"| Branş | n | Ortalama ± SD ({birim}) |", "|---|---|---|"]
    for b, n, ort, sd in sonuc["satirlar"]:
        ad = f"**{b}**" if b == sonuc.get("brans") else b
        satir.append(f"| {ad} | {n} | {_orneklem_sayi(ort, sonuc.get('basamak', 3))} ± "
                     f"{_orneklem_sayi(sd, sonuc.get('basamak', 3))} |")
    return "\n".join(satir) + f"\n\nKaynak: {sonuc['kaynak']}"


def normatif_degerlendir(degisken, deger, cinsiyet, spor_dali="Genel/Yok", test_adi=None, yas=None):
    """Girilen değeri normatif tabloya göre değerlendirir. Kademe 2 örneklem kaydı orneklem_karsilastir'a gider."""
    if degisken not in NORMATIF:
        return None
    kapsam = NORMATIF_KAPSAM.get(degisken)
    if kapsam is not None and (test_adi is None or not kapsam(test_adi)):
        return None
    norm = NORMATIF[degisken]
    if norm.get("tur") == "orneklem":                 # Paket 35: Erkek'e düşme yok, yaş sınırı var, kategori yok
        return orneklem_karsilastir(degisken, deger, cinsiyet, spor_dali, yas, test_adi)
    dusuk_iyi = norm.get("dusuk_iyi", False)
    kaynak = norm.get("kaynak", "")

    # Branşa özgü norm ara
    cinsiyet_normu = None
    branslar = norm.get("branslar", {})
    for brans_adi, brans_veri in branslar.items():
        if brans_adi in spor_dali or spor_dali in brans_adi:
            if cinsiyet in brans_veri:
                cinsiyet_normu = brans_veri[cinsiyet]
                kaynak = brans_veri.get("kaynak", kaynak)
            break

    # Genel norm
    if cinsiyet_normu is None:
        cinsiyet_normu = norm.get(cinsiyet) or norm.get("Erkek")
    if cinsiyet_normu is None:
        return None

    try:
        d = float(deger)
    except (ValueError, TypeError):
        return None

    kategori = "Bilinmiyor"
    for kat, (alt, ust) in cinsiyet_normu.items():
        if alt <= d < ust:
            kategori = kat
            break

    renk = kategori_rengi(kategori)
    return {"kategori": kategori, "renk": renk, "kaynak": kaynak, "dusuk_iyi": dusuk_iyi}


SPORCU_DOSYA = "sporcular.xlsx"
# Sonuç dosyasındaki ölçüm olmayan sütunlar (grafiklerde değişken sayılmaz)
OTURUM_ADI_KOLON = "Oturum Adı"         # Paket 38d: kullanıcının oturuma verdiği ad (isteğe bağlı)
META_KOLONLAR = ["Sporcu", "Kategori", "Batarya", "Branş", "Test", "Tarih", "Notlar",
                 "Tarih_dt", "Test Yaşı", "Oturum", "Yer", "Uygulayıcı", OTURUM_ADI_KOLON]
TEST_DOSYA = "test_sonuclari.xlsx"

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


def turetilmis_degerler(test_adi, degerler, sporcu_satir, sporcu_kilo):
    """
    Girilen değerlerden otomatik hesaplanan değerler (en iyi deneme, KTK3+ toplamları, VO2max,
    asimetri…). Tekli giriş ve toplu giriş (Test Oturumu) AYNI fonksiyonu kullanır; Streamlit
    çağrısı yoktur. Dönen: (hesaplanan: dict, uyarilar: [str]).
    """
    uyarilar = []
    hesaplanan = {}

    sure_anahtarlari = [k for k in degerler if k.startswith("Deneme") and "(sn)" in k]
    if sure_anahtarlari:
        sureler = [guvenli_float(degerler[k]) for k in sure_anahtarlari if degerler[k]]
        sureler = [s for s in sureler if s > 0]
        if sureler:
            en_iyi = min(sureler)
            hesaplanan["En İyi Süre (sn)"] = en_iyi
            if test_adi == "30m Sprint":
                hesaplanan["Hız (m/s)"] = round(30 / en_iyi, 2)

    mesafe_anahtarlari = [k for k in degerler if "(cm)" in k]
    # Tek ölçüm / farklı anlamlı cm değişkenleri olan testlerde "en iyi" hesaplanmaz
    if test_adi in ("Omuz Rotasyon Testi (Sopa/İp)", "Oturma Yüksekliği", "Oturma Yüksekliği (TSYT)",
                    "Kulaç Uzunluğu (TSYT)", "Boy ve Vücut Ağırlığı (TSYT)", "Sargent Dikey Sıçrama Testi (Duvar)"):
        mesafe_anahtarlari = []
    if mesafe_anahtarlari:
        mesafeler = [guvenli_float(degerler[k]) for k in mesafe_anahtarlari if degerler[k]]
        mesafeler = [m for m in mesafeler if m > 0]
        if mesafeler:
            hesaplanan["En İyi Değer (cm)"] = max(mesafeler)

    # ── Paket 35c: Sargent — en iyi sıçrama erişimi − ayakta erişim (kullanıcıdan istenmez) ──
    if test_adi == "Sargent Dikey Sıçrama Testi (Duvar)":
        ayakta = guvenli_float(degerler.get("Ayakta Erişim (cm)", 0))
        erisim = [v for v in (guvenli_float(degerler.get(k, 0)) for k in SARGENT_DENEMELER) if v > 0]
        if erisim and ayakta <= 0:
            uyarilar.append("⚠️ Ayakta erişim girilmedi; sıçrama yüksekliği hesaplanamadı.")
        elif erisim and max(erisim) <= ayakta:
            uyarilar.append("⚠️ En yüksek sıçrama erişimi ayakta erişimden büyük değil; değerleri kontrol edin.")
        elif erisim:
            hesaplanan["Sıçrama Yüksekliği — En İyi (cm)"] = round(max(erisim) - ayakta, 1)

    # ── Paket 35: rölatif kuvvet = 1RM / kayıtlı vücut ağırlığı (kullanıcıdan istenmez) ──
    if test_adi in ROLATIF_KUVVET:
        giris, cikis = ROLATIF_KUVVET[test_adi]
        yuk = guvenli_float(degerler.get(giris, 0))
        if yuk > 0 and sporcu_kilo > 0:
            hesaplanan[cikis] = round(yuk / sporcu_kilo, 3)
        elif yuk > 0:
            uyarilar.append("⚠️ Sporcunun kayıtlı vücut ağırlığı yok; rölatif değer hesaplanamadı. "
                            "Sporcu profiline kilo (kg) girin.")

    if "Pik Güç (W)" in degerler and "Min Güç (W)" in degerler:
        pik = guvenli_float(degerler.get("Pik Güç (W)"))
        ort = guvenli_float(degerler.get("Ortalama Güç (W)"))
        mn = guvenli_float(degerler.get("Min Güç (W)"))
        if pik > 0 and sporcu_kilo > 0:
            hesaplanan["Pik Güç (W/kg)"] = round(pik / sporcu_kilo, 2)
            hesaplanan["Ortalama Güç (W/kg)"] = round(ort / sporcu_kilo, 2)
            hesaplanan["Yorgunluk İndeksi (%)"] = round((pik - mn) / pik * 100, 1)

    if test_adi == "Cooper 12 Dakika Koşusu" and "Tamamlanan Mesafe (m)" in degerler:
        mesafe = guvenli_float(degerler.get("Tamamlanan Mesafe (m)"))
        if mesafe > 0:
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round((mesafe - 504.9) / 44.73, 1)

    if test_adi in ["20m Mekik Koşusu (Beep Test)", "20m Mekik Koşusu (Eurofit/Léger)"] and "Son Seviye" in degerler:
        seviye = guvenli_float(degerler.get("Son Seviye"))
        if seviye > 0:
            # Léger et al. (1988) 20m MSRT VO2max denklemi
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(22.859 + (seviye * 1.593), 1)

    # ── PACER / 20m mekik tur sayisindan VO2max (Mahar 2006) ──
    if test_adi in ["PACER Testi", "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)",
                    "20m Mekik Koşusu (PREFIT)"] and "Tamamlanan Tur Sayısı" in degerler:
        tur = guvenli_float(degerler.get("Tamamlanan Tur Sayısı"))
        _yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        _cins = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        if tur > 0 and _yas > 0:
            _kod = 1 if _cins == "Erkek" else 0
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(
                47.438 - (0.265 * _yas) + (4.571 * _kod) + (0.182 * tur), 1)

    if test_adi == "20m Mekik Koşusu (ALPHA)" and "Son Hız (km/h)" in degerler:
        hiz = guvenli_float(degerler.get("Son Hız (km/h)"))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        if hiz > 0 and sporcu_yas > 0:
            vo2_alpha = 31.025 + (3.238 * hiz) - (3.248 * sporcu_yas) + (0.1536 * sporcu_yas * hiz)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_alpha, 1)

    if test_adi == "Bel Çevresi ve VKİ (Vücut Kompozisyonu)":
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        if sporcu_boy > 0 and sporcu_kilo > 0:
            boy_m = sporcu_boy / 100
            vki = round(sporcu_kilo / (boy_m ** 2), 1)
            hesaplanan["VKİ (kg/m²)"] = vki

    # ── Yo-Yo: VO2max tahmini (Bangsbo et al., 2008) ──
    # Tüm Yo-Yo testleri (18 adet) ada göre ayrılır:
    #   IR1 → VO2max = mesafe × 0.0084 + 36.4
    #   IR2 → VO2max = mesafe × 0.0136 + 45.3
    if test_adi.startswith("Yo-Yo") and "Tamamlanan Mesafe (m)" in degerler:
        mesafe = guvenli_float(degerler.get("Tamamlanan Mesafe (m)"))
        if mesafe > 0:
            if "IR2" in test_adi:
                hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(mesafe * 0.0136 + 45.3, 1)
            elif "IR1" in test_adi:
                hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(mesafe * 0.0084 + 36.4, 1)

    # ── FitnessGram: PACER VO2max ──
    if test_adi == "PACER (20m Mekik Koşusu)" and "Tamamlanan Tur Sayısı" in degerler:
        tur = guvenli_float(degerler.get("Tamamlanan Tur Sayısı"))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        if tur > 0 and sporcu_yas > 0:
            # Mahar et al. (2006) PACER VO2peak formülü
            cinsiyet_kodu = 1 if sporcu_cinsiyet == "Erkek" else 0
            vo2_pacer = 47.438 - (0.265 * sporcu_yas) + (4.571 * cinsiyet_kodu) + (0.182 * tur)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_pacer, 1)

    # ── CAPL-2 CAMSA: toplam = beceri (0-14) + süre puanı (1-14, CAPL-2 tablosundan girilir) ──
    if test_adi == "CAPL Engel Parkuru (Motor Beceri)":
        _b = guvenli_float(degerler.get("Beceri Puanı (0-14)", 0))
        _sp = guvenli_float(degerler.get("Süre Puanı (1-14)", 0))
        if _sp > 0:
            hesaplanan["Toplam CAMSA Puanı (1-28)"] = round(_b + _sp, 1)

    # ── Yüzme T-30: ortalama hız = mesafe / 1800 sn (Olbrecht ve ark. 1985) ──
    if test_adi == "T-30 Yüzme Testi":
        _m30 = guvenli_float(degerler.get("Toplam Mesafe (m)", 0))
        if _m30 > 0:
            hesaplanan["T-30 Hızı (m/sn)"] = round(_m30 / 1800, 3)

    # ── FitnessGram: Trunk Lift en iyi değer ──
    if test_adi == "Trunk Lift (Gövde Kaldırma) Testi":
        d1 = guvenli_float(degerler.get("Deneme 1 (cm)", 0))
        d2 = guvenli_float(degerler.get("Deneme 2 (cm)", 0))
        en_iyi_tl = max(d1, d2)
        if en_iyi_tl > 0:
            # FitnessGram maks. 30.5 cm sınırı
            hesaplanan["En İyi Kaldırma (cm)"] = min(en_iyi_tl, 30.5)

    # ── FitnessGram: 1 Mil VO2max ──
    if test_adi == "1 Mil Yürüyüş/Koşu Testi":
        dk = guvenli_float(degerler.get("Süre (dakika)", 0))
        sn = guvenli_float(degerler.get("Süre (saniye)", 0))
        sporcu_yas = guvenli_float(sporcu_satir.get("Yaş", 0))
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        cinsiyet_kodu = 1 if sporcu_cinsiyet == "Erkek" else 0
        sure_toplam_dk = dk + (sn / 60)
        if sure_toplam_dk > 0 and sporcu_yas > 0 and sporcu_boy > 0 and sporcu_kilo > 0:
            vki = sporcu_kilo / ((sporcu_boy / 100) ** 2)
            vo2_mil = 108.94 - (8.41 * sure_toplam_dk) + (0.34 * (sure_toplam_dk ** 2)) + (0.21 * sporcu_yas * cinsiyet_kodu) - (0.84 * vki)
            hesaplanan["Toplam Süre (dk)"] = round(sure_toplam_dk, 2)
            hesaplanan["VO2max Tahmini (ml/kg/min)"] = round(vo2_mil, 1)

    # ── FitnessGram: Deri Kıvrımı Vücut Yağ % ──
    if test_adi == "Vücut Kompozisyonu - Deri Kıvrımı":
        triceps = guvenli_float(degerler.get("Triceps Deri Kıvrımı (mm)", 0))
        baldır = guvenli_float(degerler.get("Baldır Deri Kıvrımı (mm)", 0))
        # e/k küçük girilse de kabul (harf dönüştürme işlevi yerine eşleme: Türkçe i/İ kuralına dokunmaz)
        cinsiyet_gir = {"e": "E", "E": "E", "k": "K", "K": "K"}.get(str(degerler.get("Cinsiyet (E/K)", "")).strip(), "")
        sporcu_cinsiyet = str(sporcu_satir.get("Cinsiyet", "Erkek"))
        # Girişten yoksa sporcu profilinden al
        if cinsiyet_gir not in ["E", "K"]:
            cinsiyet_gir = "E" if sporcu_cinsiyet == "Erkek" else "K"
        if triceps > 0 and baldır > 0:
            toplam_mm = triceps + baldır
            hesaplanan["Toplam Deri Kıvrımı (mm)"] = toplam_mm
            if cinsiyet_gir == "E":
                yag_yuzde = 0.735 * toplam_mm + 1.0
            else:
                yag_yuzde = 0.610 * toplam_mm + 5.1
            hesaplanan["Vücut Yağ % (Tahmini)"] = round(yag_yuzde, 1)
            # Yağsız vücut kütlesi
            if sporcu_kilo > 0:
                hesaplanan["Yağsız Kütle (kg)"] = round(sporcu_kilo * (1 - yag_yuzde / 100), 1)

    # ── CMJ / SJ / DJ en iyi değer ──
    if "CMJ" in test_adi or "Dikey Sıçrama" in test_adi:
        for prefix in ["CMJ", "SJ", "DJ"]:
            denemeleri = [guvenli_float(degerler.get(f"{prefix} Deneme {i} (cm)", 0)) for i in range(1, 4)]
            en_iyi = max(denemeleri)
            if en_iyi > 0:
                hesaplanan[f"{prefix} En İyi (cm)"] = en_iyi
        # CMJ-SJ elastik enerji farkı
        cmj_en_iyi = hesaplanan.get("CMJ En İyi (cm)", 0)
        sj_en_iyi  = hesaplanan.get("SJ En İyi (cm)", 0)
        if cmj_en_iyi > 0 and sj_en_iyi > 0:
            hesaplanan["Elastik Enerji Katkısı (cm)"] = round(cmj_en_iyi - sj_en_iyi, 1)
        # Tek CMJ varsa (Deneme 1/2/3 cm)
        if "CMJ En İyi (cm)" not in hesaplanan:
            denemeleri = [guvenli_float(degerler.get(f"Deneme {i} (cm)", 0)) for i in range(1, 4)]
            en_iyi = max(denemeleri)
            if en_iyi > 0:
                hesaplanan["CMJ En İyi (cm)"] = en_iyi
    if "Nordic" in test_adi and "NHT" in test_adi:
        sag = guvenli_float(degerler.get("Sağ Bacak Pik Kuvveti (N)", 0))
        sol = guvenli_float(degerler.get("Sol Bacak Pik Kuvveti (N)", 0))
        sag_kg = guvenli_float(degerler.get("Sağ Bacak (N/kg)", 0))
        sol_kg = guvenli_float(degerler.get("Sol Bacak (N/kg)", 0))
        if sag > 0 and sol > 0:
            guclu = max(sag, sol)
            zayif = min(sag, sol)
            asimetri = round((guclu - zayif) / guclu * 100, 1)
            hesaplanan["Asimetri İndeksi (%)"] = asimetri
            guclu_taraf = "Sağ" if sag >= sol else "Sol"
            hesaplanan["Güçlü Taraf"] = guclu_taraf
            if asimetri < 10:
                hesaplanan["Klinik Yorum"] = "✅ Simetrik (< %10)"
            elif asimetri < 15:
                hesaplanan["Klinik Yorum"] = "⚠️ Dikkat: Takip önerilir (%10-15)"
            else:
                hesaplanan["Klinik Yorum"] = "🔴 Yüksek Risk: Müdahale gerekli (> %15)"
        if sag_kg > 0 and sol_kg > 0:
            guclu_kg = max(sag_kg, sol_kg)
            zayif_kg = min(sag_kg, sol_kg)
            asimetri_kg = round((guclu_kg - zayif_kg) / guclu_kg * 100, 1)
            hesaplanan["Asimetri İndeksi N/kg (%)"] = asimetri_kg

    # ── İzokinetik H:K Oranı Otomatik ──
    if "İzokinetik" in test_adi or "Keytsman" in test_adi:
        quad_dom = guvenli_float(degerler.get("İzokinetik Kuadriseps 180°/sn Dom. (Nm/kg)", 0))
        ham_dom  = guvenli_float(degerler.get("İzokinetik Hamstring 180°/sn Dom. (Nm/kg)", 0))
        quad_nd  = guvenli_float(degerler.get("İzokinetik Kuadriseps 180°/sn N-Dom. (Nm/kg)", 0))
        ham_nd   = guvenli_float(degerler.get("İzokinetik Hamstring 180°/sn N-Dom. (Nm/kg)", 0))
        if quad_dom > 0 and ham_dom > 0:
            hk_dom = round(ham_dom / quad_dom * 100, 1)
            hesaplanan["H:K Oranı Dom. (%)"] = hk_dom
            hesaplanan["H:K Dom. Yorum"] = "✅ Normal" if hk_dom >= 60 else "🔴 Risk: < %60"
        if quad_nd > 0 and ham_nd > 0:
            hk_nd = round(ham_nd / quad_nd * 100, 1)
            hesaplanan["H:K Oranı N-Dom. (%)"] = hk_nd
            hesaplanan["H:K N-Dom. Yorum"] = "✅ Normal" if hk_nd >= 60 else "🔴 Risk: < %60"
        if quad_dom > 0 and quad_nd > 0:
            asim_quad = round(abs(quad_dom - quad_nd) / max(quad_dom, quad_nd) * 100, 1)
            hesaplanan["Kuadriseps Asimetri (%)"] = asim_quad
        if ham_dom > 0 and ham_nd > 0:
            asim_ham = round(abs(ham_dom - ham_nd) / max(ham_dom, ham_nd) * 100, 1)
            hesaplanan["Hamstring Asimetri (%)"] = asim_ham

    # ── KTK3+ Motor Koordinasyon otomatik toplamları (0 geçerli skordur) ──
    hesaplanan.update(ktk3_toplamlari(test_adi, degerler))

    if test_adi == "Tek Ayak Engel Üzerinden Sıçrama (Hopping for Height)":
        hh_sag = guvenli_float(degerler.get("Sağ Bacak Puanı (maks 39)", 0))
        hh_sol = guvenli_float(degerler.get("Sol Bacak Puanı (maks 39)", 0))
        if hh_sag > 0 or hh_sol > 0:
            hesaplanan["Toplam Puan (maks 78)"] = int(min(hh_sag, 39) + min(hh_sol, 39))
        if hh_sag > 0 and hh_sol > 0:
            hh_asim = round(abs(hh_sag - hh_sol) / max(hh_sag, hh_sol) * 100, 1)
            hesaplanan["Bacak Asimetrisi (%)"] = hh_asim
            hesaplanan["Güçlü Bacak"] = "Sağ" if hh_sag >= hh_sol else "Sol"
            if hh_asim < 10:
                hesaplanan["Asimetri Yorumu"] = "✅ Simetrik (< %10)"
            elif hh_asim < 15:
                hesaplanan["Asimetri Yorumu"] = "⚠️ Takip önerilir (%10-15)"
            else:
                hesaplanan["Asimetri Yorumu"] = "🔴 Belirgin fark (> %15)"

    # ── FSC: Top Sektirme (BOT-2) — iki denemenin en iyisi, maks 10 ──
    if test_adi == "Top Sektirme — Alternatif El (BOT-2)":
        bd = [guvenli_float(degerler.get(k, 0)) for k in
              ["Deneme 1 (doğru sektirme, maks 10)", "Deneme 2 (doğru sektirme, maks 10)"]]
        if max(bd) > 0:
            en_iyi_bd = int(min(max(bd), 10))
            hesaplanan["En İyi Sektirme (maks 10)"] = en_iyi_bd
            if en_iyi_bd == 10:
                hesaplanan["Tavan Notu"] = "Üst sınıra ulaştı (10/10)"

    # ── FSC: Omuz Rotasyonu — biakromiyal genişlik girildiyse net skor ──
    if test_adi == "Omuz Rotasyon Testi (Sopa/İp)":
        aralik = guvenli_float(degerler.get("En Dar El Aralığı (cm)", 0))
        biak = guvenli_float(degerler.get("Biakromiyal Genişlik (cm) — opsiyonel", 0))
        if aralik > 0 and biak > 0:
            hesaplanan["Net Omuz Rotasyon Skoru (cm)"] = round(aralik - biak, 1)

    # ── FSC: Oturma Yüksekliği — bacak uzunluğu ve OY/Boy oranı ──
    if test_adi == "Oturma Yüksekliği":
        oy = guvenli_float(degerler.get("Oturma Yüksekliği (cm)", 0))
        sporcu_boy = guvenli_float(sporcu_satir.get("Boy (cm)", 0))
        if oy > 0 and sporcu_boy > 0:
            if oy >= sporcu_boy:
                uyarilar.append("⚠️ Oturma yüksekliği boydan büyük ya da eşit girildi. "
                           "Oturak yüksekliğinin çıkarıldığını ve profildeki boyu kontrol edin.")
            else:
                hesaplanan["Bacak Uzunluğu (cm)"] = round(sporcu_boy - oy, 1)
                hesaplanan["Oturma Yüksekliği / Boy Oranı"] = round(oy / sporcu_boy, 3)
    return hesaplanan, uyarilar


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

# ── 1) ÇİZİM TAKIMI ──
TG_TUVAL = (260, 140)        # viewBox genişlik × yükseklik — her görsel bununla çizilir
TG_ZEMIN = 116               # zemin çizgisinin y'si (altında ölçü okları için şerit: 116-128)
TG_KALINLIK = {"figur": 3.2, "govde": 4.0, "esya": 2.0, "olcu": 1.6, "zemin": 1.5, "vurgu": 4.0, "kilavuz": 0.8}
TG_YAZI = 8.5                # not ve ölçü etiketi
TG_BASLIK_YAZI = 9.5         # üst başlık (kalın)
TG_EN_COK_YAZI = 3           # sahne başına yazı sınırı
# Paket 34: renk hex değil yedekli CSS değişkeni — var(--tg-murekkep, <açık yedek>) … Değişkenler TEMA_CSS'te iki tema
# için tanımlı; tanımsız kaldığı bağlamda (rapor, dışa aktarım) yedek açık renk çizilir, figür kaybolmaz.
TG_RENK = {"figur": tg_renk("murekkep"), "esya": tg_renk("ikincil"), "olcu": tg_renk("ana"),
           "zemin": tg_renk("ikincil"), "dolgu": tg_renk("cizgi"), "yuzey": tg_renk("yuzey")}
# Çocuk figürünün parça uzunlukları (tuval biriminde; ayakta boy ≈ 92)
_TG_BOY = {"govde": 30, "boyun": 9, "bas": 6.5, "uyluk": 22, "baldir": 23, "ust": 16, "on": 15, "ayak": 6,
           "omuz": 2.0, "kalca": 2.0}
# Ayakta temel poz: uzuvlar ayrışık (yakın/uzak bacak ve kol üst üste binmez). Her poz bundan türer.
# Bacak açıları ayak bilekleri arası ≥ 3 birim olacak biçimde seçildi (u1=4/b1=-3/u2=-5/b2=2 ile 1,4 kalıyordu).
TG_TEMEL_POZ = {"g": 0, "u1": 7, "b1": -1, "u2": -6, "b2": 0, "k1": 9, "o1": 7, "k2": -8, "o2": -6,
                "a1": 90, "a2": 90}
TG_UCLAR = ("el1", "el2", "ayak1", "ayak2")   # uzuv uçları (örtüşme denetimi)
# Figür rolü → GÖRSEL SİSTEM'deki katman (FIGUR_KATMANI): renk, opaklık, kalınlık ve kesik çizgi oradan gelir
TG_ROL_KATMANI = {"olculen": "olculen", "partner": "ikinci_kisi", "iz": "onceki_an"}
TG_EN_YAKIN_UC = 3.0
# Yazı yerleşimi (Paket 16): üst ve alt şerit yalnız yazıya ait; çizim bu şeritlere girmez.
TG_SERIT_UST = 16            # üst şerit y ∈ [0, 16]: başlık
TG_SERIT_ALT = 128           # alt şerit y ∈ [128, 140]: not
TG_YAZI_PAYI = 4             # etiket tuval kenarından en az
TG_CIZGI_PAYI = 6            # yazı kutusu ↔ en yakın figür/eşya çizgisi en az (Paket 17: kutu değil gerçek çizgi)
TG_SATIR = 11                # alt alta iki yazının taban farkı en az (8,5 punto için)
TG_OLCU_Y = 121              # zemin üstü mesafe okları: zemin çizgisinin altında, alt şeritten (128) önce
# Büyük harf kuralı: etiket büyük harf, rakam ya da özel adla başlar (özel ad kendi yazımını korur).
# Büyük harfler etiket metnine elle yazılır — dönüştürme işlevi kullanılmaz (Türkçe i/İ kuralı).
TG_OZEL_ADLAR = ("TSYT", "KTK3+", "Yo-Yo", "Pro Agility", "SWFT", "SJFT", "NBA", "Borg", "Wingate")
# Yedi bölmeli rakam bölmeleri (a üst, b sağ üst, c sağ alt, d alt, e sol alt, f sol üst, g orta) — yalnız sıra
# numarası rozetinde kullanılır; sayaç rakam göstermez (Paket 19)
_TG_RAKAM = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
             8: "abcdefg", 9: "abcdfg"}


def _tg_xml_sekilleri(xml, dx=0.0, dy=0.0):
    """
    Çizim xml'indeki şekillerin geometrisi (denetim: yazının EN YAKIN ÇİZGİYE uzaklığı). Yazı dışarıda.
    ("cizgi", x1, y1, x2, y2, yarı_kalınlık) — çizgi, dikdörtgen kenarı, yol parçası;
    ("disk", cx, cy, r) — dolu daire/elips (yarıçap çizgi payıyla); ("alan", x0, y0, x1, y1) — dolu dikdörtgen.
    """
    xml = re.sub(r"<text\b.*?</text>", "", xml, flags=re.S)
    sekiller = []
    for ad, govde in re.findall(r"<(line|rect|circle|ellipse|path)\b([^>]*)>", xml):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', govde))
        f = lambda n: float(a.get(n, 0) or 0)
        k = f("stroke-width") / 2 if a.get("stroke", "none") != "none" else 0.0
        dolu = a.get("fill", "black") != "none"
        if ad == "line":
            sekiller.append(("cizgi", f("x1") + dx, f("y1") + dy, f("x2") + dx, f("y2") + dy, k))
        elif ad == "rect":
            x0, y0, x1, y1 = f("x") + dx, f("y") + dy, f("x") + f("width") + dx, f("y") + f("height") + dy
            if dolu:
                sekiller.append(("alan", x0 - k, y0 - k, x1 + k, y1 + k))
            else:
                sekiller += [("cizgi", x0, y0, x1, y0, k), ("cizgi", x1, y0, x1, y1, k),
                             ("cizgi", x1, y1, x0, y1, k), ("cizgi", x0, y1, x0, y0, k)]
        elif ad == "circle":
            sekiller.append(("disk", f("cx") + dx, f("cy") + dy, f("r") + k))
        elif ad == "ellipse":                          # elips: 24 parçalı çevre
            cx, cy, rx, ry = f("cx") + dx, f("cy") + dy, f("rx"), f("ry")
            n = [(cx + rx * _math.cos(i * _math.pi / 12), cy + ry * _math.sin(i * _math.pi / 12)) for i in range(25)]
            sekiller += [("cizgi", *a_, *b_, k) for a_, b_ in zip(n, n[1:])]
        else:
            noktalar, cx, cy, kip, sayilar = [], 0.0, 0.0, "M", []
            for parca in re.findall(r"[MLQqlmz]|-?\d+(?:\.\d+)?", a.get("d", "")):
                if parca.isalpha():
                    if parca == "z" and noktalar:
                        noktalar.append(noktalar[0])
                    kip, sayilar = parca, []
                    continue
                sayilar.append(float(parca))
                gerek = 4 if kip in "Qq" else 2
                if len(sayilar) == gerek:
                    goreli = kip.islower()
                    p = [(sayilar[i] + (cx if goreli else 0), sayilar[i + 1] + (cy if goreli else 0)) for i in range(0, gerek, 2)]
                    noktalar += p
                    cx, cy = p[-1]
                    sayilar = []
            sekiller += [("cizgi", x1 + dx, y1 + dy, x2 + dx, y2 + dy, k)
                         for (x1, y1), (x2, y2) in zip(noktalar, noktalar[1:])]
    return sekiller


def _tg_xml_kutulari(xml, dx=0.0, dy=0.0):
    """Çizim xml'indeki şekillerin sınır kutuları (çizgi kalınlığı dahil); yazı dışarıda. Denetim içindir."""
    xml = re.sub(r"<text\b.*?</text>", "", xml, flags=re.S)
    kutular = []
    for ad, govde in re.findall(r"<(line|rect|circle|ellipse|path)\b([^>]*)>", xml):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', govde))
        f = lambda n: float(a.get(n, 0) or 0)
        k = f("stroke-width") / 2 if a.get("stroke", "none") != "none" else 0.0
        if ad == "line":
            xs, ys = [f("x1"), f("x2")], [f("y1"), f("y2")]
        elif ad == "rect":
            xs, ys = [f("x"), f("x") + f("width")], [f("y"), f("y") + f("height")]
        elif ad == "circle":
            xs, ys = [f("cx") - f("r"), f("cx") + f("r")], [f("cy") - f("r"), f("cy") + f("r")]
        elif ad == "ellipse":
            xs, ys = [f("cx") - f("rx"), f("cx") + f("rx")], [f("cy") - f("ry"), f("cy") + f("ry")]
        else:
            xs, ys, cx, cy, kip = [], [], 0.0, 0.0, "M"
            sayilar = []
            for parca in re.findall(r"[MLQqlmz]|-?\d+(?:\.\d+)?", a.get("d", "")):
                if parca.isalpha():
                    kip, sayilar = parca, []
                    continue
                sayilar.append(float(parca))
                gerek = 4 if kip in "Qq" else 2
                if len(sayilar) == gerek:
                    goreli = kip.islower()
                    noktalar = [(sayilar[i] + (cx if goreli else 0), sayilar[i + 1] + (cy if goreli else 0))
                                for i in range(0, gerek, 2)]
                    for x, y in noktalar:
                        xs.append(x)
                        ys.append(y)
                    cx, cy = noktalar[-1]
                    sayilar = []
            if not xs:
                continue
        kutular.append((min(xs) - k + dx, min(ys) - k + dy, max(xs) + k + dx, max(ys) + k + dy))
    return kutular


def _tg_yon(aci):
    """Aşağıdan ölçülen açı (derece, + = ileri/+x) → birim vektör (SVG: y aşağı)."""
    r = _math.radians(aci)
    return _math.sin(r), _math.cos(r)


def tg_eklemler(p):
    """
    Poz → eklem noktaları. p: hx, hy (kalça), g (gövde eğimi, + ileri), u/b (uyluk/baldır), k/o (üst kol/ön kol)
    1 = yakın, 2 = uzak; a1/a2 ayak açısı (90 = ileri); yon (+1 sağa, −1 sola bakar); s ölçek; cephe (önden).
    """
    s, yon = p.get("s", 1.0), p.get("yon", 1)
    L = {k: v * s for k, v in _TG_BOY.items()}
    hx, hy = p["hx"], p["hy"]

    def uc(x, y, aci, uz):
        dx, dy = _tg_yon(aci)
        return x + yon * dx * uz, y + dy * uz

    g = _math.radians(p.get("g", 0))
    ux, uy = yon * _math.sin(g), -_math.cos(g)          # gövde doğrultusu (yukarı)
    px, py = -uy, ux                                    # gövdeye dik (omuz/kalça çizgisi)
    boyun = (hx + ux * L["govde"], hy + uy * L["govde"])
    bas = (boyun[0] + ux * L["boyun"], boyun[1] + uy * L["boyun"])
    e = {"kalca": (hx, hy), "boyun": boyun, "bas": bas,
         "bas_ust": (bas[0] + ux * L["bas"], bas[1] + uy * L["bas"]),     # başın tepesi (ölçü bağı için)
         # çene: baş çemberinde yüzün baktığı yanın altı (yüz = gövdeye dik, yon yönünde) — ölçü bağı için
         "cene": (bas[0] + (0.6 * -uy - 0.8 * ux) * L["bas"], bas[1] + (0.6 * ux - 0.8 * uy) * L["bas"]),
         "omuz_a": (boyun[0] + px * L["omuz"], boyun[1] + py * L["omuz"]),
         "omuz_b": (boyun[0] - px * L["omuz"], boyun[1] - py * L["omuz"]),
         "kalca_a": (hx + px * L["kalca"], hy + py * L["kalca"]),
         "kalca_b": (hx - px * L["kalca"], hy - py * L["kalca"])}
    on = p.get("cephe", False)
    for i, isaret in (("1", 1), ("2", -1)):
        kok_b = e["kalca_a" if isaret > 0 else "kalca_b"] if on else (hx, hy)
        kok_k = e["omuz_a" if isaret > 0 else "omuz_b"] if on else boyun
        diz = uc(*kok_b, p.get("u" + i, 0), L["uyluk"])
        ayak = uc(*diz, p.get("b" + i, 0), L["baldir"])
        e["kok_b" + i], e["kok_k" + i] = kok_b, kok_k
        e["diz" + i], e["ayak" + i] = diz, ayak
        e["parmak" + i] = uc(*ayak, p.get("a" + i, 90), L["ayak"])
        dirsek = uc(*kok_k, p.get("k" + i, 0), L["ust"])
        e["dirsek" + i], e["el" + i] = dirsek, uc(*dirsek, p.get("o" + i, 0), L["on"])
    return e


# Figürün son karesindeki çizgi parçaları (yazı ↔ en yakın çizgi denetimi; çizim _tg_parcalar ile aynı)
_TG_FIGUR_CIZGILERI = [("parmak1", "ayak1"), ("ayak1", "diz1"), ("diz1", "kok_b1"), ("parmak2", "ayak2"),
                       ("ayak2", "diz2"), ("diz2", "kok_b2"), ("kalca", "boyun"), ("el1", "dirsek1"),
                       ("dirsek1", "kok_k1"), ("el2", "dirsek2"), ("dirsek2", "kok_k2"),
                       ("omuz_a", "omuz_b"), ("kalca_a", "kalca_b")]


def _tg_d(noktalar):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in noktalar)


def _tg_parcalar(e):
    """Figür parçaları: uzak uzuvlar soluk; gövde kalın; omuz ve kalça kısa çizgi."""
    return {
        "bacak2": _tg_d([e["parmak2"], e["ayak2"], e["diz2"], e["kok_b2"]]),
        "kol2": _tg_d([e["el2"], e["dirsek2"], e["kok_k2"]]),
        "govde": _tg_d([e["kalca"], e["boyun"]]),
        "kusak": _tg_d([e["omuz_a"], e["omuz_b"]]) + " " + _tg_d([e["kalca_a"], e["kalca_b"]]),
        "bacak1": _tg_d([e["parmak1"], e["ayak1"], e["diz1"], e["kok_b1"]]),
        "kol1": _tg_d([e["el1"], e["dirsek1"], e["kok_k1"]]),
    }


def _tg_ara(p0, p1, f):
    """İki poz arasında açı/konum ara değeri (uzuv boyu korunur)."""
    sonuc = dict(p1)
    for k, v in p1.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and k in p0 and k != "yon":
            sonuc[k] = p0[k] + (v - p0[k]) * f
    if f < 0.5:
        sonuc["yon"] = p0.get("yon", 1)
    return sonuc


def _tg_kareler(anahtarlar, adim=6):
    """[(t, poz)] → sık kareler: SMIL doğrusal ara değerde uzuvlar kısalmasın."""
    kareler = []

    def taban(p):
        e = tg_eklemler(p)
        return max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))
    for (t0, p0), (t1, p1) in zip(anahtarlar, anahtarlar[1:]):
        z0, z1 = taban(p0), taban(p1)
        for j in range(adim):
            f = j / adim
            q = _tg_ara(p0, p1, f * f * (3 - 2 * f))
            if abs(z0 - z1) < 0.5:                    # iki anahtar aynı zeminde: ara karede de o zeminde
                q = dict(q, hy=q["hy"] + (z0 - taban(q)))
            elif taban(q) > max(z0, z1):              # zemine gömülmez
                q = dict(q, hy=q["hy"] + (max(z0, z1) - taban(q)))
            kareler.append((t0 + (t1 - t0) * f, q))
    kareler.append(anahtarlar[-1])
    return kareler


def _tg_anim(nitelik, degerler, zamanlar, sure):
    kt = ";".join(f"{t:.4f}" for t in zamanlar)
    return (f'<animate attributeName="{nitelik}" values="{";".join(degerler)}" keyTimes="{kt}" '
            f'dur="{sure}s" begin="0s" fill="freeze" calcMode="linear"/>')


def tg_poz(hx, **k):
    """Temel pozdan türeyen poz (ayakta; kalça yüksekliği ölçeğe göre)."""
    s = k.get("s", 1.0)
    p = {"hx": hx, "hy": TG_ZEMIN - (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s, **TG_TEMEL_POZ}
    p.update(k)
    return p


def tg_yerlestir(p, ayak_x=None, bacak="1", zemin=None):
    """Pozu zemine oturtur: en alttaki ayak noktası (bilek ya da parmak) zemine değer; ayak_x verilirse o ayak bu x'e gelir."""
    zemin = TG_ZEMIN if zemin is None else zemin
    e = tg_eklemler(p)
    q = dict(p, hy=p["hy"] + (zemin - max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))))
    if ayak_x is not None:
        q["hx"] = p["hx"] + (ayak_x - e["ayak" + bacak][0])
    return q


class TgSahne:
    """Tek tuvalde bir test sahnesi. Her öğe hem hareketli hem durağan (son kare) olarak üretilir."""

    def __init__(self, sure=3.0):
        self.sure = sure
        self.ogeler = []          # (hareketli_xml, duragan_xml)
        self.yazi_sayisi = 0
        self.olculer = []         # ölçü okları (x1, y1, x2, y2) — denetim uzunluk > 0 ister
        self.cubuklar = []        # çubuk / çubuk_iki: [(t, x1, y1, x2, y2)] her karede (Paket 25 denetimi)
        self.son_eklemler = None  # ÖLÇÜLEN figürün son karedeki eklemleri — denetim uç mesafesine bakar
        self.tum_eklemler = []    # her figürün her karedeki eklemleri — denetim tuval sınırına bakar
        self.yazi_kutulari = []   # (x0, y0, x1, y1, metin) — denetim çakışmaya bakar
        self.olcu_kayit = []      # {"uc": (x1, y1, x2, y2), "etiket", "metre", "es"} — ölçek ve etiket denetimi
        self.figurler = []        # {"rol", "opaklik", "son"} — ikinci figür denetimi
        self.cizim_sekilleri = [] # (tur, şekil…) son kare geometrisi — yazı ↔ en yakın çizgi denetimi
        self.cizim_kutulari = []  # (x0, y0, x1, y1, tur) son kare: tur "esya" | "figur" | "isaret" (ok, kılavuz, iz)
        self.figur_alani = []     # (x0, y0, x1, y1) figürün bütün karelerdeki alanı — şerit denetimi
        self.zaman_seritleri = [] # periyot şeritleri (x0, x1, y) — süreli testler
        self.sayaclar = []        # sayaç kutuları (x0, y0, x1, y1)
        self.kronometreler = []   # süreölçer simgeleri (x0, y0, x1, y1)
        self.numaralar = []       # sıra numarası rozetleri (n, x, y)
        self.hedefler = []        # vuruş hedefleri (tür, merkez_x, merkez_y)
        # Paket 21: durağan kopya ayrı bir sahne olabilir (kayan tur — Koordinasyon Parkuru). None: durağan = son kare
        self.duragan = None
        self.kayan_kutular = []   # kaydir ile ötelenen öğelerin kutuları (y aralığı; x kaydığı için her yere uğrayabilir)
        self.kaymalar = []        # kaydir anahtarları [(t, dx, dy)] — kayan sahnede hız denetimi
        self.istasyon_araliklari = []   # kayan turda beceri/istasyon pencereleri [(t0, t1)] (0-1)
        self.parkur_kaymasi = []  # kayan turda parkurun kayması [(t, dx)] (tuval x = dünya x + dx) — hız denetimi
        self.donusler = []        # figür grubu dönüşleri: {"t0", "t1", "cx", "cy", "bas_r", "kareler": [(t, eklemler)]}

    def _kaydet(self, xml, tur, dx=0.0, dy=0.0):
        self.cizim_kutulari += [(*k, tur) for k in _tg_xml_kutulari(xml, dx, dy)]
        self.cizim_sekilleri += [(tur, *g) for g in _tg_xml_sekilleri(xml, dx, dy)]

    # ── çizim yardımcıları (renk ve kalınlık yalnız takımdan) ──
    def esya(self, xml, tur="esya"):
        self._kaydet(xml, tur)
        self.ogeler.append((xml, xml))

    def cizgi(self, x1, y1, x2, y2, tur="esya", kesik=False, ok=False):
        """ok=True: iki uçta ok başı; ok="son": yalnız (x2, y2) ucunda."""
        r, k = TG_RENK[tur if tur in TG_RENK else "olcu"], TG_KALINLIK[tur]
        da = ' stroke-dasharray="4 3"' if kesik else (' stroke-dasharray="2 2"' if tur == "kilavuz" else "")
        xml = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{r}" '
               f'stroke-width="{k}" stroke-linecap="round"{da}/>')
        if ok:
            uz = _math.hypot(x2 - x1, y2 - y1) or 1
            ux, uy = (x2 - x1) / uz, (y2 - y1) / uz
            for (qx, qy, sx) in ((x2, y2, 1), (x1, y1, -1))[:1 if ok == "son" else 2]:
                bx, by = qx - sx * ux * 5, qy - sx * uy * 5
                xml += (f'<path d="M{qx:.1f},{qy:.1f} L{bx - uy * 2.2:.1f},{by + ux * 2.2:.1f} '
                        f'L{bx + uy * 2.2:.1f},{by - ux * 2.2:.1f} z" fill="{r}"/>')
        return xml

    def kutu(self, x, y, w, h, dolgu="dolgu", rx=1.5):
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                f'fill="{TG_RENK[dolgu]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')

    def nokta(self, x, y, r=3.2, dolu=False):
        dolgu = TG_RENK["olcu"] if dolu else "none"
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{dolgu}" stroke="{TG_RENK["olcu"]}" '
                f'stroke-width="{TG_KALINLIK["olcu"]}"/>')

    @staticmethod
    def genislik(metin, boy=TG_YAZI):
        """Yazının tuval birimindeki yaklaşık genişliği (yerleşim ve denetim için)."""
        return len(metin) * boy * 0.56

    def _yazi(self, x, y, metin, boy=TG_YAZI, hiza="middle", kalin=False, yer="etiket"):
        self.yazi_sayisi += 1
        w = self.genislik(metin, boy)
        x0 = x - w / 2 if hiza == "middle" else (x if hiza == "start" else x - w)
        self.yazi_kutulari.append((x0, y - boy * 0.72, x0 + w, y + boy * 0.22, metin, y, yer))   # taban, yer: baslik/not/etiket
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{boy}" fill="{TG_RENK["olcu"]}" '
                f'text-anchor="{hiza}"{" font-weight=\'600\'" if kalin else ""}>{_html.escape(metin)}</text>')

    # ── üç yazı yeri: başlık, not, ölçü/işaret etiketi ──
    def baslik(self, metin, t=0.0):
        """Üst şerit (y ∈ [0, 16])."""
        self.belir(self._yazi(TG_TUVAL[0] / 2, 11, metin, TG_BASLIK_YAZI, kalin=True, yer="baslik"), t, tur="isaret")

    def baslik_nobet(self, varsayilan, pencereler):
        """
        Başlık yuvasında nöbetleşe yazı (Paket 25): `varsayilan` pencereler dışında, her (metin, t0, t1)
        penceresinde onun yerine `metin` görünür; pencere bitince başlık geri gelir. Yeni yazı yeri açmaz: yazı
        sayısında ve yerleşim denetiminde TEK yazıdır (en geniş metnin kutusu). self.yuva: denetim için kayıt.
        """
        sayi, k0 = self.yazi_sayisi, len(self.yazi_kutulari)
        xml = [self._yazi(TG_TUVAL[0] / 2, 11, m, TG_BASLIK_YAZI, kalin=True, yer="baslik")
               .replace("<text ", '<text data-yuva="baslik" ', 1)
               for m in [varsayilan] + [p[0] for p in pencereler]]
        kutular = self.yazi_kutulari[k0:]
        del self.yazi_kutulari[k0:]
        self.yazi_kutulari.append(max(kutular, key=lambda k: k[2] - k[0]))
        self.yazi_sayisi = sayi + 1
        self.yuva = {"varsayilan": varsayilan, "pencereler": [tuple(p) for p in pencereler]}
        araliklar = sorted((a, b) for _, a, b in pencereler)
        disari, t = [], 0.0
        for a, b in araliklar:
            if a > t + 1e-9:
                disari.append((t, a))
            t = max(t, b)
        if t < 1 - 1e-9:
            disari.append((t, 1.0))
        for parca, ara in [(xml[0], disari)] + [(x, [(a, b)]) for x, (_, a, b) in zip(xml[1:], pencereler)]:
            self._nobet(parca, ara)

    def _nobet(self, xml, araliklar):
        """xml yalnız araliklar [(t0, t1)] içinde görünür (kesikli opaklık); durağan kopyada sonda görünüyorsa var."""
        zam, deg = [0.0], ["1" if araliklar and araliklar[0][0] <= 1e-9 else "0"]
        for a, b in araliklar:
            if a > 1e-9:
                zam.append(a)
                deg.append("1")
            if b < 1 - 1e-9:
                zam.append(b)
                deg.append("0")
        self._kaydet(xml, "isaret")
        a = _tg_anim("opacity", deg, zam, self.sure).replace('calcMode="linear"', 'calcMode="discrete"')
        sonda = bool(araliklar) and araliklar[-1][1] >= 1 - 1e-9
        self.ogeler.append((f'<g opacity="{deg[0]}">{a}{xml}</g>', xml if sonda else ""))

    def not_(self, metin, t=0.0):
        """Alt şerit (y ∈ [128, 140])."""
        self.belir(self._yazi(TG_TUVAL[0] / 2, 137.5, metin, yer="not"), t, tur="isaret")

    def olcu(self, x1, y1, x2, y2, etiket=None, uc="son", t=0.0, kilavuzlar=(), metre=None, es=None, bag=(),
             etiket_yer="uc", etiket_dx=0):
        """
        Ölçü oku (iki uçlu) + etiket okun bir ucunda. kilavuzlar: [(x1, y1, x2, y2)] kesik kılavuzlar.
        metre: protokoldeki mesafe (ölçek tablosuyla karşılaştırılır). es: etiketsiz ok yalnız etiketli bir
        okun simetrik eşi olabilir (o okun sırası).
        etiket_yer: "uc" (yatay ok: ucun yanında) ya da "orta" (okun ortasında, üstte; etiket_dx ile kaydırılır —
        figür/eşya payı için). Dikey okta etiket ("sol" verilirse solda)
        her zaman okun yanında, ortadadır (sağda; sığmazsa solda).
        bag: [(uç, eksen, eklemler, kural)] — okun bir ucu ölçülen figürün son karesindeki eklemden gelir
        (ör. (1, "y", ("ayak1", "ayak2"), "max") = ikinci ucun y'si en alttaki ayak). Denetim ≤ 2 birim ister.
        """
        self.olculer.append((x1, y1, x2, y2))
        self.olcu_kayit.append({"uc": (x1, y1, x2, y2), "etiket": etiket, "metre": metre, "es": es,
                                "bag": tuple(bag)})
        xml = "".join(self.cizgi(*k, tur="olcu", kesik=True) for k in kilavuzlar)
        xml += self.cizgi(x1, y1, x2, y2, "olcu", ok=True)
        if etiket:
            qx, qy, rx, ry = (x2, y2, x1, y1) if uc == "son" else (x1, y1, x2, y2)
            w = self.genislik(etiket)
            if abs(qx - rx) >= abs(qy - ry) and etiket_yer == "orta":
                xml += self._yazi((x1 + x2) / 2 + etiket_dx, (y1 + y2) / 2 - 5, etiket, kalin=True)
            elif abs(qx - rx) >= abs(qy - ry):      # yatay ok: etiket ucun yanında; sığmazsa ucun üstünde
                sag = qx > rx
                taban = min(qy + 3, TG_SERIT_ALT - 2)
                if (sag and qx + 11 + w <= TG_TUVAL[0] - TG_YAZI_PAYI) or (not sag and qx - 11 - w >= TG_YAZI_PAYI):
                    xml += self._yazi(qx + (11 if sag else -11), taban, etiket, hiza="start" if sag else "end", kalin=True)
                else:
                    xml += self._yazi(qx, qy - 5, etiket, hiza="end" if sag else "start", kalin=True)
            else:                                    # dikey ok: etiket okun yanında, ortada
                orta_y = (y1 + y2) / 2 + 3
                if etiket_yer != "sol" and x1 + 7 + w <= TG_TUVAL[0] - TG_YAZI_PAYI:
                    xml += self._yazi(x1 + 7, orta_y, etiket, hiza="start", kalin=True)
                else:
                    xml += self._yazi(x1 - 7, orta_y, etiket, hiza="end", kalin=True)
        self.belir(xml, t, tur="isaret")

    def isaret(self, etiket, hedef, yazi_xy, hiza="middle", t=0.0):
        """Etiket, ince kesik kılavuzla gösterdiği noktaya bağlı (serbest yazı yok)."""
        hx_, hy_ = hedef
        yx, yy = yazi_xy
        w = self.genislik(etiket)
        if hiza == "start":
            yx = min(yx, TG_TUVAL[0] - TG_YAZI_PAYI - w)
        elif hiza == "end":
            yx = max(yx, TG_YAZI_PAYI + w)
        bag_y = yy + 3 if hy_ > yy else yy - 9
        xml = (self.cizgi(yx, bag_y, hx_, hy_, "kilavuz") + self.nokta(hx_, hy_, 1.8, dolu=True)
               + self._yazi(yx, yy, etiket, hiza=hiza, kalin=True))
        self.belir(xml, t, tur="isaret")

    # ── zamanlı öğeler ──
    def belir(self, xml, t, t2=None, tur="esya"):
        """xml grubu t anında (0-1) belirir ve kalır; t = 0 ise baştan görünür."""
        if t <= 0:
            self.esya(xml, tur)
            return
        self._kaydet(xml, tur)
        t2 = min(1.0, t + 0.06) if t2 is None else t2
        a = _tg_anim("opacity", ["0", "0", "1", "1"], [0, t, t2, 1], self.sure)
        self.ogeler.append((f'<g opacity="1">{a}{xml}</g>', f"<g>{xml}</g>"))

    def goster(self, xml, t0, t1=None, tur="esya"):
        """xml grubu [t0, t1) aralığında görünür (t1 yoksa sona kadar). Durağan kopyada yalnız sonda görünen kalır."""
        if t1 is None or t1 >= 1:
            self.belir(xml, t0, min(1.0, t0 + 1e-3) if t0 > 0 else None, tur)
            return
        self._kaydet(xml, tur)
        deg, zam = (["1", "0", "0"], [0, t1, 1]) if t0 <= 0 else (["0", "1", "0", "0"], [0, t0, t1, 1])
        a = _tg_anim("opacity", deg, zam, self.sure).replace('calcMode="linear"', 'calcMode="discrete"')
        self.ogeler.append((f'<g opacity="0">{a}{xml}</g>', ""))

    def sayac(self, x, y, anlar, boy=16):
        """
        Sayaç — TEK biçim (Paket 19): kutu içinde çetele. anlar'daki her anda bir çizgi belirir (beşincisi dördünü
        çapraz keser). Rakam yazmaz: çizilen çetele sayılan şeyi gösterir, sonucun kendisi değildir.
        Döndürür: kutunun (x0, y0, x1, y1).
        """
        n = len(anlar)
        ara = 3.4
        grup = [min(5, n - 5 * g) for g in range((n + 4) // 5)] or [0]
        gen = 6 + sum(min(k, 4) * ara + 4 for k in grup)
        yuk = boy
        self.esya(self.kutu(x, y, gen, yuk, dolgu="yuzey", rx=1.5))
        kal = TG_KALINLIK["olcu"]
        cx, i = x + 5, 0
        for g, k in enumerate(grup):
            gx = cx
            for j in range(k):
                if j < 4:
                    xml = self.cizgi(cx + j * ara, y + 4, cx + j * ara, y + yuk - 4, "olcu")
                else:                                       # beşinci: dördünü çapraz keser
                    xml = self.cizgi(gx - 1.5, y + yuk - 5, gx + 3 * ara + 1.5, y + 5, "olcu")
                self.belir(xml, anlar[i], min(1.0, anlar[i] + 1e-3), tur="isaret")
                i += 1
            cx += min(k, 4) * ara + 4
        self.sayaclar.append((x, y, x + gen, y + yuk))
        return x, y, x + gen, y + yuk

    def kronometre(self, cx, cy, t0=0.0, r=8, t1=None):
        """
        Süre ölçümü simgesi: kadran + düğme; ibre t0'dan sonra döner, t1 verilirse o anda durur (ör. CAMSA: vuruş).
        Rakam yok (değer gösterilmez).
        """
        kal = TG_KALINLIK["olcu"]
        self.esya(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["olcu"]}" '
                  f'stroke-width="{kal}"/>' + self.cizgi(cx, cy - r - 3, cx, cy - r, "olcu")
                  + self.cizgi(cx - 2.5, cy - r - 3, cx + 2.5, cy - r - 3, "olcu"))
        ibre = self.cizgi(cx, cy, cx, cy - r + 2, "olcu")
        m = f"{cx:.1f} {cy:.1f}"
        if t1 is None:
            an = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};720 {m}" '
                  f'keyTimes="0;{t0:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        else:
            an = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};720 {m};720 {m}" '
                  f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        self._kaydet(ibre, "isaret")
        self.ogeler.append((f'<g>{an}{ibre}</g>', f'<g transform="rotate(300 {cx:.1f} {cy:.1f})">{ibre}</g>'))
        self.kronometreler.append((cx - r, cy - r - 3, cx + r, cy + r))
        return cx - r, cy - r - 3, cx + r, cy + r

    def figur_xml(self, e, rol="partner", s=1.0, cephe=False):
        """
        Tek pozluk figürün DURAĞAN çizimi (animasyonsuz), figur() ile aynı katman ve kalınlık kuralları. Kayan
        parkurun içine konur (ör. CAMSA'da topu atan uygulayıcı); sahneye kendisi eklenmez, figür sayılmaz.
        """
        katman_adi = TG_ROL_KATMANI[rol]
        katman = FIGUR_KATMANI[katman_adi]
        renk, opak = tg_renk(katman["renk"]), katman["opaklik"]
        kademe = 1.0 if s >= 0.9 else (0.8 if s >= 0.75 else 0.7)
        olcek = kademe * katman["incelik"]
        kesik = f' stroke-dasharray="{katman["kesik"]}"' if katman["kesik"] else ""
        parca = _tg_parcalar(e)
        xml = ""
        for ad in ("bacak2", "kol2", "govde", "kusak", "bacak1", "kol1"):
            kal = TG_KALINLIK["govde" if ad == "govde" else "figur"] * olcek
            uzak = not (cephe or ad in ("govde", "kusak", "bacak1", "kol1"))
            o = round(opak * (FIGUR_DERINLIK_OPAKLIK if uzak else 1.0), 3)
            soluk = f' stroke-opacity="{o}"' if o < 1 else ""
            xml += (f'<path d="{parca[ad]}" fill="none" stroke="{renk}" stroke-width="{kal:.2f}" stroke-linecap="round" '
                    f'stroke-linejoin="round"{soluk}{kesik} data-katman="{katman_adi}"'
                    + (' data-derinlik="1"' if uzak else "") + "/>")
        bx, by = e["bas"]
        xml += (f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{_TG_BOY["bas"] * s:.1f}" fill="{renk}" data-katman="{katman_adi}"'
                + (f' fill-opacity="{opak}"' if opak < 1 else "") + "/>")
        return xml

    @property
    def bacaklar(self):
        """Tek tek çizilen gidiş-dönüşlerin görünme aralıkları [(t0, t1)] (Spider, Paket 24)."""
        if not hasattr(self, "_bacaklar"):
            self._bacaklar = []
        return self._bacaklar

    def numara(self, x, y, n, t=0.0, t_bitis=None):
        """
        Sıra numarası rozeti (çok dönüşlü parkur): küçük halka içinde çizilmiş rakam — yazı öğesi değildir.
        Sayaçtan ayrı bir şeydir: bir değer değil, sırayı gösterir.
        """
        r, h, w = 4.6, 4.8, 2.6
        xml = (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["olcu"]}" '
               f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
        ox, oy = x - w / 2, y - h / 2
        u = {"a": (0, 0, w, 0), "b": (w, 0, w, h / 2), "c": (w, h / 2, w, h), "d": (0, h, w, h),
             "e": (0, h / 2, 0, h), "f": (0, 0, 0, h / 2), "g": (0, h / 2, w, h / 2)}
        for b in _TG_RAKAM[n % 10]:
            x1, y1, x2, y2 = u[b]
            xml += (f'<line x1="{ox + x1:.1f}" y1="{oy + y1:.1f}" x2="{ox + x2:.1f}" y2="{oy + y2:.1f}" '
                    f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-linecap="round"/>')
        if t_bitis is None:
            self.belir(xml, t, tur="isaret")
        else:                                   # kayan turda o anki istasyonun numarası (yalnız o aralıkta)
            self.goster(xml, t, t_bitis, tur="isaret")
        self.numaralar.append((n, x, y))

    def kaydir(self, xml, anahtarlar, tur="esya"):
        """xml grubunu [(t, dx, dy)] boyunca öteler; son konumda durur."""
        self._kaydet(xml, tur, anahtarlar[-1][1], anahtarlar[-1][2])
        self.kaymalar.append(list(anahtarlar))
        dys = [dy for _, _, dy in anahtarlar]
        self.kayan_kutular += [(x0, y0 + min(dys), x1, y1 + max(dys)) for x0, y0, x1, y1 in _tg_xml_kutulari(xml, 0, 0)]
        kt = ";".join(f"{t:.4f}" for t, _, _ in anahtarlar)
        deg = [f"{dx:.1f} {dy:.1f}" for _, dx, dy in anahtarlar]
        a = (f'<animateTransform attributeName="transform" type="translate" values="{";".join(deg)}" '
             f'keyTimes="{kt}" dur="{self.sure}s" begin="0s" fill="freeze"/>')
        self.ogeler.append((f'<g transform="translate({deg[-1]})">{a}{xml}</g>',
                            f'<g transform="translate({deg[-1]})">{xml}</g>'))

    def top(self, yol, r=4.0, iz=False):
        """yol: [(t, x, y)] — top bu noktalardan geçer ve son noktada kalır. iz=True: uçuş izi kesik çizgi."""
        x0, y0 = yol[0][1], yol[0][2]
        anahtar = [(0.0, 0.0, 0.0)]
        for t, x, y in yol:
            if t > anahtar[-1][0] + 1e-6:
                anahtar.append((t, x - x0, y - y0))
        if anahtar[-1][0] < 1:
            anahtar.append((1.0, anahtar[-1][1], anahtar[-1][2]))
        self.kaydir(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="{r}" fill="{TG_RENK["olcu"]}"/>', anahtar)

    def figur(self, hareket, donus=None):
        """
        Hareket kitaplığından gelen [(t, poz)] anahtarlarıyla figür; son karede durur.
        hareket.olay["rol"] == "partner" (hk_ikinci_figur): daha ince ve soluk çizilir — ölçülen belli olsun.
        """
        anahtarlar = hareket.anahtarlar if hasattr(hareket, "anahtarlar") else hareket
        rol = (hareket.olay.get("rol") if hasattr(hareket, "olay") else None) or "olculen"
        partner = rol in ("partner", "iz")          # iz: aynı sporcunun başlangıç pozu, daha da soluk (Paket 17)
        kareler = _tg_kareler(anahtarlar)
        zam = [t for t, _ in kareler]
        eklemler = [tg_eklemler(p) for _, p in kareler]
        self.tum_eklemler += eklemler
        if not partner:
            self.son_eklemler = eklemler[-1]
        katman_adi = TG_ROL_KATMANI[rol]
        katman = FIGUR_KATMANI[katman_adi]
        opak = katman["opaklik"]
        renk = tg_renk(katman["renk"])
        self.figurler.append({"rol": rol, "opaklik": opak, "son": eklemler[-1],
                              "kareler": list(zip(zam, eklemler)),
                              "bas_r": _TG_BOY["bas"] * anahtarlar[-1][1].get("s", 1.0)})
        s_ = anahtarlar[-1][1].get("s", 1.0)
        pay = TG_KALINLIK["govde"] * max(s_, 0.7) / 2

        def alan(e):
            xs = [p[0] for k, p in e.items()] + [e["bas"][0] - _TG_BOY["bas"] * s_, e["bas"][0] + _TG_BOY["bas"] * s_]
            ys = [p[1] for k, p in e.items()] + [e["bas"][1] - _TG_BOY["bas"] * s_, e["bas"][1] + _TG_BOY["bas"] * s_]
            return min(xs) - pay, min(ys) - pay, max(xs) + pay, max(ys) + pay
        self.cizim_kutulari.append((*alan(eklemler[-1]), "figur"))
        son = eklemler[-1]
        for a, b in _TG_FIGUR_CIZGILERI:
            self.cizim_sekilleri.append(("figur", "cizgi", *son[a], *son[b], TG_KALINLIK["figur"] * (1.0 if s_ >= 0.9 else (0.8 if s_ >= 0.75 else 0.7)) / 2))
        self.cizim_sekilleri.append(("figur", "disk", *son["bas"], _TG_BOY["bas"] * s_))
        tum = [alan(e) for e in eklemler]
        self.figur_alani.append((min(a[0] for a in tum), min(a[1] for a in tum),
                                 max(a[2] for a in tum), max(a[3] for a in tum)))
        parcalar = [_tg_parcalar(e) for e in eklemler]
        cephe = anahtarlar[-1][1].get("cephe", False)
        s = anahtarlar[-1][1].get("s", 1.0)
        kademe = 1.0 if s >= 0.9 else (0.8 if s >= 0.75 else 0.7)    # kalınlık yalnız üç kademede (takım)
        olcek = kademe * katman["incelik"]
        kesik = f' stroke-dasharray="{katman["kesik"]}"' if katman["kesik"] else ""
        hareketli, duragan = [], []
        for ad in ("bacak2", "kol2", "govde", "kusak", "bacak1", "kol1"):
            kal = TG_KALINLIK["govde" if ad == "govde" else "figur"] * olcek
            uzak = not (cephe or ad in ("govde", "kusak", "bacak1", "kol1"))
            o = round(opak * (FIGUR_DERINLIK_OPAKLIK if uzak else 1.0), 3)
            soluk = f' stroke-opacity="{o}"' if o < 1 else ""
            ortak = (f'fill="none" stroke="{renk}" stroke-width="{kal:.2f}" stroke-linecap="round" '
                     f'stroke-linejoin="round"{soluk}{kesik} data-katman="{katman_adi}"'
                     + (' data-derinlik="1"' if uzak else ""))
            son = parcalar[-1][ad]
            hareketli.append(f'<path d="{son}" {ortak}>{_tg_anim("d", [pp[ad] for pp in parcalar], zam, self.sure)}</path>')
            duragan.append(f'<path d="{son}" {ortak}/>')
        r = _TG_BOY["bas"] * s
        bx, by = eklemler[-1]["bas"]
        ortak = (f'r="{r:.1f}" fill="{renk}" data-katman="{katman_adi}"'
                 + (f' fill-opacity="{opak}"' if opak < 1 else ""))
        ax = _tg_anim("cx", [f"{e['bas'][0]:.1f}" for e in eklemler], zam, self.sure)
        ay = _tg_anim("cy", [f"{e['bas'][1]:.1f}" for e in eklemler], zam, self.sure)
        hareketli.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" {ortak}>{ax}{ay}</circle>')
        duragan.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" {ortak}/>')
        if donus:      # (t0, t1, cx, cy): figür grubu bu aralıkta (cx, cy) çevresinde 360° döner (öne takla)
            t0, t1, cx, cy = donus
            m = f"{cx:.1f} {cy:.1f}"
            rot = (f'<animateTransform attributeName="transform" type="rotate" values="0 {m};0 {m};360 {m};360 {m}" '
                   f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{self.sure}s" begin="0s" fill="freeze"/>')
            hareketli = [f"<g>{rot}"] + hareketli + ["</g>"]
            self.donusler.append({"t0": t0, "t1": t1, "cx": cx, "cy": cy, "bas_r": _TG_BOY["bas"] * s,
                                  "kareler": [(t, e) for t, e in zip(zam, eklemler) if t0 - 1e-9 <= t <= t1 + 1e-9]})
        self.ogeler.append(("".join(hareketli), "".join(duragan)))
        return eklemler[-1]

    def cubuk(self, x1, y1, yol, tur="esya", kalinlik="vurgu"):
        """(x1, y1)'de sabit, öbür ucu yol [(t, x, y)] boyunca giden çubuk (ör. dinamometre kolu; ince: zincir)."""
        zam = [t for t, _, _ in yol]
        ax = _tg_anim("x2", [f"{x:.1f}" for _, x, _ in yol], zam, self.sure)
        ay = _tg_anim("y2", [f"{y:.1f}" for _, _, y in yol], zam, self.sure)
        _, xs, ys = yol[-1]
        ortak = (f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{xs:.1f}" y2="{ys:.1f}" stroke="{TG_RENK["esya"]}" '
                 f'stroke-width="{TG_KALINLIK[kalinlik]}" stroke-linecap="round"')
        self._kaydet(f"<line {ortak}/>", tur)
        self.ogeler.append((f"<line {ortak}>{ax}{ay}</line>", f"<line {ortak}/>"))
        self.cubuklar.append([(t, x1, y1, x, y) for t, x, y in yol])

    def cubuk_iki(self, yol, tur="esya", kalinlik="esya"):
        """İki ucu da hareketli çubuk: yol [(t, x1, y1, x2, y2)] (ör. çift palalı kürek sapı). Son karede durur."""
        zam = [k[0] for k in yol]
        anim = "".join(_tg_anim(ad, [f"{k[i]:.1f}" for k in yol], zam, self.sure)
                       for i, ad in ((1, "x1"), (2, "y1"), (3, "x2"), (4, "y2")))
        _, a, b, c, d = yol[-1]
        ortak = (f'x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{TG_RENK["esya"]}" '
                 f'stroke-width="{TG_KALINLIK[kalinlik]}" stroke-linecap="round"')
        self._kaydet(f"<line {ortak}/>", tur)
        self.ogeler.append((f"<line {ortak}>{anim}</line>", f"<line {ortak}/>"))
        self.cubuklar.append([tuple(k) for k in yol])

    def yol(self, noktalar, t=0.0):
        """Güzergâh: ince kesik çizgi (hk_kavisli_yol'un olay["yol"] noktaları)."""
        d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(noktalar))
        self.belir(f'<path d="{d}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
                   f'stroke-dasharray="3 2" stroke-linecap="round"/>', t, tur="isaret")

    def svg(self, hareketli=True, etiket="", sinif="tg-svg"):
        if not hareketli and self.duragan is not None:       # bilerek farklı durağan kompozisyon (Paket 21)
            return self.duragan.svg(False, etiket, sinif)
        w, h = TG_TUVAL
        zemin = (f'<line x1="6" y1="{TG_ZEMIN}" x2="{w - 6}" y2="{TG_ZEMIN}" stroke="{TG_RENK["zemin"]}" '
                 f'stroke-width="{TG_KALINLIK["zemin"]}" stroke-linecap="round"/>')
        ic = "".join(a if hareketli else d for a, d in self.ogeler)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" class="{sinif}" role="img" '
                f'aria-label="{_html.escape(etiket)}" font-family="{_html.escape(YAZI_AILESI.replace(chr(34), ""))}">'
                f'<title>{_html.escape(etiket)}</title>{zemin}{ic}</svg>')


# ── 2) HAREKET KİTAPLIĞI ──
# Her fonksiyon TgHareket döndürür: anahtarlar [(t, poz)] (son anahtar = ölçüm anı) ve olay
# (ölçüm için gereken noktalar/zamanlar: ör. tepe yüksekliği, topun bırakıldığı an ve el konumu).
TgHareket = _namedtuple("TgHareket", ["anahtarlar", "olay"])


def _hk_kos_pozu(hx, faz, yon=1, s=1.0, g=12):
    a = dict(u1=38, b1=-2, u2=-32, b2=-80, k1=-38, o1=45, k2=42, o2=115)
    b = dict(u1=-32, b1=-80, u2=38, b2=-2, k1=42, o1=115, k2=-38, o2=45)
    return tg_yerlestir(tg_poz(hx, yon=yon, s=s, g=g, **(a if faz % 2 == 0 else b)))


def _hk_kos_anahtarlari(x0, x1, t0, t1, yon, s, faz0=0):
    adim = max(2, int(abs(x1 - x0) / (26 * s)))
    return [(t0 + (t1 - t0) * i / adim, _hk_kos_pozu(x0 + (x1 - x0) * i / adim, faz0 + i, yon, s)) for i in range(adim + 1)]


def hk_duz_kos(x0, x1, s=1.0, cikis_t=0.12, bitis_x=None):
    """Düz koşu: çıkış duruşunda bekler, x0 → x1 koşar. Son anahtar = bitiş_x çizgisini geçiş (ölçüm anı)."""
    yon = 1 if x1 >= x0 else -1
    cikis = tg_yerlestir(tg_poz(x0, s=s, yon=yon, g=25, u1=20, b1=-8, u2=-10, b2=-25, k1=-30, o1=20, k2=35, o2=90))
    # ilk adım çıkış duruşunun önünde başlar: koşu pozunda geride kalan ayak çıkış çizgisinin gerisine taşmasın
    an = [(0.0, cikis), (cikis_t, cikis)] + _hk_kos_anahtarlari(x0 + yon * 22 * s, x1, cikis_t + 0.03, 1.0, yon, s)
    return TgHareket(an, {"cikis_x": x0, "bitis_x": bitis_x if bitis_x is not None else x1})


def hk_donuslu_kos(duraklar, s=1.0, dokun=True, baslangic="yan", t0=0.0, t1=1.0):
    """
    Dönüşlü koşu: duraklar [x0, x1, x2, ...] arası koşar; ara duraklarda öne eğilip çizgiye elle dokunur
    (dokun=True). olay["dokunma"] = [(t, x)]. Son anahtar = son durağı geçiş.
    """
    an = []
    bolum = len(duraklar) - 1
    dokunma = []
    if baslangic == "yan":
        bas = tg_yerlestir(tg_poz(duraklar[0], s=s, cephe=True, g=10, u1=20, b1=-5, u2=-20, b2=5, a1=90, a2=-90,
                                  k1=25, o1=60, k2=-25, o2=-60))
        an += [(0.0, bas), (0.06, bas)]
        t_bas = 0.08
    else:
        t_bas = 0.0
    sure = (1.0 - t_bas) / bolum
    for i in range(bolum):
        xa, xb = duraklar[i], duraklar[i + 1]
        yon = 1 if xb > xa else -1
        son_bolum = i == bolum - 1
        hedef = xb - yon * (0 if son_bolum else 7 * s)
        # ayak penceresi ta–tb: t0/t1 (hareketin kendi zaman aralığı) parametre olarak korunur. Paket 20'ye dek
        # döngü t0/t1'i eziyor, sondaki yeniden ölçekleme bütün kareleri son ayağın penceresine yığıyordu.
        ta = t_bas + i * sure
        tb = ta + sure * (1.0 if son_bolum or not dokun else 0.8)
        an += _hk_kos_anahtarlari(xa + (0 if i == 0 else yon * 7 * s), hedef, ta + (0.01 if an else 0), tb, yon, s)[(1 if an else 0):]
        if dokun and not son_bolum:
            td = ta + sure
            an.append((td, tg_yerlestir(tg_poz(xb - yon * 2 * s, yon=yon, s=s, g=68, u1=62, b1=-22, u2=10, b2=-30,
                                               k1=-6, o1=-2, k2=30, o2=40))))
            dokunma.append((td, xb))
    if (t0, t1) != (0.0, 1.0):        # başka bir hareketle art arda kullanım için zaman aralığı
        an = [(t0 + (t1 - t0) * t, p) for t, p in an]
        dokunma = [(t0 + (t1 - t0) * t, x) for t, x in dokunma]
    return TgHareket(an, {"dokunma": dokunma})


def hk_dikey_sicrama(x, yukselme=12, s=1.0):
    """
    Kollar serbest aktif sıçrama (TSYT): dur → çök (kollar geride) → kalk (kollar yukarı) → TEPE (ölçüm anı).
    CMJ / SJ / DJ'nin ayırt edici anları için hk_sicrama_ani (Paket 18).
    """
    dur = tg_poz(x, s=s)
    cok = tg_yerlestir(tg_poz(x, s=s, g=35, u1=78, b1=-25, u2=72, b2=-22, k1=-55, o1=-40, k2=-48, o2=-30),
                       ayak_x=tg_eklemler(dur)["ayak1"][0])
    kalk = tg_yerlestir(tg_poz(x, s=s, k1=112, o1=126, k2=102, o2=116))
    tepe = dict(kalk, hy=kalk["hy"] - yukselme, a1=40, a2=36, u2=-6, b2=-4)
    e = tg_eklemler(tepe)
    return TgHareket([(0, dur), (0.12, dur), (0.4, cok), (0.62, kalk), (1.0, tepe)],
                     {"zemin_ayak_y": TG_ZEMIN,
                      "tepe_ayak_y": max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))})


def hk_sicrama_ani(x, kip, s=1.0, kutu=None):
    """
    Sıçrama varyantının AYIRT EDİCİ ANI (Paket 18): son anahtar o andır ve durağan görselde o kalır.
    "cmj": ayakta → ön-çömelmenin en alt noktası (çök-sıçra'nın çök'ü); "sj": 90° diz açısında statik çömelme,
    bekler (ön-çömelme yok); "dj": kutunun üstünden öne iner — düşüş anı (havada, kutu ile zemin arasında).
    Eller kalçada. kutu = (sol_x, sag_x, yükseklik). olay: "kalca", "diz", "ayak" (son kare), "kalca_yolu" (cmj),
    "dusus_yolu" (dj).
    """
    kol = dict(k1=-42, o1=52, k2=-22, o2=70)
    dur = tg_poz(x, s=s, **kol)
    cok = tg_yerlestir(tg_poz(x, s=s, g=30, u1=70, b1=-20, u2=58, b2=-8, k1=-44, o1=-16, k2=-30, o2=-4),
                       ayak_x=tg_eklemler(dur)["ayak1"][0])         # 90° çömelme; gövde eğikken eller kalçada
    olay = {"kip": kip}
    if kip == "cmj":                         # ön-çömelme SJ'nin 90°'sinden derin: iki an durağan karede ayrışsın
        dip_kol = dict(k1=-56, o1=-28, k2=-40, o2=-14)          # gövde öne eğikken de eller kalçada
        dip = tg_yerlestir(tg_poz(x, s=s, g=42, u1=88, b1=-34, u2=80, b2=-22, **dip_kol),
                           ayak_x=tg_eklemler(dur)["ayak1"][0])
        an = [(0, dur), (0.3, dur), (1.0, dip)]
        olay["kalca_yolu"] = (dur["hy"], dip["hy"])
    elif kip == "sj":
        kollar_asagi = dict(cok, k1=8, o1=6, k2=-6, o2=-4)
        an = [(0, kollar_asagi), (0.25, cok), (1.0, cok)]
    else:
        sol, sag, yuk = kutu
        ust = TG_ZEMIN - yuk
        uzerinde = tg_yerlestir(tg_poz((sol + sag) / 2, s=s, **kol), zemin=ust)
        adim = tg_yerlestir(tg_poz(sag + 2 * s, s=s, u1=30, b1=10, u2=-10, b2=-6, **kol), zemin=ust)
        adim["hy"] -= 2 * s
        dusus = tg_yerlestir(tg_poz(sag + 14 * s, s=s, u1=10, b1=6, u2=-6, b2=-2, a1=60, a2=60, **kol),
                             zemin=(ust + TG_ZEMIN) / 2)
        an = [(0, uzerinde), (0.3, uzerinde), (0.6, adim), (1.0, dusus)]
        e0, e1 = tg_eklemler(uzerinde), tg_eklemler(dusus)
        olay["dusus_yolu"] = (e0["ayak1"], e1["ayak1"], (e1["ayak1"][0] + 4 * s, TG_ZEMIN))
    e = tg_eklemler(an[-1][1])
    olay.update({"kalca": e["kalca"], "diz": e["diz1"], "ayak": e["ayak1"]})
    return TgHareket(an, olay)


def hk_yana_sicrama(x_sol, x_sag, sicrama=6, s=1.0):
    """Çift ayakla yana sıçrama (önden); son anahtar havada, çıtanın üstünde (sayılan an)."""
    on = dict(cephe=True, u1=4, b1=4, u2=-4, b2=-4, a1=90, a2=-90, k1=35, o1=80, k2=-35, o2=-80, s=s)
    orta = (x_sol + x_sag) / 2
    an = []
    for i in range(sicrama):
        x = x_sol if i % 2 == 0 else x_sag
        yer = tg_poz(x, **on)
        an.append((i / sicrama, yer))
    son_hava = tg_poz(orta, **on)
    son_hava = dict(son_hava, hy=son_hava["hy"] - 10, u1=10, b1=-2, u2=-10, b2=2, k1=50, o1=95, k2=-50, o2=-95)
    an.append((1.0, son_hava))
    return TgHareket(an, {"orta": orta})


def hk_tek_ayak_sekme(x0, engel_x, sekme_sonra=2, adim=14, yukselme=22, s=1.0, ayak="1"):
    """
    Tek ayak sekme: yaklaş, engelin üstünden geç (yüksek), inişten sonra aynı ayakla `sekme_sonra` sıçrama.
    Diğer ayak kalkık kalır. olay["iz"]: engel üstünden geçişin yolu (kesik iz için).
    engel_x=None: engel yok, x0'dan `sekme_sonra` sekme (ör. çember dizisi). ayak: destek ayağı ("1" yakın, "2" uzak).
    """
    d, k = ("1", "2") if ayak in ("1", "cift") else ("2", "1")       # d: destek, k: kalkık bacak
    kalkik = {"u" + k: 55, "b" + k: -70, "k1": 30, "o1": 60, "k2": -25, "o2": 20}
    yer = lambda x: tg_poz(x, s=s, **kalkik)
    hava = lambda x, h: dict(yer(x), hy=yer(x)["hy"] - h, **{"u" + d: 15, "b" + d: -15})
    if ayak == "cift":          # çift ayak sıçrama (CAMSA 1): iki ayak birlikte, inişte dizler bükük, havada toplanır
        yer = lambda x: _hk_uclari_ayir(tg_yerlestir(tg_poz(x, s=s, g=16, u1=30, b1=-16, u2=26, b2=-20,
                                                             k1=-40, o1=-20, k2=-34, o2=-14)))
        hava = lambda x, h: dict(_hk_uclari_ayir(tg_poz(x, s=s, g=8, u1=50, b1=-6, u2=46, b2=-10,
                                                         k1=60, o1=80, k2=54, o2=74)),
                                 hy=yer(x)["hy"] - h)
    if engel_x is None:
        an, x = [(0, yer(x0))], x0
        for i in range(sekme_sonra):
            an += [((i + 0.5) / sekme_sonra, hava(x + adim / 2, yukselme)), ((i + 1) / sekme_sonra, yer(x + adim))]
            x += adim
        return TgHareket(an, {"iz": [], "inisler": [x0 + adim * (i + 1) for i in range(sekme_sonra)]})
    inis = engel_x + 2 * adim
    an = [(0, yer(x0)), (0.14, yer(engel_x - 2 * adim)), (0.3, hava(engel_x, yukselme)), (0.44, yer(inis))]
    x = inis
    for i in range(sekme_sonra):
        t0 = 0.44 + (i + 0.5) * 0.56 / sekme_sonra
        an += [(t0, hava(x + adim / 2, 8)), (0.44 + (i + 1) * 0.56 / sekme_sonra, yer(x + adim))]
        x += adim
    iz = [tg_eklemler(p)["ayak" + d] for p in (yer(engel_x - 2 * adim), hava(engel_x, yukselme), yer(inis))]
    return TgHareket(an, {"iz": iz})


def hk_atma(x, tur="geriye", yon=1, s=1.0, tekrar=2, on_ayak_x=None):
    """
    Atma. tur="geriye": topu önde tutar, hafif çöker, gövdeyi gererek baş üzerinden geriye bırakır
    (ölçüm anı = bırakma; figür bırakma pozunda durur). tur="duvara": göğüs önünden at, yakala.
    tur="suplex": manken geriye köprüyle baş üstünden; tur="one": sporcu mankene sırtını döner, öne eğilir,
    manken sırtının üstünden öne devrilir (iki güreş atışı ayrı hareketlerdir). `tekrar`: atış sayısı.
    olay["birakma_t"], olay["el"] = bırakma anında el; olay["el_yolu"] = bırakmaya kadar el konumları.
    """
    if tur == "suplex":
        return _hk_suplex(x, tekrar=tekrar, s=s)
    if tur == "one":
        return _hk_one_devirme(x, tekrar=tekrar, s=s)
    if tur == "ileri":                                    # iki elle baş üzerinden ileri fırlatma (Latorre)
        p0 = tg_poz(x, yon=yon, s=s, k1=20, o1=40, k2=14, o2=34)
        p1 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=-22, u1=6, b1=-4, u2=-14, b2=-6, k1=176, o1=-150, k2=170, o2=-156))
        p2 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=14, u1=16, b1=2, u2=-18, b2=-8, k1=120, o1=112, k2=104, o2=96))
        an = [(0, p0), (0.15, p0), (0.42, p1), (0.6, p2), (1.0, p2)]
        el_yolu = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an) if t <= 0.6 + 1e-9]
        return TgHareket(an, {"birakma_t": 0.6, "el": tg_eklemler(p2)["el1"], "el_yolu": el_yolu,
                              "tut": tg_eklemler(p2)["el1"]})
    if tur == "geriye":
        p0 = tg_poz(x, yon=yon, s=s, k1=25, o1=40, k2=18, o2=34)
        p1 = tg_yerlestir(tg_poz(x, yon=yon, s=s, g=22, u1=42, b1=-28, u2=36, b2=-24, k1=8, o1=25, k2=2, o2=18))
        p2 = tg_poz(x, yon=yon, s=s, g=-16, k1=150, o1=166, k2=138, o2=154, a1=118, a2=112)
        an = [(0, p0), (0.15, p0), (0.38, p1), (0.6, p2), (1.0, p2)]
        t_b = 0.6
    else:   # duvara at - yakala (on_ayak_x: en öndeki ayak ucu bu x'te durur — ör. duvardan 1 m)
        if on_ayak_x is not None:
            e = tg_eklemler(tg_poz(x, s=s, yon=yon))
            x += on_ayak_x - max(e[k][0] * yon for k in ("ayak1", "ayak2", "parmak1", "parmak2")) * yon
        tut = tg_poz(x, s=s, yon=yon, k1=95, o1=120, k2=78, o2=105)
        at = tg_poz(x, s=s, yon=yon, k1=150, o1=125, k2=78, o2=105)
        an = [(0, tut), (0.12, at), (0.42, tut), (0.54, at), (1.0, tut)]
        t_b = 0.12
    el_yolu = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an) if t <= t_b + 1e-9]
    return TgHareket(an, {"birakma_t": t_b, "el": tg_eklemler(dict(an[-1][1]) if tur == "geriye" else an[0][1])["el1"],
                          "el_yolu": el_yolu, "tut": tg_eklemler(an[-1][1])["el1"]})


def hk_kavrama(x, s=1.0):
    """El kavrama: aleti göğüs önünden indirir, kol gergin ve aşağıda SIKAR (ölçüm anı: parmaklar kapanır)."""
    p0 = tg_poz(x, s=s, k1=45, o1=150)
    p1 = tg_poz(x, s=s, k1=10, o1=8)
    p2 = dict(p1, k1=11, o1=11)
    return TgHareket([(0, p0), (0.12, p0), (0.5, p1), (0.75, p1), (1.0, p2)], {"el": tg_eklemler(p2)["el1"]})


def hk_oturarak_uzanma(ayak_x, s=1.0, egim=50, tek_bacak=False):
    """
    Bacaklar gergin oturuş; kalçadan bükülüp iki kolla öne uzanır, EN UZAK noktada durur.
    tek_bacak=True (Back-Saver): yalnız yakın bacak düz ve kutuda; uzak bacak dizden bükülü, ayak tabanı yerde.
    """
    hx = ayak_x - (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s - 1
    # uzak bacak yerde, yakın bacak hafif yukarıda (yandan bakışta iki ayak tabanı da sehpaya dayalı, üst üste değil)
    temel = dict(hy=TG_ZEMIN - 5, u1=90, b1=90, u2=84, b2=84, a1=180, a2=172, s=s)
    if tek_bacak:
        temel.update(u2=140, b2=26, a2=80)
    p0 = tg_poz(hx, g=0, k1=30, o1=60, k2=20, o2=48, **temel)
    p1 = tg_poz(hx, g=egim, k1=96, o1=94, k2=86, o2=78, **temel)
    return TgHareket([(0, p0), (0.2, p0), (0.8, p1), (1.0, p1)], {"el": tg_eklemler(p1)["el1"]})


def hk_denge(tur="kiris_geriye", x0=60, x1=170, taban=None, adim=6, s=1.0):
    """
    Denge. tur="kiris_geriye": kirişte geriye yürüme (yüz bir yöne, ilerleme ters yöne), kollar yanda;
    tur="kiris_ileri": kirişte öne yürüme.
    tur="platform": iki platform arasında yana geçiş — olay["platform"] platformun öteleme anahtarları.
    """
    if tur in ("kiris_geriye", "kiris_ileri"):           # ileri: yüz ilerleme yönünde (KMS balans)
        taban = TG_ZEMIN if taban is None else taban
        an = []
        for i in range(adim + 1):
            f = 1 if i % 2 else -1
            p = tg_poz(x0 + (x1 - x0) * i / adim, yon=-1 if tur == "kiris_geriye" else 1, s=s, u1=12 * f, b1=6 * f,
                       u2=-12 * f, b2=-6 * f, k1=72, o1=84, k2=-64, o2=-78)
            an.append((i / adim, tg_yerlestir(p, zemin=taban)))
        return TgHareket(an, {"adimlar": [x0 + (x1 - x0) * i / adim for i in range(adim + 1)]})
    taban = TG_ZEMIN - 7 if taban is None else taban
    on = dict(cephe=True, u1=5, b1=5, u2=-6, b2=-5, a1=90, a2=-90, k1=20, o1=18, k2=-22, o2=-18, s=s)
    a, b_, c = (tg_yerlestir(tg_poz(x, **on), zemin=taban) for x in (x0, x0 + 30, x0 + 60))
    egil = dict(b_, g=-35, k1=-30, o1=-26, k2=-50, o2=-46, u1=20, b1=-10, u2=10, b2=-15)
    egil = tg_yerlestir(egil, zemin=taban)
    an = [(0, a), (0.15, a), (0.32, b_), (0.45, egil), (0.62, dict(b_, k1=60, o1=60)), (1.0, c)]
    return TgHareket(an, {"platform": [(0, 0, 0), (0.42, 0, 0), (0.52, 15, -30), (0.62, 60, 0), (1, 60, 0)]})


def hk_antropometri(x, tur="ayakta", oturak_y=None, s=1.0):
    """
    Ayakta antropometri. tur="ayakta": dik duruş (boy); "oturarak": dizler 90° oturuş (oturma yüksekliği);
    "kulac": önden, kollar aşağıdan yere paralel açılır. Son anahtar = ölçüm anı.
    """
    if tur == "ayakta":
        p = tg_poz(x, s=s)
        return TgHareket([(0, p), (1, p)], {"bas_ust": tg_eklemler(p)["bas"][1] - _TG_BOY["bas"] * s})
    if tur == "oturarak":
        p = tg_poz(x, s=s, hy=oturak_y, u1=90, b1=0, u2=82, b2=-8, k1=24, o1=64, k2=16, o2=56)
        return TgHareket([(0, p), (1, p)], {"bas_ust": tg_eklemler(p)["bas"][1] - _TG_BOY["bas"] * s})
    p0 = tg_poz(x, s=s, cephe=True, u1=5, b1=5, u2=-5, b2=-5, a1=90, a2=-90, k1=10, o1=6, k2=-10, o2=-6)
    p1 = dict(p0, k1=90, o1=90, k2=-90, o2=-90)
    return TgHareket([(0, p0), (0.15, p0), (0.6, p1), (1, p1)], {"eller": (tg_eklemler(p1)["el2"], tg_eklemler(p1)["el1"])})


def hk_iz(hareket, sira=0, dx=0.0):
    """
    Hareketin bir anahtar pozunu (varsayılan: başlangıç) sabit, çok soluk bir iz olarak verir: durağan görselde
    hareketin nereden başladığı görünür (CMJ ayakta, SJ çömelik, DJ kutunun üstünde başlar). Ölçülen figür değildir.
    """
    p = dict(hareket.anahtarlar[sira][1])
    p["hx"] += dx                                   # dx: hareketin gerisine kaydırılmış iz (art arda okunsun)
    return TgHareket([(0.0, p), (1.0, p)], {"rol": "iz"})


def hk_ikinci_figur(hareket, rol="partner"):
    """
    Aynı sahnede ikinci figür (partner, manken, rakip). Ölçülen sporcu normal kalınlıkta ve tam opak;
    ikinci figür GÖRSEL SİSTEM'deki "ikinci_kisi" katmanıyla (ayrı renk tonu, ince) çizilir. Temas (tutuş, atış)
    için iki figürün anahtarları aynı zamanlarla kurulur; eller ve kalçalar aynı noktaya getirilebilir.
    """
    anahtarlar = hareket.anahtarlar if hasattr(hareket, "anahtarlar") else hareket
    olay = dict(hareket.olay) if hasattr(hareket, "olay") else {}
    olay["rol"] = rol
    return TgHareket(anahtarlar, olay)


def _hk_catmull(noktalar, n=10):
    """Noktalardan geçen yumuşak eğri (Catmull-Rom)."""
    p = [noktalar[0]] + list(noktalar) + [noktalar[-1]]
    cikti = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for j in range(n):
            t = j / n
            cikti.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                      + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    cikti.append(tuple(noktalar[-1]))
    return cikti


def hk_kavisli_yol(noktalar, s=0.5, kip="kos", yumusak=True, t0=0.0, t1=1.0, baslangic=None, dokun=()):
    """
    Düz olmayan güzergâh (zemin düzleminde): viraj, S çizgisi, köşe dönüşü, çeviklik parkuru. noktalar: [(x, y)]
    geçiş noktaları — y zemindeki derinliktir; figürün ayakları bu noktada durur. yumusak=False: köşeli yol.
    kip="kos" ya da "paten". baslangic="yuzustu": ilk noktada yüzüstü yatar, kalkıp koşar (Illinois).
    dokun: bu sıradaki noktalarda öne eğilip yere elle dokunur (VAT köşeleri). olay["yol"]: kesik çizgi noktaları,
    olay["dokunma"]: [(t, x, y)].
    """
    if baslangic == "yuzustu":
        t_bas = t0 + 0.12 * (t1 - t0)
        ilk = TgHareket([], {})
        x0, y0 = noktalar[0]
        yon0 = 1 if noktalar[1][0] >= x0 else -1
        yat = tg_poz(x0 - yon0 * 24 * s, s=s, yon=yon0, g=88, u1=-88, b1=-90, u2=-92, b2=-94, a1=0, a2=4,
                     k1=8, o1=70, k2=-4, o2=62)
        yat = dict(yat, hy=y0 - 3 * s)
        alt = hk_kavisli_yol(noktalar, s, kip, yumusak, t_bas, t1, None, dokun)
        return TgHareket([(t0, yat), (t0 + 0.05 * (t1 - t0), yat)] + alt.anahtarlar, alt.olay)
    yol = _hk_catmull(noktalar) if yumusak else list(noktalar)
    uz = [0.0]
    for a, b in zip(yol, yol[1:]):
        uz.append(uz[-1] + _math.dist(a, b))
    adim = 20 * s
    sayi = max(2, int(uz[-1] / adim))
    an, yon = [], 1
    for i in range(sayi + 1):
        hedef = uz[-1] * i / sayi
        j = max(0, min(len(yol) - 2, next((k for k in range(len(uz) - 1) if uz[k + 1] >= hedef), len(yol) - 2)))
        f = (hedef - uz[j]) / ((uz[j + 1] - uz[j]) or 1)
        x = yol[j][0] + (yol[j + 1][0] - yol[j][0]) * f
        y = yol[j][1] + (yol[j + 1][1] - yol[j][1]) * f
        dx = yol[j + 1][0] - yol[j][0]
        if abs(dx) > 0.3:
            yon = 1 if dx > 0 else -1
        p = _hk_paten_pozu(x, i, yon, s) if kip == "paten" else _hk_kos_pozu(x, i, yon, s)
        an.append((t0 + (t1 - t0) * i / sayi, tg_yerlestir(p, zemin=y)))
    dokunma = []
    for j in dokun:                          # en yakın kareyi o noktada yere dokunma pozuyla değiştir
        nx, ny = noktalar[j]
        i = min(range(len(an)), key=lambda k: _math.dist((an[k][1]["hx"], tg_eklemler(an[k][1])["ayak1"][1]), (nx, ny)))
        yon_i = an[i][1].get("yon", 1)
        an[i] = (an[i][0], tg_yerlestir(tg_poz(nx - yon_i * 6 * s, yon=yon_i, s=s, g=68, u1=62, b1=-22, u2=10, b2=-30,
                                                k1=-6, o1=-2, k2=30, o2=40), zemin=ny))
        dokunma.append((an[i][0], nx, ny))
    return TgHareket(an, {"yol": yol, "dokunma": dokunma})


def _hk_paten_pozu(hx, faz, yon=1, s=1.0):
    """Paten süzülme pozu: gövde öne eğik, destek dizi bükük, iten bacak geride-yanda gergin."""
    a = dict(g=40, u1=38, b1=-18, u2=-52, b2=-64, a2=150, k1=-34, o1=6, k2=58, o2=82)
    b = dict(g=40, u2=38, b2=-18, u1=-52, b1=-64, a1=150, k2=-34, o2=6, k1=58, o1=82)
    return tg_yerlestir(tg_poz(hx, yon=yon, s=s, **(a if faz % 2 == 0 else b)))


def hk_paten(x0, x1, s=1.0, cikis_t=0.1, adim=None):
    """
    Buz üstü kayma adımı: durarak başlangıç (çömelik), sonra iten bacak geride-yanda gerilir ve uzun süzülme
    (aynı poz ilerler), ardından bacak değişir. Son anahtar = x1 (bitiş çizgisini geçiş — ölçüm anı).
    Zemin çizgisi değişmez; yalnız hareket farklıdır.
    """
    yon = 1 if x1 >= x0 else -1
    adim = adim or 34 * s
    cikis = tg_yerlestir(tg_poz(x0, s=s, yon=yon, g=42, u1=55, b1=-25, u2=40, b2=-30, k1=-20, o1=20, k2=40, o2=70))
    an = [(0.0, cikis), (cikis_t, cikis)]
    sayi = max(2, int(abs(x1 - x0) / adim))
    for i in range(sayi):
        ta = cikis_t + (1 - cikis_t) * i / sayi
        tb = cikis_t + (1 - cikis_t) * (i + 0.75) / sayi
        xa = x0 + (x1 - x0) * i / sayi + yon * (30 if i == 0 else 8) * s   # ilk itiş çıkışın önünde
        xb = x0 + (x1 - x0) * (i + 0.75) / sayi
        an += [(ta + 0.01, _hk_paten_pozu(xa, i, yon, s)), (tb, _hk_paten_pozu(xb, i, yon, s))]   # it + süzül
    an.append((1.0, _hk_paten_pozu(x1, sayi, yon, s)))
    return TgHareket(an, {"cikis_x": x0, "bitis_x": x1})


def _hk_suplex(x, tekrar=2, s=1.0, mesafe=22):
    """
    Güreş atışı (suplex): sporcu mankeni belinden kavrar, kaldırır, gövdesini geriye gererek mankeni başının
    üstünden arkasına sırtüstü devirir. `tekrar` atış; son anahtar = son atışın tamamlandığı an (sayılan an).
    Manken hk_ikinci_figur ile soluk çizilir; kavrama karesinde sporcunun elleri mankenin kalçasındadır.
    """
    xm = x + mesafe
    dur = tg_poz(x, s=s, k1=40, o1=70, k2=30, o2=60)
    kavra = tg_yerlestir(tg_poz(x, s=s, g=15, u1=38, b1=-22, u2=30, b2=-24, k1=25, o1=40, k2=18, o2=34))
    kaldir = tg_yerlestir(tg_poz(x, s=s, g=-30, u1=28, b1=-32, u2=20, b2=-30, k1=150, o1=170, k2=140, o2=160))
    bitir = tg_yerlestir(tg_poz(x + 4, s=s, g=-12, u1=20, b1=-20, u2=10, b2=-22, k1=95, o1=112, k2=80, o2=100))
    m_dur = tg_poz(xm, s=s, yon=-1, k1=55, o1=80, k2=45, o2=72)
    m_kavra = tg_poz(xm - 2, s=s, yon=-1, g=10, k1=60, o1=85, k2=50, o2=78)
    m_havada = dict(tg_poz(x + 2, s=s, yon=-1, g=95, u1=-35, b1=-45, u2=-25, b2=-40, k1=150, o1=150, k2=140, o2=140),
                    hy=TG_ZEMIN - 60 * s)
    m_yerde = dict(tg_poz(x - 40 * s, s=s, yon=-1, g=92, u1=-150, b1=-70, u2=-140, b2=-80, k1=160, o1=170, k2=150, o2=160),
                   hy=TG_ZEMIN - 7 * s)
    a_an, m_an = [], []
    pay = 1.0 / tekrar
    sayac = []
    for i in range(tekrar):
        b = i * pay
        a_an += [(b, dur), (b + 0.18 * pay, kavra), (b + 0.5 * pay, kaldir), (b + 0.85 * pay, bitir)]
        m_an += [(b, m_dur), (b + 0.18 * pay, m_kavra), (b + 0.5 * pay, m_havada), (b + 0.85 * pay, m_yerde)]
        sayac.append(b + 0.85 * pay)
    a_an.append((1.0, bitir))
    m_an.append((1.0, m_yerde))
    temas = (tg_eklemler(kavra)["el1"], tg_eklemler(m_kavra)["kalca"])
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an, "partner"), "atis_anlari": sayac, "temas": temas})


def _hk_ayna(p, merkez):
    """Pozun x = merkez çevresinde aynası (yön döner; açılar yöne göre tanımlı olduğu için değişmez)."""
    return dict(p, hx=2 * merkez - p["hx"], yon=-p.get("yon", 1))


def _hk_one_pozlari(x, s=1.0, mesafe=22):
    """Öne devirmenin anahtar pozları: sporcu x'te sağa bakar, manken x + mesafe'de sola bakar."""
    xm = x + mesafe
    return {
        "dur": tg_poz(x, s=s, k1=40, o1=70, k2=30, o2=60),
        "gir": tg_yerlestir(tg_poz(x + 12 * s, s=s, yon=-1, g=22, u1=30, b1=-18, u2=22, b2=-24,
                                   k1=-150, o1=-110, k2=-135, o2=-95)),
        "yukle": tg_yerlestir(tg_poz(x + 10 * s, s=s, yon=-1, g=62, u1=48, b1=-14, u2=36, b2=-22,
                                     k1=-60, o1=-20, k2=-48, o2=-12)),
        "bitir": tg_yerlestir(tg_poz(x + 6 * s, s=s, yon=-1, g=52, u1=40, b1=-16, u2=-20, b2=-34,
                                     k1=40, o1=20, k2=26, o2=8)),
        "m_dur": tg_poz(xm, s=s, yon=-1, k1=55, o1=80, k2=45, o2=72),
        "m_gir": tg_poz(xm - 4 * s, s=s, yon=-1, g=24, k1=60, o1=85, k2=50, o2=78),
        "m_ucus": dict(tg_poz(x + 4 * s, s=s, yon=-1, g=150, u1=160, b1=170, u2=150, b2=165,
                              k1=-40, o1=-20, k2=-30, o2=-10), hy=TG_ZEMIN - 50 * s),
        "m_yerde": dict(tg_poz(x - 22 * s, s=s, yon=1, g=-92, u1=88, b1=92, u2=84, b2=96,
                               k1=-100, o1=-95, k2=-108, o2=-100), hy=TG_ZEMIN - 7 * s),
    }


def _hk_one_devirme(x, tekrar=2, s=1.0, mesafe=22):
    """
    Öne devirme: sporcu mankene sırtını dönerek içeri girer (yön değişir), kollarıyla mankeni omzunun üstünden
    kavrar, öne eğilip mankeni sırtının üstünden önüne sırtüstü devirir. Son anahtar = atışın tamamlandığı an.
    Suplex'ten ayrımı: bitişte sporcu öne eğik ve atış yönüne bakar; manken önüne düşer.
    """
    P = _hk_one_pozlari(x, s, mesafe)
    dur = P["dur"]
    gir, yukle, bitir = P["gir"], P["yukle"], P["bitir"]
    m_dur, m_gir, m_ucus, m_yerde = P["m_dur"], P["m_gir"], P["m_ucus"], P["m_yerde"]
    a_an, m_an, sayac = [], [], []
    pay = 1.0 / tekrar
    for i in range(tekrar):
        b = i * pay
        a_an += [(b, dur), (b + 0.2 * pay, gir), (b + 0.5 * pay, yukle), (b + 0.85 * pay, bitir)]
        m_an += [(b, m_dur), (b + 0.2 * pay, m_gir), (b + 0.5 * pay, m_ucus), (b + 0.85 * pay, m_yerde)]
        sayac.append(b + 0.85 * pay)
    a_an.append((1.0, bitir))
    m_an.append((1.0, m_yerde))
    temas = (tg_eklemler(gir)["el1"], tg_eklemler(m_gir)["boyun"])
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an, "partner"), "atis_anlari": sayac, "temas": temas})


def hk_pedal(x, s=1.0, tur=4):
    """
    Bisiklet ergometresinde oturarak pedal çevirme. Kalça selede sabit; ayaklar krank çemberinde döner
    (iki bacak yarım tur farkla), diz öne bakar (iki parçalı ters kinematik). Gövde öne eğik, eller gidonda.
    olay: "krank" (merkez), "sele", "gidon", "r" (krank yarıçapı). Son anahtar = 30 sn'nin sonu.
    """
    hx, hy = x, TG_ZEMIN - 50 * s
    cx, cy = hx + 8 * s, hy + 30 * s
    r = 7.5 * s
    L1, L2 = _TG_BOY["uyluk"] * s, _TG_BOY["baldir"] * s
    ust = dict(g=28, k1=58, o1=84, k2=52, o2=76, s=s)
    govde = tg_eklemler(tg_poz(hx, hy=hy, **ust))
    gidon = (govde["el1"][0] + 1, govde["el1"][1])

    def bacak(aci):
        px, py = cx + r * _math.cos(aci), cy + r * _math.sin(aci)
        d = min(_math.dist((hx, hy), (px, py)), L1 + L2 - 0.01)
        a = _math.atan2(px - hx, py - hy)                       # kalçadan pedala (aşağıdan ölçülen)
        ic = _math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
        u = a + ic                                                # diz öne
        dx, dy = hx + L1 * _math.sin(u), hy + L1 * _math.cos(u)
        b = _math.atan2(px - dx, py - dy)
        return _math.degrees(u), _math.degrees(b)
    an, adim = [], 8
    for i in range(tur * adim + 1):
        aci = 2 * _math.pi * i / adim                # tepe noktada pedal öne (+x) gider: sürücü sağa bakar (Paket 27)
        u1, b1 = bacak(aci)
        u2, b2 = bacak(aci + _math.pi)
        an.append((i / (tur * adim), tg_poz(hx, hy=hy, u1=u1, b1=b1, u2=u2, b2=b2, a1=96, a2=96, **ust)))
    return TgHareket(an, {"krank": (cx, cy), "sele": (hx, hy + 2), "gidon": gidon, "r": r})


def hk_nordic(diz_x, diz_y, s=1.0, son_aci=58, yon=1):
    """
    Nordic hamstring: diz üstü, ayak bilekleri sabit (baldır geride yatay); diz eklemi çevresinde gövde + uyluk
    düz bir çizgi halinde öne YAVAŞÇA iner (eksantrik). Son anahtar = kopma anı (son_aci, dikeyden).
    olay: "diz" (sabit), "bilek" (sabit tutulan nokta), "aci_yolu" [(t, açı)].
    """
    L = _TG_BOY["uyluk"] * s

    def poz(aci, kol):
        r = _math.radians(aci)
        return dict(tg_poz(diz_x + yon * L * _math.sin(r), s=s, yon=yon, g=aci, u1=-aci, b1=-90, u2=-aci, b2=-80,
                           a1=0, a2=6, **kol), hy=diz_y - L * _math.cos(r))
    dik = dict(k1=28, o1=96, k2=20, o2=88)            # kollar göğüs önünde çapraz
    hazir = dict(k1=70, o1=60, k2=60, o2=52)          # kopma anında eller düşüşü karşılamaya hazır
    acilar = [(0.0, 0), (0.15, 0), (0.45, 18), (0.75, 38), (1.0, son_aci)]
    an = [(t, poz(a, dik if t < 0.75 else hazir)) for t, a in acilar]
    e = tg_eklemler(an[-1][1])
    return TgHareket(an, {"diz": (diz_x, diz_y), "bilek": e["ayak1"], "aci_yolu": acilar})


def hk_dinamometre(kalca_x, kalca_y, s=1.0):
    """
    İzokinetik dinamometre koltuğunda oturuş: uyluk yatay ve sabit, diz ekseni cihaz başında, kaval kemiği kola
    bağlı. Sıra: 90° izometrik (kaval dik) → 180°/sn izokinetik ekstansiyon-fleksiyon → 45° izometrik (son anahtar).
    b1 = kavalın dikeyden açısı: 0 → diz 90° fleksiyon, 45 → diz 45° fleksiyon. olay: "diz", "ayak_yolu" (kol ucu).
    """
    ust = dict(g=-12, u1=90, u2=88, b2=8, a1=90, a2=96, k1=8, o1=-6, k2=14, o2=2, s=s)
    an = [(t, dict(tg_poz(kalca_x, hy=kalca_y, b1=b, **ust))) for t, b in
          [(0.0, 0), (0.22, 0), (0.36, 82), (0.5, 4), (0.64, 82), (0.78, 4), (0.86, 45), (1.0, 45)]]
    yol = [(t, *tg_eklemler(p)["ayak1"]) for t, p in _tg_kareler(an)]
    return TgHareket(an, {"diz": tg_eklemler(an[0][1])["diz1"], "ayak_yolu": yol})


def hk_iki_uke_atis(x_sol, x_sag, s=1.0, mesafe=22):
    """
    Judo SJFT: iki uke (atılan) x_sol ve x_sag'da durur, tori ortadan başlar; sağdaki ukeye koşup öne devirme
    (sırttan atış), soldakine koşup aynısı, sonra kalkmış olan sağdakine bir kez daha: 3 atış (A, B, C periyotları).
    olay: "ukeler" [sol, sağ] (hk_ikinci_figur), "atis_anlari" [3].
    """
    orta = (x_sol + x_sag) / 2
    xa = x_sag - mesafe * s                                  # sağdakine atış konumu (sağa bakar)
    Rp = _hk_one_pozlari(xa, s, mesafe * s)
    c = (x_sag + x_sol) / 2                                   # ayna: sağdaki ukeyi soldakine taşır
    Lp = {k: _hk_ayna(v, c) for k, v in Rp.items()}
    t_an = [(0.0, tg_poz(orta, s=s, k1=40, o1=70, k2=30, o2=60)), (0.05, tg_poz(orta, s=s, k1=40, o1=70, k2=30, o2=60))]
    t_an += _hk_kos_anahtarlari(orta, xa, 0.06, 0.13, 1, s)[1:]
    t_an += [(0.14, Rp["dur"]), (0.18, Rp["gir"]), (0.23, Rp["yukle"]), (0.28, Rp["bitir"])]
    t_an += _hk_kos_anahtarlari(Rp["bitir"]["hx"], Lp["dur"]["hx"], 0.3, 0.42, -1, s)[1:]
    t_an += [(0.43, Lp["dur"]), (0.47, Lp["gir"]), (0.52, Lp["yukle"]), (0.57, Lp["bitir"])]
    t_an += _hk_kos_anahtarlari(Lp["bitir"]["hx"], Rp["dur"]["hx"], 0.59, 0.71, 1, s)[1:]
    t_an += [(0.72, Rp["dur"]), (0.76, Rp["gir"]), (0.81, Rp["yukle"]), (0.86, Rp["bitir"]), (1.0, Rp["bitir"])]
    sag = [(0.0, Rp["m_dur"]), (0.14, Rp["m_dur"]), (0.18, Rp["m_gir"]), (0.23, Rp["m_ucus"]), (0.28, Rp["m_yerde"]),
           (0.42, Rp["m_yerde"]), (0.6, Rp["m_dur"]), (0.72, Rp["m_dur"]), (0.76, Rp["m_gir"]), (0.81, Rp["m_ucus"]),
           (0.86, Rp["m_yerde"]), (1.0, Rp["m_yerde"])]
    sol = [(0.0, Lp["m_dur"]), (0.43, Lp["m_dur"]), (0.47, Lp["m_gir"]), (0.52, Lp["m_ucus"]), (0.57, Lp["m_yerde"]),
           (1.0, Lp["m_yerde"])]
    return TgHareket(t_an, {"ukeler": [hk_ikinci_figur(sol), hk_ikinci_figur(sag)], "atis_anlari": [0.28, 0.57, 0.86]})


def hk_uchikomi(x, tekrar=3, s=1.0, mesafe=22):
    """
    Uchi-komi: tutuş alınır, tori giriş yapar (sırtını döner, kalçayı ukenin önüne sokar) ve çıkar; ATIŞ YOK.
    Son anahtar = son giriş anı (durağan görselde giriş görünür). olay: "partner", "giris_anlari".
    """
    P = _hk_one_pozlari(x, s, mesafe * s)
    tut = tg_poz(x, s=s, g=12, u1=14, b1=2, u2=-14, b2=-6, k1=68, o1=92, k2=58, o2=84)
    m_tut = tg_poz(x + mesafe * s, s=s, yon=-1, g=10, u1=12, b1=2, u2=-12, b2=-6, k1=64, o1=88, k2=54, o2=80)
    gir = P["gir"]
    m_gir = P["m_gir"]
    a_an, m_an, giris = [(0.0, tut)], [(0.0, m_tut)], []
    pay = 1.0 / tekrar
    for i in range(tekrar):
        b = i * pay
        a_an += [(b + 0.15 * pay, tut), (b + 0.55 * pay, gir)]
        m_an += [(b + 0.15 * pay, m_tut), (b + 0.55 * pay, m_gir)]
        giris.append(b + 0.55 * pay)
        if i < tekrar - 1:
            a_an.append((b + 0.95 * pay, tut))
            m_an.append((b + 0.95 * pay, m_tut))
    a_an.append((1.0, gir))
    m_an.append((1.0, m_gir))
    return TgHareket(a_an, {"partner": hk_ikinci_figur(m_an), "giris_anlari": giris})


# Vuruş teknikleri (yan görünüş, sağa bakan sporcu; 1 = yakın/ön, 2 = uzak/arka uzuv). Değerler gardan farktır.
_HK_GARD = dict(g=8, u1=14, b1=4, u2=-16, b2=-8, k1=30, o1=150, k2=20, o2=160)
_HK_TEKNIK = {
    "jab": dict(k1=88, o1=90), "tsuki": dict(k1=88, o1=90),
    "cross": dict(g=16, k2=88, o2=90, u2=-24),
    "hook": dict(g=12, k1=96, o1=150), "uchi": dict(g=12, k1=96, o1=150),
    "uppercut": dict(g=4, k2=44, o2=172),
    "teep": dict(g=-10, u1=95, b1=86, u2=-4, b2=0), "ap": dict(g=-10, u1=95, b1=86, u2=-4, b2=0),
    "geri": dict(g=-10, u1=95, b1=86, u2=-4, b2=0),
    "yop": dict(g=-30, u1=92, b1=92, u2=-4, b2=0),
    "knee": dict(g=-6, u2=100, b2=-20, k1=60, o1=110, k2=56, o2=104),
    "roundhouse": dict(g=-18, u2=88, b2=82, u1=4, b1=0),
    "dollyo": dict(g=-28, u2=116, b2=110, u1=6, b1=0),
}


def hk_vurus(x, teknikler, s=1.0, yon=1):
    """
    Vuruş serisi (boks, kickboks, Muay Thai, karate, taekwondo): gardda bekler, sıradaki tekniği uzatır, garda
    döner. Son anahtar = son tekniğin vuruş anı (durağan görselde vuruş görünür). olay: "darbe_anlari",
    "erisim" (son vuruşta en öndeki uç: el ya da ayak — hedef bu noktaya konur).
    """
    gard = tg_yerlestir(tg_poz(x, s=s, yon=yon, **_HK_GARD))
    an, darbe = [(0.0, gard), (0.08, gard)], []
    pay = 0.92 / len(teknikler)
    for i, t in enumerate(teknikler):
        b = 0.08 + i * pay
        vur = tg_yerlestir(tg_poz(x, s=s, yon=yon, **dict(_HK_GARD, **_HK_TEKNIK[t])))
        an.append((b + 0.45 * pay, vur))
        darbe.append(b + 0.45 * pay)
        if i < len(teknikler) - 1:
            an.append((b + 0.9 * pay, gard))
    an.append((1.0, an[-1][1]))
    e = tg_eklemler(an[-1][1])
    uc = max((e[k] for k in ("el1", "el2", "ayak1", "ayak2", "parmak1", "parmak2")), key=lambda q: q[0] * yon)
    return TgHareket(an, {"darbe_anlari": darbe, "erisim": uc})


def hk_asilma_bukumlu(x, bar_y, s=1.0):
    """
    Asılı durma, bükümlü kol (Eurofit BAH): bara avuçlar öne tutunur, dirsekler bükük, çene barın ÜSTÜNDE; ayaklar
    yerden kesik. Son anahtar = asılı (süre ölçülürken). olay: "el", "cene_y".
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    kol = dict(k1=24, o1=172, k2=30, o2=178)
    govde = tg_poz(x, s=s, u1=50, b1=-30, u2=36, b2=-44, a1=70, a2=64, **kol)
    e = tg_eklemler(govde)
    asili = dict(govde, hy=govde["hy"] + (bar_y - e["el1"][1]))          # eller barda
    asili = _hk_uclari_ayir(asili, el=(-4.2, 0))                         # öbür el barda, biraz geride
    uzan = tg_yerlestir(tg_poz(x, s=s, k1=170, o1=172, k2=186, o2=184))
    an = [(0.0, uzan), (0.12, uzan), (0.3, asili), (1.0, asili)]
    son = tg_eklemler(asili)
    return TgHareket(an, {"el": son["el1"], "cene_y": son["bas"][1] + L["bas"] * 0.8})


def hk_asilma(x, tutma_y, s=1.0):
    """
    Askıda kavrama (gi/kurtka yakası): altında durup uzanır, yakayı kavrar, ayaklar yerden kesilir ve asılı
    kalır; son anahtar = asılı (süre ölçülürken). Eller tutma noktasında. olay: "el" (tutma noktası).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    asili = dict(tg_poz(x, s=s, u1=56, b1=-34, u2=40, b2=-50, k1=174, o1=176, k2=188, o2=186, a1=70, a2=64),
                 hy=tutma_y + L["govde"] + L["ust"] + L["on"])
    uzan = tg_yerlestir(tg_poz(x, s=s, k1=170, o1=172, k2=186, o2=184))
    an = [(0.0, uzan), (0.12, uzan), (0.25, asili), (1.0, asili)]
    return TgHareket(an, {"el": tg_eklemler(asili)["el1"]})


def hk_yan_adim(x_sol, x_sag, tekrar=3, s=1.0):
    """Yana karışık adım (önden): ayaklar açılıp kapanarak sağ-sol çizgiler arası gidip gelir; son anahtar sağda."""
    on = dict(cephe=True, a1=90, a2=-90, k1=40, o1=80, k2=-40, o2=-80, s=s, g=6)
    acik = dict(on, u1=12, b1=8, u2=-12, b2=-8)
    kapali = dict(on, u1=5, b1=3, u2=-5, b2=-3)
    an, n = [], 2 * tekrar
    for i in range(n + 1):
        x = x_sol if i % 2 == 0 else x_sag
        an.append((i / n, tg_poz(x, **acik)))
        if i < n:
            an.append(((i + 0.5) / n, tg_poz((x_sol + x_sag) / 2, **kapali)))
    return TgHareket(an, {})


def _hk_iki_parca(kok, hedef, L1, L2, yon=1, bukum=1):
    """
    İki parçalı uzuv ters kinematiği: kökten hedefe (el ya da ayak) uzanan iki açıyı verir (aşağıdan ölçülen,
    + = yöne doğru). bukum: ara eklemin (dirsek/diz) hangi yana kırılacağı (+1 / −1).
    """
    dx, dy = hedef[0] - kok[0], hedef[1] - kok[1]
    d = max(1e-6, min(_math.hypot(dx, dy), L1 + L2 - 1e-6))
    a = _math.atan2(dx * yon, dy)
    ic = _math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    t1 = a + bukum * ic
    ex, ey = kok[0] + yon * L1 * _math.sin(t1), kok[1] + L1 * _math.cos(t1)
    t2 = _math.atan2((hedef[0] - ex) * yon, hedef[1] - ey)
    return _math.degrees(t1), _math.degrees(t2)


def _hk_kollar_hedefe(p, el1, el2=None, bukum1=1, bukum2=1):
    """Pozun kollarını hedef noktalara uzatır (omuz yerinden). Gövde ve bacaklar aynı kalır."""
    s, yon = p.get("s", 1.0), p.get("yon", 1)
    e = tg_eklemler(p)
    L1, L2 = _TG_BOY["ust"] * s, _TG_BOY["on"] * s
    q = dict(p)
    q["k1"], q["o1"] = _hk_iki_parca(e["kok_k1"], el1, L1, L2, yon, bukum1)
    if el2 is not None:
        q["k2"], q["o2"] = _hk_iki_parca(e["kok_k2"], el2, L1, L2, yon, bukum2)
    return q


def _hk_kol_sec(p, kol, hedef, olcut):
    """
    Tek kolu hedefe uzatır; iki dirsek çözümünden olcut(dirsek, omuz) değeri küçük olanı seçer
    (ör. dirsek yukarıda: lambda d, o: d[1]; dirsek dışta: lambda d, o: -abs(d[0] - o[0])).
    """
    en = None
    for b in (1, -1):
        q = _hk_kollar_hedefe(p, hedef, None, b, b) if kol == "1" else dict(p)
        if kol == "2":
            s_, yon = p.get("s", 1.0), p.get("yon", 1)
            e0 = tg_eklemler(p)
            q["k2"], q["o2"] = _hk_iki_parca(e0["kok_k2"], hedef, _TG_BOY["ust"] * s_, _TG_BOY["on"] * s_, yon, b)
        e = tg_eklemler(q)
        puan = olcut(e["dirsek" + kol], e["kok_k" + kol])
        if en is None or puan < en[0]:
            en = (puan, q)
    return en[1]


def _hk_yere_koy(p, noktalar):
    """Pozu dikey kaydırır: verilen eklemlerden en alttaki zemine değer (yatış, diz üstü, şınav)."""
    e = tg_eklemler(p)
    return dict(p, hy=p["hy"] + (TG_ZEMIN - max(e[k][1] for k in noktalar)))


def _hk_uclari_ayir(p, el=(4.0, 0.0), pay=3.4):
    """
    Yandan bakışta uzak el/ayak yakınınkinin tam arkasına düşerse (TG_EN_YAKIN_UC) ayırır — figür tek çubuk gibi
    görünmesin. Uzak el, yakın elin el=(dx, dy) kadar yanına uzanır (yerde/barda kalsın diye yön çağırandan);
    uzak ayak için uyluk ve baldır açısı en az değişecek biçimde aranır; ayak yere girmez, en çok 5,5 birim
    yukarıda kalabilir (uzak uzuv tuvalde biraz yukarıda: derinlik).
    """
    q = dict(p)
    e = tg_eklemler(q)
    if _math.dist(e["el1"], e["el2"]) < pay:
        hedef = (e["el1"][0] + el[0], e["el1"][1] + el[1])
        eski = e["dirsek2"]
        q = _hk_kol_sec(q, "2", hedef, lambda d, o: _math.dist(d, eski))
        e = tg_eklemler(q)
    if _math.dist(e["ayak1"], e["ayak2"]) < pay:
        alt = max(e["ayak2"][1], e["parmak2"][1])
        en = None
        for du in range(-16, 17):
            for db in range(-16, 17):
                r = dict(q, u2=q.get("u2", 0) + du, b2=q.get("b2", 0) + db)
                f = tg_eklemler(r)
                yuk = alt - max(f["ayak2"][1], f["parmak2"][1])      # uzak ayak biraz yukarıda olabilir (derinlik)
                if _math.dist(f["ayak1"], f["ayak2"]) < pay or not -0.6 <= yuk <= 5.5:
                    continue
                if en is None or abs(du) + abs(db) < en[0]:
                    en = (abs(du) + abs(db), r)
        if en:
            q = en[1]
    return q


def _hk_ayir_hepsi(an, **kw):
    """Anahtarların hepsine _hk_uclari_ayir; aynı poz nesnesi aynı kalır (tekrarlı hareketlerde 'is' karşılaştırması)."""
    hazir = {}
    return [(t, hazir.setdefault(id(p), _hk_uclari_ayir(p, **kw))) for t, p in an]


def hk_uzun_atlama(x_cizgi, mesafe, s=1.0):
    """
    Durarak uzun atlama: ayak uçları çizginin gerisinde çöker (kollar geride), kol salınımıyla sıçrar, havada
    dizler öne, iki ayak birlikte iner. Son anahtar = iniş (ölçüm anı). olay: "cizgi", "topuk_x" (en geri ayak).
    """
    ayak = ("ayak1", "ayak2", "parmak1", "parmak2")
    hazir = tg_yerlestir(tg_poz(x_cizgi - 10 * s, s=s, g=40, u1=72, b1=-30, u2=66, b2=-26,
                                k1=-62, o1=-52, k2=-52, o2=-42))
    on = max(tg_eklemler(hazir)[k][0] for k in ayak)
    hazir = dict(hazir, hx=hazir["hx"] - (on - x_cizgi) - 1)               # ayak uçları çizginin hemen gerisinde
    dur = tg_poz(hazir["hx"], s=s, k1=40, o1=50, k2=34, o2=44)
    dur = dict(dur, hx=dur["hx"] - max(tg_eklemler(dur)[k][0] for k in ayak) + x_cizgi - 1)
    kalk = tg_yerlestir(tg_poz(x_cizgi + 6 * s, s=s, g=42, u1=-24, b1=-30, u2=-30, b2=-36, a1=20, a2=16,
                               k1=152, o1=156, k2=144, o2=150), ayak_x=x_cizgi, bacak="2")
    ucus = dict(tg_poz(x_cizgi + mesafe * 0.55, s=s, g=24, u1=96, b1=22, u2=88, b2=16, k1=112, o1=100, k2=104, o2=94),
                hy=TG_ZEMIN - 52 * s)
    inis = tg_yerlestir(tg_poz(0, s=s, g=38, u1=78, b1=-8, u2=70, b2=-14, k1=96, o1=84, k2=88, o2=78))
    geri = min(tg_eklemler(inis)[k][0] for k in ("ayak1", "ayak2"))
    inis = dict(inis, hx=inis["hx"] + (x_cizgi + mesafe - geri))           # en geri ayak (topuk) mesafede
    an = [(0, dur), (0.12, dur), (0.35, hazir), (0.5, kalk), (0.72, ucus), (1.0, inis)]
    return TgHareket(an, {"cizgi": x_cizgi, "topuk_x": x_cizgi + mesafe})


def hk_mekik(x_kalca, tur="situp", tekrar=2, s=1.0):
    """
    Sırtüstü gövde fleksiyonu. tur="situp": dizler 90°, eller ense arkasında, gövde dizlere kadar kalkar;
    tur="curlup": dizler ≈ 140°, eller uyluklarda, yalnız baş ve omuzlar kalkar, parmaklar ileri kayar.
    Son anahtar = üst nokta (sayılan an). olay: "el_yolu" (curl-up'ta parmak ucunun ileri kayışı).
    """
    hy = TG_ZEMIN - 3 * s
    if tur == "situp":
        bacak = dict(u1=135, b1=47, u2=128, b2=40, a1=90, a2=96)
        yat = tg_poz(x_kalca, s=s, hy=hy, g=-88, **bacak)
        kalk = tg_poz(x_kalca, s=s, hy=hy, g=28, **bacak)
    else:
        bacak = dict(u1=112, b1=68, u2=106, b2=62, a1=90, a2=96)
        yat = tg_poz(x_kalca, s=s, hy=hy, g=-88, **bacak)
        kalk = tg_poz(x_kalca, s=s, hy=hy, g=-62, **bacak)
    if tur == "situp":                                   # eller ense arkasında: başın gerisine uzanır, dirsekler önde
        def kollar(p):
            e = tg_eklemler(p)
            gx, gy = e["bas"][0] - e["boyun"][0], e["bas"][1] - e["boyun"][1]
            hed = (e["bas"][0] - 0.2 * gx, e["bas"][1] - 0.2 * gy)
            q = _hk_kol_sec(p, "1", hed, lambda d, o: -(d[0] - o[0]) * p.get("yon", 1))
            return _hk_kol_sec(q, "2", (hed[0] - 1.5 * s, hed[1] + 1.5 * s), lambda d, o: -(d[0] - o[0]) * p.get("yon", 1))
        yat, kalk = kollar(yat), kollar(kalk)
        el_yolu = []
    else:                                                # eller uyluk üstünde, kalkınca öne kayar
        def kollar(p, ileri):
            e = tg_eklemler(p)
            kx, ky = e["kalca"]
            dx, dy = e["diz1"][0] - kx, e["diz1"][1] - ky
            hed = (kx + dx * ileri, ky + dy * ileri - 1)
            return _hk_kollar_hedefe(p, hed, (hed[0] - 2 * s, hed[1] + 1.2 * s), 1, 1)
        yat, kalk = kollar(yat, 0.12), kollar(kalk, 0.9)
        el_yolu = [tg_eklemler(yat)["el1"], tg_eklemler(kalk)["el1"]]
    an, pay = [(0.0, yat)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, kalk)] + ([(i * pay + pay, yat)] if i < tekrar - 1 else [])
    an.append((1.0, kalk))
    return TgHareket(_hk_ayir_hepsi(an, el=(-4.2, 0)), {"el_yolu": el_yolu})


def _hk_sinav_pozu(x, s, diz, kol):
    """Şınav pozu: gövde (diz üstüde gövde + uyluk) düz çizgi; eller omuz altında yerde, destek ayak ucu ya da diz."""
    en_iyi = None
    for g10 in range(400, 900, 5):
        g = g10 / 10
        p = tg_poz(x, s=s, g=g, u1=-g, b1=(-90 if diz else -g), u2=-g + 2, b2=(-96 if diz else -g + 2),
                   a1=0 if not diz else -90, a2=4 if not diz else -94, **kol)
        destek = ("diz1", "diz2") if diz else ("parmak1", "parmak2")
        p = _hk_yere_koy(p, destek)
        e = tg_eklemler(p)
        hata = abs(e["el1"][1] - TG_ZEMIN)
        if en_iyi is None or hata < en_iyi[0]:
            en_iyi = (hata, p)
    return en_iyi[1]


def hk_sinav(x, s=1.0, diz=False, tekrar=2):
    """
    Şınav (FitnessGram/PYFP; diz üstü: BOT-2): üstte kollar düz, altta dirsek 90°; gövde düz çizgi.
    Son anahtar = alt nokta (dirsek 90°). olay: "dirsek_acisi" (son karede).
    """
    ust = _hk_sinav_pozu(x, s, diz, dict(k1=0, o1=0, k2=4, o2=4))
    alt = _hk_sinav_pozu(x, s, diz, dict(k1=-58, o1=32, k2=-52, o2=38))
    an, pay = [(0.0, ust)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, alt)] + ([(i * pay + pay, ust)] if i < tekrar - 1 else [])
    an.append((1.0, alt))
    return TgHareket(_hk_ayir_hepsi(an, el=(-4.2, 0)), {"dirsek_acisi": 180 - abs(-58 - 32)})


def hk_modifiye_barfiks(x_topuk, s=1.0, tekrar=2, asili=False, bar_y=None):
    """
    Modified pull-up: sırtüstü, topuklar yerde, vücut düz; avuçlar öne bakarak bara tutunur. Altta kollar düz,
    üstte göğüs/çene bara çekilir. Bar yeri alttaki ellerden. Son anahtar = üst nokta. olay: "bar".
    asili=True (Paket 35, genel barfiks): aynı hareketin bantsız, yüksek bardaki varyantı — x_topuk gövdenin x'i,
    bar_y barın yüksekliği; altta kollar tam açık asılı (ayaklar yerden kesik), üstte çene barın üstünde.
    olay: "bar", "cene_y" (üst noktada çenenin y'si).
    """
    if asili:
        return _hk_asili_barfiks(x_topuk, bar_y, s, tekrar)

    def govde(g):
        p = tg_poz(0, s=s, g=-g, u1=g, b1=g, u2=g - 2, b2=g - 2, a1=150, a2=146, k1=180, o1=180, k2=176, o2=176)
        p = tg_yerlestir(p, ayak_x=x_topuk)
        return p
    alt = govde(80)
    bar = tg_eklemler(alt)["el1"]
    ust = govde(62)                                  # çene bardan 7-8 inç aşağıdaki elastik bandın üstüne çıkar
    ust = _hk_kollar_hedefe(ust, bar, (bar[0] - 2 * s, bar[1]), -1, -1)
    an, pay = [(0.0, alt)], 1.0 / tekrar
    for i in range(tekrar):
        an += [(i * pay + 0.5 * pay, ust)] + ([(i * pay + pay, alt)] if i < tekrar - 1 else [])
    an.append((1.0, ust))
    return TgHareket(_hk_ayir_hepsi(an, el=(-2.6, 2.6)), {"bar": bar})


# Paket 35b: bench press kol açıları (aşağıdan ölçülür, + = kalçaya doğru). Üstte kollar omuz üstünde dik;
# altta üst kol gövde boyunca (dirsek gövde çizgisinin hemen üstünde), ön kol yaklaşık dikey → bar alt göğüste.
BENCH_KOL_UST = (170, 172)
BENCH_KOL_ALT = (94, 178)
BENCH_KAVRAMA = (-4.2, 0.5)          # uzak el, yakın ele göre (yandan kavrama genişliğinin izdüşümü)
BENCH_ARA_ADIM = 8                   # iniş ve çıkışta ara anahtar sayısı (eller her karede barda)
BARFIKS_ARA_ADIM = 6


def _hk_asili_barfiks(x, bar_y, s, tekrar):
    """Genel barfiks (hk_modifiye_barfiks(asili=True)): pronasyon, tam açık asılı → çene bar üstünde."""
    L = {k: v * s for k, v in _TG_BOY.items()}
    bacak = dict(u1=14, b1=-28, u2=8, b2=-34, a1=150, a2=146)          # dizler hafif bükük: ayaklar yerden kesik
    alt = tg_poz(x, s=s, g=0, k1=178, o1=178, k2=182, o2=182, **bacak)
    alt = dict(alt, hy=alt["hy"] + (bar_y - tg_eklemler(alt)["el1"][1]))
    bar = tg_eklemler(alt)["el1"]
    ust = tg_poz(x - 3.5 * s, s=s, g=-6, **bacak)                       # baş barın gerisinden geçer, çene üstte
    ust = dict(ust, hy=ust["hy"] + (bar_y - 1.6 * s - tg_eklemler(ust)["cene"][1]))
    ust = _hk_kol_sec(ust, "1", bar, lambda d, o: -d[1])                # dirsek aşağıda
    ust = _hk_kol_sec(ust, "2", (bar[0] - 4.0, bar[1] + 0.5), lambda d, o: -d[1])
    alt = _hk_uclari_ayir(alt, el=(-4.0, 0.5))
    ust = _hk_aci_yakin(alt, ust)
    # Paket 35b: yalnız alt ve üst anahtar bara kilitliyse ara karede eller bardan kopuyordu (açı ara değeri).
    # Gövde ve bacaklar ara değerle yükselir; her ara anahtarda iki el IK ile barda (uzak el kavrama ofsetinde),
    # dirsek alt ve üst anahtarın dirsekleri arasındaki noktaya en yakın çözüm; açılar bir öncekine yakın (±360° yok).
    ea, eu = tg_eklemler(alt), tg_eklemler(ust)
    yol, onceki = [alt], alt
    for j in range(1, BARFIKS_ARA_ADIM):
        f = j / BARFIKS_ARA_ADIM
        p = _tg_ara(alt, ust, f)
        for kol, hedef in (("1", bar), ("2", (bar[0] - 4.0, bar[1] + 0.5))):
            ref = tuple(ea["dirsek" + kol][i] + (eu["dirsek" + kol][i] - ea["dirsek" + kol][i]) * f for i in (0, 1))
            p = _hk_kol_sec(p, kol, hedef, lambda d, o, r=ref: _math.dist(d, r))
        onceki = _hk_aci_yakin(onceki, p)
        yol.append(onceki)
    yol.append(ust)
    an, pay = [], 1.0 / tekrar
    for i in range(tekrar):
        cik = [(i * pay + 0.5 * pay * j / BARFIKS_ARA_ADIM, p) for j, p in enumerate(yol)]
        in_ = [(i * pay + 0.5 * pay + 0.5 * pay * j / BARFIKS_ARA_ADIM, p) for j, p in enumerate(yol[::-1])][1:]
        an += (cik if i == 0 else cik[1:]) + (in_ if i < tekrar - 1 else [])
    an.append((1.0, ust))
    return TgHareket(an, {"bar": bar, "cene_y": tg_eklemler(ust)["cene"][1]})


def hk_bench_press(x_kalca, sehpa_y, s=1.0):
    """
    Bench press (1RM, yandan): sehpada sırtüstü (baş, üst sırt, kalça sehpada; iki ayak yerde), kapalı kavrayış.
    Kollar tam açık → bar alt göğse iner → kollar tam açılır. Son anahtar = kollar tam açık (geçerli kaldırış).
    Paket 35b: altta üst kol gövde boyunca (dirsek gövde çizgisinin üstünde), ön kol yaklaşık dikey; bar boyundan
    kalçaya doğru alt göğüs hizasında. Kol açıları üst ↔ alt arasında BENCH_ARA_ADIM ara anahtarla değişir; her
    anahtarda uzak el yakın elin kavrama ofsetinde (BENCH_KAVRAMA) IK ile. Uzak ayak da zemine IK ile basar.
    olay: "bar" [(t, x, y)] bar ekseni (el), "gogus_y" (alt noktada barın y'si), "ayak" (ayak bileği).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    hy = sehpa_y - 2.0 * s
    ayak = (x_kalca + 27 * s, TG_ZEMIN - 1.0)
    ayak2 = (ayak[0] - 4.0, TG_ZEMIN - 1.0)                             # uzak ayak: ayrık ve zeminde
    u, b = _hk_iki_bag((x_kalca, hy), ayak, L["uyluk"], L["baldir"], 1)
    u2, b2 = _hk_iki_bag((x_kalca, hy), ayak2, L["uyluk"], L["baldir"], 1)
    yat = dict(tg_poz(x_kalca, s=s, g=-90, u1=u, b1=b, u2=u2, b2=b2, a1=100, a2=96), hy=hy)

    def kollar(k, o, onceki):
        p = dict(yat, k1=k, o1=o)
        e = tg_eklemler(p)
        hedef = (e["el1"][0] + BENCH_KAVRAMA[0], e["el1"][1] + BENCH_KAVRAMA[1])
        ref = (tg_eklemler(onceki)["dirsek2"] if onceki                 # dirsek dalı bir öncekinden sürer
               else (e["dirsek1"][0] + BENCH_KAVRAMA[0], e["dirsek1"][1] + BENCH_KAVRAMA[1]))
        p = _hk_kol_sec(p, "2", hedef, lambda d, o_: _math.dist(d, ref))
        return _hk_aci_yakin(onceki, p) if onceki else p
    (k0, o0), (k1, o1) = BENCH_KOL_UST, BENCH_KOL_ALT
    inis, onceki = [], None
    for j in range(BENCH_ARA_ADIM, -1, -1):                              # alttan üste: dal altta belirgin
        f = j / BENCH_ARA_ADIM
        onceki = kollar(k0 + (k1 - k0) * f, o0 + (o1 - o0) * f, onceki)
        inis.insert(0, onceki)
    acik, gogus = inis[0], inis[-1]
    alt_el = tg_eklemler(gogus)["el1"]
    n = BENCH_ARA_ADIM
    an = ([(0.0, acik)] + [(0.15 + 0.35 * j / n, p) for j, p in enumerate(inis)]
          + [(0.5 + 0.35 * j / n, p) for j, p in enumerate(inis[::-1])][1:] + [(1.0, acik)])
    bar = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an)]
    bas = tg_eklemler(acik)["bas"]
    # spotçu (ikinci figür): barın başında, hafif öne eğik, eller barın hemen üstünde hazır
    bx_, by_ = bar[-1][1], bar[-1][2]
    sp = tg_yerlestir(tg_poz(bas[0] - 26, s=s, g=18, u1=14, b1=-4, u2=4, b2=-10))
    sp = _hk_kollar_hedefe(sp, (bx_ - 3, by_ - 3), (bx_ - 7, by_ - 2), -1, -1)
    return TgHareket(an, {"bar": bar, "gogus_y": alt_el[1], "ayak": ayak, "bas": bas,
                          "spotcu": hk_ikinci_figur([(0.0, sp), (1.0, sp)]), "spotcu_bas": tg_eklemler(sp)["bas"]})


def _hk_comelme_pozu(x_ayak, s, g, u, b):
    """Arka çömelme pozu: ayak bileği x_ayak'ta sabit, bar üst sırtta, eller barda (dirsekler aşağıda)."""
    p = tg_yerlestir(tg_poz(x_ayak, s=s, g=g, u1=u, b1=b, u2=u - 5, b2=b - 5, a1=90, a2=88), ayak_x=x_ayak)
    e = tg_eklemler(p)
    r = _math.radians(g)
    bar = (e["boyun"][0] - 2.8 * s * _math.cos(r) - 1.5 * s * _math.sin(r),     # boynun gerisinde, omuzların üstünde
           e["boyun"][1] - 2.8 * s * _math.sin(r) + 1.5 * s * _math.cos(r))
    ref = (e["boyun"][0] - 5 * s * _math.cos(r) - 10 * s * _math.sin(r),            # dirsek: gövdenin gerisinde, aşağıda
           e["boyun"][1] - 5 * s * _math.sin(r) + 10 * s * _math.cos(r))
    p = _hk_kol_sec(p, "1", (bar[0] + 1.2 * s, bar[1]), lambda d, o: _math.dist(d, ref))
    p = _hk_kol_sec(p, "2", (bar[0] - 3.4, bar[1] + 0.6), lambda d, o: _math.dist(d, ref))
    return _hk_uclari_ayir(p, el=(-3.6, 0.6)), bar


def _hk_aci_yakin(onceki, p, adlar=("k1", "o1", "k2", "o2")):
    """Uzuv açılarını önceki poza en yakın eşdeğerine (±360°) çeker: ara karede kol tersine dönmesin."""
    q = dict(p)
    for k in adlar:
        if k in q and k in onceki:
            q[k] = q[k] + 360 * round((onceki[k] - q[k]) / 360)
    return q


def hk_arka_comelme(x_ayak, s=1.0, g=40, u=80, b=-24):
    """
    Arka çömelme (back squat 1RM, yandan): bar üst sırtta; dik duruş → diz açısı 90°'yi geçene kadar çömelme.
    Son anahtar = en alt nokta (ayırt edici an: derinlik). olay: "bar" [(t, x, y)], "diz_acisi" (altta, iç açı),
    "diz" (altta diz noktası).
    """
    dik, _ = _hk_comelme_pozu(x_ayak, s, 0, 7, -1)
    ara, _ = _hk_comelme_pozu(x_ayak, s, g * 0.55, u * 0.5, b * 0.5)          # ara poz: eller inişte barda kalsın
    cok, _ = _hk_comelme_pozu(x_ayak, s, g, u, b)
    ara = _hk_aci_yakin(dik, ara)
    cok = _hk_aci_yakin(ara, cok)
    an = [(0.0, dik), (0.25, dik), (0.62, ara), (1.0, cok)]
    bar = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        r = _math.radians(p.get("g", 0))
        bar.append((t, e["boyun"][0] - 2.8 * s * _math.cos(r) - 1.5 * s * _math.sin(r),
                    e["boyun"][1] - 2.8 * s * _math.sin(r) + 1.5 * s * _math.cos(r)))
    return TgHareket(an, {"bar": bar, "diz_acisi": 180 - (u - b), "diz": tg_eklemler(cok)["diz1"]})


def hk_leg_press(kalca, s=1.0, egim=45, uzak=0.94, yakin=0.5, g=-58):
    """
    Leg press (1RM, yandan, kızak egim° açılı): kalça ve sırt minderde, ayaklar platformda; bacaklar açık → platform
    belirlenen derinliğe iner (dizler göğse yaklaşır) → bacaklar açılır (diz kilitlenmez). Son anahtar = itiş sonu.
    olay: "platform" [(t, x1, y1, x2, y2)], "ray" (yön birim vektörü), "alt" (en alt anahtarın sırası).
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    hx, hy = kalca
    r = _math.radians(egim)
    ray = (_math.cos(r), -_math.sin(r))
    bacak = L["uyluk"] + L["baldir"]

    def poz(oran):
        ayak = (hx + ray[0] * bacak * oran, hy + ray[1] * bacak * oran)
        el = (hx - 2 * s, hy - 1 * s)                                         # tutamaklar kalçanın yanında
        return _hk_uclari_ayir(_hk_oturus(hx, hy, ayak, s, g, el, (el[0] - 4.2, el[1] + 0.5), a=-90 - egim))
    acik, alt = poz(uzak), poz(yakin)
    an = [(0.0, acik), (0.15, acik), (0.55, alt), (1.0, acik)]
    platform = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        cx, cy = e["ayak1"][0] + ray[0] * 1.6 * s, e["ayak1"][1] + ray[1] * 1.6 * s    # tabanın hemen önünde
        dx, dy = -ray[1], ray[0]                                               # rayya dik
        platform.append((t, cx - dx * 10 * s, cy - dy * 10 * s, cx + dx * 6 * s, cy + dy * 6 * s))
    return TgHareket(an, {"platform": platform, "ray": ray, "alt": 2, "boyun": tg_eklemler(acik)["boyun"]})


def _hk_ara_ekle(an, en_cok=60.0):
    """
    Ardışık anahtarlar arasında uzuv açısı en_cok dereceden fazla değişiyorsa araya _tg_ara ile anahtar ekler:
    _tg_kareler'in kare başına açı adımı ≈ 0,25 × anahtar farkı → ≤ 15°. Açılar önce bir öncekine yakınlaştırılır
    (±360° ters dönme yok).
    """
    adlar = ("u1", "b1", "u2", "b2", "k1", "o1", "k2", "o2", "a1", "a2", "g")

    def taban(p):
        e = tg_eklemler(p)
        return max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2"))
    sonuc = [an[0]]
    for (t1, p1) in an[1:]:
        t0, p0 = sonuc[-1]
        p1 = _hk_aci_yakin(p0, p1, adlar)
        fark = max([abs(p1.get(k, 0) - p0.get(k, 0)) for k in adlar])
        n = max(1, _math.ceil(fark / en_cok))
        ayni_zemin = abs(taban(p0) - taban(p1)) < 0.5             # iki uç yerdeyse ara anahtar da yerde
        for j in range(1, n):
            q = _tg_ara(p0, p1, j / n)
            if ayni_zemin:
                q = dict(q, hy=q["hy"] + (taban(p0) - taban(q)))
            sonuc.append((t0 + (t1 - t0) * j / n, q))
        sonuc.append((t1, p1))
    return sonuc


def hk_sargent(duvar_x, s=1.0, yukselme=6.0):
    """
    Sargent dikey sıçrama (duvar + tebeşir, önden: sporcu duvara yan, duvar figürün yanında dikey çizgi). Duvara
    yaklaşır → duvara yakın kol yukarı, parmak ucu duvarda (ayakta erişim, alt iz) → hafif uzaklaşır → çömelir
    (hazırlık çömelmesi) → sıçrar → ZİRVEDE duvara dokunur (üst iz). Son anahtar = zirve (ölçüm anı).
    olay: "alt_iz", "ust_iz" (duvardaki tebeşir izleri = el noktası), "alt_t" (ayakta erişim anı), "duvar_x".
    """
    L = {k: v * s for k, v in _TG_BOY.items()}
    kol = (L["ust"] + L["on"]) * 0.99
    on = dict(cephe=True, s=s, a1=90, a2=-90)

    def duz(hx, **k):
        return tg_yerlestir(tg_poz(hx, **{**on, "u1": 5, "b1": 5, "u2": -5, "b2": -5,
                                          "k1": 10, "o1": 6, "k2": -10, "o2": -6, **k}))

    def duvara(p):                                    # yakın kol duvara, en yükseğe (parmak ucu duvarda)
        kok = tg_eklemler(p)["kok_k1"]
        hx_ = duvar_x - 1.0
        hedef = (hx_, kok[1] - _math.sqrt(max(0.0, kol * kol - (hx_ - kok[0]) ** 2)))
        return _hk_kol_sec(p, "1", hedef, lambda d, o: -d[0]), hedef
    # Paket 36: önden çizimde kolu yandan (abdüksiyonla) kaldırmak eli duvarın içinden geçiriyordu. Yakın kol
    # gövdeye yakın bükülerek yükselir; her ara anahtarda el IK ile duvarın solundaki bir hedefte (dirsek gövdeye
    # doğru). Sıçrama için duvardan bir adım uzaklaşılır.
    def el1(p, hedef):
        return _hk_kol_sec(p, "1", hedef, lambda d, o: d[0])

    def omuz(p):
        return tg_eklemler(p)["kok_k1"]
    yakin = duvar_x - 1.0 - L["bas"] - 2.5            # baş duvara değmez
    uzak = yakin - 8.0 * s                             # duvardan bir adım uzaklaşır
    gel = duz(yakin - 34 * s)
    dur = duz(yakin)
    ko = omuz(dur)
    kaldir = el1(duz(yakin, k2=-14, o2=-10), (ko[0] + 4 * s, ko[1] - 2 * s))            # el omuz hizasında, önde
    eris, alt_iz = duvara(duz(yakin, k2=-14, o2=-10))
    ara_x = (yakin + uzak) / 2
    indir = el1(duz(ara_x), (omuz(duz(ara_x))[0] + 4 * s, omuz(duz(ara_x))[1] - 2 * s))
    geri = duz(uzak)
    cok = tg_yerlestir(tg_poz(uzak, **{**on, "u1": 34, "b1": -26, "u2": -34, "b2": 26,
                                       "k1": 20, "o1": 12, "k2": -28, "o2": -20}))
    kc = omuz(cok)
    cok = el1(cok, (kc[0] + 3 * s, kc[1] + kol * 0.85))                                  # kol aşağıda, gövdeye yakın
    kalk = tg_yerlestir(tg_poz(uzak, **{**on, "u1": 4, "b1": 4, "u2": -4, "b2": -4, "a1": 150, "a2": -150,
                                        "k2": -150, "o2": -160}))
    kk = omuz(kalk)
    savur = el1(dict(kalk, k2=-90, o2=-110), (kk[0] + 4 * s, kk[1] - 2 * s))             # kol önden yukarı
    savur = tg_yerlestir(dict(cok, k1=savur["k1"], o1=savur["o1"], k2=-80, o2=-100))
    kalk = el1(kalk, (duvar_x - 3.0, kk[1] - kol * 0.9))
    hy0 = kalk["hy"]
    kh = omuz(kalk)                                                    # zirve: üst iz tuvalin üst payında
    dx = duvar_x - 1.0 - kh[0]
    yukselme = max(yukselme, kh[1] - _math.sqrt(max(0.0, kol * kol - dx * dx)) - 21.5)
    tepe = dict(kalk, hy=hy0 - yukselme, k2=-148, o2=-156)            # uzak kol yukarı-yana (başlık payı)
    tepe, ust_iz = duvara(tepe)
    def yol(p0, p1, adim=4):
        """p0 → p1 arası: gövde ara değer, yakın el iki ucun elleri arasındaki doğru üzerinde (IK, dirsek sürekli)."""
        e0, e1 = tg_eklemler(p0), tg_eklemler(p1)
        sonuc, dirsek = [], e0["dirsek1"]
        tab = [max(e[k][1] for k in ("ayak1", "ayak2", "parmak1", "parmak2")) for e in (e0, e1)]
        zemin0 = tab[0] if abs(tab[0] - TG_ZEMIN) < 0.5 and abs(tab[1] - TG_ZEMIN) < 0.5 else None
        for j in range(1, adim):
            f = j / adim
            q = _tg_ara(p0, p1, f)
            hedef = (e0["el1"][0] + (e1["el1"][0] - e0["el1"][0]) * f, e0["el1"][1] + (e1["el1"][1] - e0["el1"][1]) * f)
            q = _hk_kol_sec(q, "1", hedef, lambda d, o, r=dirsek: _math.dist(d, r) + 100 * max(0.0, d[0] - (duvar_x - 1.5)))
            if zemin0 is not None:                                     # iki uç yerdeyse ara poz da yerde
                q = tg_yerlestir(q)
            dirsek = tg_eklemler(q)["dirsek1"]
            sonuc.append(q)
        return sonuc
    duraklar = [(0.0, gel), (0.06, gel), (0.2, dur), (0.27, kaldir), (0.34, eris), (0.44, eris), (0.5, indir),
                (0.56, geri), (0.68, cok), (0.77, savur), (0.86, kalk), (1.0, tepe)]
    an = [duraklar[0]]
    for (t0, p0), (t1, p1) in zip(duraklar, duraklar[1:]):
        if p0 is not p1:
            ara = yol(p0, p1)
            an += [(t0 + (t1 - t0) * (j + 1) / (len(ara) + 1), q) for j, q in enumerate(ara)]
        an.append((t1, p1))
    return TgHareket(_hk_ara_ekle(an), {"alt_iz": alt_iz, "ust_iz": ust_iz, "alt_t": 0.34, "duvar_x": duvar_x})


def hk_govde_kaldirma(x_kalca, s=1.0):
    """Trunk lift: yüzüstü, eller kalça yanında; baş ve üst gövde yavaşça kalkar. Son anahtar = en yüksek nokta."""
    hy = TG_ZEMIN - 3 * s
    ortak = dict(u1=-90, b1=-90, u2=-88, b2=-88, a1=-90, a2=-88, k1=-86, o1=-90, k2=-80, o2=-86)
    yat = tg_poz(x_kalca, s=s, hy=hy, g=90, **ortak)
    kalk = tg_poz(x_kalca, s=s, hy=hy, g=58, **ortak)
    return TgHareket(_hk_ayir_hepsi([(0, yat), (0.2, yat), (0.8, kalk), (1.0, kalk)], el=(4.2, 0)), {})


def hk_flamingo(x, s=1.0, tutar=True, zemin=None, kayip=0.45):
    """
    Tek ayak denge: destek ayağı düz, öbür bacak dizden bükülü geride (tutar=True: eliyle bileğinden tutar).
    kayip anında denge kaybı: serbest ayak yere değer, sonra pozisyon yeniden alınır. Son anahtar = dengede.
    olay: "kayip_t".
    """
    zemin = TG_ZEMIN if zemin is None else zemin
    serbest = dict(u2=-14, b2=-150, a2=-170)
    kol1 = dict(k1=70, o1=86)
    p = tg_yerlestir(tg_poz(x, s=s, u1=2, b1=0, **serbest, **kol1, k2=-30, o2=-40), zemin=zemin)
    if tutar:
        e = tg_eklemler(p)
        p = _hk_kollar_hedefe(p, e["el1"], e["ayak2"], 1, -1)          # öbür el serbest ayağın bileğinde
    sallan = dict(p, g=-8, k1=110, o1=120)
    yere = tg_yerlestir(tg_poz(x + 4 * s, s=s, u1=6, b1=2, u2=-12, b2=-8, k1=40, o1=60, k2=-36, o2=-50), zemin=zemin)
    an = [(0, p), (kayip - 0.15, p), (kayip - 0.05, sallan), (kayip, yere), (kayip + 0.2, p), (1.0, p)]
    return TgHareket(an, {"kayip_t": kayip})


def hk_masa_dokunma(x, masa_y, disk_dx, s=1.0, tur=4):
    """
    Plate tapping (önden): baskın olmayan el ortadaki plakada; baskın el iki disk arasında sırayla dokunur.
    Son anahtar = bir diske dokunuş. olay: "diskler" [(x, y), (x, y)], "plaka".
    """
    p = tg_poz(x, s=s, cephe=True, u1=5, b1=5, u2=-5, b2=-5, a1=90, a2=-90, g=10)
    plaka = (x - 3 * s, masa_y - 1)
    sol, sag = (x - disk_dx, masa_y - 1), (x + disk_dx, masa_y - 1)
    disari = lambda d, o: -abs(d[0] - x)                  # dirsekler gövdenin dışında
    def el(h):
        q = _hk_kol_sec(p, "1", h, disari)
        return _hk_kol_sec(q, "2", plaka, disari)
    an = [(i / tur, el(sag if i % 2 == 0 else sol)) for i in range(tur + 1)]
    return TgHareket(an, {"diskler": [sol, sag], "plaka": plaka})


def hk_omuz_esneme(x, s=1.0):
    """
    Shoulder stretch (arkadan): bir el omuz üstünden sırta, öbürü bel altından yukarı; parmak uçları sırtta
    buluşur. Son anahtar = buluşma. olay: "bulusma".
    """
    p = tg_poz(x, s=s, cephe=True, u1=4, b1=4, u2=-4, b2=-4, a1=90, a2=-90)
    e = tg_eklemler(p)
    # üstteki kol: dirsek yukarıda ve dışta (başın arkasında kalmasın); alttaki: dirsek belde, dışta
    ust = dict(p, k1=145, o1=-34, k2=-40, o2=128)
    acik = dict(p, k1=145, o1=-62, k2=-40, o2=152)       # eller henüz buluşmamış
    q = tg_eklemler(ust)
    bx, by = (q["el1"][0] + q["el2"][0]) / 2, (q["el1"][1] + q["el2"][1]) / 2
    bas = dict(p, k1=8, o1=6, k2=-8, o2=-6)
    return TgHareket([(0, bas), (0.2, bas), (0.6, acik), (1.0, ust)], {"bulusma": (bx, by)})


def hk_omuz_rotasyon(x, s=1.0):
    """
    Omuz rotasyonu (sopa/ip): kollar dirsekten bükülmeden önden-aşağıdan baş üstünden sırta geçer ve döner.
    Yandan; olay["el_yolu"] sopanın izlediği yay. Son anahtar = sırtta.
    """
    an, yol = [], []
    for i, a in enumerate([10, 10, 60, 120, 180, 240, 300, 330]):
        t = [0, 0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0][i]
        q = tg_poz(x, s=s, k1=a, o1=a, k2=a + 9, o2=a + 9)
        an.append((t, q))
    for t, q in _tg_kareler(an):
        yol.append(tg_eklemler(q)["el1"])
    return TgHareket(an, {"el_yolu": yol})


def hk_top_sektirme(x, s=1.0, tekrar=4):
    """Tek elle aşağı sektirme, top yerden sekip öbür ele; eller sırayla. olay: "top_yolu" [(t, x, y)]."""
    ust = lambda k: dict(k1=30 if k == 1 else 24, o1=70 if k == 1 else 64, k2=24 if k == 2 else 18,
                         o2=64 if k == 2 else 40)
    an, yol = [], []
    for i in range(tekrar + 1):
        k = 1 + i % 2
        p = tg_poz(x, s=s, g=10, u1=8, b1=-2, u2=-8, b2=-4, **ust(k))
        an.append((i / tekrar, p))
        e = tg_eklemler(p)
        el = e["el1"] if k == 1 else e["el2"]
        yol.append((i / tekrar, el[0] + 2, el[1] + 3))
        if i < tekrar:
            yol.append(((i + 0.5) / tekrar, el[0] + 3, TG_ZEMIN - 2.5))
    return TgHareket(an, {"top_yolu": yol})


def hk_top_yakala(x_cocuk, x_atan, s_cocuk=0.7, s_atan=0.95):
    """
    Uygulayıcı (ikinci kişi) alttan atar, çocuk iki eliyle yakalar. olay: "atan" (hk_ikinci_figur),
    "top_yolu" [(t, x, y)]. Son anahtar = yakalama.
    """
    c0 = tg_poz(x_cocuk, s=s_cocuk, k1=30, o1=60, k2=24, o2=54)
    c1 = tg_poz(x_cocuk, s=s_cocuk, g=6, k1=74, o1=96, k2=60, o2=84)
    a0 = tg_poz(x_atan, s=s_atan, yon=-1, k1=-30, o1=-10, k2=10, o2=20)
    a1 = tg_poz(x_atan, s=s_atan, yon=-1, g=10, k1=70, o1=80, k2=12, o2=22)
    e0, e1 = tg_eklemler(a1), tg_eklemler(c1)
    bas_t, bit_t = 0.35, 0.8
    yol = [(0.0, *tg_eklemler(a0)["el1"]), (bas_t, *e0["el1"])]
    for i in range(1, 9):
        f = i / 8
        yol.append((bas_t + (bit_t - bas_t) * f, e0["el1"][0] + (e1["el1"][0] - e0["el1"][0]) * f,
                    e0["el1"][1] + (e1["el1"][1] - e0["el1"][1]) * f - 34 * f * (1 - f)))
    yol.append((1.0, *e1["el1"]))
    atan = hk_ikinci_figur([(0, a0), (0.2, a0), (bas_t, a1), (1.0, a1)])
    return TgHareket([(0, c0), (0.3, c0), (0.6, c0), (bit_t, c1), (1.0, c1)], {"atan": atan, "top_yolu": yol})


def hk_takla(x, s=1.0, mesafe=None):
    """
    Öne takla (TSYT koordinasyon 1. istasyon): dur → çömel, eller minderde → BÜZÜL (dizler göğüste, baş içeri) →
    büzük gövde döner (olay["donus"]: (t0, t1, merkez_x, merkez_y) — sahne figür grubunu bu aralıkta 360° çevirir)
    → çömel, kollar önde → kalk. mesafe: dönüş boyunca ileri yuvarlanma (kayan sahnede parkur bu kadar kayar).
    """
    mesafe = 30 * s if mesafe is None else mesafe
    dur = tg_poz(x, s=s)
    comel = tg_yerlestir(tg_poz(x, s=s, g=62, u1=118, b1=-28, u2=112, b2=-34, a1=150, a2=146))
    comel = _hk_kollar_hedefe(comel, (x + 13 * s, TG_ZEMIN), (x + 11 * s, TG_ZEMIN), 1, 1)
    # büzük: gövde dik-öne yuvarlak (20°), uyluklar gövdenin önünde göğse (145°), baldırlar geriye-aşağı,
    # eller baldırları kavrar; uzak el/ayak yakınınkinden ayrı (uzuv uçları ≥ 3 birim — düğüm gibi görünmesin)
    buzul = tg_yerlestir(tg_poz(x, s=s, g=20, u1=145, b1=-25, u2=137, b2=-33, a1=120, a2=114))
    e = tg_eklemler(buzul)
    baldir = ((e["diz1"][0] + e["ayak1"][0]) / 2, (e["diz1"][1] + e["ayak1"][1]) / 2)
    buzul = _hk_uclari_ayir(_hk_kollar_hedefe(buzul, baldir, (baldir[0] - 2 * s, baldir[1] + 2 * s), 1, 1), el=(-3.6, 0))
    kalk = tg_yerlestir(tg_poz(x, s=s, g=50, u1=112, b1=-30, u2=106, b2=-36, a1=150, a2=146,
                               k1=96, o1=96, k2=90, o2=90))
    # dönüş merkezi: büzük gövdenin çevreleyen kutusunun ortası; yarıçap R = merkezden en uzak nokta (baş çemberi
    # ve çizgi kalınlığı dahil). Gövde, merkez zeminden R yukarıda olacak biçimde kaldırılır → 360° boyunca en alt
    # nokta hiçbir an zemin çizgisini geçmez (Paket 22: önceki merkez eklem ortalamasıydı, 10,7 birim gömülüyordu).
    e = tg_eklemler(buzul)
    noktalar = list(e.values())
    cx = (min(p[0] for p in noktalar) + max(p[0] for p in noktalar)) / 2
    cy = (min(p[1] for p in noktalar) + max(p[1] for p in noktalar)) / 2
    r_bas = _TG_BOY["bas"] * s
    R = max(max(_math.dist((cx, cy), p) for p in noktalar), _math.dist((cx, cy), e["bas"]) + r_bas)
    R += TG_KALINLIK["govde"] * s / 2
    kalkis = (TG_ZEMIN - R) - cy
    buzul = dict(buzul, hy=buzul["hy"] + kalkis)
    cy += kalkis
    an = [(0.0, dur), (0.16, comel), (0.28, buzul), (0.72, buzul), (0.86, kalk), (1.0, dur)]
    return TgHareket(an, {"donus": (0.28, 0.72, cx, cy), "yuvarlanma": mesafe})


def hk_alttan_gec(x, h, s=1.0, uzunluk=None):
    """
    Engelin altından eğilerek geçme: gövde öne eğik, dizler bükük; başın tepesi engel yüksekliği h'nin
    (zeminden) altında kalır. x → x + uzunluk ilerler. olay["bas_ust_en_yuksek"]: geçişteki en yüksek baş noktası.
    """
    uzunluk = 40 * s if uzunluk is None else uzunluk
    dur = tg_poz(x, s=s)
    egik = []
    for i, f in enumerate((0.0, 0.5, 1.0)):
        a = dict(u1=70, b1=-40, u2=40, b2=-70) if i % 2 == 0 else dict(u1=40, b1=-70, u2=70, b2=-40)
        p = tg_yerlestir(tg_poz(x + 8 * s + uzunluk * f, s=s, g=74, k1=60, o1=40, k2=50, o2=30, **a))
        egik.append(p)
    son = tg_poz(x + uzunluk + 16 * s, s=s)
    an = [(0.0, dur), (0.2, egik[0]), (0.5, egik[1]), (0.8, egik[2]), (1.0, son)]
    ust = min(tg_eklemler(p)["bas_ust"][1] for p in egik)
    return TgHareket(an, {"bas_ust_en_yuksek": ust})


def hk_engel_ustu(x, h, s=1.0, uzunluk=None):
    """
    Alçak engelin üstünden adımlayarak geçme: öndeki bacak dizden kalkar ve engeli aşar, arkadaki çekilir.
    x → x + uzunluk. olay["ayak_en_alt_ustte"]: engelin üstündeyken öndeki ayağın en alt noktası (zeminden yükseklik).
    """
    uzunluk = 36 * s if uzunluk is None else uzunluk
    dur = tg_poz(x, s=s)
    kaldir = tg_yerlestir(tg_poz(x + 6 * s, s=s, g=14, u1=96, b1=10, u2=-14, b2=-24, k1=-30, o1=10, k2=40, o2=70),
                          bacak="2")
    ustte = dict(tg_poz(x + uzunluk * 0.5, s=s, g=16, u1=70, b1=-6, u2=-60, b2=-10, k1=40, o1=70, k2=-30, o2=10))
    e = tg_eklemler(ustte)
    ustte = dict(ustte, hy=ustte["hy"] - (max(e["ayak1"][1], e["parmak1"][1]) - (TG_ZEMIN - h - 3 * s)))
    cek = tg_yerlestir(tg_poz(x + uzunluk * 0.8, s=s, g=10, u1=-10, b1=-20, u2=96, b2=10, k1=40, o1=70, k2=-30, o2=10))
    son = tg_poz(x + uzunluk, s=s)
    an = [(0.0, dur), (0.25, kaldir), (0.5, ustte), (0.75, cek), (1.0, son)]
    e = tg_eklemler(ustte)
    return TgHareket(an, {"ayak_en_alt_ustte": TG_ZEMIN - max(e["ayak1"][1], e["parmak1"][1])})


def hk_egil_al(x, s=1.0, tur="al", hedef_dx=None):
    """
    Eğilip yerden alma/bırakma ve top yönetimi. tur="al": eğil, eller yerde (topun üstünde), kalk, top göğüste;
    tur="birak": aynı hareket ters (göğüsten yere). tur="ayak": tek ayak üstünde, öbür ayakla topu ileri iter.
    tur="tut": ayakta, kollar önde göğüs hizasında (yakalama). olay["el"]: en alt anda el (ayak: ayak ucu).
    """
    hedef_dx = 16 * s if hedef_dx is None else hedef_dx
    dur = tg_poz(x, s=s)
    if tur == "ayak":
        it = tg_yerlestir(tg_poz(x, s=s, g=8, u1=-6, b1=-6, u2=40, b2=24, a2=110, k1=30, o1=50, k2=-30, o2=-10))
        return TgHareket([(0.0, dur), (0.5, it), (1.0, dur)], {"el": tg_eklemler(it)["parmak2"], "an": 0.5})
    if tur == "tut":
        tut = tg_poz(x, s=s, k1=74, o1=92, k2=66, o2=86)
        return TgHareket([(0.0, dur), (0.4, tut), (1.0, tut)], {"el": tg_eklemler(tut)["el1"], "an": 0.4})
    egil = tg_yerlestir(tg_poz(x, s=s, g=72, u1=70, b1=-60, u2=64, b2=-66))     # derin çömelme: el yere değer
    egil = _hk_kollar_hedefe(egil, (x + hedef_dx, TG_ZEMIN - 3 * s), (x + hedef_dx - 2 * s, TG_ZEMIN - 3 * s), 1, 1)
    gogus = tg_poz(x, s=s, k1=40, o1=110, k2=34, o2=104)
    an = [(0.0, gogus if tur == "birak" else dur), (0.5, egil), (1.0, dur if tur == "birak" else gogus)]
    return TgHareket(an, {"el": tg_eklemler(egil)["el1"], "an": 0.5})


def _hk_yerinde(hareket, x_c, t0, t1, w0, ref_x):
    """
    Kayan sahne yardımcısı: bir hareketin anahtarlarını [t0, t1] (saniye) aralığına koyar, figürü tuvalde x_c'de
    tutar; hareketin x'teki yol alışı dünyadaki ilerleme olur (w0 + hx − ref_x). [(T, poz, W)] döndürür.
    """
    out = []
    for t, p in hareket.anahtarlar:
        w = w0 + (p["hx"] - ref_x)
        out.append((t0 + (t1 - t0) * t, dict(p, hx=x_c), w))
    return out


KAYAN_HIZ_ISTASYON = 130.0    # birim/sn (≈ 0,50 tuval/sn): bir beceri yapılırken parkurun kayma hızı sınırı (Paket 23)
KAYAN_HIZ_GECIS = 225.0       # birim/sn (≈ 0,87 tuval/sn): istasyonlar arası geçişte (Paket 23)


def _hk_hiz_siniri(K, araliklar, v_ist=KAYAN_HIZ_ISTASYON, v_gecis=KAYAN_HIZ_GECIS):
    """
    Kayan turda zaman gerdirme (Paket 22). K: [(T sn, poz, W)]; araliklar: istasyon pencereleri [(t0, t1)] (sn).
    Her ardışık anahtar çifti en az |ΔW| / v sürer (istasyon içinde v_ist, geçişte v_gecis); kısa olan uzatılır,
    yerinde yapılan beceriler (ΔW = 0) süresini korur. Döndürür: (yeni K, ger) — ger eski zamanı yeniye çevirir.
    """
    eski = [t for t, _, _ in K]
    yeni = [eski[0]]
    for i in range(1, len(K)):
        dt, dw = eski[i] - eski[i - 1], abs(K[i][2] - K[i - 1][2])
        orta = (eski[i] + eski[i - 1]) / 2
        v = v_ist if any(a <= orta <= b for a, b in araliklar) else v_gecis
        yeni.append(yeni[-1] + max(dt, dw / v * 1.001))

    def ger(t):
        if t <= eski[0]:
            return yeni[0] + (t - eski[0])
        for i in range(1, len(eski)):
            if t <= eski[i]:
                f = (t - eski[i - 1]) / ((eski[i] - eski[i - 1]) or 1)
                return yeni[i - 1] + (yeni[i] - yeni[i - 1]) * f
        return yeni[-1] + (t - eski[-1])
    return [(yeni[i], p, w) for i, (_, p, w) in enumerate(K)], ger


KAYAN_DURAKLAMA = 0.5         # sn: her istasyon penceresinin başında parkur durur, ad belirir (Paket 25)


def _hk_hazir_durus(p, pay=1.5):
    """
    Duraklama pozu (Paket 26): iki ayak zaten zemindeyse (bilekler TG_ZEMIN'den ≤ pay) poz aynen döner. Değilse hx,
    g ve kol açıları korunur; bacaklar (u1, b1, u2, b2, a1, a2) nötr duruşa (TG_TEMEL_POZ) alınır, hy iki ayak
    zemine değecek biçimde düzeltilir — koşu ortasındaki havadaki ayak 0,5 sn donmuş görünmesin.
    """
    e = tg_eklemler(p)
    if max(TG_ZEMIN - e["ayak1"][1], TG_ZEMIN - e["ayak2"][1]) <= pay:
        return p
    q = dict(p, **{k: TG_TEMEL_POZ[k] for k in ("u1", "b1", "u2", "b2", "a1", "a2")})
    return tg_yerlestir(q)


def _hk_duraklat(K, baslar, sure=KAYAN_DURAKLAMA):
    """
    Kayan turda ritim (Paket 25): her istasyon başlangıcında (baslar, sn) figür ve parkur `sure` kadar durur —
    dünya ilerlemesi sıfır; göz hareketin başladığını fark eder. Figür duraklamada iki ayağı yerde, nötr hazır
    duruştadır (_hk_hazir_durus, Paket 26). Başlangıç anahtarı kopyalanır, sonraki
    bütün anahtarlar kaydırılır. Döndürür: (yeni K, kay) — kay(t, sonra): eski zamanı yeniye çevirir; sonra=True
    ise tam başlangıç anındaki olay duraklamadan SONRAya düşer (top olayları, dönüş), False ise önceye (pencere).
    """
    baslar = sorted(baslar)

    def kay(t, sonra=True):
        return t + sure * sum(1 for b in baslar if b < t - 1e-9 or (sonra and abs(b - t) <= 1e-9))
    yeni = []
    for t, p, w in K:
        yeni.append((kay(t, False), p, w))
        if any(abs(b - t) <= 1e-9 for b in baslar):
            q = _hk_hazir_durus(p)                       # iki ayak yerde (Paket 26)
            if q is not p:                               # kısa geçişle hazır duruşa, sonra bekler
                yeni.append((kay(t, False) + min(0.12, sure / 3), q, w))
            yeni.append((kay(t, True), dict(q), w))
    return yeni, kay


KOORDINASYON_ISTASYONLARI = ("Öne takla", "Denge tahtası", "Engel üzerinden top atma", "Tek ayak sekme",
                             "Elle top yer değiştirme", "Ayakla top yer değiştirme", "Duvara top atma",
                             "Alttan-üstten engel geçişi", "Slalom")   # TSYT protokolü 2-10. adımlar, aynı sıra


def hk_koordinasyon_turu(x_c=118, s=0.7, m=34.5):
    """
    TSYT Koordinasyon Parkuru — KAYAN SAHNE turu. Figür tuvalde x_c'de kalır, parkur (dünya) altından kayar;
    figür o anda yanından geçtiği istasyonun hareketini yapar. Sıra ve içerik protokolden (dokuz istasyon):
    1 öne takla · 2 denge tahtası (koşarak) · 3 engel üzerinden top atma (at, altından geç, tut, altından dön, bırak)
    · 4 tek ayak sekme (3 sağ, 3 sol) · 5 elle top yer değiştirme · 6 ayakla top yer değiştirme · 7 duvara top
    atma (al, at, tut, bırak) · 8 alttan-üstten engel (80-40-80-40) · 9 slalom (4 dikey engel), bitiş fotoseli.
    m: 1 m kaç birim (figürle aynı ölçek). 3. ve 7. istasyonlarda protokoldeki 2 ve 3 topun ilki gösterilir.
    olay: "sure" (sn), "kayma" [(t, dx)] (tuval x = dünya x + dx), "ekipman" (dünya konumları), "istasyonlar"
    [(no, t0, t1)], "toplar" [[(t, x, y)] tuvalde], "donus" (t0, t1, cx, cy) tuvalde.
    """
    Z = TG_ZEMIN
    K, T, W = [], 0.0, 0.0                              # anahtarlar [(T sn, poz, W)], şimdiki zaman ve dünya x'i
    ek = {}
    ist = []
    olaylar = []                                         # top olayları: (top, T, tur, veri)

    def ekle(hareket, sure, ref_x=None):
        nonlocal T, W
        ref = hareket.anahtarlar[0][1]["hx"] if ref_x is None else ref_x
        parca = _hk_yerinde(hareket, x_c, T, T + sure, W, ref)
        K.extend(parca[1:] if K and abs(parca[0][0] - K[-1][0]) < 1e-9 else parca)
        T, W = parca[-1][0], parca[-1][2]

    def kos(mesafe, sure, yon=1, adim=24):
        nonlocal T, W
        n = max(2, int(abs(mesafe) / (adim * s)))
        for i in range(1, n + 1):
            K.append((T + sure * i / n, _hk_kos_pozu(x_c, i, yon, s), W + mesafe * i / n))
        T, W = T + sure, W + mesafe

    def dur(sure):
        nonlocal T
        K.append((T + sure, dict(K[-1][1]), W))
        T += sure

    # başlangıç: başlama çizgisinde (fotosel), "çık" komutu
    K.append((0.0, tg_poz(x_c, s=s), 0.0))
    ek["baslangic"] = W + 10 * s
    dur(0.25)
    kos(0.45 * m, 0.3, adim=9)
    # 1 — öne takla (minder)
    t0 = T
    ek["minder"] = (W - 0.15 * m, W + 1.6 * m)
    tk = hk_takla(0, s, mesafe=1.0 * m)
    d0, d1, cx, cy = tk.olay["donus"]
    sure = 0.75
    a0 = len(K)
    ekle(tk, sure)
    for i in range(a0, len(K)):                         # dönüş boyunca ileri yuvarlanma (dünya ilerler)
        tt, p, w = K[i]
        f = min(1.0, max(0.0, ((tt - t0) / sure - d0) / (d1 - d0)))
        K[i] = (tt, p, w + tk.olay["yuvarlanma"] * f)
    W = K[-1][2]
    donus = (t0 + d0 * sure, t0 + d1 * sure, x_c + cx, cy)
    ist.append((1, t0, T))
    kos(0.4 * m, 0.25, adim=12)
    # 2 — denge tahtası 3 m; başlangıç ve bitişte 30 cm'lik bölgeler; koşarak geçer
    t0 = T
    ust = Z - 0.2 * m
    ek["denge"] = (W - 0.1 * m, W + 2.9 * m, ust)
    n = 10                                               # tahta üstünde 10 adım (sık kare: zaman dengesi)
    for i in range(1, n + 1):
        K.append((T + 0.6 * i / n, tg_yerlestir(_hk_kos_pozu(x_c, i, 1, s), zemin=ust), W + 3.0 * m * i / n))
    T, W = T + 0.6, W + 3.0 * m
    K.append((T + 0.05, _hk_kos_pozu(x_c, 1, 1, s), W + 0.3 * m))
    T, W = T + 0.05, W + 0.3 * m
    ist.append((2, t0, T))
    kos(0.4 * m, 0.2, adim=12)
    # 3 — engel (130 cm) üzerinden top: çemberden al, at, altından geç, tut, altından dön, çembere bırak
    t0 = T
    cember3 = W + 0.35 * m
    engel = W + 0.9 * m
    ek["engel_ust"] = (engel, 1.3 * m)
    ek["cember3"] = cember3
    al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
    olaylar.append(("t3", 0.0, "dunya", (cember3, Z - 3.2 * s)))
    olaylar.append(("t3", T + 0.25 * al.olay["an"], "el", None))
    ekle(al, 0.25)
    at = hk_atma(0, "ileri", s=s)
    t_at = T + 0.22 * at.olay["birakma_t"]
    ekle(at, 0.22)
    alt = hk_alttan_gec(0, 1.3 * m, s, uzunluk=1.3 * m)
    t_tut = T + 0.32
    olaylar.append(("t3", t_at, "ucus", (engel, Z - 1.3 * m - 14 * s, t_tut)))
    ekle(alt, 0.3)
    tut = hk_egil_al(0, s, "tut")
    ekle(tut, 0.1)
    olaylar.append(("t3", T, "el", None))
    # son eğik karede kalça direklerin (engel ± 6) dışında: doğrulma ancak sonra başlar (Paket 26)
    geri = hk_alttan_gec(0, 1.3 * m, s, uzunluk=(W - 8 * s) - (engel - 6 - 1.5))
    geri = TgHareket([(t, dict(p, hx=-p["hx"], yon=-1)) for t, p in geri.anahtarlar], geri.olay)
    ekle(geri, 0.3)
    bir = hk_egil_al(0, s, "birak", hedef_dx=W - cember3)      # top yine çemberin ortasına
    bir = TgHareket([(t, dict(p, hx=-p["hx"], yon=-1)) for t, p in bir.anahtarlar], bir.olay)
    t_bir = T + 0.22 * bir.olay["an"]
    ekle(bir, 0.22)
    olaylar.append(("t3", t_bir, "dunya", None))
    gec = hk_alttan_gec(0, 1.3 * m, s, uzunluk=(engel + 0.6 * m) - W - 16 * s)
    ekle(gec, 0.3)
    ist.append((3, t0, T))
    kos(0.3 * m, 0.15)
    # 4 — tek ayak sekme: bitişik 6 çember (60 cm), ilk üçü sağ (yakın), sonraki üçü sol (uzak) ayak
    t0 = T
    ek["sekme"] = [W + 0.3 * m + i * 0.6 * m for i in range(6)]
    for ayak, bas in (("1", W), ("2", W + 1.8 * m)):
        sk = hk_tek_ayak_sekme(bas, None, sekme_sonra=3, adim=0.6 * m, yukselme=8 * s, s=s, ayak=ayak)
        ekle(sk, 0.33)
    ist.append((4, t0, T))
    kos(0.3 * m, 0.15)
    # 5 — elle top yer değiştirme: üç çember, aralarında 1 m; A ve B'de top, C boş → A→C, B→A, C→B
    t0 = T
    A, B, C = W + 0.5 * m, W + 1.5 * m, W + 2.5 * m
    ek["el_cember"] = (A, B, C)
    olaylar += [("t5a", 0.0, "dunya", (A, Z - 3.2 * s)), ("t5b", 0.0, "dunya", (B, Z - 3.2 * s))]
    for top, kaynak, hedef in (("t5a", A, C), ("t5b", B, A), ("t5a", C, B)):
        kos(kaynak - 0.35 * m - W, 0.08, 1 if kaynak - 0.35 * m >= W else -1)
        al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
        olaylar.append((top, T + 0.12 * al.olay["an"], "el", None))
        ekle(al, 0.12)
        yon = 1 if hedef > kaynak else -1
        kos(hedef - kaynak, 0.08, yon)
        bir = hk_egil_al(0, s, "birak", hedef_dx=0.35 * m)
        olaylar.append((top, T + 0.12 * bir.olay["an"], "dunya", None))
        ekle(bir, 0.12)
    ist.append((5, t0, T))
    kos(C + 0.25 * m - W, 0.15)
    # 6 — ayakla top yer değiştirme (aynı düzen, 3 numara hentbol topları)
    t0 = T
    A, B, C = W + 0.5 * m, W + 1.5 * m, W + 2.5 * m
    ek["ayak_cember"] = (A, B, C)
    olaylar += [("t6a", 0.0, "dunya", (A, Z - 2.6 * s)), ("t6b", 0.0, "dunya", (B, Z - 2.6 * s))]
    for top, kaynak, hedef in (("t6a", A, C), ("t6b", B, A), ("t6a", C, B)):
        yon = 1 if hedef > kaynak else -1
        kos(kaynak - yon * 0.4 * m - W, 0.07, 1 if kaynak - yon * 0.4 * m >= W else -1)
        it = hk_egil_al(0, s, "ayak")
        it = TgHareket([(t, dict(p, yon=yon)) for t, p in it.anahtarlar], it.olay)
        t_it = T + 0.1 * it.olay["an"]
        ekle(it, 0.1)
        olaylar.append((top, t_it, "yuvarlan", (hedef, Z - 2.6 * s, t_it + 0.1)))
        kos(hedef - yon * 0.4 * m - W, 0.1, yon)
    ist.append((6, t0, T))
    kos(C + 0.25 * m - W, 0.15)
    # 7 — duvara top atma: duvardan 1,5 m'deki üç çember (aralarında 20 cm); al, at, tut, bırak
    t0 = T
    c7 = W + 0.35 * m
    duvar = c7 + 1.5 * m
    ek["duvar"] = duvar
    ek["duvar_cember"] = [c7, c7 - 0.8 * m, c7 - 1.6 * m]
    olaylar += [("t7", 0.0, "dunya", (c7, Z - 2.4 * s))]
    al = hk_egil_al(0, s, "al", hedef_dx=0.35 * m)
    olaylar.append(("t7", T + 0.15 * al.olay["an"], "el", None))
    ekle(al, 0.15)
    at = hk_atma(0, "duvara", s=s)
    at = TgHareket([(t / 0.42, p) for t, p in at.anahtarlar if t <= 0.42 + 1e-9], at.olay)   # tek atış: at, tut
    tb = at.olay["birakma_t"] / 0.42
    t_b = T + 0.4 * tb
    t_don = T + 0.4
    olaylar.append(("t7", t_b, "duvar", (duvar, Z - 0.9 * m, t_don)))
    ekle(at, 0.4)
    olaylar.append(("t7", t_don, "el", None))
    bir = hk_egil_al(0, s, "birak", hedef_dx=0.35 * m)
    olaylar.append(("t7", T + 0.15 * bir.olay["an"], "dunya", None))
    ekle(bir, 0.15)
    ist.append((7, t0, T))
    kos(duvar - W + 0.25 * m, 0.2)
    # 8 — alttan-üstten: dört engel (80-40-80-40 cm), aralarında 1 m
    t0 = T
    engeller = [(W + 0.6 * m + i * 1.0 * m, (0.8, 0.4)[i % 2] * m) for i in range(4)]
    ek["alttan_ustten"] = engeller
    for i, (ex, eh) in enumerate(engeller):
        hedef_x = ex + 0.5 * m
        if i % 2 == 0:
            ekle(hk_alttan_gec(0, eh, s, uzunluk=hedef_x - W - 24 * s), 0.22)
        else:
            ekle(hk_engel_ustu(0, eh, s, uzunluk=hedef_x - W), 0.18)
    ist.append((8, t0, T))
    kos(0.3 * m, 0.12)
    # 9 — slalom: dört dikey engel, aralarında 80 cm; başlama yönü serbest
    t0 = T
    kazik = [W + 0.4 * m + i * 0.8 * m for i in range(4)]
    ek["slalom"] = kazik
    nok = [(W, Z)] + [(k + 0.0, Z + (2.5 if i % 2 == 0 else -2.5) * s) for i, k in enumerate(kazik)] + [(kazik[-1] + 0.6 * m, Z)]
    sl = hk_kavisli_yol(nok, s=s)
    ekle(sl, 0.65)
    ist.append((9, t0, T))
    # bitiş fotoseli
    ek["bitis"] = W + 0.4 * m
    kos(0.6 * m, 0.25)
    # hız sınırı (Paket 22): istasyon süresi kat ettiği mesafeden; bütün zamanlar aynı gerdirmeyle taşınır
    K[:], ger = _hk_hiz_siniri(K, [(a, b) for _, a, b in ist])
    ist[:] = [(n, ger(a), ger(b)) for n, a, b in ist]
    olaylar[:] = [(k, ger(t) if t > 0 else t, tur,
                   (veri[0], veri[1], ger(veri[2])) if tur in ("ucus", "duvar", "yuvarlan") else veri)
                  for k, t, tur, veri in olaylar]
    donus = (ger(donus[0]), ger(donus[1]), donus[2], donus[3])
    K[:], kay = _hk_duraklat(K, [a for _, a, _ in ist])          # ritim (Paket 25): istasyon başında duraklama
    ist[:] = [(n, kay(a, False), kay(b, False)) for n, a, b in ist]
    olaylar[:] = [(k, kay(t) if t > 0 else t, tur,
                   (veri[0], veri[1], kay(veri[2])) if tur in ("ucus", "duvar", "yuvarlan") else veri)
                  for k, t, tur, veri in olaylar]
    donus = (kay(donus[0]), kay(donus[1]), donus[2], donus[3])
    T = K[-1][0]
    toplam = T

    # zaman → 0-1; kayma dx(t) = x_c − W(t)
    an = [(t / toplam, p) for t, p, _ in K]
    kayma = [(t / toplam, x_c - w) for t, _, w in K]

    def dx_at(t):
        for (ta, da), (tb_, db) in zip(kayma, kayma[1:]):
            if ta <= t <= tb_:
                return da + (db - da) * ((t - ta) / ((tb_ - ta) or 1))
        return kayma[-1][1]

    def el_at(t):
        for (ta, pa), (tb_, pb) in zip(an, an[1:]):
            if ta <= t <= tb_:
                ea, eb = tg_eklemler(pa), tg_eklemler(pb)
                f = (t - ta) / ((tb_ - ta) or 1)
                ka = "el1"
                return (ea[ka][0] + (eb[ka][0] - ea[ka][0]) * f, ea[ka][1] + (eb[ka][1] - ea[ka][1]) * f)
        return tg_eklemler(an[-1][1])["el1"]

    # toplar: dünya/el/uçuş durumları → tuvalde [(t, x, y)]
    zamanlar = sorted({t for t, _ in an})
    toplar = {}
    for top in dict.fromkeys(o[0] for o in olaylar):
        ev = sorted([o for o in olaylar if o[0] == top], key=lambda o: o[1])
        ev = [(t / toplam, tur, veri) for _, t, tur, veri in ev]
        yol = []
        konum = None
        for i, (te, tur, veri) in enumerate(ev):
            sonraki = ev[i + 1][0] if i + 1 < len(ev) else 1.0
            if tur == "dunya":
                konum = veri if veri is not None else (yol[-1][1] - dx_at(te), Z - 3.2 * s)
                aralik = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
                yol += [(z, konum[0] + dx_at(z), konum[1]) for z in aralik]
            elif tur == "el":
                aralik = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
                yol += [(z, el_at(z)[0] + 2 * s, el_at(z)[1] - 2 * s) for z in aralik]
            elif tur in ("ucus", "duvar", "yuvarlan"):
                hx_, hy_, t_son = veri
                t_son /= toplam
                bas = (el_at(te)[0], el_at(te)[1]) if tur != "yuvarlan" else (yol[-1][1], yol[-1][2])
                if tur == "duvar":                       # duvara gidip döner, ele
                    orta = (te + t_son) / 2
                    for j in range(5):
                        f = j / 4
                        z = te + (orta - te) * f
                        yol.append((z, bas[0] + (hx_ + dx_at(z) - 2 - bas[0]) * f, bas[1] + (hy_ - bas[1]) * f))
                    son = el_at(t_son)
                    for j in range(1, 5):
                        f = j / 4
                        z = orta + (t_son - orta) * f
                        yol.append((z, hx_ + dx_at(z) - 2 + (son[0] - hx_ - dx_at(z) + 2) * f, hy_ + (son[1] - hy_) * f))
                elif tur == "ucus":                      # engelin üstünden: tepe hy_ (dünya x hx_ üstünde)
                    son_d = el_at(t_son)
                    b_d = (bas[0] - dx_at(te), bas[1])   # dünyada
                    s_d = (son_d[0] - dx_at(t_son), son_d[1])
                    for j in range(1, 9):
                        f = j / 8
                        z = te + (t_son - te) * f
                        xd = b_d[0] + (s_d[0] - b_d[0]) * f
                        yd = b_d[1] + (s_d[1] - b_d[1]) * f - 4 * (min(b_d[1], s_d[1]) - hy_) * f * (1 - f)
                        yol.append((z, xd + dx_at(z), yd))
                else:                                     # ayakla itilen top yerde yuvarlanır
                    b_d = bas[0] - dx_at(te)
                    for j in range(1, 6):
                        f = j / 5
                        z = te + (t_son - te) * f
                        yol.append((z, b_d + (hx_ - b_d) * f + dx_at(z), hy_))
                    yol += [(z, hx_ + dx_at(z), hy_) for z in zamanlar if t_son < z < sonraki] + [(sonraki, hx_ + dx_at(sonraki), hy_)]
        yol = [(0.0, *yol[0][1:])] + yol if yol[0][0] > 0 else yol
        temiz = []
        for p in yol:
            if not temiz or p[0] > temiz[-1][0] + 1e-6:
                temiz.append(p)
        toplar[top] = temiz
    # oynatma süresi = tur süresi (Paket 22: sıkıştırma yok; hız sınırı yukarıda)
    olay = {"sure": round(toplam, 2), "kayma": kayma, "ekipman": ek,
            "istasyonlar": [(n, a / toplam, b / toplam) for n, a, b in ist],
            "istasyon_adlari": [KOORDINASYON_ISTASYONLARI[n - 1] for n, _, _ in ist],
            "toplar": list(toplar.values()), "donus": (donus[0] / toplam, donus[1] / toplam, donus[2], donus[3]),
            "dunya_son": W}
    return TgHareket(an, olay)


def hk_yana_kayma(x0, x1, s=1.0, adim=None):
    """
    Yana kayma (side slide, önden görünüş): ayaklar açılır-kapanır, gövde dik, ayaklar çapraz geçmez; x0 → x1.
    Her adım: açık (ayaklar ayrık) → kapalı (ayaklar yanaşık), hafif yaylanma.
    """
    adim = 14 * s if adim is None else adim
    n = max(2, int(abs(x1 - x0) / adim))
    on = dict(cephe=True, a1=90, a2=-90, k1=40, o1=70, k2=-40, o2=-70, s=s, g=0)
    an = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        acik = i % 2 == 1
        p = tg_poz(x, **on, **(dict(u1=16, b1=16, u2=-16, b2=-16) if acik else dict(u1=4, b1=4, u2=-4, b2=-4)))
        an.append((i / n, tg_yerlestir(p) if not acik else dict(tg_yerlestir(p), hy=tg_yerlestir(p)["hy"] - 2 * s)))
    an[-1] = (1.0, tg_yerlestir(tg_poz(x1, **on, u1=4, b1=4, u2=-4, b2=-4)))
    return TgHareket(an, {})


def hk_skipping(x0, x1, s=1.0, adim=None):
    """
    Skipping (adım-sekme; ipli atlama değil): her adımda destek ayağında küçük sekme, öbür diz öne-yukarı kalkar,
    karşı kol öne; ayaklar sırayla. x0 → x1.
    """
    adim = 20 * s if adim is None else adim
    n = max(2, int(abs(x1 - x0) / adim))
    an = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        if i % 2 == 0:
            p = tg_poz(x, s=s, g=6, u1=0, b1=0, u2=70, b2=-10, k1=-30, o1=20, k2=50, o2=110)   # sağ diz yukarı
        else:
            p = tg_poz(x, s=s, g=6, u1=70, b1=-10, u2=0, b2=0, k1=50, o1=110, k2=-30, o2=20)   # sol diz yukarı
        p = tg_yerlestir(p)
        an.append((i / n, dict(p, hy=p["hy"] - (4 * s if i % 2 else 3 * s))))     # sekme: destek ayağı yerden kalkar
    an[-1] = (1.0, tg_yerlestir(tg_poz(x1, s=s)))
    return TgHareket(an, {})


def hk_topa_vurus(x, s=1.0):
    """
    Topa vuruş (iç-üst ayak/ayak üstü): destek ayağı topun yanında, vuran bacak geriden öne savrulur; vuruş anı
    olay["vurus_t"], ayak ucu olay["ayak"]. Son anahtar = vuruş sonrası (bacak önde).
    """
    yaklas = tg_yerlestir(tg_poz(x - 16 * s, s=s, g=10, u1=30, b1=-10, u2=-30, b2=-60, k1=-30, o1=10, k2=30, o2=60))
    geri = tg_yerlestir(tg_poz(x, s=s, g=6, u1=0, b1=0, u2=-40, b2=-100, k1=40, o1=60, k2=-40, o2=-10), bacak="1")
    vur = tg_yerlestir(tg_poz(x, s=s, g=-6, u1=0, b1=0, u2=40, b2=30, a2=120, k1=-40, o1=-10, k2=50, o2=70), bacak="1")
    son = tg_yerlestir(tg_poz(x + 4 * s, s=s, g=-4, u1=-6, b1=-6, u2=70, b2=60, a2=130, k1=-40, o1=-10, k2=60, o2=80),
                       bacak="1")
    an = [(0.0, yaklas), (0.35, geri), (0.6, vur), (1.0, son)]
    return TgHareket(an, {"vurus_t": 0.6, "ayak": tg_eklemler(vur)["parmak2"]})


CAMSA_BECERILERI = ("Çift ayak sıçrama", "Yana kayma", "Top yakalama", "Hedefe atış", "Skipping",
                    "Tek ayak sekme", "Topa vuruş")   # CAMSA (CAPL-2), sabit sıra


def _hk_tur_toplari(an, kayma, olaylar, toplam, Z, s):
    """
    Kayan turda topların tuval yolu. olaylar: (top, T sn, tür, veri). Türler: "dunya" (dünyada duran; veri (x, y)
    ya da None = bulunduğu yer), "el" (elde), "ucus" ((tepe_y, T_son, hedef) — hedef "el" ya da dünya (x, y);
    başlangıç verilmezse elden), "dunyadan" ((x0, y0) dünyadan fırlar → sonraki "el" anına uçar, tepe yüksek).
    """
    zamanlar = sorted({t for t, _ in an})

    def dx_at(t):
        for (ta, da), (tb, db) in zip(kayma, kayma[1:]):
            if ta <= t <= tb:
                return da + (db - da) * ((t - ta) / ((tb - ta) or 1))
        return kayma[-1][1]

    def el_at(t):
        for (ta, pa), (tb, pb) in zip(an, an[1:]):
            if ta <= t <= tb:
                ea, eb = tg_eklemler(pa)["el1"], tg_eklemler(pb)["el1"]
                f = (t - ta) / ((tb - ta) or 1)
                return (ea[0] + (eb[0] - ea[0]) * f, ea[1] + (eb[1] - ea[1]) * f)
        return tg_eklemler(an[-1][1])["el1"]

    sonuc = []
    for top in dict.fromkeys(o[0] for o in olaylar):
        ev = sorted([(t / toplam, tur, veri) for k, t, tur, veri in olaylar if k == top], key=lambda o: o[0])
        yol, konum = [], None
        for i, (te, tur, veri) in enumerate(ev):
            sonraki = ev[i + 1][0] if i + 1 < len(ev) else 1.0
            ara = [te] + [z for z in zamanlar if te < z < sonraki] + [sonraki]
            if tur == "dunya":
                konum = veri if veri is not None else (yol[-1][1] - dx_at(te), yol[-1][2])
                yol += [(z, konum[0] + dx_at(z), konum[1]) for z in ara]
            elif tur == "el":
                yol += [(z, el_at(z)[0] + 2 * s, el_at(z)[1] - 2 * s) for z in ara]
            elif tur == "ucus":
                tepe_y, t_son, hedef = veri
                t_son /= toplam
                b = (yol[-1][1] - dx_at(te), yol[-1][2]) if yol else (el_at(te)[0] - dx_at(te), el_at(te)[1])
                if hedef == "el":
                    sv = el_at(t_son)
                    h = (sv[0] - dx_at(t_son), sv[1])
                else:
                    h = hedef
                for j in range(1, 11):
                    f = j / 10
                    z = te + (t_son - te) * f
                    xd = b[0] + (h[0] - b[0]) * f
                    yd = b[1] + (h[1] - b[1]) * f - 4 * (min(b[1], h[1]) - tepe_y) * f * (1 - f)
                    yol.append((z, xd + dx_at(z), yd))
                if hedef != "el":
                    yol += [(z, h[0] + dx_at(z), h[1]) for z in ara if z > t_son]
        if yol[0][0] > 0:
            yol = [(0.0, *yol[0][1:])] + yol
        temiz = []
        for p in yol:
            if not temiz or p[0] > temiz[-1][0] + 1e-6:
                temiz.append(p)
        sonuc.append(temiz)
    return sonuc


def hk_camsa_turu(x_c=118, s=0.7, m=34.5):
    """
    CAPL-2 motor beceri testi CAMSA — KAYAN SAHNE turu (Koordinasyon Parkuru ile aynı yapı). Figür x_c'de kalır,
    parkur altından kayar. Sabit sıra (Cao ve ark. 2020; Chang ve ark. 2021): 1 çift ayak sıçrama (3 çember) ·
    2 yana kayma (iki kez, biri ters yönde) · 3 uygulayıcının attığı topu yakalama · 4 hedefe atış · 5 skipping (5 m)
    · 6 tek ayak sekme (6 çember) · 7 iki koni arasından topa vuruş — süre vuruşla durur.
    Protokolde yalnız skipping mesafesi (5 m) ve çember sayıları var; öbür aralıklar şematik.
    olay: "sure", "kayma", "ekipman", "beceriler" [(no, t0, t1)], "beceri_adlari", "toplar", "uygulayici" (eklemler).
    """
    Z = TG_ZEMIN
    K, T, W = [], 0.0, 0.0
    ek, bec, olaylar = {}, [], []

    def ekle(hareket, sure):
        nonlocal T, W
        ref = hareket.anahtarlar[0][1]["hx"]
        parca = _hk_yerinde(hareket, x_c, T, T + sure, W, ref)
        K.extend(parca[1:] if K and abs(parca[0][0] - K[-1][0]) < 1e-9 else parca)
        T, W = parca[-1][0], parca[-1][2]

    def kos(mesafe, sure, yon=1, adim=12):
        nonlocal T, W
        n = max(2, int(abs(mesafe) / (adim * s)))
        for i in range(1, n + 1):
            K.append((T + sure * i / n, _hk_kos_pozu(x_c, i, yon, s), W + mesafe * i / n))
        T, W = T + sure, W + mesafe

    K.append((0.0, tg_poz(x_c, s=s), 0.0))
    K.append((0.2, tg_poz(x_c, s=s), 0.0))
    T = 0.2
    # 1 — çift ayak sıçrama: üç çemberin üzerinden
    t0 = T
    ek["cift_cember"] = [W + (0.45 + 0.6 * i) * m for i in range(3)]
    ekle(hk_tek_ayak_sekme(0, None, sekme_sonra=4, adim=0.6 * m, yukselme=7 * s, s=s, ayak="cift"), 0.9)
    bec.append((1, t0, T))
    kos(0.5 * m, 0.15)
    # 2 — yana kayma: koniye kadar ve geri (iki kez, biri ters yönde)
    t0 = T
    ek["kayma_koni"] = (W - 0.2 * m, W + 2.2 * m)
    ekle(hk_yana_kayma(0, 2.0 * m, s), 0.45)
    ekle(hk_yana_kayma(2.0 * m, 0.4 * m, s), 0.4)
    bec.append((2, t0, T))
    kos(0.8 * m, 0.15)
    # 3 — top yakalama: uygulayıcı karşıdan atar
    t0 = T
    ek["uygulayici"] = W + 2.6 * m
    tut = hk_egil_al(0, s, "tut")
    olaylar.append(("top", 0.0, "dunya", (ek["uygulayici"] - 6 * s, Z - 0.95 * m)))
    olaylar.append(("top", T + 0.05, "ucus", (Z - 1.6 * m, T + 0.5 * tut.olay["an"] + 0.12, "el")))
    olaylar.append(("top", T + 0.5 * tut.olay["an"] + 0.12, "el", None))
    ekle(TgHareket([(0, tut.anahtarlar[0][1]), (0.3, tut.anahtarlar[0][1])] + [(0.3 + 0.7 * t, p) for t, p in tut.anahtarlar[1:]], tut.olay), 0.5)
    bec.append((3, t0, T))
    kos(ek["uygulayici"] + 0.6 * m - W, 0.2)            # uygulayıcının yanından geçer: hedef önünde açık kalır
    # 4 — hedefe atış: hedef karşıda (duvarda)
    t0 = T
    ek["hedef"] = (W + 3.0 * m, Z - 1.2 * m)
    at = hk_atma(0, "duvara", s=s)
    at = TgHareket([(t / 0.42, p) for t, p in at.anahtarlar if t <= 0.42 + 1e-9], at.olay)
    t_b = T + 0.45 * (at.olay["birakma_t"] / 0.42)
    olaylar.append(("top", t_b, "ucus", (Z - 1.5 * m, t_b + 0.18, ek["hedef"])))
    ekle(at, 0.45)
    bec.append((4, t0, T))
    kos(0.5 * m, 0.12)
    # 5 — skipping 5 m
    t0 = T
    ek["skip"] = (W, W + 5.0 * m)
    ekle(hk_skipping(0, 5.0 * m, s), 0.9)
    bec.append((5, t0, T))
    kos(0.5 * m, 0.12)
    # 6 — tek ayak sekme: altı çemberin üzerinden
    t0 = T
    ek["tek_cember"] = [W + (0.3 + 0.6 * i) * m for i in range(6)]
    ekle(hk_tek_ayak_sekme(0, None, sekme_sonra=7, adim=0.6 * m, yukselme=7 * s, s=s), 0.9)
    bec.append((6, t0, T))
    kos(0.5 * m, 0.12)
    # 7 — iki koni arasından topa vuruş; süre vuruşla durur
    t0 = T
    vur = hk_topa_vurus(0, s)
    top_x = W + 16 * s + (vur.olay["ayak"][0] - vur.anahtarlar[0][1]["hx"]) - 16 * s
    ek["vurus_top"] = top_x
    ek["koniler"] = (top_x + 2.6 * m, top_x + 3.4 * m)
    olaylar.append(("futbol", 0.0, "dunya", (top_x + 2 * s, Z - 2.8 * s)))
    t_v = T + 0.45 * vur.olay["vurus_t"]
    olaylar.append(("futbol", t_v, "ucus", (Z - 3.5 * s, t_v + 0.35, (sum(ek["koniler"]) / 2, Z - 2.8 * s))))
    ekle(vur, 0.45)
    ek["bitis_t"] = t_v
    bec.append((7, t0, T))
    K.append((T + 0.35, dict(K[-1][1]), W))
    # hız sınırı (Koordinasyon turuyla aynı kural): beceri süresi kat ettiği mesafeden
    K[:], ger = _hk_hiz_siniri(K, [(a, b) for _, a, b in bec])
    bec[:] = [(n, ger(a), ger(b)) for n, a, b in bec]
    olaylar[:] = [(k, ger(t) if t > 0 else t, tur, (veri[0], ger(veri[1]), veri[2]) if tur == "ucus" else veri)
                  for k, t, tur, veri in olaylar]
    ek["bitis_t"] = ger(ek["bitis_t"])
    K[:], kay = _hk_duraklat(K, [a for _, a, _ in bec])           # ritim (Paket 25): beceri başında duraklama
    bec[:] = [(n, kay(a, False), kay(b, False)) for n, a, b in bec]
    olaylar[:] = [(k, kay(t) if t > 0 else t, tur, (veri[0], kay(veri[1]), veri[2]) if tur == "ucus" else veri)
                  for k, t, tur, veri in olaylar]
    ek["bitis_t"] = kay(ek["bitis_t"])
    T = K[-1][0]
    toplam = T
    an = [(t / toplam, p) for t, p, _ in K]
    kayma = [(t / toplam, x_c - w) for t, _, w in K]
    uyg = tg_poz(ek["uygulayici"], s=s, yon=-1, k1=60, o1=90, k2=50, o2=80)
    return TgHareket(an, {"sure": round(toplam, 2), "kayma": kayma, "ekipman": ek,
                          "beceriler": [(n, a / toplam, b / toplam) for n, a, b in bec],
                          "beceri_adlari": [CAMSA_BECERILERI[n - 1] for n, _, _ in bec],
                          "bitis_t": ek["bitis_t"] / toplam,
                          "toplar": _hk_tur_toplari(an, kayma, olaylar, toplam, Z, s),
                          "uygulayici": tg_eklemler(uyg), "uygulayici_s": s})


def hk_servis(x, s=1.0):
    """
    Tenis servisi (yandan): top havaya atılır (atan kol yukarı), raket kolu arkada bükülü, sonra yukarıdan vuruş
    (vuruş anı olay["vurus_t"], temas noktası olay["temas"]; top başta olay["tutan_el"]de). Son anahtar = TEMAS
    anı (Paket 24): raket yukarıda, kol uzanmış — durağan kare başlıktaki anı gösterir, vuruş sonrası çizilmez.
    hk_atma'nın baş üstü kol yolundan türetilmiştir. olay["raket"]: [(t, x, y)] raket başı (vuran elin uzantısı).
    """
    dur = tg_poz(x, s=s, k1=20, o1=60, k2=10, o2=30)
    atis = tg_poz(x, s=s, g=-8, u1=8, b1=-4, u2=-12, b2=-20, k1=-40, o1=-110, k2=170, o2=175)     # top elden çıkar
    yay = tg_poz(x, s=s, g=-14, u1=20, b1=-10, u2=-16, b2=-40, k1=150, o1=-30, k2=170, o2=178)     # raket sırtta
    vur = tg_yerlestir(tg_poz(x + 4 * s, s=s, g=10, u1=10, b1=-6, u2=-30, b2=-60, k1=168, o1=175, k2=60, o2=40))
    an = [(0.0, dur), (0.25, atis), (0.6, yay), (1.0, vur)]
    raket = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        (ex, ey), (dx, dy) = e["el1"], e["dirsek1"]
        u = _math.hypot(ex - dx, ey - dy) or 1
        raket.append((t, ex + (ex - dx) / u * 9 * s, ey + (ey - dy) / u * 9 * s))
    e = tg_eklemler(vur)
    temas = (e["el1"][0] + 2 * s, e["el1"][1] - 10 * s)
    return TgHareket(an, {"vurus_t": 1.0, "temas": temas, "atan_el": tg_eklemler(atis)["el2"],
                            "tutan_el": tg_eklemler(dur)["el2"], "raket": raket})


def hk_serbest_stil(x0, x1, su_y, s=1.0, kulac=4):
    """
    Serbest stil (yandan): gövde su çizgisinde yatay, yüz suda; kollar sırayla — biri su altında çeker
    (öne → aşağı → kalçaya), öbürü suyun ÜSTÜNDEN öne döner; bacaklar küçük çırpış. x0 → x1.
    Açılar sürekli azalır (−45°/anahtar): toparlanma suyun üstünden geçer, ara değer su altına kaçmaz.
    """
    an = []
    n = kulac * 8 - 5                    # son kare kulaç ortası (Paket 24): i ≡ 3 (mod 8) → yakın kol −45° (suda
                                         # çekişte), uzak kol 135° (suyun üstünde önde, toparlanmada)
    for i in range(n + 1):
        f = i / n
        a = 90 - 45 * i                                   # yakın kol: 90 (öne) → 0 (aşağı) → −90 (kalça) → −180 (üst)…
        cirp = 8 if i % 2 else -8
        p = tg_poz(x0 + (x1 - x0) * f, s=s, g=88, u1=-88 + cirp, b1=-84 + cirp, u2=-88 - cirp, b2=-84 - cirp,
                   a1=-180, a2=-176, k1=a, o1=a - 10, k2=a - 180, o2=a - 190)
        p = dict(p, hy=su_y + 2 * s)
        an.append((f, p))
    return TgHareket(an, {"su_y": su_y})


def hk_split(x, s=1.0, uzaklik=6.0):
    """
    Ön split (yandan): öndeki bacak öne, arkadaki geriye uzanır, gövde dik, kollar yanlarda. Kalça (kasık)
    zeminden `uzaklik` birim yukarıda kalır (0 = tam split). Ayaktan hamle → split; son anahtar = ölçüm anı.
    olay["kasik"]: son karede kasık noktası (ölçü bağı için kalça eklemi).
    """
    dur = tg_poz(x, s=s, k1=20, o1=20, k2=-20, o2=-20)
    hamle = tg_yerlestir(tg_poz(x, s=s, u1=50, b1=10, u2=-40, b2=-70, a2=150, k1=60, o1=70, k2=-60, o2=-70))
    L = (_TG_BOY["uyluk"] + _TG_BOY["baldir"]) * s
    a = _math.degrees(_math.acos(max(0.0, min(1.0, uzaklik / L))))     # bacak açısı: kasık zeminden uzaklik kadar
    split = tg_yerlestir(tg_poz(x, s=s, u1=a, b1=a, u2=-a, b2=-a, a1=180, a2=-180, k1=90, o1=95, k2=-90, o2=-95))
    an = [(0.0, dur), (0.3, hamle), (0.85, split), (1.0, split)]
    return TgHareket(an, {"kasik": tg_eklemler(split)["kalca"], "L": L})


def _hk_iki_bag(kok, uc, L1, L2, isaret=1):
    """
    İki parçalı uzuv için ters kinematik (uyluk–baldır, üst kol–ön kol): kökten uca ulaşan iki açı (0 = aşağı,
    90 = ileri, 180 = yukarı; figür sağa bakar). isaret=+1: orta eklem yukarı/öne (diz yukarı), −1: aşağı/geriye
    (dirsek aşağıda). Uç erişilemiyorsa uzuv o yöne gergin uzanır.
    """
    dx, dy = uc[0] - kok[0], uc[1] - kok[1]
    d = max(1e-6, min(_math.hypot(dx, dy), L1 + L2 - 1e-6))
    th = _math.degrees(_math.atan2(dx, dy))
    al = _math.degrees(_math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))))
    a1 = th + isaret * al
    r = _math.radians(a1)
    ox, oy = kok[0] + _math.sin(r) * L1, kok[1] + _math.cos(r) * L1
    a2 = _math.degrees(_math.atan2(uc[0] - ox, uc[1] - oy))
    return a1, a2


def _hk_oturus(hx, hy, ayak, s, g, el1, el2, a=100):
    """Oturuş pozu: kalça (hx, hy) koltukta, ayaklar `ayak` noktasında (dizler yukarı), eller el1/el2 hedeflerinde."""
    L = _TG_BOY
    u, b = _hk_iki_bag((hx, hy), ayak, L["uyluk"] * s, L["baldir"] * s, 1)
    p = dict(tg_poz(hx, s=s, g=g, u1=u, b1=b, u2=u - 6, b2=b - 6, a1=a, a2=a), hy=hy)   # uzak bacak ayrışık
    boyun = tg_eklemler(p)["boyun"]
    k1, o1 = _hk_iki_bag(boyun, el1, L["ust"] * s, L["on"] * s, -1)
    k2, o2 = _hk_iki_bag(boyun, el2, L["ust"] * s, L["on"] * s, -1)
    return dict(p, k1=k1, o1=o1, k2=k2, o2=o2)


def hk_kurek_ergometre(ayak_x, s=0.7, kulac=2):
    """
    Kürek ergometresi (yandan, sağa bakar): ayaklar ayaklıkta sabit, koltuk rayda kayar. Kulaç: yakalama (dizler
    göğüste, kollar uzun, gövde önde) → itiş (bacaklar) → bitiş (bacaklar gergin, gövde geride, tutamak göğüste)
    → dönüş. Son anahtar = BİTİŞ anı (kulacın ayırt edici konumu). olay: "ayaklik", "tutamak" [(t, x, y)],
    "koltuk" [(t, x, y)] (kalça), "koltuk_y".
    """
    hy = TG_ZEMIN - 16 * s
    ayak = (ayak_x, TG_ZEMIN - 13 * s)
    yakala_x, bitis_x = ayak_x - 25 * s, ayak_x - 44.5 * s
    ust = (_TG_BOY["govde"] + 0) * s

    def omuz(hx, g):
        r = _math.radians(g)
        return hx + _math.sin(r) * ust, hy - _math.cos(r) * ust

    def poz(hx, g, tut):
        return _hk_oturus(hx, hy, ayak, s, g, tut, (tut[0] - 4.5 * s, tut[1] + 3 * s))   # uzak el ayrışık (Paket 25)   # uzak el ayrışık

    sx, sy = omuz(yakala_x, 28)
    yakala = poz(yakala_x, 28, (ayak_x - 3 * s, ayak[1] - 20 * s))
    itis = poz(ayak_x - 36 * s, 22, (ayak_x - 10 * s, ayak[1] - 21 * s))
    bx, by = omuz(bitis_x, -24)
    bitis = poz(bitis_x, -24, (bx + 9 * s, by + 12 * s))
    donus = poz(bitis_x + 3 * s, 20, (ayak_x - 6 * s, ayak[1] - 22 * s))
    an = []
    for i in range(kulac):
        t = i / kulac
        d = 1 / kulac
        an += [(t, yakala), (t + 0.22 * d, itis), (t + 0.45 * d, bitis)]
        if i < kulac - 1:
            an += [(t + 0.7 * d, donus)]
    an[-1] = (1.0, bitis)
    tut, kol = [], []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        tut.append((t, e["el1"][0], e["el1"][1]))
        kol.append((t, p["hx"], p["hy"]))
    return TgHareket(an, {"ayaklik": ayak, "tutamak": tut, "koltuk": kol, "koltuk_y": hy})


def hk_kayak_ergometre(x, s=0.7, kulac=2):
    """
    Kano/kayak ergometresi (yandan, sağa bakar): koltukta oturuş, bacaklar öne uzanık (dizler hafif bükük),
    çift palalı kürek iki elde. Bir yanda yakalama (alttaki el önde-aşağıda, üstteki el baş hizasında), çekiş
    (alttaki el kalçaya, üstteki el öne iter); sonra öbür yan. Son anahtar = YAKALAMA (pala suya girer).
    Üst el yüzün önünde kalır; sap hiçbir karede baş çemberinden geçmez (Paket 25). Gövde çalışır (Paket 27):
    yakalamada öne kapanır (g = 34°), çekişte açılır (g = 6°) — omuz alçalıp yükselir; kalça koltukta kalır.
    olay: "kurek" [(t, x1, y1, x2, y2)] kürek sapı (alt uç → üst uç), "ayaklik", "koltuk_y".
    """
    hy = TG_ZEMIN - 16 * s
    ayak = (x + 40 * s, TG_ZEMIN - 10 * s)
    g_yak, g_cek = 34, 6           # gövde: yakalamada öne kapanır, çekişte açılır (28° aralık; Paket 27)

    def boyun(g):
        r = _math.radians(g)
        return x + _math.sin(r) * _TG_BOY["govde"] * s, hy - _math.cos(r) * _TG_BOY["govde"] * s

    def poz(g, alt, ust, yakin_alt):
        e1, e2 = (alt, ust) if yakin_alt else (ust, alt)
        return _hk_oturus(x, hy, ayak, s, g, e1, e2, a=110)

    bx, by = boyun(g_yak)
    yak_alt, yak_ust = (bx + 26 * s, by + 22 * s), (bx + 18 * s, by - 8 * s)    # üst el yüzün önünde (Paket 25)
    bx, by = boyun(g_cek)
    cek_alt, cek_ust = (bx + 2 * s, by + 25 * s), (bx + 22 * s, by - 2 * s)
    an = []
    yanlar = [True, False] * kulac
    n = len(yanlar)
    for i, yakin in enumerate(yanlar):
        t = i / n
        an += [(t, poz(g_yak, yak_alt, yak_ust, yakin)), (t + 0.6 / n, poz(g_cek, cek_alt, cek_ust, yakin))]
    an.append((1.0, poz(g_yak, yak_alt, yak_ust, True)))
    kurek = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        (ax, ay), (cx, cy) = e["el1"], e["el2"]        # uçlar ellere bağlı: kareler arası uç değiş tokuşu yok
        ux, uy = cx - ax, cy - ay                      # (sıralama değişince sap baştan geçecek biçimde süpürüyordu)
        u = _math.hypot(ux, uy) or 1
        kurek.append((t, ax - ux / u * 24 * s, ay - uy / u * 24 * s, cx + ux / u * 24 * s, cy + uy / u * 24 * s))
    return TgHareket(an, {"kurek": kurek, "ayaklik": ayak, "koltuk_y": hy})


def _hk_bar_uzanis(p, hedef_y, s):
    """Gövde eğimini ayarlayıp kolları düz aşağı uzatarak elleri zemindeki barın yüksekliğine getirir (koparma çıkışı)."""
    en_iyi = None
    for g in range(20, 80):
        q = tg_yerlestir(dict(p, g=g))
        e = tg_eklemler(q)
        a = 8                                            # kollar dik aşağı, hafif öne
        q = dict(q, k1=a, o1=a, k2=a - 2, o2=a - 2)
        y = tg_eklemler(q)["el1"][1]
        if en_iyi is None or abs(y - hedef_y) < en_iyi[0]:
            en_iyi = (abs(y - hedef_y), q)
    return en_iyi[1]


def hk_koparma(x, s=0.6, plaka=7.0):
    """
    Koparma (snatch, yandan): bar yerde (plaka zemine değer), geniş tutuş → çekiş (gövde ve bacaklar açılır,
    parmak ucu) → bar baş üstünde, kollar kilitli, derin çömelişte karşılama. Son anahtar = KARŞILAMA (ayırt
    edici an: tek hareketle yerden baş üstüne). olay["bar"]: [(t, x, y)] bar ekseni (el).
    """
    bas = _hk_bar_uzanis(tg_poz(x, s=s, u1=78, b1=-28, u2=74, b2=-32), TG_ZEMIN - plaka, s)   # diz önde, kalça diz üstünde
    cek = tg_yerlestir(tg_poz(x + 2 * s, s=s, g=-6, u1=8, b1=-6, u2=4, b2=-10, a1=150, a2=150, k1=4, o1=4, k2=2, o2=2))
    karsila = tg_yerlestir(tg_poz(x - 2 * s, s=s, g=22, u1=112, b1=-30, u2=108, b2=-34, k1=-168, o1=-170, k2=-158, o2=-160))
    karsila = _hk_uclari_ayir(karsila, el=(-5.5 * s / 0.6, 0.5), pay=5.0)     # uzak kol görünür (Paket 25)
    an = [(0.0, bas), (0.15, bas), (0.5, cek), (1.0, karsila)]
    bar = [(t, *tg_eklemler(p)["el1"]) for t, p in _tg_kareler(an)]
    return TgHareket(an, {"bar": bar, "plaka": plaka})


def hk_silkme(x, s=0.6):
    """
    Silkme (jerk, yandan): bar omuzda (ön tutuş, dirsekler önde) → çöküş → itiş → makas: ön bacak önde bükük, arka
    bacak geride, bar baş üstünde kollar kilitli. Son anahtar = MAKAS karşılama (ayırt edici an). olay["bar"]: [(t, x, y)].
    """
    def omuzda(p):                                        # ön tutuş: bar boynun önünde, omuz hizasında; dirsek önde
        p = tg_yerlestir(p)
        bx, by = tg_eklemler(p)["boyun"]
        k, o = _hk_iki_bag((bx, by), (bx + 6 * s, by + 3 * s), _TG_BOY["ust"] * s, _TG_BOY["on"] * s, 1)
        return dict(p, k1=k, o1=o, k2=k - 2, o2=o - 2)
    raf = omuzda(tg_poz(x, s=s))
    cok = omuzda(tg_poz(x, s=s, u1=30, b1=-20, u2=26, b2=-24))
    it = tg_yerlestir(tg_poz(x, s=s, u1=4, b1=-4, u2=0, b2=-8, a1=150, a2=150, k1=178, o1=180, k2=176, o2=178))
    makas = tg_yerlestir(tg_poz(x, s=s, g=2, u1=62, b1=8, u2=-38, b2=-62, a2=150, k1=-178, o1=-178, k2=-168, o2=-168))
    makas = _hk_uclari_ayir(makas, el=(-5.5 * s / 0.6, 0.5), pay=5.0)         # uzak kol görünür (Paket 25)
    an = [(0.0, raf), (0.2, raf), (0.45, cok), (0.65, it), (1.0, makas)]
    bar = []
    for t, p in _tg_kareler(an):
        e = tg_eklemler(p)
        bar.append((t, e["el1"][0], e["el1"][1]))
    return TgHareket(an, {"bar": bar})


def hk_eggbeater_sicrama(x, su_y, s=0.6, bekle=4):
    """
    Suda dikey sıçrama (su topu, yandan): derin suda dik; bekleme sırasında bacaklar sırayla dairesel çırpar
    (eggbeater), eller suyu yanlara iter; "git" ile bacak ve kol itişiyle yükselir, yakın kol yukarı uzanır.
    Son anahtar = TEPE (ölçüm anı: elin su yüzeyinden yüksekliği). olay["el"]: son karede uzanan elin ucu.
    """
    hy0 = su_y + 24 * s
    an = []
    for i in range(bekle):
        a = 25 if i % 2 else -15
        p = dict(tg_poz(x, s=s, g=6, u1=78, b1=a, u2=74, b2=-a + 10, a1=150, a2=150,
                        k1=70 + a / 2, o1=95, k2=60 - a / 2, o2=88), hy=hy0)
        an.append((0.45 * i / (bekle - 1), p))
    cok = dict(tg_poz(x, s=s, g=8, u1=95, b1=-30, u2=90, b2=-34, a1=150, a2=150, k1=40, o1=70, k2=36, o2=66), hy=hy0 + 3 * s)
    tepe = dict(tg_poz(x, s=s, g=-2, u1=20, b1=-6, u2=10, b2=-16, a1=170, a2=170, k1=176, o1=178, k2=40, o2=20),
                hy=su_y + 2 * s)
    an += [(0.6, cok), (1.0, tepe)]
    return TgHareket(an, {"el": tg_eklemler(tepe)["el1"], "su_y": su_y})


def hk_tutus(x, yon=1, s=1.0, adim=6, tur=3):
    """Karşılıklı tutuş (güreş duruşu): gövde öne eğik, eller rakibin ense/omzunda; küçük yan adımlarla döner."""
    an = []
    for i in range(tur + 1):
        f = 1 if i % 2 else -1
        p = tg_yerlestir(tg_poz(x + f * adim * (i > 0), s=s, yon=yon, g=38, u1=30 + 6 * f, b1=-22, u2=-14 - 6 * f, b2=-30,
                                k1=95, o1=110, k2=80, o2=96))
        an.append((i / tur, p))
    return TgHareket(an, {})


# ── 3) SAHNELER: hareket + ekipman + ölçülen büyüklük + en çok üç yazı ──
def _tg_parabol(x0, y0, x1, y1, tepe, t0, t1, n=10):
    return [(t0 + (t1 - t0) * i / n, x0 + (x1 - x0) * i / n,
             y0 + (y1 - y0) * i / n - 4 * tepe * (i / n) * (1 - i / n)) for i in range(n + 1)]


def _tg_direk(S, x, alt=3):
    """Zemin çizgisini kesen kısa çizgi (başlangıç/dönüş çizgisi): alt şeride girmez."""
    S.esya(S.cizgi(x, TG_ZEMIN - 5, x, TG_ZEMIN + alt, tur="figur"))


def _tg_boy():
    S = TgSahne(2.6)
    S.esya(S.kutu(86, 21, 5, TG_ZEMIN - 21, rx=1) + "".join(S.cizgi(91, y, 94, y) for y in range(30, TG_ZEMIN, 10)))
    S.esya(S.kutu(96, TG_ZEMIN - 4, 40, 4))
    h = hk_antropometri(106)
    e = S.figur(h)
    ust = e["bas_ust"][1]
    S.kaydir(S.cizgi(86, ust - 1.6, 124, ust - 1.6, tur="figur"), [(0, 0, -9), (0.15, 0, -9), (0.5, 0, 0), (1, 0, 0)])
    S.baslik("Topuk, kalça, sırt ve baş aynı dikeyde")
    S.olcu(150, TG_ZEMIN, 150, ust, "Boy (cm)", t=0.55, kilavuzlar=[(124, ust, 150, ust)],
           bag=[(1, "y", ("bas_ust",), "min")])
    S.not_("Derin nefes alıp tutarken ölçülür · tartı: kg", t=0.7)
    return S


def _tg_oturma(baslik="Dizler 90°, gözler karşıya", notu="Oturma yüzeyinden başın üstüne"):
    S = TgSahne(2.4)
    oturak = TG_ZEMIN - 23
    S.esya(S.kutu(60, oturak, 32, TG_ZEMIN - oturak))
    S.esya(S.kutu(54, 21, 4, TG_ZEMIN - 21, rx=1))
    h = hk_antropometri(70, "oturarak", oturak_y=oturak)
    e = S.figur(h)
    ust = e["bas_ust"][1]
    S.kaydir(S.cizgi(54, ust - 1.6, 92, ust - 1.6, tur="figur"), [(0, 0, -9), (0.15, 0, -9), (0.5, 0, 0), (1, 0, 0)])
    S.baslik(baslik)
    S.olcu(126, oturak, 126, ust, "Oturma yüksekliği", t=0.55,
           kilavuzlar=[(92, oturak, 126, oturak), (92, ust, 126, ust)], bag=[(1, "y", ("bas_ust",), "min")])
    S.not_(notu, t=0.7)
    return S


def _tg_kulac():
    S = TgSahne(2.4)
    S.esya(S.cizgi(70, 34, 190, 34) + "".join(S.cizgi(x, 34, x, 37) for x in range(70, 191, 10)))
    h = hk_antropometri(130, "kulac")
    S.figur(h)
    (sx, sy), (dx, dy) = h.olay["eller"]
    S.baslik("Kollar yere paralel, avuç içleri karşıya")
    S.olcu(sx, 22, dx, 22, "Kulaç", t=0.65, kilavuzlar=[(sx, sy - 2, sx, 22), (dx, dy - 2, dx, 22)],
           bag=[(0, "x", ("el1", "el2"), "min"), (1, "x", ("el1", "el2"), "max")])
    S.not_("İki orta parmak ucu arası (cm)", t=0.7)
    return S


def _tg_esneklik():
    S = TgSahne(3.2)
    z = TG_ZEMIN
    S.esya(S.kutu(170, z - 20, 50, 20))
    S.esya(S.cizgi(160, z - 21, 240, z - 21) + "".join(S.cizgi(x, z - 24, x, z - 21) for x in range(164, 240, 6)))
    h = hk_oturarak_uzanma(170)
    S.figur(h)
    el = h.olay["el"][0]
    S.kaydir(S.kutu(176, z - 28, 5, 7, dolgu="yuzey", rx=1),
             [(0, 0, 0), (0.45, 0, 0), (0.8, el - 178.5, 0), (1, el - 178.5, 0)])
    S.baslik("Ayak tabanı sehpaya dayalı, dizler gergin")
    S.isaret("Cetvelin itildiği nokta", (el, z - 28), (el + 4, 52), hiza="start", t=0.82)
    S.not_("Sıfır noktası: TSYT sehpasının kendi cetveli", t=0.82)
    return S


def _tg_dikey():
    S = TgSahne(2.8)
    S.esya(S.kutu(92, TG_ZEMIN - 3, 48, 3))
    h = hk_dikey_sicrama(116, yukselme=20, s=0.75)
    e = S.figur(h)
    ayaklar = ("ayak1", "ayak2", "parmak1", "parmak2")
    tepe = max(e[k][1] for k in ayaklar)              # son karede (tepe) en alttaki ayak noktası
    ayak_x = max(e[k][0] for k in ayaklar)
    S.baslik("Kollar serbest, beklemeden çök ve sıçra")
    S.olcu(152, TG_ZEMIN, 152, tepe, "Sıçrama yüksekliği", t=0.95, kilavuzlar=[(ayak_x + 2, tepe, 152, tepe)],
           bag=[(1, "y", ayaklar, "max")])
    S.not_("Aynı noktaya, dizler gergin in", t=0.95)
    return S


def _tg_kavrama(baslik="Ayakta, kol gergin ve aşağıda", isaret="Olanca kuvvetle sık (kg)",
                notu="Her el bir kez, tek ölçüm"):
    S = TgSahne(2.6)
    h = hk_kavrama(118)
    S.figur(h)
    x, y = h.olay["el"]
    S.belir(f'<rect x="{x - 4:.1f}" y="{y - 7:.1f}" width="8" height="14" rx="2.5" fill="{TG_RENK["yuzey"]}" '
            f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>', 0.45)
    S.belir("".join(S.cizgi(x + 7 + i * 3, y - 4 - i, x + 7 + i * 3, y + 4 + i, "olcu") for i in range(2)), 0.85,
            tur="isaret")
    S.baslik(baslik)
    S.isaret(isaret, (x + 4, y), (x + 34, y - 30), hiza="start", t=0.85)
    S.not_(notu, t=0.85)
    return S


def _tg_saglik_topu():
    S = TgSahne(3.0)
    _tg_direk(S, 80)
    h = hk_atma(72, "geriye", yon=-1, s=0.85)
    S.figur(h)
    (_, x0, y0) = h.olay["el_yolu"][-1]
    dusus = 176
    ucus = _tg_parabol(x0, y0, dusus, TG_ZEMIN - 4, 16, h.olay["birakma_t"], 0.92)
    S.top(h.olay["el_yolu"] + ucus[1:])
    iz = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (_, x, y) in enumerate(ucus))
    S.belir(f'<path d="{iz}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
            f'stroke-dasharray="2 2"/>' + S.nokta(dusus, TG_ZEMIN - 1, 2.2), 0.93, tur="isaret")
    S.baslik("Sırt atış alanına dönük, atış çizgisinde")
    S.olcu(80, TG_OLCU_Y, dusus, TG_OLCU_Y, "Atış mesafesi", uc="son", t=0.93)
    S.not_("Baş üzerinden geriye, yaklaşık 45° ile", t=0.6)
    return S


def _tg_pro_agility():
    S = TgSahne(4.2)
    for x in (55, 130, 205):
        _tg_direk(S, x)
    h = hk_donuslu_kos([130, 205, 55, 150], s=0.8)
    S.figur(h)
    for t, x in h.olay["dokunma"]:
        S.belir(S.nokta(x, TG_ZEMIN, 3.2), t, tur="isaret")
    S.baslik("Orta → 4,57 m → 9,14 m → orta (18,28 m)")
    S.olcu(55, TG_OLCU_Y, 130, TG_OLCU_Y, "4,57 m", uc="ilk", metre=4.57)
    S.olcu(130, TG_OLCU_Y, 205, TG_OLCU_Y, es=0, metre=4.57)
    S.not_("Her dönüşte çizgiye elle dokun", t=0.3)
    return S


def _tg_surat():
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_surat"][0]              # 1 m (20 m = 190 birim)
    cizgi_x, f1, f2 = 25, 25 + m, 25 + 21 * m
    _tg_direk(S, cizgi_x)
    for x in (f1, f2):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    S.esya(S.cizgi(cizgi_x, TG_OLCU_Y, f1, TG_OLCU_Y, "olcu"), tur="isaret")
    h = hk_duz_kos(17, f2 + 3, s=0.8, bitis_x=f2)       # ön ayak ucu çıkış çizgisinde
    S.figur(h)
    S.baslik("Çıkış çizgisi, başlangıç fotoselinin 1 m gerisi")
    S.olcu(f1, 30, f2, 30, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(f1, TG_ZEMIN - 28, f1, 30), (f2, TG_ZEMIN - 28, f2, 30)])
    S.not_("Bitiş fotoselini yavaşlamadan geç", t=0.8)
    return S


def _tg_koordinasyon_genel():
    """Koordinasyon Parkuru — GENEL GÖRÜNÜM (durağan kopya): dokuz istasyon yan yana, sıra numaralı."""
    S = TgSahne(4.6)
    y = TG_ZEMIN
    k = TG_KALINLIK["esya"]
    S.esya(S.kutu(22, y - 3, 18, 3)                                                       # takla minderi
           + S.kutu(44, y - 6, 22, 3) + S.cizgi(46, y - 3, 46, y) + S.cizgi(64, y - 3, 64, y)   # denge tahtası
           + S.cizgi(72, y, 72, y - 48) + S.cizgi(84, y, 84, y - 48) + S.cizgi(72, y - 48, 84, y - 48)  # yüksek engel
           + "".join(f'<ellipse cx="{x}" cy="{y - 1}" rx="4" ry="1.6" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
                     for x in (94, 102, 110))                                             # sekme çemberleri
           + "".join(f'<circle cx="{x}" cy="{y - 4}" r="3" fill="none" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
                     for x in (122, 134, 146))                                            # top yer değiştirme
           + S.kutu(156, y - 50, 4, 50, rx=0.8)                                              # duvar
           + "".join(S.cizgi(x, y, x, y - hh) + S.cizgi(x, y - hh, x + 4, y - hh)
                     for x, hh in ((168, 30), (175, 15), (182, 30), (189, 15)))           # alttan-üstten
           + "".join(S.cizgi(x, y, x, y - 22) for x in (202, 208, 214, 220)))             # slalom
    for x in (12, 230):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    # istasyon sırası (protokol 2-10. adımlar): takla, denge, engel üstünden top, sekme, elle top, ayakla top,
    # duvara top, alttan-üstten, slalom. Elle ve ayakla yer değiştirme aynı düzeneği paylaşır (5 ve 6).
    for n, x in enumerate((31, 55, 78, 102, 128, 140, 158, 178, 211), 1):
        S.numara(x, 56 if n != 6 else 46, n)
    h = hk_duz_kos(22, 228, s=0.55, cikis_t=0.04, bitis_x=230)
    S.figur(h)
    S.baslik("Dokuz istasyon, tek parkur")
    S.olcu(12, 30, 230, 30, "Süre", etiket_yer="orta", kilavuzlar=[(12, TG_ZEMIN - 28, 12, 30), (230, TG_ZEMIN - 28, 230, 30)])
    S.not_("Hatalı istasyon yeniden yapılır (süre cezası yok)", t=0.05)
    return S


def _tg_cember(x, y, r):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="1.6" fill="none" stroke="{TG_RENK["esya"]}" '
            f'stroke-width="{TG_KALINLIK["esya"]}"/>')


def _tg_koordinasyon():
    """
    Koordinasyon Parkuru (TSYT) — KAYAN SAHNE (Paket 21). Parkur tuvalden geniş çizilir ve bir grup olarak sola
    kayar; figür tuvalin ortasına yakın kalır ve yanından geçen istasyonun hareketini yapar (sıra protokolden,
    hk_koordinasyon_turu). Başlık, not, istasyon numarası ve süreölçer sabit katmanda — parkurla kaymaz.
    Durağan kopya BİLEREK farklı: genel görünüm, dokuz istasyon numaralı (_tg_koordinasyon_genel).
    """
    m = TG_OLCEK["_tg_koordinasyon"][0]
    h = hk_koordinasyon_turu(x_c=118, s=0.7, m=m)
    o, ek, Z = h.olay, h.olay["ekipman"], TG_ZEMIN
    S = TgSahne(o["sure"])
    r = 0.3 * m                                                          # 60 cm çember
    xml = "".join(S.kutu(x - 1.5, Z - 26, 3, 26, dolgu="yuzey", rx=0.8) for x in (ek["baslangic"], ek["bitis"]))
    a, b = ek["minder"]
    xml += S.kutu(a, Z - 3, b - a, 3)                                                    # 1 minder
    a, b, ust = ek["denge"]
    xml += (S.kutu(a, ust, b - a, Z - ust, rx=0.6)                                       # 2 denge tahtası
            + "".join(S.cizgi(x, ust - 2, x, ust, "olcu") for x in (a + 0.3 * m, b - 0.3 * m)))  # 30 cm bölgeler
    ex, eh = ek["engel_ust"]
    xml += S.cizgi(ex - 6, Z, ex - 6, Z - eh) + S.cizgi(ex + 6, Z, ex + 6, Z - eh) + S.cizgi(ex - 6, Z - eh, ex + 6, Z - eh)
    xml += _tg_cember(ek["cember3"], Z - 1, r)                                          # 3 topun çemberi
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["sekme"])                          # 4 sekme çemberleri
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["el_cember"] + ek["ayak_cember"])  # 5-6
    xml += S.kutu(ek["duvar"], Z - 1.6 * m, 4, 1.6 * m, rx=0.8)                          # 7 duvar
    xml += "".join(_tg_cember(x, Z - 1, r) for x in ek["duvar_cember"])
    for x, hh in ek["alttan_ustten"]:                                                    # 8 alttan-üstten
        xml += S.cizgi(x - 5, Z, x - 5, Z - hh) + S.cizgi(x + 5, Z, x + 5, Z - hh) + S.cizgi(x - 5, Z - hh, x + 5, Z - hh)
    xml += "".join(S.cizgi(x, Z, x, Z - 0.9 * m) for x in ek["slalom"])                   # 9 slalom
    S.kaydir(xml, [(t, dx, 0) for t, dx in o["kayma"]])
    for yol in o["toplar"]:
        S.top(yol, r=2.2)
    S.figur(h, donus=o["donus"])
    S.istasyon_araliklari = [(a, b) for _, a, b in o["istasyonlar"]]
    S.parkur_kaymasi = list(o["kayma"])
    for n, t0, t1 in o["istasyonlar"]:                                                  # sabit katman
        S.numara(22, 32, n, t0, t_bitis=t1)
    S.kronometre(238, 34, t0=o["istasyonlar"][0][1] * 0.5)
    S.baslik_nobet("Dokuz istasyon sırayla, tek parkur",                # istasyon adı başlık yerinde (Paket 25)
                   [(ad, t0, t1) for ad, (_, t0, t1) in zip(o["istasyon_adlari"], o["istasyonlar"])])
    S.not_("Hatalı istasyon yeniden yapılır (süre cezası yok)", t=0.02)
    S.duragan = _tg_koordinasyon_genel()
    return S


def _tg_mekik(baslik="Her sinyalde karşı çizgiye", notu="Sinyali iki kez üst üste kaçıran bitirir"):
    """20 m mekik (TSYT; Eurofit/Léger, PACER, ALPHA, PREFIT, CAPL aynı çizim — etiket protokolün kendisinden)."""
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_mekik"][0]
    a, b = 30, 30 + 20 * m
    for x in (a, b):
        _tg_direk(S, x)
    h = hk_donuslu_kos([a, b, a + 4], s=0.8, dokun=False, baslangic="kos")
    S.figur(h)
    for t, x in ((0.5, b), (0.98, a)):     # sinyal anı: çizgide küçük ses dalgası
        S.belir("".join(f'<path d="M{x - 6 - 3 * i:.1f},{56 - 2 * i} q{-3 - i},{4 + 2 * i} 0,{8 + 4 * i}" fill="none" '
                        f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>' for i in range(2)), t,
                tur="isaret")
    S.baslik(baslik)
    S.olcu(a, 30, b, 30, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(a, TG_ZEMIN - 7, a, 30), (b, TG_ZEMIN - 7, b, 30)])
    S.not_(notu, t=0.05)
    return S


def _tg_geriye_denge(tur="kiris_geriye", baslik="Kiriş üzerinde geriye doğru, en çok 8 adım",
                     notu="Kiriş 3 m · genişlik 6 / 4,5 / 3 cm"):
    """Kirişte yürüme: KTK geriye; KMS balans öne (tur="kiris_ileri")."""
    S = TgSahne(3.6)
    taban = TG_ZEMIN - 10
    S.esya(S.kutu(26, taban, 208, 5, rx=0.8) + S.kutu(36, taban + 5, 6, 5, rx=0.5) + S.kutu(218, taban + 5, 6, 5, rx=0.5))
    h = hk_denge(tur, 60, 170, taban=taban, s=0.85)
    S.figur(h)
    for i, x in enumerate(h.olay["adimlar"][1:], 1):
        S.belir(S.cizgi(x, taban - 2, x, taban + 2, "olcu"), i / 6, tur="isaret")
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_yana_sicrama(baslik="Çift ayakla sağa-sola, 15 sn", isaret="Çıtanın üzerinden",
                     notu="2 deneme · çıtaya basmak, tek ayakla inmek geçersiz"):
    """Yana sıçrama (KTK3+; KMS aynı çizim, etiket kendi protokolünden)."""
    S = TgSahne(3.2)
    S.esya(S.kutu(80, TG_ZEMIN - 3, 100, 3) + S.kutu(128.5, TG_ZEMIN - 8, 3, 5, rx=0.5))
    h = hk_yana_sicrama(112, 148, s=0.85)
    S.figur(h)
    _tg_periyot_seridi(S, [(15, True), (None, None), (15, True)], x0=12, y=22, olcek=2.0)
    S.baslik(baslik)
    S.isaret(isaret, (130, TG_ZEMIN - 8), (176, 86), hiza="start", t=0.05)
    S.not_(notu, t=0.5)
    return S


def _tg_yana_platform():
    S = TgSahne(3.8)
    yuk = 7

    def platform(x):
        return (S.kutu(x, TG_ZEMIN - yuk, 22, 4, dolgu="yuzey", rx=1)
                + S.cizgi(x + 3, TG_ZEMIN - 3, x + 3, TG_ZEMIN) + S.cizgi(x + 19, TG_ZEMIN - 3, x + 19, TG_ZEMIN))
    S.esya(platform(122))
    h = hk_denge("platform", 103, taban=TG_ZEMIN - yuk, s=0.85)
    S.kaydir(platform(92), h.olay["platform"])
    S.figur(h)
    _tg_periyot_seridi(S, [(20, True), (None, None), (20, True)], x0=12, y=22, olcek=1.6)
    S.baslik("20 sn: boştaki platformu yana koy, üstüne bas")
    S.isaret("Koy + bas = puan", (174, TG_ZEMIN - yuk), (200, 60), hiza="start", t=0.62)
    S.not_("2 deneme · yön serbest, hep aynı yöne", t=0.05)
    return S


def _tg_goz_el():
    S = TgSahne(3.8)
    m = TG_OLCEK["_tg_goz_el"][0]            # 1 m (0,66 ölçekli çocuğa göre)
    duvar = 231                              # duvar yüzü
    S.esya(S.kutu(duvar + 1, 21, 6, TG_ZEMIN - 21, rx=0.8))
    S.esya(f'<line x1="{duvar}" y1="{TG_ZEMIN - m}" x2="{duvar}" y2="{TG_ZEMIN - 2 * m}" stroke="{TG_RENK["olcu"]}" '
           f'stroke-width="{TG_KALINLIK["vurgu"]}" stroke-linecap="round"/>')
    ayaklar = ("ayak1", "ayak2", "parmak1", "parmak2")
    h = hk_atma(duvar - m - 10, "duvara", s=0.66, on_ayak_x=duvar - m)      # en öndeki ayak ucu duvardan 1 m geride
    e = S.figur(h)
    on = max(e[k][0] for k in ayaklar)
    el = h.olay["tut"]
    hedef = (duvar - 2, TG_ZEMIN - 1.5 * m)
    yol = [(0, *el)]
    for b0 in (0.12, 0.54):
        yol += [(b0, *el), (b0 + 0.12, *hedef), (b0 + 0.3, *el)]
    S.top(yol, r=3.2)
    S.esya(S.cizgi(246, TG_ZEMIN, 246, TG_ZEMIN - m, "olcu", kesik=True), tur="isaret")
    _tg_periyot_seridi(S, [(30, True), (None, None), (30, True)], x0=12, y=22, olcek=1.2)
    S.baslik("30 sn: kareye at, sektikten sonra yakala")
    oy = TG_ZEMIN - 30                       # duvar ile ayak ucu arası boşlukta, kılavuzla zemine bağlı
    S.olcu(on, oy, duvar, oy, "1 m", etiket_yer="orta", etiket_dx=8, metre=1, kilavuzlar=[(on, TG_ZEMIN - 1, on, oy)],
           bag=[(0, "x", ayaklar, "max")])
    S.not_("Hedef kare 1 × 1 m, alt kenarı yerden 1 m")
    return S


def _tg_tek_ayak():
    S = TgSahne(3.4)
    for i in range(3):
        S.esya(S.kutu(124, TG_ZEMIN - 3.5 * (i + 1), 14, 3.5, rx=0.6))
    h = hk_tek_ayak_sekme(96, 131, s=0.8, adim=12, yukselme=20)
    S.figur(h)
    iz = h.olay["iz"]
    S.belir(f'<path d="M{iz[0][0]:.1f},{iz[0][1]:.1f} Q{iz[1][0]:.1f},{iz[1][1] - 18:.1f} {iz[2][0]:.1f},{iz[2][1]:.1f}" '
            f'fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.45,
            tur="isaret")
    S.baslik("Tek ayak; diğer ayak yere değmez")
    S.isaret("5'er cm sünger blok", (131, TG_ZEMIN - 10.5), (70, 70), hiza="end", t=0.05)
    S.not_("İnişten sonra aynı ayakla en az 2 sıçrama", t=0.5)
    return S


# ── Branşa özgü sahneler (Paket 15-16) ──
def _tg_periyot_seridi(S, parcalar, x0=20, y=20, olcek=1.0, t=0.0, imlec=None):
    """
    Zaman çubuğu: protokolün aralık yapısı tek şeritte. parcalar [(süre, aktif_mi[, yükseklik])] — aktif dolu,
    dinlenme açık kutu; (None, None) = süresi protokolde verilmeyen ara (kesik bağ); yükseklik (≤ 2) blokları
    yukarı doğru büyütür (30-15 IFT'de artan hız). Yazı içermez.
    imlec: [(t, oran)] — şeridin altındaki küçük üçgen bu anlarda şeridin bu oranındadır (hareketle eşleşir).
    Döndürür (x0, x1, y, aktif_bloklar[(xa, xb)]).
    """
    xml, x, bloklar = "", x0, []
    for parca in parcalar:
        sure, aktif = parca[0], parca[1]
        oran = parca[2] if len(parca) > 2 else 1.0     # (süre, aktif, yükseklik oranı): artımlı hız basamağı
        if sure is None:
            xml += (f'<line x1="{x + 1:.1f}" y1="{y + 3}" x2="{x + 7:.1f}" y2="{y + 3}" stroke="{TG_RENK["olcu"]}" '
                    f'stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="1.5 1.5"/>')
            x += 8
            continue
        w = sure * olcek
        hh = 6 * oran
        xml += (f'<rect x="{x:.1f}" y="{y + 6 - hh:.1f}" width="{w:.1f}" height="{hh:.1f}" rx="1" '
                f'fill="{TG_RENK["olcu"] if aktif else TG_RENK["yuzey"]}" stroke="{TG_RENK["yuzey"] if aktif else TG_RENK["olcu"]}" '
                f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
        if aktif:
            bloklar.append((x, x + w))
        x += w
    S.belir(xml, t)
    if imlec:
        uc = f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>'
        S.kaydir(uc, [(tt, (x - x0) * o, 0) for tt, o in imlec], tur="isaret")
    S.zaman_seritleri.append((x0, x, y))
    return x0, x, y, bloklar


def _tg_yoyo(brans="", surum="IR1"):
    """
    Yo-Yo IR1 ve IR2 — bütün branşlar aynı sahneyi kullanır; branş adı yalnız başlıkta. IR2 farkı yalnız notta:
    protokolde dinlenme aynı (10 sn aktif), başlangıç hızı yüksek (13 km/h).
    """
    S = TgSahne(4.6)
    m = TG_OLCEK["_tg_yoyo"][0]
    bas_x, dinlenme_x, uzak_x = 60, 60 - 5 * m, 60 + 20 * m
    for x in (dinlenme_x, bas_x, uzak_x):
        S.esya(f'<path d="M{x - 3.5:.1f},{TG_ZEMIN} L{x:.1f},{TG_ZEMIN - 9} L{x + 3.5:.1f},{TG_ZEMIN} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.esya(S.cizgi(dinlenme_x, TG_OLCU_Y, bas_x, TG_OLCU_Y, "kilavuz"), tur="isaret")   # 5 m dinlenme alanı
    s = 0.8
    mekik = hk_donuslu_kos([bas_x, uzak_x - 4, bas_x + 2], s=s, dokun=False, baslangic="kos", t1=0.72)
    dinlenme = hk_donuslu_kos([bas_x + 2, dinlenme_x + 4, bas_x], s=s, dokun=False, baslangic="kos", t0=0.74)
    S.figur(TgHareket(mekik.anahtarlar + dinlenme.anahtarlar, {}))
    for t, x in ((0.36, uzak_x), (0.72, bas_x)):
        S.belir("".join(f'<path d="M{x - 6 - 3 * i:.1f},{50 - 2 * i} q{-3 - i},{4 + 2 * i} 0,{8 + 4 * i}" fill="none" '
                        f'stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["olcu"]}"/>' for i in range(2)), t,
                tur="isaret")
    # şematik şerit: koşu blokları bip hızlandıkça kısalır, her koşudan sonra eşit dinlenme bloğu
    kosular = [16, 14, 12.5, 11, 10, 9]
    parca = [p for k in kosular for p in ((k, True), (10, False))]
    toplam = sum(k for k, _ in parca)
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.8,
                       imlec=[(0, 0), (0.72, kosular[0] / toplam), (1.0, (kosular[0] + 10) / toplam)])
    S.baslik(f"{brans} · Bip sesiyle 20 m çift yön koşu" if brans else "Bip sesiyle 20 m çift yön koşu")
    S.olcu(bas_x, TG_OLCU_Y, uzak_x, TG_OLCU_Y, "20 m", uc="son", metre=20)
    S.not_("Her turda 10 sn aktif dinlenme (5 m gidip gelme)" if surum == "IR1"
           else "Başlangıç 13 km/h · her turda 10 sn aktif dinlenme", t=0.72)
    return S


def _tg_imlec_atis(atislar, bloklar, x0, x1):
    """Zaman çubuğu imleci: her atış, sırasıyla bir aktif bloğun sonuna denk gelir."""
    uz = (x1 - x0) or 1
    an = [(0.0, 0.0)]
    for t, (xa, xb) in zip(atislar, bloklar):
        an.append((t, (xb - 2 - x0) / uz))
    if an[-1][0] < 1:
        an.append((1.0, 1.0))
    return an


def _tg_swft():
    """SWFT: suplex (geriye köprüyle sırtüstü devirme); ölçülen = TOPLAM atış (tek sayaç)."""
    S = TgSahne(6.0)
    S.esya(S.kutu(96, TG_ZEMIN - 3, 152, 3, rx=1))
    h = hk_atma(176, "suplex", tekrar=3)
    S.figur(h.olay["partner"])
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(30, True), (20, False), (30, True), (20, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.8, imlec=None)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    sx0, sy0, sx1, sy1 = S.sayac(44, 60, atis, boy=20)
    S.baslik("Manken suplex tekniğiyle sırtüstü devrilir")
    S.isaret("Toplam atış sayısı", ((sx0 + sx1) / 2, sy0), (12, 50), hiza="start", t=atis[0])
    S.not_("3 × 30 sn aktif, aralarında 20 sn pasif dinlenme")
    return S


def _tg_sjft():
    """Modified SJFT: öne devirme (manken sırttan öne); ölçülen = HER PERİYOTTA atış (periyot başına sayaç)."""
    S = TgSahne(6.0)
    S.esya(S.kutu(60, TG_ZEMIN - 3, 188, 3, rx=1))
    h = hk_atma(170, "one", tekrar=3)
    S.figur(h.olay["partner"])
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(15, True), (10, False), (30, True), (10, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=1.2, imlec=None)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(atis, bloklar):
        S.sayac((xa + xb) / 2 - 7, 36, [t], boy=14)
    S.baslik("Her periyotta manken en çok sayıda devrilir")
    ilk = S.sayaclar[0]
    S.isaret("Periyot başına atış", ((ilk[0] + ilk[2]) / 2, ilk[3]), (12, 76), hiza="start", t=atis[0])
    S.not_("15 sn / 30 sn / 30 sn, aralarında 10 sn dinlenme")
    return S


def _tg_gures_mac():
    return _tg_mac([(60, True), (10, False), (60, True)], 0.7, "Eşit ağırlık kategorisinde iki sporcu",
                   "2 × 3 dk, 30 sn ara", "Her periyot sonunda KAH ve RPE (Borg)")


def _tg_paten_30():
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_paten_30"][0]
    x0, x1 = 28, 28 + 30 * m
    for x in (x0, x1):
        _tg_direk(S, x)
    S.figur(hk_paten(x0 - 6, x1, s=0.8))
    S.baslik("Durarak başlangıç, 30 m maksimal hız")
    S.olcu(x0, 30, x1, 30, "30 m", etiket_yer="orta", metre=30, kilavuzlar=[(x0, TG_ZEMIN - 7, x0, 30), (x1, TG_ZEMIN - 7, x1, 30)])
    S.not_("3 deneme, en iyi süre kaydedilir", t=0.8)
    return S


def _tg_paten_6_30():
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_paten_6_30"][0]
    x0, x6, x30 = 28, 28 + 6 * m, 28 + 30 * m
    for x in (x0, x6, x30):
        S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))
    S.figur(hk_paten(x0 - 6, x30, s=0.8))
    S.baslik("Durarak başlangıç; fotosel 6. ve 30. metrede")
    S.olcu(x0, 52, x6, 52, "6 m", uc="son", metre=6, kilavuzlar=[(x0, TG_ZEMIN - 28, x0, 52), (x6, TG_ZEMIN - 28, x6, 52)])
    S.olcu(x0, 30, x30, 30, "30 m", etiket_yer="orta", metre=30, kilavuzlar=[(x0, 52, x0, 30), (x30, TG_ZEMIN - 28, x30, 30)])
    return S


def _tg_s_turn():
    """
    S-Turn (yandan): buz yüzeyi zemin çizgisinin gerisinde ince bir şerit (derinlik). Koniler şeridin ortasında,
    güzergâh konilerin bir önünden bir arkasından geçer; figürün ayakları her karede güzergâhın üzerindedir.
    """
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_s_turn"][0]
    arka, orta, sapma = TG_ZEMIN - 18, TG_ZEMIN - 9, 6   # buz şeridi derinliği: arka, orta (koniler), ön = zemin
    koniler = [48 + i * 3 * m for i in range(5)]
    bas_x, bit_x = 22, koniler[-1] + 40
    for x in (bas_x, bit_x):                              # başlangıç/bitiş: buzdaki çizgi (derinliğe yatık)
        S.esya(S.cizgi(x + 3, arka + 1, x - 3, TG_ZEMIN - 1, tur="esya"))
    noktalar = ([(bas_x, orta)] + [(x, orta + (sapma if i % 2 == 0 else -sapma)) for i, x in enumerate(koniler)]
                + [(bit_x, orta)])
    h = hk_kavisli_yol(noktalar, s=0.5, kip="paten")
    S.yol(h.olay["yol"])
    for i, x in enumerate(koniler):                        # koni: yolun yanında (önden geçilen koni yoldan önce çizilir)
        S.esya(f'<path d="M{x - 3:.1f},{orta + 1} L{x:.1f},{orta - 7} L{x + 3:.1f},{orta + 1} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(h)
    S.baslik("5 koni S şeklinde, 3 m aralıkla")
    S.olcu(koniler[0], TG_OLCU_Y, koniler[1], TG_OLCU_Y, "3 m", uc="son", metre=3,
           kilavuzlar=[(koniler[0], orta + 2, koniler[0], TG_OLCU_Y), (koniler[1], orta + 2, koniler[1], TG_OLCU_Y)])
    S.not_("3 deneme, en iyi süre kaydedilir", t=0.8)
    return S


def _tg_wingate(brans=""):
    """Wingate: ergometrede oturarak 30 sn maksimal pedal; direnç vücut ağırlığının %7,5'i. Branş adı yalnız başlıkta."""
    S = TgSahne(3.0)
    h = hk_pedal(110, s=0.85, tur=6)
    o = h.olay
    (cx, cy), (sx, sy), (gx, gy) = o["krank"], o["sele"], o["gidon"]
    k = TG_KALINLIK["esya"]
    volan = (cx + 34, cy - 6)
    S.esya(S.cizgi(cx - 34, TG_ZEMIN - 2, cx + 52, TG_ZEMIN - 2)                        # taban
           + S.cizgi(cx - 26, TG_ZEMIN - 2, sx - 2, sy + 4) + S.cizgi(sx - 8, sy + 2, sx + 6, sy + 2)   # sele borusu
           + S.cizgi(cx, cy, volan[0], volan[1]) + S.cizgi(volan[0], volan[1], volan[0] + 6, TG_ZEMIN - 2)
           + S.cizgi(sx + 2, sy + 10, gx, gy + 18) + S.cizgi(gx, gy + 18, gx, gy) + S.cizgi(gx - 4, gy, gx + 3, gy)
           + f'<circle cx="{volan[0]:.1f}" cy="{volan[1]:.1f}" r="13" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{k}"/>'
           + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.2" fill="{TG_RENK["esya"]}"/>')
    S.figur(h)
    _tg_periyot_seridi(S, [(30, True)], x0=12, y=22, olcek=3.0, imlec=[(0, 0), (1, 1)])
    S.baslik(f"{brans} · 30 sn oturarak maksimal pedal" if brans else "30 sn oturarak maksimal pedal")
    S.not_("Direnç: vücut ağırlığının %7,5'i")
    return S


# ── Branşa özgü sahneler, 2. parti (Paket 17): Futbol, Voleybol, Basketbol, Hentbol, Atletizm ──
def _tg_zemin_seridi(x0, sx, sz):
    """
    İki boyutlu güzergâhı yandan görünüşe indirger (Paket 18; Pro Agility ve S-Turn ile aynı yol): yan eksen
    (metre) zemin çizgisi boyunca uzanır, derinlik yalnız zeminin hemen gerisinde ince bir şeride sıkışır
    (perspektif saha çizilmez). Döndürür: P(x_m, z_m) → tuval noktası.
    """
    def P(xm, zm):
        return x0 + xm * sx, TG_ZEMIN - 2 - zm * sz
    return P


def _tg_koni(S, x, y, h=7):
    S.esya(f'<path d="M{x - 3:.1f},{y + 1:.1f} L{x:.1f},{y - h:.1f} L{x + 3:.1f},{y + 1:.1f} z" '
           f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')


def _tg_fotosel(S, x):
    S.esya(S.kutu(x - 1.5, TG_ZEMIN - 26, 3, 26, dolgu="yuzey", rx=0.8))


def _tg_deneme_seridi(S, deneme, sag=248, y=20, w=8, olcek=1.6, t=0.0):
    """Deneme yapısı: her deneme bir blok, araları protokolde süre verilmeyen ya da aralıklı toparlanma (kesik)."""
    parca = []
    for i in range(deneme):
        parca += [(w, True)] + ([(None, None)] if i < deneme - 1 else [])
    gen = deneme * w * olcek + (deneme - 1) * 8
    return _tg_periyot_seridi(S, parca, x0=sag - gen, y=y, olcek=olcek, t=t)


def _tg_sprint(mesafe, baslik, notu, deneme, blok=False, fotosel=True):
    """
    Düz sprint (Atletizm 10/20/100/200/400 m, NBA 3/4 saha, Voleybol 20 m): çıkış ve bitiş fotoseli, üstte mesafe
    oku (şematik — mesafe ok boyuyla değil etiketle verilir), sağ üstte deneme şeridi.
    fotosel=False: protokol yalnız kronometre diyorsa çıkış ve bitiş yalnız çizgi.
    """
    S = TgSahne(3.2)
    x0, x1 = 30, 222
    for x in (x0, x1):
        (_tg_fotosel if fotosel else _tg_direk)(S, x)
    if blok:                                           # blok başlangıç (blok ya da ayakta)
        S.esya(f'<path d="M{x0 - 22:.1f},{TG_ZEMIN} L{x0 - 10:.1f},{TG_ZEMIN} L{x0 - 10:.1f},{TG_ZEMIN - 6:.1f} z" '
               f'fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(hk_duz_kos(x0 - 8, x1 + 3, s=0.8, bitis_x=x1))
    if deneme:                                          # 0: dayanıklılık koşusu (tek koşu, şerit yok)
        _tg_deneme_seridi(S, deneme)
    S.baslik(baslik)
    S.olcu(x0, 32, x1, 32, mesafe, etiket_yer="orta",
           kilavuzlar=[(x0, TG_ZEMIN - 28, x0, 32), (x1, TG_ZEMIN - 28, x1, 32)])
    S.not_(notu, t=0.8)
    return S


def _tg_hizlanma_profili():
    """Sprint hızlanma profili: fotosel 0, 10, 20, 30 m; bölüm okları eş uzunlukta (ölçekli)."""
    S = TgSahne(3.4)
    m = TG_OLCEK["_tg_hizlanma_profili"][0]
    xs = [30 + i * 10 * m for i in range(4)]
    for x in xs:
        _tg_fotosel(S, x)
    S.figur(hk_duz_kos(xs[0] - 8, xs[-1] + 3, s=0.8, bitis_x=xs[-1]))
    _tg_deneme_seridi(S, 3)
    S.baslik("Fotosel 10., 20. ve 30. metrede: bölüm süreleri")
    S.olcu(xs[0], 32, xs[1], 32, "10 m", etiket_yer="orta", metre=10,
           kilavuzlar=[(x, TG_ZEMIN - 28, x, 32) for x in xs])
    for a, b in zip(xs[1:], xs[2:]):
        S.olcu(a, 32, b, 32, es=0, metre=10)
    S.not_("3 deneme; her bölüm için en iyi değer", t=0.8)
    return S


def _tg_rsa():
    """RSA: 30 m tekrarlı sprint; zaman çubuğu 6 sprint ve aralarındaki 25 sn pasif dinlenme."""
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_rsa"][0]
    x0, x1 = 36, 36 + 30 * m
    for x in (x0, x1):
        _tg_fotosel(S, x)
    S.figur(hk_duz_kos(x0 - 8, x1 + 3, s=0.8, bitis_x=x1))
    sprint = 5                                         # şematik: sprint süresi protokolde yok, dar blok
    parca = [p for i in range(6) for p in ([(sprint, True)] + ([(25, False)] if i < 5 else []))]
    toplam = 6 * sprint + 5 * 25
    _tg_periyot_seridi(S, parca, x0=248 - toplam * 0.55, y=20, olcek=0.55, imlec=[(0, 0), (1, sprint / toplam)])
    S.baslik("6 × 30 m sprint, arada 25 sn pasif dinlenme")
    S.olcu(x0, TG_OLCU_Y, x1, TG_OLCU_Y, "30 m", uc="ilk", metre=30)      # zeminde, fotoseller arası
    S.not_("Durarak başlangıç; en iyi ve ortalama süre", t=0.8)
    return S


def _tg_list():
    """LIST: 20 m mekik; zaman çubuğu 5 × 15 dk bölüm (her bölüm yürüyüş → koşu → hızlı koşu → sprint → dinlenme)."""
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_list"][0]
    a, b = 30, 30 + 20 * m
    for x in (a, b):
        _tg_direk(S, x)
    S.figur(hk_donuslu_kos([a + 4, b - 4, a + 30], s=0.8, dokun=False, baslangic="kos"))
    _tg_periyot_seridi(S, [(15, True)] * 5, x0=248 - 75 * 1.1, y=20, olcek=1.1, imlec=[(0, 0), (1, 0.06)])
    S.baslik("Yürü → koş → hızlı koş → sprint → dinlen")
    S.olcu(a, 32, b, 32, "20 m", etiket_yer="orta", metre=20, kilavuzlar=[(a, TG_ZEMIN - 7, a, 32), (b, TG_ZEMIN - 7, b, 32)])
    S.not_("5 × 15 dk bölüm (toplam 75 dk), 20 m alan", t=0.05)
    return S


def _tg_30_15():
    """
    30-15 IFT: 40 m; 30 sn koşu (mekik) + 15 sn yürüme. Zaman çubuğunda koşu blokları her aşamada YÜKSELİR
    (hız +0,5 km/h) — Yo-Yo'da ise koşu blokları kısalır, dinlenme sabittir: iki testin farkı şeritte görünür.
    """
    S = TgSahne(4.4)
    m = TG_OLCEK["_tg_30_15"][0]
    a, b = 36, 36 + 40 * m
    for x in (a, b):
        _tg_direk(S, x)
    for x in (a + 3 * m, b - 3 * m):                   # 3 m güvenlik bölgeleri
        S.esya(S.cizgi(x, TG_ZEMIN, x, TG_ZEMIN - 22, "kilavuz"), tur="isaret")
    kos = hk_donuslu_kos([a + 4, b - 6], s=0.7, dokun=False, baslangic="kos", t1=0.7)
    yuru = hk_donuslu_kos([b - 6, b - 30], s=0.7, dokun=False, baslangic="kos", t0=0.72)
    S.figur(TgHareket(kos.anahtarlar + yuru.anahtarlar, {}))
    parca = [p for i in range(5) for p in ((30, True, 0.6 + 0.2 * i), (15, False, 0.4))]   # yürüme alçak, koşu yükselir
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.6, imlec=[(0, 0), (0.7, 30 / 225), (1.0, 45 / 225)])
    S.baslik("30 sn koşu / 15 sn yürüme; hız artarak")
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, "40 m", uc="ilk", metre=40)        # zeminde, çizgiler arası
    S.not_("Başlangıç 8 km/h, her aşamada +0,5 km/h", t=0.05)
    return S


# Çeviklik parkurları (metre). Yan eksen zemin boyunca, derinlik zeminin gerisinde ince şeritte (sz küçük);
# dönüş noktaları işaretli, sıralama başlıkta. olcek = (1 m yan eksende kaç birim, 1 m derinlikte kaç birim).
_TG_PARKURLAR = {
    # Illinois: 10 × 5 m, 8 koni (4 köşe + ortada 3,3 m arayla 4); yüzüstü başla, zigzag + slalom (~60 m)
    "illinois": dict(olcek=(17, 2.6), x0=58, s=0.62,
                     koniler=[(0, 0), (10, 0), (0, 5), (10, 5), (0, 2.5), (3.3, 2.5), (6.6, 2.5), (10, 2.5)],
                     yol=[(0, 0.4), (10, 0.4), (0, 2.5), (1.65, 3.3), (4.95, 1.7), (8.25, 3.3), (10, 2.5),
                          (8.25, 1.7), (4.95, 3.3), (1.65, 1.7), (0, 2.5), (10, 4.6), (0, 4.6)],
                     baslangic="yuzustu", dokun=(), donus=(1, 2, 6, 10, 11)),
    # Voleybol (VAT): 9 m yan, 18 m derinlik; ortadan sol ön → sağ ön → sağ arka → sol arka → orta, köşede dokun
    "vat": dict(olcek=(18, 0.75), x0=50, s=0.62,
                koniler=[(0, 0), (9, 0), (9, 18), (0, 18)],
                yol=[(4.5, 9), (0, 0), (9, 0), (9, 18), (0, 18), (4.5, 9)],
                baslangic=None, dokun=(1, 2, 3, 4), donus=(1, 2, 3, 4)),
    # NBA Lane: boya alanı 4,9 m yan × 5,8 m derinlik (koni yok); aşağı → sol → yukarı → sağ → aşağı
    "nba_lane": dict(olcek=(28, 2.4), x0=62, s=0.62, koniler=[],
                     yol=[(4.9, 5.8), (4.9, 0), (0, 0), (0, 5.8), (4.9, 5.8), (4.9, 0)],
                     baslangic=None, dokun=(), donus=(1, 2, 3, 4)),
    # T-testi (Karate KAT, Taekwondo): A başlangıç; B 9,14 m ileride; C ve D B'nin 4,57 m solu/sağı
    "t_testi": dict(olcek=(18, 1.5), x0=48, s=0.62,
                    koniler=[(4.57, 0), (4.57, 9.14), (0, 9.14), (9.14, 9.14)],
                    yol=[(4.57, 0), (4.57, 9.14), (0, 9.14), (9.14, 9.14), (4.57, 9.14), (4.57, 0)],
                    baslangic=None, dokun=(), donus=(1, 2, 3, 4)),          # A→B→C→D→B→A (Semenick 1990)
    # Spider (tenis): tekler kortu 8,23 m; arka çizginin gerisinden 5 topa sırayla, sağdan; her top kareye
    "spider": dict(olcek=(19, 2.0), x0=52, s=0.6, koniler=[],
                   yol=[(4.115, -0.4), (8.23, 0), (4.115, -0.4), (8.23, 5.49), (4.115, -0.4), (4.115, 11.89),
                        (4.115, -0.4), (0, 5.49), (4.115, -0.4), (0, 0), (4.115, -0.4)],
                   baslangic=None, dokun=(1, 3, 5, 7, 9), donus=(1, 3, 5, 7, 9),
                   tek_tek=True,                                  # yalnız o anki gidiş-dönüş çizilir (Paket 24)
                   rozet=[(9, -3), (9, -8), (-13, -6), (-9, -8), (-9, -3)]),   # her rozet kendi topunun dış yanında
    # Squash SIST (Wilkinson ve ark., 2009): kort 6,4 m eni; derinlik arka duvardan (ön duvar 9,75 m); T'den
    # sinyalin gösterdiği köşeye, ayak hedefte, T'ye dönüş. Köşe sırası sinyale göredir — çizimdeki sıra örnektir.
    "sist": dict(olcek=(24, 2.0), x0=54, s=0.6, koniler=[],
                 yol=[(3.2, 4.31), (0, 9.75), (3.2, 4.31), (6.4, 0), (3.2, 4.31), (6.4, 9.75), (3.2, 4.31),
                      (0, 0), (3.2, 4.31)],
                 baslangic=None, dokun=(), donus=(1, 3, 5, 7), tek_tek=True,
                 rozet=[(-9, -6), (9, -3), (9, -6), (-9, -3)]),
    # Ghost Drill (Squash): kort 6,4 m × 9,75 m; T noktasından 6 köşeye sırayla, her köşeden T'ye; köşede raketle duvar
    "ghost": dict(olcek=(26, 1.3), x0=48, s=0.62, koniler=[],
                  yol=[(3.2, 4.3), (0.5, 9.2), (3.2, 4.3), (5.9, 9.2), (3.2, 4.3), (0.5, 4.9), (3.2, 4.3),
                       (5.9, 4.9), (3.2, 4.3), (0.5, 0.6), (3.2, 4.3), (5.9, 0.6), (3.2, 4.3)],
                  baslangic=None, dokun=(1, 3, 5, 7, 9, 11), donus=(1, 3, 5, 7, 9, 11)),
}


def _tg_parkur_bacaklari(S, noktalar):
    """
    Merkezden çıkıp merkeze dönen güzergâh (Spider, Paket 24): her gidiş-dönüş (merkez → hedef → merkez) yalnız
    figür o bacaktayken görünür (goster t0–t1); son bacak sona kadar kalır (durağan kopyada o görünür). Zamanlar
    hk_kavisli_yol(yumusak=False) ile aynı: süre güzergâh uzunluğuyla orantılı.
    """
    uz = [0.0]
    for a, b in zip(noktalar, noktalar[1:]):
        uz.append(uz[-1] + _math.dist(a, b))
    for i in range(0, len(noktalar) - 2, 2):
        d = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(noktalar[i:i + 3]))
        t0 = uz[i] / uz[-1]
        t1 = uz[i + 2] / uz[-1] if i + 2 < len(noktalar) - 1 else None
        S.goster(f'<path d="{d}" fill="none" stroke="{TG_RENK["olcu"]}" stroke-width="{TG_KALINLIK["kilavuz"]}" '
                 f'stroke-dasharray="3 2" stroke-linecap="round"/>', t0, t1, tur="isaret")
        S.bacaklar.append((t0, 1.0 if t1 is None else t1))


def _tg_parkur(tur, baslik, notu, isaret_yazi=None, isaret_yeri=(150, 52), serit=None):
    """
    Çeviklik parkuru (Illinois, VAT, NBA Lane, Hentbol, T-testi, Ghost Drill): yandan görünüş; güzergâh zemin
    çizgisi boyunca, derinlik ince şeritte. Dönüş noktaları SIRA NUMARALI (Paket 19): aynı yerden birden çok kez
    dönülüyorsa numaralar o noktanın üstünde alt alta durur (ör. Illinois sağ uç: 1, 3, 5). serit: zaman çubuğu.
    """
    d = _TG_PARKURLAR[tur]
    S = TgSahne(7.0)
    P = _tg_zemin_seridi(d["x0"], *d["olcek"])
    noktalar = [P(*n) for n in d["yol"]]
    h = hk_kavisli_yol(noktalar, s=d["s"], kip="kos", yumusak=False, baslangic=d["baslangic"], dokun=d["dokun"])
    if d.get("tek_tek"):
        _tg_parkur_bacaklari(S, noktalar)
    else:
        S.yol(h.olay["yol"])
    for x, y in sorted((P(*k) for k in d["koniler"]), key=lambda q: q[1]):     # arkadaki koni önce
        _tg_koni(S, x, y)
    for x, y in noktalar[1:-1]:                                                   # dönüş noktaları
        S.esya(S.nokta(x, y, 1.6), tur="isaret")
    ust = min(y for _, y in noktalar) - 8                                         # numara sütunları güzergâhın üstünde
    orta = sum(x for x, _ in noktalar) / len(noktalar)
    sutun = []                                                                     # [(x, kaç numara)]
    for n, (i, (rx, ry)) in enumerate(zip(d["donus"], d.get("rozet", ()))):    # rozet: noktanın yanında, ayrık
        S.numara(noktalar[i][0] + rx, noktalar[i][1] + ry, n + 1)
    for n, i in enumerate(() if d.get("rozet") else d["donus"], 1):
        x, _ = noktalar[i]
        x += -9 if x <= orta else 9                    # sütun noktanın dış yanında: figür numaranın üstüne binmesin
        j = next((k for k, (sx, _) in enumerate(sutun) if abs(sx - x) < 10), None)
        if j is None:
            sutun.append((x, 0))
            j = len(sutun) - 1
        sx, kac = sutun[j]
        S.numara(sx, ust - 10 * kac, n)
        sutun[j] = (sx, kac + 1)
    if serit:
        _tg_periyot_seridi(S, serit[0], x0=12, y=22, olcek=serit[1])
    for t, x, y in h.olay["dokunma"]:
        S.belir(S.nokta(x, y, 2.6, dolu=True), t, tur="isaret")
    S.figur(h)
    S.baslik(baslik)
    if isaret_yazi:
        bx, by = noktalar[0]
        S.isaret(isaret_yazi, (bx, by), isaret_yeri, hiza="start", t=0.02)
    S.not_(notu, t=0.6)
    return S


def _tg_sicrama_turleri(turler, baslik, notu, bekleme=None):
    """
    CMJ / SJ / DJ yan yana (soldan), her varyant için TEK figür; durağan karede her biri kendi ayırt edici anında
    (Paket 18): CMJ ön-çömelmenin en alt noktası + aşağı-yukarı ok; SJ 90° statik çömelme + diz açısı ve bekleme
    işareti (protokol süre veriyorsa etiketle, ör. "2 sn bekleme"), çöküş oku yok; DJ kutudan düşüş anı + düşüş yolu.
    """
    S = TgSahne(2.4)
    s = 0.7
    m = TG_OLCEK["_tg_sicrama_turleri"][0]
    yer = {"CMJ": 40, "SJ": 102} if "DJ" in turler else {"CMJ": 80, "SJ": 176}
    ok = TG_RENK["olcu"]
    for t in turler:
        if t == "DJ":
            yuk = 0.3 * m
            sol, sag = 162, 186
            S.esya(S.kutu(sol, TG_ZEMIN - yuk, sag - sol, yuk, rx=1))
            h = hk_sicrama_ani((sol + sag) / 2, "dj", s=s, kutu=(sol, sag, yuk))
            a, b, c = h.olay["dusus_yolu"]
            S.belir(f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{b[0]:.1f},{a[1] - 2:.1f} {b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f}" '
                    f'fill="none" stroke="{ok}" stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.6,
                    tur="isaret")
            hx_, hy_ = h.olay["kalca"]
            S.belir(S.cizgi(hx_ + 22, hy_ - 10, hx_ + 22, hy_ + 14, "olcu", ok="son"), 0.9, tur="isaret")   # düşüş: aşağı ok
        else:
            h = hk_sicrama_ani(yer[t], t.lower(), s=s)
        S.figur(h)
        kx, ky = h.olay["kalca"]
        if t == "CMJ":                       # çök-sıçra: kalçanın yanında aşağı-yukarı ok
            y0, y1 = h.olay["kalca_yolu"]
            S.belir(S.cizgi(kx + 24, y0 - 6, kx + 24, y1 + 8, "olcu", ok=True), 0.9, tur="isaret")
        elif t == "SJ":                      # 90° diz açısı yayı + bekleme (iki dikey çizgi), çöküş oku yok
            dx, dy = h.olay["diz"]
            r = 6
            ua = _math.atan2(kx - dx, ky - dy)
            ba = _math.atan2(h.olay["ayak"][0] - dx, h.olay["ayak"][1] - dy)
            p1 = (dx + r * _math.sin(ua), dy + r * _math.cos(ua))
            p2 = (dx + r * _math.sin(ba), dy + r * _math.cos(ba))
            S.esya(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} Q{dx + 1.4 * r * _math.sin((ua + ba) / 2):.1f},'
                   f'{dy + 1.4 * r * _math.cos((ua + ba) / 2):.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{ok}" '
                   f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>', tur="isaret")
            S.esya(S.cizgi(kx + 22, ky - 30, kx + 22, ky - 18, "vurgu") + S.cizgi(kx + 29, ky - 30, kx + 29, ky - 18, "vurgu"),
                   tur="isaret")                                                   # bekleme (duraklat) işareti
            if bekleme:
                S.isaret(bekleme, (kx + 25.5, ky - 30), (kx + 30, ky - 48), hiza="start", t=0.3)
    S.baslik(baslik)
    if "DJ" in turler:
        S.olcu(156, TG_ZEMIN, 156, TG_ZEMIN - 0.3 * m, "30 cm", metre=0.3, etiket_yer="sol", t=0.05)
    S.not_(notu, t=0.4)
    return S


def _tg_nordic():
    """Nordic hamstring (NordBord): diz üstü, bilekler kancada; gövde yavaşça öne. Kanca kuvveti ölçer (her bacak)."""
    S = TgSahne(4.0)
    tahta = TG_ZEMIN - 4
    S.esya(S.kutu(50, tahta, 128, 4, rx=1))
    h = hk_nordic(124, tahta - 2, s=0.9)
    bx, by = h.olay["bilek"]
    S.esya(S.cizgi(bx - 3, tahta, bx - 3, by - 5) + S.kutu(bx - 6, by - 6.5, 7, 3, dolgu="yuzey", rx=1))   # kanca + sensör
    S.figur(hk_iz(h))                     # başlangıç: dik diz üstü
    S.figur(h)
    S.baslik("Diz üstü, bilekler sabit; gövde yavaşça öne")
    S.isaret("Pik kuvvet (N)", (bx - 3, by - 6.5), (172, 50), hiza="start", t=0.1)
    S.not_("3 tekrar, her bacak ayrı; en yüksek değer", t=0.6)
    return S


def _tg_diz_dinamometre():
    """İzokinetik dinamometre: koltuk, cihaz başı diz ekseninde, kol kavala bağlı; 90° / 45° kılavuzları."""
    S = TgSahne(5.0)
    kx, ky = 96, TG_ZEMIN - 44
    h = hk_dinamometre(kx, ky)
    dx, dy = h.olay["diz"]
    L = _TG_BOY["baldir"]
    S.esya(S.kutu(66, ky + 3, 38, 5, rx=1) + S.cizgi(72, ky + 8, 72, TG_ZEMIN) + S.cizgi(98, ky + 8, 98, TG_ZEMIN)
           + S.cizgi(68, ky + 3, 60, ky - 36))                                       # koltuk + sırtlık
    S.esya(S.cizgi(dx - 8, dy + 6, dx - 8, TG_ZEMIN) + S.cizgi(dx - 16, TG_ZEMIN, dx, TG_ZEMIN)
           + f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="7" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{TG_KALINLIK["esya"]}"/>')                             # cihaz başı diz ekseninde
    for aci in (0, 45):                                                               # 90° ve 45° fleksiyon kılavuzu
        r = _math.radians(aci)
        S.esya(S.cizgi(dx, dy, dx + L * _math.sin(r), dy + L * _math.cos(r), "kilavuz"), tur="isaret")
    S.cubuk(dx, dy, h.olay["ayak_yolu"])
    S.figur(h)
    S.baslik("Diz 90° ve 45°'de izometrik, 180°/sn izokinetik")
    S.isaret("Pik tork (Nm/kg)", (dx, dy - 7), (150, 44), hiza="start", t=0.05)
    S.not_("Her iki bacak; H:K oranı ve asimetri", t=0.6)
    return S


# ── Branşa özgü sahneler, 3. parti (Paket 18): mücadele sporları ──
def _tg_minder(S, x0=40, x1=246):
    S.esya(S.kutu(x0, TG_ZEMIN - 3, x1 - x0, 3, rx=1))


def _tg_sjft_judo():
    """
    Judo SJFT: iki uke 6 m arayla (ikinci kişi rengi), tori ortadan başlar; A, B, C periyotlarında birer atış
    gösterilir (sağ → sol → sağ). Zaman çubuğu 15/10/30/10/30 sn; her aktif bloğun altında periyot sayacı.
    """
    S = TgSahne(7.0)
    m = TG_OLCEK["_tg_sjft_judo"][0]
    x_sol, x_sag = 70, 70 + 6 * m
    _tg_minder(S, 30, 250)
    h = hk_iki_uke_atis(x_sol, x_sag, s=0.7)
    for u in h.olay["ukeler"]:
        S.figur(u)
    S.figur(h)
    atis = h.olay["atis_anlari"]
    parca = [(15, True), (10, False), (30, True), (10, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=1.0)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(atis, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(atis, bloklar):
        S.sayac((xa + xb) / 2 - 6, 34, [t], boy=14)
    S.baslik("İki uke 6 m arayla; tori ortadan koşup atar")
    ilk = S.sayaclar[-1]
    S.isaret("Periyot başına atış", (ilk[2], (ilk[1] + ilk[3]) / 2), (110, 42), hiza="start", t=atis[0])
    S.not_("A 15 sn, B 30 sn, C 30 sn; aralarda 10 sn dinlenme")
    return S


def _tg_ukft():
    """UKFT: tutuş, giriş-çıkış tekrarı (atış yok); 3 × 30 sn set, 30 sn dinlenme; set başına giriş sayacı."""
    S = TgSahne(5.0)
    _tg_minder(S, 70, 230)
    h = hk_uchikomi(140, tekrar=3, s=0.8)
    S.figur(h.olay["partner"])
    S.figur(h)
    giris = h.olay["giris_anlari"]
    parca = [(30, True), (30, False), (30, True), (30, False), (30, True)]
    x0, x1, y, bloklar = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=0.7)
    S.kaydir(f'<path d="M{x0:.1f},{y + 8} l-2.5,4 l5,0 z" fill="{TG_RENK["olcu"]}"/>',
             [(t, (x1 - x0) * o, 0) for t, o in _tg_imlec_atis(giris, bloklar, x0, x1)], tur="isaret")
    for t, (xa, xb) in zip(giris, bloklar):
        S.sayac((xa + xb) / 2 - 6, 34, [t], boy=14)
    S.baslik("Tutuş alınır, giriş-çıkış tekrarlanır; atış yok")
    ilk = S.sayaclar[0]
    S.isaret("Set başına giriş", ((ilk[0] + ilk[2]) / 2, ilk[3]), (12, 70), hiza="start", t=giris[0])
    S.not_("3 × 30 sn set, aralarında 30 sn dinlenme")
    return S


def _tg_vurus(teknikler, baslik, notu, sayac_yazi, parca, olcek, hedef=None):
    """
    Vuruş protokolleri (TSAT, KSDT, MTSDT, KSKT, Boks): tek çizim, parametreyle ayrışır — teknik dizisi (tekme
    yüksekliği tekniğin kendisinden: dollyo baş, roundhouse/geri gövde), hedef ("torba": kum torbası; "ped": ayaklı
    tekme pedi, yüksekliği son tekniğin erişim noktasında — branşa göre parametre) ve tempo (zaman çubuğu).
    Sayaç vuruşları çeteleyle sayar.
    """
    S = TgSahne(5.0)
    x = 166
    h = hk_vurus(x, teknikler, s=0.75)
    ex, ey = h.olay["erisim"]
    if hedef == "torba":                         # tavana asılı kum torbası; ön yüzü son vuruşun erişim noktasında
        S.esya(S.cizgi(ex + 8, 21, ex + 8, 30) + S.kutu(ex + 1, 30, 14, 66, rx=4))
        S.hedefler.append(("torba", ex + 8, 63))
    elif hedef == "ped":                         # ayaklı tekme pedi; yüksekliği son tekniğin erişim noktası
        S.esya(S.cizgi(ex + 9, TG_ZEMIN, ex + 9, ey + 9) + S.kutu(ex + 1, ey - 9, 10, 18, rx=3))
        S.hedefler.append(("ped", ex + 6, ey))
    S.figur(h)
    _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=olcek)
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, h.olay["darbe_anlari"], boy=16)
    S.baslik(baslik)
    S.isaret(sayac_yazi, (sx1, (sy0 + sy1) / 2), (36, 76), hiza="start", t=h.olay["darbe_anlari"][0])
    S.not_(notu)
    return S


def _tg_mac(parca, olcek, baslik, sure_yazi, notu):
    """Simüle maç (Güreş, Sambo, MMA, BJJ): iki sporcu tutuşta (rakip ikinci kişi renginde); tur yapısı şeritte."""
    S = TgSahne(3.6)
    S.esya(f'<ellipse cx="150" cy="{TG_ZEMIN - 1}" rx="92" ry="4.5" fill="{TG_RENK["dolgu"]}" '
           f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    S.figur(hk_ikinci_figur(hk_tutus(168, yon=-1)))
    S.figur(hk_tutus(132, yon=1))
    x0, x1, y, _ = _tg_periyot_seridi(S, parca, x0=12, y=22, olcek=olcek, imlec=[(0, 0), (1, 1)])
    S.baslik(baslik)
    S.isaret(sure_yazi, ((x0 + x1) / 2, y + 6), (12, 52), hiza="start")
    S.not_(notu)
    return S


def _tg_asilma(baslik, notu):
    """Gi/kurtka yakasından asılı kalma (BJJ, Sambo): bar, yakalar, asılı sporcu; süreölçer saniye sayar."""
    S = TgSahne(5.0)
    x, bar_y, tut_y = 110, 26, 34
    S.esya(S.cizgi(74, TG_ZEMIN, 74, bar_y) + S.cizgi(146, TG_ZEMIN, 146, bar_y) + S.cizgi(70, bar_y, 150, bar_y))
    S.esya(f'<path d="M{x - 9},{bar_y} L{x - 3},{tut_y + 2} M{x + 9},{bar_y} L{x + 3},{tut_y + 2}" fill="none" '
           f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["vurgu"]}" stroke-linecap="round"/>')   # yakalar
    h = hk_asilma(x, tut_y, s=0.75)
    S.figur(h)
    kx0, ky0, kx1, ky1 = S.kronometre(206, 76, t0=0.25)
    S.baslik(baslik)
    S.isaret("Asılma süresi (sn)", ((kx0 + kx1) / 2, ky0), (162, 46), hiza="start", t=0.25)
    S.not_(notu)
    return S


def _tg_yan_adim():
    """Masa tenisi yan adım: 3 m sağ-sol, 15 sn; önden görünüş."""
    S = TgSahne(3.6)
    m = TG_OLCEK["_tg_yan_adim"][0]
    a, b = 92, 92 + 3 * m
    for x in (a, b):
        _tg_direk(S, x)
    S.figur(hk_yan_adim(a + 6, b - 6, tekrar=3, s=0.8))
    _tg_periyot_seridi(S, [(15, True)], x0=12, y=22, olcek=2.0, imlec=[(0, 0), (1, 1)])
    S.baslik("Yan adım: 3 m sağ-sol, 15 sn")
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, "3 m", uc="son", metre=3)
    S.not_("Reaksiyon: 20 deneme · masa başı vuruş: 30 sn")
    return S


# ── Çocuk ve genç fiziksel uygunluk bataryaları (Paket 19) ──
def _tg_mat(S, x0, x1):
    S.esya(S.kutu(x0, TG_ZEMIN - 2, x1 - x0, 2, rx=1))


def _tg_uzun_atlama(baslik, notu, etiket="Mesafe (cm)"):
    """Durarak uzun atlama (Eurofit, ALPHA, PREFIT, CNPFM, Latorre, CAPL): çizgi, iniş; ok çizgiden en geri topuğa."""
    S = TgSahne(3.0)
    cizgi = 90
    _tg_direk(S, cizgi)
    h = hk_uzun_atlama(cizgi, 96, s=0.8)
    S.figur(h)
    S.baslik(baslik)
    S.olcu(cizgi, TG_OLCU_Y, h.olay["topuk_x"], TG_OLCU_Y, etiket, uc="ilk", t=0.95,
           bag=[(1, "x", ("ayak1", "ayak2"), "min")])
    S.not_(notu, t=0.3)
    return S


def _tg_mekik_kosusu(mesafe, baslik, notu, gidis=4, blok=False):
    """Kısa mekik koşusu (10 × 5 m, 4 × 10 m, 8 × 25 m): iki çizgi arası dönüşlü koşu; ok şematik, mesafe etikette."""
    S = TgSahne(4.0)
    a, b = 44, 222
    for x in (a, b):
        _tg_direk(S, x)
    if blok:                                              # sünger bloklar: dönüşte biri alınıp karşıya taşınır
        S.esya("".join(S.kutu(x - 3, TG_ZEMIN - 5, 6, 5, dolgu="yuzey", rx=1) for x in (a - 10, a - 18)))
    duraklar = [a + 4] + [b - 4 if i % 2 == 0 else a + 4 for i in range(gidis)]
    S.figur(hk_donuslu_kos(duraklar, s=0.75, dokun=blok, baslangic="kos"))
    S.baslik(baslik)
    S.olcu(a, TG_OLCU_Y, b, TG_OLCU_Y, mesafe, uc="son")
    S.not_(notu, t=0.05)
    return S


def _tg_otur_uzan(baslik, notu, sifir_cm, tek_bacak=False):
    """
    Otur-uzan varyantları. Cetvelin SIFIR NOKTASI varyantın kendi protokolünden çizilir (varsayılan yok):
    sifir_cm = ayak tabanı hizasının ölçekteki değeri (Eurofit 15, FitnessGram/ALPHA Back-Saver 22,9, CNPFM 0).
    Sıfır, ayak tabanının bu kadar gerisindedir (gövdeye doğru); ok sıfırdan ayak tabanına. tek_bacak: Back-Saver.
    """
    S = TgSahne(3.2)
    m = TG_OLCEK["_tg_otur_uzan"][0]
    z, ayak = TG_ZEMIN, 170
    sifir = ayak - sifir_cm / 100 * m
    S.esya(S.kutu(ayak, z - 20, 50, 20))
    S.esya(S.cizgi(min(sifir, ayak) - 8, z - 21, 240, z - 21)
           + "".join(S.cizgi(x, z - 24, x, z - 21) for x in range(int(min(sifir, ayak)) - 6, 240, 6)))
    S.esya(S.cizgi(sifir, z - 27, sifir, z - 21, "vurgu"), tur="isaret")          # ölçeğin sıfırı
    h = hk_oturarak_uzanma(ayak, tek_bacak=tek_bacak)
    S.figur(h)
    el = h.olay["el"][0]
    S.kaydir(S.kutu(176, z - 28, 5, 7, dolgu="yuzey", rx=1),
             [(0, 0, 0), (0.45, 0, 0), (0.8, el - 178.5, 0), (1, el - 178.5, 0)])
    S.baslik(baslik)
    if sifir_cm:
        yazi = f"{sifir_cm:g} cm".replace(".", ",")
        S.olcu(sifir, z - 46, ayak, z - 46, yazi, uc="son", metre=sifir_cm / 100,
               kilavuzlar=[(sifir, z - 27, sifir, z - 46), (ayak, z - 21, ayak, z - 46)])
    else:
        S.isaret("Sıfır: ayak tabanı", (sifir, z - 27), (sifir - 40, z - 52), hiza="end", t=0.05)
    S.not_(notu, t=0.3)
    return S


def _tg_govde_fleksiyonu(tur, baslik, notu, isaret="Tekrar sayısı"):
    """Mekik (sit-up) ve curl-up: mat, figür, tekrarları sayan çetele. Curl-up'ta parmak ucu ölçüm şeridini aşar."""
    S = TgSahne(3.4)
    _tg_mat(S, 70, 210)
    h = hk_mekik(140, tur, tekrar=2, s=0.85)
    if tur == "curlup":                                   # ölçüm şeridi: parmak uçlarının altında
        (x0, _), (x1, _) = h.olay["el_yolu"]
        S.esya(S.kutu(min(x0, x1) - 1, TG_ZEMIN - 3.5, abs(x1 - x0) + 2, 1.5, dolgu="yuzey", rx=0.5))
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret(isaret, (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_sinav(baslik, notu, diz=False):
    """Şınav (FitnessGram, PYFP) ve diz üstü şınav (BOT-2): alt nokta dirsek 90°; çetele tekrarları sayar."""
    S = TgSahne(3.0)
    _tg_mat(S, 60, 220)
    h = hk_sinav(140, s=0.85, diz=diz)
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_modifiye_barfiks(baslik, notu):
    """Modified pull-up: alçak bar (uçtan görünüş), sırtüstü düz vücut, çene bara; çetele tekrarları sayar."""
    S = TgSahne(3.0)
    h = hk_modifiye_barfiks(206, s=0.85)
    bx, by = h.olay["bar"]
    S.esya(S.cizgi(bx, TG_ZEMIN, bx, by + 3) + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="{TG_RENK["esya"]}"/>')
    bant = by + 0.19 * TG_OLCEK["_tg_modifiye_barfiks"][0]       # elastik bant bardan 7-8 inç (18-20 cm) aşağıda
    S.esya(f'<circle cx="{bx:.1f}" cy="{bant:.1f}" r="1.3" fill="{TG_RENK["yuzey"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["kilavuz"]}"/>')
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_plaka(S, yol, r=7.0):
    """Bar ucundaki plaka diski (yandan): yol [(t, x, y)] boyunca kayar (halter ile aynı çizim)."""
    b0 = yol[0]
    S.kaydir(f'<circle cx="{b0[1]:.1f}" cy="{b0[2]:.1f}" r="{r}" fill="{TG_RENK["dolgu"]}" '
             f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>',
             [(t, x - b0[1], y - b0[2]) for t, x, y in yol])


def _tg_bench_press(baslik, notu):
    """1RM bench press: sehpa + bar dikmesi; bar göğse iner, kollar tam açılır; spotçu barın başında (ikinci figür)."""
    S = TgSahne(3.0)
    s, sehpa_y = 0.85, TG_ZEMIN - 18
    h = hk_bench_press(150, sehpa_y, s=s)
    bas_x = h.olay["bas"][0]
    S.esya(S.kutu(bas_x - 6, sehpa_y, 150 - bas_x + 14, 3.5, rx=1)
           + S.cizgi(bas_x + 2, sehpa_y + 3.5, bas_x + 2, TG_ZEMIN) + S.cizgi(156, sehpa_y + 3.5, 156, TG_ZEMIN))
    ust_y = min(y for _, _, y in h.olay["bar"])
    dx = bas_x - 9
    S.esya(S.cizgi(dx, TG_ZEMIN, dx, ust_y + 4) + S.cizgi(dx, ust_y + 4, dx + 4, ust_y + 4))   # bar dikmesi (kanca)
    S.figur(h.olay["spotcu"])                                               # spotçu: barın başında, eller hazır
    _tg_plaka(S, h.olay["bar"])
    S.figur(h)
    S.baslik(baslik)
    sb = h.olay["spotcu_bas"]
    S.isaret("Spotçu", (sb[0] - 5, sb[1] - 4), (sb[0] - 30, 38), hiza="middle", t=0.0)
    S.not_(notu)
    return S


def _tg_arka_comelme(baslik, notu):
    """1RM arka çömelme: kafes (iki dikme + güvenlik demiri), bar üst sırtta; diz açısı 90°'yi geçene kadar."""
    S = TgSahne(3.0)
    s, xa = 0.85, 140
    h = hk_arka_comelme(xa, s=s)
    alt_y = h.olay["bar"][-1][2]
    ust_y = h.olay["bar"][0][2]
    arka = xa - 52                                                            # kafes dikmesi (yandan: dikmeler üst üste)
    demir = alt_y + 9.5                                                       # güvenlik demiri: en alt noktanın hemen altında
    S.esya(S.cizgi(arka, TG_ZEMIN, arka, ust_y - 8) + S.cizgi(arka - 3, demir, xa + 20, demir))
    S.figur(hk_iz(h))                                                         # başlangıç: dik duruş
    _tg_plaka(S, h.olay["bar"])
    S.figur(h)
    S.baslik(baslik)
    dx_, dy_ = h.olay["diz"]
    S.isaret("Diz 90°'yi geçer", (dx_, dy_), (176, 58), hiza="start", t=0.98)
    S.not_(notu)
    return S


def _tg_leg_press(baslik, notu):
    """1RM leg press (45° kızak): minder, ray, platform + plaka; platform belirlenen derinliğe iner, bacaklar açılır."""
    S = TgSahne(3.2)
    s = 0.85
    kalca = (92, TG_ZEMIN - 22)
    h = hk_leg_press(kalca, s=s)
    rx, ry = h.olay["ray"]
    px, py = -ry, rx                                                          # rayya dik (aşağı-sağ)
    hx, hy = kalca
    boyun = h.olay["boyun"]
    # oturak ve sırt minderi (kalçanın altından boyun gerisine), gövde çerçevesi
    S.esya(S.cizgi(hx - 4, hy + 4, hx + 8, hy + 4) + S.cizgi(hx - 4, hy + 4, boyun[0] - 3, boyun[1] + 3)
           + S.cizgi(hx + 2, hy + 4, hx + 2, TG_ZEMIN) + S.cizgi(hx - 30, TG_ZEMIN, 236, TG_ZEMIN, "esya"))
    a0 = (hx + rx * 26 + px * 7, hy + ry * 26 + py * 7)                    # ray: platformun alt ucunun altından
    a1 = (hx + rx * 72 + px * 7, hy + ry * 72 + py * 7)
    S.esya(S.cizgi(*a0, *a1) + S.cizgi(a1[0], a1[1], a1[0], TG_ZEMIN))     # ray + arka dikme
    S.cubuk_iki(h.olay["platform"], kalinlik="vurgu")
    plaka = [(t, (x1 + x2) / 2 + rx * 7 + px * 2, (y1 + y2) / 2 + ry * 7 + py * 2)
             for t, x1, y1, x2, y2 in h.olay["platform"]]
    S.figur(hk_iz(h, sira=h.olay["alt"]))                                     # belirlenen derinlik
    _tg_plaka(S, plaka, r=6.0)
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_barfiks(baslik, notu):
    """Genel barfiks: _tg_modifiye_barfiks'in yüksek bar, bantsız varyantı (bar uçtan görünüş, dikmeye bağlı); çetele."""
    S = TgSahne(3.0)
    bar_y = 30
    h = hk_modifiye_barfiks(160, s=0.8, asili=True, bar_y=bar_y)
    bx, by = h.olay["bar"]
    dikme = bx + 34
    S.esya(S.cizgi(bx, by, dikme, by) + S.cizgi(dikme, by, dikme, TG_ZEMIN)
           + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="{TG_RENK["esya"]}"/>')
    S.figur(h)
    anlar = [t for t, p in h.anahtarlar[1:] if p is h.anahtarlar[-1][1]][:2]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru tekrar sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_sargent(baslik, notu):
    """
    Sargent: duvar (önden, sporcunun yanında), ayakta erişimde alt tebeşir izi, zirvede üst iz; iki iz arası ölçü
    oku. Ok şematiktir (figür ölçeği 0,85; tuvale sığsın diye sıçrama yüksekliği küçük çizilir).
    """
    S = TgSahne(3.4)
    dx = 146
    h = hk_sargent(dx, s=0.85)
    (_, ya), (_, yu) = h.olay["alt_iz"], h.olay["ust_iz"]
    S.esya(S.kutu(dx, 20.5, 6, TG_ZEMIN - 20.5, dolgu="dolgu", rx=0.5))                 # duvar
    S.belir(S.cizgi(dx - 3, ya, dx + 6, ya, "olcu"), h.olay["alt_t"], tur="isaret")     # alt iz: ayakta erişim
    S.belir(S.cizgi(dx - 3, yu, dx + 6, yu, "olcu"), 0.99, tur="isaret")               # üst iz: sıçrama
    S.figur(h)
    S.baslik(baslik)
    S.olcu(dx + 14, ya, dx + 14, yu, "Sıçrama yüksekliği", t=0.99,
           kilavuzlar=[(dx + 6, ya, dx + 14, ya), (dx + 6, yu, dx + 14, yu)], bag=[(1, "y", ("el1",), "min")])
    S.not_(notu)
    return S


def _tg_govde_kaldirma(baslik, notu):
    """
    Trunk lift: yüzüstü, üst gövde kalkar; dikey ok yerden ÇENEYE (son kare). Yerdeki işaret göz hizasındadır ama
    yalnız başı nötr tutmak içindir — ölçüm noktası değildir (Paket 20: önceki sürüm göze ölçüyordu).
    """
    S = TgSahne(3.0)
    _tg_mat(S, 6, 96)
    h = hk_govde_kaldirma(58, s=0.9)
    e = S.figur(h)
    cx, cy = e["cene"]
    bx = e["bas"][0]
    S.baslik(baslik)
    S.olcu(bx + 16, TG_ZEMIN, bx + 16, cy, "Çeneye kadar (en çok 30,5 cm)", t=0.85,
           kilavuzlar=[(cx + 2, cy, bx + 16, cy)], bag=[(1, "y", ("cene",), "min")])
    S.not_(notu)
    return S


def _tg_bukumlu_asilma(baslik, notu):
    """Bent Arm Hang: yüksek bar, avuçlar öne, çene barın üstünde, dirsekler bükük; süreölçer."""
    S = TgSahne(5.0)
    x, bar_y = 112, 36
    S.esya(S.cizgi(84, TG_ZEMIN, 84, bar_y) + S.cizgi(140, TG_ZEMIN, 140, bar_y) + S.cizgi(80, bar_y, 144, bar_y))
    S.figur(hk_asilma_bukumlu(x, bar_y, s=0.8))
    kx0, ky0, kx1, ky1 = S.kronometre(214, 84, t0=0.3)
    S.baslik(baslik)
    S.isaret("Asılı kalma süresi", ((kx0 + kx1) / 2, ky0), (158, 56), hiza="start", t=0.3)
    S.not_(notu)
    return S


def _tg_flamingo(baslik, notu, kiris=False, tutar=True):
    """Tek ayak denge (Eurofit kirişte, PREFIT ve Latorre yerde): bir denge kaybı ve çetelesi."""
    S = TgSahne(4.0)
    m = TG_OLCEK["_tg_flamingo"][0]
    taban = TG_ZEMIN
    if kiris:                                             # 50 cm × 4 cm kiriş
        yuk, uz = 0.04 * m, 0.5 * m
        S.esya(S.kutu(170 - uz / 2, TG_ZEMIN - yuk, uz, yuk, rx=0.5))
        taban = TG_ZEMIN - yuk
    h = hk_flamingo(170, s=0.85, tutar=tutar, zemin=taban)
    S.figur(h)
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, [h.olay["kayip_t"]])
    S.baslik(baslik)
    S.isaret("Denge kaybı sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=h.olay["kayip_t"])
    S.not_(notu)
    return S


def _tg_plate_tapping(baslik, notu):
    """Plate tapping (önden): masa, 60 cm arayla iki disk, ortada plaka; baskın el disklere sırayla dokunur."""
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_plate_tapping"][0]
    x, masa = 130, TG_ZEMIN - 0.7 * m
    dx = 0.3 * m
    S.esya(S.cizgi(x - 68, masa, x + 68, masa) + S.cizgi(x - 62, masa, x - 62, TG_ZEMIN) + S.cizgi(x + 62, masa, x + 62, TG_ZEMIN))
    r = 0.1 * m
    S.esya("".join(f'<ellipse cx="{x + k * dx:.1f}" cy="{masa - 1:.1f}" rx="{r:.1f}" ry="1.6" fill="{TG_RENK["dolgu"]}" '
                   f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>' for k in (-1, 1))
           + S.kutu(x - 6, masa - 2.5, 6, 1.5, dolgu="yuzey", rx=0.5))
    h = hk_masa_dokunma(x, masa, dx, s=0.9)
    S.figur(h)
    S.baslik(baslik)
    S.olcu(x - dx, masa + 14, x + dx, masa + 14, "60 cm", uc="ilk", metre=0.6,
           kilavuzlar=[(x - dx, masa + 2, x - dx, masa + 14), (x + dx, masa + 2, x + dx, masa + 14)])
    S.not_(notu)
    return S


def _tg_omuz_esneme(baslik, notu):
    """Shoulder stretch (arkadan): bir el omuz üstünden, öbürü bel altından; parmak uçları sırtta buluşur mu."""
    S = TgSahne(3.0)
    h = hk_omuz_esneme(110, s=0.95)
    S.figur(h)
    S.baslik(baslik)
    S.isaret("Parmak uçları değerse: geçti", h.olay["bulusma"], (150, 56), hiza="start", t=0.9)
    S.not_(notu)
    return S


def _tg_omuz_rotasyon(baslik, notu):
    """Omuz rotasyonu (sopa/ip): kollar düz, sopa önden baş üstünden sırta; elin izlediği yay kesik çizgi."""
    S = TgSahne(3.6)
    h = hk_omuz_rotasyon(120, s=0.75)
    S.yol(h.olay["el_yolu"])
    S.figur(h)
    yol = h.olay["el_yolu"]
    x0, y0 = yol[0]
    S.kaydir(S.cizgi(x0 - 4, y0, x0 + 4, y0, "vurgu"),
             [(i / (len(yol) - 1), x - x0, y - y0) for i, (x, y) in enumerate(yol)])
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_top_sektirme(baslik, notu):
    """Alternatif elle top sektirme (BOT-2): top elden yere, yerden öbür ele; çetele doğru sektirmeleri sayar."""
    S = TgSahne(3.6)
    h = hk_top_sektirme(170, s=0.85)
    S.figur(h)
    yol = h.olay["top_yolu"]
    S.top(yol, r=2.4)
    anlar = [t for t, _, y in yol if y > TG_ZEMIN - 4][:4]
    sx0, sy0, sx1, sy1 = S.sayac(12, 40, anlar)
    S.baslik(baslik)
    S.isaret("Doğru sektirme sayısı", (sx1, (sy0 + sy1) / 2), (sx1 + 8, 64), hiza="start", t=anlar[0])
    S.not_(notu)
    return S


def _tg_top_yakalama(baslik, notu):
    """KMS top yakalama: uygulayıcı (ikinci kişi) 1,5 m'den atar, çocuk iki eliyle yakalar."""
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_top_yakalama"][0]
    xc, xa = 84, 84 + 1.5 * m
    h = hk_top_yakala(xc, xa)
    S.figur(h.olay["atan"])
    S.figur(h)
    S.top(h.olay["top_yolu"], r=3.2)
    S.baslik(baslik)
    S.olcu(xc, TG_OLCU_Y, xa, TG_OLCU_Y, "1,5 m", uc="son", metre=1.5)
    S.not_(notu)
    return S


def _tg_top_firlatma(baslik, notu):
    """Latorre top fırlatma: çizgi gerisinden iki elle baş üzerinden ileri; ok çizgiden düşüşe (üstte, kılavuzlu)."""
    S = TgSahne(3.0)
    cizgi = 70
    _tg_direk(S, cizgi)
    h = hk_atma(cizgi - 10, "ileri", s=0.75)
    S.figur(h)
    (_, x0, y0) = h.olay["el_yolu"][-1]
    dusus = 214
    ucus = _tg_parabol(x0, y0, dusus, TG_ZEMIN - 3, 20, h.olay["birakma_t"], 0.92)
    S.top(h.olay["el_yolu"] + ucus[1:], r=3.6)
    S.baslik(baslik)
    S.olcu(cizgi, 34, dusus, 34, "Fırlatma mesafesi", etiket_yer="orta", t=0.93,
           kilavuzlar=[(cizgi, TG_ZEMIN - 6, cizgi, 34), (dusus, TG_ZEMIN - 8, dusus, 34)])
    S.not_(notu)
    return S


def _tg_capl_genel(baslik, notu):
    """CAMSA — GENEL GÖRÜNÜM (durağan kopya): yedi beceri yan yana, sıra numaralı; figür 3. beceride (yakalama)."""
    S = TgSahne(3.0)
    Z, k = TG_ZEMIN, TG_KALINLIK["esya"]
    cember = lambda x: (f'<ellipse cx="{x:.1f}" cy="{Z - 1}" rx="4" ry="1.4" fill="none" stroke="{TG_RENK["esya"]}" '
                        f'stroke-width="{k}"/>')
    xml = "".join(cember(x) for x in (24, 33, 42))                                   # 1 çift ayak: 3 çember
    for x in (54, 76):                                                               # 2 yana kayma konileri
        xml += f'<path d="M{x - 3},{Z} L{x},{Z - 7} L{x + 3},{Z} z" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
    xml += S.kutu(128, Z - 46, 4, 46, rx=0.8) + S.kutu(124, Z - 40, 4, 8, dolgu="yuzey", rx=0.8)   # 4 hedef
    xml += S.cizgi(140, Z + 2, 176, Z + 2, "kilavuz")                                  # 5 skipping 5 m
    xml += "".join(cember(x) for x in (184, 193, 202, 211, 220, 229))                   # 6 tek ayak: 6 çember
    for x in (244, 252):                                                             # 7 vuruş konileri
        xml += f'<path d="M{x - 3},{Z} L{x},{Z - 7} L{x + 3},{Z} z" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" stroke-width="{k}"/>'
    S.esya(xml)
    for n, x in enumerate((33, 65, 100, 126, 158, 206, 248), 1):
        S.numara(x, 56, n)
    h = hk_egil_al(100, s=0.55, tur="tut")                                           # 3: top yakalama anı
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu, t=0.05)
    return S


def _tg_capl_parkur(baslik, notu):
    """
    CAPL-2 motor beceri testi CAMSA — KAYAN SAHNE (Paket 22; Koordinasyon Parkuru ile aynı yapı). Parkur tuvalden
    geniş, grup olarak kayar; figür ortada kalır ve yanından geçen becerinin hareketini yapar (sıra protokolden,
    hk_camsa_turu). Topu atan uygulayıcı parkurun içinde (ikinci kişi, durağan). Başlık, not, beceri numarası ve
    süreölçer sabit katmanda; süreölçer vuruşta durur. Durağan kopya: genel görünüm (_tg_capl_genel).
    """
    m = TG_OLCEK["_tg_capl_parkur"][0]
    h = hk_camsa_turu(x_c=118, s=0.7, m=m)
    o, ek, Z = h.olay, h.olay["ekipman"], TG_ZEMIN
    S = TgSahne(o["sure"])
    r = 0.3 * m
    koni = lambda x: (f'<path d="M{x - 4:.1f},{Z} L{x:.1f},{Z - 10:.1f} L{x + 4:.1f},{Z} z" fill="{TG_RENK["dolgu"]}" '
                      f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>')
    xml = "".join(_tg_cember(x, Z - 1, r) for x in ek["cift_cember"] + ek["tek_cember"])  # 1 ve 6 çemberler
    xml += "".join(koni(x) for x in ek["kayma_koni"] + ek["koniler"])                       # 2 ve 7 koniler
    hx, hy = ek["hedef"]                                                                      # 4 hedef
    xml += S.kutu(hx + 4, Z - 1.6 * m, 4, 1.6 * m, rx=0.8) + S.kutu(hx, hy - 5, 4, 10, dolgu="yuzey", rx=0.8)
    a, b = ek["skip"]                                                                         # 5 skipping 5 m
    xml += S.cizgi(a, Z + 2, a, Z - 3, "kilavuz") + S.cizgi(b, Z + 2, b, Z - 3, "kilavuz")
    xml += S.figur_xml(o["uygulayici"], "partner", o["uygulayici_s"])                          # 3 uygulayıcı
    S.kaydir(xml, [(t, dx, 0) for t, dx in o["kayma"]])
    for yol in o["toplar"]:
        S.top(yol, r=2.2)
    S.figur(h)
    S.istasyon_araliklari = [(a, b) for _, a, b in o["beceriler"]]
    S.parkur_kaymasi = list(o["kayma"])
    for n, t0, t1 in o["beceriler"]:
        S.numara(22, 32, n, t0, t_bitis=t1)
    S.kronometre(238, 34, t0=o["beceriler"][0][1], t1=o["bitis_t"])
    S.baslik_nobet(baslik, [(ad, t0, t1) for ad, (_, t0, t1) in zip(o["beceri_adlari"], o["beceriler"])])
    S.not_(notu, t=0.02)
    S.duragan = _tg_capl_genel(baslik, notu)
    return S


def _tg_tenis_servis(baslik, notu):
    """
    Tenis servisi (yandan, kort şematik): arka çizgi gerisinden top havaya, raket yukarıdan; son kare TEMAS anı
    (Paket 24) — raket yukarıda, top temasta, hız oku topun çıkış yönünde, radarın kesik ışını oka bağlı. Servis
    karesi işaretli. Radar servis atanın arkasında. Raket başı vuran elin uzantısı (kayan halka).
    """
    S = TgSahne(3.0)
    m = TG_OLCEK["_tg_tenis_servis"][0]
    Z = TG_ZEMIN
    arka = 46                                                   # arka çizgi
    file_x = arka + 11.89 * m
    servis_x = file_x + 6.40 * m
    S.esya(S.cizgi(arka, Z - 3, arka, Z + 3) + S.cizgi(servis_x, Z - 3, servis_x, Z + 3)
           + S.cizgi(file_x, Z, file_x, Z - 0.914 * m) + S.kutu(file_x - 1, Z - 0.914 * m - 1, 2, 2, rx=0.5))
    S.esya(S.kutu(14, Z - 34, 8, 6, dolgu="yuzey", rx=1) + S.cizgi(18, Z - 28, 18, Z))   # radar tabancası (sehpada)
    h = hk_servis(arka - 10, s=0.75)
    S.figur(h)
    ry = h.olay["raket"]
    x0, y0 = ry[0][1], ry[0][2]
    S.kaydir(f'<ellipse cx="{x0:.1f}" cy="{y0:.1f}" rx="2.4" ry="3.6" fill="none" stroke="{TG_RENK["esya"]}" '
             f'stroke-width="{TG_KALINLIK["esya"]}"/>', [(t, x - x0, y - y0) for t, x, y in ry])
    tv = h.olay["vurus_t"]
    ax, ay = h.olay["atan_el"]
    tx, ty = h.olay["temas"]
    hedef = (file_x + 4.5 * m, Z - 2)
    bx, by = h.olay["tutan_el"]
    yol = [(0.0, bx, by), (0.25, ax, ay)] + [(0.25 + (tv - 0.25) * f, ax + (tx - ax) * f, ay + (ty - ay) * f - 18 * f * (1 - f))
                                             for f in (0.25, 0.5, 0.75, 1.0)]      # elde → atış → tepe → temas
    S.top(yol, r=2.0)                       # top temas noktasında kalır (Paket 24): durağan kare = vuruş anı
    ux, uy = hedef[0] - tx, hedef[1] - ty
    u = _math.hypot(ux, uy) or 1
    ox, oy = tx + ux / u * 6, ty + uy / u * 6
    sx, sy = tx + ux / u * 30, ty + uy / u * 30
    S.belir(S.cizgi(ox, oy, sx, sy, "olcu", ok="son"), 0.97, tur="isaret")              # hız oku: topun çıkış yönü
    S.belir(f'<path d="M22,{Z - 31:.1f} L{(ox + sx) / 2:.1f},{(oy + sy) / 2:.1f}" fill="none" stroke="{TG_RENK["olcu"]}" '
            f'stroke-width="{TG_KALINLIK["kilavuz"]}" stroke-dasharray="2 2"/>', 0.97, tur="isaret")   # radar ışını
    S.baslik(baslik)
    S.isaret("Servis karesi", hedef, (hedef[0] - 2, 70), hiza="middle", t=0.9)
    S.not_(notu)
    return S


def _tg_yuzme(baslik, notu):
    """
    Yüzme (CSS, T-30): havuz yandan — zemin çizgisi havuz tabanı, su çizgisi aynı kalınlıkta ikinci yatay çizgi;
    yüzücü serbest stil, kollar sırayla (toparlanma suyun üstünden). Su açık dolguyla gövdeyi örter; durağan kare
    kulaç ortası (Paket 24). Mesafe/süre farkı etiketlerde.
    """
    S = TgSahne(4.0)
    su = 72
    S.esya(f'<rect x="14" y="{su}" width="232" height="{TG_ZEMIN - su}" fill="{TG_RENK["dolgu"]}" fill-opacity="0.35"/>'
           + S.cizgi(14, su, 246, su, "zemin") + S.cizgi(14, su - 8, 14, TG_ZEMIN) + S.cizgi(246, su - 8, 246, TG_ZEMIN))
    S.figur(hk_serbest_stil(54, 200, su, s=0.75))         # son kare: bir kol suda çeker, öbürü suyun üstünde önde
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_split(baslik, notu):
    """Jimnastik esneklik profili — split: ayaktan hamleyle ön split; ölçü kasıktan zemine (0 = tam split)."""
    S = TgSahne(3.0)
    h = hk_split(120, s=0.85, uzaklik=10)
    e = S.figur(h)
    kx, ky = e["kalca"]
    S.baslik(baslik)
    S.olcu(kx + 52, TG_ZEMIN, kx + 52, ky, "Kasık–zemin (cm)", t=0.9,
           kilavuzlar=[(kx + 4, ky, kx + 52, ky)], bag=[(1, "y", ("kalca",), "min")])
    S.not_(notu)
    return S


def _tg_kurek_ergometre(baslik, notu):
    """
    Kürek ergometresi (2000 m ve 6 dk aynı çizim, fark etiketlerde): ray, önde volan gövdesi ve ekran, ayaklık;
    koltuk rayda kalçayla kayar; zincir volandan tutamağa. Son kare = kulacın bitişi (bacaklar gergin, tutamak göğüste).
    """
    S = TgSahne(4.0)
    s = 0.9
    ayak_x = 172
    h = hk_kurek_ergometre(ayak_x, s=s)
    ky = h.olay["koltuk_y"]
    fx, fy = ayak_x + 22, TG_ZEMIN - 20
    S.esya(S.cizgi(40, TG_ZEMIN - 7, fx, TG_ZEMIN - 7) + S.cizgi(46, TG_ZEMIN - 7, 46, TG_ZEMIN)
           + S.cizgi(fx + 6, TG_ZEMIN - 10, fx + 12, TG_ZEMIN))                              # ray ve ayakları
    S.esya(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="11" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["esya"]}"/>' + S.cizgi(fx - 2, fy - 11, fx - 8, fy - 30)
           + S.kutu(fx - 15, fy - 38, 12, 8, dolgu="yuzey", rx=1))                           # volan, ekran kolu, ekran
    ax, ay = h.olay["ayaklik"]
    S.esya(S.kutu(ax + 1, ay - 8, 4, 14, rx=1))                                              # ayaklık
    k0 = h.olay["koltuk"][0]
    S.kaydir(S.kutu(k0[1] - 7, ky + 1, 14, 4, rx=1), [(t, x - k0[1], 0) for t, x, _ in h.olay["koltuk"]])
    S.cubuk(fx, fy, h.olay["tutamak"], kalinlik="kilavuz")                                   # zincir
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_kayak_ergometre(baslik, notu):
    """
    Kano/kayak ergometresi (200, 500, 1000 m aynı çizim, fark etiketlerde): alçak koltuk, ayaklık, önde volan
    gövdesi; çift palalı kürek iki yana sırayla çekilir. Son kare = yakalama (pala aşağıda, öne uzanmış).
    """
    S = TgSahne(4.0)
    s = 0.9
    x = 96
    h = hk_kayak_ergometre(x, s=s)
    ky = h.olay["koltuk_y"]
    ax, ay = h.olay["ayaklik"]
    S.esya(S.cizgi(60, TG_ZEMIN - 6, 228, TG_ZEMIN - 6) + S.cizgi(66, TG_ZEMIN - 6, 66, TG_ZEMIN)
           + S.cizgi(222, TG_ZEMIN - 6, 222, TG_ZEMIN))                                      # gövde kirişi
    S.esya(S.kutu(x - 10, ky + 1, 20, TG_ZEMIN - 6 - ky - 1, rx=1)                            # koltuk
           + S.kutu(ax + 1, ay - 8, 4, TG_ZEMIN - 6 - ay + 8, rx=1))                           # ayaklık
    S.esya(f'<circle cx="{ax + 26:.1f}" cy="{TG_ZEMIN - 18}" r="10" fill="{TG_RENK["dolgu"]}" stroke="{TG_RENK["esya"]}" '
           f'stroke-width="{TG_KALINLIK["esya"]}"/>')                                         # volan gövdesi
    S.cubuk_iki(h.olay["kurek"], kalinlik="esya")                                            # çift palalı kürek
    S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_halter(baslik, notu):
    """
    Halter 1RM: solda koparma (yerden tek hareketle baş üstüne, derin çömelişte karşılama), sağda silkme (omuzdan
    baş üstüne, makas). Bar yandan plaka diski olarak görünür. Son kare = her ikisinde bar baş üstünde, kollar kilitli.
    """
    S = TgSahne(3.0)
    s = 0.6
    k = hk_koparma(78, s=s)
    j = hk_silkme(182, s=s)
    r = k.olay["plaka"]
    for h in (k, j):
        b0 = h.olay["bar"][0]
        S.kaydir(f'<circle cx="{b0[1]:.1f}" cy="{b0[2]:.1f}" r="{r}" fill="{TG_RENK["dolgu"]}" '
                 f'stroke="{TG_RENK["esya"]}" stroke-width="{TG_KALINLIK["esya"]}"/>',
                 [(t, x - b0[1], y - b0[2]) for t, x, y in h.olay["bar"]])
        S.figur(h)
    S.baslik(baslik)
    S.not_(notu)
    return S


def _tg_suda_sicrama(baslik, notu):
    """
    Su topu suda dikey sıçrama: derin su (dip yok), su çizgisi ve açık dolgu; eggbeater beklemesi, sonra sıçrama.
    Ölçü: su yüzeyinden uzanan elin ucuna (son kare, tepe).
    """
    S = TgSahne(3.0)
    su = 76
    S.esya(f'<rect x="20" y="{su}" width="220" height="{TG_ZEMIN - su}" fill="{TG_RENK["dolgu"]}" fill-opacity="0.35"/>'
           + S.cizgi(20, su, 240, su, "zemin"))
    h = hk_eggbeater_sicrama(120, su, s=0.6)
    S.figur(h)
    ex, ey = h.olay["el"]
    S.baslik(baslik)
    S.olcu(ex + 26, su, ex + 26, ey, "Su yüzeyinden (cm)", t=0.9,
           kilavuzlar=[(ex + 3, ey, ex + 26, ey)], bag=[(1, "y", ("el1",), "min")])
    S.not_(notu)
    return S


# Ölçek tablosu: sahne → (1 m kaç tuval birimi, açıklama). Protokoldeki mesafe okları bu ölçekle çizilir;
# figür (≈ 1,35 m çocuk ≈ 92 birim) ile mesafe ölçeği aynı değilse "şematik" yazılır.
TG_OLCEK = {
    "_tg_surat": (9.5, "şematik: 20 m tuvale sığsın diye figürden küçük ölçek"),
    "_tg_pro_agility": (75 / 4.57, "şematik"),
    "_tg_mekik": (10.0, "şematik"),
    "_tg_goz_el": (46.0, "figürle aynı ölçek (0,66 ölçekli çocuk: 1,32 m ≈ 61 birim)"),
    "_tg_yoyo": (8.0, "şematik"),
    "_tg_paten_30": (6.2, "şematik"),
    "_tg_paten_6_30": (6.2, "şematik"),
    "_tg_s_turn": (12.0, "şematik, yandan: buz yüzeyi zemin çizgisinin gerisinde ince şerit"),
    # Paket 17 — düz sprintte (_tg_sprint) ok şematiktir: 10 m'den 400 m'ye aynı boy, mesafe etikette
    "_tg_hizlanma_profili": (6.4, "şematik"),
    "_tg_rsa": (6.4, "şematik"),
    "_tg_list": (10.0, "şematik"),
    "_tg_30_15": (5.0, "şematik"),
    "_tg_sjft_judo": (23.0, "şematik: iki uke arası 6 m"),
    "_tg_modifiye_barfiks": (30.4, "figürle aynı ölçek (0,85 ölçekli figür; elastik bant bardan 19 cm aşağıda)"),
    "_tg_otur_uzan": (68.0, "şematik: sıfır ile ayak tabanı arası okunsun diye cetvel figürden büyük ölçekte"),
    "_tg_flamingo": (58.0, "figürle aynı ölçek (0,85 ölçekli çocuk)"),
    "_tg_plate_tapping": (61.5, "figürle aynı ölçek (0,9 ölçekli çocuk)"),
    "_tg_top_yakalama": (58.0, "figürle aynı ölçek (0,7 ölçekli çocuk, 3-6 yaş)"),
    "_tg_yan_adim": (25.0, "şematik"),
    "_tg_sicrama_turleri": (35.8, "figürle aynı ölçek (yetişkin ≈ 1,8 m ≈ 64 birim)"),
    "_tg_tenis_servis": (11.0, "şematik: arka çizgiden servis karesine (11,89 + 6,40 m) tuvale sığsın; figür ölçeksiz"),
    "_tg_capl_parkur": (34.5, "figürle aynı ölçek; yalnız skipping 5 m protokolde, öbür aralıklar şematik"),
    "_tg_koordinasyon": (34.5, "figürle aynı ölçek (0,7 ölçekli çocuk ≈ 1,3 m ≈ 45 birim); kayan sahne"),
}


import functools as _functools
_TG_YOYO_KRITIK = ("20 m çift yön koşu, bip sesiyle artan hız; her turda 10 sn aktif dinlenme (5 m gidip gelme); "
                   "2 kez üst üste bipe yetişemeyen testi bitirir.")
_TG_YOYO2_KRITIK = ("IR1 ile aynı 20 m çift yön format ve 10 sn aktif dinlenme; başlangıç hızı daha yüksek (13 km/h); "
                    "2 kez üst üste bipe yetişemeyen bitirir.")
_TG_WINGATE_KRITIK = ("Ergometrede oturarak, vücut ağırlığının %7,5'i dirençle 30 sn maksimal pedal çevirme; "
                      "pik güç, ortalama güç ve yorgunluk indeksi hesaplanır.")
_TG_WINGATE = {"Wingate 30sn Bisiklet Testi": "", "Wingate (Muay Thai)": "Muay Thai", "Wingate (MMA)": "MMA",
               "Wingate (Kickboks)": "Kickboks"}
_TG_YOYO_IR1 = ["Güreş", "Judo", "Tenis", "Muay Thai", "BJJ", "Badminton", "Masa Tenisi", "Squash", "Karate",
                "Taekwondo", "Boks", "Futbol", "Basketbol", "Voleybol", "Hentbol", "Genel"]

# Test → (sahne, en kritik ayrıntı — protokolden)
TEST_GORSELLERI = {
    "Boy ve Vücut Ağırlığı (TSYT)": (_tg_boy, "Topuk, kalça, sırt ve baş aynı dikey doğrultuda; sırt cetvele değmez, gözler karşıya; ölçüm derin nefes tutulurken alınır."),
    "Oturma Yüksekliği (TSYT)": (_tg_oturma, "Dizler 90°, kalça-sırt-baş aynı dikeyde; oturma yüzeyinden başın üstüne ölçülür."),
    "Kulaç Uzunluğu (TSYT)": (_tg_kulac, "Kollar yere paralel ve gergin, avuç içleri karşıya; iki orta parmak ucu arası ölçülür."),
    "Esneklik (Uzan Eriş) — TSYT": (_tg_esneklik, "Ayak tabanları sehpaya tam dayalı, dizler gergin; cetvel yavaşça itilir ve en uzak noktada beklenir. Sıfır noktası talimatta yazmaz: yalnız TSYT sehpasıyla ölçülür."),
    "Dikey Sıçrama (TSYT, kollar serbest)": (_tg_dikey, "Kollar serbest, beklemeden çöküp sıçrar; aynı noktaya ve dizler gergin iner — uzağa düşerse deneme tekrarlanır."),
    "El Kavrama Kuvveti (TSYT)": (_tg_kavrama, "Ayakta, kol gergin ve aşağıya uzanmış; her el için tek ölçüm."),
    "Geriye Sağlık Topu Atma (TSYT)": (_tg_saglik_topu, "Sırt atış alanına dönük; top baş üzerinden geriye, yaklaşık 45° ile atılır; çizgiyi aşıp geriye düşen atış tekrarlanır."),
    "Çeviklik — Pro Agility 5-10-5 (TSYT)": (_tg_pro_agility, "Orta çizgiden 4,57 m → 9,14 m → orta; her dönüşte çizgiye elle dokunulur."),
    "20m Sürat (TSYT)": (_tg_surat, "Çıkış çizgisi başlangıç fotoselinin 1 m gerisinde; bitiş fotoseli yavaşlamadan geçilir."),
    "Koordinasyon Parkuru (TSYT)": (_tg_koordinasyon, "Dokuz istasyon tek parkurda, fotoselle ölçülür; hatalı istasyon yeniden yapılır (süre cezası yok)."),
    "Mekik Koşusu (TSYT)": (_tg_mekik, "Her sinyalde 20 m ilerideki çizgiye basılır; sinyali iki kez üst üste kaçıran çocuğun testi biter."),
    "Dengede Geriye Yürüme (Balancing Backwards)": (_tg_geriye_denge, "Kiriş üzerinde geriye doğru yürünür; bir denemede en çok 8 adım sayılır, ayak yere değince deneme biter."),
    "Yana Sıçrama (Jumping Sideways)": (_tg_yana_sicrama, "15 sn boyunca çıtanın üzerinden çift ayakla sağa-sola; çıtaya basma ve tek ayakla iniş geçersiz."),
    "Yana Platform Değiştirme (Moving Sideways)": (_tg_yana_platform, "20 sn: boştaki platformu yana koy, üstüne bas; her koyma ve her basma bir puan."),
    "Göz-El Koordinasyonu (Duvara Atıp Yakalama)": (_tg_goz_el, "Duvardan 1 m uzakta; top 1 × 1 m kareye (alt kenarı 1 m yükseklikte) atılır, sektikten sonra yakalanır."),
    "Tek Ayak Engel Üzerinden Sıçrama (Hopping for Height)": (_tg_tek_ayak, "Tek ayakla engelin üzerinden geçilir; inişten sonra aynı ayakla en az 2 sıçrama daha yapılmalı."),
    # Paket 15 — Güreş
    "Special Wrestling Fitness Test (SWFT)": (_tg_swft, "3 × 30 sn aktif periyot, aralarında 20 sn pasif dinlenme; manken suplex tekniğiyle sırtüstü devrilir; test bitiminde ve 1. dakikada KAH ölçülür."),
    "Modified SJFT (Güreş için)": (_tg_sjft, "3 periyot: 15 sn / 30 sn / 30 sn, aralarında 10 sn dinlenme; her periyotta manken en çok sayıda devrilir; test bitiminde ve 1. dakikada KAH ölçülür."),
    "Simulated Wrestling Match (6 dk)": (_tg_gures_mac, "Eşit ağırlık kategorisinde iki sporcu; 2 × 3 dakika mat süresi, 30 sn ara; her periyot sonunda KAH ve RPE (Borg)."),
    # Paket 15 — Buz Hokeyi (NHL/NHLTM Off-Ice bir bataryadır, tek sahneye sığmaz: görseli yok)
    "30m Paten Hızı": (_tg_paten_30, "Durarak başlangıç; 30 m düz buz maksimal hızla kat edilir; 3 deneme, en iyi süre."),
    "Hızlanma Paten Testi (6m + 30m)": (_tg_paten_6_30, "Durarak başlangıç; fotosel 6. ve 30. metredeki süreleri ayrı kaydeder; 3 deneme, en iyi değerler."),
    "S-Turn Testi": (_tg_s_turn, "5 koni S şeklinde 3 m aralıkla; koniler slalom yaparak geçilir; 3 deneme, en iyi süre."),
    # Yo-Yo IR1: 16 test tek sahne, branş adı yalnız başlıkta
    **{f"Yo-Yo IR1 ({b})": (_functools.partial(_tg_yoyo, "" if b == "Genel" else b), _TG_YOYO_KRITIK) for b in _TG_YOYO_IR1},
    # Paket 17 — Futbol, Voleybol, Basketbol, Hentbol, Atletizm (+ Halter dikey sıçrama, Yo-Yo IR2 Genel)
    "Yo-Yo IR2 (Futbol)": (_functools.partial(_tg_yoyo, "Futbol", "IR2"), _TG_YOYO2_KRITIK),
    "Yo-Yo IR2 (Genel)": (_functools.partial(_tg_yoyo, "", "IR2"), _TG_YOYO2_KRITIK),
    "10m Sprint": (_functools.partial(_tg_sprint, "10 m", "Durarak başlangıç, 10 m maksimal hız",
                                      "3 deneme · arada 3-5 dk tam toparlanma", 3),
                   "Durarak başlangıç (ayakta veya blok); 10 m maksimal hız; 3 deneme, arada 3-5 dk tam toparlanma; en iyi süre."),
    "20m Sprint": (_functools.partial(_tg_sprint, "20 m", "Durarak başlangıç, 20 m maksimal hız",
                                      "3 deneme; en iyi süre kaydedilir", 3),
                   "Durarak başlangıç; 20 m maksimal hız (hızlanma + geçiş fazı); 3 deneme, en iyi süre."),
    "100m Sprint": (_functools.partial(_tg_sprint, "100 m", "Blok veya ayakta başlangıç, 100 m",
                                       "2-3 deneme · arada 8-10 dk tam toparlanma", 3, True),
                    "Blok veya ayakta başlangıç; 100 m maksimal; 2-3 deneme, arada 8-10 dk tam toparlanma; en iyi süre."),
    "200m Sprint": (_functools.partial(_tg_sprint, "200 m", "Virajlı pistte 200 m, blok ya da ayakta",
                                       "2 deneme · arada 10-15 dk tam toparlanma", 2, True),
                    "Virajlı pistte, blok veya ayakta başlangıç; 200 m maksimal; 2 deneme, arada 10-15 dk toparlanma."),
    "400m Sprint": (_functools.partial(_tg_sprint, "400 m", "Blok veya ayakta başlangıç, pistte 400 m",
                                       "2 deneme · arada 15-20 dk tam toparlanma", 2, True),
                    "Blok veya ayakta başlangıç; 400 m maksimal; 2 deneme, arada 15-20 dk tam toparlanma; en iyi süre."),
    "Sprint Hızlanma Profili (10-20-30m)": (_tg_hizlanma_profili, "Fotosel 10, 20 ve 30. metrede; 0-10, 10-20, 20-30 m bölüm süreleri ayrı; 3 deneme, her bölümde en iyi değer."),
    "30-15 İntermittent Fitness Test (30-15 IFT)": (_tg_30_15, "40 m alan (3 m güvenlik bölgeleri); 30 sn koşu + 15 sn yürüme; hız 8 km/h'den her aşamada 0,5 km/h artar; 2 kez üst üste yetişemeyen bitirir."),
    "RSA Testi (Repeated Sprint Ability)": (_tg_rsa, "6 × 30 m sprint, her sprint arasında 25 sn pasif dinlenme; durarak başlangıç; en iyi, ortalama süre ve yorgunluk indeksi."),
    "Loughborough İntermittent Shuttle Test (LIST)": (_tg_list, "20 m alanda yürüyüş → koşu → hızlı koşu → sprint → dinlenme döngüsü; standart 5 × 15 dk bölüm (toplam 75 dk)."),
    "Illinois Çeviklik Testi": (_functools.partial(_tg_parkur, "illinois", "10 × 5 m, 8 koni: zigzag + slalom (~60 m)",
                                                   "3 deneme, en iyi süre kaydedilir", "Yüzüstü başlangıç"),
                                "Yüzüstü, baş başlangıç çizgisinde başlar; 10 × 5 m alanda 8 koniyle zigzag + slalom (~60 m); 3 deneme, en iyi süre."),
    "Hentbol Çeviklik ve Sprint Testi": (_functools.partial(_tg_parkur, "illinois", "Illinois çeviklik parkuru",
                                                            "30 m sprint ayrıca; 3 deneme, en iyi süre", "Yüzüstü başlangıç"),
                                         "İki bileşen: 30 m sprint (durarak) ve standart Illinois çeviklik; her biri 3 deneme, en iyi süre."),
    "Voleybol Çeviklik Testi (VAT)": (_functools.partial(_tg_parkur, "vat", "Ortadan 4 köşeye, her köşede yere dokun",
                                                         "Saha 9 × 18 m · 2 deneme, en iyi süre"),
                                      "Orta noktadan sol ön → sağ ön → sağ arka → sol arka köşe → başlangıç; her köşede zemine dokunulur; 2 deneme."),
    "NBA Lane Agility Testi": (_functools.partial(_tg_parkur, "nba_lane", "Aşağı → sol → yukarı → sağ → aşağı",
                                                  "2 deneme; en iyi süre (az = iyi)", "Serbest atış çizgisi köşesi"),
                               "Serbest atış çizgisi köşesinden, savunma duruşunda; boya alanı çevresinde aşağı → sol → yukarı → sağ → aşağı; 2 deneme."),
    "NBA 3/4 Saha Sprint Testi": (_functools.partial(_tg_sprint, "Yaklaşık 21 m", "Basket altından karşı basket altına",
                                                     "Durarak başlangıç; 2 deneme, en iyi süre", 2),
                                  "Basket altından karşı basket altına (yaklaşık 3/4 saha ≈ 21 m), durarak başlangıç; 2 deneme, en iyi süre."),
    "20m Sprint - Voleybol": (_functools.partial(_tg_sprint, "20 m", "Durarak başlangıç, 20 m maksimal hız",
                                                 "3 deneme yapılır; en iyi süre kaydedilir", 3),
                              "Durarak başlangıç; 20 m maksimal hız; 3 deneme, en iyi süre."),
    "Dikey Sıçrama - Voleybol (CMJ + SJ + DJ)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ", "DJ"),
                                                                     "Soldan: CMJ, SJ (90° statik), DJ (30 cm)",
                                                                     "Eller kalçada; 3 deneme, en iyi yükseklik"),
                                                 "CMJ: eller kalçada, ön-çömelmeyle; SJ: 90° statik başlangıç, ön-çömelme yok; DJ: 30 cm'den inip minimal temasla sıçrama; 3'er deneme."),
    "Dikey Sıçrama - Basketbol (CMJ + SJ)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                                 "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                                 "Eller kalçada; 3 deneme, en iyi değer", "2 sn bekleme"),
                                             "CMJ: eller kalçada, serbest ön-çömelmeyle; SJ: 90° statik çömelme, 2 sn bekleme, ön-çömelme yok; 3'er deneme."),
    "Dikey Sıçrama (Hentbol)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                    "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                    "Standart CMJ ve SJ protokolü"),
                                "Standart CMJ (ön-çömelmeyle) ve SJ (statik çömelmeden, ön-çömelme yok) protokolü."),
    "Dikey Sıçrama ve CMJ (Halter)": (_functools.partial(_tg_sicrama_turleri, ("CMJ", "SJ"),
                                                          "Soldan: CMJ çök-sıçra, SJ statik çömelmeden",
                                                          "Eller kalçada; CMJ − SJ farkı da izlenir"),
                                      "Standart CMJ ve SJ, eller kalçada; CMJ − SJ farkı reaktif kuvvet göstergesidir."),
    "Nordic Hamstring Kuvvet Testi (NHT)": (_tg_nordic, "Diz üstü, bacaklar cihaza (ya da partnere) sabit; gövde öne kontrollü ve yavaşça iner; her bacak eksantrik pik kuvveti; 3 tekrar, en yüksek."),
    "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)": (_tg_diz_dinamometre, "Dinamometrede izometrik: kuadriseps 90°, hamstring 45° diz fleksiyonunda; izokinetik 180°/sn; her iki bacak, pik tork (Nm/kg)."),
    # Paket 18 — mücadele sporları (JPFT ve MMA Fiziksel Uygunluk Bataryası çok bileşenli: görselsiz)
    "Special Judo Fitness Test (SJFT)": (_tg_sjft_judo, "İki uke 6 m aralıkla, tori ortada; A = 15 sn, B = 30 sn, C = 30 sn, aralarında 10 sn; her periyotta en çok ippon atış; HR0 ve HR1."),
    "Uchi-Komi Fitness Test (UKFT)": (_tg_ukft, "Uke direnmez; tori seçtiği teknikle 30 sn boyunca giriş-çıkış yapar, tam devirme yok; 3 set, aralarında 30 sn dinlenme."),
    "Taekwondo Spesifik Aerobik Test (TSAT)": (_functools.partial(
        _tg_vurus, ("ap", "yop", "dollyo"), "Ap chagi, dollyo chagi, yop chagi; 2 dk",
        "Kombinasyon her 20 sn'de değişir; HR0, HR3", "Toplam teknik sayısı", [(20, True)] * 6, 0.8, "ped"),
        "2 dakika boyunca ap chagi, dollyo chagi, yop chagi maksimal hızda; kombinasyon her 20 sn'de değişir; HR0 ve HR3."),
    "Karate Spesifik Dayanıklılık Testi (KSDT)": (_functools.partial(
        _tg_vurus, ("tsuki", "uchi", "geri"), "Tsuki, uchi, geri; 2 dk kumite simülasyonu",
        "Kombinasyon her 30 sn'de değişir; HR0, HR1, HR3", "Toplam teknik sayısı", [(30, True)] * 4, 0.8, "ped"),
        "2 dk maksimal kumite simülasyonu (tsuki, uchi, geri); kombinasyon her 30 sn'de değişir; HR0, HR1, HR3."),
    "Muay Thai Spesifik Dayanıklılık Testi (MTSDT)": (_functools.partial(
        _tg_vurus, ("jab", "cross", "teep", "knee", "roundhouse"), "Jab-cross-hook, teep, roundhouse, knee",
        "5 × 3 dk tur, aralarında 2 dk pasif dinlenme", "Tur başına teknik sayısı",
        [(3, True), (2, False)] * 4 + [(3, True)], 4.5, "torba"),
        "Kum torbası ya da pao; 5 × 3 dk tur, aralarında 2 dk pasif dinlenme; her tur teknik sayısı ve HR."),
    "Kickboks Spesifik Kondisyon Testi (KSKT)": (_functools.partial(
        _tg_vurus, ("jab", "cross", "roundhouse"), "Kum torbasına yumruk + tekme serisi",
        "3 × 2 dk tur, aralarında 1 dk pasif dinlenme", "Tur başına darbe sayısı",
        [(2, True), (1, False)] * 2 + [(2, True)], 12, "torba"),
        "Kum torbasına 3 × 2 dk maksimal yumruk + tekme serisi, aralarında 1 dk pasif dinlenme; tur başına darbe ve HR."),
    "Boks Spesifik Dayanıklılık Testi": (_functools.partial(
        _tg_vurus, ("hook", "uppercut", "jab", "cross"), "Jab, cross, hook, uppercut kombinasyonları",
        "3 × 3 dk tur, aralarında 1 dk pasif dinlenme", "Tur başına darbe sayısı",
        [(3, True), (1, False)] * 2 + [(3, True)], 9, "torba"),
        "Kum torbası ya da lapa; 3 × 3 dk maksimal kombinasyon serisi, aralarında 1 dk pasif dinlenme; HR ve RPE."),
    "Sambo Spesifik Fitness Testi (SSFT)": (_functools.partial(
        _tg_mac, [(3, True), (1, False)] * 2 + [(3, True)], 8, "Kurtkalı simüle maç; atış ve kilit sayılır",
        "3 × 3 dk, 1 dk ara", "HR her tur sonunda ölçülür"),
        "3 × 3 dk simüle maç (resmi sambo süreleri), aralarında 1 dk pasif dinlenme; atış ve kilit sayısı, HR."),
    "MMA Spesifik Kondisyon Testi (MMA-SCT)": (_functools.partial(
        _tg_mac, [(5, True), (1, False)] * 2 + [(5, True)], 5.5, "Simüle maç (UFC/Bellator formatı)",
        "3 × 5 dk, 1 dk ara", "Vuruş, takedown, yerden kontrol sayılır; HR"),
        "3 × 5 dk simüle maç, aralarında 1 dk pasif dinlenme; vuruş, takedown ve yerden kontrol sayısı; HR."),
    "BJJ Spesifik Dayanıklılık Testi (BJJSFT)": (_functools.partial(
        _tg_mac, [(5, True), (1, False)] * 2 + [(5, True)], 5.5, "Simüle maç; her turda partner değişir",
        "3 × 5 dk, 1 dk ara", "Teknik/geçiş sayısı; HR her tur sonunda"),
        "3 × 5 dk simüle maç, aralarında 1 dk pasif dinlenme; partner her turda değişir; teknik/geçiş sayısı, HR."),
    "BJJ Kavrama Kuvveti ve Dayanıklılığı": (_functools.partial(
        _tg_asilma, "Gi yakasına iki elle asılı kalma", "MVC 3 deneme · %60 MVC'de 60 sn tutma"),
        "Gi yakasına iki elle asılı kalma süresi (sn); ayrıca her el MVC 3 deneme ve %60 MVC'de 60 sn tutma."),
    "El Kavrama ve Kurtka Kavrama (Sambo)": (_functools.partial(
        _tg_asilma, "Kurtka yakasından tek el ve çift el asılma", "MVC: her el için 3 deneme (kg)"),
        "Kurtka yakasına tek el ve çift el asılı kalma süreleri (sn); ayrıca her el için 3 deneme MVC (kg)."),
    "Karate Çeviklik Testi (KAT)": (_functools.partial(
        _tg_parkur, "t_testi", "A → B → C → D → B → A", "4 koni T şeklinde · 3 deneme, en iyi süre",
        "A: başlangıç"),
        "4 koni T şeklinde; standart T-testi sırası A → B → C → D → B → A; 3 deneme, en iyi süre."),
    "Taekwondo Çeviklik ve Hız Testi": (_functools.partial(
        _tg_parkur, "t_testi", "T-testi; 10 m sprint ayrıca ölçülür", "3 deneme, en iyi süre", "A: başlangıç"),
        "İki bileşen: 10 m sprint (durarak) ve standart T-testi; her biri 3 deneme, en iyi süre."),
    "Masa Tenisi Reaksiyon ve Çeviklik Testi": (_tg_yan_adim, "Üç bileşen: görsel uyarana reaksiyon (20 deneme), 3 m sağ-sol yan adım (15 sn), masa başı vuruş (30 sn)."),
    # Paket 19 — Çocuk ve genç fiziksel uygunluk bataryaları. Aynı hareket tek çizim; etiketler testin kendi protokolünden.
    # Eurofit
    "Flamingo Denge Testi": (_functools.partial(
        _tg_flamingo, "Kirişte tek ayak, öbür ayak elde, 1 dk", "Kiriş 50 cm × 4 cm · her yere değişte sayaç", kiris=True),
        "Dominant ayakla 50 cm × 4 cm kirişte durulur, öbür bacak dizden bükülüp elle tutulur; 1 dakikada yere dokunma sayısı."),
    "Plate Tapping (Disk Dokunma) Testi": (_functools.partial(
        _tg_plate_tapping, "Öbür el ortadaki plakada", "Diskler arasında 25 tur (50 dokunma) · süre"),
        "Baskın olmayan el ortadaki plakada; baskın el 60 cm arayla duran iki diske sırayla 25 tur (50 dokunma) dokunur; süre."),
    "Otur-Uzan (Sit and Reach) Testi": (_functools.partial(
        _tg_otur_uzan, "Bacaklar düz, ayak tabanları kutuda", "Ayak tabanı hizası 15 cm, sıfır değil", 15),
        "Eurofit kutusunda ayak tabanı hizası ölçekte 15 cm'dir (sıfır değil); parmak uçlarına uzanan 15 cm alır. 2 deneme."),
    "Durarak Uzun Atlama": (_functools.partial(
        _tg_uzun_atlama, "İki ayak çizginin arkasında, kol salınımı", "3 deneme, en iyisi"),
        "İki ayak başlangıç çizgisinin arkasında; kol salınımıyla maksimal yatay atlama. 3 deneme, en iyi mesafe (cm)."),
    "El Kavrama Kuvveti (Eurofit)": (_functools.partial(
        _tg_kavrama, "Ayakta, kol gövdeye paralel ve uzatılmış", "Maksimal güçle sık (kg)", "Her el 2 deneme · iki elin en iyisi toplanır"),
        "Ayakta, kol gövdeye paralel ve uzatılmış; her el 2 deneme. Skor iki elin en iyi değerlerinin toplamıdır (kg)."),
    "Asılı Durma - Bükümlü Kol (Bent Arm Hang)": (_functools.partial(
        _tg_bukumlu_asilma, "Çene barın üstünde, avuçlar öne", "Çene barın altına düşünce süre durur"),
        "Çene bar seviyesinin üstünde, avuçlar öne (pronasyon) asılı kalınır; çene barın altına düştüğünde süre durur."),
    "Mekik (Sit-Up) Testi - 30sn": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında kenetli", "30 sn içinde doğru tekrar sayısı"),
        "Sırtüstü, dizler 90° bükülü, eller ense arkasında kenetli; 30 saniyede tamamlanan doğru tekrar sayısı."),
    "10x5m Mekik Koşusu (Shuttle Run)": (_functools.partial(
        _tg_mekik_kosusu, "5 m", "İki çizgi arası 10 kez (5 gidiş-5 dönüş)", "Her dönüşte çizgiyi bir ayakla geç", 10),
        "5 m aralıklı iki çizgi arasında 10 kez (5 gidiş-5 dönüş); her dönüşte çizgi bir ayakla geçilir. Toplam süre."),
    "20m Mekik Koşusu (Eurofit/Léger)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "Bipe 2 kez üst üste yetişemeyince biter"),
        "20 m ardışık bip sesleri arasında koşulur; hız her dakika artar; bipe 2 kez üst üste yetişemeyince test biter."),
    # FitnessGram (PYFP aynı protokolü uygular — aynı ad aynı çizim)
    "PACER (20m Mekik Koşusu)": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "20 m ardışık ses sinyalleri arasında koşulur; hız her dakika artar; 2 kez üst üste yetişemeyince test biter."),
    "Push-Up (Şınav) Testi": (_functools.partial(
        _tg_sinav, "Dakikada 20 vuruş, alt noktada dirsek 90°", "Form bozulana kadar"),
        "Standart şınav, alt noktada dirsek 90°; metronom dakikada 20 vuruş; form bozulana kadar doğru tekrar sayısı."),
    "Modified Pull-Up Testi": (_functools.partial(
        _tg_modifiye_barfiks, "Sırtüstü, vücut düz, avuçlar öne", "Çene elastik bandın üstüne · form bozulana kadar"),
        "Sırtüstü, bar uzanmış kolların 1-2 inç üstünde, avuçlar öne, vücut düz; çene bardan 7-8 inç aşağıdaki bandın üstüne çekilir."),
    "Curl-Up (Kademeli Mekik) Testi": (_functools.partial(
        _tg_govde_fleksiyonu, "curlup", "Dizler yaklaşık 140°, eller uyluklarda", "Dakikada 20 vuruş · en çok 75 tekrar",
        "Parmaklar şeridi aşar"),
        "Dizler yaklaşık 140°, eller uyluklarda; baş ve omuzlar kalkarken parmaklar ölçüm şeridini aşar; en çok 75 tekrar."),
    "Trunk Lift (Gövde Kaldırma) Testi": (_functools.partial(
        _tg_govde_kaldirma, "Yüzüstü, baş ve gövde yavaşça kalkar", "Yerden çeneye · 2 deneme"),
        "Yüzüstü; gözler yerdeki işarette (baş nötr), üst gövde yavaşça kaldırılır; yerden ÇENEYE ölçülür; en çok 30,5 cm."),
    "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ayak tabanı hizası 22,9 cm (9 inç), sıfır değil",
        22.9, tek_bacak=True),
        "Bir bacak düz, öbürü dizden bükülü ve ayak tabanı yerde; cetvelin 22,9 cm (9 inç) işareti kutunun ayak kenarındadır."),
    "Shoulder Stretch (Omuz Esnekliği) Testi": (_functools.partial(
        _tg_omuz_esneme, "Bir el omuz üstünden, öbürü bel altından", "Her omuz ayrı · geçti / kalmadı"),
        "Bir el omuz üzerinden, öbürü bel altından sırta uzatılır; parmak uçları sırtta değiyorsa geçti. Her omuz ayrı."),
    "1 Mil Yürüyüş/Koşu Testi": (_functools.partial(
        _tg_sprint, "1 mil (1609 m)", "Mümkün olduğunca hızlı, 4 tur × 400 m", "Bitişte kalp atımı: ilk 15 sn × 4", 0,
        fotosel=False),
        "1 mil (1609 m; 400 m pistte 4 tur) olabildiğince hızlı tamamlanır; bitişte kalp atımı ilk 15 saniye × 4."),
    # Presidential (PYFP): FitnessGram'la aynı protokol — çizim aynı, ad farklıysa kendi kaydı
    "Curl-Up (Mekik) Testi": (_functools.partial(
        _tg_govde_fleksiyonu, "curlup", "Dizler yaklaşık 140°, eller uyluklarda", "Dakikada 20 vuruş · en çok 75 tekrar",
        "Parmaklar şeridi aşar"),
        "FitnessGram curl-up ile aynı: dizler yaklaşık 140°, parmaklar ölçüm şeridini aşar; en çok 75 tekrar."),
    "PACER Testi": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "FitnessGram PACER ile aynı: 20 m ardışık sinyaller arasında; 2 kez üst üste yetişemeyince test biter."),
    "Push-Up Testi": (_functools.partial(
        _tg_sinav, "Dakikada 20 vuruş, alt noktada dirsek 90°", "Form bozulana kadar"),
        "FitnessGram şınav ile aynı: alt noktada dirsek 90°, dakikada 20 vuruş, form bozulana kadar."),
    "Trunk Lift Testi": (_functools.partial(
        _tg_govde_kaldirma, "Yüzüstü, baş ve gövde yavaşça kalkar", "Yerden çeneye · 2 deneme"),
        "FitnessGram trunk lift ile aynı: yüzüstü, yerden çeneye ölçülür; kayıt en çok 30,5 cm."),
    "Back-Saver Sit and Reach": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ayak tabanı hizası 22,9 cm (9 inç), sıfır değil",
        22.9, tek_bacak=True),
        "FitnessGram ile aynı: cetvelin 22,9 cm (9 inç) işareti kutunun ayak kenarında; her bacak ayrı ölçülür."),
    "Shoulder Stretch Testi": (_functools.partial(
        _tg_omuz_esneme, "Bir el omuz üstünden, öbürü bel altından", "Her omuz ayrı · geçti / kalmadı"),
        "FitnessGram ile aynı: parmak uçları sırtta değiyorsa geçti; her omuz ayrı değerlendirilir."),
    # CAPL
    "CAPL Engel Parkuru (Motor Beceri)": (_functools.partial(
        _tg_capl_parkur, "Yedi beceri sırayla; süre vuruşla durur", "Beceri 0–14 + süre 1–14 = toplam 1–28"),
        "CAMSA: çift ayak sıçrama, yana kayma, top yakalama, hedefe atış, 5 m skipping, tek ayak sekme, topa vuruş; "
        "süre vuruşla durur; beceri 0–14 + süre 1–14 = 1–28."),
    "CAPL Duran Uzun Atlama (Fiziksel Uygunluk)": (_functools.partial(
        _tg_uzun_atlama, "Ayak uçları çizginin gerisinde, kol salınımı", "2 deneme, en iyisi"),
        "Ayak uçları çizginin gerisinde, ayaklar omuz genişliğinde; kollar salınarak çift ayakla atlanır. 2 deneme, en iyisi."),
    "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)": (_functools.partial(
        _tg_mekik, "Ardışık ses sinyalleri arasında 20 m", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "FitnessGram PACER ile aynı protokol: 20 m sinyaller arasında; sonuç CAPL-2 normlarıyla puana dönüştürülür."),
    # ALPHA
    "20m Mekik Koşusu (ALPHA)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "PACER/Léger ile aynı protokol"),
        "PACER/Léger ile aynı 20 m protokol; ALPHA'da VO2max tahmin formülü farklıdır (son hız ve yaş)."),
    "El Kavrama Kuvveti (ALPHA)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Var gücüyle sık (kg)", "Her el 2 deneme · iki elin ortalaması"),
        "Ayakta, dirsek tam ekstansiyonda; dinamometre yaş ve ele göre ayarlanır; her el 2 deneme, iki elin en iyilerinin ortalaması."),
    "Durarak Uzun Atlama (ALPHA)": (_functools.partial(
        _tg_uzun_atlama, "Ayak uçları çizginin gerisinde, çift ayak", "2 deneme, en iyisi"),
        "Ayaklar omuz genişliğinde, ayak uçları çizginin gerisinde; çift ayakla maksimum mesafeye atlanır. 2 deneme."),
    "4x10m Mekik Koşusu (ALPHA)": (_functools.partial(
        _tg_mekik_kosusu, "10 m", "10 m'yi 4 kez (2 gidiş-2 dönüş)", "Her dönüşte bir blok alınıp karşıya taşınır", 4,
        blok=True),
        "10 m aralıklı iki çizgi arasında 4 kez (2 gidiş-2 dönüş); her dönüşte yerden bir sünger blok alınıp taşınır."),
    "Back-Saver Sit and Reach (ALPHA)": (_functools.partial(
        _tg_otur_uzan, "Bir bacak düz, öbür diz bükülü ayak yerde", "Ölçek FitnessGram'dan: taban hizası 22,9 cm",
        22.9, tek_bacak=True),
        "Bir bacak düz, öbürü bükülü; ölçek FitnessGram ile aynı kabul edilir (taban hizası 22,9 cm) — ALPHA kılavuzundan doğrulanamadı."),
    "Plate Tapping (El Plakası Vurma)": (_functools.partial(
        _tg_plate_tapping, "Öbür el iki diskin arasındaki plakada", "25 tur (50 dokunuş) · 2 deneme, en az süre"),
        "Dominant olmayan el plakada; dominant el 60 cm arayla duran iki diske sırayla 25 tur (50 dokunuş); 2 deneme."),
    # PREFIT (3-6 yaş)
    "Durarak Uzun Atlama (PREFIT)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin arkasından çift ayak, kollar öne", "2 deneme, en iyisi", "Topuğa kadar"),
        "Başlangıç çizgisinin arkasından çift ayakla atlanır, kollar öne sallanabilir; topuğun değdiği noktaya kadar ölçülür."),
    "20m Mekik Koşusu (PREFIT)": (_functools.partial(
        _tg_mekik, "Ses sinyalleri arasında 20 m, yavaş başlangıç", "Sinyale 2 kez üst üste yetişemeyince biter"),
        "PREFIT'e özel yavaş başlangıç hızıyla 20 m sinyaller arasında koşulur; 2 kez üst üste yetişemeyince biter."),
    "El Kavrama Kuvveti (PREFIT)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Çocuk dinamometresi (kg)", "Her el 2 deneme · dominant elin en iyisi"),
        "Ayakta, dirsek tam ekstansiyonda; çocuk dinamometresi zorunlu; her el 2 deneme, dominant elin en iyi değeri."),
    "4x10m Mekik Koşusu (PREFIT)": (_functools.partial(
        _tg_mekik_kosusu, "10 m", "10 m'yi 4 kez (2 gidiş-2 dönüş)", "Her dönüşte bir blok alınıp taşınır · 2 deneme", 4,
        blok=True),
        "10 m'yi 4 kez (2 gidiş-2 dönüş) koşar; her dönüşte yerden bir blok alıp karşı çizgiye taşır. 2 deneme, en iyi süre."),
    "Flamingo Denge Testi (PREFIT)": (_functools.partial(
        _tg_flamingo, "Düz zeminde tek ayak, 30 sn", "Denge tahtası yok · her denge kaybında sayaç", tutar=False),
        "Düz zeminde (denge tahtası yok) dominant ayakta durulur, öbür ayak kalçaya yakın; 30 saniyede denge kaybı sayısı."),
    # CNPFM
    "50m Sprint": (_functools.partial(
        _tg_sprint, "50 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2),
        "Ayakta başlangıç pozisyonundan 50 m maksimal hızla koşulur; kronometre ya da fotosel; 2 deneme, en iyi süre."),
    "Mekik Koşusu (50m × 8)": (_functools.partial(
        _tg_mekik_kosusu, "25 m", "25 m'yi 8 kez (4 gidiş-4 dönüş)", "Her dönüşte çizgiyi geçip dön · toplam 200 m", 8),
        "25 m'yi 8 kez (4 gidiş-4 dönüş) maksimal hızla koşar; her dönüşte çizgiyi geçip döner; toplam 200 m."),
    "Durarak Uzun Atlama (CNPFM)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin gerisinde, kol salınımıyla çift ayak", "3 deneme, en iyisi"),
        "Çizginin gerisinde ayaklar omuz genişliğinde; kollar sallanarak çift ayakla atlanır. 3 deneme, en iyi mesafe."),
    "Otur-Uzan Testi (CNPFM)": (_functools.partial(
        _tg_otur_uzan, "İki bacak düz, ayak tabanları plakada", "Kılavuzdan doğrulanamadı · 2 deneme", 0),
        "Ayak tabanları plakaya dayalı; skor sınırları eksi değer içerdiğinden sıfır ayak tabanında kabul edilir (kılavuzdan doğrulanamadı)."),
    "1000m Koşusu - Erkek / 800m Koşusu - Kadın (CNPFM)": (_functools.partial(
        _tg_sprint, "1000 m (E) / 800 m (K)", "Tempolu koşu, yürüyüşe izin var", "400 m pist: 2,5 tur / 2 tur", 0,
        fotosel=False),
        "Erkekler 1000 m (2,5 tur), kadınlar 800 m (2 tur); tempolu koşu önerilir, yürümeye izin verilir ama skor düşer."),
    "Mekik (Sit-Up) 1 Dakika (CNPFM)": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında, ayaklar sabit", "1 dk · dirsekler dizlere, sırt yere"),
        "Dizler 90°, eller ense arkasında kenetli, ayaklar sabit; her tekrarda dirsekler dizlere, sırt yere değmeli; 1 dakika."),
    # KMS (3-6 yaş)
    "Yana Sıçrama (KMS)": (_functools.partial(
        _tg_yana_sicrama, "Çift ayakla sağa-sola, 15 sn", "Engel 50 cm × 2 cm", "2 deneme · her iki yöne geçiş bir tekrar"),
        "50 cm × 2 cm engelin üzerinden 15 saniye çift ayakla sağa-sola sıçranır; her iki yöne geçiş bir tekrar; 2 deneme."),
    "Balans (Denge) Testi (KMS)": (_functools.partial(
        _tg_geriye_denge, "kiris_ileri", "Kiriş üzerinde öne doğru yürü", "Kiriş 3 m × 6 cm · düşmeden adım sayısı, 2 deneme"),
        "3 m × 6 cm kiriş (ya da bant) üzerinde öne yürünür; düşmeden tamamlanan adım sayısı ya da mesafe; 2 deneme."),
    "Top Yakalama Testi (KMS)": (_functools.partial(
        _tg_top_yakalama, "Uygulayıcı atar, çocuk iki eliyle yakalar", "10 denemede başarılı yakalama sayısı"),
        "Uygulayıcı topu 1,5 m mesafeden atar; çocuk iki eliyle yakalamaya çalışır; 10 denemede başarılı yakalama sayısı."),
    "20m Sprint (KMS)": (_functools.partial(
        _tg_sprint, "20 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2, fotosel=False),
        "Ayakta başlangıç pozisyonundan işaretle 20 m maksimal hızla koşulur; kronometreyle; 2 deneme, en iyi süre."),
    # Latorre Román (3-6 yaş)
    "20m Sprint (Latorre)": (_functools.partial(
        _tg_sprint, "20 m", "Ayakta çıkış, maksimal hız", "2 deneme, en iyi süre", 2),
        "Ayakta başlangıç pozisyonundan işaretle 20 m maksimal hızla koşulur; kronometre ya da fotosel; 2 deneme."),
    "Durarak Uzun Atlama (Latorre)": (_functools.partial(
        _tg_uzun_atlama, "Çizginin gerisinde, kol salınımıyla çift ayak", "2 deneme, en iyisi"),
        "Çizginin gerisinde ayaklar omuz genişliğinde; kollar sallanarak çift ayakla atlanır. 2 deneme, en iyi mesafe."),
    "El Kavrama Kuvveti (Latorre)": (_functools.partial(
        _tg_kavrama, "Ayakta, dirsek tam ekstansiyonda", "Çocuk dinamometresi (kg)", "Her el 2 deneme · dominant elin en iyisi"),
        "Ayakta, dirsek tam ekstansiyonda, çocuk boyutunda dinamometre; her el 2 deneme, dominant elin en iyi değeri."),
    "Tek Ayak Denge Testi (Latorre)": (_functools.partial(
        _tg_flamingo, "Düz zeminde tek ayak, gözler açık, 30 sn", "Her denge kaybında sayaç · 2 deneme", tutar=False),
        "Düz zeminde dominant ayakta, gözler açık; 30 saniyede denge kaybı sayısı; 2 deneme."),
    "Top Fırlatma Testi (Latorre)": (_functools.partial(
        _tg_top_firlatma, "İki elle baş üzerinden, çizginin gerisinden", "2 deneme, en iyisi (cm)"),
        "Çizginin gerisinden (oturarak ya da ayakta) top iki elle başın üzerinden fırlatılır; 2 deneme, en iyi mesafe."),
    # Flaman Spor Pusulası
    "Top Sektirme — Alternatif El (BOT-2)": (_functools.partial(
        _tg_top_sektirme, "Bir elle sektir, öbür elle karşıla", "Art arda en çok 10 doğru sektirme · 2 deneme"),
        "Tenis topu bir elle sektirilir, öbür elle karşılanır, eller sırayla değişir; art arda en çok 10 doğru sektirme."),
    "Omuz Rotasyon Testi (Sopa/İp)": (_functools.partial(
        _tg_omuz_rotasyon, "Dirsekler bükülmeden baş üstünden sırta", "En dar el aralığı (cm) · düşük skor iyi"),
        "Sopa avuçlar aşağı geniş tutulur, dirsek bükülmeden baş üstünden sırta geçirilip geri getirilir; en dar el aralığı."),
    "Diz Üstü Şınav — 30 sn (BOT-2)": (_functools.partial(
        _tg_sinav, "Dizler matta, gövde baştan dizlere düz", "30 sn içinde doğru tekrar", diz=True),
        "Diz üstü: dizler matta, eller omuz genişliğinde, gövde baştan dizlere düz; 30 saniyede doğru tekrar sayısı."),
    "Oturma Yüksekliği": (_functools.partial(
        _tg_oturma, "Gövde dik, eller uyluklarda", "Oturak yüksekliği çıkarılır: net değer"),
        "Oturağa oturulur, sırt ve kalça ölçüm çubuğunda, baş Frankfurt düzleminde; okunan değerden oturak yüksekliği çıkarılır."),
    # Paket 25 — açıkta kalan testler: çizimleri zaten vardı, kayıtları eksikti (etiketler kendi protokollerinden)
    "20m Mekik Koşusu (Beep Test)": (_functools.partial(
        _tg_mekik, "Ardışık bip sesleri arasında 20 m", "Bipe 2 kez yetişemeyince biter"),
        "20 m çift yönlü koşu; hız bip sesleriyle artar; bipe 2 kez yetişemeyen sporcu testi bitirir."),
    "Cooper 12 Dakika Koşusu": (_functools.partial(
        _tg_sprint, "400 m pist", "12 dakikada olabildiğince uzun mesafe", "Yürüyüşe izin var · mesafe (m) ölçülür", 0,
        fotosel=False),
        "400 m pistte 12 dakika boyunca olabildiğince uzun mesafe; yürüyüşe izin var; kat edilen mesafe ölçülür."),
    "30-15 Aralıklı Fitness Testi (IFT)": (_tg_30_15,
        "40 m'de ses sinyaline göre 30 sn koşu, 15 sn yürüyüş; her aşamada hız 0,5 km/h artar."),
    "Nordic Hamstring Kuvvet Testi — Genel (NHT)": (_tg_nordic,
        "Diz üstü, bilekler sabit; gövde kontrollü öne indirilir; her bacak ayrı, 3 tekrar, en yüksek değer."),
    "Dikey Sıçrama (CMJ)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ",), "CMJ: eller kalçada, çök ve sıçra", "3 deneme, en iyi değer"),
        "Eller kalçada, ön-çömelmeyle maksimal dikey sıçrama; 3 deneme, en iyi değer."),
    "Dikey Sıçrama Tam Batarya (CMJ + SJ + DJ)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ", "SJ", "DJ"), "Soldan: CMJ, SJ (90° statik), DJ (30 cm)",
        "Eller kalçada; 3 deneme, en iyi yükseklik"),
        "CMJ (ön-çömelmeli), SJ (90° statik çömelmeden, 2 sn bekleme) ve DJ (30 cm'den); her biri 3 deneme."),
    "30m Sprint": (_functools.partial(
        _tg_sprint, "30 m", "Durarak başlangıç, 30 m maksimal hız", "3 deneme · arada 3-5 dk dinlenme", 3),
        "Durarak başlangıç, 30 m düz pist, maksimal hız; 3 deneme, aralarında 3-5 dk dinlenme."),
    # Paket 24 — kürek, kano/kayak, halter, squash, su topu (protokoller önce kaynakla karşılaştırıldı)
    "2000m Kürek Ergometre Testi": (_functools.partial(
        _tg_kurek_ergometre, "2000 m, en kısa sürede", "Süre, ortalama güç (watt) ve tempo (spm)"),
        "Kürek ergometresinde 2000 m en kısa sürede; süre, ortalama güç ve tempo monitörden kaydedilir."),
    "6 Dakika Kürek Ergometre Testi": (_functools.partial(
        _tg_kurek_ergometre, "6 dakikada en uzun mesafe", "Mesafe (m) ve ortalama güç (watt)"),
        "Kürek ergometresinde 6 dakikada en uzun mesafe; mesafe ve ortalama güç kaydedilir."),
    "200m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "200 m, maksimal", "Süre (sn), ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 200 m maksimal; süre, ortalama güç ve kürek frekansı kaydedilir."),
    "500m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "500 m, maksimal", "Süre (sn), ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 500 m maksimal; süre, ortalama güç ve kürek frekansı kaydedilir."),
    "1000m Ergometre Testi (Kano/Kayak)": (_functools.partial(
        _tg_kayak_ergometre, "1000 m, maksimal", "Süre, ortalama güç (watt), tempo (spm)"),
        "Kano/kayak ergometresinde 1000 m maksimal; süre, ortalama güç, kürek frekansı ve test sonu KAH kaydedilir."),
    "Koparma (Snatch) / Silkme (Clean & Jerk) 1RM": (_functools.partial(
        _tg_halter, "Koparma (sol) · silkme (sağ)", "1RM: en ağır başarılı kaldırış (kg)"),
        "Koparmada bar yerden tek hareketle baş üstüne, silkmede omuzdan baş üstüne; 1RM en ağır başarılı kaldırış."),
    "Squash Artımlı Mekik Testi (SIST)": (_functools.partial(
        _tg_parkur, "sist", "T'den köşeye, ayak hedefte, vuruş taklidi", "1 dk kademe: 14 hareketle başlar, dakikada +1",
        "T: başlangıç", (150, 50)),
        "T'den sinyalin gösterdiği köşeye (dört köşe), ayak hedefte, vuruş taklidi, T'ye dönüş; istemli tükenmeye kadar."),
    "Su Topu Spesifik Aerobik Test (WPOAT)": (_functools.partial(
        _tg_yuzme, "Serbest stil, 100 m tekrarlar", "Her 100 m süresi (sn) kaydedilir"),
        "Serbest stil 100 m tekrarlar; her 100 m süresi kaydedilir (düzen kaynakla doğrulanamadı, protokol notu)."),
    "Dikey Sıçrama - Suda (Su Topu)": (_functools.partial(
        _tg_suda_sicrama, "Eggbeater ile bekle, sonra sıçra", "3 deneme, en iyi değer"),
        "Derin suda eggbeater ile bekleyip maksimal sıçrama; yükseklik su yüzeyinden ölçülür; 3 deneme, en iyi değer."),
    # Paket 23 — tenis, yüzme, jimnastik, badminton (protokoller önce kaynakla karşılaştırıldı)
    "Spider Test (Tenis Çeviklik Testi)": (_functools.partial(
        _tg_parkur, "spider", "Arka çizginin gerisinden 5 topa, sağdan başla", "Her top tek tek kareye · 2 deneme, en iyisi",
        "Başlangıç karesi", (150, 50)),
        "Arka çizginin gerisindeki kareden 5 topu sağdan başlayarak tek tek toplayıp kareye bırakır; 2 deneme, en iyi süre."),
    "T-Testi (Çeviklik)": (_functools.partial(
        _tg_parkur, "t_testi", "A → B → C → D → B → A", "Yana kaymada ayak çaprazlanmaz · 3 deneme, en iyisi",
        "A: başlangıç"),
        "Standart T-testi: A'dan 9,14 m ileri B, 4,57 m sola C, 9,14 m sağa D, B'ye dön, A'ya geri koş; 3 deneme."),
    "CMJ (Badminton)": (_functools.partial(
        _tg_sicrama_turleri, ("CMJ",), "Eller kalçada, çök ve sıçra", "3 deneme, en iyi değer"),
        "Standart CMJ: eller kalçada, ani çökmeyle maksimal sıçrama; 3 deneme, en iyi değer."),
    "Tenis Servis Hızı ve İsabeti": (_functools.partial(
        _tg_tenis_servis, "Top havaya, raket yukarıdan", "Radar: hız (km/h) · 10 + 10 servis, isabet (%)"),
        "Arka çizginin gerisinden servis; radar hızı (km/h) ve isabet (%) kaydedilir; 10 birinci + 10 ikinci servis."),
    "Critical Swimming Speed (CSS) Testi": (_functools.partial(
        _tg_yuzme, "400 m ve 200 m, ayrı ayrı maksimal", "CSS = (400 − 200) / (T400 − T200)"),
        "Tam toparlanmayla iki maksimal yüzüş (400 m ve 200 m); CSS = (400 − 200) / (T400 − T200), m/sn."),
    "T-30 Yüzme Testi": (_functools.partial(
        _tg_yuzme, "30 dakika kesintisiz, düzenli tempo", "Toplam mesafe (m) · hız = mesafe / 1800 sn"),
        "30 dakika boyunca kesintisiz, düzenli tempoyla en uzun mesafe; T-30 hızı = mesafe / 1800 sn."),
    "Jimnastik Esneklik Profili": (_functools.partial(
        _tg_split, "Ön split, gövde dik", "Split: 0 = tam split · omuz, kalça, köprü ayrıca"),
        "Dört ölçüm: omuz fleksiyonu (°), kalça fleksiyonu (°), split (kasık–zemin, 0 = tam split), köprü (omuz yüksekliği)."),
    # Paket 19 — Squash Ghost Drill (çok dönüşlü parkur, numaralı)
    "Ghost Drill (Squash Çeviklik Testi)": (_functools.partial(
        _tg_parkur, "ghost", "T'den 6 köşeye sırayla, her köşeden T'ye", "30 sn × 6 set, aralarında 30 sn dinlenme",
        "T noktası", (150, 50), ([(30, True), (30, False)] * 5 + [(30, True)], 0.45)),
        "T noktasından 6 köşeye belirli sırayla; her noktada raketle duvara vurup T'ye dönülür; 30 sn × 6 set, aralarında 30 sn."),
    # Paket 16 — Wingate: dört test tek sahne, branş adı yalnız başlıkta
    **{t: (_functools.partial(_tg_wingate, b), _TG_WINGATE_KRITIK) for t, b in _TG_WINGATE.items()},
    # Paket 35 — Genel Kuvvet Rafı (Laboratuvar › Maksimal Kuvvet ve Kas Dayanıklılığı)
    "1RM Bench Press": (_functools.partial(
        _tg_bench_press, "Bar göğse iner, kollar tam açılır", "Kademeli ısınma · spotçu zorunlu"),
        "Sırtüstü, baş-sırt-kalça sehpada, ayaklar yerde, kapalı kavrayış; bar göğse iner, kollar tam açılır. "
        "Kademeli ısınma ve spotçu zorunlu."),
    "1RM Squat (Arka Çömelme)": (_functools.partial(
        _tg_arka_comelme, "Bar üst sırtta, diz açısı 90°'yi geçene kadar", "Kademeli ısınma · spotçu zorunlu"),
        "Bar üst sırtta; diz açısı 90°'yi geçene kadar çömelinir, dik duruşa dönülür. Güvenlik demiri en alt "
        "noktanın hemen altında; kademeli ısınma ve spotçu zorunlu."),
    "1RM Leg Press": (_functools.partial(
        _tg_leg_press, "Ayak yeri ve hareket açıklığı sabit", "Kademeli ısınma · spotçu zorunlu · diz kilitlenmez"),
        "Sırt ve kalça minderde, ayaklar platformda; platform belirlenen derinliğe iner, bacaklar açılır (diz "
        "kilitlenmez). Kademeli ısınma ve spotçu zorunlu."),
    "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)": (_functools.partial(
        _tg_barfiks, "Tam açık asılıdan çene barın üstüne", "Sallanma yok · form bozulana kadar"),
        "Avuçlar öne, kollar tam açık asılı; çene barın üstüne çekilir, kollar tam açılana dek inilir. Doğru "
        "tekrar sayısı; vücut ağırlığına bağımlıdır."),
    "Şınav (Push-Up) — Maksimum Tekrar (Genel)": (_functools.partial(
        _tg_sinav, "Alt noktada dirsek 90°, gövde düz", "Ara vermeden · form bozulana kadar"),
        "Eller omuz altında, gövde düz; alt noktada dirsek 90°, üstte kollar tam açık. Metronom yok; ara vermeden "
        "doğru tekrar sayısı."),
    "Mekik (Sit-Up) — 1 Dakika (Genel)": (_functools.partial(
        _tg_govde_fleksiyonu, "situp", "Dizler 90°, eller ense arkasında kenetli", "1 dakikada doğru tekrar sayısı"),
        "Sırtüstü, dizler 90° bükülü, eller ense arkasında kenetli, ayaklar sabit; 1 dakikada doğru tekrar sayısı."),
    # Paket 35c — Sargent (duvar + tebeşir)
    "Sargent Dikey Sıçrama Testi (Duvar)": (_functools.partial(
        _tg_sargent, "Sıçrama yüksekliği = üst iz − alt iz", "Üç deneme, en yüksek iz"),
        "Duvara yan, parmak uçları tebeşirli: ayakta erişim duvara işaretlenir; kollar ve hazırlık çömelmesi serbest "
        "sıçranır, zirvede duvara dokunulur. Sıçrama yüksekliği = üst iz − alt iz; üç denemenin en iyisi."),
}
# Hangi sahne hangi hareketi kullanıyor (sonraki testler için kitaplık haritası; denetim de bakar)
TG_HAREKET_KITAPLIGI = ("hk_duz_kos", "hk_donuslu_kos", "hk_dikey_sicrama", "hk_yana_sicrama", "hk_tek_ayak_sekme",
                        "hk_ikinci_figur", "hk_kavisli_yol", "hk_paten", "hk_tutus", "hk_pedal",
                        "hk_nordic", "hk_dinamometre", "hk_iz", "hk_sicrama_ani",
                        "hk_iki_uke_atis", "hk_uchikomi", "hk_vurus", "hk_asilma", "hk_yan_adim",
                        "hk_uzun_atlama", "hk_mekik", "hk_sinav", "hk_modifiye_barfiks", "hk_govde_kaldirma",
                        "hk_flamingo", "hk_masa_dokunma", "hk_omuz_esneme", "hk_omuz_rotasyon", "hk_top_sektirme",
                        "hk_top_yakala", "hk_asilma_bukumlu",
                        "hk_atma", "hk_kavrama", "hk_oturarak_uzanma", "hk_denge", "hk_antropometri",
                        "hk_takla", "hk_alttan_gec", "hk_engel_ustu", "hk_egil_al", "hk_koordinasyon_turu",
                        "hk_yana_kayma", "hk_skipping", "hk_topa_vurus", "hk_camsa_turu",
                        "hk_servis", "hk_serbest_stil", "hk_split",
                        "hk_kurek_ergometre", "hk_kayak_ergometre", "hk_koparma", "hk_silkme", "hk_eggbeater_sicrama",
                        "hk_bench_press", "hk_arka_comelme", "hk_leg_press", "hk_sargent")


# Bilerek GÖRSELSİZ testler (Paket 23): hareket değil (ölçüm, anket, laboratuvar cihazı) ya da tek harekete
# inmeyen çok bileşenli batarya ya da protokolü doğrulanamamış test. Eksik sayılmaz; sonraki paketlerde gündeme
# gelmez. Test adı → neden. Bir test hem burada hem TEST_GORSELLERI'nde olamaz (denetim).
TEST_GORSELSIZ = {
    **{ad: "hareket değil: vücut kompozisyonu ölçümü" for ad in (
        "Vücut Kompozisyonu - Deri Kıvrımı", "Vücut Kompozisyonu (PYFP)", "Bel Çevresi ve VKİ (Vücut Kompozisyonu)",
        "Vücut Kompozisyonu (PREFIT)", "Vücut Kompozisyonu (CNPFM)", "Vücut Kompozisyonu (Latorre)",
        "DEXA (Dual-Energy X-ray Absorptiometry)", "Biyoelektrik İmpedans Analizi (BIA)",
        "Hidrostatik Tartım (Su Altı Tartımı)")},
    "CAPL Günlük Adım Sayısı (Günlük Davranış)": "hareket değil: pedometre kaydı",
    "CAPL Motivasyon ve Güven Anketi": "hareket değil: anket",
    **{ad: "laboratuvar ölçümü: cihaz ve fizyolojik çıktı, hareketin kendisi değil" for ad in (
        "VO2max Direkt Ölçüm (Ergospirometri)", "Laktat Eşiği Testi", "Kardiyopulmoner Egzersiz Testi (CPET)",
        "İzokinetik Kuvvet Testi", "EMG Tabanlı Kas Aktivasyonu", "Force-Velocity Profili (F-V)",
        "Rate of Force Development (RFD) Ölçümü")},
    **{ad: "çok bileşenli batarya: tek harekete inmiyor" for ad in (
        "Judo Fiziksel Uygunluk Testi (JPFT)", "MMA Fiziksel Uygunluk Bataryası", "Atletik Güç Testi Bataryası",
        "Kuru Kara Testleri (Dry-Land) — Yüzme", "Jimnastik Fiziksel Uygunluk Testi (GFT)")},
    "Badminton Spesifik Çeviklik Testi (BAT)": "protokol kaynakla doğrulanamadı: güzergâh uydurulmaz (protokol notu)",
    "Rugby League Match Simulation Protocol (RLMSP)": "maç benzetimi: yürüme, koşu, sprint ve temas dizisi; tek harekete inmiyor",
    "NFL Combine Testleri": "çok bileşenli batarya: tek harekete inmiyor",
    "Rugby Union Fitness Test Bataryası": "çok bileşenli batarya: tek harekete inmiyor",
    "NHL/NHLTM Off-Ice Testleri": "çok bileşenli batarya: tek harekete inmiyor",
}


def tg_sahne(test_adi):
    """Sahneyi kurar (denetim ve görsel üretimi aynı yoldan geçer)."""
    return TEST_GORSELLERI[test_adi][0]()


def test_gorseli_html(test_adi, buyuk=False, kabuk=0, duragan=False):
    """
    Hareketli + durağan (reduced-motion) kopya. Görseli olmayan test için None.
    kabuk (0/1): görsel değiştiğinde (başka test ya da "tekrar oynat") sayfa kodu bunu çevirir; iç içe
    yapı bir kat değişir, tarayıcı SVG'yi yeniden kurar ve hareket baştan bir kez oynar (JavaScript yok).
    """
    if test_adi not in TEST_GORSELLERI:
        return None
    S = tg_sahne(test_adi)
    sinif = "tg-svg tg-buyuk" if buyuk else "tg-svg"
    ic = (f'<div class="tg-hareketli">{S.svg(True, test_adi, sinif)}</div>'
          f'<div class="tg-duragan">{S.svg(False, test_adi, sinif)}</div>')
    if duragan:                                     # Paket 38a: "Durdur" — yalnız son kare
        ic = f'<div>{S.svg(False, test_adi, sinif)}</div>'
    if kabuk % 2:
        ic = f'<div class="tg-ic">{ic}</div>'
    return f'<div class="tg-kap">{ic}</div>'


def tg_kabugu(anahtar):
    """Gösterilecek görselin anahtarı (test, tekrar sayacı) öncekinden farklıysa kabuğu çevirir."""
    if st.session_state.get("tg_son_anahtar") != anahtar:
        st.session_state["tg_son_anahtar"] = anahtar
        st.session_state["tg_kabuk"] = 1 - st.session_state.get("tg_kabuk", 0)
    return st.session_state.get("tg_kabuk", 0)


@st.dialog("Test görseli", width="large")
def test_gorseli_penceresi(test_adi, protokol):
    """Büyük görsel + en kritik ayrıntı + saha özeti adımları."""
    st.markdown(f"**{test_adi}**")
    st.markdown(test_gorseli_html(test_adi, buyuk=True), unsafe_allow_html=True)
    st.info(TEST_GORSELLERI[test_adi][1], icon=":material/priority_high:")
    st.markdown("**Adım adım**")
    st.markdown(protokol_ozet_cikar(protokol))


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
