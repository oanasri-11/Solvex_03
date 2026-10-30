from app.db.session import Base, engine

# Import all models
from app.models.user import User
from app.models.patientprofile import PatientProfile
from app.models.doctorprofile import DoctorProfile

# Add all your other model imports here

# Create tables
Base.metadata.create_all(bind=engine)

print("Tables created:")
for table in Base.metadata.tables:
    print(f"- {table}")