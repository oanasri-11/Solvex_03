import app.models  # registers all models with Base.metadata
from app.db.base import Base, metadata

tables = sorted(metadata.tables.keys())
print('Tables registered in Base.metadata:')
for t in tables:
    print('  -', t)
print()
print('Total tables:', len(tables))

expected = [
    'users', 'patient_profiles', 'doctor_profiles', 'doctor_patient_assignments',
    'patient_monitoring_modes', 'patient_conditions', 'measurement_schedules',
    'schedule_slots', 'blood_pressure_readings', 'alerts', 'alert_readings',
    'priority_assessments', 'case_reviews', 'patient_help_requests',
    'contact_requests', 'follow_up_actions', 'notifications', 'rule_versions',
    'audit_logs',
]
missing = [t for t in expected if t not in metadata.tables]
extra = [t for t in tables if t not in expected]
print('Missing:', missing)
print('Extra:', extra)
assert not missing, 'Missing tables!'
assert not extra, 'Unexpected tables!'
print()
print('ALL 19 TABLES REGISTERED OK')

# Verify relationships are configured on each mapper
print()
print('Relationships per mapper:')
for cls in [Base.classes.Users if hasattr(Base.classes, 'Users') else None]:
    pass
# Inspect all mapped classes
from sqlalchemy.orm import class_mapper
mapped = []
for tname in expected:
    # find class by tablename
    for cls in Base._registry._class_registry.values():
        if hasattr(cls, '__tablename__') and cls.__tablename__ == tname:
            mapped.append(cls)
            break

for cls in mapped:
    mapper = class_mapper(cls)
    rels = [(r.key, r.direction.name) for r in mapper.relationships]
    fks = [str(fk) for fk in cls.__table__.foreign_keys]
    print(f"  {cls.__name__}: relationships={rels}")
    if fks:
        print(f"    foreign_keys={fks}")
print()
print('RELATIONSHIP/FK INSPECTION COMPLETE')
