import os
import uuid
import requests
import schedule
import time
import pytz
from flask import Flask, render_template, request, session, redirect, url_for, abort
from werkzeug.utils import secure_filename
from threading import Thread
from datetime import datetime, timedelta

from utils.pick_generator import generate_pick  # Your pick generator

# Env vars
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change_this")
app.permanent_session_lifetime = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory VIP access tracking (use DB in production)
confirmed_vips = set()

# -------------------
# 📢 VIP Pick Sender
# -------------------
def send_daily_pick():
    pick = generate_pick()
    if not pick:
        print("❌ Error: Pick generation failed.")
        return

    message = f"🔥 SignalCore AI VIP Pick\n\n{pick}"

    try:
        tg = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
        print("Telegram:", tg.status_code)
    except Exception as e:
        print("Telegram error:", e)

    try:
        dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("Discord:", dc.status_code)
    except Exception as e:
        print("Discord error:", e)

# -------------------
# ⏰ Scheduler Setup
# -------------------
def run_scheduler():
    tz = pytz.timezone("America/Puerto_Rico")
    print(f"[{datetime.now(tz)}] Scheduler started.")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

# -------------------
# 🌐 Routes
# -------------------

@app.route('/')
def root_redirect():
    # 🔁 Auto-generate order for new users
    if 'order_id' not in session:
        return redirect(url_for('generate_order'))
    return redirect(url_for('vip_payment'))

@app.route('/vip')
def vip_payment():
    order_id = session.get('order_id')
    is_vip = order_id in confirmed_vips
    return render_template("vip_payment.html", is_vip=is_vip, order_id=order_id)

@app.route('/generate-order')
def generate_order():
    session['order_id'] = str(uuid.uuid4())
    return redirect(url_for('vip_payment'))

@app.route('/submit-proof', methods=['GET', 'POST'])
def submit_proof():
    if request.method == 'POST':
        txid = request.form.get('txid')
        screenshot = request.files.get('screenshot')
        print("🧾 Manual proof submitted:", txid)

        if screenshot and screenshot.filename:
            filename = secure_filename(screenshot.filename)
            screenshot.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("Saved:", filename)
        return "✅ We received your proof. You’ll be verified soon."
    return render_template("submit_proof.html")

@app.route('/ipn', methods=['POST'])
def nowpayments_webhook():
    try:
        data = request.json
        print("🔔 Webhook received:", data)

        if data.get("payment_status") == "finished":
            order_id = data.get("order_id")
            if order_id:
                confirmed_vips.add(order_id)
                print(f"✅ VIP access granted for order {order_id}")
                return "OK", 200

        return "Ignored", 200
    except Exception as e:
        print("❌ Webhook error:", str(e))
        abort(400)

@app.route('/ping')
def ping():
    return "pong"

# -------------------
# 🚀 Start App
# -------------------
def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    run_scheduler()
