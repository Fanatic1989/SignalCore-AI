# vip_data.py
import json
import os

DATA_FILE = "vip_store.json"

# Load VIP data from file
def load_vips():
    if not os.path.exists(DATA_FILE):
        return set()
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except Exception:
            return set()

# Save VIP data to file
def save_vips(vips):
    with open(DATA_FILE, "w") as f:
        json.dump(list(vips), f)

# Add a new VIP order ID
def add_vip(order_id):
    vips = load_vips()
    vips.add(order_id)
    save_vips(vips)

# Remove a VIP
def remove_vip(order_id):
    vips = load_vips()
    vips.discard(order_id)
    save_vips(vips)

# Check if an order ID is a VIP
def is_vip(order_id):
    return order_id in load_vips()

# List all VIPs
def list_vips():
    return list(load_vips())

