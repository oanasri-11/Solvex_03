"""ConnectedDevice model (Section 11b)."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConnectedDevice(Base):
    __tablename__ = "connected_devices"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    device_model = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=True)
    mac_address = Column(String(50), nullable=True)
    validation_status = Column(String(50), default="unvalidated", nullable=False)  # stride_bp_validated, unvalidated
    paired_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<ConnectedDevice(id={self.id}, patient_id={self.patient_id}, model={self.device_model})>"
