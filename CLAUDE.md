# Ölçüt — devralma notu

Streamlit uygulaması, sporcu performans takibi: test oturumu girişi, yaşa/cinsiyete göre norm karşılaştırma, gelişim takibi, sporcu/oturum karşılaştırması, antrenör ve veli raporu. Şu an **Paket 38j** (son etiket `v107-38h`).
Kullanıcı: Ertuğrul (spor bilimleri doktora öğrencisi, Gazi Üniversitesi). **Türkçe yazın, adım adım açıklayın.**
Veri dosyaları çalışma klasöründen okunur, git'e girmez (`.gitignore`): `sporcular.xlsx`, `test_sonuclari.xlsx`, `ilgi_anketi.xlsx`, `ayarlar.json`, `oturum_taslagi.json`; uygulamanın ürettiği `.streamlit/config.toml` da girmez.

## Yapı (Bölme Aşama 1–2 tamam; davranış bölmeden önceki v101-38f ile aynı)
- `uygulama.py` (~550 satır): sayfa yapılandırması, tema, yan menü, sayfa yönlendirme. Uzun içe aktarma listeleri testlerin `app["ad"]` erişimi içindir.
- `olcut/` — katmanlı modüller; her modül yalnız kendinden AŞAĞIDAKİLERİ içe aktarır (test_45a, `_OLCUT_KATMAN`). Sıra:
  `ortak` → `disa_aktarma` (PDF / CSV / Excel baytı) → `tema` → `esik` (HFZ) → `katalog_islemleri` (son TEST_KATALOGU burada) → `gorseller/cizim` → `gorseller/hareketler` → `gorseller/sahneler` → `norm` (son NORMATIF ve NORMATIF_YAS burada) → `analiz` → `kayit` → `raporlar` → `oneri` → `karsilastirma` → `bilesenler` → `sayfalar/*` (sayfalar birbirini içe aktarmaz).
  Yeni modül önce `_OLCUT_KATMAN`'a yazılır. Hiçbir modül `uygulama`'yı içe aktarmaz.
- `veri/` — yalnız sabit değer (test_44a): `katalog`, `normlar_yas`, `normlar_tsyt`, `normlar_kategorik` (Kademe 2 örneklemleri + künyeler), `metinler`, `brans_profilleri`. Kaynak/künye sabitleri normlarla aynı dosyada.
- `araclar/` — `reg.py` (regresyon, 5 örnek sporcu), `yukle.py` (yükleyici), `esitlik.py` (sürüm ↔ çalışma kopyası derin eşitlik + modül tutarlılığı + akış sonrası yerinde değişiklik), `sayfa_goruntusu.py` (her sayfanın ekran öğelerini döker; sürümler arası karşılaştırma).

## Komutlar
- Çalıştırma: `python -m streamlit run uygulama.py` (veri dosyalarının olduğu klasörden; başka klasörden tam yolla da çalışır). Kısa `streamlit` komutu bu bilgisayarda PATH'te değil.
- Testler: `python -m pytest test_uygulama.py -q` (~6–8 dk; 184 test). Windows'ta Türkçe çıktı için `PYTHONUTF8=1`.
- Regresyon: `python araclar/reg.py <TAM YOL>\uygulama.py cikti.json` (araç çalışma klasörünü değiştirdiği için tam yol). Taban: `v101-38f` çıktısı.
- Derin eşitlik: `python araclar/esitlik.py <git sürümü> [--akis]` · Sayfa görüntüsü: `python araclar/sayfa_goruntusu.py uygulama.py cikti.json`.

## Etiketler
`v100-testler-yesil` (17 kırmızı → yeşil, Paket 38e) · `v101-38f` (veli raporu: en iyi deneme, yetişkin dili, sapma derecesi; regresyon tabanı) · `v102-temel`, `v103-gorseller`, `v104-cekirdek`, `v105-sayfalar` (Bölme Aşama 2 grupları) · `v106-38g` (karşılaştırma ekranı, dil, normsuz olağandışı değer) · `v107-38h` (grafik renkleri Streamlit sürümüne göre; açılış uyarısı yok).

## Çalışma kuralları
- Her değişiklikten önce git commit, sonra değişiklik. Sonra: söz dizimi, testler, regresyon (yalnız paketin dokunduğu yer değişmeli; fark varsa açıkla). Paket adlandırması sürüyor (38g'den sonra 38h…); her paket tek commit.
- Renkler yalnızca `olcut/tema.py`'de; grafik rengi `grafik_renk()` ile (Streamlit tema yuvaları `#00000N`); 8 haneli hex veya rgba grafik rengine verilmez (kaynak-tarama testi 17d/41f).
- Grafik tema yuvaları (38h): Streamlit 1.58 `chartCategoricalColors`/`chartSequentialColors`'ı yalnız `[theme]`'de tanır; `tema_toml()` kurulu sürüme bakıp ya tema başına ya `[theme]`'e iki temanın karışımını yazar. Yazı/çizgi Streamlit'in kendi tema grileri (`#000037`, `#000035`). Streamlit betik klasöründeki `.streamlit/config.toml`'u da okur; kod değişince açık eski sunucu dosyayı eski içerikle yeniden yazar → sunucuyu yeniden başlatın.
- Norm kaynağı: yalnızca açık yayımlanmış/resmî kaynaklar; kaynağı kayda yaz. Yeniden kullanım izni belirsiz üçüncü taraf materyali kullanıcı karar vermeden ekleme.
- 11 yaş altında grup içi sıralama ve "daha iyi/kötü" etiketi yok. Hiçbir raporda başka çocuğun adı geçmez. Grupta n < 20 ise yüzdelik yok.
- Veli dili: aralık dili ("çoğu A–B arasında, aralığın içinde / biraz / belirgin şekilde / çok üstünde-altında"; çok uzaksa "Değer doğru mu?"), sınıf etiketi yok, yargılayıcı cümle yok. Yetişkinde "Çocuğunuz…" yerine "Sporcu…", çocuk/büyüme dili yok.
- Erişilebilirlik: yazı ≥14 px, dokunma hedefi ≥44 px, kontrast ≥4.5:1, renk tek başına anlam taşımaz (simge + sözcük), varsayılan açık tema.
- Test Oturumu / Test Uygula: ölçüm sırasında karşılaştırma gösterilmez; aykırı değerde engelleme değil uyarı (normlu: ≈P1–P99; normsuz: dünya rekoru ötesi ya da önceki ölçümün ×3 / ÷3'ü).

## Sonuçlar ve Karşılaştırma (Paket 38g)
Sonuçlar sayfasının üstünde segment: **Sonuçlar | Karşılaştırma** (`olcut/sayfalar/karsilastirma.py`, hesap `olcut/karsilastirma.py`).
- *Sporcular arası*: iki "Sporcu seç" sütunu (Grup A / B; onay kutusu, arama, Tümünü seç / Temizle; B boşsa yalnız A içinde), oturum süzgeci (varsayılan Tüm oturumlar), ortak testler, "Karşılaştır" (basılana kadar sonuç pasif; seçim değişince "sonuç eski"). Tablo (tarih, değer, birim) + grafik + grup ortalaması/aralığı; karışık yaş/cinsiyette uyarı ve isteğe bağlı Z.
- *Oturumlar arası*: iki "Oturum seç" sütunu (ad + tarih + sporcu sayısı); aynı sporcu için Önce / Sonra / Fark, yön testin yönünden (simge + sözcük); "İstatistik göster": n ≥ 6 Wilcoxon işaretli sıra + eşleştirilmiş sıra-iki serili r, n < 6 yalnız tanımlayıcı.
- Eski "Kapsam" radio'su kalktı; mantığı (`kayit.oturum_degerleri`, `oturumlar_arasi_fark`) yeni ekranın altında kullanılır.

## PDF ve dışa aktarma (Paket 38i)
- Raporlar: "PDF olarak indir" (`olcut/sayfalar/raporlar.py` `rapor_indirme`). Ekrandaki rapor HTML'i aynen çevrilir (`disa_aktarma.pdf_cevir`); sıra: kurulu Edge/Chrome başsız yazdırma → WeasyPrint → xhtml2pdf; hiçbiri yoksa yazdırmaya hazır HTML + talimat. Tarayıcı yolunda süreç + dosya bekleme toplamı en çok `PDF_SURE_SN` = 20 sn. A4 ve kart bölünmemesi `RAPOR_CSS`'teki `@page` / `@media print`'te. Dosya adı `Veli_raporu_<Ad_Soyad>_<GGAAYYYY>.pdf` (`guvenli_dosya_adi`).
- Karşılaştırma: "Tabloyu Excel olarak indir" + "CSV olarak indir" (UTF-8 BOM, `;`, ondalık virgül; 38j: metin hücresi `= + - @` ya da sekmeyle başlarsa başına `'`). Oturum sütunlarında oturumun adı (etiket değil). Tablolar `karsilastirma.sporcular_arasi_disa` / `oturumlar_arasi_disa` / `grup_ozeti_disa` / `istatistik_disa`: ekrandaki sonuçtan yazılır, hesap yok; sıra/yüzdelik sütunu yok, çeyrekler yalnız her grupta n ≥ 20.

## Elle deneme: örnek veri
`Desktop\Olcut_Demo\` — hayali 17 sporcu (soyadı "Demo"). Çocuklar 9–11 yaş: Elif, Mert, Zeynep, Kaan, Defne, Emre ve yeni beş çocuk Ali, Ece, Can, Nisa, Burak; yetişkin/genç 16–28 yaş: Barış, Selin, Onur, Ceren, Tolga, Aylin. İki oturum: "Demo · Ön Test" (15.09.2026) ve "Demo · Son Test" (25.10.2026), her biri 17 sporcu / 201 kayıt (toplam 402; dosyadan sayıldı). İlgi anketi 11 çocukta dolu.
- Yeni beş çocuğun fiziksel profili ayrı bir branş grubuna yakın (1. sıra, 38j hesabı): Ali → Top sporları, Ece → Raket sporları, Can → Yüzme, Nisa → Jimnastik, Burak → Dövüş sporları. İlgi ile fiziksel profil Ali ve Can'da uyumlu; Ece ve Nisa'da bilerek uyumsuz; Burak'ta ilgi fiziksel sıralamada 3. sırada (kısmi).
- Eski 12 sporculuk veri: `Olcut_Demo\yedek_12sporcu\`.

Gerçek veriye dokunmadan denemek için uygulamayı bu klasörden başlatın:
`cd ..\Olcut_Demo` → `python -m streamlit run ..\Olcut\uygulama.py`

## Şimdi yapılacaklar (sırayla)
1. **Elle deneme** (demo verisiyle): Sonuçlar → Karşılaştırma (iki sekme, pasif/eski durumu, 11 yaş altı ve karışık uyarıları, Wilcoxon), Test Oturumu'nda normsuz testte ×3 uyarısı, yaşıt kartı ve veli raporunda "Değer doğru mu?" (sabit not yok). Telefon genişliğinde iki sütunun alt alta dizildiğine bak.
2. **v100/38d'nin kalan doğrulaması**: oturum adı alanı, Sonuçlar'da oturum süzgeci, odak çerçevesi tek çerçeve (dış kutuda).
3. Temizlik (davranışa dokunmadan): testler `olcut` modüllerinden doğrudan içe aktarırsa `uygulama.py`'deki uzun içe aktarma listeleri kısalır.

## Tasarım referansı
Arayüz taslağı (Adım 1–4, Sıradaki kipi, Sonuçlar, Veli kartı): https://claude.ai/artifact/GX76RBE4t77hFPoFrDYuaZ

## Bekleyen işler
Yeni test paketleri (FMS, antropometri, kendi hokey/ragbi protokolleri, kaleci testleri), pozisyon ve amaç alanı, norm genişletme (bacak presi, barfiks, şınav, mekik), kuvvet platformu içe aktarma (RFD/GRF). SQLite'a geçiş yok (xlsx yeterli).
- (karar bekliyor) Karşılaştırma dışa aktarımında sporcu adı yerine kod seçeneği.
- (karar bekliyor) Branş grubu eşleştirmesinde gruplar arası uzaklık farkları çok küçük: ayırt edilemezlik kuralı (ör. ilk iki grubun farkı eşiğin altındaysa "ayırt edilemedi").
