"""
Sonuçlar — tek sporcu dört soru kartı (Paket 38b: Nasıl gelişiyor? · Yaşıtlarına göre nerede? · Güçlü ve geliştirilecek
yönler · Hangi branşa uygun?): süzgeçler, özet kutuları, gelişim, yaşıt kartı, nitelik çubukları ve ayrıntılı analiz geçişi.

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import os
import pandas as pd
import re
import streamlit as st
from datetime import date
from io import BytesIO
from olcut.analiz import (
    ESLESTIRME_AYIRT_ESIGI, fiziksel_pencere,
    GRUP_KONUM_YUZDELIK_N, VELI_ARALIK_YERI, VELI_DOGRU_MU_BASLIK, VELI_KONUM_EN_AZ_YAS, _konum_sayi, brans_grubu_eslestir,
    gelisim_ozeti, grup_ici_konum, rapor_konum_degiskenleri, sporcu_fsc_profili, sporcu_profil_bilgisi)
from olcut.bilesenler import _gecerli_secim, _git_rapor, _nitelik_kartina_git, grup_konum_penceresi
from olcut.katalog_islemleri import NITELIK_DIGER, NITELIK_KARTLARI, nitelik_karti, test_niteligi, test_tablosu_duzelt
from olcut.kayit import GRUP_KOLON, _sayi_kisa, oturum_secenekleri
from olcut.norm import SPORCU_DOSYA, TEST_DOSYA, sporcu_z_profili
from olcut.oneri import ozet_kartlari_html
from olcut.ortak import _girildi, _tarih_gunu, ad_bicimi, veri_yolu
from olcut.raporlar import (
    VELI_FIZIKSEL_AYIRT_EDILEMEZ,
    _aralik_sayi, _gelisim_grafik_svg, _veli_duzeyi, gelisim_bolumu_html, gelisim_metni, konum_seridi_veli_svg,
    test_degisken_etiketi, veli_aralik_konumu, veli_konum_uygun)
from olcut.tema import kategori_bilgisi, palet, renk_css


BRANS_EN_AZ_NITELIK = 5


SONUC_YASIT_METNI = "Aynı yaş bandı ve cinsiyetteki {n} sporcunun çoğu {a}–{b} {birim} arasında."


NITELIK_DURUM_ETIKETI = {"ust": ("✓", "güçlü"), "orta": ("≈", "orta"), "alt": ("!", "geliştir")}


NITELIK_NOTU = "Yön göstericidir, tanı değil."


def sonuc_kart_gorunumu():
    """Tek sporcu seçili ve 'Ayrıntılı analiz' kapalı → dört soru kartı."""
    s = st.session_state.get("sonuc_sporcu")
    return (os.path.exists(veri_yolu(TEST_DOSYA)) and s not in (None, "Tüm Sporcuları Göster")
            and not st.session_state.get("sonuc_ayrintili", False))


def sonuc_suzgecleri(df_test):
    """Oturum ve sporcu süzgeci (ayrıntılı görünümle aynı anahtarlar: sonuc_oturum, sonuc_sporcu)."""
    if "Oturum" in df_test.columns:
        _ot_deger = df_test["Oturum"].fillna("").astype(str).str.strip()
        df_oturumlu = df_test[(_ot_deger != "") & (_ot_deger != "nan")]
        if not df_oturumlu.empty:
            ot_etiket = oturum_secenekleri(df_oturumlu)                     # Paket 38d: ortak liste
            _gecerli_secim("sonuc_oturum", ["Tüm kayıtlar"] + list(ot_etiket))
            ot_secim = st.selectbox("Test oturumu", ["Tüm kayıtlar"] + list(ot_etiket),
                                    format_func=lambda k: k if k == "Tüm kayıtlar" else ot_etiket[k],
                                    key="sonuc_oturum")
            if ot_secim != "Tüm kayıtlar":
                df_test = df_test[df_test["Oturum"] == ot_secim]
    sporcular = ["Tüm Sporcuları Göster"] + sorted(df_test["Sporcu"].unique().tolist())
    _gecerli_secim("sonuc_sporcu", sporcular)
    return df_test, st.selectbox("Sporcu Filtrele", sporcular, key="sonuc_sporcu", format_func=ad_bicimi)


def notlu_olcum_sayisi(df):
    if "Notlar" not in df.columns:
        return 0
    n = df["Notlar"].fillna("").astype(str).str.strip()
    return int(((n != "") & (n != "nan")).sum())


def sporcu_ozet_kutulari(df_s, ozetler):
    """Dört özet kutusu: Test, Ölçüm, Gelişen test (son iki ölçüm iyi yönde), Not düşülen ölçüm."""
    gelisen = len({o["test"] for o in ozetler if o.get("iyi_yonde") is True})
    return [("Test", df_s["Test"].nunique()), ("Ölçüm", len(df_s)), ("Gelişen test", gelisen),
            ("Not düşülen ölçüm", notlu_olcum_sayisi(df_s))]


def varsayilan_gelisim_cifti(ozetler):
    """Kart 1'in ilk açılan testi: en çok ölçümü olan, eşitse son ölçümü en yeni olan."""
    def anahtar(o):
        t = _tarih_gunu(o["olcumler"][-1][0]) if o["olcumler"] else None
        return (len(o["olcumler"]), t or date.min)
    return max(range(len(ozetler)), key=lambda i: anahtar(ozetler[i])) if ozetler else None


def yon_oku(o):
    """Son iki ölçüm farkının oku: ▲ arttı, ▼ azaldı, = değişmedi (iyi/kötü sözle söylenir, renkle değil)."""
    if o.get("fark") is None:
        return ""
    return "▲" if o["fark"] > 0 else ("▼" if o["fark"] < 0 else "=")


def sonuc_karti_cumlesi(o):
    """Antrenör sonuç kartı (Paket 38c): "7 cm arttı — daha iyi" / "1 düşme arttı — daha kötü"; yön yoksa yalnız değişim."""
    m = gelisim_metni(o)
    return m.replace(" — bir önceki ölçümden düşük", " — daha kötü")


# Paket 38g: yaşıt kartını antrenör okur — veli metnindeki "antrenörle birlikte" yerine doğrudan çağrı.
SONUC_DOGRU_MU = "Bu sonuç aralıktan çok uzak; ölçüm ya da kayıt hatası olabilir. Ölçümü ve kaydı kontrol edin."


def yasit_karti_metni(k, ad):
    """Paket 38g: veli raporuyla aynı derece dili — biraz / belirgin şekilde / çok (+ "Değer doğru mu?")."""
    yer = veli_aralik_konumu(k)
    return (SONUC_YASIT_METNI.format(n=k["n"], a=_aralik_sayi(k["p10"], k["birim"]), b=_aralik_sayi(k["p90"], k["birim"]),
                                     birim=k["birim"]).replace("  ", " ")
            + " " + VELI_ARALIK_YERI[yer].format(ad=ad)
            + (f" {VELI_DOGRU_MU_BASLIK} {SONUC_DOGRU_MU}" if yer.endswith("_cok") else ""))


def yasit_yetersiz_nedeni(k):
    """Yaşıt kartı gösterilemiyorsa kısa neden (veli kartının koşulları)."""
    if k.get("durum") != "tamam":
        return f"Aynı yaş bandı ve cinsiyette yeterli ölçüm yok (n = {k.get('n', 0)})."
    if test_niteligi(k["test"]) == "antropometri":
        return "Vücut ölçülerinde yaşıt karşılaştırması gösterilmez."
    if k.get("yas") is None or k["yas"] < VELI_KONUM_EN_AZ_YAS:
        return f"{VELI_KONUM_EN_AZ_YAS} yaş altında yaşıt karşılaştırması gösterilmez."
    if k["n"] < GRUP_KONUM_YUZDELIK_N:
        return f"En az {GRUP_KONUM_YUZDELIK_N} sporcu gerekir; şu an n = {k['n']}."
    if k.get("yon") is None:
        return "Bu ölçünün iyi yönü tanımlı değil."
    return ""


def nitelik_durumlari(zp):
    """
    Nitelik başına normatif seviye (1-6) ortalaması: her testten en iyi değişkeni (veli özetindeki gibi), vücut
    ölçüleri ve niteliksiz testler dışarıda. Düzey _veli_duzeyi ile (yeni eşik yok).
    """
    gruplar = {}
    for r in (zp or {}).get("satirlar", []):
        if r.get("Tür") != "Performans" or not r.get("Kategori"):
            continue
        sev = kategori_bilgisi(r["Kategori"])["seviye"]
        kart = nitelik_karti(r["Test"])
        if sev is None or kart in (NITELIK_DIGER, "Vücut ölçüleri"):
            continue
        g = gruplar.setdefault(kart, {})
        g[r["Test"]] = max(g.get(r["Test"], 0), sev)
    sonuc = []
    for kart, _ in NITELIK_KARTLARI:
        if kart in gruplar:
            s = list(gruplar[kart].values())
            ort = sum(s) / len(s)
            sonuc.append({"nitelik": kart, "seviye": round(ort, 1), "test_sayisi": len(s), "durum": _veli_duzeyi(ort)})
    return sonuc


def nitelik_cubuklari_html(durumlar):
    """Yatay çubuklar; renge ek olarak simge ve kelime (✓ güçlü, ≈ orta, ! geliştir)."""
    p = ['<div class="sk-cubuklar">']
    for d in durumlar:
        isaret, kelime = NITELIK_DURUM_ETIKETI[d["durum"]]
        sev = max(1, min(6, round(d["seviye"])))
        k = kategori_bilgisi(next(a for a, s_, *_ in palet("acik")["norm"] if s_ == sev))
        renk = k["zemin"] if sev != 1 else k["yazi"]
        aciklama = f"{d['nitelik']}: {kelime} (ortalama seviye {_konum_sayi(d['seviye'])} / 6, {d['test_sayisi']} test)"
        p.append(f'<div class="sk-cubuk" role="img" aria-label="{_html.escape(aciklama)}" '
                 f'style="display:grid;grid-template-columns:minmax(110px,1fr) 2fr auto;gap:10px;align-items:center;'
                 f'margin:6px 0;font-size:14px"><span>{_html.escape(d["nitelik"])}</span>'
                 f'<span style="background:{renk_css("cizgi")};border-radius:6px;height:14px;display:block">'
                 f'<span style="display:block;height:14px;border-radius:6px;width:{d["seviye"] / 6 * 100:.0f}%;'
                 f'background:{renk}"></span></span><b>{isaret} {kelime}</b></div>')
    p.append("</div>")
    return "".join(p)


def excel_verisi(dataframe):
    """Sonuç tablosunu sütun genişlikleri ayarlı .xlsx olarak döner."""
    buffer = BytesIO()
    cols = [k for k in dataframe.columns if k != "Tarih_dt"]
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe[cols].to_excel(writer, index=False, sheet_name="Sonuçlar")
        ws = writer.sheets["Sonuçlar"]
        for i, kolon in enumerate(cols, start=1):
            uz = [len(str(x)) for x in dataframe[kolon].tolist()]
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = max(max(uz) if uz else 0, len(str(kolon))) + 4
    return buffer.getvalue()


def kart_hatasi(hata):
    """Bir kartın hatası öbürlerini durdurmaz: sade Türkçe uyarı, teknik iz 'Ayrıntı' açılırında."""
    import traceback as _tb
    st.warning("Bu kart şu an gösterilemiyor; öbür kartlar çalışmaya devam ediyor.", icon=":material/error:")
    with st.expander("Ayrıntı"):
        st.code("".join(_tb.format_exception(type(hata), hata, hata.__traceback__)), language=None)


@st.dialog("Tüm testlerin gelişimi", width="large")
def tum_gelisim_penceresi(sporcu, df_test):
    ozetler = [gelisim_ozeti(df_test, sporcu, t, d) for t, d in rapor_konum_degiskenleri(df_test, sporcu)]
    if not ozetler:
        st.info("Bu sporcunun sayısal sonucu yok.")
        return
    st.markdown(gelisim_bolumu_html(ozetler, {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}),
                unsafe_allow_html=True)


def sonuclar_sporcu_sayfasi():
    """Tek sporcu: sporcu kartı, dört özet kutusu, dört soru kartı, en altta kapalı 'Tüm kayıtlar'."""
    st.header("Test Sonuçları ve Analiz")
    df_tum = test_tablosu_duzelt(pd.read_excel(veri_yolu(TEST_DOSYA)))
    df_tum["Tarih_dt"] = pd.to_datetime(df_tum["Tarih"], format="%d.%m.%Y", errors="coerce")
    df_test, filtre = sonuc_suzgecleri(df_tum)
    if filtre == "Tüm Sporcuları Göster":           # seçim artık geçersiz: ayrıntılı görünüme dön
        st.rerun()
    st.toggle("Ayrıntılı analiz (7 sekme)", key="sonuc_ayrintili",
              help="Veri tablosu, trend, karşılaştırma, normatif konum, profil, Z-skor ve branşa yönlendirme sekmeleri.")
    df_s = df_test[df_test["Sporcu"] == filtre]
    renk = {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}
    kp = sporcu_profil_bilgisi(filtre)
    ad = ad_bicimi(str(kp.get("Ad", "") or "").strip() or filtre)
    ciftler = rapor_konum_degiskenleri(df_test, filtre)
    ozetler = [gelisim_ozeti(df_test, filtre, t, d) for t, d in ciftler]

    with st.container(border=True):                 # sporcu kartı
        son_t = df_s["Tarih_dt"].max()
        alanlar = [("Yaş", kp.get("Yaş")), ("Cinsiyet", kp.get("Cinsiyet")), ("Kilo", kp.get("Kilo (kg)")),
                   ("Grup", kp.get(GRUP_KOLON))]
        bilgi = " · ".join(f"{e}: {_sayi_kisa(v) if isinstance(v, float) else v}{' kg' if e == 'Kilo' else ''}"
                           for e, v in alanlar if _girildi(v))
        c1, c2, c3 = st.columns([2.4, 1.2, 1.4], vertical_alignment="center")
        c1.markdown(f"### {_html.escape(ad_bicimi(filtre))}\n{_html.escape(bilgi)}  \n{df_s['Test'].nunique()} test · "
                    f"{len(df_s)} kayıt · son ölçüm {son_t.strftime('%d.%m.%Y') if pd.notna(son_t) else '—'}")
        if c2.button("Grup içi konum", icon=":material/groups:", key="gk_ac", width="stretch"):
            grup_konum_penceresi(filtre, df_tum)
        c3.button("Veli raporu (PDF)", icon=":material/description:", key="sk_veli", width="stretch",
                  on_click=_git_rapor, args=(filtre,),
                  help="Raporlar sayfasında açılır; tarayıcıda Yazdır → PDF olarak kaydedin.")
    st.markdown(ozet_kartlari_html(sporcu_ozet_kutulari(df_s, ozetler)), unsafe_allow_html=True)

    secim = None
    if ciftler:
        anahtarlar = [f"{t} › {d}" for t, d in ciftler]
        _gecerli_secim("sk_test", anahtarlar)
        secim_k = st.selectbox("Kartlardaki test", anahtarlar, key="sk_test",
                               format_func=lambda k: test_degisken_etiketi(*k.split(" › ", 1)),
                               **({} if "sk_test" in st.session_state
                                  else {"index": varsayilan_gelisim_cifti(ozetler)}))
        secim = anahtarlar.index(secim_k)

    ust = st.columns(2)
    alt = st.columns(2)
    with ust[0].container(border=True):             # 1 · Nasıl gelişiyor?
        try:
            st.markdown("#### Nasıl gelişiyor?")
            if secim is None:
                st.info("Bu sporcunun sayısal sonucu yok.")
            else:
                o = ozetler[secim]
                t_son, v_son = o["olcumler"][-1]
                st.markdown(f"Son değer: **{_konum_sayi(v_son)}{(' ' + o['birim']) if o['birim'] else ''}** ({t_son})")
                if len(o["olcumler"]) >= 2:
                    st.markdown(f"**{yon_oku(o)} {_html.escape(sonuc_karti_cumlesi(o))}**")
                    st.markdown(_gelisim_grafik_svg(o, renk), unsafe_allow_html=True)
                else:
                    st.caption("İlk ölçüm; gelişim ikinci ölçümle görünür.")
            if ciftler:
                if st.button("Tüm testlerin gelişimi →", key="sk_tum_gelisim", type="tertiary"):
                    tum_gelisim_penceresi(filtre, df_test)
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with ust[1].container(border=True):             # 2 · Yaşıtlarına göre nerede?
        try:
            st.markdown("#### Yaşıtlarına göre nerede?")
            k = (grup_ici_konum(df_tum, pd.read_excel(veri_yolu(SPORCU_DOSYA)) if os.path.exists(veri_yolu(SPORCU_DOSYA)) else pd.DataFrame(),
                                filtre, *ciftler[secim]) if secim is not None else {"durum": "yetersiz", "n": 0})
            if veli_konum_uygun(k):
                st.markdown(yasit_karti_metni(k, ad))
                st.markdown(konum_seridi_veli_svg(k, renk), unsafe_allow_html=True)
                st.caption(f"Antrenör notu: yüzdelik ≈ P{k['yuzdelik']} · n = {k['n']}" if k.get("yuzdelik") is not None
                           else f"Antrenör notu: n = {k['n']}")
            else:
                st.markdown("**Karşılaştırma için yeterli veri yok.**")
                neden = yasit_yetersiz_nedeni(k)
                if neden:
                    st.caption(neden)
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with alt[0].container(border=True):             # 3 · Güçlü ve geliştirilecek yönler
        try:
            st.markdown("#### Güçlü ve geliştirilecek yönler")
            durumlar = nitelik_durumlari(sporcu_z_profili(df_test, filtre))
            if durumlar:
                st.markdown(nitelik_cubuklari_html(durumlar), unsafe_allow_html=True)
                st.caption(NITELIK_NOTU + " Çubuk: o nitelikteki testlerin normatif seviye ortalaması (1-6).")
            else:
                st.info("Normla karşılaştırılan performans testi yok.")
        except Exception as _kart_h:
            kart_hatasi(_kart_h)
    with alt[1].container(border=True):             # 4 · Hangi branşa uygun?
        try:
            st.markdown("#### Hangi branşa uygun?")
            kapsanan = sorted({nitelik_karti(t) for t in df_s["Test"].unique()} - {NITELIK_DIGER})
            if len(kapsanan) < BRANS_EN_AZ_NITELIK:
                st.markdown(f'<div style="border:2px dashed {renk_css("cizgi")};border-radius:10px;padding:12px 14px;'
                            f'font-size:14px">En az {BRANS_EN_AZ_NITELIK} farklı niteliği kapsayan test gerekir; '
                            f'şu an {len(kapsanan)} nitelik var.</div>', unsafe_allow_html=True)
                if st.toggle("Eksik testleri öner", key="sk_eksik"):
                    for kart in [k_ for k_, _ in NITELIK_KARTLARI if k_ not in kapsanan]:
                        st.button(f"{kart} testleri →", key=f"sk_eksik::{kart}", type="tertiary",
                                  on_click=_nitelik_kartina_git, args=(kart,))
            else:
                fsc = sporcu_fsc_profili(df_tum, filtre)
                esl = brans_grubu_eslestir(fsc, kp.get("Yaş"))
                if esl["uygun"] and esl.get("ayirt_edilemez"):           # Paket 38p: grup adı yok
                    st.markdown(VELI_FIZIKSEL_AYIRT_EDILEMEZ)
                    st.caption(f"Yayılım (en uzak − en yakın grup) {esl['yayilim']:.2f}".replace(".", ",")
                               + f", eşik {ESLESTIRME_AYIRT_ESIGI:.2f}".replace(".", ",") + ".")
                elif esl["uygun"]:
                    st.markdown("Fiziksel profili bu gruplara yakın (sıra yok): **"
                                + ", ".join(fiziksel_pencere(esl)) + "**")
                    st.caption("Bilgilendiricidir, eleyici değildir; ilgi ve antrenman süresiyle birlikte okunur.")
                else:
                    st.info(esl.get("neden") or "Branş eşleştirmesi yapılamadı.")
                st.button("Ayrıntı: Branşa Yönlendirme →", key="sk_brans", type="tertiary",
                          on_click=lambda: st.session_state.__setitem__("sonuc_ayrintili", True))
        except Exception as _kart_h:
            kart_hatasi(_kart_h)

    with st.expander("Tüm kayıtlar", icon=":material/table_rows:", expanded=False):
        _tum_kolon = [k_ for k_ in df_s.columns if k_ != "Tarih_dt"]
        st.dataframe(df_s[[k_ for k_ in _tum_kolon if k_ not in ("Kategori", "Batarya")]], width="stretch")
        dosya_adi = re.sub(r"[^\w]+", "_", filtre).strip("_") + "_sonuclar.xlsx"
        st.download_button("⬇️ Excel (.xlsx) İndir", excel_verisi(df_s), key="sk_excel", file_name=dosya_adi,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
