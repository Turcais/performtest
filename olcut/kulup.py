"""
Kulüpler (Paket 38n): her kulüp kulupler/<kod>/ altında kendi dosyalarıyla (sporcular.xlsx, test_sonuclari.xlsx,
ilgi_anketi.xlsx, oturum_taslagi.json, ayarlar.json) + kulup.json (bilgiler). Kulüp seçilmemişse ya da "kulupler"
klasörü yoksa "Genel" çalışma alanı: çalışma klasöründeki bugünkü dosyalar. Silme yok; "Arşivle" listeden gizler.
Dosya yolu: ortak.veri_yolu (os.chdir yok).
"""
import json as _json
import os
import re
import unicodedata
from datetime import date
import pandas as pd
from olcut.analiz import ANTRENMAN_KOLON, ANTRENMAN_TARIH_KOLON, ILGI_DOSYA
from olcut.kayit import GRUP_KOLON
from olcut.norm import META_KOLONLAR, SPORCU_DOSYA, TEST_DOSYA
from olcut.ortak import DOGUM_KOLON, KULUP_KLASORU, KULUP_KODU_KALIBI, kulup_klasoru

KULUP_DOSYA = "kulup.json"
GENEL_ALAN = "Genel"
KULUP_ALANLARI = {                     # alan: (etiket, varsayılan)
    "ad": ("Kulüp adı", ""),
    "sehir": ("Şehir", ""),
    "branslar": ("Branşlar", []),
    "iletisim": ("İletişim kişisi", ""),
    "sozlesme_baslangic": ("Sözleşme başlangıcı", ""),
    "sozlesme_bitis": ("Sözleşme bitişi", ""),
    "karsilastirma_onayi": ("Kulüpler arası karşılaştırmaya onay", False),   # 38o kullanacak
    "arsiv": ("Arşivde", False),
}
_BOS_SUTUNLAR = {
    SPORCU_DOSYA: ["Ad", "Soyad", "Yaş", "Cinsiyet", "Spor Dalı", "Derece", "Boy (cm)", "Kilo (kg)", ANTRENMAN_KOLON,
                   GRUP_KOLON, DOGUM_KOLON, ANTRENMAN_TARIH_KOLON],
    TEST_DOSYA: [k for k in META_KOLONLAR if k != "Tarih_dt"],
    ILGI_DOSYA: ["Sporcu", "Tarih", "Anket"],
}
_TR_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")


def kulup_kodu(ad, mevcut=()):
    """Türkçe harfsiz, küçük harf, tireli kod ('Arslan SK' → 'arslan-sk'); varsa sonuna -2, -3…"""
    kod = unicodedata.normalize("NFKD", str(ad).translate(_TR_ASCII)).encode("ascii", "ignore").decode().lower()
    kod = re.sub(r"[^a-z0-9]+", "-", kod).strip("-") or "kulup"
    aday, i = kod, 2
    while aday in set(mevcut):
        aday, i = f"{kod}-{i}", i + 1
    return aday


def _bilgi_tamamla(bilgi):
    return {k: bilgi.get(k, v) if isinstance(bilgi, dict) else v for k, (_, v) in KULUP_ALANLARI.items()}


def kulup_oku(kod):
    """kulup.json (eksik alanlar varsayılanla) ya da None (geçersiz kod, klasör/dosya yok, bozuk)."""
    if not KULUP_KODU_KALIBI.match(kod or ""):
        return None
    try:
        with open(os.path.join(kulup_klasoru(kod), KULUP_DOSYA), encoding="utf-8") as f:
            return _bilgi_tamamla(_json.load(f))
    except (OSError, ValueError):
        return None


def kulup_kaydet(kod, bilgi):
    """Bilgileri kulup.json'a yazar (önce geçici dosya). Döner: True/False."""
    yol = os.path.join(kulup_klasoru(kod), KULUP_DOSYA)
    try:
        with open(yol + ".yaziliyor", "w", encoding="utf-8") as f:
            _json.dump(_bilgi_tamamla(bilgi), f, ensure_ascii=False, indent=1)
        os.replace(yol + ".yaziliyor", yol)
        return True
    except OSError:
        return False


def kulupler(arsiv=False):
    """{kod: bilgi} — kulupler/ altındaki geçerli kulüpler, ada göre; arşivdekiler yalnız arsiv=True ise."""
    if not os.path.isdir(KULUP_KLASORU):
        return {}
    sonuc = {}
    for kod in sorted(os.listdir(KULUP_KLASORU)):
        b = kulup_oku(kod)
        if b is not None and (arsiv or not b["arsiv"]):
            sonuc[kod] = b
    return dict(sorted(sonuc.items(), key=lambda x: x[1]["ad"].casefold()))


def kulup_olustur(bilgi):
    """Yeni kulüp: kod adından; klasör + kulup.json + başlık satırlı boş xlsx dosyaları. Döner: kod."""
    ad = str(bilgi.get("ad", "")).strip()
    if not ad:
        raise ValueError("Kulüp adı gerekli")
    mevcut = os.listdir(KULUP_KLASORU) if os.path.isdir(KULUP_KLASORU) else []
    kod = kulup_kodu(ad, mevcut)
    os.makedirs(kulup_klasoru(kod))
    for dosya, sutunlar in _BOS_SUTUNLAR.items():
        pd.DataFrame(columns=sutunlar).to_excel(os.path.join(kulup_klasoru(kod), dosya), index=False)
    kulup_kaydet(kod, {**bilgi, "ad": ad, "arsiv": False})
    return kod


def kulup_arsivle(kod, arsiv=True):
    b = kulup_oku(kod)
    return b is not None and kulup_kaydet(kod, {**b, "arsiv": bool(arsiv)})


def calisma_alani_adi(kod):
    """Seçicide görünen ad: '' → Genel; kulüpte kulup.json adı."""
    if not kod:
        return GENEL_ALAN
    b = kulup_oku(kod)
    return b["ad"] if b else kod


def bugun_metni():
    return date.today().strftime("%d.%m.%Y")
