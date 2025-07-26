from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import cv2
import numpy as np
from svgpathtools import Path, Line, wsvg, parse_path
import ezdxf
from io import BytesIO
from PIL import Image
from xml.dom import minidom

# ---- GOOGLE CLOUD STORAGE ----
from google.cloud import storage

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DXF_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DXF_FOLDER, exist_ok=True)

def log(msg):
    print("==== [DEBUG] " + msg)

def raster_to_svg_paths(image_path):
    log(f"Reading image: {image_path}")
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise Exception("Failed to load image!")
    log("Image loaded.")
    edges = cv2.Canny(image, 100, 200)
    log("Canny edges detected.")
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    log(f"Contours found: {len(contours)}")
    paths = []
    for contour in contours:
        if len(contour) < 2:
            continue
        segments = []
        for i in range(len(contour) - 1):
            start = complex(contour[i][0][0], -contour[i][0][1])
            end = complex(contour[i + 1][0][0], -contour[i + 1][0][1])
            segments.append(Line(start, end))
        path = Path(*segments)
        paths.append(path)
    log(f"SVG paths created: {len(paths)}")
    return paths

def save_svg(paths, output_path):
    log(f"Saving SVG: {output_path}")
    wsvg(paths, filename=output_path)
    log("SVG saved.")

def svg_to_dxf(svg_path, dxf_path):
    log(f"Converting SVG to DXF: {svg_path} -> {dxf_path}")
    doc = ezdxf.new()
    msp = doc.modelspace()
    doc_svg = minidom.parse(svg_path)
    path_strings = [path.getAttribute('d') for path in doc_svg.getElementsByTagName('path')]
    doc_svg.unlink()
    for path_str in path_strings:
        parsed = parse_path(path_str)
        for segment in parsed:
            try:
                start = segment.start
                end = segment.end
                msp.add_line((start.real, start.imag), (end.real, end.imag))
            except Exception as e:
                log(f"DXF segment error: {e}")
    doc.saveas(dxf_path)
    log("DXF saved.")

def upload_to_gcs(local_file_path, destination_blob_name):
    log(f"Uploading {local_file_path} to GCS as {destination_blob_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket('vectorforge-uploads')
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    # Don't use blob.make_public() — uniform bucket-level access means ACLs are managed at the bucket level!
    public_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
    log(f"Uploaded to GCS: {public_url}")
    return public_url

@app.route('/convert', methods=['POST'])
def convert_image():
    log("Incoming /convert request.")
    file = request.files.get('file') or request.files.get('image')
    if not file or file.filename == '':
        log("No file/image provided.")
        return jsonify({'error': 'No image provided'}), 400
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.png")
    svg_path = os.path.join(DXF_FOLDER, f"{unique_id}.svg")
    dxf_path = os.path.join(DXF_FOLDER, f"{unique_id}.dxf")
    file.save(input_path)
    log(f"File saved: {input_path}")

    try:
        paths = raster_to_svg_paths(input_path)
        if not paths:
            log("No vector paths generated from image!")
            return jsonify({'error': 'No paths found in image. Try a darker or clearer drawing.'}), 400
        save_svg(paths, svg_path)
        svg_to_dxf(svg_path, dxf_path)
        if not os.path.exists(dxf_path) or os.path.getsize(dxf_path) < 100:
            log("DXF file was not created or is empty!")
            return jsonify({'error': 'DXF generation failed. Check the drawing and try again.'}), 500
        # ---- Upload to Google Cloud Storage ----
        gcs_url = upload_to_gcs(dxf_path, f'outputs/{unique_id}.dxf')
    except Exception as e:
        log(f"Exception during conversion: {str(e)}")
        return jsonify({'error': f'Failed to convert image: {str(e)}'}), 500

    log("Returning GCS DXF URL.")
    return jsonify({'dxf_url': gcs_url})

@app.route('/', methods=['GET'])
def health_check():
    return 'VectorForge API is running ✅'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
