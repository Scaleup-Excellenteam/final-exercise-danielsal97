import os
import json
import uuid
import datetime
from flask import Flask, request, jsonify, send_file
import logging
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = '../shared_files/uploads'
OUTPUT_FOLDER = '../shared_files/outputs'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# In-memory storage
uploads = {}


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        uid = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = secure_filename(f"{timestamp}_{uid}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        uploads[uid] = {
            'filename': file.filename,
            'timestamp': timestamp,
            'status': 'pending',
            'explanation': None
        }
        logger.info(f"File uploaded: {filename}")
        return jsonify({"uid": uid}), 201


@app.route('/status', methods=['GET'])
def get_status():
    """
    Check the status of the uploaded file processing.
    """
    uid = request.args.get('uid')
    if uid not in uploads:
        return jsonify({
            'status': 'not found',
            'filename': None,
            'timestamp': None,
            'explanation': None
        }), 404

    upload_info = uploads[uid]

    output_files = os.listdir(OUTPUT_FOLDER)
    for file in output_files:
        if uid in file:
            upload_info['status'] = 'done'
            output_file_path = os.path.join(OUTPUT_FOLDER, file)
            with open(output_file_path, 'r') as f:
                explanation = json.load(f)
            return jsonify({
                'status': "done",
                'filename': upload_info['filename'],
                'timestamp': upload_info['timestamp'],
                'explanation': explanation
            })

    return jsonify({
        'status': upload_info['status'],
        'filename': upload_info['filename'],
        'timestamp': upload_info['timestamp'],
        'explanation': upload_info['explanation']
    })


if __name__ == '__main__':
    app.run(debug=True)
