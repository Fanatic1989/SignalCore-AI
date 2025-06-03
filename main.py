import os
import uuid
import pytz
import time
import schedule
import requests
from flask import Flask, render_template, request, session, redirect, url_for, abort
from threading import Thread
from datetime import datetime, timedelta

from utils.pick_generator import generate_pick
from vip_data import load_vips, save_vips

# === 🔐 ENV VARIABLES ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Zariah*1")
TIMEZONE = os.getenv("TIMEZONE", "America/Puerto_Rico")

# === ⚙️ APP SETUP ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "this_should_be_secret")
app.permanent_session_lifetime = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === 🔐 VIP DB ===
vips = load_vips()

# === 📢 SIGNAL LOGIC ===
def send_daily_pick():
    try:
        pick = generate_pick()
        if not pick:
            print("❌ No pick generated.")
            return

        message = f"🔥 SignalCore AI VIP Pick\n\n{pick}"

        tg = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
        print("📤 Telegram:", tg.status_code)

        dc = requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("📤 Discord:", dc.status_code)
    except Exception as e:
        print("❌ Error in send_daily_pick:", str(e))

# === ⏰ SCHEDULER ===
def run_scheduler():
    tz = pytz.timezone(TIMEZONE)
    print(f"[{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

# === ROUTES ===

@app.route('/')
@app.route('/vip')
def vip_payment():
    order_id = session.get('order_id')
    is_vip = order_id in vips
    return render_template("vip_payment.html", is_vip=is_vip, order_id=order_id)

@app.route('/generate-order')
def generate_order():
    new_order_id = str(uuid.uuid4())
    session['order_id'] = new_order_id
    return redirect(url_for('vip_payment'))

@app.route('/ipn', methods=['POST'])
def nowpayments_webhook():
    try:
        data = request.json
        print("🔔 Webhook:", data)

        if data.get("payment_status") == "finished":
            order_id = data.get("order_id")
            if order_id:
                vips[order_id] = {"expires": (datetime.utcnow() + timedelta(days=7)).isoformat()}
                save_vips(vips)
                print(f"✅ Payment confirmed: {order_id}")
                return "OK", 200
        return "Ignored", 200
    except Exception as e:
        print("❌ Webhook error:", str(e))
        abort(400)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Unauthorized", 403
        session['admin'] = True

    if not session.get("admin"):
        return '''
        <form method="post">
            <input type="password" name="password" placeholder="Admin Password">
            <button type="submit">Login</button>
        </form>
        '''

    pick = generate_pick() or "❌ No picks available right now."
    return render_template("admin.html", preview=pick, vips=vips)

@app.route('/ping')
def ping():
    return "pong"

# === RUN APP ===
def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    send_daily_pick()  # 🔁 First signal test on launch
    Thread(target=keep_alive).start()
    run_scheduler()
