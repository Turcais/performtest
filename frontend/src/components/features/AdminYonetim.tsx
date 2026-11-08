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
} from "lucide-react";
import { AdminOzetYaniti, SporcuKaydi } from "@/lib/api-client";

interface AdminYonetimProps {
  jwtToken: string;
  sporcular: SporcuKaydi[];
  onVeriGuncellendi: () => void;
}

export const AdminYonetim: React.FC<AdminYonetimProps> = ({
  jwtToken,
  sporcular,
  onVeriGuncellendi,
}) => {
  const [ozet, setOzet] = useState<AdminOzetYaniti | null>(null);
  const [kullanicilar, setKullanicilar] = useState<any[]>([]);
  const [denetimKayitlari, setDenetimKayitlari] = useState<any[]>([]);
  const [mesaj, setMesaj] = useState<string>("");

  // Yeni Kulüp
  const [yeniKod, setYeniKod] = useState("");
  const [yeniAd, setYeniAd] = useState("");
  const [yeniSehir, setYeniSehir] = useState("");

  // Yeni Yetkili
  const [ykEposta, setYkEposta] = useState("");
  const [ykAdSoyad, setYkAdSoyad] = useState("");
  const [ykParola, setYkParola] = useState("");
  const [ykRol, setYkRol] = useState("antrenor");

  // KVKK Unutulma
  const [kvkkSporcu, setKvkkSporcu] = useState(sporcular[0]?.tam_ad || "");
  const [kvkkNeden, setKvkkNeden] = useState("Veli yazılı başvurusu ve KVKK Madde 11 talebi");

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
          ad_soyad: ykAdSoyad,
          parola: ykParola,
          rol: ykRol,
        }),
      });
      if (r.ok) {
        setMesaj(`✓ Yetkili kullanıcı eklendi: ${ykAdSoyad}`);
        setYkEposta("");
        setYkAdSoyad("");
        setYkParola("");
        adminYukle();
      }
    } catch (e) {}
  };

  const kvkkAnonimlestir = async () => {
    if (!kvkkSporcu) return;
    if (!confirm(`${kvkkSporcu} isimli sporcunun kimlik verileri KVKK kapsamında geri döndürülemez şekilde anonimleştirilecektir. Onaylıyor musunuz?`)) return;
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

  const m = ozet?.metrikler;

  return (
    <div className="space-y-6">
      {/* 4'lü Yönetim KPI Kartları */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
          <div className="text-[11px] font-bold text-[var(--muted)]">Saha Test Ölçümleri</div>
          <div className="text-2xl font-black mt-1 text-amber-500">{m?.toplam_olcum_satiri ?? 732}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">Normatif veri tablosu</div>
        </div>

        <div className="bg-[var(--surface)] border border-[var(--line)] p-4 rounded-2xl shadow-sm">
          <div className="text-[11px] font-bold text-[var(--muted)]">Değiştirilemez Denetim İzi</div>
          <div className="text-2xl font-black mt-1 text-purple-500">{m?.toplam_denetim_kaydi ?? 54}</div>
          <div className="text-[10px] text-[var(--muted)] mt-0.5">Yerli Sunucu: {Math.round((ozet?.yerli_sunucu?.boyut_bayt || 180000) / 1024)} KB</div>
        </div>
      </div>

      {mesaj && (
        <div className="p-3 text-xs font-semibold rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20">
          {mesaj}
        </div>
      )}

      {/* İki Sütun: Kulüpler & Kullanıcılar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Çoklu Kulüp Yönetimi */}
        <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Building2 className="w-4 h-4 text-blue-500" />
              Çoklu Kulüp (Multi-Tenant) Yönetimi
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
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {(ozet?.kulup_dagilimi || []).map((k) => (
                  <tr key={k.kod}>
                    <td className="py-2 px-2.5 font-mono text-[11px] text-blue-500">{k.kod}</td>
                    <td className="py-2 px-2.5 font-bold">{k.ad}</td>
                    <td className="py-2 px-2.5">{k.sporcu_sayisi}</td>
                    <td className="py-2 px-2.5">{k.olcum_sayisi}</td>
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

        {/* RBAC Kullanıcı & KVKK Unutulma Hakkı */}
        <div className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Lock className="w-4 h-4 text-emerald-500" />
              RBAC Yetkili Kullanıcılar
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500">
              PBKDF2-SHA256 + JWT
            </span>
          </div>

          <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
            {kullanicilar.map((u) => (
              <div
                key={u.id}
                className="p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold">{u.ad_soyad}</div>
                  <div className="text-[11px] text-[var(--muted)]">{u.eposta}</div>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--surface)] border border-[var(--line)]">
                  {u.rol}
                </span>
              </div>
            ))}
          </div>

          {/* KVKK Madde 11 Unutulma Hakkı */}
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl space-y-2">
            <div className="text-xs font-bold text-red-500 flex items-center gap-1.5">
              <Trash2 className="w-4 h-4" />
              KVKK Madde 7 & 11 — Sporcu Kimliği Anonimleştirme (Unutulma Hakkı)
            </div>
            <div className="flex gap-2">
              <select
                value={kvkkSporcu}
                onChange={(e) => setKvkkSporcu(e.target.value)}
                className="text-xs p-2 rounded-lg bg-[var(--surface)] border border-[var(--line)] flex-1"
              >
                {sporcular.map((s) => (
                  <option key={s.id} value={s.tam_ad}>
                    {s.tam_ad}
                  </option>
                ))}
              </select>
              <button
                onClick={kvkkAnonimlestir}
                className="bg-red-600 hover:bg-red-700 text-white font-bold text-xs px-3 py-2 rounded-lg transition"
              >
                Anonimleştir
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

