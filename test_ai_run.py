import sys, os, time
sys.path.insert(0, 'C:/Users/HP/Desktop/Solvex_03/Backend')
os.environ['DATABASE_URL'] = 'sqlite:///./test_ai.db'
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.db.session import SessionLocal, Base, engine
from app.core.security import create_access_token, hash_password
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.models.patientprofile import PatientProfile
from app.models.doctorprofile import DoctorProfile
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.user import User
from app.routes import ai as ai_route
Base.metadata.create_all(bind=engine)
app = FastAPI(); app.include_router(ai_route.router, prefix='/api/v1')
client = TestClient(app)
db = SessionLocal()
assignments = db.query(DoctorPatientAssignment).filter(DoctorPatientAssignment.is_active==True).all()
if not assignments:
    du = create_user(db, UserCreate(email='td@test.com', full_name='Dr Test', role='doctor', hashed_password=hash_password('pw'))); du.is_verified=True; db.commit()
    dp = DoctorProfile(user_id=du.id, license_number='L1', specialization='Cardio'); db.add(dp); db.commit(); db.refresh(dp)
    pu = create_user(db, UserCreate(email='tp@test.com', full_name='Pat Test', role='patient', hashed_password=hash_password('pw'))); pu.is_verified=True; db.commit()
    pp = PatientProfile(user_id=pu.id, gender='male'); db.add(pp); db.commit(); db.refresh(pp)
    a = DoctorPatientAssignment(doctor_id=dp.id, patient_id=pp.id, is_active=True); db.add(a); db.commit(); assignments=[a]
a=assignments[0]
dp=db.query(DoctorProfile).filter(DoctorProfile.id==a.doctor_id).first()
du=db.query(User).filter(User.id==dp.user_id).first()
pp=db.query(PatientProfile).filter(PatientProfile.id==a.patient_id).first()
token=create_access_token(data={'sub':str(du.id),'email':du.email,'role':'doctor'})
t0=time.time()
r=client.post(f'/api/v1/ai/patients/{pp.id}/summary', json={'period_days':30}, headers={'Authorization':f'Bearer {token}'})
print('STATUS', r.status_code, 'ELAPSED', round(time.time()-t0,2))
if r.status_code==200:
    d=r.json(); print('SECTIONS', len(d.get('sections',[])))
    for s in d.get('sections',[]): print(' -', s.get('title'))
    print('LIMITATIONS', d.get('data_limitations'))
else:
    print(r.text[:500])
db.close()
