# file: utils/stat_utils.py

from pybaseball import playerid_lookup, statcast_pitcher
from datetime import datetime
from functools import lru_cache
import pandas as pd
import requests
from utils.mlb_api import get_pitcher_advanced_metrics_by_name, get_player_id


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

from utils.mlb_api import get_pitcher_advanced_metrics_by_name

def get_advanced_pitching_metrics(pitcher_name: str):
    """Wrapper to return advanced metrics from MLB API."""
    data = get_pitcher_advanced_metrics_by_name(pitcher_name)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame([data])
