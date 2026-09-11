def test_create_and_get_medicine(client):
    # 1. Sign up admin
    res = client.post("/api/v1/auth/signup", json={
        "name": "Admin Tester",
        "email": "tester@apex.com",
        "password": "Password123!",
        "organization_name": "Apex Pharma",
        "licence_no": "LIC-001"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Medicine with full tablet contents
    medicine_payload = {
        "brand_name": "Paracip 500",
        "generic_name": "Paracetamol Tablets IP",
        "category": "Analgesic",
        "manufacturer": "Cipla Ltd",
        "dosage_form": "Tablet",
        "strength": "500 mg",
        "active_ingredients": [
            {"name": "Paracetamol IP", "strength": "500", "unit": "mg", "purpose": "Analgesic & Antipyretic"}
        ],
        "inactive_excipients": ["Starch", "Povidone", "Magnesium Stearate"],
        "tablet_shape": "Round",
        "tablet_color": "White",
        "score_line": "Bisected",
        "coating_type": "Uncoated",
        "indications": "Fever and headache.",
        "dosage_instructions": "Take 1 tablet every 6 hours.",
        "warnings_and_precautions": "Do not exceed 4000mg per day.",
        "storage_conditions": "Store below 30°C.",
        "schedule_type": "OTC"
    }
    create_res = client.post("/api/v1/medicines", json=medicine_payload, headers=headers)
    assert create_res.status_code == 201, create_res.text
    med_data = create_res.json()
    assert med_data["brand_name"] == "Paracip 500"
    assert len(med_data["active_ingredients"]) == 1
    assert med_data["active_ingredients"][0]["name"] == "Paracetamol IP"

    # 3. Retrieve medicine list & search
    list_res = client.get("/api/v1/medicines?q=Paracip")
    assert list_res.status_code == 200
    results = list_res.json()
    assert len(results) >= 1
    assert results[0]["brand_name"] == "Paracip 500"
