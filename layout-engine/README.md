# Pharmaceutical Layout Engine — Smart Medicine Platform

**Module Ownership**: Member 3 (`/layout-engine/`)  
**Current Status**: Production-Ready | **242 Tests Passing** (0 Failures)  

---

## 1. Purpose & Architectural Scope

The Layout Engine is a deterministic, standalone microservice that computes collision-free physical placements for pharmaceutical packaging (blister packs and folding cartons). It arranges tablet cavities, batch-linked serialization codes (QR, DataMatrix, Barcode, Human-Readable), and regulatory medicine information while enforcing physical boundary and margin constraints.

> **IMPORTANT ARCHITECTURAL BOUNDARY**:
> - The Layout Engine operates **purely in-memory** and **does NOT access the PostgreSQL database**.
> - The Layout Engine does **NOT verify pharmaceutical authenticity or cryptographic signatures**; verification is exclusively performed by the Backend Core (`/backend/`).
> - The Layout Engine accepts structured packaging data and outputs mathematical coordinates, vector SVG previews, and ISO 32000 compliant PDF documents.

---

## 2. Input / Output Flow

```text
┌────────────────────────────────────────────────────────┐
│                      Input Request                     │
│  Standard LayoutRequest OR Structured Print Data       │
│  (Package dimensions, Cavity configs, QR/DataMatrix,   │
│   Backend medicine/batch objects, Print constraints)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│            Structured Print Data Adapter               │
│  Maps: dosage -> strength, batch_number -> batch,      │
│  mfg_date -> mfg, exp_date -> exp, serial_number -> SN │
│  Normalizes code types (QR, DataMatrix, Barcode)       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Layout Engine Pipeline                │
│  1. Pydantic validation & physical boundary checks     │
│  2. Deterministic spatial placement algorithms         │
│  3. Optimization evaluation (Cost / Balanced / Access) │
│  4. Common score normalization & tie-breaking          │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     [ LayoutPlan ]     [ SVG Preview ]  [ PDF Export ]
   Coordinates & metrics   Vector markup    ISO 32000 binary
```

---

## 3. Key Integration Capabilities (Task 19)

### 1. QR Code Support & Normalization
- Full support for `CodeType.QR` (`"qr"`).
- Case-insensitive normalization for code types and aliases:
  - `qr`, `QR`, `qrcode`, `QRCode`, `QRCODE`, `qr-code`, `qr_code` → `CodeType.QR`
  - `datamatrix`, `DATAMATRIX`, `DataMatrix`, `data-matrix` → `CodeType.DATAMATRIX`
  - `barcode`, `BARCODE`, `BarCode`, `bar-code` → `CodeType.BARCODE`
  - `human-readable`, `HUMAN-READABLE`, `humanreadable` → `CodeType.HUMAN_READABLE`
- Accepted aliases: `type` for `code_type`, `value` for `code_value`, `min_size_mm` for `minimum_code_size_mm`.

### 2. QR and DataMatrix Square Sizing
- When only `minimum_code_size_mm` (or `min_size_mm`) is provided for 2D matrix symbologies (QR, DataMatrix), dimensions automatically default to square (`min_size` $\times$ `min_size` mm).
- Explicit rectangular dimensions (`code_width_mm`, `code_height_mm`) are respected when explicitly provided.
- When minimum size is omitted, existing default behavior is preserved (DataMatrix defaults to $20.0 \times 6.0$ mm).

### 3. Backend Pharmaceutical Field Mapping
The engine maps structured backend print-data without modifying or overwriting authoritative values:
- `dosage` → `strength`
- `batch_number` → `batch`
- `manufacturing_date` → `mfg`
- `expiry_date` → `exp`
- `serial_number` → human-readable serial text element (`id="serial_no"`)

### 4. Dual Code Placement
- Coexistence of a scannable 2D code (`batch_code`, `ElementType.CODE`) and human-readable serial text (`serial_no`, `ElementType.TEXT`, prefixed with `"SN: "`).
- Both elements are placed collision-free using the existing deterministic placement engine and validated against package boundaries and margins.

---

## 4. Supported Optimization Targets

| Target | Description | Objective Priority |
| :--- | :--- | :--- |
| **`COST`** | Minimizes unused printable area and element footprints | Highest space utilization & compact density |
| **`BALANCED`** | Balances visual hierarchy, scan reliability, and spacing | Trade-off between density and legibility |
| **`ACCESSIBILITY`** | Maximizes readability, typography scale, and clearance | High spacing quality, contrast, and scan buffer |
| **`RECOMMEND`** | Evaluates all 3 strategies under unified scoring model | Recommends highest-scoring valid plan + all 3 alternatives |

---

## 5. API Endpoints

### 1. `POST /api/v1/layout/optimize` (Primary Integration Endpoint)
- **Purpose**: Primary integration route for Web and Backend services. Accepts either standard `LayoutRequest` or backend-style structured print data (with `medicine`, `batch`, `code`, or `codes` list).
- **Content-Type**: `application/json`
- **Success (200)**: Returns `LayoutPlan` with `recommended_strategy`, overall score, sub-scores, placed physical elements (`tablet_cavity`, `text`, `code`), and alternative candidate evaluations.
- **Validation Failure (422)**: Returns structured error schema (`VALIDATION_ERROR`).

### 2. `POST /api/layouts/recommend` (Retained Compatibility Route)
- **Purpose**: Generates and evaluates the physical layout using standard `LayoutRequest`.
- **Content-Type**: `application/json`
- **Success (200)**: Returns `LayoutPlan`.

### 3. `POST /api/layouts/preview` (Retained Compatibility Route)
- **Purpose**: Generates standalone vector SVG markup representing the layout.
- **Content-Type**: `application/json`
- **Success (200)**: Returns `{"success": true, "layout_id": "...", "svg": "<svg...", "validation": {...}}`.

### 4. `POST /api/layouts/pdf` (Retained Compatibility Route)
- **Purpose**: Exports the physical layout to an ISO 32000 compliant PDF document.
- **Content-Type**: `application/pdf`
- **Success (200)**: Binary PDF stream with `Content-Disposition: inline; filename="{layout_id}.pdf"`.
- **Placement Failure (400)**: Returns structured failure message; zero fake PDFs generated.

---

## 6. Physical Units & Dimensions

- **Primary Unit**: Millimeters (`mm`) across all inputs, coordinates, and models.
- **Angles**: Degrees (`0.0`, `90.0`, `180.0`, `270.0`).
- **Coordinate Space**: Origin `(0, 0)` is at the top-left of the package.
- **PDF Conversion**: Rendered to PDF points only at export time using exact standard conversion:  
  $$\text{points} = \text{mm} \times \frac{72}{25.4}$$

---

## 7. SVG / PDF Rendering

- **Package Boundary**: Drawn to exact outer physical dimensions (`package_width_mm` $\times$ `package_height_mm`).
- **Printable Area**: Visualized with dashed boundary lines according to offset and dimensions.
- **Tablet Cavities**: Rendered accurately by geometry shape (Bézier circles for round cavities, rounded rectangles for oblong/capsule cavities).
- **Code Reservation**: Renders reserved physical zones and type labels for QR (`.code-reserved-qr`), DataMatrix (`.code-reserved-datamatrix`), and Barcode (`.code-reserved-barcode`).
- **Medicine Information**: Rendered with proportional font sizes, selectable text, and visual hierarchy.

---

## 8. How to Run the Service

```bash
# From within the /layout-engine/ directory:
py -3.14 -m uvicorn app.main:app --port 8001 --reload
```
Interactive OpenAPI documentation is available at `http://localhost:8001/docs`.

---

## 9. How to Run Tests

```bash
# Run complete test suite (242 tests):
py -3.14 -m pytest -v

# Run Task 19 integration tests:
py -3.14 -m pytest -v tests/test_task19_integration.py
```

---

## 10. Current Status

- **Engine Status**: Production-Ready
- **Test Suite**: **242 / 242 Tests Passing** (0 Failures)
- **Git Branch**: `member3/layout-engine`
