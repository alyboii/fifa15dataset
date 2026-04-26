import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

COLORS = {
    "green": "#00d4a0",
    "gold": "#ffd700",
    "bg": "#0a0e1a",
    "card": "#111827",
    "text": "#ffffff",
    "muted": "#94a3b8",
    "forward": "#ef4444",
    "midfielder": "#3b82f6",
    "defender": "#22c55e",
    "goalkeeper": "#f59e0b",
}

POSITION_COLORS = {
    "Forward": COLORS["forward"],
    "Midfielder": COLORS["midfielder"],
    "Defender": COLORS["defender"],
    "Goalkeeper": COLORS["goalkeeper"],
}

_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def radar_chart(player_row: pd.Series, player_name: str) -> go.Figure:
    categories = ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physic"]
    cols = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
    values = [float(player_row.get(c, 0) or 0) for c in cols]
    values_closed = values + [values[0]]
    cats_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor=f"rgba(0,212,160,0.2)",
        line=dict(color=COLORS["green"], width=2),
        name=player_name,
    ))
    fig.update_layout(
        **_LAYOUT,
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 100], color=COLORS["muted"], gridcolor="#1e293b"),
            angularaxis=dict(color=COLORS["text"], gridcolor="#1e293b"),
        ),
        showlegend=False,
        height=350,
    )
    return fig


def position_bar_chart(df: pd.DataFrame) -> go.Figure:
    counts = (
        df["position_group"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "group", "position_group": "count"})
    )
    counts.columns = ["group", "count"]
    color_map = [POSITION_COLORS.get(g, COLORS["green"]) for g in counts["group"]]

    fig = go.Figure(go.Bar(
        x=counts["group"],
        y=counts["count"],
        marker_color=color_map,
        text=counts["count"],
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig.update_layout(
        **_LAYOUT,
        title="Player Count by Position Group",
        xaxis=dict(showgrid=False, color=COLORS["text"]),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", color=COLORS["muted"]),
        height=350,
    )
    return fig


def age_overall_line(df: pd.DataFrame) -> go.Figure:
    age_avg = df.groupby("age")["overall"].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=age_avg["age"],
        y=age_avg["overall"],
        mode="lines+markers",
        line=dict(color=COLORS["green"], width=2),
        marker=dict(color=COLORS["gold"], size=6),
        fill="tozeroy",
        fillcolor="rgba(0,212,160,0.08)",
    ))
    fig.add_vline(x=29, line_dash="dash", line_color=COLORS["gold"],
                  annotation_text="Peak Age ~29", annotation_font_color=COLORS["gold"])
    fig.update_layout(
        **_LAYOUT,
        title="Average Overall Rating by Age",
        xaxis=dict(title="Age", color=COLORS["muted"], showgrid=False),
        yaxis=dict(title="Avg Overall", color=COLORS["muted"], gridcolor="#1e293b"),
        height=350,
    )
    return fig


def overall_histogram(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["overall"],
        nbinsx=40,
        marker_color=COLORS["green"],
        opacity=0.8,
    ))
    fig.update_layout(
        **_LAYOUT,
        title="Overall Rating Distribution",
        xaxis=dict(title="Overall", color=COLORS["muted"], showgrid=False),
        yaxis=dict(title="Count", color=COLORS["muted"], gridcolor="#1e293b"),
        height=350,
    )
    return fig


def value_wage_scatter(df: pd.DataFrame) -> go.Figure:
    sample = df[df["value_eur"] > 0].dropna(subset=["value_eur", "wage_eur"]).sample(
        min(3000, len(df)), random_state=42
    )
    fig = px.scatter(
        sample,
        x="value_eur",
        y="wage_eur",
        color="position_group",
        color_discrete_map=POSITION_COLORS,
        hover_data=["short_name", "overall"],
        log_x=True,
        log_y=True,
        opacity=0.7,
    )
    fig.update_layout(
        **_LAYOUT,
        title="Market Value vs Wage (log scale)",
        xaxis=dict(title="Value (€)", color=COLORS["muted"], gridcolor="#1e293b"),
        yaxis=dict(title="Wage (€/week)", color=COLORS["muted"], gridcolor="#1e293b"),
        legend=dict(bgcolor=COLORS["card"]),
        height=400,
    )
    return fig


def correlation_heatmap(df: pd.DataFrame, cols: list) -> go.Figure:
    corr = df[cols].corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, "#1e3a5f"], [0.5, COLORS["card"]], [1, COLORS["green"]]],
        zmin=-1, zmax=1,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        **_LAYOUT,
        title="Correlation Matrix",
        height=450,
        xaxis=dict(color=COLORS["muted"]),
        yaxis=dict(color=COLORS["muted"]),
    )
    return fig


def top_leagues_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    league_avg = (
        df.groupby("league_name")["overall"]
        .agg(["mean", "count"])
        .query("count >= 50")
        .nlargest(n, "mean")
        .reset_index()
    )
    fig = go.Figure(go.Bar(
        x=league_avg["mean"].round(1),
        y=league_avg["league_name"],
        orientation="h",
        marker_color=COLORS["green"],
        text=league_avg["mean"].round(1),
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig.update_layout(
        **_LAYOUT,
        title=f"Top {n} Leagues by Average Overall",
        xaxis=dict(title="Avg Overall", color=COLORS["muted"], showgrid=False, range=[60, 80]),
        yaxis=dict(color=COLORS["text"], autorange="reversed"),
        height=400,
    )
    return fig


def top_nations_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    nation_avg = (
        df.groupby("nationality_name")["overall"]
        .agg(["mean", "count"])
        .query("count >= 30")
        .nlargest(n, "mean")
        .reset_index()
    )
    fig = go.Figure(go.Bar(
        x=nation_avg["mean"].round(1),
        y=nation_avg["nationality_name"],
        orientation="h",
        marker_color=COLORS["gold"],
        text=nation_avg["mean"].round(1),
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig.update_layout(
        **_LAYOUT,
        title=f"Top {n} Nations by Average Overall",
        xaxis=dict(title="Avg Overall", color=COLORS["muted"], showgrid=False, range=[60, 85]),
        yaxis=dict(color=COLORS["text"], autorange="reversed"),
        height=400,
    )
    return fig


def missing_values_bar(df: pd.DataFrame) -> go.Figure:
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(20)
    pct = (missing / len(df) * 100).round(1)

    fig = go.Figure(go.Bar(
        x=missing.index.tolist(),
        y=pct.values,
        marker_color=[COLORS["forward"] if p > 50 else COLORS["green"] for p in pct.values],
        text=[f"{p}%" for p in pct.values],
        textposition="outside",
        textfont=dict(color=COLORS["text"]),
    ))
    fig.update_layout(
        **_LAYOUT,
        title="Top 20 Columns with Missing Data (%)",
        xaxis=dict(color=COLORS["muted"], showgrid=False, tickangle=-45),
        yaxis=dict(title="Missing %", color=COLORS["muted"], gridcolor="#1e293b"),
        height=400,
    )
    return fig


def potential_histogram(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["overall"], nbinsx=40, name="Overall",
                               marker_color=COLORS["green"], opacity=0.7))
    fig.add_trace(go.Histogram(x=df["potential"], nbinsx=40, name="Potential",
                               marker_color=COLORS["gold"], opacity=0.7))
    fig.update_layout(
        **_LAYOUT,
        barmode="overlay",
        title="Overall vs Potential Distribution",
        xaxis=dict(title="Rating", color=COLORS["muted"], showgrid=False),
        yaxis=dict(title="Count", color=COLORS["muted"], gridcolor="#1e293b"),
        legend=dict(bgcolor=COLORS["card"]),
        height=350,
    )
    return fig


def similarity_comparison_bar(cosine_df: pd.DataFrame, euclidean_df: pd.DataFrame, player_name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Cosine",
        x=cosine_df["short_name"],
        y=cosine_df["similarity_score"],
        marker_color=COLORS["green"],
        opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        name="Euclidean (norm.)",
        x=euclidean_df["short_name"],
        y=euclidean_df["similarity_score"],
        marker_color=COLORS["gold"],
        opacity=0.85,
    ))
    fig.update_layout(
        **_LAYOUT,
        barmode="group",
        title=f"Similarity Score Comparison — {player_name}",
        xaxis=dict(tickangle=-30, color=COLORS["muted"], showgrid=False),
        yaxis=dict(title="Score", color=COLORS["muted"], gridcolor="#1e293b", range=[0, 1]),
        legend=dict(bgcolor=COLORS["card"]),
        height=350,
    )
    return fig
