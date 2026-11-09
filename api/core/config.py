"""
PerformTest — Yerli Sunucu (On-Premise) ve KVKK Uyumlu Uygulama Yapılandırması.
Tüm veriler kurum içi / yerli sunucuda barındırılan PostgreSQL/SQLite ve yerel disk üzerinde tutulur.
"""
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Ayarlar:
    PROJE_ADI: str = "Performetre — Performans Ölçme ve Değerlendirme & Yetenek Seçimi Platformu"
    MARKA_ADI: str = "Performetre"
    API_V1_ONEK: str = "/api/v1"
    ORTAM: str = os.getenv("PERFORMTEST_ORTAM", os.getenv("OLCUT_ORTAM", "development"))

    # Yerli Sunucu Veritabanı (PostgreSQL / SQLite WAL)
    DATABASE_URL: str = os.getenv(
        "PERFORMTEST_DATABASE_URL",
        os.getenv(
            "OLCUT_DATABASE_URL",
            "postgresql+psycopg://performtest_kullanici:performtest_gizli_parola@localhost:5432/performtest_db",
        ),
    )

    # JWT Kimlik Doğrulama (Web + Admin + Mobil)
    JWT_GIZLI_ANAHTAR: str = os.getenv(
        "PERFORMTEST_JWT_SECRET",
        os.getenv("OLCUT_JWT_SECRET", "performtest-yerli-sunucu-gizli-anahtar-256bit-2026"),
    )
    JWT_ALGORITMA: str = "HS256"
    ACCESS_TOKEN_SURESI_DAKIKA: int = 60
    REFRESH_TOKEN_SURESI_GUN: int = 14

    # Yerel Veri & Rapor Depolama (Excel uyumluluğu ve PDF/HTML rapor arşivi)
    YEREL_VERI_DIZINI: str = os.getenv("PERFORMTEST_VERI_DIZINI", "./yerel_veri")
    YEDEKLEME_DIZINI: str = os.getenv("PERFORMTEST_YEDEK_DIZINI", "./yerel_veri/yedekler")

    # KVKK ve Güvenlik İlkeleri
    KVKK_DENETIM_LOGU_ZORUNLU: bool = True
    CORS_IZINLI_KOKENLER: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",   # PerformTest Web Frontend & Admin Panel (Next.js)
            "http://localhost:8000",   # PerformTest All-in-One Sunucu
            "http://localhost:8081",   # PerformTest Mobil Uygulama (Expo / React Native)
            "http://localhost:8501",   # Streamlit Referans Arayüzü
        ]
    )


ayarlar = Ayarlar()
