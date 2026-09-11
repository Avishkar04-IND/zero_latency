import json
from datetime import date, timedelta
from backend.app.services.audit_service import sanitize_details, log_audit_event
from backend.app.models.audit_log import AuditLog
from backend.app.models.organization import Organization
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.scan import Scan


def test_audit_service_sanitization():
    payload = {
        "username": "tester",
        "password": "SecretPassword123!",
        "token": "jwt.token.here",
        "nested": {
            "api_key": "abc-123-secret",
            "safe_field": "visible_value"
        }
    }
    sanitized = sanitize_details(payload)
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["safe_field"] == "visible_value"
    assert sanitized["username"] == "tester"


def test_log_audit_event(db_session):
    event = log_audit_event(
        db=db_session,
        action="TEST_ACTION",
        user_id=1,
        organization_id=2,
        branch_id=3,
        entity_type="test_entity",
        entity_id="101",
        details={"key": "value", "password": "sensitive"},
        ip_address="127.0.0.1",
        commit=True,
    )
    assert event is not None
    assert event.id is not None
    assert event.action == "TEST_ACTION"
    assert event.entity_type == "test_entity"
    assert event.entity_id == "101"

    loaded = db_session.query(AuditLog).filter(AuditLog.id == event.id).first()
    assert loaded is not None
    details = json.loads(loaded.details)
    assert details["key"] == "value"
    assert details["password"] == "[REDACTED]"


def test_auth_audit_trail(client, db_session):
    # 1. Signup
    signup_payload = {
        "name": "Audit Tester",
        "email": "audit.test@pharma.com",
        "password": "Password123!",
        "role": "ORG_ADMIN",
        "organization_name": "Audit Test Labs",
        "licence_no": "LIC-AUDIT-01"
    }
    res_signup = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res_signup.status_code == 201

    # 2. Login
    login_payload = {
        "email": "audit.test@pharma.com",
        "password": "Password123!"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Refresh
    res_refresh = client.post("/api/v1/auth/refresh", headers=headers)
    assert res_refresh.status_code == 200

    # 4. Logout
    res_logout = client.post("/api/v1/auth/logout", headers=headers)
    assert res_logout.status_code == 200

    # Verify audit logs in database
    actions = [log.action for log in db_session.query(AuditLog).all()]
    assert "USER_REGISTERED" in actions
    assert "LOGIN" in actions
    assert "REFRESH_TOKEN" in actions
    assert "LOGOUT" in actions


def test_analytics_endpoints(client, db_session):
    # 1. Overview
    res_overview = client.get("/api/v1/analytics/overview")
    assert res_overview.status_code == 200
    ov_data = res_overview.json()
    assert "total_medicines" in ov_data
    assert "total_batches" in ov_data
    assert "total_codes_generated" in ov_data
    assert "authenticity_rate" in ov_data
    assert "active_batches" in ov_data

    # 2. Risk
    res_risk = client.get("/api/v1/analytics/risk")
    assert res_risk.status_code == 200
    risk_data = res_risk.json()
    assert "average_risk_score" in risk_data
    assert "counterfeit_alert_count" in risk_data

    # 3. Batches
    res_batches = client.get("/api/v1/analytics/batches")
    assert res_batches.status_code == 200
    batches_data = res_batches.json()
    assert "total_batches" in batches_data
    assert "by_status" in batches_data
    assert "total_units_manufactured" in batches_data

    # 4. Codes
    res_codes = client.get("/api/v1/analytics/codes")
    assert res_codes.status_code == 200
    codes_data = res_codes.json()
    assert "total_codes" in codes_data
    assert "active_codes" in codes_data
    assert "scanned_codes" in codes_data


def test_analytics_audit_logs_query(client, db_session):
    # Setup test org and admin
    signup_payload = {
        "name": "Audit Query Admin",
        "email": "audit.query@pharma.com",
        "password": "Password123!",
        "role": "ORG_ADMIN",
        "organization_name": "Audit Query Pharma",
        "licence_no": "LIC-AQ-01"
    }
    res = client.post("/api/v1/auth/signup", json=signup_payload)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query audit logs
    res_logs = client.get("/api/v1/analytics/audit-logs", headers=headers)
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert any(l["action"] == "USER_REGISTERED" for l in logs)

    # Query with filter
    res_filtered = client.get("/api/v1/analytics/audit-logs?action=USER_REGISTERED", headers=headers)
    assert res_filtered.status_code == 200
    filtered_logs = res_filtered.json()
    assert all(l["action"] == "USER_REGISTERED" for l in filtered_logs)


def test_batch_and_layout_audit_logging(client, db_session):
    # Register org admin
    signup_payload = {
        "name": "Audit Batch Admin",
        "email": "audit.batch@pharma.com",
        "password": "Password123!",
        "role": "ORG_ADMIN",
        "organization_name": "Audit Batch Pharma",
        "licence_no": "LIC-AB-01"
    }
    res = client.post("/api/v1/auth/signup", json=signup_payload)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create medicine
    med_payload = {
        "brand_name": "AuditCillin",
        "generic_name": "Amoxicillin",
        "category": "Antibiotic",
        "manufacturer": "Audit Batch Pharma",
        "strength": "500 mg",
        "active_ingredients": [{"name": "Amoxicillin", "strength": "500", "unit": "mg"}],
        "indications": "Bacterial infections",
        "dosage_instructions": "1 tablet every 8 hours",
        "warnings_and_precautions": "Complete full course"
    }
    res_med = client.post("/api/v1/medicines", json=med_payload, headers=headers)
    assert res_med.status_code == 201
    med_id = res_med.json()["id"]

    # Create batch
    today = date.today()
    batch_payload = {
        "medicine_id": med_id,
        "batch_no": "BT-AUDIT-001",
        "mfg_date": str(today - timedelta(days=30)),
        "exp_date": str(today + timedelta(days=365)),
        "quantity": 10000,
        "mrp": 75.0,
        "status": "active"
    }
    res_batch = client.post("/api/v1/batches", json=batch_payload, headers=headers)
    assert res_batch.status_code == 201
    batch_id = res_batch.json()["id"]

    # Update batch
    res_patch = client.patch(f"/api/v1/batches/{batch_id}", json={"status": "quarantined"}, headers=headers)
    assert res_patch.status_code == 200

    # Generate code
    res_code = client.post("/api/v1/codes/generate", json={"batch_id": batch_id, "count": 1, "prefix": "AUD"}, headers=headers)
    assert res_code.status_code == 201
    serial = res_code.json()["codes"][0]["serial_number"]

    # Query layout print data
    res_layout = client.get(f"/api/v1/layouts/print-data/{serial}")
    assert res_layout.status_code == 200

    # Query batch layout print data
    res_batch_layout = client.get(f"/api/v1/layouts/print-data/batch/{batch_id}")
    assert res_batch_layout.status_code == 200

    # Check that audit log has recorded each event
    recorded_actions = [l.action for l in db_session.query(AuditLog).all()]
    assert "BATCH_CREATED" in recorded_actions
    assert "BATCH_UPDATED" in recorded_actions
    assert "CODE_GENERATED" in recorded_actions
    assert "LAYOUT_REQUESTED" in recorded_actions
    assert "LAYOUT_BATCH_REQUESTED" in recorded_actions
