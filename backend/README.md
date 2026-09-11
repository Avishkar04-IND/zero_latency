# Smart Medicine Backend Engine (Member 1)

This is the backend for the **Smart Medicine Identification, Authentication & Accessibility Platform** built with **FastAPI, SQLAlchemy 2.0, Pydantic v2, and SQLite / PostgreSQL**.

---

## Quick Start (Instant Local Running)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Seed Database (50 Clinical Medicines + Codes + Batches + Scans)
Run the seed script to instantly populate the database with 50 realistic medicines, full tablet active ingredients, batches, QR codes, and analytics events:
```bash
# From workspace root
python -m backend.app.seeds.run_seed
```

Default credentials seeded:
- **Email:** `admin@pharma.com`
- **Password:** `Admin@12345`

### 3. Start the FastAPI Development Server
```bash
# From workspace root:
python -m uvicorn backend.app.main:app --reload --port 8000
```

Interactive API documentation will be available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Automated Tests

Run the test suite with `pytest`:
```bash
python -m pytest backend/tests -v
```

---

## Switching to PostgreSQL / Supabase

By default, the backend runs on zero-setup SQLite (`medicine_platform.db`).  
To connect to a managed PostgreSQL database (e.g. Supabase, Neon, Render):

1. Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
# On Windows PowerShell:
$env:DATABASE_URL="postgresql://user:password@host:5432/dbname"
```
2. Run the seed script:
```bash
python -m backend.app.seeds.run_seed
```

---

## Git Workflow for Member 1

According to the team collaboration rules:
```bash
# Ensure you are on member1/backend branch
git checkout -b member1/backend

# Add backend and docs
git add backend/ docs/

# Commit with standard style
git commit -m "feat(backend): implement medicine catalog, code generation and verification engine"

# Push to your branch
git push origin member1/backend
```
Then open a Pull Request from `member1/backend` into `integration`.
