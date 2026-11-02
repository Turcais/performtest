"""
Kayıt düzelt (Paket 38s): Sonuçlar sayfasının üstündeki "Kayıt düzelt" bölümü. Kayıtlı bir ölçümün değerini düzeltme,
başka sporcuya taşıma, silme (işaret; kalıcı değil) ve geri alma. Her işlem onay penceresinden geçer; yazmadan önce
yedek alınır, değişiklik kaydına yazılır. Hesap ve dosya işleri: olcut/duzeltme.py.
"""
import pandas as pd
import streamlit as st
from olcut.bilesenler import _gecerli_secim
from olcut.duzeltme import (
    DuzeltmeHatasi, degisiklik_kaydi_oku, duzeltme_onizleme, girilen_degiskenler, ham_tablo, kayit_duzelt,
    kayit_geri_al, kayit_sil, kayit_tasi, kilitli_oturum, oturum_satirlari, satir_kilitli, silindi_mi,
    tasima_onizleme)
from olcut.kayit import deger_metni, oturum_secenekleri
from olcut.katalog_islemleri import SILINDI_KOLON, silinmemis
from olcut.norm import SPORCU_DOSYA
from olcut.ortak import ad_bicimi, tablo_oku, veri_yolu

KD_OTURUMSUZ = "Oturumsuz kayıtlar (tekli giriş)"
KD_ISLEMLER = ("Değer düzelt", "Başka sporcuya taşı", "Sil", "Geri al")
KD_ACIKLAMA = ("Kalıcı silme yoktur: silinen kayıt hesaplara ve raporlara girmez, \"Geri al\" ile döner. "
               "Her işlemden önce kayıt dosyasının yedeği alınır; her değişiklik tarih, eski ve yeni değerle "
               "değişiklik kaydına yazılır.")


def _satir_no_metni(n):
    return f"satır {int(n) + 2}"            # Excel'deki satır (başlık + 1'den başlar); değişiklik kaydıyla aynı


def _kayit_etiketi(r, n):
    return f"{ad_bicimi(str(r['Sporcu']))} · {r['Test']} · {r['Tarih']} ({_satir_no_metni(n)})"


def _degisiklik_tablosu(degisiklikler):
    return pd.DataFrame([{"Alan": a, "Eski": deger_metni(e), "Yeni": deger_metni(y)} for a, e, y in degisiklikler])


def _bitti(mesaj):
    st.session_state["kd::mesaj"] = mesaj
    st.cache_data.clear()                   # Bugün kartı ve sonuç ekranları yeni dosyayı okusun
    st.rerun()


_ISLEM_FONK = {"duzelt": kayit_duzelt, "tasi": kayit_tasi, "sil": kayit_sil, "geri": kayit_geri_al}


def _bekleyen_ayarla(baslik, onizleme, tur, args, uyarilar=()):
    """Onay bekleyen işlem; pencere her çalıştırmada bundan çizilir (kapatılınca ya da Vazgeç'te silinir)."""
    st.session_state["kd::bekleyen"] = {"baslik": baslik, "tablo": onizleme, "tur": tur, "args": args,
                                        "uyarilar": list(uyarilar)}


def _bekleyeni_sil():
    st.session_state.pop("kd::bekleyen", None)


@st.dialog("İşlemi onaylayın", width="large", on_dismiss=_bekleyeni_sil)
def onay_penceresi():
    b = st.session_state.get("kd::bekleyen")
    if not b:
        return
    st.markdown(f"**{b['baslik']}**")
    if b["tablo"] is not None and not b["tablo"].empty:
        st.dataframe(b["tablo"], hide_index=True, width="stretch")
    for u in b["uyarilar"]:
        st.warning(u, icon=":material/warning:")
    if b["uyarilar"]:
        st.caption("Uyarı engel değildir; değer doğruysa onaylayabilirsiniz.")
    st.caption("Onaylayınca önce yedek alınır, sonra kayıt dosyası ve değişiklik kaydı yazılır.")
    c1, c2 = st.columns(2)
    if c1.button("Onayla", type="primary", icon=":material/check:", key="kd_onayla", width="stretch"):
        try:
            n = _ISLEM_FONK[b["tur"]](*b["args"])
        except DuzeltmeHatasi as h:
            st.error(str(h), icon=":material/error:")
            return
        _bekleyeni_sil()
        _bitti(f"✓ İşlem kaydedildi ({n} değişiklik, değişiklik kaydına yazıldı)." if n else "Değişen bir şey yok.")
    if c2.button("Vazgeç", key="kd_vazgec", width="stretch"):
        _bekleyeni_sil()
        st.rerun()


def _kayit_listesi(df, satirlar, son):
    """Önizleme listesi: sporcu, test, tarih ve son sütun ("Satır" = Excel satırı ya da silinme zamanı)."""
    t = df.loc[satirlar, ["Sporcu", "Test", "Tarih"]].copy()
    t["Sporcu"] = t["Sporcu"].astype(str).map(ad_bicimi)
    t[son] = [int(i) + 2 for i in satirlar] if son == "Satır" else df.loc[satirlar, son].astype(str).values
    return t


def _hata(h):
    st.error(str(h), icon=":material/error:")


def kayit_duzelt_sayfasi():
    st.subheader("Kayıt düzelt")
    st.caption(KD_ACIKLAMA)
    if st.session_state.get("kd::mesaj"):
        st.success(st.session_state.pop("kd::mesaj"))
    df = ham_tablo()
    if df.empty or "Sporcu" not in df.columns:
        st.info("Henüz kayıtlı ölçüm yok.")
        return
    kilit = kilitli_oturum()
    if kilit:
        st.info(f"Test Oturumu'nda açık taslak var: \"{kilit}\" oturumunun kayıtları taslak kaydedilene ya da "
                "silinene kadar düzenlenemez.", icon=":material/lock:")
    silinmis = df[df.apply(silindi_mi, axis=1)] if SILINDI_KOLON in df.columns else df.iloc[0:0]
    etkin = silinmemis(df)
    if kilit and "Oturum" in etkin.columns:
        etkin = etkin[etkin["Oturum"].astype(str).str.strip() != kilit]

    # ── Seçim: oturum → sporcu → kayıt ──
    ot_etiket = oturum_secenekleri(df.loc[[n for n in df.index if not satir_kilitli(df.loc[n], kilit or "")]])
    oturumsuz = ("Oturum" not in df.columns) or df["Oturum"].fillna("").astype(str).str.strip().isin(["", "nan"]).any()
    secenekler = list(ot_etiket) + ([KD_OTURUMSUZ] if oturumsuz else [])
    if not secenekler:
        st.info("Düzenlenebilir kayıt yok.")
        return
    _gecerli_secim("kd_oturum", secenekler)
    oturum = st.selectbox("Oturum", secenekler, key="kd_oturum",
                          format_func=lambda k: k if k == KD_OTURUMSUZ else ot_etiket[k])

    def oturumda(d):
        if "Oturum" not in d.columns:
            return d
        o = d["Oturum"].fillna("").astype(str).str.strip()
        return d[o.isin(["", "nan"])] if oturum == KD_OTURUMSUZ else d[o == str(oturum)]

    e_ot, s_ot = oturumda(etkin), oturumda(silinmis)
    sporcular = sorted(set(e_ot["Sporcu"].astype(str)) | set(s_ot["Sporcu"].astype(str)))
    _gecerli_secim("kd_sporcu", sporcular)
    sporcu = st.selectbox("Sporcu", sporcular, key="kd_sporcu", format_func=ad_bicimi)
    e_sp = e_ot[e_ot["Sporcu"].astype(str) == sporcu]
    s_sp = s_ot[s_ot["Sporcu"].astype(str) == sporcu]

    islem = st.segmented_control("İşlem", KD_ISLEMLER, key="kd_islem",
                                 **({} if "kd_islem" in st.session_state else {"default": KD_ISLEMLER[0]}))
    islem = islem or KD_ISLEMLER[0]

    if islem == "Geri al":
        _geri_al_bolumu(s_ot, s_sp, sporcu, oturum)
    elif e_sp.empty:
        st.info("Bu sporcunun bu oturumda etkin kaydı yok.")
    else:
        kayitlar = list(e_sp.index)
        _gecerli_secim("kd_kayit", kayitlar)
        n = st.selectbox("Kayıt", kayitlar, key="kd_kayit", format_func=lambda i: _kayit_etiketi(df.loc[i], i))
        r = df.loc[n]
        if islem == "Değer düzelt":
            _duzelt_bolumu(df, n, r)
        elif islem == "Başka sporcuya taşı":
            _tasi_bolumu(df, n, e_sp, sporcu)
        else:
            _sil_bolumu(df, n, e_ot, e_sp, sporcu, oturum)

    if st.session_state.get("kd::bekleyen"):
        onay_penceresi()
    with st.expander("Değişiklik kaydı", icon=":material/history:"):
        log = degisiklik_kaydi_oku()
        if log.empty:
            st.caption("Henüz değişiklik yok.")
        else:
            st.dataframe(log.iloc[::-1], hide_index=True, width="stretch")
            st.caption(f"Dosya: {veri_yolu('degisiklik_kaydi.xlsx')} · yedekler: {veri_yolu('yedekler')}")


def _duzelt_bolumu(df, n, r):
    girilen = girilen_degiskenler(r)
    if not girilen:
        st.info("Bu kayıtta düzeltilecek girilen değer yok.")
        return
    _gecerli_secim("kd_degisken", girilen)
    degisken = st.selectbox("Değer", girilen, key="kd_degisken",
                            format_func=lambda k: f"{k}: {deger_metni(r.get(k)) or '—'}")
    yeni = st.text_input("Yeni değer", key=f"kd_yeni::{n}::{degisken}", value=deger_metni(r.get(degisken)),
                         help="Ondalık için virgül ya da nokta. En iyi deneme, asimetri, indeks gibi hesaplanan "
                              "değerler ve test yaşı yeniden hesaplanır.")
    aciklama = st.text_input("Açıklama (isteğe bağlı)", key="kd_aciklama_duzelt",
                             placeholder="ör. kâğıttaki değer yanlış aktarılmış")
    if st.button("Önizle ve onayla", icon=":material/edit:", key="kd_duzelt"):
        try:
            o = duzeltme_onizleme(n, degisken, yeni, df)
        except DuzeltmeHatasi as h:
            _hata(h)
            return
        if not o["degisiklikler"]:
            st.info("Değer aynı; değişen bir şey yok.")
            return
        _bekleyen_ayarla(f"Düzeltme: {_kayit_etiketi(r, n)}", _degisiklik_tablosu(o["degisiklikler"]),
                         "duzelt", (n, degisken, yeni, aciklama), o["uyarilar"])


def _profildeki_sporcular():
    d = tablo_oku(veri_yolu(SPORCU_DOSYA))
    if d is None or d.empty:
        return []
    return sorted((d["Ad"].astype(str) + " " + d["Soyad"].astype(str)).tolist())


def _tasi_bolumu(df, n, e_sp, sporcu):
    kapsam = st.radio("Taşınacak", ["Bu kayıt", f"Bu sporcunun bu oturumdaki bütün kayıtları ({len(e_sp)})"],
                      key="kd_tasi_kapsam", horizontal=True)
    satirlar = [n] if kapsam == "Bu kayıt" else list(e_sp.index)
    hedefler = [s for s in _profildeki_sporcular() if s != sporcu]
    if not hedefler:
        st.info("Taşınacak başka sporcu yok.")
        return
    _gecerli_secim("kd_hedef", hedefler)
    hedef = st.selectbox("Doğru sporcu", hedefler, key="kd_hedef", format_func=ad_bicimi)
    aciklama = st.text_input("Açıklama (isteğe bağlı)", key="kd_aciklama_tasi")
    if st.button("Önizle ve onayla", icon=":material/move_item:", key="kd_tasi"):
        try:
            o = tasima_onizleme(satirlar, hedef, df)
        except DuzeltmeHatasi as h:
            _hata(h)
            return
        tablo = pd.DataFrame([{"Kayıt": f"{df.loc[i, 'Test']} · {df.loc[i, 'Tarih']}", "Alan": a,
                               "Eski": deger_metni(e), "Yeni": deger_metni(y)}
                              for i, v in o.items() for a, e, y in v["degisiklikler"]])
        uyarilar = [u for v in o.values() for u in v["uyarilar"]]
        _bekleyen_ayarla(f"{len(satirlar)} kayıt {ad_bicimi(sporcu)} → {ad_bicimi(hedef)}", tablo,
                         "tasi", (satirlar, hedef, aciklama), uyarilar)


def _sil_bolumu(df, n, e_ot, e_sp, sporcu, oturum):
    secenek = ["Bu kayıt", f"Bu sporcunun bu oturumdaki bütün kayıtları ({len(e_sp)})"]
    if oturum != KD_OTURUMSUZ:
        secenek.append(f"Bütün oturum ({e_ot['Sporcu'].nunique()} sporcu, {len(e_ot)} kayıt)")
    kapsam = st.radio("Silinecek", secenek, key="kd_sil_kapsam")
    satirlar = [n] if kapsam == secenek[0] else (list(e_sp.index) if kapsam == secenek[1] else list(e_ot.index))
    aciklama = st.text_input("Neden (isteğe bağlı)", key="kd_aciklama_sil", placeholder="ör. protokol dışı ölçüm")
    if st.button("Önizle ve onayla", icon=":material/delete:", key="kd_sil"):
        tablo = _kayit_listesi(df, satirlar, "Satır")
        _bekleyen_ayarla(f"{len(satirlar)} kayıt silinecek (geri alınabilir)", tablo, "sil", (satirlar, aciklama))


def _geri_al_bolumu(s_ot, s_sp, sporcu, oturum):
    if s_ot.empty:
        st.info("Bu oturumda silinmiş kayıt yok.")
        return
    secenek = []
    if not s_sp.empty:
        secenek.append(f"Bu sporcunun silinmiş kayıtları ({len(s_sp)})")
    secenek.append(f"Bu oturumdaki bütün silinmiş kayıtlar ({len(s_ot)})")
    kapsam = st.radio("Geri alınacak", secenek, key="kd_geri_kapsam")
    satirlar = list(s_sp.index) if (not s_sp.empty and kapsam == secenek[0]) else list(s_ot.index)
    tablo = _kayit_listesi(s_ot, satirlar, SILINDI_KOLON)
    st.dataframe(tablo, hide_index=True, width="stretch")
    if st.button("Geri al", icon=":material/undo:", key="kd_geri"):
        _bekleyen_ayarla(f"{len(satirlar)} kayıt geri alınacak", None, "geri", (satirlar,))
