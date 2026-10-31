"""RAWDH (روض) — Live Backend Simulation & Clinical Cohort Seeder.

Generates realistic clinical telemonitoring data directly in the backend SQLite database:
1. Doctor: Dr. Karim Benali (dr.karim@clinic.com / Password123!)
2. 5 Multi-persona Patients with diverse clinical statuses (P1-P4):
   - Fatima Zahra (Crisis / P1_critical / CKD)
   - Marc Dupuis (High Priority / P2_high / Stage 2 HTN)
   - Jean Moreau (Moderate Priority / P3_moderate / Diabetes)
   - Amina Benali (Within Target / Telemonitoring / Improving 14-day curve)
   - Ahmed Cherif (Within Target / Self-monitoring / Routine)
3. 14 Days of Time-stamped AM/PM Readings for realistic trend charts.
4. Multi-tier alerts (critical_emergency, severe_single_reading, persistent_elevation).
5. Open contact tasks / outreach queue items.
6. Connected BLE hardware monitors (OMRON HEM-7361T-EBK).
7. Individual clinical targets, 722 schedules, and informed consents.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure Backend package is in sys.path
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
from app.db.session import SessionLocal, Base, engine
from app.models.user import User
from app.services.priority_service import calculate_patient_priority

client = TestClient(app)

def run_simulation():
    print("=======================================================================")
    print("  RAWDH (روض) — LIVE BACKEND DATA SIMULATION & SEED ENGINE")
    print("=======================================================================")

    # 1. Ensure clean tables or wipe existing simulation records
    db = SessionLocal()
    existing_karim = db.query(User).filter(User.email == "dr.karim@clinic.com").first()
    
    if existing_karim:
        print("[!] Previous simulation data detected. Re-syncing database tables...")
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF"))
            for table in Base.metadata.sorted_tables:
                conn.execute(text(f"DELETE FROM {table.name}"))
            conn.execute(text("PRAGMA foreign_keys = ON"))
            conn.commit()
        print("[+] Database tables cleared.")
    else:
        db.close()

    # -------------------------------------------------------------------------
    # 1. System Administrator
    # -------------------------------------------------------------------------
    admin_reg = client.post("/api/v1/auth/register", json={
        "email": "admin@rawdh.dz",
        "password": "Password123!",
        "full_name": "RAWDH System Administrator",
        "phone": "+213550000001",
        "role": "admin",
    })
    admin_token = client.post("/api/v1/auth/login", json={
        "email": "admin@rawdh.dz",
        "password": "Password123!",
    }).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[+] Created Admin: admin@rawdh.dz")

    # -------------------------------------------------------------------------
    # 2. Doctor: Dr. Karim Benali
    # -------------------------------------------------------------------------
    doc_reg = client.post("/api/v1/auth/register", json={
        "email": "dr.karim@clinic.com",
        "password": "Password123!",
        "full_name": "Dr. Karim Benali",
        "phone": "+213770000001",
        "role": "doctor",
    })
    doc_uid = doc_reg.json()["id"]

    doc_profile = client.post("/api/v1/doctors", json={
        "user_id": doc_uid,
        "license_number": "DZ-CARDIO-1088",
        "specialization": "Cardiology & Telemonitoring",
        "speciality": "Cardiology",
        "first_name": "Karim",
        "last_name": "Benali",
        "facility": "Clinique Al-Amal d'Alger",
    }, headers=admin_headers)
    doc_id = doc_profile.json()["id"]

    doc_token = client.post("/api/v1/auth/login", json={
        "email": "dr.karim@clinic.com",
        "password": "Password123!",
    }).json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    print(f"[+] Provisioned Doctor: Dr. Karim Benali (ID: {doc_id})")

    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------
    # Helper to create patient with complete clinical baseline
    # -------------------------------------------------------------------------
    def create_patient_persona(
        email: str,
        full_name: str,
        phone: str,
        dob: str,
        gender: str,
        age_band: str,
        target_sys: int,
        target_dia: int,
        condition: str,
        mode: str = "telemonitoring",
    ):
        p_res = client.post("/api/v1/patients", json={
            "email": email,
            "password": "Password123!",
            "full_name": full_name,
            "phone": phone,
            "date_of_birth": dob,
            "gender": gender,
            "age_band": age_band,
            "under_treatment": True,
            "clinical_context": {"notes": condition},
        }, headers=admin_headers)
        p_id = p_res.json()["id"]

        # Assign to Dr. Karim
        client.post("/api/v1/doctor-assignments", json={
            "doctor_id": doc_id,
            "patient_id": p_id,
        }, headers=admin_headers)

        # Login
        p_token = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!",
        }).json()["access_token"]
        p_headers = {"Authorization": f"Bearer {p_token}"}

        # Consents
        client.post("/api/v1/patients/me/consents", json={
            "type": "data_sharing",
            "text_version": "1.0",
            "accepted": True,
        }, headers=p_headers)

        # Monitoring mode
        client.post(f"/api/v1/doctor/patients/{p_id}/monitoring-modes", json={
            "patient_id": p_id,
            "mode": mode,
        }, headers=doc_headers)

        # Target BP
        client.put(f"/api/v1/doctor/patients/{p_id}/target", json={
            "systolic": target_sys,
            "diastolic": target_dia,
            "reason_code": "CLINICAL_GUIDELINE_DEFAULT",
            "note": f"Target individualisé fixé à <{target_sys}/{target_dia} mmHg",
        }, headers=doc_headers)

        return p_id, p_headers

    # -------------------------------------------------------------------------
    # 3. Patient: Fatima Zahra (Crisis / P1_critical / CKD)
    # -------------------------------------------------------------------------
    fatima_id, fatima_headers = create_patient_persona(
        email="fatima.zahra@email.com",
        full_name="Fatima Zahra",
        phone="+213660000003",
        dob="1955-03-12",
        gender="female",
        age_band="65-79",
        target_sys=130,
        target_dia=80,
        condition="Hypertension Réfractaire, Insuffisance Rénale Chronique (CKD Stage 3)",
    )

    # Ingest baseline readings leading up to severe crisis
    for day_offset in range(10, 0, -1):
        dt = now - timedelta(days=day_offset, hours=10)
        client.post("/api/v1/readings", json={
            "patient_id": fatima_id,
            "systolic": 162 + (day_offset % 6),
            "diastolic": 98 + (day_offset % 4),
            "pulse": 82,
            "measured_at": dt.isoformat(),
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=fatima_headers)

    # Trigger Severe Crisis Reading (186/122 mmHg with symptoms) -> Tier: critical_emergency
    client.post("/api/v1/readings", json={
        "patient_id": fatima_id,
        "systolic": 186,
        "diastolic": 122,
        "pulse": 94,
        "measured_at": (now - timedelta(minutes=45)).isoformat(),
        "capture_method": "device",
        "arm": "left",
        "posture": "sitting",
        "symptoms_reported": ["severe_headache", "blurred_vision"],
    }, headers=fatima_headers)
    print(f"[+] Patient 1: Fatima Zahra (ID: {fatima_id}) -> Crisis (186/122 mmHg, CKD, P1)")

    # -------------------------------------------------------------------------
    # 4. Patient: Marc Dupuis (Stage 2 HTN / Persistent Elevation / P2_high)
    # -------------------------------------------------------------------------
    marc_id, marc_headers = create_patient_persona(
        email="marc.dupuis@email.com",
        full_name="Marc Dupuis",
        phone="+213660000002",
        dob="1968-05-14",
        gender="male",
        age_band="40-64",
        target_sys=135,
        target_dia=85,
        condition="HTN Stage 2, Dyslipidémie, Amlodipine 5mg QD",
    )

    # 14 days of realistic fluctuating elevated readings for trend chart
    marc_curve = [
        (152, 94), (155, 95), (158, 96), (160, 98),
        (164, 100), (162, 98), (159, 97), (165, 101),
        (168, 102), (166, 100), (163, 98), (167, 102),
        (165, 99), (168, 102)
    ]
    for i, (sys_val, dia_val) in enumerate(marc_curve):
        day_offset = 14 - i
        dt_am = (now - timedelta(days=day_offset)).replace(hour=8, minute=20)
        dt_pm = (now - timedelta(days=day_offset)).replace(hour=20, minute=45)
        # AM
        client.post("/api/v1/readings", json={
            "patient_id": marc_id,
            "systolic": sys_val,
            "diastolic": dia_val,
            "pulse": 76,
            "measured_at": dt_am.isoformat(),
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=marc_headers)
        # PM
        client.post("/api/v1/readings", json={
            "patient_id": marc_id,
            "systolic": sys_val + 2,
            "diastolic": dia_val + 1,
            "pulse": 78,
            "measured_at": dt_pm.isoformat(),
            "capture_method": "manual" if i % 3 == 0 else "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=marc_headers)

    print(f"[+] Patient 2: Marc Dupuis (ID: {marc_id}) -> Persistent Elevation (168/102 mmHg, P2)")

    # -------------------------------------------------------------------------
    # 5. Patient: Jean Moreau (Moderate Priority / Diabetes / P3_moderate)
    # -------------------------------------------------------------------------
    jean_id, jean_headers = create_patient_persona(
        email="jean.moreau@email.com",
        full_name="Jean Moreau",
        phone="+213660000004",
        dob="1961-09-18",
        gender="male",
        age_band="65-79",
        target_sys=130,
        target_dia=80,
        condition="Diabète de Type 2, Hypertension Artérielle",
    )
    for day_offset in range(12, 0, -1):
        dt = now - timedelta(days=day_offset, hours=9)
        client.post("/api/v1/readings", json={
            "patient_id": jean_id,
            "systolic": 142 + (day_offset % 5),
            "diastolic": 88 + (day_offset % 4),
            "pulse": 74,
            "measured_at": dt.isoformat(),
            "capture_method": "device",
        }, headers=jean_headers)
    print(f"[+] Patient 3: Jean Moreau (ID: {jean_id}) -> Diabetes Co-morbidity (144/90 mmHg, P3)")

    # -------------------------------------------------------------------------
    # 6. Patient: Amina Benali (Within Target / Telemonitoring / Improving Curve)
    # -------------------------------------------------------------------------
    amina_id, amina_headers = create_patient_persona(
        email="amina.benali@email.com",
        full_name="Amina Benali",
        phone="+213660000001",
        dob="1964-06-20",
        gender="female",
        age_band="40-64",
        target_sys=130,
        target_dia=80,
        condition="Hypertension essentielle, Ramipril 5mg",
    )

    # Set 722 Diagnostic protocol schedule
    client.post(f"/api/v1/doctor/patients/{amina_id}/schedules", json={
        "patient_id": amina_id,
        "protocol": "722_diagnostic",
        "readings_per_slot": 2,
        "cycle_length_days": 7,
        "pattern": "daily",
        "owner": "doctor",
    }, headers=doc_headers)

    # Pair BLE OMRON device
    client.post("/api/v1/patients/me/devices", json={
        "device_model": "OMRON HEM-7361T-EBK (Bluetooth Smart)",
        "serial_number": "OM-8839210-DZ",
        "mac_address": "00:1B:44:11:3A:B7",
        "validation_status": "stride_bp_validated",
    }, headers=amina_headers)

    # Ingest 14 days of readings showing a clear progressive IMPROVEMENT curve
    # Day 14: 138/88 -> Day 1: 124/79 (optimal control)
    amina_trend = [
        (138, 88), (137, 87), (136, 86), (135, 85),
        (134, 84), (132, 83), (131, 82), (130, 82),
        (129, 81), (128, 80), (127, 80), (126, 79),
        (125, 79), (124, 78)
    ]
    for i, (sys_val, dia_val) in enumerate(amina_trend):
        day_offset = 14 - i
        dt_am = (now - timedelta(days=day_offset)).replace(hour=8, minute=15)
        dt_pm = (now - timedelta(days=day_offset)).replace(hour=20, minute=30)
        # AM Reading
        client.post("/api/v1/readings", json={
            "patient_id": amina_id,
            "systolic": sys_val,
            "diastolic": dia_val,
            "pulse": 72,
            "measured_at": dt_am.isoformat(),
            "capture_method": "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=amina_headers)
        # PM Reading
        client.post("/api/v1/readings", json={
            "patient_id": amina_id,
            "systolic": sys_val + 1,
            "diastolic": dia_val + 1,
            "pulse": 74,
            "measured_at": dt_pm.isoformat(),
            "capture_method": "manual" if i % 4 == 0 else "device",
            "arm": "left",
            "posture": "sitting",
        }, headers=amina_headers)

    # Ingest today's morning reading for Amina
    client.post("/api/v1/readings", json={
        "patient_id": amina_id,
        "systolic": 124,
        "diastolic": 78,
        "pulse": 71,
        "measured_at": (now - timedelta(hours=2)).isoformat(),
        "capture_method": "device",
        "arm": "left",
        "posture": "sitting",
    }, headers=amina_headers)

    # Doctor dispatches outreach task to Amina
    client.post(f"/api/v1/doctor/patients/{amina_id}/contact-requests", json={
        "patient_id": amina_id,
        "message": "Excellent progrès sur la courbe tensionnelle. Poursuivre le Ramipril 5mg.",
        "urgency": "routine",
    }, headers=doc_headers)

    print(f"[+] Patient 4: Amina Benali (ID: {amina_id}) -> Improving Control (124/78 mmHg, OMRON BLE, 722 Schedule)")

    # -------------------------------------------------------------------------
    # 7. Patient: Ahmed Cherif (Self-Monitoring / P4_routine)
    # -------------------------------------------------------------------------
    ahmed_id, ahmed_headers = create_patient_persona(
        email="ahmed.cherif@email.com",
        full_name="Ahmed Cherif",
        phone="+213660000005",
        dob="1972-11-04",
        gender="male",
        age_band="40-64",
        target_sys=135,
        target_dia=85,
        condition="Hypertension légère de grade 1 contrôlée par hygiène de vie",
        mode="self_monitoring",
    )
    for day_offset in range(7, 0, -1):
        dt = now - timedelta(days=day_offset, hours=11)
        client.post("/api/v1/readings", json={
            "patient_id": ahmed_id,
            "systolic": 126 + (day_offset % 3),
            "diastolic": 80 + (day_offset % 2),
            "pulse": 70,
            "measured_at": dt.isoformat(),
            "capture_method": "manual",
        }, headers=ahmed_headers)
    print(f"[+] Patient 5: Ahmed Cherif (ID: {ahmed_id}) -> Self-Monitoring Stable (126/80 mmHg, P4)")

    # -------------------------------------------------------------------------
    # 8. Force Server Priority Assessment Calculation for all 5 patients
    # -------------------------------------------------------------------------
    db_session = SessionLocal()
    for pid in [fatima_id, marc_id, jean_id, amina_id, ahmed_id]:
        calculate_patient_priority(db_session, pid)
    db_session.close()

    print("\n=======================================================================")
    print("  SIMULATION DATA GENERATION COMPLETE!")
    print("=======================================================================")
    print("  Doctor Login:   dr.karim@clinic.com     / Password123!")
    print("  Patient Logins:")
    print("    - Fatima Zahra: fatima.zahra@email.com / Password123! (Crisis/P1)")
    print("    - Marc Dupuis:  marc.dupuis@email.com  / Password123! (High/P2)")
    print("    - Jean Moreau:  jean.moreau@email.com  / Password123! (Moderate/P3)")
    print("    - Amina Benali: amina.benali@email.com / Password123! (Target/722)")
    print("    - Ahmed Cherif: ahmed.cherif@email.com / Password123! (Self-Mon)")
    print("=======================================================================\n")

if __name__ == "__main__":
    run_simulation()
