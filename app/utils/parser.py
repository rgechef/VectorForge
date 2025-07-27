def parse_prompt(prompt: str) -> dict:
    result = {
        "shape": "box",
        "width": 100,
        "height": 50,
        "depth": 50,
        "fillet": 5,
        "holes": 2
    }

    if "mounting holes" in prompt:
        result["holes"] = 4

    if "rounded" in prompt:
        result["fillet"] = 10

    return result