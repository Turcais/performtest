"""
Ölçüt — Otomatik denetim giriş noktası (geriye dönük uyumluluk cephesi).

Testler modüler olarak `tests/` paketinde 7 alan dosyasına bölünmüştür:
- `tests/conftest.py` (ortak fikstürler ve yardımcılar)
- `tests/test_01_mimari_ve_sozdizimi.py`
- `tests/test_02_katalog_ve_protokol.py`
- `tests/test_03_norm_ve_hesaplama.py`
- `tests/test_04_analiz_brans_ve_oneri.py`
- `tests/test_05_gorseller_ve_tema.py`
- `tests/test_06_kayit_oturum_ve_duzeltme.py`
- `tests/test_07_raporlar_karsilastirma_ve_kulupler.py`

ÇALIŞTIRMA
----------
    python -m pytest                 # önerilen: tests/ altındaki 233 testi çalıştırır
    python -m pytest test_uygulama.py -q   # geriye dönük uyumlu: aynı 233 testi çalıştırır
"""
from tests.conftest import *  # noqa: F401,F403
from tests.test_01_mimari_ve_sozdizimi import *  # noqa: F401,F403
from tests.test_02_katalog_ve_protokol import *  # noqa: F401,F403
from tests.test_03_norm_ve_hesaplama import *  # noqa: F401,F403
from tests.test_04_analiz_brans_ve_oneri import *  # noqa: F401,F403
from tests.test_05_gorseller_ve_tema import *  # noqa: F401,F403
from tests.test_06_kayit_oturum_ve_duzeltme import *  # noqa: F401,F403
from tests.test_07_raporlar_karsilastirma_ve_kulupler import *  # noqa: F401,F403
