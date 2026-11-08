"""
Uygulama ve paket ad alanı yükleyici: Streamlit çalıştırmadan veri/ ve olcut/ modüllerindeki tüm sabitleri ve
fonksiyonları katman sırasına göre tek bir sözlükte (NS) toplar; regresyon (reg.py), derin eşitlik (esitlik.py)
ve test fikstürleri (tests/conftest.py) tarafından kullanılır.
"""
import ast
import importlib
import io
import math as _math
import os
import sys


class K:
    def __init__(s, *a, **k): pass
    def __getattr__(s, n): return K()
    def __call__(s, *a, **k): return K()
    def __enter__(s): return K()
    def __exit__(s, *a): return False
    def __iter__(s): return iter([K() for _ in range(8)])
    def __bool__(s): return False


for m in ("streamlit", "plotly", "plotly.graph_objects", "plotly.express", "streamlit.components.v1"):
    sys.modules.setdefault(m, K())


VERI_MODULLERI = (
    "veri.normlar_kategorik",
    "veri.normlar_tsyt",
    "veri.brans_profilleri",
    "veri.metinler",
)

OLCUT_MODULLERI = (
    "olcut.ortak",
    "olcut.tema",
    "olcut.esik",
    "olcut.katalog_islemleri",
    "olcut.gorseller.cizim",
    "olcut.gorseller.hareketler",
    "olcut.gorseller.sahneler",
    "olcut.norm",
    "olcut.analiz",
    "olcut.kayit",
    "olcut.raporlar",
    "olcut.oneri",
    "olcut.bilesenler",
    "olcut.sayfalar.ana_sayfa",
    "olcut.sayfalar.test_oturumu",
    "olcut.sayfalar.nitelik",
    "olcut.sayfalar.sonuclar",
)


def modulleri_yukle(kl, ns=None):
    """kl altındaki veri/ ve olcut/ modüllerinde tanımlanan tüm adları katman sırasına göre ns'ye yükler."""
    if ns is None:
        ns = {}
    if not os.path.isdir(os.path.join(kl, "olcut")):
        return ns
    if kl in sys.path:
        sys.path.remove(kl)
    sys.path.insert(0, kl)
    ns.setdefault("_math", _math)
    for m_ad in VERI_MODULLERI + OLCUT_MODULLERI:
        yol = os.path.join(kl, *m_ad.split(".")) + ".py"
        if not os.path.exists(yol):
            continue
        mod = importlib.import_module(m_ad)
        agac = ast.parse(io.open(yol, encoding="utf-8").read())
        for d in agac.body:
            adlar = (
                [d.name]
                if isinstance(d, (ast.FunctionDef, ast.ClassDef))
                else [t.id for t in d.targets if isinstance(t, ast.Name)]
                if isinstance(d, ast.Assign)
                else []
            )
            for ad in adlar:
                if hasattr(mod, ad):
                    ns[ad] = getattr(mod, ad)
    # _TR_ASCII ve _AYRILMA_EKI gibi modül içi sabitleri uygulama öncesi durumla tam uyumlu tut
    ns.pop("SURUM", None)
    return ns


def yukle(dosya):
    kl = os.path.dirname(os.path.abspath(dosya))   # veri/ ve olcut/ paketleri uygulamanın yanında
    if kl in sys.path:
        sys.path.remove(kl)
    sys.path.insert(0, kl)
    s = io.open(dosya, encoding="utf-8").read()
    tree = ast.parse(s)
    son = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SAYFALAR":
            son = n.lineno
            break
    NS = {"__name__": "olcut"}
    modulleri_yukle(kl, NS)
    exec(compile("\n".join(s.splitlines()[: son - 1 if son else None]), "olcut", "exec"), NS)
    return NS


LEAF = ("protokol", "aciklama", "olcum", "birim", "degerlendirme")


def testler(NS):
    out = {}

    def yuru(d, yol):
        for k, v in d.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                if any(x in v for x in LEAF):
                    out[k] = " > ".join(yol)
                else:
                    yuru(v, yol + [k])

    yuru(NS["TEST_KATALOGU"], [])
    return out
