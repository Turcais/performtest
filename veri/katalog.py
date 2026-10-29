"""
Test kataloğu: kategori → alt başlık → (branş) → test → protokol, kaynak, değişkenler.

Bölme Aşama 1: uygulama.py'den birebir taşındı (davranış değişmedi). Yalnız sabit değerler; fonksiyon, çağrı ya da
içe aktarma yok (test_44a denetler).
"""


TEST_KATALOGU = {
    # ════════════════════════════════════════════════════════════
    # TÜRKİYE SPORTİF YETENEK MODELİ (TSYT) — Paket 9, çekirdek batarya
    # Protokoller: GSB TSYT uygulama talimatı belgeleri + norm kitabı Bölüm 7 (s. 86-90).
    # Normlar: NORMATIF_YAS'ta TSYT_NORMLARI ile (yaş × cinsiyet × doğum çeyreği × 19 persentil).
    # ════════════════════════════════════════════════════════════
    "Türkiye Sportif Yetenek Modeli (TSYT)": {
        "TSYT Bataryası — 7-11 Yaş (GSB)": {
            "_kunye": {
                "gelistiren": "T.C. Gençlik ve Spor Bakanlığı — Türkiye Sportif Yetenek Taraması ve Spora Yönlendirme Programı (Millî Eğitim Bakanlığı iş birliği)",
                "ulke": "Türkiye (81 il, 922 ilçe)",
                "yil": "Program 2017-2018 eğitim yılından beri; norm kitabı 2023 (2018-2023 verisi)",
                "hedef_yas": "Tarama: ilkokul 3. sınıf. Normlar: 7-11 yaş, erkek/kadın, doğum çeyreğine göre ayrı",
                "yas_araligi": (7, 11),                      # hedef_yas: "Normlar: 7-11 yaş"
                "yayginlik": "Türkiye'nin ulusal yetenek taraması. Norm kitabında 3.548.689 veri kullanılmıştır. Bu bölüm genel taramanın testlerini (antropometri, esneklik, dikey sıçrama, el kavrama, geriye sağlık topu, çeviklik, 20 m sürat) ve kapsamlı test aşamasının koordinasyon parkuru ile mekik koşusunu içerir. Koordinasyon parkuru ve mekik koşusu için kitapta norm tablosu yoktur."
            },

            "Boy ve Vücut Ağırlığı (TSYT)": {
                "protokol": """
**Amaç:** Boy uzunluğunu ve vücut ağırlığını TSYT talimatına göre ölçmektir.

**Ekipman:** Boy ölçüm cetveli (stadiometre), tartı.

**Uygulama:**
1. **Boy:** Çocuk ayakkabısız ve spor kıyafetiyle durur. Topuk, kalça, sırt ve başın arka bölümünün iz düşümü aynı dikey doğrultudadır; sırt cetvel hizasındadır ama cetvele değmez.
2. Baş, gözler karşıya bakacak şekilde tutulur. Çocuk derin bir nefes alıp tutar; ölçüm bu anda alınır (cm).
3. **Vücut ağırlığı:** Çocuk ayakkabısız ve spor kıyafetiyle tartıya çıkar, değer sabitlenene kadar hareketsiz durur (kg).

**Skorlama:** Boy (cm) ve vücut ağırlığı (kg). Tanımlayıcı ölçülerdir; iyi/kötü yorumu yapılmaz.

**Normatif:** TSYT norm tabloları (7-11 yaş, erkek/kadın, doğum çeyreğine göre): boy Tablo 9.x.1, vücut ağırlığı Tablo 9.x.3 (x = 1 → 7 yaş … 5 → 11 yaş). Doğum tarihi biliniyorsa çocuğun kendi çeyreğinin tablosu, bilinmiyorsa dört çeyreğin ortalaması kullanılır.
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 86; norm tabloları 9.1.1-9.5.3)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı; kitapta TSYTSYP Uygulama Talimatı, 2022 olarak anılır).",
                "degiskenler": ["Boy (cm)", "Vücut Ağırlığı (kg)"]
            },

            "Oturma Yüksekliği (TSYT)": {
                "protokol": """
**Amaç:** Oturma yüksekliğini (gövde + baş uzunluğu) TSYT talimatına göre ölçmektir.

**Ekipman:** Ölçüm sandalyesi, telemetre (baş üstü ölçer).

**Uygulama:**
1. Çocuk ölçüm sandalyesine oturur; dizler 90°'dedir.
2. Kalça, sırt ve başın arka bölümünün iz düşümü aynı dikey doğrultudadır; gözler karşıya bakar.
3. Telemetre baş üstüne indirilir ve değer kaydedilir (cm).

**Skorlama:** Oturma yüksekliği (cm). Tanımlayıcı ölçüdür.

**Not:** TSYT norm değerleri (10 yaş medyanı ≈ 73-75 cm) oturma yüzeyinden ölçülen yüksekliğe karşılık gelir. Uygulamadaki FSC "Oturma Yüksekliği" testi Ankara normlarıyla ayrı tutulur; TSYT normu yalnızca bu teste bağlıdır.

**Normatif:** TSYT Tablo 9.x.7 (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 86; norm tabloları 9.1.7-9.5.7)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Oturma Yüksekliği (cm)"]
            },

            "Kulaç Uzunluğu (TSYT)": {
                "protokol": """
**Amaç:** Kulaç uzunluğunu (kollar yana açıkken iki orta parmak ucu arasındaki mesafe) ölçmektir.

**Ekipman:** Duvara sabitlenmiş ya da yatay tutulan ölçüm cetveli/şerit metre.

**Uygulama:**
1. Çocuğun sırtı ölçüm yüzeyine dayalıdır; kalça, sırt ve başın arka bölümünün iz düşümü aynı dikey doğrultudadır.
2. Kollar, avuç içleri karşıya bakacak şekilde, yere paralel olarak yanlara gergin açılır.
3. İki kolun orta parmak uçları arasındaki uzaklık ölçülür ve kaydedilir (cm).

**Skorlama:** Kulaç uzunluğu (cm). Tanımlayıcı ölçüdür.

**Not:** Protokol belgesi ölçümü ayakta (topuk, kalça, sırt ve baş aynı dikey doğrultuda), norm kitabı oturarak (ölçüm sandalyesinde dizler 90°) tarif eder. Kollar yere paralel açıldığı için ölçülen mesafe aynıdır; ayakta ya da oturarak, kurumunuzun uyguladığı biçim kayda not edilmelidir.

**Normatif:** TSYT Tablo 9.x.9 (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 87; norm tabloları 9.1.9-9.5.9)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Kulaç Uzunluğu (cm)"]
            },

            "Esneklik (Uzan Eriş) — TSYT": {
                "protokol": """
**Amaç:** Gövde ve arka bacak (hamstring) esnekliğini TSYT esneklik sehpasıyla ölçmektir.

**Ekipman:** TSYT esneklik sehpası (üzerinde kayar cetvel bulunan otur-uzan sehpası).

**Uygulama:**
1. Çocuk ayakkabısız oturur; iki ayak tabanını esneklik sehpasının dayanma bölümüne tam olarak dayar.
2. Dizler gergin kalır; kalça ekleminden bükülerek, nefes vererek, iki kolla öne uzanır.
3. Sehpanın üzerindeki cetveli parmak uçlarıyla yavaş ve akıcı biçimde iterek en uzak noktaya götürür ve orada birkaç saniye bekler.
4. 5-10 sn dinlenme verilir, cetvel başlangıç noktasına çekilir ve ikinci deneme yapılır.
5. İki denemenin değeri ayrı ayrı kaydedilir (cm).

**Skorlama:** Cetvelin itildiği nokta (cm). Yüksek değer = iyi.

**⚠️ Sıfır noktası:** TSYT talimatı ve norm kitabı, cetvel ölçeğinin sıfırının ayak tabanına göre nerede olduğunu YAZMAZ (talimat metninde ve fotoğrafında ölçek görünmüyor). Bu yüzden TSYT normu yalnızca TSYT esneklik sehpasıyla alınan ölçüme bağlanır. Eurofit otur-uzan (ayak tabanı 15 cm), FitnessGram/ALPHA Back-Saver (ayak tabanı 22.9 cm) ya da başka bir sehpayla alınan değer bu normla karşılaştırılmaz; o testler katalogda ayrı yer alır. Norm tablolarında en düşük değer 4-5 cm, en yüksek 50 cm'dir; ölçek negatif değer içermez.

**Not:** Kitap, iki denemeden hangisinin norma girdiğini yazmaz. Uygulama her denemeyi aynı normla ayrı değerlendirir.

**Normatif:** TSYT Tablo 9.x.5 (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 86; norm tabloları 9.1.5-9.5.5)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },

            "Dikey Sıçrama (TSYT, kollar serbest)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü, kolların serbest kullanıldığı aktif sıçramayla ölçmektir.

**Ekipman:** Sıçrama matı (temas süresinden yükseklik hesaplayan).

**Uygulama:**
1. Test ayakkabılı yapılır. Çocuk sıçrama matının üzerinde, ayaklar omuz genişliğinde açık, dik durur.
2. Hızla dizlerini bükerek çöker ve hiç beklemeden, kollarını da kullanarak, olabildiğince yükseğe sıçrar.
3. İnişte dizlerini bükmeden sıçradığı noktaya düşmeye dikkat eder. Sıçrama noktasından uzağa düşerse ölçüm kaydedilmez ve deneme tekrarlanır.
4. İki deneme yapılır; iki değer de kaydedilir (cm).

**Skorlama:** Sıçrama yüksekliği (cm). Yüksek değer = iyi.

**Not:** Kollar serbesttir (kol salınımı yüksekliği artırır). Uygulamadaki "eller belde" CMJ testleriyle karşılaştırılmaz. Kitap iki denemeden hangisinin norma girdiğini yazmaz; her deneme aynı normla ayrı değerlendirilir.

**Normatif:** TSYT Tablo 9.x.11 (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 87; norm tabloları 9.1.11-9.5.11)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },

            "El Kavrama Kuvveti (TSYT)": {
                "protokol": """
**Amaç:** Sağ ve sol el kavrama kuvvetini el dinamometresiyle ölçmektir.

**Ekipman:** Kilogram ölçekli el dinamometresi.

**Uygulama:**
1. Uygulayıcı dinamometrenin kilogram biriminde olduğunu kontrol eder ve sıkma kolu aralığını çocuğun parmaklarının ikinci boğumuna göre ayarlar.
2. Çocuk bir kez hafifçe sıkarak testi tanır, ardından biraz dinlenir.
3. Ayakta, kol gergin ve aşağıya uzanmış durumdayken dinamometreyi olanca kuvvetiyle sıkar.
4. Bir kez sol, bir kez sağ elle yapılır; iki değer ayrı ayrı kaydedilir (kg).

**Skorlama:** Sağ el ve sol el kavrama kuvveti (kg). Yüksek değer = iyi.

**Not:** Her el için tek ölçüm alınır. Eurofit/ALPHA el kavrama protokollerinden (dirsek açısı, deneme sayısı) farklıdır; normları birbirine bağlanmaz.

**Normatif:** TSYT Tablo 9.x.13 (sağ el) ve 9.x.15 (sol el) (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 87; norm tabloları 9.1.13-9.5.15)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Sağ El (kg)", "Sol El (kg)"]
            },

            "Geriye Sağlık Topu Atma (TSYT)": {
                "protokol": """
**Amaç:** Tüm vücut patlayıcı gücünü (kalça-gövde-kol zinciri) geriye doğru sağlık topu atışıyla ölçmektir.

**Ekipman:** 1 kg sağlık topu (çevresi 60-70 cm), şerit metre, atış çizgisi.

**Uygulama:**
1. Çocuk sırtı atış alanına dönük, ayaklar omuz genişliğinde açık durur; topu iki eliyle önde tutar.
2. Dizlerini hafifçe büker, ardından vücudunu hızla gererek topu iki koluyla baş üzerinden geriye doğru fırlatır.
3. Atış açısının yaklaşık 45° olması sağlanmaya çalışılır.
4. Atış sırasında çizgiyi aşarak geriye düşen çocuğun atışı tekrarlanır; kontrolsüz atışlar dikkate alınmaz.
5. Uygun açı ve hızla yapılan iki deneme kaydedilir (cm).

**Skorlama:** Atış mesafesi (cm). Yüksek değer = iyi.

**Not:** "Top Fırlatma Testi (Latorre)" farklı bir protokoldür (top ağırlığı, atış yönü ve duruş farklı); TSYT normu yalnızca bu teste bağlıdır. Protokol belgesinde "atış alanı açısı 30" olarak geçen değer (derece işareti metinde kaybolmuş olabilir) atışın yapıldığı alanın genişliğini, kitaptaki 45° ise atış açısını tarif eder. Kitap iki denemeden hangisinin norma girdiğini yazmaz; her deneme aynı normla ayrı değerlendirilir.

**Normatif:** TSYT Tablo 9.x.17 (7-11 yaş, erkek/kadın, doğum çeyreğine göre).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 88; norm tabloları 9.1.17-9.5.17)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },

            "Çeviklik — Pro Agility 5-10-5 (TSYT)": {
                "protokol": """
**Amaç:** Yön değiştirme hızını (çevikliği) ölçmektir. TSYT'nin çeviklik testi Pro Agility'dir (5-10-5 yard mekik).

**Ekipman:** Fotosel (başlangıç-bitiş), iki işaret hunisi, ölçüm şeridi.

**Uygulama:**
1. Parkur kurulur: başlangıç-bitiş fotoselinin sağında ve solunda **4,57 m** (5 yard) uzaklığa birer işaret hunisi konur.
2. Çocuk parkurun orta çizgisinin 50 cm gerisinde, koşu yönüne yan duruş pozisyonunda bekler; duruş ve ilk koşu yönü çocuğun tercihidir.
3. Çıkış komutuyla başlama yönündeki hedefe koşar ve eliyle dokunur.
4. Hızla dönerek tam ters yöndeki hedefe (9,14 m) koşar ve eliyle dokunur.
5. Tekrar dönüp orta çizgiyi (başlangıç-bitiş) hızla geçerek testi bitirir. Toplam mesafe 18,28 m'dir.
6. Uygulayıcı, ellerin hedeflere dokunduğunu dikkatle izler.

**Skorlama:** Süre (sn), fotoselle. Düşük değer = iyi.

**Not:** Bu test Eurofit "10x5m Mekik Koşusu" ve ALPHA/PREFIT "4x10m Mekik Koşusu" ile AYNI DEĞİLDİR (mesafe, dönüş sayısı ve başlangıç pozisyonu farklı); normları birbirine bağlanmaz.

**Normatif:** TSYT Tablo 9.x.19 (7-11 yaş, erkek/kadın, doğum çeyreğine göre). Kitap persentilleri performans yönünde verir (95 = en hızlı); uygulama bunları ham değer sırasına çevirerek saklar.
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 88, Resim 7.8; norm tabloları 9.1.19-9.5.19)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Süre (sn)"]
            },

            "20m Sürat (TSYT)": {
                "protokol": """
**Amaç:** Hızlanma ve sürati 20 m koşuyla ölçmektir.

**Ekipman:** Fotosel (başlangıç ve 20 m'de bitiş), güvenlik için bitiş sonrasında minder/yumuşak malzeme.

**Uygulama:**
1. Çocuk, başlangıç fotoselinin 1 m gerisindeki çıkış çizgisine bir ayağının ucunu koyar; fotosele dokunmaz.
2. Hazır olunca ileriye doğru en yüksek süratle koşar.
3. 20 m ilerideki varış çizgisini yavaşlamadan geçer.

**Skorlama:** Süre (sn), fotoselle. Düşük değer = iyi.

**Not:** Başlangıç 1 m geride olduğundan süre "uçan" bir başlangıcı içerir; duran başlangıçlı 20 m testleri (ör. KMS, Latorre) ile karşılaştırılmaz.

**Normatif:** TSYT Tablo 9.x.21 (7-11 yaş, erkek/kadın, doğum çeyreğine göre). Kitap persentilleri performans yönünde verir (95 = en hızlı).
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 88; norm tabloları 9.1.21-9.5.21)\nGençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Antropometrik ölçüm ve performans test protokolleri (uygulama talimatı).",
                "degiskenler": ["Süre (sn)"]
            },

            "Koordinasyon Parkuru (TSYT)": {
                "protokol": """
**Amaç:** Genel motor koordinasyonu (yuvarlanma, denge, top becerileri, sekme, engel geçme, slalom) tek bir zamanlı parkurla ölçmektir. Kapsamlı test aşamasının testidir.

**Ekipman:** Fotosel (başlangıç ve bitiş; el kronometresi kabul edilmez), jimnastik minderleri, denge tahtası (3 m × 15 cm × 20 cm), 130 × 130 cm engel, 60 cm çapında çemberler, voleybol topları, 3 numara ve 1 numara hentbol topları, 80/40 cm yükseklikte 4 engel seti, 4 dikey engel (slalom çubuğu), renkli bant.

**Uygulama:**
1. **Başlangıç:** Çocuk başlama çizgisinde durur; "çık" komutuyla fotoseli geçince süre başlar.
2. **Öne takla:** Başlama çizgisinin hemen önündeki minderde baş ve eller yere değerek öne takla atar ve kalkar. Gelişigüzel yuvarlanma hatadır; çocuk durdurulur, hareket tekrarlanır.
3. **Denge tahtası:** 3 m'lik denge tahtasının başlangıç ve bitişindeki 30 cm'lik işaretli bölgelere basmak şartıyla tahtanın üzerinden koşarak geçer. İşaretli bölgelere basmamak hatadır, tekrarlatılır.
4. **Engel üzerinden top atma:** Çemberlerdeki iki voleybol topunu tek tek 130 cm'lik engelin üzerinden atar, engelin altından geçip topu tutar, yine altından geçerek topu aldığı çembere bırakır. Engeli aşmayan atış tekrarlatılır.
5. **Tek ayak sekme:** Yan yana (bitişik) altı çemberden ilk üçünü sağ, sonraki üçünü sol ayakla sekerek geçer. Çember dışına basma, elin ya da diğer ayağın yere değmesi hatadır, tekrarlatılır.
6. **Elle top yer değiştirme:** Aralarında 1 m olan üç çemberden ikisindeki voleybol toplarının yerini, boş çemberi kullanarak elle değiştirir. Çemberden çıkan top ya da aynı çembere iki top konması düzelttirilir.
7. **Ayakla top yer değiştirme:** Aynı düzenekte 3 numara hentbol toplarının yerini ayakla değiştirir. Topa elle dokunursa top eski yerine konur ve ayakla tekrarlatılır.
8. **Duvara top atma:** Duvardan 1,5 m uzaktaki (aralarında 20 cm olan) üç çemberdeki 1 numara hentbol toplarını tek tek duvara atar, tutar ve aldığı çembere bırakır. Çembere konmayan top için çocuk geri çağrılır.
9. **Alttan-üstten engel geçişi:** Aralarında 1 m olan dört engeli (80-40-80-40 cm yükseklik, 130 cm genişlik) sırayla alttan-üstten-alttan-üstten geçer. Sıra hatası tekrarlatılır.
10. **Slalom:** Aralarında 80 cm olan dört dikey engel arasından slalom koşar; başlama yönü serbesttir. Engel atlamak ya da eksik geçmek tekrarlatılır.
11. **Bitiş:** Bitiş fotoselini hızla geçer; süre durur.

**Skorlama:** Parkurun tamamlanma süresi (sn), fotoselle. Düşük değer = iyi. Hatalar süre cezası değil, istasyonun yeniden yapılması olarak süreye yansır.

**Not:** Parkur dokuz istasyondan oluşur (2-10. adımlar); ayrıntılı ölçüler protokol belgesi ve kitabın Şekil 7.2'sindendir.

**Normatif:** ⚠️ Norm kitabında bu test için norm tablosu YOKTUR (kitabın 9. bölümündeki 11 ölçüm arasında yer almaz). Programda persentil gösterilmez; süre sporcunun kendi önceki ölçümleriyle karşılaştırılabilir.
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Koordinasyon testine ve mekik koşusuna ait protokol (uygulama talimatı).\nGençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 89-90, Şekil 7.2)",
                "degiskenler": ["Süre (sn)"]
            },

            "Mekik Koşusu (TSYT)": {
                "protokol": """
**Amaç:** Aerobik dayanıklılığı, sinyalle hızlanan 20 m mekik koşusuyla ölçmektir. Kapsamlı test aşamasının testidir.

**Ekipman:** 20 m düz koşu alanı, 10 koşu yolu için 33 kuka, TSYT sinyal kaydı (resmî web adresinden), ses sistemi ve mikrofon.

**Uygulama:**
1. Çocuklara 20 m'lik çizgiler tanıtılır ve her sinyalde karşı çizgiye ulaşmaları gerektiği anlatılır.
2. Çocuk başlangıç çizgisinde durur; üçlü sinyal sesiyle koşuya başlar.
3. Her sinyalde 20 m ilerideki çizgiye basar ve bir sonraki sinyalle geri koşar.
4. Koşu **7 km/sa** ile başlar; her seviyede hız **0,5 km/sa** artar.
5. Sinyali bir kez kaçıran çocuk devam eder; bir sonraki sinyali yakalarsa hata hakkı sıfırlanır.
6. Sinyali **iki kez üst üste** kaçıran çocuğun testi biter; tamamladığı mekik (tur) sayısı kaydedilir.

**Skorlama:** Tamamlanan mekik (20 m tur) sayısı. Yüksek değer = iyi. Talimatın veri sınırları: 21-119 tur.

**Not:** Bu test Eurofit/Léger 20 m mekik koşusuyla AYNI DEĞİLDİR: Léger 8,5 km/sa ile başlar, TSYT çocukların yaşına göre daha geniş süre aralıklı bir sinyalle 7 km/sa'ten başlar. Léger normları, VO2max formülleri ve PACER normları bu teste uygulanmaz.

**Normatif:** ⚠️ Norm kitabında bu test için norm tablosu YOKTUR. Programda persentil gösterilmez.
                """,
                "kaynak": "Gençlik ve Spor Bakanlığı. Türkiye Sportif Yetenek Taraması: Koordinasyon testine ve mekik koşusuna ait protokol (uygulama talimatı).\nGençlik ve Spor Bakanlığı (2023). Türkiye Sportif Yetenek Modeli: 7-11 Yaş Fiziksel Uygunluk Norm Değerleri. Ankara: Gençlik ve Spor Bakanlığı. ISBN 978-605-5050-60-3. (Bölüm 7, s. 90, Şekil 7.3; Tablo 7.3 veri sınırları)",
                "degiskenler": ["Tamamlanan Mekik Sayısı"]
            },
        },
    },

    "Çocuk ve Genç Fiziksel Uygunluk Bataryaları": {
        "Eurofit Fiziksel Uygunluk Test Bataryası": {
            "_kunye": {
                "gelistiren": "Avrupa Konseyi (Council of Europe), Spor Geliştirme Komitesi",
                "ulke": "Avrupa (uluslararası — Strazburg merkezli)",
                "yil": "1988 (deneysel versiyon 1983)",
                "hedef_yas": "6-18 yaş okul çağı çocuk ve gençler (1995'te 18-65 yaş yetişkin versiyonu eklendi)",
                "yas_araligi": (6, 18),                      # hedef_yas: "6-18 yaş okul çağı" (18-65 ayrı yetişkin sürümü)
                "yayginlik": "30'dan fazla Avrupa ülkesinde milyonlarca öğrenciye uygulanmıştır; Avrupa okullarında en yaygın kullanılan fiziksel uygunluk bataryasıdır. Türkiye'de de çeşitli akademik çalışmalarda kullanılmıştır."
            },
            "Flamingo Denge Testi": {
                "protokol": """
**Amaç:** Okul çağı çocuklarında vücudun genel statik dengesini tek ayak üzerinde durma performansı ile değerlendirmektir.

**Hedef Grup:** Okul çağı çocukları.

**Ekipman:** 50 cm uzunluğunda, 4 cm yüksekliğinde, 3 cm genişliğinde standart metal denge kirişi.

**Uygulama:**
1. Denek dominant ayağı ile kiriş üzerinde dururken diğer bacağını dizden bükerek geriye çeker ve eliyle tutar.
2. Test 1 dakika sürer; denek dengesini kaybedip yere dokunduğunda sayaç işletilir.

**Skorlama:** 1 dakikada yere dokunma (düşme) sayısı kaydedilir — az = iyi.
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.\nTsigilis, N., Douda, H., & Tokmakidis, S. P. (2001). Test-retest reliability of the Eurofit test battery. Perceptual and Motor Skills, 92(3), 1295-1300.",
                "degiskenler": ["Düşme Sayısı (1 dk)", "Dominant Ayak (Sağ/Sol)"]
            },
            "Plate Tapping (Disk Dokunma) Testi": {
                "protokol": """
**Amaç:** Üst ekstremite hareket hızını ve el-göz koordinasyonunu değerlendirmektir.

**Ekipman:** Masa üzerine 60 cm aralıkla yerleştirilmiş iki disk (20 cm çapında) ve ortada referans plakası.

**Uygulama:**
1. Denek baskın olmayan eli ortadaki plakaya koyar.
2. Komutla beraber, baskın el ile diskler arasında 25 tur (50 dokunma) art arda dokunulur.

**Skorlama:** 25 tur tamamlama süresi (saniye) — az = iyi.
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Süre (sn)"]
            },
            "Otur-Uzan (Sit and Reach) Testi": {
                "protokol": """
**Amaç:** Alt sırt ve hamstring kas grubu esnekliğini değerlendirmektir.

**Ekipman:** Standart sit-and-reach kutusu (ölçüm cetveli ile).

**Uygulama:**
1. Denek bacaklar düz, ayak tabanları kutuya değecek şekilde oturur.
2. Dizleri bükmeden, elleriyle mümkün olduğunca ileri uzanır.
3. 2 deneme yapılır, en iyi değer kaydedilir.

**Skorlama:** Uzanma mesafesi (cm). **Ölçeğin sıfır noktası ayak tabanı DEĞİLDİR:** Eurofit kutusunda ayak tabanı hizası ölçekte **15 cm**'dir; parmak uçlarına uzanan çocuk 15 cm alır, ayakları geçemeyen 15'in altında kalır. Programdaki normlar (Tomkinson ve ark., 2018) bu ölçeğe göredir: "15 cm skoru, katılımcının ayak parmaklarına uzanmasına karşılık gelir."

**Dikkat:** Sıfırı ayak tabanında olan bir kutu kullanılıyorsa okunan değere 15 cm eklenerek girilmelidir; aksi halde persentil ve branş eşleştirmesi ~15 cm düşük sonuç verir.
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.\nTomkinson, G. R., et al. (2018). European normative values for physical fitness in children and adolescents aged 9-17 years. British Journal of Sports Medicine, 52(22), 1445-1456. (ölçek: 15 cm = ayak parmakları)",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "Durarak Uzun Atlama": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü değerlendirmektir.

**Uygulama:**
1. İki ayak başlangıç çizgisinin arkasında.
2. Kol salınımı ile maksimal yatay atlama yapılır.
3. 3 deneme uygulanır, en iyi değer kaydedilir.

**Skorlama:** Mesafe (cm).
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"]
            },
            "El Kavrama Kuvveti (Eurofit)": {
                "protokol": """
**Amaç:** El ve önkol statik kas kuvvetini değerlendirmektir.

**Ekipman:** Ayarlanabilir el dinamometresi.

**Uygulama:**
1. Denek ayakta, kol gövdeye paralel ve uzatılmış şekilde dinamometreyi maksimal güçle sıkar.
2. Her el için 2 deneme yapılır.

**Skorlama:** İki elin en iyi değerlerinin toplamı (kg).
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Sağ El En İyi (kg)", "Sol El En İyi (kg)"]
            },
            "Asılı Durma - Bükümlü Kol (Bent Arm Hang)": {
                "protokol": """
**Amaç:** Üst ekstremite kas kuvveti ve dayanıklılığını (fonksiyonel kuvvet) değerlendirmektir.

**Ekipman:** Yüksek bar.

**Uygulama:**
1. Denek bara çenesi bar seviyesinin üstünde olacak şekilde asılır (pronated grip).
2. Bu pozisyonu mümkün olduğunca uzun süre korur.
3. Çene barın altına düştüğünde test sona erer.

**Skorlama:** Asılı kalınan toplam süre (saniye).
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Süre (sn)"]
            },
            "Mekik (Sit-Up) Testi - 30sn": {
                "protokol": """
**Amaç:** Karın (abdominal) kas kuvveti ve dayanıklılığını değerlendirmektir.

**Ekipman:** Mat, kronometre.

**Uygulama:**
1. Denek sırtüstü yatar, dizler 90° bükülü, eller ense arkasında kenetli.
2. 30 saniye içinde maksimum sayıda mekik (gövde kalkışı) yapılır.

**Skorlama:** 30 saniyede tamamlanan doğru tekrar sayısı.
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Tekrar Sayısı (30sn)"]
            },
            "10x5m Mekik Koşusu (Shuttle Run)": {
                "protokol": """
**Amaç:** Koşu hızı, çeviklik ve yön değiştirme yeteneğini değerlendirmektir.

**Ekipman:** 5m aralıklı iki paralel çizgi, kronometre.

**Uygulama:**
1. Denek iki çizgi arasında mümkün olduğunca hızlı 10 kez (5 gidiş-5 dönüş) koşar.
2. Her dönüşte çizgiyi bir ayağıyla geçmesi gerekir.

**Skorlama:** Toplam süre (saniye) — az = iyi.
                """,
                "kaynak": "Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Süre (sn)"]
            },
            "20m Mekik Koşusu (Eurofit/Léger)": {
                "protokol": """
**Amaç:** Kardiyorespiratuar (aerobik) dayanıklılığı ve VO2max'ı saha koşullarında tahmin etmektir.

**Ekipman:** 20m düz alan, sesli sinyal (beep) cihazı.

**Uygulama:**
1. Denek 20m mesafeyi ardışık bip sesleri arasında koşar.
2. Hız her dakika kademeli olarak artar (Léger 1 dakikalık protokolü: başlangıç 8.5 km/sa, her dakika +0.5 km/sa).
3. Bipe 2 kez üst üste yetişemeyince test sona erer.

**Skorlama:** Tamamlanan seviye ve tur sayısı; VO2max = 22.859 + (Seviye × 1.593)

**Koşulan süre (dakika):** Eurofit skoru, çocuğun bıraktığı ana kadar koştuğu süredir; **0.5 dakika hassasiyetle** kaydedilir (ör. 5.5 dk). Bu alan Flaman Spor Pusulası / Opstoel ve ark. (2015) ile aynı birimdir ve branş grubu eşleştirmesinde kullanılır. Seviye ve tekrardan otomatik çevrilmez; süre uygulama sırasında okunup ayrıca girilmelidir.
                """,
                "kaynak": "Léger, L. A., Mercier, D., Gadoury, C., & Lambert, J. (1988). The multistage 20 metre shuttle run test for aerobic fitness. Journal of Sports Sciences, 6(2), 93–101.\nCouncil of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.\nOpstoel, K., et al. (2015). PLoS ONE, 10(5), e0126282. (SR skoru: dakika, 0.5 dk hassasiyet, EUROFIT)",
                "degiskenler": ["Son Seviye", "Son Tekrar", "Koşulan Süre (dk)"]
            }
        },
        "FitnessGram": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "PACER (20m Mekik Koşusu)": {
                "protokol": """
**Amaç:** Sağlıkla ilişkili kardiyorespiratuar dayanıklılığı değerlendirmektir.

**Ekipman:** 20 metrelik düz zemin, PACER ses sinyali (beep) cihazı.

**Uygulama:**
1. Sporcu 20 metrelik mesafeyi ardışık ses sinyalleri arasında koşarak tamamlar.
2. Sinyal hızı her dakika artarak koşu temposunu hızlandırır.
3. Sporcu 2 kez üst üste sinyale yetişemediğinde test biter.

**Skorlama:** Tamamlanan toplam tur sayısı; VO2max tahmini hesaplanabilir.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nMahar, M. T. et al. (2006). Development and validation of a regression model to estimate VO2peak from PACER. Journal of Physical Activity and Health, 3(s2), S34-S46.",
                "degiskenler": ["Tamamlanan Tur Sayısı"]
            },
            "Push-Up (Şınav) Testi": {
                "protokol": """
**Amaç:** Üst beden kas kuvveti ve dayanıklılığını değerlendirmektir.

**Uygulama:**
1. Standart şınav pozisyonu (90° dirsek fleksiyonu).
2. Metronom ritmine uygun (dakikada 20 vuruş) tekrar yapılır.
3. Form bozulana kadar devam edilir.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "Modified Pull-Up Testi": {
                "protokol": """
**Amaç:** Üst beden kas kuvveti ve dayanıklılığının Push-Up'a alternatif değerlendirmesidir; özellikle Push-Up'ı tamamlayamayan bireyler için kullanılır.

**Ekipman:** Ayarlanabilir yatay bar, elastik bant.

**Uygulama:**
1. Sporcu sırtüstü yatar; bar, uzatılmış kolların 2,5-5 cm (1-2 inç) üstüne ayarlanır. Elastik bant bardan 18-20 cm (7-8 inç) aşağıya gerilir.
2. Avuçlar öne bakacak şekilde (pronated) bara tutunulur; vücut düz çizgi oluşturur, yalnız topuklar yerde.
3. Çene elastik bandın üstüne çıkana kadar çekilir, kollar düzleşene kadar inilir. Tempo verilmez.
4. Form bozulana kadar devam edilir.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nWelk, G. J., & Meredith, M. D. (Eds.). (2008). FitnessGram/ActivityGram Test Administration Manual (4th ed.). Human Kinetics.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "Curl-Up (Kademeli Mekik) Testi": {
                "protokol": """
**Amaç:** Karın (abdominal) kas kuvveti ve dayanıklılığını değerlendirmektir.

**Ekipman:** Mat, ölçüm şeridi (5-9 yaş: 3 inç = 7,6 cm; 10 yaş ve üstü: 4,5 inç = 11,4 cm genişliğinde), metronom (dakikada 20 vuruş).

**Uygulama:**
1. Sporcu sırtüstü yatar, dizler yaklaşık 140° açıyla bükülü, ayaklar yere düz basar.
2. Eller uyluğa yerleştirilir; ölçüm şeridi parmak uçlarının altına konur.
3. Metronom ritmine uygun olarak baş ve omuzlar yerden kaldırılır, parmaklar şeridi aşacak şekilde ileri kaydırılır.
4. Ritim bozulana veya 75 tekrara ulaşılana kadar devam edilir.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı (maksimum 75).
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nMorrow, J. R., Beets, M. W., & Welk, G. J. (2013). Reliability and validity of FitnessGram. American Journal of Preventive Medicine, 44(1S1), S12-S20.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "Trunk Lift (Gövde Kaldırma) Testi": {
                "protokol": """
**Amaç:** Sırt ekstansör kaslarının kuvvetini ve esnekliğini değerlendirmektir.

**Ekipman:** Mat, cetvel, yere konan küçük bir işaret.

**Uygulama:**
1. Sporcu yüzüstü yatar, eller kalça altına veya yanına konumlandırılır.
2. Yere, sporcunun göz hizasına bir işaret konur; sporcu hareket boyunca bu işarete bakar. İşaret başı nötr tutmak içindir — ölçüm noktası değildir.
3. Başı ve üst gövdesini yavaşça ve kontrollü biçimde yerden kaldırır; en yüksek noktada ölçüm alınana kadar bekler.
4. Yerden ÇENEYE kadar olan yükseklik ölçülür (göze değil).
5. 2 deneme yapılır, en iyi değer kaydedilir.

**Skorlama:** Kaldırma yüksekliği (cm); 30,5 cm (12 inç) üstü 30,5 cm olarak kaydedilir.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nBianco, A. et al. (2015). The FitnessGram trunk lift test: a critical review. Measurement in Physical Education and Exercise Science, 19(4), 204-213.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "Back-Saver Sit and Reach (Tek Bacak Otur-Uzan)": {
                "protokol": """
**Amaç:** Hamstring kaslarının esnekliğini, bel sağlığını riske atmadan tek taraflı değerlendirmektir.

**Ekipman:** Standart sit-and-reach kutusu (30 cm yüksekliğinde).

**Uygulama:**
1. Sporcu oturur; bir bacak düz uzatılır, diğer bacak dizden bükülü, ayak tabanı yere basar.
2. Düz bacak üzerindeki iki el ile öne uzanılır ve pozisyon 1-2 sn korunur.
3. Her bacak için 2 deneme yapılır, en iyi değer kaydedilir.

**Skorlama:** Uzanma mesafesi (cm). **Ölçeğin sıfır noktası ayak tabanı DEĞİLDİR:** FitnessGram'da cetvelin **9 inç (22.9 cm)** işareti kutunun ayak tarafındaki kenarına gelir; parmak uçlarına uzanan 22.9 cm alır. FitnessGram skoru inç olarak, yarım inç hassasiyetle ve **en fazla 12 inç (30.5 cm)** kaydeder. Programa cm girilir.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nPatrick, D. G. et al. (1999). Criterion-referenced health standards for back saver sit and reach. Research Quarterly for Exercise and Sport, 70(4), 423-427.",
                "degiskenler": ["Sağ Bacak - En İyi (cm)", "Sol Bacak - En İyi (cm)"]
            },
            "Shoulder Stretch (Omuz Esnekliği) Testi": {
                "protokol": """
**Amaç:** Omuz ekleminin esnekliğini (fleksiyon ve ekstansiyon) değerlendirmektir.

**Ekipman:** Gerekmez.

**Uygulama:**
1. **Sağ omuz:** Sağ el omuz üzerinden sırta doğru uzatılır; sol el bel altından sırta doğru uzatılır. Eller birbirine değiyor mu kontrol edilir.
2. **Sol omuz:** Aynı işlem sol el üstte olacak şekilde tekrarlanır.
3. Her iki omuz ayrı ayrı değerlendirilir.

**Skorlama:** Her omuz için Geçti / Kalmadı (Pass / Did Not Pass).

**Geçme Kriteri:** Parmak uçları sırtta birbirine değiyorsa → GEÇTİ.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Sağ Omuz (Geçti/Kalmadı)", "Sol Omuz (Geçti/Kalmadı)"]
            },
            "1 Mil Yürüyüş/Koşu Testi": {
                "protokol": """
**Amaç:** PACER'a alternatif olarak kardiyorespiratuar dayanıklılığı değerlendirmektir; VO2max tahmini yapılabilir.

**Ekipman:** Ölçülmüş 1 mil (1609 m) pist, kronometre, KAH monitörü (opsiyonel).

**Uygulama:**
1. Sporcu 1 mil (4 tur × 400m pistte) mesafeyi mümkün olduğunca hızlı tamamlar.
2. Test bitiminde kalp atım hızı (HR) ölçülür (ilk 15 saniye × 4).

**Skorlama:**
- Tamamlama süresi (dakika:saniye)
- VO2max tahmini: VO2max = 108.94 − (8.41 × Süre_dk) + (0.34 × Süre_dk²) + (0.21 × Yaş×Cinsiyet) − (0.84 × VKİ)
  *(Cinsiyet: Erkek=1, Kadın=0)*
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nCureton, K. J. et al. (1995). Validation of the one-mile run as a test of aerobic capacity in children. Research Quarterly for Exercise and Sport, 66(4), 402-412.",
                "degiskenler": ["Süre (dakika)", "Süre (saniye)", "HR Test Sonu (bpm)"]
            },
            "Vücut Kompozisyonu - Deri Kıvrımı": {
                "protokol": """
**Amaç:** Vücut yağ yüzdesini deri kıvrımı ölçümleriyle tahmin etmektir.

**Ekipman:** Skinfold kaliperi (Lange veya Harpenden).

**Uygulama:**
1. **Triceps deri kıvrımı:** Sağ kolun arka orta noktasından, dikey olarak ölçülür.
2. **Baldır (Calf) deri kıvrımı:** Sağ baldırın iç yüzeyinden, maksimum çevre noktasında dikey olarak ölçülür.
3. Her ölçüm için 2 deneme yapılır; fark 2mm'yi geçiyorsa 3. deneme alınır.

**Skorlama:**
- Triceps + Baldır toplamı (mm)
- Vücut Yağ % tahmini (yaş ve cinsiyete göre FitnessGram tablolarından):
  - **Erkek:** %Yağ = 0.735 × (Triceps + Baldır) + 1.0
  - **Kız:** %Yağ = 0.610 × (Triceps + Baldır) + 5.1

**HFZ Notu:** FitnessGram'da vücut yağı HFZ'si yaşa ve cinsiyete göre değişir. Tablo değerleri kaynağından doğrulanamadığı için programa eşik girilmedi; yalnız yağ yüzdesi hesaplanır.
                """,
                "kaynak": "Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.\nSlaughter, M. H. et al. (1988). Skinfold equations for estimation of body fatness in children and youth. Human Biology, 60(5), 709-723.",
                "degiskenler": ["Triceps Deri Kıvrımı (mm)", "Baldır Deri Kıvrımı (mm)", "Cinsiyet (E/K)"]
            }
        },
        "Presidential Youth Fitness Program": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Curl-Up (Mekik) Testi": {
                "protokol": """
**Uygulama:** FitnessGram → Curl-Up (Kademeli Mekik) Testi ile aynı protokol uygulanır.

**PYFP Farkı:** Sağlık Uygunluk Zonu (HFZ) yerine **Sağlıklı Uygunluk Standardı (HFS)** normatif değerleri kullanılır. HFS, ulusal temsili örneklemden (NHANES) türetilmiştir.

**Skorlama:** Maksimum 75 tekrar.
                """,
                "kaynak": "Corbin, C. B., Welk, G. J., Corbin, W. R., & Welk, K. A. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "PACER Testi": {
                "protokol": """
**Uygulama:** FitnessGram → PACER (20m Mekik Koşusu) ile aynı protokol uygulanır.

**PYFP Farkı:** Sonuçlar PYFP'nin HFS norm tablolarına göre değerlendirilir. PACER, PYFP'de aerobik kapasitenin birincil ölçüm aracıdır.

**Skorlama:** Tamamlanan toplam tur sayısı.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tamamlanan Tur Sayısı"]
            },
            "Push-Up Testi": {
                "protokol": """
**Uygulama:** FitnessGram → Push-Up (Şınav) Testi ile aynı protokol uygulanır.

**PYFP Farkı:** HFS norm değerleri kullanılır. Push-Up, PYFP'de üst beden kuvvetinin birincil ölçüm aracıdır.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "Modified Pull-Up Testi": {
                "protokol": """
**Uygulama:** FitnessGram → Modified Pull-Up Testi ile aynı protokol uygulanır.

**PYFP Farkı:** Push-Up tamamlanamayan durumlarda alternatif olarak uygulanır; HFS norm değerleri kullanılır.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tekrar Sayısı"]
            },
            "Trunk Lift Testi": {
                "protokol": """
**Uygulama:** FitnessGram → Trunk Lift (Gövde Kaldırma) Testi ile aynı protokol uygulanır.

**PYFP Farkı:** HFS norm değerleri kullanılır. Maksimum kayıt 30.5 cm ile sınırlıdır.

**Skorlama:** Yerden çeneye kaldırma yüksekliği (cm); maksimum 30.5 cm.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "Back-Saver Sit and Reach": {
                "protokol": """
**Uygulama:** FitnessGram → Back-Saver Sit and Reach (Tek Bacak Otur-Uzan) ile aynı protokol uygulanır.

**PYFP Farkı:** HFS norm değerleri kullanılır. Her iki bacak ayrı ayrı ölçülür ve değerlendirilir.

**Skorlama:** Her bacak için uzanma mesafesi (cm). **Ölçeğin sıfır noktası ayak tabanı DEĞİLDİR:** FitnessGram'da cetvelin **9 inç (22.9 cm)** işareti kutunun ayak tarafındaki kenarına gelir; parmak uçlarına uzanan 22.9 cm alır. FitnessGram skoru inç olarak, yarım inç hassasiyetle ve **en fazla 12 inç (30.5 cm)** kaydeder. Programa cm girilir.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Sağ Bacak - En İyi (cm)", "Sol Bacak - En İyi (cm)"]
            },
            "Shoulder Stretch Testi": {
                "protokol": """
**Uygulama:** FitnessGram → Shoulder Stretch (Omuz Esnekliği) Testi ile aynı protokol uygulanır.

**PYFP Farkı:** HFS norm değerleri kullanılır. Her iki omuz ayrı ayrı değerlendirilir.

**Skorlama:** Her omuz için Geçti / Kalmadı.
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Sağ Omuz (Geçti/Kalmadı)", "Sol Omuz (Geçti/Kalmadı)"]
            },
            "Vücut Kompozisyonu (PYFP)": {
                "protokol": """
**Uygulama:** FitnessGram → Vücut Kompozisyonu - Deri Kıvrımı ile aynı protokol uygulanır (Triceps + Baldır deri kıvrımı).

**PYFP Farkı:** VKİ de alternatif kompozisyon göstergesi olarak kabul edilir. HFS norm değerleri kullanılır.

**Skorlama:** Vücut yağ % (deri kıvrımı) veya VKİ (kg/m²).
                """,
                "kaynak": "Corbin, C. B. et al. (2013). The Presidential Youth Fitness Program. Research Quarterly for Exercise and Sport, 84(4), 415-423.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Triceps Deri Kıvrımı (mm)", "Baldır Deri Kıvrımı (mm)", "Cinsiyet (E/K)"]
            }
        },
        "Canadian Assessment of Physical Literacy (CAPL)": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "CAPL Engel Parkuru (Motor Beceri)": {
                "protokol": """
**Amaç:** Temel hareket becerilerini ve çevikliği tek, zamanlı bir parkurda değerlendirmektir. CAPL-2'nin motor beceri testi CAMSA'dır (Canadian Agility and Movement Skill Assessment).

**Ekipman:** Çemberler (3 + 6), koniler, top (yakalama ve hedefe atış için), hedef, vuruş topu, kronometre.

**Uygulama:**
1. **Başlangıç:** Çocuk çemberlerin başında hazır bekler; "başla" komutuyla süre başlar.
2. **Çift ayak sıçrama:** Üç çemberin üzerinden çift ayakla sıçrar.
3. **Yana kayma:** İki kez yana kayar; biri ters yönde.
4. **Top yakalama:** Uygulayıcının attığı topu yakalar.
5. **Hedefe atış:** Topu hedefe atar.
6. **Skipping:** 5 m skipping yapar (adım-sekme; ipli atlama değildir).
7. **Tek ayak sekme:** Altı çemberin üzerinden tek ayakla seker.
8. **Topa vuruş:** Topa vurarak iki koninin arasından geçirir; süre vuruşla durur.
9. İki gösterim ve iki alıştırmadan sonra iki zamanlı deneme yapılır.

**Skorlama:**
- Beceri puanı 0–14: yedi becerideki 14 ölçüt, her biri 1 puan (çift ayak sıçrama 2, yana kayma 3, top yakalama 1, hedefe atış 2, skipping 2, tek ayak sekme 2, topa vuruş 2).
- Süre puanı 1–14: tamamlama süresi (0,1 sn) 14 puanlık ölçeğe çevrilir; kısa süre = yüksek puan.
- Toplam CAMSA puanı 1–28: beceri ve süre puanı eşit ağırlıkta toplanır.

**Not:** Süreyi puana çeviren tablo CAPL-2 kılavuzundadır ve kaynakla doğrulanamadığı için programda hesaplanmaz; süre puanı kılavuzdan okunup girilir, toplam program tarafından toplanır. Hangi denemenin skor olduğu kaynaklarda ayrışır: Chang ve ark. (2021) iki zamanlı denemenin iyisini, Cao ve ark. (2020) 2. denemeyi kullanır. Önceki sürümde yazan "slalom, denge tahtası, bariyer, geri koşu" parkuru ve 1–10 teknik puanı CAMSA'ya ait değildir.
                """,
                "kaynak": "Longmuir, P. E., Boyer, C., Lloyd, M., Yang, Y., McGarry, J., Borghese, M. M., & Tremblay, M. S. (2015). The Canadian Assessment of Physical Literacy: methods for children in grades 4 to 6 (8 to 12 years). BMC Public Health, 15(1), 1-11.\nLongmuir, P. E. et al. (2018). CAPL-2: Canadian Assessment of Physical Literacy, Second Edition. Healthy Active Living and Obesity Research Group, CHEO Research Institute.\nCao et al. (2020). Performances of the Canadian Agility and Movement Skill Assessment (CAMSA), and validity of timing components in comparison with three commonly used agility tests in Chinese boys: an exploratory study. PeerJ, 8, e8784. https://doi.org/10.7717/peerj.8784\nChang, J., Yong, L., Yan, H., Wang, J., & Song, N. (2021). Measurement properties of Canadian Agility and Movement Skill Assessment for children aged 9–12 years using Rasch analysis. Frontiers in Public Health, 9, 745449. https://doi.org/10.3389/fpubh.2021.745449",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Beceri Puanı (0-14)", "Süre Puanı (1-14)"]
            },
            "CAPL Duran Uzun Atlama (Fiziksel Uygunluk)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü ölçmek — CAPL'ın "Fiziksel Uygunluk" alanı kapsamındadır.

**Ekipman:** Kaymaz zemin, mezura veya ölçüm bandı.

**Uygulama:**
1. Çocuk ayak uçları çizginin gerisinde, ayaklar omuz genişliğinde durur.
2. Kollarını salarak çift ayakla maksimum mesafeye atlar.
3. 2 deneme yapılır; en iyi mesafe kaydedilir.

**Skorlama:** En iyi atlama mesafesi (cm).
                """,
                "kaynak": "Longmuir, P. E. et al. (2015). The Canadian Assessment of Physical Literacy. BMC Public Health, 15(1), 1-11.\nLongmuir, P. E. et al. (2018). CAPL-2. CHEO Research Institute.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "CAPL 20m Mekik Koşusu (Fiziksel Uygunluk)": {
                "protokol": """
**Amaç:** Kardiyorespiratuar dayanıklılığı değerlendirmek — CAPL'ın "Fiziksel Uygunluk" alanı kapsamındadır.

**Uygulama:** FitnessGram → PACER (20m Mekik Koşusu) ile aynı protokol uygulanır.

**CAPL Farkı:** Sonuçlar CAPL-2 yaş/cinsiyet norm tablolarına göre fiziksel uygunluk puanına dönüştürülür (8–12 yaş).

**Skorlama:** Tamamlanan toplam tur sayısı.
                """,
                "kaynak": "Longmuir, P. E. et al. (2018). CAPL-2. CHEO Research Institute.\nPlowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). The Cooper Institute.",
                "degiskenler": ["Tamamlanan Tur Sayısı"]
            },
            "CAPL Günlük Adım Sayısı (Günlük Davranış)": {
                "protokol": """
**Amaç:** Çocuğun günlük fiziksel aktivite düzeyini nesnel olarak ölçmek — CAPL'ın "Günlük Davranış" alanı kapsamındadır.

**Ekipman:** Pedometre veya akselometre (7 günlük ölçüm önerilir).

**Uygulama:**
1. Çocuk okul içi ve dışı tüm aktivitelerde pedometreyi takar.
2. Her gün sonunda adım sayısı kaydedilir.
3. En az 4 geçerli gün (≥10 saat/gün) veri toplanır.
4. Hafta içi ve hafta sonu günleri ayrı kaydedilir.

**Skorlama:**
- Günlük ortalama adım sayısı (adım/gün)
- Referans: ≥12.000 adım/gün (erkek), ≥11.000 adım/gün (kız) — sağlıklı aktivite düzeyi

**Not:** CAPL-2'de akselometre ile orta-şiddetli fiziksel aktivite süresi (MVPA, dakika/gün) de ek gösterge olarak kullanılmaktadır.
                """,
                "kaynak": "Longmuir, P. E. et al. (2015). The Canadian Assessment of Physical Literacy. BMC Public Health, 15(1), 1-11.\nTremblay, M. S. et al. (2011). Canadian Physical Activity Guidelines for Children. Applied Physiology, Nutrition and Metabolism, 36(1), 59-64.",
                "degiskenler": ["Pzt Adım", "Sal Adım", "Çar Adım", "Per Adım", "Cum Adım", "Cmt Adım", "Paz Adım"]
            },
            "CAPL Motivasyon ve Güven Anketi": {
                "protokol": """
**Amaç:** Çocuğun fiziksel aktiviteye katılım motivasyonunu ve öz-yeterlilik algısını değerlendirmek — CAPL'ın "Motivasyon ve Güven" alanı kapsamındadır.

**Ekipman:** CAPL standart anket formu (8–12 yaş için uyarlanmış dil).

**Uygulama:**
1. Çocuk anketi bağımsız olarak doldurur (yaklaşık 10–15 dakika).
2. 5'li Likert skalası (1=Hiç katılmıyorum → 5=Tamamen katılıyorum).
3. Alt ölçekler: Öz-yeterlilik, içsel motivasyon, fiziksel aktivitenin önemi.

**Skorlama:**
- Her alt ölçek için ortalama puan (1–5)
- Toplam motivasyon-güven skoru (CAPL norm tablosuyla karşılaştırılır)

**Not:** Bu alan CAPL'ı diğer fiziksel uygunluk bataryalarından ayıran temel özelliktir; yalnızca fiziksel performansı değil, fiziksel okuryazarlığın bilişsel/duyuşsal boyutunu da ölçer.
                """,
                "kaynak": "Longmuir, P. E. et al. (2015). The Canadian Assessment of Physical Literacy. BMC Public Health, 15(1), 1-11.\nWhitehead, M. (2010). Physical literacy: Throughout the lifecourse. Routledge.",
                "degiskenler": ["Öz-Yeterlilik Puanı (1-5)", "İçsel Motivasyon Puanı (1-5)", "Aktivite Önemi Puanı (1-5)"]
            }
        },
        "ALPHA Health-Related Fitness Test Battery": {
            "_kunye": {
                "gelistiren": "ALPHA Çalışma Grubu (Ruiz, Castro-Piñero, España-Romero, Ortega ve ark.) — Granada Üniversitesi liderliğinde, AB destekli konsorsiyum",
                "ulke": "İspanya merkezli, Avrupa Birliği genelinde (ALPHA: Assessing Levels of Physical Activity projesi)",
                "yil": "2010-2011 (yayın: Ruiz ve ark., 2011, British Journal of Sports Medicine)",
                "hedef_yas": "6-18 yaş çocuk ve adölesanlar (sağlıkla ilişkili uygunluk odaklı)",
                "yas_araligi": (6, 18),                      # hedef_yas: "6-18 yaş"
                "yayginlik": "Avrupa Birliği genelinde okul tabanlı sağlık taramalarında yaygın kullanılır; Eurofit ve FitnessGram ile birlikte dünyada en çok atıf alan üç bataryadan biridir. İspanya, İsveç, Yunanistan ve diğer AB ülkelerinde ulusal referans değerleri oluşturulmuştur."
            },
            "20m Mekik Koşusu (ALPHA)": {
                "protokol": """
**Amaç:** Kardiyorespiratuar kapasiteyi (VO2max) saha koşullarında tahmin etmektir — bataryanın "altın standart" testi olarak kabul edilir.

**Ekipman:** 20m düz alan, sesli sinyal (beep) cihazı.

**Uygulama:** PACER/Léger ile aynı protokol; ALPHA bataryasında VO2max tahmin formülü farklıdır.

**Skorlama:** VO2max = 31.025 + (3.238 × Son Hız) − (3.248 × Yaş) + (0.1536 × Yaş × Son Hız)
                """,
                "kaynak": "Ruiz, J. R., Castro-Piñero, J., España-Romero, V., Artero, E. G., Ortega, F. B., Cuenca, M. M., ... & Castillo, M. J. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery for children and adolescents. British Journal of Sports Medicine, 45(6), 518-524.",
                "degiskenler": ["Son Hız (km/h)", "Tamamlanan Tur Sayısı"]
            },
            "El Kavrama Kuvveti (ALPHA)": {
                "protokol": """
**Amaç:** Sağlıkla ilişkili üst ekstremite kas-iskelet kuvvetini değerlendirmektir.

**Ekipman:** Ayarlanabilir el dinamometresi (kavrama genişliği yaş/ele göre ayarlanır).

**Uygulama:** Ayakta, dirsek tam ekstansiyonda, dinamometre var gücüyle sıkılır. Her el için 2 deneme yapılır.

**Skorlama:** İki elin en iyi değerlerinin ortalaması (kg).
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.",
                "degiskenler": ["Sağ El (kg)", "Sol El (kg)"]
            },
            "Durarak Uzun Atlama (ALPHA)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü (kas-iskelet uygunluğu) değerlendirmektir.

**Ekipman:** Kaymaz yüzey, mezura, koniler.

**Uygulama:** Denek ayaklar omuz genişliğinde, ayak uçları çizginin gerisinde durarak çift ayakla maksimum mesafeye atlar. 2 deneme yapılır.

**Skorlama:** En iyi mesafe (cm).
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "4x10m Mekik Koşusu (ALPHA)": {
                "protokol": """
**Amaç:** Koşu hızı, çeviklik ve motor uygunluğu değerlendirmektir (genişletilmiş ALPHA versiyonunda yer alır).

**Ekipman:** 10m aralıklı iki çizgi, kronometre, sünger bloklar.

**Uygulama:** Denek 10m'lik mesafeyi 4 kez (2 gidiş-2 dönüş) maksimal hızla koşar; her dönüşte yerden bir bloğu alıp diğer çizgiye taşır.

**Skorlama:** Toplam süre (saniye) — az = iyi.
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.",
                "degiskenler": ["Süre (sn)"]
            },
            "Bel Çevresi ve VKİ (Vücut Kompozisyonu)": {
                "protokol": """
**Amaç:** Vücut kompozisyonunu ve merkezi adipositeyi (karın bölgesi yağlanması) değerlendirmektir.

**Ekipman:** Mezura (bel çevresi), boy/kilo ölçer.

**Uygulama:**
1. Bel çevresi, son kosta ile iliak krest arası orta noktadan ölçülür.
2. VKİ = Kilo (kg) / Boy² (m²) formülüyle hesaplanır.

**Skorlama:** Bel çevresi (cm), VKİ (kg/m²).
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.",
                "degiskenler": ["Bel Çevresi (cm)"]
            },
            "Back-Saver Sit and Reach (ALPHA)": {
                "protokol": """
**Amaç:** Hamstring ve alt sırt esnekliğini değerlendirmektir — ALPHA bataryasının genişletilmiş (extended) versiyonunda yer alır.

**Ekipman:** Standart sit-and-reach kutusu (30 cm yüksekliğinde).

**Uygulama:**
1. Denek oturur; bir bacak düz uzatılır, diğer bacak dizden bükülü, ayak tabanı yere basar.
2. İki el ile düz bacak üzerinden öne uzanılır ve pozisyon 2 saniye korunur.
3. Her bacak için 2 deneme yapılır; en iyi değer kaydedilir.

**Skorlama:** Uzanma mesafesi (cm). Ölçek FitnessGram ile aynı kabul edilir: ayak tabanı hizası **22.9 cm (9 inç)**; parmak uçlarına uzanan 22.9 cm alır. **Not:** Bu ölçek ALPHA kılavuzunun kendisinden doğrulanamadı; FitnessGram protokolünden alınmıştır.

**ALPHA Farkı:** FitnessGram'dakiyle aynı protokol; sonuçlar ALPHA Avrupa norm tablolarıyla (yaş/cinsiyet) değerlendirilir.
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.\nCastro-Piñero, J. et al. (2009). Criterion-related validity of field-based fitness tests in youth. British Journal of Sports Medicine, 43(13), 964-969.",
                "degiskenler": ["Sağ Bacak - En İyi (cm)", "Sol Bacak - En İyi (cm)"]
            },
            "Plate Tapping (El Plakası Vurma)": {
                "protokol": """
**Amaç:** Üst ekstremite hareket hızını ve el-göz koordinasyonunu değerlendirmektir — ALPHA bataryasının genişletilmiş versiyonunda yer alır.

**Ekipman:** İki adet 20 cm çaplı disk (plaka), aralarında 60 cm mesafe, yatay yüzey; kronometre.

**Uygulama:**
1. Dominant olmayan el, iki diskin arasındaki plakaya yerleştirilir.
2. Dominant el ile iki disk arasında sırayla, 25 tur (50 dokunuş) olabildiğince hızlı dokunulur.
3. Her dokunuşta elin diske tam olarak değmesi gerekir.
4. 2 deneme yapılır; en iyi değer (en az süre) kaydedilir.

**Skorlama:** 25 çift dokunuşu tamamlama süresi (saniye) — az = iyi.

**Not:** Eurofit bataryasında da yer alır; ALPHA'da normatif değerlendirme için Avrupa referans tabloları kullanılır.
                """,
                "kaynak": "Ruiz, J. R. et al. (2011). Field-based fitness assessment in young people: the ALPHA health-related fitness test battery. British Journal of Sports Medicine, 45(6), 518-524.\nCouncil of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
            }
        },
        "PREFIT (Anaokulu Çocukları)": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Durarak Uzun Atlama (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların alt ekstremite patlayıcı gücünü değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Kaymaz zemin, mezura veya ölçüm bandı.

**Uygulama:**
1. Çocuk başlangıç çizgisinin arkasından çift ayakla maksimum mesafeye atlar.
2. Kollarını öne sallayarak yardım alabilir.
3. 2 deneme yapılır; en iyi mesafe kaydedilir.

**Skorlama:** Topuğun değdiği noktaya kadar mesafe (cm).
                """,
                "kaynak": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children: the PREFIT battery. Sports Medicine, 45(8), 1125-1155.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "20m Mekik Koşusu (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların kardiyorespiratuar dayanıklılığını değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 20m düz alan, sesli sinyal (beep) cihazı — PREFIT'e özel yavaş başlangıç hızı (8.5 km/h) kullanılır.

**Uygulama:**
1. Çocuk 20 metrelik mesafeyi ses sinyalleri arasında koşarak tamamlar.
2. PREFIT versiyonunda başlangıç hızı standart versiyondan daha düşüktür; küçük çocuklar için uyarlanmıştır.
3. Sinyal hızı kademeli olarak artar.
4. Çocuk 2 kez üst üste sinyale yetişemediğinde test biter.

**Skorlama:** Tamamlanan toplam tur sayısı.

**Not:** Standart beep testi 3-6 yaş için uyarlanmamıştır; PREFIT versiyonu bu yaş grubuna özel validasyon çalışmalarıyla geliştirilmiştir.
                """,
                "kaynak": "Cadenas-Sanchez, C. et al. (2016). Assessing physical fitness in preschool children: feasibility and reliability of the PREFIT battery. Journal of Science and Medicine in Sport, 19(11), 910-915.\nOrtega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children. Sports Medicine, 45(8), 1125-1155.",
                "degiskenler": ["Tamamlanan Tur Sayısı"]
            },
            "El Kavrama Kuvveti (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların üst ekstremite kas kuvvetini değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Çocuk boyutuna uygun el dinamometresi (küçük kavrama aralığı).

**Uygulama:**
1. Çocuk ayakta, dirsek tam ekstansiyonda dinamometreyi sıkar.
2. Her el için 2 deneme yapılır.
3. En iyi değer kaydedilir.

**Skorlama:** Dominant elin en iyi değeri (kg).

**Not:** Yetişkin dinamometresi bu yaş grubu için uygun değildir; çocuk dinamometresi zorunludur.
                """,
                "kaynak": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children. Sports Medicine, 45(8), 1125-1155.\nCadenas-Sanchez, C. et al. (2016). PREFIT battery feasibility and reliability. Journal of Science and Medicine in Sport, 19(11), 910-915.",
                "degiskenler": ["Sağ El (kg)", "Sol El (kg)"]
            },
            "4x10m Mekik Koşusu (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların koşu hızı ve çevikliğini değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 10m aralıklı iki çizgi, kronometre, sünger bloklar.

**Uygulama:**
1. Çocuk 10m'lik mesafeyi 4 kez (2 gidiş-2 dönüş) maksimal hızla koşar.
2. Her dönüşte yerden bir bloğu alıp diğer çizgiye taşır.
3. 2 deneme yapılır; en iyi süre kaydedilir.

**Skorlama:** En iyi süre (saniye) — az = iyi.
                """,
                "kaynak": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children. Sports Medicine, 45(8), 1125-1155.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
            },
            "Flamingo Denge Testi (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların statik dengesini değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Düz zemin (denge tahtası bu yaşta kullanılmaz), kronometre.

**Uygulama:**
1. Çocuk dominant ayağı üzerinde tek ayak durur; diğer bacak geri bükülü, ayak kalçaya yakın tutulur.
2. 30 saniye boyunca denge korunmaya çalışılır.
3. Her düşme veya denge kaybında sayaç artırılır.

**Skorlama:** 30 saniyede denge kaybı sayısı — az = iyi.

**Not:** PREFIT'te yetişkin Flamingo testinin (1 dakika, denge tahtası) basitleştirilmiş versiyonu kullanılır.
                """,
                "kaynak": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children. Sports Medicine, 45(8), 1125-1155.\nCadenas-Sanchez, C. et al. (2016). PREFIT battery feasibility and reliability. Journal of Science and Medicine in Sport, 19(11), 910-915.",
                "degiskenler": ["Düşme Sayısı (30 sn)"]
            },
            "Vücut Kompozisyonu (PREFIT)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların vücut kompozisyonunu değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Boy ölçer, tartı, mezura (bel çevresi için).

**Uygulama:**
1. **Boy:** Stadiometre ile çocuk dik dururken ölçülür (cm).
2. **Kilo:** Hafif kıyafetle tartılır (kg).
3. **Bel Çevresi:** Umbilikus hizasından mezura ile ölçülür (cm).
4. VKİ = Kilo / Boy² formülüyle hesaplanır.

**Skorlama:**
- Boy (cm), Kilo (kg)
- VKİ (kg/m²)
- Bel Çevresi (cm)

**Not:** Bu yaş grubunda deri kıvrımı ölçümü teknik güçlük nedeniyle rutin önerilmez; VKİ ve bel çevresi birincil göstergelerdir.
                """,
                "kaynak": "Ortega, F. B. et al. (2015). Systematic review and proposal of a field-based physical fitness-test battery in preschool children. Sports Medicine, 45(8), 1125-1155.",
                "degiskenler": ["Boy (cm)", "Kilo (kg)", "Bel Çevresi (cm)"]
            }
        },
        "Chinese National Physical Fitness Measurement (CNPFM)": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "50m Sprint": {
                "protokol": """
**Amaç:** Çin ulusal standartlarına göre maksimal koşu hızını ölçmektir.

**Ekipman:** 50m düz pist, kronometre veya fotosel sistemi.

**Uygulama:**
1. Sporcu ayakta başlangıç pozisyonunda hazır bekler.
2. Başlangıç komutuyla 50 metre mesafe maksimal hızla koşulur.
3. 2 deneme yapılır; en iyi süre kaydedilir.

**Skorlama:** En iyi tamamlama süresi (sn) — az = iyi.
                """,
                "kaynak": "Sun, H. et al. (2014). Physical fitness of children and adolescents in China. Journal of Sport and Health Science, 3(4), 263-267.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
            },
            "Mekik Koşusu (50m × 8)": {
                "protokol": """
**Amaç:** Çeviklik, hız ve kısa mesafe dayanıklılığını ölçmektir — CNPFM'nin temel koordinasyon testidir.

**Ekipman:** 25m düz alan, kronometre, koniler.

**Uygulama:**
1. Sporcu 25m mesafeyi 8 kez (4 gidiş-4 dönüş) maksimal hızla koşar.
2. Her dönüşte çizgiyi geçip geri döner.
3. Toplam mesafe: 200m.

**Skorlama:** Toplam tamamlama süresi (sn) — az = iyi.
                """,
                "kaynak": "Sun, H. et al. (2014). Physical fitness of children and adolescents in China. Journal of Sport and Health Science, 3(4), 263-267.\nChina National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.",
                "degiskenler": ["Süre (sn)"]
            },
            "Durarak Uzun Atlama (CNPFM)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü ölçmektir.

**Ekipman:** Mezura veya atlama matı, kaymaz zemin.

**Uygulama:**
1. Sporcu çizginin gerisinde ayaklar omuz genişliğinde durur.
2. Kollarını sallayarak çift ayakla maksimum mesafeye atlar.
3. 3 deneme yapılır; en iyi mesafe kaydedilir.

**Skorlama:** En iyi atlama mesafesi (cm).
                """,
                "kaynak": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.\nSun, H. et al. (2014). Physical fitness of children and adolescents in China. Journal of Sport and Health Science, 3(4), 263-267.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"]
            },
            "Otur-Uzan Testi (CNPFM)": {
                "protokol": """
**Amaç:** Alt sırt ve hamstring esnekliğini ölçmektir.

**Ekipman:** Standart sit-and-reach kutusu.

**Uygulama:**
1. Sporcu çift bacak uzatılmış oturur, ayak tabanları kutu yüzeyine değer.
2. İki el ile öne uzanılır ve pozisyon 2 saniye korunur.
3. 2 deneme yapılır; en iyi değer kaydedilir.

**Skorlama:** Uzanma mesafesi (cm). Çin standardında topuklar ölçüm cihazının plakasına dayanır ve skor sınırları eksi değer içerir; bu, sıfır noktasının ayak tabanında olduğunu gösterir. Resmi CNPFM kılavuzundan ayrıca doğrulanamadı.

**Normatif:** ⚠️ Bu test için programda **yaş/cinsiyet bazlı persentil tablosu YOKTUR.** Önceden bağlı olan Eurofit normları (Tomkinson ve ark., 2018) ayak tabanını 15 cm sayan farklı bir ölçek kullandığı için kaldırıldı (6 numaralı sabit karar: test norma yalnızca protokol gerçekten eşleştiğinde bağlanır).
                """,
                "kaynak": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "1000m Koşusu - Erkek / 800m Koşusu - Kadın (CNPFM)": {
                "protokol": """
**Amaç:** Aerobik dayanıklılığı ölçmektir — CNPFM'nin temel kardiyorespiratuar testidir.

**Ekipman:** Standart atletizm pisti (400m), kronometre.

**Uygulama:**
1. Erkekler 1000m (2.5 tur), kadınlar 800m (2 tur) koşar.
2. Tempolu koşu önerilir; yürüyüşe izin verilir ancak skor düşer.

**Skorlama:** Tamamlama süresi (dakika:saniye) — az = iyi.
                """,
                "kaynak": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.\nSun, H. et al. (2014). Physical fitness of children and adolescents in China. Journal of Sport and Health Science, 3(4), 263-267.",
                "degiskenler": ["Cinsiyet (E/K)", "Süre (dakika)", "Süre (saniye)"]
            },
            "Mekik (Sit-Up) 1 Dakika (CNPFM)": {
                "protokol": """
**Amaç:** Karın kas kuvveti ve dayanıklılığını ölçmektir.

**Ekipman:** Mat, kronometre.

**Uygulama:**
1. Sporcu sırtüstü yatar, dizler 90° bükülü, eller ense arkasında kenetli, ayaklar sabitlenir.
2. 1 dakika boyunca maksimum sayıda mekik yapılır.
3. Her tekrarda dirsekler dizlere değmeli, sırt yere değmelidir.

**Skorlama:** 1 dakikada tamamlanan geçerli tekrar sayısı.
                """,
                "kaynak": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.",
                "degiskenler": ["Tekrar Sayısı (1 dk)"]
            },
            "Vücut Kompozisyonu (CNPFM)": {
                "protokol": """
**Amaç:** Çin ulusal standartlarına göre vücut kompozisyonunu değerlendirmektir.

**Ekipman:** Boy ölçer, tartı.

**Uygulama:**
1. Boy stadiometre ile ölçülür (cm).
2. Kilo hafif kıyafetle ölçülür (kg).
3. VKİ hesaplanır.

**Skorlama:** VKİ (kg/m²).

**CNPFM VKİ Sınıflandırması (18+ yaş):**
- < 18.5: Zayıf
- 18.5–23.9: Normal
- 24.0–27.9: Fazla kilolu
- ≥ 28.0: Obez
                """,
                "kaynak": "China National Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China.\nZhou, B. F. (2002). Predictive values of body mass index and waist circumference for risk factors of certain related diseases in Chinese adults. Biomedical and Environmental Sciences, 15(1), 83-96.",
                "degiskenler": ["Boy (cm)", "Kilo (kg)"]
            }
        },
        "Karlsruher Motorik-Screening": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Yana Sıçrama (KMS)": {
                "protokol": """
**Amaç:** Anaokulu çocuklarının koordinasyon ve hız kuvvetini ölçmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 50 cm uzunluğunda, 2 cm yüksekliğinde tahta engel, kronometre.

**Uygulama:**
1. Çocuk engelin bir yanında çift ayak durur.
2. 15 saniye boyunca engelin sağından soluna çift ayak sıçrar.
3. Her iki yöne geçiş bir tekrar sayılır.
4. 2 deneme yapılır; dinlenme aralığı verilir.

**Skorlama:** 15 saniyede yapılan geçerli sıçrama sayısı — çok = iyi.
                """,
                "kaynak": "Worth, A., & Bös, K. (2015). Das Karlsruher Motorik-Screening für Kindergartenkinder (KMSK). Motorik, 38(1), 15-22.",
                "degiskenler": ["Deneme 1 (tekrar)", "Deneme 2 (tekrar)"]
            },
            "Balans (Denge) Testi (KMS)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların dinamik dengesini değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 3 m uzunluğunda, 6 cm genişliğinde denge kirişi veya bant.

**Uygulama:**
1. Çocuk denge kirişi üzerinde öne doğru yürür.
2. Düşmeden kat edilen mesafe veya adım sayısı kaydedilir.
3. 2 deneme yapılır.

**Skorlama:** Düşmeden tamamlanan adım sayısı veya mesafe (cm).
                """,
                "kaynak": "Worth, A., & Bös, K. (2015). Das Karlsruher Motorik-Screening für Kindergartenkinder (KMSK). Motorik, 38(1), 15-22.",
                "degiskenler": ["Deneme 1 (adım)", "Deneme 2 (adım)"]
            },
            "Top Yakalama Testi (KMS)": {
                "protokol": """
**Amaç:** El-göz koordinasyonunu ve reaksiyon hızını değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Standart boyutta yumuşak top (çocuk boyu), mezura.

**Uygulama:**
1. Uygulayıcı 1.5 m mesafeden topu çocuğa atar.
2. Çocuk topu iki eliyle yakalamaya çalışır.
3. 10 deneme yapılır.

**Skorlama:** 10 denemede başarılı yakalama sayısı.
                """,
                "kaynak": "Worth, A., & Bös, K. (2015). Das Karlsruher Motorik-Screening für Kindergartenkinder (KMSK). Motorik, 38(1), 15-22.",
                "degiskenler": ["Yakalama Sayısı (10 denemede)"]
            },
            "20m Sprint (KMS)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların lokomotor hız gelişimini ölçmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 20m düz alan, kronometre.

**Uygulama:**
1. Çocuk ayakta başlangıç pozisyonunda hazır bekler.
2. Başlangıç işaretiyle 20 metre maksimal hızla koşar.
3. 2 deneme yapılır; en iyi süre kaydedilir.

**Skorlama:** En iyi tamamlama süresi (sn) — az = iyi.
                """,
                "kaynak": "Worth, A., & Bös, K. (2015). Das Karlsruher Motorik-Screening für Kindergartenkinder (KMSK). Motorik, 38(1), 15-22.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
            }
        },
        "Latorre Román Fitness Battery": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "20m Sprint (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocuklarda lokomotor hızı değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 20m düz alan, kronometre veya fotosel.

**Uygulama:**
1. Çocuk ayakta başlangıç pozisyonunda hazır bekler.
2. Başlangıç işaretiyle 20 metre maksimal hızla koşar.
3. 2 deneme yapılır; en iyi süre kaydedilir.

**Skorlama:** En iyi tamamlama süresi (sn) — az = iyi.
                """,
                "kaynak": "Latorre-Román, P. A., Mora-López, D., & García-Pinillos, F. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526.\nLatorre-Román, P. A. et al. (2017). Physical fitness in preschool children. European Journal of Pediatrics, 176(3), 365-371.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
            },
            "Durarak Uzun Atlama (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocuklarda alt ekstremite patlayıcı gücünü değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Mezura veya atlama matı, kaymaz zemin.

**Uygulama:**
1. Çocuk çizginin gerisinde ayaklar omuz genişliğinde durur.
2. Kollarını sallayarak çift ayakla maksimum mesafeye atlar.
3. 2 deneme yapılır; en iyi mesafe kaydedilir.

**Skorlama:** En iyi atlama mesafesi (cm).
                """,
                "kaynak": "Latorre-Román, P. A. et al. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "El Kavrama Kuvveti (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocuklarda üst ekstremite kas kuvvetini değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Çocuk boyutuna uygun el dinamometresi.

**Uygulama:**
1. Çocuk ayakta, dirsek tam ekstansiyonda dinamometreyi sıkar.
2. Her el için 2 deneme yapılır; en iyi değer kaydedilir.

**Skorlama:** Dominant elin en iyi değeri (kg).
                """,
                "kaynak": "Latorre-Román, P. A. et al. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526.",
                "degiskenler": ["Sağ El (kg)", "Sol El (kg)"]
            },
            "Tek Ayak Denge Testi (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocuklarda statik dengeyi değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Düz zemin, kronometre.

**Uygulama:**
1. Çocuk dominant ayağı üzerinde tek ayak durur; gözler açık.
2. 30 saniye boyunca denge korunmaya çalışılır.
3. Her denge kaybında sayaç artırılır.
4. 2 deneme yapılır.

**Skorlama:** 30 saniyede denge kaybı sayısı — az = iyi.
                """,
                "kaynak": "Latorre-Román, P. A. et al. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526.",
                "degiskenler": ["Deneme 1 (düşme sayısı)", "Deneme 2 (düşme sayısı)"]
            },
            "Top Fırlatma Testi (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocuklarda üst ekstremite kuvvetini ve koordinasyonunu değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** 1 kg medisin topu veya standart çocuk topu, mezura.

**Uygulama:**
1. Çocuk çizginin gerisinde oturur veya ayakta durur.
2. Topu iki eliyle başın üzerinden maksimum mesafeye fırlatır.
3. 2 deneme yapılır; en iyi mesafe kaydedilir.

**Skorlama:** En iyi fırlatma mesafesi (cm).
                """,
                "kaynak": "Latorre-Román, P. A. et al. (2016). Battery of tests to assess motor fitness in preschool children. Revista Internacional de Medicina y Ciencias de la Actividad Física y del Deporte, 16(63), 509-526.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)"]
            },
            "Vücut Kompozisyonu (Latorre)": {
                "protokol": """
**Amaç:** Okul öncesi çocukların büyüme ve vücut kompozisyonunu değerlendirmektir.

**Hedef Grup:** 3-6 yaş.

**Ekipman:** Boy ölçer (stadiometre), tartı.

**Uygulama:**
1. Boy: Çocuk dik dururken stadiometre ile ölçülür (cm).
2. Kilo: Hafif kıyafetle tartılır (kg).
3. VKİ hesaplanır.

**Skorlama:** Boy (cm), Kilo (kg), VKİ (kg/m²).
                """,
                "kaynak": "Latorre-Román, P. A. et al. (2017). Physical fitness in preschool children. European Journal of Pediatrics, 176(3), 365-371.",
                "degiskenler": ["Boy (cm)", "Kilo (kg)"]
            }
        },

        "KTK3+ Motor Koordinasyon Test Bataryası": {
            "_kunye": {
                "gelistiren": "Orijinal KTK: Ernst J. Kiphard & Friedhelm Schilling. KTK3+ uyarlaması: Matthieu Lenoir ve ekibi (Universiteit Gent, Hareket ve Spor Bilimleri Bölümü)",
                "ulke": "Almanya (orijinal KTK, 1974) — KTK3+ normları Flaman Bölgesi / Belçika",
                "yil": "1974 (KTK) · 2021 (KTK3+ normatif çalışması)",
                "hedef_yas": "KTK: 5-14 yaş · KTK3+ normatif tabloları: 6-19 yaş",
                "yas_araligi": (6, 19),                      # hedef_yas: "KTK3+ normatif tabloları: 6-19 yaş" (5-14 orijinal KTK)
                "yayginlik": "Dünyada kaba motor koordinasyonu ölçmek için en yaygın kullanılan bataryadır. Flaman Spor Pusulası (Sports Compass / SportKompas) yetenek yönlendirme modelinin motor koordinasyon bloğunu oluşturur. Brezilya, Portekiz, İtalya, Çin, Slovakya ve Türkiye dahil çok sayıda ülkede uygulanmıştır."
            },

            "Dengede Geriye Yürüme (Balancing Backwards)": {
                "protokol": """
**Amaç:** Dinamik denge ve vücut kontrolünü, giderek daralan kirişler üzerinde geriye yürüyerek değerlendirmektir.

**Hedef Grup:** 6-19 yaş.

**Ekipman:** 3 metre uzunluğunda, 3 cm yüksekliğinde ahşap kirişler; genişlikleri sırasıyla **6.0 cm**, **4.5 cm** ve **3.0 cm**. Kirişler yerden yaklaşık 5 cm yükseltilmiş destekler üzerine yerleştirilir.

**Uygulama:**
1. Çocuk her kiriş için önce bir kez ileri, bir kez geri yürüyerek deneme (alıştırma) yapar.
2. Ardından aynı kirişte **geriye doğru** 3 geçerli deneme yapılır.
3. Her denemede atılan adım sayısı sayılır; bir denemede **en fazla 8 adım** kaydedilir (8. adımdan sonra sayım durur).
4. Ayak yere değdiğinde o deneme sona erer; o ana kadarki adım sayısı yazılır.
5. Aynı sıra üç kiriş için de tekrarlanır: önce 6 cm, sonra 4.5 cm, en son 3 cm.

**Skorlama:** Her kiriş için 3 denemenin adım toplamı (maks. 24), üç kirişin toplamı **maksimum 72 adım**dır. Yüksek skor = iyi.

**Normatif:** Flaman normları (Coppens ve ark., 2021; n=2.271, 6-19 yaş) programda yaş ve cinsiyete göre otomatik uygulanır.
                """,
                "kaynak": "Kiphard, E. J., & Schilling, F. (2007). Körperkoordinationstest für Kinder (KTK), 2. Auflage. Beltz Test GmbH, Weinheim.\nCoppens, E., Laureys, F., Mostaert, M., D'Hondt, E., Deconinck, F. J. A., & Lenoir, M. (2021). Validation of a motor competence assessment tool for children and adolescents (KTK3+) with normative values for 6- to 19-year-olds. Frontiers in Physiology, 12, 652952.\nVandorpe, B., Vandendriessche, J., Lefevre, J., et al. (2011). The KörperkoordinationsTest für Kinder: reference values and suitability for 6-12-year-old children in Flanders. Scandinavian Journal of Medicine & Science in Sports, 21(3), 378-388.",
                "degiskenler": ["6 cm Kiriş - Toplam Adım", "4.5 cm Kiriş - Toplam Adım", "3 cm Kiriş - Toplam Adım"]
            },

            "Yana Sıçrama (Jumping Sideways)": {
                "protokol": """
**Amaç:** Alt ekstremite hız-koordinasyonunu (ritmik, tekrarlı yana sıçrama becerisini) ölçmektir.

**Hedef Grup:** 6-19 yaş.

**Ekipman:** 100 × 60 cm ölçülerinde bir zemin matı; ortasına uzunlamasına sabitlenmiş **60 × 4 × 2 cm** ahşap çıta; kronometre.

**Uygulama:**
1. Çocuk çıtanın bir yanında, çift ayak üzerinde durur.
2. Önce 5 sıçramalık alıştırma yapılır.
3. Komutla birlikte **15 saniye** boyunca çıtanın üzerinden çift ayakla sağa-sola, olabildiğince hızlı sıçrar.
4. Çıtaya basmak, matın dışına çıkmak veya tek ayakla inmek geçersiz sayılır.
5. **2 deneme** yapılır; denemeler arasında kısa dinlenme verilir.

**Skorlama:** İki denemede yapılan **geçerli sıçramaların toplamı**. Yüksek skor = iyi.

**Normatif:** Flaman normları (Coppens ve ark., 2021) yaş ve cinsiyete göre otomatik uygulanır.
                """,
                "kaynak": "Kiphard, E. J., & Schilling, F. (2007). Körperkoordinationstest für Kinder (KTK), 2. Auflage. Beltz Test GmbH, Weinheim.\nCoppens, E., Laureys, F., Mostaert, M., D'Hondt, E., Deconinck, F. J. A., & Lenoir, M. (2021). Validation of a motor competence assessment tool for children and adolescents (KTK3+) with normative values for 6- to 19-year-olds. Frontiers in Physiology, 12, 652952.",
                "degiskenler": ["Deneme 1 (sıçrama sayısı)", "Deneme 2 (sıçrama sayısı)"]
            },

            "Yana Platform Değiştirme (Moving Sideways)": {
                "protokol": """
**Amaç:** Vücudun bir bütün olarak yer değiştirme (lateral yer değiştirme) koordinasyonunu ve hızını ölçmektir.

**Hedef Grup:** 6-19 yaş.

**Ekipman:** 2 adet ahşap platform (**25 × 25 × 5.7 cm**, her birinin altında 3.7 cm'lik 4 ayak); kronometre.

**Uygulama:**
1. Çocuk platformlardan birinin üzerinde durur; ikinci platform yanındadır.
2. Komutla birlikte **20 saniye** boyunca: elleriyle boştaki platformu yanına koyar → üzerine adımlar → arkada kalan platformu alıp yanına koyar → üzerine adımlar... şeklinde yana doğru ilerler.
3. Yön serbesttir; sürekli aynı yöne ilerlenir.
4. **2 deneme** yapılır.

**Skorlama:** Her deneme için **platform yerleştirme sayısı + platform üzerine adımlama sayısı** toplanır (20 saniyede). İki denemenin toplamı skordur. Yüksek skor = iyi.

**Normatif:** Flaman normları (Coppens ve ark., 2021) yaş ve cinsiyete göre otomatik uygulanır.
                """,
                "kaynak": "Kiphard, E. J., & Schilling, F. (2007). Körperkoordinationstest für Kinder (KTK), 2. Auflage. Beltz Test GmbH, Weinheim.\nCoppens, E., Laureys, F., Mostaert, M., D'Hondt, E., Deconinck, F. J. A., & Lenoir, M. (2021). Validation of a motor competence assessment tool for children and adolescents (KTK3+) with normative values for 6- to 19-year-olds. Frontiers in Physiology, 12, 652952.",
                "degiskenler": ["Deneme 1 (puan)", "Deneme 2 (puan)"]
            },

            "Göz-El Koordinasyonu (Duvara Atıp Yakalama)": {
                "protokol": """
**Amaç:** Üst ekstremite nesne kontrolünü — göz-el koordinasyonunu — ölçmektir. Bu test KTK3+ ile bataryaya eklenmiştir ve klasik KTK'da bulunmaz.

**Hedef Grup:** 6-19 yaş.

**Ekipman:** Tenis topu; düz duvar; duvara çizilmiş **1 m² (1 × 1 m) hedef kare** (karenin alt kenarı yerden 1 m yükseklikte); kronometre.

**Uygulama:**
1. Çocuk duvardan **1 metre** uzakta durur.
2. Komutla birlikte **30 saniye** boyunca tenis topunu hedef kareye atıp sektikten sonra yakalar.
3. Top kareye isabet etmezse veya yakalanamazsa o tekrar sayılmaz.
4. **2 deneme** yapılır.

**Skorlama:** İki denemede yapılan **başarılı yakalama sayısının toplamı**. Yüksek skor = iyi.

**Normatif:** Flaman normları (Coppens ve ark., 2021) yaş ve cinsiyete göre otomatik uygulanır. **Dikkat:** 6-7 yaş grubunda taban etkisi vardır (medyan değerler 0-5 aralığındadır); bu yaşlarda tek bir skor üzerinden yorum yapmak yanıltıcı olabilir.
                """,
                "kaynak": "Coppens, E., Laureys, F., Mostaert, M., D'Hondt, E., Deconinck, F. J. A., & Lenoir, M. (2021). Validation of a motor competence assessment tool for children and adolescents (KTK3+) with normative values for 6- to 19-year-olds. Frontiers in Physiology, 12, 652952.",
                "degiskenler": ["Deneme 1 (yakalama)", "Deneme 2 (yakalama)"]
            },

            "Tek Ayak Engel Üzerinden Sıçrama (Hopping for Height)": {
                "protokol": """
**Amaç:** Tek bacak üzerinde dinamik denge ve sıçrama koordinasyonunu ölçmektir. Klasik KTK'nın (KTK4) dördüncü alt testidir.

**Hedef Grup:** 5-14 yaş (orijinal KTK normları).

**Ekipman:** 12 adet sünger blok (**50 × 20 × 5 cm**). Bloklar üst üste konularak yükseklik 5'er cm artırılır.

**Uygulama:**
1. Başlangıç yüksekliği çocuğun yaşına göre belirlenir (genellikle 6 yaş altı: 0 cm; 6-7 yaş: 5 cm; daha büyükler: 15 cm'den başlanabilir).
2. Çocuk tek ayak üzerinde sıçrayarak engelin üzerinden geçer ve **indikten sonra aynı ayakla en az 2 sıçrama daha** yaparak kontrolü koruduğunu gösterir.
3. Her yükseklikte **3 deneme hakkı** vardır.
4. Yükseklik 5 cm artırılarak devam edilir; iki bacak ayrı ayrı test edilir.

**Skorlama (bacak başına):** 1. denemede başarı = **3 puan**, 2. denemede = **2 puan**, 3. denemede = **1 puan**. Her bacak için maksimum **39 puan**, toplam **78 puan**. Yüksek skor = iyi.

**Normatif:** ⚠️ Bu test için programda **yaş/cinsiyet bazlı persentil tablosu YOKTUR.** Gerekçe: KTK3+ normatif çalışması (Coppens ve ark., 2021) bu testi bataryadan çıkarmış ve yerine göz-el koordinasyonunu koymuştur; makale "HH testi KTK4 protokolünden sıklıkla çıkarılmaktadır" demektedir. Orijinal Alman persentil tabloları (Kiphard & Schilling) yalnızca basılı test kılavuzunda yer alır ve telifli olduğu için programa alınmamıştır.

**Karşılaştırma için yayınlanmış ORTALAMALAR (persentil değil, yalnızca ortalama):**
- İtalya (Giuriato ve ark., 2021; n=2.206): 6 yaş K 21.6 / E 25.7 · 8 yaş K 33.9 / E 36.2 · 10 yaş K 51.2 / E 50.7 · 12 yaş K 54.0 / E 55.6
- Slovakya (Chovanová ve ark., 2023; n=381): 7 yaş K 42.1 / E 38.2 · 9 yaş K 24.8 / E 32.4

Bu değerler ortalamadır; bir çocuğun persentil sırasını vermez. Uygun bir persentil çalışması bulunduğunda programa eklenecektir.
                """,
                "kaynak": "Kiphard, E. J., & Schilling, F. (2007). Körperkoordinationstest für Kinder (KTK), 2. Auflage. Beltz Test GmbH, Weinheim.\nGiuriato, M., Biino, V., Bellafiore, M., Battaglia, G., Palma, A., Baldari, C., Guidetti, L., Gallotta, M. C., Schena, F., & Lanza, M. (2021). Gross motor coordination: We have a problem! A study with the Körperkoordinations Test für Kinder in youth (6-13 years). Frontiers in Pediatrics, 9, 785990. https://doi.org/10.3389/fped.2021.785990\nChovanová, E., Majherová, M., & Bendíková, E. (2023). Level of motor coordination in school-aged children. Physical Activity Review, 11(2).",
                "degiskenler": ["Sağ Bacak Puanı (maks 39)", "Sol Bacak Puanı (maks 39)"]
            }
        },

        "Flaman Spor Pusulası (FSC) — Ek Testler": {
            "_kunye": {
                "gelistiren": "Gent Üniversitesi, Hareket ve Spor Bilimleri Bölümü (Lenoir, Philippaerts, Vaeyens, Pion ve ark.)",
                "ulke": "Belçika (Flaman Bölgesi)",
                "yil": "2015 (Opstoel ve ark., PLoS ONE; Pion, doktora tezi)",
                "hedef_yas": "Branşa yönlendirme çalışması 9-11 yaş (n=620; 347 erkek, 273 kız)",
                "yas_araligi": (9, 11),                      # hedef_yas: "9-11 yaş"
                "yayginlik": "Flaman Spor Pusulası (Sports Compass / SportKompas) 17 testlik yönlendirme bataryasıdır: 5 antropometrik, 8 fiziksel uygunluk, 4 motor koordinasyon. KTK motor koordinasyon testleri 'KTK3+ Motor Koordinasyon Test Bataryası' altında, Eurofit ile ortak testler (20m mekik, otur-uzan, 10x5m, durarak uzun atlama, mekik) kendi bataryalarında yer alır. Bu bölüm bataryanın kalan dört testini toplar: top sektirme, omuz rotasyonu, diz üstü şınav, oturma yüksekliği."
            },

            "Top Sektirme — Alternatif El (BOT-2)": {
                "protokol": """
**Amaç:** Üst ekstremite nesne kontrolünü (top sektirme becerisini) değerlendirmektir. Flaman Spor Pusulası'nın motor koordinasyon bloğunda yer alır; BOT-2'nin üst ekstremite koordinasyonu alt testinden alınmış kısa bir maddedir.

**Hedef Grup:** Opstoel ve ark. (2015) çalışmasında 9-11 yaş.

**Ekipman:** Tenis topu, düz ve sert zemin.

**Uygulama:**
1. Çocuk ayakta durur ve tenis topunu bir elle yere sektirir.
2. Top her sektirmede diğer elle karşılanıp sektirilir; eller sırayla değişir.
3. Hedef, art arda **10 doğru sektirme**dir. Kontrol kaybedildiğinde veya eller sırayla değişmediğinde sayım durur.
4. İlk denemede 10'a ulaşılamazsa **ikinci deneme** yapılır.

**Skorlama:** Art arda yapılan doğru sektirme sayısı (maksimum 10). İki denemeden en iyisi kaydedilir. Yüksek skor = iyi.

**Güvenirlik:** Test-tekrar test r = .59 (8-12 yaş); iç korelasyon r = .82 (8-11 yaş) (BOT-2 kılavuzu, Opstoel ve ark., 2015'te aktarıldığı şekliyle).

**Normatif:** ⚠️ Bu test için programda **yaş/cinsiyet bazlı persentil tablosu YOKTUR.** Gerekçe: BOT-2 normları basılı ve telifli kılavuzdadır ve tek tek madde düzeyinde değil, alt test düzeyinde (ölçek puanı) verilir; bu maddenin ham skoru için yayınlanmış bir persentil çalışması bulunamamıştır.

**Karşılaştırma için yayınlanmış ORTALAMALAR (persentil değil):** Opstoel ve ark. (2015), 9-11 yaş Flaman çocuklar — dövüş sporları grubu 8.00 ± 2.66, diğer tüm çocuklar (birlikte) 8.79 ± 2.16; grup ortalamaları 8.00-9.02 aralığındadır.

**⚠️ Tavan etkisi:** Maksimum skor 10 olduğu ve ortalamalar 8-9 civarında toplandığı için test, bu yaş grubunda iyi çocukları birbirinden ayırt etmekte zayıftır (Opstoel ve ark., 2015). 10 skoru "üst sınıra ulaştı" olarak okunmalıdır.
                """,
                "kaynak": "Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric characteristics, physical fitness and motor coordination of 9 to 11 year old children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. https://doi.org/10.1371/journal.pone.0126282\nBruininks, R. H., & Bruininks, B. D. (2005). Bruininks-Oseretsky Test of Motor Proficiency, Second Edition (BOT-2). Minneapolis, MN: Pearson Assessment.",
                "degiskenler": ["Deneme 1 (doğru sektirme, maks 10)", "Deneme 2 (doğru sektirme, maks 10)"]
            },

            "Omuz Rotasyon Testi (Sopa/İp)": {
                "protokol": """
**Amaç:** Omuz kuşağının hareketliliğini (esnekliğini) değerlendirmektir. Flaman Spor Pusulası'nın fiziksel uygunluk bloğunda yer alır.

**Hedef Grup:** Opstoel ve ark. (2015) çalışmasında 9-11 yaş.

**Ekipman:** Üzerinde santimetre ölçeği bulunan sopa veya ip; ölçüm şeridi. Biakromiyal genişlik ölçülecekse antropometre veya kaliper.

**Uygulama:**
1. Sporcu ayakta, sopayı/ipi gövdenin önünde iki eliyle avuçlar aşağı bakacak şekilde geniş tutar.
2. Kolları dirsekler bükülmeden baş üzerinden geriye, sırtın arkasına doğru geçirir ve öne geri getirir.
3. El aralığı her denemede daraltılır; hareketin dirsek bükülmeden tamamlanabildiği **en dar el aralığı** belirlenir.
4. El aralığı 0.5 cm hassasiyetle kaydedilir.

**Skorlama:** Hareketin tamamlanabildiği en dar el aralığı (cm). **Düşük skor = iyi** esneklik (Opstoel ve ark., 2015).

**Omuz genişliği düzeltmesi:** Kaynakların bir kısmında net skor, el aralığından biakromiyal genişlik çıkarılarak hesaplanır (geniş omuzlu çocuk aleyhine farkı giderir). Opstoel ve ark. (2015) bu düzeltmenin yapılıp yapılmadığını belirtmez. Program ham el aralığını her zaman kaydeder; biakromiyal genişlik girilirse **net skoru** da ayrıca hesaplar. Farklı ölçüm günlerini ve çocukları karşılaştırırken aynı skor türü kullanılmalıdır.

**Güvenirlik:** Test-tekrar test r = .73-.96 (9-13 yaş; Fetz & Kornexl, 1993, Opstoel ve ark., 2015'te aktarıldığı şekliyle).

**Normatif:** ⚠️ Bu test için programda **yaş/cinsiyet bazlı persentil tablosu YOKTUR.** Bu protokol için yayınlanmış, açık erişimli bir persentil çalışması bulunamamıştır. Flaman branş grubu ortalamaları (Opstoel ve ark., 2015) Paket 4'te branş grubu profilleri ile birlikte girilecektir.
                """,
                "kaynak": "Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric characteristics, physical fitness and motor coordination of 9 to 11 year old children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. https://doi.org/10.1371/journal.pone.0126282\nFetz, F., & Kornexl, E. (1993). Sportmotorische Tests (3. Aufl.). Wien: ÖBV.\nJohnson, B. L., & Nelson, J. K. (1986). Practical measurements for evaluation in physical education (4th ed.). Minneapolis, MN: Burgess.",
                "degiskenler": ["En Dar El Aralığı (cm)", "Biakromiyal Genişlik (cm) — opsiyonel"]
            },

            "Diz Üstü Şınav — 30 sn (BOT-2)": {
                "protokol": """
**Amaç:** Üst beden kas kuvveti ve dayanıklılığını değerlendirmektir. Flaman Spor Pusulası'nın fiziksel uygunluk bloğunda yer alır; BOT-2'nin kuvvet alt testinden alınmıştır.

**Hedef Grup:** Opstoel ve ark. (2015) çalışmasında 9-11 yaş.

**Ekipman:** Mat, kronometre.

**Uygulama:**
1. Sporcu diz üstü şınav pozisyonu alır: dizler matta, eller omuz genişliğinde yerde, gövde baştan dizlere kadar düz.
2. Komutla birlikte **30 saniye** boyunca mümkün olduğunca çok sayıda doğru şınav yapılır.
3. Gövdenin düz çizgisi bozulan veya tam yapılmayan tekrarlar sayılmaz. Form ölçütlerinin ayrıntısı BOT-2 uygulama kılavuzunda tanımlıdır; aynı uygulayıcı her ölçümde aynı ölçütleri kullanmalıdır.

**Skorlama:** 30 saniyede tamamlanan doğru tekrar sayısı. Yüksek skor = iyi.

**Güvenirlik:** Test-tekrar test r = .88 (8-12 yaş); iç korelasyon r = .87 (8-11 yaş) (BOT-2 kılavuzu, Opstoel ve ark., 2015'te aktarıldığı şekliyle).

**Not:** FitnessGram şınav testi (tam şınav, metronom ritmi, süre sınırı yok) ile protokolü farklıdır; skorlar birbirinin yerine kullanılamaz ve o testin normlarına bağlanmamıştır.

**Normatif:** ⚠️ Bu test için programda **yaş/cinsiyet bazlı persentil tablosu YOKTUR.** Gerekçe: BOT-2 normları basılı ve telifli kılavuzdadır ve madde düzeyinde değil, alt test düzeyinde verilir; 30 saniyelik diz üstü şınav ham skoru için yayınlanmış bir persentil çalışması bulunamamıştır. Flaman branş grubu ortalamaları (Opstoel ve ark., 2015) Paket 4'te girilecektir.
                """,
                "kaynak": "Opstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric characteristics, physical fitness and motor coordination of 9 to 11 year old children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. https://doi.org/10.1371/journal.pone.0126282\nBruininks, R. H., & Bruininks, B. D. (2005). Bruininks-Oseretsky Test of Motor Proficiency, Second Edition (BOT-2). Minneapolis, MN: Pearson Assessment.",
                "degiskenler": ["Diz Üstü Şınav Tekrarı (30 sn)"]
            },

            "Oturma Yüksekliği": {
                "protokol": """
**Amaç:** Baş-gövde uzunluğunu ölçmek ve boyla birlikte bacak uzunluğunu ve gövde/boy oranını hesaplamaktır. Flaman Spor Pusulası'nın antropometri bloğunda yer alır.

**Hedef Grup:** Normlar 6-17 yaş (Ankara, 2017).

**Ekipman:** Stadiometre veya antropometre (Opstoel ve ark., 2015: portatif Harpenden stadiometre, 0.1 cm; Özer & Özdemir, 2020: Martin tipi antropometre, 1 mm), yüksekliği bilinen sabit bir oturak/sıra.

**Uygulama:**
1. Sporcu ayakkabısız, hafif kıyafetle oturağa oturur; sırt ve kalça ölçüm çubuğuna dayanır.
2. Gövde dik, baş Frankfurt düzleminde (göz-kulak hattı yere paralel) tutulur; eller uyluklar üzerinde, ayaklar destekli.
3. Ölçüm kafası başın en üst noktasına (vertex) indirilir ve okuma yapılır.
4. Oturak yüksekliği okunan değerden **çıkarılarak** net oturma yüksekliği bulunur. Programa bu net değer girilir.

**Skorlama:** Net oturma yüksekliği (cm, 0.1 cm). Program, sporcu profilindeki boyu kullanarak şunları otomatik hesaplar:
- Bacak Uzunluğu (cm) = Boy − Oturma Yüksekliği
- Oturma Yüksekliği / Boy oranı

**Normatif:** Ankara 2017 okul çocukları (Özer & Özdemir, 2020; n=1.485, 6-17 yaş, E/K) yaş ve cinsiyete göre persentil olarak programda otomatik uygulanır. Bu bir **antropometrik ölçüdür**: Yüksek ya da düşük değer "iyi" veya "kötü" anlamına gelmez, yalnızca akranlara göre konumu gösterir.

**Persentillerin hesaplanması:** P5-P95 değerleri makalenin Tablo 3 ve 4'teki L, M, S parametrelerinden standart LMS formülüyle hesaplanmıştır. Makalenin tablolarında iki sütun grubu birbiriyle çelişir: Basılı SD sütunu, persentil/LMS sütunlarının ima ettiği yayılımla uyuşmaz (örneğin 17 yaş erkekte basılı SD 3.06 cm, LMS'ten çıkan örtülü SD 4.01 cm). Ayrıca basılı uç persentiller (P3-P5, P90-P97) kendi L, M, S değerleriyle de tutarsızdır. Esas alınan taraf L, M, S'tir. Tutarlılık kontrolü: 24 yaş × cinsiyet hücresinin hepsinde P5-P95 ve P25-P75 aralıklarından çıkan örtülü SD, yuvarlamadan önce 0.02 cm içinde aynıdır; örtülü SD ergenlikte genişleyip (12-13 yaş ≈ 4.6 cm) sonra daralır (17 yaş kız ≈ 3.4 cm) — biyolojik olarak beklenen örüntü. Basılı P25/P50/P75 değerleri de LMS hesabıyla 0.06 cm içinde örtüşür.

**Oturma yüksekliği / boy oranı için karşılaştırma ORTALAMALARI (Ankara 2017, persentil değil):**
- Erkek: 6 yaş 0.54 · 7-8 yaş 0.53 · 9-12 yaş 0.52 · 13-14 yaş 0.51 · 15-17 yaş 0.53 (SD 0.01-0.03)
- Kız: 6 yaş 0.54 · 7-8 yaş 0.53 · 9 yaş 0.52 · 10-12 yaş 0.53 · 13 yaş 0.52 · 14-17 yaş 0.54 (SD 0.01-0.03)
                """,
                "kaynak": "Özer, B. K., & Özdemir, A. (2020). Secular changes in anthropometric measurements of schoolchildren in Ankara, Turkey (1950–2017). Papers on Anthropology, 29(1), 121-139. https://doi.org/10.12697/poa.2020.29.1.09\nOpstoel, K., Pion, J., Elferink-Gemser, M., Hartman, E., Willemse, B., Philippaerts, R., Visscher, C., & Lenoir, M. (2015). Anthropometric characteristics, physical fitness and motor coordination of 9 to 11 year old children participating in a wide range of sports. PLoS ONE, 10(5), e0126282. https://doi.org/10.1371/journal.pone.0126282",
                "degiskenler": ["Oturma Yüksekliği (cm)"]
            }
        }

    },

    "Branşa Özgü Testler": {
        "Bireysel Sporlar": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Güreş": {
                "Special Wrestling Fitness Test (SWFT)": {
                    "protokol": """
    **Amaç:** Güreşçilerin branşa özgü fiziksel hazırlık düzeyini değerlendirmektir.

    **Ekipman:** Ağırlıklı manken (dummy), kalp atım hızı (KAH) monitörü.

    **Manken Ağırlığı (Marković Protokolü):**

    | Sporcu Ağırlığı   | Manken Ağırlığı |
    |--------------------|-----------------|
    | < 75 kg            | 22 kg           |
    | 75.00 – 89.99 kg    | 27 kg           |
    | ≥ 90 kg             | 32 kg           |

    **Uygulama:**
    1. Isınma: 10 dakika genel ısınma.
    2. 3 × 30 saniyelik aktif periyot, aralarında 20 saniye pasif dinlenme.
    3. Her periyotta sporcu mankeni suplex tekniğiyle maksimum sayıda sırtüstü devirir.
    4. Test bitiminde (HR0) ve 1. dakika dinlenmede (HR1) kalp atım hızı ölçülür.

    **Skorlama:**
    - TnThrows: Toplam atış sayısı
    - SWFT Index = (HR0 + HR1) / TnThrows × 100 (düşük = iyi)
    - TnThrows/BM: Vücut ağırlığına normalize atış sayısı
                    """,
                    "kaynak": "Marković, M., Kukić, F., Dopsaj, M., Kasum, G., Toskić, L., & Zarić, I. (2021). Validity of a novel specific wrestling fitness test. Journal of Strength and Conditioning Research, 35(12S), S51–S57.\nMarkovic, M., Dopsaj, M., Kasum, G. et al. (2017). Reliability of the two new specific wrestling tests. Archives of Budo, 13, 17–28.",
                    "degiskenler": ["Periyot 1 Atış Sayısı", "Periyot 2 Atış Sayısı", "Periyot 3 Atış Sayısı", "HR0 (bpm)", "HR1-dk (bpm)", "Manken Ağırlığı (kg)"]
                },
                "Modified SJFT (Güreş için)": {
                    "protokol": """
    **Amaç:** Özel judo fitness testinin güreşe uyarlanmış versiyonu; aerobik-anaerobik kapasiteyi ölçer.

    **Uygulama:**
    1. 3 periyot: 15 sn / 30 sn / 30 sn — aralarında 10 sn dinlenme.
    2. Her periyotta manken maksimum sayıda devrilir.
    3. Test bitiminde ve 1. dakikada HR ölçümü yapılır.

    **Skorlama:** SJFT Index = (HR0 + HR1) / TnThrows × 100
                    """,
                    "kaynak": "Franchini, E., Sterkowicz, S., Meira Jr, C. M., Gomes, F. R., & Tani, G. (2011). Technical variation in a sample of high level judo players. Perceptual and Motor Skills, 112(3), 768–776.",
                    "degiskenler": ["Periyot 1 Atış", "Periyot 2 Atış", "Periyot 3 Atış", "HR0 (bpm)", "HR1-dk (bpm)"]
                },
                "Simulated Wrestling Match (6 dk)": {
                    "protokol": """
    **Amaç:** Gerçek müsabaka koşullarını simüle ederek fizyolojik yanıtı ölçmek.

    **Uygulama:**
    1. Eşit ağırlık kategorisinde iki sporcu.
    2. 2 × 3 dakika mat süresi, 30 sn ara.
    3. Her periyot sonunda HR ve RPE (Borg skalası) ölçümü.

    **Skorlama:** HR, RPE, kazanılan/kaybedilen puan.
                    """,
                    "kaynak": "Yoon, J. (2002). Physiological profiles of elite senior wrestlers. Sports Medicine, 32(4), 225–233.",
                    "degiskenler": ["HR Periyot 1 Sonu (bpm)", "HR Periyot 2 Sonu (bpm)", "RPE Periyot 1 (6-20)", "RPE Periyot 2 (6-20)", "Kazanılan Puan", "Kaybedilen Puan"]
                },
                "Yo-Yo IR1 (Güreş)": {
                    "protokol": """
**Amaç:** Güreşçilerin aralıklı aerobik dayanıklılık kapasitesini değerlendirmektir.

**Ekipman:** 20m düz alan, beep ses sistemi, kronometre.

**Uygulama:**
1. 20m çift yön koşu, bip sesiyle artan hız.
2. Her turda 10 saniyelik aktif dinlenme (5m gidip gelme).
3. 2 kez üst üste bipe yetişemeyen testi bitirir.

**Skorlama:**
- Tamamlanan mesafe (m)
- VO2max (Maksimal Oksijen Tüketimi) = Mesafe × 0.0084 + 36.4

**Normatif (Elit Erkek Güreşçi):** > 1600m = İyi; > 2000m = Mükemmel
                    """,
                    "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test. Sports Medicine, 38(1), 37-51.\nYoon, J. (2002). Physiological profiles of elite senior wrestlers. Sports Medicine, 32(4), 225-233.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Judo": {
                "Special Judo Fitness Test (SJFT)": {
                    "protokol": """
    **Amaç:** Judocularda branşa özgü aerobik-anaerobik kapasiteyi değerlendirmektir — judoda geçerlilik ve güvenirliği en yüksek spesifik test olarak kabul edilmektedir.

    **Ekipman:** Judo matı, kronometre, KAH monitörü, iki uke (atılan sporcu) — her biri yaklaşık kendi ağırlığında.

    **Uygulama:**
    1. İki uke 6 metre aralıkla durur; tori (test edilen) ortada başlar.
    2. 3 periyot: **A = 15 sn**, **B = 30 sn**, **C = 30 sn** — A ile B arası 10 sn, B ile C arası 10 sn dinlenme.
    3. Her periyotta tori maksimum sayıda ippon (tam devirmeli) atış yapar.
    4. Test biter bitmez HR (HR0) ölçülür; 1 dakika sonra tekrar (HR1) ölçülür.

    **Skorlama:**
    - Toplam atış sayısı (TnThrows = A + B + C)
    - SJFT İndeksi = (HR0 + HR1) / TnThrows — **düşük = iyi**

    **Normatif (Elit Erkek):**
    - Mükemmel: İndeks < 11
    - İyi: 11–13
    - Orta: 13–15
    - Zayıf: > 15
                    """,
                    "kaynak": "Franchini, E., Sterkowicz, S., Meira Jr, C. M., Gomes, F. R., & Tani, G. (2011). Technical variation in a sample of high level judo players. Perceptual and Motor Skills, 112(3), 768-776.\nFranchini, E., Nakamura, F. Y., Takito, M. Y., Kiss, M. A., & Sterkowicz, S. (1998). Specific fitness test development for judo. Revista Brasileira de Medicina do Esporte, 4(3), 73-77.",
                    "degiskenler": ["Periyot A Atış", "Periyot B Atış", "Periyot C Atış", "HR0 (bpm)", "HR1-dk (bpm)"]
                },
                "Judo Fiziksel Uygunluk Testi (JPFT)": {
                    "protokol": """
    **Amaç:** Judocularda genel fiziksel uygunluğu çoklu parametrelerle değerlendirmektir.

    **Ekipman:** Pull-up barı, mat, kronometre.

    **Uygulama — 4 bileşen:**
    1. **Maksimal Pull-Up:** Pronated kavrayışla maksimum tekrar sayısı (kol tam ekstansiyondan çeneye kadar).
    2. **10m × 4 Mekik Koşusu:** 4 × 10m mekik koşusu süresi (sn).
    3. **Countermovement Jump (CMJ):** Eller kalçada, ön-çömelmeyle sıçrama; 3 deneme, en iyi.
    4. **Uchi-Komi Fitness Test (UKFT):** 30 sn boyunca bir partnerle maksimum sayıda uchi-komi (teknik giriş) tekrarı.

    **Skorlama:** Her bileşen ayrı ayrı kaydedilir; normatif tablolarla değerlendirilir.
                    """,
                    "kaynak": "Franchini, E., Julio, U. F., Panissa, V. L. G., Lira, F. S., Gerosa-Neto, J., & Branco, B. H. M. (2015). Short-term low-volume high-intensity intermittent training is superior to continuous training for fat loss and muscular gains in judo athletes. Journal of Exercise Rehabilitation, 11(5), 261-269.\nFranchini, E., & Del Vecchio, F. B. (2011). Estudos em modalidades esportivas de combate. Revista Brasileira de Educação Física e Esporte, 25(esp), 67-81.",
                    "degiskenler": ["Pull-Up (tekrar)", "10m×4 Koşu (sn)", "CMJ En İyi (cm)", "UKFT Tekrar Sayısı (30sn)"]
                },
                "Uchi-Komi Fitness Test (UKFT)": {
                    "protokol": """
    **Amaç:** Judocuların branşa özgü anaerobik kapasitesini ve teknik dayanıklılığını değerlendirmektir.

    **Ekipman:** Judo matı, kronometre, partner (uke).

    **Uygulama:**
    1. Tori ve uke judogi giyer; uke direnmez.
    2. Tori 30 saniye boyunca seçtiği bir teknikle maksimum uchi-komi (giriş-çıkış, tam devirmesiz) yapar.
    3. 3 set; setler arası 30 sn dinlenme.
    4. Her setin ardından HR ölçülür.

    **Skorlama:**
    - Her setteki tekrar sayısı
    - Setler arası yorgunluk düşüşü (%)

    **Not:** Basit ekipman gerektirdiği ve sahaya özgü olduğu için antrenman ortamında sıkça kullanılır.
                    """,
                    "kaynak": "Franchini, E., Brito, C. J., & Artioli, G. G. (2012). Weight loss in combat sports: physiological, psychological and performance effects. Journal of the International Society of Sports Nutrition, 9(1), 52.\nLopes-Silva, J. P. et al. (2021). Uchi-komi fitness test for monitoring judo-specific physical fitness. International Journal of Sports Physiology and Performance, 16(3), 430-436.",
                    "degiskenler": ["Set 1 (tekrar)", "Set 2 (tekrar)", "Set 3 (tekrar)", "HR Set 1 Sonu (bpm)", "HR Set 2 Sonu (bpm)", "HR Set 3 Sonu (bpm)"]
                },
                "Yo-Yo IR1 (Judo)": {
                    "protokol": """
**Amaç:** Judocuların aralıklı aerobik dayanıklılık kapasitesini değerlendirmektir.

**Ekipman:** 20m düz alan, beep ses sistemi, kronometre.

**Uygulama:**
1. 20m çift yön koşu, bip sesiyle artan hız.
2. Her turda 10 saniyelik aktif dinlenme (5m gidip gelme).
3. 2 kez üst üste bipe yetişemeyen testi bitirir.

**Skorlama:**
- Tamamlanan mesafe (m)
- VO2max (Maksimal Oksijen Tüketimi) = Mesafe × 0.0084 + 36.4

**Normatif (Elit Erkek Judocu):** > 1600m = İyi; > 2000m = Mükemmel
                    """,
                    "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test. Sports Medicine, 38(1), 37-51.\nFranchini, E. et al. (2011). Physiological profiles of elite judo athletes. Sports Medicine, 41(2), 147-166.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Yüzme": {
                "Critical Swimming Speed (CSS) Testi": {
                    "protokol": """
    **Amaç:** Yüzücünün aerobik eşiğine karşılık gelen kritik yüzme hızını (laktat eşiği tahmini) belirlemektir — yüzmede en yaygın kullanılan dayanıklılık testidir.

    **Ekipman:** Standart 25m veya 50m yüzme havuzu, kronometre.

    **Uygulama:**
    1. Sporcu tam dinlenmiş olarak 2 maksimal mesafe yüzer: **400m** ve **200m** (aralarında tam toparlanma; dinlenme süresi kaynaklarda farklıdır — "en az 30 dk" değeri doğrulanamadı).
    2. Her ikisi de kendi stilinde (genellikle serbest stil) maksimal tempoyla yüzülür.
    3. Her iki mesafenin süresi kaydedilir.

    **Skorlama:**
    - CSS (m/sn) = (400 − 200) / (T400 − T200)
      *(T400 = 400m süresi (sn), T200 = 200m süresi (sn))*
    - CSS, aerobik antrenman yoğunluğunun belirlenmesinde kullanılır.

    **Not:** İki mesafeli formül, mesafe–süre doğrusunun eğimidir (Wakayoshi ve ark., 1992'nin kritik hız yaklaşımı). "r > 0.90" ve geçerlik ifadeleri bu pakette kaynakla yeniden doğrulanmadı.
                    """,
                    "kaynak": "Wakayoshi, K., Yoshida, T., Udo, M., Kasai, T., Moritani, T., Mutoh, Y., & Miyashita, M. (1992). A simple method for determining critical speed as swimming fatigue threshold in competitive swimming. International Journal of Sports Medicine, 13(5), 367-371.\nPritchard, H. J., Phelan, L., & Hopkins, W. G. (2020). Validity and reliability of the critical swimming speed test. Journal of Science and Medicine in Sport, 23(11), 1067-1071.",
                    "degiskenler": ["200m Süresi (sn)", "400m Süresi (sn)"]
                },
                "T-30 Yüzme Testi": {
                    "protokol": """
    **Amaç:** 30 dakikada kat edilen maksimal mesafeyle aerobik kapasiteyi değerlendirmektir — yüzmedeki Cooper testi eşdeğeri.

    **Ekipman:** 25m veya 50m havuz, kronometre, tur sayacı.

    **Uygulama:**
    1. Sporcu 30 dakika boyunca maksimal tempo ve sürdürülebilir hızda yüzer.
    2. Her tur kaydedilir.
    3. Yüzme stili sabit tutulur (genellikle serbest).

    **Skorlama:** 30 dakikada tamamlanan toplam mesafe (m). T-30 hızı = mesafe (m) / 1800 sn (Olbrecht ve ark., 1985; Deminice ve ark., 2007 aktarımıyla); anaerobik eşik hızıyla yüksek ilişkilidir.

    **Not:** Önceki sürümdeki ">2000m = Mükemmel" eşiği kaynakla doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "Olbrecht, J., Madsen, Ø., Mader, A., Liesen, H., & Hollmann, W. (1985). Relationship between swimming velocity and lactic acid concentration during continuous and intermittent training exercises. International Journal of Sports Medicine, 6(2), 74-77.\nDeminice, R., Papoti, M., Zagatto, A. M., & Prado Júnior, M. V. (2007). Validity of 30 minutes test (T-30) in aerobic capacity, stroke parameters and aerobic performance determination of trained swimmers. Revista Brasileira de Medicina do Esporte, 13(3), 195-199.\nToubekis, A. G., Tsami, A. P., & Tokmakidis, S. P. (2006). Critical velocity and lactate threshold in young swimmers. International Journal of Sports Medicine, 27(2), 117-123.",
                    "degiskenler": ["Toplam Mesafe (m)"]
                },
                "Kuru Kara Testleri (Dry-Land) — Yüzme": {
                    "protokol": """
    **Amaç:** Yüzücülerin kara üzerindeki kuvvet ve güç özelliklerini değerlendirmektir; su içi performansla ilişkisi güçlüdür.

    **Ekipman:** Pull-up barı, medisin topu (3 kg), kronometre, dinamometre.

    **Uygulama — 3 bileşen:**
    1. **Maksimal Pull-Up (pronated):** Tam ekstansiyondan çeneye kadar maksimum tekrar sayısı.
    2. **Medisin Topu Fırlatma (Overhead Throw):** 3 kg medisin topunu oturarak iki eliyle başın üzerinden maksimum mesafeye fırlatma; 3 deneme, en iyi.
    3. **Dikey Sıçrama (CMJ):** Eller kalçada, maksimal sıçrama; 3 deneme, en iyi.

    **Skorlama:**
    - Pull-up tekrar sayısı
    - Medisin topu fırlatma mesafesi (m)
    - CMJ yüksekliği (cm)

    **Not:** Kara testleri, özellikle start ve dönüş performansıyla anlamlı korelasyon göstermektedir.
                    """,
                    "kaynak": "Morais, J. E., Silva, A. J., Marinho, D. A., Seifert, L., & Barbosa, T. M. (2019). Cluster analysis of the kinematics of young swimmers' technique during the front-crawl. International Journal of Performance Analysis in Sport, 19(2), 229-246.\nLoturco, I. et al. (2016). Strength and power qualities are highly associated with swimming performance in elite competitive swimmers with physical disability. Journal of Strength and Conditioning Research, 30(7), 2007-2014.",
                    "degiskenler": ["Pull-Up (tekrar)", "Medisin Topu Fırlatma (m)", "CMJ En İyi (cm)"]
                }
            },

            "Atletizm": {
                "10m Sprint": {
                    "protokol": """
**Amaç:** Patlayıcı hızlanma kapasitesini ölçmek — atletizm, futbol ve tüm hız sporlarında kullanılır.

**Ekipman:** Fotosel sistemi veya kronometre, düz pist.

**Uygulama:**
1. Durarak başlangıç (ayakta veya blok).
2. 10 metre boyunca maksimal hızla koş.
3. 3 deneme; en iyi süre kaydedilir.
4. Deneme arası tam toparlanma (3-5 dk).

**Skorlama:** En iyi 10m süresi (sn)
                    """,
                    "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.\nSeitz, L. B. et al. (2014). Journal of Strength and Conditioning Research, 28(2), 401-409.",
                    "degiskenler": ["10m Sprint (sn)"]
                },
                "20m Sprint": {
                    "protokol": """
**Amaç:** Hızlanma + geçiş fazını ölçmek.

**Ekipman:** Fotosel sistemi veya kronometre, düz pist.

**Uygulama:**
1. Durarak başlangıç.
2. 20 metre boyunca maksimal hızla koş.
3. 3 deneme; en iyi süre kaydedilir.

**Skorlama:** En iyi 20m süresi (sn)
                    """,
                    "kaynak": "Haugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
                    "degiskenler": ["20m Sprint (sn)"]
                },
                "100m Sprint": {
                    "protokol": """
**Amaç:** Maksimal sprint kapasitesini ölçmek — atletizm standardı.

**Ekipman:** Fotosel sistemi veya kronometre, atletizm pisti.

**Uygulama:**
1. Blok veya ayakta başlangıç.
2. 100m boyunca maksimal hızla koş.
3. 2-3 deneme; en iyi süre kaydedilir.
4. Deneme arası tam toparlanma (8-10 dk).

**Skorlama:** En iyi 100m süresi (sn)
                    """,
                    "kaynak": "World Athletics (2023). Performance Standards.\nHaugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
                    "degiskenler": ["100m Sprint (sn)"]
                },
                "200m Sprint": {
                    "protokol": """
**Amaç:** Maksimal hız dayanıklılığını ölçmek.

**Ekipman:** Fotosel sistemi veya kronometre, atletizm pisti.

**Uygulama:**
1. Blok veya ayakta başlangıç, virajlı pistte.
2. 200m boyunca maksimal hızla koş.
3. 2 deneme; en iyi süre kaydedilir.
4. Deneme arası tam toparlanma (10-15 dk).

**Skorlama:** En iyi 200m süresi (sn)
                    """,
                    "kaynak": "World Athletics (2023). Performance Standards.\nHaugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
                    "degiskenler": ["200m Sprint (sn)"]
                },
                "Sprint Hızlanma Profili (10-20-30m)": {
                    "protokol": """
    **Amaç:** Sprintçilerin hızlanma fazını, maksimal hıza geçiş noktasını ve maksimal hızını ayrı ayrı değerlendirmektir.

    **Ekipman:** Fotosel sistemi (10m, 20m ve 30m noktalarında), düz pist.

    **Uygulama:**
    1. Sporcu durarak başlangıç yapar (blok veya ayakta).
    2. 30 metre boyunca maksimal hızla koşar.
    3. Fotosel sistemi 10m, 20m ve 30m bölüm sürelerini ayrı ayrı kaydeder.
    4. 3 deneme yapılır; her bölüm için en iyi değer alınır.

    **Skorlama:**
    - 0–10m süresi (sn) — hızlanma fazı
    - 10–20m süresi (sn) — geçiş fazı
    - 20–30m süresi (sn) — maksimal hız fazı
    - Maksimal hız (km/h) = 10 / en iyi 10m bölüm süresi × 3.6

    **Not:** Bölüm analizi, antrenman müdahaleleri için spesifik güçlü/zayıf yönlerin belirlenmesine imkân tanır.
                    """,
                    "kaynak": "Mackala, K., & Mero, A. (2013). A kinematic analysis of three best 100m performances ever. Journal of Human Kinetics, 36, 149-160.\nHayes, P. R., & Quinn, M. D. (2009). A mathematical model for quantifying training. European Journal of Applied Physiology, 107(4), 517-522.",
                    "degiskenler": ["0-10m (sn)", "10-20m (sn)", "20-30m (sn)"]
                },
                "Atletik Güç Testi Bataryası": {
                    "protokol": """
    **Amaç:** Atlet ve sprinterlerin patlayıcı güç profilini çok yönlü değerlendirmektir.

    **Ekipman:** Sıçrama platformu veya Vertec, mezura, medisin topu (4 kg erkek / 3 kg kadın).

    **Uygulama — 4 bileşen:**
    1. **CMJ (Countermovement Jump):** Eller kalçada, 3 deneme, en iyi (cm).
    2. **SJ (Squat Jump):** 90° statik başlangıç, 3 deneme, en iyi (cm).
    3. **Durarak Üçlü Atlama:** Tek ayak → tek ayak → çift ayak; 3 deneme, en iyi (m).
    4. **Medisin Topu Atışı (Overhead Backward):** Sırtı hedefe dönük, iki elle başın üzerinden geri atış; 3 deneme, en iyi (m).

    **Skorlama:** Her bileşen için en iyi değer.
                    """,
                    "kaynak": "Sleivert, G., & Taingahue, M. (2004). The relationship between maximal jump-squat power and sprint acceleration in athletes. European Journal of Applied Physiology, 91(1), 46-52.\nMeylan, C. M., Cronin, J. B., Oliver, J. L., Hopkins, W. G., & Contreras, B. (2014). The effect of maturation on adaptations to strength training and detraining in 11–15-year-olds. Scandinavian Journal of Medicine & Science in Sports, 24(3), e156-e164.",
                    "degiskenler": ["CMJ En İyi (cm)", "SJ En İyi (cm)", "Üçlü Atlama (m)", "Medisin Topu Atışı (m)"]
                },
                "400m Sprint": {
                    "protokol": """
**Amaç:** Maksimal hız dayanıklılığını ölçmek — en zorlu sprint mesafesi.

**Ekipman:** Kronometre veya fotosel, atletizm pisti (400m).

**Uygulama:**
1. Blok veya ayakta başlangıç.
2. 400m boyunca maksimal hızla koş.
3. 2 deneme; en iyi süre kaydedilir.
4. Deneme arası tam toparlanma (15-20 dk).

**Skorlama:** En iyi 400m süresi (sn)

**Dünya Rekoru:** 43.03 sn — Wayde van Niekerk (RSA), Rio 2016
                    """,
                    "kaynak": "World Athletics (2023). Performance Standards.\nHaugen, T. et al. (2019). IJSPP, 14(9), 1153-1160.",
                    "degiskenler": ["400m Sprint (sn)"]
                },
                "30-15 İntermittent Fitness Test (30-15 IFT)": {
                    "protokol": """
    **Amaç:** Orta ve uzun mesafe koşucuların aerobik kapasitesini (VIFT) saha koşullarında değerlendirmektir — VO2max ile yüksek korelasyon gösterir.

    **Ekipman:** 40m düz alan (3m'lik güvenlik bölgeleriyle işaretli), ses sistemi (30-15 IFT ses kaydı), kronometre.

    **Uygulama:**
    1. Sporcu 40m'yi ses sinyalleriyle belirlenen hızda koşar.
    2. Her 30 saniyelik koşunun ardından 15 saniyelik yürüyüş dinlenmesi yapılır.
    3. Koşu hızı her aşamada 0.5 km/h artar (başlangıç 8 km/h).
    4. Sporcu 2 kez üst üste sinyale yetişemediğinde test sona erer.

    **Skorlama:**
    - VIFT (son tamamlanan aşamanın hızı, km/h)
    - VO2max tahmini: VO2max = 28.156 + (2.996 × VIFT)

    **Not:** 30-15 IFT, aralıklı performans gerektiren sporlarda (orta mesafe, futbol, rugby) giderek artan kullanımıyla öne çıkmaktadır.
                    """,
                    "kaynak": "Buchheit, M. (2008). The 30-15 intermittent fitness test: accuracy for individualizing interval training of young intermittent sport players. Journal of Strength and Conditioning Research, 22(2), 365-374.\nBuchheit, M. (2010). The 30-15 intermittent fitness test: 10 year review. Myorobie Journal, 1(9), 278.",
                    "degiskenler": ["Son Hız - VIFT (km/h)"]
                }
            },

            "Tenis": {
                "Spider Test (Tenis Çeviklik Testi)": {
                    "protokol": """
    **Amaç:** Tenis oyuncularının sahaya özgü çevikliğini, hızını ve yön değiştirme kapasitesini değerlendirmektir — literatürde en çok kullanılan tenis spesifik çeviklik testidir.

    **Ekipman:** Tenis kortu, 5 tenis topu, arka çizginin hemen gerisinde ortada işaretli başlangıç karesi, kronometre.

    **Uygulama:**
    1. Sporcu arka çizginin hemen gerisinde, ortadaki başlangıç karesinde başlar.
    2. İşaretle 5 topu sağdan başlayarak sırayla toplar; her seferinde tek top taşır ve topu başlangıç karesine bırakır.
    3. Süre son top kareye konduğunda durur.
    4. 2 deneme yapılır (aralarında 3 dk); en iyi süre kaydedilir.

    **Skorlama:** En iyi tamamlama süresi (sn) — az = iyi.

    **Not:** Başlangıç karesi, tek top taşıma, sağdan başlama ve 2 deneme kaynakla doğrulandı. Topların yeri yaygın tarife göredir (arka çizgi–tekler yan çizgisi köşeleri, servis çizgisi–yan çizgi kesişimleri, file ortası); özgün şekil metinden doğrulanamadı. "<15.5 sn = Mükemmel" eşiği doğrulanamadı.
                    """,
                    "kaynak": "Roetert, E. P., & Ellenbecker, T. S. (2007). Complete conditioning for tennis (2nd ed.). Human Kinetics.\nFernandez-Fernandez, J., Sanz-Rivas, D., & Mendez-Villanueva, A. (2009). A review of the activity profile and physiological demands of tennis match play. Strength and Conditioning Journal, 31(4), 15-26.\nEfDeportes, 206 (2015): Test de la araña y la raqueta (protokol aktarımı: başlangıç karesi, tek top, sağdan, 2 deneme).",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
                },
                "Tenis Servis Hızı ve İsabeti": {
                    "protokol": """
    **Amaç:** Servis hızını ve isabet oranını değerlendirmektir — tenis performansının en kritik teknik-fiziksel bileşenidir.

    **Ekipman:** Radar tabancası veya Hawk-Eye sistemi, standart tenis topu, tenis kortu.

    **Uygulama:**
    1. Sporcu standart servis pozisyonunda (arka çizgi arkasında) durur.
    2. 10 birinci servis atılır; radar hızı ve isabet kaydedilir.
    3. 10 ikinci servis atılır; hız ve isabet kaydedilir.

    **Skorlama:**
    - Birinci servis ortalama hızı (km/h)
    - Birinci servis isabet oranı (%)
    - İkinci servis ortalama hızı (km/h)
    - İkinci servis isabet oranı (%)

    **Not:** 10 + 10 servisten oluşan bu düzen standart bir test protokolü olarak kaynakla doğrulanamadı; gösterilen kaynaklar (Kovacs 2007; Reid ve ark. 2013 — forehand üzerine) bu düzeni tanımlamaz. ">200 km/h = Mükemmel" eşiği doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "Kovacs, M. S. (2007). Tennis physiology: training the competitive athlete. Sports Medicine, 37(3), 189-198.\nReid, M., Elliott, B., & Crespo, M. (2013). Mechanics and learning practices associated with the tennis forehand: a review. Journal of Sports Science and Medicine, 12(2), 225-231.",
                    "degiskenler": ["1. Servis Ort. Hız (km/h)", "1. Servis İsabet (%)", "2. Servis Ort. Hız (km/h)", "2. Servis İsabet (%)"]
                },
                "Yo-Yo IR1 (Tenis)": {
                    "protokol": """
    **Amaç:** Tenis oyuncularının aralıklı aerobik dayanıklılığını değerlendirmektir.

    **Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme, artan hız).

    **Tenis Farkı:** Sonuçlar tenis norm tablolarıyla değerlendirilir; tenis maçının aralıklı yapısıyla paralel fizyolojik talep oluşturur.

    **Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4

    **Normatif (Elit Erkek):** >1600m = İyi
                    """,
                    "kaynak": "Fernandez-Fernandez, J. et al. (2009). A review of the activity profile and physiological demands of tennis match play. Strength and Conditioning Journal, 31(4), 15-26.\nKovacs, M. S. (2007). Tennis physiology. Sports Medicine, 37(3), 189-198.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                },
                "T-Testi (Çeviklik)": {
                    "protokol": """
    **Amaç:** Lateral (yanlara) hareket yeteneğini ve çevikliği değerlendirmektir.

    **Ekipman:** 4 koni (T şeklinde), kronometre.

    **Uygulama:**
    1. A konisinden başlanır; 9,14 m (10 yd) ilerideki B konisine koşulur (sağ elle dokunulur).
    2. B'den 4,57 m (5 yd) soldaki C'ye yana kayma (sol elle dokunulur).
    3. C'den 9,14 m sağdaki D'ye yana kayma (sağ elle dokunulur).
    4. D'den B'ye yana kayma (sol elle dokunulur), B'den A'ya geri geri koşu.
    5. Yana kaymada ayaklar çaprazlanmaz; 3 deneme, en iyi süre (0,1 sn).

    **Skorlama:** En iyi süre (sn).

    **Not:** Sıra Semenick (1990) / Pauole ve ark. (2000) standart T-testidir; önceki sürümdeki D→C→B sırası düzeltildi. "<9.5 sn = Mükemmel" eşiği doğrulanamadı.
                    """,
                    "kaynak": "Pauole, K., Madole, K., Garhammer, J., Lacourse, M., & Rozenek, R. (2000). Reliability and validity of the T-test as a measure of agility, leg power, and leg speed in college-aged men and women. Journal of Strength and Conditioning Research, 14(4), 443-450.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                }
            },
            "Muay Thai": {
                "Muay Thai Spesifik Dayanıklılık Testi (MTSDT)": {
                    "protokol": """
**Amaç:** Muay Thai sporcularının müsabakaya özgü anaerobik-aerobik kapasitesini değerlendirmektir.

**Ekipman:** Kum torbası veya pao (pad), eldiven, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 5 × 3 dakikalık tur yapar (profesyonel Muay Thai formatı).
2. Turlar arası 2 dk pasif dinlenme.
3. Her turda: jab-cross-hook, teep, roundhouse kick, knee kombinasyonları.
4. Her tur sonunda HR ve toplam teknik sayısı kaydedilir.

**Skorlama:**
- Her turdaki toplam teknik sayısı
- Yorgunluk indeksi (%) = (Tur1 − Tur5) / Tur1 × 100
- HR profili (bpm)

**Normatif (Elit Erkek):** Yorgunluk indeksi < %20 = İyi
                    """,
                    "kaynak": "Crisafulli, A., Vitelli, S., Cappai, I., Milia, R., Tocco, F., Melis, F., & Concu, A. (2009). Physiological responses and energy cost during a simulation of a Muay Thai boxing match. Applied Physiology, Nutrition, and Metabolism, 34(2), 143-150.",
                    "degiskenler": ["Tur 1 Teknik", "Tur 2 Teknik", "Tur 3 Teknik", "Tur 4 Teknik", "Tur 5 Teknik", "HR Tur 1 (bpm)", "HR Tur 5 (bpm)"]
                },
                "Wingate (Muay Thai)": {
                    "protokol": """
**Uygulama:** Standart Wingate 30sn Bisiklet Testi protokolü uygulanır (%7.5 vücut ağırlığı direnç).

**Muay Thai Farkı:** Sonuçlar Muay Thai normatif değerleriyle değerlendirilir.

**Skorlama:** Pik Güç (W), Ortalama Güç (W), Yorgunluk İndeksi (%)
                    """,
                    "kaynak": "Crisafulli, A. et al. (2009). Applied Physiology, Nutrition, and Metabolism, 34(2), 143-150.",
                    "degiskenler": ["Pik Güç (W)", "Ortalama Güç (W)", "Min Güç (W)"]
                },
                "Yo-Yo IR1 (Muay Thai)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme).

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Crisafulli, A. et al. (2009). Applied Physiology, Nutrition, and Metabolism, 34(2), 143-150.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "BJJ (Jiujitsu)": {
                "BJJ Spesifik Dayanıklılık Testi (BJJSFT)": {
                    "protokol": """
**Amaç:** Brezilya jiujitsu sporcularının müsabakaya özgü aerobik-anaerobik kapasitesini değerlendirmektir.

**Ekipman:** BJJ matı, gi veya no-gi kıyafet, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 3 × 5 dakikalık simüle maç yapar.
2. Turlar arası 1 dk pasif dinlenme.
3. Her turda teknik/geçiş sayısı kaydedilir; partner her turda değişir.
4. Her tur sonunda HR ölçülür.

**Skorlama:**
- Her turdaki tekrar/geçiş sayısı
- Yorgunluk indeksi (%)
- HR profili (bpm)
                    """,
                    "kaynak": "Andreato, L. V., Franchini, E., de Moraes, S. M. F., Pastório, J. J., da Silva, D. F., Esteves, J. V. D. C., & Gomes, T. L. M. (2013). Physiological and technical-tactical analysis in Brazilian jiu-jitsu competition. Asian Journal of Sports Medicine, 4(2), 137-143.",
                    "degiskenler": ["Tur 1 Teknik", "Tur 2 Teknik", "Tur 3 Teknik", "HR Tur 1 (bpm)", "HR Tur 2 (bpm)", "HR Tur 3 (bpm)"]
                },
                "BJJ Kavrama Kuvveti ve Dayanıklılığı": {
                    "protokol": """
**Amaç:** BJJ'de kritik olan el ve ön kol kavrama kuvvetini ve dayanıklılığını değerlendirmektir.

**Ekipman:** El dinamometresi, gi yaka veya kavrama aparatı, kronometre.

**Uygulama:**
1. **MVC:** Her el için 3 deneme; en iyi değer (kg).
2. **Kavrama Dayanıklılığı:** %60 MVC'de 60 sn tutma.
3. **Gi Kavrama:** Gi yakasına iki elle asılı kalma süresi (sn).

**Skorlama:**
- MVC sağ/sol (kg)
- Kavrama dayanıklılık süresi (sn)
- Gi asılma süresi (sn)
                    """,
                    "kaynak": "Andreato, L. V. et al. (2013). Asian Journal of Sports Medicine, 4(2), 137-143.\nDell'Isola, A. M. B. et al. (2016). Journal of Strength and Conditioning Research, 30(6), 1766-1772.",
                    "degiskenler": ["MVC Sağ El (kg)", "MVC Sol El (kg)", "Kavrama Dayanıklılık (sn)", "Gi Asılma Süresi (sn)"]
                },
                "Yo-Yo IR1 (BJJ)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Andreato, L. V. et al. (2013). Asian Journal of Sports Medicine, 4(2), 137-143.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Sambo": {
                "Sambo Spesifik Fitness Testi (SSFT)": {
                    "protokol": """
**Amaç:** Sambo sporcularının müsabakaya özgü kuvvet dayanıklılığını ve anaerobik kapasitesini değerlendirmektir.

**Ekipman:** Sambo matı, kurtka, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 3 × 3 dakikalık simüle maç yapar (resmi sambo süreleri).
2. Turlar arası 1 dk pasif dinlenme.
3. Her turda atış ve kilit (submission) tekniği sayısı kaydedilir.
4. HR her tur sonunda ölçülür.

**Not:** Sambo güreş ve judo tekniklerini içerir; SWFT ve SJFT protokollerinin hibrit uygulaması da geçerlidir.

**Skorlama:**
- Her turdaki teknik sayısı
- Yorgunluk indeksi (%)
- HR profili (bpm)
                    """,
                    "kaynak": "Franchini, E., Del Vecchio, F. B., Matsushigue, K. A., & Artioli, G. G. (2011). Physiological profiles of elite judo athletes. Sports Medicine, 41(2), 147-166.\nGarkavy, G. A. (2007). Physical preparation of sambo wrestlers. Theory and Practice of Physical Culture, 9, 45-48.",
                    "degiskenler": ["Tur 1 Teknik", "Tur 2 Teknik", "Tur 3 Teknik", "HR Tur 1 (bpm)", "HR Tur 3 (bpm)"]
                },
                "El Kavrama ve Kurtka Kavrama (Sambo)": {
                    "protokol": """
**Amaç:** Sambo'da belirleyici olan kurtka kavrama kuvvetini değerlendirmektir.

**Ekipman:** El dinamometresi, sambo kurtkası, kronometre.

**Uygulama:**
1. MVC her el için 3 deneme (kg).
2. Tek el kurtka yakasına asılı kalma süresi (sn).
3. Çift el kurtka yakasından asılı kalma süresi (sn).

**Skorlama:** MVC sağ/sol (kg), tek el asılma (sn), çift el asılma (sn).
                    """,
                    "kaynak": "Franchini, E. et al. (2011). Sports Medicine, 41(2), 147-166.\nGarkavy, G. A. (2007). Theory and Practice of Physical Culture, 9, 45-48.",
                    "degiskenler": ["MVC Sağ El (kg)", "MVC Sol El (kg)", "Tek El Asılma (sn)", "Çift El Asılma (sn)"]
                }
            },
            "MMA": {
                "MMA Spesifik Kondisyon Testi (MMA-SCT)": {
                    "protokol": """
**Amaç:** MMA sporcularının müsabakaya özgü çok yönlü kapasitesini değerlendirmektir.

**Ekipman:** MMA matı veya kafes, eldiven, kronometre, KAH monitörü, partner.

**Uygulama:**
1. Sporcu 3 × 5 dakikalık simüle maç yapar (UFC/Bellator formatı).
2. Turlar arası 1 dk pasif dinlenme.
3. Her turda vuruş, takedown ve yerden kontrol teknik sayısı kaydedilir.
4. HR her tur sonunda ölçülür.

**Skorlama:**
- Toplam teknik sayısı (tur bazında)
- Yorgunluk indeksi (%)
- HR profili (bpm)
                    """,
                    "kaynak": "Kirk, C., Clark, D. R., Langan-Evans, C., & Morton, J. P. (2020). The physical demands of mixed martial arts: a systematic review using perceived exertion scores. Physiology & Behavior, 225, 113-125.",
                    "degiskenler": ["Tur 1 Teknik", "Tur 2 Teknik", "Tur 3 Teknik", "HR Tur 1 (bpm)", "HR Tur 3 (bpm)", "RPE (6-20)"]
                },
                "MMA Fiziksel Uygunluk Bataryası": {
                    "protokol": """
**Amaç:** MMA sporcularının çok yönlü fiziksel profilini değerlendirmektir.

**Ekipman:** Pull-up barı, kronometre, fotosel.

**Uygulama — 5 bileşen:**
1. Pull-Up (maks. tekrar)
2. 30m Sprint (3 deneme, en iyi)
3. CMJ (3 deneme, en iyi, cm)
4. Illinois Çeviklik (3 deneme, en iyi, sn)
5. Yo-Yo IR1 (tamamlanan mesafe, m)
                    """,
                    "kaynak": "Kirk, C. et al. (2020). Physiology & Behavior, 225, 113-125.\nBuse, G. J. (2006). British Journal of Sports Medicine, 40(2), 169-172.",
                    "degiskenler": ["Pull-Up (tekrar)", "30m Sprint (sn)", "CMJ En İyi (cm)", "Illinois Çeviklik (sn)", "Yo-Yo IR1 (m)"]
                },
                "Wingate (MMA)": {
                    "protokol": """
**Uygulama:** Standart Wingate 30sn protokolü uygulanır (%7.5 vücut ağırlığı direnç).

**Skorlama:** Pik Güç (W), Ortalama Güç (W), Yorgunluk İndeksi (%)
                    """,
                    "kaynak": "Kirk, C. et al. (2020). Physiology & Behavior, 225, 113-125.",
                    "degiskenler": ["Pik Güç (W)", "Ortalama Güç (W)", "Min Güç (W)"]
                }
            },
            "Jimnastik": {
                "Jimnastik Fiziksel Uygunluk Testi (GFT)": {
                    "protokol": """
**Amaç:** Jimnastikçilerin kuvvet, güç ve esneklik profilini değerlendirmektir — FIG referanslı.

**Ekipman:** Pull-up barı, paralel bar, mat, esneklik ölçer.

**Uygulama — 5 bileşen:**
1. Pull-Up (pronated, maks. tekrar)
2. Paralel Bar Şınav — Dips (maks. tekrar)
3. L-Sit Hold — askıda L pozisyonu (sn)
4. Otur-Uzan (cm)
5. CMJ (3 deneme, en iyi, cm)

**Normatif (Elit Erkek):** Pull-Up > 20 = Mükemmel; L-Sit > 15 sn = Mükemmel
                    """,
                    "kaynak": "Arkaev, L. I., & Suchilin, N. G. (2004). Gymnastics: How to Create Champions. Meyer & Meyer Sport.\nSlater, L. V. et al. (2019). Journal of Strength and Conditioning Research, 33(11), 3064-3073.",
                    "degiskenler": ["Pull-Up (tekrar)", "Dips (tekrar)", "L-Sit (sn)", "Otur-Uzan (cm)", "CMJ En İyi (cm)"]
                },
                "Jimnastik Esneklik Profili": {
                    "protokol": """
**Amaç:** Jimnastikçilerin eklem hareket açıklığını (ROM) çok yönlü değerlendirmektir.

**Ekipman:** Gonyometre veya dijital açı ölçer, mat.

**Uygulama:**
1. Omuz Fleksiyon ROM (°)
2. Kalça Fleksiyon — aktif tek bacak kaldırma (°)
3. Split — zemine uzaklık (cm; 0 = tam split)
4. Bridge — yerden omuz yüksekliği (cm)

**Not:** Dört ölçümün yöntemi (açı ölçer konumu, split'te ölçülen nokta) gösterilen kaynaklarda tanımlı değildir; FIG Puanlama Kuralları bir test protokolü değildir. Görsel yalnız split ölçümünü (kasık–zemin) gösterir; yöntem doğrulanamadı.
                    """,
                    "kaynak": "Arkaev, L. I., & Suchilin, N. G. (2004). Gymnastics: How to Create Champions. Meyer & Meyer Sport.\nFIG (2022). Code of Points. International Gymnastics Federation.",
                    "degiskenler": ["Omuz Fleksiyon (°)", "Kalça Fleksiyon (°)", "Split Uzaklık (cm)", "Köprü Yüksekliği (cm)"]
                }
            },
            "Badminton": {
                "Badminton Spesifik Çeviklik Testi (BAT)": {
                    "protokol": """
**Amaç:** Badmintoncuların sahaya özgü çevikliğini ve hızını değerlendirmektir.

**Ekipman:** Standart badminton kortu (13.4 × 6.1m), kronometre.

**Uygulama:**
1. Sporcu kortun T noktasından başlar.
2. Sırasıyla 6 köşe noktasına koşup raket ile işarete dokunur.
3. Her dönüşte split-step yapılır.
4. 2 deneme; en iyi süre kaydedilir.

**Not:** Bu protokol kaynakla doğrulanamadı: gösterilen kaynak (Abian-Vicen ve ark., 2012) bir dehidrasyon çalışmasıdır ve çeviklik testi tanımlamaz; "6 köşe" sırası belirsizdir (kortta 4 köşe vardır). Doğrulanmış benzer test: Badcamp (International Journal of Sports Physiology and Performance, 2016, 11(3), 305-310) — 5,6 × 4,2 m alan, merkezden köşeler ve uzun kenar ortalarındaki 6 hedefe, sıra ışıklı uyaranla. "< 30 sn = Mükemmel" eşiği doğrulanamadı. Protokol doğrulanana kadar görsel konmaz.
                    """,
                    "kaynak": "Abian-Vicen, J., Del Coso, J., González-Millán, C., Salinero, J. J., & Abian, P. (2012). Analysis of dehydration and strength in elite badminton players. PLoS One, 7(5), e37821.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
                },
                "Yo-Yo IR1 (Badminton)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır.

**Normatif (Elit Erkek Badminton):** > 1800m = İyi

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Abian-Vicen, J. et al. (2012). PLoS One, 7(5), e37821.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                },
                "CMJ (Badminton)": {
                    "protokol": """
**Uygulama:** Standart CMJ protokolü (eller kalçada, 3 deneme, en iyi değer).

**Badminton Farkı:** Smaç, fileye çıkma ve savunma hareketleriyle doğrudan ilişkilidir.

**Normatif (Elit Erkek):** > 45 cm = İyi
                    """,
                    "kaynak": "Abian-Vicen, J. et al. (2012). PLoS One, 7(5), e37821.",
                    "degiskenler": ["CMJ En İyi (cm)"]
                }
            },
            "Masa Tenisi": {
                "Masa Tenisi Reaksiyon ve Çeviklik Testi": {
                    "protokol": """
**Amaç:** Masa tenisçilerinin reaksiyon süresi ve çevikliğini değerlendirmektir.

**Ekipman:** Işıklı reaksiyon sistemi veya kronometre, masa tenisi masası.

**Uygulama:**
1. Reaksiyon Süresi: Görsel uyarana tepki; 20 deneme ortalaması (ms).
2. Yan Adım Çeviklik: 3m sağ-sol; 15 sn boyunca maks. tekrar.
3. Masa Başı Vuruş: 30 sn içinde maks. vuruş sayısı.

**Normatif (Elit Erkek):** Reaksiyon < 180 ms = Mükemmel
                    """,
                    "kaynak": "Placek, J. et al. (2020). Fitness characteristics of elite table tennis players. Journal of Human Kinetics, 72, 175-184.",
                    "degiskenler": ["Reaksiyon Süresi (ms)", "Yan Adım (tekrar/15sn)", "Masa Başı Vuruş (tekrar/30sn)"]
                },
                "Yo-Yo IR1 (Masa Tenisi)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Zagatto, A. M. et al. (2010). Journal of Sports Sciences, 28(1), 71-79.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Squash": {
                "Ghost Drill (Squash Çeviklik Testi)": {
                    "protokol": """
**Amaç:** Squash oyuncularının sahaya özgü çevikliğini ve dayanıklılığını değerlendirmektir.

**Ekipman:** Standart squash kortu, raket (opsiyonel), kronometre.

**Uygulama:**
1. Sporcu T noktasından başlar; 6 köşeyi belirli sırayla koşar.
2. Her noktada raket ile duvara vurur ve T'ye döner.
3. 30 sn × 6 set; setler arası 30 sn dinlenme.
4. Her set tamamlanan tur sayısı kaydedilir.

**Normatif (Elit Erkek):** Set başına > 5 tur = Mükemmel
                    """,
                    "kaynak": "Wilkinson, M., Leedale-Brown, D., & Winter, E. M. (2009). Validity of a squash-specific fitness test. International Journal of Sports Physiology and Performance, 4(1), 29-40.",
                    "degiskenler": ["Set 1 (tur)", "Set 2 (tur)", "Set 3 (tur)", "Set 4 (tur)", "Set 5 (tur)", "Set 6 (tur)"]
                },
                "Squash Artımlı Mekik Testi (SIST)": {
                    "protokol": """
**Amaç:** Squash oyuncularının aerobik kapasitesini sahaya özgü hareketlerle değerlendirmektir.

**Ekipman:** Squash kortu, ses sistemi (SIST kayıt), kronometre.

**Uygulama:**
1. Oyuncu T noktasında başlar; her ses sinyalinde gösterilen hedefe (iki ön köşe, iki arka köşe) gider, hedefe bir ayağını basar, en yakın yan duvara doğru güçlü bir vuruşu topsuz taklit eder ve T'ye döner.
2. Kademeler 1 dakikadır: 1. kademede 14 hareket, her dakika 1 hareket eklenir.
3. Test istemli tükenmeye kadar sürer.

**Skorlama:** Son tamamlanan aşama, toplam süre (dk).

**Not:** T'den başlama, dört köşe hedefi, ayak hedefte + vuruş taklidi, 1 dk kademe (14 hareketle başlar, dakikada +1) ve istemli tükenme kaynakla doğrulandı (Wilkinson ve ark., 2009; UKSCA squash testleri derlemesi aktarımı). Köşe sırası sinyale göredir; görseldeki sıra örnektir. Laboratuvar sürümünde laktat eşiğine kadar 4 dk kademeler kullanılır (Wilkinson ve ark., 2009 özeti). Önceki "2 kez üst üste sinyale yetişemeyince biter" ölçütü doğrulanamadı.
                    """,
                    "kaynak": "Wilkinson, M., Leedale-Brown, D., & Winter, E. M. (2009). Reproducibility of physiological and performance measures from a squash-specific fitness test. International Journal of Sports Physiology and Performance, 4(1), 41-53.",
                    "degiskenler": ["Son Aşama", "Toplam Süre (dk)"]
                },
                "Yo-Yo IR1 (Squash)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır.

**Normatif (Elit Erkek Squash):** > 2000m = İyi

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Nikolaidis, P. T. et al. (2018). Journal of Human Kinetics, 61, 95-105.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Karate": {
                "Karate Spesifik Dayanıklılık Testi (KSDT)": {
                    "protokol": """
**Amaç:** Karatecilerin müsabakaya özgü anaerobik-aerobik dayanıklılığını değerlendirmektir.

**Ekipman:** Standart karate alanı (8×8m), kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 2 dakikalık maksimal yoğunlukta kumite simülasyonu yapar (standart teknik kombinasyonları: tsuki, uchi, geri).
2. Her 30 sn'de bir teknik kombinasyon değiştirilir.
3. Test sonrası HR0 (hemen), HR1 (1. dk) ve HR3 (3. dk) ölçülür.

**Skorlama:**
- Toplam teknik sayısı
- HR0 ve HR3 değerleri
- Toparlanma indeksi: (HR0 − HR3) / HR0 × 100

**Normatif (Elit Erkek):** Toparlanma indeksi > %30 = İyi
                    """,
                    "kaynak": "Chaabène, H., Hachana, Y., Franchini, E., Mkaouer, B., & Chamari, K. (2012). Physical and physiological profile of elite karate athletes. Sports Medicine, 42(10), 829-843.\nTabben, M. et al. (2015). Physiological and fitness differences between karate and judo. Journal of Sports Sciences, 33(8), 819-826.",
                    "degiskenler": ["Toplam Teknik Sayısı", "HR0 (bpm)", "HR1 (bpm)", "HR3 (bpm)"]
                },
                "Karate Çeviklik Testi (KAT)": {
                    "protokol": """
**Amaç:** Karatecilerin yön değiştirme hızını ve reaksiyon süresini değerlendirmektir.

**Ekipman:** 4 koni (T şeklinde), kronometre.

**Uygulama:**
1. Standart T-testi protokolü uygulanır (A→B→C→D→B→A; Semenick 1990 / Pauole ve ark. 2000).
2. 3 deneme; en iyi süre kaydedilir.

**Skorlama:** En iyi süre (sn).

**Normatif (Elit Erkek Karateci):** < 9.0 sn = Mükemmel
                    """,
                    "kaynak": "Chaabène, H. et al. (2012). Physical and physiological profile of elite karate athletes. Sports Medicine, 42(10), 829-843.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                },
                "Yo-Yo IR1 (Karate)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme).

**Karate Farkı:** Sonuçlar karate normatif değerleriyle değerlendirilir.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4

**Normatif (Elit Erkek Karateci):** > 1600m = İyi
                    """,
                    "kaynak": "Chaabène, H. et al. (2012). Sports Medicine, 42(10), 829-843.\nTabben, M. et al. (2015). Journal of Sports Sciences, 33(8), 819-826.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Taekwondo": {
                "Taekwondo Spesifik Aerobik Test (TSAT)": {
                    "protokol": """
**Amaç:** Taekwondocuların müsabakaya özgü dayanıklılığını değerlendirmektir.

**Ekipman:** Standart taekwondo müsabaka alanı, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 2 dakika boyunca standart teknik kombinasyonları (ap chagi, dollyo chagi, yop chagi) maksimal hızda uygular.
2. Her 20 sn'de bir kombinasyon değişir.
3. HR0 ve HR3 kaydedilir.

**Skorlama:**
- Toplam teknik sayısı
- HR0 (bpm), HR3 (bpm)
- Toparlanma indeksi (%)
                    """,
                    "kaynak": "Bridge, C. A., Santos, J. F. S., Chaabène, H., Pieter, W., & Franchini, E. (2014). Physical and physiological profiles of taekwondo athletes. Sports Medicine, 44(6), 713-733.",
                    "degiskenler": ["Toplam Teknik Sayısı", "HR0 (bpm)", "HR3 (bpm)"]
                },
                "Taekwondo Çeviklik ve Hız Testi": {
                    "protokol": """
**Amaç:** Taekwondocuların hız ve çeviklik profilini değerlendirmektir.

**Ekipman:** 20m düz alan, fotosel veya kronometre.

**Uygulama:**
1. **10m Sprint:** Durarak başlangıç, 3 deneme; en iyi süre.
2. **T-Testi:** Standart T-testi protokolü; 3 deneme, en iyi süre.

**Skorlama:**
- 10m sprint süresi (sn)
- T-testi süresi (sn)

**Normatif (Elit Erkek):** 10m < 1.70 sn = Mükemmel
                    """,
                    "kaynak": "Bridge, C. A. et al. (2014). Sports Medicine, 44(6), 713-733.\nFilimonov, V. I. et al. (1983). Means of increasing strength of the punch. NSCA Journal, 7(6), 65-66.",
                    "degiskenler": ["10m Sprint (sn)", "T-Testi (sn)"]
                },
                "Yo-Yo IR1 (Taekwondo)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme).

**Taekwondo Farkı:** Sonuçlar taekwondo normatif değerleriyle değerlendirilir.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4

**Normatif (Elit Erkek):** > 1600m = İyi
                    """,
                    "kaynak": "Bridge, C. A. et al. (2014). Sports Medicine, 44(6), 713-733.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Kickboks": {
                "Kickboks Spesifik Kondisyon Testi (KSKT)": {
                    "protokol": """
**Amaç:** Kickbokscuların müsabakaya özgü anaerobik kapasitesini ve yorgunluk direncini değerlendirmektir.

**Ekipman:** Kum torbası, eldiven, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 3 × 2 dakikalık maksimal kombinasyon serisi yapar (yumruk + tekme).
2. Turlar arası 1 dk pasif dinlenme.
3. Her tur sonunda HR ölçülür.
4. Her turdaki darbe sayısı kaydedilir.

**Skorlama:**
- Her turdaki toplam darbe sayısı
- Turlar arası yorgunluk indeksi (%) = (Tur1 − Tur3) / Tur1 × 100
- HR her tur sonu (bpm)

**Normatif (Elit Erkek):** Yorgunluk indeksi < %15 = Mükemmel
                    """,
                    "kaynak": "Ouergui, I., Hammouda, O., Chtourou, H., Gmada, N., & Franchini, E. (2014). Physiological responses and time-motion analysis of kickboxing competition. Journal of Strength and Conditioning Research, 28(12), 3340-3347.",
                    "degiskenler": ["Tur 1 Darbe Sayısı", "Tur 2 Darbe Sayısı", "Tur 3 Darbe Sayısı", "HR Tur 1 (bpm)", "HR Tur 2 (bpm)", "HR Tur 3 (bpm)"]
                },
                "Wingate (Kickboks)": {
                    "protokol": """
**Uygulama:** Standart Wingate 30sn Bisiklet Testi protokolü uygulanır (%7.5 vücut ağırlığı direnç).

**Kickboks Farkı:** Sonuçlar kickboks normatif değerleriyle değerlendirilir.

**Skorlama:** Pik Güç (W), Ortalama Güç (W), Yorgunluk İndeksi (%)

**Normatif (Elit Erkek Kickboksör):** Pik Güç > 1100W = Mükemmel
                    """,
                    "kaynak": "Ouergui, I. et al. (2014). JSCR, 28(12), 3340-3347.",
                    "degiskenler": ["Pik Güç (W)", "Ortalama Güç (W)", "Min Güç (W)"]
                }
            },
            "Boks": {
                "Boks Spesifik Dayanıklılık Testi": {
                    "protokol": """
**Amaç:** Boksörlerin müsabaka koşullarına özgü aerobik-anaerobik kapasitesini değerlendirmektir.

**Ekipman:** Kum torbası veya lapa (focus mitt), eldiven, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 3 × 3 dakikalık maksimal kombinasyon serisi yapar.
2. Turlar arası 1 dk pasif dinlenme (profesyonel boks kuralları).
3. Her tur; jab, cross, hook, uppercut kombinasyonları içerir.
4. Her tur sonunda HR ve RPE kaydedilir.

**Skorlama:**
- Her turdaki toplam darbe sayısı
- Yorgunluk indeksi (%)
- HR profili (bpm)
                    """,
                    "kaynak": "Davis, P., Benson, P. R., Pitty, J. D., Connorton, A. J., & Waldock, R. (2015). The activity profile of elite male amateur boxing. International Journal of Sports Physiology and Performance, 10(1), 53-57.",
                    "degiskenler": ["Tur 1 Darbe Sayısı", "Tur 2 Darbe Sayısı", "Tur 3 Darbe Sayısı", "HR Tur 1 (bpm)", "HR Tur 3 (bpm)", "RPE (6-20)"]
                },
                "Yo-Yo IR1 (Boks)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır.

**Boks Farkı:** Sonuçlar boks normatif değerleriyle değerlendirilir.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Davis, P. et al. (2013). International Journal of Sports Physiology and Performance, 8(1), 3-12.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },
            "Halter": {
                "Koparma (Snatch) / Silkme (Clean & Jerk) 1RM": {
                    "protokol": """
**Amaç:** Haltercilerin olimpik kaldırışlarda maksimal kuvvetini ölçmektir.

**Ekipman:** Olimpik halter barı ve plakalar, antrenman platformu.

**Uygulama:**
1. Kapsamlı ısınma (10-15 dk genel + spesifik).
2. Kademeli ağırlık artışıyla 1RM deneme:
   - %60 × 5, %75 × 3, %85 × 2, %90 × 1, %95 × 1, 1RM denemesi.
3. Başarısız denemeler kaydedilir.
4. 1RM; ya doğrudan ya da en ağır başarılı kaldırıştan tahmin yoluyla belirlenir.

**Skorlama:**
- Snatch 1RM (kg)
- Clean & Jerk 1RM (kg)
- Toplam (kg)
- Vücut ağırlığına normalize: 1RM / Vücut ağırlığı

**Not:** Önceki "85 kg, Snatch > 155 kg = Uluslararası düzey" eşiği doğrulanamadı (IWF sıklet kategorileri 2018'de değişti); norm gösterilmez. Isınma basamakları (%60 × 5 … %95 × 1) gösterilen kaynakta bu biçimiyle doğrulanamadı.
                    """,
                    "kaynak": "Haff, G. G., & Triplett, N. T. (2016). Essentials of Strength Training and Conditioning (4th ed.). Human Kinetics.\nIWF Technical and Competition Rules (2022). International Weightlifting Federation.",
                    "degiskenler": ["Snatch 1RM (kg)", "Clean & Jerk 1RM (kg)", "Vücut Ağırlığı (kg)"]
                },
                "Dikey Sıçrama ve CMJ (Halter)": {
                    "protokol": """
**Uygulama:** Standart CMJ ve SJ protokolü uygulanır (eller kalçada, force plate tercih edilir).

**Halter Farkı:** Haltercilerde CMJ yüksekliği patlayıcı güç gelişiminin güvenilir göstergesidir; antrenman periyodizasyonunda izleme amaçlı kullanılır.

**Skorlama:** CMJ (cm), SJ (cm), CMJ−SJ farkı (reaktif kuvvet göstergesi)
                    """,
                    "kaynak": "Suchomel, T. J., Nimphius, S., & Stone, M. H. (2016). The importance of muscular strength in athletic performance. Sports Medicine, 46(10), 1419-1449.",
                    "degiskenler": ["CMJ En İyi (cm)", "SJ En İyi (cm)"]
                }
            },
            "Kürek": {
                "2000m Kürek Ergometre Testi": {
                    "protokol": """
**Amaç:** Kürekçilerin aerobik kapasitesini ve güç dayanıklılığını değerlendirmektir — kürek performansının altın standart testi.

**Ekipman:** Kürek ergometresi (Concept2 Model D/E tercih edilir).

**Uygulama:**
1. 10-15 dk ısınma (düşük direnç).
2. 2000m maksimal hızda kürek çekilir.
3. Tempo (vuruş/dk), güç (watt) ve süre kaydedilir.

**Skorlama:**
- 2000m tamamlama süresi (dk:sn)
- Ortalama güç (watt)
- Ortalama vuruş/dk (spm)

**Not:** Rowing Australia 2000 m protokolü (2020): Concept2 ergometre, sürtünme (drag) katsayısı kategoriye göre (ör. ağır sıklet erkek 130, hafif sıklet erkek 125, ağır sıklet kadın 110); toplam süre, ortalama 500 m temposu, ortalama güç ve ortalama vuruş sayısı monitör belleğinden kaydedilir. "Hafif sıklet < 6:30, ağır sıklet < 6:00 = Mükemmel" eşikleri doğrulanamadı; norm gösterilmez. Kaynak listesindeki Malcolm ve Mahony (2018) künyesi bulunamadı, çıkarıldı.
                    """,
                    "kaynak": "Lawton, T. W., Cronin, J. B., & McGuigan, M. R. (2011). Strength testing and training of rowers: a review. Sports Medicine, 41(5), 413-432.",
                    "degiskenler": ["Süre (dakika)", "Süre (saniye)", "Ortalama Güç (watt)", "Ortalama Tempo (spm)"]
                },
                "6 Dakika Kürek Ergometre Testi": {
                    "protokol": """
**Amaç:** Aerobik kapasiteyi ve güç dayanıklılığını değerlendirmektir — 2000m'ye tamamlayıcı test.

**Ekipman:** Kürek ergometresi (Concept2).

**Uygulama:**
1. 6 dakika boyunca maksimal mesafe kürek çekilir.
2. Direnç sabit tutulur.

**Skorlama:**
- Tamamlanan mesafe (m)
- Ortalama güç (watt)

**Not:** 6 dk testi Huerta Ojeda ve ark. (2022) ile doğrulandı: Concept2 Model D, sürtünme katsayısı 111–114, 6 dakikada en uzun mesafe; ortalama güç kaydedilir. Lawton ve ark. (2011) kuvvet testleri derlemesidir, bu testi tanımlamaz.
                    """,
                    "kaynak": "Huerta Ojeda, Á. ve ark. (2022). Six-minute rowing test: a valid and reliable method for assessing power output in amateur male rowers. PeerJ, 10, e14060.\nLawton, T. W., Cronin, J. B., & McGuigan, M. R. (2011). Strength testing and training of rowers: a review. Sports Medicine, 41(5), 413-432.",
                    "degiskenler": ["Tamamlanan Mesafe (m)", "Ortalama Güç (watt)"]
                }
            },
            "Kano/Kayak": {
                "200m Ergometre Testi (Kano/Kayak)": {
                    "protokol": """
**Amaç:** Kano ve kayak sporcularının anaerobik pik gücünü ve sprint kapasitesini değerlendirmektir — 200m yarışma mesafesine özgü test.

**Ekipman:** Kano/kayak ergometresi (Dansprint veya Kayak C2).

**Uygulama:**
1. 10 dk düşük yoğunluklu ısınma.
2. 200m mesafe maksimal hızda tamamlanır.
3. 2 deneme; aralarında en az 20 dk dinlenme.

**Skorlama:**
- Tamamlama süresi (sn)
- Ortalama güç (watt)
- Maksimal kürek frekansı (spm)

**Not:** van Someren ve Palmer (2003) 200 m su üstü derecesini laboratuvar testleriyle (değiştirilmiş Wingate, 2 dk ergometre) tahmin eder; 200 m ergometre protokolünü (2 deneme, 20 dk dinlenme) tanımlamaz — doğrulanamadı. "< 38 sn" eşiği doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "van Someren, K. A., & Palmer, G. S. (2003). Prediction of 200-m sprint kayaking performance. Canadian Journal of Applied Physiology, 28(4), 505-517.",
                    "degiskenler": ["Süre (sn)", "Ortalama Güç (watt)", "Maks. Tempo (spm)"]
                },
                "500m Ergometre Testi (Kano/Kayak)": {
                    "protokol": """
**Amaç:** Kano ve kayak sporcularının anaerobik-aerobik karışık kapasitesini değerlendirmektir — 500m yarışma mesafesine özgü test.

**Ekipman:** Kano/kayak ergometresi (Dansprint veya Kayak C2).

**Uygulama:**
1. 10 dk düşük yoğunluklu ısınma.
2. 500m mesafe maksimal hızda tamamlanır.
3. Tempo ve güç değerleri her 100m'de kaydedilir.

**Skorlama:**
- Tamamlama süresi (sn)
- Ortalama güç (watt)
- Ortalama kürek frekansı (spm)

**Not:** Fry ve Morton (1991) seçkin kanocuların fizyolojik ve kinantropometrik özelliklerini tanımlar; 500 m ergometre protokolü (her 100 m kayıt) bu pakette doğrulanamadı. "< 1:45" eşiği doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "Fry, R. W., & Morton, A. R. (1991). Physiological and kinanthropometric attributes of elite flatwater kayakists. Medicine & Science in Sports & Exercise, 23(11), 1297-1301.",
                    "degiskenler": ["Süre (sn)", "Ortalama Güç (watt)", "Ortalama Tempo (spm)"]
                },
                "1000m Ergometre Testi (Kano/Kayak)": {
                    "protokol": """
**Amaç:** Kano ve kayak sporcularının aerobik kapasitesini ve güç dayanıklılığını değerlendirmektir — 1000m yarışma mesafesine özgü test.

**Ekipman:** Kano/kayak ergometresi (Dansprint veya Kayak C2).

**Uygulama:**
1. 10-15 dk düşük yoğunluklu ısınma.
2. 1000m mesafe maksimal hızda tamamlanır.
3. Tempo ve güç değerleri her 250m'de kaydedilir.
4. Test sonrası HR ölçülür.

**Skorlama:**
- Tamamlama süresi (dk:sn)
- Ortalama güç (watt)
- Ortalama kürek frekansı (spm)
- Test sonu HR (bpm)

**Not:** 1000 m ergometre protokolü (her 250 m kayıt, test sonu KAH) gösterilen kaynaklarda bu biçimiyle doğrulanamadı. "< 3:45" eşiği doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "Fry, R. W., & Morton, A. R. (1991). Medicine & Science in Sports & Exercise, 23(11), 1297-1301.\nvan Someren, K. A., & Palmer, G. S. (2003). Canadian Journal of Applied Physiology, 28(4), 505-517.",
                    "degiskenler": ["Süre (dakika)", "Süre (saniye)", "Ortalama Güç (watt)", "Ortalama Tempo (spm)", "HR Test Sonu (bpm)"]
                }
            },
        },
        "Takım Sporları": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Futbol": {
                "Yo-Yo IR1 (Futbol)": {
                    "protokol": """
    **Amaç:** Yüksek yoğunluklu aralıklı koşu kapasitesini ölçmek.

    **Ekipman:** 20m düz alan, beep ses sistemi, kronometre.

    **Uygulama:**
    1. 20m çift yön koşu, bip sesiyle artan hız.
    2. Her turda 10 saniyelik aktif dinlenme (5m gidip gelme).
    3. 2 kez üst üste bipe yetişemeyen testi bitirir.

    **Skorlama:**
    - Tamamlanan mesafe (m)
    - VO2max = Mesafe × 0.0084 + 36.4

    **Normatif (Elit Erkek Futbolcu):** ≥2400m = İyi
                    """,
                    "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test: a useful tool for evaluation of physical performance in intermittent sports. Sports Medicine, 38(1), 37–51.",
                    "degiskenler": ["Tamamlanan Mesafe (m)", "Son Seviye"]
                },
                "Yo-Yo IR2 (Futbol)": {
                    "protokol": """
    **Amaç:** Elit futbolcularda çok yüksek yoğunluklu aralıklı performansı ölçmek.

    **Ekipman:** 20m düz alan, beep ses sistemi.

    **Uygulama:** IR1 ile aynı format; başlangıç hızı daha yüksek (13 km/h). 10 sn aktif dinlenme.

    **Skorlama:** Toplam mesafe (m); VO2max = Mesafe × 0.0136 + 45.3 *(IR2 denklemi)*

    **Normatif (Elit Erkek Futbolcu):** ≥800m = İyi
                    """,
                    "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test. Sports Medicine, 38(1), 37–51.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                },
                "RSA Testi (Repeated Sprint Ability)": {
                    "protokol": """
    **Amaç:** Futbolcularda tekrarlı sprint kapasitesini ve yorgunluk direncini değerlendirmektir.

    **Ekipman:** 30m düz alan, fotosel veya kronometre.

    **Uygulama:**
    1. 6 × 30m sprint; her sprint arasında 25 sn pasif dinlenme.
    2. Durarak başlangıç, her sprinte tam dinlenmeden geçilir.
    3. Tüm sprintler kronometreyle kaydedilir.

    **Skorlama:**
    - En iyi sprint süresi (sn)
    - Ortalama sprint süresi (sn)
    - Yorgunluk İndeksi (%) = (Toplam süre − İdeal toplam süre) / İdeal toplam süre × 100
      *(İdeal toplam süre = En iyi sprint × sprint sayısı)*

    **Normatif (Elit Erkek Futbolcu):** Yorgunluk İndeksi < %3 = Mükemmel
                    """,
                    "kaynak": "Girard, O., Mendez-Villanueva, A., & Bishop, D. (2011). Repeated-sprint ability — part I: factors contributing to fatigue. Sports Medicine, 41(8), 673–694.\nGabbet, T. J. (2010). The development of a test of repeated-sprint ability for elite women's soccer players. Journal of Strength and Conditioning Research, 24(5), 1191–1194.",
                    "degiskenler": ["Sprint 1 (sn)", "Sprint 2 (sn)", "Sprint 3 (sn)", "Sprint 4 (sn)", "Sprint 5 (sn)", "Sprint 6 (sn)"]
                },
                "İzometrik ve İzokinetik Diz Kuvveti Profili (Keytsman et al., 2024)": {
                "protokol": """
**Amaç:** Elit futbolcuların diz ekstansör (kuadriseps) ve fleksör (hamstring) kaslarının izometrik ve izokinetik kuvvet profilini ölçmek; H:K (Hamstring/Kuadriseps) oranı ve bacaklar arası asimetriyi değerlendirmektir.

**Ekipman:** İzokinetik dinamometre (Biodex System 3, Cybex veya eşdeğeri), bilgisayar ve veri kayıt yazılımı.

**Uygulama:**
1. Isınma: 10 dk bisiklet ergometresi (düşük yoğunluk) + 2×20 tekrar leg extension ve leg curl (%50-60 1RM).
2. **İzometrik Ölçüm:** Kuadriseps için 90° diz fleksiyon, hamstring için 45° diz fleksiyonda 4 saniyelik maksimal istemli kasılma (MVC). 2 tekrar, 30 sn dinlenme arası.
3. **İzokinetik Ölçüm:** 180°/sn açısal hızda 5 maksimal konsantrik diz ekstansiyonu ve fleksiyonu. İlk 3 submaksimal ısınma tekrarı yapılır. En yüksek 3 tekrarın ortalaması alınır.
4. Her iki bacak ölçülür; dominant bacak "topa vurulan bacak" olarak tanımlanır.

**Skorlama:**
- İzometrik pik tork (Nm/kg) — kuadriseps (90°) ve hamstring (45°)
- İzokinetik pik tork (Nm/kg) — 180°/sn'de kuadriseps ve hamstring
- H:K Oranı (%) = Hamstring pik torku / Kuadriseps pik torku × 100
- Asimetri İndeksi (%) = (Dominant − Dominant olmayan) / Dominant × 100

**Normatif Değerler (Keytsman et al., 2024 — n=364, Belçika Profesyonel Ligi):**

| Parametre | Dominant Bacak | Dominant Olmayan |
|-----------|---------------|-----------------|
| İzometrik Kuadriseps (Nm/kg) | 2.85 ± 0.49 | 2.77 ± 0.48 |
| İzometrik Hamstring (Nm/kg) | 1.58 ± 0.32 | 1.49 ± 0.30 |
| İzometrik H:K Oranı (%) | 55.6 ± 10.2 | 53.9 ± 10.1 |
| İzokinetik Kuadriseps 180°/sn (Nm/kg) | 2.12 ± 0.38 | 2.14 ± 0.37 |
| İzokinetik Hamstring 180°/sn (Nm/kg) | 1.43 ± 0.27 | 1.39 ± 0.27 |
| İzokinetik H:K Oranı 180°/sn (%) | 67.5 ± 10.8 | 65.2 ± 11.4 |

**Klinik Eşikler (Croisier et al., 2008):**
- H:K < %60 → hamstring yaralanma riski artmış
- Asimetri İndeksi > %10 → klinik değerlendirme önerilir
                """,
                "kaynak": "Keytsman, C., Verbrugghe, J., & Eijnde, B. O. (2024). The isometric and isokinetic knee extension and flexion muscle strength profile of elite soccer players. BMC Sports Science, Medicine and Rehabilitation, 16(1), 180. https://doi.org/10.1186/s13102-024-00961-y\nCroisier, J. L., Ganteaume, S., Binet, J., Genty, M., & Ferret, J. M. (2008). Strength imbalances and prevention of hamstring injury in professional soccer players: a prospective study. American Journal of Sports Medicine, 36(8), 1469-1475.",
                "degiskenler": ["İzometrik Kuadriseps Dom. (Nm/kg)", "İzometrik Hamstring Dom. (Nm/kg)", "İzometrik H:K Dom. (%)", "İzometrik Kuadriseps N-Dom. (Nm/kg)", "İzometrik Hamstring N-Dom. (Nm/kg)", "İzokinetik Kuadriseps 180°/sn Dom. (Nm/kg)", "İzokinetik Hamstring 180°/sn Dom. (Nm/kg)", "İzokinetik H:K 180°/sn Dom. (%)", "İzokinetik Kuadriseps 180°/sn N-Dom. (Nm/kg)", "İzokinetik Hamstring 180°/sn N-Dom. (Nm/kg)", "Pozisyon"]
            },
            "Nordic Hamstring Kuvvet Testi (NHT)": {
                "protokol": """
**Amaç:** Hamstring kaslarının eksantrik kuvvetini ve bacaklar arası asimetriyi ölçmektir — hamstring yaralanma riskinin en önemli göstergelerinden biridir; tüm branşlara uygulanabilir.

**Ekipman:** Kuvvet platformu (force plate) veya izokinetik dinamometre (NordBord sistemi en yaygın) ya da partner + düz zemin (basit versiyon).

**Uygulama:**

**A) NordBord veya Kuvvet Platformu ile (Standart Protokol):**
1. Sporcu diz üstü pozisyonda, bacaklar cihaza sabitlenir.
2. Gövdesini öne doğru kontrollü biçimde yavaşça yere indirir.
3. Her bacaktan ayrı ayrı maksimal eksantrik hamstring kuvveti ölçülür.
4. 3 tekrar; en yüksek değer alınır.

**B) Partner ile Saha Versiyonu (Kuvvet Ölçümü Olmadan):**
1. Sporcu diz üstü, partner ayak bileklerini sabit tutar.
2. Kollar önde çaprazlanmış, gövde mümkün olduğunca yavaş ve kontrollü öne düşürülür.
3. Düşmeye engel olamayacak noktada eller yere konulur.
4. Tekrar sayısı ve kontrol süresi kaydedilir (kalite değerlendirmesi).

**Skorlama:**
- NordBord: Her bacak pik kuvveti (N) ve relatif kuvvet (N/kg)
- Asimetri İndeksi (%) = (Güçlü − Zayıf) / Güçlü × 100
- Basit versiyon: Eksantrik kontrol süresi (sn) ve teknik kalite puanı (1-5)

**Normatif Değerler (Al Attar et al., 2017; Ekstrand et al., 2011 — Elit Futbolcular):**
- Pik kuvvet erkek elit futbolcu: 337 ± 66 N (dominant bacak)
- Asimetri İndeksi < %10 = Simetrik ve güvenli
- Asimetri İndeksi > %15 = Yüksek yaralanma riski

**Klinik Not:** Nordic Hamstring egzersizini içeren sakatlık önleme programları futbolcularda hamstring yaralanma sıklığını %50'ye kadar azaltmaktadır.
                """,
                "kaynak": "Al Attar, W. S. A., Soomro, N., Sinclair, P. J., Pappas, E., & Sanders, R. H. (2017). Effect of injury prevention programs that include the Nordic hamstring exercise on hamstring injury rates in soccer players: a systematic review and meta-analysis. Sports Medicine, 47(5), 907-916.\nEkstrand, J., Hägglund, M., & Waldén, M. (2011). Epidemiology of muscle injuries in professional football (soccer). American Journal of Sports Medicine, 39(6), 1226-1232.\nStein, C. J., Gans, I., Griffith, K., Kinderknecht, J., Yates, B., & Micheli, L. J. (2021). Hamstring injury prevention in youth soccer using the Nordic hamstring exercise. Orthopaedic Journal of Sports Medicine, 9(3), 2325967121989169.",
                "degiskenler": ["Sağ Bacak Pik Kuvveti (N)", "Sol Bacak Pik Kuvveti (N)", "Sağ Bacak (N/kg)", "Sol Bacak (N/kg)"]
            },
                "Loughborough İntermittent Shuttle Test (LIST)": {
                    "protokol": """
    **Amaç:** Futbol maçının aralıklı aktivite örüntüsünü (yürüyüş, tempolu koşu, sprint, dinlenme) saha koşullarında simüle eden branşa özgü yorgunluk testidir; aerobik ve anaerobik kapasiteyi birlikte değerlendirir.

    **Ekipman:** 20m düz alan, ses sistemi (LIST protokol kaydı), kronometre.

    **Uygulama:**
    1. Her bölüm 5 farklı koşu hızından oluşur: yürüyüş → koşu → hızlı koşu → sprint → dinlenme.
    2. Standart protokolde 5 × 15 dakikalık bölüm uygulanır (toplam 75 dk — yarım saha simülasyonu).
    3. Kısa versiyon: 2 × 15 dakika (araştırma amaçlı).
    4. Her sprint sonunda mesafe ve HR kaydedilir.

    **Skorlama:**
    - Tamamlanan bölüm ve sprint sayısı
    - Ortalama sprint süresi (sn)
    - Test sonu HR (bpm)

    **Not:** Futbol-spesifik yorgunluk protokolü olarak Bangsbo'nun Yo-Yo testine güçlü bir alternatif sayılır; geçerlilik ve güvenirliği yüksektir.
                    """,
                    "kaynak": "Nicholas, C. W., Nuttall, F. E., & Williams, C. (2000). The Loughborough Intermittent Shuttle Test: a field test that simulates the activity pattern of soccer. Journal of Sports Sciences, 18(2), 97–104.",
                    "degiskenler": ["Tamamlanan Bölüm Sayısı", "Ortalama Sprint Süresi (sn)", "HR Test Sonu (bpm)"]
                },
                "Illinois Çeviklik Testi": {
                    "protokol": """
    **Amaç:** Çeviklik, hız ve koordinasyonu ölçmek.

    **Ekipman:** 8 koni, 10×5m alan, kronometre.

    **Uygulama:**
    1. Sporcu yüzüstü yatar, başı başlangıç çizgisinde.
    2. Komutla kalkar, zigzag + slalom parkurunu tamamlar (~60m).
    3. 3 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi süre (sn).

    **Normatif (Elit Erkek Futbolcu):** <15.2 sn = Mükemmel
                    """,
                    "kaynak": "Sheppard, J. M., & Young, W. B. (2006). Agility literature review: Classifications, training and testing. Journal of Sports Sciences, 24(9), 919–932.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                }
            },

            "Basketbol": {
                "NBA Lane Agility Testi": {
                    "protokol": """
    **Amaç:** Basketbolcularda yön değiştirme hızını ve ayak çalışmasını değerlendirmektir — NBA Draft Combine'ın temel çeviklik testidir.

    **Ekipman:** Standart NBA boyalarıyla işaretlenmiş basketbol sahası (boya dikdörtgeni), kronometre.

    **Uygulama:**
    1. Sporcu serbest atış çizgisi sol köşesinden başlar, savunma duruşunda (defensive stance) bekler.
    2. Aşağı → sol → yukarı → sağ → aşağı sırasıyla boya alanının çevresini dolaşır.
    3. Her köşede yön değiştirerek tamamlar.
    4. 2 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi tamamlama süresi (sn) — az = iyi.

    **Normatif (NBA Draft):** <10.5 sn = Mükemmel; >11.5 sn = Zayıf
                    """,
                    "kaynak": "Hoare, D. G. (2000). Predicting success in junior elite basketball players: the contribution of anthropometric and physiological attributes. Journal of Science and Medicine in Sport, 3(4), 391-405.\nNBA Draft Combine Official Test Protocols (2023). NBA Basketball Operations.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
                },
                "NBA 3/4 Saha Sprint Testi": {
                    "protokol": """
    **Amaç:** Basketbol sahasında lineer hız ve çabuk başlangıç kapasitesini ölçmektir — NBA Draft Combine standardı.

    **Ekipman:** Basketbol sahası (28m), fotosel veya kronometre.

    **Uygulama:**
    1. Sporcu bir basket altından karşı basket altına (yaklaşık 3/4 saha = ~21m) maksimal hızla koşar.
    2. Durarak başlangıç.
    3. 2 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi tamamlama süresi (sn).

    **Normatif (NBA Draft):** <3.0 sn = Mükemmel
                    """,
                    "kaynak": "Drinkwater, E. J., Pyne, D. B., & McKenna, M. J. (2008). Design and interpretation of anthropometric and fitness testing of basketball players. Sports Medicine, 38(7), 565-578.\nNBA Draft Combine Official Test Protocols (2023). NBA Basketball Operations.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
                },
                "Dikey Sıçrama - Basketbol (CMJ + SJ)": {
                    "protokol": """
    **Amaç:** Alt ekstremite patlayıcı gücünü ölçmektir; basketbolda smaç, ribaund ve savunma sıçramalarıyla doğrudan ilişkilidir.

    **Ekipman:** Sıçrama platformu veya Vertec (yükseklik ölçer), kronometre.

    **Uygulama:**
    **A) Countermovement Jump (CMJ):**
    1. Eller kalçada, dik duruş.
    2. Serbest ön-çömelme (countermovement) ile maksimal dikey sıçrama.
    3. 3 deneme; en iyi değer.

    **B) Squat Jump (SJ):**
    1. 90° diz açısında statik çömelme pozisyonu, 2 sn bekleme.
    2. Ön-çömelme olmadan maksimal sıçrama.
    3. 3 deneme; en iyi değer.

    **C) Serbest Kollu CMJ (NBA standardı):**
    1. Eller serbest, kollar sıçramaya yardımcı.
    2. NBA Draft Combine'da standart protokol.

    **Skorlama:** Sıçrama yüksekliği (cm); CMJ − SJ farkı reaktif kuvvet göstergesidir.

    **Normatif (NBA Draft):** CMJ (serbest kollu) >85 cm = Mükemmel
                    """,
                    "kaynak": "Drinkwater, E. J. et al. (2008). Design and interpretation of anthropometric and fitness testing of basketball players. Sports Medicine, 38(7), 565-578.\nBosco, C., Luhtanen, P., & Komi, P. V. (1983). A simple method for measurement of mechanical power in jumping. European Journal of Applied Physiology, 50(2), 273-282.",
                    "degiskenler": ["CMJ Deneme 1 (cm)", "CMJ Deneme 2 (cm)", "CMJ Deneme 3 (cm)", "SJ Deneme 1 (cm)", "SJ Deneme 2 (cm)", "SJ Deneme 3 (cm)"]
                },
                "Yo-Yo IR1 (Basketbol)": {
                    "protokol": """
    **Amaç:** Basketbolcuların aralıklı aerobik dayanıklılık kapasitesini ölçmektir.

    **Uygulama:** Futbol versiyonuyla aynı protokol uygulanır (20m çift yön, 10 sn aktif dinlenme).

    **Basketbol Farkı:** Sonuçlar basketbol pozisyonuna göre değerlendirilir; guard'lar genellikle forvet ve pivotlardan daha yüksek mesafe tamamlar.

    **Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4

    **Normatif (Elit Erkek):** Guard >1600m, Forward >1400m, Center >1200m
                    """,
                    "kaynak": "Castagna, C., Impellizzeri, F. M., Rampinini, E., D'Ottavio, S., & Manzi, V. (2008). The Yo-Yo intermittent recovery test in basketball players. Journal of Science and Medicine in Sport, 11(2), 202-208.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },

            "Voleybol": {
                "Dikey Sıçrama - Voleybol (CMJ + SJ + DJ)": {
                    "protokol": """
    **Amaç:** Smaç, blok ve servis sıçramalarıyla doğrudan ilişkili alt ekstremite patlayıcı gücünü değerlendirmektir.

    **Ekipman:** Sıçrama platformu veya Vertec.

    **Uygulama:**
    **A) CMJ (Countermovement Jump):** Eller kalçada, ön-çömelme ile maksimal sıçrama. 3 deneme.
    **B) SJ (Squat Jump):** 90° diz açısında statik başlangıç, ön-çömelme yok. 3 deneme.
    **C) DJ (Drop Jump):** 30 cm yüksekten inişin ardından minimal temas süresiyle maksimal sıçrama. 3 deneme.

    **Skorlama:**
    - Her sıçrama tipi için en iyi yükseklik (cm)
    - Reaktif Kuvvet İndeksi (RKİ) = DJ yüksekliği / Temas süresi

    **Normatif (Elit Kadın Voleybolcu):** CMJ >45 cm = Mükemmel
                    """,
                    "kaynak": "Sheppard, J. M., Gabbett, T. J., & Stanganelli, L. C. R. (2009). An analysis of playing positions in elite men's volleyball: considerations for competition demands and physiologic characteristics. Journal of Strength and Conditioning Research, 23(6), 1858-1866.\nMarcelino, R. et al. (2014). Volleyball game related statistics that discriminate between winning and losing teams. Journal of Sports Science and Medicine, 13(1), 24-31.",
                    "degiskenler": ["CMJ En İyi (cm)", "SJ En İyi (cm)", "DJ En İyi (cm)", "DJ Temas Süresi (ms)"]
                },
                "20m Sprint - Voleybol": {
                    "protokol": """
    **Amaç:** Voleybolcularda kısa mesafe hızını ve çabuk başlangıç kapasitesini ölçmektir.

    **Ekipman:** 20m düz alan, fotosel veya kronometre.

    **Uygulama:**
    1. Sporcu durarak başlangıç yapar.
    2. 20 metre maksimal hızla koşar.
    3. 3 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi süre (sn).

    **Normatif (Elit Erkek):** <2.85 sn = Mükemmel
                    """,
                    "kaynak": "Sheppard, J. M. et al. (2009). An analysis of playing positions in elite men's volleyball. Journal of Strength and Conditioning Research, 23(6), 1858-1866.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                },
                "Voleybol Çeviklik Testi (VAT)": {
                    "protokol": """
    **Amaç:** Voleybolcuların sahaya özgü yön değiştirme ve çeviklik kapasitesini ölçmektir.

    **Ekipman:** Voleybol sahası (9×18m), 4 koni, kronometre.

    **Uygulama:**
    1. Sporcu sahada orta noktadan başlar.
    2. Sırasıyla: sol ön köşe → sağ ön köşe → sağ arka köşe → sol arka köşe → başlangıç noktasına döner.
    3. Her köşede zemine dokunulur.
    4. 2 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi tamamlama süresi (sn).
                    """,
                    "kaynak": "Gabbett, T., Georgieff, B., Anderson, S., Cotton, B., Savovic, D., & Nicholson, L. (2006). Changes in skill and physical fitness following training in talent-identified volleyball players. Journal of Strength and Conditioning Research, 20(1), 29-35.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)"]
                },
                "Yo-Yo IR1 (Voleybol)": {
                    "protokol": """
    **Amaç:** Voleybolcuların aerobik dayanıklılık kapasitesini ölçmektir.

    **Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme, artan hız).

    **Voleybol Farkı:** Pozisyona göre değerlendirme yapılır; libero ve pasörlerin genellikle daha yüksek aerobik kapasiteye sahip olduğu bildirilmektedir.

    **Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4
                    """,
                    "kaynak": "Gabbett, T. J., & Georgieff, B. (2007). Physiological and anthropometric characteristics of junior national, state, and novice volleyball players. Journal of Strength and Conditioning Research, 21(3), 902-908.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                }
            },

            "Buz Hokeyi": {
                "S-Turn Testi": {
                    "protokol": """
    **Amaç:** Paten çevikliğini ve dönüş hızını ölçmek.

    **Ekipman:** Buz pisti, 5 koni (S şeklinde 3m aralıklarla), kronometre.

    **Uygulama:**
    1. Sporcu start çizgisinde hazır bekler.
    2. Koniler S şeklinde slalom yaparak geçilir.
    3. 3 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi süre (sn) — az = iyi.
                    """,
                    "kaynak": "Peyer, K. L., Pivarnik, J. M., Eisenmann, J. C., & Vorkapich, M. (2011). Physiological characteristics of National Hockey League (NHL) draft picks. Journal of Strength and Conditioning Research, 25(9), 2365-2369.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                },
                "30m Paten Hızı": {
                    "protokol": """
    **Amaç:** Buzda düz çizgide maksimal paten hızını ölçmek.

    **Ekipman:** Buz pisti, fotosel veya kronometre.

    **Uygulama:**
    1. Sporcu durarak başlangıç yapar.
    2. 30 metre düz buz maksimal hızla kat edilir.
    3. 3 deneme yapılır; en iyi süre kaydedilir.

    **Skorlama:** En iyi süre (sn).
                    """,
                    "kaynak": "Burr, J. F. et al. (2008). Relationship of physical fitness test results and hockey playing potential in elite-level ice hockey players. Journal of Strength and Conditioning Research, 22(5), 1535-1543.",
                    "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
                },
                "NHL/NHLTM Off-Ice Testleri": {
                    "protokol": """
    **Amaç:** Buz dışı (kara) testlerle hokeycilerin genel fiziksel uygunluğunu değerlendirmektir — NHL Draft Combine standardı.

    **Ekipman:** Bisiklet ergometresi, pull-up barı, dinamometre, Vertec.

    **Uygulama — 5 bileşen:**
    1. **VO2max (Bisiklet):** Kademeli artan yük protokolü; gaz analizi veya Wingate yöntemiyle.
    2. **Pull-Up:** Maksimum tekrar sayısı (tam ekstansiyondan çeneye).
    3. **Bench Press (Relative):** Vücut ağırlığının %75'iyle maksimum tekrar.
    4. **CMJ:** Eller serbest, ön-çömelmeyle sıçrama yüksekliği (cm).
    5. **El Kavrama Kuvveti:** Dominant el, 3 deneme, en iyi (kg).

    **Skorlama:** Her bileşen NHL Draft Combine normatif tablolarıyla değerlendirilir.

    **Normatif (NHL Draft, Erkek):**
    - VO2max: >60 ml/kg/min = Mükemmel
    - Pull-Up: >12 tekrar = Mükemmel
                    """,
                    "kaynak": "Peyer, K. L. et al. (2011). Physiological characteristics of NHL draft picks. Journal of Strength and Conditioning Research, 25(9), 2365-2369.\nBurr, J. F. et al. (2008). Physical fitness test results and hockey playing potential in elite-level ice hockey players. Journal of Strength and Conditioning Research, 22(5), 1535-1543.",
                    "degiskenler": ["VO2max (ml/kg/min)", "Pull-Up (tekrar)", "Bench Press (tekrar)", "CMJ (cm)", "El Kavrama (kg)"]
                },
                "Hızlanma Paten Testi (6m + 30m)": {
                    "protokol": """
    **Amaç:** Hokeycilerin hem çabuk başlangıç hızlanmasını (6m) hem de maksimal paten hızını (30m) aynı anda ölçmektir.

    **Ekipman:** Buz pisti, çoklu fotosel sistemi (6m ve 30m noktalarında), kronometre.

    **Uygulama:**
    1. Sporcu durarak başlangıç yapar.
    2. Fotosel sistemi 6. ve 30. metredeki süreleri ayrı ayrı kaydeder.
    3. 3 deneme yapılır; en iyi değerler kaydedilir.

    **Skorlama:**
    - 6m süresi (sn) — çabuk başlangıç / hızlanma
    - 30m süresi (sn) — maksimal paten hızı

    **Not:** İki ölçümün birlikte alınması, hokeycinin hem hızlanma profilini hem de maksimal hızını karşılaştırmalı değerlendirmeye imkân tanır.
                    """,
                    "kaynak": "Burr, J. F. et al. (2008). Relationship of physical fitness test results and hockey playing potential in elite-level ice hockey players. Journal of Strength and Conditioning Research, 22(5), 1535-1543.\nFarrell, P. et al. (2009). Ice hockey performance testing battery. Strength and Conditioning Journal, 31(4), 44-49.",
                    "degiskenler": ["6m Süresi (sn)", "30m Süresi (sn)"]
                }
            },

            "Rugby": {
                "Rugby League Match Simulation Protocol (RLMSP)": {
                    "protokol": """
    **Amaç:** Rugby maçının fizyolojik taleplerini simüle eden branşa özgü dayanıklılık testidir.

    **Ekipman:** Düz alanda koni parkuru, ses sistemi (RLMSP kaydı), kronometre, KAH monitörü.

    **Uygulama:**
    1. Hız ses sinyaliyle belirlenir; sporcu renkli koniler arasında yürüme, hafif koşu, hızlı koşu ve sprint yapar; dakikada yaklaşık bir temas (çarpışma) vardır.
    2. Sprint bölümleri maksimal hızla, diğer bölümler sinyalin verdiği hızla tamamlanır.
    3. KAH ve RPE bölüm sonlarında kaydedilir.

    **Not:** Sykes ve ark. (2013) protokolü dört çeyreğe bölünür; toplam yaklaşık 8.444 m, dakikada yaklaşık 97 m. Yedek oyuncu sürümü (RLMSP-i; Waldron ve ark., 2013) 2 × 23 dk, arada 20 dk pasif dinlenmedir (Mullen, Twist ve Highton, 2019 aktarımı). Önceki "5 devre × 10 dk (toplam 50 dk)" yapısı ve "20 m" alan ölçüsü doğrulanamadı. Değişken adlarındaki "devre" bölüm anlamında kullanılır.

    **Skorlama:**
    - Tamamlanan devre sayısı
    - Sprint bölümleri ortalama süresi (sn)
    - Her devre sonu HR (bpm)
                    """,
                    "kaynak": "Gabbett, T. J. (2005). Science of rugby league football: a review. Journal of Sports Sciences, 23(9), 961-976.\nGabbett, T. J., Jenkins, D. G., & Abernethy, B. (2012). Physical demands of professional rugby league training and competition using microtechnology. Journal of Science and Medicine in Sport, 15(1), 80-86.\nSykes, D., Nicholas, C., Lamb, K., & Twist, C. (2013). An evaluation of the external validity and reliability of a rugby league match simulation protocol. Journal of Sports Sciences, 31(1), 48-57.\nMullen, T., Twist, C., & Highton, J. (2019). Stochastic ordering of simulated rugby match activity produces reliable movements and associated measures of subjective task load, cognitive and neuromuscular function. Journal of Sports Sciences, 37(21), 2506-2512.",
                    "degiskenler": ["Tamamlanan Devre", "Sprint Ort. Süresi (sn)", "HR Devre 1 (bpm)", "HR Devre 2 (bpm)", "HR Devre 3 (bpm)"]
                },
                "NFL Combine Testleri": {
                    "protokol": """
    **Amaç:** Amerikan futbolu oyuncularının fiziksel uygunluğunu çok yönlü değerlendirmektir — NFL Draft'ın standart test bataryasıdır.

    **Ekipman:** Fotosel sistemi, Vertec, tartı, mezura.

    **Uygulama — 6 bileşen:**
    1. **40-yard Dash (36.58m):** Durarak başlangıç, maksimal sprint; 2 deneme.
    2. **Bench Press (102.3 kg / 225 lbs):** Maksimum tekrar sayısı.
    3. **Dikey Sıçrama (CMJ):** Serbest kollu, Vertec ile ölçüm; 3 deneme.
    4. **Durarak Uzun Atlama:** Çift ayak, 3 deneme, en iyi.
    5. **20-yard Shuttle (18.3m):** 5+10+5 yard mekik; 2 deneme.
    6. **3-Cone Drill (L-Drill):** L şeklinde çeviklik parkuru; 2 deneme.

    **Skorlama:** Her bileşen için en iyi değer; NFL pozisyon normlarıyla değerlendirilir.

    **Not:** Altı bileşen (40 yard — 10, 20 ve 40 yardda süre; 225 lb bench tekrar; dikey sıçrama — ayakta uzanma ile en yüksek dokunma farkı; durarak uzun atlama; 5-10-5 kısa mekik; L şeklinde 3 koni) kulüp kaynaklarıyla doğrulandı; deneme sayıları doğrulanamadı. "40 yard < 4.40 sn" ve "dikey > 38 inç" eşikleri doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "McGee, K. J., & Burkett, L. N. (2003). The National Football League combine: a reliable predictor of draft status? Journal of Strength and Conditioning Research, 17(1), 6-11.\nGarstecki, M. A., Latin, R. W., & Cuppett, M. M. (2004). Comparison of selected physical fitness and performance variables between NCAA Division I and II football players. Journal of Strength and Conditioning Research, 18(2), 292-297.",
                    "degiskenler": ["40-yard (sn)", "Bench Press (tekrar)", "Dikey Sıçrama (cm)", "Uzun Atlama (cm)", "20-yard Shuttle (sn)", "3-Cone Drill (sn)"]
                },
                "Rugby Union Fitness Test Bataryası": {
                    "protokol": """
    **Amaç:** Rugby Union oyuncularının pozisyona göre fiziksel uygunluğunu değerlendirmektir — World Rugby (eski IRB) standartları.

    **Ekipman:** Fotosel, dinamometre, bisiklet ergometresi, kronometre.

    **Uygulama — 5 bileşen:**
    1. **Yo-Yo IR1:** Standart protokol (20m, 10 sn dinlenme).
    2. **10m Sprint:** Durarak başlangıç, fotosel; 3 deneme.
    3. **CMJ:** Eller kalçada; 3 deneme, en iyi.
    4. **El Kavrama Kuvveti:** Dominant el dinamometre; 3 deneme.
    5. **Bench Press (1RM veya relatif):** Maksimal kaldırma veya vücut ağırlığına normalize.

    **Skorlama:** Her bileşen için en iyi değer; pozisyona göre (forward/back) normatif tablolarla değerlendirilir.

    **Not:** Bu beş bileşenli düzen bir "World Rugby standardı" olarak doğrulanamadı; her bileşen kendi standart protokolüyle uygulanır. ">2200 m" ve "<1.65 sn" eşikleri doğrulanamadı; norm gösterilmez. Kaynak listesindeki Cuthbert ve ark. (2019) künyesi bulunamadı, çıkarıldı.
                    """,
                    "kaynak": "Duthie, G., Pyne, D., & Hooper, S. (2003). Applied physiology and game analysis of rugby union. Sports Medicine, 33(13), 973-991.",
                    "degiskenler": ["Yo-Yo IR1 (m)", "10m Sprint (sn)", "CMJ (cm)", "El Kavrama (kg)", "Bench Press (kg)"]
                }
            },
            "Hentbol": {
                "Yo-Yo IR1 (Hentbol)": {
                    "protokol": """
**Uygulama:** Standart Yo-Yo IR1 protokolü uygulanır (20m çift yön, 10 sn aktif dinlenme).

**Hentbol Farkı:** Sonuçlar hentbol pozisyonuna göre değerlendirilir; kaleciler diğer pozisyonlardan farklı aerobik profile sahiptir.

**Skorlama:** Tamamlanan mesafe (m); VO2max = Mesafe × 0.0084 + 36.4

**Normatif (Elit Erkek):** > 2000m = İyi
                    """,
                    "kaynak": "Michalsik, L. B., Madsen, K., & Aagaard, P. (2015). Technical activity profile and influence of body anthropometry on playing performance in male elite team handball. Journal of Strength and Conditioning Research, 29(2), 416-428.",
                    "degiskenler": ["Tamamlanan Mesafe (m)"]
                },
                "Hentbol Çeviklik ve Sprint Testi": {
                    "protokol": """
**Amaç:** Hentbolcuların sahaya özgü çevikliğini ve hızını değerlendirmektir.

**Ekipman:** 30m düz alan + koni seti, fotosel veya kronometre.

**Uygulama:**
1. **30m Sprint:** Durarak başlangıç, 3 deneme; en iyi süre.
2. **Illinois Çeviklik:** Standart protokol; 3 deneme, en iyi süre.

**Skorlama:**
- 30m sprint süresi (sn)
- Illinois çeviklik süresi (sn)

**Normatif (Elit Erkek Hentbolcu):** 30m < 4.0 sn = Mükemmel
                    """,
                    "kaynak": "Michalsik, L. B. et al. (2015). JSCR, 29(2), 416-428.\nMohr, M. et al. (2014). Physiological responses to elite team handball. Scandinavian Journal of Medicine & Science in Sports, 24(6), 994-1001.",
                    "degiskenler": ["30m Sprint (sn)", "Illinois Çeviklik (sn)"]
                },
                "Dikey Sıçrama (Hentbol)": {
                    "protokol": """
**Uygulama:** Standart CMJ ve SJ protokolü uygulanır.

**Hentbol Farkı:** Hentbolda fırlatma ve blok sıçramalarıyla doğrudan ilişkilidir; sonuçlar hentbol normlarıyla değerlendirilir.

**Normatif (Elit Erkek Pivot):** CMJ > 50 cm = Mükemmel
                    """,
                    "kaynak": "Michalsik, L. B. et al. (2015). JSCR, 29(2), 416-428.",
                    "degiskenler": ["CMJ En İyi (cm)", "SJ En İyi (cm)"]
                }
            },
            "Su Topu": {
                "Su Topu Spesifik Aerobik Test (WPOAT)": {
                    "protokol": """
**Amaç:** Su topu oyuncularının suda aerobik kapasitesini değerlendirmektir.

**Ekipman:** 25m veya 50m havuz, kronometre, KAH monitörü.

**Uygulama:**
1. Sporcu 6 × 100m aralıklı serbest stil yüzme yapar.
2. Her 100m arasında 30 sn dinlenme.
3. Her 100m süresi ve HR kaydedilir.

**Skorlama:**
- Her 100m süresi (sn)
- Ortalama 100m süresi (sn)
- HR toparlanma profili

**Not:** 6 × 100 m / 30 sn düzeni kaynakla doğrulanamadı: gösterilen kaynak (Platanou, 2005) suda dikey sıçrama üzerinedir, bu testi tanımlamaz; Erzurum Caf ve ark. (2019) künyesi bulunamadı, çıkarıldı. Doğrulanmış su topu dayanıklılık testi: WIST (Mujika ve ark., 2006, IJSPP 1, 27-39). "< 70 sn" eşiği doğrulanamadı; norm gösterilmez. Görsel yalnız serbest stil yüzüşü gösterir.
                    """,
                    "kaynak": "Platanou, T. (2005). On-water and dryland vertical jump in water polo players. Journal of Sports Medicine and Physical Fitness, 45(1), 26-31.",
                    "degiskenler": ["100m Tur 1 (sn)", "100m Tur 2 (sn)", "100m Tur 3 (sn)", "100m Tur 4 (sn)", "100m Tur 5 (sn)", "100m Tur 6 (sn)"]
                },
                "Dikey Sıçrama - Suda (Su Topu)": {
                    "protokol": """
**Amaç:** Su içindeki dikey sıçrama yüksekliğini ölçmektir — su topu oyuncusunun fırlatma ve blok performansıyla doğrudan ilişkilidir.

**Ekipman:** Havuz (dip yok), mezura veya ölçüm çubuğu.

**Uygulama:**
1. Sporcu havuzda eggbeater (yumurta çırpıcı) hareketi yaparken yerinde bekler.
2. "Git" komutuyla maksimal dikey sıçrama yapar.
3. Sıçrama yüksekliği su yüzeyinden ölçülür.
4. 3 deneme; en iyi değer kaydedilir.

**Skorlama:** Su yüzeyinden maksimal sıçrama yüksekliği (cm).

**Not:** Su yüzeyinden ölçüm ve 3 deneme Platanou (2006) ile doğrulandı (Yunan birinci lig ortalaması 68,6 ± 5,4 cm — tanımlayıcı, norm değil). Bekleme sırasındaki eggbeater ayrıntısı kaynakta yazılı değildir. "> 70 cm = Mükemmel" eşiği doğrulanamadı; norm gösterilmez.
                    """,
                    "kaynak": "Platanou, T. (2005). On-water and dryland vertical jump in water polo players. Journal of Sports Medicine and Physical Fitness, 45(1), 26-31.\nPlatanou, T. (2006). Simple 'in-water' vertical jump testing in water polo. Kinesiology, 38(1), 57-62.",
                    "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"]
                }
            }
        }
    },

    "Laboratuvar ve Fizyolojik Testler": {
        "Aerobik (Saha ve Laboratuvar)": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "20m Mekik Koşusu (Beep Test)": {
                "protokol": """
**Amaç:** Maksimal aerobik kapasiteyi (VO2max) saha koşullarında tahmin etmek.

**Ekipman:** 20m düz alan, beep ses sistemi, kronometre.

**Uygulama:**
1. 20m çift yön koşu, bip sesiyle artan hız.
2. Başlangıç hızı 8.5 km/h, her dakika 0.5 km/h artar.
3. Bipe 2 kez yetişemeyen sporcu testi bitirir.

**Skorlama:** VO2max (Maksimal Oksijen Tüketimi) = 22.859 + (Seviye × 1.593)
                """,
                "kaynak": "Léger, L. A., Mercier, D., Gadoury, C., & Lambert, J. (1988). The multistage 20 metre shuttle run test for aerobic fitness. Journal of Sports Sciences, 6(2), 93-101.",
                "degiskenler": ["Son Seviye", "Son Tekrar"]
            },
            "Cooper 12 Dakika Koşusu": {
                "protokol": """
**Amaç:** VO2max (Maksimal Oksijen Tüketimi) tahmini için klasik saha testi.

**Ekipman:** Düz atletizm pisti (400m), kronometre.

**Uygulama:**
1. Sporcu 12 dakika boyunca mümkün olduğunca fazla mesafe koşar.
2. Yürüyüş yapılabilir ancak skor düşer.
3. 12. dakika sonunda kat edilen mesafe ölçülür.

**Skorlama:** VO2max (Maksimal Oksijen Tüketimi) = (Mesafe − 504.9) / 44.73

**Normatif (Elit Erkek):** > 3000m = Mükemmel
                """,
                "kaynak": "Cooper, K. H. (1968). A means of assessing maximal oxygen intake. JAMA, 203(3), 201-204.",
                "degiskenler": ["Tamamlanan Mesafe (m)"]
            },
            "Yo-Yo IR1 (Genel)": {
                "protokol": """
**Amaç:** Yüksek yoğunluklu aralıklı koşu kapasitesini ve VO2max (Maksimal Oksijen Tüketimi)'i tahmin etmektir — tüm branşlara uygulanabilen genel versiyon.

**Ekipman:** 20m düz alan, beep ses sistemi, kronometre.

**Uygulama:**
1. 20m çift yön koşu, bip sesiyle artan hız (başlangıç 10 km/h).
2. Her turda 10 saniyelik aktif dinlenme (5m gidip gelme).
3. 2 kez üst üste bipe yetişemeyen testi bitirir.

**Skorlama:**
- Tamamlanan mesafe (m)
- VO2max (Maksimal Oksijen Tüketimi) = Mesafe × 0.0084 + 36.4

**Normatif (Genel, Elit Erkek):** > 2000m = İyi; > 2400m = Mükemmel
                """,
                "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test: a useful tool for evaluation of physical performance in intermittent sports. Sports Medicine, 38(1), 37-51.",
                "degiskenler": ["Tamamlanan Mesafe (m)", "Son Seviye"]
            },
            "Yo-Yo IR2 (Genel)": {
                "protokol": """
**Amaç:** Elit sporcularda çok yüksek yoğunluklu aralıklı performansı ölçmek — IR1'den daha yüksek başlangıç hızıyla.

**Ekipman:** 20m düz alan, beep ses sistemi (IR2 versiyonu).

**Uygulama:**
1. IR1 ile aynı format (20m çift yön, 10 sn aktif dinlenme).
2. Başlangıç hızı daha yüksektir (13 km/h).
3. 2 kez üst üste bipe yetişemeyen testi bitirir.

**Skorlama:**
- Tamamlanan mesafe (m)
- VO2max (Maksimal Oksijen Tüketimi) = Mesafe × 0.0136 + 45.3 *(IR2 denklemi; IR1'den farklıdır)*

**Normatif (Elit Erkek):** > 800m = İyi
                """,
                "kaynak": "Bangsbo, J., Iaia, F. M., & Krustrup, P. (2008). The Yo-Yo intermittent recovery test. Sports Medicine, 38(1), 37-51.",
                "degiskenler": ["Tamamlanan Mesafe (m)"]
            },
            "30-15 Aralıklı Fitness Testi (IFT)": {
                "protokol": """
**Amaç:** Aerobik kapasiteyi (VIFT) aralıklı koşu formatında değerlendirmektir — özellikle takım sporları için geliştirilmiştir.

**Ekipman:** 40m düz alan, ses sistemi (30-15 IFT kaydı), kronometre.

**Uygulama:**
1. 40m'yi ses sinyalleriyle belirlenen hızda koş.
2. Her 30 sn koşunun ardından 15 sn yürüyüş yap.
3. Her aşamada hız 0.5 km/h artar (başlangıç 8 km/h).
4. 2 kez üst üste sinyale yetişemeyince test biter.

**Skorlama:**
- VIFT (son aşamanın hızı, km/h)
- VO2max (Maksimal Oksijen Tüketimi) tahmini = 28.156 + (2.996 × VIFT)

**Normatif (Elit Erkek):** VIFT > 19 km/h = Mükemmel
                """,
                "kaynak": "Buchheit, M. (2008). The 30-15 intermittent fitness test: accuracy for individualizing interval training of young intermittent sport players. Journal of Strength and Conditioning Research, 22(2), 365-374.",
                "degiskenler": ["Son Hız - VIFT (km/h)"]
            },
            "VO2max Direkt Ölçüm (Ergospirometri)": {
                "protokol": """
**Amaç:** Maksimal oksijen tüketimini (VO2max) doğrudan ölçmektir — aerobik kapasitenin altın standart testidir.

**Ekipman:** Bisiklet ergometresi veya koşu bandı, metabolik analiz sistemi (ergospirometri), maske/snorkel, KAH monitörü.

**Uygulama:**
1. 5 dakika ısınma (düşük yoğunluk).
2. Kademeli artan yük protokolü (her 2-3 dk bir basamak) veya rampa protokolü.
3. Solunum gazları anlık ölçülür (O₂ tüketimi, CO₂ üretimi, VE).
4. Sporcu tamamen tükenerek maksimal eforu verdiğinde test biter.
5. VO2max kriterleri: VO2 plato (< 2.1 ml/kg/dk artış), RER > 1.10, KAH ≥ yaş tahmini maksimuma.

**Skorlama:**
- VO2max (ml/kg/min) — mutlak ve relatif
- VT1 (birinci ventilasyon eşiği) ve VT2 (ikinci ventilasyon eşiği)
- RER (solunum değişim oranı)
- Maksimal güç (watt) veya hız (km/h)

**Normatif (Elit Erkek Dayanıklılık):** > 70 ml/kg/min = Mükemmel
                """,
                "kaynak": "Poole, D. C., & Jones, A. M. (2017). Measurement of the maximum oxygen uptake (VO2max): VO2peak is no longer acceptable. Journal of Applied Physiology, 122(4), 997-1002.\nBalady, G. J. et al. (2010). Clinician's guide to cardiopulmonary exercise testing in adults. Circulation, 122(2), 191-225.",
                "degiskenler": ["VO2max (ml/kg/min)", "VT1 (ml/kg/min)", "VT2 (ml/kg/min)", "Maks. Güç/Hız", "Maks. KAH (bpm)", "Test Protokolü"]
            },
            "Laktat Eşiği Testi": {
                "protokol": """
**Amaç:** Kan laktat konsantrasyonunun egzersiz yoğunluğuyla ilişkisini belirleyerek aerobik (LT1) ve anaerobik (LT2) eşikleri saptamaktır.

**Ekipman:** Bisiklet ergometresi veya koşu bandı, kan laktat analizörü (Lactate Pro, YSI vb.), kapiler kan örnekleme kiti.

**Uygulama:**
1. Kademeli artan yük protokolü (her basamak 3-5 dk).
2. Her basamak sonunda kan örneği alınır (parmak ucu / kulak memesi).
3. Dinlenme laktat değeri (< 1.0 mmol/L) temel alınır.
4. Laktat-yoğunluk eğrisi çizilir.

**Skorlama:**
- LT1 (Birinci Laktat Eşiği): Laktatın bazalden anlamlı artışı (~2 mmol/L)
- LT2 / OBLA: Laktat 4 mmol/L sabit noktası
- Her eşiğe karşılık gelen güç (W) veya hız (km/h) ve KAH (bpm)
                """,
                "kaynak": "Faude, O., Kindermann, W., & Meyer, T. (2009). Lactate threshold concepts. Sports Medicine, 39(6), 469-490.\nSjödin, B., & Jacobs, I. (1981). Onset of blood lactate accumulation and marathon running performance. International Journal of Sports Medicine, 2(01), 23-26.",
                "degiskenler": ["LT1 Güç/Hız", "LT1 KAH (bpm)", "LT1 Laktat (mmol/L)", "LT2 Güç/Hız", "LT2 KAH (bpm)", "LT2 Laktat (mmol/L)"]
            },
            "Kardiyopulmoner Egzersiz Testi (CPET)": {
                "protokol": """
**Amaç:** Egzersiz sırasında kardiyovasküler, pulmoner ve metabolik sistemleri eş zamanlı değerlendirmektir.

**Ekipman:** Ergospirometri sistemi, EKG (12 derivasyonlu), KAH monitörü, sfigmomanometre, bisiklet ergometresi veya koşu bandı.

**Uygulama:**
1. İstirahat EKG ve kan basıncı ölçümü.
2. Rampa veya kademeli protokol (bireyselleştirilmiş yük artışı).
3. Solunum gazları, EKG, KAH, kan basıncı anlık kaydedilir.
4. Maksimal efor veya semptom sınırlı test tamamlanır.
5. Toparlanma dönemi (5-10 dk) izlenir.

**Skorlama:**
- VO2max / VO2peak (ml/kg/min)
- VE/VCO2 eğimi
- Oksijen nabzı (VO2/KAH)
- VT1 ve VT2 noktaları
- Egzersiz kapasitesi (MET veya watt)
                """,
                "kaynak": "Wasserman, K. et al. (2005). Principles of Exercise Testing and Interpretation (4th ed.). Lippincott Williams & Wilkins.\nATS/ACCP Statement on Cardiopulmonary Exercise Testing (2003). American Journal of Respiratory and Critical Care Medicine, 167(2), 211-277.",
                "degiskenler": ["VO2max (ml/kg/min)", "VE/VCO2 Eğimi", "Oksijen Nabzı (ml/atım)", "VT1 (ml/kg/min)", "VT2 (ml/kg/min)", "Maks. KAH (bpm)", "Test Protokolü"]
            }
        },
        "Anaerobik, Güç ve Nöromüsküler": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "Wingate 30sn Bisiklet Testi": {
                "protokol": """
**Amaç:** Anaerobik pik güç ve anaerobik kapasiteyi ölçmek.

**Ekipman:** Monark bisiklet ergometresi, vücut ağırlığının %7.5'i direnç.

**Uygulama:** 5 dk ısınma, ardından "hazır ol" komutuyla 30 saniye maksimal pedal çevirme.

**Skorlama:** Pik Güç, Ortalama Güç, Yorgunluk İndeksi = (Pik-Min)/Pik × 100
                """,
                "kaynak": "Bar-Or, O. (1987). The Wingate anaerobic test: An update on methodology, reliability and validity. Sports Medicine, 4(6), 381-394.",
                "degiskenler": ["Pik Güç (W)", "Ortalama Güç (W)", "Min Güç (W)"]
            },
            "İzokinetik Kuvvet Testi": {
                "protokol": """
**Amaç:** Eklem hareketinde açısal hız sabit tutularak kasın maksimal tork üretimini ölçmektir — kas kuvvetinin en objektif laboratuvar yöntemi.

**Ekipman:** İzokinetik dinamometre (Biodex, Cybex, Humac Norm vb.).

**Uygulama:**
1. Sporcu dinamometreye sabitlenir; test edilecek eklem hizalanır.
2. Birkaç submaksimal ısınma tekrarı yapılır.
3. Seçilen açısal hızlarda (60°/sn, 180°/sn, 300°/sn) konsantrik/eksantrik ölçümler alınır.
4. Her hızda 5-10 maksimal tekrar.

**Skorlama:**
- Pik Tork (Nm) — her açısal hızda
- Relatif Pik Tork (Nm/kg)
- H:Q Oranı (Hamstring/Kuadriseps)
- Yorgunluk indeksi (%)

**Klinik Not:** H:Q oranı < 0.60 çapraz bağ yaralanması risk göstergesidir.
                """,
                "kaynak": "Dvir, Z. (2004). Isokinetics: Muscle testing, interpretation and clinical applications (2nd ed.). Churchill Livingstone.\nCoombs, R., & Garbutt, G. (2002). Developments in the use of the hamstring/quadriceps ratio. Journal of Sports Science and Medicine, 1(3), 56-62.",
                "degiskenler": ["Pik Tork 60°/sn (Nm)", "Pik Tork 180°/sn (Nm)", "H:Q Oranı 60°/sn", "H:Q Oranı 180°/sn", "Test Ekstremitesi (Sağ/Sol)", "Eklem"]
            },
            "Force-Velocity Profili (F-V)": {
                "protokol": """
**Amaç:** Kasın kuvvet-hız ilişkisini belirleyerek bireysel nöromüsküler profili ortaya koymaktır; antrenman yönelimini optimize etmekte kullanılır.

**Ekipman:** Güç ölçer (force plate) veya lineer enkoder + serbest ağırlık.

**Uygulama:**
1. Sporcu birden fazla farklı yükte (%30, %45, %60, %75, %90 1RM) squat jump veya bench press throw yapar.
2. Her yükte 3 maksimal tekrar; en yüksek güç değeri alınır.
3. Kuvvet (F) ve hız (v) değerleri koordinat sistemine işlenerek doğrusal regresyon uygulanır.

**Skorlama:**
- F₀ (teorik maksimal kuvvet, N)
- v₀ (teorik maksimal hız, m/s)
- Pmax (maksimal güç, W)
- F-V eğimi (kuvvet-hız dengesi)
                """,
                "kaynak": "Samozino, P. et al. (2012). Optimal force-velocity profile in ballistic movements. Medicine & Science in Sports & Exercise, 44(2), 313-322.\nMorin, J. B., & Samozino, P. (2016). Interpreting power-force-velocity profiles for individualized and specific training. International Journal of Sports Physiology and Performance, 11(2), 267-272.",
                "degiskenler": ["F₀ (N)", "v₀ (m/s)", "Pmax (W)", "F-V Eğimi", "Test Egzersizi"]
            },
            "Nordic Hamstring Kuvvet Testi — Genel (NHT)": {
                "protokol": """
**Amaç:** Tüm branşlarda hamstring kaslarının eksantrik kuvvetini ve bacaklar arası asimetriyi ölçmektir — hamstring yaralanma riskinin en önemli nesnel göstergesi.

**Ekipman:** NordBord kuvvet ölçer veya izokinetik dinamometre (standart) / partner + düz zemin (saha versiyonu).

**Uygulama — Standart (NordBord):**
1. Sporcu diz üstü pozisyonda, bacaklar cihaza sabitlenir.
2. Eller göğüste çaprazlanmış, gövde öne doğru kontrollü indirilir.
3. Her bacak ayrı ayrı test edilir; 3 tekrar, en yüksek değer alınır.

**Uygulama — Saha (Partner):**
1. Sporcu diz üstü, partner ayak bileklerini sabit tutar.
2. Gövde mümkün olduğunca yavaş ve kontrollü öne düşürülür.
3. Kontrol kalitesi 1-5 arası puanlanır.

**Skorlama:**
- Pik kuvvet (N) ve relatif kuvvet (N/kg) — her bacak
- Asimetri İndeksi (%) = (Güçlü − Zayıf) / Güçlü × 100
- Saha versiyonu: Kontrol süresi (sn) + kalite puanı (1-5)

**Normatif ve Klinik Eşikler:**
- Asimetri < %10 = Simetrik
- Asimetri %10-15 = Dikkat: takip önerilir
- Asimetri > %15 = Yüksek yaralanma riski, müdahale gerekli

**Not:** Nordic Hamstring egzersizini içeren programlar hamstring yaralanma sıklığını %50'ye kadar azaltmaktadır (Al Attar et al., Sports Medicine, 2017).
                """,
                "kaynak": "Al Attar, W. S. A. et al. (2017). Effect of injury prevention programs that include the Nordic hamstring exercise on hamstring injury rates in soccer players. Sports Medicine, 47(5), 907-916.\nEkstrand, J., Hägglund, M., & Waldén, M. (2011). Epidemiology of muscle injuries in professional football. American Journal of Sports Medicine, 39(6), 1226-1232.\nKorhonen, R. K. et al. (2022). Reliability and validity of the NordBord for hamstring muscle strength assessment. Journal of Strength and Conditioning Research, 36(4), 934-940.",
                "degiskenler": ["Sağ Bacak Pik Kuvveti (N)", "Sol Bacak Pik Kuvveti (N)", "Sağ Bacak (N/kg)", "Sol Bacak (N/kg)"]
            },
            "EMG Tabanlı Kas Aktivasyonu": {
                "protokol": """
**Amaç:** Yüzey elektromiyografi (EMG) ile kasın elektriksel aktivasyon düzeyini ölçerek nöromüsküler koordinasyon ve kas yorgunluğunu değerlendirmektir.

**Ekipman:** Yüzey EMG sistemi (Delsys, Noraxon, BTS vb.), elektrotlar, iletken jel.

**Uygulama:**
1. Deri hazırlama: tıraş, zımpara ile temizleme, alkol silinmesi.
2. Elektrotlar kas gövdesi üzerine motor nokta yönünde yapıştırılır.
3. MVC (maksimal istemli kasılma) referans ölçümü alınır.
4. Test hareketi sırasında EMG kaydedilir.

**Skorlama:**
- RMS (Root Mean Square, µV veya %MVC) — aktivasyon şiddeti
- MPF (Ortalama Güç Frekansı, Hz) — yorgunluk göstergesi
- Aktivasyon başlangıç zamanı (onset, ms)
- Co-activation oranı (%)
                """,
                "kaynak": "Merletti, R., & Farina, D. (2016). Surface Electromyography: Physiology, Engineering and Applications. Wiley-IEEE Press.\nHermens, H. J. et al. (2000). Development of recommendations for SEMG sensors and sensor placement procedures. Journal of Electromyography and Kinesiology, 10(5), 361-374.",
                "degiskenler": ["Test Kası", "MVC (µV)", "RMS Egzersiz (µV)", "MPF (Hz)", "Aktivasyon Oranı (%MVC)"]
            },
            "Rate of Force Development (RFD) Ölçümü": {
                "protokol": """
**Amaç:** Kuvvetin ne kadar hızlı üretildiğini ölçmektir — sporda patlayıcı performansın kritik belirleyicisidir.

**Ekipman:** Kuvvet platformu (force plate), bilgisayar ve veri kayıt yazılımı.

**Uygulama:**
1. Sporcu kuvvet platformu üzerinde izometrik mid-thigh pull (IMTP) veya izometrik squat pozisyonu alır.
2. "Hazır-Git" komutuyla mümkün olduğunca hızlı maksimal kuvvet üretir.
3. 3-5 deneme; en iyi 3 değer analiz edilir.

**Skorlama:**
- Pik Kuvvet (N ve N/kg)
- RFD 0-50ms, 0-100ms, 0-200ms (N/s)
- Zirveye Ulaşma Süresi (ms)

**Not:** RFD 0-50ms güreş, judo, sprint gibi patlayıcı branşlarda en güçlü performans tahmincisidir.
                """,
                "kaynak": "Aagaard, P. et al. (2002). Increased rate of force development and neural drive of human skeletal muscle following resistance training. Journal of Applied Physiology, 93(4), 1318-1326.\nHaff, G. G. et al. (2015). Force-time curve characteristics of dynamic and isometric muscle actions. Journal of Strength and Conditioning Research, 19(4), 741-748.",
                "degiskenler": ["Pik Kuvvet (N)", "Pik Kuvvet (N/kg)", "RFD 0-50ms (N/s)", "RFD 0-100ms (N/s)", "RFD 0-200ms (N/s)", "Zirveye Ulaşma (ms)"]
            },
            "Dikey Sıçrama (CMJ)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü ölçmek.

**Ekipman:** Sıçrama platformu (force plate) veya Vertec / uygulama tabanlı ölçüm sistemi.

**Uygulama:**
1. Sporcu ayaklar omuz genişliğinde, eller kalçada dik durur.
2. Serbest ön-çömelme (countermovement) ile maksimal dikey sıçrama yapılır.
3. İniş sırasında dizler hafif bükülü olmalı, sert iniş yapılmamalı.
4. 3 deneme yapılır, en iyi değer kaydedilir; denemeler arası 30 sn dinlenme.

**Skorlama:** Sıçrama yüksekliği (cm).

**Normatif (Elit Erkek):** > 55 cm = Mükemmel; > 45 cm = İyi
                """,
                "kaynak": "Bosco, C., Luhtanen, P., & Komi, P. V. (1983). A simple method for measurement of mechanical power in jumping. European Journal of Applied Physiology, 50(2), 273-282.",
                "degiskenler": ["Deneme 1 (cm)", "Deneme 2 (cm)", "Deneme 3 (cm)"]
            },
            "Dikey Sıçrama Tam Batarya (CMJ + SJ + DJ)": {
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı güç profilini üç farklı sıçrama tipiyle kapsamlı değerlendirmek — reaktif kuvvet ve elastik enerji kullanımı hakkında bilgi verir.

**Ekipman:** Force plate veya Vertec, 30 cm yükseklik (DJ için).

**Uygulama:**

**A) CMJ (Countermovement Jump — Ön-Çömelme Sıçraması):**
1. Eller kalçada, dik duruş.
2. Serbest ön-çömelme ile maksimal sıçrama.
3. 3 deneme, en iyi değer (cm).

**B) SJ (Squat Jump — Statik Sıçrama):**
1. 90° diz açısında statik çömelme, 2 sn bekleme.
2. Ön-çömelme olmadan maksimal sıçrama.
3. 3 deneme, en iyi değer (cm).

**C) DJ (Drop Jump — Derinlik Sıçraması):**
1. 30 cm yüksekten inişin ardından minimal temas süresiyle maksimal sıçrama.
2. Eklem açısı minimal, zemin teması mümkün olduğunca kısa.
3. 3 deneme, en iyi değer (cm) ve temas süresi (ms).

**Skorlama:**
- CMJ, SJ, DJ yükseklikleri (cm)
- CMJ − SJ farkı: elastik enerji kullanımı göstergesi
- Reaktif Kuvvet İndeksi (RKİ) = DJ yüksekliği / Temas süresi

**Normatif (Elit Erkek):** CMJ > 55 cm, SJ > 50 cm = Mükemmel
                """,
                "kaynak": "Bosco, C., Luhtanen, P., & Komi, P. V. (1983). European Journal of Applied Physiology, 50(2), 273-282.\nMarkovic, G. (2007). Does plyometric training improve vertical jump height? British Journal of Sports Medicine, 41(6), 349-355.",
                "degiskenler": ["CMJ Deneme 1 (cm)", "CMJ Deneme 2 (cm)", "CMJ Deneme 3 (cm)", "SJ Deneme 1 (cm)", "SJ Deneme 2 (cm)", "SJ Deneme 3 (cm)", "DJ Deneme 1 (cm)", "DJ Temas Süresi (ms)"]
            },
            "Sargent Dikey Sıçrama Testi (Duvar)": {          # Paket 35c: ekipmansız (duvar + tebeşir)
                "protokol": """
**Amaç:** Alt ekstremite patlayıcı gücünü ekipmansız ölçmektir.

**Ekipman:** Duvar (ya da işaretli levha), tebeşir tozu (ya da ele sürülecek krem/tebeşir), ölçü bandı.

**Uygulama:**
1. Isınma yapılır. Sporcu parmak uçlarını tebeşirler.
2. Duvara yan durur, duvara yakın kolu yukarı uzatır, iki ayak yerde düz; parmak ucu duvara işaretlenir (ayakta erişim).
3. Duvardan hafif uzaklaşır; kolları ve bacaklarını kullanarak olabildiğince yükseğe sıçrar ve zirvede duvara dokunup iz bırakır. Hazırlık çömelmesi (countermovement) serbesttir.
4. Üç deneme yapılır; en yüksek iz kaydedilir.

**Skorlama:** Sıçrama erişimi − ayakta erişim (cm); üç denemenin en iyisi. Sıçrama yüksekliği otomatik hesaplanır; ayrıca girilmez.

**Not:** Kollar ve hazırlık çömelmesi serbesttir; sonuç "eller belde" CMJ ile ve TSYT sıçrama matı ölçümüyle karşılaştırılmaz. TSYT'nin 7-11 yaş sıçrama normları mat ölçümüne aittir, bu teste uygulanmaz. Ölçüm hatası parmak ucu işaretleme ve zirvede dokunma yeteneğine bağlıdır.

**Örneklem karşılaştırması (Kademe 2 — yüzdelik norm değil):** Sıçrama yüksekliği, Morassutti ve ark. (2025) örnekleminin ortalaması ± SD değeriyle yan yana gösterilir; kategori ya da yüzdelik verilmez. Erkek 53 ± 14 cm (n=422), kadın 37 ± 11 cm (n=538); 20-29 yaş Kanadalı üniversite öğrencisi, karma atletik düzey (nicelleştirilmemiş), 2010-2019. Kaynak protokol: 1,27 m duvar skalası, alt uç yerden 1,91 m; baskın el ve yan duruş; tek kol savurma + tek hazırlık çömelmesi (ek karşı hareket yok); 3 deneme, en iyisi; ayakkabılı. Protokolümüz kolları ve çömelmeyi serbest bırakıyorsa değerler kaynakla birebir karşılaştırılamaz; elit/branşa özgü norm değildir. Karşılaştırma yalnız 20-29 yaşta gösterilir.
                """,
                "kaynak": "Sargent, D. A. (1921). The physical test of a man. American Physical Education Review, 26, 188-194.\nMorassutti, O. N., van Wyk, P. M., & Duquette, A. M. (2025). Vertical jumping power normative-reference values: Utilizing a large cohort of Canadian university students. Biomedical Human Kinetics, 17, 147-157. https://doi.org/10.2478/bhk-2025-0014 (örneklem karşılaştırması)",
                "degiskenler": ["Ayakta Erişim (cm)", "Sıçrama Erişimi — Deneme 1 (cm)", "Sıçrama Erişimi — Deneme 2 (cm)",
                                "Sıçrama Erişimi — Deneme 3 (cm)"]
            },
            "30m Sprint": {
                "protokol": """
**Amaç:** Maksimal koşu hızını ölçmek.

**Uygulama:** Durarak başlangıç, 30m düz pist, 3 deneme (3-5 dk dinlenme aralarında).

**Normatif (Elit Erkek):** <3.80 sn = Mükemmel
                """,
                "kaynak": "Mackala, K., & Mero, A. (2013). A kinematic analysis of three best 100m performances ever. Journal of Human Kinetics, 36, 149–160.",
                "degiskenler": ["Deneme 1 (sn)", "Deneme 2 (sn)", "Deneme 3 (sn)"]
            }
        },
        "Antropometri ve Vücut Kompozisyonu": {
            "_kunye": {"yas_araligi": None},          # hedef_yas metni yok (Paket 32)
            "DEXA (Dual-Energy X-ray Absorptiometry)": {
                "protokol": """
**Amaç:** Vücut kompozisyonunu (yağ kütlesi, yağsız kütle, kemik mineral yoğunluğu) bölgesel ve total olarak hassas biçimde ölçmektir — referans standart.

**Ekipman:** DEXA tarayıcı (Hologic, GE Lunar vb.).

**Uygulama:**
1. Sporcu en az 2 saat aç, yoğun egzersiz yapmamış.
2. Metal içermeyen giysilerle cihaza yatar.
3. Tarama süresi yaklaşık 10-15 dakika.
4. Cihaz düşük doz X-ray ile iki farklı enerji düzeyinde tarama yapar.

**Skorlama:**
- Toplam vücut yağ yüzdesi (%)
- Yağ kütlesi (kg)
- Yağsız kütle / LBM (kg)
- Kemik mineral yoğunluğu / BMD (g/cm²)
- Bölgesel analiz (kollar, bacaklar, gövde)

**Not:** RED-S ve kemik sağlığı takibinde klinik referans standarttır.
                """,
                "kaynak": "Nana, A. et al. (2015). Methodology review: using dual-energy X-ray absorptiometry (DXA) for the assessment of body composition in athletes. International Journal of Sport Nutrition and Exercise Metabolism, 25(2), 198-215.\nMoon, J. R. (2013). Body composition in athletes and sports nutrition. Proceedings of the Nutrition Society, 72(3), 325-333.",
                "degiskenler": ["Vücut Yağ (%)", "Yağ Kütlesi (kg)", "Yağsız Kütle (kg)", "BMD (g/cm²)", "Tarama Tarihi"]
            },
            "Biyoelektrik İmpedans Analizi (BIA)": {
                "protokol": """
**Amaç:** Vücuttan geçirilen düşük düzeyli elektrik akımına karşı direnci ölçerek vücut kompozisyonunu tahmin etmektir.

**Ekipman:** BIA cihazı (InBody, Tanita, Seca vb.).

**Uygulama:**
1. Ölçüm koşulları: sabah aç karnına, idrar sonrası, egzersiz yapılmamış, hidrasyon normal.
2. Sporcu cihaza çıplak ayak (ve elle tutma) temas ederek pozisyon alır.

**Ölçüm Öncesi Dikkat:**
- 4 saat öncesinde yemek yememek
- 24 saat öncesinde alkol tüketmemek
- 12 saat öncesinde yoğun egzersiz yapmamak

**Skorlama:**
- Vücut yağ yüzdesi (%)
- Yağsız vücut kütlesi (kg)
- Toplam vücut suyu (L)
- Segmental kas kütlesi (kol, bacak, gövde)
- Bazal metabolizma hızı (kcal)
                """,
                "kaynak": "Kyle, U. G. et al. (2004). Bioelectrical impedance analysis — part I: review of principles and methods. Clinical Nutrition, 23(5), 1226-1243.\nMalina, R. M. (2007). Body composition in athletes: assessment and estimated fatness. Clinics in Sports Medicine, 26(1), 37-68.",
                "degiskenler": ["Vücut Yağ (%)", "Yağsız Kütle (kg)", "Toplam Vücut Suyu (L)", "BMH (kcal)", "Cihaz Modeli"]
            },
            "Hidrostatik Tartım (Su Altı Tartımı)": {
                "protokol": """
**Amaç:** Arşimet ilkesine dayalı su yer değiştirme yöntemiyle vücut yoğunluğunu ölçmek ve yağ yüzdesini tahmin etmektir.

**Ekipman:** Su tartım tankı, sualtı tartı, spirometre (rezidüel volüm için).

**Uygulama:**
1. Sporcu suya girer ve tartım koltuğuna oturur.
2. Tam ekspirasyon sonrası suya tamamen dalar.
3. Sualtı ağırlığı ölçülür; rezidüel akciğer volümü (RV) ölçülür veya tahmin edilir.
4. 3-10 deneme; en yüksek 3 değerin ortalaması alınır.

**Formül:**
- Vücut Yoğunluğu = Kara ağırlığı / [(Kara − Sualtı) / Su yoğunluğu − RV]
- % Yağ = (4.95 / Yoğunluk − 4.50) × 100 (Siri formülü; ör. yoğunluk 1.060 g/ml → %17.0)

**Not:** Günümüzde büyük ölçüde DEXA ile ikame edilmiş; araştırma altın standardı olmayı sürdürüyor.
                """,
                "kaynak": "Brozek, J. et al. (1963). Densitometric analysis of body composition. Annals of the New York Academy of Sciences, 110, 113-140.\nSiri, W. E. (1956). The gross composition of the body. Advances in Biological and Medical Physics, 4, 239-280.\nNot: 1956 bölümü iki bileşenli yoğunluk yaklaşımını ve üç bileşenli formülü (yoğunluk + vücut suyu) içerir; yaygın kullanılan 4.95/D − 4.50 hali Siri (1961), Techniques for Measuring Body Composition (Brožek & Henschel, ed.) bölümüne atfedilir, o metin görülmedi.",
                "degiskenler": ["Kara Ağırlığı (kg)", "Sualtı Ağırlığı (kg)", "Rezidüel Volüm (L)", "Vücut Yoğunluğu (g/ml)", "Yağ % (Siri)"]
            }
        },
        # Paket 35: tek başına seçilebilen kuvvet testleri (önceden yalnız NFL/Rugby/NHL ve çocuk bataryalarının değişkeniydi)
        "Maksimal Kuvvet ve Kas Dayanıklılığı": {
            "_kunye": {"yas_araligi": None},          # batarya değil; yaş aralığı rafa değil teste/örnekleme bağlı
            "1RM Bench Press": {
                "protokol": """
**Amaç:** Serbest ağırlıkla bench press'te tek tekrarda kaldırılabilen en yüksek yükü (1RM) belirlemektir.

**Ön koşul (teknik yetkinlik):** Test yalnız hareketi antrenmanında doğru teknikle düzenli uygulayan sporcuya yapılır. Teknik yetkinliği yetersiz sporcuda 1RM denemesi yapılmaz.

**Ekipman:** Olimpik bar, plakalar, kilit (klips), bench press sehpası, tartı.

**Güvenlik:** Kademeli ısınma setleri zorunludur. Spotçu zorunludur: deneyimli bir spotçu her denemede barın başında
hazır bulunur; sporcu ile spotçu denemeden önce işaretlerde anlaşır. Plakalar kilitle sabitlenir.

**Uygulama:**
1. Beş temas noktası: baş, üst sırt ve kalça sehpada; iki ayak yere düz basar. Kapalı, avuçlar öne bakan (pronasyon) kavrayış; eller barda eşit aralıklı. Açık (başparmaksız) kavrayışa izin verilmez.
2. Her denemede bar göğse indirilir ve kollar tam açılana dek itilir.
3. Isınma: kolayca 5-10 tekrar yapılabilen hafif yükle bir set.
4. 1 dk dinlenme; yük 4-9 kg (ya da %5-10) artırılır, 3-5 tekrar.
5. 2 dk dinlenme; aynı artışla 2-3 tekrar.
6. 2-4 dk dinlenme; aynı artışla 1RM denemesi.
7. Deneme başarılıysa 2-4 dk dinlenme, yük artırılarak yeni deneme; başarısızsa 2-4 dk dinlenme, yük 2-4 kg (ya da %2,5-5) azaltılarak yeni deneme.
8. 1RM'ye 3-5 deneme içinde ulaşılması hedeflenir.

**Skorlama:** Tam hareket açıklığında başarıyla kaldırılan en yüksek yük (kg). Rölatif değer (kg/kg) sporcunun kayıtlı vücut ağırlığından otomatik hesaplanır; ayrıca girilmez.

**Örneklem karşılaştırması (Kademe 2 — yüzdelik norm değil):** Rölatif değer, Aydos ve ark. (2004)
örnekleminin branş ortalaması ± SD değeriyle yan yana gösterilir; kategori ya da yüzdelik verilmez. Örneklem: n=77 erkek,
18-30 yaş, üniversite kulüp sporcusu (milli takım değil); branş başına n=10-15; 2004. Bu çalışma standart 1RM protokolü
tarif etmez: sporcunun kaldırdığı "maksimal ağırlık" kaydedilmiş, ısınma 10 dakika hafif ağırlıklarla yapılmıştır;
bench press sırtüstü yatar vaziyette çift elle ağırlık takılı halter barını presleyerek uygulanmıştır. Karşılaştırma yalnız 18 yaş ve üstü erkek sporcuda gösterilir; kadında ve 18 yaş altında referans yoktur.

**Bilgi notu (değerlendirmede kullanılmaz):** Elit Türk milli boksör ve kickboksçularda standart 1RM protokolüyle (Baechle & Earle) Smith makinesinde ölçülen rölatif bench press: boks 1,44 ± 0,19 (n=7), kickboks 1,31 ± 0,14 (n=6). Kaynak: Can İ, Bayrakdaroğlu S (2019), CBÜ Beden Eğitimi ve Spor Bilimleri Dergisi, 14(1), 121-128.
                """,
                "kaynak": 'Baechle, T. R., & Earle, R. W. (Eds.). (2008). Essentials of Strength Training and Conditioning (3rd ed.). Human Kinetics.\nNot: 1RM adımları NSCA protokolünün Human Kinetics yayımı özetiyle (Szymanski & Vazquez, Strength Training for Baseball) karşılaştırıldı; kitabın kendisi görülmedi. Can ve Bayrakdaroğlu (2019) 1RM için aynı kitabı kaynak gösterir.\nAydos, L., Pepe, H., & Karakuş, H. (2004). Bazı takım ve ferdi sporlarda rölatif kuvvet değerlerinin araştırılması. Gazi Üniversitesi Kırşehir Eğitim Fakültesi Dergisi, 5(2), 305-315. (örneklem karşılaştırması)\nCan, İ., & Bayrakdaroğlu, S. (2019). Türk milli boksör ve kickbokscularda üst vücut kuvvet özelliği ve bench throw hareketi esnasındaki bazı parametrelerin karşılaştırılması. CBÜ Beden Eğitimi ve Spor Bilimleri Dergisi, 14(1), 121-128. (yalnız protokol bilgi notu; Smith makinesi — serbest ağırlıkla karşılaştırılmaz)',
                "degiskenler": ["1RM Bench Press (kg)"]
            },
            "1RM Squat (Arka Çömelme)": {
                "protokol": """
**Amaç:** Serbest ağırlıkla arka çömelmede (back squat) tek tekrarda kaldırılabilen en yüksek yükü (1RM) belirlemektir.

**Ön koşul (teknik yetkinlik):** Test yalnız hareketi antrenmanında doğru teknikle düzenli uygulayan sporcuya yapılır. Teknik yetkinliği yetersiz sporcuda 1RM denemesi yapılmaz.

**Ekipman:** Olimpik bar, plakalar, kilit (klips), güvenlik demirli squat sehpası (kafes), tartı.

**Güvenlik:** Kademeli ısınma setleri zorunludur. Spotçu zorunludur: en az bir deneyimli spotçu sporcunun arkasında
hazır bulunur; güvenlik demirleri çömelişin en alt noktasının hemen altına ayarlanır. Plakalar kilitle sabitlenir.

**Uygulama:**
1. Bar üst sırtta (omuzların arkasında), kapalı kavrayış; ayaklar yaklaşık omuz genişliğinde.
2. Derinlik: diz açısı 90°'yi geçene kadar çömelinir, dik duruşa dönülür. Derinlik her denemede aynı tutulur; derinliğe inilmeyen tekrar sayılmaz.
3. Isınma: kolayca 5-10 tekrar yapılabilen hafif yükle bir set.
4. 1 dk dinlenme; yük artırılarak 3-5 tekrar (alt ekstremitede artış üst ekstremiteden büyüktür, yaklaşık %10-20).
5. 2 dk dinlenme; yük artırılarak 2-3 tekrar.
6. 2-4 dk dinlenme; 1RM denemesi.
7. Deneme başarılıysa 2-4 dk dinlenme, yük artırılarak yeni deneme; başarısızsa 2-4 dk dinlenme, yük azaltılarak yeni deneme.
8. 1RM'ye 3-5 deneme içinde ulaşılması hedeflenir.

**Skorlama:** Belirtilen derinlikte başarıyla kaldırılan en yüksek yük (kg). Rölatif değer (kg/kg) sporcunun kayıtlı vücut ağırlığından otomatik hesaplanır; ayrıca girilmez.

**Örneklem karşılaştırması (Kademe 2 — yüzdelik norm değil):** Rölatif değer, Aydos ve ark. (2004)
örnekleminin branş ortalaması ± SD değeriyle yan yana gösterilir; kategori ya da yüzdelik verilmez. Örneklem: n=77 erkek,
18-30 yaş, üniversite kulüp sporcusu (milli takım değil); branş başına n=10-15; 2004. Bu çalışma standart 1RM protokolü
tarif etmez: sporcunun kaldırdığı "maksimal ağırlık" kaydedilmiş, ısınma 10 dakika hafif ağırlıklarla yapılmıştır;
squat diz eklemi 90°'yi geçecek şekilde yere oturup kalkarak (diz açısı 90°'yi geçene kadar) uygulanmıştır. Karşılaştırma yalnız 18 yaş ve üstü erkek sporcuda gösterilir; kadında ve 18 yaş altında referans yoktur.
                """,
                "kaynak": 'Baechle, T. R., & Earle, R. W. (Eds.). (2008). Essentials of Strength Training and Conditioning (3rd ed.). Human Kinetics.\nNot: 1RM adımları NSCA protokolünün Human Kinetics yayımı özetiyle (Szymanski & Vazquez, Strength Training for Baseball) karşılaştırıldı; kitabın kendisi görülmedi. Can ve Bayrakdaroğlu (2019) 1RM için aynı kitabı kaynak gösterir.\nAydos, L., Pepe, H., & Karakuş, H. (2004). Bazı takım ve ferdi sporlarda rölatif kuvvet değerlerinin araştırılması. Gazi Üniversitesi Kırşehir Eğitim Fakültesi Dergisi, 5(2), 305-315. (örneklem karşılaştırması)',
                "degiskenler": ["1RM Squat (kg)"]
            },
            "1RM Leg Press": {
                "protokol": """
**Amaç:** Leg press makinesinde tek tekrarda itilebilen en yüksek yükü (1RM) belirlemektir.

**Ön koşul (teknik yetkinlik):** Test yalnız hareketi antrenmanında doğru teknikle düzenli uygulayan sporcuya yapılır. Teknik yetkinliği yetersiz sporcuda 1RM denemesi yapılmaz.

**Ekipman:** Leg press makinesi (tipi kayda geçer: kızaklı açılı ya da yatay), plakalar, tartı.

**Güvenlik:** Kademeli ısınma setleri zorunludur. Spotçu zorunludur: spotçu makinenin güvenlik kilitlerine erişebilecek
konumda bulunur. Dizler itişin sonunda kilitlenmez.

**Uygulama:**
1. Sırt ve kalça minderde, ayaklar platformda yaklaşık kalça genişliğinde; ayak yeri ve hareket açıklığı (inişteki diz açısı) test öncesi belirlenip kaydedilir, her denemede aynı tutulur.
2. Güvenlik kilitleri açılır; platform belirlenen derinliğe indirilir ve bacaklar açılana dek itilir.
3. Isınma: kolayca 5-10 tekrar yapılabilen hafif yükle bir set.
4. 1 dk dinlenme; yük artırılarak 3-5 tekrar (alt ekstremitede artış üst ekstremiteden büyüktür, yaklaşık %10-20).
5. 2 dk dinlenme; yük artırılarak 2-3 tekrar.
6. 2-4 dk dinlenme; 1RM denemesi.
7. Deneme başarılıysa 2-4 dk dinlenme, yük artırılarak yeni deneme; başarısızsa 2-4 dk dinlenme, yük azaltılarak yeni deneme.
8. 1RM'ye 3-5 deneme içinde ulaşılması hedeflenir.

**Skorlama:** Belirlenen hareket açıklığında başarıyla itilen en yüksek yük (kg). Rölatif değer (kg/kg) sporcunun kayıtlı vücut ağırlığından otomatik hesaplanır. Makine tipleri arasında yük karşılaştırılmaz; sporcu aynı makinede izlenir.

**Norm:** Bu test için doğrulanmış norm bulunmamaktadır.
                """,
                "kaynak": 'Baechle, T. R., & Earle, R. W. (Eds.). (2008). Essentials of Strength Training and Conditioning (3rd ed.). Human Kinetics.\nNot: 1RM adımları NSCA protokolünün Human Kinetics yayımı özetiyle (Szymanski & Vazquez, Strength Training for Baseball) karşılaştırıldı; kitabın kendisi görülmedi. Can ve Bayrakdaroğlu (2019) 1RM için aynı kitabı kaynak gösterir.\nNorm kaynağı yok (açık erişimli doğrulanmış norm bulunamadı).',
                "degiskenler": ["1RM Leg Press (kg)"]
            },
            "Barfiks (Pull-Up) — Maksimum Tekrar (Genel)": {
                "protokol": """
**Amaç:** Üst ekstremite çekiş kas dayanıklılığını, vücut ağırlığıyla yapılan tam barfiks tekrar sayısıyla değerlendirmektir.

**Ekipman:** Sporcu asılıyken ayakları yere değmeyecek yükseklikte yatay bar.

**Uygulama:**
1. Avuçlar öne bakar (pronasyon), eller yaklaşık omuz genişliğinde; kollar tam açık asılı başlanır.
2. Çene barın üstüne çıkana kadar çekilir, kollar tam açılana dek inilir.
3. Sallanma, bacakla tekme ya da kalça hamlesi yapılmaz.
4. Tekrar kurala uygun yapılamadığında test biter.

**Skorlama:** Doğru formda tamamlanan tam tekrar sayısı.

**Yorum:** Barfiks tekrar sayısı vücut ağırlığına bağımlıdır; sıklet sporlarında mutlak tekrar yerine zaman içindeki değişim yorumlanmalıdır.

**Norm:** Bu test için doğrulanmış norm bulunmamaktadır.
                """,
                "kaynak": ("Norm kaynağı yok (açık erişimli doğrulanmış norm bulunamadı). Hareket tanımı sahada yaygın tam "
                           "barfiks tanımıdır; dayandığı yayımlanmış protokol metni bu pakette doğrulanmadı."),
                "degiskenler": ["Barfiks (tekrar)"]
            },
            "Şınav (Push-Up) — Maksimum Tekrar (Genel)": {
                "protokol": """
**Amaç:** Üst ekstremite itiş kas dayanıklılığını, ara vermeden yapılan şınav tekrar sayısıyla değerlendirmektir.

**Ekipman:** Mat.

**Uygulama:**
1. Standart şınav pozisyonu: eller omuz altında, gövde baştan topuğa düz çizgi; destek ayak uçlarıdır.
2. Alt noktada dirsek 90°'ye bükülür, üstte kollar tam açılır.
3. Metronom kullanılmaz; tekrarlar ara vermeden yapılır.
4. Gövde düzlüğü bozulduğunda ya da tekrar tamamlanamadığında test biter.

**Skorlama:** Doğru formda tamamlanan tekrar sayısı. Diz üstü pozisyon kullanıldıysa notlara yazılır (aynı sporcunun ölçümleri aynı pozisyonla karşılaştırılır).

**Norm:** Bu test için doğrulanmış norm bulunmamaktadır.
                """,
                "kaynak": ("Plowman, S. A., & Meredith, M. D. (2013). FitnessGram/ActivityGram Reference Guide (4th ed.). "
                           "The Cooper Institute. (yalnız hareket tanımı: 90° şınav; metronom temposu ve çocuk/genç HFZ "
                           "eşikleri bu genel testte kullanılmaz)\nNorm kaynağı yok (açık erişimli doğrulanmış norm bulunamadı)."),
                "degiskenler": ["Şınav (tekrar)"]
            },
            "Mekik (Sit-Up) — 1 Dakika (Genel)": {
                "protokol": """
**Amaç:** Karın kas dayanıklılığını 1 dakikada yapılan mekik tekrar sayısıyla değerlendirmektir.

**Ekipman:** Mat, kronometre.

**Uygulama:**
1. Sırtüstü yatılır; dizler 90° bükülü, eller ense arkasında kenetli, ayaklar bir yardımcı tarafından sabitlenir.
2. Gövde dizlere doğru kalkar ve sırt yere değene kadar iner; bu bir tekrardır.
3. Süre 1 dakikadır; kurala uymayan tekrar sayılmaz.

**Skorlama:** 1 dakikada tamamlanan doğru tekrar sayısı.

**Norm:** Bu test için doğrulanmış norm bulunmamaktadır.
                """,
                "kaynak": ("Council of Europe (1988). Eurofit: Handbook for the Eurofit tests of physical fitness. Rome. "
                           "(hareket tanımı: dizler 90°, eller ense arkasında; Eurofit'te süre 30 sn)\nChina National "
                           "Student Physical Health Standard (2014). Ministry of Education of the People's Republic of China. "
                           "(süre: 1 dakika)\nNorm kaynağı yok (açık erişimli doğrulanmış norm bulunamadı)."),
                "degiskenler": ["Mekik (tekrar)"]
            }
        }
    }
}
