import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from utils.mlb_api import get_probable_pitchers_for_date, get_game_lineups, get_live_lineup
from utils.stat_utils import get_pitcher_stats, get_batter_metrics_by_pitch
from datetime import datetime, timedelta
from utils.style_helpers import style_delta_table
from utils.formatting_utils import format_baseball_stats

# --- Helper Function ---
def calculate_and_display_delta():
    # Get the date for the next day
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Get the games for tomorrow
    games = get_game_lineups(tomorrow)

    # Loop through each game and fetch pitcher and lineup data
    for game, data in games.items():
        home_team = data.get("home")
        away_team = data.get("away")
        game_pk = data.get("gamePk")

        # Get the starting pitchers for both teams
        probables_map = get_probable_pitchers_for_date(tomorrow)
        away_pitcher = probables_map.get(f"{away_team} @ {home_team}", {}).get("away_pitcher")
        home_pitcher = probables_map.get(f"{away_team} @ {home_team}", {}).get("home_pitcher")

        # Get lineups from the previous day (or use a fallback if no lineups)
        away_lineup, home_lineup = get_live_lineup(game_pk, starters_only=True) if game_pk else ([], [])

        # Get the batter and pitcher stats
        away_pitcher_df = get_pitcher_stats(away_pitcher)
        home_pitcher_df = get_pitcher_stats(home_pitcher)

        # Create dataframes for the batter's performance by pitch type
        away_batter_df = pd.DataFrame()  # Fetch away batter data
        home_batter_df = pd.DataFrame()  # Fetch home batter data

        # Calculate deltas
        matchup_df = pd.merge(
            away_pitcher_df, home_pitcher_df, on="pitch_type", suffixes=("_away", "_home")
        )

        # Calculate delta values
        for metric in ["K%", "Whiff%", "PutAway%", "SLG", "wOBA", "BA"]:
            matchup_df[f"Δ {metric}"] = (matchup_df[f"{metric}_home"] - matchup_df[f"{metric}_away"]).round(2)

        # Select top 3 batters for each delta category (e.g., Whiff%, K%, etc.)
        top_3_away = {}
        top_3_home = {}

        for metric in ["K%", "Whiff%", "PutAway%", "SLG", "wOBA", "BA"]:
            top_3_away[metric] = matchup_df.nlargest(3, f"Δ {metric}")[['pitch_type', f'Δ {metric}']]
            top_3_home[metric] = matchup_df.nlargest(3, f"Δ {metric}")[['pitch_type', f'Δ {metric}']]

        # --- Display Results ---
        st.title(f"Matchup for {away_team} vs {home_team} ({tomorrow})")
        
        # Display the delta table
        st.markdown("### Delta Table for Away Team")
        st.dataframe(style_delta_table(top_3_away), use_container_width=True)

        st.markdown("### Delta Table for Home Team")
        st.dataframe(style_delta_table(top_3_home), use_container_width=True)

# --- Call the Function ---
if __name__ == "__main__":
    calculate_and_display_delta()
