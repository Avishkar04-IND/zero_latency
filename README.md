# Smart Medicine Platform

> An accessible, AI-powered pharmaceutical management, verification, layout optimization, and visual-accessibility ecosystem.

---

## 1. Project Overview

**Smart Medicine Platform** is an end-to-end platform built for modern pharmaceutical verification, medicine management, packaging layout optimization, and screen-free mobile accessibility. Designed for supply chain verification and visually impaired end-users, the platform integrates high-density DataMatrix/QR verification, AI voice assistance, packaging area optimization algorithms, and accessible Android mobile interfaces.

---

## 2. System Architecture

The ecosystem consists of four decoupled modules communicating over RESTful API contracts:

```text
               +----------------------------------+
               |        Next.js Web Panel         |
               |  (Admin & User Management + Voice)|
               +----------------+-----------------+
                                |
                                | REST API
                                v
+--------------------+   REST   +--------------------+   REST   +--------------------+
| Accessible Mobile  |--------->|   FastAPI Core     |<-------->| Layout Optimizer   |
| (Flutter / TTS-STT)|          | Backend & Database |          |   Engine (Python)  |
+--------------------+          +--------------------+          +--------------------+
                                         |
                                         v
                                +--------------------+
                                | PostgreSQL Database|
                                +--------------------+
```

---

## 3. Four Modules & Team Ownership

The repository is divided into four isolated primary directories to ensure clean git workflows and zero merge conflicts during parallel development:

| Directory | Module | Technology | Primary Owner | Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| `backend/` | **Core Backend & Security** | Python / FastAPI / PostgreSQL | **Member 1** | APIs, DB schema, batch/medicine management, secure QR/DataMatrix generation, verification & RBAC. |
| `web/` | **Web Admin Panel & Assistant** | Next.js / TypeScript / React | **Member 2** | Dashboard UI, medicine/batch management UI, verification portal, web analytics, general voice/chatbot assistant & API. |
| `layout-engine/` | **Layout Optimizer** | Python / Algorithm / ReportLab | **Member 3** | Package dimensions, print area algorithms, DataMatrix/QR placement, accessibility layouts, SVG/PDF preview generation. |
| `mobile/` | **Accessible Mobile App** | Flutter / Android / TTS / STT | **Member 4** | Screen-reader & gesture UI for visually impaired, camera QR scanner, voice-guided navigation, haptic feedback, assistant integration. |

---

## 4. Technology Stack

* **Core Backend (`backend/`)**: Python 3.11+, FastAPI, PostgreSQL, Pydantic v2, SQLAlchemy / SQLModel, Uvicorn, PyJWT.
* **Web Panel (`web/`)**: Next.js 14+ (App Router), TypeScript, React 18, Tailwind CSS, Lucide Icons.
* **Layout Engine (`layout-engine/`)**: Python 3.11+, FastAPI, NumPy, ReportLab / SVGwrite.
* **Mobile Application (`mobile/`)**: Flutter 3.x, Dart, Mobile Scanner / QR, Text-To-Speech (TTS), Speech-To-Text (STT), Haptic Feedback.
* **Shared Documentation (`docs/`)**: Markdown API contracts, OpenAPI specs, architecture blueprints.

---

## 5. Repository Structure

```text
smart-medicine-platform/
│
├── backend/                  # Member 1: FastAPI core backend & DB
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── web/                      # Member 2: Next.js user/admin panel & voice assistant
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/api/
│   │   ├── lib/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── config/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── mobile/                   # Member 4: Accessible Flutter application
│   ├── lib/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── features/
│   │   ├── widgets/
│   │   └── main.dart
│   ├── test/
│   ├── android/
│   ├── assets/
│   ├── pubspec.yaml
│   └── README.md
│
├── layout-engine/            # Member 3: Standalone layout optimization service
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── algorithms/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── docs/                     # Shared architectural & API documentation
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACT.md
│   ├── DATABASE_SCHEMA.md
│   ├── INTEGRATION.md
│   └── DEMO_FLOW.md
│
├── .github/                  # GitHub workflows, templates, CODEOWNERS
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   ├── CODEOWNERS
│   └── pull_request_template.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## 6. Development Workflow & Branch Strategy

To ensure stability and seamless multi-instance Antigravity development:

### Branching Hierarchy
```text
main (Production Ready / Stable)
  │
  └── integration (Staging & Integration Testing)
       │
       ├── member1/backend
       ├── member2/web-assistant
       ├── member3/layout-engine
       └── member4/mobile-accessibility
```

### Git Rules & Guidelines
1. **Never push directly to `main` or `integration`**.
2. **Work strictly inside your designated module directory** (`backend/`, `web/`, `layout-engine/`, or `mobile/`).
3. Create pull requests targeting `integration` first.
4. Run local linting and unit tests before opening a PR.
5. Keep commits small, self-contained, and descriptive.
6. **Zero Secrets Policy**: Never commit credentials, private keys, or `.env` files.

---

## 7. API Contract & Communication Rules

* **API-First Rule**: All cross-module interfaces are strictly governed by [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).
* **Contract Changes**: If an API endpoint or payload structure needs modification, update `docs/API_CONTRACT.md` **first** and notify the team before updating code.
* **No Direct DB Access**: Web and Mobile modules **must** communicate through backend API endpoints. Direct database calls are strictly prohibited.

---

## 8. Integration Strategy & Mocking

* Each frontend/mobile module is built with an abstraction layer supporting mock API responses (`msw` or local mock services).
* Members can develop independently without waiting for live backend endpoints.
* Integration testing is conducted against the `integration` branch.

---

## 9. How to Run Each Module

### Backend (`backend/`)
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate | On Unix: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Web Panel (`web/`)
```bash
cd web
npm install
npm run dev
# Server will run on http://localhost:3000
```

### Layout Engine (`layout-engine/`)
```bash
cd layout-engine
python -m venv .venv
# On Windows: .venv\Scripts\activate | On Unix: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Mobile Application (`mobile/`)
```bash
cd mobile
flutter pub get
flutter run
```

---

## 10. Team Responsibilities Summary

* **`backend/`** → Member 1
* **`web/`** → Member 2
* **`layout-engine/`** → Member 3
* **`mobile/`** → Member 4
* **`docs/`** → Shared Team Ownership

---

## 11. Architectural Principles

1. **Module Ownership**: Clear file system boundaries.
2. **API-First Integration**: Documented contracts.
3. **No Direct DB Access**: Centralized security model.
4. **Mock-First Capability**: Unblocked frontend development.
5. **Stable Main Branch**: Continuous integration.
6. **Accessibility First**: First-class TTS/STT and gesture integration.
