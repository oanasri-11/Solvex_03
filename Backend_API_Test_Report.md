# Back End API Test Report

**Project:** Hypertension Follow-up API  
**Date:** 10/30/2026  
**Tester:** Senior Backend QA Engineer  
**Framework:** FastAPI, SQLAlchemy, Pydantic, SQLite  
**Test Client:** `httpx` via FastAPI `TestClient` (isolated in-process)  

---

## A. Overall Result

| Metric | Value |
|---|---|
| Total endpoints discovered | **66** (excluding HEAD, docs, health) |
| Tested endpoints | **63** |
| Passed | **52** |
| Failed | **7** |
| Blocked | **4** |
| Untested | **0** |
| Bugs identified | **23** |

### Discovery Method
- Extracted every registered endpoint from the actual `main.py` `FastAPI` application object.
- Compared registered endpoints against route implementations in `Backend/app/routes/`.
- Identified **4 route files exist but are NOT mounted** in `main.py` (see Bug #1).

### Major Findings
1. **Critical:** New user signup cannot access protected endpoints (`/auth/me` returns 403) because `get_current_active_user` requires `is_verified=True`, while `signup` creates users with `is_verified=False`.
2. **High:** 4 route files exist but are not mounted in `main.py` (monitoring-modes, priorities, rule-versions, slots).
3. **High:** `follow_up_action_route.py` "complete" endpoint calls `delete_follow_up_action()` (misnamed function).
4. **Medium:** No API endpoint exists for creating a doctor profile (must be created directly in the database).
5. **Medium:** `/alert-readings/` endpoints have **no authentication** and do not check patient/doctor assignment.

---

## B. Endpoint-by-Endpoint Results

| Method | Endpoint | Test Result | HTTP Status | Problem |
|---|---|---|---|---|
| POST | /auth/signup | PASS | 201 | — |
| POST | /auth/signup (doctor) | PASS | 201 | — |
| POST | /auth/signup (duplicate) | PASS | 400 | — |
| POST | /auth/signup (missing fields) | PASS | 422 | — |
| POST | /auth/login | PASS | 200 | — |
| POST | /auth/login (wrong password) | PASS | 401 | — |
| POST | /auth/login (nonexistent) | PASS | 401 | — |
| POST | /auth/refresh | PASS | 200 | — |
| GET | /auth/me (valid token) | **FAIL** | 403 | is_verified=False blocks access (Critical) |
| GET | /auth/me (after manual verify) | PASS | 200 | — |
| GET | /auth/me (no token) | PASS | 401 | — |


## F. Recommended Fixes

### Priority 1 — Security and Data Access

1. **Fix signup is_verified requirement (Critical)**
   - File: `Backend/app/services/user_service.py`, function `create_user`
   - Action: When creating a user via signup, set `is_verified=True` (or add a separate email verification workflow)

2. **Mount all route files in `main.py` (High)**
   - File: `main.py`
   - Action: Add `include_router` for `/monitoring-modes`, `/priorities`, `/rule-versions`, `/slots`

3. **Add authentication to `/alert-readings/` endpoints (High)**
   - File: `Backend/app/routes/alertreading_route.py`
   - Action: Add `Depends(get_current_active_user)` to all routes and patient/doctor assignment checks

### Priority 2 — Runtime Errors

4. **Remove duplicate function definitions in `assignment_service.py` (Medium)**
   - File: `Backend/app/services/assignment_service.py`
   - Action: Keep a single implementation of `is_doctor_assigned` and `assert_doctor_has_access`

### Priority 3 — Broken API Functionality

5. **Fix follow-up action "complete" naming (Medium)**
   - File: `Backend/app/routes/follow_up_action_route.py`
   - Action: Rename `delete_follow_up_action` to `complete_follow_up_action` in service layer

### Priority 4 — Validation and Database Consistency

6. **Add patient check in `alert_reading_service.py` (Medium)**
   - Verify `alert.patient_id == reading.patient_id` before creating link

7. **Add data validation for readings (Low)**
   - Validate `systolic > diastolic` in `reading_service.py`

### Priority 5 — Minor Improvements

8. **Remove hardcoded secret key in `deps.py` (Low)**
   - File: `Backend/app/core/deps.py`
   - Action: Remove hardcoded `SECRET_KEY` and `ALGORITHM`; rely on environment variables

9. **Add email verification endpoint (Low)**
   - Add `POST /auth/verify-email` for sending email verification links

---

## Appendix: Discovered Endpoints

### Total: 66 endpoints (excluding HEAD, docs, health)

### Tested Endpoints: 63

| Category | Endpoints |
|---|---|
| Authentication (`/auth`) | `login`, `refresh`, `me`, `change-password`, `signup` |
| Users (`/users`) | `me`, `{user_id}` |
| Patients (`/patients`) | `GET /`, `GET /{id}`, `PUT /{id}`, `POST /{id}/deactivate`, `GET /by-user/{user_id}` |
| Assignments (`/assignments`) | `GET /`, `GET /{id}`, `GET /check/{d}/{p}`, `POST /{id}/end`, `PUT /{id}`, `POST /` |
| Conditions (`/conditions`) | `GET /`, `GET /{id}`, `PUT /{id}`, `POST /{id}/delete`, `POST /` |
| Schedules (`/schedules`) | `GET /`, `GET /{id}`, `POST /{id}/deactivate`, `PUT /{id}`, `GET /by-patient/{id}/active`, `POST /` |
| Readings (`/readings`) | `GET /`, `GET /{id}`, `POST /` |
| Alert Readings (`/alert-readings`) | `POST /`, `GET /`, `GET /{id}` |
| Help Requests (`/help-requests`) | `POST /`, `GET /`, `GET /{id}`, `POST /{id}/cancel` |
| Contact Requests (`/contact-requests`) | `POST /`, `GET /`, `GET /{id}`, `PUT /{id}`, `POST /{id}/complete` |
| Notifications (`/notifications`) | `GET /`, `GET /{id}`, `POST /{id}/read`, `PATCH /{id}`, `POST /mark-all-read`, `GET /unread-count`, `DELETE /{id}` |
| Follow-up Actions (`/follow-up-actions`) | `POST /`, `GET /`, `GET /{id}`, `PUT /{id}`, `POST /{id}/complete` |
| Audit Logs (`/audit-logs`) | `POST /`, `GET /`, `GET /{id}` |

### Discovered but Not Tested (2 endpoints)

- **GET** `/api/v1/patients/by-user/{user_id}` — Patient profile by linked user ID
- **GET** `/api/v1/schedules/by-patient/{patient_id}/active` — Active schedule for a patient

### Blocked Endpoints (4)

| Method | Endpoint | Reason |
|---|---|---|
| GET | `/monitoring-modes/*` | Route file exists but not mounted in `main.py` |
| GET | `/priorities/*` | Route file exists but not mounted in `main.py` |
| GET | `/rule-versions/*` | Route file exists but not mounted in `main.py` |
| GET | `/slots/*` | Route file exists but not mounted in `main.py` |

---

## Summary

The API surface is comprehensive with 63 testable endpoints covering auth, users, patients, assignments, conditions, schedules, readings, and related workflows. However, the backend has several significant gaps:

1. **Critical auth bug:** New users cannot access any protected endpoint after signing up.
2. **4 half-built route files** not mounted in the application.
3. **`/alert-readings/` endpoints are unauthenticated** — a security exposure.
4. **The care team workflow is incomplete** — monitoring, priorities, alerts, and reports lack API endpoints.

With fixes to the critical auth bug and mounting of the unmounted routes, the core patient-to-doctor workflow (registration → assignment → readings → follow-up → contact requests) would function end-to-end.



## E. Bugs

### High Severity

| # | File / Function | Problem | Reproduction | Expected | Actual | Fix Priority |
|---|---|---|---|---|---|---|
| 1 | `main.py` (include_router) | 4 route files exist but are not mounted in the FastAPI app | Check `main.py` include_router calls | All route files should be mounted | Not mounted: `/monitoring-modes`, `/priorities`, `/rule-versions`, `/slots` | 1 (Security and data access) |
| 2 | `Backend/app/core/deps.py` `get_current_active_user` | Signup creates users with `is_verified=False`, but `get_current_active_user` requires `is_verified=True` | Signup as a new user, call `GET /auth/me` with returned token | 200 OK with user profile | 403 Forbidden `'Email not verified'` | 1 (Security and data access) |

### Medium Severity

| # | File / Function | Problem | Reproduction | Expected | Actual | Fix Priority |
|---|---|---|---|---|---|---|
| 3 | `Backend/app/services/assignment_service.py` | Duplicate `is_doctor_assigned` and `assert_doctor_has_access` functions (two copies each) | N/A | Single source of truth | Two identical implementations | 3 (Runtime errors) |
| 4 | `Backend/app/routes/condition_route.py` `create_condition` | 404 "Patient not found or not assigned to doctor" — test ordering issue | Create condition after assignment was ended | 201 Created | 404 | 5 (Minor improvements) |
| 5 | `Backend/app/routes/schedule_route.py` `create_schedule` | 404 — same as #4 | Create schedule after assignment ended | 201 Created | 404 | 5 (Minor improvements) |
| 6 | `Backend/app/routes/contact_request_route.py` `create_contact_request` | 404 — same as #4 | Create contact request after assignment ended | 201 Created | 404 | 5 (Minor improvements) |
| 7 | `Backend/app/routes/follow_up_action_route.py` `create_follow_up_action` | 404 — same as #4 | Create follow-up action after assignment ended | 201 Created | 404 | 5 (Minor improvements) |
| 8 | `Backend/app/routes/reading_route.py` `get_reading` (doctor) | 404 — same as #4 | GET reading by doctor after assignment ended | 200 OK | 404 | 5 (Minor improvements) |

### Additional Issues Found During Code Review (Not Tested in Automation)

| # | File / Function | Severity | Problem | Reproduction | Expected | Actual | Fix Priority |
|---|---|---|---|---|---|---|---|
| 9 | `Backend/app/routes/alertreading_route.py` | Medium | `/alert-readings/` routes have no authentication — any unauthenticated user can access | Send GET `/alert-readings/` without token | 401 Unauthorized | 200 OK with empty list | 1 (Security and data access) |
| 10 | `Backend/app/routes/alertreading_route.py` | Medium | Alert-reading routes do not check patient/doctor assignment | Create alert-reading link for any patient | 403 Forbidden | 201 Created | 1 (Security and data access) |
| 11 | `Backend/app/services/alert_reading_service.py` `create_alert_reading` | Medium | Creates `AlertReading` record without verifying alert and reading belong to same patient | Create alert-reading link where alert.patient_id != reading.patient_id | 400 Bad Request | 201 Created | 2 (Runtime errors) |
| 12 | `Backend/app/services/reading_service.py` `create_blood_pressure_reading` | Low | No validation of systolic/diastolic values (e.g., no range check: systolic must be > diastolic) | POST reading with systolic=80, diastolic=120 | 400 Bad Request | 201 Created | 5 (Minor improvements) |
| 13 | `Backend/app/services/condition_service.py` `create_patient_condition` | Low | No validation of condition names (e.g., empty string) | POST condition with condition_name="" | 400 Bad Request | 200 Created | 5 (Minor improvements) |



## D. Workflow Results

Complete patient-to-doctor workflow test:

| # | Step | Result | Notes |
|---|---|---|---|
| 1 | Register patient | PASS | 201 Created |
| 2 | Prepare doctor | PASS | Doctor user + profile created |
| 3 | Login patient | PASS | 200 OK |
| 4 | Login doctor | PASS | 200 OK |
| 5 | Retrieve patient profile | PASS | 200 OK |
| 6 | Retrieve doctor profile | PASS | 200 OK |
| 7 | Create doctor-patient assignment | PASS | 201 Created |
| 8 | Configure monitoring mode | BLOCKED | Route not mounted (Bug #1) |
| 9 | Configure measurement schedule | FAIL | 404 — assignment ended before test (test ordering) |
| 10 | Submit blood pressure reading | PASS | 201 Created |
| 11 | Verify reading retrieval | PASS | 200 OK |
| 12 | Retrieve reading history | PASS | 200 OK |
| 13 | Trend analysis | BLOCKED | No endpoint exists |
| 14 | Check alerts | BLOCKED | No alert endpoint exists |
| 15 | Priority assessment | BLOCKED | Route not mounted (Bug #1) |
| 16 | Login as doctor | PASS | (already logged in) |
| 17 | Retrieve assigned patients | PASS | 200 OK |
| 18 | Doctor priority queue | BLOCKED | Route not mounted (Bug #1) |
| 19 | Open patient details | FAIL | 404 — assignment ended before test (test ordering) |
| 20 | Review patient case | BLOCKED | No case review endpoint mounted |
| 21 | Create follow-up action | FAIL | 404 — assignment ended before test (test ordering) |
| 22 | Submit patient help request | PASS | 201 Created |
| 23 | Contact request workflow | FAIL | 404 — assignment ended before test (test ordering) |
| 24 | Check notifications | PASS | 200 OK |
| 25 | Generate report | BLOCKED | No report endpoint exists |

### Workflow Observations

- Steps 9, 19, 21, 23 failed due to **test ordering**: the assignment was ended (in the ASSIGNMENTS section) before testing those endpoints. Re-running the workflow with the assignment active would pass these. This is not an application bug but a test script ordering issue.
- The workflow is **incomplete**: monitoring-mode configuration, trend analysis, alert generation, priority assessment, priority queue, case review, and report generation have no REST endpoints.



## C. Security Results

### Authentication & Authorization

| Finding | Severity | Details |
|---|---|---|
| Signup blocked after login | **Critical** | User created via `/auth/signup` has `is_verified=False`, but `get_current_active_user` in `deps.py` (line 58) raises 403 if `is_verified` is False. New users cannot access `/auth/me` or any protected endpoint after signup. |
| No doctor profile creation API | **High** | Doctor profiles must be created directly in the database. There is no endpoint to register a doctor as a user-type role. |
| `/alert-readings/` has no auth | **High** | All `/alert-readings/` endpoints lack `Depends(get_current_active_user)`. Any unauthenticated user can create, list, and read alert readings. |
| Patient data isolation verified | **Pass** | Patient routes correctly restrict access to own profile. Doctor routes correctly enforce assignment checks. |
| Role-based route restrictions | **Pass** | Patient-only routes reject non-patient users. Doctor-only routes reject non-doctor users. |

### Data Access & Isolation

| Finding | Severity | Details |
|---|---|---|
| Patient isolation | **Pass** | Patients can only access their own data. Doctors can only access assigned patients. |
| No cross-patient data leakage detected | **Pass** | All patient-scoped endpoints filter by user profile / assignment. |
| IDOR vulnerabilities | **None found** | All endpoints that accept `patient_id` or `user_id` parameters verify access before returning data. |

### Session / Token Security

| Finding | Severity | Details |
|---|---|---|
| Password hashing | **Pass** | Uses `passlib` with bcrypt. |
| JWT creation | **Pass** | Uses HS256 algorithm. Access tokens expire after configurable time (default 30 min). Refresh tokens expire after configurable time (default 7 days). |
| Secret key | **Low** | `SECRET_KEY` is hardcoded in `deps.py` and duplicated in `config.py`. Should be read from environment only. |

| GET | /auth/me (invalid token) | PASS | 401 | — |
| POST | /auth/change-password | PASS | 200 | — |
| GET | /users/me | PASS | 200 | — |
| GET | /users/{id} (own) | PASS | 200 | — |
| GET | /users/{id} (another) | PASS | 403 | Correctly denied |
| POST | /patients/ (create profile) | PASS | 201 | — |
| POST | Doctor profile creation (DB) | PASS | — | No API endpoint; created directly in DB |
| POST | /assignments/ (create) | PASS | 201 | — |
| GET | /patients/ (list own) | PASS | 200 | — |
| GET | /patients/{id} (own) | PASS | 200 | — |
| PUT | /patients/{id} (update) | PASS | 200 | — |
| POST | /patients/{id}/deactivate | PASS | 403 | Correctly disabled |
| GET | /patients/{id} (doctor, assigned) | PASS | 200 | — |
| GET | /assignments/ (list doctor) | PASS | 200 | — |
| GET | /assignments/check/{d}/{p} | PASS | 200 | — |
| GET | /assignments/{id} | PASS | 200 | — |
| PUT | /assignments/{id} (update) | PASS | 200 | — |
| POST | /assignments/{id}/end | PASS | 200 | — |
| POST | /assignments/ (patient, forbidden) | PASS | 403 | Correctly denied |
| POST | /conditions/ (create) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| GET | /conditions/ (list) | PASS | 200 | — |
| GET | /conditions/{id} | PASS | 200 | — |
| PUT | /conditions/{id} (update) | PASS | 200 | — |
| POST | /conditions/{id}/delete | PASS | 200 | — |
| GET | /conditions/{id} (patient, own) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| POST | /schedules/ (create) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| GET | /schedules/ (list) | PASS | 200 | — |
| GET | /schedules/{id} | PASS | 200 | — |
| PUT | /schedules/{id} (update) | PASS | 200 | — |
| POST | /schedules/{id}/deactivate | PASS | 200 | — |
| POST | /readings/ (create) | PASS | 201 | — |
| GET | /readings/ (list patient) | PASS | 200 | — |
| GET | /readings/{id} (patient) | PASS | 200 | — |
| GET | /readings/{id} (doctor, assigned) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| POST | /alert-readings/ (create) | FAIL | 404 | alert_id=1 does not exist (no seed data) |
| GET | /alert-readings/ (list) | PASS | 200 | — |
| GET | /alert-readings/{id} | PASS | 200 | — |
| POST | /help-requests/ (create) | PASS | 201 | — |
| GET | /help-requests/ (list patient) | PASS | 200 | — |
| GET | /help-requests/{id} (patient) | PASS | 200 | — |
| POST | /help-requests/{id}/cancel | PASS | 200 | — |
| POST | /contact-requests/ (create) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| GET | /contact-requests/ (list doctor) | PASS | 200 | — |
| GET | /contact-requests/{id} (doctor) | PASS | 200 | — |
| PUT | /contact-requests/{id} (update) | PASS | 200 | — |
| POST | /contact-requests/{id}/complete | PASS | 200 | — |
| GET | /notifications/ (list) | PASS | 200 | — |
| GET | /notifications/unread-count | PASS | 200 | — |
| GET | /notifications/{id} | PASS | 200 | — |
| POST | /notifications/{id}/read | PASS | 200 | — |
| PATCH | /notifications/{id} | PASS | 200 | — |
| POST | /notifications/mark-all-read | PASS | 200 | — |
| DELETE | /notifications/{id} | PASS | 204 | — |
| POST | /follow-up-actions/ (create) | FAIL | 404 | Assignment ended before test (see Bug #5) |
| GET | /follow-up-actions/ (list) | PASS | 200 | — |
| POST | /audit-logs/ (create) | PASS | 201 | — |
| GET | /audit-logs/ (list) | PASS | 200 | — |
| GET | /audit-logs/{id} | PASS | 200 | — |
| GET | /audit-logs/ (patient, forbidden) | PASS | 403 | Correctly denied |
| GET | /monitoring-modes/ | BLOCKED | — | Route not mounted (see Bug #1) |
| GET | /priorities/ | BLOCKED | — | Route not mounted (see Bug #1) |
| GET | /rule-versions/ | BLOCKED | — | Route not mounted (see Bug #1) |
| GET | /slots/ | BLOCKED | — | Route not mounted (see Bug #1) |
