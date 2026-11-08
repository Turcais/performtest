"""
Ölçüt ekran (UI) katmanı: her sayfa kendi modülündedir ve birbirini içe aktarmaz (test_45a).
"""
from olcut.sayfalar.ana_sayfa import _yonlendirme_gizle_degisti, yonlendirme_ekrani
from olcut.sayfalar.hakkinda import hakkinda_sayfasi
from olcut.sayfalar.karsilastirma import karsilastirma_sayfasi
from olcut.sayfalar.kayit_duzelt import kayit_duzelt_sayfasi
from olcut.sayfalar.kulupler import kulupler_sayfasi
from olcut.sayfalar.nitelik import nitelik_sayfasi
from olcut.sayfalar.raporlar import kaynakca_sayfasi, raporlar_sayfasi
from olcut.sayfalar.sonuclar import sonuc_kart_gorunumu, sonuclar_sporcu_sayfasi
from olcut.sayfalar.sonuclar_genel import sonuclari_goruntule_sayfasi
from olcut.sayfalar.sporcu_girisi import sporcu_girisi_sayfasi
from olcut.sayfalar.test_oturumu import (
    _qp_al,
    _qp_ayarla,
    taslak_deger_sayisi,
    taslak_oku,
    test_oturumu_sayfasi,
)
from olcut.sayfalar.test_uygula import test_uygula_sayfasi

__all__ = [
    "_yonlendirme_gizle_degisti",
    "yonlendirme_ekrani",
    "hakkinda_sayfasi",
    "karsilastirma_sayfasi",
    "kayit_duzelt_sayfasi",
    "kulupler_sayfasi",
    "nitelik_sayfasi",
    "kaynakca_sayfasi",
    "raporlar_sayfasi",
    "sonuc_kart_gorunumu",
    "sonuclar_sporcu_sayfasi",
    "sonuclari_goruntule_sayfasi",
    "sporcu_girisi_sayfasi",
    "_qp_al",
    "_qp_ayarla",
    "taslak_deger_sayisi",
    "taslak_oku",
    "test_oturumu_sayfasi",
    "test_uygula_sayfasi",
]
