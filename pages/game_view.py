# file: pages/game_view.py

import streamlit as st
from urllib.parse import unquote

st.set_page_config(page_title="Matchup View", layout="wide")

# ✅ Use st.query_params safely (they are already strings, not lists)
query_params = st.query_params

home = unquote(query_params.get("home", "Unknown"))
away = unquote(query_params.get("away", "Unknown"))
game_time = query_params.get("time", "Unknown")

# 🧾 Display Matchup Header
st.title(f"🏟️ {away} @ {home}")
st.markdown(f"🕒 **Game Time (UTC):** {game_time}")
st.markdown("---")

# 🚧 Placeholder for more details
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{away} Lineup")
    st.info("Lineup and pitcher data coming soon!")

with col2:
    st.subheader(f"{home} Lineup")
    st.info("Lineup and pitcher data coming soon!")
