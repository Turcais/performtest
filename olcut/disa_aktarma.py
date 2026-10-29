"""
Dışa aktarma (Paket 38i): rapor HTML'ini PDF'e çevirme, güvenli dosya adı, tabloyu CSV / Excel baytına yazma.
Hesap yapmaz ve içerik eklemez: kendisine verilen HTML'i ya da tabloyu olduğu gibi yazar.

PDF çevirici sırası: (1) sistemde kurulu Chromium tabanlı tarayıcı (Edge Windows'ta hep kurulu; Chrome/Chromium da
olur) başsız kipte yazdırır — ekrandaki raporla aynı çizim: SVG, Türkçe, CSS @page; (2) WeasyPrint; (3) xhtml2pdf.
Hiçbiri yoksa ya da çeviremezse None döner; sayfa yazdırmaya hazır HTML ve talimat gösterir.
"""
import datetime
import io
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata

import pandas as pd

_TR_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")

PDF_YAZDIRMA_ADIMLARI = (
    "PDF çevirici bulunamadı; raporu yazdırmaya hazır HTML olarak indirin, sonra:\n"
    "1. İnen dosyayı çift tıklayıp tarayıcıda açın.\n"
    "2. Ctrl + P (Mac'te Cmd + P) ile yazdırmayı açın.\n"
    "3. Hedef / Yazıcı olarak \"PDF olarak kaydet\"i seçin; kâğıt A4.\n"
    "4. Kaydet'e basın.\n"
    "Kalıcı çözüm: Microsoft Edge ya da Google Chrome kurulu olmalı ya da komut satırında "
    "`python -m pip install xhtml2pdf` çalıştırın.")

_TARAYICI_ADLARI = ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")
_TARAYICI_YOLLARI = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)
PDF_BEKLEME_SN = 60


def guvenli_dosya_adi(*parcalar):
    """Parçaları "_" ile birleştirir; Türkçe harfler ASCII karşılığına, boşluk ve işaretler "_"e döner."""
    metin = "_".join(str(p) for p in parcalar if p not in (None, ""))
    metin = unicodedata.normalize("NFKD", metin.translate(_TR_ASCII)).encode("ascii", "ignore").decode()
    metin = re.sub(r"[^A-Za-z0-9.-]+", "_", metin)
    return re.sub(r"_+", "_", metin).strip("._") or "dosya"


def tarih_eki(gun=None):
    """GGAAYYYY (ör. 29102026)."""
    return (gun or datetime.date.today()).strftime("%d%m%Y")


# ── PDF ──
def _tarayici_bul():
    for ad in _TARAYICI_ADLARI:
        yol = shutil.which(ad)
        if yol:
            return yol
    return next((y for y in _TARAYICI_YOLLARI if os.path.exists(y)), None)


def _pdf_tamam(yol):
    """Dosya yazılıp kapandı mı (PDF başı ve sonu yerinde)?"""
    try:
        with open(yol, "rb") as f:
            veri = f.read()
    except OSError:
        return None
    return veri if veri[:4] == b"%PDF" and b"%%EOF" in veri[-1024:] else None


def _tarayici_ile(html, tarayici=None):
    tarayici = tarayici or _tarayici_bul()
    if not tarayici:
        return None
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        giris, cikis = os.path.join(d, "rapor.html"), os.path.join(d, "rapor.pdf")
        with open(giris, "w", encoding="utf-8") as f:
            f.write(html)
        komut = [tarayici, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                 "--disable-extensions", f"--user-data-dir={os.path.join(d, 'profil')}", "--no-pdf-header-footer",
                 f"--print-to-pdf={cikis}", pathlib.Path(giris).as_uri()]
        ek = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        subprocess.run(komut, capture_output=True, timeout=PDF_BEKLEME_SN, **ek)
        # Edge işi alt sürece bırakıp hemen dönebiliyor: dosya tamamlanana kadar bekle
        son = time.monotonic() + PDF_BEKLEME_SN
        while time.monotonic() < son:
            veri = _pdf_tamam(cikis)
            if veri:
                return veri
            time.sleep(0.2)
    return None


def _weasyprint_ile(html):
    import weasyprint
    return weasyprint.HTML(string=html).write_pdf()


def _xhtml2pdf_ile(html):
    from xhtml2pdf import pisa
    tampon = io.BytesIO()
    sonuc = pisa.CreatePDF(html, dest=tampon, encoding="utf-8")
    return None if sonuc.err else tampon.getvalue()


_CEVIRICILER = (("tarayıcı", _tarayici_ile), ("WeasyPrint", _weasyprint_ile), ("xhtml2pdf", _xhtml2pdf_ile))


def _modul_var(ad):
    import importlib.util
    try:
        return importlib.util.find_spec(ad) is not None
    except (ImportError, ValueError):
        return False


def pdf_cevirici():
    """Kullanılabilecek ilk çeviricinin adı ya da None (çevirmeden, ucuz denetim)."""
    if _tarayici_bul():
        return "tarayıcı"
    return next((ad for ad, m in (("WeasyPrint", "weasyprint"), ("xhtml2pdf", "xhtml2pdf")) if _modul_var(m)), None)


def pdf_cevir(html, ceviriciler=None):
    """HTML → (PDF baytı, çevirici adı); hiçbiri çeviremezse (None, None). Hata fırlatmaz."""
    for ad, cevir in (ceviriciler or _CEVIRICILER):
        try:
            veri = cevir(html)
        except Exception:                      # kurulu değil, zaman aşımı, bozuk çıktı: sıradakini dene
            veri = None
        if veri and veri[:4] == b"%PDF":
            return veri, ad
    return None, None


# ── Tablo ──
def tablo_csv(tablo):
    """Excel'de Türkçe düzgün açılan CSV: UTF-8 BOM, ";" ayırıcı, ondalık virgül."""
    return ("\ufeff" + tablo.to_csv(index=False, sep=";", decimal=",", lineterminator="\r\n")).encode("utf-8")


def tablo_xlsx(sayfalar):
    """{sayfa adı: DataFrame} → .xlsx baytı (boş sayfa yazılmaz)."""
    tampon = io.BytesIO()
    with pd.ExcelWriter(tampon, engine="openpyxl") as yazici:
        for ad, tablo in sayfalar.items():
            if tablo is not None and not tablo.empty:
                tablo.to_excel(yazici, sheet_name=ad[:31], index=False)
    return tampon.getvalue()
