from datetime import datetime

def log_result(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"📝 {timestamp} Logged pick: {message}")
