from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pickle
import os

COOKIES_FILE = "betonline_cookies.pkl"

SPORT_URLS = {
    "NBA": "https://www.betonline.ag/sportsbook/basketball/nba",
    "MLB": "https://www.betonline.ag/sportsbook/baseball/mlb",
    "NHL": "https://www.betonline.ag/sportsbook/hockey/nhl",
}

def save_cookies(driver, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("💾 Cookies saved.")

def load_cookies(driver, filepath):
    with open(filepath, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    print("✅ Cookies loaded.")

def setup_driver():
    options = Options()
    # Comment out to see browser for login
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def fetch_all_sports():
    driver = setup_driver()

    # First-time login
    if not os.path.exists(COOKIES_FILE):
        print("🔐 Please log in to BetOnline manually.")
        driver.get("https://www.betonline.ag/sportsbook/basketball/nba")
        input("👉 After login, press ENTER here to save cookies...")
        save_cookies(driver, COOKIES_FILE)
    else:
        driver.get("https://www.betonline.ag/")
        time.sleep(5)
        load_cookies(driver, COOKIES_FILE)

    all_lines = {}

    for sport, url in SPORT_URLS.items():
        print(f"\n🎯 Visiting {sport} page...")
        driver.get(url)
        time.sleep(10)  # wait for content to load

        screenshot_name = f"{sport.lower()}_debug.png"
        driver.save_screenshot(screenshot_name)
        print(f"📸 Screenshot saved: {screenshot_name}")

        # Parse logic (optional - use screenshot for now)
        try:
            elements = driver.find_elements(By.CLASS_NAME, "some-class")  # update this
            lines = [el.text for el in elements if el.text]
            all_lines[sport] = lines
            print(f"📊 {sport} lines found:", lines)
        except Exception as e:
            print(f"⚠️ Could not extract lines for {sport}: {e}")
            all_lines[sport] = []

    driver.quit()
    return all_lines
