# RAWDH (روض) — Testing & Simulation Guide

A simple, clear, and concise guide to running all unit, integration, simulation, and end-to-end (E2E) tests for the RAWDH telemonitoring platform.

---

## 1. Quick Test Commands (One-Liners)

### Run Everything

```bash
# 1. Frontend Unit & Integration Tests (57 tests)
npm --prefix Frontend run test

# 2. Generate Real Multi-Persona Simulation Data in Backend
python simulate_backend_data.py

# 3. Live Simulation Integration Tests (19 tests - Charts, Patients, Alerts)
python test_live_simulation_integration.py

# 4. Full-System End-to-End Integration Suite (11 Scenarios / 33 Assertions)
python test_full_system_integration.py

# 5. Backend Core E2E Tests (15 tests)
python Backend/test_v3_e2e.py

# 6. Backend Comprehensive API Suite (15 tests)
python Backend/test_v3_comprehensive.py
```

---

## 2. Test Suite Overview

| Test Suite | File / Command | Scope | Target | Tests / Status |
|:---|:---|:---|:---|:---:|
| **Frontend Unit & Mappers** | `Frontend/src/__tests__/mappers.test.ts` | Data transformers, DTO mappers, time formatters | Client | **16 Passed** |
| **Frontend API Client** | `Frontend/src/__tests__/apiClient.test.ts` | Axios interceptors, JWT Bearer injection, 401 refresh | Client | **6 Passed** |
| **Frontend Services** | `Frontend/src/__tests__/*Service.test.ts` | Auth, Doctor, Patient, Reading, Alert, Device services | API Mock | **31 Passed** |
| **Frontend UI Integration** | `Frontend/src/__tests__/integrationFlows.test.ts` | Doctor triage, Patient guidance, 422 resiliency flows | Integration | **4 Passed** |
| **Live Simulation Runner** | `test_live_simulation_integration.py` | Validates live backend data, charts, patients, alerts, SLA | Full Stack | **19 Passed** |
| **Full System E2E Runner** | `test_full_system_integration.py` | 11 End-to-end clinical lifecycle scenarios against live DB | Full Stack | **33 Passed** |
| **Backend Core E2E** | `Backend/test_v3_e2e.py` | Doctor/Patient provisioning, consent, reading ingestion | Backend | **15 Passed** |
| **Backend Comprehensive** | `Backend/test_v3_comprehensive.py` | Priority triage, audit trail, reports, SLA escalation | Backend | **15 Passed** |
| **Total** | **All Suites** | **Complete Telemonitoring Platform** | **End-to-End** | **139 / 139 Passed (100%)** |

---

## 3. Real Backend Data Simulation Engine

Static mock data fixtures have been completely decoupled from the frontend. The entire application is now driven by dynamic backend simulation:

### Seed / Re-Seed Simulated Cohort

```bash
python simulate_backend_data.py
```

This generates a clinical telemonitoring database:
- **Doctor:** `dr.karim@clinic.com` / `Password123!` (Cardiologist, Clinique Al-Amal)
- **5 Clinical Patient Personas:**
  1. **Fatima Zahra** (`fatima.zahra@email.com` / `Password123!`): Age 71, CKD Stage 3, Severe crisis reading (186/122 mmHg), **P1_critical** triage status.
  2. **Marc Dupuis** (`marc.dupuis@email.com` / `Password123!`): Age 58, Stage 2 HTN, 14 days of fluctuating readings (156–168 / 94–102 mmHg), **P2_high** triage status.
  3. **Jean Moreau** (`jean.moreau@email.com` / `Password123!`): Age 65, Type 2 Diabetes comorbidity, **P3_moderate** triage status.
  4. **Amina Benali** (`amina.benali@email.com` / `Password123!`): Age 62, Telemonitoring, 722 Diagnostic schedule, OMRON BLE device, progressive 14-day improving curve (138/88 down to 124/78 mmHg).
  5. **Ahmed Cherif** (`ahmed.cherif@email.com` / `Password123!`): Age 54, Self-monitoring, stable readings, **P4_routine** triage status.

### Verify Live Simulation Integration

```bash
python test_live_simulation_integration.py
```

Validates:
- Real SVG Chart Data generation for both Doctor (`BPLineChart` with 14-day longitudinal curve) and Patient (7-day trend curve & 14-day history).
- Priority Queue sorting (P1–P4) with real clinical scores and delta calculations.
- Caseload alert delivery, SLA timer halt upon acknowledgment, and evidence packets.
- Patient safety guidance confirmation, OMRON BLE device inventory, and preferences mutation.

---

## 4. Frontend Tests (Vitest)

Frontend tests verify all API client interceptors, state transformations, error normalization, and mock integration flows.

### Commands

```bash
# Run tests once
npm --prefix Frontend run test

# Run tests in watch mode (interactive)
npm --prefix Frontend run test:watch

# Verify production build and TypeScript types
npm --prefix Frontend run build

# Run linter
npm --prefix Frontend run lint
```

---

## 5. Running the Live Integrated System

To spin up both Frontend and Backend together in live interactive mode:

### Step 1: Start Backend (FastAPI)

```bash
cd Backend
python main.py
# Server runs on http://127.0.0.1:8000
# Interactive OpenAPI documentation: http://127.0.0.1:8000/docs
```

### Step 2: Start Frontend (Vite)

```bash
cd Frontend
npm run dev
# App runs on http://localhost:5173
```

You can log in directly using the pre-seeded credentials:
- **Doctor Workspace:** `dr.karim@clinic.com` / `Password123!` (Clicking "Login as Doctor" authenticates live against backend)
- **Patient Workspace:** `amina.benali@email.com` / `Password123!` (Clicking "Login as Patient" authenticates live against backend)
