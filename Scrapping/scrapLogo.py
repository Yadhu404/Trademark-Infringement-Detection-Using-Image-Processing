from selenium import webdriver
from selenium.webdriver.common.by import By
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

def smart_image_scraper(url, download_path='scraped_images'):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
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


def compare_images(input_image_path, scraped_images_dir, similarity_threshold=0.75):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Load and preprocess the input image
    input_image = preprocess(Image.open(input_image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        input_features = model.encode_image(input_image)

    similarities = []

    for file in os.listdir(scraped_images_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image_path = os.path.join(scraped_images_dir, file)
                image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
                with torch.no_grad():
                    image_features = model.encode_image(image)
                    similarity = torch.nn.functional.cosine_similarity(input_features, image_features).item()
                    similarities.append((file, similarity))
            except Exception as e:
                print(f"Error processing image {file}: {e}")

    # Sort and display top matches
    similarities.sort(key=lambda x: x[1], reverse=True)
    for fname, score in similarities[:5]:
        print(f"\n{fname} - SIMILARITY : {score:.2f}")
        if score > similarity_threshold:
            print("\n\n\t>> THIS LOGO MAY ALREADY EXIST!")

# subdomain = "www"
# print("1. gamedevrocket\n2. w3schools\n3. playstore\n4. amazon\n5. poki\n6. Pinterest")
# platform = input("Enter the platform: ").strip().lower()

# if platform == "playstore":
#     subdomain = "play"
#     platform = 'google'


# url = f"https://{subdomain}.{platform}.com/"

# if platform == "pinterest":
#     url = 'https://za.pinterest.com/wendy181818/brands-and-logos/'

url = 'https://www.graphicdesigneire.ie/graphic-design-blog/top-101-most-famous-logos-of-all-time-ranked'

print(f"\nOPENING WEBSITE: {url}\n")

smart_image_scraper(url)

input_logo_path = input("\nENTER THE PATH TO YOUR INPUT IMAGE: ").strip()
compare_images(input_logo_path, 'scraped_images')
