"""
Kimlik Doğrulama ve Oturum Yönetimi Uç Noktaları (`/api/v1/auth`).
"""
from datetime import datetime, timezone
from flask import Blueprint, request

from api.core.http_yardimci import giris_gerekli, json_yanit
from api.core.security import YETKI_MATRISI, jwt_olustur, parola_dogrula
from api.db import veritabani

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/login")
def login():
    veri = request.get_json(silent=True) or {}
    eposta = str(veri.get("eposta") or veri.get("email") or "").strip().lower()
    parola = str(veri.get("parola") or veri.get("password") or "")
    if not eposta or not parola:
        return json_yanit({"hata": "E-posta ve parola zorunludur."}, 400)

    with veritabani.baglanti() as con:
        k = con.execute("SELECT * FROM kullanicilar WHERE lower(eposta) = ?", (eposta,)).fetchone()
        if not k or not k["aktif"]:
            return json_yanit({"hata": "Geçersiz kullanıcı veya pasif hesap."}, 401)
        if not parola_dogrula(parola, k["parola_hash"]):
            return json_yanit({"hata": "E-posta veya parola hatalı."}, 401)
        simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        con.execute("UPDATE kullanicilar SET son_giris = ? WHERE id = ?", (simdi, k["id"]))

    access_token = jwt_olustur(
        kullanici_id=k["id"],
        eposta=k["eposta"],
        rol=k["rol"],
        kulup_kodu=k["kulup_kodu"],
        token_tipi="access",
    )
    refresh_token = jwt_olustur(
        kullanici_id=k["id"],
        eposta=k["eposta"],
        rol=k["rol"],
        kulup_kodu=k["kulup_kodu"],
        sure_dakika=60 * 24 * 14,
        token_tipi="refresh",
    )
    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=k["eposta"],
        rol=k["rol"],
        kulup_kodu=k["kulup_kodu"],
        islem_turu="OTURUM_ACMA",
        hedef_tablo="kullanicilar",
        hedef_id=k["id"],
        neden="Başarılı JWT girişi",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "kullanici": {
                "id": k["id"],
                "eposta": k["eposta"],
                "ad_soyad": k["ad_soyad"],
                "rol": k["rol"],
                "kulup_kodu": k["kulup_kodu"],
                "yetkiler": sorted(YETKI_MATRISI.get(k["rol"], set())),
            },
        }
    )


@auth_bp.get("/me")
@giris_gerekli
def me():
    k = request.kullanici  # type: ignore[attr-defined]
    rol = k.get("role", "")
    return json_yanit(
        {
            "id": k.get("sub"),
            "eposta": k.get("email"),
            "rol": rol,
            "kulup_kodu": k.get("club"),
            "yetkiler": sorted(YETKI_MATRISI.get(rol, set())),
        }
    )

