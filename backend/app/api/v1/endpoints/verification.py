from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.scan import VerifyCodeRequest, VerificationResultResponse
from backend.app.services.verifier import verify_medicine_code
from backend.app.api.v1.deps import get_current_user

router = APIRouter(prefix="/codes", tags=["Verification"])


@router.post("/verify", response_model=VerificationResultResponse)
def verify_code(
    req: VerifyCodeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Public Verification API for Mobile App (Flutter camera scanner) and Web.
    Validates serial identifier, checks batch expiry, detects suspicious duplicate scans,
    and returns full verified medicine specifications with accessibility voice guidance.
    """
    client_ip = request.client.host if request.client else None
    user_id = current_user.id if current_user else None

    result = verify_medicine_code(
        db=db,
        raw_input=req.code_or_serial,
        device_info=req.device_info or "Mobile Scanner",
        ip_address=client_ip,
        latitude=req.latitude,
        longitude=req.longitude,
        user_id=user_id
    )

    return result
