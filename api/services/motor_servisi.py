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
    def _ozel_test_getir(cls, test_adi: str) -> dict[str, Any] | None:
        import json as _json

        try:
            with veritabani.baglanti() as con:
                r = con.execute("SELECT * FROM ozel_testler WHERE test_adi = ?", (test_adi,)).fetchone()
                if not r:
                    return None
                d = dict(r)
                try:
                    d["alanlar"] = _json.loads(d.get("alanlar_json") or '[["Değer", "sayısal"]]')
                except Exception:
                    d["alanlar"] = [["Değer", "sayısal"]]
                return d
        except Exception:
            return None

    @classmethod
    def katalog_ozeti(cls) -> dict[str, Any]:
        b = cls.baglam()
        katalog = b["TEST_KATALOGU"]
        tum = cls.tum_testler()
        kaynaklar = cls.kaynakca_listesi()
        kategoriler = list(
            dict.fromkeys(list(katalog.keys()) + [t["kategori"] for t in tum if t.get("kategori")])
        )
        gruplar = list(b["BRANS_GRUBU_PROFILLERI"]["gruplar"].keys())
        return {
            "surum": b.get("SURUM", "1.0"),
            "kategoriler": kategoriler,
            "toplam_kategori": len(kategoriler),
            "toplam_test": len(tum),
            "brans_gruplari": gruplar,
            "toplam_brans_grubu": len(gruplar),
            "toplam_kaynakca": len(kaynaklar),
        }

    @classmethod
    def tum_testler(cls, arama: str = "", kategori: str = "") -> list[dict[str, Any]]:
        import json as _json

        b = cls.baglam()
        silinen_set: set[str] = set()
        ozel_satirlar: list[dict[str, Any]] = []
        try:
            with veritabani.baglanti() as con:
                silinen_set = {
                    r["test_adi"] for r in con.execute("SELECT test_adi FROM silinen_testler").fetchall()
                }
                ozel_satirlar = [
                    dict(r)
                    for r in con.execute("SELECT * FROM ozel_testler ORDER BY olusturma_zamani DESC").fetchall()
                ]
        except Exception:
            pass

        ozel_adlar = {o["test_adi"] for o in ozel_satirlar}
        sonuc = []

        # 1. Süper Admin tarafından eklenen özel testler
        for o in ozel_satirlar:
            test_adi = o["test_adi"]
            if test_adi in silinen_set:
                continue
            kat = o.get("kategori") or "Özel Protokoller"
            nitelik = o.get("nitelik") or "Genel"
            if kategori and kat != kategori:
                continue
            if (
                arama
                and arama.lower() not in test_adi.lower()
                and arama.lower() not in kat.lower()
                and arama.lower() not in nitelik.lower()
            ):
                continue
            try:
                alanlar = _json.loads(o.get("alanlar_json") or '[["Değer", "sayısal"]]')
            except Exception:
                alanlar = [["Değer", "sayısal"]]
            sonuc.append(
                {
                    "test_adi": test_adi,
                    "kisa_ad": o.get("kisa_ad") or test_adi[:22],
                    "kategori": kat,
                    "batarya": o.get("batarya") or "Özel Protokol",
                    "brans": o.get("brans") or "Genel",
                    "nitelik": nitelik,
                    "bilesen": o.get("bilesen") or "Atletik Performans",
                    "hareket_tipi": o.get("hareket_tipi") or "otomatik",
                    "norm_var_mi": o.get("norm_medyan") is not None,
                    "alanlar": alanlar,
                    "aciklama": o.get("aciklama") or "",
                    "ozel_mi": True,
                }
            )

        # 2. Yerleşik katalog testleri (silinenler hariç)
        for t in b["katalog_testleri"]():
            test_adi = t["ad"]
            if test_adi in silinen_set or test_adi in ozel_adlar:
                continue
            kat = t.get("kategori", "")
            yol = t.get("yol") or ("", "", "")
            nitelik = b["test_niteligi"](test_adi) or ""
            if kategori and kat != kategori:
                continue
            if (
                arama
                and arama.lower() not in test_adi.lower()
                and arama.lower() not in kat.lower()
                and arama.lower() not in nitelik.lower()
            ):
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
                    "nitelik": nitelik,
                    "bilesen": b["test_bileseni"](test_adi),
                    "norm_var_mi": bool(b["test_norm_var_mi"](test_adi)),
                    "alanlar": bilgi.get("alanlar", []),
                    "aciklama": bilgi.get("aciklama", ""),
                    "ozel_mi": False,
                }
            )
        return sonuc

    @classmethod
    def test_svg_html(cls, test_adi: str, buyuk: bool = True) -> dict[str, Any]:
        from api.services.svg_sahne_motoru import gelismis_test_sahnesi_uret

        b = cls.baglam()
        ozel = cls._ozel_test_getir(test_adi)
        return gelismis_test_sahnesi_uret(b, test_adi, ozel_test=ozel)

    @classmethod
    def kaynakca_listesi(cls) -> list[dict[str, Any]]:
        b = cls.baglam()
        kaynakca = b["KAYNAKCA"]
        silinen_set: set[str] = set()
        ozel_satirlar: list[dict[str, Any]] = []
        try:
            with veritabani.baglanti() as con:
                silinen_set = {
                    r["anahtar"] for r in con.execute("SELECT anahtar FROM silinen_kaynakcalar").fetchall()
                }
                ozel_satirlar = [
                    dict(r)
                    for r in con.execute(
                        "SELECT * FROM ozel_kaynakcalar ORDER BY olusturma_zamani DESC"
                    ).fetchall()
                ]
        except Exception:
            pass

        liste: list[dict[str, Any]] = []
        for o in ozel_satirlar:
            if o["anahtar"] not in silinen_set:
                liste.append(
                    {
                        "anahtar": o["anahtar"],
                        "metin": o["metin"],
                        "kaynak": o["metin"],
                        "ozel_mi": True,
                    }
                )

        if isinstance(kaynakca, dict):
            for k, v in kaynakca.items():
                if str(k) in silinen_set:
                    continue
                if isinstance(v, dict):
                    liste.append({"anahtar": str(k), **v, "ozel_mi": False})
                else:
                    liste.append({"anahtar": str(k), "metin": str(v), "kaynak": str(v), "ozel_mi": False})
        else:
            for i, k in enumerate(kaynakca):
                anahtar = f"ref-{i + 1}"
                if anahtar in silinen_set or str(k) in silinen_set:
                    continue
                liste.append({"anahtar": anahtar, "indeks": i + 1, "metin": str(k), "kaynak": str(k), "ozel_mi": False})
        return liste

    @classmethod
    def test_degerlendir(
        cls, test_adi: str, degisken: str, deger: float, yas: float, cinsiyet: str
    ) -> dict[str, Any]:
        import math as _math

        ozel = cls._ozel_test_getir(test_adi)
        if ozel and ozel.get("norm_medyan") is not None and ozel.get("norm_s"):
            m = float(ozel["norm_medyan"])
            s = max(float(ozel["norm_s"]), 0.01)
            l_val = float(ozel.get("norm_l") if ozel.get("norm_l") is not None else 1.0)
            yon = str(ozel.get("yon") or "yuksek_iyi")
            if m > 0 and deger > 0:
                if abs(l_val) > 1e-6:
                    z_ham = (((deger / m) ** l_val) - 1.0) / (l_val * s)
                else:
                    z_ham = _math.log(deger / m) / s
            else:
                z_ham = (deger - m) / (m * s if m else s)
            z_perf = -z_ham if yon == "dusuk_iyi" else z_ham
            z_perf = round(max(-4.0, min(4.0, z_perf)), 2)
            pct_sayi = round(0.5 * (1.0 + _math.erf(z_perf / _math.sqrt(2.0))) * 100.0, 1)
            alt_sinir = round(max(0.0, m * (1.0 - 3.0 * s)), 2)
            ust_sinir = round(m * (1.0 + 3.0 * s), 2)
            return {
                "test_adi": test_adi,
                "degisken": degisken,
                "deger": deger,
                "yas": yas,
                "cinsiyet": cinsiyet,
                "persentil": {"persentil": pct_sayi, "persentil_aralik": f"P{int(round(pct_sayi))}"},
                "z_skoru": {"z": round(z_ham, 2), "z_performans": z_perf, "yontem": "Cole & Green LMS (Özel Norm)"},
                "norm_sonuc": {"durum": "Normal" if abs(z_perf) <= 2.0 else "Uç Değer"},
                "esik_kontrolu": {"uyari_var_mi": abs(z_perf) > 3.0},
                "makul_aralik": [alt_sinir, ust_sinir],
            }

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
            return html.replace("Ölçüt", "Performetre")

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
            return html.replace("Ölçüt", "Performetre")

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
