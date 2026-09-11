/**
 * Layout Engine type contracts for Web ↔ Member 3 Layout Engine integration.
 * Based on the live LayoutRequest / LayoutPlan schemas from:
 *   layout-engine/app/models/layout_models.py
 */

// ─── Request types ────────────────────────────────────────────────────────────

export interface LayoutPackage {
  package_width_mm: number;
  package_height_mm: number;
  printing_area_width_mm: number;
  printing_area_height_mm: number;
  printing_area_x_mm?: number;
  printing_area_y_mm?: number;
  margin_left_mm?: number;
  margin_right_mm?: number;
  margin_top_mm?: number;
  margin_bottom_mm?: number;
}

export interface LayoutTablet {
  tablet_count: number;
  /** For round tablets */
  tablet_diameter_mm?: number;
  /** For non-round tablets — both required together */
  tablet_width_mm?: number;
  tablet_height_mm?: number;
}

export interface LayoutCode {
  /** Code type: "QR", "datamatrix", "barcode", "human-readable" */
  type: string;
  value: string;
  min_size_mm?: number;
  serial_number?: string;
}

/** Flexible medicine/batch fields accepted by the StructuredPrintDataRequest adapter */
export interface LayoutMedicineInfo {
  name: string;
  dosage?: string;
  manufacturer?: string;
}

export interface LayoutBatchInfo {
  batch_number: string;
  manufacturing_date: string;
  expiry_date: string;
}

/**
 * Primary request body for POST /api/v1/layout/optimize
 * Maps to StructuredPrintDataRequest on the Layout Engine side.
 */
export interface LayoutOptimizeRequest {
  package: LayoutPackage;
  tablet: LayoutTablet;
  medicine?: LayoutMedicineInfo;
  batch?: LayoutBatchInfo;
  code?: LayoutCode;
  optimization_target?: "RECOMMEND" | "COST" | "BALANCED" | "ACCESSIBILITY";
}

// ─── Response types ───────────────────────────────────────────────────────────

export interface LayoutElement {
  id: string;
  type: "text" | "code" | "rectangle" | "tablet_cavity";
  content?: string | null;
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_mm: number;
  font_size_mm?: number | null;
  rotation_deg?: number;
  code_type?: string | null;
}

export interface LayoutValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface LayoutAlternative {
  strategy: string;
  score: number;
  space_utilization: number;
  readability: number;
  print_efficiency: number;
  cost_efficiency: number;
  scan_reliability: number;
  warnings: string[];
  errors: string[];
  layout?: Record<string, unknown> | null;
}

/** Response from POST /api/v1/layout/optimize */
export interface LayoutOptimizeResponse {
  id?: string | null;
  success: boolean;
  recommended_strategy?: string | null;
  score?: number | null;
  space_utilization?: number | null;
  readability?: number | null;
  print_efficiency?: number | null;
  cost_efficiency?: number | null;
  scan_reliability?: number | null;
  balanced_score?: number | null;
  accessibility_score?: number | null;
  used_printable_area?: number | null;
  unused_printable_area?: number | null;
  candidates_evaluated?: number | null;
  elements: LayoutElement[];
  validation?: LayoutValidation | null;
  alternatives?: LayoutAlternative[] | null;
  warnings: string[];
  errors: string[];
  layout?: Record<string, unknown> | null;
}

/** Response from POST /api/layouts/preview */
export interface LayoutPreviewResponse {
  success: boolean;
  layout_id?: string | null;
  svg?: string | null;
  validation?: LayoutValidation | null;
}

/** Request for POST /api/layouts/pdf */
export interface LayoutPdfRequest {
  request: LayoutOptimizeRequest;
}

/** Dimensions form state (user-supplied per session — not stored in backend) */
export interface PackageDimensions {
  package_width_mm: number;
  package_height_mm: number;
  printing_area_width_mm: number;
  printing_area_height_mm: number;
  tablet_count: number;
  tablet_diameter_mm: number;
}

/** Default dimensions for a standard 10-tablet blister strip */
export const DEFAULT_PACKAGE_DIMENSIONS: PackageDimensions = {
  package_width_mm: 120.0,
  package_height_mm: 60.0,
  printing_area_width_mm: 105.0,
  printing_area_height_mm: 50.0,
  tablet_count: 10,
  tablet_diameter_mm: 9.0,
};
