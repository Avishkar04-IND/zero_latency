from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BranchBase(BaseModel):
    name: str = Field(..., description="Branch or manufacturing facility name", json_schema_extra={"example": "Mumbai Unit 1"})
    code: Optional[str] = Field(None, description="Unique facility identifier/code", json_schema_extra={"example": "BR-MUM-01"})
    address: Optional[str] = Field(None, description="Physical location address", json_schema_extra={"example": "Plot 42, MIDC Industrial Area"})
    city: Optional[str] = Field(None, description="City", json_schema_extra={"example": "Mumbai"})
    state: Optional[str] = Field(None, description="State / Province", json_schema_extra={"example": "Maharashtra"})
    contact_email: Optional[str] = Field(None, description="Branch contact email", json_schema_extra={"example": "mumbai.unit1@pharma.com"})
    contact_phone: Optional[str] = Field(None, description="Branch phone number", json_schema_extra={"example": "+91-22-5555-0101"})


class BranchCreate(BranchBase):
    organization_id: Optional[int] = Field(None, description="Optional organization override for super admins")


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
