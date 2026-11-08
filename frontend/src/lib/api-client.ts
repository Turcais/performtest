/**
 * PerformTest Web Frontend & Admin Paneli — Merkezi Tipli REST API İstemcisi
 *
 * Yerli sunucuda çalışan `api/` (`http://localhost:8000/api/v1`) katmanı ile
 * JWT (`Bearer`) tabanlı iletişim kurar.
 */

export const API_TABAN_URL =
  process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export type KullaniciRolu =
  | "super_admin"
  | "kulup_yoneticisi"
  | "antrenor"
  | "sporcu_veli";

export interface GirisYaniti {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  kullanici: {
    id: string;
    eposta: string;
    ad_soyad: string;
    rol: KullaniciRolu;
    kulup_kodu: string;
    yetkiler: string[];
  };
}

export interface SporcuKaydi {
  id: string;
  kulup_kodu: string;
  ad: string;
  soyad: string;
  tam_ad: string;
  yas: number | null;
  cinsiyet: string;
  spor_dali: string;
  boy_cm: number | null;
  kilo_kg: number | null;
  olcum_sayisi: number;
}

export interface BransEslestirme {
  ayirt_edilemez: boolean;
  pencere: string[];
  siralama: Array<[string, number]>;
  katki?: Record<string, Record<string, number>>;
  neden?: string | null;
  uygun?: boolean;
  yayilim?: number;
}

export interface SporcuAnalizYaniti {
  sporcu: string;
  kulup_kodu: string;
  profil: Record<string, unknown>;
  z_profili: {
    hata: string | null;
    satirlar: Array<Record<string, unknown>>;
  };
  bilesik_z: Record<string, unknown>;
  fiziksel_pencere: string[] | null;
  brans_eslestirme?: BransEslestirme;
  kayitli_testler: Array<{ Test: string; "Ölçüm sayısı": number; "Son ölçüm": string }>;
  radar_svg: string;
  rapor_tarihi: string;
}

export interface AdminOzetYaniti {
  metrikler: {
    aktif_kulup_sayisi: number;
    aktif_kullanici_sayisi: number;
    toplam_sporcu: number;
    toplam_olcum_satiri: number;
    toplam_ilgi_anketi: number;
    toplam_denetim_kaydi: number;
  };
  yerli_sunucu: {
    veritabani_motoru: string;
    veritabani_dosyasi: string;
    boyut_bayt: number;
    kvkk_uyum_modu: string;
  };
  kulup_dagilimi: Array<{
    kod: string;
    ad: string;
    sehir: string;
    sporcu_sayisi: number;
    olcum_sayisi: number;
  }>;
}

export async function apiIstegi<T>(
  yol: string,
  secenekler: RequestInit = {},
  token?: string
): Promise<T> {
  const basliklar: Record<string, string> = {
    "Content-Type": "application/json",
    ...((secenekler.headers as Record<string, string>) || {}),
  };
  if (token) {
    basliklar["Authorization"] = `Bearer ${token}`;
  }
  const yanit = await fetch(`${API_TABAN_URL}${yol}`, {
    ...secenekler,
    headers: basliklar,
  });
  if (!yanit.ok) {
    throw new Error(`API Hatası (${yanit.status}): ${yol}`);
  }
  return yanit.json() as Promise<T>;
}

export const PerformTestApi = {
  girisYap: (eposta: string, parola: string) =>
    apiIstegi<GirisYaniti>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ eposta, parola }),
    }),

  sporculariListele: (kulupKodu = "merkez") =>
    apiIstegi<{ kulup_kodu: string; toplam: number; sporcular: SporcuKaydi[] }>(
      `/sporcular?kulup_kodu=${encodeURIComponent(kulupKodu)}`
    ),

  sporcuAnaliziGetir: (sporcuAdi: string, kulupKodu = "merkez") =>
    apiIstegi<SporcuAnalizYaniti>(
      `/sporcular/${encodeURIComponent(sporcuAdi)}/analiz?kulup_kodu=${encodeURIComponent(kulupKodu)}`
    ),

  sporculariKarsilastir: (sporcuA: string, sporcuB: string, kulupKodu = "merkez") =>
    apiIstegi<Record<string, unknown>>(
      `/karsilastir?kulup_kodu=${encodeURIComponent(kulupKodu)}&sporcu_a=${encodeURIComponent(sporcuA)}&sporcu_b=${encodeURIComponent(sporcuB)}`
    ),

  adminOzetiGetir: (token: string) =>
    apiIstegi<AdminOzetYaniti>("/admin/ozet", {}, token),

  veritabaniYedekle: (token: string) =>
    apiIstegi<{ dosya: string; boyut_bayt: number; zaman: string }>(
      "/admin/yedekle",
      { method: "POST" },
      token
    ),
};
