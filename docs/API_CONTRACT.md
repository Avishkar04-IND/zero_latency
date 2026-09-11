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

## 7. Layout Recommendation APIs

### Endpoint: Recommend & Optimize Package Layout
* **Endpoint**: `/api/layouts/recommend`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**:
  ```json
  {
    "package": {
      "package_width_mm": 130.0,
      "package_height_mm": 65.0,
      "printing_area_width_mm": 110.0,
      "printing_area_height_mm": 55.0,
      "printing_area_x_mm": 10.0,
      "printing_area_y_mm": 5.0
    },
    "tablet": {
      "tablet_count": 6,
      "tablet_diameter_mm": 9.0
    },
    "code": {
      "value": "MED001-DM",
      "code_type": "datamatrix",
      "min_size_mm": 12.0
    },
    "information": {
      "medicine_name": "Amoxicillin",
      "strength": "500 mg",
      "batch": "B2026-X",
      "mfg": "2026-03",
      "exp": "2028-03"
    },
    "constraints": {
      "minimum_margin_mm": 2.0,
      "minimum_element_spacing_mm": 1.5
    },
    "optimization_target": "RECOMMEND|COST|BALANCED|ACCESSIBILITY"
  }
  ```
* **Response**:
  ```json
  {
    "id": "layout_recommendation_balanced_001",
    "success": true,
    "recommended_strategy": "BALANCED",
    "score": 83.42,
    "space_utilization": 0.582,
    "readability": 0.880,
    "print_efficiency": 0.850,
    "scan_reliability": 0.940,
    "cost_efficiency": 0.582,
    "package": { "..." : "..." },
    "elements": [],
    "alternatives": [
      { "strategy": "BALANCED", "score": 83.42 },
      { "strategy": "COST", "score": 81.15 },
      { "strategy": "ACCESSIBILITY", "score": 79.80 }
    ],
    "validation": { "valid": true, "errors": [], "warnings": [] }
  }
  ```
* **Error Responses**: `422 Unprocessable Entity` (Validation), `200 OK with success: false` (Placement failure)

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
