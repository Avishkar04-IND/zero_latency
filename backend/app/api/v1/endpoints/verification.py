from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.scan import VerifyCodeRequest, VerificationResultResponse
from backend.app.services.verifier import verify_medicine_code
from backend.app.api.v1.deps import get_current_user

router = APIRouter(tags=["Verification"])


@router.post("/verification/verify", response_model=VerificationResultResponse)
@router.post("/codes/verify", response_model=VerificationResultResponse)
def verify_code(
    req: VerifyCodeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Unified Verification API supporting:
    - Shared API Contract & Flutter Mobile (RealApiService): POST /api/v1/verification/verify
    - Web Portal & Legacy: POST /api/v1/codes/verify
    Validates serial/identifier (e.g. MD110), checks batch expiry, detects counterfeits,
    and returns full verified medicine specifications with accessibility voice guidance.
    """
    raw_code = req.get_raw_code()
    if not raw_code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "code_data is required and cannot be empty",
                    "details": ["Field 'code_data' must be a non-empty string"]
                }
            }
        )

    client_ip = request.client.host if request.client else None
    user_id = current_user.id if current_user else None

    result = verify_medicine_code(
        db=db,
        raw_input=raw_code,
        device_info=req.device_info or req.source or "Mobile Scanner",
        ip_address=client_ip,
        latitude=req.latitude,
        longitude=req.longitude,
        user_id=user_id
    )

    return result
