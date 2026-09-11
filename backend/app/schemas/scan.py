from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.medicine import MedicineResponse
from backend.app.schemas.batch import BatchResponse


class VerifyCodeRequest(BaseModel):
    code_or_serial: str = Field(
        ...,
        description="Medicine code to verify: serial (e.g. MED-FA5A-40E0-DBD1), scanned QR URL (https://smartmed.org/v/...), or GS1 DataMatrix string",
        json_schema_extra={"example": "MED-FA5A-40E0-DBD1"}
    )
    device_info: Optional[str] = Field(
        default="Mobile Scanner",
        description="Client device information",
        json_schema_extra={"example": "Flutter Mobile Client / Patient Phone"}
    )
    latitude: Optional[float] = Field(default=None, description="Optional GPS latitude for geolocation telemetry", json_schema_extra={"example": 19.0760})
    longitude: Optional[float] = Field(default=None, description="Optional GPS longitude for geolocation telemetry", json_schema_extra={"example": 72.8777})


class VerificationResultResponse(BaseModel):
    status: str  # GENUINE, EXPIRED, SUSPICIOUS_MULTIPLE_SCANS, INVALID, REVOKED
    is_genuine: bool
    risk_score: int  # 0 to 100
    risk_reasons: List[str] = []
    scanned_serial: str
    scan_count: int
    message: str
    verified_at: datetime
    medicine: Optional[MedicineResponse] = None
    batch: Optional[BatchResponse] = None
    voice_guidance: Optional[Dict[str, str]] = None  # Key audio fields for TTS


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
