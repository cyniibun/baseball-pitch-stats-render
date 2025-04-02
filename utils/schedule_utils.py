# file: utils/schedule_utils.py

from pybaseball import schedule_and_record
from datetime import datetime
import pandas as pd
import pytz
import time

def get_today_schedule():
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).date()

    all_teams = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
    ]

    games_today = []
    start_time = time.time()

    for team in all_teams:
        try:
            print(f"[DEBUG] Fetching schedule for: {team}")
            schedule = schedule_and_record(datetime.now().year, team)
            todays_games = schedule[schedule['Date'].dt.date == today]

            for _, row in todays_games.iterrows():
                games_today.append({
                    'team': team,
                    'opponent': row['Opp'],
                    'home': row['Home'],
                    'time': row['Time'],
                    'result': row['Result'],
                })
        except Exception as e:
            print(f"[ERROR] Failed for {team}: {e}")
            continue

    seen = set()
    unique_games = []
    for game in games_today:
        matchup_key = tuple(sorted([game['team'], game['opponent']]))
        if matchup_key not in seen:
            seen.add(matchup_key)
            unique_games.append(game)

    print(f"[DEBUG] Total unique games: {len(unique_games)}")
    print(f"[DEBUG] Finished in {time.time() - start_time:.2f} seconds")
    return unique_games
