"""
Ölçüt REST API ve Web/Admin Sunucusu Giriş Noktası (`api/main.py`).

Çalıştırma:
    py -3.14 -m api.main

Adresler:
    - Web Uygulaması : http://localhost:8000/
    - Admin Paneli   : http://localhost:8000/admin
    - API Sağlık     : http://localhost:8000/api/v1/health
"""
from flask import Flask, Response

from api.arayuz_html import WEB_VE_ADMIN_HTML
from api.core.config import ayarlar
from api.core.http_yardimci import json_yanit
from api.db import veritabani
from api.routers.admin import admin_bp
from api.routers.auth import auth_bp
from api.routers.katalog import katalog_bp
from api.routers.mobil import mobil_bp
from api.routers.sporcular import sporcular_bp
from api.services.motor_servisi import OlcutMotorServisi


def uygulama_bilgisi() -> dict:
    """API sağlık kontrolü ve katalog özeti."""
    ozet = OlcutMotorServisi.katalog_ozeti()
    return {
        "proje": ayarlar.PROJE_ADI,
        "api_onek": ayarlar.API_V1_ONEK,
        "ortam": ayarlar.ORTAM,
        "motor": ozet,
        "moduller": [
            f"{ayarlar.API_V1_ONEK}/auth",
            f"{ayarlar.API_V1_ONEK}/katalog",
            f"{ayarlar.API_V1_ONEK}/sporcular",
            f"{ayarlar.API_V1_ONEK}/oturumlar",
            f"{ayarlar.API_V1_ONEK}/analiz",
            f"{ayarlar.API_V1_ONEK}/admin",
            f"{ayarlar.API_V1_ONEK}/mobil",
        ],
    }


def uygulama_olustur(demo_yukle_otomatik: bool = True) -> Flask:
    """Flask tabanlı REST API ve Web/Admin sunucusunu yapılandırır."""
    app = Flask(__name__)

    if demo_yukle_otomatik:
        with veritabani.baglanti() as con:
            mevcut_sp = con.execute("SELECT COUNT(*) AS n FROM sporcular").fetchone()["n"]
        if mevcut_sp == 0:
            veritabani.demo_verisini_yukle()

    @app.after_request
    def cors_basliklari_ekle(yanit: Response) -> Response:
        yanit.headers["Access-Control-Allow-Origin"] = "*"
        yanit.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        yanit.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return yanit

    @app.get("/")
    def ana_sayfa():
        return Response(WEB_VE_ADMIN_HTML, mimetype="text/html; charset=utf-8")

    @app.get("/admin")
    def admin_sayfasi():
        return Response(WEB_VE_ADMIN_HTML, mimetype="text/html; charset=utf-8")

    @app.get("/api/v1/health")
    def saglik():
        return json_yanit(uygulama_bilgisi())

    app.register_blueprint(auth_bp)
    app.register_blueprint(katalog_bp)
    app.register_blueprint(sporcular_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mobil_bp)

    return app


app = uygulama_olustur()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
