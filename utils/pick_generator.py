import random
from datetime import date

def generate_pick():
    # Dummy data until scrapers/API integration complete
    players = ["LeBron James", "Stephen Curry", "Nikola Jokic"]
    teams = ["Lakers", "Warriors", "Nuggets"]
    stat_types = ["Points", "Rebounds", "Assists"]

    player = random.choice(players)
    team = teams[players.index(player)]
    stat = random.choice(stat_types)

    value_stake = round(random.uniform(22, 35), 1)
    value_betonline = round(value_stake - random.uniform(1.0, 3.0), 1)
    ai_proj = round(value_stake + random.uniform(1.5, 4.0), 1)
    confidence = random.randint(68, 83)
    diff = round(ai_proj - value_stake, 1)

    return f"""🏀 NBA  
📆 {date.today().strftime('%B %d, %Y')}  
📊 {player} – {team}  
🎯 Stake: Over {value_stake} {stat}  
🎯 BetOnline: Under {value_betonline} {stat}  

📉 Book Average: {value_stake - 2.2}  
🧠 AI Projected: {ai_proj}  
📈 Confidence: {confidence}% | Diff: +{diff}"""
