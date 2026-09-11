from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.batch import Batch
from backend.app.models.medicine import Medicine
from backend.app.schemas.batch import BatchCreate, BatchUpdate, BatchResponse, BatchDetailResponse
from backend.app.api.v1.deps import get_current_user

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchDetailResponse])
def list_batches(
    medicine_id: Optional[int] = Query(None, description="Filter batches by medicine"),
    status_filter: Optional[str] = Query(None, description="Filter by status (active, expired, recalled)"),
    db: Session = Depends(get_db)
):
    """Lists manufacturing batches."""
    query = db.query(Batch)
    if medicine_id:
        query = query.filter(Batch.medicine_id == medicine_id)
    if status_filter:
        query = query.filter(Batch.status == status_filter)
    return query.order_by(Batch.exp_date.desc()).all()


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    req: BatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Creates a new production batch for a registered medicine."""
    med = db.query(Medicine).filter(Medicine.id == req.medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    batch = Batch(
        medicine_id=req.medicine_id,
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
    return batch


@router.get("/{id}", response_model=BatchDetailResponse)
def get_batch(id: int, db: Session = Depends(get_db)):
    """Retrieves batch details by ID."""
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.put("/{id}", response_model=BatchResponse)
def update_batch(
    id: int,
    req: BatchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Updates batch information, including recall actions."""
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(batch, key, val)

    db.commit()
    db.refresh(batch)
    return batch
