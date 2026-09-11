from datetime import date, timedelta
import json
from backend.app.models.organization import Organization
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.services.code_generator import generate_serial_number, compute_code_hash


def test_verify_genuine_and_counterfeit_code(client, db_session):
    # Setup test medicine & batch
    org = Organization(name="Test Org", licence_no="LIC-1", contact_email="test@org.com")
    db_session.add(org)
    db_session.flush()

    med = Medicine(
        organization_id=org.id,
        brand_name="Dolo-650",
        generic_name="Paracetamol",
        category="Analgesic",
        manufacturer="Micro Labs",
        strength="650 mg",
        dosage_form="Tablet",
        active_ingredients=json.dumps([{"name": "Paracetamol IP", "strength": "650", "unit": "mg", "purpose": "Active"}]),
        indications="Fever",
        dosage_instructions="1 tablet",
        warnings_and_precautions="No alcohol"
    )
    db_session.add(med)
    db_session.flush()

    # Batch 1: Active
    batch = Batch(
        medicine_id=med.id,
        batch_no="DL-2026",
        mfg_date=date.today() - timedelta(days=30),
        exp_date=date.today() + timedelta(days=365),
        status="active"
    )
    db_session.add(batch)
    db_session.flush()

    serial = generate_serial_number(prefix="MED")
    code = Code(
        batch_id=batch.id,
        serial_number=serial,
        code_hash=compute_code_hash(serial),
        status="active",
        scan_count=0
    )
    db_session.add(code)
    db_session.commit()

    # 1. Verify genuine code
    verify_res = client.post("/api/v1/codes/verify", json={
        "code_or_serial": serial,
        "device_info": "Mobile Test Client"
    })
    assert verify_res.status_code == 200
    res_data = verify_res.json()
    assert res_data["status"] == "GENUINE"
    assert res_data["is_genuine"] is True
    assert res_data["risk_score"] == 0
    assert res_data["medicine"]["brand_name"] == "Dolo-650"

    # 2. Verify invalid/counterfeit code
    invalid_res = client.post("/api/v1/codes/verify", json={
        "code_or_serial": "MED-FAKE-0000-FAKE",
        "device_info": "Mobile Test Client"
    })
    assert invalid_res.status_code == 200
    inv_data = invalid_res.json()
    assert inv_data["status"] == "INVALID"
    assert inv_data["is_genuine"] is False
    assert inv_data["risk_score"] == 100
