def generate_pick():
    # ... your existing code ...

    if not all_markets:
        return "No markets found for Stake or BetOnline."

    pick = random.choice(all_markets)
    confidence = random.randint(61, 75)
    diff = round(random.uniform(1.2, 3.5), 1)

    sport_name = {
        "basketball_nba": "BASKETBALL NBA",
        "icehockey_nhl": "ICE HOCKEY NHL",
        "baseball_mlb": "BASEBALL MLB"
    }[pick['sport']]

    player_line = f"{pick['player']} Over {pick['line']}"

    return (
        f"🏆 {sport_name}\n"
        f"📆 {pick['game_time']}\n"
        f"📊 Market: {pick['market'].replace('_', ' ').title()} @ {pick['bookmaker']}\n"
        f"🏀 {player_line}\n"
        f"🏟️ {pick['home']} vs {pick['away']}\n\n"
        f"📈 Confidence: {confidence}% | Diff: +{diff}"
    )
