# utils/style_utils.py

def get_batter_red_green_shade(percent, high_is_bad=True):
    try:
        val = float(percent)
    except:
        return "color: white;"
    capped = min(val, 50)
    alpha = capped / 50
    if high_is_bad:
        return f"background-color: rgba(255, 0, 0, {alpha:.2f}); color: white;"  # High bad = red
    else:
        green_alpha = 1 - alpha
        return f"background-color: rgba(0, 153, 0, {green_alpha:.2f}); color: white;"  # Low good = green

def get_batter_blue_red_shade(val):
    try:
        val = float(val)
    except:
        return "color: white;"
    capped = min(val, 1.0)
    alpha = capped
    return (
        f"background-color: rgba(0, 102, 255, {alpha:.2f}); color: white;" if val > 0.3
        else f"background-color: rgba(255, 0, 0, {1 - alpha:.2f}); color: white;"
    )

def get_pitcher_red_green_shade(percent, high_is_good=True):
    try:
        val = float(percent)
    except:
        return "color: white;"
    capped = min(val, 50)
    alpha = capped / 50
    if high_is_good:
        return f"background-color: rgba(0, 153, 0, {alpha:.2f}); color: white;"  # High good = green
    else:
        red_alpha = 1 - alpha
        return f"background-color: rgba(255, 0, 0, {red_alpha:.2f}); color: white;"  # Low bad = red

def get_pitcher_blue_red_shade(val):
    try:
        val = float(val)
    except:
        return "color: white;"
    capped = min(val, 1.0)
    alpha = capped
    return (
        f"background-color: rgba(255, 0, 0, {alpha:.2f}); color: white;" if val > 0.3
        else f"background-color: rgba(0, 102, 255, {1 - alpha:.2f}); color: white;"
    )

def get_delta_red_blue(val):
    try:
        val = float(val)
    except:
        return "color: white;"
    if val > 0:
        alpha = min(val, 50) / 50
        return f"background-color: rgba(0, 102, 255, {alpha:.2f}); color: white;"
    elif val < 0:
        alpha = min(abs(val), 50) / 50
        return f"background-color: rgba(255, 0, 0, {alpha:.2f}); color: white;"
    else:
        return "color: white;"

def get_red_shade(percent_str):
    try:
        value = float(percent_str.strip('%')) if isinstance(percent_str, str) else float(percent_str)
    except:
        return "color: white;"  # Fallback

    capped = min(value, 50)
    alpha = capped / 50  # Normalize to 0.0–1.0 range

    return f"background-color: rgba(255, 0, 0, {alpha:.2f}); color: white;"
