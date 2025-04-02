import streamlit as st
from utils.mlb_api import fetch_today_schedule  # Assume this fetches current MLB games
from datetime import datetime
import pytz

st.set_page_config(page_title="Today's MLB Games", layout="wide")
st.title("🌗 Today's MLB Games")

# Fetch today's games from MLB API or fallback method
games = fetch_today_schedule()

if not games:
    st.warning("No games found for today.")
else:
    for game in games:
        home = game.get("home", "Unknown")
        away = game.get("away", "Unknown")
        time_str = game.get("gameTime", "")

        try:
            utc_dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            eastern = pytz.timezone("US/Eastern")
            est_dt = utc_dt.astimezone(eastern)
            formatted_time = est_dt.strftime("%B %d, %Y at %I:%M %p EST")
        except:
            formatted_time = time_str

        game_link = f"/game_view?home={home.replace(' ', '%20')}&away={away.replace(' ', '%20')}&time={time_str}"

        with st.container():
            st.markdown(f"### [{away} @ {home}]({game_link})")
            st.markdown(f":clock1: **Game Time:** {formatted_time}")
            st.markdown("---")
