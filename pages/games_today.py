import streamlit as st
from utils.mlb_api import fetch_today_schedule

def show_schedule_page():
    st.title("📅 Today's MLB Games")

    games = fetch_today_schedule()

    if not games:
        st.info("No games scheduled for today.")
    else:
        for game in games:
            matchup = f"{game['away']} at {game['home']}"
            game_time = game['gameTime']
            st.markdown(f"### {matchup}")
            st.text(f"Time: {game_time}")
