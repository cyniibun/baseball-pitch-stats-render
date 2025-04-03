import streamlit as st
from utils.schedule_utils import get_schedule
from datetime import datetime
import pytz

st.set_page_config(page_title="MLB Schedule", layout="wide")
st.title("📅 MLB Schedule")

# Load today's + tomorrow's schedule
schedule_df = get_schedule()

if schedule_df.empty:
    st.warning("No games found for today or tomorrow.")
else:
    eastern = pytz.timezone("US/Eastern")
    schedule_df = schedule_df.sort_values(by="Date")

    for _, game in schedule_df.iterrows():
        home = game.get("home") or game.get("Home", "Unknown")
        away = game.get("opponent") or game.get("Away", "Unknown")
        game_time = game["Date"]

        try:
            if pd.isna(game_time):
                formatted_time = "TBD"
                iso_time = ""
            else:
                if game_time.tzinfo is None:
                    game_time = pytz.utc.localize(game_time)
                game_time = game_time.astimezone(eastern)
                formatted_time = game_time.strftime("%B %d, %Y at %I:%M %p EST")
                iso_time = game_time.isoformat()
        except:
            formatted_time = "TBD"
            iso_time = ""

        game_link = (
            f"/game_view?home={home.replace(' ', '%20')}"
            f"&away={away.replace(' ', '%20')}"
            f"&time={iso_time}"
        )

        with st.container():
            st.markdown(f"### [{away} @ {home}]({game_link})")
            st.markdown(f":clock1: **Game Time:** {formatted_time}")
            st.markdown("---")
