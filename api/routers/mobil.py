"""
Mobil Uygulama Saha Senkronizasyon Uç Noktaları (`/api/v1/mobil`).

İlerleyen dönemde geliştirilecek React Native / Expo mobil uygulaması için:
- `/paket`: Saha cihazının çevrimdışı çalışabilmesi için hafifletilmiş test kataloğu + sporcu listesi paketi
- `/senkronize-et`: İnternet bağlantısı olmayan spor salonlarında toplanan saha ölçümlerini toplu (batch) olarak sunucuya kaydeder
"""
from datetime import datetime, timezone
import json
import uuid
from flask import Blueprint, request

from api.core.http_yardimci import json_yanit, yetki_gerekli
from api.db import veritabani
from api.services.motor_servisi import OlcutMotorServisi

mobil_bp = Blueprint("mobil", __name__, url_prefix="/api/v1/mobil")


@mobil_bp.get("/paket")
def mobil_saha_paketi():
    kulup = request.args.get("kulup_kodu", "merkez").strip() or "merkez"
    with veritabani.baglanti() as con:
        sporcular = con.execute(
            "SELECT id, tam_ad, yas, cinsiyet, spor_dali, grup_sinif FROM sporcular WHERE kulup_kodu = ? AND silindi_mi = 0 ORDER BY tam_ad",
            (kulup,),
        ).fetchall()
    testler = OlcutMotorServisi.tum_testler()
    return json_yanit(
        {
            "kulup_kodu": kulup,
            "paket_zamani": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sporcu_sayisi": len(sporcular),
            "sporcular": [dict(r) for r in sporcular],
            "test_sayisi": len(testler),
            "testler": testler,
        }
    )


@mobil_bp.post("/senkronize-et")
@yetki_gerekli("oturum:yaz")
def mobil_senkronize_et():
    veri = request.get_json(silent=True) or {}
    kullanici = request.kullanici  # type: ignore[attr-defined]
    cihaz_id = str(veri.get("cihaz_id") or "mobil-saha-cihazi").strip()
    kulup = str(veri.get("kulup_kodu") or kullanici.get("club") or "merkez").strip()
    kayitlar = veri.get("kayitlar") or []
    if not isinstance(kayitlar, list) or not kayitlar:
        return json_yanit({"hata": "Senkronize edilecek kayitlar listesi boş olamaz."}, 400)

    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    eklenen_ids = []
    with veritabani.baglanti() as con:
        for k in kayitlar:
            sporcu_adi = str(k.get("sporcu_adi") or "").strip()
            test_adi = str(k.get("test_adi") or "").strip()
            olcumler = k.get("olcumler") or {}
            if not sporcu_adi or not test_adi or not olcumler:
                continue
            ts_id = f"ts-mob-{uuid.uuid4().hex[:10]}"
            con.execute(
                """
                INSERT INTO test_sonuclari
                (id, kulup_kodu, sporcu_adi, test_adi, tarih, test_yasi, oturum, yer, uygulayici, olcumler_json, silindi_mi, olusturma_zamani)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    ts_id,
                    kulup,
                    sporcu_adi,
                    test_adi,
                    str(k.get("tarih") or datetime.now().strftime("%d.%m.%Y")),
                    k.get("test_yasi"),
                    str(k.get("oturum") or "Mobil Saha Oturumu"),
                    str(k.get("yer") or "Saha"),
                    kullanici.get("email", ""),
                    json.dumps(olcumler, ensure_ascii=False),
                    simdi,
                ),
            )
            eklenen_ids.append(ts_id)

        senkron_id = f"sync-{uuid.uuid4().hex[:10]}"
        con.execute(
            """
            INSERT INTO mobil_senkron_kuyrugu
            (id, cihaz_id, kulup_kodu, kullanici_eposta, kayit_sayisi, veri_json, islenme_zamani)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                senkron_id,
                cihaz_id,
                kulup,
                kullanici.get("email", ""),
                len(eklenen_ids),
                json.dumps(kayitlar, ensure_ascii=False),
                simdi,
            ),
        )

    veritabani.denetim_kaydi_ekle(
        kullanici_eposta=kullanici.get("email", "antrenor"),
        rol=kullanici.get("role", "antrenor"),
        kulup_kodu=kulup,
        islem_turu="MOBIL_TOPLU_SENKRON",
        hedef_tablo="test_sonuclari",
        hedef_id=senkron_id,
        yeni_deger={"cihaz_id": cihaz_id, "eklenen_kayit_sayisi": len(eklenen_ids)},
        neden="Mobil çevrimdışı saha ölçümleri senkronizasyonu",
        ip_adresi=request.remote_addr or "127.0.0.1",
    )
    return json_yanit(
        {
            "senkron_id": senkron_id,
            "cihaz_id": cihaz_id,
            "kulup_kodu": kulup,
            "islenen_kayit_sayisi": len(eklenen_ids),
            "kayit_idleri": eklenen_ids,
        },
        201,
    )

