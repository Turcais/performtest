"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar, SekmeTipi } from "@/components/layout/Sidebar";
import { SporcuAnaliz } from "@/components/features/SporcuAnaliz";
import { SahaOlcum } from "@/components/features/SahaOlcum";
import { Karsilastirma } from "@/components/features/Karsilastirma";
import { TestKatalogu } from "@/components/features/TestKatalogu";
import { AdminYonetim } from "@/components/features/AdminYonetim";
import { Vitrin } from "@/components/landing/Vitrin";
import { SporcuKaydi, SporcuAnalizYaniti } from "@/lib/api-client";

export default function PerformTestStudioPage() {
  const [oturumAcik, setOturumAcik] = useState<boolean>(false);
  const [mobilMenuAcik, setMobilMenuAcik] = useState<boolean>(false);
  const [aktifSekme, setAktifSekme] = useState<SekmeTipi>("analiz");
  const [aktifKulup, setAktifKulup] = useState<string>("merkez");
  const [kulupler, setKulupler] = useState<Array<{ kod: string; ad: string }>>([
    { kod: "merkez", ad: "PerformTest Merkez Lab" },
    { kod: "demo-kulup-a", ad: "Ankara Gençlik Spor Kulübü" },
    { kod: "demo-kulup-b", ad: "İstanbul Atletik SK" },
  ]);
  const [jwtToken, setJwtToken] = useState<string>("");
  const [kullaniciAdi, setKullaniciAdi] = useState<string>("PerformTest Sistem Yöneticisi");
  const [rol, setRol] = useState<string>("super_admin");

  const [sporcular, setSporcular] = useState<SporcuKaydi[]>([]);
  const [seciliSporcu, setSeciliSporcu] = useState<string>("");
  const [analiz, setAnaliz] = useState<SporcuAnalizYaniti | null>(null);
  const [analizYukleniyor, setAnalizYukleniyor] = useState<boolean>(false);

  // Dinamik Katalog Sayıları (Varsayılan 196 test, 191 kaynakça)
  const [toplamTest, setToplamTest] = useState<number>(196);
  const [toplamKaynakca, setToplamKaynakca] = useState<number>(191);

  const katalogOzetYukle = async () => {
    try {
      const r = await fetch("/api/v1/katalog/ozet");
      const d = await r.json();
      if (d && typeof d.toplam_test === "number") {
        setToplamTest(d.toplam_test);
        setToplamKaynakca(d.toplam_kaynakca ?? 191);
      }
    } catch {}
  };

  // SVG Sahne Modalı
  const [modalSvgTest, setModalSvgTest] = useState<string | null>(null);
  const [modalSvgHtml, setModalSvgHtml] = useState<string>("");

  // Yeni Sporcu Modalı
  const [yeniSporcuModal, setYeniSporcuModal] = useState<boolean>(false);
  const [yeniAd, setYeniAd] = useState("");
  const [yeniSoyad, setYeniSoyad] = useState("");
  const [yeniYas, setYeniYas] = useState(10);
  const [yeniCinsiyet, setYeniCinsiyet] = useState("Erkek");
  const [yeniBoy, setYeniBoy] = useState(142);
  const [yeniKilo, setYeniKilo] = useState(36);
  const [yeniBrans, setYeniBrans] = useState("Genel Atletik Performans");

  // Sayfa ilk yüklendiğinde kayıtlı oturum kontrolü (yoksa Vitrin sitesi görüntülenir)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const kayitliToken = localStorage.getItem("performtest_jwt");
      const kayitliKullanici = localStorage.getItem("performtest_user");
      if (kayitliToken && kayitliKullanici) {
        try {
          const u = JSON.parse(kayitliKullanici);
          setJwtToken(kayitliToken);
          setKullaniciAdi(u.ad_soyad || u.sub || "Kullanıcı");
          setRol(u.rol || u.role || "kullanici");
          if (u.kulup || u.club) setAktifKulup(u.kulup || u.club);
          setOturumAcik(true);
        } catch {
          localStorage.removeItem("performtest_jwt");
          localStorage.removeItem("performtest_user");
        }
      }
    }
  }, []);

  const girisYap = async (eposta: string, parola: string) => {
    try {
      const r = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ eposta, parola }),
      });
      const d = await r.json();
      if (d.access_token) {
        setJwtToken(d.access_token);
        setKullaniciAdi(d.kullanici.ad_soyad);
        setRol(d.kullanici.rol);
        if (d.kullanici.kulup) {
          setAktifKulup(d.kullanici.kulup);
        }
        setOturumAcik(true);
        if (typeof window !== "undefined") {
          localStorage.setItem("performtest_jwt", d.access_token);
          localStorage.setItem("performtest_user", JSON.stringify(d.kullanici));
        }
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const handleGirisBasarili = (token: string, kullanici: any) => {
    setJwtToken(token);
    setKullaniciAdi(kullanici.ad_soyad || kullanici.sub || "Kullanıcı");
    setRol(kullanici.rol || kullanici.role || "kullanici");
    if (kullanici.kulup || kullanici.club) {
      setAktifKulup(kullanici.kulup || kullanici.club);
    }
    setOturumAcik(true);
    if (typeof window !== "undefined") {
      localStorage.setItem("performtest_jwt", token);
      localStorage.setItem("performtest_user", JSON.stringify(kullanici));
    }
  };

  const handleDemoGiris = async (rolEposta?: string, parola?: string) => {
    const ep = rolEposta || "admin@performtest.yerli";
    const pw = parola || "PerformAdmin2026!";
    await girisYap(ep, pw);
  };

  const cikisYap = () => {
    setJwtToken("");
    setOturumAcik(false);
    setKullaniciAdi("");
    setRol("");
    if (typeof window !== "undefined") {
      localStorage.removeItem("performtest_jwt");
      localStorage.removeItem("performtest_user");
    }
  };

  const rolDegis = (epostaParola: string) => {
    const [ep, pw] = epostaParola.split("|");
    girisYap(ep, pw);
  };

  // Sporcuları yükle
  const sporculariYukle = async () => {
    try {
      const headers: Record<string, string> = {};
      if (jwtToken) {
        headers["Authorization"] = `Bearer ${jwtToken}`;
      }
      const r = await fetch(`/api/v1/sporcular?kulup_kodu=${encodeURIComponent(aktifKulup)}`, { headers });
      const d = await r.json();
      const liste = d.sporcular || [];
      setSporcular(liste);
      if (liste.length > 0 && (!seciliSporcu || !liste.some((s: any) => s.tam_ad === seciliSporcu))) {
        setSeciliSporcu(liste[0].tam_ad);
      }
    } catch {}
  };

  useEffect(() => {
    if (oturumAcik) {
      sporculariYukle();
      katalogOzetYukle();
    }
  }, [aktifKulup, oturumAcik, jwtToken]);

  // Seçili sporcu analizi yükle
  useEffect(() => {
    if (!seciliSporcu || !oturumAcik) return;
    setAnalizYukleniyor(true);
    const headers: Record<string, string> = {};
    if (jwtToken) {
      headers["Authorization"] = `Bearer ${jwtToken}`;
    }
    fetch(`/api/v1/sporcular/${encodeURIComponent(seciliSporcu)}/analiz?kulup_kodu=${encodeURIComponent(aktifKulup)}`, {
      headers,
    })
      .then((r) => r.json())
      .then((d) => setAnaliz(d))
      .catch(() => {})
      .finally(() => setAnalizYukleniyor(false));
  }, [seciliSporcu, aktifKulup, oturumAcik, jwtToken]);

  const svgProtokolAc = (testAdi: string) => {
    setModalSvgTest(testAdi);
    fetch(`/api/v1/katalog/svg?test_adi=${encodeURIComponent(testAdi)}`)
      .then((r) => r.json())
      .then((d) => setModalSvgHtml(d.svg_html || ""))
      .catch(() => {});
  };

  // Rol yetki sınırlarına göre aktif sekmeyi koru
  useEffect(() => {
    const isVeli = rol === "sporcu_veli" || rol === "veli";
    const isAntrenor = rol === "antrenor";
    if (isVeli && (aktifSekme === "admin" || aktifSekme === "oturum" || aktifSekme === "karsilastir")) {
      setAktifSekme("analiz");
    }
    if (isAntrenor && aktifSekme === "admin") {
      setAktifSekme("analiz");
    }
  }, [rol, aktifSekme]);

  const yeniSporcuKaydet = async () => {
    try {
      const r = await fetch("/api/v1/sporcular", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          kulup_kodu: aktifKulup,
          ad: yeniAd,
          soyad: yeniSoyad,
          yas: yeniYas,
          cinsiyet: yeniCinsiyet,
          boy_cm: yeniBoy,
          kilo_kg: yeniKilo,
          spor_dali: yeniBrans,
        }),
      });
      if (r.ok) {
        setYeniSporcuModal(false);
        setYeniAd("");
        setYeniSoyad("");
        sporculariYukle();
      }
    } catch {}
  };

  if (!oturumAcik) {
    return (
      <Vitrin
        onGirisBasarili={handleGirisBasarili}
        onDemoGiris={handleDemoGiris}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg)] text-[var(--text)] overflow-x-hidden">
      {/* Üst Bar */}
      <Navbar
        aktifKulup={aktifKulup}
        onKulupDegis={setAktifKulup}
        kulupler={kulupler}
        kullaniciAdi={kullaniciAdi}
        rol={rol}
        onRolDegis={rolDegis}
        onCikisYap={cikisYap}
        onMobilMenuAc={() => setMobilMenuAcik(true)}
      />

      {/* Ana Gövde */}
      <div className="flex-1 flex min-w-0">
        <Sidebar
          aktifSekme={aktifSekme}
          onSekmeSec={setAktifSekme}
          toplamSporcu={sporcular.length}
          toplamTest={toplamTest}
          toplamKaynakca={toplamKaynakca}
          rol={rol}
          mobilMenuAcik={mobilMenuAcik}
          onMobilMenuKapat={() => setMobilMenuAcik(false)}
          aktifKulup={aktifKulup}
          onKulupDegis={setAktifKulup}
          kulupler={kulupler}
        />

        <main className="flex-1 min-w-0 p-3 sm:p-4 lg:p-6 pb-24 lg:pb-6 overflow-x-hidden overflow-y-auto">
          {aktifSekme === "analiz" && (
            <SporcuAnaliz
              sporcular={sporcular}
              seciliSporcu={seciliSporcu}
              onSporcuSec={setSeciliSporcu}
              analiz={analiz}
              yukleniyor={analizYukleniyor}
              onYeniSporcuModal={() => setYeniSporcuModal(true)}
              onSvgProtokolAc={svgProtokolAc}
              aktifKulup={aktifKulup}
              rol={rol}
              jwtToken={jwtToken}
              onOlcumKaydedildi={sporculariYukle}
            />
          )}

          {aktifSekme === "oturum" && (
            <SahaOlcum
              sporcular={sporcular}
              aktifKulup={aktifKulup}
              jwtToken={jwtToken}
              rol={rol}
              onOlcumKaydedildi={sporculariYukle}
            />
          )}

          {aktifSekme === "karsilastir" && (
            <Karsilastirma sporcular={sporcular} aktifKulup={aktifKulup} rol={rol} />
          )}

          {aktifSekme === "katalog" && (
            <TestKatalogu
              rol={rol}
              jwtToken={jwtToken}
              toplamTest={toplamTest}
              toplamKaynakca={toplamKaynakca}
              onKatalogGuncellendi={katalogOzetYukle}
            />
          )}

          {aktifSekme === "admin" && (
            <AdminYonetim
              jwtToken={jwtToken}
              sporcular={sporcular}
              rol={rol}
              toplamTest={toplamTest}
              toplamKaynakca={toplamKaynakca}
              onVeriGuncellendi={() => {
                sporculariYukle();
                katalogOzetYukle();
              }}
            />
          )}
        </main>
      </div>

      {/* SVG Protokol Modalı */}
      {modalSvgTest && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setModalSvgTest(null)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 max-w-3xl w-full max-h-[85vh] overflow-y-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3 mb-4">
              <h3 className="font-extrabold text-base">{modalSvgTest} — Protokol Sahnesi</h3>
              <button
                onClick={() => setModalSvgTest(null)}
                className="text-xs font-bold px-2.5 py-1 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)]"
              >
                ✕ Kapat
              </button>
            </div>
            <div key={modalSvgTest} dangerouslySetInnerHTML={{ __html: modalSvgHtml }} />
          </div>
        </div>
      )}

      {/* Yeni Sporcu Kayıt Modalı */}
      {yeniSporcuModal && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setYeniSporcuModal(false)}
        >
          <div
            className="bg-[var(--surface)] border border-[var(--line)] rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[var(--line)] pb-3">
              <h3 className="font-extrabold text-sm">🏃 Yeni Sporcu & KVKK Açık Rıza</h3>
              <button
                onClick={() => setYeniSporcuModal(false)}
                className="text-xs font-bold px-2 py-0.5 rounded-lg border border-[var(--line)] hover:bg-[var(--surface-2)]"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Ad</label>
                <input
                  value={yeniAd}
                  onChange={(e) => setYeniAd(e.target.value)}
                  placeholder="Örn: Kerem"
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Soyad</label>
                <input
                  value={yeniSoyad}
                  onChange={(e) => setYeniSoyad(e.target.value)}
                  placeholder="Örn: Yılmaz"
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Yaş</label>
                <input
                  type="number"
                  step="0.5"
                  value={yeniYas}
                  onChange={(e) => setYeniYas(parseFloat(e.target.value))}
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Cinsiyet</label>
                <select
                  value={yeniCinsiyet}
                  onChange={(e) => setYeniCinsiyet(e.target.value)}
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                >
                  <option value="Erkek">Erkek</option>
                  <option value="Kadın">Kadın</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Boy (cm)</label>
                <input
                  type="number"
                  step="0.5"
                  value={yeniBoy}
                  onChange={(e) => setYeniBoy(parseFloat(e.target.value))}
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Kilo (kg)</label>
                <input
                  type="number"
                  step="0.5"
                  value={yeniKilo}
                  onChange={(e) => setYeniKilo(parseFloat(e.target.value))}
                  className="w-full p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] text-[var(--muted)] font-bold block mb-1">Spor Dalı / Branş</label>
              <input
                value={yeniBrans}
                onChange={(e) => setYeniBrans(e.target.value)}
                className="w-full text-xs p-2 rounded-lg bg-[var(--surface-2)] border border-[var(--line)] focus:outline-none"
              />
            </div>

            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-[11px] text-[var(--muted)] leading-relaxed">
              ☑️ <strong>6698 Sayılı KVKK Veli Açık Rıza Onayı:</strong> Antropometrik ve atletik performans verilerinin yerli sunucuda işlenmesine yönelik aydınlatma metni onaylanmıştır.
            </div>

            <button
              onClick={yeniSporcuKaydet}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2.5 rounded-xl shadow-md transition"
            >
              Sporcuyu Kaydet
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

