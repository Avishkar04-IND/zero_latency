# API Contract — Smart Medicine Identification & Verification Platform

> **Version:** 1.0.0  
> **Base URL:** `http://localhost:8000/api/v1`  
> **Swagger UI:** `http://localhost:8000/docs`  
> **ReDoc:** `http://localhost:8000/redoc`

This contract is shared across **Member 1 (Backend)**, **Member 2 (Web Admin)**, and **Member 3 (Mobile Client)**.  
Any alterations to existing endpoints or payload structures must be updated here first.

---

## 1. Authentication & Session

### `POST /auth/login`
Authenticates company admin, inspector, or consumer.

* **Request Body:**
```json
{
  "email": "admin@pharma.com",
  "password": "Admin@12345"
}
```

* **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "name": "Dr. Rajiv Sharma",
  "email": "admin@pharma.com",
  "role": "ORG_ADMIN",
  "organization_id": 1,
  "organization_name": "Apex National Pharma",
  "branch_id": 1,
  "branch_name": "Mumbai Unit 1"
}
```

### `POST /auth/refresh`
Refreshes the caller's JWT access token.

* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "role": "ORG_ADMIN",
  "organization_id": 1,
  "branch_id": 1
}
```

### `POST /auth/logout`
Acknowledges user logout.

* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
```json
{
  "status": "success",
  "message": "Successfully logged out"
}
```

---

## 2. Organizations & Branch Hierarchy

### `GET /organizations/me`
Retrieves the authenticated user's organization profile and its registered manufacturing branches.

* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
```json
{
  "id": 1,
  "name": "Apex National Pharma",
  "licence_no": "LIC-MH-2026-001",
  "contact_email": "admin@apexpharma.com",
  "contact_phone": "+91-22-24900000",
  "address": "Worli Pharma City, Mumbai",
  "created_at": "2026-09-11T07:24:50Z",
  "branches": [
    {
      "id": 1,
      "organization_id": 1,
      "name": "Mumbai Unit 1",
      "code": "BR-MUM-01",
      "city": "Mumbai",
      "state": "Maharashtra",
      "contact_phone": "+91-22-12345678",
      "is_active": true,
      "created_at": "2026-09-11T08:00:00Z"
    }
  ]
}
```

### `GET /branches`
Lists branches scoped to the caller's organization.

* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "name": "Mumbai Unit 1",
    "code": "BR-MUM-01",
    "city": "Mumbai",
    "state": "Maharashtra",
    "contact_email": "mumbai.unit1@pharma.com",
    "contact_phone": "+91-22-12345678",
    "is_active": true,
    "created_at": "2026-09-11T08:00:00Z"
  }
]
```

### `POST /branches`
Creates a new branch / manufacturing facility. Organization is derived server-side from caller's token.

* **Headers:** `Authorization: Bearer <token>` (Requires `ORG_ADMIN` or `SUPER_ADMIN`)
* **Request Body:**
```json
{
  "name": "Bhiwandi Packaging Unit",
  "code": "BR-BHW-02",
  "address": "Bhiwandi Logistics Hub",
  "city": "Bhiwandi",
  "state": "Maharashtra",
  "contact_phone": "+91-22-98765432"
}
```

* **Response (201 Created):**
```json
{
  "id": 2,
  "organization_id": 1,
  "name": "Bhiwandi Packaging Unit",
  "code": "BR-BHW-02",
  "address": "Bhiwandi Logistics Hub",
  "city": "Bhiwandi",
  "state": "Maharashtra",
  "contact_phone": "+91-22-98765432",
  "is_active": true,
  "created_at": "2026-09-11T08:15:00Z"
}
```

---

## 3. Medicine Catalog & Tablet Composition

### `GET /medicines`
Lists medicines with live search and category filters.

* **Query Parameters:**
  - `q` (string, optional): Search keyword (matches brand or generic name).
  - `category` (string, optional): Therapeutic category filter.
  - `limit` (integer, default `100`): Pagination page size.
  - `offset` (integer, default `0`): Pagination offset.

* **Response (200 OK):**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "brand_name": "Dolo-650",
    "generic_name": "Paracetamol Tablets IP",
    "category": "Analgesic & Antipyretic",
    "manufacturer": "Micro Labs Limited",
    "dosage_form": "Tablet",
    "strength": "650 mg",
    "active_ingredients": [
      {
        "name": "Paracetamol IP",
        "strength": "650",
        "unit": "mg",
        "purpose": "Active Analgesic & Antipyretic"
      }
    ],
    "inactive_excipients": [
      "Starch IP",
      "Microcrystalline Cellulose",
      "Povidone K-30",
      "Sodium Starch Glycolate",
      "Magnesium Stearate"
    ],
    "tablet_shape": "Capsule-shaped",
    "tablet_color": "White",
    "score_line": "Single break-line on one side",
    "coating_type": "Uncoated",
    "indications": "Relief of mild to moderate pain including headache, body ache, toothache, and reduction of fever.",
    "dosage_instructions": "Take 1 tablet every 6 to 8 hours with water. Maximum 4 tablets in 24 hours. Do not exceed.",
    "warnings_and_precautions": "Overdose may cause serious liver damage. Avoid consumption with alcohol.",
    "side_effects": "Rare: allergic skin rash, nausea.",
    "storage_conditions": "Store below 30°C in a dry place.",
    "schedule_type": "OTC",
    "voice_summary_en": "Dolo 650 milligram tablet. Contains Paracetamol. For fever and body pain.",
    "voice_summary_hi": "डोलो 650 मिलीग्राम टैबलेट। इसमें पैरासिटामोल है। यह बुखार और दर्द के लिए है।",
    "voice_summary_mr": "डोलो 650 मिलिगॅ्रम गोळी. यात पॅरासिटामॉल आहे. ताप आणि अंगदुखीसाठी.",
    "created_at": "2026-09-11T07:24:50Z"
  }
]
```

### `GET /medicines/{id}`
Returns full technical details and chemical composition for a single medicine record.

### `POST /medicines`
Creates a new master medicine formulation. Organization ID is automatically derived from the authenticated caller's context.

* **Headers:** `Authorization: Bearer <token>`
* **Request Body:** Complete tablet composition object (brand name, generic name, active ingredients JSON, excipients, tablet shape, color, warnings, voice summaries).
* **Response (201 Created):** MedicineResponse object with assigned ID.

### `PATCH /medicines/{id}`
Partially updates medicine specifications, warnings, or lifecycle status (`active`, `discontinued`, `under_review`).

* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):** Updated MedicineResponse object.

---

## 4. Production Batch Management

### `POST /batches`
Creates a manufacturing batch for a registered medicine. Server-side validation requires `exp_date > mfg_date` and `quantity > 0`. Creator identity (`created_by`) and branch facility (`branch_id`) are derived server-side.

* **Headers:** `Authorization: Bearer <token>` (Requires `ORG_ADMIN`, `BRANCH_ADMIN`, or `OPERATOR`)
* **Request Body:**
```json
{
  "medicine_id": 1,
  "batch_no": "BT-2026-101",
  "mfg_date": "2026-06-01",
  "exp_date": "2028-09-01",
  "quantity": 50000,
  "mrp": 32.50,
  "status": "active",
  "branch_id": 1
}
```

* **Response (201 Created):**
```json
{
  "id": 1,
  "medicine_id": 1,
  "branch_id": 1,
  "created_by": 1,
  "batch_no": "BT-2026-101",
  "mfg_date": "2026-06-01",
  "exp_date": "2028-09-01",
  "quantity": 50000,
  "mrp": 32.50,
  "status": "active",
  "created_at": "2026-09-11T08:30:00Z"
}
```

### `GET /batches`
Lists manufacturing batches with optional filtering by `medicine_id`, `branch_id`, or `status_filter`. Automatically scopes to the caller's organization.

### `GET /batches/{id}`
Returns batch record with auto-populated registered medicine specifications and branch name.

### `PATCH /batches/{id}`
Updates batch attributes, such as updating quantity or setting `status: "recalled"`.

---

## 5. Code Generation (Manufacturer / Web Admin)

### `POST /codes/generate`
Generates cryptographically unique, non-sequential serial identifiers and QR/DataMatrix print assets.

* **Headers:** `Authorization: Bearer <token>`
* **Request Body:**
```json
{
  "batch_id": 1,
  "count": 5
}
```

* **Response (201 Created):**
```json
{
  "total_generated": 5,
  "batch_id": 1,
  "batch_no": "BT-2026-101",
  "medicine_name": "Dolo-650",
  "codes": [
    {
      "id": 101,
      "batch_id": 1,
      "serial_number": "MED-7F2A-9C14-B83D",
      "code_hash": "a4f890123ef...",
      "qr_data_url": "data:image/png;base64,iVBORw0KGgo...",
      "qr_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" ...</svg>",
      "datamatrix_code": "(01)08901234567890(17)280911(10)BT-2026-101(21)MED-7F2A-9C14-B83D",
      "status": "active",
      "scan_count": 0,
      "first_scanned_at": null,
      "created_at": "2026-09-11T07:24:50Z"
    }
  ]
}
```

### `GET /codes/{serial}/svg`
Streams the high-resolution vector SVG directly (`image/svg+xml`) for packaging print assets.

---

## 6. Layout Engine Print Data Integration (Member 3 & Web Admin)

The Layout Engine and Web Admin retrieve backend-authoritative packaging specifications, manufacturer identity, and pre-formatted label lines without directly accessing the database.

### `GET /layouts/print-data/{code_or_serial}`
Fetches verified structured printing data for a specific package unit code or serial (e.g. `MD110` or `MD110-X7K9`).

* **Response (200 OK):**
```json
{
  "code": "MD110-X7K9",
  "serial_number": "MD110-X7K9",
  "code_hash": "a4f890123ef...",
  "datamatrix_code": "(01)08901234567890(17)280911(10)BT-2026-101(21)MD110-X7K9",
  "qr_svg": "<svg ...</svg>",
  "qr_data_url": "data:image/png;base64,...",
  "medicine": {
    "name": "Dolo-650",
    "generic_name": "Paracetamol Tablets IP",
    "strength": "650 mg",
    "dosage_form": "Tablet",
    "tablet_shape": "Capsule-shaped",
    "tablet_color": "White",
    "coating_type": "Uncoated",
    "storage_conditions": "Store below 30°C in a dry place."
  },
  "batch": {
    "batch_number": "BT-2026-101",
    "mfg_date": "2026-06-01",
    "exp_date": "2028-09-01",
    "quantity": 50000,
    "mrp": 32.50,
    "status": "active"
  },
  "manufacturer": {
    "name": "Micro Labs Limited",
    "licence_no": "LIC-MH-2026-001",
    "contact_email": "admin@microlabs-demo.com",
    "address": "Race Course Road, Bangalore"
  },
  "branch": {
    "name": "Mumbai Formulation Facility",
    "code": "BR-MUM-01",
    "city": "Mumbai",
    "state": "Maharashtra"
  },
  "warnings": [
    "Overdose may cause serious liver damage. Avoid consumption with alcohol."
  ],
  "print_data": {
    "line1_header": "Dolo-650 650 mg",
    "line2_generic": "Generic: Paracetamol Tablets IP",
    "line3_batch_exp": "B.No: BT-2026-101 | Mfg: 2026-06-01 | Exp: 2028-09-01",
    "line4_mrp": "MRP Rs. 32.50 (Inclusive of all taxes)",
    "line5_storage": "Storage: Store below 30°C in a dry place.",
    "line6_license": "Mfg. Lic. No: LIC-MH-2026-001",
    "barcode_payload": "(01)08901234567890(17)280911(10)BT-2026-101(21)MD110-X7K9"
  }
}
```

### `GET /layouts/print-data/batch/{batch_id}`
Returns the batch packaging template specifications along with all generated package unit codes for multi-pack, carton, or blister strip layout generation.

---

## 7. Mobile Code Verification & Authenticity

### `POST /codes/verify`
The primary endpoint called by the **Flutter Mobile App camera scanner**.

* **Request Body:**
```json
{
  "code_or_serial": "MED-7F2A-9C14-B83D",
  "device_info": "Flutter Mobile Android 14",
  "latitude": 19.0760,
  "longitude": 72.8777
}
```

*Note: `code_or_serial` accepts direct serial numbers, full scanned URLs (`https://smartmed.org/v/MED-...`), or GS1 DataMatrix strings.*

* **Response 1: Genuine Medicine (200 OK):**
```json
{
  "status": "GENUINE",
  "is_genuine": true,
  "risk_score": 0,
  "risk_reasons": [],
  "scanned_serial": "MED-7F2A-9C14-B83D",
  "scan_count": 1,
  "message": "Verified Genuine: Dolo-650 (Paracetamol Tablets IP) is authentic.",
  "verified_at": "2026-09-11T07:30:00Z",
  "medicine": {
    "brand_name": "Dolo-650",
    "generic_name": "Paracetamol Tablets IP",
    "strength": "650 mg",
    "dosage_form": "Tablet",
    "active_ingredients": [
      {
        "name": "Paracetamol IP",
        "strength": "650",
        "unit": "mg",
        "purpose": "Active Analgesic & Antipyretic"
      }
    ],
    "dosage_instructions": "Take 1 tablet every 6 to 8 hours with water.",
    "warnings_and_precautions": "Overdose may cause serious liver damage."
  },
  "batch": {
    "batch_no": "BT-2026-101",
    "mfg_date": "2026-06-13",
    "exp_date": "2028-09-01",
    "mrp": 32.5
  },
  "voice_guidance": {
    "status_alert": "Genuine verified medicine",
    "medicine_info": "Dolo-650 650 mg, generic Paracetamol Tablets IP.",
    "expiry_info": "Expiry date is September 2028.",
    "instructions": "Take 1 tablet every 6 to 8 hours with water."
  }
}
```

* **Response 2: Counterfeit / Invalid Code (200 OK):**
```json
{
  "status": "INVALID",
  "is_genuine": false,
  "risk_score": 100,
  "risk_reasons": [
    "Unregistered serial number: Code does not exist in the official manufacturer database"
  ],
  "scanned_serial": "MED-FAKE-0000",
  "scan_count": 1,
  "message": "ALERT: Counterfeit / Invalid Code detected. This medicine package is unverified and potentially unsafe.",
  "verified_at": "2026-09-11T07:30:00Z",
  "medicine": null,
  "batch": null,
  "voice_guidance": {
    "alert": "Warning! Unverified or counterfeit medicine.",
    "action": "Do not consume. Contact your pharmacist immediately."
  }
}
```

* **Response 3: Expired Medicine (200 OK):**
```json
{
  "status": "EXPIRED",
  "is_genuine": false,
  "risk_score": 75,
  "risk_reasons": [
    "Medicine expired on August 12, 2024"
  ],
  "scanned_serial": "EXP-2A1B-3C4D-5E6F",
  "scan_count": 2,
  "message": "EXPIRED MEDICINE: Taxim-O 200 reached expiry on 2024-08-12. Do NOT consume.",
  "medicine": { "brand_name": "Taxim-O 200" }
}
```

* **Response 4: Suspicious Scan Anomaly (200 OK):**
```json
{
  "status": "SUSPICIOUS_MULTIPLE_SCANS",
  "is_genuine": false,
  "risk_score": 85,
  "risk_reasons": [
    "Abnormal scan frequency: This unit code has been scanned 9 times."
  ],
  "message": "SUSPICIOUS ACTIVITY: Code scanned 9 times. Verify physical foil integrity."
}
```

---

---

## 8. Accessibility & Multilingual Voice Synthesis

### `GET /accessibility/medicine/{id}/voice?lang=en`
Generates voice-synthesizer text for Flutter TTS and Android TalkBack.

* **Query Parameters:**
  - `lang`: `en` (English), `hi` (Hindi), `mr` (Marathi)

* **Response (200 OK):**
```json
{
  "language": "en",
  "medicine_id": 1,
  "brand_name": "Dolo-650",
  "generic_name": "Paracetamol Tablets IP",
  "full_spoken_summary": "Dolo 650 milligram tablet. Contains Paracetamol. For fever and body pain. Take one tablet every 6 hours after meals.",
  "sections": {
    "overview": "Medicine: Dolo-650. Generic: Paracetamol Tablets IP. Strength: 650 mg.",
    "composition": "Active contents: Paracetamol IP 650 mg. Physical form: Capsule-shaped, Uncoated tablet.",
    "dosage": "Take 1 tablet every 6 to 8 hours with water. Maximum 4 tablets in 24 hours.",
    "warnings": "Overdose may cause serious liver damage. Avoid consumption with alcohol.",
    "storage": "Store below 30°C in a dry place."
  },
  "supported_voice_commands": [
    "Scan medicine",
    "Repeat",
    "Next",
    "Expiry",
    "Warnings",
    "Go back"
  ]
}
```

---

## 9. Analytics & Audit Trail

### `GET /analytics/dashboard`
Returns live platform KPIs for the Web Admin dashboard.

### `GET /analytics/overview`
Authoritative summary of total registered medicines, batches, codes, total scans, authenticity percentage, and batch status counts.

* **Response (200 OK):**
```json
{
  "total_medicines": 50,
  "total_batches": 50,
  "total_codes_generated": 100,
  "total_scans": 24,
  "authenticity_rate": 91.7,
  "active_batches": 48,
  "quarantined_batches": 1,
  "recalled_batches": 0,
  "expired_batches": 1
}
```

### `GET /analytics/risk`
Calculates platform risk metrics, average risk score, low/medium/high scan classifications, and returns active counterfeit anomaly alerts.

* **Response (200 OK):**
```json
{
  "average_risk_score": 8.5,
  "low_risk_scans": 22,
  "medium_risk_scans": 1,
  "high_risk_scans": 1,
  "counterfeit_alert_count": 2,
  "recent_alerts": [
    {
      "id": 12,
      "serial": "MED-FAKE-9999",
      "result": "INVALID",
      "risk_score": 100,
      "device": "Flutter Scanner Android 14",
      "time": "2026-09-11T20:30:00Z",
      "risk_reasons": ["Unregistered serial number"]
    }
  ]
}
```

### `GET /analytics/batches`
Manufacturing batch inventory metrics including status distribution, total manufactured units, and inventory value at MRP.

* **Response (200 OK):**
```json
{
  "total_batches": 50,
  "by_status": {
    "active": 48,
    "quarantined": 1,
    "expired": 1
  },
  "total_units_manufactured": 2500000,
  "total_inventory_value_mrp": 125000000.0
}
```

### `GET /analytics/codes`
Code lifecycle KPIs including active, revoked, scanned, and unscanned counts.

* **Response (200 OK):**
```json
{
  "total_codes": 100,
  "active_codes": 98,
  "revoked_codes": 2,
  "scanned_codes": 15,
  "unscanned_codes": 85,
  "max_single_code_scans": 3
}
```

### `GET /analytics/audit-logs`
Provides a tamper-evident audit trail for administrative, production, and security actions. Automatically scoped to the authenticated caller's tenant organization.

* **Headers:** `Authorization: Bearer <token>`
* **Query Parameters:**
  - `action`: Filter by action (e.g. `LOGIN`, `BATCH_CREATED`, `CODE_GENERATED`, `LAYOUT_REQUESTED`)
  - `entity_type`: Filter by entity (e.g. `batch`, `medicine`, `user`, `code`)
  - `user_id`: Filter by actor user ID
  - `limit`: Pagination limit (default 50)
  - `offset`: Pagination offset (default 0)

* **Response (200 OK):**
```json
[
  {
    "id": 101,
    "user_id": 1,
    "organization_id": 1,
    "branch_id": 1,
    "action": "BATCH_CREATED",
    "entity_type": "batch",
    "entity_id": "51",
    "details": {
      "batch_no": "BT-2026-151",
      "medicine_id": 1,
      "quantity": 50000,
      "status": "active"
    },
    "ip_address": "127.0.0.1",
    "created_at": "2026-09-11T20:45:00Z"
  }
]
```
