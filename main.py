from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import os
import uuid
import potrace
import ezdxf
import numpy as np

app = Flask(__name__)
CORS(app)  # 🔓 Enable CORS for external apps like 3DShapeSnap.ai

@app.route('/')
def index():
    return jsonify({"status": "VectorForge is live!"})

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    output_format = request.form.get('format', 'dxf')  # dxf or stl
    filename = f"/tmp/{uuid.uuid4().hex}.png"
    file.save(filename)

    try:
        # Open image and convert to bitmap for tracing
        image = Image.open(filename).convert('L')  # Grayscale
        bitmap = potrace.Bitmap(np.array(image) > 128)
        path = bitmap.trace()

        if output_format == 'dxf':
            out_path = f"/tmp/{uuid.uuid4().hex}.dxf"
            doc = ezdxf.new()
            msp = doc.modelspace()

            for curve in path:
                for segment in curve:
                    if isinstance(segment, potrace.Curve):
                        start = segment.start_point
                        for c in segment.c:
                            msp.add_line((start.x, start.y), (c.x, c.y))
                            start = c
                    else:
                        msp.add_line((segment.start_point.x, segment.start_point.y),
                                     (segment.end_point.x, segment.end_point.y))
            doc.saveas(out_path)

        elif output_format == 'stl':
            out_path = f"/tmp/{uuid.uuid4().hex}.stl"
            # ⚠️ Placeholder STL response — replace with real STL logic later
            with open(out_path, 'w') as f:
                f.write("solid VectorForge\nendsolid VectorForge\n")

        else:
            return jsonify({'error': 'Invalid format'}), 400

        return send_file(out_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(filename)

if __name__ == '__main__':
    app.run(debug=False)
