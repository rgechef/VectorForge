from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve static files (DXFs + previews)
app.mount("/static", StaticFiles(directory="static"), name="static")

# DXF block definitions
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
        "description": "Ergonomic grip curve block",
        "preview_image": "/static/preview/grip_handle.png",
        "dxf_file": "/static/dxf/grip_handle.dxf"
    },
    {
        "id": "notch_cutout",
        "name": "NotchCutout",
        "description": "Rectangular cutout for locking or joining",
        "preview_image": "/static/preview/notch_cutout.png",
        "dxf_file": "/static/dxf/notch_cutout.dxf"
    },
    {
        "id": "mount_tab",
        "name": "MountTab",
        "description": "Flat tab with holes for mounting",
        "preview_image": "/static/preview/mount_tab.png",
        "dxf_file": "/static/dxf/mount_tab.dxf"
    },
    {
        "id": "lid_snap_ridge",
        "name": "LidSnapRidge",
        "description": "Ridge for press-fit lids",
        "preview_image": "/static/preview/lid_snap_ridge.png",
        "dxf_file": "/static/dxf/lid_snap_ridge.dxf"
    },
    {
        "id": "fillet_edge",
        "name": "FilletEdge",
        "description": "Curved fillet corner template",
        "preview_image": "/static/preview/fillet_edge.png",
        "dxf_file": "/static/dxf/fillet_edge.dxf"
    },
    {
        "id": "hinge_slot",
        "name": "HingeSlot",
        "description": "Rotating pivot slot",
        "preview_image": "/static/preview/hinge_slot.png",
        "dxf_file": "/static/dxf/hinge_slot.dxf"
    },
    {
        "id": "snap_tab",
        "name": "SnapTab",
        "description": "Snap-in tab for interlocking",
        "preview_image": "/static/preview/snap_tab.png",
        "dxf_file": "/static/dxf/snap_tab.dxf"
    },
    {
        "id": "support_ridge",
        "name": "SupportRidge",
        "description": "Reinforcement rib or ridge",
        "preview_image": "/static/preview/support_ridge.png",
        "dxf_file": "/static/dxf/support_ridge.dxf"
    },
    {
        "id": "hex_grid_panel",
        "name": "HexGridPanel",
        "description": "Infill panel with hexagon cutouts",
        "preview_image": "/static/preview/hex_grid_panel.png",
        "dxf_file": "/static/dxf/hex_grid_panel.dxf"
    }
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

