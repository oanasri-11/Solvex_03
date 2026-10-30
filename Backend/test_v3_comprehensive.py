"""Comprehensive Verification Suite for all Hypertension Monitoring v3 modules."""

import sys
import os
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_comprehensive_tests():
    uid = str(uuid.uuid4())[:8]
    print(f"=== Starting Comprehensive API v3 Test Run [ID: {uid}] ===")

    # 1. Admin setup
    admin_email = f"admin_{uid}@clinic.org"
    res = client.post("/api/v1/auth/register", json={
        "email": admin_email,
        "password": "Password123!",
        "full_name": "Clinic Admin",
        "phone": f"+213550{uid[:6]}",
        "role": "admin",
    })
    assert res.status_code == 201, f"Admin register failed: {res.text}"
    admin_token = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "Password123!"}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("PASS: 1. Admin Registration & Login")

    # 2. Doctor setup
    doc_email = f"doc_{uid}@clinic.org"
    res = client.post("/api/v1/auth/register", json={
        "email": doc_email,
        "password": "Password123!",
        "full_name": "Dr. Nadia Slimani",
        "phone": f"+213770{uid[:6]}",
        "role": "doctor",
    })
    assert res.status_code == 201
    doc_uid = res.json()["id"]
    res = client.post("/api/v1/doctors", json={
        "user_id": doc_uid,
        "license_number": f"DZ-{uid}",
        "specialization": "Internal Medicine",
        "speciality": "Internal Medicine",
        "first_name": "Nadia",
        "last_name": "Slimani",
        "facility": "Clinique Al-Amal",
    }, headers=admin_headers)
    assert res.status_code == 201
    doc_id = res.json()["id"]
    doc_token = client.post("/api/v1/auth/login", json={"email": doc_email, "password": "Password123!"}).json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    print("PASS: 2. Doctor User & Profile Creation")

    # 3. Patient Enrollment
    pat_email = f"pat_{uid}@clinic.org"
    res = client.post("/api/v1/patients", json={
        "email": pat_email,
        "password": "Password123!",
        "full_name": "Mohamed Brahimi",
        "phone": f"+213660{uid[:6]}",
        "date_of_birth": "1958-03-15",
        "gender": "male",
        "age_band": "65-79",
        "under_treatment": True,
    }, headers=admin_headers)
    assert res.status_code == 201
    pat_id = res.json()["id"]
    pat_token = client.post("/api/v1/auth/login", json={"email": pat_email, "password": "Password123!"}).json()["access_token"]
    pat_headers = {"Authorization": f"Bearer {pat_token}"}
    print("PASS: 3. Patient Enrollment & Profile Creation")

    # 4. Doctor-Patient Assignment
    res = client.post("/api/v1/doctor-assignments", json={
        "doctor_id": doc_id,
        "patient_id": pat_id,
    }, headers=admin_headers)
    assert res.status_code == 201
    print("PASS: 4. Doctor-Patient Assignment")

    # 5. Consent & Mode
    res = client.post("/api/v1/patients/me/consents", json={
        "type": "data_sharing",
        "text_version": "1.0",
        "accepted": True,
    }, headers=pat_headers)
    assert res.status_code == 201

    res = client.post(f"/api/v1/doctor/patients/{pat_id}/monitoring-modes", json={
        "patient_id": pat_id,
        "mode": "telemonitoring",
    }, headers=doc_headers)
    assert res.status_code in (200, 201), f"Set mode failed: {res.text}"
    print("PASS: 5. Patient Consent & Monitoring Mode Setting")

    # 6. Set Schedule (722 Protocol)
    res = client.post(f"/api/v1/doctor/patients/{pat_id}/schedules", json={
        "patient_id": pat_id,
        "protocol": "722_diagnostic",
        "readings_per_slot": 2,
        "cycle_length_days": 7,
        "pattern": "daily",
        "owner": "doctor",
    }, headers=doc_headers)
    assert res.status_code in (200, 201), f"Set schedule failed: {res.text}"
    print("PASS: 6. Measurement Schedule Setup")

    # 7. Post Readings (One regular, One severe triggering alert)
    res = client.post("/api/v1/readings", json={
        "patient_id": pat_id,
        "systolic": 138,
        "diastolic": 86,
        "pulse": 70,
        "measured_at": "2026-10-30T08:05:00Z",
        "capture_method": "manual",
    }, headers=pat_headers)
    assert res.status_code == 201

    res = client.post("/api/v1/readings", json={
        "patient_id": pat_id,
        "systolic": 185,
        "diastolic": 115,
        "pulse": 88,
        "measured_at": "2026-10-30T20:10:00Z",
        "capture_method": "manual",
        "symptoms_reported": ["headache", "dizziness"],
    }, headers=pat_headers)
    assert res.status_code == 201
    print("PASS: 7. Ingestion of Standard & Concerning Readings")

    # 8. Check Alerts
    res = client.get("/api/v1/doctor/me/alerts", headers=doc_headers)
    assert res.status_code == 200, f"Doctor alerts failed: {res.text}"
    alerts = res.json()
    assert len(alerts) >= 1, "Expected at least 1 alert"
    alert_id = alerts[0]["id"]
    print(f"PASS: 8. Alert Generation (Tier: {alerts[0].get('tier')}, Trigger: {alerts[0].get('trigger_reason')})")

    # 9. Acknowledge Alert
    res = client.post(f"/api/v1/alerts/{alert_id}/acknowledge", json={
        "decision": "monitor_closely",
        "note": "Patient alerted with elevated BP and headache",
    }, headers=doc_headers)
    assert res.status_code == 200
    print("PASS: 9. Alert Acknowledgment by Doctor")

    # 10. Patient Help Request
    res = client.post("/api/v1/patients/me/help-requests", json={
        "patient_id": pat_id,
        "type": "technical_issue",
        "description": "Is the medium cuff appropriate for 33cm arm circumference?",
    }, headers=pat_headers)
    assert res.status_code == 201, f"Help request failed: {res.text}"
    print("PASS: 10. Patient Help Request Submission")

    # 11. Doctor Contact Request
    res = client.post(f"/api/v1/doctor/patients/{pat_id}/contact-requests", json={
        "patient_id": pat_id,
        "message": "Please call clinic to review your evening reading",
    }, headers=doc_headers)
    assert res.status_code == 201, f"Contact request failed: {res.text}"
    print("PASS: 11. Doctor Contact Request Creation")

    # 12. Doctor Priority Queue
    res = client.get("/api/v1/doctor/me/priority-queue", headers=doc_headers)
    assert res.status_code == 200
    print(f"PASS: 12. Doctor Priority Queue Access (Patients: {len(res.json().get('items', []))})")

    # 13. Case Review Creation
    res = client.post(f"/api/v1/doctor/patients/{pat_id}/reviews", json={
        "patient_id": pat_id,
        "summary": "Persistent stage 2 readings on 722 protocol",
        "status": "completed",
    }, headers=doc_headers)
    assert res.status_code == 201, f"Review create failed: {res.text}"
    print("PASS: 13. Case Review & Clinical Documentation")

    # 14. Report Generation
    res = client.get(f"/api/v1/doctor/patients/{pat_id}/reports/preview", headers=doc_headers)
    assert res.status_code == 200, f"Report preview failed: {res.text}"
    print("PASS: 14. Patient Report Generation")

    # 15. Audit Log Access
    res = client.get("/api/v1/admin/audit-logs?limit=5", headers=admin_headers)
    assert res.status_code == 200, f"Audit logs failed: {res.text}"
    logs = res.json()
    print(f"PASS: 15. Admin Audit Log Verification (Entries: {len(logs)})")

    print("\n=======================================================")
    print("ALL 15 COMPREHENSIVE END-TO-END TESTS COMPLETED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_comprehensive_tests()
