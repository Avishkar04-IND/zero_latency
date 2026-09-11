from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.schemas.code import CodeGenerateRequest, CodeResponse, CodeGenerateBatchResponse
from backend.app.services.code_generator import (
    generate_serial_number,
    compute_code_hash,
    format_gs1_datamatrix,
    generate_qr_assets
)
from backend.app.api.v1.deps import get_current_user

router = APIRouter(prefix="/codes", tags=["Codes"])


@router.post("/generate", response_model=CodeGenerateBatchResponse, status_code=status.HTTP_201_CREATED)
def generate_codes(
    req: CodeGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Generates N unique cryptographic serial numbers, QR codes, and GS1 DataMatrix identifiers
    for a specific medicine batch.
    """
    batch = db.query(Batch).filter(Batch.id == req.batch_id).first()
    if not batch:
        valid_batches = db.query(Batch.id, Batch.batch_no).order_by(Batch.id.asc()).limit(5).all()
        examples = ", ".join([f"ID {b.id} ({b.batch_no})" for b in valid_batches])
        raise HTTPException(
            status_code=404,
            detail=f"Batch ID '{req.batch_id}' not found. Batch IDs start at 1. Available batches: {examples}. Please use batch_id: 1 (or any valid batch ID)."
        )

    medicine = batch.medicine
    created_codes: List[Code] = []

    prefix = (req.prefix or "MED").strip().upper()

    for _ in range(req.count):
        # Generate non-sequential cryptographic serial with specified prefix
        serial = generate_serial_number(prefix=prefix)
        
        # Ensure collision-free uniqueness
        while db.query(Code).filter(Code.serial_number == serial).first():
            serial = generate_serial_number(prefix=prefix)

        # Compute tamper-evident HMAC hash
        c_hash = compute_code_hash(serial)

        # Generate GS1 DataMatrix representation
        datamatrix = format_gs1_datamatrix(
            gtin="8901234567890",
            exp_date=batch.exp_date,
            batch_no=batch.batch_no,
            serial_number=serial
        )

        # Payload formatted for mobile camera scanner
        scanner_payload = f"https://smartmed.org/v/{serial}"

        # Generate SVG and Base64 PNG QR assets
        assets = generate_qr_assets(scanner_payload)

        code_entity = Code(
            batch_id=batch.id,
            serial_number=serial,
            code_hash=c_hash,
            qr_data_url=assets.get("qr_data_url"),
            qr_svg=assets.get("qr_svg"),
            datamatrix_code=datamatrix,
            status="active",
            scan_count=0
        )
        db.add(code_entity)
        created_codes.append(code_entity)

    db.commit()

    for c in created_codes:
        db.refresh(c)

    return CodeGenerateBatchResponse(
        total_generated=len(created_codes),
        batch_id=batch.id,
        batch_no=batch.batch_no,
        medicine_name=medicine.brand_name if medicine else "Unknown Medicine",
        codes=[CodeResponse.model_validate(c) for c in created_codes]
    )


@router.get("/batch/{batch_id}", response_model=List[CodeResponse])
def get_codes_by_batch(batch_id: int, db: Session = Depends(get_db)):
    """Retrieves all generated codes for a production batch."""
    return db.query(Code).filter(Code.batch_id == batch_id).order_by(Code.id.desc()).all()


@router.get("/{serial}", response_model=CodeResponse)
def get_code_by_serial(serial: str, db: Session = Depends(get_db)):
    """Retrieves code record by serial identifier."""
    code = db.query(Code).filter(Code.serial_number == serial).first()
    if not code:
        raise HTTPException(status_code=404, detail="Code record not found")
    return code


@router.get("/{serial}/svg")
def download_code_svg(serial: str, db: Session = Depends(get_db)):
    """Streams the raw SVG QR code asset for printing or layout preview."""
    code = db.query(Code).filter(Code.serial_number == serial).first()
    if not code or not code.qr_svg:
        raise HTTPException(status_code=404, detail="SVG asset not available for this code")
    return Response(content=code.qr_svg, media_type="image/svg+xml")
