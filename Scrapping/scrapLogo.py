from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import requests
import torch
import clip
from PIL import Image
from torchvision import transforms
# from sklearn.exceptions import DataConversionWarning
import warnings
warnings.filterwarnings("ignore")


#PLATFORMS AND URLS,SEARCH QUERIES
platforms = {
    "play.google" : 
    {
        "url" : "https://play.google.com/store",
        "searchQ" : "/search?q="
    },
    "amazon" : 
    {
        "url" : "https://www.amazon.in",
        "searchQ" : "/s?k="
    },
    "flipkart" : 
    {
        "url" : "https://www.flipkart.com",
        "searchQ" : "/search?q="
    },
    "walmart" : 
    {
        "url" : "https://www.walmart.com",
        "searchQ" : "/search?q="
    },
    "alibaba" : 
    {
        "url" : "https://www.alibaba.com/trade",
        "searchQ" : "/search?spm="
    },
    "ebay" : 
    {
        "url" : "https://www.ebay.com",
        "searchQ" : "/sch/i.html?_nkw="
    }
}


#DELETES THE SCRAPPED LOGOS
def delete_logos(pathToRemove):
    if not os.path.isdir(pathToRemove):
        return
    
    for logo in os.listdir(pathToRemove):
        file = os.path.join(pathToRemove, logo)

        if os.path.isfile(file):
            try:
                os.remove(file)
            except Exception as e:
                print("ERROR")
        else:
            print(f"${file} is not a file.")
                


#SCRAPPING
def smart_image_scraper(url, companyName, download_path='scraped_images'):

    if not os.path.exists(download_path):
        os.makedirs(download_path)
    else:
        delete_logos(download_path)

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)

    try:

        newUrl = f"{platforms[url]["url"]}{platforms[url]["searchQ"]}{companyName}"
        print(newUrl)
        driver.get(newUrl)

        time.sleep(8)  # Wait for the page to load

        scroll_pause_time = 2
        num_scrolls = 15  # Increase for more images

        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(num_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Reached the end
            last_height = new_height

        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img')

        for idx, img in enumerate(image_elements):
            src = img.get_attribute('src')
            if src and src.startswith('http') and ('.jpg' in src or '.png' in src or '.jpeg' in src):
                try:
                    img_data = requests.get(src).content
                    with open(os.path.join(download_path, f'image_{idx}.jpg'), 'wb') as handler:
                        handler.write(img_data)
                except Exception as e:
                    print(f"\nFAILED TO DOWNLOAD IMAGE {src}: {e}")

    finally:
        driver.quit()

#COMPARE SCRAPPED LOGO
def compare_images(input_image_path, scraped_images_dir, similarity_threshold=0.60):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    input_image = preprocess(Image.open(input_image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        input_features = model.encode_image(input_image)

    results = []

    for file in os.listdir(scraped_images_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image_path = os.path.join(scraped_images_dir, file)
                image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
                with torch.no_grad():
                    image_features = model.encode_image(image)
                    similarity = torch.nn.functional.cosine_similarity(input_features, image_features).item()
                    results.append({
                        'filename': file,
                        'similarity': round(similarity, 2),
                        'is_similar': similarity > similarity_threshold
                    })
            except Exception as e:
                print(f"Error processing image {file}: {e}")

    results.sort(key=lambda x: x['similarity'], reverse=True)
    print("RESULT FROM SCRAP : ",results)
    return results[:1]