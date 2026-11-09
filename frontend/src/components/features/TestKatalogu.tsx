"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  BookOpen,
  Search,
  Library,
  Play,
  Award,
  Zap,
  PlusCircle,
  Trash2,
  Sparkles,
  X,
  RotateCcw,
} from "lucide-react";

interface TestKataloguProps {
  rol?: string;
  jwtToken?: string;
  toplamTest?: number;
  toplamKaynakca?: number;
  onKatalogGuncellendi?: () => void;
}

export const TestKatalogu: React.FC<TestKataloguProps> = ({
  rol = "super_admin",
  jwtToken = "",
  toplamTest = 196,
  toplamKaynakca = 191,
  onKatalogGuncellendi,
}) => {
  const isSuperAdmin = rol === "super_admin";

  const [tumTestler, setTumTestler] = useState<any[]>([]);
  const [arama, setArama] = useState<string>("");
  const [seciliTest, setSeciliTest] = useState<string>("Boy ve Vücut Ağırlığı (TSYT)");
  const [sahneDetay, setSahneDetay] = useState<any>(null);
  const [kaynakcaModal, setKaynakcaModal] = useState<boolean>(false);
  const [kaynakcalar, setKaynakcalar] = useState<any[]>([]);
  const [durumMesaji, setDurumMesaji] = useState<string | null>(null);

  // Yeni Test + Otomatik SVG Ekleme Modalı (Süper Admin)
  const [yeniTestModal, setYeniTestModal] = useState<boolean>(false);
  const [ytAd, setYtAd] = useState<string>("");
  const [ytKategori, setYtKategori] = useState<string>("Sürat ve Çabukluk");
  const [ytNitelik, setYtNitelik] = useState<string>("sürat");
  const [ytHareketTipi, setYtHareketTipi] = useState<string>("sprint");
  const [ytDegisken, setYtDegisken] = useState<string>("Süre (sn)");
  const [ytBirim, setYtBirim] = useState<string>("sn");
  const [ytYon, setYtYon] = useState<string>("dusuk_iyi");
  const [ytNormMedyan, setYtNormMedyan] = useState<string>("4.20");
  const [ytNormS, setYtNormS] = useState<string>("0.12");
  const [ytAciklama, setYtAciklama] = useState<string>("");
  const [ytKaydediliyor, setYtKaydediliyor] = useState<boolean>(false);

  // Yeni Kaynakça Ekleme State (Süper Admin)
  const [ykAnahtar, setYkAnahtar] = useState<string>("");
  const [ykMetin, setYkMetin] = useState<string>("");

  const svgRef = useRef<HTMLDivElement>(null);

  const testleriYukle = (secilecekTestAdi?: string) => {
    fetch(`/api/v1/katalog/testler?arama=${encodeURIComponent(arama)}`)
      .then((r) => r.json())
      .then((d) => {
        const liste = d.testler || [];
        setTumTestler(liste);
        if (secilecekTestAdi) {
          setSeciliTest(secilecekTestAdi);
        } else if (liste.length > 0 && !liste.some((x: any) => x.test_adi === seciliTest)) {
          setSeciliTest(liste[0].test_adi);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    testleriYukle();
  }, [arama]);

  const svgYukle = (tAdi: string) => {
    if (!tAdi) return;
    fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(tAdi)}`)
      .then((r) => r.json())
      .then((d) => setSahneDetay(d))
      .catch(() => {});
  };

  useEffect(() => {
    svgYukle(seciliTest);
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

  const yeniTestKaydet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ytAd.trim()) return;
    setYtKaydediliyor(true);
    try {
      const r = await fetch("/api/v1/admin/katalog/testler", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: jwtToken ? `Bearer ${jwtToken}` : "",
        },
        body: JSON.stringify({
          test_adi: ytAd.trim(),
          kategori: ytKategori,
          nitelik: ytNitelik,
          hareket_tipi: ytHareketTipi,
          degisken_adi: ytDegisken || "Ölçüm Değeri",
          birim: ytBirim,
          yon: ytYon,
          norm_medyan: ytNormMedyan ? parseFloat(ytNormMedyan) : null,
          norm_s: ytNormS ? parseFloat(ytNormS) : 0.15,
          norm_l: 1.0,
          aciklama:
            ytAciklama.trim() ||
            `${ytAd.trim()} bilimsel saha protokolü. Biyomotor nitelik: ${ytNitelik}.`,
        }),
      });
      const d = await r.json();
      if (r.ok && d.durum === "eklendi") {
        setYeniTestModal(false);
        const eklenenAd = d.test_adi;
        setYtAd("");
        setYtAciklama("");
        setDurumMesaji(
          `✓ "${eklenenAd}" kataloğa eklendi ve 3D/Vektör SVG biyomekanik sahnesi otomatik sentezlendi! (Toplam: ${d.toplam_test} Test)`
        );
        testleriYukle(eklenenAd);
        svgYukle(eklenenAd);
        if (onKatalogGuncellendi) onKatalogGuncellendi();
      } else {
        setDurumMesaji(`✕ Hata: ${d.hata || "Test eklenemedi"}`);
      }
    } catch {
      setDurumMesaji("✕ Sunucu iletişim hatası.");
    } finally {
      setYtKaydediliyor(false);
    }
  };

  const testSil = async (testAdi: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!confirm(`"${testAdi}" test protokolünü katalogdan kaldırmak istediğinize emin misiniz?`)) return;
    try {
      const r = await fetch(`/api/v1/admin/katalog/testler/${encodeURIComponent(testAdi)}`, {
        method: "DELETE",
        headers: {
          Authorization: jwtToken ? `Bearer ${jwtToken}` : "",
        },
      });
      const d = await r.json();
      if (r.ok && d.durum === "silindi") {
        setDurumMesaji(`✓ "${testAdi}" katalogdan çıkarıldı. (Güncel Katalog: ${d.toplam_test} Test)`);
        testleriYukle();
        if (onKatalogGuncellendi) onKatalogGuncellendi();
      }
    } catch {}
  };

  const yeniKaynakcaEkle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ykMetin.trim()) return;
    try {
      const r = await fetch("/api/v1/admin/katalog/kaynakca", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: jwtToken ? `Bearer ${jwtToken}` : "",
        },
        body: JSON.stringify({
          anahtar: ykAnahtar.trim() || `custom_${Date.now()}`,
          metin: ykMetin.trim(),
        }),
      });
      const d = await r.json();
      if (r.ok && d.durum === "eklendi") {
        setYkAnahtar("");
        setYkMetin("");
        kaynakcaYukle();
        if (onKatalogGuncellendi) onKatalogGuncellendi();
      }
    } catch {}
  };

  const kaynakcaSil = async (anahtar: string) => {
    if (!confirm(`"${anahtar}" kaynakçasını kütüphaneden silmek istediğinize emin misiniz?`)) return;
    try {
      const r = await fetch(`/api/v1/admin/katalog/kaynakca/${encodeURIComponent(anahtar)}`, {
        method: "DELETE",
        headers: {
          Authorization: jwtToken ? `Bearer ${jwtToken}` : "",
        },
      });
      if (r.ok) {
        kaynakcaYukle();
        if (onKatalogGuncellendi) onKatalogGuncellendi();
      }
    } catch {}
  };

  const gosterilenToplamTest = arama ? tumTestler.length : toplamTest;

  return (
    <div className="space-y-4">
      {durumMesaji && (
        <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-blue-500 text-xs font-bold flex items-center justify-between">
          <span>{durumMesaji}</span>
          <button onClick={() => setDurumMesaji(null)} className="text-[11px] underline ml-3">
            Kapat
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
        {/* Sol Sütun: Dinamik Test Kataloğu */}
        <div className="lg:col-span-4 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-3.5 sm:p-4 flex flex-col max-h-80 lg:max-h-none lg:h-[calc(100vh-7.5rem)]">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5 sm:mb-3">
            <div className="font-bold text-sm flex items-center gap-1.5">
              <span>{gosterilenToplamTest} Test Kataloğu</span>
            </div>
            <div className="flex items-center gap-1.5">
              {isSuperAdmin && (
                <button
                  onClick={() => setYeniTestModal(true)}
                  className="flex items-center gap-1 text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition"
                  title="Yeni Test Protokolü Ekle ve Otomatik SVG Sahnesi Oluştur"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>+ Test Ekle</span>
                </button>
              )}
              <button
                onClick={kaynakcaYukle}
                className="flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
              >
                <Library className="w-3.5 h-3.5 text-blue-500" />
                {toplamKaynakca} Kaynakça
              </button>
            </div>
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
                  className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between gap-2 ${
                    aktif
                      ? "bg-blue-500/10 border-blue-500 shadow-sm"
                      : "bg-[var(--surface-2)] border-[var(--line)] hover:border-blue-400/50"
                  }`}
                >
                  <div className="min-w-0">
                    <div className="text-xs font-bold truncate flex items-center gap-1.5">
                      <span className="truncate">{t.test_adi}</span>
                      {t.ozel_mi && (
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-500/15 text-purple-500 font-bold shrink-0">
                          Özel SVG
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-[var(--muted)] truncate">
                      {t.kategori} · {t.nitelik || "Genel"}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        t.norm_var_mi
                          ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                          : "bg-[var(--surface)] text-[var(--muted)] border border-[var(--line)]"
                      }`}
                    >
                      {t.norm_var_mi ? "Normlu" : "Protokol"}
                    </span>
                    {isSuperAdmin && (
                      <button
                        onClick={(e) => testSil(t.test_adi, e)}
                        title="Bu testi katalogdan kaldır"
                        className="p-1 rounded-lg hover:bg-red-500/15 text-[var(--muted)] hover:text-red-500 transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sağ Sütun: Biyomekanik SVG Sahnesi ve Bilimsel Protokol */}
        <div className="lg:col-span-8 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-4 sm:p-6 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--line)] pb-3">
            <div>
              <h2 className="text-base font-extrabold tracking-tight">{seciliTest}</h2>
              <p className="text-xs text-[var(--muted)] font-medium mt-0.5">
                İzometrik Biyomekanik SVG Sahne & Protokol Bilgi Kartı
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-500 border border-blue-500/20">
                {sahneDetay?.nitelik || "Protokol"}
              </span>
              {isSuperAdmin && seciliTest && (
                <button
                  onClick={() => testSil(seciliTest)}
                  className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Testi Sil</span>
                </button>
              )}
            </div>
          </div>

          {sahneDetay ? (
            <div className="space-y-4">
              <p className="text-xs text-[var(--muted)] leading-relaxed">{sahneDetay.aciklama}</p>

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
              <div ref={svgRef} dangerouslySetInnerHTML={{ __html: sahneDetay.svg_html || "" }} />
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-[var(--muted)]">Protokol sahnesi yükleniyor...</div>
          )}
        </div>
      </div>

      {/* Modal: Süper Admin Yeni Test Ekle & Otomatik SVG Sentezle */}
      {yeniTestModal && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setYeniTestModal(false)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-3xl p-6 max-w-xl w-full max-h-[90vh] overflow-y-auto shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm">Yeni Test Protokolü & Otomatik SVG Oluşturucu</h3>
                  <p className="text-[11px] text-[var(--muted)]">
                    Test eklendiğinde vitrin sayacı güncellenir ve 3D/vektör SVG biyomekanik animasyonu otomatik üretilir.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setYeniTestModal(false)}
                className="p-1.5 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={yeniTestKaydet} className="space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="sm:col-span-2">
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    Test Protokol Adı *
                  </label>
                  <input
                    required
                    value={ytAd}
                    onChange={(e) => setYtAd(e.target.value)}
                    placeholder="Örn: 30m Flying Sprint Testi veya Reaktif Çeviklik Koşusu"
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)] font-bold focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">Kategori</label>
                  <select
                    value={ytKategori}
                    onChange={(e) => setYtKategori(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                  >
                    <option value="Sürat ve Çabukluk">Sürat ve Çabukluk</option>
                    <option value="Patlayıcı Güç ve Pliometrik">Patlayıcı Güç ve Pliometrik</option>
                    <option value="Kuvvet ve Kas Dayanıklılığı">Kuvvet ve Kas Dayanıklılığı</option>
                    <option value="Çeviklik ve Koordinasyon">Çeviklik ve Koordinasyon</option>
                    <option value="Aerobik Dayanıklılık">Aerobik Dayanıklılık</option>
                    <option value="Esneklik ve Mobilite">Esneklik ve Mobilite</option>
                    <option value="Denge ve Propriosepsiyon">Denge ve Propriosepsiyon</option>
                    <option value="Antropometri">Antropometri</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    Biyomotor Nitelik
                  </label>
                  <select
                    value={ytNitelik}
                    onChange={(e) => setYtNitelik(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                  >
                    <option value="sürat">Sürat / İvme</option>
                    <option value="patlayıcı güç">Patlayıcı Güç</option>
                    <option value="kuvvet">Kuvvet</option>
                    <option value="çeviklik">Çeviklik</option>
                    <option value="dayanıklılık">Aerobik Dayanıklılık</option>
                    <option value="esneklik">Esneklik</option>
                    <option value="denge">Denge</option>
                    <option value="koordinasyon">Koordinasyon</option>
                    <option value="reaksiyon">Reaksiyon Hızı</option>
                    <option value="antropometri">Antropometri</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="text-[11px] font-bold text-blue-500 block mb-1">
                    🎨 Otomatik Biyomekanik SVG Hareket Arketipi (3D/Vektör Sahne Sentezi)
                  </label>
                  <select
                    value={ytHareketTipi}
                    onChange={(e) => setYtHareketTipi(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 font-bold text-[var(--text)]"
                  >
                    <option value="sprint">🏃 Sprint, İvmelenme & Fotosel Kapısı Koşu Sahnesi</option>
                    <option value="yatay_sicrama">🦘 Yatay Sıçrama, Patlayıcı Güç & Parabolik Uçuş Sahnesi</option>
                    <option value="dikey_sicrama">⬆️ Dikey Sıçrama (CMJ / Squat Jump) & Kuvvet Platformu</option>
                    <option value="ceviklik">🔀 Çeviklik, T-Testi, Slalom & Yön Değiştirme Konileri</option>
                    <option value="mekik_dayaniklilik">🫀 20m Mekik (Yo-Yo / Beep) & Aerobik Dayanıklılık Parkuru</option>
                    <option value="kuvvet_ust">💪 Üst Gövde, Dinamometre & İzometrik Kuvvet Sahnesi</option>
                    <option value="firlatma">🏐 Sağlık Topu Fırlatma & Balistik Üst Ekstremite Gücü</option>
                    <option value="denge">⚖️ Flamingo / Y-Denge & Proprioseptif Denge Platformu</option>
                    <option value="esneklik">🧘 Otur-Uzan & Eklem Hareket Açıklığı (ROM) Sehpası</option>
                    <option value="reaksiyon">⚡ Görsel-Motor Işık & Reaksiyon Koordinasyon Sahnesi</option>
                    <option value="antropometri">📏 Antropometrik Stadiometre & Vücut Kompozisyon Sahnesi</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    Ölçülen Değişken Adı
                  </label>
                  <input
                    value={ytDegisken}
                    onChange={(e) => setYtDegisken(e.target.value)}
                    placeholder="Örn: En İyi Süre (sn)"
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    Birim & Performans Yönü
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      value={ytBirim}
                      onChange={(e) => setYtBirim(e.target.value)}
                      placeholder="sn / cm / kg"
                      className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                    />
                    <select
                      value={ytYon}
                      onChange={(e) => setYtYon(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                    >
                      <option value="dusuk_iyi">Düşük İyi (Süre)</option>
                      <option value="yuksek_iyi">Yüksek İyi (Mesafe/Skor)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    LMS Referans Medyanı (M)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={ytNormMedyan}
                    onChange={(e) => setYtNormMedyan(e.target.value)}
                    placeholder="Örn: 4.20"
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    LMS Varyasyon Katsayısı (S)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={ytNormS}
                    onChange={(e) => setYtNormS(e.target.value)}
                    placeholder="Örn: 0.12"
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)]"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="text-[11px] font-bold text-[var(--muted)] block mb-1">
                    Uygulama Protokolü ve Saha Kuralları Açıklaması
                  </label>
                  <textarea
                    rows={3}
                    value={ytAciklama}
                    onChange={(e) => setYtAciklama(e.target.value)}
                    placeholder="Örn: Sporcu çıkış çizgisinin 50 cm gerisinden başlar, fotosel kapıları arasından maksimum hızla geçer. En iyi 2 denemenin ortalaması alınır."
                    className="w-full p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-[var(--line)]">
                <button
                  type="button"
                  onClick={() => setYeniTestModal(false)}
                  className="px-4 py-2 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] font-semibold"
                >
                  İptal
                </button>
                <button
                  type="submit"
                  disabled={ytKaydediliyor}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold shadow-md shadow-blue-500/20 transition"
                >
                  <Sparkles className="w-4 h-4" />
                  {ytKaydediliyor ? "SVG Sentezleniyor..." : "Testi Kataloğa Ekle & SVG Üret"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Bilimsel Kaynakça Kütüphanesi (+ Süper Admin Ekle/Çıkar) */}
      {kaynakcaModal && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setKaynakcaModal(false)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
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

            {isSuperAdmin && (
              <form
                onSubmit={yeniKaynakcaEkle}
                className="p-3.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)] space-y-2 text-xs"
              >
                <div className="font-bold text-blue-500">+ Yeni Bilimsel Makale / Kaynakça Ekle</div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <input
                    value={ykAnahtar}
                    onChange={(e) => setYkAnahtar(e.target.value)}
                    placeholder="Kısa Kod (örn: Buchheit_2024)"
                    className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
                  />
                  <input
                    required
                    value={ykMetin}
                    onChange={(e) => setYkMetin(e.target.value)}
                    placeholder="APA Atıf Metni (Yazar, Yıl, Dergi, DOI)..."
                    className="sm:col-span-2 p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold transition"
                >
                  Kaynakçayı Kütüphaneye Ekle
                </button>
              </form>
            )}

            <div className="flex-1 overflow-y-auto space-y-2.5 pr-2 text-xs text-[var(--muted)] leading-relaxed">
              {kaynakcalar.map((k: any, i: number) => (
                <div
                  key={k.anahtar || i}
                  className="p-2.5 rounded-xl bg-[var(--surface-2)] border border-[var(--line)] flex items-start justify-between gap-2"
                >
                  <div>
                    <strong className="text-blue-500 mr-1.5">[{i + 1}]</strong>
                    <span className="text-[var(--text)]">{k.metin || k.kaynak || JSON.stringify(k)}</span>
                  </div>
                  {isSuperAdmin && k.anahtar && (
                    <button
                      onClick={() => kaynakcaSil(k.anahtar)}
                      title="Kaynakçayı sil"
                      className="p-1 rounded-lg hover:bg-red-500/15 text-[var(--muted)] hover:text-red-500 shrink-0"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
