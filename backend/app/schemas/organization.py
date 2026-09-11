from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.branch import BranchResponse


class OrganizationBase(BaseModel):
    name: str
    licence_no: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    licence_no: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class OrganizationDetailResponse(OrganizationResponse):
    branches: List[BranchResponse] = []
