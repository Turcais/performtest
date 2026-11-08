"""
Test Kataloğu, Bilimsel Kaynakça, İzometrik SVG Diyagramlar ve Canlı Ölçüm Değerlendirme Uç Noktaları
(`/api/v1/katalog` ve `/api/v1/analiz`).
"""
from flask import Blueprint, request

from api.core.http_yardimci import json_yanit
from api.services.motor_servisi import OlcutMotorServisi

katalog_bp = Blueprint("katalog", __name__, url_prefix="/api/v1")


@katalog_bp.get("/katalog/ozet")
def katalog_ozet():
    return json_yanit(OlcutMotorServisi.katalog_ozeti())


@katalog_bp.get("/katalog/testler")
def katalog_testler():
    arama = request.args.get("arama", "").strip()
    kategori = request.args.get("kategori", "").strip()
    testler = OlcutMotorServisi.tum_testler(arama=arama, kategori=kategori)
    return json_yanit({"toplam": len(testler), "testler": testler})


@katalog_bp.get("/katalog/svg")
def katalog_svg():
    test_adi = request.args.get("test_adi", "").strip()
    if not test_adi:
        return json_yanit({"hata": "test_adi parametresi zorunludur."}, 400)
    return json_yanit(OlcutMotorServisi.test_svg_html(test_adi))


@katalog_bp.get("/katalog/kaynakca")
def katalog_kaynakca():
    liste = OlcutMotorServisi.kaynakca_listesi()
    return json_yanit({"toplam": len(liste), "kaynakca": liste})


@katalog_bp.post("/analiz/degerlendir")
def analiz_degerlendir():
    veri = request.get_json(silent=True) or {}
    test_adi = str(veri.get("test_adi") or "").strip()
    degisken = str(veri.get("degisken") or "").strip()
    cinsiyet = str(veri.get("cinsiyet") or "Erkek").strip()
    try:
        deger = float(veri.get("deger"))
        yas = float(veri.get("yas"))
    except (TypeError, ValueError):
        return json_yanit({"hata": "deger ve yas sayısal olmalıdır."}, 400)
    if not test_adi or not degisken:
        return json_yanit({"hata": "test_adi ve degisken zorunludur."}, 400)
    sonuc = OlcutMotorServisi.test_degerlendir(
        test_adi=test_adi,
        degisken=degisken,
        deger=deger,
        yas=yas,
        cinsiyet=cinsiyet,
    )
    return json_yanit(sonuc)

