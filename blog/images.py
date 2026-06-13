"""Convert uploaded images to a compact web format (WebP or AVIF) before they
are written to storage, so both local media and the production R2 bucket hold
small, modern files instead of the original PNG/JPEG.

Driven by two settings (see config/settings.py):
    IMAGE_UPLOAD_FORMAT  'webp' (default) or 'avif'
    IMAGE_UPLOAD_QUALITY  1-100 (default 80)

Pillow 12 ships native WebP and AVIF encoders; if the configured format isn't
actually available we fall back to WebP rather than failing the upload.
"""

import io
import os

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, features

# Formats we can emit and the file extension each maps to.
_EXT = {"WEBP": "webp", "AVIF": "avif"}


def _target_format() -> str:
    """Resolve the configured Pillow format, falling back to WEBP if the
    requested encoder isn't built into this Pillow."""
    fmt = getattr(settings, "IMAGE_UPLOAD_FORMAT", "webp").upper()
    if fmt not in _EXT:
        fmt = "WEBP"
    if fmt == "AVIF" and not features.check("avif"):
        fmt = "WEBP"
    return fmt


def convert_to_web_image(file):
    """Re-encode an uploaded image file to the configured web format.

    Returns ``(ContentFile, "<name>.<ext>")`` ready to hand to
    ``FieldFile.save()``. Raises if the file can't be read as an image, so the
    caller can decide whether to keep the original.
    """
    fmt = _target_format()
    quality = int(getattr(settings, "IMAGE_UPLOAD_QUALITY", 80))

    # Read from the start regardless of any prior pointer position.
    file.seek(0)
    with Image.open(file) as img:
        # Respect EXIF orientation, then flatten to a mode the encoder accepts.
        img = ImageOps.exif_transpose(img)
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )
        img = img.convert("RGBA" if has_alpha else "RGB")

        buffer = io.BytesIO()
        save_kwargs = {"quality": quality}
        if fmt == "WEBP":
            save_kwargs["method"] = 6  # slowest/best WebP compression
        img.save(buffer, format=fmt, **save_kwargs)

    base = os.path.splitext(os.path.basename(getattr(file, "name", "image")))[0]
    return ContentFile(buffer.getvalue()), f"{base or 'image'}.{_EXT[fmt]}"
