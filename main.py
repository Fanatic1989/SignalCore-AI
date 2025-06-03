import os
import uuid
import pytz
import time
import requests
import schedule
from flask import Flask, render_template, request, session, redirect, url_for, abort
from werkzeug.utils import secure_filename
from threading import Thread
from datetime import datetime, timedelta

from utils.pick_generator import generate_pick
from vip_data import load_vips, save_vips

# === 🔐 ENV VARIABLES ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Zariah*1")
TIMEZONE = os.getenv("TIMEZONE", "America/Puerto_Rico")

# === ⚙️ FLASK APP SETUP ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "this_should_be_secret")
app.permanent_session_lifetime = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === 🧠 VIP DB ===
vips = load_vips()

# === 📢 SEND PICK ===
def send_pick(message):
    # Telegram
    try:
        tg = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
        print("📤 Telegram:", tg.status_code, tg.text)
    except Exception as e:
        print("❌ Telegram Error:", str(e))

    # Discord
    try:
        dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("📤 Discord:", dc.status_code, dc.text)
    except Exception as e:
        print("❌ Discord Error:", str(e))

# === 📅 SCHEDULED PICK ===
def send_daily_pick():
    pick = generate_pick()
    if not pick:
        print("❌ Error: Pick generation failed.")
        return

    message = f"🔥 SignalCore AI VIP Pick\n\n{pick}"
    send_pick(message)

# === ⏰ SCHEDULER LOOP ===
def run_scheduler():
    tz = pytz.timezone(TIMEZONE)
    print(f"[{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

# === 🌐 ROUTES ===

@app.route('/')
@app.route('/vip')
def vip_payment():
    order_id = session.get('order_id')
    is_vip = order_id in vips
    return render_template("vip_payment.html", is_vip=is_vip, order_id=order_id)

@app.route('/generate-order')
def generate_order():
    order_id = str(uuid.uuid4())
    session['order_id'] = order_id
    return redirect(url_for('vip_payment'))

@app.route('/ipn', methods=['POST'])
def nowpayments_webhook():
    try:
        data = request.json
        print("🔔 Webhook received:", data)

        if data.get("payment_status") == "finished":
            order_id = data.get("order_id")
            if order_id:
                vips[order_id] = {"expires": (datetime.utcnow() + timedelta(days=7)).isoformat()}
                save_vips(vips)
                print(f"✅ Payment confirmed: {order_id}")
                return "OK", 200
        return "Ignored", 200
    except Exception as e:
        print("❌ Webhook Error:", str(e))
        abort(400)

@app.route('/submit-proof', methods=['GET', 'POST'])
def submit_proof():
    if request.method == 'POST':
        txid = request.form.get('txid')
        screenshot = request.files.get('screenshot')
        print("🧾 Proof Submitted – TXID:", txid)

        if screenshot and screenshot.filename:
            filename = secure_filename(screenshot.filename)
            screenshot.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("📸 Screenshot saved:", filename)

        session['order_id'] = txid
        vips[txid] = {"expires": (datetime.utcnow() + timedelta(days=7)).isoformat()}
        save_vips(vips)
        return redirect(url_for('vip_payment'))

    return render_template("submit_proof.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get("password")
        if password != ADMIN_PASSWORD:
            return "Unauthorized", 403
        session['admin'] = True

    if not session.get("admin"):
        return '''
            <form method="post">
                <input type="password" name="password" placeholder="Admin password">
                <button type="submit">Login</button>
            </form>
        '''

    return render_template("admin.html", vips=vips)

@app.route('/send-pick', methods=['POST'])
def send_pick_manual():
    if not session.get("admin"):
        return "Unauthorized", 403

    pick = request.form.get("pick")
    if pick:
        send_pick(f"🔥 SignalCore AI VIP Pick\n\n{pick}")
    return redirect(url_for('admin_panel'))

@app.route('/add-vip', methods=['POST'])
def add_vip_manual():
    if not session.get("admin"):
        return "Unauthorized", 403

    order_id = request.form.get("order_id")
    days = int(request.form.get("days", 7))
    if order_id:
        vips[order_id] = {"expires": (datetime.utcnow() + timedelta(days=days)).isoformat()}
        save_vips(vips)
        print(f"✅ Admin added VIP: {order_id}")
    return redirect(url_for('admin_panel'))

@app.route('/ping')
def ping():
    return "pong"

# === 🚀 RUN ===
def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    run_scheduler()
