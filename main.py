from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Block library
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
    },
    {
        "id": "tray_wall",
        "name": "TrayWall",
        "description": "U-shaped wall segment for trays",
        "preview_image": "/static/preview/tray_wall.png",
        "dxf_file": "/static/dxf/tray_wall.dxf"
    },
    {
        "id": "slot_channel",
        "name": "SlotChannel",
        "description": "For joining parts with tabs",
        "preview_image": "/static/preview/slot_channel.png",
        "dxf_file": "/static/dxf/slot_channel.dxf"
    },
    {
        "id": "pipe_end",
        "name": "PipeEnd",
        "description": "Hollow or solid pipe edge profile",
        "preview_image": "/static/preview/pipe_end.png",
        "dxf_file": "/static/dxf/pipe_end.dxf"
    },
    {
        "id": "grip_handle",
        "name": "GripHandle",
        "description": "Grip-style handle extrusion",
        "preview_image": "/static/preview/grip_handle.png",
        "dxf_file": "/static/dxf/grip_handle.dxf"
    }
]

@app.get("/blocks")
def get_blocks():
    return JSONResponse(content={"blocks": block_library})

@app.post("/convert")
def convert_block(block_id: str = Query(...)):
    block = next((b for b in block_library if b["id"] == block_id), None)
    if block:
        dxf_path = "." + block["dxf_file"]
        if os.path.exists(dxf_path):
            return FileResponse(dxf_path, media_type="application/dxf", filename=os.path.basename(dxf_path))
        else:
            return JSONResponse(status_code=404, content={"error": "DXF file not found"})
    return JSONResponse(status_code=404, content={"error": "Block not found"})
