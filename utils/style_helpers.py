import pandas as pd
from .style_utils import (
    get_batter_red_green_shade,
    get_batter_blue_red_shade,
    get_pitcher_red_green_shade,
    get_pitcher_blue_red_shade,
    get_delta_red_blue
)

def style_pitcher_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return df.style.applymap(get_pitcher_blue_red_shade, subset=["BA", "SLG", "wOBA"]) \
                   .applymap(lambda x: get_pitcher_red_green_shade(x, high_is_good=True), subset=["K%", "Whiff%", "PutAway%"])

def style_batter_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return df.style.applymap(lambda x: get_batter_red_green_shade(x, high_is_bad=True), subset=["K%", "Whiff%", "PutAway%"]) \
                   .applymap(get_batter_blue_red_shade, subset=["BA", "SLG", "wOBA"])

def style_delta_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    delta_cols = [col for col in df.columns if "Δ" in col]
    return df.style.applymap(get_delta_red_blue, subset=delta_cols)
