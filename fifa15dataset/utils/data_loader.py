import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "players_15.csv"

MAIN_STATS = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
FEATURE_COLS = MAIN_STATS + ["log_value"]

GK_STATS = [
    "goalkeeping_diving", "goalkeeping_handling", "goalkeeping_kicking",
    "goalkeeping_positioning", "goalkeeping_reflexes", "goalkeeping_speed",
]

FORWARDS = ["ST", "CF", "LW", "RW", "LF", "RF"]
MIDFIELDERS = ["CAM", "CM", "CDM", "LM", "RM", "LAM", "RAM", "LCM", "RCM", "LDM", "RDM"]
DEFENDERS = ["CB", "LB", "RB", "LWB", "RWB", "LCB", "RCB"]


def _get_position_group(pos: str) -> str:
    if pos in FORWARDS:
        return "Forward"
    if pos in MIDFIELDERS:
        return "Midfielder"
    if pos in DEFENDERS:
        return "Defender"
    if pos == "GK":
        return "Goalkeeper"
    return "Unknown"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, low_memory=False)

    df["main_position"] = df["player_positions"].str.split(", ").str[0]
    df["position_group"] = df["main_position"].apply(_get_position_group)

    df["log_value"] = np.log1p(df["value_eur"].fillna(0))
    df["growth"] = df["potential"] - df["overall"]

    return df


@st.cache_data
def get_outfield_data(df: pd.DataFrame):
    df_out = df[df["position_group"] != "Goalkeeper"].copy()
    df_out = df_out.reset_index(drop=True)
    return df_out


@st.cache_data
def get_gk_data(df: pd.DataFrame):
    df_gk = df[df["position_group"] == "Goalkeeper"].copy()
    df_gk = df_gk.reset_index(drop=True)
    return df_gk
