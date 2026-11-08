/**
 * Ölçüt Mobil Uygulama — Saha Ölçümleri İçin Çevrimdışı (Offline-First) Senkronizasyon Servisi
 *
 * Spor salonu veya açık sahada internet bağlantısı kesildiğinde ölçümleri yerel kuyrukta tutar;
 * bağlantı sağlandığında `/api/v1/mobil/senkronize-et` uç noktasına toplu (batch) olarak gönderir.
 */

export interface SahaOlcumKaydi {
  gecici_id: string;
  sporcu_adi: string;
  test_adi: string;
  tarih: string;
  test_yasi?: number;
  oturum?: string;
  yer?: string;
  olcumler: Record<string, number | string>;
  senkronize_edildi: boolean;
}

export class MobilSahaSenkronServisi {
  private kuyruk: SahaOlcumKaydi[] = [];
  private apiTabanUrl: string;

  constructor(apiTabanUrl = "http://localhost:8000/api/v1") {
    this.apiTabanUrl = apiTabanUrl;
  }

  public olcumKuyrugaEkle(kayit: Omit<SahaOlcumKaydi, "senkronize_edildi">): void {
    this.kuyruk.push({ ...kayit, senkronize_edildi: false });
  }

  public bekleyenKayitlar(): SahaOlcumKaydi[] {
    return this.kuyruk.filter((k) => !k.senkronize_edildi);
  }

  public async sunucuIleSenkronizeEt(
    jwtToken: string,
    kulupKodu = "merkez",
    cihazId = "mobil-saha-tablet-01"
  ): Promise<{ islenen_kayit_sayisi: number; senkron_id: string }> {
    const bekleyenler = this.bekleyenKayitlar();
    if (bekleyenler.length === 0) {
      return { islenen_kayit_sayisi: 0, senkron_id: "" };
    }

    const yanit = await fetch(`${this.apiTabanUrl}/mobil/senkronize-et`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({
        cihaz_id: cihazId,
        kulup_kodu: kulupKodu,
        kayitlar: bekleyenler,
      }),
    });

    if (!yanit.ok) {
      throw new Error(`Mobil senkronizasyon başarısız: ${yanit.status}`);
    }

    const veri = await yanit.json();
    this.kuyruk = this.kuyruk.map((k) => ({ ...k, senkronize_edildi: true }));
    return veri;
  }
}
