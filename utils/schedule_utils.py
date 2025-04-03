import os
import json
import time
from datetime import datetime
from pybaseball import schedule_and_record

CACHE_DIR = "cached_schedules"
EXPIRATION_HOURS = 6
LOG_FILE = os.path.join(CACHE_DIR, "schedule_fetch_log.txt")


def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")


def fetch_schedule_by_date(date, force_refresh=False):
    date_str = date.strftime("%Y-%m-%d")
    cache_file = os.path.join(CACHE_DIR, f"{date_str}.json")

    # Check for cache
    if not force_refresh and os.path.exists(cache_file):
        file_age_hours = (time.time() - os.path.getmtime(cache_file)) / 3600
        if file_age_hours < EXPIRATION_HOURS:
            try:
                with open(cache_file, "r") as f:
                    log_event(f"[CACHE] Used fresh cache for {date_str} ({file_age_hours:.2f} hrs old)")
                    return json.load(f)
            except Exception as e:
                log_event(f"[WARN] Failed to load cache for {date_str}: {e}")
        else:
            log_event(f"[STALE] Cache expired for {date_str} ({file_age_hours:.2f} hrs) — re-fetching...")

    # Fetch fresh data
    try:
        games = []
        all_teams = [
            'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
            'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
            'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
        ]

        for team in all_teams:
            schedule = schedule_and_record(date.year, team)
            schedule = schedule[schedule["Date"].dt.date == date.date()]
            for _, row in schedule.iterrows():
                games.append({
                    "team": team,
                    "opponent": row["Opp"],
                    "home": row["Home"],
                    "time": row["Time"],
                    "result": row["Result"]
                })

        # Save cache
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(games, f)

        log_event(f"[FETCH] Fresh schedule saved to cache for {date_str}")
        return games

    except Exception as e:
        log_event(f"[ERROR] Failed to fetch schedule for {date_str}: {e}")
        return []


def preload_upcoming_days(days=2):
    from datetime import timedelta
    today = datetime.now().date()
    for offset in range(days):
        fetch_schedule_by_date(datetime.combine(today + timedelta(days=offset), datetime.min.time()))


# Optional preload when run as script
if __name__ == "__main__":
    preload_upcoming_days()
