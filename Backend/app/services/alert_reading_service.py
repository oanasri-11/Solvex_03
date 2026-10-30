"""AlertReading service.

Operations for the AlertReading association model (links an alert to its evidence
readings), following classic SQLAlchemy syntax. Alert evidence is immutable: no
update or delete is exposed.
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.AlertReading import AlertReading
from app.models.Alert import Alert
from app.models.BloodPressureReading import BloodPressureReading
from app.schemas.alertreading import (
    AlertReadingCreate,
    AlertReadingUpdate,
    AlertReadingOut,
)


def create_alert_reading(db: Session, link_in: AlertReadingCreate) -> Optional[AlertReading]:
    """Link an alert to an evidence reading. Verifies both records exist."""
    try:
        alert = db.query(Alert).filter(Alert.id == link_in.alert_id).first()
        reading = (
            db.query(BloodPressureReading)
            .filter(BloodPressureReading.id == link_in.reading_id)
            .first()
        )
        if not alert or not reading:
            return None

        existing = (
            db.query(AlertReading)
            .filter(
                AlertReading.alert_id == link_in.alert_id,
                AlertReading.reading_id == link_in.reading_id,
            )
            .first()
        )
        if existing:
            return existing

        db_link = AlertReading(
            alert_id=link_in.alert_id,
            reading_id=link_in.reading_id,
        )
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        return db_link
    except SQLAlchemyError:
        db.rollback()
        raise


def get_alert_reading_by_id(db: Session, link_id: int) -> Optional[AlertReading]:
    """Retrieve an alert-reading link by its primary key."""
    return db.query(AlertReading).filter(AlertReading.id == link_id).first()


def get_all_alert_readings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    alert_id: Optional[int] = None,
    reading_id: Optional[int] = None,
):
    """List alert-reading links with optional alert_id / reading_id filters."""
    query = db.query(AlertReading)
    if alert_id is not None:
        query = query.filter(AlertReading.alert_id == alert_id)
    if reading_id is not None:
        query = query.filter(AlertReading.reading_id == reading_id)
    return query.offset(skip).limit(limit).all()


# Note: update/delete are intentionally omitted. Alert evidence links are immutable.
