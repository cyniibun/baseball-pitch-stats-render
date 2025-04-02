import requests

def get_game_lineups(game_date: str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={game_date}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {}

    games = resp.json().get("dates", [])[0].get("games", [])
    lineup_data = {}
    for game in games:
        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]
        game_pk = game["gamePk"]
        lineup_data[f"{away} @ {home}"] = {
            "gamePk": game_pk,
            "home": home,
            "away": away
        }
    return lineup_data

def get_lineup_for_game(game_pk: int):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None, None

    data = resp.json()
    home_players = data['teams']['home']['players']
    away_players = data['teams']['away']['players']

    def extract_lineup(players):
        lineup = []
        for pid, player in players.items():
            try:
                pos = player['position']['abbreviation']
                if pos in ["P", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", "C"]:
                    lineup.append(f"{player['person']['fullName']} - {pos}")
            except:
                continue
        return lineup

    return extract_lineup(away_players), extract_lineup(home_players)
