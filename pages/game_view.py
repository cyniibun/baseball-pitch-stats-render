import streamlit as st
from urllib.parse import unquote
from utils.lineup_utils import get_game_lineups, get_lineup_for_game
from datetime import datetime
import pytz

st.set_page_config(page_title="Matchup View", layout="wide")

# Read and decode query params
query_params = st.query_params
home = unquote(query_params.get("home", "Unknown"))
away = unquote(query_params.get("away", "Unknown"))
game_time_utc = query_params.get("time", "Unknown")

# Format game time to EST
try:
    # Parse the UTC ISO time
    utc_dt = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
    eastern = pytz.timezone("US/Eastern")
    est_dt = utc_dt.astimezone(eastern)
    formatted_time = est_dt.strftime("%B %d, %Y at %I:%M %p EST")
except Exception:
    formatted_time = game_time_utc  # fallback in case of parsing error

# Display matchup header
st.title(f"🏟️ {away} @ {home}")
st.markdown(f"🕒 **Game Time:** {formatted_time}")
st.markdown("---")

# Placeholder columns
col1, col2 = st.columns(2)

# Parse date from time param (e.g. 2025-04-02T16:40:00Z → 2025-04-02)
date_only = game_time.split("T")[0]

# Find gamePk by matching teams
lineup_map = get_game_lineups(date_only)
key = f"{away} @ {home}"
game_pk = lineup_map.get(key, {}).get("gamePk")

if game_pk:
    away_lineup, home_lineup = get_lineup_for_game(game_pk)
else:
    away_lineup, home_lineup = [], []

with col1:
    st.subheader(f"{away} Lineup")
    if away_lineup:
        for player in away_lineup:
            st.markdown(f"- {player}")
    else:
        st.info("Lineup not available yet.")

with col2:
    st.subheader(f"{home} Lineup")
    if home_lineup:
        for player in home_lineup:
            st.markdown(f"- {player}")
    else:
        st.info("Lineup not available yet.")
