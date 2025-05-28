import json
import os
from datetime import datetime, timedelta

VIP_FILE = "vip_users.json"

def load_vips():
    """Load the VIP user dictionary from the JSON file."""
    if os.path.exists(VIP_FILE):
        try:
            with open(VIP_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("❌ Failed to parse VIP JSON. Starting fresh.")
            return {}
    return {}

def save_vips(vip_dict):
    """Save the current VIP user dictionary to the JSON file."""
    try:
        with open(VIP_FILE, "w") as f:
            json.dump(vip_dict, f, indent=2)
        print("✅ VIP list saved.")
    except Exception as e:
        print(f"❌ Error saving VIPs: {e}")

def is_vip(order_id):
    """Check if the given order ID is an active VIP (not expired)."""
    vips = load_vips()
    if order_id in vips:
        expiry_str = vips[order_id].get("expires")
        if expiry_str:
            expiry_date = datetime.fromisoformat(expiry_str)
            if expiry_date > datetime.utcnow():
                return True
            else:
                print(f"⚠️ VIP expired: {order_id}")
    return False

def add_vip(order_id, days=7):
    """Add or extend a VIP by order ID."""
    vips = load_vips()
    now = datetime.utcnow()
    expires = now + timedelta(days=days)

    vips[order_id] = {
        "expires": expires.isoformat()
    }

    save_vips(vips)
    print(f"✅ VIP added: {order_id} (expires {expires})")

def remove_vip(order_id):
    """Remove a VIP manually by order ID."""
    vips = load_vips()
    if order_id in vips:
        del vips[order_id]
        save_vips(vips)
        print(f"❌ VIP removed: {order_id}")
    else:
        print(f"ℹ️ No VIP found for: {order_id}")
