import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pybaseball import schedule_and_record

CACHE_DIR = "cached_schedules"

def fetch_schedule_by_date(date, force_refresh=False):
    date_str = date.strftime("%Y-%m-%d")
    cache_file = os.path.join(CACHE_DIR, f"{date_str}.json")

    if not force_refresh and os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load cache for {date_str}: {e}")

    # Fallback to fresh fetch
    print(f"[FETCH] Fetching fresh data for {date_str}")
    games = []
    all_teams = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
    ]

    for team in all_teams:
        try:
            schedule = schedule_and_record(date.year, team)
            day_schedule = schedule[schedule["Date"].dt.date == date.date()]
            for _, row in day_schedule.iterrows():
                games.append({
                    "team": team,
                    "opponent": row["Opp"],
                    "home": row["Home"],
                    "time": row["Time"],
                    "result": row["Result"]
                })
        except Exception as e:
            print(f"[ERROR] Could not fetch for {team} on {date_str}: {e}")
            break  # Break on first failure to prevent infinite loop

    # Save to cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(games, f)

    return games


def get_schedule():
    """Returns a DataFrame of games for today and tomorrow, using cache or fallback."""
    all_games = []

    for offset in [0, 1]:  # Today and Tomorrow
        target_date = (datetime.utcnow() + timedelta(days=offset)).date()
        games = fetch_schedule_by_date(datetime.combine(target_date, datetime.min.time()))

        for game in games:
            game["Date"] = f"{target_date} {game.get('time', '00:00')}"
            game["Home"] = game.get("home", "Unknown")
            game["Away"] = game.get("opponent", "Unknown")
            all_games.append(game)

    if not all_games:
        return pd.DataFrame()

    df = pd.DataFrame(all_games)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    return df.dropna(subset=["Date"])

# Attempt to test fetching today's schedule to confirm no infinite loop
test_df = get_schedule()
test_df.head()
