import json
import logging
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "authorization",
    "api_key",
    "credentials",
    "client_secret",
}


def sanitize_details(data: Any) -> Any:
    """Recursively scrub sensitive keys like passwords or tokens from audit metadata."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEYS:
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = sanitize_details(v)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_details(item) for item in data]
    return data


def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[Union[str, int]] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    commit: bool = True,
) -> Optional[AuditLog]:
    """
    Records an authoritative audit log entry with sanitized metadata.
    Does not crash the request if database write encounters an issue.
    """
    try:
        sanitized = sanitize_details(details) if details else None
        details_str = json.dumps(sanitized) if sanitized is not None else None

        audit_entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            branch_id=branch_id,
            action=action.upper(),
            entity_type=entity_type.lower() if entity_type else None,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details_str,
            ip_address=ip_address,
        )
        db.add(audit_entry)
        if commit:
            db.commit()
            db.refresh(audit_entry)
        else:
            db.flush()
        return audit_entry
    except Exception as exc:
        logger.warning(f"Failed to record audit log event '{action}': {exc}")
        return None
