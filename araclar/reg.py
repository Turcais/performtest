"""Regresyon: 5 örnek sporcu — hesap, norm, rapor verisi ve raporların gelişim/konum dışındaki HTML'i."""
import sys, os, json, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from yukle import yukle
uyg, cikti = sys.argv[1], sys.argv[2]
d = os.path.dirname(os.path.abspath(cikti)) + "/calis_" + os.path.basename(cikti).split('.')[0]
os.makedirs(d, exist_ok=True); os.chdir(d)
sp = [dict(Ad="Ece", Soyad="K", Yaş=10, Cinsiyet="Kadın", **{"Doğum Tarihi": "15.04.2016", "Boy (cm)": 140, "Kilo (kg)": 33, "Spor Dalı": "Genel/Yok"}),
      dict(Ad="Mert", Soyad="T", Yaş=9, Cinsiyet="Erkek", **{"Doğum Tarihi": "02.11.2016", "Boy (cm)": 135, "Kilo (kg)": 30, "Spor Dalı": "Futbol"}),
      dict(Ad="Ali", Soyad="Y", Yaş=24, Cinsiyet="Erkek", **{"Boy (cm)": 178, "Kilo (kg)": 80, "Spor Dalı": "Güreş (Serbest)"}),
      dict(Ad="Ayşe", Soyad="D", Yaş=22, Cinsiyet="Kadın", **{"Boy (cm)": 165, "Kilo (kg)": 58, "Spor Dalı": "Voleybol"}),
      dict(Ad="Can", Soyad="B", Yaş=13, Cinsiyet="Erkek", **{"Boy (cm)": 158, "Kilo (kg)": 47, "Spor Dalı": "Judo"})]
pd.DataFrame(sp).to_excel("sporcular.xlsx", index=False)
o = dict(Kategori="-", Batarya="-", Branş="-", Notlar="", Oturum="", Yer="", Uygulayıcı="")
ts = []
for ad, yas, tarih, test, deg in [
    ("Ece K", 10, "01.03.2026", "20m Sürat (TSYT)", {"Süre (sn)": 4.6}), ("Ece K", 10, "01.09.2026", "20m Sürat (TSYT)", {"Süre (sn)": 4.4}),
    ("Ece K", 10, "01.09.2026", "Dikey Sıçrama (TSYT, kollar serbest)", {"Deneme 1 (cm)": 24, "Deneme 2 (cm)": 26, "En İyi Değer (cm)": 26}),
    ("Ece K", 10, "01.09.2026", "Boy ve Vücut Ağırlığı (TSYT)", {"Boy (cm)": 140, "Vücut Ağırlığı (kg)": 33}),
    ("Mert T", 9, "01.03.2026", "Flamingo Denge Testi", {"Düşme Sayısı (1 dk)": 6}), ("Mert T", 9, "01.09.2026", "Flamingo Denge Testi", {"Düşme Sayısı (1 dk)": 4}),
    ("Mert T", 9, "01.09.2026", "Esneklik (Uzan Eriş) — TSYT", {"Deneme 1 (cm)": 20, "Deneme 2 (cm)": 22, "En İyi Değer (cm)": 22}),
    ("Mert T", 9, "01.09.2026", "El Kavrama Kuvveti (TSYT)", {"Sağ El (kg)": 14, "Sol El (kg)": 13}),
    ("Ali Y", 24, "01.05.2026", "Sargent Dikey Sıçrama Testi (Duvar)", {"Ayakta Erişim (cm)": 225, "Sıçrama Erişimi — Deneme 1 (cm)": 270, "Sıçrama Yüksekliği — En İyi (cm)": 45}),
    ("Ali Y", 24, "01.09.2026", "Sargent Dikey Sıçrama Testi (Duvar)", {"Ayakta Erişim (cm)": 225, "Sıçrama Erişimi — Deneme 1 (cm)": 277, "Sıçrama Yüksekliği — En İyi (cm)": 52}),
    ("Ali Y", 24, "01.09.2026", "1RM Squat (Arka Çömelme)", {"1RM Squat (kg)": 150, "Rölatif Squat (kg/kg)": 1.875}),
    ("Ali Y", 24, "01.09.2026", "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)", {"Barfiks (tekrar)": 14}),
    ("Ayşe D", 22, "01.09.2026", "Sargent Dikey Sıçrama Testi (Duvar)", {"Ayakta Erişim (cm)": 210, "Sıçrama Erişimi — Deneme 1 (cm)": 248, "Sıçrama Yüksekliği — En İyi (cm)": 38}),
    ("Ayşe D", 22, "01.09.2026", "Yo-Yo IR1 (Genel)", {"Son Seviye": 15, "Son Tekrar": 4}),
    ("Can B", 13, "01.02.2026", "30m Sprint", {"Deneme 1 (sn)": 5.1, "En İyi Süre (sn)": 5.1, "Hız (m/s)": 5.88}),
    ("Can B", 13, "01.08.2026", "30m Sprint", {"Deneme 1 (sn)": 4.9, "En İyi Süre (sn)": 4.9, "Hız (m/s)": 6.12}),
    ("Can B", 13, "01.08.2026", "Mekik (Sit-Up) — 1 Dakika (Genel)", {"Mekik (tekrar)": 38})]:
    ts.append({**o, "Sporcu": ad, "Test Yaşı": yas, "Tarih": tarih, "Test": test, **deg})
for i in range(24):                                     # havuz: 12-13 yaş erkek 30m sprint (Can için n ≥ 20)
    sp.append(dict(Ad=f"H{i}", Soyad="Z", Yaş=13, Cinsiyet="Erkek")); ts.append({**o, "Sporcu": f"H{i} Z", "Test Yaşı": 13, "Tarih": "01.08.2026", "Test": "30m Sprint", "En İyi Süre (sn)": 4.6 + i * 0.04})
pd.DataFrame(sp).to_excel("sporcular.xlsx", index=False); pd.DataFrame(ts).to_excel("test_sonuclari.xlsx", index=False)
g = yukle(uyg)

def temiz(x):
    if isinstance(x, float):
        return None if x != x else round(x, 9)
    if isinstance(x, dict):
        return {str(k): temiz(v) for k, v in x.items() if k != "birim"}
    if isinstance(x, (list, tuple)):
        return [temiz(v) for v in x]
    if hasattr(x, "item"):
        return temiz(x.item())
    return x if isinstance(x, (int, str, bool, type(None))) else repr(x)

def html_kes(h):
    h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r"<h2>Kendi gelişimi</h2>.*?(?=<h2>Bu bilgiyi okurken</h2>)", "", h, flags=re.S)
    h = re.sub(r"<h2>Kendi gelişimi ve grup içi konum</h2>.*?(?=<h2>7\. )", "", h, flags=re.S)
    return h

sonuc = {}
for s in ["Ece K", "Mert T", "Ali Y", "Ayşe D", "Can B"]:
    v = g["rapor_verisi"](s)
    r = {k: temiz(v[k]) for k in ("zp", "esl", "bilesikler", "testler", "normsuz", "sinirlar", "kaynaklar", "puan")}
    r["gelisim"] = [temiz({k: x[k] for k in ("test", "degisken", "olcumler", "fark", "yuzde", "yon", "iyi_yonde", "ilk")}) for x in v["gelisim"]]
    r["konum"] = [temiz({k: x.get(k) for k in ("durum", "n", "deger", "ortalama", "degerler", "yuzdelik", "ceyrek", "p10", "p90", "bant", "yon")}) for x in v["konum"]]
    r["veli"] = html_kes(g["veli_raporu_html"](v)); r["antrenor"] = html_kes(g["antrenor_raporu_html"](v))
    sonuc[s] = r
df = pd.read_excel("test_sonuclari.xlsx")
spd = {f"{a['Ad']} {a['Soyad']}": a for a in sp}
nd = []
for _, row in df.iterrows():
    b = spd[row["Sporcu"]]
    vals = {k: row[k] for k in df.columns if k not in ("Sporcu", "Test", "Tarih", "Kategori", "Batarya", "Branş", "Notlar", "Oturum", "Yer", "Uygulayıcı", "Test Yaşı") and pd.notna(row[k])}
    nd.append(temiz([row["Test"], g["turetilmis_degerler"](row["Test"], {k: str(v) for k, v in vals.items()}, b, b.get("Kilo (kg)", 0) or 0),
                     {k: [g["normatif_degerlendir"](k, v, b["Cinsiyet"], b.get("Spor Dalı", "Genel/Yok"), row["Test"], yas=row["Test Yaşı"]),
                          g["yas_persentil_bul"](row["Test"], k, row["Test Yaşı"], b["Cinsiyet"], v)] for k, v in vals.items()}]))
sonuc["_hesap"] = nd
json.dump(sonuc, open(cikti, "w"), ensure_ascii=False, indent=0, sort_keys=True, default=str)
print("yazıldı", cikti, sum(len(json.dumps(v, default=str)) for v in sonuc.values()))
