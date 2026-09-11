import sys
from fastapi.testclient import TestClient
from backend.app.main import app

# Set UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

client = TestClient(app)

print("=== 1. HEALTH CHECK ===")
res = client.get("/health")
print("Status:", res.status_code, res.json())
assert res.status_code == 200

print("\n=== 2. MEDICINES LIST (TABLET CONTENT) ===")
res = client.get("/api/v1/medicines?limit=3")
data = res.json()
print("Status:", res.status_code, f"Fetched {len(data)} medicines")
first_med = data[0]
print(f"Medicine: {first_med['brand_name']} ({first_med['generic_name']})")
print(f"Form & Strength: {first_med['dosage_form']} {first_med['strength']}")
print(f"Active Ingredients: {first_med['active_ingredients']}")
print(f"Excipients: {first_med['inactive_excipients']}")
assert len(first_med["active_ingredients"]) > 0

print("\n=== 3. ANALYTICS DASHBOARD ===")
res = client.get("/api/v1/analytics/dashboard")
overview = res.json()["overview"]
print("Status:", res.status_code)
print("Overview KPIs:", overview)
assert overview["total_medicines"] >= 50

print("\n=== 4. CODE VERIFICATION CHECK ===")
# Fetch first code from database
codes_res = client.get("/api/v1/medicines")
verify_res = client.post("/api/v1/codes/verify", json={
    "code_or_serial": "MED-FAKE-9999-0000",
    "device_info": "Mobile Scanner Test"
})
print("Counterfeit Verify:", verify_res.status_code, verify_res.json()["status"], verify_res.json()["message"][:50] + "...")
assert verify_res.json()["status"] == "INVALID"

print("\n=== 6. ACCESSIBILITY VOICE (HINDI & MARATHI) ===")
res_hi = client.get(f"/api/v1/accessibility/medicine/{first_med['id']}/voice?lang=hi")
print("Hindi Audio Script:", res_hi.status_code, res_hi.json()["full_spoken_summary"])

res_mr = client.get(f"/api/v1/accessibility/medicine/{first_med['id']}/voice?lang=mr")
print("Marathi Audio Script:", res_mr.status_code, res_mr.json()["full_spoken_summary"])

print("\n>>> ALL SYSTEM VERIFICATION CHECKS COMPLETED AND FULLY FUNCTIONAL! <<<")
