from datetime import date, timedelta
from backend.app.services.code_generator import (
    generate_serial_number,
    compute_code_hash,
    format_gs1_datamatrix,
    generate_qr_assets
)


def test_serial_and_hash_generation():
    serial = generate_serial_number(prefix="MED")
    assert serial.startswith("MED-")
    assert len(serial.split("-")) == 4

    h1 = compute_code_hash(serial)
    h2 = compute_code_hash(serial)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256


def test_gs1_and_qr_assets():
    exp = date.today() + timedelta(days=365)
    gs1 = format_gs1_datamatrix("8901234567890", exp, "BATCH01", "MED-11-22-33")
    assert "(01)08901234567890" in gs1
    assert "(10)BATCH01" in gs1

    assets = generate_qr_assets("https://smartmed.org/v/MED-11-22-33")
    assert "qr_svg" in assets
    assert "<svg" in assets["qr_svg"]
    assert "qr_data_url" in assets
