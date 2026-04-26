import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="FIFA 15 Player Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

css = (Path(__file__).parent / "assets" / "style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">⚽ FIFA 15 Player Intelligence</h1>
    <p class="hero-subtitle">
        16,155 oyuncu · Cosine & Euclidean Benzerlik · Makine Öğrenmesi Tabanlı Oyuncu Analizi
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🏠 Ana Sayfa** — Genel istatistikler ve top oyuncular")
with col2:
    st.info("**🔍 Oyuncu Arama** — ML ile benzer oyuncu bul")
with col3:
    st.info("**📊 EDA Paneli** — Keşifsel veri analizi")

st.markdown("""
<hr class="divider">
<p style="text-align:center; color:#94a3b8; font-size:0.85rem;">
    FIFA 15 dataset · SofIFA kaynaklı · Staj portfolyo projesi
</p>
""", unsafe_allow_html=True)
