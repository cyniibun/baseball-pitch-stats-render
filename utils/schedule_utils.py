# utils/schedule_utils.py

from pybaseball import schedule_and_record
from datetime import datetime
import pytz

def fetch_schedule_by_date(target_date: datetime):
    eastern = pytz.timezone("US/Eastern")
    target_date = eastern.localize(target_date)

    all_teams = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
    ]

    games = []
    seen = set()

    for team in all_teams:
        try:
            schedule = schedule_and_record(target_date.year, team)
            day_games = schedule[schedule['Date'].dt.date == target_date.date()]
            for _, row in day_games.iterrows():
                matchup_key = tuple(sorted([team, row['Opp']]))
                if matchup_key not in seen:
                    seen.add(matchup_key)
                    games.append({
                        "home": team if row["Home"] else row["Opp"],
                        "away": row["Opp"] if row["Home"] else team,
                        "gameTime": row["Date"].isoformat()
                    })
        except Exception as e:
            print(f"[ERROR] Failed fetching for {team}: {e}")
            continue

    return games
