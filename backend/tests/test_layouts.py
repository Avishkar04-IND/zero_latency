import json
from datetime import date, timedelta
from backend.app.models.organization import Organization
from backend.app.models.branch import Branch
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.models.user import User
from backend.app.core.security import get_password_hash, create_access_token


def test_layout_print_data_and_custom_prefix(client, db_session):
    # Setup Organization, Branch, User, Medicine, Batch
    org = Organization(name="Lupin Global Pharma", licence_no="LIC-LUP-01", contact_email="contact@lupin.com")
    db_session.add(org)
    db_session.flush()

    branch = Branch(organization_id=org.id, name="Pune Biotech Park", code="BR-PUN-01", city="Pune", state="Maharashtra")
    db_session.add(branch)
    db_session.flush()

    user = User(
        name="Packaging Engineer",
        email="pack@lupin.com",
        password_hash=get_password_hash("Pass123!"),
        role="ORG_ADMIN",
        organization_id=org.id,
        branch_id=branch.id,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    med = Medicine(
        organization_id=org.id,
        brand_name="Glucophage 500",
        generic_name="Metformin Hydrochloride",
        category="Antidiabetic",
        manufacturer="Lupin Global Pharma",
        strength="500 mg",
        dosage_form="Tablet",
        active_ingredients=json.dumps([{"name": "Metformin HCl", "strength": "500", "unit": "mg", "purpose": "Active"}]),
        indications="Type 2 Diabetes",
        dosage_instructions="1 tablet twice daily with meals",
        warnings_and_precautions="Take with food to minimize GI upset",
        storage_conditions="Store below 25°C in a dry place."
    )
    db_session.add(med)
    db_session.flush()

    batch = Batch(
        medicine_id=med.id,
        branch_id=branch.id,
        created_by=user.id,
        batch_no="GLU-2026-B1",
        mfg_date=date.today() - timedelta(days=20),
        exp_date=date.today() + timedelta(days=700),
        quantity=50000,
        mrp=45.0,
        status="active"
    )
    db_session.add(batch)
    db_session.commit()

    token = create_access_token(user.id, extra_claims={"role": user.role, "org_id": org.id})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Generate codes using a custom prefix (e.g. "MD110" or "GLU")
    gen_res = client.post("/api/v1/codes/generate", json={
        "batch_id": batch.id,
        "count": 2,
        "prefix": "MD110"
    }, headers=headers)
    assert gen_res.status_code == 201
    gen_data = gen_res.json()
    assert gen_data["total_generated"] == 2
    assert len(gen_data["codes"]) == 2
    serial_1 = gen_data["codes"][0]["serial_number"]
    assert serial_1.startswith("MD110-")

    # 2. Query Authoritative Layout Print Data by code/serial
    layout_res = client.get(f"/api/v1/layouts/print-data/{serial_1}")
    assert layout_res.status_code == 200
    layout_data = layout_res.json()

    # Verify structured medicine information
    assert layout_data["code"] == serial_1
    assert layout_data["medicine"]["name"] == "Glucophage 500"
    assert layout_data["medicine"]["generic_name"] == "Metformin Hydrochloride"
    assert layout_data["medicine"]["strength"] == "500 mg"
    assert layout_data["medicine"]["dosage_form"] == "Tablet"

    # Verify batch information
    assert layout_data["batch"]["batch_number"] == "GLU-2026-B1"
    assert layout_data["batch"]["mrp"] == 45.0

    # Verify manufacturer and branch information
    assert layout_data["manufacturer"]["name"] == "Lupin Global Pharma"
    assert layout_data["manufacturer"]["licence_no"] == "LIC-LUP-01"
    assert layout_data["branch"]["name"] == "Pune Biotech Park"
    assert layout_data["branch"]["code"] == "BR-PUN-01"

    # Verify pre-formatted typography lines for packaging layout engine
    print_lines = layout_data["print_data"]
    assert "Glucophage 500 500 mg" in print_lines["line1_header"]
    assert "Metformin Hydrochloride" in print_lines["line2_generic"]
    assert "B.No: GLU-2026-B1" in print_lines["line3_batch_exp"]
    assert "MRP Rs. 45.00" in print_lines["line4_mrp"]
    assert "LIC-LUP-01" in print_lines["line6_license"]
    assert print_lines["barcode_payload"] is not None

    # 3. Query Batch Print Data Bundle
    batch_layout_res = client.get(f"/api/v1/layouts/print-data/batch/{batch.id}")
    assert batch_layout_res.status_code == 200
    batch_bundle = batch_layout_res.json()
    assert batch_bundle["batch"]["batch_number"] == "GLU-2026-B1"
    assert batch_bundle["total_codes"] == 2
    assert len(batch_bundle["unit_codes"]) == 2

    # 4. 404 tests for non-existent records
    not_found_res = client.get("/api/v1/layouts/print-data/NONEXISTENT-999")
    assert not_found_res.status_code == 404

    batch_not_found = client.get("/api/v1/layouts/print-data/batch/99999")
    assert batch_not_found.status_code == 404
