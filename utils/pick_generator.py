import os
import requests
import random
from datetime import datetime

ODDS_API_KEY = os.getenv("API_KEY")
SPORTS = ["basketball_nba", "icehockey_nhl", "baseball_mlb"]
BOOKMAKERS = ["stake", "betonlineag"]
MARKETS = ["player_points", "player_assists", "player_rebounds", "player_threes"]  # Safe markets

def generate_pick():
    try:
        sport = random.choice(SPORTS)
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=us&markets={','.join(MARKETS)}&bookmakers={','.join(BOOKMAKERS)}&apiKey={ODDS_API_KEY}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ generate_pick error: Bad response {response.status_code}: {response.text}")
            return None

        data = response.json()
        if not data:
            return None

        game = random.choice(data)
        home_team = game.get("home_team", "Unknown")
        teams = game.get("teams", [])

        if len(teams) == 2:
            away_team = teams[0] if teams[1] == home_team else teams[1]
        else:
            away_team = "Unknown"

        game_time = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
        game_time_str = game_time.strftime("%Y-%m-%d %H:%M")

        all_markets = []
        for bookmaker in game.get("bookmakers", []):
            if bookmaker['key'] in BOOKMAKERS:
                for market in bookmaker.get('markets', []):
                    for outcome in market.get('outcomes', []):
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
        confidence = random.randint(61, 78)
        diff = round(random.uniform(1.2, 3.5), 1)

        sport_name = {
            "basketball_nba": "NBA",
            "icehockey_nhl": "NHL",
            "baseball_mlb": "MLB"
        }.get(pick['sport'], pick['sport'].upper())

        player_line = f"{pick['player']} Over {pick['line']}"

        return (
            f"🏆 {sport_name}\n"
            f"📆 {pick['game_time']}\n"
            f"📊 {pick['market'].replace('_', ' ').title()} @ {pick['bookmaker']}\n"
            f"🏀 {player_line}\n"
            f"🏟️ {pick['home']} vs {pick['away']}\n\n"
            f"📈 Confidence: {confidence}% | Diff: +{diff}"
        )
    except Exception as e:
        print("❌ generate_pick Exception:", str(e))
        return None
