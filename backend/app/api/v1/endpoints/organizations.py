from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.organization import Organization
from backend.app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from backend.app.api.v1.deps import require_admin_user

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    """Lists registered pharmaceutical manufacturers and organizations."""
    return db.query(Organization).order_by(Organization.name).all()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    req: OrganizationCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin_user)
):
    """Registers a new pharmaceutical company/manufacturer."""
    existing = db.query(Organization).filter(Organization.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this name already exists")

    org = Organization(
        name=req.name,
        licence_no=req.licence_no,
        contact_email=req.contact_email,
        contact_phone=req.contact_phone,
        address=req.address
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/{id}", response_model=OrganizationResponse)
def get_organization(id: int, db: Session = Depends(get_db)):
    """Retrieves organization details by ID."""
    org = db.query(Organization).filter(Organization.id == id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
