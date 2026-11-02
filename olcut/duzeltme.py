"""
Paket 38s — kayıtlı ölçümü düzeltme, başka sporcuya taşıma, silme ve geri alma. Streamlit çağrısı yok.

- Satır kimliği: test dosyasındaki satır sırası. Dosyadan satır hiç çıkmaz (kayıt yalnız eklenir, silme işarettir),
  bu yüzden numara kalıcıdır. Yazmadan önce satırın hâlâ aynı kayıt olduğu (sporcu, test, tarih) denetlenir.
- Silme kalıcı değil: "Silindi" sütununa zaman yazılır; test_tablosu_duzelt bu satırları her okumada çıkarır.
- Her işlemden önce test dosyasının yedeği (yedekler/), her değişen alan değişiklik kaydına (degisiklik_kaydi.xlsx);
  ikisi de çalışma alanına özel (veri_yolu).
- Diskte çalışmalı bir oturum taslağı varsa o oturumun ("çalışma · ölçüm zamanı") kayıtları düzenlenemez.
"""
import json as _json
import os
import shutil
import pandas as pd
from datetime import datetime
from olcut.analiz import sporcu_profil_bilgisi
from olcut.katalog_islemleri import SILINDI_KOLON, kanonik_test, test_bilgisi
from olcut.kayit import calisma_oturum_adi, deger_metni, makullukte_uyarilar, onceki_olcumler
from olcut.norm import META_KOLONLAR, SWFT_TEST, TEST_DOSYA, swft_turetilmis, turetilmis_degerler
from olcut.ortak import DOGUM_KOLON, _girildi, guvenli_float, tam_yas, tarih_coz, veri_yolu


DEGISIKLIK_DOSYA = "degisiklik_kaydi.xlsx"
YEDEK_KLASOR = "yedekler"
TASLAK_DOSYA_ADI = "oturum_taslagi.json"          # Test Oturumu'nun taslağı (sayfalar/test_oturumu.TASLAK_DOSYA)
DEGISIKLIK_KOLONLARI = ["Zaman", "İşlem", "Satır", "Sporcu", "Test", "Tarih", "Oturum", "Alan", "Eski değer",
                        "Yeni değer", "Açıklama"]
ISLEM_DUZELT, ISLEM_TASI, ISLEM_SIL, ISLEM_GERI_AL = "Düzeltme", "Taşıma", "Silme", "Geri alma"
_KIMLIK_ALANLARI = ("Sporcu", "Test", "Tarih")
_META = set(META_KOLONLAR) | {SILINDI_KOLON}


class DuzeltmeHatasi(ValueError):
    """İşlem yapılamaz (kilitli oturum, değişmiş dosya, geçersiz değer…); metni kullanıcıya gösterilir."""


# ── Okuma ──
def ham_tablo():
    """Test dosyası olduğu gibi (silinenler dahil); index = dosyadaki satır numarası. Dosya yoksa boş tablo."""
    yol = veri_yolu(TEST_DOSYA)
    if not os.path.exists(yol):
        return pd.DataFrame()
    return pd.read_excel(yol).reset_index(drop=True)


def silindi_mi(satir):
    return _girildi(satir.get(SILINDI_KOLON))


def kilitli_oturum():
    """Diskteki taslak bir çalışmanın ölçüm zamanına aitse o oturumun kimliği ("çalışma · zaman"), yoksa None."""
    try:
        with open(veri_yolu(TASLAK_DOSYA_ADI), encoding="utf-8") as f:
            t = _json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(t, dict) or not t.get("testler") or not t.get("sporcular"):
        return None
    b = t.get("bilgi") if isinstance(t.get("bilgi"), dict) else {}
    return calisma_oturum_adi(b["calisma"], b["zaman"]) if b.get("calisma") and b.get("zaman") else None


def satir_kilitli(satir, kilit=None):
    kilit = kilitli_oturum() if kilit is None else kilit
    return bool(kilit) and str(satir.get("Oturum", "") or "").strip() == kilit


def girilen_degiskenler(satir):
    """Kaydın elle girilen değişkenleri: katalogdaki değişkenler; katalogda yoksa dolu sütunlardan türetilenler çıkar."""
    bilgi = test_bilgisi(str(satir.get("Test", "")))
    if bilgi and bilgi.get("degiskenler"):
        return list(bilgi["degiskenler"])
    dolu = {k: deger_metni(v) for k, v in satir.items() if k not in _META and _girildi(v)}
    turetilen = set(_turet(str(satir.get("Test", "")), dolu, {}))
    return [k for k in dolu if k not in turetilen]


def _turet(test, degerler, profil):
    """Kayda yazılan türetilmiş sayılar (test_kaydi_olustur ile aynı süzgeç: yalnız int/float); SWFT dahil."""
    kilo = guvenli_float(profil.get("Kilo (kg)", 0)) if _girildi(profil.get("Kilo (kg)")) else 0
    h, _ = turetilmis_degerler(test, degerler, profil, kilo)
    if kanonik_test(test) == SWFT_TEST:
        h.update(swft_turetilmis(degerler, kilo))
    return {k: v for k, v in h.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def _sayi_ya_da_metin(v):
    """Girilen metni kaydedilecek değere çevirir: sayıysa sayı (ondalık virgül kabul), değilse kırpılmış metin."""
    m = deger_metni(v)
    if m == "":
        return ""
    try:
        f = float(m.replace(",", "."))
        return int(f) if f.is_integer() else f
    except ValueError:
        return m


def _ayni(a, b):
    return deger_metni(a) == deger_metni(b)


def _test_yasi(profil, tarih, eski, tasima=False):
    """
    Kayıt günündeki yaş (test_kaydi_olustur ile aynı): doğum tarihinden. Doğum yoksa düzeltmede eskisi kalır;
    taşımada yeni sporcunun profil yaşı (eskisi başka sporcunundur).
    """
    y = tam_yas(profil.get(DOGUM_KOLON), tarih)
    if y is None and tasima and _girildi(profil.get("Yaş")):
        y = profil.get("Yaş")
    return eski if y is None else y


# ── Önizleme: ne değişecek, hangi uyarılar çıkar (dosya değişmez) ──
def _yeniden_hesapla(satir_no, satir, girilen, profil, eski_profil, tasima=False):
    """
    Satırın yeni hâli için değişiklik listesi [(alan, eski, yeni)] ve aykırı değer uyarıları. girilen: yeni girilen
    değerler (bütün girilen değişkenler); türetilenler ve test yaşı yeniden hesaplanır.
    """
    test = str(satir.get("Test", ""))
    eski_h = _turet(test, {k: deger_metni(satir.get(k)) for k in girilen}, eski_profil)
    yeni_h = _turet(test, {k: deger_metni(v) for k, v in girilen.items()}, profil)
    degisen = []
    for k, v in girilen.items():
        if not _ayni(satir.get(k), v):
            degisen.append((k, satir.get(k), v))
    for k in list(dict.fromkeys(list(eski_h) + list(yeni_h))):
        if k in girilen:
            continue
        yeni = yeni_h.get(k, "")
        if not _ayni(satir.get(k), yeni):
            degisen.append((k, satir.get(k), yeni))
    tarih = tarih_coz(satir.get("Tarih"))
    ty = _test_yasi(profil, tarih, satir.get("Test Yaşı"), tasima)
    if not _ayni(satir.get("Test Yaşı"), ty):
        degisen.append(("Test Yaşı", satir.get("Test Yaşı"), ty))
    sporcu = str(profil.get("_ad") or satir.get("Sporcu"))
    yas = ty if _girildi(ty) else None
    tum = {**{k: v for k, v in girilen.items() if _girildi(v)}, **yeni_h}
    uyarilar = makullukte_uyarilar(test, tum, yas, str(profil.get("Cinsiyet", "") or "").strip(),
                                   profil.get(DOGUM_KOLON), tarih, sporcu,
                                   onceki_olcumler(sporcu, test, tarih, haric_satir=satir_no))
    return degisen, uyarilar


def _profil(sporcu):
    p = dict(sporcu_profil_bilgisi(sporcu))
    p["_ad"] = sporcu
    return p


def _satir_al(df, satir_no, silinmis_olabilir=False):
    if satir_no not in df.index:
        raise DuzeltmeHatasi("Kayıt bulunamadı; sayfa yenilenmiş olabilir.")
    r = df.loc[satir_no]
    if silindi_mi(r) and not silinmis_olabilir:
        raise DuzeltmeHatasi("Bu kayıt silinmiş; önce geri alın.")
    if satir_kilitli(r):
        raise DuzeltmeHatasi(f"\"{r.get('Oturum')}\" oturumunun taslağı Test Oturumu'nda açık. Taslağı kaydedin ya "
                             "da silin; sonra düzenleyin.")
    return r


def duzeltme_onizleme(satir_no, degisken, yeni, df=None):
    """Tek değer düzeltmesi: {"degisiklikler": [(alan, eski, yeni)], "uyarilar": [...]}. Dosya değişmez."""
    df = ham_tablo() if df is None else df
    r = _satir_al(df, satir_no)
    girilenler = girilen_degiskenler(r)
    if degisken not in girilenler:
        raise DuzeltmeHatasi(f"\"{degisken}\" girilen bir değer değil (hesaplanır); girilen değerlerden birini seçin.")
    girilen = {k: r.get(k) for k in girilenler}
    girilen[degisken] = _sayi_ya_da_metin(yeni)
    if not any(_girildi(v) and deger_metni(v) != "" for v in girilen.values()):
        raise DuzeltmeHatasi("Kayıtta hiç değer kalmıyor; değeri boşaltmak yerine kaydı silin.")
    p = _profil(str(r.get("Sporcu")))
    degisen, uyarilar = _yeniden_hesapla(satir_no, r, girilen, p, p)
    return {"degisiklikler": degisen, "uyarilar": uyarilar}


def tasima_onizleme(satir_nolari, yeni_sporcu, df=None):
    """Kayıtları başka sporcuya taşıma: {satır: {"degisiklikler", "uyarilar"}}. Test yaşı yeni sporcuya göre."""
    df = ham_tablo() if df is None else df
    if not str(yeni_sporcu or "").strip():
        raise DuzeltmeHatasi("Hedef sporcuyu seçin.")
    yeni_p = _profil(yeni_sporcu)
    if len(yeni_p) <= 1:
        raise DuzeltmeHatasi(f"\"{yeni_sporcu}\" sporcu listesinde yok.")
    out = {}
    for n in satir_nolari:
        r = _satir_al(df, n)
        if str(r.get("Sporcu")) == yeni_sporcu:
            raise DuzeltmeHatasi("Kayıt zaten bu sporcuda.")
        girilen = {k: r.get(k) for k in girilen_degiskenler(r)}
        degisen, uyarilar = _yeniden_hesapla(n, r, girilen, yeni_p, _profil(str(r.get("Sporcu"))), tasima=True)
        out[n] = {"degisiklikler": [("Sporcu", r.get("Sporcu"), yeni_sporcu)] + degisen, "uyarilar": uyarilar}
    return out


# ── Yazma: yedek + dosya + değişiklik kaydı ──
def yedek_al():
    """Test dosyasının zaman damgalı kopyası yedekler/ altında (çalışma alanına özel). Dönen: yedeğin yolu ya da None."""
    kaynak = veri_yolu(TEST_DOSYA)
    if not os.path.exists(kaynak):
        return None
    klasor = veri_yolu(YEDEK_KLASOR)
    os.makedirs(klasor, exist_ok=True)
    hedef = os.path.join(klasor, f"test_sonuclari_{datetime.now():%Y%m%d-%H%M%S-%f}.xlsx")
    shutil.copy2(kaynak, hedef)
    return hedef


def degisiklik_kaydi_oku():
    yol = veri_yolu(DEGISIKLIK_DOSYA)
    if not os.path.exists(yol):
        return pd.DataFrame(columns=DEGISIKLIK_KOLONLARI)
    metin = {k: str for k in DEGISIKLIK_KOLONLARI if k != "Satır"}      # eski/yeni değer sayı ya da metin olabilir
    return pd.read_excel(yol, dtype=metin).fillna("")


def _kayda_ekle(satirlar):
    eski = degisiklik_kaydi_oku()
    yeni = pd.DataFrame(satirlar, columns=DEGISIKLIK_KOLONLARI)
    (yeni if eski.empty else pd.concat([eski, yeni], ignore_index=True)).to_excel(
        veri_yolu(DEGISIKLIK_DOSYA), index=False)


def _uygula(beklenen, degisiklikler, islem, aciklama=""):
    """
    beklenen: {satır: (sporcu, test, tarih)} — önizlemedeki kayıt; dosya o arada değiştiyse işlem yapılmaz.
    degisiklikler: {satır: [(alan, eski, yeni)]}. Önce yedek, sonra test dosyası, sonra değişiklik kaydı.
    """
    df = ham_tablo()
    for n, kim in beklenen.items():
        if n not in df.index or tuple(str(df.at[n, a]) for a in _KIMLIK_ALANLARI) != tuple(map(str, kim)):
            raise DuzeltmeHatasi("Kayıt dosyası bu arada değişmiş; sayfayı yenileyip yeniden deneyin.")
    zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    log = []
    for n, liste in degisiklikler.items():
        r = df.loc[n]
        for alan, eski, yeni in liste:
            if alan not in df.columns:
                df[alan] = pd.Series([None] * len(df), dtype="object")
            elif df[alan].dtype != object:
                df[alan] = df[alan].astype(object)
            df.at[n, alan] = None if deger_metni(yeni) == "" else yeni
            log.append([zaman, islem, int(n) + 2, r.get("Sporcu"), r.get("Test"), r.get("Tarih"),
                        str(r.get("Oturum", "") or "") if _girildi(r.get("Oturum")) else "",
                        alan, deger_metni(eski), deger_metni(yeni), aciklama])
    if not log:
        return 0
    yedek_al()
    df.to_excel(veri_yolu(TEST_DOSYA), index=False)
    _kayda_ekle(log)
    return len(log)


def _kimlik(df, satirlar):
    return {n: tuple(df.at[n, a] for a in _KIMLIK_ALANLARI) for n in satirlar}


def kayit_duzelt(satir_no, degisken, yeni, aciklama=""):
    """Tek değeri düzeltir; türetilenler ve test yaşı yeniden hesaplanır. Dönen: değişen alan sayısı."""
    df = ham_tablo()
    o = duzeltme_onizleme(satir_no, degisken, yeni, df)
    return _uygula(_kimlik(df, [satir_no]), {satir_no: o["degisiklikler"]}, ISLEM_DUZELT, aciklama)


def kayit_tasi(satir_nolari, yeni_sporcu, aciklama=""):
    """Kayıtları başka sporcuya taşır; test yaşı (ve kiloya bağlı türetilenler) yeni sporcuya göre."""
    df = ham_tablo()
    o = tasima_onizleme(satir_nolari, yeni_sporcu, df)
    return _uygula(_kimlik(df, satir_nolari), {n: v["degisiklikler"] for n, v in o.items()}, ISLEM_TASI, aciklama)


def kayit_sil(satir_nolari, aciklama=""):
    """Kayıtları silindi olarak işaretler (kalıcı silme yok)."""
    df = ham_tablo()
    zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    d = {}
    for n in satir_nolari:
        r = _satir_al(df, n)
        d[n] = [(SILINDI_KOLON, "", zaman)]
    return _uygula(_kimlik(df, satir_nolari), d, ISLEM_SIL, aciklama)


def kayit_geri_al(satir_nolari, aciklama=""):
    """Silindi işaretini kaldırır."""
    df = ham_tablo()
    d = {}
    for n in satir_nolari:
        r = _satir_al(df, n, silinmis_olabilir=True)
        if silindi_mi(r):
            d[n] = [(SILINDI_KOLON, r.get(SILINDI_KOLON), "")]
    return _uygula(_kimlik(df, list(d)), d, ISLEM_GERI_AL, aciklama)


# ── Seçim yardımcıları (ekran) ──
def oturum_satirlari(df, oturum, sporcu=None, silinmis=False):
    """Oturumun (isteğe bağlı tek sporcunun) satır numaraları; silinmis=True ise yalnız silinmişler, False ise etkinler."""
    if df.empty or "Oturum" not in df.columns:
        return []
    d = df[df["Oturum"].astype(str) == str(oturum)]
    if sporcu is not None:
        d = d[d["Sporcu"].astype(str) == str(sporcu)]
    return [n for n, r in d.iterrows() if silindi_mi(r) == silinmis]
