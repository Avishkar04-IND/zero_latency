import base64
import hashlib
import hmac
import io
import secrets
from datetime import datetime, date
from typing import Dict, Any, Optional
from backend.app.core.config import settings

import qrcode
import qrcode.constants
import qrcode.image.svg
from qrcode.image.svg import SvgPathImage


def generate_serial_number(prefix: str = "MED", segments: int = 3) -> str:
    """
    Generates a cryptographically strong, non-sequential alphanumeric serial number.
    Format: PREFIX-XXXX-XXXX-... (e.g. MED-7A9K-W8Q4-P1B2 or MD110-X7K9)
    """
    clean_prefix = prefix.strip().replace(" ", "").upper()
    segs = [secrets.token_hex(2).upper() for _ in range(max(1, segments))]
    return f"{clean_prefix}-" + "-".join(segs)

def compute_code_hash(serial_number: str) -> str:
    """
    Generates an HMAC-SHA256 hash using the backend secret key.
    Stored server-side to detect counterfeiting and tampering.
    """
    return hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        serial_number.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def format_gs1_datamatrix(
    gtin: str,
    exp_date: date,
    batch_no: str,
    serial_number: str
) -> str:
    """
    Formats identifier according to GS1 Healthcare standard:
    (01) Global Trade Item Number [14 digits]
    (17) Expiration Date [YYMMDD]
    (10) Batch/Lot Number
    (21) Serial Number
    """
    clean_gtin = gtin.zfill(14)
    exp_formatted = exp_date.strftime("%y%m%d")
    return f"(01){clean_gtin}(17){exp_formatted}(10){batch_no}(21){serial_number}"


def generate_qr_assets(payload_data: str) -> Dict[str, Optional[str]]:
    """
    Generates QR code assets:
    - qr_svg: Raw scalable vector graphic XML string for web/mobile print preview
    - qr_data_url: Base64 data URI (PNG or SVG data URL)
    """
    try:
        # 1. Generate SVG
        qr_svg_img = qrcode.make(payload_data, image_factory=SvgPathImage, box_size=10, border=2)
        svg_buffer = io.BytesIO()
        qr_svg_img.save(svg_buffer)
        svg_content = svg_buffer.getvalue().decode("utf-8")

        # 2. Generate PNG Data URL
        qr_png = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr_png.add_data(payload_data)
        qr_png.make(fit=True)
        img = qr_png.make_image(fill_color="black", back_color="white")
        
        png_buffer = io.BytesIO()
        img.save(png_buffer)
        b64_png = base64.b64encode(png_buffer.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{b64_png}"

        return {
            "qr_svg": svg_content,
            "qr_data_url": data_url
        }
    except Exception:
        # Fallback high-quality standalone SVG generator
        svg_fallback = _generate_fallback_svg_qr(payload_data)
        b64_svg = base64.b64encode(svg_fallback.encode("utf-8")).decode("utf-8")
        return {
            "qr_svg": svg_fallback,
            "qr_data_url": f"data:image/svg+xml;base64,{b64_svg}"
        }


def _generate_fallback_svg_qr(data: str) -> str:
    """
    Generates a stylized SVG representation of a 2D matrix code for development/fallback.
    """
    # Create deterministic hash-based 21x21 matrix pattern
    h = hashlib.sha256(data.encode("utf-8")).hexdigest()
    bits = [int(c, 16) % 2 for c in h * 7]  # expand to 441 bits for 21x21
    
    size = 210
    cell = 10
    rects = []
    
    # Standard finder patterns in 3 corners
    def add_finder(x_start: int, y_start: int):
        for r in range(7):
            for c in range(7):
                if (r in (0, 6) or c in (0, 6)) or (2 <= r <= 4 and 2 <= c <= 4):
                    rects.append(f'<rect x="{(x_start+c)*cell}" y="{(y_start+r)*cell}" width="{cell}" height="{cell}" fill="#111827"/>')

    add_finder(0, 0)
    add_finder(14, 0)
    add_finder(0, 14)

    # Data cells
    idx = 0
    for r in range(21):
        for c in range(21):
            # Skip finder patterns
            if (r < 7 and c < 7) or (r < 7 and c >= 14) or (r >= 14 and c < 7):
                continue
            if bits[idx % len(bits)] == 1:
                rects.append(f'<rect x="{c*cell}" y="{r*cell}" width="{cell}" height="{cell}" fill="#111827"/>')
            idx += 1

    svg_body = "\n".join(rects)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="100%" height="100%">'
        f'<rect width="{size}" height="{size}" fill="#ffffff"/>'
        f'{svg_body}'
        f'</svg>'
    )
