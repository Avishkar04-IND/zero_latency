import json
from datetime import date, timedelta
from backend.app.seeds.seed_data import MEDICINES_DATA
from backend.app.services.code_generator import (
    generate_serial_number,
    compute_code_hash,
    format_gs1_datamatrix,
    generate_qr_assets
)

out = []
out.append("-- ==============================================================================")
out.append("-- COMPLETE SUPABASE INITIALIZATION & 50 MEDICINES FULL SEED")
out.append("-- ==============================================================================")

with open("docs/SUPABASE_SETUP.sql", "r", encoding="utf-8") as f:
    schema_sql = f.read()

split_marker = "-- INITIAL SEED:"
if split_marker in schema_sql:
    schema_only = schema_sql.split(split_marker)[0]
else:
    schema_only = schema_sql

out.append(schema_only)
out.append("\n-- ==============================================================================")
out.append("-- SEED ORGANIZATIONS")
out.append("-- ==============================================================================")
out.append("""INSERT INTO organizations (id, name, licence_no, contact_email, address)
VALUES
(1, 'Apex National Pharma', 'LIC-MH-2026-001', 'admin@apexpharma.com', 'Worli Pharma City, Mumbai'),
(2, 'Cipla Laboratories', 'LIC-MH-2026-002', 'contact@cipla-demo.com', 'Vikhroli, Mumbai'),
(3, 'GlaxoSmithKline Healthcare', 'LIC-KA-2026-003', 'info@gsk-demo.com', 'Bangalore Tech Park'),
(4, 'Micro Labs Global', 'LIC-KA-2026-004', 'admin@microlabs-demo.com', 'Race Course Road, Bangalore')
ON CONFLICT (name) DO NOTHING;""")

out.append("\n-- ==============================================================================")
out.append("-- SEED BRANCHES")
out.append("-- ==============================================================================")
out.append("""INSERT INTO branches (id, organization_id, name, code, address, city, state, contact_email, is_active)
VALUES
(1, 1, 'Main Packaging Unit - Mumbai', 'BR-MUM-01', 'Worli Pharma City, Mumbai', 'Mumbai', 'Maharashtra', 'mumbai.plant@apexpharma.com', TRUE),
(2, 2, 'Cipla Formulation Lab - Vikhroli', 'BR-VIK-02', 'Vikhroli, Mumbai', 'Mumbai', 'Maharashtra', 'vikhroli@cipla-demo.com', TRUE),
(3, 3, 'GSK Bangalore Tech Hub', 'BR-BLR-01', 'Bangalore Tech Park', 'Bangalore', 'Karnataka', 'bangalore@gsk-demo.com', TRUE),
(4, 4, 'Micro Labs Peenya Unit', 'BR-PEE-01', 'Peenya Industrial Area, Bangalore', 'Bangalore', 'Karnataka', 'peenya@microlabs-demo.com', TRUE)
ON CONFLICT (id) DO NOTHING;""")

out.append("\n-- ==============================================================================")
out.append("-- SEED USERS")
out.append("-- ==============================================================================")
out.append("""INSERT INTO users (id, organization_id, branch_id, name, email, password_hash, role, is_active)
VALUES
(1, 1, 1, 'Dr. Rajiv Sharma', 'admin@pharma.com', '$2b$12$e8iV7E1ePvZzQxMh6w1wte5L92d3v9W6x0L6v4y1A5g4R2n0Q7G6e', 'ORG_ADMIN', TRUE)
ON CONFLICT (email) DO NOTHING;""")

out.append("\n-- ==============================================================================")
out.append("-- SEED 50 MEDICINES WITH TABLET COMPOSITION, BATCHES & CODES")
out.append("-- ==============================================================================")

def esc(val):
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''") + "'"

today = date.today()

for idx, m in enumerate(MEDICINES_DATA, 1):
    org_id = 1
    mfg = m["manufacturer"].lower()
    if "cipla" in mfg:
        org_id = 2
    elif "glaxo" in mfg or "gsk" in mfg:
        org_id = 3
    elif "micro" in mfg:
        org_id = 4

    act_json = json.dumps(m["active_ingredients"])
    inact_json = json.dumps(m["inactive_excipients"])

    med_sql = f"""INSERT INTO medicines (id, organization_id, brand_name, generic_name, category, manufacturer, dosage_form, strength, active_ingredients, inactive_excipients, tablet_shape, tablet_color, score_line, coating_type, indications, dosage_instructions, warnings_and_precautions, side_effects, storage_conditions, schedule_type, voice_summary_en, voice_summary_hi, voice_summary_mr, status)
VALUES ({idx}, {org_id}, {esc(m['brand_name'])}, {esc(m['generic_name'])}, {esc(m['category'])}, {esc(m['manufacturer'])}, {esc(m['dosage_form'])}, {esc(m['strength'])}, {esc(act_json)}, {esc(inact_json)}, {esc(m['tablet_shape'])}, {esc(m['tablet_color'])}, {esc(m['score_line'])}, {esc(m['coating_type'])}, {esc(m['indications'])}, {esc(m['dosage_instructions'])}, {esc(m['warnings_and_precautions'])}, {esc(m.get('side_effects'))}, {esc(m['storage_conditions'])}, {esc(m['schedule_type'])}, {esc(m['voice_summary_en'])}, {esc(m['voice_summary_hi'])}, {esc(m['voice_summary_mr'])}, 'active')
ON CONFLICT (id) DO NOTHING;"""
    out.append(med_sql)

    # Batch
    if idx == 5:
        mfg_d = today - timedelta(days=750)
        exp_d = today - timedelta(days=30)
        b_no = f"EXP-2024-{idx+100}"
    else:
        mfg_d = today - timedelta(days=90)
        exp_d = today + timedelta(days=720)
        b_no = f"BT-2026-{idx+100}"

    mrp = round(25.0 + (idx * 3.5), 2)
    batch_sql = f"""INSERT INTO batches (id, medicine_id, branch_id, created_by, batch_no, mfg_date, exp_date, quantity, mrp, status)
VALUES ({idx}, {idx}, {org_id}, 1, {esc(b_no)}, {esc(mfg_d)}, {esc(exp_d)}, 50000, {mrp}, 'active')
ON CONFLICT (id) DO NOTHING;"""
    out.append(batch_sql)

    # 2 codes per batch
    for c_sub in range(1, 3):
        c_id = (idx - 1) * 2 + c_sub
        prefix = "MED" if idx != 5 else "EXP"
        serial = generate_serial_number(prefix=prefix)
        c_hash = compute_code_hash(serial)
        dm = format_gs1_datamatrix("8901234567890", exp_d, b_no, serial)
        assets = generate_qr_assets(f"https://smartmed.org/v/{serial}")
        
        code_sql = f"""INSERT INTO codes (id, batch_id, serial_number, code_hash, qr_data_url, qr_svg, datamatrix_code, status, scan_count)
VALUES ({c_id}, {idx}, {esc(serial)}, {esc(c_hash)}, {esc(assets.get('qr_data_url'))}, {esc(assets.get('qr_svg'))}, {esc(dm)}, 'active', 0)
ON CONFLICT (id) DO NOTHING;"""
        out.append(code_sql)

# Set sequences
out.append("""
SELECT setval(pg_get_serial_sequence('organizations', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM organizations;
SELECT setval(pg_get_serial_sequence('branches', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM branches;
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM users;
SELECT setval(pg_get_serial_sequence('medicines', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM medicines;
SELECT setval(pg_get_serial_sequence('batches', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM batches;
SELECT setval(pg_get_serial_sequence('codes', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM codes;
SELECT setval(pg_get_serial_sequence('scans', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM scans;
SELECT setval(pg_get_serial_sequence('audit_logs', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM audit_logs;
SELECT setval(pg_get_serial_sequence('layouts', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM layouts;
SELECT setval(pg_get_serial_sequence('localizations', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM localizations;
""")

with open("docs/SUPABASE_FULL_SEED.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Successfully generated docs/SUPABASE_FULL_SEED.sql")
