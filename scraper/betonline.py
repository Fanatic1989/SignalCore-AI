from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config  # your credentials

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def login(driver):
    driver.get("https://www.betonline.ag/sportsbook/login")
    wait = WebDriverWait(driver, 20)
    
    # Wait for email field
    email_field = wait.until(EC.presence_of_element_located((By.ID, "login-email")))
    email_field.send_keys(config.BETONLINE_EMAIL)
    
    password_field = driver.find_element(By.ID, "login-password")
    password_field.send_keys(config.BETONLINE_PASSWORD)
    
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
    login_button.click()
    
    # Wait for the page to load after login, e.g. sportsbook page appears
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sportsbook-content")))
    print("✅ Logged in successfully")

def get_lines_for_sport(driver, sport_url):
    print(f"🌐 Navigating to {sport_url}")
    driver.get(sport_url)
    wait = WebDriverWait(driver, 20)
    # Wait until the betting lines container appears
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.event")))
    
    time.sleep(5)  # extra wait for full JS load

    events = driver.find_elements(By.CSS_SELECTOR, "div.event")
    print(f"✅ Found {len(events)} events")

    for event in events[:5]:  # limit to first 5 for now
        teams = event.find_elements(By.CSS_SELECTOR, "span.team-name")
        lines = event.find_elements(By.CSS_SELECTOR, "span.price")
        if len(teams) == 2 and lines:
            print(f"Match: {teams[0].text} vs {teams[1].text}")
            print(f"Lines: {[line.text for line in lines]}")
            print("---")

def main():
    driver = setup_driver()
    try:
        login(driver)
        sports = {
            "NBA": "https://www.betonline.ag/sportsbook/basketball/nba",
            "MLB": "https://www.betonline.ag/sportsbook/baseball/mlb",
            "NHL": "https://www.betonline.ag/sportsbook/hockey/nhl"
        }
        for sport, url in sports.items():
            get_lines_for_sport(driver, url)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
