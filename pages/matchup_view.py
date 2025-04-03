import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from urllib.parse import unquote
from utils.stat_utils import get_pitcher_stats, get_batter_metrics_by_pitch
from utils.style_helpers import style_pitcher_table, style_batter_table, style_delta_table

st.set_page_config(page_title="Batter vs Pitcher Matchup", layout="wide")

# --- Query Params ---
query_params = st.query_params
batter_name = unquote(query_params.get("batter", "Unknown"))
team_name = unquote(query_params.get("team", "Unknown"))
home_team = unquote(query_params.get("home", "Unknown"))
away_team = unquote(query_params.get("away", "Unknown"))
home_pitcher = unquote(query_params.get("home_pitcher", "Not Announced"))
away_pitcher = unquote(query_params.get("away_pitcher", "Not Announced"))

# Determine opponent pitcher
pitcher_name = away_pitcher if team_name == home_team else home_pitcher

st.title(f"Matchup: {batter_name} vs. {pitcher_name}")
st.markdown(f"**Team:** {team_name}")
st.markdown("---")

# --- Fetch Stats ---
pitcher_df = get_pitcher_stats(pitcher_name)
batter_df = get_batter_metrics_by_pitch(batter_name)

if pitcher_df.empty or batter_df.empty:
    st.warning("Insufficient data to display matchup.")
else:
    # Round values for display
    batter_df = batter_df.round(2)
    pitcher_df = pitcher_df.round(2)

    # Filter to common pitch types
    common_pitches = set(pitcher_df["pitch_type"]) & set(batter_df["pitch_type"])
    pitcher_df = pitcher_df[pitcher_df["pitch_type"].isin(common_pitches)]
    batter_df = batter_df[batter_df["pitch_type"].isin(common_pitches)]

    # Merge for delta calculation
    matchup_df = pd.merge(
        pitcher_df,
        batter_df,
        on="pitch_type",
        suffixes=("_P", "_B")
    )

    for metric in ["K%", "Whiff%", "PutAway%", "SLG", "wOBA", "BA"]:
        matchup_df[f"Δ {metric}"] = (matchup_df[f"{metric}_B"] - matchup_df[f"{metric}_P"]).round(2)

    # --- Display Pitcher Table ---
    st.markdown("### Pitcher Arsenal")
    pitcher_cols = ["pitch_type", "PA", "BA", "SLG", "wOBA", "K%", "Whiff%", "PutAway%"]
    st.dataframe(style_pitcher_table(pitcher_df[pitcher_cols]), use_container_width=True)

    # --- Display Batter Table ---
    st.markdown("### Batter Metrics by Pitch Type")
    batter_cols = ["pitch_type", "BA", "SLG", "wOBA", "K%", "Whiff%", "PutAway%"]
    st.dataframe(style_batter_table(batter_df[batter_cols]), use_container_width=True)

    # --- Delta Table ---
    st.markdown("### Matchup Delta Table")
    delta_cols = [
        "pitch_type", 
        "K%_P", "K%_B", "Δ K%",
        "Whiff%_P", "Whiff%_B", "Δ Whiff%",
        "PutAway%_P", "PutAway%_B", "Δ PutAway%",
        "SLG_P", "SLG_B", "Δ SLG",
        "wOBA_P", "wOBA_B", "Δ wOBA",
        "BA_P", "BA_B", "Δ BA"
    ]
    st.dataframe(style_delta_table(matchup_df[delta_cols]), use_container_width=True)
