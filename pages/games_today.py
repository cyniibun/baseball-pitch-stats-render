import streamlit as st
from urllib.parse import quote
from utils.mlb_api import fetch_today_schedule

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
            st.markdown(f"🕒 **Game Time (UTC):** {game_time}")
            st.markdown("---")
