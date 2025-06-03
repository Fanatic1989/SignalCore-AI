import requests
import hashlib
import time

URL = "https://www.betonline.ag/sportsbook/basketball/nba"  # Change as needed
CHECK_INTERVAL = 3600  # Check every hour
HASH_FILE = "utils/.last_hash"

def get_site_hash():
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            return hashlib.sha256(response.text.encode('utf-8')).hexdigest()
    except Exception as e:
        print("❌ Error fetching site:", e)
    return None

def load_last_hash():
    try:
        with open(HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_hash(current_hash):
    with open(HASH_FILE, 'w') as f:
        f.write(current_hash)

def check_for_updates():
    current_hash = get_site_hash()
    if not current_hash:
        return

    last_hash = load_last_hash()

    if current_hash != last_hash:
        print("🔄 Site content changed! Time to recheck scraper.")
        # You could email yourself or trigger an alert here.
        save_hash(current_hash)
    else:
        print("✅ No change detected.")

# Example standalone loop
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(CHECK_INTERVAL)
