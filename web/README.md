# Web User & Admin Panel — Smart Medicine Platform

> Primary Owner: **Member 2**

---

## Overview

The `web/` directory contains the Next.js (TypeScript) Web Application providing the administrative interface, medicine and batch management portal, code verification interface, analytics dashboards, and general voice/chatbot assistant integration.

---

## Directory Structure

```text
web/
├── src/
│   ├── app/                 # Next.js App Router routes
│   │   ├── dashboard/       # System metrics & overall health
│   │   ├── medicines/       # Medicine catalog UI
│   │   ├── batches/         # Manufacturing batch tracking
│   │   ├── codes/           # DataMatrix/QR generation UI
│   │   ├── verification/    # Code verification UI
│   │   ├── analytics/       # Verification & scan analytics
│   │   ├── assistant/       # Web chatbot & voice assistant UI
│   │   └── settings/        # System configuration
│   ├── components/          # Shared UI components
│   ├── features/            # Feature-specific logic & modules
│   ├── services/api/        # API client integrations
│   ├── lib/                 # Utility functions & helpers
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript definitions
│   └── config/              # Constants & site configuration
├── public/                  # Static assets & images
├── package.json             # NPM dependencies & scripts
├── tsconfig.json            # TypeScript compiler configuration
└── README.md
```

---

## Responsibilities

* Web user panel and admin management dashboard
* Medicine catalog and batch code management UI
* Code generation interface and manual verification portal
* Verification activity analytics and scan location reports
* General chatbot and web voice assistant UI
* Exposing assistant integration endpoints consumable by the mobile app

---

## Local Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start development server:
   ```bash
   npm run dev
   ```
3. Open browser at `http://localhost:3000`.
