# file: utils/stat_utils.py

from pybaseball import playerid_lookup, statcast_pitcher
from datetime import datetime
from functools import lru_cache
import pandas as pd
import requests

@lru_cache(maxsize=32)
def get_player_id(name):
    try:
        first, last = name.strip().split(" ", 1)
        result = playerid_lookup(last, first)
        return int(result.iloc[0]['key_mlbam']) if not result.empty else None
    except:
        return None

def get_pitcher_stats(name, start_date="2024-04-01", end_date=None):
    pid = get_player_id(name)
    if not pid:
        return pd.DataFrame()

    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = statcast_pitcher(start_date, end_date, pid)

    if df.empty:
        return pd.DataFrame()

    df = df[df["pitch_type"].notna()]
    grouped = df.groupby("pitch_type")

    summary = grouped.agg(
        PA=('batter', 'count'),
        BA=('estimated_ba_using_speedangle', 'mean'),
        SLG=('estimated_slg_using_speedangle', 'mean'),
        wOBA=('estimated_woba_using_speedangle', 'mean'),
        K_rate=('events', lambda x: (x == 'strikeout').sum() / len(x) * 100),
        Whiff_rate=('description', lambda x: x.str.contains("swinging_strike").sum() / len(x) * 100),
        PutAway_rate=('description', lambda x: (x.str.contains("strikeout|swinging_strike")).sum() / len(x) * 100)
    )

    return summary.rename(columns={
        'K_rate': 'K%',
        'Whiff_rate': 'Whiff%',
        'PutAway_rate': 'PutAway%'
    }).round(2)

def get_advanced_pitching_metrics(pitcher_name: str):
    """Fetch basic advanced metrics for a given pitcher using MLB API"""
    try:
        # Use MLB stats API to get player search
        search_url = f"https://statsapi.mlb.com/api/v1/people/search?names={pitcher_name}"
        search_resp = requests.get(search_url).json()
        results = search_resp.get("people", [])
        if not results:
            return pd.DataFrame()

        player_id = results[0]["id"]

        # Use player_id to get season stats
        stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&group=pitching"
        stats_resp = requests.get(stats_url).json()
        splits = stats_resp.get("stats", [])[0].get("splits", [])
        if not splits:
            return pd.DataFrame()

        stats = splits[0].get("stat", {})

        data = {
            "BA": [stats.get("avg", "N/A")],
            "SLG": [stats.get("slg", "N/A")],
            "wOBA": [stats.get("obp", "N/A")],  # substitute for now
            "Whiff%": ["N/A"],  # Not in this endpoint
            "K%": [stats.get("strikeOuts", "N/A")],
            "PutAway%": ["N/A"],  # Requires deeper analysis
        }

        return pd.DataFrame(data)
    except Exception as e:
        print(f"[ERROR] Failed to fetch advanced metrics: {e}")
        return pd.DataFrame()
