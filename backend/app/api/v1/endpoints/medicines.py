import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.core.database import get_db
from backend.app.models.medicine import Medicine
from backend.app.models.organization import Organization
from backend.app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse, MedicineSummary
from backend.app.api.v1.deps import get_current_user

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("", response_model=List[MedicineResponse])
def list_medicines(
    q: Optional[str] = Query(None, description="Search by brand name or generic name"),
    category: Optional[str] = Query(None, description="Filter by therapeutic category"),
    organization_id: Optional[int] = Query(None, description="Filter by manufacturer organization"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns list of registered medicines with full tablet composition.
    Supports live search and category filtering for Web & Mobile catalogs.
    """
    query = db.query(Medicine)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Medicine.brand_name.ilike(search_pattern),
                Medicine.generic_name.ilike(search_pattern),
                Medicine.category.ilike(search_pattern)
            )
        )

    if category:
        query = query.filter(Medicine.category.ilike(f"%{category.strip()}%"))

    if organization_id:
        query = query.filter(Medicine.organization_id == organization_id)

    medicines = query.order_by(Medicine.brand_name).offset(offset).limit(limit).all()
    return medicines


@router.post("", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    req: MedicineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Creates a new medicine master record with comprehensive tablet contents & active ingredients.
    """
    # Resolve organization_id
    org_id = req.organization_id
    if not org_id and current_user and current_user.organization_id:
        org_id = current_user.organization_id
    elif not org_id:
        # Fallback to first organization in DB
        first_org = db.query(Organization).first()
        if not first_org:
            first_org = Organization(
                name="Apex Healthcare Ltd",
                licence_no="LIC-MFG-001",
                contact_email="admin@apexhealth.com",
                address="Mumbai Pharma Zone, India"
            )
            db.add(first_org)
            db.flush()
        org_id = first_org.id

    # Serialize active ingredients & excipients
    active_json = json.dumps([item.model_dump() for item in req.active_ingredients])
    inactive_json = json.dumps(req.inactive_excipients or [])

    # Synthesize fallback voice summaries if omitted
    voice_en = req.voice_summary_en or (
        f"This is {req.brand_name}, containing {req.generic_name} {req.strength}. "
        f"Used for {req.indications}. Caution: {req.warnings_and_precautions}"
    )

    med = Medicine(
        organization_id=org_id,
        brand_name=req.brand_name,
        generic_name=req.generic_name,
        category=req.category,
        manufacturer=req.manufacturer,
        dosage_form=req.dosage_form,
        strength=req.strength,
        active_ingredients=active_json,
        inactive_excipients=inactive_json,
        tablet_shape=req.tablet_shape,
        tablet_color=req.tablet_color,
        score_line=req.score_line,
        coating_type=req.coating_type,
        indications=req.indications,
        dosage_instructions=req.dosage_instructions,
        warnings_and_precautions=req.warnings_and_precautions,
        side_effects=req.side_effects,
        storage_conditions=req.storage_conditions,
        schedule_type=req.schedule_type,
        voice_summary_en=voice_en,
        voice_summary_hi=req.voice_summary_hi,
        voice_summary_mr=req.voice_summary_mr
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/{id}", response_model=MedicineResponse)
def get_medicine(id: int, db: Session = Depends(get_db)):
    """Fetches complete tablet details, composition, safety info, and audio strings by medicine ID."""
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    return med


@router.put("/{id}", response_model=MedicineResponse)
def update_medicine(
    id: int,
    req: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Updates medicine specifications and composition."""
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine record not found")

    update_data = req.model_dump(exclude_unset=True)

    if "active_ingredients" in update_data and update_data["active_ingredients"] is not None:
        med.active_ingredients = json.dumps([item.model_dump() if hasattr(item, "model_dump") else item for item in req.active_ingredients])
        del update_data["active_ingredients"]

    if "inactive_excipients" in update_data and update_data["inactive_excipients"] is not None:
        med.inactive_excipients = json.dumps(req.inactive_excipients)
        del update_data["inactive_excipients"]

    for key, val in update_data.items():
        setattr(med, key, val)

    db.commit()
    db.refresh(med)
    return med


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Deletes a medicine record."""
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    db.delete(med)
    db.commit()
    return None
