from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.medicine import MedicineSummary


class BatchBase(BaseModel):
    batch_no: str
    mfg_date: date
    exp_date: date
    quantity: int = 10000
    mrp: float = 50.0
    status: str = "active"


class BatchCreate(BatchBase):
    medicine_id: int


class BatchUpdate(BaseModel):
    batch_no: Optional[str] = None
    mfg_date: Optional[date] = None
    exp_date: Optional[date] = None
    quantity: Optional[int] = None
    mrp: Optional[float] = None
    status: Optional[str] = None


class BatchResponse(BatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medicine_id: int
    created_at: Optional[datetime] = None


class BatchDetailResponse(BatchResponse):
    model_config = ConfigDict(from_attributes=True)

    medicine: Optional[MedicineSummary] = None
