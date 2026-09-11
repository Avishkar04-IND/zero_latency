from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class LayoutPrintMedicineInfo(BaseModel):
    name: str
    generic_name: str
    strength: str
    dosage_form: str
    tablet_shape: Optional[str] = None
    tablet_color: Optional[str] = None
    coating_type: Optional[str] = None
    active_ingredients: Optional[Any] = None
    inactive_excipients: Optional[Any] = None
    storage_conditions: Optional[str] = None
    schedule_type: Optional[str] = None


class LayoutPrintBatchInfo(BaseModel):
    batch_number: str
    mfg_date: str
    exp_date: str
    quantity: int
    mrp: float
    status: str


class LayoutPrintManufacturerInfo(BaseModel):
    name: str
    licence_no: str
    contact_email: str
    address: Optional[str] = None


class LayoutPrintBranchInfo(BaseModel):
    name: str
    code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None


class LayoutPrintLabelData(BaseModel):
    line1_header: str = Field(..., description="Brand name & strength header")
    line2_generic: str = Field(..., description="Generic name / INN classification")
    line3_batch_exp: str = Field(..., description="Batch number, mfg, and exp string")
    line4_mrp: str = Field(..., description="Formatted Maximum Retail Price in INR")
    line5_storage: str = Field(..., description="Storage & environmental instructions")
    line6_license: str = Field(..., description="Manufacturing license attribution")
    barcode_payload: str = Field(..., description="GS1 DataMatrix or verification URL payload")


class LayoutPrintDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    serial_number: str
    code_hash: str
    datamatrix_code: Optional[str] = None
    qr_svg: Optional[str] = None
    qr_data_url: Optional[str] = None
    medicine: LayoutPrintMedicineInfo
    batch: LayoutPrintBatchInfo
    manufacturer: LayoutPrintManufacturerInfo
    branch: Optional[LayoutPrintBranchInfo] = None
    warnings: List[str] = []
    print_data: LayoutPrintLabelData


class LayoutBatchPrintDataResponse(BaseModel):
    batch: LayoutPrintBatchInfo
    medicine: LayoutPrintMedicineInfo
    manufacturer: LayoutPrintManufacturerInfo
    branch: Optional[LayoutPrintBranchInfo] = None
    label_template: LayoutPrintLabelData
    total_codes: int
    unit_codes: List[LayoutPrintDataResponse]
