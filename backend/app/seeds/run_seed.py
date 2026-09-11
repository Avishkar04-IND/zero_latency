import json
from datetime import date, datetime, timedelta, timezone
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
# Import all models
import backend.app.models
from backend.app.models.organization import Organization
from backend.app.models.branch import Branch
from backend.app.models.user import User
from backend.app.models.medicine import Medicine
from backend.app.models.batch import Batch
from backend.app.models.code import Code
from backend.app.models.scan import Scan
from backend.app.models.localization import Localization
from backend.app.seeds.seed_data import MEDICINES_DATA
from backend.app.services.code_generator import (
    generate_serial_number,
    compute_code_hash,
    format_gs1_datamatrix,
    generate_qr_assets
)


import sys

# Ensure UTF-8 output on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def seed_database():
    print("[INIT] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create or get Organizations
        print("[ORGS] Seeding pharmaceutical organizations...")
        orgs = [
            ("Apex National Pharma", "LIC-MH-2026-001", "admin@apexpharma.com", "Worli Pharma City, Mumbai"),
            ("Cipla Laboratories", "LIC-MH-2026-002", "contact@cipla-demo.com", "Vikhroli, Mumbai"),
            ("GlaxoSmithKline Healthcare", "LIC-KA-2026-003", "info@gsk-demo.com", "Bangalore Tech Park"),
            ("Micro Labs Global", "LIC-KA-2026-004", "admin@microlabs-demo.com", "Race Course Road, Bangalore"),
        ]
        org_map = {}
        for name, lic, email, addr in orgs:
            org = db.query(Organization).filter(Organization.name == name).first()
            if not org:
                org = Organization(name=name, licence_no=lic, contact_email=email, address=addr)
                db.add(org)
                db.flush()
            org_map[name] = org.id

        default_org_id = list(org_map.values())[0]

        # 1b. Seed Branches for each Organization
        print("[BRANCHES] Seeding manufacturing branches...")
        branches_data = [
            (org_map["Apex National Pharma"], "Main Packaging Unit - Mumbai", "BR-MUM-01", "Worli Pharma City, Mumbai", "Mumbai", "Maharashtra", "mumbai.plant@apexpharma.com"),
            (org_map["Cipla Laboratories"], "Cipla Formulation Lab - Vikhroli", "BR-VIK-02", "Vikhroli, Mumbai", "Mumbai", "Maharashtra", "vikhroli@cipla-demo.com"),
            (org_map["GlaxoSmithKline Healthcare"], "GSK Bangalore Tech Hub", "BR-BLR-01", "Bangalore Tech Park", "Bangalore", "Karnataka", "bangalore@gsk-demo.com"),
            (org_map["Micro Labs Global"], "Micro Labs Peenya Unit", "BR-PEE-01", "Peenya Industrial Area, Bangalore", "Bangalore", "Karnataka", "peenya@microlabs-demo.com"),
        ]
        org_branch_map = {}
        for o_id, b_name, b_code, b_addr, b_city, b_state, b_email in branches_data:
            branch = db.query(Branch).filter(Branch.name == b_name).first()
            if not branch:
                branch = Branch(
                    organization_id=o_id,
                    name=b_name,
                    code=b_code,
                    address=b_addr,
                    city=b_city,
                    state=b_state,
                    contact_email=b_email,
                    is_active=True
                )
                db.add(branch)
                db.flush()
            org_branch_map[o_id] = branch.id

        default_branch_id = org_branch_map.get(default_org_id)

        # 2. Create Default Admin User
        print("[USER] Seeding default company admin user...")
        admin_email = "admin@pharma.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Dr. Rajiv Sharma",
                email=admin_email,
                password_hash=get_password_hash("Admin@12345"),
                role="ORG_ADMIN",
                organization_id=default_org_id,
                branch_id=default_branch_id,
                is_active=True
            )
            db.add(admin)
            db.flush()

        # 3. Seed 50 Medicines with full tablet contents
        print(f"[MEDICINES] Seeding {len(MEDICINES_DATA)} medicines with full tablet composition...")
        today = date.today()
        seeded_codes_list = []

        for idx, med_data in enumerate(MEDICINES_DATA):
            # Select organization
            mfg = med_data["manufacturer"]
            org_id = default_org_id
            for o_name, o_id in org_map.items():
                if any(k in mfg.lower() for k in ["cipla", "glaxo", "micro"]):
                    if "cipla" in mfg.lower() and "cipla" in o_name.lower():
                        org_id = o_id
                    elif "glaxo" in mfg.lower() and "glaxo" in o_name.lower():
                        org_id = o_id
                    elif "micro" in mfg.lower() and "micro" in o_name.lower():
                        org_id = o_id

            # Check if medicine already exists
            existing_med = db.query(Medicine).filter(Medicine.brand_name == med_data["brand_name"]).first()
            if not existing_med:
                med = Medicine(
                    organization_id=org_id,
                    brand_name=med_data["brand_name"],
                    generic_name=med_data["generic_name"],
                    category=med_data["category"],
                    manufacturer=med_data["manufacturer"],
                    dosage_form=med_data["dosage_form"],
                    strength=med_data["strength"],
                    active_ingredients=json.dumps(med_data["active_ingredients"]),
                    inactive_excipients=json.dumps(med_data["inactive_excipients"]),
                    tablet_shape=med_data["tablet_shape"],
                    tablet_color=med_data["tablet_color"],
                    score_line=med_data["score_line"],
                    coating_type=med_data["coating_type"],
                    indications=med_data["indications"],
                    dosage_instructions=med_data["dosage_instructions"],
                    warnings_and_precautions=med_data["warnings_and_precautions"],
                    side_effects=med_data["side_effects"],
                    storage_conditions=med_data["storage_conditions"],
                    schedule_type=med_data["schedule_type"],
                    voice_summary_en=med_data["voice_summary_en"],
                    voice_summary_hi=med_data["voice_summary_hi"],
                    voice_summary_mr=med_data["voice_summary_mr"],
                    status="active"
                )
                db.add(med)
                db.flush()
            else:
                med = existing_med

            # 4. Create Batch for each medicine
            # For medicine #5, create an expired batch for demo test verification!
            if idx == 4:
                mfg_d = today - timedelta(days=750)
                exp_d = today - timedelta(days=30)  # Expired last month
                b_no = f"EXP-2024-{idx+101}"
                b_status = "active"  # expired by date
            else:
                mfg_d = today - timedelta(days=90)
                exp_d = today + timedelta(days=720)  # 2 years expiry
                b_no = f"BT-2026-{idx+101}"
                b_status = "active"

            existing_batch = db.query(Batch).filter(Batch.batch_no == b_no).first()
            if not existing_batch:
                batch = Batch(
                    medicine_id=med.id,
                    branch_id=org_branch_map.get(org_id),
                    created_by=admin.id if admin else None,
                    batch_no=b_no,
                    mfg_date=mfg_d,
                    exp_date=exp_d,
                    quantity=50000,
                    mrp=round(25.0 + (idx * 3.5), 2),
                    status=b_status
                )
                db.add(batch)
                db.flush()
            else:
                batch = existing_batch

            # 5. Generate secure codes for each batch
            # Ensure at least 2 unique codes per batch
            existing_codes = db.query(Code).filter(Code.batch_id == batch.id).count()
            if existing_codes == 0:
                for code_idx in range(2):
                    prefix = "MED" if idx != 4 else "EXP"
                    serial = generate_serial_number(prefix=prefix)
                    c_hash = compute_code_hash(serial)
                    datamatrix = format_gs1_datamatrix(
                        gtin="8901234567890",
                        exp_date=batch.exp_date,
                        batch_no=batch.batch_no,
                        serial_number=serial
                    )
                    payload = f"https://smartmed.org/v/{serial}"
                    assets = generate_qr_assets(payload)

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
                    db.flush()
                    seeded_codes_list.append((code_entity, med, batch))

        # 5b. Seed Canonical Project Demo Medicine: Paracetamol 500 mg (MD110 & EXP-7903-6B98-2D0A)
        print("[DEMO] Seeding canonical project verification demo medicine (MD110)...")
        demo_org = db.query(Organization).filter(Organization.name == "Demo Pharma").first()
        if not demo_org:
            demo_org = Organization(
                name="Demo Pharma",
                licence_no="LIC-MH-2026-DEMO",
                contact_email="contact@demopharma.com",
                address="Demo Pharma Tech Park, Mumbai"
            )
            db.add(demo_org)
            db.flush()

        demo_branch = db.query(Branch).filter(Branch.name == "Demo Pharma Main Unit").first()
        if not demo_branch:
            demo_branch = Branch(
                organization_id=demo_org.id,
                name="Demo Pharma Main Unit",
                code="BR-DEMO-01",
                address="Demo Pharma Tech Park, Mumbai",
                city="Mumbai",
                state="Maharashtra",
                contact_email="mumbai@demopharma.com",
                is_active=True
            )
            db.add(demo_branch)
            db.flush()

        demo_med = db.query(Medicine).filter(Medicine.brand_name == "Paracetamol 500 mg").first()
        if not demo_med:
            demo_med = Medicine(
                organization_id=demo_org.id,
                brand_name="Paracetamol 500 mg",
                generic_name="Paracetamol Tablets IP",
                category="Analgesic & Antipyretic",
                manufacturer="Demo Pharma",
                dosage_form="Tablet",
                strength="500 mg",
                active_ingredients=json.dumps([{"name": "Paracetamol IP", "strength": "500", "unit": "mg", "purpose": "Active Analgesic"}]),
                inactive_excipients=json.dumps(["Starch", "Microcrystalline Cellulose", "Magnesium Stearate", "Povidone"]),
                tablet_shape="Round",
                tablet_color="White",
                score_line="Single break-line",
                coating_type="Uncoated",
                indications="Relief of mild to moderate pain including headache and reduction of fever.",
                dosage_instructions="Take 1 tablet every 6 to 8 hours with water. Maximum 4 tablets in 24 hours.",
                warnings_and_precautions="Do not exceed recommended dose. Avoid consumption with alcohol.",
                side_effects="Rare: mild nausea, skin rash.",
                storage_conditions="Store below 30°C in a dry place. Protect from light.",
                schedule_type="OTC",
                voice_summary_en="Paracetamol 500 milligram tablet. Contains Paracetamol. For fever and pain relief.",
                voice_summary_hi="पैरासिटामोल 500 मिलीग्राम टैबलेट। बुखार और दर्द से राहत के लिए।",
                voice_summary_mr="पॅरासिटामॉल 500 मिलिगॅ्रम गोळी. ताप आणि वेदना कमी करण्यासाठी.",
                status="active"
            )
            db.add(demo_med)
            db.flush()

        # Demo Batch 1: Authentic batch PCM26A01 (Exp: 2028-09-10)
        batch_pcm26 = db.query(Batch).filter(Batch.batch_no == "PCM26A01").first()
        if not batch_pcm26:
            batch_pcm26 = Batch(
                medicine_id=demo_med.id,
                branch_id=demo_branch.id,
                created_by=admin.id if admin else None,
                batch_no="PCM26A01",
                mfg_date=date(2026, 1, 15),
                exp_date=date(2028, 9, 10),
                quantity=50000,
                mrp=20.0,
                status="active"
            )
            db.add(batch_pcm26)
            db.flush()

        # Code MD110
        code_md110 = db.query(Code).filter(Code.serial_number == "MD110").first()
        if not code_md110:
            md110_assets = generate_qr_assets("https://smartmed.org/v/MD110")
            code_md110 = Code(
                batch_id=batch_pcm26.id,
                serial_number="MD110",
                code_hash=compute_code_hash("MD110"),
                qr_data_url=md110_assets.get("qr_data_url"),
                qr_svg=md110_assets.get("qr_svg"),
                datamatrix_code=format_gs1_datamatrix("8901234567890", date(2028, 9, 10), "PCM26A01", "MD110"),
                status="active",
                scan_count=0
            )
            db.add(code_md110)
            db.flush()

        # Demo Batch 2: Expired batch PCM24EXP (Exp: 2024-08-12)
        batch_pcm24exp = db.query(Batch).filter(Batch.batch_no == "PCM24EXP").first()
        if not batch_pcm24exp:
            batch_pcm24exp = Batch(
                medicine_id=demo_med.id,
                branch_id=demo_branch.id,
                created_by=admin.id if admin else None,
                batch_no="PCM24EXP",
                mfg_date=date(2022, 6, 1),
                exp_date=date(2024, 8, 12),
                quantity=20000,
                mrp=20.0,
                status="expired"
            )
            db.add(batch_pcm24exp)
            db.flush()

        # Code EXP-7903-6B98-2D0A
        code_exp_target = db.query(Code).filter(Code.serial_number == "EXP-7903-6B98-2D0A").first()
        if not code_exp_target:
            exp_assets = generate_qr_assets("https://smartmed.org/v/EXP-7903-6B98-2D0A")
            code_exp_target = Code(
                batch_id=batch_pcm24exp.id,
                serial_number="EXP-7903-6B98-2D0A",
                code_hash=compute_code_hash("EXP-7903-6B98-2D0A"),
                qr_data_url=exp_assets.get("qr_data_url"),
                qr_svg=exp_assets.get("qr_svg"),
                datamatrix_code=format_gs1_datamatrix("8901234567890", date(2024, 8, 12), "PCM24EXP", "EXP-7903-6B98-2D0A"),
                status="active",
                scan_count=0
            )
            db.add(code_exp_target)
            db.flush()

        # 6. Seed Realistic Scan Events & Suspicious Scan for Analytics Demo
        print("[SCANS] Seeding realistic scan audit logs and security scenarios...")
        if seeded_codes_list and db.query(Scan).count() == 0:
            now = datetime.now(timezone.utc)

            # Scenario A: Genuine First-time Scan
            c1, m1, b1 = seeded_codes_list[0]
            c1.scan_count = 1
            c1.first_scanned_at = now - timedelta(hours=2)
            c1.last_scanned_at = now - timedelta(hours=2)
            scan1 = Scan(
                code_id=c1.id,
                scanned_serial=c1.serial_number,
                verification_result="GENUINE",
                risk_score=0,
                risk_reasons=json.dumps(["Authentic medicine verified"]),
                device_info="Flutter Mobile Android 14 (SM-S918B)",
                location_lat=19.0760,
                location_lng=72.8777,
                timestamp=now - timedelta(hours=2)
            )
            db.add(scan1)

            # Scenario B: Expired Batch Scan (Medicine #5)
            c_exp, m_exp, b_exp = seeded_codes_list[8]  # index 8 or 9
            scan_exp = Scan(
                code_id=c_exp.id,
                scanned_serial=c_exp.serial_number,
                verification_result="EXPIRED",
                risk_score=75,
                risk_reasons=json.dumps([f"Medicine expired on {b_exp.exp_date}"]),
                device_info="Flutter Mobile iOS 17.4",
                location_lat=28.7041,
                location_lng=77.1025,
                timestamp=now - timedelta(hours=1)
            )
            db.add(scan_exp)

            # Scenario C: Suspicious Repeated Scans (Multiple scans detected across locations)
            c_susp, m_susp, b_susp = seeded_codes_list[1]
            c_susp.scan_count = 9
            c_susp.first_scanned_at = now - timedelta(days=1)
            c_susp.last_scanned_at = now - timedelta(minutes=15)
            scan_susp = Scan(
                code_id=c_susp.id,
                scanned_serial=c_susp.serial_number,
                verification_result="SUSPICIOUS_MULTIPLE_SCANS",
                risk_score=85,
                risk_reasons=json.dumps(["High scan frequency: Scanned 9 times in 24 hours across multiple devices"]),
                device_info="Mobile Web Scanner",
                location_lat=12.9716,
                location_lng=77.5946,
                timestamp=now - timedelta(minutes=15)
            )
            db.add(scan_susp)

            # Scenario D: Counterfeit / Invalid Serial Scan
            scan_fake = Scan(
                code_id=None,
                scanned_serial="MED-FAKE-9999-0000",
                verification_result="INVALID",
                risk_score=100,
                risk_reasons=json.dumps(["Unregistered serial number: Not found in pharmaceutical database"]),
                device_info="Unknown Android Device",
                location_lat=18.5204,
                location_lng=73.8567,
                timestamp=now - timedelta(minutes=5)
            )
            db.add(scan_fake)

        db.commit()
        print("[SUCCESS] DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print(f"   * Total Medicines: {db.query(Medicine).count()}")
        print(f"   * Total Batches: {db.query(Batch).count()}")
        print(f"   * Total Unique Codes: {db.query(Code).count()}")
        print(f"   * Admin Login: {admin_email} | Password: Admin@12345")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
