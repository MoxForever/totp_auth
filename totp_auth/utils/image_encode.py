import base64
from pathlib import Path


def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        raw = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/{image_path.suffix};base64,{raw}"
