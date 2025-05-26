import os
import requests
import schedule
import time
import pytz
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from threading import Thread
from datetime import datetime, timedelta

from utils.pick_generator import generate_pick  # ✅ Your pick generator

# ENV variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "this_should_be_secret")
app.permanent_session_lifetime = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------
# 📢 SEND PICK FUNCTION
# ---------------------
def send_daily_pick():
    pick = generate_pick()
    if not pick:
        print("❌ Error: Pick generation failed, skipping post.")
        return

    message = f"🔥 SignalCore AI VIP Pick\n\n{pick}"

    try:
        tg = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
        print("Telegram:", tg.status_code, tg.text)
    except Exception as e:
        print("❌ Telegram error:", str(e))

    try:
        dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("Discord:", dc.status_code, dc.text)
    except Exception as e:
        print("❌ Discord error:", str(e))

# ---------------------
# 🌐 WEB ROUTES
# ---------------------
@app.route('/')
@app.route('/vip')
def vip_payment():
    is_vip = session.get('is_vip', False)
    return render_template('vip_payment.html', is_vip=is_vip)

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
        session['is_vip'] = True
        return redirect(url_for('vip_payment'))
    return render_template('submit_proof.html')

@app.route('/ping')
def ping():
    return "pong"

# ---------------------
# ⏱️ SCHEDULER THREAD
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
# 🚀 RUN APP
# ---------------------
if __name__ == '__main__':
    Thread(target=keep_alive).start()
    run_scheduler()
