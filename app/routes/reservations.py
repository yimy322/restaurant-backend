from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Reservation, ReservationCreate
from app.services.restaurant_service import request_table_reservation

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.get("/", response_model=List[Reservation])
def list_reservations(session: Session = Depends(get_session)):
    return session.exec(select(Reservation)).all()

@router.post("/", response_model=Reservation)
def create_reservation(reservation_in: ReservationCreate, session: Session = Depends(get_session)):
    try:
        return request_table_reservation(
            session=session,
            customer_name=reservation_in.customer_name,
            phone=reservation_in.phone,
            reservation_date=reservation_in.reservation_date,
            reservation_time=reservation_in.reservation_time,
            guests=reservation_in.guests,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))