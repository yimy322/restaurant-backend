from datetime import date, time
from typing import List
from sqlmodel import Session, select
from app.models import Dish, OpeningHour, Reservation

def get_menu(session: Session) -> List[dict]:
    """devuelve todos los platos con el nombre de su categoria."""
    dishes = session.exec(select(Dish)).all()
    return [
        {
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "category": dish.category.name if dish.category else None,
        }
        for dish in dishes
    ]

def get_opening_hours(session: Session) -> List[dict]:
    """devuelve el horario de atencion por día de la semana."""
    hours = session.exec(select(OpeningHour)).all()
    return [
        {
            "day_of_week": h.day_of_week,
            "open_time": h.open_time.strftime("%H:%M"),
            "close_time": h.close_time.strftime("%H:%M"),
        }
        for h in hours
    ]

def request_table_reservation(
    session: Session,
    customer_name: str,
    phone: str,
    reservation_date: date,
    reservation_time: time,
    guests: int,
) -> Reservation:
    """crea una reserva nueva con estado 'pending'."""
    reservation = Reservation(
        customer_name=customer_name,
        phone=phone,
        reservation_date=reservation_date,
        reservation_time=reservation_time,
        guests=guests,
        status="pending",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation