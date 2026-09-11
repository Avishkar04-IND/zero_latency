import json
import re
from datetime import date, datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from backend.app.models.code import Code
from backend.app.models.batch import Batch
from backend.app.models.medicine import Medicine
from backend.app.models.scan import Scan


def extract_serial_number(raw_input: str) -> str:
    """
    Intelligently extracts the medicine serial number from various scanner formats:
    - Direct serial: 'MED-7A9K-W8Q4-P1B2'
    - Web verification URL: 'https://smartmed.org/verify?serial=MED-7A9K-W8Q4-P1B2'
    - GS1 DataMatrix string: '(01)08901234567890(17)261231(10)BT99(21)MED-7A9K-W8Q4-P1B2'
    - Scanned JSON: '{"serial": "MED-7A9K-W8Q4-P1B2"}'
    """
    trimmed = raw_input.strip()

    # 1. Check if JSON
    if trimmed.startswith("{") and trimmed.endswith("}"):
        try:
            data = json.loads(trimmed)
            if "serial" in data:
                return data["serial"]
            if "serial_number" in data:
                return data["serial_number"]
        except Exception:
            pass

    # 2. Check GS1 Application Identifier (21)
    gs1_match = re.search(r"\(21\)([A-Za-z0-9\-]+)", trimmed)
    if gs1_match:
        return gs1_match.group(1)

    # 3. Check URL parameters
    url_match = re.search(r"[?&](?:serial|code|id)=([A-Za-z0-9\-]+)", trimmed)
    if url_match:
        return url_match.group(1)

    # 4. Standard MED-XXXX-XXXX regex match
    med_match = re.search(r"(MED-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)", trimmed)
    if med_match:
        return med_match.group(1)

    # Fallback to direct string
    return trimmed


def verify_medicine_code(
    db: Session,
    raw_input: str,
    device_info: Optional[str] = "Mobile Scanner",
    ip_address: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Core verification and anti-counterfeit analysis engine.
    """
    serial = extract_serial_number(raw_input)
    now = datetime.now(timezone.utc)
    today = date.today()

    # Lookup code in database
    code_record = db.query(Code).filter(Code.serial_number == serial).first()

    if not code_record:
        # Code does NOT exist: Definite counterfeit or unregistered
        scan_log = Scan(
            code_id=None,
            user_id=user_id,
            scanned_serial=serial,
            verification_result="INVALID",
            risk_score=100,
            risk_reasons=json.dumps(["Unregistered serial number: Not found in pharmaceutical registry"]),
            device_info=device_info,
            ip_address=ip_address,
            location_lat=latitude,
            location_lng=longitude,
            timestamp=now
        )
        db.add(scan_log)
        db.commit()

        return {
            "is_valid": False,
            "verification_status": "INVALID",
            "medicine": None,
            "batch": None,
            "scanned_at": now,
            "raw_code": serial,
            "message": "ALERT: Counterfeit / Invalid Code detected. This medicine package is unverified and potentially unsafe.",
            "status": "INVALID",
            "is_genuine": False,
            "risk_score": 100,
            "risk_reasons": ["Unregistered serial number: Code does not exist in the official manufacturer database"],
            "scanned_serial": serial,
            "scan_count": 1,
            "verified_at": now,
            "voice_guidance": {
                "status_alert": "Warning! Unverified or counterfeit medicine.",
                "medicine_info": "Unregistered medicine code.",
                "expiry_info": "Unknown",
                "instructions": "Do not consume. Contact your pharmacist immediately."
            }
        }

    # Fetch batch & medicine
    batch = code_record.batch
    medicine = batch.medicine if batch else None

    risk_reasons: List[str] = []
    risk_score = 0
    status = "GENUINE"

    # Check 1: Batch or code status
    if code_record.status in ["revoked", "recalled"] or (batch and batch.status == "recalled"):
        status = "REVOKED"
        risk_score = 100
        risk_reasons.append("Batch or specific unit has been recalled by manufacturer or regulatory authorities")

    # Check 2: Expiry check
    elif batch and batch.exp_date < today:
        status = "EXPIRED"
        risk_score = 75
        risk_reasons.append(f"Medicine expired on {batch.exp_date.strftime('%B %d, %Y')}")

    # Check 3: Repeated scan evaluation (Contextual anomaly detection)
    new_scan_count = code_record.scan_count + 1
    if status == "GENUINE":
        if new_scan_count > 5:
            status = "SUSPICIOUS_MULTIPLE_SCANS"
            risk_score = min(90, 40 + (new_scan_count * 5))
            risk_reasons.append(
                f"Abnormal scan frequency: This unit code has been scanned {new_scan_count} times."
            )
        elif new_scan_count > 1:
            # Re-scanned 2-5 times (Likely consumer reviewing details)
            risk_reasons.append(f"Previously scanned {code_record.scan_count} time(s). Verified authentic packaging.")

    # Update code record
    if code_record.first_scanned_at is None:
        code_record.first_scanned_at = now
    code_record.last_scanned_at = now
    code_record.scan_count = new_scan_count

    # Create scan audit log
    scan_log = Scan(
        code_id=code_record.id,
        user_id=user_id,
        scanned_serial=serial,
        verification_result=status,
        risk_score=risk_score,
        risk_reasons=json.dumps(risk_reasons),
        device_info=device_info,
        ip_address=ip_address,
        location_lat=latitude,
        location_lng=longitude,
        timestamp=now
    )
    db.add(scan_log)
    db.commit()

    # Formulate user-friendly message
    if status == "GENUINE":
        message = f"Verified Genuine: {medicine.brand_name if medicine else 'Medicine'} ({medicine.generic_name if medicine else ''}) is authentic."
    elif status == "EXPIRED":
        message = f"EXPIRED MEDICINE: {medicine.brand_name if medicine else 'Medicine'} reached expiry on {batch.exp_date if batch else 'unknown'}. Do NOT consume."
    elif status == "REVOKED":
        message = f"RECALLED PRODUCT: Batch {batch.batch_no if batch else 'unknown'} has been officially recalled. Do not consume."
    else:
        message = f"SUSPICIOUS ACTIVITY: Code scanned {new_scan_count} times. Verify physical foil integrity."

    # Voice guidance for TTS
    voice_guidance = {
        "status_alert": f"{'Genuine verified medicine' if status == 'GENUINE' else 'Warning: ' + status}",
        "medicine_info": f"{medicine.brand_name if medicine else ''} {medicine.strength if medicine else ''}, generic {medicine.generic_name if medicine else ''}.",
        "expiry_info": f"Expiry date is {batch.exp_date.strftime('%B %Y') if batch else 'unknown'}.",
        "instructions": medicine.dosage_instructions if medicine else ""
    }

    # Map status to shared API contract status
    if status == "GENUINE":
        contract_status = "AUTHENTIC"
    elif status == "EXPIRED":
        contract_status = "EXPIRED"
    elif status == "REVOKED":
        contract_status = "RECALLED"
    elif status == "SUSPICIOUS_MULTIPLE_SCANS":
        contract_status = "SUSPECTED_COUNTERFEIT"
    else:
        contract_status = "INVALID"

    is_valid = (contract_status == "AUTHENTIC")

    med_info = None
    if medicine:
        med_info = {
            "id": str(medicine.id),
            "name": medicine.brand_name,
            "generic_name": medicine.generic_name,
            "dosage": medicine.strength or medicine.dosage_instructions or "Standard",
            "manufacturer": medicine.manufacturer or (medicine.organization.name if medicine.organization else "Unknown"),
            "description": medicine.indications or "",
            "storage_instructions": medicine.storage_conditions or "",
            "warnings": medicine.warnings_and_precautions or "",
            "dosage_form": medicine.dosage_form,
            "active_ingredients": medicine.active_ingredients,
            "inactive_excipients": medicine.inactive_excipients,
            "voice_summary_en": medicine.voice_summary_en,
            "voice_summary_hi": medicine.voice_summary_hi,
            "voice_summary_mr": medicine.voice_summary_mr
        }

    batch_info = None
    if batch:
        batch_info = {
            "id": str(batch.id),
            "batch_number": batch.batch_no,
            "manufacture_date": str(batch.mfg_date) if batch.mfg_date else None,
            "expiry_date": str(batch.exp_date),
            "quantity": batch.quantity,
            "status": batch.status
        }

    return {
        "is_valid": is_valid,
        "verification_status": contract_status,
        "medicine": med_info,
        "batch": batch_info,
        "scanned_at": now,
        "raw_code": serial,
        "message": message,
        "status": status,
        "is_genuine": (status == "GENUINE"),
        "risk_score": risk_score,
        "risk_reasons": risk_reasons,
        "scanned_serial": serial,
        "scan_count": new_scan_count,
        "verified_at": now,
        "voice_guidance": voice_guidance
    }
