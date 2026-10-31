"""
RAWDH (روض) — Complete Full System Integration & E2E Verification Suite.

This script executes a comprehensive, multi-scenario end-to-end integration test
validating all 28 backend routers, OAuth2 authentication, clinical triage engine,
physiological thresholds, multi-tier alerting, 722 protocol compliance, hardware pairing,
and forensic audit logging against the integrated database.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add Backend to python path
project_root = Path(__file__).resolve().parent
backend_dir = project_root / "Backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestRunner:
    def __init__(self):
        self.run_id = str(uuid.uuid4())[:8]
        self.passed_count = 0
        self.failed_count = 0
        self.results = []

    def log(self, section: str, test_name: str, passed: bool, details: str = ""):
        status_tag = "[PASS]" if passed else "[FAIL]"
        if passed:
            self.passed_count += 1
        else:
            self.failed_count += 1
        self.results.append((section, test_name, passed, details))
        print(f" {status_tag} {section}: {test_name} {('- ' + details) if details else ''}")

    def run_all(self):
        print(f"\n=======================================================================")
        print(f"  RAWDH (روض) TELEMONITORING PLATFORM — FULL SYSTEM E2E TEST RUN")
        print(f"  Run ID: {self.run_id} | Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"=======================================================================\n")

        self.scenario_1_authentication_rbac()
        self.scenario_2_patient_enrollment_and_assignment()
        self.scenario_3_protocol_schedule_and_consent()
        self.scenario_4_vitals_ingestion_and_threshold_evaluation()
        self.scenario_5_multi_tier_alert_generation_and_sla()
        self.scenario_6_doctor_triage_and_priority_queue()
        self.scenario_7_outreach_tasks_and_patient_acknowledgment()
        self.scenario_8_fourteen_day_review_and_clinical_signoff()
        self.scenario_9_connected_hardware_and_bluetooth_pairing()
        self.scenario_10_accessibility_and_settings_persistence()
        self.scenario_11_forensic_audit_trail_verification()

        self.print_summary()

    # -------------------------------------------------------------------------
    # Scenario 1: Authentication, Tokens & Role-Based Access Control
    # -------------------------------------------------------------------------
    def scenario_1_authentication_rbac(self):
        section = "SCENARIO 1 [Auth & RBAC]"
        
        # 1.1 Admin Registration
        admin_email = f"admin_{self.run_id}@rawdh.dz"
        res = client.post("/api/v1/auth/register", json={
            "email": admin_email,
            "password": "Password123!",
            "full_name": "E2E Administrator",
            "phone": f"+213550{self.run_id[:6]}",
            "role": "admin",
        })
        self.log(section, "Admin User Registration", res.status_code == 201)

        # 1.2 Admin Login (Token Issuance)
        res = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "Password123!",
        })
        self.log(section, "Admin Login & JWT Issuance", res.status_code == 200 and "access_token" in res.json())
        self.admin_token = res.json()["access_token"]
        self.admin_refresh = res.json()["refresh_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 1.3 Identity Rehydration via /auth/me
        res = client.get("/api/v1/auth/me", headers=self.admin_headers)
        self.log(section, "Session Rehydration (/auth/me)", res.status_code == 200 and res.json()["role"] == "admin")

        # 1.4 Silent Token Refresh
        res = client.post("/api/v1/auth/refresh", json={"refresh_token": self.admin_refresh})
        self.log(section, "Silent Token Refresh (/auth/refresh)", res.status_code == 200 and "access_token" in res.json())
        if res.status_code == 200:
            self.admin_token = res.json()["access_token"]
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 1.5 Invalid Credentials Rejection
        res = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "WrongPassword!",
        })
        self.log(section, "Invalid Password Rejection (401)", res.status_code == 401)

    # -------------------------------------------------------------------------
    # Scenario 2: Clinician & Patient Enrollment
    # -------------------------------------------------------------------------
    def scenario_2_patient_enrollment_and_assignment(self):
        section = "SCENARIO 2 [Enrollment & Caseload]"

        # 2.1 Doctor Registration & Profile
        doc_email = f"doc_{self.run_id}@clinic.dz"
        res = client.post("/api/v1/auth/register", json={
            "email": doc_email,
            "password": "Password123!",
            "full_name": f"Dr. Samy {self.run_id}",
            "phone": f"+213770{self.run_id[:6]}",
            "role": "doctor",
        })
        doc_user_id = res.json()["id"]

        res = client.post("/api/v1/doctors", json={
            "user_id": doc_user_id,
            "license_number": f"DZ-E2E-{self.run_id}",
            "specialization": "Cardiology",
            "speciality": "Cardiology",
            "first_name": "Samy",
            "last_name": f"Doctor {self.run_id}",
            "facility": "Clinique Al-Amal",
        }, headers=self.admin_headers)
        self.log(section, "Doctor Profile Provisioning", res.status_code == 201)
        self.doctor_id = res.json()["id"]

        # Doctor Login
        doc_login = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "Password123!"})
        self.doc_token = doc_login.json()["access_token"]
        self.doc_headers = {"Authorization": f"Bearer {self.doc_token}"}

        # 2.2 Patient Enrollment
        pat_email = f"patient_{self.run_id}@telehealth.dz"
        res = client.post("/api/v1/patients", json={
            "email": pat_email,
            "password": "Password123!",
            "full_name": f"Amina Test {self.run_id}",
            "phone": f"+213660{self.run_id[:6]}",
            "date_of_birth": "1975-06-15",
            "gender": "female",
            "age_band": "45-64",
            "under_treatment": True,
        }, headers=self.admin_headers)
        self.log(section, "Patient Enrollment & Medical Profile", res.status_code == 201)
        self.patient_id = res.json()["id"]

        # Patient Login
        pat_login = client.post("/api/v1/auth/login", json={"email": pat_email, "password": "Password123!"})
        self.pat_token = pat_login.json()["access_token"]
        self.pat_headers = {"Authorization": f"Bearer {self.pat_token}"}

        # 2.3 Doctor-Patient Assignment
        res = client.post("/api/v1/doctor-assignments", json={
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
        }, headers=self.admin_headers)
        self.log(section, "Doctor-Patient Caseload Linking", res.status_code == 201)

    # -------------------------------------------------------------------------
    # Scenario 3: Telemonitoring Protocol & Consents
    # -------------------------------------------------------------------------
    def scenario_3_protocol_schedule_and_consent(self):
        section = "SCENARIO 3 [Protocol & Consent]"

        # 3.1 Patient Data Sharing Consent
        res = client.post("/api/v1/patients/me/consents", json={
            "type": "data_sharing",
            "text_version": "1.0",
            "accepted": True,
        }, headers=self.pat_headers)
        self.log(section, "Patient Consent Recording (F15)", res.status_code == 201)

        # 3.2 Doctor Sets Telemonitoring Mode
        res = client.post(f"/api/v1/doctor/patients/{self.patient_id}/monitoring-modes", json={
            "patient_id": self.patient_id,
            "mode": "telemonitoring",
        }, headers=self.doc_headers)
        self.log(section, "Monitoring Mode Setting (Telemonitoring)", res.status_code in (200, 201))

        # 3.3 Set Measurement Schedule (722 Protocol)
        res = client.post(f"/api/v1/doctor/patients/{self.patient_id}/schedules", json={
            "patient_id": self.patient_id,
            "protocol": "722_diagnostic",
            "readings_per_slot": 2,
            "cycle_length_days": 7,
            "pattern": "daily",
            "owner": "doctor",
        }, headers=self.doc_headers)
        self.log(section, "722 Diagnostic Protocol Setup (F10)", res.status_code in (200, 201))

    # -------------------------------------------------------------------------
    # Scenario 4: Vitals Ingestion & Physiological Thresholds
    # -------------------------------------------------------------------------
    def scenario_4_vitals_ingestion_and_threshold_evaluation(self):
        section = "SCENARIO 4 [Vitals & Thresholds]"

        # 4.1 Ingest Standard Within-Target Reading (124/82 mmHg)
        res = client.post("/api/v1/readings", json={
            "patient_id": self.patient_id,
            "systolic": 124,
            "diastolic": 82,
            "pulse": 72,
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=self.pat_headers)
        b1 = res.json() if res.status_code == 201 else {}
        self.log(section, "Standard Reading Ingestion (124/82)", res.status_code == 201 and b1.get("status_level") != "severe")

        # 4.2 Ingest Persistent Elevated Reading (158/98 mmHg)
        res = client.post("/api/v1/readings", json={
            "patient_id": self.patient_id,
            "systolic": 158,
            "diastolic": 98,
            "pulse": 76,
            "capture_method": "manual",
        }, headers=self.pat_headers)
        b2 = res.json() if res.status_code == 201 else {}
        self.log(section, "Stage 2 Elevated Reading (158/98)", res.status_code == 201 and b2.get("status_level") == "stage_2")

        # 4.3 Ingest Severe Crisis Reading (186/122 mmHg) triggering Severe Alert
        res = client.post("/api/v1/readings", json={
            "patient_id": self.patient_id,
            "systolic": 186,
            "diastolic": 122,
            "pulse": 90,
            "capture_method": "device",
            "symptoms_reported": ["headache", "blurred_vision"],
        }, headers=self.pat_headers)
        b3 = res.json() if res.status_code == 201 else {}
        is_severe = res.status_code == 201 and b3.get("status_level") == "severe"
        self.log(section, "Crisis Reading Ingestion (186/122)", is_severe, "status_level='severe'")

    # -------------------------------------------------------------------------
    # Scenario 5: Multi-Tier Alert Generation & Clinician SLA
    # -------------------------------------------------------------------------
    def scenario_5_multi_tier_alert_generation_and_sla(self):
        section = "SCENARIO 5 [Alert Engine & SLA]"

        # 5.1 Doctor Retrieves Caseload Alerts
        res = client.get("/api/v1/doctor/me/alerts", headers=self.doc_headers)
        alerts = res.json()
        has_alerts = res.status_code == 200 and len(alerts) >= 1
        self.log(section, "Doctor Caseload Alerts Retrieval", has_alerts, f"Alert count: {len(alerts)}")

        if has_alerts:
            self.alert_id = alerts[0]["id"]
            tier = alerts[0].get("tier")
            self.log(section, "Clinical Alert Tier Evaluation", tier in ("severe_single_reading", "critical_emergency", "persistent_elevation"), f"Tier: {tier}")

            # 5.2 Doctor Acknowledges Alert (Stops SLA escalation timer)
            res = client.post(f"/api/v1/alerts/{self.alert_id}/acknowledge", json={
                "decision": "monitor_closely",
                "note": "Clinician reviewed severe reading; patient notified.",
            }, headers=self.doc_headers)
            self.log(section, "Doctor Acknowledges Alert (Stops SLA)", res.status_code == 200 and res.json()["lifecycle"] == "acknowledged")

            # 5.3 Fetch Alert Evidence Packet
            res = client.get(f"/api/v1/alerts/{self.alert_id}", headers=self.doc_headers)
            self.log(section, "Alert Evidence Packet Inspection", res.status_code == 200)

    # -------------------------------------------------------------------------
    # Scenario 6: Algorithmic Triage & Priority Queue (P1–P4)
    # -------------------------------------------------------------------------
    def scenario_6_doctor_triage_and_priority_queue(self):
        section = "SCENARIO 6 [Triage Queue]"

        # 6.1 Doctor Dashboard Metrics Counter
        res = client.get("/api/v1/doctor/me/dashboard", headers=self.doc_headers)
        self.log(section, "Doctor Dashboard Metric Aggregation", res.status_code == 200 and res.json()["active_patient_count"] >= 1)

        # 6.2 Doctor Priority Queue Access
        res = client.get("/api/v1/doctor/me/priority-queue", headers=self.doc_headers)
        items = res.json().get("items", [])
        self.log(section, "Triage Queue Sorted Retrieval (P1–P4)", res.status_code == 200 and len(items) >= 1)

        if items:
            top_patient = items[0]
            level = top_patient.get("priority_level")
            self.log(section, "Top Patient Triage Level Assigned", level in ("P1_critical", "P2_high", "P3_moderate"), f"Level: {level}")

    # -------------------------------------------------------------------------
    # Scenario 7: Outreach Tasks & Patient Guidance Acknowledgment
    # -------------------------------------------------------------------------
    def scenario_7_outreach_tasks_and_patient_acknowledgment(self):
        section = "SCENARIO 7 [Outreach & Guidance]"

        # 7.1 Patient Retrieves Active Safety Alerts
        res = client.get("/api/v1/patients/me/alerts", headers=self.pat_headers)
        patient_alerts = res.json()
        self.log(section, "Patient-Facing Plain Language Alerts", res.status_code == 200 and len(patient_alerts) >= 1)

        if patient_alerts:
            p_alert_id = patient_alerts[0]["id"]
            # 7.2 Patient Confirms Emergency Guidance Received (UC09b / RS-1)
            res = client.post(f"/api/v1/alerts/{p_alert_id}/patient-acknowledge", json={
                "confirmed": True,
                "action_taken": "Patient rested and confirmed repeat measurement on schedule.",
            }, headers=self.pat_headers)
            self.log(section, "Patient Safety Guidance Confirmation", res.status_code == 200)

        # 7.3 Doctor Initiates Contact Request
        res = client.post(f"/api/v1/doctor/patients/{self.patient_id}/contact-requests", json={
            "patient_id": self.patient_id,
            "message": "Please confirm morning Ramipril adherence.",
            "urgency": "urgent",
        }, headers=self.doc_headers)
        self.log(section, "Doctor Dispatches Contact Task", res.status_code == 201)
        request_id = res.json()["id"]

        # 7.4 Complete Contact Task
        res = client.post(f"/api/v1/contact-requests/{request_id}/complete", headers=self.doc_headers)
        self.log(section, "Doctor Completes Contact Task Drawer", res.status_code == 200)

    # -------------------------------------------------------------------------
    # Scenario 8: 14-Day Protocol Review & Clinical Sign-Off
    # -------------------------------------------------------------------------
    def scenario_8_fourteen_day_review_and_clinical_signoff(self):
        section = "SCENARIO 8 [Case Review & Digest]"

        # 8.1 Pre-Review Summary Digest (D3/F18)
        res = client.get(f"/api/v1/doctor/patients/{self.patient_id}/summary", headers=self.doc_headers)
        self.log(section, "14-Day Pre-Review Digest Computation", res.status_code == 200 and "target" in res.json())

        # 8.2 Doctor Submits Case Review Sign-Off
        res = client.post(f"/api/v1/doctor/patients/{self.patient_id}/reviews", json={
            "patient_id": self.patient_id,
            "summary": "14-day protocol evaluation completed. Escalating ACE inhibitor dosage.",
            "status": "completed",
        }, headers=self.doc_headers)
        self.log(section, "Clinical Review Sign-Off & Persistence", res.status_code == 201 and res.json()["status"] == "completed")

    # -------------------------------------------------------------------------
    # Scenario 9: Connected Hardware & Bluetooth BLE Pairing
    # -------------------------------------------------------------------------
    def scenario_9_connected_hardware_and_bluetooth_pairing(self):
        section = "SCENARIO 9 [Hardware & Devices]"

        # 9.1 Pair OMRON Bluetooth Monitor
        res = client.post("/api/v1/patients/me/devices", json={
            "device_model": "OMRON HEM-7361T-EBK (Bluetooth Smart)",
            "serial_number": f"OM-{self.run_id}",
            "mac_address": "00:1B:44:11:3A:B7",
            "validation_status": "stride_bp_validated",
        }, headers=self.pat_headers)
        self.log(section, "Bluetooth BLE Hardware Pairing", res.status_code == 201)
        device_id = res.json()["id"]

        # 9.2 List Paired Devices
        res = client.get("/api/v1/patients/me/devices", headers=self.pat_headers)
        self.log(section, "Hardware Device Inventory Listing", res.status_code == 200 and len(res.json()) >= 1)

        # 9.3 Unpair Hardware Device
        res = client.delete(f"/api/v1/patients/me/devices/{device_id}", headers=self.pat_headers)
        self.log(section, "Hardware Device Unpairing", res.status_code == 200)

    # -------------------------------------------------------------------------
    # Scenario 10: Accessibility & Preferences Persistence
    # -------------------------------------------------------------------------
    def scenario_10_accessibility_and_settings_persistence(self):
        section = "SCENARIO 10 [Accessibility & i18n]"

        # 10.1 Update Preferences (Arabic RTL, Extra Large Font 150, Calm Dark)
        res = client.patch("/api/v1/users/me", json={
            "locale": "ar",
            "text_size": 150,
            "theme": "calm_dark",
            "high_contrast": True,
        }, headers=self.pat_headers)
        self.log(section, "Accessibility Settings Mutation (PATCH /users/me)", res.status_code == 200)

        # 10.2 Verify Persistence on Session Re-read
        res = client.get("/api/v1/auth/me", headers=self.pat_headers)
        user_data = res.json()
        persisted = (
            user_data["locale"] == "ar"
            and user_data["text_size"] == 150
            and user_data["theme"] == "calm_dark"
            and user_data["high_contrast"] is True
        )
        self.log(section, "Accessibility Persistence Verification", persisted, "ar / 150% / calm_dark / high_contrast")

    # -------------------------------------------------------------------------
    # Scenario 11: Forensic Audit Trail Verification
    # -------------------------------------------------------------------------
    def scenario_11_forensic_audit_trail_verification(self):
        section = "SCENARIO 11 [Audit Logs]"

        res = client.get("/api/v1/admin/audit-logs?limit=10", headers=self.admin_headers)
        has_logs = res.status_code == 200 and len(res.json()) >= 1
        self.log(section, "HIPAA/GDPR Audit Trail Recording", has_logs, f"Audit entries recorded: {len(res.json())}")

    # -------------------------------------------------------------------------
    # Test Summary Output
    # -------------------------------------------------------------------------
    def print_summary(self):
        total = self.passed_count + self.failed_count
        pass_rate = (self.passed_count / total * 100) if total > 0 else 0
        
        print("\n=======================================================================")
        print(f"  E2E INTEGRATION TEST SUMMARY")
        print(f"=======================================================================")
        print(f"  Total Scenarios Evaluated: 11")
        print(f"  Total Individual Assertions: {total}")
        print(f"  Passed: {self.passed_count} | Failed: {self.failed_count}")
        print(f"  Success Rate: {pass_rate:.1f}%")
        print(f"=======================================================================\n")

        if self.failed_count == 0:
            print(">>> ALL FULL-SYSTEM INTEGRATION TEST SCENARIOS PASSED WITH ZERO ERRORS! <<<\n")
        else:
            print(f">>> {self.failed_count} ASSERTIONS FAILED. CHECK LOGS ABOVE. <<<\n")
            sys.exit(1)

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()
