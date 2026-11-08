"""
Motor Servisi: Mevcut `veri/` ve `olcut/` bilimsel hesaplama motorunu
Web Frontend, Admin Paneli ve Mobil Uygulama için doğrudan sarmalar.

Bu servis sayesinde 196 testlik katalog, norm, persentil, Z-skoru, 6 branş grubu
eşleştirme matrisi (Opstoel 2015), izometrik SVG sahneleri, A4 HTML/PDF rapor
üreticileri ve 191 kaynaklı bilimsel kütüphane tek satır bile kopyalanmadan
REST API üzerinden sunulur.
"""
from contextlib import contextmanager
import os
from typing import Any

import pandas as pd

from api.db import veritabani
from araclar.yukle import yukle

_KOK_DIZIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_UYGULAMA_YOLU = os.path.join(_KOK_DIZIN, "uygulama.py")
_CALISMA_ONBELLEK_DIZINI = os.path.join(_KOK_DIZIN, "yerel_veri", "calisma_onbellek")


class OlcutMotorServisi:
    """`veri/` ve `olcut/` katmanlarını bellekte tekil (singleton) olarak yükler ve sunar."""

    _baglam: dict[str, Any] | None = None

    @classmethod
    def baglam(cls) -> dict[str, Any]:
        if cls._baglam is None:
            try:
                from araclar.yukle import modulleri_yukle
                ns = modulleri_yukle(_KOK_DIZIN)
                if ns and "TEST_KATALOGU" in ns:
                    cls._baglam = ns
                else:
                    cls._baglam = yukle(_UYGULAMA_YOLU)
            except Exception:
                cls._baglam = yukle(_UYGULAMA_YOLU)
        return cls._baglam

    @classmethod
    @contextmanager
    def _kulup_calisma_ortami(cls, kulup_kodu: str = "merkez"):
        """
        Veritabanındaki kulüp verilerini geçici çalışma dizinine senkronize ederek
        `rapor_verisi`, `sporcu_z_profili` ve `sporcu_fsc_profili` gibi dosya okuyan
        orijinal `olcut/` fonksiyonlarının veritabanı kayıtlarıyla birebir çalışmasını sağlar.
        """
        hedef_dizin = os.path.join(_CALISMA_ONBELLEK_DIZINI, kulup_kodu)
        os.makedirs(hedef_dizin, exist_ok=True)
        df_sp, df_ts, df_ia = veritabani.kulup_dataframeleri(kulup_kodu)
        df_sp.to_excel(os.path.join(hedef_dizin, "sporcular.xlsx"), index=False)
        df_ts.to_excel(os.path.join(hedef_dizin, "test_sonuclari.xlsx"), index=False)
        df_ia.to_excel(os.path.join(hedef_dizin, "ilgi_anketi.xlsx"), index=False)

        eski_dizin = os.getcwd()
        try:
            os.chdir(hedef_dizin)
            yield df_sp, df_ts, df_ia
        finally:
            os.chdir(eski_dizin)

    @classmethod
    def katalog_ozeti(cls) -> dict[str, Any]:
        b = cls.baglam()
        katalog = b["TEST_KATALOGU"]
        testler = b["katalog_testleri"]()
        return {
            "surum": b.get("SURUM", "1.0"),
            "kategoriler": list(katalog.keys()),
            "toplam_kategori": len(katalog),
            "toplam_test": len(testler),
            "brans_gruplari": list(b["BRANS_GRUBU_PROFILLERI"]["gruplar"].keys()),
            "toplam_kaynakca": len(b["KAYNAKCA"]),
        }

    @classmethod
    def tum_testler(cls, arama: str = "", kategori: str = "") -> list[dict[str, Any]]:
        b = cls.baglam()
        sonuc = []
        for t in b["katalog_testleri"]():
            test_adi = t["ad"]
            kat = t.get("kategori", "")
            yol = t.get("yol") or ("", "", "")
            if kategori and kat != kategori:
                continue
            if arama and arama.lower() not in test_adi.lower() and arama.lower() not in kat.lower():
                continue
            bilgi = b["test_bilgisi"](test_adi) or {}
            batarya = yol[1] if len(yol) > 1 and yol[1] else ""
            sonuc.append(
                {
                    "test_adi": test_adi,
                    "kisa_ad": b["test_kisa"](test_adi, batarya),
                    "kategori": kat,
                    "batarya": batarya,
                    "brans": yol[2] if len(yol) > 2 and yol[2] else "",
                    "nitelik": b["test_niteligi"](test_adi),
                    "bilesen": b["test_bileseni"](test_adi),
                    "norm_var_mi": bool(b["test_norm_var_mi"](test_adi)),
                    "alanlar": bilgi.get("alanlar", []),
                    "aciklama": bilgi.get("aciklama", ""),
                }
            )
        return sonuc

    @classmethod
    def test_svg_html(cls, test_adi: str, buyuk: bool = True) -> dict[str, Any]:
        from api.services.svg_sahne_motoru import gelismis_test_sahnesi_uret

        b = cls.baglam()
        return gelismis_test_sahnesi_uret(b, test_adi)

    @classmethod
    def kaynakca_listesi(cls) -> list[dict[str, Any]]:
        b = cls.baglam()
        kaynakca = b["KAYNAKCA"]
        if isinstance(kaynakca, dict):
            return [{"anahtar": k, **(v if isinstance(v, dict) else {"metin": str(v)})} for k, v in kaynakca.items()]
        return [{"indeks": i + 1, "kaynak": k} for i, k in enumerate(kaynakca)]

    @classmethod
    def test_degerlendir(
        cls, test_adi: str, degisken: str, deger: float, yas: float, cinsiyet: str
    ) -> dict[str, Any]:
        b = cls.baglam()
        persentil = b["yas_persentil_bul"](test_adi, degisken, yas, cinsiyet, deger)
        z_skor = b["yas_z_skoru"](test_adi, degisken, yas, cinsiyet, deger)
        norm_sonuc = b["normatif_degerlendir"](degisken, deger, cinsiyet, test_adi=test_adi, yas=yas)
        esik = b["esik_degerlendir"](test_adi, degisken, deger, yas, cinsiyet)
        makul = b["makul_aralik"](test_adi, degisken, yas, cinsiyet)
        return {
            "test_adi": test_adi,
            "degisken": degisken,
            "deger": deger,
            "yas": yas,
            "cinsiyet": cinsiyet,
            "persentil": persentil,
            "z_skoru": z_skor,
            "norm_sonuc": norm_sonuc,
            "esik_kontrolu": esik,
            "makul_aralik": list(makul) if makul else None,
        }

    @classmethod
    def sporcu_kapsamli_analiz(cls, kulup_kodu: str, sporcu_adi: str) -> dict[str, Any]:
        """
        Sporcunun veritabanındaki tüm ölçümlerini `olcut/analiz.py`, `olcut/norm.py` ve `olcut/oneri.py`
        üzerinden geçirerek Z-profilini, bileşik Z puanlarını, Opstoel (2015) branş grubu eşleştirmesini,
        gelişim serilerini ve SVG radar grafiğini döndürür.
        """
        b = cls.baglam()
        with cls._kulup_calisma_ortami(kulup_kodu):
            rv = b["rapor_verisi"](sporcu_adi)
            zp = rv["zp"]
            satirlar = zp.get("satirlar", [])
            radar_html = ""
            if satirlar:
                eksenler = [f"{s['Test'][:18]}" for s in satirlar[:8]]
                degerler = [float(s.get("Z (performans)", s.get("Z", 0)) or 0) for s in satirlar[:8]]
                if len(eksenler) >= 3:
                    radar_html = b["radar_svg"](
                        eksenler,
                        [(sporcu_adi, degerler, "#2563eb", False)],
                    )
            return {
                "sporcu": sporcu_adi,
                "kulup_kodu": kulup_kodu,
                "profil": rv["bilgi"],
                "z_profili": {
                    "hata": zp.get("hata"),
                    "satirlar": satirlar,
                },
                "bilesik_z": rv["bilesikler"],
                "brans_eslestirme": rv["esl"],
                "fiziksel_pencere": rv["fiziksel_uc"],
                "ilgi_puanlari": rv["puan"],
                "kesisim_pencereleri": rv["pen"],
                "kayitli_testler": rv["testler"],
                "gelisim_ozetleri": rv["gelisim_test"],
                "sinir_notlari": rv["sinirlar"],
                "radar_svg": radar_html,
                "rapor_tarihi": rv["rapor_tarihi"],
            }

    @classmethod
    def sporcu_raporu_html(cls, kulup_kodu: str, sporcu_adi: str, rapor_turu: str = "veli") -> str:
        """`olcut/raporlar.py` üzerinden yazdırılabilir A4 Veli veya Antrenör HTML karnesi üretir."""
        b = cls.baglam()
        with cls._kulup_calisma_ortami(kulup_kodu):
            rv = b["rapor_verisi"](sporcu_adi)
            if rapor_turu == "antrenor":
                html = b["antrenor_raporu_html"](rv)
            else:
                html = b["veli_raporu_html"](rv)
            return html.replace("Ölçüt", "PerformTest")

    @classmethod
    def kulup_raporu_html(cls, kulup_kodu: str, sporcu_listesi: bool = True) -> str:
        """`olcut/kulup_raporu.py` üzerinden seçili kulübün yazdırılabilir A4 toplu HTML raporunu üretir."""
        from olcut.kulup_raporu import kulup_raporu_html as _kr_html

        b = cls.baglam()
        with veritabani.baglanti() as con:
            kr = con.execute("SELECT * FROM kulupler WHERE kod = ?", (kulup_kodu,)).fetchone()
        import json as _json
        kulup_bilgi = {
            "ad": kr["ad"] if kr else kulup_kodu,
            "sehir": kr["sehir"] if kr else "",
            "branslar": _json.loads(kr["branslar_json"] or "[]") if kr else [],
        }
        with cls._kulup_calisma_ortami(kulup_kodu) as (df_sp, df_ts, _):
            df_duzeltilmis = b["test_tablosu_duzelt"](df_ts) if not df_ts.empty else df_ts
            html = _kr_html(kulup_bilgi, df_sp, df_duzeltilmis, sporcu_listesi=sporcu_listesi)
            return html.replace("Ölçüt", "PerformTest")

    @classmethod
    def sporcu_karsilastir(cls, kulup_kodu: str, sporcu_a: str, sporcu_b: str) -> dict[str, Any]:
        """İki sporcunun Z-profillerini, fiziksel pencerelerini ve ortak radar grafiğini karşılaştırır."""
        b = cls.baglam()
        with cls._kulup_calisma_ortami(kulup_kodu):
            rv_a = b["rapor_verisi"](sporcu_a)
            rv_b = b["rapor_verisi"](sporcu_b)

            harita_a = {
                f"{s['Test']} › {s['Değişken']}": s
                for s in rv_a["zp"].get("satirlar", [])
            }
            harita_b = {
                f"{s['Test']} › {s['Değişken']}": s
                for s in rv_b["zp"].get("satirlar", [])
            }
            ortak_anahtarlar = [k for k in harita_a if k in harita_b]
            tum_anahtarlar = list(dict.fromkeys(list(harita_a.keys()) + list(harita_b.keys())))

            karsilastirma_satirlari = []
            for k in tum_anahtarlar:
                sa = harita_a.get(k, {})
                sb = harita_b.get(k, {})
                za = sa.get("Z (performans)", sa.get("Z"))
                zb = sb.get("Z (performans)", sb.get("Z"))
                fark = (round(float(za) - float(zb), 2) if za is not None and zb is not None else None)
                karsilastirma_satirlari.append(
                    {
                        "anahtar": k,
                        "test": sa.get("Test") or sb.get("Test"),
                        "degisken": sa.get("Değişken") or sb.get("Değişken"),
                        "deger_a": sa.get("Değer"),
                        "deger_b": sb.get("Değer"),
                        "z_a": za,
                        "z_b": zb,
                        "z_fark": fark,
                    }
                )

            radar_html = ""
            if len(ortak_anahtarlar) >= 3:
                secilen = ortak_anahtarlar[:8]
                eksenler = [harita_a[k]["Test"][:18] for k in secilen]
                degerler_a = [float(harita_a[k].get("Z (performans)", harita_a[k].get("Z", 0)) or 0) for k in secilen]
                degerler_b = [float(harita_b[k].get("Z (performans)", harita_b[k].get("Z", 0)) or 0) for k in secilen]
                radar_html = b["radar_svg"](
                    eksenler,
                    [
                        (sporcu_a, degerler_a, "#2563eb", False),
                        (sporcu_b, degerler_b, "#f59e0b", True),
                    ],
                )

            return {
                "kulup_kodu": kulup_kodu,
                "sporcu_a": {
                    "ad": sporcu_a,
                    "profil": rv_a["bilgi"],
                    "fiziksel_pencere": rv_a["fiziksel_uc"],
                    "bilesik_z": rv_a["bilesikler"],
                },
                "sporcu_b": {
                    "ad": sporcu_b,
                    "profil": rv_b["bilgi"],
                    "fiziksel_pencere": rv_b["fiziksel_uc"],
                    "bilesik_z": rv_b["bilesikler"],
                },
                "ortak_test_sayisi": len(ortak_anahtarlar),
                "satirlar": karsilastirma_satirlari,
                "radar_svg": radar_html,
            }
