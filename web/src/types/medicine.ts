export interface ActiveIngredient {
  name: string;
  strength: string;
  unit: string;
  purpose: string;
}

export interface MedicineSummary {
  id: number;
  brand_name: string;
  generic_name: string;
  category: string;
  manufacturer: string;
  strength: string;
  dosage_form: string;
  schedule_type?: string | null;
}

export interface MedicineResponse {
  id: number;
  organization_id: number;
  brand_name: string;
  generic_name: string;
  category: string;
  manufacturer: string;
  dosage_form: string;
  strength: string;
  active_ingredients: ActiveIngredient[];
  inactive_excipients: string[];
  tablet_shape?: string | null;
  tablet_color?: string | null;
  score_line?: string | null;
  coating_type?: string | null;
  indications: string;
  dosage_instructions: string;
  warnings_and_precautions: string;
  side_effects?: string | null;
  storage_conditions?: string | null;
  schedule_type?: string | null;
  voice_summary_en?: string | null;
  voice_summary_hi?: string | null;
  voice_summary_mr?: string | null;
  created_at?: string | null;
}

export interface MedicineQueryParams {
  q?: string;
  category?: string;
  organization_id?: number;
  limit?: number;
  offset?: number;
}
