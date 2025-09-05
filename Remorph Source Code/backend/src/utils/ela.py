from io import BytesIO
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

def error_level_analysis(im: Image.Image, quality: int = 90):
    """
    Recompresses the image at given JPEG quality and returns ELA image + stats.
    Works on a copy; returns (ela_image, mean_abs_diff).
    """
    tmp = BytesIO()
    im.save(tmp, "JPEG", quality=quality)
    tmp.seek(0)
    recompressed = Image.open(tmp)
    ela_img = ImageChops.difference(im, recompressed)
    extrema = ela_img.getextrema()
    # Normalize for visualization
    scale = 1
    for channel_extrema in extrema:
        scale = max(scale, channel_extrema[1])
    if scale > 0:
        ela_img = ImageEnhance.Brightness(ela_img).enhance(255.0/scale)
    arr = np.asarray(ela_img).astype("float32")
    mean_abs = float(np.mean(np.abs(arr)))
    return ela_img, mean_abs
