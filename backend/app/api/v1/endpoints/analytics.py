from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.models.scan import Scan

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
            "timestamp": s.timestamp.isoformat() if s.timestamp else None
        }
        for s in scans
    ]
