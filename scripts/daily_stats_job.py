# -*- coding: utf-8 -*-

import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime
from utils.stat_utils import get_batter_metrics_by_pitch, get_pitcher_arsenal_stats
from utils.team_utils import get_all_mlb_players
from pathlib import Path

# Output directory
if os.environ.get("RENDER"):
    DATA_DIR = Path("/data/daily_stats")
else:
    DATA_DIR = Path("data/daily_stats")

DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_stats_to_csv(data, filename):
    file_path = DATA_DIR / filename
    data.to_csv(file_path, index=False)
    print(f"[✓] Saved: {file_path}")

def run_daily_stat_pull():
    print(f"📊 Running daily stat pull @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- Get all MLB player IDs ---
    all_players = get_all_mlb_players()  # Returns Dict w/ 'batters' and 'pitchers'

    # --- Pull Batter Stats by Pitch Type ---
    batter_data = []
    for batter_id in all_players["batters"]:
        batter_stats = get_batter_metrics_by_pitch(batter_id)
        if not batter_stats.empty:
            batter_stats["batter_id"] = batter_id
            batter_data.append(batter_stats)

    df_batters = pd.concat(batter_data, ignore_index=True)
    save_stats_to_csv(df_batters, f"batters_by_pitch_{datetime.today().date()}.csv")

    # --- Pull Pitcher Arsenal Stats ---
    pitcher_data = []
    for pitcher_id in all_players["pitchers"]:
        pitcher_stats = get_pitcher_arsenal_stats(pitcher_id)
        if not pitcher_stats.empty:
            pitcher_stats["pitcher_id"] = pitcher_id
            pitcher_data.append(pitcher_stats)

    df_pitchers = pd.concat(pitcher_data, ignore_index=True)
    save_stats_to_csv(df_pitchers, f"pitchers_by_pitch_{datetime.today().date()}.csv")

    print("✅ Stat pull complete.")

if __name__ == "__main__":
    run_daily_stat_pull()
