"use client";

import React, { useState } from "react";
import {
  Activity,
  Moon,
  Sun,
  FileSpreadsheet,
  FileText,
  Building2,
  Lock,
  LogOut,
  Menu,
} from "lucide-react";

interface NavbarProps {
  aktifKulup: string;
  onKulupDegis: (kod: string) => void;
  kulupler: Array<{ kod: string; ad: string }>;
  kullaniciAdi: string;
  rol: string;
  onRolDegis: (epostaParola: string) => void;
  onCikisYap?: () => void;
  onMobilMenuAc?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  aktifKulup,
  onKulupDegis,
  kulupler,
  rol,
  onRolDegis,
  onCikisYap,
  onMobilMenuAc,
}) => {
  const [tema, setTema] = useState<"dark" | "light">("dark");

  const toggleTema = () => {
    const yeni = tema === "dark" ? "light" : "dark";
    setTema(yeni);
    document.documentElement.setAttribute("data-theme", yeni);
  };

  const isVeli = rol === "sporcu_veli" || rol === "veli";
  const isAntrenor = rol === "antrenor";
  const isKulupAdmin = rol === "kulup_yoneticisi";
  const isSuperAdmin = rol === "super_admin";
  const aktifKulupObj = kulupler.find((k) => k.kod === aktifKulup);

  const rolSelectDegeri = isVeli
    ? "veli@performetre.yerli|Veli123!"
    : isAntrenor
    ? "antrenor@performetre.yerli|Koc123!"
    : isKulupAdmin
    ? "kulup-a@performetre.yerli|Kulup123!"
    : "admin@performetre.yerli|PerformAdmin2026!";

  return (
    <header className="h-14 sm:h-16 border-b border-[var(--line)] bg-[var(--surface)] px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm gap-2">
      <div className="flex items-center gap-2 sm:gap-5 min-w-0">
        {/* Mobil Hamburger Menü Düğmesi */}
        {onMobilMenuAc && (
          <button
            onClick={onMobilMenuAc}
            className="lg:hidden p-2 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] text-[var(--text)] hover:text-blue-500 transition shrink-0"
            aria-label="Menüyü Aç"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Activity className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
          </div>
          <div className="min-w-0">
            <div className="font-extrabold text-sm sm:text-base tracking-tight flex items-center gap-1.5 truncate">
              <span>Performetre</span>
              <span className="hidden xs:inline-block text-[9px] sm:text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500 border border-blue-500/20">
                Studio
              </span>
            </div>
            <div className="hidden sm:block text-xs text-[var(--muted)] font-medium truncate">
              Performans Ölçme ve Değerlendirme Platformu
            </div>
          </div>
        </div>

        {/* Kulüp Alanı (Süper admin değiştirebilir, diğerleri kendi kulübüne kilitlidir) */}
        {!isVeli && (
          <div className="hidden md:flex items-center gap-2 pl-4 border-l border-[var(--line)]">
            <Building2 className="w-4 h-4 text-[var(--muted)]" />
            <span className="text-xs font-semibold text-[var(--muted)]">Kulüp:</span>
            {isSuperAdmin ? (
              <select
                value={aktifKulup}
                onChange={(e) => onKulupDegis(e.target.value)}
                className="text-xs font-semibold bg-[var(--surface-2)] border border-[var(--line)] rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {kulupler.map((k) => (
                  <option key={k.kod} value={k.kod}>
                    {k.ad} ({k.kod})
                  </option>
                ))}
              </select>
            ) : (
              <span className="text-xs font-bold px-2 py-1 rounded bg-[var(--surface-2)] border border-[var(--line)] text-[var(--text)]">
                {aktifKulupObj?.ad || aktifKulup}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
        {/* Kullanıcı Rol Rozeti */}
        <div className="hidden xl:flex items-center gap-1.5">
          <span
            className={`text-[11px] font-extrabold px-2.5 py-1 rounded-lg border ${
              isVeli
                ? "bg-amber-500/10 text-amber-500 border-amber-500/20"
                : isAntrenor
                ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                : isKulupAdmin
                ? "bg-blue-500/10 text-blue-500 border-blue-500/20"
                : "bg-purple-500/10 text-purple-500 border-purple-500/20"
            }`}
          >
            {isVeli ? "👨‍👩‍👦 Veli" : isAntrenor ? "🏃 Antrenör" : isKulupAdmin ? "🏢 Kulüp Yöneticisi" : "⚡ Süper Admin"}
          </span>
        </div>

        {/* Hızlı Rapor Düğmeleri - Yalnızca Yetkili Rollere */}
        {!isVeli && (
          <button
            onClick={() => window.open(`/api/v1/kulupler/${encodeURIComponent(aktifKulup)}/rapor`, "_blank")}
            className="hidden md:flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
            title="Kulüp A4 Gelişim Raporu"
          >
            <FileText className="w-3.5 h-3.5 text-blue-500" />
            Kulüp Raporu
          </button>
        )}

        {(isSuperAdmin || isKulupAdmin) && (
          <button
            onClick={() => {
              window.location.href = `/api/v1/admin/disa-aktar/${encodeURIComponent(aktifKulup)}`;
            }}
            className="hidden md:flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
            title="Excel / CSV Veri Paketi"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
            Excel (.zip)
          </button>
        )}

        {/* Rol Simülatörü */}
        <div className="flex items-center gap-1 sm:gap-2 bg-[var(--surface-2)] border border-[var(--line)] rounded-lg px-2 py-1">
          <Lock className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-amber-500 shrink-0" />
          <select
            value={rolSelectDegeri}
            onChange={(e) => onRolDegis(e.target.value)}
            className="text-[11px] sm:text-xs font-semibold bg-transparent border-0 focus:outline-none max-w-[105px] sm:max-w-none truncate"
          >
            <option value="admin@performetre.yerli|PerformAdmin2026!">Süper Admin</option>
            <option value="kulup-a@performetre.yerli|Kulup123!">Kulüp Yöneticisi</option>
            <option value="antrenor@performetre.yerli|Koc123!">Ölçüm Antrenörü</option>
            <option value="veli@performetre.yerli|Veli123!">Sporcu Velisi</option>
          </select>
        </div>

        {/* Tema Değiştirici */}
        <button
          onClick={toggleTema}
          className="p-2 rounded-lg border border-[var(--line)] bg-[var(--surface-2)] hover:text-blue-500 transition shrink-0"
          aria-label="Tema Değiştir"
        >
          {tema === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-blue-600" />}
        </button>

        {/* Çıkış Yap / Vitrine Dön */}
        {onCikisYap && (
          <button
            onClick={onCikisYap}
            className="flex items-center gap-1.5 text-xs font-bold p-2 sm:px-3 sm:py-1.5 rounded-lg border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-500 transition shrink-0"
            title="Oturumu Kapat ve Vitrin Sitesine Dön"
          >
            <LogOut className="w-4 h-4 sm:w-3.5 sm:h-3.5" />
            <span className="hidden sm:inline">Vitrine Dön</span>
          </button>
        )}
      </div>
    </header>
  );
};

