from datetime import datetime
import requests
import pytz
import pandas as pd
import streamlit as st
import logging

# Set Streamlit logging to debug level
logging.getLogger('streamlit').setLevel(logging.DEBUG)

# Global cache for storing player stats
stats_cache = {}
batter_stats_cache = {}

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

# --- Get season batting stats for a given batter ID ---
def get_batting_stats(player_id, season):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}&group=batting"
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
                "contactPitches": stat.get("contactPitches", 0),
            }
    return None

# --- Calculate advanced batting metrics from raw MLB API stats ---
def calculate_batter_advanced_metrics(stats):
    try:
        strikeouts = stats.get("strikeOuts", 0)
        batters_faced = stats.get("battersFaced", 0)
        two_strike_counts = stats.get("twoStrikeCounts", 0)

        # Debugging the calculation process
        st.write(f"Calculating Advanced Batter Metrics: Strikeouts: {strikeouts}, Batters Faced: {batters_faced}, Two Strike Counts: {two_strike_counts}")

        # K% Calculation: Strikeouts / Batters faced
        k_rate = (
            (strikeouts / batters_faced) * 100
            if batters_faced > 0 else 0
        )

        # PutAway% Calculation: Strikeouts / Two Strike Counts
        putaway_rate = (
            (strikeouts / two_strike_counts) * 100
            if two_strike_counts > 0 else 0
        )

        return {
            "BA": stats.get("BA", "N/A"),
            "SLG": stats.get("SLG", "N/A"),
            "wOBA": stats.get("wOBA", "N/A"),
            "K%": round(k_rate, 2) if k_rate is not None else "N/A",
            "PutAway%": round(putaway_rate, 2) if putaway_rate is not None else "N/A"
        }
    except (TypeError, ZeroDivisionError, KeyError) as e:
        st.write(f"[ERROR] Failed to calculate batter metrics: {e}")
        return {
            "BA": "N/A",
            "SLG": "N/A",
            "wOBA": "N/A",
            "K%": "N/A",
            "PutAway%": "N/A"
        }

# --- Combine name + advanced batter metric lookup ---
def get_batter_advanced_metrics_by_name(full_name, season=None):
    if full_name in batter_stats_cache:  # Use cached data if available
        return batter_stats_cache[full_name]
    
    try:
        first, last = full_name.strip().split(" ", 1)
        player_id = get_player_id(first, last)
        if not player_id:
            return {}

        if not season:
            season = datetime.now().year

        raw_stats = get_batting_stats(player_id, season)
        if not raw_stats:
            return {}

        advanced_metrics = calculate_batter_advanced_metrics(raw_stats)
        batter_stats_cache[full_name] = advanced_metrics  # Cache the results
        return advanced_metrics
    except Exception as e:
        print(f"[ERROR] Failed to fetch batter advanced metrics for {full_name}: {e}")
        return {}

# --- Fetch the lineups for a given game ---
def get_lineups_for_game(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        teams = data["gameData"]["teams"]
        
        home_team = teams["home"]["team"]["name"]
        away_team = teams["away"]["team"]["name"]
        
        home_lineup = [player["person"]["fullName"] for player in data["liveData"]["linescore"]["home"]["battingOrder"]]
        away_lineup = [player["person"]["fullName"] for player in data["liveData"]["linescore"]["away"]["battingOrder"]]
        
        return home_team, away_team, home_lineup, away_lineup
    return None, None, [], []

# --- Fetch and calculate batter metrics for the lineups ---
def calculate_lineup_metrics(game_pk, season=None):
    home_team, away_team, home_lineup, away_lineup = get_lineups_for_game(game_pk)
    
    home_metrics = {player: get_batter_advanced_metrics_by_name(player, season) for player in home_lineup}
    away_metrics = {player: get_batter_advanced_metrics_by_name(player, season) for player in away_lineup}
    
    return home_team, away_team, home_lineup, away_lineup, home_metrics, away_metrics

# --- Main function to display dynamic lineups and their batter metrics ---
def display_game_lineups_and_metrics(game_pk, season=None):
    home_team, away_team, home_lineup, away_lineup, home_metrics, away_metrics = calculate_lineup_metrics(game_pk, season)
    
    st.title(f"Game: {away_team} vs {home_team}")
    
    st.subheader("Home Team Lineup and Stats:")
    for batter, metrics in home_metrics.items():
        st.write(f"{batter}: {metrics}")
        
    st.subheader("Away Team Lineup and Stats:")
    for batter, metrics in away_metrics.items():
        st.write(f"{batter}: {metrics}")

# --- Get Game State ---
def get_game_state(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    response = requests.get(url)
    
    if not response.ok:
        return None

    data = response.json()

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
# utils/mlb_api.py

def get_pitcher_advanced_metrics_by_name(full_name, season=None):
    try:
        first, last = full_name.strip().split(" ", 1)
        player_id = get_player_id(first, last)
        if not player_id:
            return {}

        if not season:
            season = datetime.now().year

        raw_stats = get_pitcher_advanced_metrics_by_name(player_name, season)
        if not raw_stats:
            return {}

        return calculate_advanced_metrics(raw_stats)
    except Exception as e:
        print(f"[ERROR] Failed to fetch advanced metrics for {full_name}: {e}")
        return {}

# --- Calculate advanced pitching metrics from raw MLB API stats ---
def calculate_advanced_metrics(stats):
    try:
        total_pitches = stats.get("numberOfPitches", 0)
        swinging_strikes = stats.get("swinging_strikes", 0)
        strikeouts = stats.get("strikeOuts", 0)
        batters_faced = stats.get("battersFaced", 0)
        two_strike_counts = stats.get("twoStrikeCounts", 0)

        # Whiff% Calculation
        whiff_rate = (swinging_strikes / total_pitches * 100) if total_pitches > 0 else 0

        # K% Calculation
        k_rate = (strikeouts / batters_faced * 100) if batters_faced > 0 else 0

        # PutAway% Calculation
        putaway_rate = (strikeouts / two_strike_counts * 100) if two_strike_counts > 0 else 0

        return {
            "BA": stats.get("BA", "N/A"),
            "SLG": stats.get("SLG", "N/A"),
            "wOBA": stats.get("wOBA", "N/A"),
            "Whiff%": round(whiff_rate, 2),
            "K%": round(k_rate, 2),
            "PutAway%": round(putaway_rate, 2)
        }
    except Exception as e:
        print(f"[ERROR] Failed to calculate pitching metrics: {e}")
        return {}

# --- Fetch pitcher advanced metrics by name ---
def get_pitcher_advanced_metrics_by_name(full_name, season=None):
    try:
        first, last = full_name.strip().split(" ", 1)
        player_id = get_player_id(first, last)
        if not player_id:
            return {}

        if not season:
            season = datetime.now().year

        raw_stats = get_pitcher_advanced_metrics_by_name(player_name, season)
        if not raw_stats:
            return {}

        return calculate_advanced_metrics(raw_stats)
    except Exception as e:
        print(f"[ERROR] Failed to fetch advanced metrics for {full_name}: {e}")
        return {}

# --- Get probable pitchers for a specific date ---
def get_probable_pitchers_for_date(date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch probable pitchers for {date_str}")
        return {}
    
    data = response.json()

    probable_pitchers = {}
    
    # Iterate over games to get the probable pitchers
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            home_team = game["teams"]["home"]["team"]["name"]
            away_team = game["teams"]["away"]["team"]["name"]
            
            # Try to get the probable pitchers, or fallback to 'Not Announced'
            home_pitcher = game["teams"]["home"].get("probablePitcher", {}).get("fullName", "Not Announced")
            away_pitcher = game["teams"]["away"].get("probablePitcher", {}).get("fullName", "Not Announced")

            # Create a key for this matchup
            key = f"{away_team} @ {home_team}"
            
            # Store the probable pitchers in the dictionary
            probable_pitchers[key] = {
                "home_pitcher": home_pitcher,
                "away_pitcher": away_pitcher
            }

    return probable_pitchers

def get_pitcher_arsenal_from_api(pitcher_name, season=None):
    """
    Pulls per-pitch-type performance data (Whiff%, PutAway%, etc.) for a given pitcher.
    We will log the data here to check if we are getting the expected response.
    """
    if not season:
        season = datetime.now().strftime("%Y-%m-%d")

    # Log the pitcher name and season to ensure correct values
    st.write(f"Fetching arsenal for pitcher: {pitcher_name}, season: {season}")

    # We use a mock API for demonstration, replace this with the actual API logic
    try:
        # Example: API URL to get detailed pitch arsenal for the pitcher
        url = f"https://api.example.com/arsenal?pitcher={pitcher_name}&season={season}"
        response = requests.get(url)
        
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            st.write(f"API Response: {data}")  # Log the raw data for inspection

            # Assuming the API returns data in the following format:
            # [{"pitch_type": "4-Seam Fastball", "PA": 50, "BA": 0.220, "SLG": 0.350, ...}, {...}, ...]
            if data:
                df = pd.DataFrame(data)
                return df
            else:
                st.warning("No data found for this pitcher in the API response.")
                return pd.DataFrame()  # Return empty DataFrame
        else:
            st.error(f"Failed to fetch pitch arsenal for {pitcher_name}. Status code: {response.status_code}")
            return pd.DataFrame()  # Return empty DataFrame if API fails

    except Exception as e:
        st.error(f"[ERROR] Error fetching pitch arsenal for {pitcher_name}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# --- Fetch the arsenal (pitch types and their performance) for a pitcher ---
def get_pitcher_arsenal_from_api(pitcher_name, season=None):
    """
    Pulls per-pitch-type performance data (Whiff%, PutAway%, etc.) for a given pitcher.
    """
    if not season:
        season = datetime.now().strftime("%Y-%m-%d")

    # Log the pitcher name and season to ensure correct values
    st.write(f"Fetching arsenal for pitcher: {pitcher_name}, season: {season}")

    try:
        # Example: API URL to get detailed pitch arsenal for the pitcher
        url = f"https://api.example.com/arsenal?pitcher={pitcher_name}&season={season}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            st.write(f"API Response: {data}")  # Log the raw data for inspection

            # Assuming the API returns data in the following format:
            # [{"pitch_type": "4-Seam Fastball", "PA": 50, "BA": 0.220, "SLG": 0.350, ...}, {...}, ...]
            if data:
                df = pd.DataFrame(data)
                return df
            else:
                st.warning("No data found for this pitcher in the API response.")
                return pd.DataFrame()  # Return empty DataFrame
        else:
            st.error(f"Failed to fetch pitch arsenal for {pitcher_name}. Status code: {response.status_code}")
            return pd.DataFrame()  # Return empty DataFrame if API fails

    except Exception as e:
        st.error(f"[ERROR] Error fetching pitch arsenal for {pitcher_name}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

