import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_data, MAIN_STATS
from utils.charts import (
    overall_histogram, potential_histogram, value_wage_scatter,
    correlation_heatmap, top_leagues_bar, top_nations_bar, missing_values_bar,
    age_overall_line, COLORS,
)

st.set_page_config(page_title="EDA Paneli — FIFA 15", page_icon="📊", layout="wide")
css = (Path(__file__).parent.parent / "assets" / "style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

df = load_data()
df_out = df[df["position_group"] != "Goalkeeper"].copy()

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">📊 EDA Paneli</h1>
    <p class="hero-subtitle">Keşifsel Veri Analizi · 16,155 Oyuncu · 110 Kolon</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Navigasyon ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Bölüm Seç")
    section = st.radio(
        "",
        options=[
            "📈 Dağılımlar",
            "💰 Finansal Analiz",
            "🔗 Korelasyon Haritası",
            "🌍 Lig & Ülke Analizi",
            "❓ Eksik Veri",
        ],
        label_visibility="collapsed",
    )

# ════════════════════════════════════════════════════════════════════════════
if section == "📈 Dağılımlar":
    st.markdown("<div class='section-header'>📈 Rating Dağılımları</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(overall_histogram(df), use_container_width=True)
    with col2:
        st.plotly_chart(potential_histogram(df), use_container_width=True)

    st.plotly_chart(age_overall_line(df), use_container_width=True)

    st.markdown("<div class='section-header'>📊 Yaş Dağılımı</div>", unsafe_allow_html=True)
    import plotly.graph_objects as go
    age_counts = df["age"].value_counts().sort_index()
    fig_age = go.Figure(go.Bar(
        x=age_counts.index, y=age_counts.values,
        marker_color=COLORS["gold"], opacity=0.8,
    ))
    fig_age.update_layout(
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        xaxis=dict(title="Yaş", showgrid=False, color=COLORS["muted"]),
        yaxis=dict(title="Oyuncu Sayısı", gridcolor="#1e293b", color=COLORS["muted"]),
        margin=dict(l=20, r=20, t=40, b=20), height=320,
        title="Yaşa Göre Oyuncu Dağılımı",
    )
    st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("""
    <div class="info-box">
    <strong>Bulgu:</strong> Overall dağılımı 60-75 aralığında yoğunlaşmıştır (normal dağılıma yakın).
    Potansiyel eğrisi sağa kaymıştır — genç oyuncuların potansiyeli özellikle yüksektir.
    Zirve yaş <strong>~29</strong>'dur; bu noktadan sonra overall düşmeye başlar.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif section == "💰 Finansal Analiz":
    st.markdown("<div class='section-header'>💰 Değer ve Ücret Analizi</div>", unsafe_allow_html=True)
    st.plotly_chart(value_wage_scatter(df), use_container_width=True)

    st.markdown("<div class='section-header'>🏆 En Değerli 20 Oyuncu</div>", unsafe_allow_html=True)
    top_val = (
        df.dropna(subset=["value_eur"])
        .nlargest(20, "value_eur")
        [["short_name", "overall", "main_position", "club_name", "nationality_name", "age", "value_eur", "wage_eur"]]
        .rename(columns={
            "short_name": "Oyuncu", "overall": "Overall",
            "main_position": "Pozisyon", "club_name": "Kulüp",
            "nationality_name": "Ülke", "age": "Yaş",
            "value_eur": "Değer (€)", "wage_eur": "Ücret (€/hafta)",
        })
    )
    top_val["Değer (€)"] = top_val["Değer (€)"].apply(lambda x: f"€{x/1_000_000:.1f}M")
    top_val["Ücret (€/hafta)"] = top_val["Ücret (€/hafta)"].apply(
        lambda x: f"€{x:,.0f}" if pd.notna(x) else "—"
    )
    st.dataframe(top_val, use_container_width=True, hide_index=True)

    import plotly.graph_objects as go
    top20 = df.dropna(subset=["value_eur"]).nlargest(20, "value_eur")
    fig_v = go.Figure(go.Bar(
        x=top20["value_eur"] / 1_000_000,
        y=top20["short_name"],
        orientation="h",
        marker_color=COLORS["gold"],
        text=[f"€{v:.1f}M" for v in top20["value_eur"] / 1_000_000],
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig_v.update_layout(
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        title="En Değerli 20 Oyuncu",
        xaxis=dict(title="Değer (Milyon €)", showgrid=False, color=COLORS["muted"]),
        yaxis=dict(color=COLORS["text"], autorange="reversed"),
        margin=dict(l=20, r=20, t=40, b=20), height=520,
    )
    st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("""
    <div class="info-box">
    <strong>Bulgu:</strong> Değer ile ücret arasında güçlü pozitif korelasyon var (log ölçekte daha net).
    Forvetler ve orta saha oyuncuları en yüksek piyasa değerlerine sahip.
    Değer dağılımı sağa çarpık — <code>log(value)</code> dönüşümü ML modeli için kritikti.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif section == "🔗 Korelasyon Haritası":
    st.markdown("<div class='section-header'>🔗 Korelasyon Analizi</div>", unsafe_allow_html=True)

    stat_groups = {
        "Ana İstatistikler": MAIN_STATS,
        "Attacking": ["crossing", "finishing", "heading_accuracy", "short_passing", "volleys"],
        "Skill": ["dribbling", "curve", "fk_accuracy", "long_passing", "ball_control"],
        "Movement": ["acceleration", "sprint_speed", "agility", "reactions", "balance"],
        "Power": ["shot_power", "jumping", "stamina", "strength", "long_shots"],
        "Mentality": ["aggression", "interceptions", "positioning", "vision", "penalties"],
        "Defending": ["marking_awareness", "standing_tackle", "sliding_tackle"],
    }

    group_choice = st.selectbox("Stat Grubu", list(stat_groups.keys()))
    selected_cols = [c for c in stat_groups[group_choice] if c in df_out.columns]

    if len(selected_cols) < 2:
        st.warning("Bu grup için yeterli kolon bulunamadı.")
    else:
        st.plotly_chart(correlation_heatmap(df_out, selected_cols), use_container_width=True)

        corr = df_out[selected_cols].corr()
        max_pair = corr.where(~(corr == 1)).stack().idxmax()
        min_pair = corr.where(~(corr == 1)).stack().idxmin()
        st.markdown(f"""
        <div class="info-box">
        <strong>En yüksek korelasyon:</strong> {max_pair[0]} ↔ {max_pair[1]}
        ({corr.loc[max_pair[0], max_pair[1]]:.2f})<br>
        <strong>En düşük korelasyon:</strong> {min_pair[0]} ↔ {min_pair[1]}
        ({corr.loc[min_pair[0], min_pair[1]]:.2f})<br><br>
        Yüksek korelasyon (>0.8) → Bu iki özelliği birden modele koymak gürültü katar (multicollinearity).
        Ana istatistikler tercih edildi.
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif section == "🌍 Lig & Ülke Analizi":
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(top_leagues_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(top_nations_bar(df), use_container_width=True)

    st.markdown("<div class='section-header'>🌍 Ülke Bazında Oyuncu Sayısı (Top 15)</div>", unsafe_allow_html=True)
    import plotly.graph_objects as go
    nation_counts = df["nationality_name"].value_counts().head(15)
    fig_n = go.Figure(go.Bar(
        x=nation_counts.index,
        y=nation_counts.values,
        marker_color=COLORS["green"],
        text=nation_counts.values,
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig_n.update_layout(
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        title="En Fazla Oyuncuya Sahip Ülkeler",
        xaxis=dict(showgrid=False, color=COLORS["muted"], tickangle=-30),
        yaxis=dict(gridcolor="#1e293b", color=COLORS["muted"]),
        margin=dict(l=20, r=20, t=40, b=20), height=360,
    )
    st.plotly_chart(fig_n, use_container_width=True)

    st.markdown("""
    <div class="info-box">
    <strong>Bulgu:</strong> En yüksek ortalama overall'a sahip lig ve ülkeler beklenen sıralamayla örtüşüyor.
    İngiltere en fazla oyuncuya sahip (1,627); ancak İspanya ortalama overall'da üstte.
    Bu fark, İngiliz futbolunun daha geniş tabanlı ancak orta seviye ağırlıklı yapısını yansıtıyor.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif section == "❓ Eksik Veri":
    st.markdown("<div class='section-header'>❓ Eksik Veri Analizi</div>", unsafe_allow_html=True)
    st.plotly_chart(missing_values_bar(df), use_container_width=True)

    st.markdown("<div class='section-header'>📋 Eksik Veri Tablosu</div>", unsafe_allow_html=True)
    missing_df = (
        df.isnull()
        .sum()
        .to_frame("Eksik Sayı")
        .assign(**{"Eksik %": lambda x: (x["Eksik Sayı"] / len(df) * 100).round(1)})
        .query("`Eksik Sayı` > 0")
        .sort_values("Eksik Sayı", ascending=False)
        .reset_index()
        .rename(columns={"index": "Kolon"})
    )
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="info-box">
    <strong>%100 eksik kolonlar:</strong> <code>release_clause_eur</code>, <code>mentality_composure</code>
    → FIFA 15'te bu özellikler yoktu, sonraki versiyonlarda eklendi. Tamamen silindi.<br><br>
    <strong>~11% eksik (pace, shooting, vb.):</strong> Bunlar goalkeeper'lar — kalecilerin bu statsları
    kartlarında yer almaz. Çözüm: outfield ve GK için ayrı pipeline.<br><br>
    <strong>~2% eksik (value_eur, wage_eur):</strong> Genç/rezerv oyuncular için finansal veri yok.
    Benzerlik modelinde <code>log(value+1)</code> = 0 olarak işlendi.
    </div>
    """, unsafe_allow_html=True)
