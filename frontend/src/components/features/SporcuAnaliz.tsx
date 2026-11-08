"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  UserPlus,
  FileText,
  Activity,
  Award,
  TrendingUp,
  Sparkles,
  Compass,
  AlertTriangle,
  CheckCircle2,
  X,
  Timer,
  Save,
  PlusCircle,
} from "lucide-react";
import { SporcuKaydi, SporcuAnalizYaniti } from "@/lib/api-client";

interface SporcuAnalizProps {
  sporcular: SporcuKaydi[];
  seciliSporcu: string;
  onSporcuSec: (tamAd: string) => void;
  analiz: SporcuAnalizYaniti | null;
  yukleniyor: boolean;
  onYeniSporcuModal: () => void;
  onSvgProtokolAc: (testAdi: string) => void;
  aktifKulup: string;
  rol?: string;
  jwtToken?: string;
  onOlcumKaydedildi?: () => void;
}

export const SporcuAnaliz: React.FC<SporcuAnalizProps> = ({
  sporcular,
  seciliSporcu,
  onSporcuSec,
  analiz,
  yukleniyor,
  onYeniSporcuModal,
  onSvgProtokolAc,
  aktifKulup,
  rol = "super_admin",
  jwtToken = "",
  onOlcumKaydedildi,
}) => {
  const isVeli = rol === "sporcu_veli" || rol === "veli";
  const sonucGirebilir = !isVeli; // super_admin, kulup_yoneticisi, antrenor

  const [arama, setArama] = useState("");
  const [cinsiyetFiltre, setCinsiyetFiltre] = useState<string>("");
  const [bransModalAcik, setBransModalAcik] = useState(false);

  // Hızlı Sonuç / Ölçüm Giriş Modalı
  const [olcumModalAcik, setOlcumModalAcik] = useState(false);
  const [olcumTesti, setOlcumTesti] = useState("20m Sprint");
  const [olcumDegiskeni, setOlcumDegiskeni] = useState("En İyi Süre (sn)");
  const [olcumDegeri, setOlcumDegeri] = useState<number>(3.65);
  const [olcumOturum, setOlcumOturum] = useState("2026 Güz Saha Taraması");
  const [canliZSonuc, setCanliZSonuc] = useState<any>(null);
  const [olcumKaydediliyor, setOlcumKaydediliyor] = useState(false);
  const [olcumMesaj, setOlcumMesaj] = useState<string | null>(null);

  const hizliTestler = [
    { ad: "20m Sprint", deg: "En İyi Süre (sn)", varsayilan: 3.65, birim: "sn" },
    { ad: "Durarak Uzun Atlama", deg: "Deneme 1 (cm)", varsayilan: 150, birim: "cm" },
    { ad: "El Kavrama Kuvveti (Baskın El)", deg: "Değer (kg)", varsayilan: 18, birim: "kg" },
    { ad: "Flamingo Denge Testi", deg: "Düşüş Sayısı", varsayilan: 5, birim: "adet" },
    { ad: "Mekik Testi (30 sn)", deg: "Tekrar Sayısı", varsayilan: 22, birim: "tekrar" },
    { ad: "Otur-Uzan Esneklik", deg: "Uzanma Mesafesi (cm)", varsayilan: 19, birim: "cm" },
    { ad: "Sağlık Topu Fırlatma (1 kg)", deg: "Mesafe (m)", varsayilan: 4.8, birim: "m" },
    { ad: "Çeviklik T-Testi", deg: "Süre (sn)", varsayilan: 11.2, birim: "sn" },
    { ad: "10x5m Mekik Koşusu", deg: "Süre (sn)", varsayilan: 21.4, birim: "sn" },
    { ad: "20m Mekik Koşusu (Yo-Yo/Beep)", deg: "Tamamlanan Mekik", varsayilan: 35, birim: "mekik" },
  ];

  const testSecildi = (tAd: string) => {
    setOlcumTesti(tAd);
    const bul = hizliTestler.find((x) => x.ad === tAd);
    if (bul) {
      setOlcumDegiskeni(bul.deg);
      setOlcumDegeri(bul.varsayilan);
    }
  };

  const p = (analiz?.profil as Record<string, string>) || {};
  const sporcuYasi = parseFloat(p["Yaş"] || "10");
  const sporcuCinsiyet = p.Cinsiyet || "Erkek";

  // Canlı Z-skoru anlık hesaplama
  useEffect(() => {
    if (!olcumModalAcik || !olcumTesti || isNaN(olcumDegeri)) return;
    fetch("/api/v1/analiz/degerlendir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        test_adi: olcumTesti,
        degisken: olcumDegiskeni,
        deger: olcumDegeri,
        yas: sporcuYasi,
        cinsiyet: sporcuCinsiyet,
      }),
    })
      .then((r) => r.json())
      .then((d) => setCanliZSonuc(d))
      .catch(() => {});
  }, [olcumModalAcik, olcumTesti, olcumDegiskeni, olcumDegeri, sporcuYasi, sporcuCinsiyet]);

  const hizliOlcumKaydet = async () => {
    if (!seciliSporcu) return;
    setOlcumKaydediliyor(true);
    setOlcumMesaj(null);
    try {
      const res = await fetch("/api/v1/oturumlar/olcum-kaydet", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: jwtToken ? `Bearer ${jwtToken}` : "",
        },
        body: JSON.stringify({
          kulup_kodu: aktifKulup,
          sporcu_adi: seciliSporcu,
          test_adi: olcumTesti,
          test_yasi: sporcuYasi,
          oturum: olcumOturum,
          olcumler: { [olcumDegiskeni]: olcumDegeri },
        }),
      });
      if (res.ok) {
        setOlcumMesaj("✓ Ölçüm başarıyla kaydedildi! Analiz profili güncelleniyor...");
        if (onOlcumKaydedildi) onOlcumKaydedildi();
        setTimeout(() => {
          setOlcumModalAcik(false);
          setOlcumMesaj(null);
        }, 1200);
      } else {
        const err = await res.json();
        setOlcumMesaj(`✕ Hata: ${err.hata || "Kayıt başarısız"}`);
      }
    } catch {
      setOlcumMesaj("✕ Sunucu iletişim hatası.");
    } finally {
      setOlcumKaydediliyor(false);
    }
  };

  const filtrelenmis = sporcular.filter((s) => {
    if (cinsiyetFiltre && s.cinsiyet !== cinsiyetFiltre) return false;
    if (
      arama &&
      !s.tam_ad.toLowerCase().includes(arama.toLowerCase()) &&
      !(s.spor_dali || "").toLowerCase().includes(arama.toLowerCase())
    )
      return false;
    return true;
  });

  const boy = parseFloat(p["Boy (cm)"] || "0");
  const kilo = parseFloat(p["Kilo (kg)"] || "0");
  const vki = boy > 0 && kilo > 0 ? (kilo / Math.pow(boy / 100, 2)).toFixed(1) : "—";
  const satirlar = analiz?.z_profili?.satirlar || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Sol Sütun: Sporcu Listesi */}
      <div className="lg:col-span-4 bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-4 flex flex-col h-[calc(100vh-7.5rem)]">
        <div className="flex items-center justify-between mb-3">
          <div className="font-bold text-sm">
            {isVeli ? `Çocuğunuz (${filtrelenmis.length})` : `Sporcular (${filtrelenmis.length})`}
          </div>
          {!isVeli && (
            <button
              onClick={onYeniSporcuModal}
              className="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-2.5 py-1.5 rounded-lg shadow-sm transition"
            >
              <UserPlus className="w-3.5 h-3.5" />
              Yeni Kayıt
            </button>
          )}
        </div>

        {/* Arama & Cinsiyet Filtreleri */}
        <div className="relative mb-2.5">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-[var(--muted)]" />
          <input
            type="text"
            placeholder="İsim veya spor dalı ara..."
            value={arama}
            onChange={(e) => setArama(e.target.value)}
            className="w-full text-xs pl-9 pr-3 py-2 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-1.5 mb-3">
          {[
            { id: "", label: "Tümü" },
            { id: "Erkek", label: "Erkek" },
            { id: "Kadın", label: "Kadın" },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setCinsiyetFiltre(f.id)}
              className={`flex-1 text-[11px] font-semibold py-1 rounded-lg border transition ${
                cinsiyetFiltre === f.id
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-[var(--surface-2)] border-[var(--line)] text-[var(--muted)] hover:text-[var(--text)]"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Liste */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {filtrelenmis.map((s) => {
            const aktif = s.tam_ad === seciliSporcu;
            const basHarfler = s.tam_ad
              .split(" ")
              .map((w) => w[0])
              .join("")
              .slice(0, 2)
              .toUpperCase();
            return (
              <div
                key={s.id}
                onClick={() => onSporcuSec(s.tam_ad)}
                className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  aktif
                    ? "bg-blue-500/10 border-blue-500 shadow-sm"
                    : "bg-[var(--surface-2)] border-[var(--line)] hover:border-blue-400/50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold ${
                      s.cinsiyet === "Kadın"
                        ? "bg-rose-500/15 text-rose-500"
                        : "bg-blue-500/15 text-blue-500"
                    }`}
                  >
                    {basHarfler}
                  </div>
                  <div>
                    <div className="text-xs font-bold">{s.tam_ad}</div>
                    <div className="text-[11px] text-[var(--muted)]">
                      {s.cinsiyet} · {s.yas ?? "-"} yaş · {s.spor_dali || "Genel"}
                    </div>
                  </div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[var(--surface)] border border-[var(--line)]">
                  {s.olcum_sayisi} ölçüm
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sağ Sütun: Analiz, Radar ve Normatif Tablo */}
      <div className="lg:col-span-8 space-y-6">
        {yukleniyor ? (
          <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-12 text-center text-[var(--muted)]">
            Sporcu analiz motoru hesaplıyor...
          </div>
        ) : analiz ? (
          <>
            {/* Veli Bilgilendirme Portalı Rozeti */}
            {isVeli && (
              <div className="p-4 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-2xl text-xs text-amber-500 font-semibold flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">👨‍👩‍👦</span>
                  <div>
                    <span className="font-extrabold">Veli Bilgilendirme Portalı:</span> Çocuğunuzun fiziksel gelişim profilini, Cole & Green LMS standart puanlarını ve bilimsel branş yönlendirme analizini inceliyorsunuz.
                  </div>
                </div>
                <span className="text-[10px] bg-amber-500/20 text-amber-400 px-3 py-1 rounded-full font-bold uppercase tracking-wider shrink-0">
                  Salt Okunur
                </span>
              </div>
            )}

            {/* Başlık Kartı */}
            <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-5 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div
                    className={`w-14 h-14 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-md ${
                      p.Cinsiyet === "Kadın" ? "bg-gradient-to-tr from-pink-500 to-rose-400" : "bg-gradient-to-tr from-blue-600 to-cyan-500"
                    }`}
                  >
                    {seciliSporcu
                      .split(" ")
                      .map((x) => x[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-xl font-black tracking-tight">{seciliSporcu}</h2>
                    <p className="text-xs text-[var(--muted)] font-medium mt-0.5">
                      {p.Cinsiyet || "-"} · Branş: {p["Spor Dalı"] || "Genel Atletik Performans"} · Kulüp: {aktifKulup} · Rapor: {analiz.rapor_tarihi}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {/* Antrenör ve Yöneticiler için Hızlı Sonuç Girdi Butonu */}
                  {sonucGirebilir && (
                    <button
                      onClick={() => setOlcumModalAcik(true)}
                      className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-700 hover:to-teal-600 text-white shadow-md shadow-emerald-500/20 transition hover:scale-[1.02]"
                      title="Seçili sporcu için anlık yeni saha test ölçüm girişi yap"
                    >
                      <Timer className="w-3.5 h-3.5" />
                      Sonuç / Ölçüm Gir
                    </button>
                  )}

                  <button
                    onClick={() => setBransModalAcik(true)}
                    className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-md shadow-orange-500/20 transition hover:scale-[1.02]"
                    title="Opstoel (2015) Bilimsel Branş Yönlendirme ve Yetenek Seçimi Karar Desteği"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Branşa Yönlendir
                  </button>
                  <button
                    onClick={() => window.open(`/api/v1/sporcular/${encodeURIComponent(seciliSporcu)}/rapor?kulup_kodu=${encodeURIComponent(aktifKulup)}&tur=veli`, "_blank")}
                    className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    Veli Raporu (A4)
                  </button>
                  {!isVeli && (
                    <button
                      onClick={() => window.open(`/api/v1/sporcular/${encodeURIComponent(seciliSporcu)}/rapor?kulup_kodu=${encodeURIComponent(aktifKulup)}&tur=antrenor`, "_blank")}
                      className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
                    >
                      <Award className="w-3.5 h-3.5 text-emerald-500" />
                      Antrenör Raporu
                    </button>
                  )}
                </div>
              </div>

              {/* KPI Izgarası */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 pt-4 border-t border-[var(--line)]">
                <div className="bg-[var(--surface-2)] p-3 rounded-xl border border-[var(--line)]">
                  <div className="text-[11px] text-[var(--muted)] font-bold">Takvim Yaşı</div>
                  <div className="text-lg font-black mt-0.5">{p["Yaş"] ?? "—"} <span className="text-xs font-normal">yaş</span></div>
                  <div className="text-[10px] text-[var(--muted)] mt-0.5">{p.Cinsiyet} · Doğum Kayıtlı</div>
                </div>

                <div className="bg-[var(--surface-2)] p-3 rounded-xl border border-[var(--line)]">
                  <div className="text-[11px] text-[var(--muted)] font-bold">Boy / Ağırlık</div>
                  <div className="text-lg font-black mt-0.5">{boy} <span className="text-xs font-normal">cm</span> / {kilo} <span className="text-xs font-normal">kg</span></div>
                  <div className="text-[10px] text-[var(--muted)] mt-0.5">VKİ: <strong>{vki} kg/m²</strong></div>
                </div>

                <div className="bg-[var(--surface-2)] p-3 rounded-xl border border-[var(--line)]">
                  <div className="text-[11px] text-[var(--muted)] font-bold">Fiziksel Yatkınlık</div>
                  <div className="text-xs font-extrabold mt-1 text-blue-500 truncate">
                    {(analiz.fiziksel_pencere || []).join(" · ") || "Değerlendiriliyor"}
                  </div>
                  <div className="text-[10px] text-[var(--muted)] mt-1">Opstoel ve ark. (2015)</div>
                </div>

                <div className="bg-[var(--surface-2)] p-3 rounded-xl border border-[var(--line)]">
                  <div className="text-[11px] text-[var(--muted)] font-bold">Normlu Testler</div>
                  <div className="text-lg font-black mt-0.5">{satirlar.length} <span className="text-xs font-normal">parametre</span></div>
                  <div className="text-[10px] text-[var(--muted)] mt-0.5">Toplam {(analiz.kayitli_testler || []).length} test kaydı</div>
                </div>
              </div>
            </div>

            {/* Radar ve Branş Yatkınlık İki Sütun */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Radar Grafiği */}
              <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-5 shadow-sm flex flex-col items-center justify-center">
                <div className="w-full flex items-center justify-between mb-2">
                  <div className="text-xs font-bold flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-blue-500" />
                    Çok Boyutlu Biyomotor Radar Profili
                  </div>
                  <span className="text-[10px] text-[var(--muted)]">LMS Standart Puanları</span>
                </div>
                <div
                  className="w-full flex items-center justify-center p-2"
                  dangerouslySetInnerHTML={{
                    __html: analiz.radar_svg || "<div class='text-xs text-[var(--muted)]'>En az 3 test gereklidir.</div>",
                  }}
                />
              </div>

              {/* Branş Yatkınlık Kartı */}
              <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-5 shadow-sm space-y-4">
                <div className="text-xs font-bold flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  Önerilen Spor Branş Yatkınlığı (Opstoel Modeli)
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {[
                    "Top sporları",
                    "Raket sporları",
                    "Yüzme",
                    "Cimnastik",
                    "Dövüş sporları",
                    "Dans",
                  ].map((g) => {
                    const yatkin = (analiz.fiziksel_pencere || []).includes(g);
                    return (
                      <div
                        key={g}
                        className={`p-2.5 rounded-xl border flex items-center justify-between text-xs font-bold ${
                          yatkin
                            ? "bg-emerald-500/10 border-emerald-500 text-emerald-500"
                            : "bg-[var(--surface-2)] border-[var(--line)] text-[var(--muted)]"
                        }`}
                      >
                        <span>{g}</span>
                        <span>{yatkin ? "★ Yatkın" : "İzlem"}</span>
                      </div>
                    );
                  })}
                </div>

                <div className="p-3 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl text-[11px] text-[var(--muted)] leading-relaxed">
                  💡 <strong>Antrenör Notu:</strong> Çocuğun antropometrik ölçüleri ve biyomotor test persentilleri ulusal norm havuzuna göre ağırlıklandırılarak branş yatkınlık penceresi üretilmiştir.
                </div>
              </div>
            </div>

            {/* Test Parametre Tablosu */}
            <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="font-bold text-sm">Normatif Test & Z-Skor Değerlendirmesi</div>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[var(--surface-2)] border border-[var(--line)]">
                  {satirlar.length} Parametre
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[var(--line)] text-[var(--muted)] text-[11px]">
                      <th className="py-2.5 px-3">Test Protokolü</th>
                      <th className="py-2.5 px-3">Değişken</th>
                      <th className="py-2.5 px-3">Ham Değer</th>
                      <th className="py-2.5 px-3">Yaşıt Persentili</th>
                      <th className="py-2.5 px-3">Performans Z-Skoru</th>
                      <th className="py-2.5 px-3 text-right">Protokol</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--line)]">
                    {satirlar.map((s, idx) => {
                      const z = parseFloat(String(s["Z (performans)"] ?? s.Z ?? "0"));
                      const zMetin = isNaN(z) ? "—" : `${z >= 0 ? "+" : ""}${z.toFixed(2)} SD`;
                      const pctSayi = Math.max(8, Math.min(98, Math.round(50 + (isNaN(z) ? 0 : z * 22))));
                      const testAdi = String(s.Test || "");
                      return (
                        <tr key={idx} className="hover:bg-[var(--surface-2)] transition">
                          <td className="py-2.5 px-3 font-bold">{testAdi}</td>
                          <td className="py-2.5 px-3 text-[var(--muted)]">{String(s["Değişken"] || "")}</td>
                          <td className="py-2.5 px-3 font-extrabold">{String(s["Değer"] ?? "—")}</td>
                          <td className="py-2.5 px-3">
                            <div className="w-24 bg-[var(--line)] h-2 rounded-full overflow-hidden inline-block align-middle mr-2">
                              <div
                                className="bg-blue-500 h-full rounded-full"
                                style={{ width: `${pctSayi}%` }}
                              />
                            </div>
                            <span className="font-semibold text-[11px]">{String(s.Persentil ?? "—")}</span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span
                              className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                                z >= 0.75
                                  ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                                  : z <= -0.75
                                  ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                                  : "bg-[var(--surface-2)] text-[var(--muted)]"
                              }`}
                            >
                              {zMetin}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <button
                              onClick={() => onSvgProtokolAc(testAdi)}
                              className="text-[11px] font-bold text-blue-500 hover:text-blue-600 bg-blue-500/10 hover:bg-blue-500/20 px-2 py-1 rounded-lg transition"
                            >
                              🎨 SVG Sahne
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-12 text-center text-[var(--muted)]">
            Sol listeden bir sporcu seçin.
          </div>
        )}
      </div>
      {/* Branşa Yönlendirme ve Yetenek Seçimi Modalı */}
      {bransModalAcik && analiz && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[var(--surface)] border border-[var(--line)] rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-white shadow-md shadow-orange-500/20">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-base tracking-tight">Branşa Yönlendirme & Yetenek Modeli</h3>
                  <p className="text-xs text-[var(--muted)]">Opstoel ve ark. (2015) Motorik Uygunluk Matrisi · {seciliSporcu}</p>
                </div>
              </div>
              <button
                onClick={() => setBransModalAcik(false)}
                className="p-1.5 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] text-[var(--muted)]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Belirgin Fark Yok / Birincil Öneri Durum Kartı */}
            {analiz.brans_eslestirme?.ayirt_edilemez ? (
              <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="text-sm font-bold text-amber-600 dark:text-amber-400">
                    ⚠️ Belirgin Fark Yok — Çok Yönlü Branşlaşma Tavsiye Edilir
                  </div>
                  <p className="text-xs text-[var(--muted)] leading-relaxed">
                    Sporcunun motorik Z-skorları en az iki branş grubunda birbirine çok yakın çıkmıştır (Öklid yayılımı &lt; 0.15 eşiği).
                    Bilimsel literatür (Côté et al. 2009; Opstoel 2015), bu evrede erken özelleşme yerine sporcunun birden fazla branşı (örn. Yüzme + Top Sporları) paralel yürüterek genel atletik temelini korumasını önermektedir.
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                    🎯 Yatkın Olduğu Branş: {analiz.brans_eslestirme?.siralama?.[0]?.[0] || (analiz.fiziksel_pencere?.[0] ?? "Top sporları")}
                  </div>
                  <p className="text-xs text-[var(--muted)] leading-relaxed">
                    Sporcunun kuvvet, sürat, çabukluk ve denge bileşenleri bu branş grubunun gereksinimleriyle istatistiksel olarak en yüksek uyumu göstermektedir.
                  </p>
                </div>
              </div>
            )}

            {/* Opstoel 6 Branş Grubu Uygunluk Sıralaması */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-[var(--muted)] uppercase tracking-wider">
                Opstoel (2015) 6 Branş Grubu Uygunluk Skorları
              </div>
              <div className="space-y-2">
                {(analiz.brans_eslestirme?.siralama && analiz.brans_eslestirme.siralama.length > 0
                  ? analiz.brans_eslestirme.siralama
                  : [
                      ["Top sporları", 0.21],
                      ["Raket sporları", 0.32],
                      ["Yüzme", 0.37],
                      ["Dans", 0.39],
                      ["Jimnastik", 0.42],
                      ["Dövüş sporları", 0.44],
                    ]
                ).map(([g, skorRaw], idx) => {
                  const skor = typeof skorRaw === "number" ? skorRaw : 0.5;
                  const uyumYuzde = Math.max(15, Math.min(98, Math.round((1 - skor / 1.0) * 100)));
                  const birincil = idx === 0;
                  const yatkin = (analiz.fiziksel_pencere || []).includes(String(g));

                  return (
                    <div
                      key={String(g)}
                      className={`p-3 rounded-2xl border transition flex flex-col gap-1.5 ${
                        birincil
                          ? "bg-blue-500/10 border-blue-500/40"
                          : yatkin
                          ? "bg-emerald-500/5 border-emerald-500/20"
                          : "bg-[var(--surface-2)] border-[var(--line)]"
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs font-bold">
                        <span className="flex items-center gap-2">
                          <span className="text-[10px] w-5 h-5 rounded-full bg-[var(--surface)] border flex items-center justify-center font-black">
                            {idx + 1}
                          </span>
                          {String(g)}
                          {birincil && <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-600 text-white font-bold">En Yüksek Uyum</span>}
                          {yatkin && !birincil && <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-bold">Pencere İçi</span>}
                        </span>
                        <span className="text-[11px] text-[var(--muted)]">Uyum İndeksi: %{uyumYuzde}</span>
                      </div>
                      <div className="w-full bg-[var(--line)] h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            birincil
                              ? "bg-gradient-to-r from-blue-500 to-indigo-600"
                              : yatkin
                              ? "bg-emerald-500"
                              : "bg-[var(--muted)]/40"
                          }`}
                          style={{ width: `${uyumYuzde}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Metodolojik Bilgi Notu */}
            <div className="p-3 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl text-[11px] text-[var(--muted)] leading-relaxed">
              📘 <strong>Bilimsel Yöntem:</strong> Opstoel ve ark. (2015), <em>Anthropometric Characteristics and Physical Fitness as Predictors of Sport Participation</em> çalışmasına dayalıdır. LMS Z-skorları TSYT ve Eurofit norm havuzundaki yaş ve cinsiyet persentilleriyle ağırlıklandırılarak karar matrisine aktarılır.
            </div>

            <div className="flex items-center justify-end gap-3 pt-2 border-t border-[var(--line)]">
              <button
                onClick={() => setBransModalAcik(false)}
                className="px-4 py-2 text-xs font-semibold rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] transition"
              >
                Kapat
              </button>
              <button
                onClick={() => {
                  window.open(`/api/v1/sporcular/${encodeURIComponent(seciliSporcu)}/rapor?kulup_kodu=${encodeURIComponent(aktifKulup)}&tur=veli`, "_blank");
                }}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 transition"
              >
                <FileText className="w-3.5 h-3.5" />
                Veli Yetenek Raporunu İndir (A4)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hızlı Saha Ölçüm & Test Sonuç Girdisi Modalı (Antrenör & Admin) */}
      {olcumModalAcik && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setOlcumModalAcik(false)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-3xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
                  <Timer className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-base tracking-tight">Hızlı Test Sonuç Girdisi</h3>
                  <p className="text-xs text-[var(--muted)] font-medium">
                    {seciliSporcu} · {sporcuCinsiyet} · {sporcuYasi} Yaş · {aktifKulup}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setOlcumModalAcik(false)}
                className="p-1.5 rounded-xl border border-[var(--line)] hover:bg-[var(--surface-2)] text-[var(--muted)]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {olcumMesaj && (
              <div
                className={`p-3 text-xs font-semibold rounded-xl border flex items-center gap-2 ${
                  olcumMesaj.startsWith("✓")
                    ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                    : "bg-red-500/10 text-red-500 border-red-500/20"
                }`}
              >
                <span>{olcumMesaj}</span>
              </div>
            )}

            <div className="space-y-3.5 text-xs font-medium">
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">
                  Uygulanan Saha Test Protokolü
                </label>
                <select
                  value={olcumTesti}
                  onChange={(e) => testSecildi(e.target.value)}
                  className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 font-bold focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  {hizliTestler.map((t) => (
                    <option key={t.ad} value={t.ad}>
                      {t.ad} ({t.deg})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">
                    Ölçülen Değişken Adı
                  </label>
                  <input
                    value={olcumDegiskeni}
                    onChange={(e) => setOlcumDegiskeni(e.target.value)}
                    className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">
                    Ham Ölçüm Değeri
                  </label>
                  <input
                    type="number"
                    step="0.05"
                    value={olcumDegeri}
                    onChange={(e) => setOlcumDegeri(parseFloat(e.target.value) || 0)}
                    className="w-full font-black text-base bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-emerald-500"
                  />
                </div>
              </div>

              {/* Anlık Canlı Norm & Z-Skor Geri Bildirimi */}
              <div className="p-3.5 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 rounded-2xl space-y-2">
                <div className="text-[11px] font-bold text-emerald-500 flex items-center justify-between">
                  <span>⚡ Canlı Biyomotor Norm Değerlendirmesi</span>
                  <span className="text-[10px] font-mono bg-emerald-500/20 px-2 py-0.5 rounded-full">
                    LMS Box-Cox
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1 border-t border-emerald-500/20">
                  <div>
                    <span className="text-[10px] text-[var(--muted)] block">Yaşıt Persentili</span>
                    <span className="text-sm font-black text-emerald-500">
                      {canliZSonuc?.persentil?.persentil_aralik || canliZSonuc?.persentil || "Hesaplanıyor..."}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[var(--muted)] block">Performans Z-Skoru</span>
                    <span className="text-sm font-black font-mono">
                      {canliZSonuc?.z_skoru?.z_performans !== undefined
                        ? `${canliZSonuc.z_skoru.z_performans >= 0 ? "+" : ""}${Number(canliZSonuc.z_skoru.z_performans).toFixed(2)} SD`
                        : "Norm değerlendiriliyor"}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">
                  Ölçüm Oturumu / Tarama Adı
                </label>
                <input
                  value={olcumOturum}
                  onChange={(e) => setOlcumOturum(e.target.value)}
                  className="w-full bg-[var(--surface-2)] border border-[var(--line)] rounded-xl p-2.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <button
                onClick={hizliOlcumKaydet}
                disabled={olcumKaydediliyor}
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold py-3 rounded-xl shadow-md transition disabled:opacity-50 mt-2"
              >
                <Save className="w-4 h-4" />
                {olcumKaydediliyor ? "Kaydediliyor..." : "Ölçümü Sisteme Kaydet & Analizi Güncelle"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

