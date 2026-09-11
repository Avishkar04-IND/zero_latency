from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    total_medicines: int
    total_batches: int
    total_codes_generated: int
    total_scans: int
    authenticity_rate: float
    active_batches: int
    quarantined_batches: int
    recalled_batches: int
    expired_batches: int


class RiskAlertItem(BaseModel):
    id: int
    serial: str
    result: str
    risk_score: int
    device: Optional[str] = None
    time: Optional[str] = None
    risk_reasons: Optional[Any] = None


class RiskAnalyticsResponse(BaseModel):
    average_risk_score: float
    low_risk_scans: int
    medium_risk_scans: int
    high_risk_scans: int
    counterfeit_alert_count: int
    recent_alerts: List[RiskAlertItem]


class BatchesAnalyticsResponse(BaseModel):
    total_batches: int
    by_status: Dict[str, int]
    total_units_manufactured: int
    total_inventory_value_mrp: float


class CodesAnalyticsResponse(BaseModel):
    total_codes: int
    active_codes: int
    revoked_codes: int
    scanned_codes: int
    unscanned_codes: int
    max_single_code_scans: int
