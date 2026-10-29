# Ölçüt — devralma notu

Streamlit tek dosya uygulaması (`uygulama.py`, ~22.000 satır, şu an **v100** = eski adıyla "uygulama (100)"). Sporcu performans takibi: test oturumu girişi, yaşa/cinsiyete göre norm karşılaştırma, gelişim takibi, antrenör ve veli raporu.
Veri dosyaları (git'e girmez, `.gitignore`'da): `sporcular.xlsx`, `test_sonuclari.xlsx`, `ilgi_anketi.xlsx`, `ayarlar.json`, `oturum_taslagi.json`.
Kullanıcı: Ertuğrul (spor bilimleri doktora öğrencisi, Gazi Üniversitesi). **Türkçe yazın, adım adım açıklayın.**

Çalıştırma: `streamlit run uygulama.py`
Testler: `python -m pytest test_uygulama.py -q` (varsayılan olarak klasördeki `uygulama.py`'yi okur; başka sürüm için `UYGULAMA=dosya.py`).
Regresyon (5 örnek sporcu): `python araclar/reg.py uygulama.py cikti.json` (araclar/yukle.py yardımcı yükleyicidir).

## Çalışma kuralları
- Her değişiklikten önce git commit, sonra değişiklik. Değişiklik sonrası: söz dizimi (`python -c "import ast;ast.parse(open('uygulama.py',encoding='utf-8').read())"`), testler, regresyon.
- Eski "yama dosyası" akışı bitti; doğrudan dosyayı düzenleyin. Paket adlandırması sürüyor (38d'den sonra 38e…); her paket tek commit.
- Renkler yalnızca `grafik_renk()` ile (Streamlit tema yuvaları `#00000N`); 8 haneli hex veya rgba grafik rengine verilmez (kullanıcının Plotly sürümü reddediyor; kaynak-tarama testi var).
- Norm kaynağı: yalnızca açık yayımlanmış/resmî kaynaklar; kaynağı kayda yaz. Yeniden kullanım izni belirsiz üçüncü taraf materyali kullanıcı karar vermeden ekleme.
- 11 yaş altında grup içi sıralama yok. Hiçbir raporda başka çocuğun adı geçmez.
- Veli dili: aralık dili ("çoğu A–B arasında, aralığın içinde/üstünde/altında"), sınıf etiketi yok, yargılayıcı cümle yok. Yetişkinde "Çocuğunuz…" yerine "Sporcu…".
- Erişilebilirlik: yazı ≥14 px, dokunma hedefi ≥44 px, kontrast ≥4.5:1, renk tek başına anlam taşımaz (simge + sözcük), varsayılan açık tema.
- Test Oturumu: ölçüm sırasında karşılaştırma gösterilmez; aykırı değerde engelleme değil uyarı.

## Şimdi yapılacaklar (sırayla)
1. **Testleri yeşile çek.** v99'da 15 test kırmızıydı (34j, 37c, 37d, 38a, 39e, 40e, 41d, 41f, 42a, 42b, 42e ve diğerleri); hepsi eski beklenti gibi görünüyor, ama her birini tek tek incele; gerçek hata olanı ayrıca bildir.
2. **v100'ü doğrula** (Paket 38d): oturum adı alanı, Sporcu Karşılaştırma'da Kapsam (Bireysel / Tek oturum / Oturumlar arası, aynı sporcu için fark), Sonuçları Görüntüle'de oturum filtresi, odak çerçevesi tek çerçeve (dış kutuda).
3. Veli raporunda aynı test için üst kutu ile alt tabloda farklı değer sorunu (önceki rapor: atlama 50/60 cm, otur-uzan 50/54 cm) çözüldü mü: örnek sporcu için veli raporu üret, her testin tek yerde ve doğru ölçümle çıktığını göster.
4. Düşme sayısı testlerinde birim ("düşme") ve yön ("daha az iyi") doğru mu kontrol et.

## Sonra: dosyayı böl (davranış DEĞİŞMEDEN)
- Aşama 1: Verileri koddan çıkar (test kataloğu, norm tabloları, metinler → JSON/ayrı veri modülleri).
- Aşama 2: Kodu sayfa/işlev bazında modüllere ayır (norm motoru, grafikler, Test Oturumu, Sonuçlar, Veli raporu, Sporcu Girişi, ortak yardımcılar).
- Her aşamadan sonra testler + regresyon çıktısı eskisiyle AYNI olmalı; fark varsa açıkla.
- SQLite'a geçiş bu aşamada YOK (xlsx şimdilik yeterli).

## Tasarım referansı
Arayüz taslağı (Adım 1–4, Sıradaki kipi, Sonuçlar, Veli kartı): https://claude.ai/artifact/GX76RBE4t77hFPoFrDYuaZ

## Bekleyen işler (bölmeden sonra)
Yeni test paketleri (FMS, antropometri, kendi hokey/ragbi protokolleri, kaleci testleri), pozisyon ve amaç alanı, norm genişletme (bacak presi, barfiks, şınav, mekik), tek tıkla PDF indirme, kuvvet platformu içe aktarma (RFD/GRF).
