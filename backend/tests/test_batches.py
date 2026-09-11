import json
from datetime import date, timedelta
from backend.app.models.organization import Organization
from backend.app.models.branch import Branch
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.user import User
from backend.app.core.security import get_password_hash, create_access_token


def test_batch_creation_and_validation(client, db_session):
    # Setup organization, branch, and user
    org = Organization(name="Sun Pharma Ltd", licence_no="LIC-SUN-01", contact_email="admin@sun.com")
    db_session.add(org)
    db_session.flush()

    branch = Branch(organization_id=org.id, name="Vadodara Plant 1", code="BR-VAD-01")
    db_session.add(branch)
    db_session.flush()

    user = User(
        name="Production Manager",
        email="manager@sun.com",
        password_hash=get_password_hash("Pass123!"),
        role="ORG_ADMIN",
        organization_id=org.id,
        branch_id=branch.id,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    # Create medicine
    med = Medicine(
        organization_id=org.id,
        brand_name="Azithral 500",
        generic_name="Azithromycin Tablets IP",
        category="Antibiotic",
        manufacturer="Sun Pharma Ltd",
        strength="500 mg",
        dosage_form="Tablet",
        active_ingredients=json.dumps([{"name": "Azithromycin", "strength": "500", "unit": "mg", "purpose": "Antibiotic"}]),
        indications="Bacterial infections",
        dosage_instructions="1 tablet daily for 3 days",
        warnings_and_precautions="Complete full course"
    )
    db_session.add(med)
    db_session.commit()

    token = create_access_token(user.id, extra_claims={"role": user.role, "org_id": org.id, "branch_id": branch.id})
    headers = {"Authorization": f"Bearer {token}"}

    today = date.today()

    # 1. Successful Batch Creation (auto-deriving branch_id & created_by)
    valid_payload = {
        "medicine_id": med.id,
        "batch_no": "AZ-2026-B1",
        "mfg_date": str(today - timedelta(days=10)),
        "exp_date": str(today + timedelta(days=730)),
        "quantity": 25000,
        "mrp": 120.50,
        "status": "active"
    }
    create_res = client.post("/api/v1/batches", json=valid_payload, headers=headers)
    assert create_res.status_code == 201
    batch_data = create_res.json()
    assert batch_data["batch_no"] == "AZ-2026-B1"
    assert batch_data["branch_id"] == branch.id
    assert batch_data["created_by"] == user.id
    batch_id = batch_data["id"]

    # 2. Validation: Expiry date before or equal to manufacture date -> 400 Bad Request
    invalid_date_payload = {
        "medicine_id": med.id,
        "batch_no": "AZ-INVALID-DATES",
        "mfg_date": str(today),
        "exp_date": str(today - timedelta(days=5)),
        "quantity": 10000,
        "mrp": 50.0
    }
    date_res = client.post("/api/v1/batches", json=invalid_date_payload, headers=headers)
    assert date_res.status_code == 400
    assert "Expiry date must be after manufacture date" in date_res.json()["detail"]

    # 3. Validation: Quantity <= 0 -> 400 Bad Request
    invalid_qty_payload = {
        "medicine_id": med.id,
        "batch_no": "AZ-INVALID-QTY",
        "mfg_date": str(today),
        "exp_date": str(today + timedelta(days=365)),
        "quantity": 0,
        "mrp": 50.0
    }
    qty_res = client.post("/api/v1/batches", json=invalid_qty_payload, headers=headers)
    assert qty_res.status_code == 400
    assert "Quantity must be greater than 0" in qty_res.json()["detail"]

    # 4. Get batch with auto-populated registered medicine specifications
    get_res = client.get(f"/api/v1/batches/{batch_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["batch_no"] == "AZ-2026-B1"
    assert detail["branch_name"] == "Vadodara Plant 1"
    assert detail["medicine"]["brand_name"] == "Azithral 500"
    assert detail["medicine"]["generic_name"] == "Azithromycin Tablets IP"

    # 5. Patch Batch (e.g. recall batch)
    patch_res = client.patch(f"/api/v1/batches/{batch_id}", json={
        "status": "recalled"
    }, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "recalled"

    # 6. Patch Medicine (e.g. update status & instructions)
    patch_med = client.patch(f"/api/v1/medicines/{med.id}", json={
        "status": "active",
        "dosage_instructions": "Take with or without food."
    }, headers=headers)
    assert patch_med.status_code == 200
    assert patch_med.json()["dosage_instructions"] == "Take with or without food."


def test_batch_multi_tenant_isolation(client, db_session):
    # Org 1
    org1 = Organization(name="Pharma Alpha", licence_no="LIC-A1", contact_email="a@alpha.com")
    # Org 2
    org2 = Organization(name="Pharma Beta", licence_no="LIC-B2", contact_email="b@beta.com")
    db_session.add_all([org1, org2])
    db_session.flush()

    med1 = Medicine(
        organization_id=org1.id,
        brand_name="AlphaCure",
        generic_name="Alpha Drug",
        category="General",
        manufacturer="Pharma Alpha",
        strength="100 mg",
        dosage_form="Tablet",
        active_ingredients="[]",
        indications="Treatment",
        dosage_instructions="1 daily",
        warnings_and_precautions="None"
    )
    db_session.add(med1)
    db_session.flush()

    user2 = User(
        name="Beta Admin",
        email="admin@beta.com",
        password_hash=get_password_hash("Pass123!"),
        role="ORG_ADMIN",
        organization_id=org2.id,
        is_active=True
    )
    db_session.add(user2)
    db_session.commit()

    token2 = create_access_token(user2.id, extra_claims={"role": user2.role, "org_id": org2.id})
    headers2 = {"Authorization": f"Bearer {token2}"}

    today = date.today()

    # User from Org 2 attempts to create batch for Org 1's medicine -> 403 Forbidden
    cross_res = client.post("/api/v1/batches", json={
        "medicine_id": med1.id,
        "batch_no": "CROSS-ORG-01",
        "mfg_date": str(today - timedelta(days=10)),
        "exp_date": str(today + timedelta(days=365)),
        "quantity": 5000,
        "mrp": 40.0
    }, headers=headers2)
    assert cross_res.status_code == 403
    assert "Cannot create batches for medicines belonging to another organization" in cross_res.json()["detail"]
