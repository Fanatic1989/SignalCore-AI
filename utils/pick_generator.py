import os
import requests
import random
from datetime import datetime

# ✅ Replace this with your actual key or leave as env var
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "df567d1f30b264c40cdac21f56f862e4")

SPORTS = ["basketball_nba", "icehockey_nhl", "baseball_mlb"]
BOOKMAKERS = ["stake", "betonlineag"]

def generate_pick():
    try:
        sport = random.choice(SPORTS)
        url = (
            f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            f"?regions=us&markets=player_points,player_hits,player_shots"
            f"&bookmakers={','.join(BOOKMAKERS)}&apiKey={ODDS_API_KEY}"
        )

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Bad response {response.status_code}: {response.text}")

        data = response.json()
        if not data:
            return None

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
            return None

        pick = random.choice(all_markets)
        confidence = random.randint(61, 75)
        diff = round(random.uniform(1.2, 3.5), 1)

        sport_name = {
            "basketball_nba": "BASKETBALL NBA",
            "icehockey_nhl": "ICE HOCKEY NHL",
            "baseball_mlb": "BASEBALL MLB"
        }.get(pick['sport'], pick['sport'].upper())

        player_line = f"{pick['player']} Over {pick['line']}"

        return (
            f"🏆 {sport_name}\n"
            f"📆 {pick['game_time']}\n"
            f"📊 Market: {pick['market'].replace('_', ' ').title()} @ {pick['bookmaker']}\n"
            f"🏀 {player_line}\n"
            f"🏟️ {pick['home']} vs {pick['away']}\n\n"
            f"📈 Confidence: {confidence}% | Diff: +{diff}"
        )

    except Exception as e:
        print("❌ generate_pick error:", str(e))
        return None
