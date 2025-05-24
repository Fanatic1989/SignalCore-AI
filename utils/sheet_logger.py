import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    print("🔐 Loading credentials from environment variable...")
    credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("SignalCore_Log").sheet1
except Exception as e:
    print(f"❌ Google Sheets auth failed: {e}")
    sheet = None

def log_to_sheet(pick, vip_list):
    if sheet:
        row = [pick] + vip_list
        sheet.append_row(row)
