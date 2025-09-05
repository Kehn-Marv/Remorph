from io import BytesIO
from PIL import Image, ImageOps

def load_image_from_bytes(data: bytes) -> Image.Image:
    im = Image.open(BytesIO(data)).convert("RGB")
    return im

def to_pil(arr):
    if isinstance(arr, Image.Image):
        return arr
    from PIL import Image
    import numpy as np
    arr = arr.astype("uint8")
    return Image.fromarray(arr)

def save_pil(img: Image.Image, path: str):
    img.save(path)

def ensure_min_size(im, min_side=256):
    w, h = im.size
    if min(w, h) >= min_side:
        return im
    scale = float(min_side) / min(w, h)
    new_w, new_h = int(w*scale), int(h*scale)
    return ImageOps.contain(im, (new_w, new_h))
