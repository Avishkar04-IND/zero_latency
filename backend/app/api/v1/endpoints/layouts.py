import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.code import Code
from backend.app.models.batch import Batch
from backend.app.services.verifier import extract_serial_number
from backend.app.schemas.layout import (
    LayoutPrintMedicineInfo,
    LayoutPrintBatchInfo,
    LayoutPrintManufacturerInfo,
    LayoutPrintBranchInfo,
    LayoutPrintLabelData,
    LayoutPrintDataResponse,
    LayoutBatchPrintDataResponse,
)

router = APIRouter(prefix="/layouts", tags=["Layout Engine Integration"])


def build_layout_print_data(code: Code) -> LayoutPrintDataResponse:
    batch = code.batch
    medicine = batch.medicine if batch else None
    org = medicine.organization if medicine else None
    branch = batch.branch if batch else None

    # Parse active ingredients
    act_ing = []
    if medicine and medicine.active_ingredients:
        try:
            act_ing = json.loads(medicine.active_ingredients) if isinstance(medicine.active_ingredients, str) else medicine.active_ingredients
        except Exception:
            act_ing = medicine.active_ingredients

    # Parse inactive excipients
    inact_exc = []
    if medicine and medicine.inactive_excipients:
        try:
            inact_exc = json.loads(medicine.inactive_excipients) if isinstance(medicine.inactive_excipients, str) else medicine.inactive_excipients
        except Exception:
            inact_exc = medicine.inactive_excipients

    med_info = LayoutPrintMedicineInfo(
        name=medicine.brand_name if medicine else "Unknown Medicine",
        generic_name=medicine.generic_name if medicine else "",
        strength=medicine.strength if medicine else "",
        dosage_form=medicine.dosage_form if medicine else "Tablet",
        tablet_shape=medicine.tablet_shape if medicine else None,
        tablet_color=medicine.tablet_color if medicine else None,
        coating_type=medicine.coating_type if medicine else None,
        active_ingredients=act_ing,
        inactive_excipients=inact_exc,
        storage_conditions=medicine.storage_conditions if medicine else None,
        schedule_type=medicine.schedule_type if medicine else None,
    )

    batch_info = LayoutPrintBatchInfo(
        batch_number=batch.batch_no if batch else "UNKNOWN",
        mfg_date=str(batch.mfg_date) if batch and batch.mfg_date else "",
        exp_date=str(batch.exp_date) if batch and batch.exp_date else "",
        quantity=batch.quantity if batch else 0,
        mrp=batch.mrp if batch else 0.0,
        status=batch.status if batch else "active",
    )

    mfg_info = LayoutPrintManufacturerInfo(
        name=org.name if org else (medicine.manufacturer if medicine else "Unknown Manufacturer"),
        licence_no=org.licence_no if org else "LIC-UNKNOWN",
        contact_email=org.contact_email if org else "contact@pharma.com",
        address=org.address if org else None,
    )

    branch_info = None
    if branch:
        branch_info = LayoutPrintBranchInfo(
            name=branch.name,
            code=branch.code,
            city=branch.city,
            state=branch.state,
            address=branch.address,
        )

    warnings_list = []
    if medicine and medicine.warnings_and_precautions:
        warnings_list.append(medicine.warnings_and_precautions)

    b_num = batch_info.batch_number
    m_date = batch_info.mfg_date
    e_date = batch_info.exp_date
    mrp_val = f"Rs. {batch_info.mrp:.2f}"

    label_data = LayoutPrintLabelData(
        line1_header=f"{med_info.name} {med_info.strength}".strip(),
        line2_generic=f"Generic: {med_info.generic_name}".strip(),
        line3_batch_exp=f"B.No: {b_num} | Mfg: {m_date} | Exp: {e_date}",
        line4_mrp=f"MRP {mrp_val} (Inclusive of all taxes)",
        line5_storage=f"Storage: {med_info.storage_conditions or 'Store in a cool, dry place.'}",
        line6_license=f"Mfg. Lic. No: {mfg_info.licence_no}",
        barcode_payload=code.datamatrix_code or f"https://smartmed.org/v/{code.serial_number}",
    )

    return LayoutPrintDataResponse(
        code=code.serial_number,
        serial_number=code.serial_number,
        code_hash=code.code_hash,
        datamatrix_code=code.datamatrix_code,
        qr_svg=code.qr_svg,
        qr_data_url=code.qr_data_url,
        medicine=med_info,
        batch=batch_info,
        manufacturer=mfg_info,
        branch=branch_info,
        warnings=warnings_list,
        print_data=label_data,
    )


@router.get("/print-data/{code_or_serial}", response_model=LayoutPrintDataResponse)
def get_layout_print_data(code_or_serial: str, db: Session = Depends(get_db)):
    """
    Authoritative Printing Data Endpoint for Layout Engine (Member 3) & Web Admin (Member 2).
    Returns verified, structured pharmaceutical specifications, batch metadata, manufacturer info,
    and formatted label typography lines for a given unit code or serial.
    """
    serial = extract_serial_number(code_or_serial)
    code = db.query(Code).filter(Code.serial_number == serial).first()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine code '{code_or_serial}' not found in registry"
        )

    return build_layout_print_data(code)


@router.get("/print-data/batch/{batch_id}", response_model=LayoutBatchPrintDataResponse)
def get_layout_batch_print_data(
    batch_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns batch-level packaging template specifications along with all or sample unit serial codes
    for multi-pack or blister sheet layout generation.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch ID '{batch_id}' not found"
        )

    codes = db.query(Code).filter(Code.batch_id == batch_id).limit(limit).all()
    unit_responses = [build_layout_print_data(c) for c in codes]

    sample_code = codes[0] if codes else None
    if sample_code:
        sample_response = build_layout_print_data(sample_code)
        label_template = sample_response.print_data
        med_info = sample_response.medicine
        mfg_info = sample_response.manufacturer
        branch_info = sample_response.branch
    else:
        # Fallback template if no codes generated yet
        medicine = batch.medicine
        org = medicine.organization if medicine else None
        branch = batch.branch

        med_info = LayoutPrintMedicineInfo(
            name=medicine.brand_name if medicine else "Unknown",
            generic_name=medicine.generic_name if medicine else "",
            strength=medicine.strength if medicine else "",
            dosage_form=medicine.dosage_form if medicine else "Tablet",
        )
        mfg_info = LayoutPrintManufacturerInfo(
            name=org.name if org else "Manufacturer",
            licence_no=org.licence_no if org else "LIC-001",
            contact_email=org.contact_email if org else "admin@pharma.com",
        )
        branch_info = LayoutPrintBranchInfo(name=branch.name) if branch else None
        label_template = LayoutPrintLabelData(
            line1_header=f"{med_info.name} {med_info.strength}".strip(),
            line2_generic=f"Generic: {med_info.generic_name}".strip(),
            line3_batch_exp=f"B.No: {batch.batch_no} | Mfg: {batch.mfg_date} | Exp: {batch.exp_date}",
            line4_mrp=f"MRP Rs. {batch.mrp:.2f} (Inclusive of all taxes)",
            line5_storage="Storage: Store in a cool, dry place.",
            line6_license=f"Mfg. Lic. No: {mfg_info.licence_no}",
            barcode_payload=f"BATCH-{batch.batch_no}",
        )

    batch_info = LayoutPrintBatchInfo(
        batch_number=batch.batch_no,
        mfg_date=str(batch.mfg_date),
        exp_date=str(batch.exp_date),
        quantity=batch.quantity,
        mrp=batch.mrp,
        status=batch.status,
    )

    return LayoutBatchPrintDataResponse(
        batch=batch_info,
        medicine=med_info,
        manufacturer=mfg_info,
        branch=branch_info,
        label_template=label_template,
        total_codes=len(unit_responses),
        unit_codes=unit_responses,
    )
