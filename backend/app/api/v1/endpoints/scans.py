from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.scan import Scan
from backend.app.schemas.scan import ScanCreate, ScanResponse
from backend.app.api.v1.deps import get_current_user

router = APIRouter(prefix="/scans", tags=["Scans & Audit"])


@router.get("", response_model=List[ScanResponse])
def list_scans(
    limit: int = Query(50, ge=1, le=200),
    result_filter: Optional[str] = Query(None, description="Filter by result (GENUINE, EXPIRED, SUSPICIOUS, INVALID)"),
    db: Session = Depends(get_db)
):
    """Lists audit scan events across the platform for fraud monitoring."""
    query = db.query(Scan)
    if result_filter:
        query = query.filter(Scan.verification_result.ilike(f"%{result_filter}%"))
    return query.order_by(Scan.timestamp.desc()).limit(limit).all()


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def record_scan_event(
    req: ScanCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Manually records an external scan event into the audit log."""
    user_id = current_user.id if current_user else None
    scan = Scan(
        scanned_serial=req.scanned_serial,
        verification_result=req.verification_result,
        risk_score=req.risk_score,
        risk_reasons=req.risk_reasons,
        device_info=req.device_info,
        ip_address=req.ip_address,
        location_lat=req.location_lat,
        location_lng=req.location_lng,
        user_id=user_id
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan
