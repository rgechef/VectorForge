from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve static files like DXF and preview images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Block definitions
block_library = [
    {
        "id": "rect_base",
        "name": "RectBase",
        "description": "2D rectangle base with size params",
        "preview_image": "/static/preview/rect_base.png",
        "dxf_file": "/static/dxf/rect_base.dxf"
    },
    {
        "id": "circle_hole",
        "name": "CircleHole",
        "description": "Drilled or punched circle cutouts",
        "preview_image": "/static/preview/circle_hole.png",
        "dxf_file": "/static/dxf/circle_hole.dxf"
    },
    {
        "id": "rounded_rect",
        "name": "RoundedRect",
        "description": "Rounded rectangle panel with curved corners",
        "preview_image": "/static/preview/rounded_rect.png",
        "dxf_file": "/static/dxf/rounded_rect.dxf"
    }
    # Add more blocks here if needed
]

@app.get("/blocks")
def get_blocks():
    return JSONResponse(content={"blocks": block_library})

@app.post("/convert")
def convert_block(block_id: str):
    block = next((b for b in block_library if b["id"] == block_id), None)
    if block:
        dxf_path = "." + block["dxf_file"]
        if os.path.exists(dxf_path):
            return FileResponse(dxf_path, media_type="application/dxf", filename=os.path.basename(dxf_path))
        else:
            return JSONResponse(status_code=404, content={"error": "DXF file not found"})
    else:
        return JSONResponse(status_code=404, content={"error": "Block not found"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
