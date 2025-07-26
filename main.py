
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import cv2
import numpy as np
from svgpathtools import Path, Line, wsvg
import ezdxf
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DXF_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DXF_FOLDER, exist_ok=True)

def raster_to_svg_paths(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

    return paths

def save_svg(paths, output_path):
    wsvg(paths, filename=output_path)

def svg_to_dxf(svg_path, dxf_path):
    doc = ezdxf.new()
    msp = doc.modelspace()

    # Parse the SVG file
    from xml.dom import minidom
    doc_svg = minidom.parse(svg_path)
    path_strings = [path.getAttribute('d') for path in doc_svg.getElementsByTagName('path')]
    doc_svg.unlink()

    from svgpathtools import parse_path
    for path_str in path_strings:
        parsed = parse_path(path_str)
        for segment in parsed:
            try:
                start = segment.start
                end = segment.end
                msp.add_line((start.real, start.imag), (end.real, end.imag))
            except:
                pass

    doc.saveas(dxf_path)

@app.route('/convert', methods=['POST'])
def convert_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.png")
    svg_path = os.path.join(DXF_FOLDER, f"{unique_id}.svg")
    dxf_path = os.path.join(DXF_FOLDER, f"{unique_id}.dxf")

    image.save(input_path)

    try:
        paths = raster_to_svg_paths(input_path)
        save_svg(paths, svg_path)
        svg_to_dxf(svg_path, dxf_path)
    except Exception as e:
        return jsonify({'error': f'Failed to convert image: {str(e)}'}), 500

    return send_file(dxf_path, as_attachment=True)

@app.route('/', methods=['GET'])
def health_check():
    return 'VectorForge API is running ✅'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
