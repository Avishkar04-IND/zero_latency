# Smart Medicine Platform — Module Integration Blueprint

## 1. Overview

This document outlines the local integration testing process between the four platform modules.

---

## 2. Integration Port Map

| Service | Port | Description |
| :--- | :--- | :--- |
| **Backend Core** | `8000` | FastAPI core REST API & DB |
| **Layout Engine** | `8001` | FastAPI packaging optimization service |
| **Web Panel** | `3000` | Next.js Web Admin & Assistant portal |
| **Mobile App** | Configurable | Flutter Android device / emulator |

---

## 3. Integration Scenarios

### Scenario A: Mobile Scan to Backend Verification
1. Mobile camera scans DataMatrix code.
2. Mobile app calls `POST http://localhost:8000/api/v1/verification/verify`.
3. Backend returns authenticity, medicine info, and expiry date.
4. Mobile app speaks results via TTS engine.

### Scenario B: Web Layout Engine Trigger
1. User configures packaging dimensions in Web UI (`/web/src/app/codes`).
2. Web app invokes Layout Engine API `POST http://localhost:8001/api/v1/layout/optimize`.
3. Layout Engine calculates coordinates and returns SVG preview rendering.

### Scenario C: Mobile Assistant Query
1. Mobile user speaks query ("When does this medicine expire?").
2. Mobile app streams query to Web Assistant API `POST http://localhost:3000/api/v1/assistant/query`.
3. Voice assistant responds with text and audio TTS stream.
