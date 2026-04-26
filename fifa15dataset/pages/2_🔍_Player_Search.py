import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_data, get_outfield_data, MAIN_STATS
from utils.similarity import build_outfield_model, find_similar_cosine, find_similar_euclidean
from utils.charts import radar_chart, similarity_comparison_bar, COLORS

st.set_page_config(page_title="Oyuncu Arama — FIFA 15", page_icon="🔍", layout="wide")
css = (Path(__file__).parent.parent / "assets" / "style.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

df_full = load_data()
df_out = get_outfield_data(df_full)
X_scaled = build_outfield_model(df_out)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">🔍 Oyuncu Benzerliği</h1>
    <p class="hero-subtitle">
        Cosine Similarity &amp; Euclidean Distance · sklearn Pipeline · StandardScaler
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Kontroller ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Arama Ayarları")
    top_n = st.slider("Gösterilecek Oyuncu Sayısı", 5, 20, 10)

    all_positions = sorted(df_out["main_position"].dropna().unique().tolist())
    position_filter = st.multiselect(
        "Pozisyon Filtresi (boş = hepsi)",
        options=all_positions,
        default=[],
    )

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
    <strong>Kullanılan Özellikler:</strong><br>
    pace · shooting · passing · dribbling · defending · physic · log(value)
    <br><br>
    <strong>Preprocessing:</strong><br>
    StandardScaler → mean=0, std=1
    </div>
    """, unsafe_allow_html=True)

# ── Oyuncu Seçimi ────────────────────────────────────────────────────────────
player_names = sorted(df_out["short_name"].dropna().unique().tolist())
selected = st.selectbox(
    "Oyuncu Seç",
    options=player_names,
    index=player_names.index("L. Messi") if "L. Messi" in player_names else 0,
)

if not selected:
    st.stop()

player_row = df_out[df_out["short_name"] == selected].iloc[0]
pos_filter = position_filter if position_filter else None

# ── Oyuncu Kartı ─────────────────────────────────────────────────────────────
face_url = player_row.get("player_face_url", "")
club = player_row.get("club_name", "—")
pos = player_row.get("main_position", "—")
pos_group = player_row.get("position_group", "—")
overall = int(player_row.get("overall", 0))
potential = int(player_row.get("potential", 0))
nation = player_row.get("nationality_name", "—")
age = int(player_row.get("age", 0))
value = player_row.get("value_eur", 0)
value_str = f"€{value/1_000_000:.1f}M" if pd.notna(value) and value > 0 else "—"

img_tag = f'<img src="{face_url}" onerror="this.style.display=\'none\'">' if face_url else ""

st.markdown(f"""
<div class="player-card">
    {img_tag}
    <div class="overall-badge">{overall}</div>
    <div class="player-card-info">
        <h2>{selected}</h2>
        <p>🏟️ {club} &nbsp;|&nbsp; 🌍 {nation} &nbsp;|&nbsp; 📌 {pos} ({pos_group})</p>
        <p>🎂 {age} yaş &nbsp;|&nbsp; 💰 {value_str} &nbsp;|&nbsp; 🎯 Potansiyel: <strong>{potential}</strong></p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Radar Chart ──────────────────────────────────────────────────────────────
col_radar, col_stats = st.columns([1, 1])

with col_radar:
    st.markdown("<div class='section-header'>🕸️ Stat Radar</div>", unsafe_allow_html=True)
    st.plotly_chart(radar_chart(player_row, selected), use_container_width=True)

with col_stats:
    st.markdown("<div class='section-header'>📊 Ana İstatistikler</div>", unsafe_allow_html=True)
    for stat in MAIN_STATS:
        val = int(player_row.get(stat, 0) or 0)
        label = stat.capitalize()
        color = COLORS["green"] if val >= 75 else (COLORS["gold"] if val >= 55 else "#ef4444")
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span style="color:#94a3b8; font-size:0.85rem;">{label}</span>
                <span style="color:{color}; font-weight:700;">{val}</span>
            </div>
            <div style="background:#1e293b; border-radius:4px; height:8px;">
                <div style="background:{color}; width:{val}%; height:100%; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Benzerlik Sonuçları ──────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🤝 Benzer Oyuncular</div>", unsafe_allow_html=True)

with st.spinner("Hesaplanıyor..."):
    cosine_res = find_similar_cosine(selected, df_out, X_scaled, top_n, pos_filter)
    euclidean_res = find_similar_euclidean(selected, df_out, X_scaled, top_n, pos_filter)

if cosine_res is None or euclidean_res is None:
    st.error("Oyuncu bulunamadı.")
    st.stop()

col_cos, col_euc = st.columns(2)

def render_results(res_df: pd.DataFrame, title: str, score_color: str):
    st.markdown(f"<div class='section-header' style='font-size:1rem;'>{title}</div>", unsafe_allow_html=True)
    for i, row in res_df.iterrows():
        score = row["similarity_score"]
        val = row["value_eur"]
        val_str = f"€{val/1_000_000:.1f}M" if pd.notna(val) and val > 0 else "—"
        st.markdown(f"""
        <div class="result-row">
            <div>
                <span style="font-weight:600; color:#fff;">{i+1}. {row['short_name']}</span>
                <span style="color:#94a3b8; font-size:0.82rem; margin-left:0.5rem;">
                    {row['main_position']} · {row['club_name']} · OVR {int(row['overall'])}
                </span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="color:#94a3b8; font-size:0.8rem;">{val_str}</span>
                <span class="similarity-badge" style="background:rgba({score_color},0.15); color:rgb({score_color});">
                    {score:.3f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_cos:
    render_results(cosine_res, "📐 Cosine Similarity", "0,212,160")

with col_euc:
    render_results(euclidean_res, "📏 Euclidean Distance (norm.)", "255,215,0")

# ── Karşılaştırma Grafiği ────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>⚖️ Metrik Karşılaştırması</div>", unsafe_allow_html=True)
st.plotly_chart(similarity_comparison_bar(cosine_res, euclidean_res, selected), use_container_width=True)

st.markdown("""
<div class="info-box">
<strong>Cosine Similarity</strong> → Oyun stilini ölçer (vektör yönü). Farklı değer/ücretteki
ama benzer oynayan oyuncuları bulur. Keşif transferlerinde idealdir.<br><br>
<strong>Euclidean Distance</strong> → Ham stat farkını ölçer (vektör uzaklığı). Aynı genel seviyedeki
oyuncuları öne çıkarır. İki metriğin farklı sonuç verdiği durumlar, istatistiksel anomali işaretidir.
</div>
""", unsafe_allow_html=True)
