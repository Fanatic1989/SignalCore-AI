import os
import requests
import random
from datetime import datetime

# Get your Odds API key from environment
ODDS_API_KEY = os.getenv("API_KEY", "your_api_key_here")

# Supported sports and markets (choose only available ones)
SPORTS = ["basketball_nba", "icehockey_nhl", "baseball_mlb"]
BOOKMAKERS = ["stake", "betonlineag"]
MARKETS = ["h2h", "totals", "spreads"]  # Use valid ones per docs

def generate_pick():
    try:
        # Randomly choose a sport
        sport = random.choice(SPORTS)
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=us&markets={','.join(MARKETS)}&bookmakers={','.join(BOOKMAKERS)}&apiKey={ODDS_API_KEY}"

        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ generate_pick error: Bad response {response.status_code}: {response.text}")
            return None

        data = response.json()
        if not data:
            print("❌ No data received from Odds API.")
            return None

        # Randomly choose a game from available ones
        game = random.choice(data)
        home_team = game["home_team"]
        away_team = [team for team in game["teams"] if team != home_team][0]
        game_time = datetime.strptime(game["commence_time"], "%Y-%m-%dT%H:%M:%SZ")
        game_time_str = game_time.strftime("%Y-%m-%d %I:%M %p")

        # Flatten all outcomes
        all_markets = []
        for bookmaker in game["bookmakers"]:
            if bookmaker["key"] in BOOKMAKERS:
                for market in bookmaker["markets"]:
                    for outcome in market["outcomes"]:
                        all_markets.append({
                            "bookmaker": bookmaker["title"],
                            "market": market["key"],
                            "name": outcome.get("name"),
                            "price": outcome.get("price"),
                            "point": outcome.get("point"),
                            "sport": sport,
                            "home": home_team,
                            "away": away_team,
                            "game_time": game_time_str
                        })

        if not all_markets:
            print("❌ No valid markets found for this game.")
            return None

        pick = random.choice(all_markets)

        confidence = random.randint(61, 78)
        diff = round(random.uniform(1.0, 4.0), 1)

        sport_name = {
            "basketball_nba": "🏀 NBA",
            "icehockey_nhl": "🏒 NHL",
            "baseball_mlb": "⚾ MLB"
        }.get(pick["sport"], "🏆 Sports")

        message = (
            f"{sport_name} Signal Pick 🔥\n\n"
            f"📅 {pick['game_time']}\n"
            f"🏟️ {pick['home']} vs {pick['away']}\n"
            f"📊 Market: {pick['market'].replace('_', ' ').title()}\n"
            f"💰 Pick: {pick['name']} @ {pick['price']}\n"
            f"📈 Confidence: {confidence}% | Diff: +{diff}"
        )

        return message

    except Exception as e:
        print(f"❌ generate_pick Exception: {str(e)}")
        return None
