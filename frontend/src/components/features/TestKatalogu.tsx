"use client";

import React, { useState, useEffect, useRef } from "react";
import { BookOpen, Search, Library, Play, Award, Zap } from "lucide-react";

export const TestKatalogu: React.FC = () => {
  const [tumTestler, setTumTestler] = useState<any[]>([]);
  const [arama, setArama] = useState<string>("");
  const [seciliTest, setSeciliTest] = useState<string>("Boy ve Vücut Ağırlığı (TSYT)");
  const [sahneDetay, setSahneDetay] = useState<any>(null);
  const [kaynakcaModal, setKaynakcaModal] = useState<boolean>(false);
  const [kaynakcalar, setKaynakcalar] = useState<any[]>([]);

  const svgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`/api/v1/katalog/testler?arama=${encodeURIComponent(arama)}`)
      .then((r) => r.json())
      .then((d) => setTumTestler(d.testler || []))
      .catch(() => {});
  }, [arama]);

  useEffect(() => {
    if (!seciliTest) return;
    fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(seciliTest)}`)
      .then((r) => r.json())
      .then((d) => setSahneDetay(d))
      .catch(() => {});
  }, [seciliTest]);

  useEffect(() => {
    if (svgRef.current) {
      svgRef.current.querySelectorAll("svg").forEach((s: any) => {
        try {
          if (s.unpauseAnimations) s.unpauseAnimations();
          if (s.setCurrentTime) s.setCurrentTime(0);
        } catch (e) {}
      });
    }
  }, [sahneDetay]);

  const kaynakcaYukle = () => {
    fetch("/api/v1/katalog/kaynakca")
      .then((r) => r.json())
      .then((d) => {
        setKaynakcalar(d.kaynakca || []);
        setKaynakcaModal(true);
      })
      .catch(() => {});
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
      {/* Sol Sütun: 196 Test Kataloğu */}
      <div className="lg:col-span-4 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-3.5 sm:p-4 flex flex-col max-h-72 lg:max-h-none lg:h-[calc(100vh-7.5rem)]">
        <div className="flex items-center justify-between mb-2.5 sm:mb-3">
          <div className="font-bold text-sm">196 Test Kataloğu</div>
          <button
            onClick={kaynakcaYukle}
            className="flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
          >
            <Library className="w-3.5 h-3.5 text-blue-500" />
            191 Kaynakça
          </button>
        </div>

        {/* Mobil Hızlı Test Seçici */}
        {tumTestler.length > 0 && (
          <div className="lg:hidden mb-2.5">
            <select
              value={seciliTest}
              onChange={(e) => setSeciliTest(e.target.value)}
              className="w-full text-xs font-bold bg-blue-500/10 border border-blue-500/30 text-[var(--text)] rounded-xl p-2.5 focus:outline-none"
            >
              {tumTestler.map((t) => (
                <option key={t.test_adi} value={t.test_adi}>
                  📋 {t.test_adi} ({t.kategori})
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="relative mb-3">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-[var(--muted)]" />
          <input
            type="text"
            placeholder="Test, nitelik veya branş ara..."
            value={arama}
            onChange={(e) => setArama(e.target.value)}
            className="w-full text-xs pl-9 pr-3 py-2 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {tumTestler.map((t) => {
            const aktif = t.test_adi === seciliTest;
            return (
              <div
                key={t.test_adi}
                onClick={() => setSeciliTest(t.test_adi)}
                className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  aktif
                    ? "bg-blue-500/10 border-blue-500 shadow-sm"
                    : "bg-[var(--surface-2)] border-[var(--line)] hover:border-blue-400/50"
                }`}
              >
                <div>
                  <div className="text-xs font-bold">{t.test_adi}</div>
                  <div className="text-[11px] text-[var(--muted)]">
                    {t.kategori} · {t.nitelik || "Genel"}
                  </div>
                </div>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    t.norm_var_mi
                      ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                      : "bg-[var(--surface)] text-[var(--muted)] border border-[var(--line)]"
                  }`}
                >
                  {t.norm_var_mi ? "Normlu" : "Protokol"}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sağ Sütun: Biyomekanik SVG Sahnesi ve Bilimsel Protokol */}
      <div className="lg:col-span-8 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
          <div>
            <h2 className="text-base font-extrabold tracking-tight">{seciliTest}</h2>
            <p className="text-xs text-[var(--muted)] font-medium mt-0.5">
              İzometrik Biyomekanik Sahne & Protokol Bilgi Kartı
            </p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-500 border border-blue-500/20">
            {sahneDetay?.nitelik || "Protokol"}
          </span>
        </div>

        {sahneDetay ? (
          <div className="space-y-4">
            <p className="text-xs text-[var(--muted)] leading-relaxed">
              {sahneDetay.aciklama}
            </p>

            {/* Alan Rozetleri */}
            <div className="flex flex-wrap gap-2">
              {(sahneDetay.alanlar || []).map((a: any, i: number) => (
                <span
                  key={i}
                  className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-[var(--surface-2)] border border-[var(--line)]"
                >
                  {a[0]} ({a[1] || "sayısal"})
                </span>
              ))}
            </div>

            {/* SVG Sahnesi */}
            <div
              ref={svgRef}
              dangerouslySetInnerHTML={{ __html: sahneDetay.svg_html || "" }}
            />
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-[var(--muted)]">Protokol sahnesi yükleniyor...</div>
        )}
      </div>

      {/* Modal: 191 Bilimsel Kaynakça */}
      {kaynakcaModal && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setKaynakcaModal(false)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3 mb-4">
              <div className="font-extrabold text-base flex items-center gap-2">
                <Library className="w-5 h-5 text-blue-500" />
                PerformTest Bilimsel Kütüphane ({kaynakcalar.length} Kaynak)
              </div>
              <button
                onClick={() => setKaynakcaModal(false)}
                className="text-xs font-bold px-2.5 py-1 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)]"
              >
                ✕ Kapat
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 text-xs text-[var(--muted)] leading-relaxed">
              {kaynakcalar.map((k: any, i: number) => (
                <div key={i} className="p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]">
                  <strong className="text-blue-500 mr-1.5">[{i + 1}]</strong>
                  <span className="text-[var(--text)]">{k.metin || k.kaynak || JSON.stringify(k)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

