"""Comprehensive End-to-End Test Suite for Hypertension Monitoring v3 API."""

import sys
import os
import uuid
from pathlib import Path

# Setup paths
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    unique = str(uuid.uuid4())[:8]
    print(f"Starting test run with run ID: {unique}")

    # 1. Register an admin
    admin_email = f"admin_{unique}@test.com"
    res = client.post("/api/v1/auth/register", json={
        "email": admin_email,
        "password": "Password123!",
        "full_name": "System Administrator",
        "phone": f"+213555{unique[:6]}",
        "role": "admin",
    })
    print("1. Register Admin:", res.status_code)
    assert res.status_code == 201

    # 2. Login as admin
    res = client.post("/api/v1/auth/login", json={
        "email": admin_email,
        "password": "Password123!",
    })
    print("2. Login Admin:", res.status_code)
    assert res.status_code == 200
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Create a Doctor user and profile
    doc_email = f"doc_{unique}@test.com"
    doc_u_res = client.post("/api/v1/auth/register", json={
        "email": doc_email,
        "password": "Password123!",
        "full_name": "Dr. Amine Benali",
        "phone": f"+213777{unique[:6]}",
        "role": "doctor",
    })
    print("3a. Register Doctor User:", doc_u_res.status_code)
    assert doc_u_res.status_code == 201
    doc_user_id = doc_u_res.json()["id"]

    doc_res = client.post("/api/v1/doctors", json={
        "user_id": doc_user_id,
        "license_number": f"LIC-{unique}",
        "specialization": "Cardiology",
        "speciality": "Cardiology",
        "first_name": "Amine",
        "last_name": "Benali",
        "facility": "CHU Mustapha",
    }, headers=admin_headers)
    print("3b. Create Doctor Profile:", doc_res.status_code)
    assert doc_res.status_code == 201
    doctor_id = doc_res.json()["id"]

    # 4. Admin enrols a patient
    patient_email = f"pat_{unique}@test.com"
    enrol_res = client.post("/api/v1/patients", json={
        "email": patient_email,
        "password": "Password123!",
        "full_name": "Fatima Zohra",
        "phone": f"+213666{unique[:6]}",
        "date_of_birth": "1965-05-12",
        "gender": "female",
        "age_band": "65-79",
        "under_treatment": True,
    }, headers=admin_headers)
    print("4. Enrol Patient:", enrol_res.status_code)
    assert enrol_res.status_code == 201
    patient_id = enrol_res.json()["id"]

    # 5. Admin links Patient to Doctor
    link_res = client.post("/api/v1/doctor-assignments", json={
        "doctor_id": doctor_id,
        "patient_id": patient_id,
    }, headers=admin_headers)
    print("5. Link Doctor to Patient:", link_res.status_code)
    assert link_res.status_code == 201

    # 6. Patient logs in
    login_pat = client.post("/api/v1/auth/login", json={
        "email": patient_email,
        "password": "Password123!",
    })
    print("6. Patient Login:", login_pat.status_code)
    assert login_pat.status_code == 200
    patient_token = login_pat.json()["access_token"]
    patient_headers = {"Authorization": f"Bearer {patient_token}"}

    # 7. Patient gets /auth/me
    me_res = client.get("/api/v1/auth/me", headers=patient_headers)
    print("7. Patient /auth/me role:", me_res.json().get("role"))
    assert me_res.status_code == 200
    assert me_res.json().get("role") == "patient"

    # 8. Patient records consent
    consent_res = client.post("/api/v1/patients/me/consents", json={
        "type": "data_sharing",
        "text_version": "1.0",
        "accepted": True,
    }, headers=patient_headers)
    print("8. Patient Records Consent:", consent_res.status_code)
    assert consent_res.status_code == 201

    # 9. Patient posts BP reading
    reading_res = client.post("/api/v1/readings", json={
        "patient_id": patient_id,
        "systolic": 142,
        "diastolic": 88,
        "pulse": 72,
        "measured_at": "2026-10-30T08:00:00Z",
        "capture_method": "manual",
    }, headers=patient_headers)
    print("9. Patient Posts Reading:", reading_res.status_code)
    assert reading_res.status_code == 201

    # 10. Patient reads summary
    summary_res = client.get("/api/v1/patients/me/summary", headers=patient_headers)
    print("10. Patient Reads Summary:", summary_res.status_code)
    assert summary_res.status_code == 200

    # 11. Patient reads trends
    trend_res = client.get("/api/v1/patients/me/trends?range=7d", headers=patient_headers)
    print("11. Patient Reads Trends:", trend_res.status_code)
    assert trend_res.status_code == 200

    # 12. Doctor logs in
    login_doc = client.post("/api/v1/auth/login", json={
        "email": doc_email,
        "password": "Password123!",
    })
    print("12. Doctor Login:", login_doc.status_code)
    assert login_doc.status_code == 200
    doc_token = login_doc.json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # 13. Doctor checks dashboard
    dash_res = client.get("/api/v1/doctor/me/dashboard", headers=doc_headers)
    print("13. Doctor Dashboard active patients:", dash_res.json().get("active_patient_count"))
    assert dash_res.status_code == 200

    # 14. Doctor sets individual target
    target_res = client.put(f"/api/v1/doctor/patients/{patient_id}/target", json={
        "systolic": 130,
        "diastolic": 80,
        "reason_code": "elderly_adjusted",
        "note": "Strict home BP control",
    }, headers=doc_headers)
    print("14. Doctor Sets Target:", target_res.status_code)
    assert target_res.status_code == 200

    # 15. Check features and config
    feat_res = client.get("/api/v1/config/features")
    print("15. Config Features:", feat_res.json().get("features"))
    assert feat_res.status_code == 200

    print("\n=======================================================")
    print("SUCCESS: ALL 15 END-TO-END WORKFLOW TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
