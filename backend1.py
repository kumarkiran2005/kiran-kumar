from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Utility: Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route: File Upload and Image Processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image with OpenCV
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({'error': 'Invalid image format'}), 400

        # Resize the image (optional)
        resized_image = cv2.resize(image, (500, 500))

        # Save resized image
        resized_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"resized_{filename}")
        cv2.imwrite(resized_filepath, resized_image)

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'original_filepath': filepath,
            'processed_filepath': resized_filepath
        }), 200

    return jsonify({'error': 'File not allowed'}), 400


# Route: Calculate Distance Between Two Points
@app.route('/distance', methods=['POST'])
def calculate_distance():
    data = request.json
    point1 = data.get('point1')  # Example: {"x": 100, "y": 150}
    point2 = data.get('point2')  # Example: {"x": 200, "y": 250}
    scale = data.get('scale', 1)  # Scale to convert pixels to real-world units

    if not point1 or not point2:
        return jsonify({'error': 'Points are required'}), 400

    try:
        # Calculate pixel distance
        p1 = np.array([point1['x'], point1['y']])
        p2 = np.array([point2['x'], point2['y']])
        pixel_distance = np.linalg.norm(p1 - p2)

        # Convert to real-world distance
        real_distance = pixel_distance * scale

        return jsonify({
            'message': 'Distance calculated successfully',
            'pixel_distance': pixel_distance,
            'real_distance': real_distance
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
