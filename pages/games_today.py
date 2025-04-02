import streamlit as st
from utils.mlb_api import fetch_today_schedule

st.title("📅 Today's MLB Games")

games = fetch_today_schedule()

if not games:
    st.info("No games scheduled for today.")
else:
    for game in games:
        st.markdown(f"### {game['away']} @ {game['home']}")
        st.markdown(f"⏰ **Game Time (UTC):** {game['gameTime']}")
        st.markdown("---")
