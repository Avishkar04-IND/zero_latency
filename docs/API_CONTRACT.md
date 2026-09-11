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

## 9. Voice & Text Assistant APIs

### Endpoint: Process Voice / Chat Query
* **Primary Endpoint**: `/api/assistant/query`
* **Compatibility Alias**: `/api/v1/assistant/query`
* **HTTP Method**: `POST`
* **Authentication**: Optional / Public (Accessible by Web Admin and Mobile Flutter accessibility app)

#### Request Schema
```json
{
  "query": "What is the expiry date?",
  "query_text": "What is the expiry date?",
  "context": {
    "medicine": {
      "brand_name": "Dolo-650",
      "generic_name": "Paracetamol Tablets IP",
      "strength": "650 mg",
      "dosage_form": "Tablet",
      "manufacturer": "Micro Labs Limited",
      "active_ingredients": [
        { "name": "Paracetamol IP", "strength": "650", "unit": "mg", "purpose": "Analgesic & Antipyretic" }
      ],
      "storage_conditions": "Store below 30°C in a dry place. Protect from moisture and direct light.",
      "warnings_and_precautions": "Overdose may cause serious liver damage. Avoid alcohol.",
      "indications": "Relief of mild to moderate pain and fever.",
      "schedule_type": "OTC"
    },
    "batch": {
      "batch_no": "BTH-DOLO-2026A1",
      "mfg_date": "2026-09-01",
      "exp_date": "2028-09-01",
      "quantity": 10000,
      "mrp": 50.0
    },
    "verification": {
      "is_genuine": true,
      "status": "GENUINE",
      "risk_score": 0
    }
  },
  "session_id": "optional_session_uuid",
  "language": "en"
}
```

> **Note**: For convenience, flat fields are also supported under `context` (e.g., `context.brand_name`, `context.exp_date`, `context.batch_no`, `context.is_genuine`).

#### Response Schema
```json
{
  "success": true,
  "intent": "expiry_date",
  "answer": "The medicine expires on 2028-09-01. The batch is within its registered shelf life.",
  "source": "verified_medicine_data",
  "has_verified_context": true,
  "confidence": 1.0,
  "data": {
    "expiry_date": "2028-09-01",
    "is_expired": false,
    "batch_no": "BTH-DOLO-2026A1"
  },
  "tts_clean_text": "The medicine expires on September 1, 2028. The batch is within its registered shelf life.",
  "suggested_actions": []
}
```

#### Supported Deterministic Intents
| Intent | Description | Sample Query |
| :--- | :--- | :--- |
| `medicine_name` | Product brand and generic name | *"What medicine is this?"*, *"Brand name?"* |
| `strength` | Active drug strength / potency | *"What is the strength?"*, *"How many mg?"* |
| `manufacturer` | Registered pharmaceutical manufacturer | *"Who manufactured this drug?"* |
| `batch_number` | Authoritative batch / lot identifier | *"What is the batch number?"* |
| `expiry_date` | Expiration date and shelf-life validity | *"When does it expire?"*, *"Is it expired?"* |
| `dosage_form` | Formulation physical form | *"Is this a tablet or capsule?"*, *"What form is this?"* |
| `ingredients` | Active pharmaceutical ingredients (APIs) | *"What are the active ingredients?"*, *"Composition?"* |
| `storage` | Storage instructions and conditions | *"How should I store this?"*, *"Keep in fridge?"* |
| `warnings` | Safety warnings, precautions, side effects | *"What are the warnings and precautions?"* |
| `indications` | Approved therapeutic uses | *"What is this used for?"*, *"Why take this?"* |
| `authenticity` | Verification status against CDSCO ledger | *"Is this medicine authentic and genuine?"* |
| `dosage_instructions` | General package label directions | *"What are the manufacturer label instructions?"* |
| `personalized_dosage` | Safety Guardrail (Blocked) | *"How many should I personally take for my fever?"* |
| `general_greeting` | Assistant introduction & capability guidance | *"Hello"*, *"Hi"* |
| `unsupported` | Controlled fallback for unverified queries | *"What is the weather?"* |

#### Safety Guardrail Behavior
1. **Zero Hallucination Policy**: The assistant strictly derives pharmaceutical answers from verified backend data. When verified context is missing or does not contain the requested field, the assistant returns:
   `"I don't have enough verified medicine information to answer that question."` (`has_verified_context: false`, `source: "unverified_context"`).
2. **Medical Advice Prohibition**: Individualized dosage queries, diagnostic queries, and prescription requests are deterministically blocked with intent `personalized_dosage`, returning:
   `"I cannot provide personalized medical diagnosis, prescriptions, or individualized dosage recommendations. Please consult a qualified doctor or licensed healthcare professional for guidance specific to your condition."` (`source: "safety_guardrail"`).

#### Error Responses
- `400 Bad Request`:
  ```json
  {
    "success": false,
    "error": {
      "code": "MISSING_QUERY",
      "message": "A non-empty 'query' string is required."
    }
  }
  ```
- `500 Internal Server Error`:
  ```json
  {
    "success": false,
    "error": {
      "code": "INTERNAL_ERROR",
      "message": "An unexpected error occurred processing assistant query."
    }
  }
  ```
