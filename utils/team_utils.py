from utils.mlb_api import get_all_team_player_ids

def get_all_mlb_players():
    """
    Returns a dict of all current MLB batters and pitchers as:
    {
        "batters": [player_id1, player_id2, ...],
        "pitchers": [player_id1, player_id2, ...]
    }
    """
    all_players = get_all_team_player_ids()  # Make sure this is defined in mlb_api
    batters = []
    pitchers = []

    for team_roster in all_players.values():
        for player in team_roster:
            if player["position"] in {"P", "SP", "RP"}:
                pitchers.append(player["id"])
            else:
                batters.append(player["id"])

    return {
        "batters": list(set(batters)),  # Deduplicated
        "pitchers": list(set(pitchers))
    }
