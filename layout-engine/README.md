# Pharmaceutical Layout Optimizer Engine — Smart Medicine Platform

> Primary Owner: **Member 3**

---

## Overview

The `layout-engine/` directory contains the independent optimization microservice responsible for calculating medicine packaging print areas, DataMatrix/QR placements, accessibility typography scaling, tablet/strip grid layouts, and generating SVG/PDF layout previews.

---

## Directory Structure

```text
layout-engine/
├── app/
│   ├── api/          # Microservice API routes & endpoints
│   ├── core/         # Engine settings & constants
│   ├── models/       # Pydantic layout request/response schemas
│   ├── services/     # SVG/PDF preview generation services
│   ├── algorithms/   # Core geometry & packing layout algorithms
│   └── main.py       # FastAPI engine entrypoint
├── tests/            # Test suite for spatial algorithms
├── requirements.txt  # Python dependencies (NumPy, ReportLab, Pillow)
└── README.md
```

---

## Responsibilities

* Package & blister strip dimension calculations
* Printable area calculation algorithms
* Optimal QR / DataMatrix code spatial placement
* High-contrast, accessibility-optimized text placement
* Tablet & strip layout packing optimization
* Printing cost & waste minimization metrics
* Rendering vector SVG and PDF packaging layout previews

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
3. Run engine server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
4. Access API documentation at `http://localhost:8001/docs`.
