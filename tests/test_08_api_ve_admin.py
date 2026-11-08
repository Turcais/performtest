"""
Faz 1–3 Entegrasyon Testleri: REST API (`api/`), Yerli İlişkisel Veritabanı,
JWT/RBAC Güvenlik Katmanı, Admin Paneli, KVKK Denetim İzi ve Mobil Senkronizasyon.
"""
import os
import tempfile

import pytest

from api.core.security import jwt_dogrula, jwt_olustur, parola_dogrula, parola_hashle
from api.db.veritabani import YerliVeritabani
import api.db as db_paket
from api.main import uygulama_olustur


@pytest.fixture(scope="module")
def api_istemci():
    """Geçici veritabanı üzerinde `Olcut_Demo` verileriyle çalışan test istemcisi."""
    with tempfile.TemporaryDirectory() as gecici_dizin:
        db_yolu = os.path.join(gecici_dizin, "test_olcut.db")
        test_db = YerliVeritabani(db_yolu=db_yolu)
        test_db.demo_verisini_yukle()

        # Modüllerdeki veritabani referansını test veritabanına yönlendir
        eski_db = db_paket.veritabani
        db_paket.veritabani = test_db
        import api.routers.admin as r_admin
        import api.routers.auth as r_auth
        import api.routers.mobil as r_mobil
        import api.routers.sporcular as r_sporcular
        import api.services.motor_servisi as s_motor

        r_auth.veritabani = test_db
        r_sporcular.veritabani = test_db
        r_admin.veritabani = test_db
        r_mobil.veritabani = test_db
        s_motor.veritabani = test_db

        uyg = uygulama_olustur(demo_yukle_otomatik=False)
        uyg.config["TESTING"] = True
        with uyg.test_client() as istemci:
            yield istemci

        db_paket.veritabani = eski_db
        r_auth.veritabani = eski_db
        r_sporcular.veritabani = eski_db
        r_admin.veritabani = eski_db
        r_mobil.veritabani = eski_db
        s_motor.veritabani = eski_db


def _token_al(istemci, eposta="admin@olcut.yerli", parola="OlcutAdmin2026!"):
    yanit = istemci.post("/api/v1/auth/login", json={"eposta": eposta, "parola": parola})
    assert yanit.status_code == 200
    return yanit.get_json()["access_token"]


def test_api_01_parola_ve_jwt_guvenligi():
    ozet = parola_hashle("GizliParola123!")
    assert parola_dogrula("GizliParola123!", ozet)
    assert not parola_dogrula("YanlisParola", ozet)

    token = jwt_olustur("u-1", "test@olcut.yerli", "super_admin", "merkez")
    cozulen = jwt_dogrula(token)
    assert cozulen["email"] == "test@olcut.yerli"
    assert cozulen["role"] == "super_admin"


def test_api_02_saglik_ve_katalog_uc_noktalari(api_istemci):
    r_saglik = api_istemci.get("/api/v1/health")
    assert r_saglik.status_code == 200
    veri = r_saglik.get_json()
    assert veri["motor"]["toplam_test"] == 196
    assert veri["motor"]["toplam_kaynakca"] == 191

    r_testler = api_istemci.get("/api/v1/katalog/testler?arama=Sprint")
    assert r_testler.status_code == 200
    assert r_testler.get_json()["toplam"] >= 1

    r_svg = api_istemci.get("/api/v1/katalog/svg?test_adi=20m%20Sprint")
    assert r_svg.status_code == 200
    svg_yanit = r_svg.get_json()
    assert "<svg" in svg_yanit["svg_html"]
    assert "pt-anatomik-figur" in svg_yanit["svg_html"]
    assert "pt-mocap-node" in svg_yanit["svg_html"]
    assert "BİYOMEKANİK SAHNE" in svg_yanit["svg_html"]


def test_api_03_canli_norm_ve_z_skoru_degerlendirme(api_istemci):
    r = api_istemci.post(
        "/api/v1/analiz/degerlendir",
        json={
            "test_adi": "Durarak Uzun Atlama",
            "degisken": "Deneme 1 (cm)",
            "deger": 152,
            "yas": 11,
            "cinsiyet": "Erkek",
        },
    )
    assert r.status_code == 200
    sonuc = r.get_json()
    assert sonuc["test_adi"] == "Durarak Uzun Atlama"
    assert sonuc["z_skoru"] is not None or sonuc["persentil"] is not None


def test_api_04_sporcular_analiz_ve_a4_raporlar(api_istemci):
    r_sp = api_istemci.get("/api/v1/sporcular?kulup_kodu=merkez")
    assert r_sp.status_code == 200
    sp_veri = r_sp.get_json()
    assert sp_veri["toplam"] == 17
    ilk_sporcu = sp_veri["sporcular"][0]["tam_ad"]

    r_analiz = api_istemci.get(f"/api/v1/sporcular/{ilk_sporcu}/analiz?kulup_kodu=merkez")
    assert r_analiz.status_code == 200
    analiz = r_analiz.get_json()
    assert analiz["sporcu"] == ilk_sporcu
    assert len(analiz["z_profili"]["satirlar"]) > 0
    assert "<svg" in analiz["radar_svg"]

    r_veli = api_istemci.get(f"/api/v1/sporcular/{ilk_sporcu}/rapor?kulup_kodu=merkez&tur=veli")
    assert r_veli.status_code == 200
    assert ilk_sporcu in r_veli.get_data(as_text=True)

    r_ant = api_istemci.get(f"/api/v1/sporcular/{ilk_sporcu}/rapor?kulup_kodu=merkez&tur=antrenor")
    assert r_ant.status_code == 200
    assert ilk_sporcu in r_ant.get_data(as_text=True)


def test_api_05_rbac_ve_admin_paneli_islemleri(api_istemci):
    # Yetkisiz istek reddedilmeli
    assert api_istemci.get("/api/v1/admin/ozet").status_code == 401

    # Antrenör rolü yeni kulüp oluşturamamalı (403 Forbidden)
    ant_token = _token_al(api_istemci, "antrenor@olcut.yerli", "Antrenor2026!")
    r_yasak = api_istemci.post(
        "/api/v1/admin/kulupler",
        headers={"Authorization": f"Bearer {ant_token}"},
        json={"kod": "yeni-kulup", "ad": "Yeni Kulüp"},
    )
    assert r_yasak.status_code == 403

    # Süper Admin tüm admin işlemlerini yapabilmeli
    adm_token = _token_al(api_istemci, "admin@olcut.yerli", "OlcutAdmin2026!")
    baslik = {"Authorization": f"Bearer {adm_token}"}

    r_ozet = api_istemci.get("/api/v1/admin/ozet", headers=baslik)
    assert r_ozet.status_code == 200
    assert r_ozet.get_json()["metrikler"]["toplam_sporcu"] == 28  # 17 + 5 + 6

    r_kulup = api_istemci.post(
        "/api/v1/admin/kulupler",
        headers=baslik,
        json={"kod": "tez-kulubu", "ad": "Bitirme Tezi Spor Kulübü", "sehir": "Ankara"},
    )
    assert r_kulup.status_code == 201

    r_yedek = api_istemci.post("/api/v1/admin/yedekle", headers=baslik)
    assert r_yedek.status_code == 201
    assert r_yedek.get_json()["boyut_bayt"] > 0

    r_denetim = api_istemci.get("/api/v1/admin/denetim-kayitlari", headers=baslik)
    assert r_denetim.status_code == 200
    assert r_denetim.get_json()["toplam"] >= 3


def test_api_06_saha_olcum_kaydi_ve_mobil_senkronizasyon(api_istemci):
    ant_token = _token_al(api_istemci, "antrenor@olcut.yerli", "Antrenor2026!")
    baslik = {"Authorization": f"Bearer {ant_token}"}

    r_olcum = api_istemci.post(
        "/api/v1/oturumlar/olcum-kaydet",
        headers=baslik,
        json={
            "kulup_kodu": "merkez",
            "sporcu_adi": "Ali Demo",
            "test_adi": "20m Sprint",
            "test_yasi": 10,
            "olcumler": {"En İyi Süre (sn)": 3.62},
        },
    )
    assert r_olcum.status_code == 201
    assert len(r_olcum.get_json()["degerlendirmeler"]) == 1

    r_paket = api_istemci.get("/api/v1/mobil/paket?kulup_kodu=demo-kulup-a")
    assert r_paket.status_code == 200
    assert r_paket.get_json()["sporcu_sayisi"] == 5

    r_sync = api_istemci.post(
        "/api/v1/mobil/senkronize-et",
        headers=baslik,
        json={
            "cihaz_id": "tablet-saha-01",
            "kulup_kodu": "demo-kulup-a",
            "kayitlar": [
                {
                    "sporcu_adi": "Can Demo",
                    "test_adi": "Durarak Uzun Atlama",
                    "test_yasi": 10,
                    "olcumler": {"En İyi Değer (cm)": 148},
                }
            ],
        },
    )
    assert r_sync.status_code == 201
    assert r_sync.get_json()["islenen_kayit_sayisi"] == 1


def test_api_07_kvkk_anonimlestirme_ve_web_arayuzu(api_istemci):
    adm_token = _token_al(api_istemci, "admin@olcut.yerli", "OlcutAdmin2026!")
    baslik = {"Authorization": f"Bearer {adm_token}"}

    # Yeni sporcu ekle ve KVKK kapsamında anonimleştir
    r_yeni = api_istemci.post(
        "/api/v1/sporcular",
        headers=baslik,
        json={"kulup_kodu": "demo-kulup-b", "ad": "Deneme", "soyad": "Sporcu", "yas": 11, "cinsiyet": "Erkek"},
    )
    assert r_yeni.status_code == 201
    sp_id = r_yeni.get_json()["id"]

    r_anon = api_istemci.post(
        "/api/v1/admin/kvkk/anonimlestir",
        headers=baslik,
        json={"sporcu_id": sp_id, "neden": "Veli KVKK silme/anonimleştirme talebi"},
    )
    assert r_anon.status_code == 200
    assert r_anon.get_json()["durum"] == "anonimlestirildi"

    # Web Frontend ve Admin SPA ekranları (PerformTest markasıyla)
    r_ana = api_istemci.get("/")
    assert r_ana.status_code == 200
    assert "PerformTest" in r_ana.get_data(as_text=True)
    assert api_istemci.get("/admin").status_code == 200


def test_api_08_performtest_karsilastirma_kulup_raporu_ve_excel_ihraci(api_istemci):
    # PerformTest kurumsal hesabıyla giriş
    pt_token = _token_al(api_istemci, "admin@performtest.yerli", "PerformAdmin2026!")
    assert pt_token

    # Başa baş sporcu karşılaştırması ve çift katmanlı Radar SVG
    r_kars = api_istemci.get("/api/v1/karsilastir?kulup_kodu=merkez&sporcu_a=Ali%20Demo&sporcu_b=Ay%C5%9Fe%20Demo")
    assert r_kars.status_code == 200
    kars_veri = r_kars.get_json()
    assert kars_veri["sporcu_a"]["ad"] == "Ali Demo"
    assert kars_veri["sporcu_b"]["ad"] == "Ayşe Demo"
    assert len(kars_veri["satirlar"]) > 0

    # A4 Kulüp Performans Raporu
    r_krapor = api_istemci.get("/api/v1/kulupler/demo-kulup-a/rapor")
    assert r_krapor.status_code == 200
    assert "Demo Kulüp A" in r_krapor.get_data(as_text=True)

    # Kulüp Excel (.zip) veri paketi ihracı
    r_zip = api_istemci.get("/api/v1/admin/disa-aktar/demo-kulup-a")
    assert r_zip.status_code == 200
    assert r_zip.mimetype == "application/zip"
    assert len(r_zip.data) > 1000
