# Database Schema Specification

This document details the relational database schema implemented in SQLAlchemy and compatible with both **PostgreSQL** and **SQLite**.

---

## Entity-Relationship Overview

```text
[organizations] 1 ───────< N [branches] 1 ───────< N [users]
       │                          │
       │ 1                        │ 1
       v N                        v N
  [medicines] 1 ─────────< N [batches] 1 ───────< N [codes] 1 ───< N [scans]
       │
       │ 1
       v N
 [localizations]
```

---

## Table Definitions

### 1. `organizations`
Represents registered pharmaceutical manufacturers and regulatory bodies.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique organization ID |
| `name` | String(255) | Unique, Not Null | Organization/Company Name |
| `licence_no` | String(100) | Not Null | Manufacturing license number (FDA/CDSCO) |
| `contact_email`| String(255) | Not Null | Official contact email |
| `contact_phone`| String(50) | Nullable | Contact phone number |
| `address` | Text | Nullable | Factory / corporate address |
| `created_at` | DateTime | Default UTC | Registration timestamp |

---

### 2. `branches`
Represents specific manufacturing plants, packaging lines, or regional distribution branches.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique branch ID |
| `organization_id` | Integer | FK(`organizations.id`), Not Null | Parent manufacturer ID |
| `name` | String(200) | Not Null | Facility or branch name |
| `code` | String(50) | Indexed, Nullable | Facility code (e.g. `BR-MUM-01`) |
| `address` | Text | Nullable | Physical facility address |
| `city` | String(100) | Nullable | City |
| `state` | String(100) | Nullable | State / Province |
| `contact_email`| String(255) | Nullable | Branch contact email |
| `contact_phone`| String(50) | Nullable | Branch contact phone |
| `is_active` | Boolean | Default True | Operational status |
| `created_at` | DateTime | Default UTC | Creation timestamp |

---

### 3. `users`
System users (Super Admins, Organization Admins, Branch Admins, Operators, and Viewers).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique user ID |
| `organization_id` | Integer | FK(`organizations.id`), Nullable | Organization membership |
| `branch_id` | Integer | FK(`branches.id`), Nullable | Branch membership |
| `name` | String(150) | Not Null | Full name |
| `email` | String(255) | Unique, Indexed, Not Null | Login email address |
| `password_hash`| String(255) | Not Null | Bcrypt hashed password |
| `role` | String(50) | Default 'ORG_ADMIN' | `SUPER_ADMIN`, `ORG_ADMIN`, `BRANCH_ADMIN`, `OPERATOR`, `VIEWER` |
| `is_active` | Boolean | Default True | Account active status |
| `created_at` | DateTime | Default UTC | Account creation date |

---

### 3. `medicines`
Master pharmaceutical formulations with chemical composition and physical tablet specs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique medicine ID |
| `organization_id` | Integer | FK(`organizations.id`), Not Null | Manufacturer ID |
| `brand_name` | String(200) | Indexed, Not Null | Brand/Trade Name (e.g. Dolo-650, Augmentin) |
| `generic_name`| String(250) | Indexed, Not Null | International Nonproprietary Name (INN) |
| `category` | String(100) | Indexed, Not Null | Therapeutic category (Analgesic, Antibiotic) |
| `manufacturer`| String(250) | Not Null | Company marketing name |
| `dosage_form` | String(50) | Default 'Tablet' | Tablet, Capsule, Syrup, etc. |
| `strength` | String(100) | Not Null | e.g., 650 mg, 500mg + 125mg |
| `active_ingredients` | Text (JSON) | Not Null | List of `{name, strength, unit, purpose}` |
| `inactive_excipients`| Text (JSON) | Nullable | List of binding/filler excipients |
| `tablet_shape`| String(50) | Default 'Round' | Physical shape (Round, Oblong, Oval) |
| `tablet_color`| String(50) | Default 'White' | Visual color |
| `score_line` | String(100) | Default 'None' | Score mark specification |
| `coating_type`| String(100) | Default 'Film-coated' | Film, Enteric, Uncoated |
| `indications` | Text | Not Null | Diseases/conditions treated |
| `dosage_instructions` | Text | Not Null | Patient directions |
| `warnings_and_precautions` | Text | Not Null | Warnings and contraindications |
| `side_effects`| Text | Nullable | Documented side effects |
| `storage_conditions` | String(255) | Nullable | Storage temperature/moisture guidance |
| `schedule_type` | String(100) | Default 'Schedule H' | Regulatory class (OTC, Schedule H, H1, X) |
| `voice_summary_en` | Text | Nullable | Voice synthesizer script in English |
| `voice_summary_hi` | Text | Nullable | Voice synthesizer script in Hindi |
| `voice_summary_mr` | Text | Nullable | Voice synthesizer script in Marathi |
| `status` | String(50) | Default 'active' | `active`, `discontinued`, `under_review` |
| `created_at` | DateTime | Default UTC | Creation timestamp |

---

### 4. `batches`
Production lot metadata and expiration timelines.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique batch ID |
| `medicine_id` | Integer | FK(`medicines.id`), Not Null | Parent medicine ID |
| `branch_id` | Integer | FK(`branches.id`), Nullable | Manufacturing facility branch ID |
| `created_by` | Integer | FK(`users.id`), Nullable | User ID who created the batch |
| `batch_no` | String(100) | Indexed, Not Null | Lot/Batch number (e.g. BT-2026-101) |
| `mfg_date` | Date | Not Null | Manufacturing date |
| `exp_date` | Date | Indexed, Not Null | Expiration date |
| `quantity` | Integer | Default 10000 | Number of units produced in batch |
| `mrp` | Float | Default 50.0 | Maximum retail price (INR) |
| `status` | String(50) | Default 'active' | `active`, `expired`, `recalled`, `quarantined` |
| `created_at` | DateTime | Default UTC | Entry timestamp |

---

### 5. `codes`
Cryptographic serial numbers, anti-tamper hashes, and generated 2D code assets.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique code ID |
| `batch_id` | Integer | FK(`batches.id`), Not Null | Batch reference |
| `serial_number` | String(100) | Unique, Indexed, Not Null | Non-sequential alphanumeric identifier |
| `code_hash` | String(128) | Indexed, Not Null | HMAC-SHA256 signature |
| `qr_data_url` | Text | Nullable | Base64 PNG data URL |
| `qr_svg` | Text | Nullable | Scalable vector graphic markup |
| `datamatrix_code`| String(255) | Nullable | GS1 standard formatted string |
| `status` | String(50) | Default 'active' | `active`, `revoked`, `scratched`, `recalled` |
| `scan_count` | Integer | Default 0 | Times verified by consumers |
| `first_scanned_at` | DateTime | Nullable | First scan timestamp |
| `last_scanned_at` | DateTime | Nullable | Most recent scan timestamp |
| `created_at` | DateTime | Default UTC | Generation timestamp |

---

### 6. `scans`
Comprehensive audit trail for every verification event across the globe.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique scan log ID |
| `code_id` | Integer | FK(`codes.id`), Nullable | Verified code reference |
| `user_id` | Integer | FK(`users.id`), Nullable | User ID if logged in |
| `scanned_serial` | String(100) | Indexed, Not Null | Scanned serial string |
| `verification_result` | String(50) | Indexed, Not Null | `GENUINE`, `EXPIRED`, `SUSPICIOUS_MULTIPLE_SCANS`, `INVALID`, `REVOKED` |
| `risk_score` | Integer | Default 0 | Fraud/Counterfeit score (0–100) |
| `risk_reasons` | Text (JSON) | Nullable | Diagnostic reasons |
| `ip_address` | String(64) | Nullable | Client IP address |
| `device_info` | String(255) | Nullable | OS / Model / Browser info |
| `location_lat` | Float | Nullable | GPS Latitude |
| `location_lng` | Float | Nullable | GPS Longitude |
| `timestamp` | DateTime | Indexed, Default UTC | Event timestamp |

---

### 7. `audit_logs`
Authoritative audit trail of administrative and security actions across the platform.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto-increment | Unique audit entry ID |
| `user_id` | Integer | FK(`users.id`), Nullable, Indexed | User who performed the action |
| `organization_id` | Integer | FK(`organizations.id`), Nullable, Indexed | Scoped tenant organization |
| `branch_id` | Integer | FK(`branches.id`), Nullable, Indexed | Associated branch facility |
| `action` | String(100) | Indexed, Not Null | Event type (`LOGIN`, `LOGOUT`, `BATCH_CREATED`, `CODE_GENERATED`, etc.) |
| `entity_type` | String(100) | Indexed, Nullable | Target entity type (`batch`, `medicine`, `code`, `user`) |
| `entity_id` | String(100) | Indexed, Nullable | Target entity identifier |
| `details` | Text (JSON) | Nullable | Sanitized payload / metadata (secrets redacted) |
| `ip_address` | String(64) | Nullable | Origin IP address |
| `created_at` | DateTime | Indexed, Default UTC | Audit event timestamp |

