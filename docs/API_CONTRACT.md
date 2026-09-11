# Smart Medicine Platform — Shared API Contract Specification

> **CRITICAL ARCHITECTURAL CONTRACT**: This document represents the binding REST API contract between the four platform modules (`backend`, `web`, `layout-engine`, `mobile`).
>
> **RULE**: No teammate should silently change an API response structure. If an API contract changes, this document MUST be updated first and all affected teammates notified before code modifications.

---

## Standard Status Codes & Global Error Format

### HTTP Status Codes
* `200 OK`: Request succeeded.
* `201 Created`: Resource successfully created.
* `400 Bad Request`: Validation failure or invalid parameters.
* `401 Unauthorized`: Missing or invalid authentication token.
* `403 Forbidden`: Insufficient role-based permissions.
* `404 Not Found`: Target resource does not exist.
* `500 Internal Server Error`: Server failure.

### Global Error Response Schema
```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable error description.",
    "details": []
  }
}
```

---

## 1. Authentication APIs

### Endpoint: Login User
* **Endpoint**: `/api/v1/auth/login`
* **HTTP Method**: `POST`
* **Authentication**: None (Public)
* **Request**:
  ```json
  {
    "username": "placeholder_string",
    "password": "placeholder_string"
  }
  ```
* **Response**:
  ```json
  {
    "access_token": "placeholder_jwt_token",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "placeholder_uuid",
      "username": "placeholder_string",
      "role": "admin|manufacturer|user"
    }
  }
  ```
* **Error Responses**: `400 Bad Request`, `401 Unauthorized`

---

## 2. Medicines APIs

### Endpoint: List Medicines
* **Endpoint**: `/api/v1/medicines`
* **HTTP Method**: `GET`
* **Authentication**: Bearer Token
* **Request**: Query parameters `?page=1&limit=20`
* **Response**:
  ```json
  {
    "total": 0,
    "items": [
      {
        "id": "placeholder_uuid",
        "name": "placeholder_string",
        "dosage": "placeholder_string",
        "manufacturer": "placeholder_string"
      }
    ]
  }
  ```
* **Error Responses**: `401 Unauthorized`

---

## 3. Batches APIs

### Endpoint: Create Batch
* **Endpoint**: `/api/v1/batches`
* **HTTP Method**: `POST`
* **Authentication**: Bearer Token (Manufacturer / Admin)
* **Request**:
  ```json
  {
    "medicine_id": "placeholder_uuid",
    "batch_number": "placeholder_string",
    "manufacturing_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "quantity": 1000
  }
  ```
* **Response**:
  ```json
  {
    "id": "placeholder_uuid",
    "batch_number": "placeholder_string",
    "status": "created",
    "created_at": "timestamp"
  }
  ```
* **Error Responses**: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`

---

## 4. Code Generation APIs

### Endpoint: Generate Batch DataMatrix/QR Codes
* **Endpoint**: `/api/v1/codes/generate`
* **HTTP Method**: `POST`
* **Authentication**: Bearer Token
* **Request**:
  ```json
  {
    "batch_id": "placeholder_uuid",
    "code_type": "DATAMATRIX|QR",
    "count": 100
  }
  ```
* **Response**:
  ```json
  {
    "batch_id": "placeholder_uuid",
    "generated_count": 100,
    "codes": [
      {
        "serial_number": "placeholder_serial",
        "verification_url": "placeholder_url",
        "code_data": "placeholder_encoded_data"
      }
    ]
  }
  ```
* **Error Responses**: `400 Bad Request`, `401 Unauthorized`

---

## 5. Code Verification APIs

### Endpoint: Verify Code / Scan
* **Endpoint**: `/api/v1/verification/verify`
* **HTTP Method**: `POST`
* **Authentication**: Optional / Public
* **Request**:
  ```json
  {
    "code_data": "placeholder_scanned_raw_string",
    "latitude": 0.0,
    "longitude": 0.0,
    "source": "mobile_app|web_portal"
  }
  ```
* **Response**:
  ```json
  {
    "is_valid": true,
    "verification_status": "AUTHENTIC|EXPIRED|SUSPECTED_COUNTERFEIT|RECALLED",
    "medicine": {
      "name": "placeholder_name",
      "dosage": "placeholder_dosage",
      "manufacturer": "placeholder_manufacturer"
    },
    "batch": {
      "batch_number": "placeholder_batch",
      "expiry_date": "YYYY-MM-DD"
    }
  }
  ```
* **Error Responses**: `400 Bad Request`, `404 Not Found`

---

## 6. Scan History APIs

### Endpoint: Get Scan History
* **Endpoint**: `/api/v1/scans/history`
* **HTTP Method**: `GET`
* **Authentication**: Bearer Token
* **Request**: Query parameters `?user_id=placeholder_uuid`
* **Response**:
  ```json
  {
    "total": 0,
    "history": [
      {
        "scan_id": "placeholder_uuid",
        "scanned_at": "timestamp",
        "medicine_name": "placeholder_name",
        "is_valid": true
      }
    ]
  }
  ```
* **Error Responses**: `401 Unauthorized`

---

## 7. Layout Optimization & Recommendation APIs

> **ARCHITECTURAL SCOPE & BOUNDARIES**:
> - The Layout Engine (`/layout-engine/`, port `8001`) operates **purely in-memory** and **does NOT connect to PostgreSQL**.
> - The Layout Engine does **NOT verify pharmaceutical authenticity or cryptographic signatures**. Verification is exclusively handled by `/api/v1/verification/verify`.
> - For identical packaging inputs, the Layout Engine produces deterministic, collision-free placements.

### Endpoint: Optimize Package Layout (Primary Integration Route)
* **Endpoint**: `/api/v1/layout/optimize`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Description**: Accepts either standard `LayoutRequest` or structured backend print data (incorporating `medicine`, `batch`, and `code`/`codes` from `/api/v1/medicines`, `/api/v1/batches`, and `/api/v1/codes/generate`).
* **Field Mappings**:
  - `dosage` → `strength`
  - `batch_number` → `batch`
  - `manufacturing_date` → `mfg`
  - `expiry_date` → `exp`
  - `serial_number` → human-readable serial text (`id="serial_no"`, formatted `"SN: <serial_number>"`)
  - Authoritative values are preserved; aliases never overwrite existing fields.
* **Code Support**:
  - Symbologies: `QR` (`qr`, `qrcode`), `DATAMATRIX` (`datamatrix`), `BARCODE`, `HUMAN_READABLE` (case-insensitive).
  - Square Sizing: When only `min_size_mm` / `minimum_code_size_mm` is provided for QR/DataMatrix, width and height default to square (`min_size` $\times$ `min_size`).
  - Dual Codes: Supports concurrent placement of a scannable 2D code (`batch_code`) and human-readable serial text (`serial_no`).
* **Structured Backend Request Example**:
  ```json
  {
    "package": {
      "package_width_mm": 120.0,
      "package_height_mm": 60.0,
      "printing_area_width_mm": 105.0,
      "printing_area_height_mm": 50.0,
      "printing_area_x_mm": 7.5,
      "printing_area_y_mm": 5.0
    },
    "tablet": {
      "tablet_count": 6,
      "tablet_diameter_mm": 9.0
    },
    "medicine": {
      "name": "Amoxicillin and Potassium Clavulanate",
      "dosage": "625 mg",
      "manufacturer": "HealthGuard Pharma"
    },
    "batch": {
      "batch_number": "BN-2026-9901",
      "manufacturing_date": "2026-03-01",
      "expiry_date": "2028-03-01"
    },
    "code": {
      "type": "QR",
      "value": "https://rx.zero-latency.org/v/BN20269901",
      "min_size_mm": 12.0,
      "serial_number": "SN-9901-7788"
    },
    "optimization_target": "RECOMMEND"
  }
  ```
* **Response**:
  ```json
  {
    "id": "layout_recommendation_accessibility_001",
    "success": true,
    "recommended_strategy": "ACCESSIBILITY",
    "score": 82.15,
    "space_utilization": 0.54,
    "readability": 0.94,
    "print_efficiency": 0.81,
    "scan_reliability": 0.96,
    "cost_efficiency": 0.54,
    "package": { "..." : "..." },
    "elements": [
      { "id": "cavity_1", "type": "tablet_cavity", "x_mm": 77.0, "y_mm": 20.0, "width_mm": 9.0, "height_mm": 9.0 },
      { "id": "med_name", "type": "text", "content": "Amoxicillin and Potassium Clavulanate", "x_mm": 8.5, "y_mm": 6.0, "width_mm": 85.1, "height_mm": 4.8 },
      { "id": "med_strength", "type": "text", "content": "625 mg", "x_mm": 8.5, "y_mm": 12.8, "width_mm": 16.0, "height_mm": 4.2 },
      { "id": "batch_no", "type": "text", "content": "B.No: BN-2026-9901", "x_mm": 8.5, "y_mm": 19.0, "width_mm": 32.4, "height_mm": 3.2 },
      { "id": "mfg_date", "type": "text", "content": "MFG: 2026-03-01", "x_mm": 26.5, "y_mm": 12.8, "width_mm": 27.0, "height_mm": 3.0 },
      { "id": "exp_date", "type": "text", "content": "EXP: 2028-03-01", "x_mm": 8.5, "y_mm": 24.2, "width_mm": 27.0, "height_mm": 3.0 },
      { "id": "batch_code", "type": "code", "content": "https://rx.zero-latency.org/v/BN20269901", "code_type": "qr", "x_mm": 95.6, "y_mm": 6.0, "width_mm": 12.0, "height_mm": 12.0 },
      { "id": "serial_no", "type": "text", "content": "SN: SN-9901-7788", "x_mm": 42.9, "y_mm": 19.0, "width_mm": 28.8, "height_mm": 3.0 },
      { "id": "manufacturer", "type": "text", "content": "Mfd: HealthGuard Pharma", "x_mm": 55.5, "y_mm": 12.8, "width_mm": 36.8, "height_mm": 3.0 }
    ],
    "alternatives": [
      { "strategy": "ACCESSIBILITY", "score": 82.15 },
      { "strategy": "BALANCED", "score": 81.88 },
      { "strategy": "COST", "score": 80.45 }
    ],
    "validation": { "valid": true, "errors": [], "warnings": [] }
  }
  ```
* **Error Responses**: `422 Unprocessable Entity` (Validation), `200 OK with success: false` (Placement failure)

### Endpoint: Recommend Package Layout (Retained Compatibility Route)
* **Endpoint**: `/api/layouts/recommend`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**: Standard `LayoutRequest` object with `package`, `tablet`, `code`, `information`, `constraints`.
* **Response**: Same `LayoutPlan` structure as `/api/v1/layout/optimize`.

---

## 8. Layout Preview & Export APIs

### Endpoint: Render Layout SVG Preview
* **Endpoint**: `/api/layouts/preview`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**:
  ```json
  {
    "layout": null,
    "request": {
      "package": { "..." : "..." },
      "tablet": { "..." : "..." },
      "code": { "..." : "..." },
      "information": { "..." : "..." }
    }
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "layout_id": "layout_recommendation_balanced_001",
    "validation": { "valid": true, "errors": [], "warnings": [] },
    "svg": "<svg ...>...</svg>"
  }
  ```
* **Error Responses**: `422 Unprocessable Entity`, `400 Bad Request`

### Endpoint: Export Layout PDF
* **Endpoint**: `/api/layouts/pdf`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**:
  ```json
  {
    "layout": null,
    "request": { "..." : "..." }
  }
  ```
* **Response**: Binary stream with `Content-Type: application/pdf` and `Content-Disposition: inline; filename="{layout_id}.pdf"`.
* **Error Responses**: `422 Unprocessable Entity`, `400 Bad Request` (Placement failure)

---

## 9. Voice Assistant APIs

### Endpoint: Process Voice / Chat Query
* **Endpoint**: `/api/v1/assistant/query`
* **HTTP Method**: `POST`
* **Authentication**: Bearer Token / API Key
* **Request**:
  ```json
  {
    "session_id": "placeholder_uuid",
    "input_type": "TEXT|AUDIO",
    "query_text": "placeholder_user_query",
    "context": {
      "current_medicine_id": "placeholder_uuid"
    }
  }
  ```
* **Response**:
  ```json
  {
    "session_id": "placeholder_uuid",
    "response_text": "placeholder_assistant_response",
    "audio_url": "placeholder_tts_audio_url",
    "suggested_actions": []
  }
  ```
* **Error Responses**: `400 Bad Request`, `500 Internal Server Error`
