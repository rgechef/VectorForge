from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.routes import generate

app = FastAPI(
    title="VectorForge",
    description="Image to DXF/STL Converter with Smart CAD Blocks",
    version="1.0.0"
)

# Health check root route
@app.get("/")
def root():
    return {"status": "VectorForge is alive"}

# Mount static file directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include image generation routes
app.include_router(generate.router, prefix="/api")

# Optional: serve block library (for frontend UI listing)
@app.get("/api/blocks")
def get_block_library():
    return JSONResponse(content=[
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
    ])
