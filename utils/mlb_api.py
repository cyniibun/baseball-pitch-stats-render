import requests
from datetime import datetime
import pytz

def fetch_today_schedule():
    # Set timezone to Eastern Time
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).strftime("%Y-%m-%d")

    # MLB API endpoint for the schedule
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    response = requests.get(url)
    data = response.json()

    games = []
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            teams = game["teams"]
            games.append({
                "home": teams["home"]["team"]["name"],
                "away": teams["away"]["team"]["name"],
                "gameTime": game["gameDate"]
            })
    return games
    print("[DEBUG] Fetched games from MLB API:", games)

