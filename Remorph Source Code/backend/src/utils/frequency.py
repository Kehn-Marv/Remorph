import numpy as np
from PIL import Image
import cv2

def fft_highfreq_ratio(im: Image.Image, frac=0.25):
    """
    Returns ratio of high-frequency energy to total energy via 2D FFT on grayscale.
    """
    gray = np.array(im.convert("L")).astype("float32") / 255.0
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    h, w = mag.shape
    cy, cx = h//2, w//2
    ry, rx = int(h*frac/2), int(w*frac/2)
    low = mag[cy-ry:cy+ry, cx-rx:cx+rx].sum()
    total = mag.sum() + 1e-8
    high = total - low
    return float(high / total)

def laplacian_variance(im: Image.Image):
    arr = np.array(im.convert("L"))
    lap = cv2.Laplacian(arr, cv2.CV_64F)
    return float(lap.var())

def jpeg_quant_score(im: Image.Image):
    """
    Rough proxy for JPEG quantization: recompress at q=95 and compare size delta.
    """
    import io
    buf_orig, buf_re = io.BytesIO(), io.BytesIO()
    im.save(buf_orig, "JPEG", quality=95)
    re = Image.open(io.BytesIO(buf_orig.getvalue()))
    re.save(buf_re, "JPEG", quality=75)
    s1, s2 = len(buf_orig.getvalue()), len(buf_re.getvalue())
    if s1 == 0: return 0.0
    return float(s2) / float(s1)
