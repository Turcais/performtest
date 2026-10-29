"""
Derin eşitlik: bir git sürümündeki uygulama ile çalışma kopyasındaki uygulamanın modül düzeyi sabitleri birebir aynı mı?

    python araclar/esitlik.py ESKI_SURUM [SABIT ...] [--akis]

ESKI_SURUM : git sürümü (ör. v101-38f, HEAD~1). O sürümdeki uygulama.py + veri/ geçici klasöre çıkarılıp yüklenir.
SABIT      : karşılaştırılacak adlar; verilmezse iki tarafta da olan bütün veri sabitleri (fonksiyon/sınıf/modül hariç).
--akis     : karşılaştırmadan sonra araclar/reg.py akışını çalıştırır ve bellekteki veri/ modüllerinin dosyadan taze
             okunanla hâlâ aynı olduğunu denetler (yerinde değişiklik bir sonraki Streamlit çalıştırmasına sızmasın).

Karşılaştırma katıdır: tür birebir (tuple ≠ list, int anahtar ≠ str anahtar, int ≠ float), sözlük anahtar SIRASI dahil,
NaN = NaN. Fark varsa ilk farkın yolu yazılır ve çıkış kodu 1 olur.
"""
import functools, io, os, runpy, subprocess, sys, tempfile, types

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "araclar"))
from yukle import yukle  # noqa: E402


def _veri_unut():
    for ad in [m for m in sys.modules if m == "veri" or m.startswith("veri.")]:
        del sys.modules[ad]


def _surum_cikar(surum, hedef):
    """git archive: o sürümdeki uygulama.py ve (varsa) veri/ klasörü hedefe."""
    dosyalar = subprocess.run(["git", "ls-tree", "-r", "--name-only", surum], cwd=KOK, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.split("\n")
    for d in [d for d in dosyalar if d == "uygulama.py" or d.startswith("veri/")]:
        icerik = subprocess.run(["git", "show", f"{surum}:{d}"], cwd=KOK, capture_output=True, check=True).stdout
        yol = os.path.join(hedef, *d.split("/"))
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        with open(yol, "wb") as f:
            f.write(icerik)
    return os.path.join(hedef, "uygulama.py")


def _yukle_yalitik(dosya, calisma):
    _veri_unut()
    eski = os.getcwd()
    os.chdir(calisma)                    # modül düzeyi kod dosya yazarsa proje klasörüne değil
    try:
        return yukle(dosya)
    finally:
        os.chdir(eski)


def _veri_mi(v):
    return not isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.ModuleType, type)) \
        and not callable(v)


def fark(a, b, yol="", sayac=None):
    """İlk farkın açıklaması ya da None. sayac[0]: karşılaştırılan düğüm sayısı."""
    if sayac is not None:
        sayac[0] += 1
    if type(a) is not type(b):
        return f"{yol or '<kök>'}: tür {type(a).__name__} ≠ {type(b).__name__}"
    if isinstance(a, dict):
        if list(a) != list(b):
            eksik, fazla = [k for k in a if k not in b], [k for k in b if k not in a]
            return (f"{yol or '<kök>'}: anahtarlar farklı (eksik {eksik[:3]}, fazla {fazla[:3]})" if eksik or fazla
                    else f"{yol or '<kök>'}: anahtar sırası farklı")
        for k in a:
            if type(k) is not type(next(x for x in b if x == k)):
                return f"{yol}[{k!r}]: anahtar türü farklı"
            f = fark(a[k], b[k], f"{yol}[{k!r}]", sayac)
            if f:
                return f
        return None
    if isinstance(a, (list, tuple)):
        if len(a) != len(b):
            return f"{yol or '<kök>'}: uzunluk {len(a)} ≠ {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            f = fark(x, y, f"{yol}[{i}]", sayac)
            if f:
                return f
        return None
    if isinstance(a, (set, frozenset)):
        return None if a == b and sorted(map(repr, a)) == sorted(map(repr, b)) else f"{yol}: küme farklı"
    if isinstance(a, float) and a != a:
        return None if b != b else f"{yol}: NaN ≠ {b!r}"
    if isinstance(a, functools.partial):         # iki yüklemede ayrı nesneler: işlev adı + argümanlar
        return (fark(a.func, b.func, f"{yol}.func", sayac) or fark(a.args, b.args, f"{yol}.args", sayac)
                or fark(a.keywords, b.keywords, f"{yol}.keywords", sayac))
    if isinstance(a, (types.FunctionType, types.BuiltinFunctionType, type)):
        return None if a.__qualname__ == b.__qualname__ else f"{yol}: {a.__qualname__} ≠ {b.__qualname__}"
    return None if a == b else f"{yol}: {a!r:.80} ≠ {b!r:.80}"


def _kod_nesneleri(nesne):
    """Fonksiyon/sınıf → içindeki bütün kod nesneleri (iç fonksiyonlar, yöntemler, özellikler dahil)."""
    kodlar = []
    if isinstance(nesne, type):
        for v in vars(nesne).values():
            v = getattr(v, "__func__", v)
            for f in ((v.fget, v.fset, v.fdel) if isinstance(v, property) else (v,)):
                if isinstance(f, types.FunctionType):
                    kodlar.append((f.__globals__, f.__code__))
    elif isinstance(nesne, types.FunctionType):
        kodlar.append((nesne.__globals__, nesne.__code__))
    sonuc = []
    while kodlar:
        g, k = kodlar.pop()
        sonuc.append((g, k))
        kodlar += [(g, c) for c in k.co_consts if isinstance(c, types.CodeType)]
    return sonuc


def modul_tutarliligi(ns):
    """
    Bölme Aşama 2: olcut/ modüllerindeki her fonksiyonun okuduğu küresel adlar, uygulama ad alanındaki SON değerle
    aynı nesne mi (ham/son hâl tuzağı: ör. HFZ eklenmemiş TEST_KATALOGU)? Modülde tanımsız ad = NameError riski.
    Döner: (denetlenen ad sayısı, sorun listesi).
    """
    import builtins, dis
    sorun, sayi, gorulen = [], 0, set()
    for ad, nesne in ns.items():
        mod = getattr(nesne, "__module__", "") or ""
        if not (isinstance(nesne, (types.FunctionType, type)) and mod.startswith("olcut.")) or id(nesne) in gorulen:
            continue
        gorulen.add(id(nesne))
        for g, kod in _kod_nesneleri(nesne):
            for ins in dis.get_instructions(kod):
                if ins.opname not in ("LOAD_GLOBAL", "LOAD_NAME"):
                    continue
                isim = ins.argval
                if isim in g:
                    if isim in ns:
                        sayi += 1
                        if g[isim] is not ns[isim] and fark(g[isim], ns[isim]):
                            sorun.append(f"{mod}.{kod.co_qualname}: '{isim}' modülde uygulamadakinden farklı")
                elif not hasattr(builtins, isim):
                    sorun.append(f"{mod}.{kod.co_qualname}: '{isim}' modülde tanımsız (NameError)")
    return sayi, sorted(set(sorun))


def _taze_veri(klasor):
    """veri/*.py dosyalarını sys.modules'a dokunmadan, her biri yeni bir ad alanında çalıştırır."""
    sonuc = {}
    vk = os.path.join(klasor, "veri")
    for ad in sorted(os.listdir(vk)) if os.path.isdir(vk) else []:
        if ad.endswith(".py") and ad != "__init__.py":
            ns = {}
            with io.open(os.path.join(vk, ad), encoding="utf-8") as f:
                exec(compile(f.read(), ad, "exec"), ns)
            sonuc[f"veri.{ad[:-3]}"] = {k: v for k, v in ns.items() if not k.startswith("__")}
    return sonuc


def main(arg):
    akis = "--akis" in arg
    arg = [a for a in arg if a != "--akis"]
    if not arg:
        print(__doc__)
        return 2
    surum, adlar = arg[0], arg[1:]
    gecici = tempfile.mkdtemp(prefix="esitlik_")
    os.makedirs(os.path.join(gecici, "eski"))
    os.makedirs(os.path.join(gecici, "calisma"))
    eski = _yukle_yalitik(_surum_cikar(surum, os.path.join(gecici, "eski")), os.path.join(gecici, "calisma"))
    yeni = _yukle_yalitik(os.path.join(KOK, "uygulama.py"), os.path.join(gecici, "calisma"))
    if not adlar:
        adlar = sorted(k for k in eski if not k.startswith("__") and _veri_mi(eski[k]))
    hata = 0
    print(f"Karşılaştırma: {surum} ↔ çalışma kopyası, {len(adlar)} sabit")
    for ad in adlar:
        if ad not in eski or ad not in yeni:
            print(f"  YOK   {ad}: {'eskide' if ad not in eski else 'yenide'} tanımlı değil")
            hata += 1
            continue
        sayac = [0]
        f = fark(eski[ad], yeni[ad], "", sayac)
        print(f"  {'FARK' if f else 'AYNI'}  {ad} ({type(eski[ad]).__name__}, {sayac[0]} düğüm){': ' + f if f else ''}")
        hata += bool(f)
    yeni_adlar = sorted(k for k in yeni if k not in eski and not k.startswith("__") and _veri_mi(yeni[k]))
    if yeni_adlar:
        print(f"  (yalnız yenide olan veri adları: {', '.join(yeni_adlar)})")
    sayi, sorunlar = modul_tutarliligi(yeni)
    print(f"Modül tutarlılığı: olcut/ fonksiyonlarının okuduğu {sayi} küresel ad, {len(sorunlar)} sorun")
    for s in sorunlar:
        print("  SORUN", s)
    hata += len(sorunlar)
    if akis:
        _veri_unut()
        eski_argv, eski_cwd = sys.argv, os.getcwd()
        sys.argv = ["reg.py", os.path.join(KOK, "uygulama.py"), os.path.join(gecici, "akis.json")]
        try:
            runpy.run_path(os.path.join(KOK, "araclar", "reg.py"), run_name="__main__")
        finally:
            sys.argv = eski_argv
            os.chdir(eski_cwd)
        taze = _taze_veri(KOK)
        print(f"Akış sonrası yerinde değişiklik denetimi ({len(taze)} veri modülü):")
        for mod, degerler in taze.items():
            bellek = sys.modules.get(mod)
            for ad, v in degerler.items():
                f = fark(v, getattr(bellek, ad, None)) if bellek else "modül yüklenmemiş"
                print(f"  {'FARK' if f else 'AYNI'}  {mod}.{ad}{': ' + f if f else ''}")
                hata += bool(f)
    print("SONUÇ:", "hepsi aynı" if not hata else f"{hata} fark")
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
