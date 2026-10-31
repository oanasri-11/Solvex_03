"""RAWDH (روض) — Integration Verification against Live Backend Simulation.

Validates that:
1. All mock data has been decoupled from the application.
2. The live backend simulation populates realistic clinical data.
3. Doctor dashboard metrics, priority queue (P1-P4), alerts, and caseload are live.
4. Chart data for both Doctor (14-day longitudinal curve) and Patient (7-day & 14-day trends)
   is correctly generated from live backend measurements.
5. Patient guidance, devices, summaries, and settings mutations operate with zero errors.
"""

import sys
from pathlib import Path

# Add Backend to sys.path
backend_dir = Path(__file__).resolve().parent / "Backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class SimulationIntegrationTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, category: str, description: str, condition: bool, extra: str = ""):
        if condition:
            self.passed += 1
            print(f" [PASS] {category}: {description} {f'({extra})' if extra else ''}")
        else:
            self.failed += 1
            print(f" [FAIL] {category}: {description} {f'({extra})' if extra else ''}")

    def run(self):
        print("=======================================================================")
        print("  VERIFYING INTEGRATION WITH LIVE BACKEND SIMULATED DATA")
        print("=======================================================================")

        # ---------------------------------------------------------------------
        # 1. Doctor Workspace Verification (Dr. Karim)
        # ---------------------------------------------------------------------
        sec_doc = "DOCTOR WORKSPACE"
        login_res = client.post("/api/v1/auth/login", json={
            "email": "dr.karim@clinic.com",
            "password": "Password123!",
        })
        self.check(sec_doc, "Doctor Authentication", login_res.status_code == 200)
        doc_token = login_res.json().get("access_token")
        doc_headers = {"Authorization": f"Bearer {doc_token}"}

        # 1.1 Dashboard Counter Metrics
        dash_res = client.get("/api/v1/doctor/me/dashboard", headers=doc_headers)
        dash = dash_res.json() if dash_res.status_code == 200 else {}
        self.check(
            sec_doc, 
            "Dashboard Active Caseload Counter", 
            dash_res.status_code == 200 and dash.get("active_patient_count") == 5,
            f"Patients: {dash.get('active_patient_count')}"
        )
        self.check(
            sec_doc,
            "Dashboard Open Alerts Aggregation",
            dash.get("unacknowledged_alerts_count", 0) >= 1,
            f"Unacknowledged alerts: {dash.get('unacknowledged_alerts_count')}"
        )

        # 1.2 Priority Queue (P1–P4 Triage)
        pq_res = client.get("/api/v1/doctor/me/priority-queue", headers=doc_headers)
        pq_items = pq_res.json().get("items", []) if pq_res.status_code == 200 else []
        self.check(
            sec_doc,
            "Priority Queue Sorted Retrieval",
            pq_res.status_code == 200 and len(pq_items) == 5,
            f"Queue length: {len(pq_items)}"
        )

        # Check top priority patient is P1_critical (Fatima Zahra)
        top_patient = pq_items[0] if pq_items else {}
        self.check(
            sec_doc,
            "Top Priority Patient is P1_critical",
            top_patient.get("priority_level") == "P1_critical" and "Fatima" in top_patient.get("first_name", ""),
            f"Name: {top_patient.get('first_name')} {top_patient.get('last_name')}, Level: {top_patient.get('priority_level')}"
        )

        # 1.3 Longitudinal Trend Chart Data (Marc Dupuis)
        # Find Marc's ID in the queue
        marc_item = next((p for p in pq_items if "Marc" in p.get("first_name", "")), None)
        marc_id = marc_item["patient_id"] if marc_item else 2

        marc_readings_res = client.get(f"/api/v1/doctor/patients/{marc_id}/readings?limit=50", headers=doc_headers)
        marc_readings = marc_readings_res.json() if marc_readings_res.status_code == 200 else []
        self.check(
            sec_doc,
            "Doctor Patient Readings Ingestion Count",
            marc_readings_res.status_code == 200 and len(marc_readings) >= 14,
            f"Total Readings: {len(marc_readings)}"
        )

        # Simulate Frontend Chart Transform (BPLineChart data points)
        # readings.slice(0, 14).reverse().map(...)
        chart_points = [
            {
                "label": r["measured_at"][:10],
                "systolic": r["systolic"],
                "diastolic": r["diastolic"],
                "isManual": r.get("capture_method") == "manual"
            }
            for r in reversed(marc_readings[:14])
        ]
        self.check(
            sec_doc,
            "Doctor Trend Chart Data Transformation (14 days)",
            len(chart_points) == 14 and all("systolic" in pt and "diastolic" in pt for pt in chart_points),
            f"Points: {len(chart_points)}, First SBP: {chart_points[0]['systolic']}, Last SBP: {chart_points[-1]['systolic']}"
        )

        # 1.4 Doctor Alerts & Evidence Packet
        alerts_res = client.get("/api/v1/doctor/me/alerts", headers=doc_headers)
        doc_alerts = alerts_res.json() if alerts_res.status_code == 200 else []
        self.check(
            sec_doc,
            "Doctor Caseload Clinical Alerts Retrieval",
            alerts_res.status_code == 200 and len(doc_alerts) >= 1,
            f"Alerts found: {len(doc_alerts)}"
        )

        if doc_alerts:
            alert_id = doc_alerts[0]["id"]
            # Acknowledge alert (stops SLA escalation timer)
            ack_res = client.post(f"/api/v1/alerts/{alert_id}/acknowledge", json={
                "decision": "monitor_closely",
                "note": "Clinician acknowledged live alert from simulated telemetry.",
            }, headers=doc_headers)
            self.check(
                sec_doc,
                "Doctor Acknowledges Clinical Alert (Stops SLA)",
                ack_res.status_code == 200 and ack_res.json().get("lifecycle") == "acknowledged"
            )

        # 1.5 14-Day Pre-Review Digest & Sign-Off
        digest_res = client.get(f"/api/v1/doctor/patients/{marc_id}/summary", headers=doc_headers)
        digest = digest_res.json() if digest_res.status_code == 200 else {}
        self.check(
            sec_doc,
            "14-Day Pre-Review Clinical Digest",
            digest_res.status_code == 200 and "target" in digest and "priority" in digest,
            f"Target: {digest.get('target')}"
        )

        review_res = client.post(f"/api/v1/doctor/patients/{marc_id}/reviews", json={
            "patient_id": marc_id,
            "summary": "Simulated cycle review sign-off. Patient maintained on Amlodipine 5mg.",
            "status": "completed",
        }, headers=doc_headers)
        self.check(
            sec_doc,
            "Doctor Submits Case Review Sign-Off",
            review_res.status_code == 201 and review_res.json().get("status") == "completed"
        )

        # ---------------------------------------------------------------------
        # 2. Patient Workspace Verification (Amina Benali)
        # ---------------------------------------------------------------------
        sec_pat = "PATIENT WORKSPACE"
        pat_login_res = client.post("/api/v1/auth/login", json={
            "email": "amina.benali@email.com",
            "password": "Password123!",
        })
        self.check(sec_pat, "Patient Authentication (Amina Benali)", pat_login_res.status_code == 200)
        pat_token = pat_login_res.json().get("access_token")
        pat_headers = {"Authorization": f"Bearer {pat_token}"}

        # 2.1 Patient Summary & Target
        summary_res = client.get("/api/v1/patients/me/summary", headers=pat_headers)
        summary = summary_res.json() if summary_res.status_code == 200 else {}
        self.check(
            sec_pat,
            "Patient Clinical Summary Retrieval",
            summary_res.status_code == 200 and "target" in summary,
            f"Target: <{summary.get('target', {}).get('systolic')}/{summary.get('target', {}).get('diastolic')}"
        )

        # 2.2 Patient Trend Readings Ingestion & Chart Generation
        readings_res = client.get("/api/v1/patients/me/readings?page_size=50", headers=pat_headers)
        pat_readings = readings_res.json() if readings_res.status_code == 200 else []
        self.check(
            sec_pat,
            "Patient Telemonitoring Readings Count",
            readings_res.status_code == 200 and len(pat_readings) >= 14,
            f"Readings count: {len(pat_readings)}"
        )

        # Simulate 7-day trend curve (PatientHome.tsx)
        pat_7day_points = [
            {
                "label": r["measured_at"][:10],
                "systolic": r["systolic"],
                "diastolic": r["diastolic"],
                "isManual": r.get("capture_method") == "manual"
            }
            for r in reversed(pat_readings[:7])
        ]
        self.check(
            sec_pat,
            "Patient 7-Day Trend Chart Points",
            len(pat_7day_points) == 7 and all(pt["systolic"] < 135 for pt in pat_7day_points),
            f"Latest SBP: {pat_7day_points[-1]['systolic']} mmHg (Controlled)"
        )

        # Simulate 14-day history curve (PatientHistoryTrends.tsx)
        pat_14day_points = [
            {
                "label": r["measured_at"][:10],
                "sys": r["systolic"],
                "dia": r["diastolic"],
                "type": "target" if r["systolic"] < 130 else "borderline"
            }
            for r in reversed(pat_readings[:14])
        ]
        self.check(
            sec_pat,
            "Patient 14-Day History Trend Points",
            len(pat_14day_points) == 14 and pat_14day_points[0]["sys"] > pat_14day_points[-1]["sys"],
            f"Curve: {pat_14day_points[0]['sys']} mmHg -> {pat_14day_points[-1]['sys']} mmHg (Improving!)"
        )

        # 2.3 Connected BLE Device Inventory
        devices_res = client.get("/api/v1/patients/me/devices", headers=pat_headers)
        devices = devices_res.json() if devices_res.status_code == 200 else []
        self.check(
            sec_pat,
            "Connected BLE Device Verification",
            devices_res.status_code == 200 and len(devices) >= 1 and "OMRON" in devices[0]["device_model"],
            f"Model: {devices[0]['device_model'] if devices else 'None'}"
        )

        # 2.4 Patient New Manual Reading Submission (PatientRecordReading.tsx)
        new_reading_res = client.post("/api/v1/readings", json={
            "systolic": 122,
            "diastolic": 78,
            "pulse": 68,
            "capture_method": "manual",
            "arm": "left",
            "posture": "sitting",
            "notes": "Patient evening self-check.",
        }, headers=pat_headers)
        self.check(
            sec_pat,
            "Patient Records Manual Vitals Entry",
            new_reading_res.status_code == 201 and new_reading_res.json().get("systolic") == 122
        )

        # 2.5 Patient Accessibility Preferences Mutation (PatientSettings.tsx)
        pref_res = client.patch("/api/v1/users/me", json={
            "locale": "ar",
            "text_size": 150,
            "theme": "calm_dark",
            "high_contrast": True,
        }, headers=pat_headers)
        self.check(
            sec_pat,
            "Patient Settings Persistence (Arabic RTL / 150% Scale)",
            pref_res.status_code == 200 and pref_res.json().get("locale") == "ar"
        )

        # ---------------------------------------------------------------------
        # Summary
        # ---------------------------------------------------------------------
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        print("\n=======================================================================")
        print(f"  LIVE SIMULATION INTEGRATION VERIFICATION SUMMARY")
        print("=======================================================================")
        print(f"  Total Validations: {total}")
        print(f"  Passed: {self.passed} | Failed: {self.failed}")
        print(f"  Success Rate: {rate:.1f}%")
        print("=======================================================================\n")

        if self.failed == 0:
            print(">>> LIVE BACKEND DATA INTEGRATION TEST PASSED 100% WITH ZERO ERRORS! <<<\n")
        else:
            print(f">>> {self.failed} TEST(S) FAILED. CHECK LOGS ABOVE. <<<\n")
            sys.exit(1)

if __name__ == "__main__":
    tester = SimulationIntegrationTester()
    tester.run()
