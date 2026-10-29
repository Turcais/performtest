"""
Niteliğe göre test bul sayfası (Paket 38b).

Bölme Aşama 2: uygulama.py'den birebir taşındı (davranış değişmedi).
"""
import html as _html
import streamlit as st
from olcut.bilesenler import _git_test_uygula, _nitelik_testi_sec
from olcut.katalog_islemleri import NITELIK_DIGER, NITELIK_KARTLARI, ara_katla, nitelik_testleri, test_bilgisi
from olcut.kayit import TOPLU_GIRIS_DISI


def nitelik_sayfasi():
    st.header("Niteliğe göre test bul")
    st.caption("Ölçmek istediğiniz niteliği seçin; o niteliğin testleri listelenir. Bir testi seçince Test Oturumu "
               "sporcu seçimiyle (Adım 2) açılır.")
    kartlar = [k for k, _ in NITELIK_KARTLARI] + ([NITELIK_DIGER] if nitelik_testleri(NITELIK_DIGER) else [])
    secili = st.session_state.get("nt_kart")
    for bas in range(0, len(kartlar), 3):
        cols = st.columns(3)
        for i, (c, k) in enumerate(zip(cols, kartlar[bas:bas + 3])):
            with c.container(key=f"nt-kart-{bas + i}"):
                st.button(f"{'✓ ' if k == secili else ''}{k} · {len(nitelik_testleri(k))} test", key=f"nt::{k}",
                          width="stretch", on_click=lambda k_=k: st.session_state.__setitem__("nt_kart", k_))
    if not secili:
        return
    liste = nitelik_testleri(secili)
    st.markdown(f"#### {secili} — {len(liste)} test")
    if secili == "Kas dayanıklılığı":
        st.caption("Kuvvette devamlılık (ör. şınav, mekik, barfiks) ve anaerobik dayanıklılık (ör. Wingate, RSA) testleri.")
    elif secili == NITELIK_DIGER:
        st.caption("Tek bir niteliğe bağlanmayan testler: anketler, adım sayısı, çok bileşenli bataryalar, EMG.")
    ara = st.text_input("Bu kartta ara", key="nt_ara", placeholder="ör. Yo-Yo, 20m, Wingate")
    if ara.strip():
        liste = [t for t in liste if ara_katla(ara) in ara_katla(t["ad"])]
        st.caption(f"{len(liste)} test bulundu")
    for i, t in enumerate(liste):
        c1, c2 = st.columns([4, 1.3], vertical_alignment="center")
        c1.markdown(f"{_html.escape(t['ad'])}  \n<span style='font-size:0.875rem'>"
                    f"{_html.escape(' › '.join(p for p in t['yol'] if p))}</span>", unsafe_allow_html=True)
        toplu = t["ad"] not in TOPLU_GIRIS_DISI and (test_bilgisi(t["ad"]) or {}).get("degiskenler")
        if toplu:
            c2.button("Seç", key=f"nt::sec::{i}", width="stretch", on_click=_nitelik_testi_sec, args=(t["ad"],),
                      help="Test Oturumu'nda sporcu seçimine geç")
        else:
            c2.button("Test Uygula →", key=f"nt::uygula::{i}", width="stretch", on_click=_git_test_uygula,
                      args=(None, t["yol"], t["ad"]), help="Bu testin özel giriş ekranı var")
