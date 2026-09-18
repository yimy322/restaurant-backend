from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import OpeningHour, OpeningHourCreate

router = APIRouter(prefix="/api/opening-hours", tags=["opening-hours"])

@router.get("/", response_model=List[OpeningHour])
def list_opening_hours(session: Session = Depends(get_session)):
    return session.exec(select(OpeningHour)).all()

@router.post("/", response_model=OpeningHour)
def create_opening_hour(hour_in: OpeningHourCreate, session: Session = Depends(get_session)):
    opening_hour = OpeningHour.model_validate(hour_in)
    session.add(opening_hour)
    session.commit()
    session.refresh(opening_hour)
    return opening_hour