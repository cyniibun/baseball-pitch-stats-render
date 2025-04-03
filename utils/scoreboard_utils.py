import streamlit as st
from utils.mlb_api import get_game_state
from streamlit_autorefresh import st_autorefresh

def render_scoreboard(game_pk, home_team="Home", away_team="Away", autorefresh=True):
    if autorefresh:
        st_autorefresh(interval=15 * 1000, key=f"autorefresh-{game_pk}")

    state = get_game_state(game_pk)
    if not state:
        st.info("Live data not available.")
        return

    status = state.get("status", "").lower()
    linescore = state.get("linescore", {})
    away = linescore.get("away", {})
    home = linescore.get("home", {})

    home_score = home.get("runs", 0)
    away_score = away.get("runs", 0)

    # Determine winner
    if home_score > away_score:
        winner = "home"
    elif away_score > home_score:
        winner = "away"
    else:
        winner = "tie"

    winner_style = "color: #0af; font-weight: bold;"
    loser_style = "color: #999;"
    tie_style = "color: #ccc; font-style: italic;"

    home_style = winner_style if winner == "home" else loser_style
    away_style = winner_style if winner == "away" else loser_style
    if winner == "tie":
        home_style = away_style = tie_style

    # ✅ Final Game Handling
    if any(term in status for term in ["final", "completed", "game over"]):
        st.markdown(f"""
        <div style="border: 1px solid #444; border-radius: 8px; padding: 16px; margin: 0.5rem 0 1.5rem 0;">
            <h4 style="margin-bottom: 0.5rem; text-align: center;">Final</h4>
            <p style="{away_style}"><strong>{away_team}</strong>: {away_score} R</p>
            <p style="{home_style}"><strong>{home_team}</strong>: {home_score} R</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ✅ Live Game Handling
    inning = state.get("inning", "-")
    half = state.get("half", "-")
    count = state.get("count", "0-0")
    outs = state.get("outs", 0)
    bases = state.get("bases", [])

    balls, strikes = map(int, count.split("-"))
    ball_icons = "🟢" * balls + "⚪️" * (3 - balls)
    strike_icons = "🔴" * strikes + "⚪️" * (2 - strikes)
    out_icons = "⚫️" * outs + "⚪️" * (3 - outs)

    # 👇 Render HTML directly
    scoreboard_html = f"""
    <div style="border: 1px solid #444; border-radius: 8px; padding: 16px; margin: 0.5rem 0 1.5rem 0;">
        <h4 style="margin-bottom: 0.5rem; text-align: center;">{half.title()} {inning}</h4>
        <div style="display: flex; justify-content: center;">
            <div style="display: flex; flex-direction: row; align-items: center; gap: 36px; flex-wrap: wrap; max-width: 800px;">
                <div style="min-width: 240px;">
                    <strong>Count:</strong><br>
                    <div style="display: flex; flex-direction: column; align-items: flex-start; line-height: 1.4;">
                        <div><strong>Balls:</strong> {ball_icons}</div>
                        <div><strong>Strikes:</strong> {strike_icons}</div>
                    </div>
                    <p style="margin: 0.25rem 0;"><strong>Outs:</strong> {out_icons}</p>
                    <div style="margin-top: 1rem;">
                        <p style="margin: 0.25rem 0;"><strong>{away_team}</strong>: {away.get('runs', 0)} R / {away.get('hits', 0)} H / {away.get('xba', '.000')}</p>
                        <p style="margin: 0.25rem 0;"><strong>{home_team}</strong>: {home.get('runs', 0)} R / {home.get('hits', 0)} H / {home.get('xba', '.000')}</p>
                    </div>
                </div>
                <div style='position: relative; width: 80px; height: 80px;'>
                    <div style='position: absolute; top: 0; left: 50%; transform: translate(-50%, -50%) rotate(45deg);
                        width: 20px; height: 20px; border: 2px solid #999; {"background-color:#0af;" if "2B" in bases else ""}'></div>
                    <div style='position: absolute; left: 0; top: 50%; transform: translate(-50%, -50%) rotate(45deg);
                        width: 20px; height: 20px; border: 2px solid #999; {"background-color:#0af;" if "3B" in bases else ""}'></div>
                    <div style='position: absolute; right: 0; top: 50%; transform: translate(50%, -50%) rotate(45deg);
                        width: 20px; height: 20px; border: 2px solid #999; {"background-color:#0af;" if "1B" in bases else ""}'></div>
                    <div style='position: absolute; bottom: 0; left: 50%; transform: translate(-50%, 50%) rotate(45deg);
                        width: 20px; height: 20px; border: 2px solid #ccc;'></div>
                </div>
            </div>
        </div>
    </div>
    """
    # ✅ Final Game Handling with Icons
    if any(term in status for term in ["final", "completed", "game over"]):
        # Determine winner and assign styles + icons
        if home_score > away_score:
            winner = "home"
            home_icon, away_icon = "🏆", "❌"
        elif away_score > home_score:
            winner = "away"
            home_icon, away_icon = "❌", "🏆"
        else:
            winner = "tie"
            home_icon = away_icon = "⚔️"

        winner_style = "color: #0af; font-weight: bold;"
        loser_style = "color: #999;"
        tie_style = "color: #ccc; font-style: italic;"

        home_style = winner_style if winner == "home" else loser_style
        away_style = winner_style if winner == "away" else loser_style
        if winner == "tie":
            home_style = away_style = tie_style

        st.markdown(f"""
        <div style="border: 1px solid #444; border-radius: 8px; padding: 16px; margin: 0.5rem 0 1.5rem 0;">
            <h4 style="margin-bottom: 0.5rem; text-align: center;">Final</h4>
            <p style="{away_style}">{away_icon} <strong>{away_team}</strong>: {away_score} R</p>
            <p style="{home_style}">{home_icon} <strong>{home_team}</strong>: {home_score} R</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(scoreboard_html, unsafe_allow_html=True)
