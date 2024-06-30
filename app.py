import datetime
import json
import os
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for
import explainer

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        uid = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{uid}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        return jsonify({
            "uid": uid,
            "filename": filename,
            "timestamp": timestamp
        }), 200

    return 'Failed to upload file', 400

@app.route('/status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'GET':
        uid = request.args.get('uid')
    elif request.method == 'POST':
        uid = request.json.get('uid')
    if not uid:
        return jsonify({"error": "No UID provided"}), 400

    output_file = explainer.process_file(uid)
    if not output_file:
        return jsonify({"error": "Processing failed or file not found"}), 500

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            explanation = json.load(f)

        html_content = generate_html_content(explanation)
        return jsonify({
            "status": "done",
            "filename": request.args.get('filename'),
            "timestamp": request.args.get('timestamp'),
            "html_content": html_content
        }), 200
    else:
        return jsonify({
            "status": "pending",
            "html_content": None
        }), 200

def generate_html_content(explanation):
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
    app.run(debug=True, port=5050)