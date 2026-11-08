"""
Yönetim (Admin) Paneli Uç Noktaları (`/api/v1/admin`).

Modüller:
1. Sistem ve Kulüp İstatistik Özeti (`/ozet`)
2. Kulüp (Tenant) Yönetimi (`/kulupler`)
3. Kullanıcı ve RBAC Rol Yönetimi (`/kullanicilar`)
4. KVKK Değiştirilemez Denetim İzi (`/denetim-kayitlari`)
5. KVKK Unutulma Hakkı & Anonimleştirme (`/kvkk/anonimlestir`)
6. Yerli Sunucu Anlık Veritabanı Yedekleme (`/yedekle`) ve Demo Veri Yükleme (`/demo-yukle`)
"""
from datetime import datetime, timezone
import json
import os
import uuid
from flask import Blueprint, request

from api.core.http_yardimci import json_yanit, yetki_gerekli
from api.core.security import KullaniciRolu, parola_hashle
from api.db import veritabani

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.get("/ozet")
@yetki_gerekli("denetim:kulup_ici_goruntule")
def admin_ozet():
    with veritabani.baglanti() as con:
        kulup_sayisi = con.execute("SELECT COUNT(*) AS n FROM kulupler WHERE arsiv = 0").fetchone()["n"]
        kullanici_sayisi = con.execute("SELECT COUNT(*) AS n FROM kullanicilar WHERE aktif = 1").fetchone()["n"]
        sporcu_sayisi = con.execute("SELECT COUNT(*) AS n FROM sporcular WHERE silindi_mi = 0").fetchone()["n"]
        olcum_sayisi = con.execute("SELECT COUNT(*) AS n FROM test_sonuclari WHERE silindi_mi = 0").fetchone()["n"]
        anket_sayisi = con.execute("SELECT COUNT(*) AS n FROM ilgi_anketleri").fetchone()["n"]
        denetim_sayisi = con.execute("SELECT COUNT(*) AS n FROM denetim_kayitlari").fetchone()["n"]
        kulup_dagilimi = con.execute(
            """
            SELECT k.kod, k.ad, k.sehir,
                   (SELECT COUNT(*) FROM sporcular s WHERE s.kulup_kodu = k.kod AND s.silindi_mi = 0) AS sporcu_sayisi,
                   (SELECT COUNT(*) FROM test_sonuclari t WHERE t.kulup_kodu = k.kod AND t.silindi_mi = 0) AS olcum_sayisi
            FROM kulupler k
            ORDER BY k.kod
            """
        ).fetchall()

    db_boyut = os.path.getsize(veritabani.db_yolu) if os.path.exists(veritabani.db_yolu) else 0
    return json_yanit(
        {
            "metrikler": {
                "aktif_kulup_sayisi": kulup_sayisi,
                "aktif_kullanici_sayisi": kullanici_sayisi,
                "toplam_sporcu": sporcu_sayisi,
                "toplam_olcum_satiri": olcum_sayisi,
                "toplam_ilgi_anketi": anket_sayisi,
                "toplam_denetim_kaydi": denetim_sayisi,
            },
            "yerli_sunucu": {
                "veritabani_motoru": "SQLite WAL / PostgreSQL Uyumlu Yerli Katman",
                "veritabani_dosyasi": os.path.basename(veritabani.db_yolu),
                "boyut_bayt": db_boyut,
                "kvkk_uyum_modu": "Aktif (Yurt İçi Barındırma + Değiştirilemez Audit Log)",
            },
            "kulup_dagilimi": [dict(r) for r in kulup_dagilimi],
        }
    )


@admin_bp.get("/kulupler")
@yetki_gerekli("kulup:duzenle")
def kulupleri_listele():
    with veritabani.baglanti() as con:
        rows = con.execute("SELECT * FROM kulupler ORDER BY kod").fetchall()
    kulupler = []
    for r in rows:
        d = dict(r)
        d["branslar"] = json.loads(d.pop("branslar_json", "[]") or "[]")
        kulupler.append(d)
    return json_yanit({"toplam": len(kulupler), "kulupler": kulupler})


@admin_bp.post("/kulupler")
@yetki_gerekli("kulup:olustur")
def kulup_olustur():
    veri = request.get_json(silent=True) or {}
    kullanici = request.kullanici  # type: ignore[attr-defined]
    kod = str(veri.get("kod") or "").strip().lower()
    ad = str(veri.get("ad") or "").strip()
    sehir = str(veri.get("sehir") or "").strip()
    branslar = veri.get("branslar") if isinstance(veri.get("branslar"), list) else ["Genel"]
    if not kod or not ad:
        return json_yanit({"hata": "Kulüp kodu ve adı zorunludur."}, 400)

    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with veritabani.baglanti() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO kulupler (kod, ad, sehir, branslar_json, iletisim, olusturma_zamani)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (kod, ad, sehir, json.dumps(branslar, ensure_ascii=False), str(veri.get("iletisim") or ""), simdi),
        )
    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "admin"),
        rol=kullanici.get("role", "super_admin"),
        kulup_kodu=kod,
        islem_turu="KULUP_OLUSTUR",
        hedef_tablo="kulupler",
        hedef_id=kod,
        yeni_deger={"kod": kod, "ad": ad, "sehir": sehir, "branslar": branslar},
        neden="Admin panelinden kulüp tanımlama",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit({"kod": kod, "ad": ad, "sehir": sehir, "branslar": branslar}, 201)


@admin_bp.get("/kullanicilar")
@yetki_gerekli("kullanici:kulup_ici_yonet")
def kullanicilari_listele():
    with veritabani.baglanti() as con:
        rows = con.execute(
            "SELECT id, eposta, ad_soyad, rol, kulup_kodu, aktif, son_giris, olusturma_zamani FROM kullanicilar ORDER BY olusturma_zamani"
        ).fetchall()
    return json_yanit({"toplam": len(rows), "kullanicilar": [dict(r) for r in rows]})


@admin_bp.post("/kullanicilar")
@yetki_gerekli("kullanici:yonet")
def kullanici_olustur():
    veri = request.get_json(silent=True) or {}
    istek_yapan = request.kullanici  # type: ignore[attr-defined]
    eposta = str(veri.get("eposta") or "").strip().lower()
    ad_soyad = str(veri.get("ad_soyad") or "").strip()
    parola = str(veri.get("parola") or "").strip()
    rol = str(veri.get("rol") or KullaniciRolu.ANTRENOR.value).strip()
    kulup_kodu = str(veri.get("kulup_kodu") or "merkez").strip()

    if not eposta or not ad_soyad or len(parola) < 6:
        return json_yanit({"hata": "E-posta, ad_soyad ve en az 6 karakterli parola zorunludur."}, 400)
    if rol not in {r.value for r in KullaniciRolu}:
        return json_yanit({"hata": f"Geçersiz rol: {rol}"}, 400)

    uid = f"usr-{uuid.uuid4().hex[:10]}"
    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with veritabani.baglanti() as con:
        mevcut = con.execute("SELECT id FROM kullanicilar WHERE eposta = ?", (eposta,)).fetchone()
        if mevcut:
            return json_yanit({"hata": "Bu e-posta adresi zaten kayıtlı."}, 409)
        con.execute(
            """
            INSERT INTO kullanicilar (id, eposta, parola_hash, ad_soyad, rol, kulup_kodu, aktif, olusturma_zamani)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (uid, eposta, parola_hashle(parola), ad_soyad, rol, kulup_kodu, simdi),
        )

    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=istek_yapan.get("email", "admin"),
        rol=istek_yapan.get("role", "super_admin"),
        kulup_kodu=kulup_kodu,
        islem_turu="KULLANICI_OLUSTUR",
        hedef_tablo="kullanicilar",
        hedef_id=uid,
        yeni_deger={"eposta": eposta, "ad_soyad": ad_soyad, "rol": rol, "kulup_kodu": kulup_kodu},
        neden="Admin panelinden yeni kullanıcı yetkilendirme",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit({"id": uid, "eposta": eposta, "ad_soyad": ad_soyad, "rol": rol, "kulup_kodu": kulup_kodu}, 201)


@admin_bp.get("/denetim-kayitlari")
@yetki_gerekli("denetim:kulup_ici_goruntule")
def denetim_kayitlarini_listele():
    limit = min(int(request.args.get("limit", 100)), 500)
    with veritabani.baglanti() as con:
        rows = con.execute(
            "SELECT * FROM denetim_kayitlari ORDER BY zaman DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return json_yanit({"toplam": len(rows), "denetim_kayitlari": [dict(r) for r in rows]})


@admin_bp.post("/kvkk/anonimlestir")
@yetki_gerekli("kvkk:yonet")
def kvkk_sporcu_anonimlestir():
    """
    KVKK Madde 7 & 11 (Kişisel verilerin silinmesi, yok edilmesi veya anonim hâle getirilmesi):
    Sporcunun kimlik bilgilerini geri döndürülemez biçimde maskeler, bilimsel norm havuzu
    bütünlüğünü korur ve işlemi denetim izine kaydeder.
    """
    veri = request.get_json(silent=True) or {}
    kullanici = request.kullanici  # type: ignore[attr-defined]
    sporcu_id = str(veri.get("sporcu_id") or "").strip()
    neden = str(veri.get("neden") or "Veli KVKK unutulma hakkı talebi").strip()
    if not sporcu_id:
        return json_yanit({"hata": "sporcu_id zorunludur."}, 400)

    with veritabani.baglanti() as con:
        sp = con.execute("SELECT * FROM sporcular WHERE id = ?", (sporcu_id,)).fetchone()
        if not sp:
            return json_yanit({"hata": "Sporcu bulunamadı."}, 404)
        maskeli_kod = f"Anonim-{sporcu_id[-6:].upper()}"
        eski_ad = sp["tam_ad"]
        con.execute(
            """
            UPDATE sporcular
            SET ad = 'Anonim', soyad = ?, tam_ad = ?, dogum_tarihi = '', anonimlestirildi = 1
            WHERE id = ?
            """,
            (sporcu_id[-6:].upper(), maskeli_kod, sporcu_id),
        )
        con.execute(
            "UPDATE test_sonuclari SET sporcu_adi = ? WHERE kulup_kodu = ? AND sporcu_adi = ?",
            (maskeli_kod, sp["kulup_kodu"], eski_ad),
        )
        con.execute(
            "UPDATE ilgi_anketleri SET sporcu_adi = ? WHERE kulup_kodu = ? AND sporcu_adi = ?",
            (maskeli_kod, sp["kulup_kodu"], eski_ad),
        )

    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "admin"),
        rol=kullanici.get("role", "super_admin"),
        kulup_kodu=sp["kulup_kodu"],
        islem_turu="KVKK_ANONIMLESTIRME",
        hedef_tablo="sporcular",
        hedef_id=sporcu_id,
        eski_deger={"durum": "Aktif Kimlik"},
        yeni_deger={"maskeli_kod": maskeli_kod, "anonimlestirildi": True},
        neden=neden,
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit({"sporcu_id": sporcu_id, "yeni_kod": maskeli_kod, "durum": "anonimlestirildi"})


@admin_bp.post("/yedekle")
@admin_bp.post("/yedek-al")
@yetki_gerekli("yedek:yonet")
def veritabani_yedekle():
    kullanici = request.kullanici  # type: ignore[attr-defined]
    sonuc = veritabani.yedek_olustur(
        kullanici_eposta=kullanici.get("email", "admin"),
        rol=kullanici.get("role", "super_admin"),
    )
    return json_yanit(sonuc, 201)


@admin_bp.post("/demo-yukle")
@yetki_gerekli("admin:tam_erisim")
def demo_yukle():
    kullanici = request.kullanici  # type: ignore[attr-defined]
    ozet = veritabani.demo_verisini_yukle()
    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "admin"),
        rol=kullanici.get("role", "super_admin"),
        islem_turu="DEMO_VERI_YUKLEME",
        hedef_tablo="tum_tablolar",
        hedef_id="Olcut_Demo",
        yeni_deger=ozet,
        neden="Olcut_Demo veri paketinin ilişkisel veritabanına aktarımı",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit(ozet)


@admin_bp.get("/disa-aktar/<kulup_kodu>")
def kulup_excel_disa_aktar(kulup_kodu: str):
    """Kulübün verilerini (`sporcular.xlsx`, `test_sonuclari.xlsx`, `ilgi_anketi.xlsx`) ZIP paketi olarak indirir."""
    import io
    import zipfile
    from flask import Response

    df_sp, df_ts, df_ia = veritabani.kulup_dataframeleri(kulup_kodu)
    bellek = io.BytesIO()
    with zipfile.ZipFile(bellek, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dosya_adi, df in (
            ("sporcular.xlsx", df_sp),
            ("test_sonuclari.xlsx", df_ts),
            ("ilgi_anketi.xlsx", df_ia),
        ):
            excel_buf = io.BytesIO()
            df.to_excel(excel_buf, index=False)
            zf.writestr(dosya_adi, excel_buf.getvalue())
    bellek.seek(0)
    return Response(
        bellek.getvalue(),
        mimetype="application/zip",
        headers={"Content-Disposition": f'attachment; filename="PerformTest_{kulup_kodu}_veri_paketi.zip"'},
    )

