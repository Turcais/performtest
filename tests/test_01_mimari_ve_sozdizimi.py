"""
Mimari, sözdizimi, veri katmanı saflığı (test_44a) ve olcut/ katman sırası (test_45a) denetimleri.
"""
import ast
import collections
import glob
import math
import os
import re
import types

import pytest

from tests.conftest import *  # noqa: F401,F403

# ════════════════════════════════════════════════════════════
# 1. Sözdizimi
# ════════════════════════════════════════════════════════════
def test_01_sozdizimi(kaynak):
    """Dosya hatasız ayrıştırılıyor."""
    try:
        ast.parse(kaynak)
    except SyntaxError as hata:
        pytest.fail(f"Sözdizimi hatası: satır {hata.lineno}: {hata.msg}")


# ════════════════════════════════════════════════════════════
# 2. Tekrarlanan sözlük anahtarı
# (12 tekrar bulunmuştu; Trunk Lift notu ve Yo-Yo üst sınırı böyle kaybolmuştu:
#  Python'da aynı anahtar ikinci kez yazılınca ilki sessizce silinir.)
# ════════════════════════════════════════════════════════════
def test_02_tekrarlanan_anahtar_yok(agac):
    sorunlar = []
    for dugum in agac.body:
        if not isinstance(dugum, (ast.Assign, ast.AnnAssign)):
            continue
        hedef = ast.unparse(dugum.targets[0] if isinstance(dugum, ast.Assign) else dugum.target)
        for d in ast.walk(dugum):
            if not isinstance(d, ast.Dict):
                continue
            satirlar = collections.defaultdict(list)
            for k in d.keys:
                if isinstance(k, ast.Constant):
                    satirlar[k.value].append(k.lineno)
            for anahtar, sat in satirlar.items():
                if len(sat) > 1:
                    sorunlar.append(f"{hedef}: {anahtar!r} — satırlar {sat}")
    assert not sorunlar, "Tekrarlanan anahtar (ilk tanım sessizce kaybolur):" + _ozet(sorunlar)




def test_00_yukleyici_gerekli_tanimlari_buldu(app):
    gerekli = ["TEST_KATALOGU", "NORMATIF_YAS", "NORMATIF_TEST", "NORMATIF", "BOLUM_BASLIKLARI",
               "protokol_formatla", "protokol_ozet_cikar", "_uygulama_araligi", "yas_z_skoru",
               "brans_grubu_eslestir", "BRANS_GRUBU_PROFILLERI", "ESLESTIRME_DEGISKENLERI",
               "KAYNAKCA", "KAYNAKCA_SINIFLAR"]
    eksik = [ad for ad in gerekli if ad not in app]
    assert not eksik, (f"Denetim için gerekli tanımlar yüklenemedi: {eksik}. "
                       f"Atlanan modül düzeyi satırlar: {app['_atlanan'][:5]}")


def test_00b_modul_duzeyinde_gizli_degisiklik_yok(agac):
    """
    Denetim yalnızca atamaları ve fonksiyonları çalıştırır. Modül düzeyinde 'SOZLUK.update(...)' gibi
    bir ifade, uygulamada çalışır ama denetimde görünmez (TSYT normları bir kez böyle gözden kaçtı).
    Bu tür değişiklikler atama olarak yazılmalı: SOZLUK = {**SOZLUK, **EK}.
    """
    sorunlar = []
    for dugum in agac.body:
        if (isinstance(dugum, ast.Expr) and isinstance(dugum.value, ast.Call)
                and isinstance(dugum.value.func, ast.Attribute)
                and dugum.value.func.attr in ("update", "append", "extend", "insert", "setdefault", "pop")
                and isinstance(dugum.value.func.value, ast.Name) and dugum.value.func.value.id.isupper()):
            sorunlar.append(f"satır {dugum.lineno}: {ast.unparse(dugum)[:80]}")
    assert not sorunlar, "Denetimin göremediği modül düzeyi değişiklik:" + _ozet(sorunlar)



# ════════════════════════════════════════════════════════════
# 44. Bölme Aşama 1: veri/ modülleri yalnız sabit değer
# ════════════════════════════════════════════════════════════
_VERI_KLASOR = os.path.join(os.path.dirname(DOSYA), "veri")
_VERI_SERBEST = (ast.Constant, ast.Dict, ast.List, ast.Tuple, ast.Set, ast.Load)


def _veri_modulleri():
    if not os.path.isdir(_VERI_KLASOR):
        return []
    return sorted(os.path.join(_VERI_KLASOR, d) for d in os.listdir(_VERI_KLASOR)
                  if d.endswith(".py") and d != "__init__.py")


def test_44a_veri_modulleri_yalniz_sabit(agac):
    """
    veri/*.py: modül düzeyinde yalnız açıklama ve atama; değerlerde yalnız sabit, sözlük, liste, demet, küme,
    eksi sayı, metin birleştirme (+) ve AYNI modülde daha önce tanımlanmış ad (ör. TSYT_KAYNAK + "…").
    Çağrı, lambda, içe aktarma, f-string yok. Uygulama her modülü içe aktarır ve hiçbir veri adını yeniden
    literal olarak tanımlamaz (iki kopya olmasın).
    """
    sorun, tum_adlar = [], {}
    for yol in _veri_modulleri():
        m = ast.parse(open(yol, encoding="utf-8").read())
        tanimli = set()
        for i, d in enumerate(m.body):
            if i == 0 and isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant):
                continue
            if not (isinstance(d, ast.Assign) and len(d.targets) == 1 and isinstance(d.targets[0], ast.Name)):
                sorun.append(f"{os.path.basename(yol)}:{d.lineno} atama değil ({type(d).__name__})")
                continue
            for x in ast.walk(d.value):
                if isinstance(x, _VERI_SERBEST):
                    continue
                if isinstance(x, ast.UnaryOp) and isinstance(x.op, ast.USub) and isinstance(x.operand, ast.Constant):
                    continue
                if isinstance(x, ast.USub) or isinstance(x, ast.Add):
                    continue
                if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Add):
                    continue
                if isinstance(x, ast.Name) and x.id in tanimli:
                    continue
                sorun.append(f"{os.path.basename(yol)}:{x.lineno} izin verilmeyen {type(x).__name__}")
            tanimli.add(d.targets[0].id)
        tum_adlar[os.path.basename(yol)[:-3]] = tanimli
    assert not sorun, sorun
    ice = {(d.module, a.name) for d in agac.body if isinstance(d, ast.ImportFrom) and (d.module or "").startswith("veri.")
           for a in d.names}
    for modul, adlar in tum_adlar.items():
        assert any(m == f"veri.{modul}" for m, _ in ice), f"veri/{modul}.py içe aktarılmıyor"
    kod = [d for y in _kaynak_dosyalari(veri=False) for d in ast.parse(_oku(y)).body]   # uygulama + olcut
    literal = {d.targets[0].id for d in kod if isinstance(d, ast.Assign) and len(d.targets) == 1
               and isinstance(d.targets[0], ast.Name) and isinstance(d.value, (ast.Dict, ast.List, ast.Tuple, ast.Constant))
               and not any(isinstance(x, (ast.Name, ast.Call)) for x in ast.walk(d.value))}   # {**X, …} literal değil
    iki_kez = sorted(literal & set().union(*tum_adlar.values())) if tum_adlar else []
    assert not iki_kez, f"Hem veri/ hem uygulama.py'de literal: {iki_kez}"


# ════════════════════════════════════════════════════════════
# 45. Bölme Aşama 2: olcut/ paketinin katman sırası (döngüsel bağımlılık yok)
# ════════════════════════════════════════════════════════════
_OLCUT_KATMAN = ["ortak", "disa_aktarma", "tema", "esik", "katalog_islemleri", "gorseller.cizim", "gorseller.hareketler",
                 "gorseller.sahneler", "norm", "analiz", "kayit", "duzeltme", "kulup", "raporlar", "oneri", "karsilastirma", "kulup_raporu", "bilesenler", "sayfalar"]


def _olcut_katmani(modul):
    ad = modul[len("olcut."):]
    return next((i for i, k in enumerate(_OLCUT_KATMAN) if ad == k or ad.startswith(k + ".")), None)


def test_45a_olcut_katman_sirasi():
    """
    Her olcut modülü yalnız kendinden AŞAĞIDAKİ katmanları içe aktarır (sayfalar birbirini içe aktarmaz);
    hiçbir modül uygulama.py'yi içe aktarmaz. Yeni bir modül önce _OLCUT_KATMAN'a yazılmalı.
    """
    kok = os.path.dirname(DOSYA)
    sorun = []
    for yol in _kaynak_dosyalari(veri=False)[1:]:
        goreli = os.path.relpath(yol, kok)[:-3].replace(os.sep, ".")
        modul = goreli[:-len(".__init__")] if goreli.endswith(".__init__") else goreli
        if modul in ("olcut", "olcut.gorseller", "olcut.sayfalar"):
            continue
        ben = _olcut_katmani(modul)
        if ben is None:
            sorun.append(f"{modul}: _OLCUT_KATMAN'da yok")
            continue
        for d in ast.walk(ast.parse(_oku(yol))):
            hedefler = ([a.name for a in d.names] if isinstance(d, ast.Import)
                        else [d.module or ""] if isinstance(d, ast.ImportFrom) else [])
            for h in hedefler:
                if h.split(".")[0] == "uygulama":
                    sorun.append(f"{modul}: uygulama'yı içe aktarıyor")
                elif h.startswith("olcut."):
                    o = _olcut_katmani(h)
                    if o is None or o >= ben:
                        sorun.append(f"{modul} → {h}: katman sırasına aykırı")
    assert not sorun, sorun



