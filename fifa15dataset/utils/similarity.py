import numpy as np
import pandas as pd
import streamlit as st
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from utils.data_loader import FEATURE_COLS, GK_STATS


@st.cache_data
def build_outfield_model(df_outfield: pd.DataFrame):
    X = df_outfield[FEATURE_COLS].fillna(0)
    pipeline = Pipeline([("scaler", StandardScaler())])
    X_scaled = pipeline.fit_transform(X)
    return X_scaled


@st.cache_data
def build_gk_model(df_gk: pd.DataFrame):
    available = [c for c in GK_STATS if c in df_gk.columns]
    X = df_gk[available].fillna(0)
    pipeline = Pipeline([("scaler", StandardScaler())])
    X_scaled = pipeline.fit_transform(X)
    return X_scaled


def find_similar_cosine(
    player_name: str,
    df: pd.DataFrame,
    X_scaled: np.ndarray,
    top_n: int = 10,
    position_filter: list | None = None,
) -> pd.DataFrame | None:
    matches = df[df["short_name"] == player_name]
    if matches.empty:
        return None

    idx = matches.index[0]
    player_vector = X_scaled[idx].reshape(1, -1)
    sims = cosine_similarity(player_vector, X_scaled)[0]

    result = df.copy()
    result["similarity_score"] = sims
    result["metric"] = "Cosine"

    mask = result.index != idx
    if position_filter:
        mask &= result["main_position"].isin(position_filter)

    return (
        result[mask]
        .nlargest(top_n, "similarity_score")
        [["short_name", "overall", "main_position", "club_name", "value_eur", "similarity_score", "metric"]]
        .reset_index(drop=True)
    )


def find_similar_euclidean(
    player_name: str,
    df: pd.DataFrame,
    X_scaled: np.ndarray,
    top_n: int = 10,
    position_filter: list | None = None,
) -> pd.DataFrame | None:
    matches = df[df["short_name"] == player_name]
    if matches.empty:
        return None

    idx = matches.index[0]
    player_vector = X_scaled[idx].reshape(1, -1)
    dists = euclidean_distances(player_vector, X_scaled)[0]

    max_dist = dists.max() if dists.max() > 0 else 1
    normalized = 1 - (dists / max_dist)

    result = df.copy()
    result["similarity_score"] = normalized
    result["metric"] = "Euclidean"

    mask = result.index != idx
    if position_filter:
        mask &= result["main_position"].isin(position_filter)

    return (
        result[mask]
        .nlargest(top_n, "similarity_score")
        [["short_name", "overall", "main_position", "club_name", "value_eur", "similarity_score", "metric"]]
        .reset_index(drop=True)
    )


def search_players(query: str, df: pd.DataFrame, limit: int = 20) -> list[str]:
    q = query.strip().lower()
    if not q:
        return df["short_name"].dropna().unique().tolist()
    mask = df["short_name"].str.lower().str.contains(q, na=False)
    return df[mask]["short_name"].dropna().unique().tolist()[:limit]
