import streamlit as st
from urllib.parse import unquote
from datetime import datetime
import pytz

st.set_page_config(page_title="Matchup View", layout="wide")

# Read and decode query params
query_params = st.query_params
home = unquote(query_params.get("home", "Unknown"))
away = unquote(query_params.get("away", "Unknown"))
game_time_utc = query_params.get("time", "Unknown")

# Format game time to EST
try:
    # Parse the UTC ISO time
    utc_dt = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
    eastern = pytz.timezone("US/Eastern")
    est_dt = utc_dt.astimezone(eastern)
    formatted_time = est_dt.strftime("%B %d, %Y at %I:%M %p EST")
except Exception:
    formatted_time = game_time_utc  # fallback in case of parsing error

# Display matchup header
st.title(f"🏟️ {away} @ {home}")
st.markdown(f"🕒 **Game Time:** {formatted_time}")
st.markdown("---")

# Placeholder columns
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{away} Lineup")
    st.info("Lineup and pitcher data coming soon!")

with col2:
    st.subheader(f"{home} Lineup")
    st.info("Lineup and pitcher data coming soon!")
