from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.branch import Branch
from backend.app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    Token,
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
)
from backend.app.api.v1.deps import get_current_user, normalize_role
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Registers a new company admin or platform user."""
    # Check if user already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Normalize role
    user_role = normalize_role(req.role)

    # Handle organization creation if registering as ORG_ADMIN
    org_id = None
    org_name = None
    if req.organization_name:
        org = db.query(Organization).filter(Organization.name == req.organization_name).first()
        if not org:
            org = Organization(
                name=req.organization_name,
                licence_no=req.licence_no or "LIC-GEN-2026",
                contact_email=req.email,
                address=req.address or "Pharmaceutical Industrial Estate"
            )
            db.add(org)
            db.flush()
        org_id = org.id
        org_name = org.name

    hashed_pw = get_password_hash(req.password)
    new_user = User(
        name=req.name,
        email=req.email,
        password_hash=hashed_pw,
        role=req.role or "ORG_ADMIN",
        organization_id=org_id,
        branch_id=req.branch_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db=db,
        action="USER_REGISTERED",
        user_id=new_user.id,
        organization_id=new_user.organization_id,
        branch_id=new_user.branch_id,
        entity_type="user",
        entity_id=new_user.id,
        details={"email": new_user.email, "role": new_user.role},
    )

    token = create_access_token(
        subject=new_user.id,
        extra_claims={
            "role": new_user.role,
            "org_id": new_user.organization_id,
            "branch_id": new_user.branch_id
        }
    )

    branch_name = new_user.branch.name if new_user.branch else None

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        organization_id=new_user.organization_id,
        organization_name=org_name,
        branch_id=new_user.branch_id,
        branch_name=branch_name
    )


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT bearer token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    log_audit_event(
        db=db,
        action="LOGIN",
        user_id=user.id,
        organization_id=user.organization_id,
        branch_id=user.branch_id,
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "role": user.role},
    )

    org_name = user.organization.name if user.organization else None
    branch_name = user.branch.name if user.branch else None

    token = create_access_token(
        subject=user.id,
        extra_claims={
            "role": user.role,
            "org_id": user.organization_id,
            "branch_id": user.branch_id
        }
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization_id=user.organization_id,
        organization_name=org_name,
        branch_id=user.branch_id,
        branch_name=branch_name
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refreshes the caller's JWT access token."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    log_audit_event(
        db=db,
        action="REFRESH_TOKEN",
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        branch_id=current_user.branch_id,
        entity_type="user",
        entity_id=current_user.id,
    )

    new_token = create_access_token(
        subject=current_user.id,
        extra_claims={
            "role": current_user.role,
            "org_id": current_user.organization_id,
            "branch_id": current_user.branch_id
        }
    )

    return RefreshTokenResponse(
        access_token=new_token,
        token_type="bearer",
        user_id=current_user.id,
        role=current_user.role,
        organization_id=current_user.organization_id,
        branch_id=current_user.branch_id
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logs out current user session."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    log_audit_event(
        db=db,
        action="LOGOUT",
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        branch_id=current_user.branch_id,
        entity_type="user",
        entity_id=current_user.id,
    )

    return LogoutResponse(status="success", message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return current_user
