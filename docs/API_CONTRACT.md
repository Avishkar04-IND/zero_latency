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

### Endpoint: Optimize Package Layout
* **Endpoint**: `/api/v1/layout/optimize`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**:
  ```json
  {
    "package_dimensions": { "length": 0.0, "width": 0.0, "height": 0.0 },
    "code_type": "DATAMATRIX",
    "text_content": { "name": "", "dosage": "", "warning": "" },
    "optimization_target": "ACCESSIBILITY|COST|BALANCED"
  }
  ```
* **Response**:
  ```json
  {
    "layout_id": "placeholder_uuid",
    "code_placement": { "x": 0.0, "y": 0.0, "size": 0.0 },
    "text_placements": [],
    "cost_score": 0.0,
    "accessibility_score": 0.0
  }
  ```
* **Error Responses**: `400 Bad Request`, `500 Internal Server Error`

---

## 8. Layout Preview APIs

### Endpoint: Render Layout Preview
* **Endpoint**: `/api/v1/layout/preview`
* **HTTP Method**: `POST`
* **Authentication**: Internal Service API Key / Bearer Token
* **Request**:
  ```json
  {
    "layout_id": "placeholder_uuid",
    "format": "SVG|PDF"
  }
  ```
* **Response**:
  ```json
  {
    "format": "SVG|PDF",
    "preview_url": "placeholder_url",
    "raw_vector": "placeholder_svg_content"
  }
  ```
* **Error Responses**: `400 Bad Request`, `404 Not Found`

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
