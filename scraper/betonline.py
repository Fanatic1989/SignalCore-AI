from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def fetch_betonline_nba_lines():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("✅ Launching browser...")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.betonline.ag/sportsbook/basketball/nba")

    time.sleep(15)  # ⏳ wait for content to load

    print("✅ Page title:", driver.title)
    driver.save_screenshot("betonline_debug.png")  # for debugging

    # Try to find elements here and parse them, e.g.:
    # elements = driver.find_elements(...)
    # lines = [e.text for e in elements if e.text]

    driver.quit()

    return []
