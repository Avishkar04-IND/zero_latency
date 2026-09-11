from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.batch import Batch
from backend.app.models.medicine import Medicine
from backend.app.schemas.batch import BatchCreate, BatchUpdate, BatchResponse, BatchDetailResponse
from backend.app.api.v1.deps import get_current_user, normalize_role
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchDetailResponse])
def list_batches(
    medicine_id: Optional[int] = Query(None, description="Filter batches by medicine"),
    branch_id: Optional[int] = Query(None, description="Filter batches by manufacturing branch"),
    status_filter: Optional[str] = Query(None, description="Filter by status (active, expired, recalled)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Lists manufacturing batches with optional filters.
    Enforces organizational tenant boundaries for manufacturer users.
    """
    query = db.query(Batch)

    # Tenant scoping if authenticated
    if current_user and current_user.organization_id:
        user_role = normalize_role(current_user.role)
        if user_role != "SUPER_ADMIN":
            query = query.join(Batch.medicine).filter(Medicine.organization_id == current_user.organization_id)

    if medicine_id:
        query = query.filter(Batch.medicine_id == medicine_id)
    if branch_id:
        query = query.filter(Batch.branch_id == branch_id)
    if status_filter:
        query = query.filter(Batch.status == status_filter)

    batches = query.order_by(Batch.exp_date.desc()).all()
    results = []
    for b in batches:
        b_dict = {
            "id": b.id,
            "medicine_id": b.medicine_id,
            "batch_no": b.batch_no,
            "mfg_date": b.mfg_date,
            "exp_date": b.exp_date,
            "quantity": b.quantity,
            "mrp": b.mrp,
            "status": b.status,
            "branch_id": b.branch_id,
            "created_by": b.created_by,
            "created_at": b.created_at,
            "branch_name": b.branch.name if b.branch else None,
            "medicine": b.medicine
        }
        results.append(BatchDetailResponse.model_validate(b_dict))
    return results


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    req: BatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Creates a new production batch for a registered medicine.
    Enforces dates/quantity validation and derives creator & branch context server-side.
    """
    # 1. Timeline validation
    if req.exp_date <= req.mfg_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expiry date must be after manufacture date"
        )

    # 2. Quantity validation
    if req.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    # 3. Lookup medicine master record
    med = db.query(Medicine).filter(Medicine.id == req.medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # 4. Multi-tenant isolation check
    if current_user and current_user.organization_id:
        user_role = normalize_role(current_user.role)
        if user_role != "SUPER_ADMIN" and med.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot create batches for medicines belonging to another organization"
            )

    # 5. Authoritative context derivation
    created_by = current_user.id if current_user else None
    branch_id = req.branch_id
    if not branch_id and current_user and current_user.branch_id:
        branch_id = current_user.branch_id

    batch = Batch(
        medicine_id=req.medicine_id,
        branch_id=branch_id,
        created_by=created_by,
        batch_no=req.batch_no,
        mfg_date=req.mfg_date,
        exp_date=req.exp_date,
        quantity=req.quantity,
        mrp=req.mrp,
        status=req.status
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    log_audit_event(
        db=db,
        action="BATCH_CREATED",
        user_id=current_user.id if current_user else None,
        organization_id=med.organization_id,
        branch_id=batch.branch_id,
        entity_type="batch",
        entity_id=batch.id,
        details={
            "batch_no": batch.batch_no,
            "medicine_id": batch.medicine_id,
            "quantity": batch.quantity,
            "status": batch.status,
        },
    )

    return batch


@router.get("/{id}", response_model=BatchDetailResponse)
def get_batch(id: int, db: Session = Depends(get_db)):
    """Retrieves batch details by ID with auto-populated registered medicine specifications."""
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    b_dict = {
        "id": batch.id,
        "medicine_id": batch.medicine_id,
        "batch_no": batch.batch_no,
        "mfg_date": batch.mfg_date,
        "exp_date": batch.exp_date,
        "quantity": batch.quantity,
        "mrp": batch.mrp,
        "status": batch.status,
        "branch_id": batch.branch_id,
        "created_by": batch.created_by,
        "created_at": batch.created_at,
        "branch_name": batch.branch.name if batch.branch else None,
        "medicine": batch.medicine
    }
    return BatchDetailResponse.model_validate(b_dict)


@router.patch("/{id}", response_model=BatchResponse)
@router.put("/{id}", response_model=BatchResponse)
def update_batch(
    id: int,
    req: BatchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Updates batch information, including recall actions (supports both PATCH and PUT)."""
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Multi-tenant isolation check
    if current_user and current_user.organization_id:
        user_role = normalize_role(current_user.role)
        if user_role != "SUPER_ADMIN" and batch.medicine.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot edit batches of another organization"
            )

    update_data = req.model_dump(exclude_unset=True)

    # Validate updated dates if both or either are provided
    new_mfg = update_data.get("mfg_date", batch.mfg_date)
    new_exp = update_data.get("exp_date", batch.exp_date)
    if new_exp <= new_mfg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expiry date must be after manufacture date"
        )

    # Validate quantity if provided
    if "quantity" in update_data and update_data["quantity"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    for key, val in update_data.items():
        setattr(batch, key, val)

    db.commit()
    db.refresh(batch)

    log_audit_event(
        db=db,
        action="BATCH_UPDATED",
        user_id=current_user.id if current_user else None,
        organization_id=batch.medicine.organization_id if batch.medicine else None,
        branch_id=batch.branch_id,
        entity_type="batch",
        entity_id=batch.id,
        details={"batch_no": batch.batch_no, "changes": update_data},
    )

    return batch

