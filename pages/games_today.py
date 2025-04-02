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

        game_link = (
            f"/game_view?home={home.replace(' ', '%20')}"
            f"&away={away.replace(' ', '%20')}"
            f"&time={game_time}"
        )

        with st.container():
            from urllib.parse import quote

            # Create encoded query string
            query = f"?home={quote(game['home'])}&away={quote(game['away'])}&time={quote(game['gameTime'])}"

            # Full URL to the dynamic page
            link = f"/game_view{query}"

            st.markdown(f"""
            ### [{game['away']} @ {game['home']}]({link})
            🕒 **Game Time (UTC):** {game['gameTime']}
            ---
            """)
