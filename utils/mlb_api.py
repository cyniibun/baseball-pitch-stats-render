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


def get_player_id(first_name, last_name):
    """Retrieve MLB player ID using Stats API search."""
    search_url = f"https://statsapi.mlb.com/api/v1/people/search?names={first_name}%20{last_name}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("people"):
            return data["people"][0]["id"]
    return None

def get_pitching_stats(player_id, season):
    """Fetch season-to-date pitching stats for a given player."""
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}&group=pitching"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        splits = data.get("stats", [])[0].get("splits", [])
        if splits:
            stat = splits[0].get("stat", {})
            return {
                "BA": stat.get("avg", "N/A"),
                "SLG": stat.get("slg", "N/A"),
                "wOBA": stat.get("wOBA", "N/A"),
                "strikeOuts": stat.get("strikeOuts", 0),
                "battersFaced": stat.get("battersFaced", 0),
                "twoStrikeCounts": stat.get("twoStrikeCounts", 0),
                "numberOfPitches": stat.get("numberOfPitches", 0),
                "contactPitches": stat.get("contactPitches", 0),
            }
    return None


def calculate_advanced_metrics(stats):
    """Calculate and collect pitching metrics."""
    try:
        whiff_rate = (
            (stats["numberOfPitches"] - stats["contactPitches"]) / stats["numberOfPitches"] * 100
            if stats["numberOfPitches"] else None
        )
        k_rate = (
            stats["strikeOuts"] / stats["battersFaced"] * 100
            if stats["battersFaced"] else None
        )
        putaway_rate = (
            stats["strikeOuts"] / stats["twoStrikeCounts"] * 100
            if stats["twoStrikeCounts"] else None
        )

        return {
            "BA": stats.get("BA", "N/A"),
            "SLG": stats.get("SLG", "N/A"),
            "wOBA": stats.get("wOBA", "N/A"),
            "Whiff%": round(whiff_rate, 2) if whiff_rate is not None else "N/A",
            "K%": round(k_rate, 2) if k_rate is not None else "N/A",
            "PutAway%": round(putaway_rate, 2) if putaway_rate is not None else "N/A"
        }
    except (TypeError, ZeroDivisionError, KeyError):
        return {
            "BA": "N/A",
            "SLG": "N/A",
            "wOBA": "N/A",
            "Whiff%": "N/A",
            "K%": "N/A",
            "PutAway%": "N/A"
        }
def get_pitcher_advanced_metrics_by_name(full_name, season=None):
    """Helper to go from name to advanced metrics dict."""
    try:
        first, last = full_name.strip().split(" ", 1)
        player_id = get_player_id(first, last)
        if not player_id:
            return {}

        if not season:
            season = datetime.now().year

        raw_stats = get_pitching_stats(player_id, season)
        if not raw_stats:
            return {}

        return calculate_advanced_metrics(raw_stats)
    except Exception as e:
        print(f"[ERROR] Failed to calculate metrics for {full_name}: {e}")
        return {}

