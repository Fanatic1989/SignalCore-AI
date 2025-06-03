import os
import datetime

def check_last_updated(file_path):
    if not os.path.exists(file_path):
        return f"⚠️ File {file_path} does not exist."

    last_modified = os.path.getmtime(file_path)
    last_modified_time = datetime.datetime.fromtimestamp(last_modified)
    now = datetime.datetime.now()
    diff = now - last_modified_time

    return f"⏱ Last updated {diff.days} days ago ({last_modified_time.strftime('%Y-%m-%d %H:%M:%S')})"

# Example usage
if __name__ == "__main__":
    print(check_last_updated("utils/pick_generator.py"))
