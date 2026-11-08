"""
Sporcu Yönetimi, Saha Ölçüm Girişi, Bireysel Analiz ve A4 Rapor Uç Noktaları
(`/api/v1/sporcular` ve `/api/v1/oturumlar`).
"""
from datetime import datetime, timezone
import json
import uuid
from flask import Blueprint, Response, request

from api.core.http_yardimci import istek_kullanicisi, json_yanit, yetki_gerekli
from api.db import veritabani
from api.services.motor_servisi import OlcutMotorServisi

sporcular_bp = Blueprint("sporcular", __name__, url_prefix="/api/v1")


@sporcular_bp.get("/sporcular")
def sporculari_listele():
    kulup = request.args.get("kulup_kodu", "merkez").strip() or "merkez"
    with veritabani.baglanti() as con:
        satirlar = con.execute(
            """
            SELECT s.*,
                   (SELECT COUNT(*) FROM test_sonuclari t
                    WHERE t.kulup_kodu = s.kulup_kodu AND t.sporcu_adi = s.tam_ad AND t.silindi_mi = 0) AS olcum_sayisi
            FROM sporcular s
            WHERE s.kulup_kodu = ? AND s.silindi_mi = 0
            ORDER BY s.ad, s.soyad
            """,
            (kulup,),
        ).fetchall()
    return json_yanit(
        {
            "kulup_kodu": kulup,
            "toplam": len(satirlar),
            "sporcular": [dict(r) for r in satirlar],
        }
    )


@sporcular_bp.post("/sporcular")
@yetki_gerekli("oturum:yaz")
def sporcu_ekle():
    veri = request.get_json(silent=True) or {}
    kullanici = request.kullanici  # type: ignore[attr-defined]
    kulup = str(veri.get("kulup_kodu") or kullanici.get("club") or "merkez").strip()
    ad = str(veri.get("ad") or "").strip()
    soyad = str(veri.get("soyad") or "").strip()
    cinsiyet = str(veri.get("cinsiyet") or "Erkek").strip()
    if not ad or not soyad:
        return json_yanit({"hata": "Ad ve soyad zorunludur."}, 400)

    tam_ad = f"{ad} {soyad}"
    sp_id = f"sp-{uuid.uuid4().hex[:10]}"
    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    yas = float(veri["yas"]) if veri.get("yas") is not None else None
    boy_cm = float(veri["boy_cm"]) if veri.get("boy_cm") is not None else None
    kilo_kg = float(veri["kilo_kg"]) if veri.get("kilo_kg") is not None else None

    with veritabani.baglanti() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO sporcular
            (id, kulup_kodu, ad, soyad, tam_ad, yas, dogum_tarihi, cinsiyet, spor_dali,
             boy_cm, kilo_kg, kvkk_onayli, kvkk_onay_tarihi, olusturma_zamani)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                sp_id,
                kulup,
                ad,
                soyad,
                tam_ad,
                yas,
                str(veri.get("dogum_tarihi") or ""),
                cinsiyet,
                str(veri.get("spor_dali") or "Genel"),
                boy_cm,
                kilo_kg,
                simdi,
                simdi,
            ),
        )

    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "sistem"),
        rol=kullanici.get("role", "antrenor"),
        kulup_kodu=kulup,
        islem_turu="SPORCU_OLUSTUR",
        hedef_tablo="sporcular",
        hedef_id=sp_id,
        yeni_deger={"tam_ad": tam_ad, "yas": yas, "cinsiyet": cinsiyet, "kulup_kodu": kulup},
        neden="Yeni sporcu kaydı ve KVKK açık rıza onayı",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit({"id": sp_id, "tam_ad": tam_ad, "kulup_kodu": kulup}, 201)


@sporcular_bp.get("/sporcular/<sporcu_adi>/analiz")
def sporcu_analiz(sporcu_adi: str):
    kulup = request.args.get("kulup_kodu", "merkez").strip() or "merkez"
    analiz = OlcutMotorServisi.sporcu_kapsamli_analiz(kulup, sporcu_adi)
    return json_yanit(analiz)


@sporcular_bp.get("/sporcular/<sporcu_adi>/rapor")
def sporcu_rapor(sporcu_adi: str):
    kulup = request.args.get("kulup_kodu", "merkez").strip() or "merkez"
    tur = request.args.get("tur", "veli").strip().lower()
    html_icerik = OlcutMotorServisi.sporcu_raporu_html(kulup, sporcu_adi, rapor_turu=tur)
    if request.args.get("format") == "json":
        return json_yanit({"sporcu": sporcu_adi, "kulup_kodu": kulup, "tur": tur, "html": html_icerik})
    return Response(html_icerik, mimetype="text/html; charset=utf-8")


@sporcular_bp.get("/kulupler/<kulup_kodu>/rapor")
def kulup_rapor(kulup_kodu: str):
    liste_ekle = request.args.get("sporcu_listesi", "1") != "0"
    html_icerik = OlcutMotorServisi.kulup_raporu_html(kulup_kodu, sporcu_listesi=liste_ekle)
    if request.args.get("format") == "json":
        return json_yanit({"kulup_kodu": kulup_kodu, "html": html_icerik})
    return Response(html_icerik, mimetype="text/html; charset=utf-8")


@sporcular_bp.get("/karsilastir")
def sporcu_karsilastir_uc_noktasi():
    kulup = request.args.get("kulup_kodu", "merkez").strip() or "merkez"
    sporcu_a = request.args.get("sporcu_a", "").strip()
    sporcu_b = request.args.get("sporcu_b", "").strip()
    if not sporcu_a or not sporcu_b:
        return json_yanit({"hata": "sporcu_a ve sporcu_b parametreleri zorunludur."}, 400)
    sonuc = OlcutMotorServisi.sporcu_karsilastir(kulup, sporcu_a, sporcu_b)
    return json_yanit(sonuc)


@sporcular_bp.post("/oturumlar/olcum-kaydet")
@yetki_gerekli("oturum:yaz")
def olcum_kaydet():
    veri = request.get_json(silent=True) or {}
    kullanici = request.kullanici  # type: ignore[attr-defined]
    kulup = str(veri.get("kulup_kodu") or kullanici.get("club") or "merkez").strip()
    sporcu_adi = str(veri.get("sporcu_adi") or "").strip()
    test_adi = str(veri.get("test_adi") or "").strip()
    olcumler = veri.get("olcumler") or {}
    if not sporcu_adi or not test_adi or not isinstance(olcumler, dict) or not olcumler:
        return json_yanit({"hata": "sporcu_adi, test_adi ve olcumler sözlüğü zorunludur."}, 400)

    kayit_id = f"ts-{uuid.uuid4().hex[:12]}"
    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tarih = str(veri.get("tarih") or datetime.now().strftime("%d.%m.%Y"))
    b = OlcutMotorServisi.baglam()

    with veritabani.baglanti() as con:
        sp = con.execute(
            "SELECT id, yas, cinsiyet FROM sporcular WHERE kulup_kodu = ? AND tam_ad = ?",
            (kulup, sporcu_adi),
        ).fetchone()
        sp_id = sp["id"] if sp else None
        yas = float(veri.get("test_yasi") or (sp["yas"] if sp and sp["yas"] else 10))
        cinsiyet = str(veri.get("cinsiyet") or (sp["cinsiyet"] if sp else "Erkek"))

        con.execute(
            """
            INSERT INTO test_sonuclari
            (id, kulup_kodu, sporcu_id, sporcu_adi, kategori, batarya, brans, test_adi,
             tarih, notlar, test_yasi, oturum, yer, uygulayici, olcumler_json, silindi_mi, olusturma_zamani)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                kayit_id,
                kulup,
                sp_id,
                sporcu_adi,
                str(veri.get("kategori") or b["test_niteligi"](test_adi) or ""),
                str(veri.get("batarya") or ""),
                str(veri.get("brans") or ""),
                test_adi,
                tarih,
                str(veri.get("notlar") or ""),
                yas,
                str(veri.get("oturum") or "Saha Oturumu"),
                str(veri.get("yer") or ""),
                kullanici.get("email", ""),
                json.dumps(olcumler, ensure_ascii=False),
                simdi,
            ),
        )

    degerlendirmeler = []
    for deg, val in olcumler.items():
        try:
            sayisal = float(val)
            degerlendirmeler.append(
                OlcutMotorServisi.test_degerlendir(test_adi, deg, sayisal, yas, cinsiyet)
            )
        except (TypeError, ValueError):
            pass

    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "sistem"),
        rol=kullanici.get("role", "antrenor"),
        kulup_kodu=kulup,
        islem_turu="OLCUM_KAYDET",
        hedef_tablo="test_sonuclari",
        hedef_id=kayit_id,
        yeni_deger={"sporcu": sporcu_adi, "test": test_adi, "olcumler": olcumler},
        neden="Saha ölçüm oturumu kaydı",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit(
        {
            "id": kayit_id,
            "sporcu_adi": sporcu_adi,
            "test_adi": test_adi,
            "tarih": tarih,
            "degerlendirmeler": degerlendirmeler,
        },
        201,
    )

