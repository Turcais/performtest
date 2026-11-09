"use client";

import React from "react";
import {
  Users,
  Timer,
  Scale,
  BookOpen,
  ShieldCheck,
  Server,
  X,
  Building2,
  FileText,
  FileSpreadsheet,
} from "lucide-react";

export type SekmeTipi = "analiz" | "oturum" | "karsilastir" | "katalog" | "admin";

interface SidebarProps {
  aktifSekme: SekmeTipi;
  onSekmeSec: (sekme: SekmeTipi) => void;
  toplamSporcu: number;
  toplamTest?: number;
  toplamKaynakca?: number;
  rol?: string;
  mobilMenuAcik?: boolean;
  onMobilMenuKapat?: () => void;
  aktifKulup?: string;
  onKulupDegis?: (kod: string) => void;
  kulupler?: Array<{ kod: string; ad: string }>;
}

export const Sidebar: React.FC<SidebarProps> = ({
  aktifSekme,
  onSekmeSec,
  toplamSporcu,
  toplamTest = 196,
  toplamKaynakca = 191,
  rol = "super_admin",
  mobilMenuAcik = false,
  onMobilMenuKapat,
  aktifKulup = "merkez",
  onKulupDegis,
  kulupler = [],
}) => {
  const isVeli = rol === "sporcu_veli" || rol === "veli";
  const isAntrenor = rol === "antrenor";
  const isKulupAdmin = rol === "kulup_yoneticisi";
  const isSuperAdmin = rol === "super_admin";

  const tumMenuler: Array<{
    id: SekmeTipi;
    etiket: string;
    kisaEtiket: string;
    alt: string;
    ikon: React.ElementType;
    badge?: string;
    roller: string[];
  }> = [
    {
      id: "analiz",
      etiket: isVeli ? "Sporcu Gelişim Raporu & Karne" : "Sporcu Performans Laboratuvarı",
      kisaEtiket: isVeli ? "Karnem" : "Analiz",
      alt: isVeli ? "LMS Z-Skor & Biyomotor Profil" : "LMS Z-Skor, Radar & Profil",
      ikon: Users,
      badge: `${toplamSporcu}`,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor", "sporcu_veli", "veli"],
    },
    {
      id: "oturum",
      etiket: "Saha Ölçüm & Sonuç Girdisi",
      kisaEtiket: "Saha Ölçüm",
      alt: "Anlık Eşik, Hata & Rekor Filtresi",
      ikon: Timer,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor"],
    },
    {
      id: "karsilastir",
      etiket: "Başa Baş Karşılaştırma",
      kisaEtiket: "Kıyasla",
      alt: "Çift Sporcu Karşılaştırma & Fark",
      ikon: Scale,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor"],
    },
    {
      id: "katalog",
      etiket: isVeli ? `${toplamTest} Test & Hareket Kataloğu` : `${toplamTest} Test & Performans Ölçme Kataloğu`,
      kisaEtiket: "Katalog",
      alt: isVeli ? "Test Protokolleri & Bilgilendirme" : `SVG Animasyon & ${toplamKaynakca} Kaynakça`,
      ikon: BookOpen,
      badge: `${toplamTest}`,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor", "sporcu_veli", "veli"],
    },
    {
      id: "admin",
      etiket: isKulupAdmin ? "Kulüp Yönetimi & KVKK" : "Performetre Yönetim & KVKK",
      kisaEtiket: "Yönetim",
      alt: isKulupAdmin ? "Kulüp İçi Sporcu & İzin Kayıtları" : "Tenant, RBAC & Denetim İzi",
      ikon: ShieldCheck,
      roller: ["super_admin", "kulup_yoneticisi"],
    },
  ];

  const menuler = tumMenuler.filter((m) => m.roller.includes(rol));

  const sekmeSecVeKapat = (id: SekmeTipi) => {
    onSekmeSec(id);
    if (onMobilMenuKapat) onMobilMenuKapat();
  };

  return (
    <>
      {/* 1. Masaüstü Sol Yan Menü (lg ve üzeri) */}
      <aside className="hidden lg:flex w-72 border-r border-[var(--line)] bg-[var(--surface)] flex-col justify-between shrink-0 p-4 min-h-[calc(100vh-4rem)]">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--muted)] px-3 mb-3 flex items-center justify-between">
            <span>{isVeli ? "Veli Portalı Modülleri" : isAntrenor ? "Antrenör & Ölçüm Modülleri" : "Performans & Saha Modülleri"}</span>
            {isVeli && (
              <span className="text-[10px] bg-amber-500/10 text-amber-500 border border-amber-500/20 px-2 py-0.5 rounded-full font-bold">
                Veli Erişimi
              </span>
            )}
          </div>

          <nav className="space-y-1.5">
            {menuler.map((m) => {
              const Ikon = m.ikon;
              const aktif = aktifSekme === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => onSekmeSec(m.id)}
                  className={`w-full flex items-start gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
                    aktif
                      ? "bg-blue-600 text-white font-bold shadow-md shadow-blue-500/20"
                      : "hover:bg-[var(--surface-2)] text-[var(--text)] font-medium"
                  }`}
                >
                  <Ikon className={`w-5 h-5 shrink-0 mt-0.5 ${aktif ? "text-white" : "text-blue-500"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs truncate flex items-center justify-between">
                      <span>{m.etiket}</span>
                      {m.badge && (
                        <span
                          className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                            aktif ? "bg-white/20 text-white" : "bg-[var(--surface-2)] text-[var(--muted)]"
                          }`}
                        >
                          {m.badge}
                        </span>
                      )}
                    </div>
                    <div
                      className={`text-[11px] truncate mt-0.5 ${
                        aktif ? "text-blue-100 font-normal" : "text-[var(--muted)]"
                      }`}
                    >
                      {m.alt}
                    </div>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Yerli Sunucu & KVKK Durum Rozeti */}
        <div className="p-3.5 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] space-y-2 mt-6">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-500">
            <Server className="w-4 h-4" />
            <span>Yerli Sunucu (On-Premise)</span>
          </div>
          <p className="text-[11px] text-[var(--muted)] leading-relaxed">
            6698 Sayılı KVKK Madde 7 & 11 uyumlu. Tüm performans ölçüm verileri kurum içi sunucuda saklanmaktadır.
          </p>
          <div className="flex items-center justify-between text-[10px] pt-1 border-t border-[var(--line)] text-[var(--muted)] font-mono">
            <span>Sürüm: v2.4 (Next.js)</span>
            <span className="text-emerald-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
              Canlı
            </span>
          </div>
        </div>
      </aside>

      {/* 2. Mobil Kayar Çekmece (Drawer) - Hamburger Tıklandığında */}
      {mobilMenuAcik && (
        <div
          className="fixed inset-0 z-50 lg:hidden bg-black/60 backdrop-blur-sm flex"
          onClick={onMobilMenuKapat}
        >
          <div
            className="w-80 max-w-[85vw] bg-[var(--surface)] border-r border-[var(--line)] h-full flex flex-col justify-between p-4 overflow-y-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
                <div className="font-extrabold text-sm">Performetre Menü</div>
                <button
                  onClick={onMobilMenuKapat}
                  className="p-1.5 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)]"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Mobil Kulüp Seçici */}
              {!isVeli && kulupler.length > 0 && (
                <div className="p-3 rounded-xl bg-[var(--surface-2)] border border-[var(--line)] space-y-1.5">
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-[var(--muted)]">
                    <Building2 className="w-3.5 h-3.5 text-blue-500" />
                    <span>Aktif Kulüp / Merkez</span>
                  </div>
                  {isSuperAdmin && onKulupDegis ? (
                    <select
                      value={aktifKulup}
                      onChange={(e) => onKulupDegis(e.target.value)}
                      className="w-full text-xs font-bold bg-[var(--surface)] border border-[var(--line)] rounded-lg p-2 focus:outline-none"
                    >
                      {kulupler.map((k) => (
                        <option key={k.kod} value={k.kod}>
                          {k.ad} ({k.kod})
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-xs font-extrabold px-2 py-1 rounded bg-[var(--surface)] border border-[var(--line)]">
                      {kulupler.find((k) => k.kod === aktifKulup)?.ad || aktifKulup}
                    </div>
                  )}
                </div>
              )}

              {/* Mobil Navigasyon */}
              <nav className="space-y-1.5">
                {menuler.map((m) => {
                  const Ikon = m.ikon;
                  const aktif = aktifSekme === m.id;
                  return (
                    <button
                      key={m.id}
                      onClick={() => sekmeSecVeKapat(m.id)}
                      className={`w-full flex items-start gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
                        aktif
                          ? "bg-blue-600 text-white font-bold shadow-md shadow-blue-500/20"
                          : "hover:bg-[var(--surface-2)] text-[var(--text)] font-medium"
                      }`}
                    >
                      <Ikon className={`w-5 h-5 shrink-0 mt-0.5 ${aktif ? "text-white" : "text-blue-500"}`} />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs truncate flex items-center justify-between">
                          <span>{m.etiket}</span>
                          {m.badge && (
                            <span
                              className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                                aktif ? "bg-white/20 text-white" : "bg-[var(--surface-2)] text-[var(--muted)]"
                              }`}
                            >
                              {m.badge}
                            </span>
                          )}
                        </div>
                        <div
                          className={`text-[11px] truncate mt-0.5 ${
                            aktif ? "text-blue-100 font-normal" : "text-[var(--muted)]"
                          }`}
                        >
                          {m.alt}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </nav>

              {/* Mobil Hızlı Rapor & Veri İhracı Butonları */}
              {!isVeli && (
                <div className="pt-2 border-t border-[var(--line)] space-y-2">
                  <div className="text-[11px] font-bold text-[var(--muted)] px-1">Hızlı Çıktı & Raporlar</div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => window.open(`/api/v1/kulupler/${encodeURIComponent(aktifKulup)}/rapor`, "_blank")}
                      className="flex items-center justify-center gap-1.5 text-xs font-semibold p-2.5 rounded-xl border border-[var(--line)] bg-[var(--surface-2)]"
                    >
                      <FileText className="w-3.5 h-3.5 text-blue-500" />
                      Kulüp Raporu
                    </button>
                    {(isSuperAdmin || isKulupAdmin) && (
                      <button
                        onClick={() => {
                          window.location.href = `/api/v1/admin/disa-aktar/${encodeURIComponent(aktifKulup)}`;
                        }}
                        className="flex items-center justify-center gap-1.5 text-xs font-semibold p-2.5 rounded-xl border border-[var(--line)] bg-[var(--surface-2)]"
                      >
                        <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
                        Excel (.zip)
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="p-3 rounded-xl border border-[var(--line)] bg-[var(--surface-2)] text-[11px] text-[var(--muted)] mt-4">
              <div className="font-bold text-emerald-500 flex items-center gap-1.5 mb-1">
                <Server className="w-3.5 h-3.5" />
                Yerli Sunucu & KVKK
              </div>
              Veriler kurum içi sunucuda şifreli saklanmaktadır.
            </div>
          </div>
        </div>
      )}

      {/* 3. Mobil Sabit Alt Sekme Çubuğu (Bottom Tab Navigation - lg altı) */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-[var(--surface)]/95 backdrop-blur-md border-t border-[var(--line)] px-1.5 py-1 flex items-center justify-around shadow-2xl">
        {menuler.map((m) => {
          const Ikon = m.ikon;
          const aktif = aktifSekme === m.id;
          return (
            <button
              key={m.id}
              onClick={() => onSekmeSec(m.id)}
              className={`flex-1 flex flex-col items-center justify-center py-1.5 px-1 rounded-xl transition-all ${
                aktif
                  ? "text-blue-500 font-extrabold bg-blue-500/10"
                  : "text-[var(--muted)] font-medium hover:text-[var(--text)]"
              }`}
            >
              <div className="relative">
                <Ikon className={`w-5 h-5 ${aktif ? "text-blue-500 scale-110" : ""} transition-transform`} />
                {m.badge && (
                  <span className="absolute -top-1.5 -right-3 text-[9px] font-black px-1 rounded-full bg-blue-600 text-white">
                    {m.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] mt-0.5 truncate max-w-[68px]">{m.kisaEtiket}</span>
            </button>
          );
        })}
      </nav>
    </>
  );
};

