"""
Rol Tabanlı Erişim Kontrolü (RBAC), Parola Özetleme (PBKDF2-HMAC-SHA256)
ve RFC 7519 Uyumlu JWT (HMAC-SHA256) Kimlik Doğrulama Katmanı.

Yerli sunucu mimarisi gereği dış bulut kimlik sağlayıcılarına (Auth0, Firebase Auth vb.)
bağımlı değildir; tamamen kurum içi sunucuda çalışır.
"""
import base64
import hashlib
import hmac
import json
import secrets
import time
from enum import StrEnum
from typing import Any

from api.core.config import ayarlar


class KullaniciRolu(StrEnum):
    SUPER_ADMIN = "super_admin"
    KULUP_YONETICISI = "kulup_yoneticisi"
    ANTRENOR = "antrenor"
    SPORCU_VELI = "sporcu_veli"


YETKI_MATRISI: dict[str, set[str]] = {
    KullaniciRolu.SUPER_ADMIN: {
        "admin:tam_erisim",
        "kulup:olustur",
        "kulup:duzenle",
        "kullanici:yonet",
        "denetim:goruntule",
        "kvkk:yonet",
        "yedek:yonet",
        "oturum:yaz",
        "analiz:goruntule",
        "rapor:indir",
    },
    KullaniciRolu.KULUP_YONETICISI: {
        "kulup:duzenle",
        "kullanici:kulup_ici_yonet",
        "denetim:kulup_ici_goruntule",
        "oturum:yaz",
        "analiz:goruntule",
        "rapor:indir",
    },
    KullaniciRolu.ANTRENOR: {
        "oturum:yaz",
        "analiz:goruntule",
        "rapor:indir",
    },
    KullaniciRolu.SPORCU_VELI: {
        "analiz:kendi_sporcusu",
        "rapor:kendi_sporcusu",
    },
}


def parola_hashle(parola: str, tuz: str | None = None) -> str:
    """Parolayı PBKDF2-HMAC-SHA256 (260.000 iterasyon) ile güvenli özetler."""
    tuz_degeri = tuz or secrets.token_hex(16)
    ozet = hashlib.pbkdf2_hmac(
        "sha256",
        parola.encode("utf-8"),
        tuz_degeri.encode("utf-8"),
        260_000,
    ).hex()
    return f"pbkdf2_sha256$260000${tuz_degeri}${ozet}"


def parola_dogrula(parola: str, kayitli_hash: str) -> bool:
    """Girilen parolayı kayıtlı PBKDF2 özetiyle sabit-zamanlı karşılaştırır."""
    try:
        algoritma, iterasyon_str, tuz, _ = kayitli_hash.split("$", 3)
        if algoritma != "pbkdf2_sha256":
            return False
        hesaplanan = hashlib.pbkdf2_hmac(
            "sha256",
            parola.encode("utf-8"),
            tuz.encode("utf-8"),
            int(iterasyon_str),
        ).hex()
        beklenen = kayitli_hash.split("$", 3)[3]
        return hmac.compare_digest(hesaplanan, beklenen)
    except Exception:
        return False


def _b64url_kodla(veri: bytes) -> str:
    return base64.urlsafe_b64encode(veri).rstrip(b"=").decode("ascii")


def _b64url_coz(metin: str) -> bytes:
    dolgu = "=" * (-len(metin) % 4)
    return base64.urlsafe_b64decode(metin + dolgu)


def jwt_olustur(
    kullanici_id: str,
    eposta: str,
    rol: str,
    kulup_kodu: str | None = None,
    sure_dakika: int | None = None,
    token_tipi: str = "access",
) -> str:
    """Standart HS256 JWT token üretir."""
    simdi = int(time.time())
    gecerlilik_sn = (sure_dakika or ayarlar.ACCESS_TOKEN_SURESI_DAKIKA) * 60
    baslik = {"alg": "HS256", "typ": "JWT"}
    govde = {
        "sub": kullanici_id,
        "email": eposta,
        "role": rol,
        "club": kulup_kodu,
        "type": token_tipi,
        "iat": simdi,
        "exp": simdi + gecerlilik_sn,
    }
    b_baslik = _b64url_kodla(json.dumps(baslik, separators=(",", ":")).encode("utf-8"))
    b_govde = _b64url_kodla(json.dumps(govde, separators=(",", ":")).encode("utf-8"))
    mesaj = f"{b_baslik}.{b_govde}".encode("ascii")
    imza = hmac.new(ayarlar.JWT_GIZLI_ANAHTAR.encode("utf-8"), mesaj, hashlib.sha256).digest()
    return f"{b_baslik}.{b_govde}.{_b64url_kodla(imza)}"


def jwt_dogrula(token: str) -> dict[str, Any]:
    """JWT imzasını ve süresini doğrular; geçerliyse payload sözlüğünü döndürür."""
    parcalar = token.split(".")
    if len(parcalar) != 3:
        raise ValueError("Geçersiz JWT biçimi.")
    b_baslik, b_govde, b_imza = parcalar
    mesaj = f"{b_baslik}.{b_govde}".encode("ascii")
    beklenen_imza = _b64url_kodla(
        hmac.new(ayarlar.JWT_GIZLI_ANAHTAR.encode("utf-8"), mesaj, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(b_imza, beklenen_imza):
        raise ValueError("JWT imzası doğrulanamadı.")
    govde = json.loads(_b64url_coz(b_govde).decode("utf-8"))
    if int(govde.get("exp", 0)) < int(time.time()):
        raise ValueError("JWT süresi dolmuş.")
    return govde


def yetki_var_mi(rol: str, aranan_yetki: str) -> bool:
    """Verilen rolün belirtilen işlem yetkisine sahip olup olmadığını kontrol eder."""
    yetkiler = YETKI_MATRISI.get(rol, set())
    return "admin:tam_erisim" in yetkiler or aranan_yetki in yetkiler


def kulup_erisim_var_mi(kullanici: dict[str, Any], hedef_kulup_kodu: str | None) -> bool:
    """Çok-kulüplü (multi-tenant) veri izolasyonu denetimi."""
    if kullanici.get("role") == KullaniciRolu.SUPER_ADMIN:
        return True
    if not hedef_kulup_kodu:
        return False
    return kullanici.get("club") == hedef_kulup_kodu
