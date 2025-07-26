from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import os
import uuid
from svgpathtools import svg2paths, wsvg
from svgwrite import Drawing

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"status": "VectorForge is live!"})

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # Load image
        image = Image.open(file_path).convert("L")
        np_img = np.array(image)

        # Dummy conversion: generate a rectangle SVG path for now
        height, width = np_img.shape
        svg_filename = filename.replace(".png", ".svg").replace(".jpg", ".svg")
        svg_path = os.path.join(OUTPUT_FOLDER, svg_filename)

        dwg = Drawing(svg_path, profile='tiny', size=(width, height))
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='none', stroke='black'))
        dwg.save()

        return jsonify({
            "message": "File converted successfully",
            "svg_path": svg_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
