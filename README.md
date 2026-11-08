# PerformTest — Biyomekanik Atletik Performans & Yetenek Seçimi Platformu

PerformTest, çocuk ve genç sporcuların antropometrik ölçümleri ile 196 farklı fiziksel uygunluk ve motorik test sonuçlarını bilimsel normlar (LMS, Z-Skoru, Persentil) ışığında değerlendiren, çok değişkenli branş yatkınlık modelleri (Opstoel ve ark.) üreten, yerli sunucu (on-premise) ve KVKK uyumlu tam yığın (full-stack) performans analiz platformudur.

---

## 🏛️ Mimari Katmanlar

```
PerformTest/
├── Olcut/
│   ├── api/                   # Python / Flask REST API (JWT, RBAC, KVKK Audit Log)
│   │   ├── core/              # Güvenlik, JWT, HTTP yardımcıları
│   │   ├── db/                # Çoklu kulüp (multi-tenant) ilişkisel veritabanı motoru
│   │   ├── models/            # Domain ve DTO modelleri
│   │   ├── routers/           # Auth, Sporcular, Katalog, Mobil, Admin rotaları
│   │   └── services/          # OlcutMotorServisi & Biyomekanik SVG Sahne Motoru
│   ├── frontend/              # Next.js 14 Web Uygulaması & Admin Paneli
│   │   ├── src/app/           # Next.js App Router (Studio & Admin)
│   │   ├── src/components/    # Modüler UI bileşenleri (SporcuAnaliz, SahaOlcum, Karsilastirma, Katalog, Admin)
│   │   └── src/lib/           # Merkezi tipli REST API istemcisi
│   ├── mobile/                # Saha Çevrimdışı (Offline-First) Senkronizasyon Servisi
│   ├── infra/                 # Docker Compose, Nginx, PostgreSQL, Redis konfigürasyonları
│   ├── olcut/                 # Çekirdek bilimsel norm, analiz ve raporlama motoru
│   ├── veri/                  # Ulusal normatif veri havuzları ve test katalogları
│   ├── tests/                 # Otomatik mimari, API ve geriye dönük regresyon testleri
│   └── baslat.bat             # Geliştirme/Dağıtım tek tık başlatıcısı
```

---

## 🚀 Hızlı Başlangıç (Lokal Geliştirme)

### Gereksinimler
- **Python**: 3.11 veya üzeri (Önerilen: Python 3.14)
- **Node.js**: v18 veya üzeri (Önerilen: v20 / v24)
- **Paket Yöneticisi**: `npm`

### 1. Tek Tıkla Başlatma (Windows)
Proje kök dizinindeki `baslat.bat` dosyasını çift tıklatarak veya terminalden çalıştırarak hem Python API'yi hem Next.js Web uygulamasını aynı anda başlatabilirsiniz:
```cmd
baslat.bat
```

### 2. Manuel Başlatma

#### Backend REST API:
```bash
cd Olcut
py -3.14 -m api.main
```
> API Dinleme Adresi: `http://localhost:8000`  
> Sağlık Kontrolü: `http://localhost:8000/api/v1/health`

#### Next.js Web Frontend:
```bash
cd Olcut/frontend
npm install
npm run build
npm run start
```
> Web Uygulaması & Admin Studio: `http://localhost:3000`

---

## 🐳 Üretim Dağıtımı (Docker & On-Premise)

KVKK uyumu gereği tüm veriler kurum içi sunucuda izole olarak tutulur:
```bash
cd Olcut/infra
docker compose up --build -d
```

Konteyner Dağılımı:
- **Nginx (Port 80)**: Tek giriş kapısı; `/api/` isteklerini API'ye, diğer istekleri Next.js frontend'e yönlendirir.
- **Next.js Frontend (Port 3000)**: Server-side rendering ve modern kullanıcı arayüzü.
- **Python API (Port 8000)**: Bilimsel norm hesaplama ve veri yönetişimi.
- **PostgreSQL 16 (Port 5432)**: İlişkisel ve çok-kulüplü veri depolama.
- **Redis 7 (Port 6379)**: Önbellek ve oturum yönetimi.

---

## 🔐 Kullanıcı Rolleri & Hızlı Giriş Hesapları

| Rol | E-Posta | Parola | Yetkiler |
|---|---|---|---|
| **Süper Admin** | `admin@performtest.yerli` | `Admin123!` | Tüm kulüpleri yönetme, DB yedeği, kullanıcı yetkilendirme, KVKK kimlik anonimleştirme |
| **Kulüp Yöneticisi** | `kulup-a@performtest.yerli` | `Kulup123!` | Kulüp sporcularını yönetme, A4 kulüp raporu, veri dışa aktarma |
| **Ölçüm Antrenörü** | `antrenor@performtest.yerli` | `Koc123!` | Saha ölçüm oturumu girişi, sporcu analiz karneleri, kıyaslama laboratuvarı |
| **Sporcu Velisi** | `veli@performtest.yerli` | `Veli123!` | Yalnızca kendi sporcusunun gelişim karnesini ve veli raporunu görüntüleme |

---

## 🧪 Otomatik Testler

Tüm mimari, API, RBAC ve görsel motor testlerini çalıştırmak için:
```bash
cd Olcut
py -3.14 -m pytest tests/test_01_mimari_ve_sozdizimi.py tests/test_08_api_ve_admin.py -v
```
