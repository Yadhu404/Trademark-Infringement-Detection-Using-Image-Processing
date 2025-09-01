from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from scrapLogo import smart_image_scraper, compare_images

app = Flask(__name__)
CORS(app)
SCRAPED_IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_images')
from flask import send_from_directory

@app.route('/scraped_images/<path:filename>')
def serve_scraped_image(filename):
    return send_from_directory(SCRAPED_IMAGE_DIR, filename)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    smart_image_scraper(url)
    return jsonify({'message': 'Images scraped successfully.'})


@app.route('/compare', methods=['POST'])
def compare():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
    image.save(path)

    results = compare_images(path, SCRAPED_IMAGE_DIR)
    return jsonify({'results': results})




if __name__ == '__main__':
    app.run(debug=True)