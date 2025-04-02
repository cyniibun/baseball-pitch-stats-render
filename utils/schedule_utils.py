def get_today_schedule():
    import traceback  # Add for detailed logging
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).date()

    all_teams = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CWS', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
    ]

    games_today = []

    for team in all_teams:
        try:
            print(f"[DEBUG] Fetching schedule for {team}...")
            schedule = schedule_and_record(datetime.now().year, team)
            schedule['Date'] = pd.to_datetime(schedule['Date'])  # Ensure datetime type
            todays_games = schedule[schedule['Date'].dt.date == today]
            for _, row in todays_games.iterrows():
                games_today.append({
                    'team': team,
                    'opponent': row['Opp'],
                    'home': row['Home'],
                    'time': row['Time'],
                    'result': row['Result'],
                })
        except Exception as e:
            print(f"[ERROR] Failed to fetch for {team}: {e}")
            traceback.print_exc()
            continue

    # Deduplicate
    seen = set()
    unique_games = []
    for game in games_today:
        matchup_key = tuple(sorted([game['team'], game['opponent']]))
        if matchup_key not in seen:
            seen.add(matchup_key)
            unique_games.append(game)

    print(f"[DEBUG] Total unique games: {len(unique_games)}")
    if unique_games:
        print(f"[DEBUG] Sample game: {unique_games[0]}")

    return unique_games
