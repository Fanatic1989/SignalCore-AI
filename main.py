import os
import requests
import schedule
import time
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz

from utils.pick_generator import generate_pick  # ✅ your pick code
# from sheet_logger import log_to_sheet  # Optional logging

# ✅ Load tokens from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

app = Flask(__name__)

# 🧠 Core pick logic
def send_daily_pick():
    pick = generate_pick()

    message = f"🔥 SignalCore AI VIP Pick\n\n{pick}"

    # Telegram
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    tg = requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})
    print("Telegram:", tg.status_code, tg.text)

    # Discord
    dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
    print("Discord:", dc.status_code, dc.text)

    # Optional: log_to_sheet(pick)

# 🌐 Ping and Flask UI
@app.route('/')
def home():
    return "✅ SignalCore AI is running 24/7."

@app.route('/ping')
def ping():
    return "pong"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ⏰ Schedule 3 drops: 12PM, 3PM, 6PM (AST/GMT-4)
def run_scheduler():
    ast = pytz.timezone("America/Puerto_Rico")
    print(f"[{datetime.now(ast).strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == '__main__':
    keep_alive()
    run_scheduler()
