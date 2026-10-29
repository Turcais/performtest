"""
Ortak arayüz bileşenleri (Streamlit): çoklu seçim, terim açıklama düğmeleri, sayfa geçişleri (_git_*,
_sayfaya_git), birden çok sayfanın kullandığı parçalar (çalışma düzenleyici, sıra listesi, grup konum penceresi).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import os
import pandas as pd
import re
import streamlit as st
from datetime import date
from veri.metinler import ACIKLAMALAR, ILGI_KAYNAKLARI, ILGI_MADDELERI, TERIM_ARAMA
from olcut.analiz import (
    ILGI_ANKET_ADI, ILGI_DOSYA, ILGI_HAKKINDA, ILGI_OLCEK, ILGI_TERCIHLERI, ILGI_UYARI, _profil_haritasi,
    gelisim_ozeti, grup_ici_konum, ilgi_son_anket, konum_metinleri, konum_seridi_svg, rapor_konum_degiskenleri)
from olcut.katalog_islemleri import (
    ONERI_IZ_SINIRI, kanonik_test, sira_uyarilari, test_ara, test_etiketli, test_izi_parcalari)
from olcut.kayit import calisma_bos, calisma_kaydet, calisma_sil, calismalar_oku
from olcut.norm import SPORCU_DOSYA
from olcut.oneri import _virgullu, konum_sekme_sirasi, sira_birlestir
from olcut.ortak import _desteklenen
from olcut.raporlar import gelisim_bolumu_html
from olcut.tema import renk_css


def coklu_secim(etiket, secenekler, *, tumunu_sec=False, **k):
    """
    st.multiselect, Türkçe (Paket 38a): yer tutucu "Seçiniz"; Streamlit'in İngilizce "Select all" seçeneği kapalı,
    gerekiyorsa üstte "Tümünü seç" düğmesi (key verilmişse).
    """
    secenekler = list(secenekler)
    if tumunu_sec and k.get("key") and secenekler:
        st.button("Tümünü seç", type="tertiary", key=f"tumu::{k['key']}",
                  on_click=lambda: st.session_state.__setitem__(k["key"], list(secenekler)))
    return st.multiselect(etiket, secenekler, **{**_desteklenen(st.multiselect, placeholder="Seçiniz",
                                                                 select_all=False), **k})


def ilgi_anketi_formu(sporcu):
    """İlgi anketi formu (Sporcu Girişi akışında). Kaydedilen ya da en son kayıt döner."""
    ilgi_kayit = ilgi_son_anket(sporcu)
    with st.expander("ℹ️ Bu anket hakkında"):
        st.markdown(ILGI_HAKKINDA)
        st.caption("Madde havuzunun kaynakları:")
        for k_kod, k_metin in ILGI_KAYNAKLARI.items():
            st.caption(f"[{k_kod}] {k_metin}")
    if ilgi_kayit:
        st.caption(f"Son anket: {ilgi_kayit.get('Tarih', '')} — yeni yanıtlar yeni kayıt olarak eklenir; "
                   "raporlar en son kaydı kullanır.")
    st.warning("⚠️ " + ILGI_UYARI)
    st.caption("Çocuk soruları kendisi yanıtlar; okuyamıyorsa yetişkin soruyu okur ama yanıtı "
               "yönlendirmez. Bir etkinliği hiç yapmadıysa \"Bilmiyorum / hiç yapmadım\" seçilir.")
    with st.form(key=f"ilgi_form_{sporcu}"):
        ilgi_tarih = st.date_input("Anket tarihi", value=date.today(), key=f"ilgi_tarih_{sporcu}")
        yeni = {}
        st.markdown("**Bunu yapmayı ne kadar seversin?**")
        # Maddeler gruplara göre değil, karışık sırayla sorulur (grup etkisini azaltmak için)
        tum_maddeler = [m for grup_m in ILGI_MADDELERI.values() for m in grup_m]
        sira_m = [tum_maddeler[(i * 7) % len(tum_maddeler)] for i in range(len(tum_maddeler))]
        for kod, metin, _ in sira_m:
            onceki = ilgi_kayit.get(kod) if ilgi_kayit else None
            try:
                onceki = int(float(onceki))
            except (TypeError, ValueError):
                onceki = 0
            secenekler = [1, 2, 3, 4, 5, 0]
            yeni[kod] = st.radio(metin, secenekler,
                                 index=secenekler.index(onceki) if onceki in secenekler else 5,
                                 format_func=lambda x: ILGI_OLCEK[x], horizontal=True,
                                 key=f"{kod}_{sporcu}")
        st.markdown("**Hangisini daha çok seversin?** (yalnızca bilgi için, puana girmez)")
        for kod, a_secenek, b_secenek in ILGI_TERCIHLERI:
            tercih_ops = [a_secenek, "İkisi de / fark etmez", b_secenek]
            onceki_t = ilgi_kayit.get(kod) if ilgi_kayit else None
            yeni[kod] = st.radio(f"{a_secenek} mi, {b_secenek.lower()} mı?", tercih_ops,
                                 index=tercih_ops.index(onceki_t) if onceki_t in tercih_ops else 1,
                                 horizontal=True, key=f"{kod}_{sporcu}")
        if st.form_submit_button("💾 Anketi kaydet"):
            kayit_i = {"Sporcu": sporcu, "Tarih": ilgi_tarih.strftime("%d.%m.%Y"),
                       "Anket": ILGI_ANKET_ADI, **yeni}
            if os.path.exists(ILGI_DOSYA):
                df_i_tum = pd.concat([pd.read_excel(ILGI_DOSYA), pd.DataFrame([kayit_i])], ignore_index=True)
            else:
                df_i_tum = pd.DataFrame([kayit_i])
            df_i_tum.to_excel(ILGI_DOSYA, index=False)
            st.success("✅ İlgi anketi kaydedildi.")
            ilgi_kayit = kayit_i
    return ilgi_kayit


def terimleri_bul(*metinler):
    """Metinlerde geçen terimler (ACIKLAMALAR'daki adlarıyla, tekrarsız)."""
    birlesik = " ".join(str(m) for m in metinler if m)
    return [t for t, kalip in TERIM_ARAMA.items() if re.search(kalip, birlesik)]


def terim_metni(terimler):
    return "\n\n".join(f"**{t}:** {ACIKLAMALAR[t]}" for t in terimler)


def ac_dugmesi(terimler, etiket="ⓘ Bu bölümdeki terimler"):
    """
    Tıklanınca açılan kısa açıklama (telefonda da çalışır). st.popover yoksa st.expander.
    Tek kaynak: ACIKLAMALAR. Bilinmeyen terim KeyError verir (otomatik denetim yakalar).
    """
    terimler = [terimler] if isinstance(terimler, str) else list(dict.fromkeys(terimler))
    if not terimler:
        return
    metin = terim_metni(terimler)
    if hasattr(st, "popover"):
        with st.popover(etiket):
            st.markdown(metin)
    else:
        with st.expander(etiket):
            st.markdown(metin)


def bolum_terimleri(terimler):
    """Bölüm başına TEK düğme: 'ⓘ Bu bölümdeki terimler' (her yerde tıklama; telefonda hover yok)."""
    ac_dugmesi(terimler, "ⓘ Bu ne demek?")                       # Paket 38a: tek dokunuş, sade dil


def _hover_metni(terimler):
    terimler = [terimler] if isinstance(terimler, str) else list(terimler)
    return "\n\n".join(f"{t}: {ACIKLAMALAR[t]}" for t in terimler)


def baslik_ac(metin, terimler, seviye="subheader"):
    """
    Başlık; masaüstünde fareyle üzerine gelince aynı açıklama (title). Düğme koymaz —
    tıklanabilir açıklama bölümün 'ⓘ Bu bölümdeki terimler' düğmesindedir.
    seviye: 'header' (##), 'subheader' (###) ya da markdown önekleri ('####', '######').
    """
    st.markdown(baslik_html(metin, terimler, seviye), unsafe_allow_html=True)


def baslik_html(metin, terimler, seviye="subheader"):
    """
    baslik_ac'ın ürettiği markdown. title içinde satır sonu OLMAMALI: boş satır markdown'da
    paragraf açar ve <span> yarıda kalır (Paket 11'de bulunan hata: birden çok terimli başlıkta
    açıklama metni ham HTML olarak başlık yerine basılıyordu). Satır sonları &#10; olarak yazılır.
    """
    onek = {"header": "##", "subheader": "###"}.get(seviye, seviye)
    baslik = _html.escape(_hover_metni(terimler), quote=True).replace("\n", "&#10;")
    return (f'{onek} <span title="{baslik}" style="text-decoration: underline dotted; '
            f'text-decoration-thickness: 1px; text-underline-offset: 5px; cursor: help;">'
            f'{_html.escape(metin)}</span>')


def sutun_yardimi(sutun_terim):
    """st.dataframe column_config: sütun başlığına (masaüstünde üzerine gelince) aynı açıklama."""
    try:
        return {s: st.column_config.Column(help=ACIKLAMALAR[t]) for s, t in sutun_terim.items()}
    except AttributeError:
        return None


# ── Paket 27: sıralı test listesi (↑ ↓) ve çalışma düzenleyici ──
def _sira_tasi(anahtar, i, yon):
    """Sıralı listede i. testi bir yukarı (yon=-1) ya da aşağı (yon=+1) taşır (düğme geri çağrısı)."""
    s = list(st.session_state.get(anahtar, []))
    j = i + yon
    if 0 <= i < len(s) and 0 <= j < len(s):
        s[i], s[j] = s[j], s[i]
        st.session_state[anahtar] = s


def _sira_cikar(t, kaynaklar):
    """Testi sıralı listeye getiren seçimlerden çıkarır (arama eklemesi, ağaç seçimi; takma adlı raf adı dahil)."""
    for k in kaynaklar:
        if isinstance(st.session_state.get(k), list):
            st.session_state[k] = [x for x in st.session_state[k] if kanonik_test(x) != t]


def _sira_listesi(onek, secilenler, kaynaklar=()):
    """
    Seçilen testleri sıralı gösterir (adın yanında ölçtüğü nitelik); ↑ ↓ ile sıra değişir, ✕ testi çıkarır
    (kaynaklar: testi getiren seçimlerin anahtarları). Sıralı listeyi döner.
    """
    anahtar = f"{onek}::sira"
    sira = sira_birlestir(st.session_state.get(anahtar, []), list(secilenler))
    st.session_state[anahtar] = sira
    for i, t in enumerate(sira):
        c1, c2, c3, c4 = st.columns([10, 1, 1, 1])
        yol_, diger_ = test_izi_parcalari(t)                       # iz çubuğu (Paket 33)
        c1.markdown(f"{i + 1}. {_html.escape(test_etiketli(t))}  \n<span style='font-size:0.8em;opacity:0.75'>"
                    f"📍 {_html.escape(yol_)}" + (f" — ayrıca: {_html.escape(', '.join(diger_[:ONERI_IZ_SINIRI]))}"
                                                 + (f" ve {len(diger_) - ONERI_IZ_SINIRI} rafta daha"
                                                    if len(diger_) > ONERI_IZ_SINIRI else "") if diger_ else "")
                    + "</span>", unsafe_allow_html=True)
        c2.button("↑", key=f"{anahtar}::yukari::{i}", disabled=i == 0, on_click=_sira_tasi, args=(anahtar, i, -1),
                  help="Yukarı taşı")
        c3.button("↓", key=f"{anahtar}::asagi::{i}", disabled=i == len(sira) - 1, on_click=_sira_tasi,
                  args=(anahtar, i, 1), help="Aşağı taşı")
        c4.button("✕", key=f"{anahtar}::cikar::{i}", on_click=_sira_cikar, args=(t, tuple(kaynaklar)),
                  disabled=not kaynaklar, help="Listeden çıkar")
    return list(st.session_state[anahtar])


def _ot_ekle(ad):
    """Arama panelinden "Ekle": test sıralı listeye düşer (kategori ağacındaki seçim değişmez)."""
    ek = list(st.session_state.get("ot::ek", []))
    if kanonik_test(ad) not in ek:
        ek.append(kanonik_test(ad))
    st.session_state["ot::ek"] = ek


def _calisma_duzenleyici(sporcu_adlari):
    """Çalışma kur / düzenle: ad, sıralı testler (aranabilir, kategoriden bağımsız), gruplar, ölçüm zamanları, atama."""
    calismalar = calismalar_oku()
    yeni_etiket = "➕ Yeni çalışma"
    secim = st.selectbox("Çalışma", [yeni_etiket] + list(calismalar), key="cl_secim")
    c = calismalar.get(secim, calisma_bos())
    k = f"cl::{secim}"
    ad = st.text_input("Çalışmanın adı", value=c["ad"], key=f"{k}::ad", placeholder="ör. NHE Tez Çalışması")
    ara = st.text_input("Test ara (kategoriden bağımsız)", key=f"{k}::ara", placeholder="ör. sürat, çeviklik, Nordic")
    bulunan = [t["ad"] for t in test_ara(ara)] if ara.strip() else []
    secenek = list(dict.fromkeys(c["testler"] + st.session_state.get(f"{k}::testler", []) + bulunan))
    secili = coklu_secim("Testler", secenek, default=c["testler"], key=f"{k}::testler", format_func=test_etiketli,
                            help="Arama kutusuna yazın, sonuçlardan seçin; sıra aşağıda düzenlenir.")
    sira = _sira_listesi(k, secili, (f"{k}::testler",)) if secili else []
    g1, g2 = st.columns(2)
    gruplar = _virgullu(g1.text_input("Gruplar (virgülle)", value=", ".join(c["gruplar"]), key=f"{k}::gruplar",
                                      placeholder="ör. Kontrol, Deney"))
    zamanlar = _virgullu(g2.text_input("Ölçüm zamanları (virgülle)", value=", ".join(c["zamanlar"]),
                                       key=f"{k}::zamanlar", placeholder="ör. Ön test, Ara test, Son test"))
    atama = {}
    if gruplar and sporcu_adlari:
        tablo = pd.DataFrame({"Sporcu": list(sporcu_adlari),
                              "Grup": [c["atamalar"].get(s, "") if c["atamalar"].get(s, "") in gruplar else ""
                                       for s in sporcu_adlari]})
        duz = st.data_editor(tablo, hide_index=True, num_rows="fixed", width="stretch",
                             key=f"{k}::atama::{'|'.join(gruplar)}",
                             column_config={"Sporcu": st.column_config.TextColumn("Sporcu", disabled=True),
                                            "Grup": st.column_config.SelectboxColumn("Grup", options=[""] + gruplar)})
        atama = {r["Sporcu"]: r["Grup"] for _, r in duz.iterrows() if isinstance(r["Grup"], str) and r["Grup"]}
    yeni = {"ad": ad.strip(), "testler": sira, "gruplar": gruplar, "zamanlar": zamanlar, "atamalar": atama}
    for u in sira_uyarilari(sira):                                  # bildirir, engellemez
        st.warning(f"Sıra uyarısı: {u}", icon=":material/info:")
    b1, b2 = st.columns(2)
    if b1.button("💾 Çalışmayı kaydet", type="primary", key=f"{k}::kaydet"):
        sorun = calisma_kaydet(yeni, eski_ad=secim if secim in calismalar else None)
        if sorun:
            st.error("Kaydedilmedi:\n\n" + "\n".join(f"- {s}" for s in sorun))
        else:
            st.success(f"✅ '{yeni['ad']}' kaydedildi ({len(sira)} test, {len(zamanlar)} ölçüm zamanı). "
                       "Test Oturumu'nda 'Çalışma' seçeneğiyle kullanılabilir.")
    if secim in calismalar and b2.button("🗑 Çalışmayı sil", key=f"{k}::sil"):
        calisma_sil(secim)
        st.success(f"'{secim}' silindi. Kayıtlı test sonuçları etkilenmez.")


# ── düğme geri çağrıları: hedef sayfanın seçim kutularını önceden doldurur ──
def _git_test_uygula(sporcu=None, yol=None, test=None):
    st.session_state["sayfa"] = "Test Uygula"
    if sporcu:
        st.session_state["tu_sporcu"] = sporcu
    if yol and test:
        kat, alt, brans = yol
        st.session_state["tu_mod"] = "📂 Kategoriye Göre"
        st.session_state["tu_kategori"] = kat
        if alt is not None:
            st.session_state[f"tu_alt::{kat}"] = alt
        if brans is not None:
            st.session_state[f"tu_brans::{kat}::{alt}"] = brans
        st.session_state[f"tu_test::{kat}::{alt}::{brans}"] = test


def _git_oturum(kategori, batarya, testler=None, sporcu=None, grup=None, brans=None):
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ot_adim"] = 1                         # Paket 38b: önerilen seçimler Adım 1'de görünür
    st.session_state["ot_kaynak"] = "Serbest seçim"
    st.session_state["ot_kategori"] = kategori
    st.session_state["ot_batarya"] = batarya
    if brans is not None:
        st.session_state["ot_brans"] = brans
    if testler:
        for k_ in [k_ for k_ in st.session_state if str(k_).startswith("ot_testler_")] + ["ot::ek", "ot::sira"]:
            st.session_state.pop(k_, None)                      # yalnız önerilen testler (Paket 33)
        st.session_state[f"ot_testler_{kategori}_{batarya}_{brans}"] = list(testler)
    if sporcu:
        st.session_state["ot_gruplar"] = [grup or "(Grubu girilmemiş)"]
        st.session_state[f"ot_sporcular_{grup or '(Grubu girilmemiş)'}"] = [sporcu]


def _git_calisma(calisma, zaman, sporcu=None, grup=""):
    """Test Oturumu: çalışma + ölçüm zamanı + (varsa) sporcu seçili açılır."""
    st.session_state["sayfa"] = "Test Oturumu"
    st.session_state["ot_adim"] = 1
    st.session_state["ot_kaynak"] = "Çalışma"
    st.session_state["ot_calisma"] = calisma
    st.session_state[f"ot_zaman::{calisma}"] = zaman
    if sporcu and grup:
        st.session_state[f"ot_c_gruplar::{calisma}"] = [grup]
        st.session_state[f"ot_c_sporcular::{calisma}::{grup}"] = [sporcu]


def _oneri_git(eylem):
    """[Devam et]: önerinin eylemi ilgili sayfayı seçimleri dolu açar."""
    e = dict(eylem)
    tur = e.pop("tur")
    if tur == "calisma":
        _git_calisma(e["calisma"], e["zaman"], e.get("sporcu"), e.get("grup", ""))
    elif tur == "oturum":
        _git_oturum(e["kategori"], e["batarya"], e.get("testler"), e.get("sporcu"), e.get("grup", ""), e.get("brans"))
    elif tur == "test_uygula":
        _git_test_uygula(e.get("sporcu"), e.get("yol"), e.get("test"))


def _git_sonuclar(sporcu):
    st.session_state["sayfa"] = "Sonuçları Görüntüle"
    st.session_state["sonuc_oturum"] = "Tüm kayıtlar"
    st.session_state["sonuc_sporcu"] = sporcu
    st.session_state["sonuc_bolum"] = SONUC_BOLUMLERI[0]           # Paket 38g: sporcunun sonuçları açılır


# Paket 38g: Sonuçlar sayfasının üst düzey bölümü — karşılaştırma "Ayrıntılı analiz" arkasında gizli kalmasın.
SONUC_BOLUMLERI = ("Sonuçlar", "Karşılaştırma")


def sonuc_bolumu_secici():
    """Sonuçlar sayfasının üstünde segment: Sonuçlar / Karşılaştırma. Seçim kaldırılırsa Sonuçlar."""
    sec = st.segmented_control("Bölüm", SONUC_BOLUMLERI, key="sonuc_bolum", label_visibility="collapsed",
                               **({} if "sonuc_bolum" in st.session_state else {"default": SONUC_BOLUMLERI[0]}))
    return sec or SONUC_BOLUMLERI[0]


def _karsilastirmaya_git():
    st.session_state["sonuc_bolum"] = SONUC_BOLUMLERI[1]


@st.dialog("Grup içi konum ve gelişim", width="large")
def grup_konum_penceresi(sporcu, df_test):
    """Sporcu kartından açılır: test + değişken seçilir; kendi değişimi ve aynı yaş bandı/cinsiyetteki konumu."""
    df_sp = pd.read_excel(SPORCU_DOSYA) if os.path.exists(SPORCU_DOSYA) else pd.DataFrame()
    ciftler = rapor_konum_degiskenleri(df_test, sporcu)
    if not ciftler:
        st.info("Bu sporcunun sayısal test sonucu yok.")
        return
    secim = st.selectbox("Test ve değişken", ciftler, format_func=lambda c: f"{c[0]} — {c[1]}", key="gk_secim")
    test, degisken = secim
    yas = _profil_haritasi(df_sp).get(sporcu, {}).get("Yaş")
    sekmeler = konum_sekme_sirasi(yas)
    gorunum = dict(zip(sekmeler, st.tabs(sekmeler)))
    with gorunum["Kendi değişimin"]:
        o = gelisim_ozeti(df_test, sporcu, test, degisken)
        # Paket 38a: raporlarla aynı kart (gerçek değerli, eksen terslenmez); tek ölçümde ilk ölçüm tablosu
        st.markdown(gelisim_bolumu_html([o], {a: renk_css(a) for a in ("ana", "ikincil", "cizgi", "murekkep")}),
                    unsafe_allow_html=True)
    with gorunum["Grup içi konum"]:
        k = grup_ici_konum(df_test, df_sp, sporcu, test, degisken)
        for m in konum_metinleri(k):
            st.markdown(m)
        if k.get("durum") == "tamam":
            st.markdown(konum_seridi_svg(k), unsafe_allow_html=True)
            st.caption("Büyük nokta: bu sporcu · çizgi: grup ortalaması · küçük noktalar: havuzdaki öbür ölçümler "
                       "(isimsiz).")


def sekme_hatasi(hata):
    """Bir sekmenin hatası öbürlerini durdurmaz: sade Türkçe uyarı, teknik iz 'Ayrıntı' açılırında."""
    import traceback as _tb
    st.warning("Bu bölüm şu an gösterilemiyor; öbür sekmeler çalışmaya devam ediyor.", icon=":material/error:")
    with st.expander("Ayrıntı"):
        st.code("".join(_tb.format_exception(type(hata), hata, hata.__traceback__)), language=None)


def _git_rapor(sporcu):
    st.session_state["sayfa"] = "Raporlar"
    st.session_state["rapor_sporcu"] = sporcu


def _gecerli_secim(anahtar, secenekler):
    """Önceden doldurulmuş seçim artık seçeneklerde yoksa bırakılır (kutu varsayılana döner, hata vermez)."""
    if anahtar in st.session_state and st.session_state[anahtar] not in list(secenekler):
        del st.session_state[anahtar]


def _nitelik_testi_sec(ad):
    """Test seçildi → Test Oturumu Adım 2 (sporcular); sıralı listede yalnız bu test."""
    for k_ in [k for k in st.session_state if str(k).startswith("ot_testler_")] + ["ot::ek", "ot::sira"]:
        st.session_state.pop(k_, None)
    st.session_state["ot_kaynak"] = "Serbest seçim"
    st.session_state["ot::ek"] = [kanonik_test(ad)]
    st.session_state["ot::sira"] = [kanonik_test(ad)]
    st.session_state["ots::testler"] = [kanonik_test(ad)]
    st.session_state["ots::calisma"] = {"ad": None, "zaman": None}
    st.session_state["ot_adim"] = 2
    st.session_state["sayfa"] = "Test Oturumu"


def _nitelik_kartina_git(kart):
    st.session_state["nt_kart"] = kart
    st.session_state["sayfa"] = "Niteliğe göre test bul"


def _sayfaya_git(hedef):
    st.session_state["sayfa"] = hedef
