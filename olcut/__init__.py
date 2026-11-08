"""
Ölçüt uygulama paketi (Bölme Aşama 2).

Katman sırası (test_45a / _OLCUT_KATMAN): her modül yalnızca kendinden önceki (alt) katmanları içe aktarır;
döngüsel bağımlılık yoktur ve hiçbir alt modül uygulama.py'yi içe aktarmaz.
"""
from olcut.ortak import SURUM

__version__ = SURUM

KATMAN_SIRASI = (
    "ortak",
    "disa_aktarma",
    "tema",
    "esik",
    "katalog_islemleri",
    "gorseller.cizim",
    "gorseller.hareketler",
    "gorseller.sahneler",
    "norm",
    "analiz",
    "kayit",
    "duzeltme",
    "kulup",
    "raporlar",
    "oneri",
    "karsilastirma",
    "kulup_raporu",
    "bilesenler",
    "sayfalar",
)

__all__ = ["SURUM", "__version__", "KATMAN_SIRASI"]
