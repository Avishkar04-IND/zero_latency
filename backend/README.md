# Backend Service — Smart Medicine Platform

> Primary Owner: **Member 1**

---

## Overview

The `backend/` directory houses the core FastAPI application and PostgreSQL database integration for the Smart Medicine Platform. It is responsible for database migrations, authentication/RBAC, medicine catalog management, batch code generation (DataMatrix/QR), code verification, and scan log tracking.

---

## Directory Structure

```text
backend/
├── app/
│   ├── api/          # Route handlers & API endpoints
│   ├── core/         # Config, security, JWT auth
│   ├── db/           # Session setup & DB connection
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Business logic & QR/DataMatrix generation
│   └── main.py       # FastAPI application entrypoint
├── tests/            # Pytest test suite
├── requirements.txt  # Python package dependencies
└── README.md
```

---

## Responsibilities

* FastAPI backend server
* PostgreSQL database ORM schemas and migrations
* Medicine catalog management APIs
* Batch code generation (DataMatrix & QR code encoding)
* Code verification & anti-counterfeiting validation APIs
* Scan activity records & audit logs
* Role-based access control (RBAC) & authentication

---

## Local Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4. Access API Docs: `http://localhost:8000/docs`
