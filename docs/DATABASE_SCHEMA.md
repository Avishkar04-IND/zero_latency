# Smart Medicine Platform — Database Schema Specification

## 1. Overview

The core backend utilizes a PostgreSQL relational database managed via SQLAlchemy / SQLModel ORM models.

---

## 2. Entity Relationship Overview (Placeholders)

### `users`
* `id`: UUID (Primary Key)
* `username`: VARCHAR(255)
* `email`: VARCHAR(255)
* `hashed_password`: VARCHAR(255)
* `role`: VARCHAR(50) — `ADMIN`, `MANUFACTURER`, `USER`
* `created_at`: TIMESTAMP

### `medicines`
* `id`: UUID (Primary Key)
* `name`: VARCHAR(255)
* `dosage`: VARCHAR(100)
* `description`: TEXT
* `manufacturer_id`: UUID (Foreign Key -> users.id)
* `created_at`: TIMESTAMP

### `batches`
* `id`: UUID (Primary Key)
* `medicine_id`: UUID (Foreign Key -> medicines.id)
* `batch_number`: VARCHAR(100)
* `manufacture_date`: DATE
* `expiry_date`: DATE
* `quantity`: INTEGER
* `status`: VARCHAR(50)

### `codes`
* `id`: UUID (Primary Key)
* `batch_id`: UUID (Foreign Key -> batches.id)
* `serial_number`: VARCHAR(255) (Unique Index)
* `code_type`: VARCHAR(50) — `DATAMATRIX`, `QR`
* `status`: VARCHAR(50) — `GENERATED`, `ACTIVE`, `VERIFIED`, `RECALLED`

### `scan_records`
* `id`: UUID (Primary Key)
* `code_id`: UUID (Foreign Key -> codes.id)
* `scanned_by`: UUID (Optional Foreign Key -> users.id)
* `scanned_at`: TIMESTAMP
* `latitude`: FLOAT
* `longitude`: FLOAT
* `verification_result`: VARCHAR(50)
