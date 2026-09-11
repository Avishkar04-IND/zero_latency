# Smart Medicine Platform — System Architecture Blueprint

## 1. High-Level Architecture Overview

The **Smart Medicine Platform** is designed as a modular, service-oriented ecosystem with strict separation of concerns among the 4 primary components:

* **Core Backend (`backend/`)**: Microservice handling database persistence, business rules, batch code generation, verification endpoints, and RBAC authentication.
* **Web Portal (`web/`)**: Next.js single-page application providing administrative dashboards, medicine management UI, analytics, and host for the shared Voice Assistant API gateway.
* **Layout Engine (`layout-engine/`)**: Dedicated Python algorithm engine calculating packaging print geometry, code placement optimization, and SVG/PDF preview generation.
* **Accessible Mobile App (`mobile/`)**: Flutter Android application optimized for screen-reader (TTS/STT), tactile gesture, and camera scanning interactions for visually impaired users.

---

## 2. Component Communication Matrix

```text
[Mobile App] ------------ REST ------------> [Core Backend]
     |                                             ^
     | (Assistant Queries)                         |
     v                                             v
[Web Assistant Gateway] -------------------> [PostgreSQL DB]
                                                   ^
[Layout Engine] <-------- REST API ----------------+
```

---

## 3. Data Flow Boundaries

* **No direct database access from Web or Mobile apps**.
* Web and Mobile apps communicate exclusively over HTTPS REST endpoints.
* Layout Engine operates as a stateless calculation service.

---

## 4. Security & Compliance Principles

* JWT-based Bearer token authentication.
* Role-Based Access Control (Admin, Manufacturer, Inspector, End User).
* Verification endpoint anonymization for public scans.
