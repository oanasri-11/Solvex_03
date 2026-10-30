
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.alertreading import (
    AlertReadingCreate,
    AlertReadingOut,
)

from app.services.alert_reading_service import (
    create_alert_reading,
    get_alert_reading_by_id,
    get_all_alert_readings,
)


router = APIRouter(
    prefix="/alert-readings",
    tags=["Alert Readings"]
)


@router.post(
    "/",
    response_model=AlertReadingOut,
    status_code=status.HTTP_201_CREATED
)
def create_alert_reading_route(
    link_in: AlertReadingCreate,
    db: Session = Depends(get_db)
):
    link = create_alert_reading(db, link_in)

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert or blood pressure reading not found."
        )

    return link


@router.get(
    "/{link_id}",
    response_model=AlertReadingOut
)
def get_alert_reading_route(
    link_id: int,
    db: Session = Depends(get_db)
):
    link = get_alert_reading_by_id(db, link_id)

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert-reading link not found."
        )

    return link


@router.get(
    "/",
    response_model=List[AlertReadingOut]
)
def get_all_alert_readings_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    alert_id: Optional[int] = Query(None, gt=0),
    reading_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
):
    return get_all_alert_readings(
        db=db,
        skip=skip,
        limit=limit,
        alert_id=alert_id,
        reading_id=reading_id
    )
