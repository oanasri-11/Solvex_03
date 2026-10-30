"""AlertReading association model linking alerts to multiple blood pressure readings."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class AlertReading(Base):
    __tablename__ = "alertreadings"
    __table_args__ = (
        UniqueConstraint("alert_id", "reading_id", name="uq_alert_reading"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    alert_id = Column(
        Integer,
        ForeignKey("alerts.id"),
        nullable=False,
        index=True,
    )
    reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=False,
        index=True,
    )

    alert = relationship("Alert", back_populates="alert_readings")
    reading = relationship("BloodPressureReading", back_populates="alert_readings")

    def __repr__(self):  # pragma: no cover
        return f"<AlertReading(id={self.id}, alert_id={self.alert_id}, reading_id={self.reading_id})>"
