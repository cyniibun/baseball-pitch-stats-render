import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.style_utils import get_red_shade, get_pitcher_red_green_shade, get_pitcher_blue_red_shade
from utils.lineup_utils import get_game_lineups, get_live_lineup
from utils.mlb_api import (
    get_probable_pitchers_for_date, 
    get_game_state, 
    get_pitcher_advanced_metrics_by_name, 
    get_batter_advanced_metrics_by_name,
    get_pitcher_arsenal_from_api
)
from utils.style_helpers import sanitize_numeric_columns
from utils.scoreboard_utils import render_scoreboard
from utils.formatting_utils import format_baseball_stats
import streamlit as st
from urllib.parse import unquote, quote
from datetime import datetime
import pytz
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Matchup View", layout="wide")

# --- Query Params ---
query_params = st.query_params
home = unquote(query_params.get("home", "Unknown"))
away = unquote(query_params.get("away", "Unknown"))
game_time_utc = query_params.get("time", "Unknown")

# --- Convert to EST ---
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
st.title(f"\U0001F3DF️ {away} @ {home}")
st.markdown(f"\U0001F552 **Game Time:** {formatted_time}")
st.markdown("---")

# --- Get Probable Pitchers ---
probables_map = get_probable_pitchers_for_date(date_only)
probables = probables_map.get(f"{away} @ {home}", {})
away_pitcher = probables.get("away_pitcher")
home_pitcher = probables.get("home_pitcher")

# --- Get GamePK & Lineups ---
lineup_map = get_game_lineups(date_only)
game_pk = lineup_map.get(f"{away} @ {home}", {}).get("gamePk")

# --- Use live active lineup (only 9 players currently in batting order) ---
away_lineup_raw, home_lineup_raw = get_live_lineup(game_pk, starters_only=True) if game_pk else ([], [])

# --- Scoreboard Render ---
if game_pk:
    render_scoreboard(game_pk, home_team=home, away_team=away)

# --- Extract Starters and Subs ---
away_lineup = away_lineup_raw
home_lineup = home_lineup_raw

# --- Fallback Pitcher ---
def fallback_pitcher_from_lineup(lineup):
    return next((p.replace(" - P", "") for p in lineup if " - P" in p), "Not Announced")

if not away_pitcher or away_pitcher == "Not Announced":
    away_pitcher = fallback_pitcher_from_lineup(away_lineup)
if not home_pitcher or home_pitcher == "Not Announced":
    home_pitcher = fallback_pitcher_from_lineup(home_lineup)

st.write("gamePk:", game_pk)

# --- Lineup Renderer ---
# --- Lineup Renderer ---
def render_lineup(pitcher_name, lineup, team_name):
    pitch_types = []
    arsenal_df = None

    st.markdown(f"<h4 style='margin-bottom: 0.25rem;'>{team_name} Starting Pitcher</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top: -0.5rem; margin-bottom: 0.5rem;'>{pitcher_name or 'Not announced yet.'}</p>", unsafe_allow_html=True)

    st.markdown("<h4 style='margin-bottom: 0.5rem;'>Pitch Arsenal</h4>", unsafe_allow_html=True)

    if pitcher_name and pitcher_name != "Not Announced":
        # Fetch the pitch arsenal (types, PA, etc.) using the correct function
        arsenal_df = get_pitcher_arsenal_from_api(pitcher_name)  # Use this function for pitch arsenal data
        
        # Debugging to check what data we are getting
        st.write(f"Pitch Arsenal for {pitcher_name}: {arsenal_df}")

        if isinstance(arsenal_df, pd.DataFrame) and not arsenal_df.empty:
            # ✅ Sanitize numerical columns
            arsenal_df = sanitize_numeric_columns(arsenal_df, ["PA", "BA", "SLG", "wOBA", "K%", "Whiff%", "PutAway%"])

            # ✅ Pre-format values to 3 decimal places, strip trailing 0s
            stat_cols = ["BA", "SLG", "wOBA", "K%", "Whiff%", "PutAway%"]
            for col in stat_cols:
                if col in arsenal_df.columns:
                    arsenal_df[col] = arsenal_df[col].map(lambda x: f"{x:.3f}".rstrip("0").rstrip(".") if pd.notnull(x) else "-")

            # ✅ Display the arsenal in a nice table
            display_df = arsenal_df[["pitch_type", "PA", "BA", "SLG", "wOBA", "K%", "Whiff%", "PutAway%"]].fillna("-")

            st.dataframe(
                display_df.style
                    .map(get_pitcher_blue_red_shade, subset=["BA", "SLG", "wOBA"])
                    .map(lambda v: get_pitcher_red_green_shade(v, high_is_good=True), subset=["K%", "Whiff%", "PutAway%"]),
                use_container_width=True
            )

            pitch_types = display_df["pitch_type"].tolist()
        else:
            st.warning(f"No pitch data found for {pitcher_name}.")
    
    height = len(arsenal_df) if arsenal_df is not None else 0
    return pitch_types, lineup, team_name, pitcher_name, height




# --- Fetch Batter K% Stats ---
def fetch_batter_k_rates(batters):
    stats = {}

    def fetch_and_store(batter):
        stats[batter] = get_batter_k_rate_by_pitch(batter) or {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_and_store, batters)

    return stats

# Gather all unique batters from both lineups
all_batters = list({player.split(" - ")[0].strip() for player in away_lineup + home_lineup if player.strip()})

# Fetch K% data for all batters in parallel
away_k_rate_lookup = fetch_batter_k_rates(home_pitcher)  # Away team batters vs home pitcher
home_k_rate_lookup = fetch_batter_k_rates(away_pitcher)  # Home team batters vs away pitcher


# --- Batting Lineup Renderer ---
def render_batting_lineup(pitch_types, pitcher_name, lineup, team_name, k_rate_lookup):
    st.subheader(f"{team_name} Batting Lineup")

    if not lineup:
        st.info("Batting order not available yet.")
        return

    st.markdown("""<style>
        .lineup-wrapper {
            overflow-x: auto;
            padding-bottom: 1rem;
            max-width: 100%;
        }

        .lineup-table {
            width: max-content;
            min-width: 600px;
            border-collapse: collapse;
            font-family: monospace;
            font-size: 13px;
            table-layout: fixed;
        }

        .lineup-table th, .lineup-table td {
            border: 1px solid #444;
            padding: 6px 10px;
            text-align: center;
            white-space: nowrap;
            color: white;
        }

        .lineup-table th {
            background-color: #1e1e1e;
        }

        .lineup-table tr:nth-child(even) {
            background-color: #2a2a2a;
        }

        .lineup-table tr:hover {
            background-color: #333333;
        }

        .lineup-table a {
            color: #4da6ff;
            text-decoration: none;
        }

        .lineup-table a:hover {
            text-decoration: underline;
        }

        .lineup-table td:last-child,
        .lineup-table th:last-child {
            position: sticky;
            right: 0;
            background-color: #1e1e1e;
            z-index: 1;
        }

        .lineup-table td:last-child::after,
        .lineup-table th:last-child::after {
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            width: 4px;
            background: linear-gradient(to right, rgba(0,0,0,0.15), transparent);
        }

        @media (max-width: 768px) {
            .lineup-table {
                font-size: 12px;
                min-width: 100%;
            }
        }
    </style>""", unsafe_allow_html=True)

    # Table headers
    headers = "<tr><th>#</th><th>Batter</th>"
    for pitch in pitch_types:
        headers += f"<th>{pitch} K%</th>"
    headers += "<th>View Matchup</th></tr>"

    rows = ""
    for i, player in enumerate(lineup):
        if player.strip() == "":
            row = f"<tr><td>-</td><td>-</td>"
            for _ in pitch_types:
                row += "<td>-</td>"
            row += "<td>-</td></tr>"
            rows += row
            continue

        batter_name = player.split(" - ")[0].strip()
        k_vals = k_rate_lookup.get(batter_name, {})

        row = f"<tr><td>{i+1}</td><td><strong>{batter_name}</strong></td>"

        for pitch in pitch_types:
            val = k_vals.get(pitch, "0.0%")
            style = get_red_shade(val)
            row += f"<td style='{style}'>{val}</td>"

        matchup_url = (
            f"/matchup_view?batter={quote(batter_name)}"
            f"&team={quote(team_name)}"
            f"&home={quote(home)}"
            f"&away={quote(away)}"
            f"&home_pitcher={quote(home_pitcher)}"
            f"&away_pitcher={quote(away_pitcher)}"
        )

        row += f"<td><a href='{matchup_url}'>View Matchup</a></td></tr>"

        rows += row

    table_html = f"""
        <div class="lineup-wrapper">
            <table class="lineup-table">
                <thead>{headers}</thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# --- Render Columns Side-by-Side ---
col1, col2 = st.columns(2)

with col1:
    pt_1, lu_1, tn_1, pn_1, h1 = render_lineup(away_pitcher, away_lineup, away)
    render_batting_lineup(pt_1, pn_1, away_lineup, away, away_k_rate_lookup)

with col2:
    pt_2, lu_2, tn_2, pn_2, h2 = render_lineup(home_pitcher, home_lineup, home)
    render_batting_lineup(pt_2, pn_2, home_lineup, home, home_k_rate_lookup)
