"""
PerformTest Studio — Web Uygulaması (`/`) ve Yönetim / Admin Merkezi (`/admin`).

Özellikler:
- PerformTest kurumsal kimliği, Açık / Koyu (Light / Dark) tema desteği
- 5 çalışma alanı:
  1. Sporcu Performans Merkezi (Z-Profili, Görsel Persentil Barları, Radar SVG, Opstoel Branş Eşleştirme, A4 Raporlar)
  2. Saha Ölçüm & Test Oturumu (Veritabanına kayıt + Görsel Norm/Z-Skoru/Makul Aralık göstergeleri + Canlı SVG sahne)
  3. Sporcu Karşılaştırma Laboratuvarı (Çift katmanlı Radar SVG + Başa baş Z-skoru fark analizi)
  4. 196 Test Kataloğu & 191 Bilimsel Kaynakça Kütüphanesi
  5. PerformTest Yönetim & KVKK Merkezi (Kulüp/Tenant yönetimi, RBAC Kullanıcılar, KVKK Anonimleştirme, Audit Log, Excel İhracı ve Yedekleme)
"""

WEB_VE_ADMIN_HTML = """<!DOCTYPE html>
<html lang="tr" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Performetre — Performans Ölçme ve Değerlendirme & Yetenek Seçimi Platformu</title>
  <style>
    :root, [data-theme="light"] {
      --bg: #f1f5f9;
      --surface: #ffffff;
      --surface-2: #f8fafc;
      --sidebar: #0f172a;
      --sidebar-hover: #1e293b;
      --ink: #0f172a;
      --muted: #64748b;
      --line: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-soft: #eff6ff;
      --accent: #0ea5e9;
      --success: #16a34a;
      --success-soft: #f0fdf4;
      --warn: #d97706;
      --warn-soft: #fffbeb;
      --danger: #dc2626;
      --danger-soft: #fef2f2;
      --shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg: #090d16;
      --surface: #111827;
      --surface-2: #1e293b;
      --sidebar: #060911;
      --sidebar-hover: #111827;
      --ink: #f8fafc;
      --muted: #94a3b8;
      --line: #1f2937;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-soft: rgba(59, 130, 246, 0.15);
      --accent: #38bdf8;
      --success: #22c55e;
      --success-soft: rgba(34, 197, 94, 0.15);
      --warn: #f59e0b;
      --warn-soft: rgba(245, 158, 11, 0.15);
      --danger: #ef4444;
      --danger-soft: rgba(239, 68, 68, 0.15);
      --shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
      font-variant-numeric: tabular-nums;
      display: flex;
      min-height: 100vh;
    }

    /* Sol Komut Kenar Çubuğu (Sidebar) */
    .sidebar {
      width: 268px;
      background: var(--sidebar);
      color: #f8fafc;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      border-right: 1px solid rgba(255,255,255,0.07);
      position: sticky;
      top: 0;
      height: 100vh;
    }
    .brand-header {
      padding: 20px 20px 18px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
      flex-shrink: 0;
    }
    .brand-title {
      font-weight: 800;
      font-size: 18px;
      letter-spacing: -0.4px;
      background: linear-gradient(90deg, #ffffff 0%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .brand-sub { font-size: 11px; color: #94a3b8; font-weight: 500; }

    .nav-section-label {
      padding: 16px 20px 6px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #64748b;
      font-weight: 700;
    }
    .nav-list { padding: 0 12px; display: flex; flex-direction: column; gap: 4px; flex: 1; }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 11px;
      padding: 11px 14px;
      border-radius: 10px;
      color: #cbd5e1;
      font-size: 13.5px;
      font-weight: 600;
      border: none;
      background: transparent;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
      width: 100%;
    }
    .nav-item:hover { background: var(--sidebar-hover); color: #fff; }
    .nav-item.active {
      background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }
    .nav-icon { font-size: 16px; width: 22px; text-align: center; }

    .sidebar-footer {
      padding: 16px;
      border-top: 1px solid rgba(255,255,255,0.08);
      font-size: 12px;
      color: #94a3b8;
    }

    /* Ana İçerik Alanı */
    .main-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .topbar {
      background: var(--surface);
      border-bottom: 1px solid var(--line);
      padding: 12px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 30;
    }
    .topbar-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .topbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

    .workspace { padding: 24px 26px; max-width: 1520px; width: 100%; margin: 0 auto; }

    /* Kartlar ve Izgaralar */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }
    .kpi-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 18px 20px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }
    .kpi-card::before {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--primary), var(--accent));
    }
    .kpi-label { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.4px; }
    .kpi-val { font-size: 28px; font-weight: 800; color: var(--ink); margin: 6px 0 2px; }
    .kpi-sub { font-size: 12px; color: var(--muted); }

    .studio-grid {
      display: grid;
      grid-template-columns: 350px 1fr;
      gap: 20px;
      align-items: start;
    }
    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }
    @media (max-width: 1120px) {
      .studio-grid, .two-col { grid-template-columns: 1fr; }
      .sidebar { width: 220px; }
    }
    @media (max-width: 780px) {
      body { flex-direction: column; }
      .sidebar { width: 100%; height: auto; position: static; }
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 20px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
    }
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line);
      flex-wrap: wrap;
    }
    .card-title { font-size: 16px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }

    /* Rozetler ve Butonlar */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      background: var(--primary-soft);
      color: var(--primary);
    }
    .badge.green { background: var(--success-soft); color: var(--success); }
    .badge.amber { background: var(--warn-soft); color: var(--warn); }
    .badge.red { background: var(--danger-soft); color: var(--danger); }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: var(--primary);
      color: #fff;
      border: 1px solid transparent;
      padding: 9px 15px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn:hover { background: var(--primary-hover); transform: translateY(-1px); }
    .btn.outline {
      background: var(--surface-2);
      color: var(--ink);
      border-color: var(--line);
    }
    .btn.outline:hover { border-color: var(--primary); color: var(--primary); }
    .btn.success { background: var(--success); }
    .btn.danger { background: var(--danger); }
    .btn.sm { padding: 6px 11px; font-size: 12px; border-radius: 8px; }

    input, select, textarea {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--ink);
      border-radius: 10px;
      font-size: 13.5px;
      margin-bottom: 10px;
      outline: none;
      transition: border-color 0.15s;
    }
    input:focus, select:focus { border-color: var(--primary); }
    label { display: block; font-size: 12.5px; font-weight: 600; color: var(--muted); margin-bottom: 4px; }

    /* Sporcu Liste Öğeleri */
    .athlete-card {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 11px 13px;
      border: 1px solid var(--line);
      border-radius: 12px;
      margin-bottom: 8px;
      cursor: pointer;
      background: var(--surface);
      transition: all 0.15s ease;
    }
    .athlete-card:hover {
      border-color: var(--primary);
      background: var(--surface-2);
    }
    .athlete-card.active {
      border-color: var(--primary);
      background: var(--primary-soft);
      box-shadow: 0 0 0 1px var(--primary);
    }
    .avatar {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #2563eb, #0ea5e9);
      color: #fff;
      font-weight: 700;
      font-size: 13px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .avatar.female { background: linear-gradient(135deg, #db2777, #f43f5e); }

    /* Görsel Persentil ve Z-Skoru Çubukları */
    .pct-bar-wrap {
      width: 130px;
      height: 8px;
      background: var(--line);
      border-radius: 999px;
      overflow: hidden;
      display: inline-block;
      vertical-align: middle;
      margin-right: 8px;
    }
    .pct-bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #3b82f6, #10b981);
    }

    table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; }
    th {
      background: var(--surface-2);
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: var(--muted);
    }
    tr:hover td { background: var(--surface-2); }

    /* Sekme Çipleri */
    .pill-group { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
    .pill {
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--muted);
      cursor: pointer;
    }
    .pill.active { background: var(--primary); color: #fff; border-color: var(--primary); }

    /* Bildirim (Toast) ve Modal */
    .toast-box {
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 999;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .toast {
      background: #0f172a;
      color: #fff;
      padding: 12px 18px;
      border-radius: 12px;
      border-left: 4px solid #22c55e;
      box-shadow: 0 10px 25px rgba(0,0,0,0.25);
      font-size: 13.5px;
      font-weight: 600;
      animation: fadeIn 0.2s ease;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(3px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }
    .modal-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 16px;
      max-width: 680px;
      width: 100%;
      max-height: 90vh;
      overflow: auto;
      padding: 24px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }
    .hidden { display: none !important; }
  </style>
</head>
<body>
  <!-- SOL KOMUT KENAR ÇUBUĞU -->
  <aside class="sidebar">
    <div class="brand-header">
      <div class="brand-logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
      </div>
      <div>
        <div class="brand-title">Performetre</div>
        <div class="brand-sub">Performans Ölçme ve Değerlendirme</div>
      </div>
    </div>

    <div class="nav-section-label">Performans & Saha</div>
    <div class="nav-list">
      <button class="nav-item active" onclick="sekmeAc('analiz', this)">
        <span class="nav-icon">📊</span> Sporcu Performans Merkezi
      </button>
      <button class="nav-item" onclick="sekmeAc('oturum', this)">
        <span class="nav-icon">⚡</span> Saha Ölçüm & Test Oturumu
      </button>
      <button class="nav-item" onclick="sekmeAc('karsilastir', this)">
        <span class="nav-icon">⚖️</span> Sporcu Karşılaştırma Lab
      </button>
      <button class="nav-item" onclick="sekmeAc('katalog', this)">
        <span class="nav-icon">🧬</span> 196 Test & Bilimsel Katalog
      </button>

      <div class="nav-section-label" style="padding-left:8px;">Kurumsal Yönetim</div>
      <button class="nav-item" onclick="sekmeAc('admin', this)">
        <span class="nav-icon">🛡️</span> Yönetim & KVKK Merkezi
      </button>
    </div>

    <div class="sidebar-footer">
      <div style="font-weight:700;color:#e2e8f0;margin-bottom:4px;">Yerli Sunucu (On-Premise)</div>
      <div>KVKK Madde 7 & 11 Uyumlu · 196 Test · 191 Bilimsel Kaynak</div>
    </div>
  </aside>

  <!-- ANA ÇALIŞMA ALANI -->
  <div class="main-area">
    <!-- ÜST KOMUT ÇUBUĞU -->
    <header class="topbar">
      <div class="topbar-left">
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:12.5px;font-weight:700;color:var(--muted);">AKTİF KULÜP:</span>
          <select id="kulupSecici" style="width:270px;margin:0;font-weight:600;" onchange="kulupDegisti()">
            <option value="merkez">merkez — Performetre Merkez Lab</option>
            <option value="demo-kulup-a">demo-kulup-a — Demo Kulüp A (Ankara)</option>
            <option value="demo-kulup-b">demo-kulup-b — Demo Kulüp B (İstanbul)</option>
          </select>
        </div>
        <button class="btn outline sm" onclick="kulupRaporuAc()">🏛️ A4 Kulüp Raporu</button>
        <button class="btn outline sm" onclick="kulupExcelIndir()">📥 Excel (.zip) İndir</button>
      </div>

      <div class="topbar-right">
        <span id="oturumDurumu" class="badge green">● Süper Admin</span>
        <select id="rolHizliSecici" style="width:205px;margin:0;font-size:12.5px;" onchange="rolDegistir(this.value)">
          <option value="admin@performtest.yerli|PerformAdmin2026!">Rol: Süper Admin</option>
          <option value="kulup-a@performtest.yerli|KulupA2026!">Rol: Kulüp Yöneticisi</option>
          <option value="antrenor@performtest.yerli|Antrenor2026!">Rol: Baş Antrenör</option>
          <option value="veli@performtest.yerli|Veli2026!">Rol: Sporcu Velisi</option>
        </select>
        <button class="btn outline sm" onclick="temaDegistir()" title="Açık / Koyu Tema">🌓 Tema</button>
      </div>
    </header>

    <main class="workspace">
      <!-- ════════════════════════════════════════════════════════════
           SEKME 1: SPORCU PERFORMANS MERKEZİ
      ════════════════════════════════════════════════════════════ -->
      <section id="sekme-analiz">
        <div class="studio-grid">
          <!-- Sol Sütun: Sporcu Seçici ve Filtreler -->
          <div class="card" style="padding:16px;">
            <div class="card-header" style="margin-bottom:12px;padding-bottom:10px;">
              <h3 class="card-title">Sporcu Kadrosu <span id="sporcuSayac" class="badge">0</span></h3>
              <button class="btn sm" onclick="yeniSporcuModalAc()">+ Yeni Sporcu</button>
            </div>
            <input id="sporcuArama" placeholder="🔍 Sporcu adı veya branş ara..." oninput="sporculariFiltrele()" />
            <div class="pill-group">
              <button class="pill active" onclick="cinsiyetFiltre('', this)">Tümü</button>
              <button class="pill" onclick="cinsiyetFiltre('Erkek', this)">Erkek</button>
              <button class="pill" onclick="cinsiyetFiltre('Kadın', this)">Kadın</button>
            </div>
            <div id="sporcuListesi" style="max-height:620px;overflow-y:auto;padding-right:4px;">Yükleniyor...</div>
          </div>

          <!-- Sağ Sütun: Sporcu Analiz Stüdyosu -->
          <div>
            <!-- Sporcu Hero Başlık Kartı -->
            <div class="card" id="sporcuHeroKarti">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
                <div style="display:flex;align-items:center;gap:14px;">
                  <div id="heroAvatar" class="avatar" style="width:54px;height:54px;font-size:18px;border-radius:14px;">PT</div>
                  <div>
                    <h2 id="seciliSporcuBaslik" style="margin:0;font-size:21px;font-weight:800;">Sporcu Seçin</h2>
                    <div id="seciliSporcuAlt" style="font-size:13px;color:var(--muted);">Kulüp kadrosundan bir sporcu seçerek analizleri görüntüleyin.</div>
                  </div>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                  <button class="btn" onclick="raporAc('veli')">📄 A4 Veli Karnesi</button>
                  <button class="btn outline" onclick="raporAc('antrenor')">📋 A4 Antrenör Raporu</button>
                  <button class="btn success" onclick="hizliOlcumEkleAc()">⚡ Saha Ölçümü Gir</button>
                </div>
              </div>

              <!-- 4 Antropometrik KPI Kutusu -->
              <div class="kpi-grid" id="sporcuKpiIzgara" style="margin-top:16px;margin-bottom:0;"></div>
            </div>

            <!-- Radar + Branş Yatkınlık İkili Izgara -->
            <div class="two-col">
              <div class="card">
                <div class="card-header">
                  <h3 class="card-title">🎯 Çok Boyutlu Z-Profili Radarı</h3>
                  <span class="badge">Akran Ortalaması = 0 SD</span>
                </div>
                <div id="radarKapsayici" style="text-align:center;min-height:260px;display:flex;align-items:center;justify-content:center;">
                  Sporcu seçildiğinde Z-skoru radarı burada çizilir.
                </div>
              </div>

              <div class="card">
                <div class="card-header">
                  <h3 class="card-title">🏆 Opstoel (2015) Branş Yatkınlık & Gelişim</h3>
                  <span class="badge green">Yetenek Seçimi</span>
                </div>
                <div id="bransYatkinlikKapsayici"></div>
              </div>
            </div>

            <!-- Görsel Persentil & Z-Skoru Tablosu -->
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">📈 Normatif Test Sonuçları, Yaşıt Persentili ve Z-Skoru Dağılımı</h3>
                <span id="testTabloSayac" class="badge">0 Test</span>
              </div>
              <div id="analizTabloKapsayici" style="overflow-x:auto;"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           SEKME 2: SAHA ÖLÇÜM & TEST OTURUMU
      ════════════════════════════════════════════════════════════ -->
      <section id="sekme-oturum" class="hidden">
        <div class="two-col">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">⚡ Saha Test Oturumu & Canlı Ölçüm Kaydı</h3>
              <span class="badge green">Anlık Eşik & Rekor Denetimli</span>
            </div>
            <div class="two-col" style="gap:12px;">
              <div>
                <label>Sporcu Seçin (Veritabanı Kaydı İçin)</label>
                <select id="otSporcuSecici" onchange="otSporcuDegisti()"></select>
              </div>
              <div>
                <label>Oturum Adı / Etiketi</label>
                <input id="otOturumAdi" value="2026 Güz Saha Ölçümü" />
              </div>
            </div>

            <label>Test Seçin (Hızlı Arama + Katalog Listesi)</label>
            <input id="otTestArama" placeholder="🔍 Test adı, branş, batarya veya nitelik ara..." oninput="otTestFiltrele()" style="margin-bottom:8px;" />
            <select id="otTestSecici" onchange="otTestDegisti()"></select>

            <div class="two-col" style="gap:12px;">
              <div>
                <label>Ölçülen Değişken</label>
                <select id="otDegiskenSecici"></select>
              </div>
              <div>
                <label>Ölçülen Değer</label>
                <input id="otDeger" type="number" step="0.01" value="152" />
              </div>
            </div>

            <div class="two-col" style="gap:12px;">
              <div>
                <label>Sporcu Test Yaşı</label>
                <input id="otYas" type="number" step="0.5" value="11" />
              </div>
              <div>
                <label>Cinsiyet</label>
                <select id="otCinsiyet">
                  <option value="Erkek">Erkek</option>
                  <option value="Kadın">Kadın</option>
                </select>
              </div>
            </div>

            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
              <button class="btn" onclick="canliDegerlendir()">🔍 Norm & Z-Skoru Hesapla</button>
              <button class="btn success" onclick="sahaOlcumuVeritabaninaKaydet()">💾 Veritabanına Kaydet & Denetim İzine İşle</button>
            </div>
          </div>

          <div>
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">📊 Anlık Performans Ölçme ve Değerlendirme</h3>
                <span id="canliDurumRozet" class="badge">Hazır</span>
              </div>
              <div id="canliSonucKartlari">
                Ölçüm değerini girip <strong>Norm & Z-Skoru Hesapla</strong> veya <strong>Veritabanına Kaydet</strong> düğmesine tıklayın.
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <h3 class="card-title" id="otSvgBaslik">🎨 Test Protokolü İzometrik Sahnesi</h3>
              </div>
              <div id="otSvgKapsayici" style="text-align:center;"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           SEKME 3: SPORCU KARŞILAŞTIRMA LABORATUVARI
      ════════════════════════════════════════════════════════════ -->
      <section id="sekme-karsilastir" class="hidden">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">⚖️ Başa Baş (Head-to-Head) Sporcu Karşılaştırma Laboratuvarı</h3>
            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
              <select id="karsSporcuA" style="width:220px;margin:0;"></select>
              <span style="font-weight:800;color:var(--muted);">VS</span>
              <select id="karsSporcuB" style="width:220px;margin:0;"></select>
              <button class="btn" onclick="sporculariKarsilastir()">Karşılaştır</button>
            </div>
          </div>
          <div id="karsilastirmaIcerik">İki sporcu seçip <strong>Karşılaştır</strong> düğmesine tıklayın.</div>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           SEKME 4: 196 TEST KATALOĞU & 191 BİLİMSEL KAYNAKÇA
      ════════════════════════════════════════════════════════════ -->
      <section id="sekme-katalog" class="hidden">
        <div class="studio-grid">
          <div class="card" style="padding:16px;">
            <div class="card-header" style="margin-bottom:10px;padding-bottom:8px;">
              <h3 class="card-title">196 Test Kataloğu</h3>
              <button class="btn outline sm" onclick="kaynakcaModalAc()">📚 191 Bilimsel Kaynakça</button>
            </div>
            <input id="katalogArama" placeholder="🔍 Test, nitelik veya branş ara..." oninput="katalogYukle()" />
            <div id="katalogListesi" style="max-height:600px;overflow-y:auto;"></div>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title" id="svgBaslik">İzometrik SVG Protokol Sahnesi & Ölçüm Alanları</h3>
              <span id="svgNitelikRozet" class="badge">Protokol</span>
            </div>
            <div id="svgKapsayici">Soldan bir test seçin.</div>
          </div>
        </div>
      </section>

      <!-- ════════════════════════════════════════════════════════════
           SEKME 5: PERFORMTEST YÖNETİM & KVKK MERKEZİ (ADMIN)
      ════════════════════════════════════════════════════════════ -->
      <section id="sekme-admin" class="hidden">
        <div class="kpi-grid" id="adminMetrikler"></div>

        <div class="two-col">
          <!-- Kulüp Yönetimi ve Yeni Kulüp Ekleme -->
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🏛️ Çoklu Kulüp (Tenant) Yönetimi</h3>
              <div style="display:flex;gap:8px;">
                <button class="btn sm" onclick="adminYedekAl()">💾 Anlık DB Yedeği Al</button>
                <button class="btn outline sm" onclick="adminDemoYukle()">🔄 Demo Verisini Eşitle</button>
              </div>
            </div>
            <div id="adminKulupTablosu" style="margin-bottom:16px;overflow-x:auto;"></div>

            <div style="background:var(--surface-2);padding:14px;border-radius:12px;border:1px solid var(--line);">
              <div style="font-weight:700;font-size:13.5px;margin-bottom:10px;">+ Yeni Spor Kulübü / Merkez Tanımla</div>
              <div class="two-col" style="gap:10px;">
                <input id="yeniKulupKod" placeholder="Kulüp kodu (örn: ankara-olimpik)" style="margin:0;" />
                <input id="yeniKulupAd" placeholder="Kulüp Adı (örn: Ankara Olimpik SK)" style="margin:0;" />
              </div>
              <div style="display:flex;gap:10px;margin-top:10px;">
                <input id="yeniKulupSehir" placeholder="Şehir (örn: Ankara)" style="margin:0;" />
                <button class="btn" style="white-space:nowrap;" onclick="yeniKulupEkle()">Kulüp Oluştur</button>
              </div>
            </div>
          </div>

          <!-- RBAC Kullanıcı Yönetimi ve KVKK Unutulma Hakkı -->
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🔐 RBAC Kullanıcı & KVKK Veri Yönetişimi</h3>
              <span class="badge green">PBKDF2-SHA256 + JWT</span>
            </div>
            <div id="adminKullaniciTablosu" style="max-height:210px;overflow-y:auto;margin-bottom:14px;"></div>

            <div style="background:var(--surface-2);padding:14px;border-radius:12px;border:1px solid var(--line);margin-bottom:14px;">
              <div style="font-weight:700;font-size:13.5px;margin-bottom:8px;">+ Yeni Yetkili Kullanıcı Ekle</div>
              <div class="two-col" style="gap:8px;">
                <input id="ykEposta" placeholder="E-posta (örn: koc@performtest.yerli)" style="margin:0;" />
                <input id="ykAdSoyad" placeholder="Ad Soyad" style="margin:0;" />
                <input id="ykParola" type="password" placeholder="Parola (en az 6 krk)" style="margin:0;" />
                <select id="ykRol" style="margin:0;">
                  <option value="antrenor">Antrenör / Ölçüm Uzmanı</option>
                  <option value="kulup_yoneticisi">Kulüp Yöneticisi</option>
                  <option value="sporcu_veli">Sporcu Velisi</option>
                  <option value="super_admin">Süper Admin</option>
                </select>
              </div>
              <button class="btn sm" style="margin-top:8px;" onclick="yeniKullaniciOlustur()">Kullanıcı Yetkilendir</button>
            </div>

            <div style="background:var(--danger-soft);padding:14px;border-radius:12px;border:1px solid rgba(220,38,38,0.25);">
              <div style="font-weight:700;font-size:13.5px;color:var(--danger);margin-bottom:6px;">
                🛡️ KVKK Madde 7 & 11 — Sporcu Kimliği Anonimleştirme (Unutulma Hakkı)
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <select id="kvkkSporcuSecici" style="flex:1;margin:0;"></select>
                <input id="kvkkNeden" placeholder="Hukuki gerekçe (örn: Veli yazılı başvurusu)" style="flex:1;margin:0;" />
                <button class="btn danger sm" onclick="kvkkSporcuAnonimlestir()">Kimliği Anonimleştir</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Değiştirilemez KVKK Denetim İzi -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📜 Değiştirilemez KVKK Denetim İzi (Immutable Audit Log)</h3>
            <span class="badge amber">Append-Only Güvenlik Kaydı</span>
          </div>
          <div id="denetimTablosuKapsayici" style="max-height:420px;overflow-y:auto;"></div>
        </div>
      </section>
    </main>
  </div>

  <!-- MODAL: YENİ SPORCU EKLE -->
  <div id="yeniSporcuModal" class="modal-backdrop hidden" onclick="if(event.target===this)this.classList.add('hidden')">
    <div class="modal-card">
      <div class="card-header">
        <h3 class="card-title">🏃 Yeni Sporcu Kaydı & KVKK Açık Rıza Beyanı</h3>
        <button class="btn outline sm" onclick="document.getElementById('yeniSporcuModal').classList.add('hidden')">✕ Kapat</button>
      </div>
      <div class="two-col" style="gap:12px;">
        <div><label>Ad</label><input id="spAd" placeholder="Örn: Kerem" /></div>
        <div><label>Soyad</label><input id="spSoyad" placeholder="Örn: Yılmaz" /></div>
        <div><label>Yaş</label><input id="spYas" type="number" step="0.5" value="10" /></div>
        <div>
          <label>Cinsiyet</label>
          <select id="spCinsiyet"><option value="Erkek">Erkek</option><option value="Kadın">Kadın</option></select>
        </div>
        <div><label>Boy (cm)</label><input id="spBoy" type="number" step="0.5" value="142" /></div>
        <div><label>Kilo (kg)</label><input id="spKilo" type="number" step="0.5" value="36" /></div>
      </div>
      <label>Spor Dalı / Branş</label>
      <input id="spBrans" value="Genel Atletik Performans" />
      <div style="background:var(--primary-soft);padding:12px;border-radius:10px;font-size:12.5px;margin-bottom:14px;">
        ☑️ <strong>6698 Sayılı KVKK Veli Açık Rıza Onayı:</strong> Sporcunun antropometrik ve sportif performans verilerinin yerli sunucuda işlenmesine yönelik aydınlatma metni onaylanmıştır.
      </div>
      <button class="btn" onclick="yeniSporcuKaydet()">Sporcuyu Kaydet</button>
    </div>
  </div>

  <!-- MODAL: SVG PROTOKOL & KAYNAKÇA -->
  <div id="genelModal" class="modal-backdrop hidden" onclick="if(event.target===this)this.classList.add('hidden')">
    <div class="modal-card">
      <div class="card-header">
        <h3 class="card-title" id="genelModalBaslik">Detay</h3>
        <button class="btn outline sm" onclick="document.getElementById('genelModal').classList.add('hidden')">✕ Kapat</button>
      </div>
      <div id="genelModalIcerik"></div>
    </div>
  </div>

  <div id="toastKutusu" class="toast-box"></div>

  <script>
    let jwtToken = "";
    let tumSporcular = [];
    let tumTestler = [];
    let aktifSporcu = "";
    let aktifCinsiyetFiltre = "";

    function bildirim(mesaj) {
      const kutu = document.getElementById("toastKutusu");
      const el = document.createElement("div");
      el.className = "toast";
      el.textContent = mesaj;
      kutu.appendChild(el);
      setTimeout(() => el.remove(), 3400);
    }

    function temaDegistir() {
      const kok = document.documentElement;
      const yeni = kok.getAttribute("data-theme") === "dark" ? "light" : "dark";
      kok.setAttribute("data-theme", yeni);
      localStorage.setItem("performtest_tema", yeni);
    }

    async function hizliGiris(eposta, parola) {
      const r = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({eposta, parola})
      });
      const d = await r.json();
      if (d.access_token) {
        jwtToken = d.access_token;
        document.getElementById("oturumDurumu").textContent = `● ${d.kullanici.ad_soyad}`;
        bildirim(`Oturum açıldı: ${d.kullanici.ad_soyad}`);
      }
    }

    function rolDegistir(deger) {
      const [eposta, parola] = deger.split("|");
      hizliGiris(eposta, parola);
    }

    function sekmeAc(ad, btn) {
      ["analiz", "oturum", "karsilastir", "katalog", "admin"].forEach(s => {
        document.getElementById("sekme-" + s).classList.toggle("hidden", s !== ad);
      });
      document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
      if (btn) btn.classList.add("active");
      if (ad === "oturum") oturumEkraniHazirla();
      if (ad === "karsilastir") karsilastirmaHazirla();
      if (ad === "katalog") katalogYukle();
      if (ad === "admin") adminYukle();
    }

    async function kulupDegisti() {
      await sporculariYukle();
      bildirim(`Aktif kulüp değiştirildi: ${document.getElementById("kulupSecici").value}`);
    }

    function cinsiyetFiltre(cins, btn) {
      aktifCinsiyetFiltre = cins;
      btn.parentElement.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      sporculariFiltrele();
    }

    async function sporculariYukle() {
      const kulup = document.getElementById("kulupSecici").value;
      const r = await fetch(`/api/v1/sporcular?kulup_kodu=${encodeURIComponent(kulup)}`);
      const d = await r.json();
      tumSporcular = d.sporcular || [];
      sporculariFiltrele();
      if (tumSporcular.length > 0) {
        sporcuAnalizYukle(tumSporcular[0].tam_ad);
      }
    }

    function sporculariFiltrele() {
      const aranan = (document.getElementById("sporcuArama").value || "").toLowerCase();
      const liste = tumSporcular.filter(s => {
        if (aktifCinsiyetFiltre && s.cinsiyet !== aktifCinsiyetFiltre) return false;
        if (aranan && !s.tam_ad.toLowerCase().includes(aranan) && !(s.spor_dali || "").toLowerCase().includes(aranan)) return false;
        return true;
      });
      document.getElementById("sporcuSayac").textContent = liste.length;
      const kutu = document.getElementById("sporcuListesi");
      kutu.innerHTML = "";
      liste.forEach(s => {
        const basHarfler = s.tam_ad.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
        const el = document.createElement("div");
        el.className = "athlete-card" + (s.tam_ad === aktifSporcu ? " active" : "");
        el.innerHTML = `
          <div style="display:flex;align-items:center;gap:11px;">
            <div class="avatar ${s.cinsiyet === 'Kadın' ? 'female' : ''}">${basHarfler}</div>
            <div>
              <div style="font-weight:700;font-size:14px;">${s.tam_ad}</div>
              <div style="font-size:12px;color:var(--muted);">${s.cinsiyet} · ${s.yas ?? "-"} yaş · ${s.spor_dali || "Genel"}</div>
            </div>
          </div>
          <span class="badge">${s.olcum_sayisi} ölçüm</span>
        `;
        el.onclick = () => {
          aktifSporcu = s.tam_ad;
          sporculariFiltrele();
          sporcuAnalizYukle(s.tam_ad);
        };
        kutu.appendChild(el);
      });
    }

    async function sporcuAnalizYukle(sporcuAdi) {
      aktifSporcu = sporcuAdi;
      const kulup = document.getElementById("kulupSecici").value;
      const r = await fetch(`/api/v1/sporcular/${encodeURIComponent(sporcuAdi)}/analiz?kulup_kodu=${encodeURIComponent(kulup)}`);
      const a = await r.json();
      const p = a.profil || {};
      const basHarfler = sporcuAdi.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
      const avatar = document.getElementById("heroAvatar");
      avatar.textContent = basHarfler;
      avatar.className = "avatar" + (p.Cinsiyet === "Kadın" ? " female" : "");

      document.getElementById("seciliSporcuBaslik").textContent = sporcuAdi;
      document.getElementById("seciliSporcuAlt").textContent =
        `${p.Cinsiyet || "-"} · Branş: ${p["Spor Dalı"] || "Genel Atletik Performans"} · Kulüp: ${kulup} · Rapor Tarihi: ${a.rapor_tarihi || ""}`;

      const boy = parseFloat(p["Boy (cm)"]) || 0;
      const kilo = parseFloat(p["Kilo (kg)"]) || 0;
      const vki = (boy > 0 && kilo > 0) ? (kilo / Math.pow(boy / 100, 2)).toFixed(1) : "—";
      const satirlar = (a.z_profili && a.z_profili.satirlar) || [];

      document.getElementById("sporcuKpiIzgara").innerHTML = `
        <div class="kpi-card">
          <div class="kpi-label">Takvim Yaşı & Cinsiyet</div>
          <div class="kpi-val">${p["Yaş"] ?? "—"} <span style="font-size:15px;font-weight:600;">yaş</span></div>
          <div class="kpi-sub">${p.Cinsiyet || ""} · Doğum: ${p["Doğum Tarihi"] || "Kayıtlı"}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Antropometri (Boy / Kilo)</div>
          <div class="kpi-val">${boy || "—"} <span style="font-size:15px;">cm</span> / ${kilo || "—"} <span style="font-size:15px;">kg</span></div>
          <div class="kpi-sub">Vücut Kütle İndeksi (VKİ): <strong>${vki} kg/m²</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Fiziksel Yatkınlık Penceresi</div>
          <div class="kpi-val" style="font-size:18px;margin-top:10px;">${(a.fiziksel_pencere || []).join(" · ") || "Değerlendiriliyor"}</div>
          <div class="kpi-sub">Opstoel ve ark. (2015) çok değişkenli model</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Değerlendirilen Normlu Test</div>
          <div class="kpi-val">${satirlar.length} <span style="font-size:15px;">parametre</span></div>
          <div class="kpi-sub">Toplam ${(a.kayitli_testler || []).length} farklı test protokolü</div>
        </div>
      `;

      // Radar
      document.getElementById("radarKapsayici").innerHTML =
        a.radar_svg || `<div style="color:var(--muted);">Radar grafiği için en az 3 normlu test gereklidir.</div>`;

      // Branş Yatkınlık & Gelişim
      const pencereler = a.fiziksel_pencere || [];
      const tumGruplar = ["Top sporları", "Raket sporları", "Yüzme", "Cimnastik", "Dövüş sporları", "Dans"];
      let bransHtml = `<div style="margin-bottom:14px;"><div style="font-size:12.5px;font-weight:700;color:var(--muted);margin-bottom:8px;">ÖNERİLEN SPOR BRANŞ GRUPLARI (OPSTOEL 2015)</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">`;
      tumGruplar.forEach(g => {
        const uygun = pencereler.includes(g);
        bransHtml += `
          <div style="padding:10px 12px;border-radius:10px;border:1px solid ${uygun ? 'var(--success)' : 'var(--line)'};background:${uygun ? 'var(--success-soft)' : 'var(--surface-2)'};display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:700;font-size:13px;">${g}</span>
            <span class="badge ${uygun ? 'green' : ''}">${uygun ? '★ Yatkın' : 'İzlem'}</span>
          </div>
        `;
      });
      bransHtml += `</div></div>`;

      const gelisimler = (a.gelisim_ozetleri || []).filter(g => g.fark !== null && g.fark !== undefined).slice(0, 4);
      if (gelisimler.length > 0) {
        bransHtml += `<div style="font-size:12.5px;font-weight:700;color:var(--muted);margin:14px 0 8px;">OTURUMLAR ARASI GELİŞİM ÖZETİ (İLK ↔ SON ÖLÇÜM)</div>`;
        gelisimler.forEach(g => {
          const iyi = g.iyi_yonde;
          bransHtml += `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;border-bottom:1px solid var(--line);font-size:13px;">
              <span><strong>${g.test}</strong> (${g.degisken})</span>
              <span class="badge ${iyi ? 'green' : 'amber'}">${g.fark > 0 ? '+' : ''}${g.fark} ${g.birim || ''} (${g.yuzde ? g.yuzde + '%' : ''})</span>
            </div>
          `;
        });
      }
      document.getElementById("bransYatkinlikKapsayici").innerHTML = bransHtml;

      // Görsel Norm Tablosu
      document.getElementById("testTabloSayac").textContent = `${satirlar.length} Parametre`;
      let tablo = `<table><thead><tr><th>Test Protokolü</th><th>Ölçülen Değişken</th><th>Ham Değer</th><th>Yaşıt Persentili</th><th>Performans Z-Skoru</th><th>Protokol</th></tr></thead><tbody>`;
      satirlar.forEach(s => {
        const z = parseFloat(s["Z (performans)"] ?? s.Z ?? 0);
        const zRenk = z >= 0.75 ? "green" : (z <= -0.75 ? "amber" : "");
        const zMetin = isNaN(z) ? "—" : `${z >= 0 ? '+' : ''}${z.toFixed(2)} SD`;
        const pctMetin = String(s.Persentil ?? "—");
        const pctSayi = Math.max(8, Math.min(98, Math.round(50 + (isNaN(z) ? 0 : z * 22))));
        const testAdi = s.Test || "";
        tablo += `
          <tr>
            <td><strong>${testAdi}</strong></td>
            <td>${s["Değişken"] || ""}</td>
            <td><strong style="font-size:14px;">${s["Değer"] ?? ""}</strong></td>
            <td>
              <div class="pct-bar-wrap"><div class="pct-bar-fill" style="width:${pctSayi}%;"></div></div>
              <span style="font-weight:600;font-size:12.5px;">${pctMetin}</span>
            </td>
            <td><span class="badge ${zRenk}">${zMetin}</span></td>
            <td><button class="btn outline sm" onclick="protokolModalAc('${testAdi.replace(/'/g, "\\'")}')">🎨 SVG Sahne</button></td>
          </tr>
        `;
      });
      tablo += `</tbody></table>`;
      document.getElementById("analizTabloKapsayici").innerHTML = tablo;
    }

    function svgAnimasyonuBaslat(kapsayici) {
      if (!kapsayici) return;
      kapsayici.querySelectorAll("svg").forEach(s => {
        try {
          if (typeof s.unpauseAnimations === "function") s.unpauseAnimations();
          if (typeof s.setCurrentTime === "function") s.setCurrentTime(0);
        } catch (e) {}
      });
    }

    async function protokolModalAc(testAdi) {
      const r = await fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(testAdi)}`);
      const d = await r.json();
      document.getElementById("genelModalBaslik").textContent = `${testAdi} — Protokol & SVG Sahnesi`;
      const icerik = document.getElementById("genelModalIcerik");
      icerik.innerHTML = `
        <p style="font-size:13.5px;color:var(--muted);">${d.aciklama || ""}</p>
        <div>${d.svg_html || ""}</div>
      `;
      document.getElementById("genelModal").classList.remove("hidden");
      svgAnimasyonuBaslat(icerik);
    }

    async function kaynakcaModalAc() {
      const r = await fetch("/api/v1/katalog/kaynakca");
      const d = await r.json();
      document.getElementById("genelModalBaslik").textContent = `Performetre Bilimsel Kütüphane (${d.toplam} Kaynak)`;
      const liste = (d.kaynakca || []).map((k, i) => `
        <div style="padding:8px 0;border-bottom:1px solid var(--line);font-size:13px;">
          <strong>[${i + 1}]</strong> ${k.metin || k.kaynak || JSON.stringify(k)}
        </div>
      `).join("");
      document.getElementById("genelModalIcerik").innerHTML = `<div style="max-height:60vh;overflow-y:auto;">${liste}</div>`;
      document.getElementById("genelModal").classList.remove("hidden");
    }

    function yeniSporcuModalAc() {
      document.getElementById("yeniSporcuModal").classList.remove("hidden");
    }

    async function yeniSporcuKaydet() {
      const kulup = document.getElementById("kulupSecici").value;
      const payload = {
        kulup_kodu: kulup,
        ad: document.getElementById("spAd").value,
        soyad: document.getElementById("spSoyad").value,
        yas: parseFloat(document.getElementById("spYas").value),
        cinsiyet: document.getElementById("spCinsiyet").value,
        boy_cm: parseFloat(document.getElementById("spBoy").value),
        kilo_kg: parseFloat(document.getElementById("spKilo").value),
        spor_dali: document.getElementById("spBrans").value
      };
      const r = await fetch("/api/v1/sporcular", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`},
        body: JSON.stringify(payload)
      });
      if (r.ok) {
        document.getElementById("yeniSporcuModal").classList.add("hidden");
        bildirim(`Yeni sporcu kaydedildi: ${payload.ad} ${payload.soyad}`);
        await sporculariYukle();
      } else {
        const h = await r.json();
        bildirim(`Hata: ${h.hata || "Kayıt başarısız"}`);
      }
    }

    function hizliOlcumEkleAc() {
      sekmeAc("oturum", document.querySelectorAll(".nav-item")[1]);
    }

    async function oturumEkraniHazirla() {
      const spSel = document.getElementById("otSporcuSecici");
      spSel.innerHTML = tumSporcular.map(s => `<option value="${s.tam_ad}" ${s.tam_ad === aktifSporcu ? 'selected' : ''}>${s.tam_ad} (${s.cinsiyet}, ${s.yas ?? '-'} yaş)</option>`).join("");
      otSporcuDegisti();

      if (tumTestler.length === 0) {
        const r = await fetch("/api/v1/katalog/testler");
        const d = await r.json();
        tumTestler = d.testler || [];
      }
      otTestFiltrele("Durarak Uzun Atlama");
      await canliDegerlendir();
    }

    async function otTestFiltrele(varsayilanSecim) {
      const aranan = (document.getElementById("otTestArama")?.value || "").trim().toLocaleLowerCase("tr-TR");
      const tSel = document.getElementById("otTestSecici");
      const mevcut = varsayilanSecim || tSel.value || "Durarak Uzun Atlama";
      const liste = aranan
        ? tumTestler.filter(t =>
            [t.test_adi, t.kategori, t.nitelik, t.batarya, t.brans]
              .filter(Boolean)
              .some(a => String(a).toLocaleLowerCase("tr-TR").includes(aranan))
          )
        : tumTestler;
      const gosterilecek = liste.length > 0 ? liste : tumTestler;
      const secilecek = gosterilecek.some(t => t.test_adi === mevcut) ? mevcut : gosterilecek[0]?.test_adi;
      tSel.innerHTML = gosterilecek.map(t => `<option value="${t.test_adi}" ${t.test_adi === secilecek ? 'selected' : ''}>${t.test_adi} (${t.kategori})</option>`).join("");
      await otTestDegisti();
    }

    function otSporcuDegisti() {
      const ad = document.getElementById("otSporcuSecici").value;
      const sp = tumSporcular.find(x => x.tam_ad === ad);
      if (sp) {
        if (sp.yas) document.getElementById("otYas").value = sp.yas;
        if (sp.cinsiyet) document.getElementById("otCinsiyet").value = sp.cinsiyet;
      }
    }

    async function otTestDegisti() {
      const testAdi = document.getElementById("otTestSecici").value;
      const t = tumTestler.find(x => x.test_adi === testAdi);
      const degSel = document.getElementById("otDegiskenSecici");
      const alanlar = (t && t.alanlar && t.alanlar.length > 0) ? t.alanlar.map(a => a[0]) : ["Deneme 1 (cm)"];
      degSel.innerHTML = alanlar.map(a => `<option value="${a}">${a}</option>`).join("");

      const r = await fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(testAdi)}`);
      const d = await r.json();
      document.getElementById("otSvgBaslik").textContent = `${testAdi} — Protokol Sahnesi`;
      const kaps = document.getElementById("otSvgKapsayici");
      kaps.innerHTML = d.svg_html || "";
      svgAnimasyonuBaslat(kaps);
    }

    async function canliDegerlendir() {
      const payload = {
        test_adi: document.getElementById("otTestSecici").value || "Durarak Uzun Atlama",
        degisken: document.getElementById("otDegiskenSecici").value || "Deneme 1 (cm)",
        deger: parseFloat(document.getElementById("otDeger").value),
        yas: parseFloat(document.getElementById("otYas").value),
        cinsiyet: document.getElementById("otCinsiyet").value
      };
      const r = await fetch("/api/v1/analiz/degerlendir", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      const d = await r.json();
      const z = d.z_skoru && typeof d.z_skoru === "object" ? (d.z_skoru.z_performans ?? d.z_skoru.z) : d.z_skoru;
      const zMetin = (z !== null && z !== undefined && !isNaN(z)) ? `${z >= 0 ? '+' : ''}${Number(z).toFixed(2)} SD` : "Norm Dışı / Tanımsız";
      const makul = d.makul_aralik ? `${d.makul_aralik[0]} – ${d.makul_aralik[1]}` : "Genel Aralık";
      document.getElementById("canliSonucKartlari").innerHTML = `
        <div class="kpi-grid" style="margin-bottom:0;">
          <div class="kpi-card">
            <div class="kpi-label">Yaşıt Persentil Dilimi</div>
            <div class="kpi-val">${d.persentil || "—"}</div>
            <div class="kpi-sub">${d.test_adi}</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Performans Z-Skoru</div>
            <div class="kpi-val">${zMetin}</div>
            <div class="kpi-sub">Yaş: ${d.yas} · ${d.cinsiyet}</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Makul Fizyolojik Aralık</div>
            <div class="kpi-val" style="font-size:22px;">${makul}</div>
            <div class="kpi-sub">Uç değer / rekor filtresi</div>
          </div>
        </div>
      `;
    }

    async function sahaOlcumuVeritabaninaKaydet() {
      const kulup = document.getElementById("kulupSecici").value;
      const sporcuAdi = document.getElementById("otSporcuSecici").value;
      const testAdi = document.getElementById("otTestSecici").value;
      const degisken = document.getElementById("otDegiskenSecici").value;
      const deger = parseFloat(document.getElementById("otDeger").value);
      const yas = parseFloat(document.getElementById("otYas").value);
      const oturum = document.getElementById("otOturumAdi").value;

      const r = await fetch("/api/v1/oturumlar/olcum-kaydet", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`},
        body: JSON.stringify({
          kulup_kodu: kulup,
          sporcu_adi: sporcuAdi,
          test_adi: testAdi,
          test_yasi: yas,
          oturum: oturum,
          olcumler: {[degisken]: deger}
        })
      });
      if (r.ok) {
        bildirim(`Ölçüm kaydedildi: ${sporcuAdi} — ${testAdi}`);
        await canliDegerlendir();
        await sporculariYukle();
      } else {
        const h = await r.json();
        bildirim(`Hata: ${h.hata || "Kayıt yetkisi gerekli"}`);
      }
    }

    async function karsilastirmaHazirla() {
      const selA = document.getElementById("karsSporcuA");
      const selB = document.getElementById("karsSporcuB");
      selA.innerHTML = tumSporcular.map((s, i) => `<option value="${s.tam_ad}" ${i === 0 ? 'selected' : ''}>${s.tam_ad}</option>`).join("");
      selB.innerHTML = tumSporcular.map((s, i) => `<option value="${s.tam_ad}" ${i === 1 ? 'selected' : ''}>${s.tam_ad}</option>`).join("");
      if (tumSporcular.length >= 2) {
        await sporculariKarsilastir();
      }
    }

    async function sporculariKarsilastir() {
      const kulup = document.getElementById("kulupSecici").value;
      const a = document.getElementById("karsSporcuA").value;
      const b = document.getElementById("karsSporcuB").value;
      const r = await fetch(`/api/v1/karsilastir?kulup_kodu=${encodeURIComponent(kulup)}&sporcu_a=${encodeURIComponent(a)}&sporcu_b=${encodeURIComponent(b)}`);
      const d = await r.json();
      let html = `
        <div class="two-col" style="margin-bottom:18px;">
          <div style="padding:14px;border-radius:12px;border:2px solid #2563eb;background:var(--primary-soft);">
            <div style="font-weight:800;font-size:17px;color:#2563eb;">🔵 ${d.sporcu_a.ad}</div>
            <div style="font-size:13px;margin-top:4px;">Yatkınlık: <strong>${(d.sporcu_a.fiziksel_pencere || []).join(", ") || "—"}</strong></div>
          </div>
          <div style="padding:14px;border-radius:12px;border:2px solid #f59e0b;background:var(--warn-soft);">
            <div style="font-weight:800;font-size:17px;color:#d97706;">🟠 ${d.sporcu_b.ad}</div>
            <div style="font-size:13px;margin-top:4px;">Yatkınlık: <strong>${(d.sporcu_b.fiziksel_pencere || []).join(", ") || "—"}</strong></div>
          </div>
        </div>
      `;
      if (d.radar_svg) {
        html += `<div style="max-width:560px;margin:0 auto 20px;">${d.radar_svg}</div>`;
      }
      html += `<table><thead><tr><th>Test & Değişken</th><th>🔵 ${d.sporcu_a.ad} (Z)</th><th>🟠 ${d.sporcu_b.ad} (Z)</th><th>Fark (ΔZ)</th></tr></thead><tbody>`;
      (d.satirlar || []).forEach(s => {
        const fark = s.z_fark !== null && s.z_fark !== undefined ? `${s.z_fark > 0 ? '+' : ''}${s.z_fark} SD` : "—";
        html += `
          <tr>
            <td><strong>${s.test || ""}</strong> — ${s.degisken || ""}</td>
            <td>${s.deger_a ?? "—"} <span class="badge">${s.z_a ?? "—"}</span></td>
            <td>${s.deger_b ?? "—"} <span class="badge amber">${s.z_b ?? "—"}</span></td>
            <td><strong>${fark}</strong></td>
          </tr>
        `;
      });
      html += `</tbody></table>`;
      document.getElementById("karsilastirmaIcerik").innerHTML = html;
    }

    function raporAc(tur) {
      if (!aktifSporcu) return;
      const kulup = document.getElementById("kulupSecici").value;
      window.open(`/api/v1/sporcular/${encodeURIComponent(aktifSporcu)}/rapor?kulup_kodu=${encodeURIComponent(kulup)}&tur=${tur}`, "_blank");
    }

    function kulupRaporuAc() {
      const kulup = document.getElementById("kulupSecici").value;
      window.open(`/api/v1/kulupler/${encodeURIComponent(kulup)}/rapor`, "_blank");
    }

    function kulupExcelIndir() {
      const kulup = document.getElementById("kulupSecici").value;
      window.location.href = `/api/v1/admin/disa-aktar/${encodeURIComponent(kulup)}`;
      bildirim(`${kulup} kulübü Excel paketi indiriliyor...`);
    }

    async function katalogYukle() {
      const arama = document.getElementById("katalogArama").value;
      const r = await fetch(`/api/v1/katalog/testler?arama=${encodeURIComponent(arama)}`);
      const d = await r.json();
      tumTestler = d.testler || [];
      const kutu = document.getElementById("katalogListesi");
      kutu.innerHTML = "";
      tumTestler.slice(0, 80).forEach((t, i) => {
        const el = document.createElement("div");
        el.className = "athlete-card" + (i === 0 ? " active" : "");
        el.innerHTML = `
          <div>
            <div style="font-weight:700;font-size:13.5px;">${t.test_adi}</div>
            <div style="font-size:12px;color:var(--muted);">${t.kategori} · ${t.nitelik || "Genel"}</div>
          </div>
          <span class="badge ${t.norm_var_mi ? 'green' : ''}">${t.norm_var_mi ? 'Normlu' : 'Protokol'}</span>
        `;
        el.onclick = () => {
          kutu.querySelectorAll(".athlete-card").forEach(c => c.classList.remove("active"));
          el.classList.add("active");
          svgGoster(t.test_adi);
        };
        kutu.appendChild(el);
      });
      if (tumTestler.length > 0) svgGoster(tumTestler[0].test_adi);
    }

    async function svgGoster(testAdi) {
      document.getElementById("svgBaslik").textContent = `${testAdi} — Protokol & SVG Sahnesi`;
      const r = await fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(testAdi)}`);
      const d = await r.json();
      document.getElementById("svgNitelikRozet").textContent = d.nitelik || "Protokol";
      const alanRozetleri = (d.alanlar || []).map(a => `<span class="badge" style="margin-right:6px;">${a[0]} (${a[1] || 'sayısal'})</span>`).join("");
      const kaps = document.getElementById("svgKapsayici");
      kaps.innerHTML = `
        <p style="font-size:14px;color:var(--muted);margin-top:0;">${d.aciklama || ""}</p>
        <div style="margin-bottom:14px;">${alanRozetleri}</div>
        <div>${d.svg_html || ""}</div>
      `;
      svgAnimasyonuBaslat(kaps);
    }

    async function adminYukle() {
      const headers = {"Authorization": `Bearer ${jwtToken}`};
      const [ozetR, audR, kulR] = await Promise.all([
        fetch("/api/v1/admin/ozet", {headers}),
        fetch("/api/v1/admin/denetim-kayitlari?limit=40", {headers}),
        fetch("/api/v1/admin/kullanicilar", {headers})
      ]);
      const ozet = await ozetR.json();
      const aud = await audR.json();
      const kull = await kulR.json();

      if (ozet.metrikler) {
        const m = ozet.metrikler;
        document.getElementById("adminMetrikler").innerHTML = `
          <div class="kpi-card"><div class="kpi-label">Aktif Kulüp (Tenant)</div><div class="kpi-val">${m.aktif_kulup_sayisi}</div><div class="kpi-sub">Çok-kulüplü izolasyon aktif</div></div>
          <div class="kpi-card"><div class="kpi-label">Kayıtlı Sporcu</div><div class="kpi-val">${m.toplam_sporcu}</div><div class="kpi-sub">KVKK açık rıza onaylı</div></div>
          <div class="kpi-card"><div class="kpi-label">Toplam Saha Ölçümü</div><div class="kpi-val">${m.toplam_olcum_satiri}</div><div class="kpi-sub">${m.toplam_ilgi_anketi} ilgi anketi kaydı</div></div>
          <div class="kpi-card"><div class="kpi-label">KVKK Denetim İzi</div><div class="kpi-val">${m.toplam_denetim_kaydi}</div><div class="kpi-sub">Yerli Sunucu: ${Math.round((ozet.yerli_sunucu?.boyut_bayt || 0)/1024)} KB</div></div>
        `;
      }

      if (ozet.kulup_dagilimi) {
        let kt = `<table><thead><tr><th>Kulüp Kodu</th><th>Kulüp Adı</th><th>Şehir</th><th>Sporcu</th><th>Ölçüm</th><th>İşlem</th></tr></thead><tbody>`;
        ozet.kulup_dagilimi.forEach(k => {
          kt += `<tr>
            <td><code>${k.kod}</code></td>
            <td><strong>${k.ad}</strong></td>
            <td>${k.sehir || "—"}</td>
            <td><span class="badge">${k.sporcu_sayisi}</span></td>
            <td><span class="badge green">${k.olcum_sayisi}</span></td>
            <td><button class="btn outline sm" onclick="window.open('/api/v1/kulupler/${k.kod}/rapor','_blank')">A4 Rapor</button></td>
          </tr>`;
        });
        kt += `</tbody></table>`;
        document.getElementById("adminKulupTablosu").innerHTML = kt;
      }

      if (kull.kullanicilar) {
        let ut = `<table><thead><tr><th>Ad Soyad</th><th>E-posta</th><th>Rol</th><th>Kulüp</th></tr></thead><tbody>`;
        kull.kullanicilar.forEach(u => {
          ut += `<tr>
            <td><strong>${u.ad_soyad}</strong></td>
            <td>${u.eposta}</td>
            <td><span class="badge">${u.rol}</span></td>
            <td>${u.kulup_kodu || "merkez"}</td>
          </tr>`;
        });
        ut += `</tbody></table>`;
        document.getElementById("adminKullaniciTablosu").innerHTML = ut;
      }

      const kvkkSel = document.getElementById("kvkkSporcuSecici");
      kvkkSel.innerHTML = tumSporcular.map(s => `<option value="${s.id}">${s.tam_ad} (${s.kulup_kodu})</option>`).join("");

      const satirlar = (aud.denetim_kayitlari || []).map(k => `
        <tr>
          <td style="white-space:nowrap;">${k.zaman}</td>
          <td><span class="badge">${k.islem_turu}</span></td>
          <td><strong>${k.kullanici_eposta}</strong> <span style="color:var(--muted);">(${k.rol})</span></td>
          <td><code>${k.hedef_tablo}:${k.hedef_id}</code></td>
          <td>${k.neden || ""}</td>
        </tr>
      `).join("");
      document.getElementById("denetimTablosuKapsayici").innerHTML = `
        <table><thead><tr><th>Zaman (UTC)</th><th>İşlem Türü</th><th>Yetkili Kullanıcı</th><th>Hedef Kayıt</th><th>Açıklama / Gerekçe</th></tr></thead><tbody>${satirlar}</tbody></table>
      `;
    }

    async function adminYedekAl() {
      const r = await fetch("/api/v1/admin/yedekle", {
        method: "POST",
        headers: {"Authorization": `Bearer ${jwtToken}`}
      });
      const d = await r.json();
      if (r.ok) {
        bildirim(`Yerli sunucu yedeği alındı: ${d.dosya}`);
        adminYukle();
      }
    }

    async function adminDemoYukle() {
      const r = await fetch("/api/v1/admin/demo-yukle", {
        method: "POST",
        headers: {"Authorization": `Bearer ${jwtToken}`}
      });
      if (r.ok) {
        bildirim("Demo veri paketi başarıyla senkronize edildi.");
        await sporculariYukle();
        await adminYukle();
      }
    }

    async function yeniKulupEkle() {
      const kod = document.getElementById("yeniKulupKod").value;
      const ad = document.getElementById("yeniKulupAd").value;
      const sehir = document.getElementById("yeniKulupSehir").value;
      const r = await fetch("/api/v1/admin/kulupler", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`},
        body: JSON.stringify({kod, ad, sehir, branslar: ["Genel Atletik Performans"]})
      });
      if (r.ok) {
        const sel = document.getElementById("kulupSecici");
        const opt = document.createElement("option");
        opt.value = kod;
        opt.textContent = `${kod} — ${ad} (${sehir})`;
        sel.appendChild(opt);
        bildirim(`Yeni kulüp tanımlandı: ${ad}`);
        adminYukle();
      }
    }

    async function yeniKullaniciOlustur() {
      const payload = {
        eposta: document.getElementById("ykEposta").value,
        ad_soyad: document.getElementById("ykAdSoyad").value,
        parola: document.getElementById("ykParola").value,
        rol: document.getElementById("ykRol").value,
        kulup_kodu: document.getElementById("kulupSecici").value
      };
      const r = await fetch("/api/v1/admin/kullanicilar", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`},
        body: JSON.stringify(payload)
      });
      if (r.ok) {
        bildirim(`Yeni kullanıcı yetkilendirildi: ${payload.eposta}`);
        adminYukle();
      } else {
        const h = await r.json();
        bildirim(`Hata: ${h.hata || "Yetkilendirme başarısız"}`);
      }
    }

    async function kvkkSporcuAnonimlestir() {
      const sporcuId = document.getElementById("kvkkSporcuSecici").value;
      const neden = document.getElementById("kvkkNeden").value || "Veli KVKK unutulma hakkı başvurusu";
      const r = await fetch("/api/v1/admin/kvkk/anonimlestir", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`},
        body: JSON.stringify({sporcu_id: sporcuId, neden})
      });
      if (r.ok) {
        const d = await r.json();
        bildirim(`Sporcu kimliği KVKK kapsamında anonimleştirildi: ${d.yeni_kod}`);
        await sporculariYukle();
        await adminYukle();
      }
    }

    window.addEventListener("DOMContentLoaded", async () => {
      const kayitliTema = localStorage.getItem("performtest_tema");
      if (kayitliTema) document.documentElement.setAttribute("data-theme", kayitliTema);
      await hizliGiris("admin@performtest.yerli", "PerformAdmin2026!");
      await sporculariYukle();
      if (window.location.pathname.startsWith("/admin")) {
        sekmeAc("admin", document.querySelectorAll(".nav-item")[4]);
      }
    });
  </script>
</body>
</html>
"""
