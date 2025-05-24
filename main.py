import os
import requests
import schedule
import time
from dotenv import load_dotenv
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

from utils.pick_generator import generate_pick
from utils.vip_rotation import get_vip_picks
from utils.logger import log_result
from utils.sheet_logger import log_to_sheet

# Load .env values
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SignalCore AI™ is running 24/7."

@app.route('/ping')
def ping():
    return "pong"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

def send_daily_pick():
    pick = generate_pick()
    vip = get_vip_picks()
    message = f"🔥 SignalCore AI Live Pick\n\n{pick}\n\n👑 VIP Picks:\n" + "\n".join(vip)

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    tg = requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})
    print("Telegram:", tg.text)

    dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
    print("Discord:", dc.status_code, dc.text)

    log_result(message)
    log_to_sheet(pick, vip)

def run_scheduler():
    ast = pytz.timezone("America/Puerto_Rico")
    now = datetime.now(ast)
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scheduler running (GMT-4)")
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    keep_alive()
    run_scheduler()
