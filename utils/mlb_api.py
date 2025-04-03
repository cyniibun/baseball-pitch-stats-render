from datetime import datetime
import requests
import pytz
import pandas as pd

# --- Fetch today's MLB schedule ---
def fetch_today_schedule():
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).strftime("%Y-%m-%d")
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

# --- Get player ID using the Stats API ---
def get_player_id(first_name, last_name):
    search_url = f"https://statsapi.mlb.com/api/v1/people/search?names={first_name}%20{last_name}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("people"):
            return data["people"][0]["id"]
    return None

# --- Get season pitching stats for a given pitcher ID ---
def get_pitching_stats(player_id, season):
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

# --- Calculate advanced pitching metrics from raw MLB API stats ---
def calculate_advanced_metrics(stats):
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

# --- Combine name + advanced metric lookup ---
def get_pitcher_advanced_metrics_by_name(full_name, season=None):
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
        print(f"[ERROR] Failed to fetch advanced metrics for {full_name}: {e}")
        return {}

# --- Placeholder for batter putaway by pitch type using MLB API ---
def get_batter_putaway_by_pitch(batter_name):
    # This is where you'd implement fetching detailed PITCHf/x data for the batter.
    # It would require gathering all swings with 2 strikes and counting outs per pitch type.
    # Placeholder returns static mock structure:
    return {
        "4-Seam Fastball": "23.5%",
        "Slider": "31.8%",
        "Changeup": "19.2%"
    }
def get_pitcher_arsenal_from_api(player_id, season=None):
    """
    Pulls per-pitch-type performance data (PutAway%, Whiff%, etc.) for a given pitcher.
    NOTE: This is a placeholder; MLB API doesn't expose detailed per-pitch-type statcast data here.
    """
    # Normally you'd hit an endpoint like Baseball Savant’s but that's not available.
    # You can replace this mock structure with scraped or cached data if needed.
    pitch_data = {
        "4-Seam Fastball": {"PA": 50, "PutAway%": 28.4},
        "Slider": {"PA": 35, "PutAway%": 36.7},
        "Changeup": {"PA": 20, "PutAway%": 22.1},
    }

    df = pd.DataFrame(pitch_data).T.reset_index().rename(columns={"index": "pitch_type"})
    return df

def get_probable_pitchers_for_date(date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    response = requests.get(url)
    data = response.json()

    probable_pitchers = {}
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            home_team = game["teams"]["home"]["team"]["name"]
            away_team = game["teams"]["away"]["team"]["name"]
            home_pitcher = game["teams"]["home"].get("probablePitcher", {}).get("fullName", "Not Announced")
            away_pitcher = game["teams"]["away"].get("probablePitcher", {}).get("fullName", "Not Announced")

            key = f"{away_team} @ {home_team}"
            probable_pitchers[key] = {
                "home_pitcher": home_pitcher,
                "away_pitcher": away_pitcher
            }

    return probable_pitchers
def get_game_state(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    resp = requests.get(url)
    if not resp.ok:
        return None

    data = resp.json()

    try:
        inning = data["liveData"]["linescore"]["currentInning"]
        half = data["liveData"]["linescore"]["inningState"]
        count_data = data["liveData"]["plays"]["currentPlay"]["count"]
        count = f"{count_data.get('balls', 0)}-{count_data.get('strikes', 0)}"
        outs = count_data.get("outs", 0)

        bases = []
        runners = data["liveData"]["plays"]["currentPlay"].get("runners", [])
        for r in runners:
            base = r.get("movement", {}).get("end", "")
            if base == "1B":
                bases.append("1B")
            elif base == "2B":
                bases.append("2B")
            elif base == "3B":
                bases.append("3B")

        linescore = {
            "away": {
                "runs": data["liveData"]["linescore"]["teams"]["away"]["runs"],
                "hits": data["liveData"]["linescore"]["teams"]["away"]["hits"],
                "xba": ".000"  # Placeholder for xBA
            },
            "home": {
                "runs": data["liveData"]["linescore"]["teams"]["home"]["runs"],
                "hits": data["liveData"]["linescore"]["teams"]["home"]["hits"],
                "xba": ".000"
            }
        }

        return {
            "inning": inning,
            "half": half,
            "count": count,
            "outs": outs,
            "bases": bases,
            "linescore": linescore
        }

    except Exception as e:
        print(f"[ERROR] Failed to parse game state: {e}")
        return None

def get_all_team_player_ids():
    """
    Returns a dictionary of all MLB teams and their players with IDs and positions:
    {
        "ATL": [{"id": 123, "name": "John Smith", "position": "P"}, ...],
        ...
    }
    """
    team_ids = [
        109, 110, 111, 112, 113, 114, 115, 116, 117, 118,
        119, 120, 121, 133, 134, 135, 136, 137, 138, 139,
        140, 141, 142, 143, 144, 145, 146, 147, 158, 159
    ]

    all_players = {}

    for team_id in team_ids:
        url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
        try:
            res = requests.get(url)
            data = res.json()

            players = []
            for entry in data.get("roster", []):
                players.append({
                    "id": entry["person"]["id"],
                    "name": entry["person"]["fullName"],
                    "position": entry["position"]["abbreviation"]
                })

            all_players[team_id] = players
        except Exception as e:
            print(f"[Error] Team ID {team_id}: {e}")
            all_players[team_id] = []

    return all_players