"use client";

import React, { useState, useEffect } from "react";
import { Scale, TrendingUp, Users } from "lucide-react";
import { SporcuKaydi } from "@/lib/api-client";

interface KarsilastirmaProps {
  sporcular: SporcuKaydi[];
  aktifKulup: string;
  rol?: string;
}

export const Karsilastirma: React.FC<KarsilastirmaProps> = ({
  sporcular,
  aktifKulup,
  rol = "super_admin",
}) => {
  const isVeli = rol === "sporcu_veli" || rol === "veli";

  if (isVeli) {
    return (
      <div className="bg-[var(--surface)] border border-amber-500/20 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4 shadow-sm">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-500 rounded-2xl flex items-center justify-center mx-auto text-3xl">
          ⚖️
        </div>
        <h3 className="text-lg font-black text-[var(--text)]">Sporcu Karşılaştırma Yetki Sınırı</h3>
        <p className="text-xs text-[var(--muted)] leading-relaxed">
          Başa baş sporcu karşılaştırma modülü yalnızca antrenör ve kulüp yöneticilerinin kullanımına açıktır.
          Veli hesabınızla yalnızca kendi çocuğunuzun atletik gelişim karnesini inceleyebilirsiniz.
        </p>
      </div>
    );
  }
  const [sporcuA, setSporcuA] = useState<string>(sporcular[0]?.tam_ad || "");
  const [sporcuB, setSporcuB] = useState<string>(sporcular[1]?.tam_ad || "");
  const [karsilastirma, setKarsilastirma] = useState<any>(null);
  const [yukleniyor, setYukleniyor] = useState<boolean>(false);

  const karsilastir = async () => {
    if (!sporcuA || !sporcuB) return;
    setYukleniyor(true);
    try {
      const r = await fetch(
        `/api/v1/karsilastir?kulup_kodu=${encodeURIComponent(
          aktifKulup
        )}&sporcu_a=${encodeURIComponent(sporcuA)}&sporcu_b=${encodeURIComponent(
          sporcuB
        )}`
      );
      const d = await r.json();
      setKarsilastirma(d);
    } catch (e) {
    } finally {
      setYukleniyor(false);
    }
  };

  useEffect(() => {
    if (sporcular.length >= 2) {
      setSporcuA(sporcular[0].tam_ad);
      setSporcuB(sporcular[1].tam_ad);
    }
  }, [sporcular]);

  useEffect(() => {
    if (sporcuA && sporcuB) {
      karsilastir();
    }
  }, [sporcuA, sporcuB, aktifKulup]);

  return (
    <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-4 sm:p-6 shadow-sm space-y-5 sm:space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 sm:gap-4 border-b border-[var(--line)] pb-4">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-500 shrink-0" />
          <h2 className="font-bold text-sm">Başa Baş (Head-to-Head) Sporcu Karşılaştırma Laboratuvarı</h2>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3 w-full lg:w-auto">
          <select
            value={sporcuA}
            onChange={(e) => setSporcuA(e.target.value)}
            className="text-xs font-bold bg-[var(--surface-2)] border border-blue-500 rounded-xl px-3 py-2 text-blue-500 focus:outline-none w-full sm:w-auto"
          >
            {sporcular.map((s) => (
              <option key={s.id} value={s.tam_ad}>
                🔵 {s.tam_ad}
              </option>
            ))}
          </select>

          <span className="font-extrabold text-xs text-[var(--muted)] text-center">VS</span>

          <select
            value={sporcuB}
            onChange={(e) => setSporcuB(e.target.value)}
            className="text-xs font-bold bg-[var(--surface-2)] border border-amber-500 rounded-xl px-3 py-2 text-amber-500 focus:outline-none w-full sm:w-auto"
          >
            {sporcular.map((s) => (
              <option key={s.id} value={s.tam_ad}>
                🟠 {s.tam_ad}
              </option>
            ))}
          </select>

          <button
            onClick={karsilastir}
            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2.5 sm:py-2 rounded-xl transition w-full sm:w-auto"
          >
            Karşılaştır
          </button>
        </div>
      </div>

      {yukleniyor ? (
        <div className="py-12 text-center text-xs text-[var(--muted)]">Kıyaslama matrisi hesaplanıyor...</div>
      ) : karsilastirma ? (
        <div className="space-y-6">
          {/* İki Sporcu Özet Kartları */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border-2 border-blue-500 bg-blue-500/10 space-y-1">
              <div className="font-extrabold text-base text-blue-500">🔵 {karsilastirma.sporcu_a?.ad}</div>
              <div className="text-xs">
                Yatkınlık Penceresi: <strong>{(karsilastirma.sporcu_a?.fiziksel_pencere || []).join(", ") || "—"}</strong>
              </div>
            </div>

            <div className="p-4 rounded-xl border-2 border-amber-500 bg-amber-500/10 space-y-1">
              <div className="font-extrabold text-base text-amber-500">🟠 {karsilastirma.sporcu_b?.ad}</div>
              <div className="text-xs">
                Yatkınlık Penceresi: <strong>{(karsilastirma.sporcu_b?.fiziksel_pencere || []).join(", ") || "—"}</strong>
              </div>
            </div>
          </div>

          {/* Karşılaştırma Radarı */}
          {karsilastirma.radar_svg && (
            <div className="flex justify-center p-4 bg-[var(--surface-2)] border border-[var(--line)] rounded-2xl">
              <div dangerouslySetInnerHTML={{ __html: karsilastirma.radar_svg }} />
            </div>
          )}

          {/* Fark Matrisi */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[var(--line)] text-[var(--muted)] text-[11px]">
                  <th className="py-2.5 px-3">Test Protokolü & Değişken</th>
                  <th className="py-2.5 px-3 text-blue-500 font-bold">🔵 {karsilastirma.sporcu_a?.ad} (Z)</th>
                  <th className="py-2.5 px-3 text-amber-500 font-bold">🟠 {karsilastirma.sporcu_b?.ad} (Z)</th>
                  <th className="py-2.5 px-3 font-bold">Fark (ΔZ)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {(karsilastirma.satirlar || []).map((s: any, idx: number) => {
                  const fark = s.z_fark !== null && s.z_fark !== undefined ? `${s.z_fark > 0 ? "+" : ""}${s.z_fark} SD` : "—";
                  return (
                    <tr key={idx} className="hover:bg-[var(--surface-2)] transition">
                      <td className="py-2.5 px-3 font-bold">
                        {s.test} <span className="text-[var(--muted)] font-normal">— {s.degisken}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        {s.deger_a ?? "—"}{" "}
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500 ml-1">
                          {s.z_a ?? "—"}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        {s.deger_b ?? "—"}{" "}
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500 ml-1">
                          {s.z_b ?? "—"}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-extrabold">{fark}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="py-12 text-center text-xs text-[var(--muted)]">İki sporcu seçip karşılaştır düğmesine tıklayın.</div>
      )}
    </div>
  );
};

