import cadquery as cq
from app.utils.parser import parse_prompt
from app.utils.exporter import export_model

def generate_model(prompt: str):
    config = parse_prompt(prompt)
    result = (
        cq.Workplane("XY")
        .box(config["width"], config["depth"], config["height"])
        .edges("|Z").fillet(config["fillet"])
    )
    return export_model(result)