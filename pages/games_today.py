# pages/games_today.py

import streamlit as st
from utils.mlb_api import fetch_today_schedule

st.set_page_config(page_title="Today's MLB Schedule", layout="wide")
st.title("📅 MLB Games Today")

with st.spinner("Fetching today's schedule..."):
    games = fetch_today_schedule()

if not games:
    st.warning("No games scheduled for today or failed to fetch schedule.")
else:
    for game in games:
        st.markdown(f"""
        ### {game['awayTeam']} @ {game['homeTeam']}
        ⏰ **Game Time (UTC):** {game['gameTime']}  
        🆔 **Game ID:** `{game['gamePk']}`
        ---  
        """)
