from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import OpeningHour, Reservation, ReservationCreate

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

@router.get("/", response_model=List[Reservation])
def list_reservations(session: Session = Depends(get_session)):
    return session.exec(select(Reservation)).all()

@router.post("/", response_model=Reservation)
def create_reservation(reservation_in: ReservationCreate, session: Session = Depends(get_session)):
    # para validar que el dia de la semana sea valido
    day_name = WEEKDAYS[reservation_in.reservation_date.weekday()]

    opening_hour = session.exec(
        select(OpeningHour).where(OpeningHour.day_of_week == day_name)
    ).first()

    if not opening_hour:
        raise HTTPException(status_code=400, detail=f"El restaurante no atiende los {day_name}.")

    # para validar que la hora de la reserva este dentro del horario de apertura
    if not (opening_hour.open_time <= reservation_in.reservation_time <= opening_hour.close_time):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Hora fuera de horario. Atendemos de "
                f"{opening_hour.open_time.strftime('%H:%M')} a "
                f"{opening_hour.close_time.strftime('%H:%M')} ese día."
            ),
        )

    reservation = Reservation.model_validate(reservation_in)
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation