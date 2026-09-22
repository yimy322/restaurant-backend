from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.models import Reservation, ReservationCreate
from app.services.restaurant_service import request_table_reservation
from app.security import get_current_admin

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
VALID_STATUSES = ["pending", "confirmed", "cancelled"]

class ReservationStatusUpdate(BaseModel):
    status: str

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

@router.patch("/{reservation_id}/status", response_model=Reservation)
def update_reservation_status(
    reservation_id: int,
    status_update: ReservationStatusUpdate,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    if status_update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(VALID_STATUSES)}",
        )

    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = status_update.status
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation