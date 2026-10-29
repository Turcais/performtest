"""
Sayfa görüntüsü: her menü sayfasını örnek veriyle (araclar/reg.py'nin 5 sporcusu + havuz) Streamlit AppTest'te açar ve
ekrandaki bütün öğeleri (tür + protobuf içeriği: metin, etiket, değer, seçenek, grafik tanımı) JSON'a döker.
Bölme Aşama 2'de sayfa kodu taşınmadan önce ve sonra alınan görüntüler birebir aynı olmalı.

    python araclar/sayfa_goruntusu.py UYGULAMA CIKTI.json

Dosyaya yazan eylem yapılmaz (yalnız açılış görüntüsü); veri geçici klasördedir.
"""
import ast, io, json, os, re, sys, tempfile

# reg kurulumu yukle.py'yi içe aktarır; o streamlit/plotly'yi kukla ile değiştirir (setdefault). Gerçekleri ÖNCE yükle.
import plotly.express, plotly.graph_objects, streamlit.components.v1  # noqa: E401,F401
from streamlit.testing.v1 import AppTest

uyg, cikti = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.dirname(uyg))   # streamlit run bunu kendisi yapar (bootstrap); AppTest yapmaz
kaynak = io.open(uyg, encoding="utf-8").read()
SAYFALAR = next(ast.literal_eval(n.value) for n in ast.parse(kaynak).body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SAYFALAR")

# reg.py'nin örnek verisi (aynı sporcular ve sonuçlar): veri kurulumu kısmı çalıştırılır, hesap kısmı değil
reg = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reg.py"), encoding="utf-8").read()
gecici = tempfile.mkdtemp(prefix="sayfa_goruntusu_")
eski_argv = sys.argv
sys.argv = ["reg.py", uyg, os.path.join(gecici, "veri.json")]
exec(compile(reg[:reg.index("g = yukle(uyg)")], "reg.py", "exec"), {"__name__": "reg_veri", "__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "reg.py")})
sys.argv = eski_argv                                        # reg kurulumu calis_veri/ klasörüne geçti (os.chdir)

def dok(dugum, derinlik=0, satirlar=None):
    satirlar = [] if satirlar is None else satirlar
    for c in (dugum.children.values() if isinstance(getattr(dugum, "children", None), dict) else ()):
        proto = getattr(c, "proto", None)
        metin = str(proto).strip().replace("\n", " | ") if proto is not None else ""
        metin = re.sub(r"/mock/media/[0-9a-f]+", "/mock/media/<ozet>", metin)   # xlsx içinde oluşturma zamanı var
        metin = re.sub(r"\$\$ID-[0-9a-f]+", "$$ID-<ozet>", metin)   # özet betik yolunu da içerir (başka klasördeki sürüm)
        satirlar.append(f"{'  ' * derinlik}{type(c).__name__}: {metin}")
        dok(c, derinlik + 1, satirlar)
    return satirlar


sonuc = {}
durumlar = [(p, {}) for p in SAYFALAR] + [                      # Sonuçlar: kart görünümü (çocuk, yetişkin) ve
    ("Sonuçları Görüntüle", {"sonuc_sporcu": "Ece K"}),          # ayrıntılı genel görünüm (tek sporcu süzgeci)
    ("Sonuçları Görüntüle", {"sonuc_sporcu": "Ali Y"}),
    ("Sonuçları Görüntüle", {"sonuc_sporcu": "Ali Y", "sonuc_ayrintili": True})]
for sayfa, ek in durumlar:
    at = AppTest.from_file(uyg, default_timeout=180)
    at.session_state["sayfa"] = sayfa
    for k, v in ek.items():
        at.session_state[k] = v
    at.run()
    ad = sayfa + ("" if not ek else " " + json.dumps(ek, ensure_ascii=False))
    sonuc[ad] = {"hata": [str(e.value)[:300] for e in at.exception], "oge": dok(at._tree)}
    print(f"{ad}: {len(sonuc[ad]['oge'])} öğe, {len(sonuc[ad]['hata'])} hata", flush=True)
json.dump(sonuc, io.open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
