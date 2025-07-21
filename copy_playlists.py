from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

# --- Add options ---
options = Options()
options.add_argument(r"user-data-dir=C:\Users\38096\AppData\Local\Google\Chrome\User Data")
options.add_argument("profile-directory=Default")

# --- Set up driver ---
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# --- Step 1: Go to YouTube ---
driver.get("https://www.youtube.com")

# Wait for you to log in manually
input("Log in to your YouTube account, then press Enter here...")

# --- Step 2: Go to Watch Later playlist ---
driver.get("https://www.youtube.com/playlist?list=WL")
time.sleep(5)

# --- Step 3: Scroll to load all videos ---
last_height = driver.execute_script("return document.documentElement.scrollHeight")
while True:
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# --- Step 4: Get all video elements ---
videos = driver.find_elements(By.XPATH, '//ytd-playlist-video-renderer')
print(f"Found {len(videos)} videos.")

# --- Step 5: Loop and save each to a custom playlist ---
for index, video in enumerate(videos):
    try:
        menu_button = video.find_element(By.ID, 'button')
        ActionChains(driver).move_to_element(video).perform()
        menu_button.click()
        time.sleep(1)

        save_button = driver.find_element(By.XPATH, '//ytd-menu-service-item-renderer[contains(., "Save to playlist")]')
        save_button.click()
        time.sleep(1)

        # Select your custom playlist — change the text to your playlist's name
        custom_playlist = driver.find_element(By.XPATH, '//yt-formatted-string[text()="New Watch Later"]')
        custom_playlist.click()
        time.sleep(1)

        # Press Escape to close the popup
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)

        print(f"Added video {index + 1}")
    except Exception as e:
        print(f"Error on video {index + 1}: {e}")
        continue

driver.quit()

