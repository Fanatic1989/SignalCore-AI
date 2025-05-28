import os
import uuid
import json
import requests
import schedule
import time
import pytz
from flask import Flask, render_template, request, session, redirect, url_for, abort, render_template_string
from werkzeug.utils import secure_filename
from threading import Thread
from datetime import datetime, timedelta
from utils.pick_generator import generate_pick
from vip_data import load_vips, save_vips

# === ENVIRONMENT VARIABLES ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
ADMIN_PASSWORD = "Zariah*1"

# === FLASK CONFIGURATION ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "this_should_be_secret")
app.permanent_session_lifetime = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === VIP MEMORY CACHE ===
confirmed_vips = load_vips()

# === PICK SENDER ===
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

# === ROUTES ===
@app.route('/')
@app.route('/vip')
def vip_payment():
    order_id = session.get('order_id')
    is_vip = order_id in confirmed_vips
    return render_template("vip_payment.html", is_vip=is_vip, order_id=order_id)

@app.route('/generate-order')
def generate_order():
    new_order_id = str(uuid.uuid4())
    session['order_id'] = new_order_id
    return redirect(url_for('vip_payment'))

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

# === NOWPAYMENTS WEBHOOK ===
@app.route('/ipn', methods=['POST'])
def nowpayments_webhook():
    try:
        data = request.json
        print("🔔 Webhook received:", data)

        if data.get("payment_status") == "finished":
            order_id = data.get("order_id")
            if order_id:
                confirmed_vips[order_id] = {
                    "expires": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }
                save_vips(confirmed_vips)
                print(f"✅ Payment confirmed and VIP access granted: {order_id}")
                return "OK", 200
        return "Ignored", 200
    except Exception as e:
        print("❌ Webhook error:", str(e))
        abort(400)

# === ADMIN PANEL ===
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == ADMIN_PASSWORD:
            vips = load_vips()
            return render_template_string("""
                <h2>✅ VIP Access Panel</h2>
                <p>Total VIPs: {{ vips|length }}</p>
                <ul>
                  {% for order_id, info in vips.items() %}
                    <li><strong>{{ order_id }}</strong> — Expires: {{ info['expires'] }}</li>
                  {% endfor %}
                </ul>
                <a href="/">← Back to Home</a>
            """, vips=vips)
        return "❌ Incorrect password", 401

    return '''
    <h2>🔒 Admin Login</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="Enter admin password" required>
        <button type="submit">Login</button>
    </form>
    '''

# === SCHEDULER THREAD ===
def run_scheduler():
    ast = pytz.timezone("America/Puerto_Rico")
    print(f"[{datetime.now(ast).strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started")

    schedule.every().day.at("12:00").do(send_daily_pick)
    schedule.every().day.at("15:00").do(send_daily_pick)
    schedule.every().day.at("18:00").do(send_daily_pick)

    while True:
        schedule.run_pending()
        time.sleep(30)

# === LAUNCH APP ===
def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=keep_alive).start()
    run_scheduler()
