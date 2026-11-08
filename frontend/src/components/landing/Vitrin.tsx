"use client";

import React, { useState } from "react";
import {
  Activity,
  Award,
  BarChart3,
  Building2,
  CheckCircle2,
  ChevronRight,
  Compass,
  FileCheck2,
  FileSpreadsheet,
  FileText,
  Fingerprint,
  Globe2,
  Lock,
  LogIn,
  Moon,
  Play,
  RotateCcw,
  Scale,
  Search,
  ShieldCheck,
  Sparkles,
  Sun,
  UserCheck,
  X,
  Zap,
} from "lucide-react";

interface VitrinProps {
  onGirisBasarili: (token: string, kullanici: any) => void;
  onDemoGiris: (rolEposta?: string, parola?: string) => void;
}

export const Vitrin: React.FC<VitrinProps> = ({ onGirisBasarili, onDemoGiris }) => {
  const [girisModalAcik, setGirisModalAcik] = useState(false);
  const [eposta, setEposta] = useState("admin@performtest.yerli");
  const [parola, setParola] = useState("PerformAdmin2026!");
  const [hata, setHata] = useState<string | null>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [tema, setTema] = useState<"light" | "dark">("dark");

  const toggleTema = () => {
    const yeni = tema === "dark" ? "light" : "dark";
    setTema(yeni);
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", yeni);
    }
  };

  const girisFormGonder = async (e: React.FormEvent) => {
    e.preventDefault();
    setHata(null);
    setYukleniyor(true);
    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eposta, parola }),
      });
      const d = await res.json();
      if (!res.ok || !d.access_token) {
        throw new Error(d.hata || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
      }
      onGirisBasarili(d.access_token, d.kullanici);
    } catch (err: any) {
      setHata(err.message || "Giriş yapılamadı.");
    } finally {
      setYukleniyor(false);
    }
  };

  const hizliDemoRolSec = (rolEposta: string, rolParola: string) => {
    setEposta(rolEposta);
    setParola(rolParola);
    onDemoGiris(rolEposta, rolParola);
  };

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] flex flex-col font-sans transition-colors duration-200">
      {/* ── Üst Menü / Navbar ── */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[var(--surface)]/90 border-b border-[var(--line)] px-6 py-3.5 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="font-extrabold text-base tracking-tight flex items-center gap-2">
              PerformTest
              <span className="text-[10px] uppercase font-black px-1.5 py-0.5 rounded-md bg-blue-500/10 text-blue-500 border border-blue-500/20">
                Studio Next
              </span>
            </div>
            <div className="text-[11px] text-[var(--muted)] font-medium">
              Biyomekanik Analiz & Yetenek Platformu
            </div>
          </div>
        </div>

        <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-[var(--muted)]">
          <a href="#ozellikler" className="hover:text-[var(--text)] transition">Özellikler</a>
          <a href="#metodoloji" className="hover:text-[var(--text)] transition">Bilimsel LMS Metodu</a>
          <a href="#katalog" className="hover:text-[var(--text)] transition">196 Test Kataloğu</a>
          <a href="#kvkk" className="hover:text-[var(--text)] transition">KVKK & Güvenlik</a>
        </nav>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleTema}
            className="p-2 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] transition text-[var(--muted)]"
            title="Tema Değiştir"
          >
            {tema === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-blue-600" />}
          </button>
          <button
            onClick={() => onDemoGiris("admin@performtest.yerli", "PerformAdmin2026!")}
            className="hidden sm:flex items-center gap-1.5 text-xs font-bold px-3.5 py-2 rounded-xl border border-blue-500/30 bg-blue-500/10 hover:bg-blue-500/20 text-blue-500 transition"
          >
            <Zap className="w-3.5 h-3.5" />
            Hızlı Demo
          </button>
          <button
            onClick={() => setGirisModalAcik(true)}
            className="flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/25 transition hover:scale-[1.02]"
          >
            <LogIn className="w-3.5 h-3.5" />
            Panele Giriş Yap
          </button>
        </div>
      </header>

      {/* ── Hero Bölümü ── */}
      <section className="relative overflow-hidden pt-16 pb-20 px-6 border-b border-[var(--line)]">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/25 text-blue-500 text-xs font-bold shadow-sm">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>PerformTest Studio 2.0 — Bilimsel Atletik Analiz & Yetenek Seçimi</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
            Sporcu Performansı, Biyomekanik Analiz ve{" "}
            <span className="bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 bg-clip-text text-transparent">
              Bilimsel Yetenek Seçimi
            </span>
          </h1>

          <p className="text-sm sm:text-base text-[var(--muted)] max-w-3xl mx-auto leading-relaxed">
            Cole &amp; Green (1992) LMS Z-skorları, TSYT ulusal norm tabanı, 196 testlik protokol kütüphanesi ve Opstoel (2015) 6 branş grubu eşleştirme motoruyla kulüpler, akademiler ve federasyonlar için yerli sunucu altyapısı.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
            <button
              onClick={() => onDemoGiris("admin@performtest.yerli", "PerformAdmin2026!")}
              className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-sm shadow-xl shadow-blue-500/30 transition hover:scale-[1.03]"
            >
              <Play className="w-4 h-4 fill-current" />
              Sistemi Canlı İncele (Demo)
            </button>
            <button
              onClick={() => setGirisModalAcik(true)}
              className="flex items-center gap-2 px-6 py-3.5 rounded-2xl border border-[var(--line)] bg-[var(--surface)] hover:bg-[var(--surface-2)] text-xs font-extrabold transition"
            >
              <Lock className="w-4 h-4 text-[var(--muted)]" />
              Kulüp Hesabı ile Giriş
            </button>
          </div>

          {/* İstatistik Göstergeleri */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-12 max-w-4xl mx-auto">
            <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--line)] shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-blue-500">196</div>
              <div className="text-xs font-bold text-[var(--muted)] mt-1">Bilimsel Test Protokolü</div>
            </div>
            <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--line)] shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-emerald-500">191</div>
              <div className="text-xs font-bold text-[var(--muted)] mt-1">Uluslararası Kaynakça</div>
            </div>
            <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--line)] shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-amber-500">6 Branş</div>
              <div className="text-xs font-bold text-[var(--muted)] mt-1">Opstoel Yetenek Grubu</div>
            </div>
            <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--line)] shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-purple-500">%100</div>
              <div className="text-xs font-bold text-[var(--muted)] mt-1">Yerli Sunucu & KVKK</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 5 Temel Çalışma Alanı ── */}
      <section id="ozellikler" className="py-20 px-6 border-b border-[var(--line)]">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight">5 Bütünleşik Çalışma Alanı</h2>
            <p className="text-xs sm:text-sm text-[var(--muted)] max-w-2xl mx-auto">
              Saha ölçümünden veli raporuna, ikili başa baş sporcu karşılaştırmasından KVKK audit log yönetimine kadar uçtan uca modern mimari.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Kart 1: Sporcu Analiz */}
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] shadow-sm space-y-3 hover:border-blue-500/50 transition">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-blue-500 flex items-center justify-center font-bold">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-base">Sporcu Performans Laboratuvarı</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Çok boyutlu biyomotor LMS radar profili, yaş-cinsiyet persentil dağılımları, VKİ ve A4 formatında tek tıkla veli ve antrenör gelişim raporları.
              </p>
            </div>

            {/* Kart 2: Saha Ölçüm */}
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] shadow-sm space-y-3 hover:border-emerald-500/50 transition">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-base">Saha Ölçüm & Canlı Test Oturumu</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Fizyolojik makul aralık ve eşik filtresi, hatalı veri giriş engeli ve gerçek zamanlı izometrik SVG biyomekanik sahnesi simülasyonu.
              </p>
            </div>

            {/* Kart 3: Karşılaştırma */}
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] shadow-sm space-y-3 hover:border-amber-500/50 transition">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center font-bold">
                <Scale className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-base">Karşılaştırma Laboratuvarı</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                İki sporcunun başa baş Z-skoru farkı (&Delta;Z), çift katmanlı radar haritası ve mevkilere göre güçlü/geliştirilecek yön ayrımı.
              </p>
            </div>

            {/* Kart 4: Katalog & Kaynakça */}
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] shadow-sm space-y-3 hover:border-purple-500/50 transition">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-500 flex items-center justify-center font-bold">
                <Compass className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-base">196 Test Kataloğu & 191 Kaynakça</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                TSYT, Eurofit, ALPHA, BOT-2 bataryaları; her testin uygulama protokolü, birimi, izometrik çizimi ve hakemli bilimsel makale atıfları.
              </p>
            </div>

            {/* Kart 5: Yönetim & KVKK */}
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] shadow-sm space-y-3 hover:border-rose-500/50 transition md:col-span-2">
              <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center font-bold">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-base">Çok-Kiracılı (Multi-Tenant) Kulüp & KVKK Merkezi</h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                Kulüplerin verileri sunucu katmanında %100 izoledir. 6698 sayılı KVKK Madde 7 ve 11 uyarınca tek tıkla kimlik anonimleştirme (maskeleme), silinemez audit log denetim izi ve yerli SQLite/PostgreSQL otomatik yedekleme.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Bilimsel Metodoloji & LMS Modeli ── */}
      <section id="metodoloji" className="py-20 px-6 border-b border-[var(--line)] bg-[var(--surface-2)]">
        <div className="max-w-5xl mx-auto space-y-10">
          <div className="text-center space-y-3">
            <div className="text-xs font-bold text-blue-500 uppercase tracking-wider">Matematiksel ve Bilimsel Temel</div>
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight">Cole &amp; Green LMS Z-Skoru ve Opstoel Modeli</h2>
            <p className="text-xs sm:text-sm text-[var(--muted)] max-w-2xl mx-auto">
              Sistem rastgele puanlama yapmaz; dünya standartlarında hakemli spor hekimliği ve pediatri norm modellerini çalıştırır.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] space-y-4">
              <h3 className="font-extrabold text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-500" />
                LMS Box-Cox Dönüşüm Formülü
              </h3>
              <div className="p-4 rounded-2xl bg-[var(--bg)] border border-[var(--line)] font-mono text-xs text-blue-500 text-center">
                Z = [ (X / M)^L - 1 ] / (L · S) &nbsp;(L &ne; 0)
              </div>
              <ul className="text-xs text-[var(--muted)] space-y-2">
                <li>• <strong>L (Lambda):</strong> Çarpıklık parametresi (Box-Cox güç dönüşümü)</li>
                <li>• <strong>M (Mu):</strong> Yaş ve cinsiyete özgü medyan (50. persentil)</li>
                <li>• <strong>S (Sigma):</strong> Varyasyon katsayısı (dağılım genişliği)</li>
                <li>• <strong>Kaynaklar:</strong> TSYT (Türkiye Sportif Yetenek Modeli), Tomkinson et al. (2018), De Onis et al. (WHO 2007).</li>
              </ul>
            </div>

            <div className="p-6 rounded-3xl bg-[var(--surface)] border border-[var(--line)] space-y-4">
              <h3 className="font-extrabold text-sm flex items-center gap-2">
                <Compass className="w-4 h-4 text-emerald-500" />
                Opstoel (2015) Branş Yönlendirme & &quot;Belirgin Fark Yok&quot; Kuralı
              </h3>
              <p className="text-xs text-[var(--muted)] leading-relaxed">
                6 ana branş grubunun (Top sporları, Dans, Jimnastik, Dövüş, Raket sporları, Yüzme) motorik gereksinimleri sporcunun Z-profiliyle ağırlıklı Öklid mesafesi üzerinden karşılaştırılır.
              </p>
              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-600 dark:text-amber-400">
                ⚠️ <strong>Belirgin Fark Yok Kuralı:</strong> İki branş arasındaki fark &lt; 0.15 ise sistem çocuğu erken özelleşmeye zorlamaz; &quot;Çok Yönlü Branşlaşma Tavsiye Edilir&quot; bilimsel kararı üretir.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Alt Bilgi / Footer ── */}
      <footer className="mt-auto py-8 px-6 border-t border-[var(--line)] bg-[var(--surface)] text-center text-xs text-[var(--muted)] space-y-2">
        <div className="font-bold text-[var(--text)]">
          PerformTest Studio — Atletik Performans, Biyomekanik Analiz ve Yetenek Seçimi Platformu
        </div>
        <div>
          © 2026 PerformTest · Tüm hakları saklıdır. · 6698 Sayılı KVKK Uyumlu Yerli Sunucu Çözümü
        </div>
      </footer>

      {/* ── Giriş / Oturum Açma Modalı ── */}
      {girisModalAcik && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[var(--surface)] border border-[var(--line)] rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm tracking-tight">PerformTest Studio Girişi</h3>
                  <p className="text-[11px] text-[var(--muted)]">Yetkili kulüp veya antrenör hesabı</p>
                </div>
              </div>
              <button
                onClick={() => setGirisModalAcik(false)}
                className="p-1.5 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] text-[var(--muted)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {hata && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-semibold">
                {hata}
              </div>
            )}

            <form onSubmit={girisFormGonder} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[var(--muted)] mb-1">E-Posta Adresi</label>
                <input
                  type="email"
                  required
                  value={eposta}
                  onChange={(e) => setEposta(e.target.value)}
                  className="w-full text-xs px-3.5 py-2.5 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="admin@performtest.yerli"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[var(--muted)] mb-1">Parola</label>
                <input
                  type="password"
                  required
                  value={parola}
                  onChange={(e) => setParola(e.target.value)}
                  className="w-full text-xs px-3.5 py-2.5 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={yukleniyor}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-md shadow-blue-500/20 transition disabled:opacity-50"
              >
                {yukleniyor ? "Doğrulanıyor..." : "Oturum Aç ve Panele Gir"}
              </button>
            </form>

            {/* Hızlı Demo Rolleri Seçici */}
            <div className="pt-3 border-t border-[var(--line)] space-y-2">
              <div className="text-[11px] font-bold text-[var(--muted)] text-center">
                Veya Tek Tıkla Demo Hesabı Seçin:
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => hizliDemoRolSec("admin@performtest.yerli", "PerformAdmin2026!")}
                  className="p-2 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] hover:border-blue-500 text-left text-[11px] transition"
                >
                  <div className="font-bold text-blue-500">👑 Süper Admin</div>
                  <div className="text-[10px] text-[var(--muted)] truncate">Tüm Kulüpler &amp; KVKK</div>
                </button>

                <button
                  type="button"
                  onClick={() => hizliDemoRolSec("kulup-a@performtest.yerli", "Kulup123!")}
                  className="p-2 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] hover:border-blue-500 text-left text-[11px] transition"
                >
                  <div className="font-bold text-emerald-500">🏢 Kulüp Yöneticisi</div>
                  <div className="text-[10px] text-[var(--muted)] truncate">Ankara Gençlik SK</div>
                </button>

                <button
                  type="button"
                  onClick={() => hizliDemoRolSec("antrenor@performtest.yerli", "Koc123!")}
                  className="p-2 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] hover:border-blue-500 text-left text-[11px] transition"
                >
                  <div className="font-bold text-amber-500">⏱️ Baş Antrenör</div>
                  <div className="text-[10px] text-[var(--muted)] truncate">Saha Ölçüm &amp; Z-Skor</div>
                </button>

                <button
                  type="button"
                  onClick={() => hizliDemoRolSec("veli@performtest.yerli", "Veli123!")}
                  className="p-2 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] hover:border-blue-500 text-left text-[11px] transition"
                >
                  <div className="font-bold text-rose-500">👨‍👩‍👦 Sporcu Velisi</div>
                  <div className="text-[10px] text-[var(--muted)] truncate">A4 Gelişim Raporu</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

