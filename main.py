import os
import requests
import schedule
import time
from flask import Flask, render_template, request
from threading import Thread
from datetime import datetime
from werkzeug.utils import secure_filename
import pytz

from utils.pick_generator import generate_pick  # ✅ Your generator

# ENV variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Setup Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------
# 📢 Pick Sender Logic
# ---------------------
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

# ---------------------
# 🌐 Web Routes
# ---------------------
@app.route('/')
@app.route('/vip')
def vip_payment():
    return render_template('vip_payment.html')

@app.route('/submit-proof', methods=['GET', 'POST'])
def submit_proof():
    if request.method == 'POST':
        txid = request.form.get('txid')
        screenshot = request.files.get('screenshot')
        print("🧾 Proof Submitted")
        print("TXID:", txid)
        if screenshot:
            filename = secure_filename(screenshot.filename)
            screenshot.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("Saved screenshot:", filename)
        return "✅ Your proof has been received and is under review."
    return render_template('submit_proof.html')

@app.route('/ping')
def ping():
    return "pong"

# ---------------------
# 🔁 Scheduler
# ---------------------
def run_scheduler():
    ast = pytz.timezone("America/Puerto_Rico")
    print(f"[{datetime.now(ast).strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# ---------------------
# 🚀 Run Everything
# ---------------------
if __name__ == '__main__':
    Thread(target=keep_alive).start()
    run_scheduler()
