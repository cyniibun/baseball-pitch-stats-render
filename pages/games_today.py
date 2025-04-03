import sys
import os
import streamlit as st
from urllib.parse import quote
from utils.mlb_api import fetch_today_schedule
from datetime import datetime
import pytz

def format_utc_to_est(utc_str):
    try:
        utc_time = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        est = pytz.timezone("US/Eastern")
        est_time = utc_time.astimezone(est)
        return est_time.strftime("%B %d, %Y at %I:%M %p ET")
    except:
        return utc_str  # fallback if parsing fails

st.set_page_config(page_title="Today's MLB Games", layout="wide")
st.title("📅 Today's MLB Games")

games = fetch_today_schedule()

if not games:
    st.warning("No games scheduled for today.")
else:
    for game in games:
        home = game.get("home", "Unknown")
        away = game.get("away", "Unknown")
        game_time = game.get("gameTime", "N/A")

        # Create encoded query string
        query = f"?home={quote(home)}&away={quote(away)}&time={quote(game_time)}"

        # Full URL to the dynamic page
        link = f"/game_view{query}"

        with st.container():
            st.markdown(f"### [{away} @ {home}]({link})")
            st.markdown(f"🕒 **Game Time:** {format_utc_to_est(game['gameTime'])}")
            st.markdown("---")
