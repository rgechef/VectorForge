import cadquery as cq
import os
from datetime import datetime

def export_model(model):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = f"model_{timestamp}"
    out_dir = "static/exports"
    os.makedirs(out_dir, exist_ok=True)
    dxf_path = os.path.join(out_dir, f"{base_name}.dxf")
    stl_path = os.path.join(out_dir, f"{base_name}.stl")
    cq.exporters.export(model, dxf_path)
    cq.exporters.export(model, stl_path)
    return {
        "dxf_file": f"/static/exports/{base_name}.dxf",
        "stl_file": f"/static/exports/{base_name}.stl"
    }