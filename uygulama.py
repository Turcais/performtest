"""
Ölçüt — Giriş noktası ve sayfa yönlendiricisi.

Sayfa yapılandırması, görsel sistem/tema kurulumu, çalışma alanı (kulüp) doğrulaması,
üst/yan menü gezinmesi ve sayfa yönlendirmesini yürütür.
İş mantığı ve hesaplamalar `olcut/` paketinde, sabit veriler `veri/` paketindedir.
"""
import html as _html
import os
import streamlit as st

from olcut.bilesenler import (
    alt_bilgi,
    bugun_karti,
    calisma_alani_dogrula,
    sonuc_bolumu_secici,
    ust_menu,
    yan_menu,
)
from olcut.norm import SPORCU_DOSYA
from olcut.ortak import ayar_oku, veri_yolu
from olcut.sayfalar import (
    _qp_al,
    _qp_ayarla,
    hakkinda_sayfasi,
    karsilastirma_sayfasi,
    kayit_duzelt_sayfasi,
    kaynakca_sayfasi,
    kulupler_sayfasi,
    nitelik_sayfasi,
    raporlar_sayfasi,
    sonuc_kart_gorunumu,
    sonuclar_sporcu_sayfasi,
    sonuclari_goruntule_sayfasi,
    sporcu_girisi_sayfasi,
    taslak_deger_sayisi,
    taslak_oku,
    test_oturumu_sayfasi,
    test_uygula_sayfasi,
    yonlendirme_ekrani,
)
from olcut.tema import (
    ACILIS_TANIM,
    UYGULAMA_ADI,
    kimlik_html,
    logo_svg,
    logo_veri_url,
    tasarimi_uygula,
)

st.set_page_config(page_title=UYGULAMA_ADI, page_icon=logo_veri_url(), layout="wide")
tasarimi_uygula()
st.sidebar.markdown(kimlik_html(), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# GEZİNME VE MENÜ YAPISI
# ════════════════════════════════════════════════════════════
SAYFALAR = ["Ana Sayfa", "Sporcu Girişi", "Niteliğe göre test bul", "Test Uygula", "Test Oturumu",
            "Sonuçları Görüntüle", "Raporlar", "Kaynakça", "Hakkında", "Kulüpler"]
UST_MENU = ["Ana Sayfa", "Raporlar", "Kaynakça", "Hakkında"]          # Paket 38k: üstte, site menüsü gibi
IKINCIL_SAYFALAR = ["Kulüpler"]                                        # Paket 38n: alt bilgiden (Hakkında'nın yanı)
YAN_MENU = [s_ for s_ in SAYFALAR if s_ not in UST_MENU + IKINCIL_SAYFALAR]   # sol menüde iş sayfaları

# Paket 38n: çalışma alanı (Genel ya da kulupler/<kod>/) — her veri okumasından ÖNCE doğrulanır
calisma_alani_dogrula()

# Paket 38b: değer girilirken sayfa yenilendiyse (adreste ?taslak=1 ve diskte taslak) kaldığı yere döner
if "sayfa" not in st.session_state and _qp_al("taslak") == "1" and taslak_oku():
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ots::otomatik"] = True
# "Açılışta bu ekranı gösterme" seçiliyse oturumun ilk açılışı doğrudan iş sayfasına (menü aynen kalır)
if "sayfa" not in st.session_state and ayar_oku().get("yonlendirme_gizle"):
    st.session_state["sayfa"] = "Test Uygula" if os.path.exists(veri_yolu(SPORCU_DOSYA)) else "Sporcu Girişi"

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

# ════════════════════════════════════════════════════════════
# SAYFA YÖNLENDİRME
# ════════════════════════════════════════════════════════════
if sayfa == "Niteliğe göre test bul":
    nitelik_sayfasi()

elif sayfa == "Ana Sayfa":
    st.markdown(f'<div class="sp-acilis">{logo_svg(72)}<div><h1>{_html.escape(UYGULAMA_ADI)}</h1>'
                f'<p>{_html.escape(ACILIS_TANIM)}</p></div></div>', unsafe_allow_html=True)
    yonlendirme_ekrani()

elif sayfa == "Sporcu Girişi":
    sporcu_girisi_sayfasi()

elif sayfa == "Test Uygula":
    test_uygula_sayfasi()

elif sayfa == "Test Oturumu":
    test_oturumu_sayfasi()

elif sayfa == "Sonuçları Görüntüle":
    _bolum = sonuc_bolumu_secici()
    if _bolum == "Karşılaştırma":
        karsilastirma_sayfasi()
    elif _bolum == "Kayıt düzelt":
        kayit_duzelt_sayfasi()
    elif sonuc_kart_gorunumu():
        sonuclar_sporcu_sayfasi()
    else:
        sonuclari_goruntule_sayfasi()

elif sayfa == "Raporlar":
    raporlar_sayfasi()

elif sayfa == "Kaynakça":
    kaynakca_sayfasi()

elif sayfa == "Hakkında":
    hakkinda_sayfasi()

elif sayfa == "Kulüpler":
    kulupler_sayfasi()

alt_bilgi(sayfa)                                 # Paket 38k: her sayfanın en altında (raporlara girmez)
