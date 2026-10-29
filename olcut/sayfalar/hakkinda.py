"""
Hakkında sayfası (Paket 38k): Ölçüt nedir, misyon, vizyon, ilkeler, ekip, bilgilendirme, veri gizliliği, iletişim,
sürüm. Metinler veri/metinler.py'de sabit; burada yalnız dizilir.
"""
import streamlit as st
from veri.metinler import (
    HAKKINDA_BILGILENDIRME, HAKKINDA_BOLUMLERI, HAKKINDA_EKIP, HAKKINDA_GIZLILIK, HAKKINDA_ILETISIM, HAKKINDA_ILKELER,
    ILETISIM_EPOSTA)
from olcut.ortak import SURUM
from olcut.tema import UYGULAMA_ADI


def _madde_listesi(maddeler):
    return "\n".join(f"- {m}" for m in maddeler)


def hakkinda_sayfasi():
    st.header(f"{UYGULAMA_ADI} Hakkında")
    for baslik, metin in HAKKINDA_BOLUMLERI:
        st.subheader(baslik)
        st.markdown(metin)
    st.subheader("İlkelerimiz")
    st.markdown(_madde_listesi(HAKKINDA_ILKELER))
    st.subheader("Ekip")
    st.markdown("\n".join(f"- **{rol}:** {' · '.join(kisiler)}" for rol, kisiler in HAKKINDA_EKIP))
    st.subheader("Bilgilendirme")
    st.markdown(_madde_listesi(HAKKINDA_BILGILENDIRME))
    st.subheader("Veri gizliliği")
    st.markdown(HAKKINDA_GIZLILIK)
    st.subheader("İletişim")
    st.markdown(f"{HAKKINDA_ILETISIM} [{ILETISIM_EPOSTA}](mailto:{ILETISIM_EPOSTA})")
    st.subheader("Sürüm")
    st.markdown(SURUM)
