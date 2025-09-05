from PIL import Image, ExifTags

def extract_exif_summary(im: Image.Image):
    try:
        raw = im.getexif()
        if not raw:
            return {}
        readable = {}
        for k, v in raw.items():
            key = ExifTags.TAGS.get(k, str(k))
            # Avoid overlong binary fields
            if isinstance(v, bytes):
                continue
            readable[key] = v
        return readable
    except Exception:
        return {}
