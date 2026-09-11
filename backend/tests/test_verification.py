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
    assert res_data["is_valid"] is True
    assert res_data["verification_status"] == "AUTHENTIC"
    assert res_data["medicine"]["name"] == "Dolo-650"

    # 2. Verify invalid/counterfeit code
    invalid_res = client.post("/api/v1/codes/verify", json={
        "code_or_serial": "MED-FAKE-0000-FAKE",
        "device_info": "Mobile Test Client"
    })
    assert invalid_res.status_code == 200
    inv_data = invalid_res.json()
    assert inv_data["status"] == "INVALID"
    assert inv_data["is_valid"] is False
    assert inv_data["verification_status"] == "INVALID"
    assert inv_data["risk_score"] == 100


def test_shared_contract_verification_verify(client, db_session):
    # Setup test medicine & batch for MD110
    org = Organization(name="Demo Pharma", licence_no="DL-DEMO", contact_email="contact@demopharma.com")
    db_session.add(org)
    db_session.flush()

    med = Medicine(
        organization_id=org.id,
        brand_name="Paracetamol 500 mg",
        generic_name="Paracetamol",
        category="Analgesic",
        manufacturer="Demo Pharma",
        strength="500 mg",
        dosage_form="Tablet",
        active_ingredients=json.dumps([{"name": "Paracetamol IP", "strength": "500", "unit": "mg", "purpose": "Active"}]),
        indications="Fever relief",
        dosage_instructions="1 tablet daily",
        warnings_and_precautions="Do not exceed"
    )
    db_session.add(med)
    db_session.flush()

    batch_valid = Batch(
        medicine_id=med.id,
        batch_no="PCM26A01",
        mfg_date=date.today() - timedelta(days=30),
        exp_date=date.today() + timedelta(days=365),
        status="active"
    )
    batch_expired = Batch(
        medicine_id=med.id,
        batch_no="PCM24EXP",
        mfg_date=date.today() - timedelta(days=700),
        exp_date=date.today() - timedelta(days=30),
        status="active"
    )
    db_session.add_all([batch_valid, batch_expired])
    db_session.flush()

    code_md110 = Code(batch_id=batch_valid.id, serial_number="MD110", code_hash="hash1", status="active", scan_count=0)
    code_exp = Code(batch_id=batch_expired.id, serial_number="EXP101", code_hash="hash2", status="active", scan_count=0)
    db_session.add_all([code_md110, code_exp])
    db_session.commit()

    # 1. Test POST /api/v1/verification/verify with code_data MD110
    res1 = client.post("/api/v1/verification/verify", json={
        "code_data": "MD110",
        "latitude": 0.0,
        "longitude": 0.0,
        "source": "mobile_app"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["is_valid"] is True
    assert data1["verification_status"] == "AUTHENTIC"
    assert data1["medicine"]["name"] == "Paracetamol 500 mg"
    assert data1["medicine"]["dosage"] == "500 mg"
    assert data1["medicine"]["manufacturer"] == "Demo Pharma"
    assert data1["batch"]["batch_number"] == "PCM26A01"
    assert data1["raw_code"] == "MD110"

    # 2. Test Unknown code
    res2 = client.post("/api/v1/verification/verify", json={
        "code_data": "UNKNOWN_CODE",
        "source": "mobile_app"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_valid"] is False
    assert data2["verification_status"] == "INVALID"
    assert data2["medicine"] is None

    # 3. Test Expired code
    res3 = client.post("/api/v1/verification/verify", json={
        "code_data": "EXP101",
        "source": "mobile_app"
    })
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["is_valid"] is False
    assert data3["verification_status"] == "EXPIRED"

    # 4. Test Missing / Empty code_data (400 validation)
    res4 = client.post("/api/v1/verification/verify", json={
        "code_data": "",
        "source": "mobile_app"
    })
    assert res4.status_code == 400
    data4 = res4.json()
    assert "error" in data4
    assert data4["error"]["code"] == "INVALID_REQUEST"

