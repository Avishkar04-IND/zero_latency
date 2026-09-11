# Layout Engine API Contract Specification

**Module Owner**: Member 3 (`/layout-engine/`)  
**Service Version**: `0.1.0`  
**Base Path**: `/api/layouts`  
**Primary Unit**: Millimeters (`mm`)  

---

## Standard Status Codes & Error Formats

| HTTP Status Code | Meaning | Condition |
| :--- | :--- | :--- |
| `200 OK` | Request Succeeded / Layout Evaluated | Valid recommendation, preview SVG rendered, or valid evaluation report returned |
| `400 Bad Request` | Layout Generation or Rendering Error | Invalid preview input or layout placement failure during binary export (e.g. PDF export on impossible layout) |
| `404 Not Found` | Resource Not Found | Target layout ID does not exist in memory/store |
| `422 Unprocessable Entity` | Request Validation Error | Negative dimensions, missing mandatory fields, or printing area exceeding packaging boundaries |
| `500 Internal Server Error` | Rendering / Processing Failure | Internal vector or binary compilation error |

### Standard Validation Error Response Schema (HTTP 422)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed. Verify physical dimensions and constraints.",
    "details": [
      "body -> package -> package_width_mm: Input should be greater than 0"
    ]
  },
  "detail": [
    {
      "loc": ["body", "package", "package_width_mm"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

### Standard Placement Failure Response Schema (HTTP 400 / HTTP 200)
```json
{
  "error": {
    "code": "HTTP_400",
    "message": "Layout generation failed. Cannot produce physical PDF preview.",
    "details": [
      "All layout strategies failed to produce a valid layout."
    ]
  },
  "detail": {
    "message": "Layout generation failed. Cannot produce physical PDF preview.",
    "errors": ["All layout strategies failed to produce a valid layout."],
    "warnings": []
  }
}
```

---

## 1. POST /api/layouts/recommend

### Purpose
Calculates deterministic, collision-free, margin-compliant physical placements for packaging blister cavities, batch-linked codes, and medicine information. Evaluates placement quality under three deterministic optimization strategies (`COST`, `BALANCED`, `ACCESSIBILITY`) and returns the recommended optimal layout along with all valid scored alternatives.

### Request Structure
- **Content-Type**: `application/json`
- **Units**:
  - Linear dimensions & coordinates: millimeters (`mm`)
  - Angles & orientations: degrees (`deg`, `0`, `90`, `180`, `270`)
- **Required Fields**:
  - `package`:
    - `package_width_mm` (float, > 0)
    - `package_height_mm` (float, > 0)
    - `printing_area_width_mm` (float, > 0)
    - `printing_area_height_mm` (float, > 0)
    - `printing_area_x_mm` (float, >= 0)
    - `printing_area_y_mm` (float, >= 0)
  - `tablet`:
    - `tablet_count` (int, >= 1)
    - Either `tablet_diameter_mm` (float, > 0 for round tablets) OR both `tablet_width_mm` and `tablet_height_mm` (for non-round/capsule tablets)
- **Optional Fields**:
  - `tablet.positions`: Pre-defined cavity coordinates `[{"x_mm": float, "y_mm": float}]`
  - `marking`:
    - `marking_enabled` (bool, default: `false`)
    - `marking_side` (`front`, `back`, `both`)
    - `marking_method` (`inkjet`, `emboss`, `deboss`, `laser`)
    - `code_value` (string, e.g. `"MED001"`)
  - `code`:
    - `code_value` / `value` (string, e.g. `"MED001-DM"`)
    - `code_type` / `type` (`human-readable`, `datamatrix`, `barcode`, default: `human-readable`)
    - `minimum_code_size_mm` / `min_size_mm` (float, > 0)
    - `code_width_mm`, `code_height_mm` (float, > 0)
    - `orientation_deg` / `orientation` (float, default: `0.0`)
  - `information`:
    - `medicine_name` (string)
    - `strength` (string)
    - `ingredients` (string)
    - `healthcare_use` (string)
    - `batch` / `batch_number` (string)
    - `mfg` / `manufacturing_date` (string)
    - `exp` / `expiry_date` (string)
    - `manufacturer` (string)
    - `mrp` (string)
    - `storage` (string)
    - `warnings` (string)
  - `constraints`:
    - `minimum_margin_mm` (float, >= 0, default: `1.0`)
    - `minimum_element_spacing_mm` (float, >= 0, default: `0.5`)
    - `minimum_text_size_mm` (float, >= 0, default: `2.0`)
  - `optimization_target`: Strategy selector string (`RECOMMEND`, `COST`, `BALANCED`, `ACCESSIBILITY`, default: `RECOMMEND`)

### Supported Optimization Targets
1. `RECOMMEND` (Default): Runs all 3 strategies, calculates standard multi-objective score (`Score = 0.30 * space_utilization + 0.25 * readability + 0.25 * print_efficiency + 0.20 * scan_reliability`), and recommends the highest scoring valid layout while returning all alternatives.
2. `COST`: Maximizes compact placement and printable area utilization (`cost_efficiency`).
3. `BALANCED`: Balances element spacing, scan clearance, and visual hierarchy (`balanced_score`).
4. `ACCESSIBILITY`: Maximizes text legibility, spacing quality, whitespace buffers, and scan reliability (`accessibility_score`).

### Example Request
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
    "medicine_name": "Amoxicillin Trihydrate",
    "strength": "500 mg",
    "batch": "BX-2026",
    "mfg": "2026-03",
    "exp": "2028-03"
  },
  "constraints": {
    "minimum_margin_mm": 2.0,
    "minimum_element_spacing_mm": 1.5
  },
  "optimization_target": "RECOMMEND"
}
```

### Success Response (HTTP 200)
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
  "warnings": [],
  "errors": [],
  "package": {
    "package_width_mm": 130.0,
    "package_height_mm": 65.0,
    "printing_area_width_mm": 110.0,
    "printing_area_height_mm": 55.0,
    "printing_area_x_mm": 10.0,
    "printing_area_y_mm": 5.0
  },
  "elements": [
    {
      "id": "cavity_1",
      "type": "tablet_cavity",
      "x_mm": 86.8,
      "y_mm": 7.0,
      "width_mm": 9.0,
      "height_mm": 9.0
    },
    {
      "id": "med_name",
      "type": "text",
      "content": "Amoxicillin Trihydrate",
      "x_mm": 12.0,
      "y_mm": 7.0,
      "width_mm": 45.0,
      "height_mm": 5.0,
      "font_size_mm": 3.2
    }
  ],
  "alternatives": [
    {
      "strategy": "BALANCED",
      "score": 83.42,
      "space_utilization": 0.582,
      "readability": 0.880,
      "print_efficiency": 0.850,
      "cost_efficiency": 0.582,
      "scan_reliability": 0.940,
      "layout": { "..." : "..." }
    },
    {
      "strategy": "COST",
      "score": 81.15,
      "space_utilization": 0.725,
      "readability": 0.760,
      "print_efficiency": 0.890,
      "cost_efficiency": 0.725,
      "scan_reliability": 0.880,
      "layout": { "..." : "..." }
    },
    {
      "strategy": "ACCESSIBILITY",
      "score": 79.80,
      "space_utilization": 0.440,
      "readability": 0.960,
      "print_efficiency": 0.780,
      "cost_efficiency": 0.440,
      "scan_reliability": 0.960,
      "layout": { "..." : "..." }
    }
  ],
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

### Placement Failure Response (HTTP 200)
When physical constraints cannot be satisfied (e.g. 100 cavities on a 20mm blister):
```json
{
  "id": "layout_recommendation_failed",
  "success": false,
  "recommended_strategy": null,
  "recommended_layout": null,
  "alternatives": [],
  "score": null,
  "errors": [
    "All layout strategies failed to produce a valid layout."
  ],
  "warnings": [],
  "validation": {
    "valid": false,
    "errors": ["All layout strategies failed to produce a valid layout."],
    "warnings": []
  }
}
```

---

## 2. POST /api/layouts/preview

### Purpose
Generates a standalone, standards-compliant SVG vector preview representing the physical packaging layout. Preserves physical aspect ratio and visually renders package boundary, printable area, round/non-round tablet cavities, text elements, and reserved DataMatrix/Barcode areas.

### Request Structure
- **Content-Type**: `application/json`
- **Body**: Accepts `LayoutPreviewRequest`:
  - `layout` (optional): An existing `LayoutPlan` object
  - `request` (optional): A `LayoutRequest` object to generate and preview in one step
  - *At least one of `layout` or `request` must be provided.*

### Example Request
```json
{
  "request": {
    "package": {
      "package_width_mm": 110.0,
      "package_height_mm": 55.0,
      "printing_area_width_mm": 90.0,
      "printing_area_height_mm": 45.0,
      "printing_area_x_mm": 10.0,
      "printing_area_y_mm": 5.0
    },
    "tablet": {
      "tablet_count": 4,
      "tablet_diameter_mm": 8.0
    },
    "code": {
      "value": "MED001",
      "code_type": "human-readable"
    },
    "information": {
      "medicine_name": "Ibuprofen",
      "strength": "400 mg"
    }
  }
}
```

### Success Response (HTTP 200)
- **Content-Type**: `application/json`
```json
{
  "success": true,
  "layout_id": "layout_recommendation_balanced_001",
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"110.0mm\" height=\"55.0mm\" viewBox=\"0 0 110.0 55.0\">\n  <style>\n    .package-boundary { fill: #ffffff; stroke: #1e293b; stroke-width: 0.5; }\n    .print-area { fill: #f8fafc; stroke: #94a3b8; stroke-width: 0.3; stroke-dasharray: 1, 1; }\n    .tablet-cavity { fill: #e2e8f0; stroke: #64748b; stroke-width: 0.3; }\n  </style>\n  <rect class=\"package-boundary\" x=\"0\" y=\"0\" width=\"110.0\" height=\"55.0\" rx=\"1\" ry=\"1\" />\n  ...\n</svg>"
}
```

### Placement / Preview Failure Response (HTTP 200)
```json
{
  "success": false,
  "layout_id": "layout_failed",
  "errors": [
    "No valid placement found: insufficient printable area or geometry conflict."
  ],
  "warnings": [],
  "validation": {
    "valid": false,
    "errors": ["No valid placement found: insufficient printable area or geometry conflict."],
    "warnings": []
  },
  "svg": null
}
```

---

## 3. POST /api/layouts/pdf

### Purpose
Exports the physical packaging layout to an ISO 32000 / PDF 1.4 binary stream. Converts millimeter dimensions to physical PDF points (`points = mm * 72 / 25.4`), matching the package boundary to the PDF MediaBox. Contains selectable text elements and accurately scaled cavities.

### Request Structure
- **Content-Type**: `application/json`
- **Body**: Accepts `LayoutPreviewRequest`:
  - `layout` (optional): An existing `LayoutPlan` object
  - `request` (optional): A `LayoutRequest` object to generate and export to PDF

### Example Request
```json
{
  "request": {
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
      "code_type": "datamatrix"
    },
    "information": {
      "medicine_name": "Amoxicillin",
      "strength": "500 mg"
    }
  }
}
```

### Success Response (HTTP 200)
- **Content-Type**: `application/pdf`
- **Headers**:
  - `Content-Disposition`: `inline; filename="layout_recommendation_balanced_001.pdf"`
  - `Content-Length`: `4128`
- **Body**: Binary PDF document starting with `%PDF-1.4` and ending with `%%EOF`.

### Placement Failure Response (HTTP 400)
When the layout cannot be placed, no fake PDF is generated.
- **Content-Type**: `application/json`
```json
{
  "error": {
    "code": "HTTP_400",
    "message": "Layout generation failed. Cannot produce physical PDF preview.",
    "details": [
      "All layout strategies failed to produce a valid layout."
    ]
  },
  "detail": {
    "message": "Layout generation failed. Cannot produce physical PDF preview.",
    "errors": [
      "All layout strategies failed to produce a valid layout."
    ],
    "warnings": []
  }
}
```
