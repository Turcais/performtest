"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Timer,
  CheckCircle2,
  AlertTriangle,
  Save,
  Activity,
  Layers,
  Search,
  X,
} from "lucide-react";
import { SporcuKaydi } from "@/lib/api-client";

interface SahaOlcumProps {
  sporcular: SporcuKaydi[];
  aktifKulup: string;
  jwtToken: string;
  rol?: string;
  onOlcumKaydedildi: () => void;
}

export const SahaOlcum: React.FC<SahaOlcumProps> = ({
  sporcular,
  aktifKulup,
  jwtToken,
  rol = "super_admin",
  onOlcumKaydedildi,
}) => {
  const isVeli = rol === "sporcu_veli" || rol === "veli";

  if (isVeli) {
    return (
      <div className="bg-[var(--surface)] border border-amber-500/20 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4 shadow-sm">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-500 rounded-2xl flex items-center justify-center mx-auto text-3xl">
          🔒
        </div>
        <h3 className="text-lg font-black text-[var(--text)]">Saha Ölçüm & Sonuç Girdisi Yetki Sınırı</h3>
        <p className="text-xs text-[var(--muted)] leading-relaxed">
          Saha ölçüm testi kaydetme ve sonuç girdisi yapma yetkisi yalnızca antrenör ve kulüp yöneticilerine tanımlıdır. Veli hesabı ile sonuç girişi yapılamaz. Çocuğunuzun test sonuçlarını <strong>Sporcu Gelişim Raporu</strong> sekmesinden inceleyebilirsiniz.
        </p>
      </div>
    );
  }
  const [seciliSporcu, setSeciliSporcu] = useState<string>(
    sporcular[0]?.tam_ad || ""
  );
  const [yas, setYas] = useState<number>(10);
  const [cinsiyet, setCinsiyet] = useState<string>("Erkek");
  const [tumTestler, setTumTestler] = useState<any[]>([]);
  const [testArama, setTestArama] = useState<string>("");
  const [seciliTest, setSeciliTest] = useState<string>("Durarak Uzun Atlama");
  const [seciliDegisken, setSeciliDegisken] = useState<string>("Deneme 1 (cm)");
  const [deger, setDeger] = useState<number>(145);
  const [oturumAdi, setOturumAdi] = useState<string>("2026 Güz Tarama Ölçümü");
  const [canliSonuc, setCanliSonuc] = useState<any>(null);
  const [svgHtml, setSvgHtml] = useState<string>("");
  const [mesaj, setMesaj] = useState<string>("");

  const svgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/v1/katalog/testler")
      .then((r) => r.json())
      .then((d) => setTumTestler(d.testler || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const sp = sporcular.find((s) => s.tam_ad === seciliSporcu);
    if (sp) {
      if (sp.yas) setYas(sp.yas);
      if (sp.cinsiyet) setCinsiyet(sp.cinsiyet);
    }
  }, [seciliSporcu, sporcular]);

  useEffect(() => {
    if (!seciliTest) return;
    const t = tumTestler.find((x) => x.test_adi === seciliTest);
    if (t && t.alanlar && t.alanlar.length > 0) {
      setSeciliDegisken(t.alanlar[0][0]);
    }
    fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(seciliTest)}`)
      .then((r) => r.json())
      .then((d) => {
        setSvgHtml(d.svg_html || "");
      })
      .catch(() => {});
  }, [seciliTest, tumTestler]);

  useEffect(() => {
    if (svgRef.current) {
      svgRef.current.querySelectorAll("svg").forEach((s: any) => {
        try {
          if (s.unpauseAnimations) s.unpauseAnimations();
          if (s.setCurrentTime) s.setCurrentTime(0);
        } catch (e) {}
      });
    }
  }, [svgHtml]);

  useEffect(() => {
    // Canlı Z-Skoru değerlendirmesi
    if (!seciliTest || isNaN(deger)) return;
    fetch("/api/v1/analiz/degerlendir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        test_adi: seciliTest,
        degisken: seciliDegisken,
        deger: deger,
        yas: yas,
        cinsiyet: cinsiyet,
      }),
    })
      .then((r) => r.json())
      .then((d) => setCanliSonuc(d))
      .catch(() => {});
  }, [seciliTest, seciliDegisken, deger, yas, cinsiyet]);

  const olcumKaydet = async () => {
    if (!seciliSporcu) return;
    try {
      const r = await fetch("/api/v1/oturumlar/olcum-kaydet", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          kulup_kodu: aktifKulup,
          sporcu_adi: seciliSporcu,
          test_adi: seciliTest,
          test_yasi: yas,
          oturum: oturumAdi,
          olcumler: { [seciliDegisken]: deger },
        }),
      });
      if (r.ok) {
        setMesaj(`✓ Ölçüm başarıyla kaydedildi: ${seciliSporcu} — ${seciliTest}`);
        onOlcumKaydedildi();
        setTimeout(() => setMesaj(""), 4000);
      } else {
        const err = await r.json();
        setMesaj(`✕ Hata: ${err.hata || "Kayıt başarısız"}`);
      }
    } catch (e) {
      setMesaj("✕ Sunucu iletişim hatası.");
    }
  };

  const z = canliSonuc?.z_skoru?.z_performans ?? canliSonuc?.z_skoru?.z ?? (typeof canliSonuc?.z_skoru === "number" ? canliSonuc.z_skoru : null);
  const zMetin = z !== null && z !== undefined && !isNaN(z) ? `${z >= 0 ? "+" : ""}${Number(z).toFixed(2)} SD` : "Norm Dışı";
  
  const pct = typeof canliSonuc?.persentil === "object" && canliSonuc?.persentil !== null
    ? (canliSonuc.persentil.persentil_aralik || canliSonuc.persentil.kategori || "P50")
    : (canliSonuc?.persentil || "—");

  const makul = Array.isArray(canliSonuc?.makul_aralik)
    ? `${canliSonuc.makul_aralik[0]} – ${canliSonuc.makul_aralik[1]}`
    : "Genel Aralık";

  const arananTest = testArama.trim().toLocaleLowerCase("tr-TR");
  const filtrelenenTestler = arananTest
    ? tumTestler.filter((t) =>
        [t.test_adi, t.kategori, t.nitelik, t.batarya, t.brans]
          .filter(Boolean)
          .some((alan) => String(alan).toLocaleLowerCase("tr-TR").includes(arananTest))
      )
    : tumTestler;
  const seciliTestObj = tumTestler.find((x) => x.test_adi === seciliTest);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Sol Sütun: Ölçüm Giriş Formu */}
      <div className="lg:col-span-5 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
          <div className="flex items-center gap-2">
            <Timer className="w-5 h-5 text-emerald-500" />
            <h2 className="font-bold text-sm">Saha Test Ölçüm & Sonuç Girdisi</h2>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
            ✓ Sonuç Girişi Aktif
          </span>
        </div>

        {mesaj && (
          <div className="p-3 text-xs font-semibold rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20">
            {mesaj}
          </div>
        )}

        <div className="space-y-3 text-xs font-medium">
          <div>
            <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Ölçülen Sporcu</label>
            <select
              value={seciliSporcu}
              onChange={(e) => setSeciliSporcu(e.target.value)}
              className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 font-bold focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {sporcular.map((s) => (
                <option key={s.id} value={s.tam_ad}>
                  {s.tam_ad} ({s.cinsiyet}, {s.yas ?? "-"} yaş)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Test Yaşı</label>
              <input
                type="number"
                step="0.5"
                value={yas}
                onChange={(e) => setYas(parseFloat(e.target.value))}
                className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Cinsiyet</label>
              <select
                value={cinsiyet}
                onChange={(e) => setCinsiyet(e.target.value)}
                className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="Erkek">Erkek</option>
                <option value="Kadın">Kadın</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-[11px] text-[var(--muted)] font-bold">Uygulanan Test Protokolü</label>
              <span className="text-[10px] font-bold text-blue-500">
                {arananTest ? `${filtrelenenTestler.length} eşleşme` : `${tumTestler.length} test`}
              </span>
            </div>

            {/* Hızlı Test Arama Kutucuğu */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-[var(--muted)] pointer-events-none" />
              <input
                type="text"
                value={testArama}
                onChange={(e) => {
                  const v = e.target.value;
                  setTestArama(v);
                  const kucuk = v.trim().toLocaleLowerCase("tr-TR");
                  if (kucuk) {
                    const eslesen = tumTestler.find((t) =>
                      [t.test_adi, t.kategori, t.nitelik, t.batarya, t.brans]
                        .filter(Boolean)
                        .some((alan) => String(alan).toLocaleLowerCase("tr-TR").includes(kucuk))
                    );
                    if (eslesen && eslesen.test_adi !== seciliTest) {
                      setSeciliTest(eslesen.test_adi);
                    }
                  }
                }}
                placeholder="Test adı, branş, batarya veya nitelik ara..."
                className="w-full text-xs pl-8 pr-8 py-2 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              {testArama && (
                <button
                  type="button"
                  onClick={() => setTestArama("")}
                  title="Aramayı Temizle"
                  className="absolute right-2.5 top-2 text-[var(--muted)] hover:text-[var(--text)] p-0.5 rounded"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Arama Yapıldığında Hızlı Tıklanabilir Sonuç Listesi */}
            {arananTest && (
              <div className="max-h-44 overflow-y-auto rounded-xl border border-blue-500/30 bg-[var(--surface-2)] divide-y divide-[var(--line)] shadow-sm">
                {filtrelenenTestler.length > 0 ? (
                  filtrelenenTestler.map((t) => {
                    const aktif = t.test_adi === seciliTest;
                    return (
                      <button
                        key={t.test_adi}
                        type="button"
                        onClick={() => {
                          setSeciliTest(t.test_adi);
                          setTestArama("");
                        }}
                        className={`w-full text-left px-3 py-2 flex items-center justify-between gap-2 transition ${
                          aktif
                            ? "bg-blue-500/15 text-blue-500 font-bold"
                            : "hover:bg-[var(--surface)] text-[var(--text)]"
                        }`}
                      >
                        <div className="min-w-0">
                          <div className="text-xs font-bold truncate">{t.test_adi}</div>
                          <div className="text-[10px] text-[var(--muted)] truncate">
                            {t.kategori} · {t.nitelik || "Genel"}
                          </div>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 shrink-0">
                          Seç
                        </span>
                      </button>
                    );
                  })
                ) : (
                  <div className="p-3 text-center text-[11px] text-[var(--muted)]">
                    &quot;{testArama}&quot; ile eşleşen test protokolü bulunamadı.
                  </div>
                )}
              </div>
            )}

            <select
              value={seciliTest}
              onChange={(e) => setSeciliTest(e.target.value)}
              className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 font-bold focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {(filtrelenenTestler.length > 0 ? filtrelenenTestler : tumTestler).map((t) => (
                <option key={t.test_adi} value={t.test_adi}>
                  {t.test_adi} ({t.kategori})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Ölçülen Değişken / Deneme</label>
            {seciliTestObj?.alanlar && seciliTestObj.alanlar.length > 1 && (
              <div className="flex flex-wrap gap-1.5 mb-1.5">
                {seciliTestObj.alanlar.map((a: any, i: number) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setSeciliDegisken(a[0])}
                    className={`text-[10px] font-bold px-2 py-1 rounded-lg border transition ${
                      seciliDegisken === a[0]
                        ? "bg-blue-600 text-white border-blue-600"
                        : "bg-[var(--surface-2)] text-[var(--muted)] border-[var(--line)] hover:text-[var(--text)]"
                    }`}
                  >
                    {a[0]}
                  </button>
                ))}
              </div>
            )}
            <input
              value={seciliDegisken}
              onChange={(e) => setSeciliDegisken(e.target.value)}
              className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Ölçülen Ham Sonuç</label>
            <input
              type="number"
              step="0.1"
              value={deger}
              onChange={(e) => setDeger(parseFloat(e.target.value) || 0)}
              className="w-full text-base font-extrabold bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Oturum / Tarama Adı</label>
            <input
              value={oturumAdi}
              onChange={(e) => setOturumAdi(e.target.value)}
              className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={olcumKaydet}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-md transition mt-4"
          >
            <Save className="w-4 h-4" />
            Ölçümü Veritabanına Kaydet
          </button>
        </div>
      </div>

      {/* Sağ Sütun: Canlı Değerlendirme & SVG Sahnesi */}
      <div className="lg:col-span-7 space-y-4 sm:space-y-6 min-w-0">
        {/* Canlı Eşik & Z-Skor Kartları */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3">
          <div className="bg-[var(--surface)] border border-[var(--line)] p-3.5 sm:p-4 rounded-2xl shadow-sm">
            <div className="text-[11px] text-[var(--muted)] font-bold">Yaşıt Persentili</div>
            <div className="text-lg sm:text-xl font-black mt-1 text-blue-500">{pct}</div>
            <div className="text-[10px] text-[var(--muted)] mt-0.5 truncate">{seciliTest}</div>
          </div>

          <div className="bg-[var(--surface)] border border-[var(--line)] p-3.5 sm:p-4 rounded-2xl shadow-sm">
            <div className="text-[11px] text-[var(--muted)] font-bold">Performans Z-Skoru</div>
            <div className="text-lg sm:text-xl font-black mt-1 text-emerald-500">{zMetin}</div>
            <div className="text-[10px] text-[var(--muted)] mt-0.5">Yaş: {yas} · {cinsiyet}</div>
          </div>

          <div className="bg-[var(--surface)] border border-[var(--line)] p-3.5 sm:p-4 rounded-2xl shadow-sm">
            <div className="text-[11px] text-[var(--muted)] font-bold">Makul Aralık</div>
            <div className="text-sm sm:text-base font-extrabold mt-1 text-amber-500">{makul}</div>
            <div className="text-[10px] text-[var(--muted)] mt-0.5">Uç değer/rekor filtresi</div>
          </div>
        </div>

        {/* Canlı SVG Protokol Sahnesi */}
        <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-3.5 sm:p-5 shadow-sm overflow-x-auto">
          <div className="text-xs font-bold mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-500 shrink-0" />
            <span className="truncate">{seciliTest} — Performans Ölçme ve Değerlendirme Protokol Sahnesi</span>
          </div>
          <div key={seciliTest} ref={svgRef} className="w-full overflow-x-auto" dangerouslySetInnerHTML={{ __html: svgHtml }} />
        </div>
      </div>
    </div>
  );
};

