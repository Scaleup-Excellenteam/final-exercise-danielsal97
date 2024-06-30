import datetime
import json
import os
import uuid
from flask import Flask, render_template, request, jsonify
import explainer
import threading
import logging

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
METADATA_FOLDER = 'metadata'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for metadata
metadata_store = {}


def process_file_async(uid, filename):
    """
    Function to process the file asynchronously.

    :param uid: Unique identifier for the file
    :param filename: Name of the file to be processed
    :return: None
    """
    output_file = os.path.join(OUTPUT_FOLDER, f"{uid}.json")
    success = explainer.process_file(uid)
    output_metadata = {
        "status": "done" if success else "failed",
        "output_file": output_file if success else None
    }
    metadata_store[uid].update(output_metadata)
    with open(os.path.join(METADATA_FOLDER, f"{uid}.json"), 'w') as f:
        json.dump(metadata_store[uid], f)
    logging.info(f"File {filename} processed. Status: {'done' if success else 'failed'}")


def is_done(output_path):
    """
    Check if the output file exists.

    :param output_path: Path to the output file
    :return: True if the file exists, False otherwise
    """
    return output_path and os.path.exists(output_path)


@app.route('/')
def index():
    """
    Render the index page.

    :return: Rendered HTML template for the index page
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and initiate processing.

    :return: JSON response with file metadata or error message
    """
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    if file:
        uid = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{timestamp}_{uid}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        metadata = {
            "uid": uid,
            "filename": file.filename,
            "timestamp": timestamp,
            "status": "processing",
            "output_file": None
        }
        metadata_store[uid] = metadata
        with open(os.path.join(METADATA_FOLDER, f"{uid}.json"), 'w') as f:
            json.dump(metadata, f)
        logging.info(f"File {file.filename} uploaded and saved to {file_path}")

        # Start processing the file in a separate thread
        threading.Thread(target=process_file_async, args=(uid, filename)).start()

        return jsonify(metadata), 200

    return 'Failed to upload file', 400


@app.route('/status', methods=['GET', 'POST'])
def check_status():
    """
    Check the processing status of the file.

    :return: JSON response with processing status and metadata
    """
    if request.method == 'GET':
        uid = request.args.get('uid')
    elif request.method == 'POST':
        uid = request.json.get('uid')
    if not uid:
        logging.error("No UID provided in the request")
        return jsonify({"error": "No UID provided"}), 400

    metadata_path = os.path.join(METADATA_FOLDER, f"{uid}.json")
    if not os.path.exists(metadata_path):
        logging.error(f"Metadata not found for UID {uid}")
        return jsonify({"error": "Metadata not found"}), 400

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    output_path = metadata.get("output_file")

    if is_done(output_path):
        with open(output_path, 'r') as f:
            explanation = json.load(f)

        html_content = generate_html_content(explanation)
        return jsonify({
            "status": "done",
            "filename": metadata["filename"],
            "timestamp": metadata["timestamp"],
            "html_content": html_content
        }), 200
    elif metadata.get("status") == "processing":
        return jsonify({
            "status": "processing",
            "filename": metadata["filename"],
            "timestamp": metadata["timestamp"],
            "html_content": None
        }), 200
    else:
        logging.error(f"Unknown status for UID {uid}")
        return jsonify({"error": "Unknown status"}), 400


def generate_html_content(explanation):
    """
    Generate HTML content from the explanation data.

    :param explanation: List of explanation data for each slide
    :return: HTML content as a string
    """
    html = ""
    for slide in explanation:
        slide_number = slide.get("slide_number")
        solutions = slide.get("solutions", [])
        solutions_html = "<ul>"
        for solution in solutions:
            solutions_html += f"<li>{solution}</li>"
        solutions_html += "</ul>"

        html += f"""
        <div>
            <h2>Slide {slide_number}</h2>
            {solutions_html}
        </div>
        """
    return html


if __name__ == '__main__':
    app.run(debug=True, port = 8867)