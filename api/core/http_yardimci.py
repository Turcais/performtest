"""
HTTP İstek/Yanıt Yardımcıları, Güvenli JSON Serileştirici ve RBAC Middleware Dekoratörleri.
"""
from functools import wraps
import math
from typing import Any

from flask import Response, jsonify, request
import pandas as pd

from api.core.security import jwt_dogrula, yetki_var_mi


def temiz_json(veri: Any) -> Any:
    """`pandas`/`numpy`/`NaN` değerlerini standart JSON tiplerine dönüştürür."""
    if veri is None:
        return None
    if isinstance(veri, float):
        if math.isnan(veri) or math.isinf(veri):
            return None
        return veri
    if isinstance(veri, (str, int, bool)):
        return veri
    if isinstance(veri, dict):
        return {str(k): temiz_json(v) for k, v in veri.items()}
    if isinstance(veri, (list, tuple, set)):
        return [temiz_json(x) for x in veri]
    if hasattr(veri, "item"):
        return temiz_json(veri.item())
    if pd.isna(veri):
        return None
    return str(veri)


def json_yanit(veri: Any, durum_kodu: int = 200) -> tuple[Response, int]:
    return jsonify(temiz_json(veri)), durum_kodu


def istek_kullanicisi() -> dict[str, Any] | None:
    """Authorization: Bearer <token> başlığından doğrulanmış kullanıcı bilgisini döndürür."""
    baslik = request.headers.get("Authorization", "")
    if not baslik.startswith("Bearer "):
        return None
    token = baslik[len("Bearer "):].strip()
    try:
        return jwt_dogrula(token)
    except ValueError:
        return None


def giris_gerekli(fn):
    @wraps(fn)
    def sarici(*args, **kwargs):
        kullanici = istek_kullanicisi()
        if not kullanici:
            return json_yanit({"hata": "Yetkisiz erişim. Geçerli bir JWT token gereklidir."}, 401)
        request.kullanici = kullanici  # type: ignore[attr-defined]
        return fn(*args, **kwargs)

    return sarici


def yetki_gerekli(aranan_yetki: str):
    def dekorator(fn):
        @wraps(fn)
        def sarici(*args, **kwargs):
            kullanici = istek_kullanicisi()
            if not kullanici:
                return json_yanit({"hata": "Yetkisiz erişim. Geçerli bir JWT token gereklidir."}, 401)
            rol = kullanici.get("role", "")
            if not yetki_var_mi(rol, aranan_yetki):
                return json_yanit(
                    {"hata": f"Bu işlem için '{aranan_yetki}' yetkisi gereklidir (Mevcut rol: {rol})."},
                    403,
                )
            request.kullanici = kullanici  # type: ignore[attr-defined]
            return fn(*args, **kwargs)

        return sarici

    return dekorator

