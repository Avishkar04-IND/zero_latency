from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CodeGenerateRequest(BaseModel):
    batch_id: int = Field(
        default=1,
        ge=1,
        description="ID of the production batch in database (e.g. 1 for Dolo 650, 2 for Augmentin)",
        json_schema_extra={"example": 1}
    )
    count: int = Field(
        default=1,
        ge=1,
        le=500,
        description="Number of unique codes to generate (max 500 per batch)",
        json_schema_extra={"example": 1}
    )


class CodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    serial_number: str
    code_hash: str
    qr_data_url: Optional[str] = None
    qr_svg: Optional[str] = None
    datamatrix_code: Optional[str] = None
    status: str
    scan_count: int
    first_scanned_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class CodeGenerateBatchResponse(BaseModel):
    total_generated: int
    batch_id: int
    batch_no: str
    medicine_name: str
    codes: List[CodeResponse]
