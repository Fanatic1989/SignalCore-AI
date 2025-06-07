from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# === YOUR LOGIN INFO ===
BETONLINE_EMAIL = "christiansucre1@gmail.com"
BETONLINE_PASSWORD = "Zariah*1"

# === CHROME PROFILE ===
profile_dir = os.path.expanduser("~/betonline_profile")

options = Options()
options.add_argument(f"--user-data-dir={profile_dir}")
options.add_argument("--profile-directory=Default")

# === INIT DRIVER ===
driver = webdriver.Chrome(options=options)
driver.get("https://www.betonline.ag/")

try:
    # === WAIT AND CLICK LOGIN BUTTON ===
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='hn-desktop-login-button']"))
    ).click()

    # === FILL EMAIL ===
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "email"))
    ).send_keys(BETONLINE_EMAIL)

    # === FILL PASSWORD ===
    driver.find_element(By.NAME, "password").send_keys(BETONLINE_PASSWORD)

    # === CLICK FINAL LOGIN BUTTON ===
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    ).click()

    # === WAIT FOR LOGIN TO COMPLETE ===
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.account-header"))  # or something post-login
    )

    print("✅ Logged in successfully.")

except Exception as e:
    print("❌ Error:", e)

# You can now continue scraping as a logged-in user

# === OPTIONAL: keep open ===
time.sleep(60 * 5)  # Keep browser open for 5 minutes

driver.quit()
