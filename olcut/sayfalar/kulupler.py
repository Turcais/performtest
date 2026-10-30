"""
Kulüpler sayfası (Paket 38n): kulüp listesi, yeni kulüp (kod otomatik; klasör ve boş dosyalar oluşur), bilgileri
düzenle, arşivle / arşivden çıkar (silmez), bu kulübe geç. Silme ve Genel veriyi kulübe taşıma bu pakette yok.
"""
from datetime import date
import pandas as pd
import streamlit as st
from olcut.bilesenler import KULUP_YENI_AC, calisma_alanina_gec
from olcut.kulup import (
    GENEL_ALAN, KULUP_ALANLARI, kulup_arsivle, kulup_kaydet, kulup_olustur, kulup_oku, kulupler)
from olcut.ortak import KULUP_KLASORU, aktif_kulup

KULUP_SAYFA_ACIKLAMA = ("Her kulübün sporcuları ve sonuçları ayrı klasörde durur (kulupler/<kod>/). Üstteki "
                        "\"Çalışma alanı\" seçicisi hangi kulüpte çalıştığınızı belirler; seçili kulübün dışındaki "
                        "hiçbir sporcu görünmez. \"Genel\", kulüpsüz bugünkü veridir.")


def _tarih(metin):
    try:
        return date.fromisoformat(str(metin)) if metin else None
    except ValueError:
        return None


def _bilgi_formu(onek, b=None):
    """Kulüp bilgileri (form içinde). Döner: bilgi sözlüğü."""
    b = b or {}
    ad = st.text_input(KULUP_ALANLARI["ad"][0] + " *", value=b.get("ad", ""), key=f"{onek}_ad")
    c1, c2 = st.columns(2)
    sehir = c1.text_input(KULUP_ALANLARI["sehir"][0], value=b.get("sehir", ""), key=f"{onek}_sehir")
    iletisim = c2.text_input(KULUP_ALANLARI["iletisim"][0], value=b.get("iletisim", ""), key=f"{onek}_iletisim")
    branslar = st.text_input(KULUP_ALANLARI["branslar"][0] + " (virgülle)", value=", ".join(b.get("branslar", [])),
                             key=f"{onek}_branslar")
    d1, d2 = st.columns(2)
    bas = d1.date_input(KULUP_ALANLARI["sozlesme_baslangic"][0], value=_tarih(b.get("sozlesme_baslangic")),
                        key=f"{onek}_bas", format="DD.MM.YYYY")
    bit = d2.date_input(KULUP_ALANLARI["sozlesme_bitis"][0], value=_tarih(b.get("sozlesme_bitis")),
                        key=f"{onek}_bit", format="DD.MM.YYYY")
    onay = st.checkbox(KULUP_ALANLARI["karsilastirma_onayi"][0], value=bool(b.get("karsilastirma_onayi", False)),
                       key=f"{onek}_onay",
                       help="Yalnız toplu değerler, kulüp adı olmadan (ileride, Paket 38o). Varsayılan kapalı.")
    return {"ad": ad.strip(), "sehir": sehir.strip(), "iletisim": iletisim.strip(),
            "branslar": [x.strip() for x in branslar.split(",") if x.strip()],
            "sozlesme_baslangic": bas.isoformat() if bas else "", "sozlesme_bitis": bit.isoformat() if bit else "",
            "karsilastirma_onayi": bool(onay)}


def _liste(tumu):
    if not tumu:
        st.info("Henüz kulüp yok. Aşağıdan \"Yeni kulüp\" ile açabilirsiniz; Genel veri olduğu gibi kalır.")
        return
    st.dataframe(pd.DataFrame([{"Kulüp": b["ad"], "Kod": k, "Şehir": b["sehir"], "Branşlar": ", ".join(b["branslar"]),
                                "Sözleşme": " – ".join(x for x in (b["sozlesme_baslangic"], b["sozlesme_bitis"]) if x),
                                "Durum": "Arşivde" if b["arsiv"] else "Etkin"} for k, b in tumu.items()]),
                 hide_index=True, width="stretch")


def kulupler_sayfasi():
    st.header("Kulüpler")
    st.caption(KULUP_SAYFA_ACIKLAMA)
    arsiv_goster = st.toggle("Arşivdekileri de göster", key="kl_arsiv_goster")
    tumu = kulupler(arsiv=True)
    _liste({k: b for k, b in tumu.items() if arsiv_goster or not b["arsiv"]})

    yeni_ac = st.session_state.pop(KULUP_YENI_AC, False)            # üstteki '+ Kulüp' ile gelindiyse açık
    with st.expander("Yeni kulüp", expanded=yeni_ac or not tumu, icon=":material/add:"):
        with st.form("kl_yeni", clear_on_submit=True):
            bilgi = _bilgi_formu("kl_yeni")
            if st.form_submit_button("Kulübü oluştur", type="primary"):
                if not bilgi["ad"]:
                    st.error("Kulüp adı gerekli.")
                else:
                    kod = kulup_olustur(bilgi)
                    st.success(f"✓ {bilgi['ad']} oluşturuldu ({KULUP_KLASORU}/{kod}/). Üstteki seçiciden geçebilirsiniz.")

    if not tumu:
        return
    st.subheader("Kulübü düzenle")
    kod = st.selectbox("Kulüp", list(tumu), key="kl_secili",
                       format_func=lambda k: tumu[k]["ad"] + (" (arşivde)" if tumu[k]["arsiv"] else ""))
    b = kulup_oku(kod)
    with st.form(f"kl_duzenle_{kod}"):
        yeni = _bilgi_formu(f"kl_d_{kod}", b)
        if st.form_submit_button("Bilgileri kaydet", type="primary"):
            if not yeni["ad"]:
                st.error("Kulüp adı gerekli.")
            else:
                kulup_kaydet(kod, {**b, **yeni})
                st.success("✓ Kaydedildi.")
    c1, c2 = st.columns(2)
    if not b["arsiv"]:
        if aktif_kulup() != kod:
            c1.button("Bu kulübe geç", key="kl_gec", on_click=calisma_alanina_gec, args=(kod,), width="stretch",
                      icon=":material/swap_horiz:")
        c2.button("Arşivle", key="kl_arsivle", on_click=_arsivle, args=(kod, True), width="stretch",
                  icon=":material/archive:", help="Listeden ve seçiciden gizler; hiçbir dosya silinmez.")
    else:
        c2.button("Arşivden çıkar", key="kl_arsivden", on_click=_arsivle, args=(kod, False), width="stretch",
                  icon=":material/unarchive:")
    if aktif_kulup() == kod:
        st.caption(f"Şu an bu kulüpte çalışıyorsunuz. Genel veriye dönmek için üstteki seçiciden \"{GENEL_ALAN}\".")


def _arsivle(kod, arsiv):
    kulup_arsivle(kod, arsiv)
    if arsiv and aktif_kulup() == kod:
        calisma_alanina_gec("")                       # arşivlenen kulüpte kalınmaz
