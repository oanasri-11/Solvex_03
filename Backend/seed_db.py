"""Seed database with realistic initial users and clinical cohort for RAWDH."""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app
from app.db.session import SessionLocal
from app.models.user import User

client = TestClient(app)

def seed_database():
    print("=== Seeding RAWDH Database ===")
    db = SessionLocal()
    existing_karim = db.query(User).filter(User.email == "dr.karim@clinic.com").first()
    db.close()

    if existing_karim:
        print("Seed data already present (dr.karim@clinic.com found). Skipping seed.")
        return

    # 1. Admin account
    admin_res = client.post("/api/v1/auth/register", json={
        "email": "admin@rawdh.dz",
        "password": "Password123!",
        "full_name": "RAWDH System Admin",
        "phone": "+213550000001",
        "role": "admin",
    })
    admin_token = client.post("/api/v1/auth/login", json={
        "email": "admin@rawdh.dz",
        "password": "Password123!",
    }).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[+] Created Admin: admin@rawdh.dz")

    # 2. Doctor: Dr. Karim B.
    doc_res = client.post("/api/v1/auth/register", json={
        "email": "dr.karim@clinic.com",
        "password": "Password123!",
        "full_name": "Dr. Karim B.",
        "phone": "+213770000001",
        "role": "doctor",
    })
    doc_uid = doc_res.json()["id"]
    doc_profile = client.post("/api/v1/doctors", json={
        "user_id": doc_uid,
        "license_number": "DZ-DOC-1001",
        "specialization": "Cardiology & Telemonitoring",
        "speciality": "Cardiology",
        "first_name": "Karim",
        "last_name": "Benali",
        "facility": "Clinique Al-Amal",
    }, headers=admin_headers)
    doc_id = doc_profile.json()["id"]
    doc_token = client.post("/api/v1/auth/login", json={
        "email": "dr.karim@clinic.com",
        "password": "Password123!",
    }).json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    print("[+] Created Doctor: Dr. Karim B. (dr.karim@clinic.com)")

    # 3. Patient: Amina Benali
    amina_res = client.post("/api/v1/patients", json={
        "email": "amina.benali@email.com",
        "password": "Password123!",
        "full_name": "Amina Benali",
        "phone": "+213660000001",
        "date_of_birth": "1978-06-20",
        "gender": "female",
        "age_band": "45-64",
        "under_treatment": True,
    }, headers=admin_headers)
    amina_id = amina_res.json()["id"]

    # Assign Amina to Dr. Karim
    client.post("/api/v1/doctor-assignments", json={
        "doctor_id": doc_id,
        "patient_id": amina_id,
    }, headers=admin_headers)

    # Amina Token & Consents
    amina_token = client.post("/api/v1/auth/login", json={
        "email": "amina.benali@email.com",
        "password": "Password123!",
    }).json()["access_token"]
    amina_headers = {"Authorization": f"Bearer {amina_token}"}

    client.post("/api/v1/patients/me/consents", json={
        "type": "data_sharing",
        "text_version": "1.0",
        "accepted": True,
    }, headers=amina_headers)

    client.post(f"/api/v1/doctor/patients/{amina_id}/monitoring-modes", json={
        "patient_id": amina_id,
        "mode": "telemonitoring",
    }, headers=doc_headers)

    # Pair Device for Amina
    client.post("/api/v1/patients/me/devices", json={
        "device_model": "OMRON HEM-7361T-EBK (Bluetooth Smart)",
        "serial_number": "OM-8839210",
        "mac_address": "00:1B:44:11:3A:B7",
        "validation_status": "stride_bp_validated",
    }, headers=amina_headers)

    # Set Schedule for Amina
    client.post(f"/api/v1/doctor/patients/{amina_id}/schedules", json={
        "patient_id": amina_id,
        "protocol": "722_diagnostic",
        "readings_per_slot": 2,
        "cycle_length_days": 7,
        "pattern": "daily",
        "owner": "doctor",
    }, headers=doc_headers)

    # Submit 7 days of readings for Amina
    now = datetime.now(timezone.utc)
    for i in range(7, 0, -1):
        day = now - timedelta(days=i)
        # Morning reading
        client.post("/api/v1/readings", json={
            "patient_id": amina_id,
            "systolic": 132 + (i % 5),
            "diastolic": 84 + (i % 3),
            "pulse": 72 + (i % 4),
            "measured_at": (day.replace(hour=8, minute=15)).isoformat(),
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=amina_headers)
        # Evening reading
        client.post("/api/v1/readings", json={
            "patient_id": amina_id,
            "systolic": 136 + (i % 6),
            "diastolic": 86 + (i % 4),
            "pulse": 75 + (i % 3),
            "measured_at": (day.replace(hour=20, minute=30)).isoformat(),
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=amina_headers)

    # High reading triggering alert
    client.post("/api/v1/readings", json={
        "patient_id": amina_id,
        "systolic": 182,
        "diastolic": 112,
        "pulse": 89,
        "measured_at": now.isoformat(),
        "capture_method": "device",
        "arm": "left",
        "posture": "sitting",
        "symptoms_reported": ["headache", "dizziness"],
    }, headers=amina_headers)

    print("[+] Created Patient: Amina Benali (amina.benali@email.com) with schedule, device & readings")

    # 4. Patient: Marc Dupuis
    marc_res = client.post("/api/v1/patients", json={
        "email": "marc.dupuis@email.com",
        "password": "Password123!",
        "full_name": "Marc Dupuis",
        "phone": "+213660000002",
        "date_of_birth": "1953-05-14",
        "gender": "male",
        "age_band": "65-79",
        "under_treatment": True,
    }, headers=admin_headers)
    marc_id = marc_res.json()["id"]

    client.post("/api/v1/doctor-assignments", json={
        "doctor_id": doc_id,
        "patient_id": marc_id,
    }, headers=admin_headers)

    marc_token = client.post("/api/v1/auth/login", json={
        "email": "marc.dupuis@email.com",
        "password": "Password123!",
    }).json()["access_token"]
    marc_headers = {"Authorization": f"Bearer {marc_token}"}

    client.post("/api/v1/patients/me/consents", json={
        "type": "data_sharing",
        "text_version": "1.0",
        "accepted": True,
    }, headers=marc_headers)

    client.post(f"/api/v1/doctor/patients/{marc_id}/monitoring-modes", json={
        "patient_id": marc_id,
        "mode": "telemonitoring",
    }, headers=doc_headers)

    client.post("/api/v1/readings", json={
        "patient_id": marc_id,
        "systolic": 158,
        "diastolic": 96,
        "pulse": 74,
        "measured_at": (now - timedelta(hours=2)).isoformat(),
        "capture_method": "manual",
    }, headers=marc_headers)
    print("[+] Created Patient: Marc Dupuis (marc.dupuis@email.com)")

    # 5. Patient: Fatima Zahra
    fatima_res = client.post("/api/v1/patients", json={
        "email": "fatima.zahra@email.com",
        "password": "Password123!",
        "full_name": "Fatima Zahra",
        "phone": "+213660000003",
        "date_of_birth": "1966-03-12",
        "gender": "female",
        "age_band": "45-64",
        "under_treatment": True,
    }, headers=admin_headers)
    fatima_id = fatima_res.json()["id"]

    client.post("/api/v1/doctor-assignments", json={
        "doctor_id": doc_id,
        "patient_id": fatima_id,
    }, headers=admin_headers)

    fatima_token = client.post("/api/v1/auth/login", json={
        "email": "fatima.zahra@email.com",
        "password": "Password123!",
    }).json()["access_token"]
    fatima_headers = {"Authorization": f"Bearer {fatima_token}"}

    client.post("/api/v1/patients/me/consents", json={
        "type": "data_sharing",
        "text_version": "1.0",
        "accepted": True,
    }, headers=fatima_headers)

    client.post(f"/api/v1/doctor/patients/{fatima_id}/monitoring-modes", json={
        "patient_id": fatima_id,
        "mode": "telemonitoring",
    }, headers=doc_headers)

    client.post("/api/v1/readings", json={
        "patient_id": fatima_id,
        "systolic": 184,
        "diastolic": 118,
        "pulse": 88,
        "measured_at": (now - timedelta(minutes=42)).isoformat(),
        "capture_method": "device",
    }, headers=fatima_headers)
    print("[+] Created Patient: Fatima Zahra (fatima.zahra@email.com)")

    # Contact request from doctor to Amina
    client.post(f"/api/v1/doctor/patients/{amina_id}/contact-requests", json={
        "patient_id": amina_id,
        "message": "Please confirm morning medication adherence and check BP again in 1 hour.",
    }, headers=doc_headers)

    print("\n[+] Database successfully seeded with active cohort for Dr. Karim!")

if __name__ == "__main__":
    seed_database()
