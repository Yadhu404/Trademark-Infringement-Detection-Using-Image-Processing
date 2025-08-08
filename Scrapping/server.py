from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from scrapLogo import smart_image_scraper, compare_images

app = Flask(__name__)
CORS(app)

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

    results = compare_images(path, 'scraped_images')
    return jsonify({'results': results})


if __name__ == '__main__':
    app.run(debug=True)
