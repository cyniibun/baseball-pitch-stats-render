import streamlit as st
from urllib.parse import unquote
from utils.lineup_utils import get_game_lineups, get_lineup_for_game
from datetime import datetime
import pytz

st.set_page_config(page_title="Matchup View", layout="wide")

# --- Query Params ---
query_params = st.query_params
home = unquote(query_params.get("home", "Unknown"))
away = unquote(query_params.get("away", "Unknown"))
game_time_utc = query_params.get("time", "Unknown")

# --- Convert to EST for display ---
try:
    utc_dt = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
    eastern = pytz.timezone("US/Eastern")
    est_dt = utc_dt.astimezone(eastern)
    formatted_time = est_dt.strftime("%B %d, %Y at %I:%M %p EST")
    date_only = est_dt.strftime("%Y-%m-%d")
except Exception:
    formatted_time = game_time_utc
    date_only = game_time_utc.split("T")[0] if "T" in game_time_utc else "Unknown"

# --- Header ---
st.title(f"🏟️ {away} @ {home}")
st.markdown(f"🕒 **Game Time:** {formatted_time}")
st.markdown("---")

# --- Find gamePK ---
lineup_map = get_game_lineups(date_only)
key = f"{away} @ {home}"
game_pk = lineup_map.get(key, {}).get("gamePk")

# --- Fetch lineups ---
if game_pk:
    away_lineup, home_lineup = get_lineup_for_game(game_pk)
else:
    away_lineup, home_lineup = [], []

# --- National League Teams ---
NATIONAL_LEAGUE_TEAMS = [
    "Atlanta Braves", "Miami Marlins", "New York Mets", "Philadelphia Phillies", "Washington Nationals",
    "Chicago Cubs", "Cincinnati Reds", "Milwaukee Brewers", "Pittsburgh Pirates", "St. Louis Cardinals",
    "Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants"
]

# --- Helper to extract pitcher and batting order ---
def extract_lineup(lineup, team_name, allow_pitcher_in_lineup=False):
    pitcher = next((p for p in lineup if " - P" in p), None)
    if allow_pitcher_in_lineup:
        hitters = [p for p in lineup if p != pitcher]
    else:
        hitters = [p for p in lineup if " - P" not in p]
    return pitcher, hitters[:9] if len(hitters) >= 9 else hitters

# --- Determine if pitcher should be in lineup for home team ---
include_pitcher_home = home in NATIONAL_LEAGUE_TEAMS

# --- UI Columns ---
col1, col2 = st.columns(2)

with col1:
    away_pitcher, away_hitters = extract_lineup(away_lineup, away, allow_pitcher_in_lineup=False)
    st.subheader(f"{away} Starting Pitcher")
    st.write(away_pitcher or "Not announced yet.")
    
    st.subheader(f"{away} Batting Lineup")
    if away_hitters:
        for i, batter in enumerate(away_hitters, 1):
            st.markdown(f"{i}. {batter}")
    else:
        st.info("Batting order not available yet.")

with col2:
    home_pitcher, home_hitters = extract_lineup(home_lineup, home, allow_pitcher_in_lineup=include_pitcher_home)
    st.subheader(f"{home} Starting Pitcher")
    st.write(home_pitcher or "Not announced yet.")

    st.subheader(f"{home} Batting Lineup")
    if home_hitters:
        for i, batter in enumerate(home_hitters, 1):
            st.markdown(f"{i}. {batter}")
    else:
        st.info("Batting order not available yet.")