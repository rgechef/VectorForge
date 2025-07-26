from flask import Flask, request, jsonify
from PIL import Image
from svgpathtools import svg2paths
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'VectorForge API is Live!'

@app.route('/vectorize', methods=['POST'])
def vectorize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    filename = 'temp_input.png'
    image.save(filename)

    try:
        # Convert image to SVG using Pillow and save
        im = Image.open(filename).convert("L").point(lambda x: 0 if x < 128 else 255, '1')
        svg_path = 'output.svg'
        im.save(svg_path)

        # Optional: analyze SVG contents (demo)
        paths, _ = svg2paths(svg_path)

        os.remove(filename)

        return jsonify({
            'message': 'Image vectorized successfully',
            'svg_file': svg_path,
            'num_paths_detected': len(paths)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
