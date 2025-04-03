import streamlit as st
from datetime import datetime, date, timedelta
import pytz
from utils.schedule_utils import fetch_schedule_by_date
import pandas as pd
schedule_df = pd.read_csv("data/schedule_cache.csv", parse_dates=["Date"])


st.set_page_config(page_title="MLB Schedule by Date", layout="wide")
st.title("📅 MLB Schedule by Date")

# --- Date Selector Mode ---
mode = st.selectbox("Choose a date option", ["Today", "Tomorrow", "Pick a date..."])

# --- Determine selected date ---
if mode == "Today":
    selected_date = date.today()
elif mode == "Tomorrow":
    selected_date = date.today() + timedelta(days=1)
else:
    selected_date = st.date_input("Select Date", date.today())

# --- Fetch games for selected date ---
games = fetch_schedule_by_date(datetime.combine(selected_date, datetime.min.time()))

# --- Display games ---
if not games:
    st.warning("No games found for this date.")
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

        game_link = (
            f"/game_view?home={home.replace(' ', '%20')}"
            f"&away={away.replace(' ', '%20')}"
            f"&time={time_str}"
        )

        with st.container():
            st.markdown(f"### [{away} @ {home}]({game_link})")
            st.markdown(f":clock1: **Game Time:** {formatted_time}")
            st.markdown("---")
