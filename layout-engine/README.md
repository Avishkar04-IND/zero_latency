# Pharmaceutical Layout Engine — Smart Medicine Platform

**Module Ownership**: Member 3 (`/layout-engine/`)  
**Current Status**: Production-Ready | **201 Tests Passing** (0 Failures)  

---

## 1. Purpose of the Layout Engine

The Layout Engine is a deterministic, standalone microservice that computes collision-free physical placements for pharmaceutical packaging (blister packs and folding cartons). It arranges tablet cavities, batch-linked serialization codes (DataMatrix, Barcode, Human-Readable), and regulatory medicine information while enforcing physical boundary and margin constraints.

---

## 2. Input / Output Flow

```text
┌────────────────────────────────────────────────────────┐
│                      Input Request                     │
│  Package dimensions, Cavity configs, Code details,     │
│  Medicine text, Constraints, Optimization target       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Layout Engine Pipeline                │
│  1. Pydantic validation & physical boundary checks    │
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

## 3. Supported Optimization Targets

| Target | Description | Objective Priority |
| :--- | :--- | :--- |
| **`COST`** | Minimizes unused printable area and element footprints | Highest space utilization & compact density |
| **`BALANCED`** | Balances visual hierarchy, scan reliability, and spacing | Trade-off between density and legibility |
| **`ACCESSIBILITY`** | Maximizes readability, typography scale, and clearance | High spacing quality, contrast, and scan buffer |
| **`RECOMMEND`** | Evaluates all 3 strategies under unified scoring model | Recommends highest-scoring valid plan + all 3 alternatives |

---

## 4. API Endpoints

### 1. `POST /api/layouts/recommend`
- **Purpose**: Generates and evaluates the physical layout according to the requested optimization strategy.
- **Content-Type**: `application/json`
- **Success (200)**: Returns `LayoutPlan` with `recommended_strategy`, `score`, metrics, `elements` list with physical coordinates, and `alternatives` array.
- **Validation Failure (422)**: Returns structured error schema (`VALIDATION_ERROR`).

### 2. `POST /api/layouts/preview`
- **Purpose**: Generates standalone vector SVG markup representing the layout.
- **Content-Type**: `application/json`
- **Success (200)**: Returns `{"success": true, "layout_id": "...", "svg": "<svg...", "validation": {...}}`.

### 3. `POST /api/layouts/pdf`
- **Purpose**: Exports the physical layout to an ISO 32000 compliant PDF document.
- **Content-Type**: `application/pdf`
- **Success (200)**: Binary PDF stream with `Content-Disposition: inline; filename="{layout_id}.pdf"`.
- **Placement Failure (400)**: Returns structured failure message; zero fake PDFs generated.

---

## 5. Physical Units & Dimensions

- **Primary Unit**: Millimeters (`mm`) across all inputs, coordinates, and models.
- **Angles**: Degrees (`0.0`, `90.0`, `180.0`, `270.0`).
- **Coordinate Space**: Origin `(0, 0)` is at the top-left of the package.
- **PDF Conversion**: Rendered to PDF points only at export time using exact standard conversion:  
  $$\text{points} = \text{mm} \times \frac{72}{25.4}$$

---

## 6. SVG / PDF Rendering

- **Package Boundary**: Drawn to exact outer physical dimensions (`package_width_mm` $\times$ `package_height_mm`).
- **Printable Area**: Visualized with dashed boundary lines according to offset and dimensions.
- **Tablet Cavities**: Rendered accurately by geometry shape (Bézier circles for round cavities, rounded rectangles for oblong/capsule cavities).
- **Code Reservation**: Renders reserved physical zones and type labels for DataMatrix and Barcode without generating fake 2D matrix or barcode symbology.
- **Medicine Information**: Rendered with proportional font sizes, selectable text, and visual hierarchy.

---

## 7. How to Run the Service

```bash
# From within the /layout-engine/ directory:
py -3.14 -m uvicorn app.main:app --port 8000 --reload
```
Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

---

## 8. How to Run Tests

```bash
# Run complete test suite (201 tests):
py -3.14 -m pytest -v

# Run specific test modules:
py -3.14 -m pytest -v tests/test_api_integration.py
py -3.14 -m pytest -v tests/test_production_hardening.py
```

---

## 9. Expected Integration Contract for the Team

- **Backend Integration**: Backend calls `POST /api/layouts/recommend` using internal service requests to retrieve layout coordinates, scores, and alternative plans for persistence.
- **Web Assistant Integration**: Web UI displays the vector SVG from `POST /api/layouts/preview` or embeds PDF previews directly via `POST /api/layouts/pdf`.
- **Error Response Schema**: All endpoints return sanitized, structured JSON error envelopes (`code`, `message`, `details`) on error status codes (`400`, `404`, `422`), with zero internal stack trace exposure.

---

## 10. Current Status

- **Engine Status**: Production-Ready
- **Test Suite**: **201 / 201 Tests Passing**
- **Git Branch**: `member3/layout-engine` (aligned, verified, and ready for PR merge into `integration`)
