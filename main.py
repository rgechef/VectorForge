from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import os
import uuid
import potrace
import ezdxf
import numpy as np
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for external apps like 3DShapeSnap.ai

@app.route('/')
def index():
    return jsonify({"status": "VectorForge is live!"})

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    output_format = request.form.get('format', 'dxf')

    if output_format not in ['dxf', 'stl']:
        return jsonify({"error": "Invalid format. Use 'dxf' or 'stl'."}), 400

    # Load image
    image = Image.open(file).convert("L")  # grayscale
    bitmap = potrace.Bitmap(np.array(image) > 128)
    path = bitmap.trace()

    # Prepare DXF or STL content
    filename = f"{uuid.uuid4()}.{output_format}"
    filepath = os.path.join("/tmp", filename)

    if output_format == 'dxf':
        doc = ezdxf.new()
        msp = doc.modelspace()
        for curve in path:
            for segment in curve:
                start = segment.start_point
                end = segment.end_point
                msp.add_line((start.x, start.y), (end.x, end.y))
        doc.saveas(filepath)
    else:
        # Placeholder: STL conversion logic to be added
        with open(filepath, "w") as f:
            f.write("solid placeholder\nendsolid\n")

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
