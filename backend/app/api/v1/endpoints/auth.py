from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.schemas.auth import LoginRequest, SignupRequest, Token, UserResponse
from backend.app.api.v1.deps import get_current_user

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

    # Handle organization creation if registering as company_admin
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
        role=req.role,
        organization_id=org_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        subject=new_user.id,
        extra_claims={
            "role": new_user.role,
            "org_id": new_user.organization_id
        }
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        organization_id=new_user.organization_id,
        organization_name=org_name
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

    org_name = user.organization.name if user.organization else None

    token = create_access_token(
        subject=user.id,
        extra_claims={
            "role": user.role,
            "org_id": user.organization_id
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
        organization_name=org_name
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return current_user
