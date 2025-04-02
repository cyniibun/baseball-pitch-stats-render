import streamlit as st
from urllib.parse import unquote
from utils.lineup_utils import get_game_lineups, get_lineup_for_game
from utils.stat_utils import get_pitcher_stats, get_advanced_pitching_metrics
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

# --- Get Lineups ---
lineup_map = get_game_lineups(date_only)
game_pk = lineup_map.get(f"{away} @ {home}", {}).get("gamePk")
away_lineup, home_lineup = get_lineup_for_game(game_pk) if game_pk else ([], [])

# --- National League Check ---
NATIONAL_LEAGUE_TEAMS = [
    "Atlanta Braves", "Miami Marlins", "New York Mets", "Philadelphia Phillies", "Washington Nationals",
    "Chicago Cubs", "Cincinnati Reds", "Milwaukee Brewers", "Pittsburgh Pirates", "St. Louis Cardinals",
    "Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants"
]

# --- Lineup Processing ---
def extract_lineup(lineup, team_name, allow_pitcher_in_lineup=False):
    pitcher = next((p for p in lineup if " - P" in p), None)
    hitters = [p for p in lineup if p != pitcher] if allow_pitcher_in_lineup else [p for p in lineup if " - P" not in p]
    return pitcher, hitters[:9]

# --- Pitcher Data Renderer ---
def render_pitcher_data(pitcher_label):
    if not pitcher_label:
        st.write("Not announced yet.")
        return
    clean_name = pitcher_label.replace(" - P", "").strip()
    st.write(pitcher_label)

    st.markdown("#### Pitch Arsenal")
    arsenal = get_pitcher_stats(clean_name)
    if arsenal is not None and not arsenal.empty:
        st.dataframe(arsenal, use_container_width=True)
    else:
        st.warning("No pitch data found.")

    st.markdown("#### Advanced Pitching Metrics")
    adv_stats = get_advanced_pitching_metrics(clean_name)
    if adv_stats is not None and not adv_stats.empty:
        st.dataframe(adv_stats, use_container_width=True)
    else:
        st.warning("No advanced stats available.")

# --- UI Columns ---
col1, col2 = st.columns(2)

with col1:
    away_pitcher, away_hitters = extract_lineup(away_lineup, away)
    st.subheader(f"{away} Starting Pitcher")
    render_pitcher_data(away_pitcher)

    st.subheader(f"{away} Batting Lineup")
    if away_hitters:
        for i, batter in enumerate(away_hitters, 1):
            st.markdown(f"{i}. {batter}")
    else:
        st.info("Batting order not available yet.")

with col2:
    include_pitcher_home = home in NATIONAL_LEAGUE_TEAMS
    home_pitcher, home_hitters = extract_lineup(home_lineup, home, allow_pitcher_in_lineup=include_pitcher_home)
    st.subheader(f"{home} Starting Pitcher")
    render_pitcher_data(home_pitcher)

    st.subheader(f"{home} Batting Lineup")
    if home_hitters:
        for i, batter in enumerate(home_hitters, 1):
            st.markdown(f"{i}. {batter}")
    else:
        st.info("Batting order not available yet.")
