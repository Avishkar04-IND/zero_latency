-- ==============================================================================
-- SMART MEDICINE IDENTIFICATION & VERIFICATION PLATFORM
-- SUPABASE / POSTGRESQL DATABASE INITIALIZATION SCRIPT
-- ==============================================================================
-- Run this complete script inside the Supabase SQL Editor (Dashboard -> SQL Editor -> New Query).
-- It will create all tables, relationships, constraints, and high-performance indexes.

-- 1. Enable UUID extension (if needed for future extensions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Clean teardown (optional, uncomment if resetting)
-- DROP TABLE IF EXISTS audit_logs CASCADE;
-- DROP TABLE IF EXISTS scans CASCADE;
-- DROP TABLE IF EXISTS codes CASCADE;
-- DROP TABLE IF EXISTS batches CASCADE;
-- DROP TABLE IF EXISTS localizations CASCADE;
-- DROP TABLE IF EXISTS layouts CASCADE;
-- DROP TABLE IF EXISTS medicines CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP TABLE IF EXISTS branches CASCADE;
-- DROP TABLE IF EXISTS organizations CASCADE;

-- ==============================================================================
-- TABLE: organizations (Pharmaceutical Manufacturers & Regulatory Bodies)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    licence_no VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: branches (Manufacturing Units & Regional Packaging Facilities)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: users (Admins, Quality Inspectors, and Consumers)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'ORG_ADMIN' NOT NULL, -- SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, OPERATOR, VIEWER
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: medicines (Master Formulations with Detailed Tablet Composition)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS medicines (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    brand_name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(250) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(250) NOT NULL,
    dosage_form VARCHAR(50) DEFAULT 'Tablet' NOT NULL, -- Tablet, Capsule, Syrup
    strength VARCHAR(100) NOT NULL,
    
    -- Tablet Chemical Composition (JSON formatted)
    active_ingredients TEXT NOT NULL, -- List of {name, strength, unit, purpose}
    inactive_excipients TEXT,         -- List of excipients/fillers
    
    -- Tablet Physical Specifications
    tablet_shape VARCHAR(50) DEFAULT 'Round',
    tablet_color VARCHAR(50) DEFAULT 'White',
    score_line VARCHAR(100) DEFAULT 'None',
    coating_type VARCHAR(100) DEFAULT 'Film-coated',
    
    -- Clinical Guidelines & Safety
    indications TEXT NOT NULL,
    dosage_instructions TEXT NOT NULL,
    warnings_and_precautions TEXT NOT NULL,
    side_effects TEXT,
    storage_conditions VARCHAR(255) DEFAULT 'Store below 30°C in a dry place. Protect from light.',
    schedule_type VARCHAR(100) DEFAULT 'Schedule H',
    
    -- Accessibility Voice Synthesizer Scripts
    voice_summary_en TEXT,
    voice_summary_hi TEXT,
    voice_summary_mr TEXT,
    
    status VARCHAR(50) DEFAULT 'active' NOT NULL, -- active, discontinued, under_review
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: batches (Manufacturing Batches & Expiry Dates)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS batches (
    id SERIAL PRIMARY KEY,
    medicine_id INTEGER REFERENCES medicines(id) ON DELETE CASCADE NOT NULL,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    batch_no VARCHAR(100) NOT NULL,
    mfg_date DATE NOT NULL,
    exp_date DATE NOT NULL,
    quantity INTEGER DEFAULT 10000 NOT NULL,
    mrp DOUBLE PRECISION DEFAULT 50.0 NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL, -- active, expired, recalled, quarantined
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: codes (Cryptographic Unique Identifiers & QR Assets)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS codes (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    code_hash VARCHAR(128) NOT NULL,
    qr_data_url TEXT,
    qr_svg TEXT,
    datamatrix_code VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' NOT NULL, -- active, revoked, scratched, recalled
    scan_count INTEGER DEFAULT 0 NOT NULL,
    first_scanned_at TIMESTAMP WITH TIME ZONE,
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: scans (Audit Log & Fraud Detection History)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    code_id INTEGER REFERENCES codes(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    scanned_serial VARCHAR(100) NOT NULL,
    verification_result VARCHAR(50) NOT NULL, -- GENUINE, EXPIRED, SUSPICIOUS_MULTIPLE_SCANS, INVALID, REVOKED
    risk_score INTEGER DEFAULT 0 NOT NULL,   -- 0 (safe) to 100 (counterfeit)
    risk_reasons TEXT,                       -- JSON string of anomaly reasons
    ip_address VARCHAR(64),
    device_info VARCHAR(255),
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: audit_logs (Authoritative Administrative & Security Event Trail)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: layouts (Blister Strip & Packaging Layout Optimizations)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS layouts (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    package_type VARCHAR(50) DEFAULT 'blister_strip' NOT NULL,
    strip_length_mm DOUBLE PRECISION DEFAULT 110.0 NOT NULL,
    strip_width_mm DOUBLE PRECISION DEFAULT 45.0 NOT NULL,
    tablet_count INTEGER DEFAULT 10 NOT NULL,
    tablet_arrangement VARCHAR(20) DEFAULT '2x5' NOT NULL,
    code_type VARCHAR(20) DEFAULT 'QR' NOT NULL,
    code_size_mm DOUBLE PRECISION DEFAULT 10.0 NOT NULL,
    code_position_x DOUBLE PRECISION DEFAULT 85.0 NOT NULL,
    code_position_y DOUBLE PRECISION DEFAULT 10.0 NOT NULL,
    strategy VARCHAR(50) DEFAULT 'balanced' NOT NULL, -- lowest_cost, balanced, max_accessibility
    layout_score DOUBLE PRECISION DEFAULT 85.0 NOT NULL,
    readability_score DOUBLE PRECISION DEFAULT 90.0 NOT NULL,
    space_utilization DOUBLE PRECISION DEFAULT 80.0 NOT NULL,
    preview_svg TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- TABLE: localizations (Multilingual Voice Translations)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS localizations (
    id SERIAL PRIMARY KEY,
    medicine_id INTEGER REFERENCES medicines(id) ON DELETE CASCADE NOT NULL,
    language VARCHAR(10) NOT NULL, -- en, hi, mr
    brand_name_local VARCHAR(200),
    generic_name_local VARCHAR(250),
    indications_local TEXT,
    dosage_local TEXT,
    warnings_local TEXT,
    voice_script TEXT
);

-- ==============================================================================
-- SCHEMA UPGRADE / COMPATIBILITY MIGRATIONS
-- (Ensures pre-existing database tables are updated with all latest columns)
-- ==============================================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL;
ALTER TABLE medicines ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active' NOT NULL;
ALTER TABLE batches ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL;
ALTER TABLE batches ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- ==============================================================================
-- HIGH-PERFORMANCE INDEXES (For Sub-10ms Mobile Lookups)
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_branches_org_id ON branches(organization_id);
CREATE INDEX IF NOT EXISTS idx_medicines_brand_name ON medicines(brand_name);
CREATE INDEX IF NOT EXISTS idx_medicines_generic_name ON medicines(generic_name);
CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines(category);
CREATE INDEX IF NOT EXISTS idx_batches_batch_no ON batches(batch_no);
CREATE INDEX IF NOT EXISTS idx_batches_exp_date ON batches(exp_date);
CREATE INDEX IF NOT EXISTS idx_codes_serial_number ON codes(serial_number);
CREATE INDEX IF NOT EXISTS idx_codes_code_hash ON codes(code_hash);
CREATE INDEX IF NOT EXISTS idx_scans_scanned_serial ON scans(scanned_serial);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scans_result ON scans(verification_result);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON audit_logs(organization_id);

-- ==============================================================================
-- INITIAL SEED: Demo Organization & Admin
-- ==============================================================================
INSERT INTO organizations (name, licence_no, contact_email, address)
VALUES ('Apex National Pharma', 'LIC-MH-2026-001', 'admin@pharma.com', 'Worli Pharma City, Mumbai')
ON CONFLICT (name) DO NOTHING;

INSERT INTO branches (organization_id, name, code, address, city, state, contact_email, is_active)
VALUES (1, 'Main Packaging Unit - Mumbai', 'BR-MUM-01', 'Worli Pharma City, Mumbai', 'Mumbai', 'Maharashtra', 'mumbai.plant@pharma.com', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO users (organization_id, branch_id, name, email, password_hash, role, is_active)
VALUES (
    1,
    1,
    'Dr. Rajiv Sharma',
    'admin@pharma.com',
    '$2b$12$e8iV7E1ePvZzQxMh6w1wte5L92d3v9W6x0L6v4y1A5g4R2n0Q7G6e', -- Hash for Admin@12345
    'ORG_ADMIN',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- Seed Demo Pharma with Paracetamol 500 mg, MD110, and EXP-7903-6B98-2D0A
INSERT INTO organizations (name, licence_no, contact_email, address)
VALUES ('Demo Pharma', 'LIC-MH-2026-DEMO', 'contact@demopharma.com', 'Demo Pharma Tech Park, Mumbai')
ON CONFLICT (name) DO NOTHING;

INSERT INTO branches (organization_id, name, code, address, city, state, contact_email, is_active)
VALUES (
    (SELECT id FROM organizations WHERE name = 'Demo Pharma'),
    'Demo Pharma Main Unit',
    'BR-DEMO-01',
    'Demo Pharma Tech Park, Mumbai',
    'Mumbai',
    'Maharashtra',
    'mumbai@demopharma.com',
    TRUE
)
ON CONFLICT DO NOTHING;

INSERT INTO medicines (organization_id, brand_name, generic_name, category, manufacturer, dosage_form, strength, active_ingredients, inactive_excipients, tablet_shape, tablet_color, score_line, coating_type, indications, dosage_instructions, warnings_and_precautions, storage_conditions, schedule_type, voice_summary_en, voice_summary_hi, voice_summary_mr, status)
VALUES (
    (SELECT id FROM organizations WHERE name = 'Demo Pharma'),
    'Paracetamol 500 mg',
    'Paracetamol Tablets IP',
    'Analgesic & Antipyretic',
    'Demo Pharma',
    'Tablet',
    '500 mg',
    '[{"name": "Paracetamol IP", "strength": "500", "unit": "mg", "purpose": "Active Analgesic"}]',
    '["Starch", "Microcrystalline Cellulose", "Magnesium Stearate", "Povidone"]',
    'Round',
    'White',
    'Single break-line',
    'Uncoated',
    'Relief of mild to moderate pain including headache and reduction of fever.',
    'Take 1 tablet every 6 to 8 hours with water as directed by physician.',
    'Do not exceed recommended dose. Avoid consumption with alcohol.',
    'Store below 30°C in a dry place. Protect from light.',
    'OTC',
    'Paracetamol 500 milligram tablet. Contains Paracetamol. For fever and pain relief.',
    'पैरासिटामोल 500 मिलीग्राम टैबलेट। बुखार और दर्द से राहत के लिए।',
    'पॅरासिटामॉल 500 मिलिगॅ्रम गोळी. ताप आणि वेदना कमी करण्यासाठी.',
    'active'
)
ON CONFLICT DO NOTHING;

INSERT INTO batches (medicine_id, branch_id, batch_no, mfg_date, exp_date, quantity, mrp, status)
VALUES (
    (SELECT id FROM medicines WHERE brand_name = 'Paracetamol 500 mg' LIMIT 1),
    (SELECT id FROM branches WHERE code = 'BR-DEMO-01' LIMIT 1),
    'PCM26A01',
    '2026-01-15',
    '2028-09-10',
    50000,
    20.0,
    'active'
)
ON CONFLICT DO NOTHING;

INSERT INTO codes (batch_id, serial_number, code_hash, datamatrix_code, status, scan_count)
VALUES (
    (SELECT id FROM batches WHERE batch_no = 'PCM26A01' LIMIT 1),
    'MD110',
    '4a2f8b5d3e1a7c9f',
    '(01)08901234567890(17)280910(10)PCM26A01(21)MD110',
    'active',
    0
)
ON CONFLICT (serial_number) DO NOTHING;

INSERT INTO batches (medicine_id, branch_id, batch_no, mfg_date, exp_date, quantity, mrp, status)
VALUES (
    (SELECT id FROM medicines WHERE brand_name = 'Paracetamol 500 mg' LIMIT 1),
    (SELECT id FROM branches WHERE code = 'BR-DEMO-01' LIMIT 1),
    'PCM24EXP',
    '2022-06-01',
    '2024-08-12',
    20000,
    20.0,
    'expired'
)
ON CONFLICT DO NOTHING;

INSERT INTO codes (batch_id, serial_number, code_hash, datamatrix_code, status, scan_count)
VALUES (
    (SELECT id FROM batches WHERE batch_no = 'PCM24EXP' LIMIT 1),
    'EXP-7903-6B98-2D0A',
    '7b3e1a9f4c2d8e5a',
    '(01)08901234567890(17)240812(10)PCM24EXP(21)EXP-7903-6B98-2D0A',
    'active',
    0
)
ON CONFLICT (serial_number) DO NOTHING;
