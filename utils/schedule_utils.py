# file: utils/schedule_utils.py

from pybaseball import schedule_and_record
from datetime import datetime
import pytz

def get_today_schedule():
    # Get today's date in Eastern Time
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).date()

    # pybaseball requires a team and year, so we'll iterate all teams
    all_teams = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
    ]

    games_today = []

    for team in all_teams:
        try:
            schedule = schedule_and_record(datetime.now().year, team)
            todays_games = schedule[schedule['Date'].dt.date == today]
            for _, row in todays_games.iterrows():
                opponent = row['Opp']
                games_today.append({
                    'team': team,
                    'opponent': opponent,
                    'home': row['Home'],
                    'time': row['Time'],
                    'result': row['Result'],
                })
        except:
            continue

    # Deduplicate mirror matchups
    seen = set()
    unique_games = []
    for game in games_today:
        matchup_key = tuple(sorted([game['team'], game['opponent']]))
        if matchup_key not in seen:
            seen.add(matchup_key)
            unique_games.append(game)

    print(f"[DEBUG] Total unique games: {len(unique_games)}")  # ✅ moved inside
    return unique_games
