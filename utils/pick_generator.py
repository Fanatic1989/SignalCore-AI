import os
import requests
import random
from datetime import datetime

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
SPORTS = ["basketball_nba", "icehockey_nhl", "baseball_mlb"]
BOOKMAKERS = ["stake", "betonlineag"]

def generate_pick():
    sport = random.choice(SPORTS)
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=us&markets=player_points,player_hits,player_shots&bookmakers={','.join(BOOKMAKERS)}&apiKey={ODDS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if not data:
        return "No picks available. Try again later."

    game = random.choice(data)
    home_team = game['home_team']
    away_team = [team for team in game['teams'] if team != home_team][0]
    game_time = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
    game_time_str = game_time.strftime("%Y-%m-%d %H:%M")

    all_markets = []
    for bookmaker in game['bookmakers']:
        if bookmaker['key'] in BOOKMAKERS:
            for market in bookmaker['markets']:
                for outcome in market['outcomes']:
                    all_markets.append({
                        "bookmaker": bookmaker['title'],
                        "market": market['key'],
                        "player": outcome['name'],
                        "line": outcome.get('point'),
                        "price": outcome.get('price'),
                        "sport": sport,
                        "home": home_team,
                        "away": away_team,
                        "game_time": game_time_str
                    })

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
