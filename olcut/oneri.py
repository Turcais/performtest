"""
Öneri motoru (Paket 33, Streamlit'siz): ana sayfanın 'şimdi şunu yap' önerileri, çalışma durumu, yarım
batarya, sıra birleştirme, özet kartları.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import pandas as pd
from datetime import date
from olcut.analiz import KENDI_DEGISIM_YASI
from olcut.gorseller.sahneler import TEST_GORSELSIZ
from olcut.katalog_islemleri import (
    TEST_KATALOGU, batarya_kisa, batarya_yas_araligi, kanonik_test, katalog_bataryalari, test_bilgisi,
    test_kisa)
from olcut.kayit import GRUP_KOLON, TOPLU_GIRIS_DISI, calisma_oturum_adi, calisma_sporculari, calismalar_oku
from olcut.ortak import DOGUM_KOLON, _girildi, _tablo_guvenli, _yas_degeri, ayar_oku, ayar_yaz, tam_yas, tarih_coz
from olcut.tema import b, renk_css


YON_TSYT = ("Türkiye Sportif Yetenek Modeli (TSYT)", "TSYT Bataryası — 7-11 Yaş (GSB)")


YON_TSYT_YAS = (7, 11)


YON_LISTE_SINIRI = 5                 # ekranda adıyla gösterilen satır; fazlası katlanır


# Yarım batarya eşiği (Paket 32) — üçü birden: testlerin en az yarısı yapılmış, bataryadaki son ölçüm 6 haftadan
# eski değil, bataryanın yas_araligi sporcunun yaşını kapsıyor (aralık None ise bu şart aranmaz).
YON_YARIM_ORAN = 0.5


YON_YARIM_GUN = 42


YON_SUSTUR_ANAHTAR = "yarim_susturulan"   # ayarlar.json: [[sporcu, batarya], …] — "Bu bataryayı bitirmeyeceğim"


def ilgi_eki(ad):
    """Türkçe ilgi eki ('Deniz Aydın' → 'Deniz Aydın’ın', 'Ali Bir' → 'Ali Bir’in', 'Ece' → 'Ece’nin')."""
    ad = str(ad).strip()
    unluler = {"a": "ı", "ı": "ı", "A": "ı", "I": "ı", "e": "i", "i": "i", "E": "i", "İ": "i",
               "o": "u", "u": "u", "O": "u", "U": "u", "ö": "ü", "ü": "ü", "Ö": "ü", "Ü": "ü"}
    son = next((unluler[c] for c in reversed(ad) if c in unluler), "i")
    return f"{ad}’{'n' if ad[-1:] in unluler else ''}{son}n"


def yarim_susturulanlar():
    """Susturulan (sporcu, batarya) çiftleri — ayarlar.json'dan; dosya yoksa/bozuksa boş."""
    v = ayar_oku().get(YON_SUSTUR_ANAHTAR, [])
    return {(str(x[0]), str(x[1])) for x in v if isinstance(x, (list, tuple)) and len(x) == 2} if isinstance(v, list) else set()


def yarim_sustur(sporcu, batarya):
    """"Bu bataryayı bitirmeyeceğim": o sporcu + batarya bir daha yarım sayılmaz (başka sporcuyu etkilemez)."""
    s = yarim_susturulanlar() | {(str(sporcu), str(batarya))}
    ayar_yaz(YON_SUSTUR_ANAHTAR, sorted([list(x) for x in s]))


def yonlendirme_durumu(df_sporcu, df_test, katalog=None, bugun=None, susturulan=()):
    """
    Veride ne var: sporcu sayısı, sonuç sayısı, yarım kalan ve tamamlanan bataryalar (sporcu adıyla).
    Bütün testleri yapılmış batarya tamamdır. Eksik testi olan batarya yalnız ÜÇ şart birden sağlanırsa yarım
    sayılır (Paket 32 — tek test bataryayı "başlatmaz"): testlerin en az yarısı yapılmış; bataryadaki son ölçüm
    YON_YARIM_GUN günden eski değil; bataryanın yas_araligi sporcunun yaşını kapsıyor (None ise aranmaz; yaş ya da
    tarih bilinmiyorsa şart sağlanmış sayılmaz). susturulan: {(sporcu, batarya)} — o çift yarım sayılmaz.
    Tahmin yok: yalnız kayıtlı sonuçlar sayılır.
    """
    bugun = tarih_coz(bugun) or date.today()
    susturulan = {tuple(x) for x in susturulan}
    sp = _tablo_guvenli(df_sporcu, ["Ad", "Soyad", "Yaş"])
    ts = _tablo_guvenli(df_test, ["Sporcu", "Test", "Tarih"])
    adlar, yaslar = [], {}
    for _, r in sp.iterrows():
        ad = f"{'' if pd.isna(r['Ad']) else r['Ad']} {'' if pd.isna(r['Soyad']) else r['Soyad']}".strip()
        if ad and ad not in adlar:
            adlar.append(ad)
            y = tam_yas(r.get(DOGUM_KOLON), bugun)            # doğum tarihi varsa bugünkü yaş, yoksa profil yaşı
            if y is None:
                try:
                    y = None if pd.isna(r["Yaş"]) or str(r["Yaş"]).strip() == "" else int(float(r["Yaş"]))
                except (TypeError, ValueError):
                    y = None
            yaslar[ad] = y
    ts = ts[ts["Sporcu"].astype(str).isin(adlar)] if adlar else ts.iloc[0:0]
    yapilan = {a: set(ts.loc[ts["Sporcu"].astype(str) == a, "Test"].astype(str)) for a in adlar}
    yarim, tamam = [], []
    for (kat, bat), testler in katalog_bataryalari(katalog).items():
        ya = batarya_yas_araligi(kat, bat, katalog)
        for a in adlar:
            if not yapilan[a] & set(testler):
                continue
            eksik = [t for t in testler if t not in yapilan[a]]
            kayit = {"sporcu": a, "kategori": kat, "batarya": bat, "eksik": eksik, "toplam": len(testler)}
            if not eksik:
                tamam.append(kayit)
                continue
            satir = ts[(ts["Sporcu"].astype(str) == a) & ts["Test"].astype(str).isin(testler)]
            tarihler = [d_ for d_ in (tarih_coz(x) for x in satir["Tarih"]) if d_ is not None]
            son = max(tarihler) if tarihler else None
            yas = yaslar.get(a)
            if ((len(testler) - len(eksik)) >= YON_YARIM_ORAN * len(testler)            # a) en az yarısı
                    and son is not None and (bugun - son).days <= YON_YARIM_GUN          # b) son ölçüm ≤ 6 hafta
                    and (ya is None or (yas is not None and ya[0] <= yas <= ya[1]))     # c) yaş aralıkta
                    and (a, bat) not in susturulan):
                yarim.append(dict(kayit, son_olcum=son))
    if not adlar:
        durum = "sporcu_yok"
    elif ts.empty:
        durum = "sonuc_yok"
    else:
        durum = "sonuc_var"
    return {"durum": durum, "sporcular": adlar, "sonuc_sayisi": int(len(ts)),
            "sonucsuz": [a for a in adlar if not yapilan[a]], "yarim": yarim, "tamam": tamam}


def yarim_cumlesi(k):
    """'Deniz Aydın’ın TSYT bataryasında 2 test eksik: 20m Sürat, Mekik Koşusu'"""
    return (f"{ilgi_eki(k['sporcu'])} {batarya_kisa(k['batarya'])} bataryasında {len(k['eksik'])} test eksik: "
            + ", ".join(test_kisa(t, k["batarya"]) for t in k["eksik"]))


def tamam_cumlesi(k):
    return f"{ilgi_eki(k['sporcu'])} {batarya_kisa(k['batarya'])} bataryası tamam ({k['toplam']} test)."


ONERI_BRANS_YASI = 11                 # bu yaşın altında branşa özgü öneri yapılmaz (temel dönem)


ONERI_TARAMA_ONCELIK = (YON_TSYT[1],)  # 7-11 yaş: TSYT önce (aralığı yaşı kapsıyorsa)


# Sporcu Girişi'ndeki spor dalı → katalogdaki branş rafı. Karşılığı olmayan dal (ör. Bisiklet, Golf) burada yok:
# 3. kural o sporcu için atlanır (boş liste gösterilmez). Atletizmde katalog rafı sürat/güç testleridir: yalnız Sprint.
SPOR_DALI_BRANS = {
    "Güreş (Serbest)": "Güreş", "Güreş (Grekoromen)": "Güreş", "Judo": "Judo", "Karate": "Karate",
    "Taekwondo": "Taekwondo", "Kickboks": "Kickboks", "Muay Thai": "Muay Thai", "Boks": "Boks",
    "Jiujitsu (BJJ)": "BJJ (Jiujitsu)", "Sambo": "Sambo", "MMA": "MMA",
    "Futbol": "Futbol", "Basketbol": "Basketbol", "Voleybol": "Voleybol", "Hentbol": "Hentbol", "Rugbi": "Rugby",
    "Buz Hokeyi": "Buz Hokeyi", "Su Topu": "Su Topu",
    "Atletizm (Sprint)": "Atletizm", "Yüzme": "Yüzme", "Kürek": "Kürek", "Kano/Kayak": "Kano/Kayak",
    "Halter": "Halter", "Jimnastik": "Jimnastik", "Tenis": "Tenis", "Masa Tenisi": "Masa Tenisi",
    "Badminton": "Badminton", "Squash": "Squash",
}


def kayit_edilebilir(test):
    """Testin değişkeni var mı (sonucu kaydedilebilir mi)."""
    return bool((test_bilgisi(test) or {}).get("degiskenler"))


def brans_rafi(dal, katalog=None):
    """Spor dalının katalog rafı → (alt, branş, [raftaki test adları]) ya da None."""
    katalog = TEST_KATALOGU if katalog is None else katalog
    b = SPOR_DALI_BRANS.get(str(dal).strip())
    for alt, v in katalog.get("Branşa Özgü Testler", {}).items():
        if not str(alt).startswith("_") and isinstance(v, dict) and isinstance(v.get(b), dict):
            return alt, b, [t for t, tv in v[b].items() if not t.startswith("_") and isinstance(tv, dict)]
    return None


def _sporcu_yasi(r, bugun):
    y = tam_yas(r.get(DOGUM_KOLON), bugun)
    if y is None:
        try:
            v = r.get("Yaş")
            y = None if v is None or pd.isna(v) or str(v).strip() == "" else int(float(v))
        except (TypeError, ValueError):
            y = None
    return y


def sayi_iyelik(n):
    """Rakamla yazılan sayının iyelik eki: 1'i, 2'si, 4'ü, 6'sı, 9'u, 10'u, 20'si, 40'ı, 100'ü, 0'ı."""
    n = int(n)
    birler = {1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}
    onlar = {1: "u", 2: "si", 3: "u", 4: "ı", 5: "si", 6: "ı", 7: "i", 8: "i", 9: "ı"}
    if n == 0:
        ek = "ı"
    elif n % 10:
        ek = birler[n % 10]
    elif n % 100:
        ek = onlar[(n // 10) % 10]
    elif n % 1000:
        ek = "ü"                                          # yüz
    else:
        ek = "i"                                          # bin
    return f"{n}'{ek}"


def _hafta_metni(gun):
    return "bu hafta" if gun < 7 else f"{gun // 7} hafta önce"


def oneri_baglami(df_sporcu, df_test, calismalar=None, bugun=None, susturulan=(), katalog=None):
    """Öneri için bir kez okunan durum: sporcular (yaş, dal, grup), kayıtlar, batarya durumu, çalışmalar."""
    bugun = tarih_coz(bugun) or date.today()
    sp = _tablo_guvenli(df_sporcu, ["Ad", "Soyad", "Yaş"])
    ts = _tablo_guvenli(df_test, ["Sporcu", "Test", "Tarih", "Oturum"])
    ts = ts.assign(Test=ts["Test"].map(lambda t: kanonik_test(t) if isinstance(t, str) else t))
    sporcular = {}
    for _, r in sp.iterrows():
        ad = f"{'' if pd.isna(r['Ad']) else r['Ad']} {'' if pd.isna(r['Soyad']) else r['Soyad']}".strip()
        if ad and ad not in sporcular:
            g = r.get(GRUP_KOLON)
            sporcular[ad] = {"yas": _sporcu_yasi(r, bugun), "dal": str(r.get("Spor Dalı") or "").strip(),
                             "grup": "" if not _girildi(g) else str(g).strip()}
    return {"bugun": bugun, "sporcular": sporcular, "ts": ts, "katalog": katalog,
            "durum": yonlendirme_durumu(df_sporcu, ts, katalog, bugun=bugun, susturulan=susturulan),
            "susturulan": {tuple(x) for x in susturulan},
            "calismalar": calismalar_oku() if calismalar is None else calismalar}


def _yapilan(b, sporcu):
    ts = b["ts"]
    return set(ts.loc[ts["Sporcu"].astype(str) == sporcu, "Test"].astype(str))


def _son_olcum(b, sporcu, testler):
    ts = b["ts"]
    s = ts[(ts["Sporcu"].astype(str) == sporcu) & ts["Test"].astype(str).isin([kanonik_test(t) for t in testler])]
    d = [x for x in (tarih_coz(v) for v in s["Tarih"]) if x is not None]
    return max(d) if d else None


def calisma_durumu(b, ad):
    """
    Çalışmanın sıradaki ölçüm zamanı: atanmış sporculardan kaçı o zamanda ölçüldü, sıradaki kim. Ölçüldü =
    "çalışma · zaman" oturumunda çalışmanın (toplu girilebilen) bütün testleri kayıtlı. Her zaman tamamsa None.
    """
    c = b["calismalar"][ad]
    katilan = [s for s in calisma_sporculari(c) if s in b["sporcular"]]
    if not katilan:
        return None
    gerek = [t for t in c["testler"] if t not in TOPLU_GIRIS_DISI and kayit_edilebilir(t)]
    ts = b["ts"]
    for z in c["zamanlar"]:
        o = ts[ts["Oturum"].astype(str) == calisma_oturum_adi(ad, z)]
        olculen = [s for s in katilan
                   if (set(gerek) <= set(o.loc[o["Sporcu"].astype(str) == s, "Test"].astype(str)) if gerek
                       else (o["Sporcu"].astype(str) == s).any())]
        if len(olculen) < len(katilan):
            kalan = [s for s in katilan if s not in olculen]
            return {"calisma": ad, "zaman": z, "toplam": len(katilan), "olculen": len(olculen), "kalan": kalan,
                    "atamalar": c["atamalar"]}
    return None


def calisma_son_dokunma(b, ad):
    """Damga (kaydetme / oturum) ile çalışmanın oturumlarındaki en yeni test tarihinin büyüğü; sıralama anahtarı."""
    from datetime import datetime as _dt
    adaylar = []
    try:
        adaylar.append(_dt.fromisoformat(b["calismalar"][ad].get("dokunuldu", "")))
    except (TypeError, ValueError):
        pass
    ts = b["ts"]
    o = ts[ts["Oturum"].astype(str).str.startswith(f"{ad} · ")]
    d = [x for x in (tarih_coz(v) for v in o["Tarih"]) if x is not None]
    if d:
        adaylar.append(_dt.combine(max(d), _dt.min.time()))
    return max(adaylar) if adaylar else _dt.min


def _calisma_onerisi(cd, sporcu):
    kalan = len(cd["kalan"])
    return {"kural": 0, "sporcu": sporcu, "calisma": cd["calisma"],
            "baslik": (f"{cd['calisma']} · {cd['zaman']} — {cd['toplam']} sporcunun {sayi_iyelik(cd['olculen'])}"
                       f" ölçüldü, sıradaki: {sporcu}"
                       + (f" ({cd['atamalar'].get(sporcu)})" if cd["atamalar"].get(sporcu) else "")),
            "gerekce": (f"başlanmış çalışma, {kalan} sporcu kaldı" if cd["olculen"]
                        else f"kurulmuş çalışma, henüz ölçüm yok; {kalan} sporcu kaldı"),
            "eylem": {"tur": "calisma", "calisma": cd["calisma"], "zaman": cd["zaman"], "sporcu": sporcu,
                      "grup": cd["atamalar"].get(sporcu, "")}}


def aktif_calismalar(b):
    """Sıradaki ölçümü olan çalışmalar, en son dokunulan önce."""
    out = [cd for cd in (calisma_durumu(b, ad) for ad in b["calismalar"]) if cd]
    return sorted(out, key=lambda cd: calisma_son_dokunma(b, cd["calisma"]), reverse=True)


def calisma_onerileri(b, ad=None):
    """0. kural. ad verilirse yalnız o çalışma; diğer aktif çalışmalar alternatif olarak arkadan gelir."""
    aktif = aktif_calismalar(b)
    if ad is not None:
        aktif = [cd for cd in aktif if cd["calisma"] == ad] + [cd for cd in aktif if cd["calisma"] != ad]
    return [_calisma_onerisi(cd, cd["kalan"][0]) for cd in aktif]


def _tarama_adaylari(b, yas):
    """Yaşı kapsayan (yas_araligi None olmayan) tarama bataryaları; 7-11 için TSYT önce."""
    if yas is None:
        return []
    adaylar = [(k, t) for k, t in katalog_bataryalari(b["katalog"]).items()
               if (lambda ya: ya is not None and ya[0] <= yas <= ya[1])(batarya_yas_araligi(*k, b["katalog"]))]
    return sorted(adaylar, key=lambda x: (x[0][1] not in ONERI_TARAMA_ONCELIK, ))


def sporcu_onerileri(b, sporcu):
    """Bir sporcu için öneriler, kural sırasıyla (ilk eşleşen kazanır; sonrakiler alternatif)."""
    bilgi = b["sporcular"].get(sporcu)
    if bilgi is None:
        return []
    yas, grup = bilgi["yas"], bilgi["grup"]
    yapilan = _yapilan(b, sporcu)
    out = []
    # 0) aktif çalışmada bu sporcunun sırası gelmiş
    for cd in aktif_calismalar(b):
        if sporcu in cd["kalan"]:
            out.append(_calisma_onerisi(cd, sporcu))
    # 1) yarım batarya (Paket 32: üç şart + susturma)
    for k in b["durum"]["yarim"]:
        if k["sporcu"] == sporcu:
            n = len(k["eksik"])
            out.append({"kural": 1, "sporcu": sporcu, "batarya": k["batarya"], "kategori": k["kategori"],
                        "baslik": f"{sporcu} · {batarya_kisa(k['batarya'])} bataryasını tamamla ({n} test)",
                        "gerekce": f"başlanmış batarya, {n} test kaldı",
                        "eylem": {"tur": "oturum", "kategori": k["kategori"], "batarya": k["batarya"],
                                  "testler": list(k["eksik"]), "sporcu": sporcu, "grup": grup}})
    # 2) yaşa uygun tarama bataryası tamamlanmamış
    adaylar = _tarama_adaylari(b, yas)
    tamam_tarama = [k for k, t in adaylar if set(t) <= yapilan]
    yarimdaki = {o["batarya"] for o in out if o["kural"] == 1}
    bekleyen = [] if tamam_tarama else [(k, t) for k, t in adaylar if (sporcu, k[1]) not in b["susturulan"]]
    tarama_bekliyor = bool(bekleyen)                     # yarım (1. kural) olan da tarama bekliyor sayılır
    if any(k[1] in yarimdaki for k, _ in adaylar):
        bekleyen = []                                    # yaşa uygun tarama zaten sürüyor (1. kural): ikinci tarama önerilmez
    if bekleyen:
        (kat, bat), testler = bekleyen[0]
        eksik = [t for t in testler if t not in yapilan]
        ya = batarya_yas_araligi(kat, bat, b["katalog"])
        out.append({"kural": 2, "sporcu": sporcu, "batarya": bat, "kategori": kat,
                    "baslik": (f"{sporcu} · {batarya_kisa(bat)} bataryasını uygula"
                               + (f" ({len(eksik)} test)" if len(eksik) == len(testler)
                                  else f" (kalan {len(eksik)} test)")),
                    "gerekce": f"yaşa uygun norm var: {batarya_kisa(bat)} {ya[0]}-{ya[1]} yaş, sporcu {yas} yaşında",
                    "eylem": {"tur": "oturum", "kategori": kat, "batarya": bat, "testler": eksik,
                              "sporcu": sporcu, "grup": grup}})
    # 3) tarama tamam (ya da yaşa uygun tarama yok) → dalına özgü batarya; 11 yaş altında ve karşılıksız dalda atlanır
    raf = brans_rafi(bilgi["dal"], b["katalog"])
    brans_testleri = []
    if raf:
        alt, brans, raf_testleri = raf
        brans_testleri = [t for t in raf_testleri if kayit_edilebilir(t)]
        eksik = [t for t in brans_testleri if kanonik_test(t) not in yapilan]
        if (yas is not None and yas >= ONERI_BRANS_YASI and not tarama_bekliyor and eksik):
            if all(t in TOPLU_GIRIS_DISI for t in eksik):
                eylem = {"tur": "test_uygula", "sporcu": sporcu, "yol": ("Branşa Özgü Testler", alt, brans),
                         "test": eksik[0]}
            else:
                eylem = {"tur": "oturum", "kategori": "Branşa Özgü Testler", "batarya": alt, "brans": brans,
                         "testler": [t for t in eksik if t not in TOPLU_GIRIS_DISI], "sporcu": sporcu, "grup": grup}
            out.append({"kural": 3, "sporcu": sporcu, "batarya": brans, "kategori": "Branşa Özgü Testler",
                        "baslik": f"{sporcu} · {brans} testleri ({len(eksik)} test)",
                        "gerekce": f"dalına özgü ölçüm: {bilgi['dal']}",
                        "eylem": eylem})
    # 4) hepsi tamam → son ölçümü en eski olanı tekrar
    tekrar = []
    for k in b["durum"]["tamam"]:
        if k["sporcu"] == sporcu:
            testler = katalog_bataryalari(b["katalog"])[(k["kategori"], k["batarya"])]
            tekrar.append((_son_olcum(b, sporcu, testler), batarya_kisa(k["batarya"]),
                           {"tur": "oturum", "kategori": k["kategori"], "batarya": k["batarya"], "testler": testler,
                            "sporcu": sporcu, "grup": grup}))
    if raf and brans_testleri and all(kanonik_test(t) in yapilan for t in brans_testleri):
        tekrar.append((_son_olcum(b, sporcu, brans_testleri), f"{raf[1]} testleri",
                       {"tur": "oturum", "kategori": "Branşa Özgü Testler", "batarya": raf[0], "brans": raf[1],
                        "testler": [t for t in brans_testleri if t not in TOPLU_GIRIS_DISI], "sporcu": sporcu,
                        "grup": grup}))
    for son, ad_, eylem in sorted([x for x in tekrar if x[0] is not None], key=lambda x: x[0]):
        out.append({"kural": 4, "sporcu": sporcu, "batarya": ad_,
                    "baslik": f"{sporcu} · {ad_} — tekrar ölç",
                    "gerekce": f"son ölçüm {_hafta_metni((b['bugun'] - son).days)}",
                    "eylem": eylem})
    return [o for o in out if str(o.get("gerekce", "")).strip()]          # gerekçesiz öneri gösterilmez


def oneri_secenekleri(b):
    """Seçici: aktif çalışmalar ("calisma::ad") ve sporcular ("sporcu::ad"); varsayılan = en öncelikli öneri."""
    calisma = [f"calisma::{cd['calisma']}" for cd in aktif_calismalar(b)]
    sporcu = [f"sporcu::{s}" for s in b["sporcular"]]
    varsayilan = calisma[0] if calisma else None
    if varsayilan is None and sporcu:
        sira = {s: min([o["kural"] for o in sporcu_onerileri(b, s)] or [9]) for s in b["sporcular"]}
        varsayilan = f"sporcu::{min(b['sporcular'], key=lambda s: sira[s])}"
    return calisma + sporcu, varsayilan


def oneriler(b, secim):
    """Seçime göre öneri listesi: ilki ana öneri, ikincisi alternatif."""
    tur, _, ad = str(secim or "").partition("::")
    if tur == "calisma":
        return calisma_onerileri(b, ad)
    if tur == "sporcu":
        return sporcu_onerileri(b, ad)
    return []


# ── H) Görselsiz testlerde boş alan yerine neden ──
def gorselsiz_metni(test_adi):
    """Görseli bilerek olmayan test için ekranda yazılacak cümle; görselli ya da bilinmeyen testte None."""
    neden = TEST_GORSELSIZ.get(kanonik_test(test_adi))
    return f"Bu test için görsel yok — {neden}" if neden else None


def sira_birlestir(onceki, secilenler):
    """Önceki sırayı korur: seçimden çıkanlar düşer, yeni seçilenler sona eklenir."""
    return [t for t in onceki if t in secilenler] + [t for t in secilenler if t not in onceki]


def _virgullu(metin):
    return [p.strip() for p in str(metin).split(",") if p.strip()]


def konum_sekme_sirasi(yas):
    """16 yaş altında (ya da yaş bilinmezken) varsayılan görünüm kendi değişimi; konum ikinci sekmede."""
    y = _yas_degeri(yas)
    return (["Kendi değişimin", "Grup içi konum"] if y is None or y < KENDI_DEGISIM_YASI
            else ["Grup içi konum", "Kendi değişimin"])


def ozet_kartlari_html(ogeler):
    """Sonuçlar üstündeki özet kartları: dar ekranda alt alta kayar, uzun değer (tarih) kesilmez."""
    return ('<div class="sp-ozet" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));'
            f'gap:{b(1.5)};margin:{b(1)} 0 {b(2)}">'
            + "".join(f'<div class="sp-kart" style="margin:0;border-left-color:{renk_css("ana")}">'
                      f'<span class="sp-etiket">{_html.escape(str(e))}</span>'
                      f'<div class="sp-deger" style="font-size:1.375rem">{_html.escape(str(d))}</div></div>'
                      for e, d in ogeler) + "</div>")
