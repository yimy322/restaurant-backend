from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Reservation, ReservationCreate

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.get("/", response_model=List[Reservation])
def list_reservations(session: Session = Depends(get_session)):
    return session.exec(select(Reservation)).all()

@router.post("/", response_model=Reservation)
def create_reservation(reservation_in: ReservationCreate, session: Session = Depends(get_session)):
    reservation = Reservation.model_validate(reservation_in)
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation