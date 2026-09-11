import { MedicineSummary } from "./medicine";

export interface BatchCreateRequest {
  medicine_id: number;
  batch_no: string;
  mfg_date: string; // YYYY-MM-DD
  exp_date: string; // YYYY-MM-DD
  quantity: number;
  mrp: number;
  status?: string;
}

export interface BatchResponse {
  id: number;
  medicine_id: number;
  batch_no: string;
  mfg_date: string;
  exp_date: string;
  quantity: number;
  mrp: number;
  status: string;
  created_at?: string | null;
}

export interface BatchDetailResponse extends BatchResponse {
  medicine?: MedicineSummary | null;
}

export interface CodeResponse {
  id: number;
  batch_id: number;
  serial_number: string;
  code_hash: string;
  qr_data_url?: string | null;
  qr_svg?: string | null;
  datamatrix_code?: string | null;
  status: string;
  scan_count: number;
  first_scanned_at?: string | null;
  created_at?: string | null;
}

export interface CodeGenerateBatchResponse {
  total_generated: number;
  batch_id: number;
  batch_no: string;
  medicine_name: string;
  codes: CodeResponse[];
}
