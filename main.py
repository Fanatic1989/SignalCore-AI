import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Home route shows VIP payment
@app.route('/')
def home():
    return render_template('vip_payment.html')

# VIP payment page (also accessible via /vip)
@app.route('/vip')
def vip_payment():
    return render_template('vip_payment.html')

# Submit payment proof
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

# Ping route (for UptimeRobot)
@app.route('/ping')
def ping():
    return "pong"

# Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
