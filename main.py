from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import potrace
import numpy as np
import svgwrite
import ezdxf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Homepage status check ===
@app.route('/')
def index():
    return {"status": "VectorForge is live!"}


# === Utility: Check file extension ===
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# === Upload + Convert Route ===
@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # === STEP 1: Convert to bitmap array ===
        img = Image.open(filepath).convert("L")  # grayscale
        bitma
