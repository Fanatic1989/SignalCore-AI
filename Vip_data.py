# vip_data.py

# In-memory VIP store (replace with database in production)
confirmed_vips = set()

def is_vip(order_id):
    return order_id in confirmed_vips

def add_vip(order_id):
    confirmed_vips.add(order_id)

def remove_vip(order_id):
    confirmed_vips.discard(order_id)

def list_vips():
    return list(confirmed_vips)
