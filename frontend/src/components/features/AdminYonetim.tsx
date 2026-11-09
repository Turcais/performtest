"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Building2,
  Users,
  Database,
  FileCheck2,
  Trash2,
  RefreshCw,
  Save,
  Lock,
  PlusCircle,
  Sparkles,
  BookOpen,
  UserPlus,
} from "lucide-react";
import { AdminOzetYaniti, SporcuKaydi } from "@/lib/api-client";

interface AdminYonetimProps {
  jwtToken: string;
  sporcular: SporcuKaydi[];
  rol?: string;
  toplamTest?: number;
  toplamKaynakca?: number;
  onVeriGuncellendi: () => void;
}

export const AdminYonetim: React.FC<AdminYonetimProps> = ({
  jwtToken,
  sporcular,
  rol = "super_admin",
  toplamTest = 196,
  toplamKaynakca = 191,
  onVeriGuncellendi,
}) => {
  const yetkisiz = rol === "sporcu_veli" || rol === "veli" || rol === "antrenor";
  const isSuperAdmin = rol === "super_admin";

  if (yetkisiz) {
    return (
      <div className="bg-[var(--surface)] border border-red-500/20 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-4 shadow-sm">
        <div className="w-16 h-16 bg-red-500/10 text-red-500 rounded-2xl flex items-center justify-center mx-auto text-3xl">
          🛡️
        </div>
        <h3 className="text-lg font-black text-[var(--text)]">Erişim Yetkisi Sınırı (403)</h3>
        <p className="text-xs text-[var(--muted)] leading-relaxed">
          PerformTest Sistem ve Tenant Yönetim Paneli yalnızca Süper Admin ve Kulüp Yöneticisi erişimine açıktır.
          Mevcut hesabınız ({rol}) bu modüle erişim yetkisine sahip değildir.
        </p>
      </div>
    );
  }

  const [ozet, setOzet] = useState<AdminOzetYaniti | null>(null);
  const [kullanicilar, setKullanicilar] = useState<any[]>([]);
  const [denetimKayitlari, setDenetimKayitlari] = useState<any[]>([]);
  const [mesaj, setMesaj] = useState<string>("");

  // Yeni Kulüp
  const [yeniKod, setYeniKod] = useState("");
  const [yeniAd, setYeniAd] = useState("");
  const [yeniSehir, setYeniSehir] = useState("");

  // Yeni Yetkili Kullanıcı
  const [ykEposta, setYkEposta] = useState("");
  const [ykAdSoyad, setYkAdSoyad] = useState("");
  const [ykParola, setYkParola] = useState("");
  const [ykRol, setYkRol] = useState("antrenor");
  const [ykKulup, setYkKulup] = useState("merkez");

  // KVKK Unutulma & Sporcu Silme
  const [kvkkSporcu, setKvkkSporcu] = useState(sporcular[0]?.tam_ad || "");
  const [kvkkNeden, setKvkkNeden] = useState("Veli yazılı başvurusu ve KVKK Madde 11 talebi");

  // Süper Admin: Katalog Test & Otomatik SVG Ekleme / Silme
  const [ktTestAdi, setKtTestAdi] = useState("");
  const [ktKategori, setKtKategori] = useState("Sürat ve Çabukluk");
  const [ktNitelik, setKtNitelik] = useState("sürat");
  const [ktHareketTipi, setKtHareketTipi] = useState("sprint");
  const [ktDegisken, setKtDegisken] = useState("En İyi Süre (sn)");
  const [ktBirim, setKtBirim] = useState("sn");
  const [ktAciklama, setKtAciklama] = useState("");
  const [sonUretilenSvg, setSonUretilenSvg] = useState<string>("");
  const [sonEklenenTestAdi, setSonEklenenTestAdi] = useState<string>("");
  const [silinecekTestAdi, setSilinecekTestAdi] = useState<string>("");

  // Süper Admin: Kaynakça Ekleme
  const [kaynakcaKod, setKaynakcaKod] = useState("");
  const [kaynakcaMetin, setKaynakcaMetin] = useState("");

  const adminYukle = async () => {
    try {
      const headers = { Authorization: `Bearer ${jwtToken}` };
      const [ozR, usR, audR] = await Promise.all([
        fetch("/api/v1/admin/ozet", { headers }),
        fetch("/api/v1/admin/kullanicilar", { headers }),
        fetch("/api/v1/admin/denetim-kayitlari?limit=30", { headers }),
      ]);
      const [oz, us, aud] = await Promise.all([ozR.json(), usR.json(), audR.json()]);
      setOzet(oz);
      setKullanicilar(us.kullanicilar || []);
      setDenetimKayitlari(aud.kayitlar || []);
    } catch (e) {}
  };

  useEffect(() => {
    adminYukle();
  }, [jwtToken]);

  useEffect(() => {
    if (sporcular.length > 0 && !kvkkSporcu) {
      setKvkkSporcu(sporcular[0].tam_ad);
    }
  }, [sporcular]);

  const yeniKulupEkle = async () => {
    if (!yeniKod || !yeniAd) return;
    try {
      const r = await fetch("/api/v1/admin/kulupler", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({ kod: yeniKod, ad: yeniAd, sehir: yeniSehir }),
      });
      if (r.ok) {
        setMesaj(`✓ Yeni kulüp tanımlandı: ${yeniAd}`);
        setYeniKod("");
        setYeniAd("");
        setYeniSehir("");
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const kulupSil = async (kod: string) => {
    if (kod === "merkez") return;
    if (!confirm(`"${kod}" kulübünü ve altındaki tüm verileri silmek istediğinize emin misiniz?`)) return;
    try {
      const r = await fetch(`/api/v1/admin/kulupler/${encodeURIComponent(kod)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (r.ok) {
        setMesaj(`✓ Kulüp silindi: ${kod}`);
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const yeniKullaniciEkle = async () => {
    if (!ykEposta || !ykParola) return;
    try {
      const r = await fetch("/api/v1/admin/kullanicilar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          eposta: ykEposta,
          ad_soyad: ykAdSoyad || ykEposta,
          parola: ykParola,
          rol: ykRol,
          kulup_kodu: ykKulup,
        }),
      });
      if (r.ok) {
        setMesaj(`✓ Yetkili kullanıcı eklendi: ${ykAdSoyad || ykEposta}`);
        setYkEposta("");
        setYkAdSoyad("");
        setYkParola("");
        adminYukle();
      }
    } catch (e) {}
  };

  const kullaniciSil = async (id: number, eposta: string) => {
    if (!confirm(`"${eposta}" kullanıcısını sistemden silmek istediğinize emin misiniz?`)) return;
    try {
      const r = await fetch(`/api/v1/admin/kullanicilar/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (r.ok) {
        setMesaj(`✓ Kullanıcı silindi: ${eposta}`);
        adminYukle();
      }
    } catch (e) {}
  };

  const kvkkAnonimlestir = async () => {
    if (!kvkkSporcu) return;
    if (
      !confirm(
        `${kvkkSporcu} isimli sporcunun kimlik verileri KVKK kapsamında geri döndürülemez şekilde anonimleştirilecektir. Onaylıyor musunuz?`
      )
    )
      return;
    try {
      const r = await fetch("/api/v1/admin/kvkk/anonimlestir", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          tam_ad: kvkkSporcu,
          hukuki_gerekce: kvkkNeden,
        }),
      });
      if (r.ok) {
        setMesaj(`✓ Sporcu başarıyla anonimleştirildi: ${kvkkSporcu}`);
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const sporcuSil = async () => {
    if (!kvkkSporcu) return;
    if (!confirm(`"${kvkkSporcu}" isimli sporcuyu ve tüm ölçümlerini tamamen silmek istediğinize emin misiniz?`))
      return;
    try {
      const r = await fetch(`/api/v1/admin/sporcular/${encodeURIComponent(kvkkSporcu)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (r.ok) {
        setMesaj(`✓ Sporcu ve ölçümleri sistemden silindi: ${kvkkSporcu}`);
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const adminTestEkleVeSvgUret = async () => {
    if (!ktTestAdi.trim()) return;
    try {
      const r = await fetch("/api/v1/admin/katalog/testler", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          test_adi: ktTestAdi.trim(),
          kategori: ktKategori,
          nitelik: ktNitelik,
          hareket_tipi: ktHareketTipi,
          degisken_adi: ktDegisken,
          birim: ktBirim,
          aciklama: ktAciklama.trim() || `${ktTestAdi.trim()} protokolü (${ktNitelik}).`,
        }),
      });
      const d = await r.json();
      if (r.ok && d.durum === "eklendi") {
        setSonUretilenSvg(d.svg_html || "");
        setSonEklenenTestAdi(d.test_adi);
        setMesaj(
          `✓ "${d.test_adi}" kataloğa eklendi, SVG sahnesi otomatik üretildi! Güncel Katalog: ${d.toplam_test} Test (Vitrin ve yan menü güncellendi)`
        );
        setKtTestAdi("");
        setKtAciklama("");
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const adminTestSil = async () => {
    if (!silinecekTestAdi.trim()) return;
    try {
      const r = await fetch(`/api/v1/admin/katalog/testler/${encodeURIComponent(silinecekTestAdi.trim())}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      const d = await r.json();
      if (r.ok) {
        setMesaj(`✓ "${silinecekTestAdi}" katalogdan silindi. Güncel Katalog: ${d.toplam_test} Test.`);
        setSilinecekTestAdi("");
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const adminKaynakcaEkle = async () => {
    if (!kaynakcaMetin.trim()) return;
    try {
      const r = await fetch("/api/v1/admin/katalog/kaynakca", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          anahtar: kaynakcaKod.trim() || `ref_${Date.now()}`,
          metin: kaynakcaMetin.trim(),
        }),
      });
      const d = await r.json();
      if (r.ok) {
        setMesaj(`✓ Yeni kaynakça eklendi! Güncel Kütüphane: ${d.toplam_kaynakca} Kaynakça.`);
        setKaynakcaKod("");
        setKaynakcaMetin("");
        adminYukle();
        onVeriGuncellendi();
      }
    } catch (e) {}
  };

  const m = ozet?.metrikler as any;
  const gosterilenTestSayisi = m?.toplam_test ?? toplamTest;
  const gosterilenKaynakcaSayisi = m?.toplam_kaynakca ?? toplamKaynakca;

  return (
    <div className="space-y-6">
      {/* 5'li Yönetim KPI Kartları */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm">
          <div className="text-[11px] font-bold text-[var(--muted)]">Aktif Kulüpler (Tenants)</div>
          <div className="text-2xl font-black mt-1 text-blue-500">{m?.aktif_kulup_sayisi ?? 3}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">İzole veri alanları</div>
        </div>

        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm">
          <div className="text-[11px] font-bold text-[var(--muted)]">Kayıtlı Sporcu</div>
          <div className="text-2xl font-black mt-1 text-emerald-500">{m?.toplam_sporcu ?? sporcular.length}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">KVKK Açık Rıza Onaylı</div>
        </div>

        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm">
          <div className="text-[11px] font-bold text-[var(--muted)]">Test Kataloğu & SVG</div>
          <div className="text-2xl font-black mt-1 text-indigo-500">{gosterilenTestSayisi}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">{gosterilenKaynakcaSayisi} Bilimsel Kaynakça</div>
        </div>

        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm">
          <div className="text-[11px] font-bold text-[var(--muted)]">Saha Test Ölçümleri</div>
          <div className="text-2xl font-black mt-1 text-amber-500">{m?.toplam_olcum_satiri ?? 732}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">Normatif veri tablosu</div>
        </div>

        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm col-span-2 lg:col-span-1">
          <div className="text-[11px] font-bold text-[var(--muted)]">Değiştirilemez Denetim İzi</div>
          <div className="text-2xl font-black mt-1 text-purple-500">{m?.toplam_denetim_kaydi ?? 54}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">
            Yerli Sunucu: {Math.round((ozet?.yerli_sunucu?.boyut_bayt || 180000) / 1024)} KB
          </div>
        </div>
      </div>

      {mesaj && (
        <div className="p-3.5 text-xs font-bold rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20 flex items-center justify-between">
          <span>{mesaj}</span>
          <button onClick={() => setMesaj("")} className="text-[11px] underline ml-3">
            Kapat
          </button>
        </div>
      )}

      {/* Süper Admin Özel: Dinamik Test Kataloğu, Otomatik SVG Üretimi & Kaynakça Ekle/Çıkar Merkezi */}
      {isSuperAdmin && (
        <div className="bg-[var(--surface)] border border-blue-500/30 rounded-2xl p-5 sm:p-6 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--line)] pb-3">
            <div className="flex items-center gap-2 font-extrabold text-sm">
              <Sparkles className="w-4 h-4 text-blue-500" />
              <span>
                Süper Admin — Dinamik Test Kataloğu ({gosterilenTestSayisi}), Otomatik SVG Sentezi & Kaynakça ({gosterilenKaynakcaSayisi}) Yönetimi
              </span>
            </div>
            <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20">
              Vitrin & Katalog Canlı Senkronize
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Sol: Yeni Test + Otomatik SVG Ekle */}
            <div className="lg:col-span-7 space-y-3 bg-[var(--surface-2)] p-4 rounded-2xl border border-[var(--line)] text-xs">
              <div className="font-bold text-blue-500 flex items-center gap-1.5">
                <PlusCircle className="w-4 h-4" />
                <span>+ Yeni Test Protokolü Ekle & Otomatik SVG Sahnesi Oluştur</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <input
                  value={ktTestAdi}
                  onChange={(e) => setKtTestAdi(e.target.value)}
                  placeholder="Test Adı (Örn: 30m Flying Sprint Testi)"
                  className="sm:col-span-2 p-2.5 rounded-xl bg-[var(--surface)] border border-[var(--line)] font-bold"
                />
                <select
                  value={ktKategori}
                  onChange={(e) => setKtKategori(e.target.value)}
                  className="p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
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
                <select
                  value={ktHareketTipi}
                  onChange={(e) => setKtHareketTipi(e.target.value)}
                  className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 font-bold"
                >
                  <option value="sprint">🎨 SVG: Sprint & Koşu Biyomekaniği</option>
                  <option value="yatay_sicrama">🎨 SVG: Yatay Sıçrama & Patlayıcı Güç</option>
                  <option value="dikey_sicrama">🎨 SVG: Dikey Sıçrama & Kuvvet Platformu</option>
                  <option value="ceviklik">🎨 SVG: Çeviklik, T-Testi & Slalom</option>
                  <option value="mekik_dayaniklilik">🎨 SVG: 20m Mekik & Dayanıklılık</option>
                  <option value="kuvvet_ust">🎨 SVG: Üst Gövde & Kavrama Kuvveti</option>
                  <option value="firlatma">🎨 SVG: Sağlık Topu & Balistik Fırlatma</option>
                  <option value="denge">🎨 SVG: Flamingo & Denge Platformu</option>
                  <option value="esneklik">🎨 SVG: Otur-Uzan & Esneklik Sehpası</option>
                  <option value="reaksiyon">🎨 SVG: Görsel-Motor & Reaksiyon Hızı</option>
                  <option value="antropometri">🎨 SVG: Antropometrik Boy/Kilo Sahnesi</option>
                </select>
                <input
                  value={ktDegisken}
                  onChange={(e) => setKtDegisken(e.target.value)}
                  placeholder="Değişken (Örn: En İyi Süre (sn))"
                  className="p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                />
                <input
                  value={ktBirim}
                  onChange={(e) => setKtBirim(e.target.value)}
                  placeholder="Birim (sn / cm / kg)"
                  className="p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                />
                <input
                  value={ktAciklama}
                  onChange={(e) => setKtAciklama(e.target.value)}
                  placeholder="Protokol uygulama kuralı ve saha açıklaması..."
                  className="sm:col-span-2 p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                />
              </div>

              <button
                onClick={adminTestEkleVeSvgUret}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold shadow-md transition flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Testi Ekle, Sayacı Artır ({gosterilenTestSayisi} → {gosterilenTestSayisi + 1}) & SVG Sentezle</span>
              </button>
            </div>

            {/* Sağ: Test Çıkar & Kaynakça Ekle */}
            <div className="lg:col-span-5 space-y-3 text-xs">
              <div className="p-4 rounded-2xl bg-[var(--surface-2)] border border-[var(--line)] space-y-2">
                <div className="font-bold text-red-500 flex items-center gap-1.5">
                  <Trash2 className="w-4 h-4" />
                  <span>Katalogdan Test Protokolü Çıkar / Sil</span>
                </div>
                <div className="flex gap-2">
                  <input
                    value={silinecekTestAdi}
                    onChange={(e) => setSilinecekTestAdi(e.target.value)}
                    placeholder="Silinecek testin tam adı..."
                    className="flex-1 p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                  />
                  <button
                    onClick={adminTestSil}
                    className="px-3 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition"
                  >
                    Testi Sil
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[var(--surface-2)] border border-[var(--line)] space-y-2">
                <div className="font-bold text-emerald-500 flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4" />
                  <span>+ Bilimsel Kaynakça Ekle ({gosterilenKaynakcaSayisi} → {gosterilenKaynakcaSayisi + 1})</span>
                </div>
                <input
                  value={kaynakcaKod}
                  onChange={(e) => setKaynakcaKod(e.target.value)}
                  placeholder="Atıf Kodu (Örn: Morin_2025)"
                  className="w-full p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                />
                <div className="flex gap-2">
                  <input
                    value={kaynakcaMetin}
                    onChange={(e) => setKaynakcaMetin(e.target.value)}
                    placeholder="Makale / APA kaynakça metni..."
                    className="flex-1 p-2 rounded-xl bg-[var(--surface)] border border-[var(--line)]"
                  />
                  <button
                    onClick={adminKaynakcaEkle}
                    className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition"
                  >
                    Ekle
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Otomatik Sentezlenen SVG Önizlemesi */}
          {sonUretilenSvg && (
            <div className="p-4 rounded-2xl bg-[var(--surface-2)] border border-blue-500/30 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-blue-500">
                <span>🎨 &quot;{sonEklenenTestAdi}&quot; İçin Otomatik Sentezlenen 3D/Vektör SVG Sahnesi:</span>
                <button onClick={() => setSonUretilenSvg("")} className="text-[11px] underline">
                  Önizlemeyi Gizle
                </button>
              </div>
              <div dangerouslySetInnerHTML={{ __html: sonUretilenSvg }} />
            </div>
          )}
        </div>
      )}

      {/* İki Sütun: Kulüpler & Kullanıcılar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Çoklu Kulüp Yönetimi */}
        <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Building2 className="w-4 h-4 text-blue-500" />
              Çoklu Kulüp (Multi-Tenant) Ekle / Çıkar
            </div>
            <button
              onClick={() => {
                fetch("/api/v1/admin/yedek-al", {
                  method: "POST",
                  headers: { Authorization: `Bearer ${jwtToken}` },
                }).then(() => setMesaj("✓ Anlık veritabanı yedeği alındı."));
              }}
              className="text-xs font-semibold px-2.5 py-1 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)]"
            >
              💾 DB Yedeği Al
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[var(--line)] text-[var(--muted)] text-[11px]">
                  <th className="py-2 px-2.5">Kod</th>
                  <th className="py-2 px-2.5">Kulüp Adı</th>
                  <th className="py-2 px-2.5">Sporcu</th>
                  <th className="py-2 px-2.5">Ölçüm</th>
                  {isSuperAdmin && <th className="py-2 px-2.5 text-right">İşlem</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {(ozet?.kulup_dagilimi || []).map((k) => (
                  <tr key={k.kod}>
                    <td className="py-2 px-2.5 font-mono text-[11px] text-blue-500">{k.kod}</td>
                    <td className="py-2 px-2.5 font-bold">{k.ad}</td>
                    <td className="py-2 px-2.5">{k.sporcu_sayisi}</td>
                    <td className="py-2 px-2.5">{k.olcum_sayisi}</td>
                    {isSuperAdmin && (
                      <td className="py-2 px-2.5 text-right">
                        {k.kod !== "merkez" && (
                          <button
                            onClick={() => kulupSil(k.kod)}
                            className="p-1 rounded-lg hover:bg-red-500/15 text-red-500 transition"
                            title="Kulübü Sil"
                          >
                            <Trash2 className="w-3.5 h-3.5 inline" />
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Yeni Kulüp Tanımla */}
          <div className="p-4 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl space-y-2">
            <div className="text-xs font-bold">+ Yeni Spor Kulübü / Merkez Tanımla</div>
            <div className="grid grid-cols-2 gap-2">
              <input
                placeholder="Kulüp Kodu (örn: izmir-sk)"
                value={yeniKod}
                onChange={(e) => setYeniKod(e.target.value)}
                className="text-xs p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)] focus:outline-none"
              />
              <input
                placeholder="Kulüp Adı"
                value={yeniAd}
                onChange={(e) => setYeniAd(e.target.value)}
                className="text-xs p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)] focus:outline-none"
              />
            </div>
            <div className="flex gap-2">
              <input
                placeholder="Şehir"
                value={yeniSehir}
                onChange={(e) => setYeniSehir(e.target.value)}
                className="text-xs p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)] flex-1 focus:outline-none"
              />
              <button
                onClick={yeniKulupEkle}
                className="bg-blue-600 text-white font-bold text-xs px-3 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Kulüp Oluştur
              </button>
            </div>
          </div>
        </div>

        {/* RBAC Kullanıcı Ekle/Çıkar & Sporcu Sil / KVKK Unutulma Hakkı */}
        <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Lock className="w-4 h-4 text-emerald-500" />
              RBAC Yetkili Kullanıcılar (Ekle / Çıkar)
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">
              PBKDF2-SHA256 + JWT
            </span>
          </div>

          <div className="max-h-40 overflow-y-auto space-y-1.5 pr-1">
            {kullanicilar.map((u) => (
              <div
                key={u.id}
                className="p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold">{u.ad_soyad}</div>
                  <div className="text-[11px] text-[var(--muted)]">
                    {u.eposta} · <span className="font-mono">{u.kulup_kodu || "merkez"}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--surface)] border border-[var(--line)]">
                    {u.rol}
                  </span>
                  {isSuperAdmin && u.eposta !== "admin@performtest.yerli" && (
                    <button
                      onClick={() => kullaniciSil(u.id, u.eposta)}
                      className="p-1 rounded-lg hover:bg-red-500/15 text-red-500 transition"
                      title="Kullanıcıyı Sil"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Yeni Kullanıcı Ekleme Formu */}
          <div className="p-3.5 bg-[var(--surface-2)] border border-[var(--line)] rounded-xl space-y-2 text-xs">
            <div className="font-bold flex items-center gap-1.5">
              <UserPlus className="w-3.5 h-3.5 text-emerald-500" />
              <span>+ Yeni Yetkili Kullanıcı / Antrenör / Veli Ekle</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                value={ykAdSoyad}
                onChange={(e) => setYkAdSoyad(e.target.value)}
                placeholder="Ad Soyad"
                className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
              />
              <input
                value={ykEposta}
                onChange={(e) => setYkEposta(e.target.value)}
                placeholder="E-posta"
                className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
              />
              <input
                type="password"
                value={ykParola}
                onChange={(e) => setYkParola(e.target.value)}
                placeholder="Parola"
                className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
              />
              <select
                value={ykRol}
                onChange={(e) => setYkRol(e.target.value)}
                className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)]"
              >
                <option value="antrenor">Antrenör</option>
                <option value="kulup_yoneticisi">Kulüp Yöneticisi</option>
                <option value="sporcu_veli">Sporcu Velisi</option>
                <option value="super_admin">Süper Admin</option>
              </select>
            </div>
            <button
              onClick={yeniKullaniciEkle}
              className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition"
            >
              Kullanıcı Oluştur
            </button>
          </div>

          {/* Sporcu Silme & KVKK Madde 11 Unutulma Hakkı */}
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl space-y-2">
            <div className="text-xs font-bold text-red-500 flex items-center gap-1.5">
              <Trash2 className="w-4 h-4" />
              Sporcu Silme & KVKK Madde 7/11 Anonimleştirme
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={kvkkSporcu}
                onChange={(e) => setKvkkSporcu(e.target.value)}
                className="text-xs p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)] flex-1 min-w-[160px]"
              >
                {sporcular.map((s) => (
                  <option key={s.id} value={s.tam_ad}>
                    {s.tam_ad}
                  </option>
                ))}
              </select>
              <button
                onClick={kvkkAnonimlestir}
                className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-3 py-2 rounded-lg transition"
              >
                KVKK Anonimleştir
              </button>
              <button
                onClick={sporcuSil}
                className="bg-red-600 hover:bg-red-700 text-white font-bold text-xs px-3 py-2 rounded-lg transition"
              >
                🗑️ Sporcuyu Sil
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Değiştirilemez KVKK Denetim İzi (Audit Log) */}
      <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
          <div className="flex items-center gap-2 font-bold text-sm">
            <FileCheck2 className="w-4 h-4 text-purple-500" />
            Değiştirilemez KVKK Denetim İzi (Immutable Audit Log)
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-500">
            Append-Only Güvenlik Kaydı
          </span>
        </div>

        <div className="max-h-60 overflow-y-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[var(--line)] text-[var(--muted)] text-[11px]">
                <th className="py-2 px-2.5">Zaman Damgası</th>
                <th className="py-2 px-2.5">Kullanıcı</th>
                <th className="py-2 px-2.5">Eylem</th>
                <th className="py-2 px-2.5">Hedef Varlık</th>
                <th className="py-2 px-2.5">IP Adresi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--line)]">
              {denetimKayitlari.map((a: any) => (
                <tr key={a.id} className="hover:bg-[var(--surface-2)] transition">
                  <td className="py-2 px-2.5 font-mono text-[11px] text-[var(--muted)]">{a.zaman_damgasi}</td>
                  <td className="py-2 px-2.5 font-bold">{a.kullanici_eposta}</td>
                  <td className="py-2 px-2.5 font-mono text-blue-500">{a.eylem}</td>
                  <td className="py-2 px-2.5">{a.hedef_varlik || "—"}</td>
                  <td className="py-2 px-2.5 font-mono text-[11px] text-[var(--muted)]">{a.ip_adresi}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
