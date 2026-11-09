"""
Yerli Sunucu İlişkisel Veritabanı Motoru, Excel<->DB Çift Yönlü Köprüsü ve KVKK Denetim İzi.

Özellikler:
- Çok-kulüplü (multi-tenant) izolasyon (`kulup_kodu`)
- Değiştirilemez (append-only) KVKK denetim izi (`denetim_kayitlari`)
- `Olcut_Demo` ve mevcut `.xlsx` / `kulup.json` dosyalarından kayıpsız içe aktarım (`demo_verisini_yukle`)
- Mevcut `olcut/` analiz ve raporlama motoru için ilişkisel tablolardan anlık `pandas.DataFrame` üretimi
- Tek tıkla veritabanı + Excel anlık yedeği (`yedek_olustur`)
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
import os
import shutil
import sqlite3
import uuid
from typing import Any

import pandas as pd

from api.core.config import ayarlar
from api.core.security import KullaniciRolu, parola_hashle

_KOK_DIZIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_VARSAYILAN_DB_YOLU = os.path.join(_KOK_DIZIN, "yerel_veri", "olcut_yerli.db")

_SONUC_USTVERI_SUTUNLARI = [
    "Sporcu",
    "Kategori",
    "Batarya",
    "Branş",
    "Test",
    "Tarih",
    "Notlar",
    "Test Yaşı",
    "Oturum",
    "Yer",
    "Uygulayıcı",
]


def _simdi_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _temiz_deger(deger: Any) -> Any:
    if deger is None:
        return None
    if isinstance(deger, float) and (math.isnan(deger) or math.isinf(deger)):
        return None
    if pd.isna(deger):
        return None
    if hasattr(deger, "isoformat"):
        return deger.isoformat()
    return deger


class YerliVeritabani:
    """Yerli sunucu ilişkisel veritabanı yöneticisi."""

    def __init__(self, db_yolu: str | None = None):
        self.db_yolu = db_yolu or os.getenv("OLCUT_SQLITE_PATH", _VARSAYILAN_DB_YOLU)
        os.makedirs(os.path.dirname(os.path.abspath(self.db_yolu)), exist_ok=True)
        self._semayi_hazirla()

    @contextmanager
    def baglanti(self):
        con = sqlite3.connect(self.db_yolu)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def _semayi_hazirla(self) -> None:
        with self.baglanti() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS kulupler (
                    kod TEXT PRIMARY KEY,
                    ad TEXT NOT NULL,
                    sehir TEXT DEFAULT '',
                    branslar_json TEXT DEFAULT '[]',
                    iletisim TEXT DEFAULT '',
                    sozlesme_baslangic TEXT DEFAULT '',
                    sozlesme_bitis TEXT DEFAULT '',
                    karsilastirma_onayi INTEGER DEFAULT 1,
                    arsiv INTEGER DEFAULT 0,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS kullanicilar (
                    id TEXT PRIMARY KEY,
                    eposta TEXT UNIQUE NOT NULL,
                    parola_hash TEXT NOT NULL,
                    ad_soyad TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    kulup_kodu TEXT,
                    aktif INTEGER DEFAULT 1,
                    son_giris TEXT,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sporcular (
                    id TEXT PRIMARY KEY,
                    kulup_kodu TEXT NOT NULL,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    tam_ad TEXT NOT NULL,
                    yas REAL,
                    dogum_tarihi TEXT DEFAULT '',
                    cinsiyet TEXT NOT NULL,
                    spor_dali TEXT DEFAULT '',
                    derece TEXT DEFAULT '',
                    boy_cm REAL,
                    kilo_kg REAL,
                    haftalik_antrenman REAL,
                    antrenman_bilgisi_tarihi TEXT DEFAULT '',
                    grup_sinif TEXT DEFAULT '',
                    kvkk_onayli INTEGER DEFAULT 1,
                    kvkk_onay_tarihi TEXT,
                    anonimlestirildi INTEGER DEFAULT 0,
                    silindi_mi INTEGER DEFAULT 0,
                    olusturma_zamani TEXT NOT NULL,
                    UNIQUE(kulup_kodu, tam_ad)
                );

                CREATE TABLE IF NOT EXISTS test_sonuclari (
                    id TEXT PRIMARY KEY,
                    kulup_kodu TEXT NOT NULL,
                    sporcu_id TEXT,
                    sporcu_adi TEXT NOT NULL,
                    kategori TEXT DEFAULT '',
                    batarya TEXT DEFAULT '',
                    brans TEXT DEFAULT '',
                    test_adi TEXT NOT NULL,
                    tarih TEXT NOT NULL,
                    notlar TEXT DEFAULT '',
                    test_yasi REAL,
                    oturum TEXT DEFAULT '',
                    yer TEXT DEFAULT '',
                    uygulayici TEXT DEFAULT '',
                    olcumler_json TEXT NOT NULL,
                    silindi_mi INTEGER DEFAULT 0,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ilgi_anketleri (
                    id TEXT PRIMARY KEY,
                    kulup_kodu TEXT NOT NULL,
                    sporcu_adi TEXT NOT NULL,
                    tarih TEXT NOT NULL,
                    anket_turu TEXT DEFAULT '',
                    yanitlar_json TEXT NOT NULL,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS denetim_kayitlari (
                    id TEXT PRIMARY KEY,
                    zaman TEXT NOT NULL,
                    kullanici_eposta TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    kulup_kodu TEXT,
                    islem_turu TEXT NOT NULL,
                    hedef_tablo TEXT NOT NULL,
                    hedef_id TEXT NOT NULL,
                    eski_deger_json TEXT,
                    yeni_deger_json TEXT,
                    neden TEXT DEFAULT '',
                    ip_adresi TEXT DEFAULT '127.0.0.1'
                );

                CREATE TABLE IF NOT EXISTS mobil_senkron_kuyrugu (
                    id TEXT PRIMARY KEY,
                    cihaz_id TEXT NOT NULL,
                    kulup_kodu TEXT NOT NULL,
                    kullanici_eposta TEXT NOT NULL,
                    kayit_sayisi INTEGER NOT NULL,
                    veri_json TEXT NOT NULL,
                    islenme_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ozel_testler (
                    test_adi TEXT PRIMARY KEY,
                    kisa_ad TEXT DEFAULT '',
                    kategori TEXT NOT NULL,
                    batarya TEXT DEFAULT 'Özel Protokol',
                    brans TEXT DEFAULT 'Genel',
                    nitelik TEXT DEFAULT 'Genel',
                    bilesen TEXT DEFAULT 'Atletik Performans',
                    hareket_tipi TEXT DEFAULT 'otomatik',
                    alanlar_json TEXT DEFAULT '[["Değer", "sayısal"]]',
                    aciklama TEXT DEFAULT '',
                    protokol_adimlari TEXT DEFAULT '',
                    kritik_ayrinti TEXT DEFAULT '',
                    yon TEXT DEFAULT 'yuksek_iyi',
                    norm_medyan REAL,
                    norm_s REAL,
                    norm_l REAL DEFAULT 1.0,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS silinen_testler (
                    test_adi TEXT PRIMARY KEY,
                    silinme_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ozel_kaynakcalar (
                    anahtar TEXT PRIMARY KEY,
                    metin TEXT NOT NULL,
                    olusturma_zamani TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS silinen_kaynakcalar (
                    anahtar TEXT PRIMARY KEY,
                    silinme_zamani TEXT NOT NULL
                );
                """
            )
        self._varsayilan_kullanicilari_hazirla()

    def _varsayilan_kullanicilari_hazirla(self) -> None:
        varsayilan_kulupler = [
            ("merkez", "Performetre Merkez Performans Laboratuvarı", "Ankara", ["Genel Atletik Performans"]),
            ("demo-kulup-a", "Demo Kulüp A", "Ankara", ["Çocuk sporları"]),
            ("demo-kulup-b", "Demo Kulüp B", "İstanbul", ["Çocuk sporları", "Atletizm"]),
        ]
        varsayilan_kullanicilar = [
            (
                "usr-pm-super-admin",
                "admin@performetre.yerli",
                "PerformAdmin2026!",
                "Performetre Sistem Yöneticisi (Süper Admin)",
                KullaniciRolu.SUPER_ADMIN.value,
                "merkez",
            ),
            (
                "usr-pm-kulup-a",
                "kulup-a@performetre.yerli",
                "Kulup123!",
                "Demo Kulüp A Yöneticisi",
                KullaniciRolu.KULUP_YONETICISI.value,
                "demo-kulup-a",
            ),
            (
                "usr-pm-antrenor",
                "antrenor@performetre.yerli",
                "Koc123!",
                "Baş Antrenör & Ölçüm Uzmanı",
                KullaniciRolu.ANTRENOR.value,
                "merkez",
            ),
            (
                "usr-pm-veli",
                "veli@performetre.yerli",
                "Veli123!",
                "Sporcu Velisi",
                KullaniciRolu.SPORCU_VELI.value,
                "merkez",
            ),
            (
                "usr-pt-super-admin",
                "admin@performtest.yerli",
                "PerformAdmin2026!",
                "Performetre Sistem Yöneticisi (Süper Admin)",
                KullaniciRolu.SUPER_ADMIN.value,
                "merkez",
            ),
            (
                "usr-pt-kulup-a",
                "kulup-a@performtest.yerli",
                "Kulup123!",
                "Demo Kulüp A Yöneticisi",
                KullaniciRolu.KULUP_YONETICISI.value,
                "demo-kulup-a",
            ),
            (
                "usr-pt-antrenor",
                "antrenor@performtest.yerli",
                "Koc123!",
                "Baş Antrenör & Ölçüm Uzmanı",
                KullaniciRolu.ANTRENOR.value,
                "merkez",
            ),
            (
                "usr-pt-veli",
                "veli@performtest.yerli",
                "Veli123!",
                "Sporcu Velisi",
                KullaniciRolu.SPORCU_VELI.value,
                "merkez",
            ),
            # Geriye dönük test uyumluluğu hesapları
            (
                "usr-super-admin",
                "admin@olcut.yerli",
                "OlcutAdmin2026!",
                "Sistem Yöneticisi (Süper Admin)",
                KullaniciRolu.SUPER_ADMIN.value,
                "merkez",
            ),
            (
                "usr-kulup-a",
                "kulup-a@olcut.yerli",
                "KulupA2026!",
                "Demo Kulüp A Yöneticisi",
                KullaniciRolu.KULUP_YONETICISI.value,
                "demo-kulup-a",
            ),
            (
                "usr-antrenor",
                "antrenor@olcut.yerli",
                "Antrenor2026!",
                "Baş Antrenör & Ölçüm Uzmanı",
                KullaniciRolu.ANTRENOR.value,
                "merkez",
            ),
            (
                "usr-veli",
                "veli@olcut.yerli",
                "Veli2026!",
                "Örnek Sporcu Velisi",
                KullaniciRolu.SPORCU_VELI.value,
                "merkez",
            ),
        ]
        simdi = _simdi_iso()
        with self.baglanti() as con:
            for kod, ad, sehir, branslar in varsayilan_kulupler:
                con.execute(
                    """
                    INSERT OR IGNORE INTO kulupler (kod, ad, sehir, branslar_json, olusturma_zamani)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (kod, ad, sehir, json.dumps(branslar, ensure_ascii=False), simdi),
                )
            for uid, eposta, parola, ad_soyad, rol, kulup in varsayilan_kullanicilar:
                mevcut = con.execute("SELECT id FROM kullanicilar WHERE eposta = ?", (eposta,)).fetchone()
                if not mevcut:
                    con.execute(
                        """
                        INSERT INTO kullanicilar (id, eposta, parola_hash, ad_soyad, rol, kulup_kodu, aktif, olusturma_zamani)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                        """,
                        (uid, eposta, parola_hashle(parola), ad_soyad, rol, kulup, simdi),
                    )

    # ════════════════════════════════════════════════════════════════
    # KVKK Değiştirilemez Denetim İzi (Immutable Audit Log)
    # ════════════════════════════════════════════════════════════════
    def denetim_kaydi_ekle(
        self,
        kullanici_eposta: str,
        rol: str,
        islem_turu: str,
        hedef_tablo: str,
        hedef_id: str,
        kulup_kodu: str | None = None,
        eski_deger: Any = None,
        yeni_deger: Any = None,
        neden: str = "",
        ip_adresi: str = "127.0.0.1",
    ) -> str:
        kayit_id = f"aud-{uuid.uuid4().hex[:12]}"
        with self.baglanti() as con:
            con.execute(
                """
                INSERT INTO denetim_kayitlari
                (id, zaman, kullanici_eposta, rol, kulup_kodu, islem_turu, hedef_tablo, hedef_id,
                 eski_deger_json, yeni_deger_json, neden, ip_adresi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    kayit_id,
                    _simdi_iso(),
                    kullanici_eposta,
                    rol,
                    kulup_kodu,
                    islem_turu,
                    hedef_tablo,
                    hedef_id,
                    json.dumps(eski_deger, ensure_ascii=False) if eski_deger is not None else None,
                    json.dumps(yeni_deger, ensure_ascii=False) if yeni_deger is not None else None,
                    neden,
                    ip_adresi,
                ),
            )
        return kayit_id

    # ════════════════════════════════════════════════════════════════
    # Olcut_Demo ve Excel'den İlişkisel Veritabanına Taşıma (Seed)
    # ════════════════════════════════════════════════════════════════
    def klasorden_kulup_yukle(self, klasor_yolu: str, kulup_kodu: str, kulup_varsayilan_ad: str) -> dict[str, int]:
        """Bir klasördeki (`sporcular.xlsx`, `test_sonuclari.xlsx`, `ilgi_anketi.xlsx`, `kulup.json`) verileri DB'ye aktarır."""
        simdi = _simdi_iso()
        sayac = {"sporcular": 0, "test_sonuclari": 0, "ilgi_anketleri": 0}
        kulup_json_yolu = os.path.join(klasor_yolu, "kulup.json")
        if os.path.isfile(kulup_json_yolu):
            with open(kulup_json_yolu, encoding="utf-8") as f:
                kj = json.load(f)
            with self.baglanti() as con:
                con.execute(
                    """
                    INSERT OR REPLACE INTO kulupler
                    (kod, ad, sehir, branslar_json, iletisim, sozlesme_baslangic, sozlesme_bitis,
                     karsilastirma_onayi, arsiv, olusturma_zamani)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        kulup_kodu,
                        kj.get("ad", kulup_varsayilan_ad),
                        kj.get("sehir", ""),
                        json.dumps(kj.get("branslar", []), ensure_ascii=False),
                        kj.get("iletisim", ""),
                        kj.get("sozlesme_baslangic", ""),
                        kj.get("sozlesme_bitis", ""),
                        1 if kj.get("karsilastirma_onayi", True) else 0,
                        1 if kj.get("arsiv", False) else 0,
                        simdi,
                    ),
                )

        # 1. Sporcular
        sp_yolu = os.path.join(klasor_yolu, "sporcular.xlsx")
        sporcu_id_haritasi: dict[str, str] = {}
        if os.path.isfile(sp_yolu):
            df_sp = pd.read_excel(sp_yolu)
            with self.baglanti() as con:
                for _, s in df_sp.iterrows():
                    ad = str(_temiz_deger(s.get("Ad")) or "").strip()
                    soyad = str(_temiz_deger(s.get("Soyad")) or "").strip()
                    if not ad and not soyad:
                        continue
                    tam_ad = f"{ad} {soyad}".strip()
                    mevcut = con.execute(
                        "SELECT id FROM sporcular WHERE kulup_kodu = ? AND tam_ad = ?",
                        (kulup_kodu, tam_ad),
                    ).fetchone()
                    sp_id = mevcut["id"] if mevcut else f"sp-{uuid.uuid4().hex[:10]}"
                    sporcu_id_haritasi[tam_ad] = sp_id
                    con.execute(
                        """
                        INSERT OR REPLACE INTO sporcular
                        (id, kulup_kodu, ad, soyad, tam_ad, yas, dogum_tarihi, cinsiyet, spor_dali,
                         derece, boy_cm, kilo_kg, haftalik_antrenman, antrenman_bilgisi_tarihi,
                         grup_sinif, kvkk_onayli, kvkk_onay_tarihi, anonimlestirildi, silindi_mi, olusturma_zamani)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 0, 0, ?)
                        """,
                        (
                            sp_id,
                            kulup_kodu,
                            ad,
                            soyad,
                            tam_ad,
                            _temiz_deger(s.get("Yaş")),
                            str(_temiz_deger(s.get("Doğum Tarihi")) or ""),
                            str(_temiz_deger(s.get("Cinsiyet")) or "Erkek"),
                            str(_temiz_deger(s.get("Spor Dalı")) or ""),
                            str(_temiz_deger(s.get("Derece")) or ""),
                            _temiz_deger(s.get("Boy (cm)")),
                            _temiz_deger(s.get("Kilo (kg)")),
                            _temiz_deger(s.get("Haftalık Antrenman")),
                            str(_temiz_deger(s.get("Antrenman Bilgisi Tarihi")) or ""),
                            str(_temiz_deger(s.get("Grup/Sınıf")) or ""),
                            simdi,
                            simdi,
                        ),
                    )
                    sayac["sporcular"] += 1

        # 2. Test Sonuçları
        ts_yolu = os.path.join(klasor_yolu, "test_sonuclari.xlsx")
        if os.path.isfile(ts_yolu):
            df_ts = pd.read_excel(ts_yolu)
            with self.baglanti() as con:
                con.execute("DELETE FROM test_sonuclari WHERE kulup_kodu = ?", (kulup_kodu,))
                for _, r in df_ts.iterrows():
                    sporcu_adi = str(_temiz_deger(r.get("Sporcu")) or "").strip()
                    test_adi = str(_temiz_deger(r.get("Test")) or "").strip()
                    if not sporcu_adi or not test_adi:
                        continue
                    olcumler = {}
                    for sutun in df_ts.columns:
                        if sutun not in _SONUC_USTVERI_SUTUNLARI:
                            val = _temiz_deger(r.get(sutun))
                            if val is not None:
                                olcumler[sutun] = val
                    con.execute(
                        """
                        INSERT INTO test_sonuclari
                        (id, kulup_kodu, sporcu_id, sporcu_adi, kategori, batarya, brans, test_adi,
                         tarih, notlar, test_yasi, oturum, yer, uygulayici, olcumler_json, silindi_mi, olusturma_zamani)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                        """,
                        (
                            f"ts-{uuid.uuid4().hex[:12]}",
                            kulup_kodu,
                            sporcu_id_haritasi.get(sporcu_adi),
                            sporcu_adi,
                            str(_temiz_deger(r.get("Kategori")) or ""),
                            str(_temiz_deger(r.get("Batarya")) or ""),
                            str(_temiz_deger(r.get("Branş")) or ""),
                            test_adi,
                            str(_temiz_deger(r.get("Tarih")) or ""),
                            str(_temiz_deger(r.get("Notlar")) or ""),
                            _temiz_deger(r.get("Test Yaşı")),
                            str(_temiz_deger(r.get("Oturum")) or ""),
                            str(_temiz_deger(r.get("Yer")) or ""),
                            str(_temiz_deger(r.get("Uygulayıcı")) or ""),
                            json.dumps(olcumler, ensure_ascii=False),
                            simdi,
                        ),
                    )
                    sayac["test_sonuclari"] += 1

        # 3. İlgi Anketi
        ia_yolu = os.path.join(klasor_yolu, "ilgi_anketi.xlsx")
        if os.path.isfile(ia_yolu):
            df_ia = pd.read_excel(ia_yolu)
            with self.baglanti() as con:
                con.execute("DELETE FROM ilgi_anketleri WHERE kulup_kodu = ?", (kulup_kodu,))
                for _, r in df_ia.iterrows():
                    sporcu_adi = str(_temiz_deger(r.get("Sporcu")) or "").strip()
                    if not sporcu_adi:
                        continue
                    yanitlar = {}
                    for sutun in df_ia.columns:
                        if sutun not in ("Sporcu", "Tarih", "Anket"):
                            val = _temiz_deger(r.get(sutun))
                            if val is not None:
                                yanitlar[sutun] = val
                    con.execute(
                        """
                        INSERT INTO ilgi_anketleri
                        (id, kulup_kodu, sporcu_adi, tarih, anket_turu, yanitlar_json, olusturma_zamani)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            f"ia-{uuid.uuid4().hex[:12]}",
                            kulup_kodu,
                            sporcu_adi,
                            str(_temiz_deger(r.get("Tarih")) or ""),
                            str(_temiz_deger(r.get("Anket")) or ""),
                            json.dumps(yanitlar, ensure_ascii=False),
                            simdi,
                        ),
                    )
                    sayac["ilgi_anketleri"] += 1

        return sayac

    def demo_verisini_yukle(self, demo_kok_yolu: str | None = None) -> dict[str, Any]:
        """`Olcut_Demo` klasöründeki merkez ve alt kulüp verilerini veritabanına aktarır."""
        aday_yollar = [
            demo_kok_yolu,
            os.path.join(_KOK_DIZIN, "tohum_veri"),
            os.path.join(os.path.dirname(_KOK_DIZIN), "Olcut_Demo"),
            os.path.join(_KOK_DIZIN, "Olcut_Demo"),
        ]
        secilen_yol = next((y for y in aday_yollar if y and os.path.isdir(y)), None)
        if not secilen_yol:
            return {"yuklendi": False, "neden": "Olcut_Demo veya tohum_veri klasörü bulunamadı."}

        ozet: dict[str, Any] = {"yuklendi": True, "kulupler": {}}
        ozet["kulupler"]["merkez"] = self.klasorden_kulup_yukle(
            secilen_yol, "merkez", "Ölçüt Merkez Performans Laboratuvarı"
        )
        kulupler_dizin = os.path.join(secilen_yol, "kulupler")
        if os.path.isdir(kulupler_dizin):
            for alt in sorted(os.listdir(kulupler_dizin)):
                alt_yol = os.path.join(kulupler_dizin, alt)
                if os.path.isdir(alt_yol):
                    ozet["kulupler"][alt] = self.klasorden_kulup_yukle(alt_yol, alt, alt)
        return ozet

    # ════════════════════════════════════════════════════════════════
    # Mevcut `olcut/` Motoru İçin İlişkisel Veriden DataFrame Üretimi
    # ════════════════════════════════════════════════════════════════
    def kulup_dataframeleri(self, kulup_kodu: str = "merkez") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Veritabanındaki ilişkisel kayıtları `olcut/` motorunun beklediği
        (`sporcular_df`, `sonuclar_df`, `ilgi_df`) DataFrame üçlüsüne dönüştürür.
        """
        with self.baglanti() as con:
            sp_rows = con.execute(
                "SELECT * FROM sporcular WHERE kulup_kodu = ? AND silindi_mi = 0 ORDER BY ad, soyad",
                (kulup_kodu,),
            ).fetchall()
            ts_rows = con.execute(
                "SELECT * FROM test_sonuclari WHERE kulup_kodu = ? AND silindi_mi = 0 ORDER BY tarih, id",
                (kulup_kodu,),
            ).fetchall()
            ia_rows = con.execute(
                "SELECT * FROM ilgi_anketleri WHERE kulup_kodu = ? ORDER BY tarih, id",
                (kulup_kodu,),
            ).fetchall()

        sp_list = [
            {
                "Ad": r["ad"],
                "Soyad": r["soyad"],
                "Yaş": r["yas"],
                "Cinsiyet": r["cinsiyet"],
                "Spor Dalı": r["spor_dali"],
                "Derece": r["derece"],
                "Boy (cm)": r["boy_cm"],
                "Kilo (kg)": r["kilo_kg"],
                "Haftalık Antrenman": r["haftalik_antrenman"],
                "Antrenman Bilgisi Tarihi": r["antrenman_bilgisi_tarihi"],
                "Doğum Tarihi": r["dogum_tarihi"],
                "Grup/Sınıf": r["grup_sinif"],
            }
            for r in sp_rows
        ]
        df_sp = pd.DataFrame(
            sp_list,
            columns=[
                "Ad",
                "Soyad",
                "Yaş",
                "Cinsiyet",
                "Spor Dalı",
                "Derece",
                "Boy (cm)",
                "Kilo (kg)",
                "Haftalık Antrenman",
                "Antrenman Bilgisi Tarihi",
                "Doğum Tarihi",
                "Grup/Sınıf",
            ],
        )

        ts_list = []
        for r in ts_rows:
            satir = {
                "Sporcu": r["sporcu_adi"],
                "Kategori": r["kategori"],
                "Batarya": r["batarya"],
                "Branş": r["brans"],
                "Test": r["test_adi"],
                "Tarih": r["tarih"],
                "Notlar": r["notlar"],
                "Test Yaşı": r["test_yasi"],
                "Oturum": r["oturum"],
                "Yer": r["yer"],
                "Uygulayıcı": r["uygulayici"],
            }
            olcumler = json.loads(r["olcumler_json"] or "{}")
            satir.update(olcumler)
            ts_list.append(satir)
        df_ts = pd.DataFrame(ts_list) if ts_list else pd.DataFrame(columns=_SONUC_USTVERI_SUTUNLARI)

        ia_list = []
        for r in ia_rows:
            satir = {
                "Sporcu": r["sporcu_adi"],
                "Tarih": r["tarih"],
                "Anket": r["anket_turu"],
            }
            satir.update(json.loads(r["yanitlar_json"] or "{}"))
            ia_list.append(satir)
        df_ia = pd.DataFrame(ia_list) if ia_list else pd.DataFrame(columns=["Sporcu", "Tarih", "Anket"])

        return df_sp, df_ts, df_ia

    def yedek_olustur(self, kullanici_eposta: str = "admin@olcut.yerli", rol: str = "super_admin") -> dict[str, Any]:
        """Yerli sunucu veritabanının zaman damgalı anlık kopyasını oluşturur ve denetim izine yazar."""
        yedek_dizin = os.path.join(os.path.dirname(os.path.abspath(self.db_yolu)), "yedekler")
        os.makedirs(yedek_dizin, exist_ok=True)
        damga = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        hedef_yol = os.path.join(yedek_dizin, f"olcut_yerli_yedek_{damga}.db")
        shutil.copy2(self.db_yolu, hedef_yol)
        boyut = os.path.getsize(hedef_yol)
        self.denetim_kaydi_ekle(
            kullanici_eposta=kullanici_eposta,
            rol=rol,
            islem_turu="SISTEM_YEDEKLEME",
            hedef_tablo="veritabani",
            hedef_id=os.path.basename(hedef_yol),
            yeni_deger={"dosya": os.path.basename(hedef_yol), "boyut_bayt": boyut},
            neden="Yerli sunucu anlık veritabanı yedeği",
        )
        return {
            "dosya": os.path.basename(hedef_yol),
            "tam_yol": hedef_yol,
            "boyut_bayt": boyut,
            "zaman": _simdi_iso(),
        }


veritabani = YerliVeritabani()
