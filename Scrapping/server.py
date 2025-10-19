from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from werkzeug.utils import secure_filename
from scrapLogo import smart_image_scraper, compare_images
from main_model import ShowMainResults

app = Flask(__name__)
CORS(app)
SCRAPED_IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_images')
from flask import send_from_directory

@app.route('/scraped_images/<path:filename>')
def serve_scraped_image(filename):
    return send_from_directory(SCRAPED_IMAGE_DIR, filename)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


#SCRAPPING AND MODEL PREDICTION
@app.route('/scrape', methods=['POST'])
def scrape():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    url = request.form.get('url')  # URL from frontend formData
    print("IMAGE NAME",image.filename)
    print("URL : ",url)

    # Save the uploaded image locally
    path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
    image.save(path)

    colab_result = search_logo_via_colab(path)
    if url == "":
        c_name = colab_result.get('brand')
        sim = colab_result.get('similarity')
        verd = colab_result.get('verdict')
        print("BRAND NAME = ",c_name," SIMILARITY = ",sim," VERDICT = ",verd)
        results = ShowMainResults(c_name, sim, verd) 
        return jsonify({'results': results})
    else:
        # Send the actual file to Colab
        company_name = colab_result.get('brand')
        print("BRAND NAME = ",company_name)
        smart_image_scraper(url, company_name)

    return jsonify({'message': 'Images scraped successfully.'})


#COMPARE THE SCRAPPED LOGO
@app.route('/compare', methods=['POST'])
def compare():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
    image.save(path)

    results = compare_images(path, SCRAPED_IMAGE_DIR)
    return jsonify({'results': results})


#GET CLIENT
def search_logo_via_colab(image_path):
    client = re_instantiate_weaviate()
    return multimodal_query(client, "Trademark", image_path=image_path,threshold=0.50)
    COLAB_URL = "https://48c4aa5c9ca0.ngrok-free.app/predict"  # Colab endpoint
    
import subprocess
import weaviate
import base64
from weaviate.classes.query import MetadataQuery
from weaviate.classes.init import Auth # Import Auth for v4 client

def re_instantiate_weaviate() -> weaviate.WeaviateClient: # Use WeaviateClient for v4
    token = ''
    WCS_API_KEY = '' # Get Weaviate API key from secrets

    # Use weaviate.connect_to_weaviate_cloud for v4 client
    client = weaviate.connect_to_weaviate_cloud(
      cluster_url = "https://ncjg01pvqtox0vjpsavkfw.c0.asia-southeast1.gcp.weaviate.cloud",  # Use cluster_url for v4
    #   auth_credentials=Auth.api_key(WCS_API_KEY), # Add Weaviate API key authentication
      # For Vertex AI authentication with access token, use headers
      headers = {
        # "X-Goog-Vertex-Api-Key": token,
      }
    )
    return client


#MODEL
def multimodal_query(client, collection_name, image_path=None, threshold = 0.50,text=None, k=3, w_img=0.7, w_txt=0.3):
    """
    Query a multimodal Weaviate collection with image, text, or both.
    Executes only one branch based on inputs.
    """
    # -------------------------------
    # Case 2: Image only
    # -------------------------------
    if image_path and os.path.exists(image_path):
        print("\n--- Running Image-Only Logo Authenticity Test ---")
        trademarks = client.collections.get(collection_name)

        # Encode image as base64
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        # Query Weaviate
        results = trademarks.query.near_image(
            near_image=b64,
            limit=k,
            return_metadata=MetadataQuery(distance=True),
            return_properties=["brandName"]  # ✅ removed categories
        )

        print("\n--- Test Results ---")
        if len(results.objects) > 0:
            match = results.objects[0]
            distance = match.metadata.distance
            similarity = 1 - distance
            brand = match.properties.get("brandName", "Unknown")
            print("SIMILRAITY = ",similarity)
            print("THRESHOLD = ",threshold)
            if similarity < threshold:
                verdict = "GENUINE"
            else:
                verdict = "Logo is fake❗"
            client.close()
            return {
              "brand": brand,
              "distance": distance,
              "similarity": similarity,
              "verdict": verdict
            }
    

if __name__ == '__main__':
    app.run(debug=True)