"""
İlişkisel Veritabanı Şema Modelleri (PostgreSQL + KVKK Denetim Yapısı).

Mevcut Excel/JSON şemasını (`sporcular.xlsx`, `test_sonuclari.xlsx`,
`ilgi_anketi.xlsx`, `degisiklik_kaydi.xlsx`, `kulup.json`) çok-kullanıcılı
ve çok-kulüplü (multi-tenant) ilişkisel yapıya taşır.
"""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class KulupModeli:
    kod: str
    ad: str
    il: str
    ilce: str
    branslar: list[str]
    aktif: bool = True
    olusturma_zamani: datetime | None = None


@dataclass
class KullaniciModeli:
    id: str
    eposta: str
    ad_soyad: str
    rol: str
    kulup_kodu: str | None
    aktif: bool = True
    son_giris: datetime | None = None


@dataclass
class SporcuModeli:
    sporcu_id: str
    kulup_kodu: str
    ad: str
    soyad: str
    dogum_tarihi: date
    cinsiyet: str          # "Erkek" | "Kız"
    baba_boy_cm: float | None = None
    anne_boy_cm: float | None = None
    kvkk_onay_id: str | None = None


@dataclass
class TestSonucuModeli:
    id: str
    sporcu_id: str
    kulup_kodu: str
    oturum_id: str
    tarih: date
    yas: float
    cinsiyet: str
    nitelik: str
    test_adi: str
    deger: float
    birim: str
    seviye_kodu: str       # P1..P5
    yuzdelik: float | None
    kaydeden_kullanici_id: str | None = None


@dataclass
class DenetimKaydiModeli:
    """KVKK ve veri bütünlüğü için değiştirilemez (append-only) denetim izi."""
    id: str
    zaman: datetime
    kullanici_id: str
    kulup_kodu: str | None
    islem_turu: str        # "OLUSTUR" | "DUZELT" | "SIL" | "DISA_AKTAR" | "KVKK_ONAY"
    hedef_tablo: str
    hedef_id: str
    eski_deger_json: str | None
    yeni_deger_json: str | None
    neden: str | None
    ip_adresi: str | None

