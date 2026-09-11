import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.models.scan import Scan
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.audit import AuditLogResponse
from backend.app.schemas.analytics import (
    AnalyticsOverviewResponse,
    RiskAnalyticsResponse,
    RiskAlertItem,
    BatchesAnalyticsResponse,
    CodesAnalyticsResponse,
)
from backend.app.api.v1.deps import get_current_user, normalize_role

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns high-level platform statistics for the Web Admin Dashboard:
    Medicine counts, batches, generated codes, scan totals, and counterfeit alert metrics.
    """
    total_meds = db.query(Medicine).count()
    total_batches = db.query(Batch).count()
    total_codes = db.query(Code).count()
    total_scans = db.query(Scan).count()

    # Scan results breakdown
    results_count = (
        db.query(Scan.verification_result, func.count(Scan.id))
        .group_by(Scan.verification_result)
        .all()
    )
    breakdown = {k: v for k, v in results_count}

    genuine_count = breakdown.get("GENUINE", 0)
    suspicious_count = breakdown.get("SUSPICIOUS_MULTIPLE_SCANS", 0) + breakdown.get("SUSPICIOUS", 0)
    invalid_count = breakdown.get("INVALID", 0)
    expired_count = breakdown.get("EXPIRED", 0)

    authenticity_rate = round((genuine_count / max(1, total_scans)) * 100, 1)

    # Top scanned medicines
    top_scans = (
        db.query(Scan.scanned_serial, func.count(Scan.id).label("count"))
        .group_by(Scan.scanned_serial)
        .order_by(func.count(Scan.id).desc())
        .limit(5)
        .all()
    )

    recent_alerts = (
        db.query(Scan)
        .filter(Scan.verification_result != "GENUINE")
        .order_by(Scan.timestamp.desc())
        .limit(6)
        .all()
    )

    return {
        "overview": {
            "total_medicines": total_meds,
            "total_batches": total_batches,
            "total_codes_generated": total_codes,
            "total_scans": total_scans,
            "authenticity_rate": authenticity_rate
        },
        "breakdown": {
            "genuine": genuine_count,
            "suspicious": suspicious_count,
            "invalid": invalid_count,
            "expired": expired_count
        },
        "recent_alerts": [
            {
                "id": a.id,
                "serial": a.scanned_serial,
                "result": a.verification_result,
                "risk_score": a.risk_score,
                "device": a.device_info,
                "time": a.timestamp.isoformat() if a.timestamp else None
            }
            for a in recent_alerts
        ],
        "top_scanned_serials": [{"serial": s[0], "scans": s[1]} for s in top_scans]
    }


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Authoritative overview of medicines, batches, codes, and authenticity performance."""
    total_meds = db.query(Medicine).count()
    total_batches = db.query(Batch).count()
    total_codes = db.query(Code).count()
    total_scans = db.query(Scan).count()

    genuine_count = db.query(Scan).filter(Scan.verification_result == "GENUINE").count()
    authenticity_rate = round((genuine_count / max(1, total_scans)) * 100, 1)

    active_batches = db.query(Batch).filter(Batch.status == "active").count()
    quarantined_batches = db.query(Batch).filter(Batch.status == "quarantined").count()
    recalled_batches = db.query(Batch).filter(Batch.status == "recalled").count()
    expired_batches = db.query(Batch).filter(Batch.status == "expired").count()

    return AnalyticsOverviewResponse(
        total_medicines=total_meds,
        total_batches=total_batches,
        total_codes_generated=total_codes,
        total_scans=total_scans,
        authenticity_rate=authenticity_rate,
        active_batches=active_batches,
        quarantined_batches=quarantined_batches,
        recalled_batches=recalled_batches,
        expired_batches=expired_batches,
    )


@router.get("/risk", response_model=RiskAnalyticsResponse)
def get_risk_analytics(db: Session = Depends(get_db)):
    """Returns risk distribution, average score, and active anomaly alerts."""
    scans = db.query(Scan).all()
    total_scans = len(scans)
    
    if total_scans == 0:
        return RiskAnalyticsResponse(
            average_risk_score=0.0,
            low_risk_scans=0,
            medium_risk_scans=0,
            high_risk_scans=0,
            counterfeit_alert_count=0,
            recent_alerts=[],
        )

    total_risk = sum(s.risk_score for s in scans)
    avg_risk = round(total_risk / total_scans, 1)

    low_risk = sum(1 for s in scans if s.risk_score <= 20)
    med_risk = sum(1 for s in scans if 20 < s.risk_score <= 60)
    high_risk = sum(1 for s in scans if s.risk_score > 60)

    alerts = (
        db.query(Scan)
        .filter(Scan.verification_result != "GENUINE")
        .order_by(Scan.timestamp.desc())
        .limit(10)
        .all()
    )

    alert_items = []
    for a in alerts:
        reasons = None
        if a.risk_reasons:
            try:
                reasons = json.loads(a.risk_reasons)
            except Exception:
                reasons = a.risk_reasons
        alert_items.append(
            RiskAlertItem(
                id=a.id,
                serial=a.scanned_serial,
                result=a.verification_result,
                risk_score=a.risk_score,
                device=a.device_info,
                time=a.timestamp.isoformat() if a.timestamp else None,
                risk_reasons=reasons,
            )
        )

    return RiskAnalyticsResponse(
        average_risk_score=avg_risk,
        low_risk_scans=low_risk,
        medium_risk_scans=med_risk,
        high_risk_scans=high_risk,
        counterfeit_alert_count=len(alerts),
        recent_alerts=alert_items,
    )


@router.get("/batches", response_model=BatchesAnalyticsResponse)
def get_batches_analytics(db: Session = Depends(get_db)):
    """Returns manufacturing batches breakdown by status, total volume and inventory MRP value."""
    batches = db.query(Batch).all()
    status_counts: Dict[str, int] = {}
    total_qty = 0
    total_value = 0.0

    for b in batches:
        status_counts[b.status] = status_counts.get(b.status, 0) + 1
        total_qty += b.quantity or 0
        total_value += (b.quantity or 0) * (b.mrp or 0.0)

    return BatchesAnalyticsResponse(
        total_batches=len(batches),
        by_status=status_counts,
        total_units_manufactured=total_qty,
        total_inventory_value_mrp=round(total_value, 2),
    )


@router.get("/codes", response_model=CodesAnalyticsResponse)
def get_codes_analytics(db: Session = Depends(get_db)):
    """Returns code lifecycle statistics: total active, revoked, and scan counts."""
    total_codes = db.query(Code).count()
    active_codes = db.query(Code).filter(Code.status == "active").count()
    revoked_codes = db.query(Code).filter(Code.status == "revoked").count()
    scanned_codes = db.query(Code).filter(Code.scan_count > 0).count()
    unscanned_codes = db.query(Code).filter(Code.scan_count == 0).count()

    max_scans_result = db.query(func.max(Code.scan_count)).scalar()
    max_scans = max_scans_result or 0

    return CodesAnalyticsResponse(
        total_codes=total_codes,
        active_codes=active_codes,
        revoked_codes=revoked_codes,
        scanned_codes=scanned_codes,
        unscanned_codes=unscanned_codes,
        max_single_code_scans=max_scans,
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by event action (e.g. LOGIN, BATCH_CREATED)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g. batch, user, code)"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns platform audit log trail with optional action and entity filtering.
    Enforces organizational tenancy boundaries for ORG_ADMIN and subordinate users.
    """
    query = db.query(AuditLog)

    if current_user and current_user.organization_id:
        user_role = normalize_role(current_user.role)
        if user_role != "SUPER_ADMIN":
            query = query.filter(AuditLog.organization_id == current_user.organization_id)

    if action:
        query = query.filter(AuditLog.action == action.upper())
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type.lower())
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for log in logs:
        details_val = log.details
        if details_val and isinstance(details_val, str):
            try:
                details_val = json.loads(details_val)
            except Exception:
                pass
        results.append(
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                organization_id=log.organization_id,
                branch_id=log.branch_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                details=details_val,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
        )
    return results


@router.get("/scans")
def get_scan_analytics(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Returns geolocation and timestamp data of recent scans for maps and heatmaps."""
    scans = db.query(Scan).order_by(Scan.timestamp.desc()).limit(100).all()
    return [
        {
            "id": s.id,
            "serial": s.scanned_serial,
            "result": s.verification_result,
            "risk_score": s.risk_score,
            "latitude": s.location_lat,
            "longitude": s.location_lng,
            "device": s.device_info,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
        }
        for s in scans
    ]
