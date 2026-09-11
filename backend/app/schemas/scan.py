from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.medicine import MedicineResponse
from backend.app.schemas.batch import BatchResponse


class VerifyCodeRequest(BaseModel):
    code_data: Optional[str] = Field(
        None,
        description="Scanned medicine code identifier, e.g. MD110, GS1 DataMatrix string, or URL",
        json_schema_extra={"example": "MD110"}
    )
    code_or_serial: Optional[str] = Field(
        None,
        description="Alternative field for serial or raw code",
        json_schema_extra={"example": "MD110"}
    )
    source: Optional[str] = Field(
        "mobile_app",
        description="Source of scan: mobile_app | web_portal",
        json_schema_extra={"example": "mobile_app"}
    )
    device_info: Optional[str] = Field(
        None,
        description="Client device information",
        json_schema_extra={"example": "Flutter Mobile Client / Patient Phone"}
    )
    latitude: Optional[float] = Field(default=0.0, description="Optional GPS latitude", json_schema_extra={"example": 19.0760})
    longitude: Optional[float] = Field(default=0.0, description="Optional GPS longitude", json_schema_extra={"example": 72.8777})

    def get_raw_code(self) -> str:
        code = self.code_data or self.code_or_serial
        return code.strip() if code else ""


class MedicineContractInfo(BaseModel):
    id: Optional[str] = None
    name: str
    generic_name: Optional[str] = None
    dosage: str
    manufacturer: str
    description: Optional[str] = None
    storage_instructions: Optional[str] = None
    warnings: Optional[str] = None
    dosage_form: Optional[str] = None
    active_ingredients: Optional[Any] = None
    inactive_excipients: Optional[Any] = None
    voice_summary_en: Optional[str] = None
    voice_summary_hi: Optional[str] = None
    voice_summary_mr: Optional[str] = None


class BatchContractInfo(BaseModel):
    id: Optional[str] = None
    batch_number: str
    manufacture_date: Optional[str] = None
    expiry_date: str
    quantity: Optional[int] = None
    status: Optional[str] = None


class VerificationResultResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the medicine is authentic and safe to consume")
    verification_status: str = Field(..., description="AUTHENTIC, EXPIRED, SUSPECTED_COUNTERFEIT, RECALLED, REVOKED, INVALID")
    medicine: Optional[MedicineContractInfo] = None
    batch: Optional[BatchContractInfo] = None
    scanned_at: Optional[datetime] = None
    raw_code: Optional[str] = None
    message: str

    # Legacy & Extended fields for full backward compatibility
    status: Optional[str] = None
    is_genuine: Optional[bool] = None
    risk_score: int = 0
    risk_reasons: List[str] = []
    scanned_serial: Optional[str] = None
    scan_count: int = 1
    verified_at: Optional[datetime] = None
    voice_guidance: Optional[Dict[str, str]] = None


class ScanCreate(BaseModel):
    scanned_serial: str
    verification_result: str
    risk_score: int = 0
    risk_reasons: Optional[str] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code_id: Optional[int]
    user_id: Optional[int]
    scanned_serial: str
    verification_result: str
    risk_score: int
    risk_reasons: Optional[str]
    device_info: Optional[str]
    ip_address: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    timestamp: datetime
