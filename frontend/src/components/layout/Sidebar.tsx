"use client";

import React from "react";
import {
  Users,
  Timer,
  Scale,
  BookOpen,
  ShieldCheck,
  Server,
  Zap,
} from "lucide-react";

export type SekmeTipi = "analiz" | "oturum" | "karsilastir" | "katalog" | "admin";

interface SidebarProps {
  aktifSekme: SekmeTipi;
  onSekmeSec: (sekme: SekmeTipi) => void;
  toplamSporcu: number;
  rol?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  aktifSekme,
  onSekmeSec,
  toplamSporcu,
  rol = "super_admin",
}) => {
  const isVeli = rol === "sporcu_veli" || rol === "veli";
  const isAntrenor = rol === "antrenor";
  const isKulupAdmin = rol === "kulup_yoneticisi";

  const tumMenuler: Array<{
    id: SekmeTipi;
    etiket: string;
    alt: string;
    ikon: React.ElementType;
    badge?: string;
    roller: string[]; // Boş ise herkes görebilir
  }> = [
    {
      id: "analiz",
      etiket: isVeli ? "Sporcu Gelişim Raporu & Karne" : "Sporcu Performans Laboratuvarı",
      alt: isVeli ? "LMS Z-Skor & Biyomotor Profil" : "LMS Z-Skor, Radar & Profil",
      ikon: Users,
      badge: `${toplamSporcu}`,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor", "sporcu_veli", "veli"],
    },
    {
      id: "oturum",
      etiket: "Saha Ölçüm & Sonuç Girdisi",
      alt: "Anlık Eşik, Hata & Rekor Filtresi",
      ikon: Timer,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor"], // Veli sonuç giremez!
    },
    {
      id: "karsilastir",
      etiket: "Başa Baş Karşılaştırma",
      alt: "Çift Sporcu Karşılaştırma & Fark",
      ikon: Scale,
      roller: ["super_admin", "kulup_yoneticisi", "antrenor"], // Veli diğer sporcuları karşılaştıramaz!
    },
    {
      id: "katalog",
      etiket: isVeli ? "196 Test & Hareket Kataloğu" : "196 Test Kataloğu & Biyomekanik",
      alt: isVeli ? "Test Protokolleri & Bilgilendirme" : "SVG Animasyon & 191 Kaynakça",
      ikon: BookOpen,
      badge: "196",
      roller: ["super_admin", "kulup_yoneticisi", "antrenor", "sporcu_veli", "veli"],
    },
    {
      id: "admin",
      etiket: isKulupAdmin ? "Kulüp Yönetimi & KVKK" : "PerformTest Yönetim & KVKK",
      alt: isKulupAdmin ? "Kulüp İçi Sporcu & İzin Kayıtları" : "Tenant, RBAC & Denetim İzi",
      ikon: ShieldCheck,
      roller: ["super_admin", "kulup_yoneticisi"], // Antrenör ve veli sistem adminini göremez!
    },
  ];

  const menuler = tumMenuler.filter((m) => m.roller.includes(rol));

  return (
    <aside className="w-72 border-r border-[var(--line)] bg-[var(--surface)] flex flex-col justify-between shrink-0 p-4 min-h-[calc(100vh-4rem)]">
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
          6698 Sayılı KVKK Madde 7 & 11 uyumlu. Tüm biyometrik test verileri kurum içi sunucuda saklanmaktadır.
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
  );
};

