"""
Ana sayfa: yönlendirme ekranı ('Ne yapmak istiyorsunuz?', Paket 16/33).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import streamlit as st
from olcut.bilesenler import _gecerli_secim, _git_test_uygula, _oneri_git, _sayfaya_git
from olcut.katalog_islemleri import katalog_testleri, test_ara, test_etiketli, test_tablosu_duzelt
from olcut.norm import SPORCU_DOSYA, TEST_DOSYA
from olcut.oneri import oneri_baglami, oneri_secenekleri, oneriler, yarim_sustur, yarim_susturulanlar
from olcut.ortak import ayar_oku, ayar_yaz, tablo_oku, veri_yolu


def _yonlendirme_gizle_degisti():
    ayar_yaz("yonlendirme_gizle", bool(st.session_state.get("yon_gizle")))


def yonlendirme_ekrani():
    """'Ne yapmak istiyorsunuz?' — durum dosyalardan okunur; her düğme ilgili sayfayı seçimleri dolu açar."""
    df_sp = tablo_oku(veri_yolu(SPORCU_DOSYA))
    df_ts = test_tablosu_duzelt(tablo_oku(veri_yolu(TEST_DOSYA)))
    b = oneri_baglami(df_sp, df_ts, susturulan=yarim_susturulanlar())
    st.markdown("#### Ne yapmak istiyorsunuz?")

    if not b["sporcular"]:
        # B) boş durum: tek düğmenin üstünde en fazla üç satır tanıtım; veri gelince görünmez
        st.markdown("Ölçüt, sporcunun test sonucunu yaşına ve cinsiyetine uygun normla karşılaştırır.  \n"
                    "**1.** Sporcu ekle → **2.** Test uygula → **3.** Sonucu gör, rapor al.")
        st.button("İlk sporcuyu ekle", icon=":material/person_add:", type="primary", width="stretch",
                  key="yon::ilk", on_click=_sayfaya_git, args=("Sporcu Girişi",))
    else:
        secenekler, varsayilan = oneri_secenekleri(b)
        _gecerli_secim("yon_secim", secenekler)
        secim = st.selectbox("Kim için?", secenekler, index=secenekler.index(varsayilan), key="yon_secim",
                             format_func=lambda s: ("Çalışma: " if s.startswith("calisma::") else "")
                             + s.partition("::")[2])
        liste = oneriler(b, secim)
        if liste:
            o = liste[0]
            with st.container(border=True):
                st.markdown(f"**{_html.escape(o['baslik'], quote=False)}**")
                st.caption(f"Neden: {o['gerekce']}")
                c1, c2 = st.columns([1, 1], vertical_alignment="center")
                c1.button("Devam et", icon=":material/arrow_forward:", type="primary", width="stretch",
                          key="yon::devam", on_click=_oneri_git, args=(o["eylem"],))
                if o["kural"] == 1:                                    # Paket 32: susturma yarım önerinin yanında
                    c2.button("Bu bataryayı bitirmeyeceğim", key="yon::sustur", icon=":material/do_not_disturb_on:",
                              width="stretch", on_click=yarim_sustur, args=(o["sporcu"], o["batarya"]),
                              help="Bu sporcu için bu batarya bir daha yarım sayılmaz (başka sporcuları etkilemez).")
            if len(liste) > 1:
                a = liste[1]
                st.button(f"Ya da: {a['baslik']}", key="yon::alternatif", type="tertiary",
                          on_click=_oneri_git, args=(a["eylem"],), help=f"Neden: {a['gerekce']}")
        else:
            st.markdown("**Önerecek bir şey yok.**")
        st.button("Başka bir test seç →", key="yon::baska", type="tertiary",
                  on_click=_git_test_uygula, args=(secim.partition("::")[2] if secim.startswith("sporcu::") else None,))
        # Paket 34 E: kapalıyken yalnız başlık; açılınca ad + kategori süzgeci, sonuçlar yol bilgisiyle ve "Uygula"
        with st.expander("Test ara", icon=":material/search:", expanded=False):
            tum = katalog_testleri()
            kategoriler = list(dict.fromkeys(t["kategori"] for t in tum))
            a1, a2 = st.columns([2, 1])
            sorgu = a1.text_input("Test adı", key="yon_ara",
                                  placeholder=f"{len(tum)} test arasında ad ya da nitelik ile ara (ör. Yo-Yo, sürat)")
            kat = a2.selectbox("Kategori", ["Tüm kategoriler"] + kategoriler, key="yon_ara_kat")
            kat = None if kat == "Tüm kategoriler" else kat
            ara_sporcu = secim.partition("::")[2] if secim.startswith("sporcu::") else None
            if sorgu.strip() or kat:
                bulunan = test_ara(sorgu, kat)
                st.caption(f"{len(bulunan)} test bulundu" + (" — ilk 12 gösteriliyor" if len(bulunan) > 12 else ""))
                for i, t in enumerate(bulunan[:12]):
                    c1, c2 = st.columns([3, 1], vertical_alignment="center")
                    c1.markdown(f"{_html.escape(test_etiketli(t['ad']))}  \n<span style='font-size:0.85em'>"
                                f"{_html.escape(' › '.join(p for p in t['yol'] if p))}</span>", unsafe_allow_html=True)
                    c2.button("Uygula", key=f"yon::ara::{i}", width="stretch",
                              on_click=_git_test_uygula, args=(ara_sporcu, t["yol"], t["ad"]))
    st.checkbox("Açılışta bu ekranı gösterme (menüden yine açılır)", key="yon_gizle",
                value=bool(ayar_oku().get("yonlendirme_gizle", False)), on_change=_yonlendirme_gizle_degisti)
