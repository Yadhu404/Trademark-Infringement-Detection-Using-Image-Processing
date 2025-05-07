from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
import imagehash
import requests
from io import BytesIO
import time
import os

# ---------- Step 1: Setup Selenium ----------
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run without opening a browser window
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')

# Try automatic Chrome driver detection (recommended)
try:
    driver = webdriver.Chrome(options=options)
except:
    # Fallback: use specific path
    chromedriver_path = "D:/Tools/chromedriver.exe"  # Change this if needed
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

driver.maximize_window()

# ---------- Step 2: User Input ----------
# subdomain = "www"
# print("1. gamedevrocket\n2. w3schools\n3. playstore\n4. amazon\n5. poki\n6. crazygames")
# platform = input("Enter the platform: ").strip().lower()

# if platform == "playstore":
#     subdomain = "play"
#     platform = 'google'

# url = f"https://{subdomain}.{platform}.com/"
url = 'https://za.pinterest.com/wendy181818/brands-and-logos/'
print(f"\nOpening website: {url}\n")

try:
    driver.get(url)
    time.sleep(5)
except Exception as e:
    print(f"❌ Failed to open URL: {e}")
    driver.quit()
    exit()

# ---------- Step 3: Collect image URLs ----------
image_elements = driver.find_elements(By.TAG_NAME, "img")
image_urls = []

for img in image_elements:
    src = img.get_attribute('src')
    if src and src.startswith("http"):
        image_urls.append(src)

driver.quit()

print(f"✅ Found {len(image_urls)} valid image URLs.\n")

# ---------- Step 4: Load Input Image ----------
input_path = input("Enter the path to your input image (png/jpg): ").strip()

try:
    input_img = Image.open(input_path).convert('RGB')
    input_hash = imagehash.phash(input_img)
except Exception as e:
    print(f"❌ Error loading input image: {e}")
    exit()

# ---------- Step 5: Compare with Images ----------
similarity_scores = []

print("\n🔍 Comparing images...\n")

for idx, img_url in enumerate(image_urls):
    try:
        response = requests.get(img_url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert('RGB')

        img_hash = imagehash.phash(img)
        hash_diff = input_hash - img_hash
        similarity = 1 - (hash_diff / 64.0)

        similarity_scores.append((img_url, similarity))
        print(f"[{idx+1}] Similarity = {similarity * 100:.2f}%")

    except Exception as e:
        print(f"[{idx+1}] ❌ Error processing image: {e}")

# ---------- Step 6: Show Top 5 Matches ----------
print("\n🎯 Top 5 Matching Images:")
similarity_scores.sort(key=lambda x: x[1], reverse=True)

for i, (url, score) in enumerate(similarity_scores[:5], 1):
    print(f"{i}. {url} — Similarity: {score * 100:.2f}%")

print("\n✅ Completed")
