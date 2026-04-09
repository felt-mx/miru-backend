import base64
import io
import numpy as np
from PIL import Image


def b64_to_array(b64: str) -> np.ndarray:
    data = base64.b64decode(b64)
    img = Image.open(io.BytesIO(data)).convert("RGB").resize((320, 180))
    return np.array(img, dtype=np.uint8)


def pixel_diff(prev: np.ndarray, curr: np.ndarray, threshold: int = 30) -> np.ndarray:
    diff = np.abs(curr.astype(np.int16) - prev.astype(np.int16))
    changed = np.any(diff > threshold, axis=-1)
    return float(changed.mean())


def frame_to_b64_thumbnail(b64: str, size: tuple[int, int] = (320, 180)) -> str:
    data = base64.b64decode(b64)
    img = Image.open(io.BytesIO(data)).convert("RGB").resize(size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode()
