"""
Ortak yardımcılar: metin ve sayı biçimleri (_e, _sayi, ad_bicimi), boş değer denetimi, tarih ve yaş, ayar ve
tablo dosyası okuma/yazma, not çözümleme. Uygulamanın başka hiçbir modülüne dayanmaz.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import inspect
import json as _json
import os
import pandas as pd
import re
from datetime import date


def _desteklenen(fn, **secenek):
    """Kurulu Streamlit sürümünün desteklediği anahtar sözcükler (eski sürümde bilinmeyen parametre verilmez)."""
    try:
        kabul = set(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        kabul = set()
    return {k: v for k, v in secenek.items() if k in kabul}


# Paket 38c: ad ve soyadda Türkçe baş harf. Sözcük TÜMÜYLE küçük ya da TÜMÜYLE büyük yazılmışsa ilk harf büyük,
# kalanı küçük (i/İ, ı/I kuralıyla; çeviri tablosu — Python'un hazır büyük/küçük harf işlevleri Türkçe kuralı
# bilmez). Karışık yazılmış
# sözcüğe dokunulmaz ("Gülru", "McDonald", "De La Cruz" aynen kalır). Kayıtta uygulanır; eski kayıtlar
# görüntülemede aynı biçimle gösterilir (kayıttaki ad, eşleştirme anahtarı olarak değişmez).
_TR_KUCUK = "abcçdefgğhıijklmnoöprsştuüvyzqwxâîû"


_TR_BUYUK = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZQWXÂÎÛ"


_TR_BUYUT = str.maketrans(_TR_KUCUK, _TR_BUYUK)


_TR_KUCULT = str.maketrans(_TR_BUYUK, _TR_KUCUK)


def _sozcuk_bicimi(m):
    s = m.group(0)
    if all(c in _TR_KUCUK for c in s) or all(c in _TR_BUYUK for c in s):
        return s[:1].translate(_TR_BUYUT) + s[1:].translate(_TR_KUCULT)
    return s


def ad_bicimi(ad):
    """'ahmet yilmaz' → 'Ahmet Yilmaz', 'MEHMET KAYA' → 'Mehmet Kaya'; karışık yazılmış sözcük aynen kalır."""
    if ad is None:
        return ""
    return re.sub(r"[^\W\d_]+", _sozcuk_bicimi, str(ad).strip())


def _girildi(v):
    """Alan doldurulmuş mu? (boş metin ve Excel'deki NaN 'girilmedi' sayılır)"""
    if v is None:
        return False
    try:
        if pd.isna(v):
            return False
    except (TypeError, ValueError):
        pass
    return str(v).strip() != ""


# ── Doğum tarihi (Paket 9): yaşın yanına, yerine değil ──
DOGUM_KOLON = "Doğum Tarihi"


def tarih_coz(deger):
    """date / Timestamp / 'gg.aa.yyyy' → date; çözülemezse None."""
    if deger is None or (not isinstance(deger, (date, str)) and not hasattr(deger, "year")):
        return None
    try:
        if pd.isna(deger):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(deger, "date") and callable(getattr(deger, "date")) and not isinstance(deger, date):
        return deger.date()
    if isinstance(deger, date):
        return deger
    metin = str(deger).strip()
    for bicim in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            from datetime import datetime as _dt
            return _dt.strptime(metin, bicim).date()
        except ValueError:
            continue
    return None


def dogum_ceyregi(dogum):
    """Takvim doğum çeyreği: 1 = Ocak-Mart, 2 = Nisan-Haziran, 3 = Temmuz-Eylül, 4 = Ekim-Aralık."""
    d = tarih_coz(dogum)
    return None if d is None else (d.month - 1) // 3 + 1


def tam_yas(dogum, tarih):
    """O tarihteki tamamlanmış yaş (yıl)."""
    d, t = tarih_coz(dogum), tarih_coz(tarih)
    if d is None or t is None:
        return None
    return t.year - d.year - ((t.month, t.day) < (d.month, d.day))


def _yas_degeri(x):
    try:
        y = float(x)
        return y if y == y else None
    except (TypeError, ValueError):
        return None


def _e(x):
    return _html.escape("" if x is None else str(x))


def _sayi(x, ondalik=2, isaret=False):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return "—"
    return f"{f:+.{ondalik}f}" if isaret else f"{f:.{ondalik}f}".rstrip("0").rstrip(".") if ondalik else f"{f:.0f}"


def _tarih_gunu(t):
    """'gg.aa.yyyy' → date ya da None."""
    try:
        g, a, y = (int(x) for x in str(t).strip().split("."))
        return date(y, a, g)
    except (TypeError, ValueError):
        return None


def guvenli_float(deger):
    try:
        return float(deger)
    except (ValueError, TypeError):
        return 0.0


METIN_DEGISKEN_KALIBI = re.compile(r"\((?:Sağ/Sol|Geçti/Kalmadı|E/K)\)")


AYAR_DOSYA = "ayarlar.json"          # yerel tercih dosyası (ör. "bir daha gösterme")


def ayar_oku():
    """Yerel tercihler (ayarlar.json). Dosya yoksa ya da bozuksa boş sözlük — ekran yine açılır."""
    try:
        with open(AYAR_DOSYA, encoding="utf-8") as f:
            veri = _json.load(f)
        return veri if isinstance(veri, dict) else {}
    except (OSError, ValueError):
        return {}


def ayar_yaz(anahtar, deger):
    veri = ayar_oku()
    veri[anahtar] = deger
    try:
        with open(AYAR_DOSYA, "w", encoding="utf-8") as f:
            _json.dump(veri, f, ensure_ascii=False, indent=1)
    except OSError:
        pass


def _tablo_guvenli(df, kolonlar):
    """Dosya yoksa (None), boşsa ya da sütun eksikse: hata yerine boş/eksiksiz tablo."""
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    df = df.copy()
    for k in kolonlar:
        if k not in df.columns:
            df[k] = ""
    return df


def tablo_oku(yol):
    """xlsx'i okur; dosya yoksa ya da okunamıyorsa None (yönlendirme ekranı hata vermeden açılsın)."""
    if not os.path.exists(yol):
        return None
    try:
        return pd.read_excel(yol)
    except Exception:
        return None


def _dt_simdi():
    from datetime import datetime as _dt
    return _dt.now()


NOT_CIPLERI = ("Yorgun", "Sakatlık şüphesi", "Zemin kaygan", "Tekrar edildi")


def not_metni(n):
    """{"etiketler": [...], "metin": "..."} → "Yorgun; Zemin kaygan; serbest not" (xlsx "Notlar")."""
    n = n or {}
    return "; ".join([str(e) for e in n.get("etiketler", []) if str(e).strip()]
                     + ([str(n["metin"]).strip()] if str(n.get("metin", "") or "").strip() else []))


def not_coz(metin):
    """not_metni'nin tersi: hazır not adları etiket, kalan serbest metin."""
    parca = [p.strip() for p in str(metin or "").split(";") if p.strip()]
    return {"etiketler": [p for p in parca if p in NOT_CIPLERI],
            "metin": "; ".join(p for p in parca if p not in NOT_CIPLERI)}
