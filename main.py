import os
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "✅ SignalCore AI is live!"

# VIP payment route
@app.route('/vip')
def vip_payment():
    return render_template('vip_payment.html')

# Submit proof route
@app.route('/submit-proof', methods=['GET', 'POST'])
def submit_proof():
    if request.method == 'POST':
        txid = request.form.get('txid')
        screenshot = request.files.get('screenshot')
        print("Proof submitted:")
        print("Transaction ID:", txid)
        print("Screenshot filename:", screenshot.filename if screenshot else "No file uploaded")
        return "✅ Your proof has been received. We’ll review it shortly."
    return render_template('submit_proof.html')

# Ping for uptime checks
@app.route('/ping')
def ping():
    return "pong"

# Run server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
