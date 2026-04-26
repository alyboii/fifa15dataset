import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_data
from utils.charts import position_bar_chart, age_overall_line, potential_histogram, COLORS

st.set_page_config(page_title="Home — FIFA 15", page_icon="🏠", layout="wide")
css = (Path(__file__).parent.parent / "assets" / "style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

df = load_data()

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">🏠 Ana Sayfa</h1>
    <p class="hero-subtitle">FIFA 15 Veri Seti Genel Bakış</p>
</div>
""", unsafe_allow_html=True)

# ── Metrik Kartları ──────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam Oyuncu", f"{len(df):,}")
c2.metric("Ülke", df["nationality_name"].nunique())
c3.metric("Lig", df["league_name"].nunique())
c4.metric("Kulüp", df["club_name"].nunique())

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Top 10 Oyuncu ────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🏆 Top 10 Oyuncu (Overall)</div>", unsafe_allow_html=True)

top10_cols = ["short_name", "overall", "potential", "main_position", "club_name",
              "nationality_name", "age", "value_eur"]
top10 = (
    df.nlargest(10, "overall")[top10_cols]
    .rename(columns={
        "short_name": "Oyuncu",
        "overall": "Overall",
        "potential": "Potansiyel",
        "main_position": "Pozisyon",
        "club_name": "Kulüp",
        "nationality_name": "Ülke",
        "age": "Yaş",
        "value_eur": "Değer (€)",
    })
)
top10["Değer (€)"] = top10["Değer (€)"].apply(
    lambda x: f"€{x/1_000_000:.1f}M" if pd.notna(x) and x > 0 else "—"
)

st.dataframe(
    top10,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Overall": st.column_config.ProgressColumn("Overall", min_value=0, max_value=100, format="%d"),
        "Potansiyel": st.column_config.ProgressColumn("Potansiyel", min_value=0, max_value=100, format="%d"),
    },
)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Grafikler ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<div class='section-header'>📊 Pozisyon Grubu Dağılımı</div>", unsafe_allow_html=True)
    st.plotly_chart(position_bar_chart(df), use_container_width=True)

with col_right:
    st.markdown("<div class='section-header'>📈 Yaşa Göre Ortalama Overall</div>", unsafe_allow_html=True)
    st.plotly_chart(age_overall_line(df), use_container_width=True)

st.markdown("<div class='section-header'>📉 Overall vs Potansiyel Dağılımı</div>", unsafe_allow_html=True)
st.plotly_chart(potential_histogram(df), use_container_width=True)

# ── Hızlı İstatistikler ──────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>📋 Hızlı İstatistikler</div>", unsafe_allow_html=True)

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Ort. Overall", f"{df['overall'].mean():.1f}")
s2.metric("Ort. Potansiyel", f"{df['potential'].mean():.1f}")
s3.metric("Ort. Yaş", f"{df['age'].mean():.1f}")
s4.metric("En Genç", f"{df['age'].min()} yaş")
s5.metric("En Yaşlı", f"{df['age'].max()} yaş")

# ── Genç Yetenkeler ──────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🌟 Genç Yıldızlar (≤21 yaş, Potansiyel ≥85)</div>", unsafe_allow_html=True)
wkids = (
    df[(df["age"] <= 21) & (df["potential"] >= 85)]
    [["short_name", "age", "overall", "potential", "growth", "main_position", "club_name"]]
    .sort_values("potential", ascending=False)
    .rename(columns={
        "short_name": "Oyuncu", "age": "Yaş", "overall": "Overall",
        "potential": "Potansiyel", "growth": "Gelişim",
        "main_position": "Pozisyon", "club_name": "Kulüp",
    })
)
st.dataframe(wkids, use_container_width=True, hide_index=True)
