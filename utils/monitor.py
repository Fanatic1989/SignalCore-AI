import requests
from datetime import datetime

# ✅ URL to monitor — update if different
MONITORED_URL = "https://signalcore-ai.onrender.com"

def check_site_health():
    try:
        response = requests.get(MONITORED_URL, timeout=10)
        if response.status_code == 200:
            return {"status": "up", "code": 200, "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "error", "code": response.status_code, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "down", "error": str(e), "timestamp": datetime.utcnow().isoformat()}
