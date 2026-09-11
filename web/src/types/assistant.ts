import { MedicineResponse, ActiveIngredient } from "./medicine";
import { BatchResponse } from "./batch";

export type AssistantIntent =
  | "medicine_name"
  | "strength"
  | "manufacturer"
  | "batch_number"
  | "expiry_date"
  | "dosage_form"
  | "ingredients"
  | "storage"
  | "warnings"
  | "indications"
  | "authenticity"
  | "dosage_instructions"
  | "personalized_dosage"
  | "general_greeting"
  | "unsupported";

export interface NormalizedMedicineData {
  brand_name?: string | null;
  generic_name?: string | null;
  strength?: string | null;
  dosage_form?: string | null;
  manufacturer?: string | null;
  category?: string | null;
  batch_no?: string | null;
  mfg_date?: string | null;
  exp_date?: string | null;
  quantity?: number | null;
  mrp?: number | null;
  active_ingredients?: ActiveIngredient[] | string[] | null;
  inactive_excipients?: string[] | null;
  indications?: string | null;
  warnings_and_precautions?: string | null;
  storage_conditions?: string | null;
  schedule_type?: string | null;
  side_effects?: string | null;
  dosage_instructions?: string | null;
  is_genuine?: boolean | null;
  verification_status?: string | null;
}

export interface NestedMedicineContext extends Partial<MedicineResponse> {
  name?: string;
  dosage?: string;
  storage_instructions?: string;
  warnings?: string;
}

export interface NestedBatchContext extends Partial<BatchResponse> {
  batch_number?: string;
  expiry_date?: string;
}

export interface NestedVerificationContext {
  status?: string;
  verification_status?: string;
  is_genuine?: boolean;
  risk_score?: number;
  scanned_serial?: string;
  verified_at?: string;
}

export interface VerifiedMedicineContext {
  medicine?: NestedMedicineContext | null;
  batch?: NestedBatchContext | null;
  verification?: NestedVerificationContext | null;
  // Support direct flat fields for client convenience
  brand_name?: string;
  name?: string;
  generic_name?: string;
  strength?: string;
  dosage?: string;
  dosage_form?: string;
  manufacturer?: string;
  batch_no?: string;
  batch_number?: string;
  mfg_date?: string;
  exp_date?: string;
  expiry_date?: string;
  active_ingredients?: ActiveIngredient[] | string[];
  storage_conditions?: string;
  storage_instructions?: string;
  warnings_and_precautions?: string;
  warnings?: string;
  indications?: string;
  side_effects?: string;
  dosage_instructions?: string;
  schedule_type?: string;
  is_genuine?: boolean;
  verification_status?: string;
  status?: string;
}

export interface AssistantQueryRequest {
  query?: string;
  query_text?: string;
  context?: VerifiedMedicineContext | null;
  medicine_context?: VerifiedMedicineContext | null;
  session_id?: string;
  language?: "en" | "hi" | "mr";
  input_type?: "TEXT" | "AUDIO";
}

export interface AssistantQueryResponse {
  success: boolean;
  intent: AssistantIntent;
  answer: string;
  source: "verified_medicine_data" | "safety_guardrail" | "unverified_context" | "system";
  has_verified_context: boolean;
  confidence: number;
  data?: Record<string, any>;
  tts_clean_text: string;
  suggested_actions?: string[];
  error?: {
    code: string;
    message: string;
  };
}
