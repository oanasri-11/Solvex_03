# RAWDH (روض) — Testing Guide

A simple, clear, and concise guide to running all unit, integration, and end-to-end (E2E) tests for the RAWDH telemonitoring platform.

---

## 1. Quick Test Commands (One-Liners)

### Run Everything

```bash
# Frontend Unit & Integration Tests (57 tests)
npm --prefix Frontend run test

# Full-System End-to-End Integration Suite (11 Scenarios / 33 Assertions)
python test_full_system_integration.py

# Backend Core E2E Tests (15 tests)
python Backend/test_v3_e2e.py

# Backend Comprehensive API Suite (15 tests)
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
| **Full System E2E Runner** | `test_full_system_integration.py` | 11 End-to-end clinical lifecycle scenarios against live DB | Full Stack | **33 Passed** |
| **Backend Core E2E** | `Backend/test_v3_e2e.py` | Doctor/Patient provisioning, consent, reading ingestion | Backend | **15 Passed** |
| **Backend Comprehensive** | `Backend/test_v3_comprehensive.py` | Priority triage, audit trail, reports, SLA escalation | Backend | **15 Passed** |
| **Total** | **All Suites** | **Complete Telemonitoring Platform** | **End-to-End** | **120 / 120 Passed (100%)** |

---

## 3. Frontend Tests (Vitest)

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

### Expected Output

```
Test Files  9 passed (9)
     Tests  57 passed (57)
  Duration  ~700ms
```

---

## 4. Full-System Integration & E2E Tests (Python)

The standalone runner `test_full_system_integration.py` executes 11 real-world clinical scenarios using FastAPI's `TestClient` against the SQLite database:

1. **Scenario 1 — Auth & RBAC**: Admin signup, login, JWT bearer issue, session rehydration (`/auth/me`), silent refresh (`/auth/refresh`), invalid credential rejection (401).
2. **Scenario 2 — Enrollment & Caseload**: Doctor profile creation, patient enrollment, doctor-patient assignment.
3. **Scenario 3 — Protocol & Consent**: Informed consent logging (F15), telemonitoring mode switch, 722 diagnostic protocol schedule setup (F10).
4. **Scenario 4 — Vitals & Physiological Thresholds**: Normal BP (124/82), Stage 2 elevated BP (158/98), severe crisis reading (186/122 with symptoms).
5. **Scenario 5 — Multi-Tier Alert Generation & SLA**: Alert generation (`critical_emergency`), doctor alert retrieval, clinician acknowledgment (stops SLA timer), evidence packet audit.
6. **Scenario 6 — Algorithmic Triage & Priority Queue (P1–P4)**: Workspace dashboard metrics, triage queue sorting, top patient priority evaluation (`P2_high` / `P1_critical`).
7. **Scenario 7 — Outreach & Patient Guidance**: Patient plain-language emergency guidance (RS-1), patient safety acknowledgment, doctor contact request dispatch and drawer resolution.
8. **Scenario 8 — 14-Day Protocol Review & Sign-Off**: Pre-review summary calculation (D3/F18), doctor clinical review sign-off and persistence.
9. **Scenario 9 — Connected Hardware & BLE Pairing**: OMRON Bluetooth monitor pairing, inventory listing, hardware unpairing.
10. **Scenario 10 — Accessibility & Preferences**: RTL Arabic locale, 150% font scale, `calm_dark` theme mutation, session persistence.
11. **Scenario 11 — Forensic Audit Trail**: Append-only HIPAA/GDPR audit log inspection.

### Command

```bash
python test_full_system_integration.py
```

### Expected Output

```
=======================================================================
  RAWDH (روض) TELEMONITORING PLATFORM — FULL SYSTEM E2E TEST RUN
=======================================================================
 [PASS] SCENARIO 1 [Auth & RBAC]: Admin User Registration 
 [PASS] SCENARIO 1 [Auth & RBAC]: Admin Login & JWT Issuance 
 [PASS] SCENARIO 1 [Auth & RBAC]: Session Rehydration (/auth/me) 
 [PASS] SCENARIO 1 [Auth & RBAC]: Silent Token Refresh (/auth/refresh) 
 [PASS] SCENARIO 1 [Auth & RBAC]: Invalid Password Rejection (401) 
 [PASS] SCENARIO 2 [Enrollment & Caseload]: Doctor Profile Provisioning 
 [PASS] SCENARIO 2 [Enrollment & Caseload]: Patient Enrollment & Medical Profile 
 [PASS] SCENARIO 2 [Enrollment & Caseload]: Doctor-Patient Caseload Linking 
 [PASS] SCENARIO 3 [Protocol & Consent]: Patient Consent Recording (F15) 
 [PASS] SCENARIO 3 [Protocol & Consent]: Monitoring Mode Setting (Telemonitoring) 
 [PASS] SCENARIO 3 [Protocol & Consent]: 722 Diagnostic Protocol Setup (F10) 
 [PASS] SCENARIO 4 [Vitals & Thresholds]: Standard Reading Ingestion (124/82) 
 [PASS] SCENARIO 4 [Vitals & Thresholds]: Stage 2 Elevated Reading (158/98) 
 [PASS] SCENARIO 4 [Vitals & Thresholds]: Crisis Reading Ingestion (186/122)
 [PASS] SCENARIO 5 [Alert Engine & SLA]: Doctor Caseload Alerts Retrieval
 [PASS] SCENARIO 5 [Alert Engine & SLA]: Clinical Alert Tier Evaluation
 [PASS] SCENARIO 5 [Alert Engine & SLA]: Doctor Acknowledges Alert (Stops SLA) 
 [PASS] SCENARIO 5 [Alert Engine & SLA]: Alert Evidence Packet Inspection 
 [PASS] SCENARIO 6 [Triage Queue]: Doctor Dashboard Metric Aggregation 
 [PASS] SCENARIO 6 [Triage Queue]: Triage Queue Sorted Retrieval (P1–P4) 
 [PASS] SCENARIO 6 [Triage Queue]: Top Patient Triage Level Assigned
 [PASS] SCENARIO 7 [Outreach & Guidance]: Patient-Facing Plain Language Alerts 
 [PASS] SCENARIO 7 [Outreach & Guidance]: Patient Safety Guidance Confirmation 
 [PASS] SCENARIO 7 [Outreach & Guidance]: Doctor Dispatches Contact Task 
 [PASS] SCENARIO 7 [Outreach & Guidance]: Doctor Completes Contact Task Drawer 
 [PASS] SCENARIO 8 [Case Review & Digest]: 14-Day Pre-Review Digest Computation 
 [PASS] SCENARIO 8 [Case Review & Digest]: Clinical Review Sign-Off & Persistence 
 [PASS] SCENARIO 9 [Hardware & Devices]: Bluetooth BLE Hardware Pairing 
 [PASS] SCENARIO 9 [Hardware & Devices]: Hardware Device Inventory Listing 
 [PASS] SCENARIO 9 [Hardware & Devices]: Hardware Device Unpairing 
 [PASS] SCENARIO 10 [Accessibility & i18n]: Accessibility Settings Mutation (PATCH /users/me) 
 [PASS] SCENARIO 10 [Accessibility & i18n]: Accessibility Persistence Verification
 [PASS] SCENARIO 11 [Audit Logs]: HIPAA/GDPR Audit Trail Recording

=======================================================================
  E2E INTEGRATION TEST SUMMARY
=======================================================================
  Total Scenarios Evaluated: 11
  Total Individual Assertions: 33
  Passed: 33 | Failed: 0
  Success Rate: 100.0%
=======================================================================
>>> ALL FULL-SYSTEM INTEGRATION TEST SCENARIOS PASSED WITH ZERO ERRORS! <<<
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

---

## 6. Bugs Resolved During Test Implementation

During test authoring and execution, the following discrepancies were identified and resolved:

1. **Patient Alert Visibility after Clinician Acknowledgment (`alert_service.py`)**:
   - *Bug:* When a doctor acknowledged an alert (`lifecycle = "acknowledged"`), `get_alerts_for_patient(active_only=True)` excluded it, prematurely hiding vital safety guidance and emergency instructions from the patient.
   - *Fix:* Updated query filter in `alert_service.py` to include `"acknowledged"` so patients retain access to emergency instructions until the alert is formally closed.
2. **Reading Ingestion Schema (`BloodPressureReadingOut`)**:
   - *Clarification:* Normalized test assertions to verify `status_level == "severe"` and alert generation directly against backend contracts rather than deprecated top-level flags.
3. **Vitest Node Environment Mocking (`setup.ts`)**:
   - *Fix:* Provided full in-memory `LocalStorageMock` in `Frontend/src/__tests__/setup.ts` to allow testing browser token storage seamlessly in Node environments.
4. **Parameter Flexibility in `readingService.getOwnReadings`**:
   - *Fix:* Updated `readingService.ts` to support both numeric limits (`10`) and filter query objects (`{ from, to, page }`).
5. **Windows Console Unicode Output**:
   - *Fix:* Reconfigured stdout stream to UTF-8 to prevent codepage 1252 exceptions when rendering Arabic test logs (`روض`).

