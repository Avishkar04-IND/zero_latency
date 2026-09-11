from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator
import json


class ActiveIngredient(BaseModel):
    name: str
    strength: str
    unit: str = "mg"
    purpose: str = "Active Ingredient"


class MedicineBase(BaseModel):
    brand_name: str
    generic_name: str
    category: str
    manufacturer: str
    dosage_form: str = "Tablet"
    strength: str
    
    # Tablet content specifications
    active_ingredients: List[ActiveIngredient]
    inactive_excipients: Optional[List[str]] = []
    
    # Tablet physical specifications
    tablet_shape: Optional[str] = "Round"
    tablet_color: Optional[str] = "White"
    score_line: Optional[str] = "None"
    coating_type: Optional[str] = "Film-coated"
    
    # Clinical & Safety Information
    indications: str
    dosage_instructions: str
    warnings_and_precautions: str
    side_effects: Optional[str] = None
    storage_conditions: Optional[str] = "Store below 30°C in a dry place. Protect from direct sunlight."
    schedule_type: Optional[str] = "Schedule H"
    
    # Accessibility Voice Summaries
    voice_summary_en: Optional[str] = None
    voice_summary_hi: Optional[str] = None
    voice_summary_mr: Optional[str] = None
    status: Optional[str] = "active"


class MedicineCreate(MedicineBase):
    organization_id: Optional[int] = None


class MedicineUpdate(BaseModel):
    brand_name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    active_ingredients: Optional[List[ActiveIngredient]] = None
    inactive_excipients: Optional[List[str]] = None
    tablet_shape: Optional[str] = None
    tablet_color: Optional[str] = None
    score_line: Optional[str] = None
    coating_type: Optional[str] = None
    indications: Optional[str] = None
    dosage_instructions: Optional[str] = None
    warnings_and_precautions: Optional[str] = None
    side_effects: Optional[str] = None
    storage_conditions: Optional[str] = None
    schedule_type: Optional[str] = None
    voice_summary_en: Optional[str] = None
    voice_summary_hi: Optional[str] = None
    voice_summary_mr: Optional[str] = None
    status: Optional[str] = None


class MedicineResponse(BaseModel):
    id: int
    organization_id: int
    brand_name: str
    generic_name: str
    category: str
    manufacturer: str
    dosage_form: str
    strength: str
    active_ingredients: List[ActiveIngredient]
    inactive_excipients: List[str]
    tablet_shape: Optional[str]
    tablet_color: Optional[str]
    score_line: Optional[str]
    coating_type: Optional[str]
    indications: str
    dosage_instructions: str
    warnings_and_precautions: str
    side_effects: Optional[str]
    storage_conditions: Optional[str]
    schedule_type: Optional[str]
    voice_summary_en: Optional[str] = None
    voice_summary_hi: Optional[str] = None
    voice_summary_mr: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None

    @field_validator("active_ingredients", mode="before")
    @classmethod
    def parse_active_ingredients(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v

    @field_validator("inactive_excipients", mode="before")
    @classmethod
    def parse_inactive_excipients(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    model_config = ConfigDict(from_attributes=True)


class MedicineSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_name: str
    generic_name: str
    category: str
    manufacturer: str
    strength: str
    dosage_form: str
    schedule_type: Optional[str]
