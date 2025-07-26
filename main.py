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
from datetime import datetime, timedelta

from google.cloud import storage

# STL/3D imports
import trimesh
from shapely.geometry import Polygon, MultiPolygon

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DXF_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DXF_FOLDER, exist_ok=True)

GCS_BUCKET = 'vectorforge-uploads'

def log(msg):
    print("==== [DEBUG] " + str(msg))

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

def save_to_gcs(local_path, dest_blob_name):
    """Upload a local file to Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(dest_blob_name)
    blob.upload_from_filename(local_path)
    log(f"Uploaded to GCS: {dest_blob_name}")
    return f"https://storage.googleapis.com/{GCS_BUCKET}/{dest_blob_name}"

def cleanup_old_files(folder, extensions=['.dxf', '.svg', '.stl', '.png'], max_age_hours=2):
    """Delete files older than max_age_hours in given folder with allowed extensions."""
    now = datetime.now()
    for fname in os.listdir(folder):
        if any(fname.lower().endswith(ext) for ext in extensions):
            fpath = os.path.join(folder, fname)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if (now - mtime) > timedelta(hours=max_age_hours):
                    os.remove(fpath)
                    log(f"Deleted old file: {fpath}")
            except Exception as e:
                log(f"Cleanup error: {e}")

def svg_to_stl(svg_path, stl_path, height=1.0):
    """Converts a simple SVG (single closed path) to a flat STL file (extrusion)."""
    from svgpathtools import svg2paths
    import shapely
    import shapely.ops

    paths, _ = svg2paths(svg_path)
    polygons = []
    for path in paths:
        pts = []
        for segment in path:
            # Use only Line segments
            if isinstance(segment, Line):
                pts.append((segment.start.real, segment.start.imag))
        if len(pts) > 2:
            polygons.append(Polygon(pts))
    if not polygons:
        raise Exception("No closed polygons found in SVG for STL export.")

    multi = MultiPolygon(polygons)
    mesh = trimesh.creation.extrude_polygon(multi, height)
    mesh.export(stl_path)
    log(f"STL saved: {stl_path}")

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
    except Exception as e:
        log(f"Exception during conversion: {str(e)}")
        return jsonify({'error': f'Failed to convert image: {str(e)}'}), 500

    if not os.path.exists(dxf_path) or os.path.getsize(dxf_path) < 100:
        log("DXF file was not created or is empty!")
        return jsonify({'error': 'DXF generation failed. Check the drawing and try again.'}), 500

    gcs_url = save_to_gcs(dxf_path, f"outputs/{unique_id}.dxf")

    log("Returning DXF file.")
    cleanup_old_files(DXF_FOLDER)
    cleanup_old_files(UPLOAD_FOLDER)
    return jsonify({"download_url": gcs_url, "status": "ok"})

@app.route('/convert_stl', methods=['POST'])
def convert_to_stl():
    log("Incoming /convert_stl request.")
    file = request.files.get('file') or request.files.get('image')
    if not file or file.filename == '':
        log("No file/image provided.")
        return jsonify({'error': 'No image provided'}), 400

    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.png")
    svg_path = os.path.join(DXF_FOLDER, f"{unique_id}.svg")
    stl_path = os.path.join(DXF_FOLDER, f"{unique_id}.stl")

    file.save(input_path)
    log(f"File saved: {input_path}")

    try:
        paths = raster_to_svg_paths(input_path)
        if not paths:
            log("No vector paths generated from image!")
            return jsonify({'error': 'No paths found in image. Try a darker or clearer drawing.'}), 400
        save_svg(paths, svg_path)
        svg_to_stl(svg_path, stl_path, height=1.0)
    except Exception as e:
        log(f"Exception during STL conversion: {str(e)}")
        return jsonify({'error': f'Failed to convert image to STL: {str(e)}'}), 500

    if not os.path.exists(stl_path) or os.path.getsize(stl_path) < 100:
        log("STL file was not created or is empty!")
        return jsonify({'error': 'STL generation failed. Check the drawing and try again.'}), 500

    gcs_url = save_to_gcs(stl_path, f"outputs/{unique_id}.stl")

    cleanup_old_files(DXF_FOLDER)
    cleanup_old_files(UPLOAD_FOLDER)
    return jsonify({"download_url": gcs_url, "status": "ok"})

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    cleanup_old_files(DXF_FOLDER)
    cleanup_old_files(UPLOAD_FOLDER)
    return jsonify({'status': 'Cleanup complete.'})

@app.route('/', methods=['GET'])
def health_check():
    return 'VectorForge API is running ✅'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)


