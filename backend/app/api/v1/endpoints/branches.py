from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.branch import Branch
from backend.app.models.organization import Organization
from backend.app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from backend.app.api.v1.deps import (
    get_current_user,
    require_roles,
    normalize_role,
    get_current_active_org_id,
)

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("", response_model=List[BranchResponse])
def list_branches(
    organization_id: Optional[int] = Query(None, description="Filter by organization (SUPER_ADMIN only)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN", "ORG_ADMIN", "BRANCH_ADMIN", "OPERATOR", "VIEWER"]))
):
    """
    Lists branches belonging to the authenticated user's organization.
    Ensures strict multi-tenant isolation.
    """
    user_role = normalize_role(current_user.role)
    query = db.query(Branch)

    if user_role == "SUPER_ADMIN":
        if organization_id:
            query = query.filter(Branch.organization_id == organization_id)
    else:
        # Standard tenant scoping: strictly restrict to current user's organization
        org_id = get_current_active_org_id(current_user)
        query = query.filter(Branch.organization_id == org_id)

    if is_active is not None:
        query = query.filter(Branch.is_active == is_active)

    return query.order_by(Branch.name.asc()).all()


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(
    req: BranchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN", "ORG_ADMIN"]))
):
    """
    Creates a new branch / manufacturing facility under the caller's organization.
    Derives organization authority server-side.
    """
    user_role = normalize_role(current_user.role)
    if user_role == "SUPER_ADMIN" and req.organization_id:
        target_org_id = req.organization_id
    else:
        target_org_id = get_current_active_org_id(current_user)

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == target_org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Target organization not found")

    # Check duplicate branch code within organization
    if req.code:
        existing_code = (
            db.query(Branch)
            .filter(Branch.organization_id == target_org_id, Branch.code == req.code)
            .first()
        )
        if existing_code:
            raise HTTPException(status_code=400, detail=f"Branch code '{req.code}' already exists in this organization")

    branch = Branch(
        organization_id=target_org_id,
        name=req.name,
        code=req.code,
        address=req.address,
        city=req.city,
        state=req.state,
        contact_email=req.contact_email,
        contact_phone=req.contact_phone,
        is_active=True
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.get("/{id}", response_model=BranchResponse)
def get_branch(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN", "ORG_ADMIN", "BRANCH_ADMIN", "OPERATOR", "VIEWER"]))
):
    """Retrieves branch details by ID, enforcing tenant isolation."""
    branch = db.query(Branch).filter(Branch.id == id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    user_role = normalize_role(current_user.role)
    if user_role != "SUPER_ADMIN":
        org_id = get_current_active_org_id(current_user)
        if branch.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied: Branch belongs to another organization")

    return branch


@router.patch("/{id}", response_model=BranchResponse)
@router.put("/{id}", response_model=BranchResponse)
def update_branch(
    id: int,
    req: BranchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN", "ORG_ADMIN", "BRANCH_ADMIN"]))
):
    """Updates branch details with role authorization checks."""
    branch = db.query(Branch).filter(Branch.id == id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    user_role = normalize_role(current_user.role)
    if user_role != "SUPER_ADMIN":
        org_id = get_current_active_org_id(current_user)
        if branch.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied: Branch belongs to another organization")
        # If branch admin, can only edit their own branch
        if user_role == "BRANCH_ADMIN" and current_user.branch_id and current_user.branch_id != branch.id:
            raise HTTPException(status_code=403, detail="Access denied: You can only manage your assigned branch")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)

    db.commit()
    db.refresh(branch)
    return branch


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN", "ORG_ADMIN"]))
):
    """Deletes a branch (requires ORG_ADMIN or SUPER_ADMIN)."""
    branch = db.query(Branch).filter(Branch.id == id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    user_role = normalize_role(current_user.role)
    if user_role != "SUPER_ADMIN":
        org_id = get_current_active_org_id(current_user)
        if branch.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied: Branch belongs to another organization")

    db.delete(branch)
    db.commit()
    return None
