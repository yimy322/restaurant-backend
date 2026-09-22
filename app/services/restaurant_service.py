from datetime import date, time
from typing import List, Optional
from sqlmodel import Session, select
from app.models import Dish, OpeningHour, Reservation

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def get_menu(session: Session, category_name: Optional[str] = None) -> List[dict]:
    """devuelve todos los platos con el nombre de su categoria, permitiendo filtrar por categoria."""
    dishes = session.exec(select(Dish)).all()
    results = [
        {
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "category": dish.category.name if dish.category else None,
        }
        for dish in dishes
    ]
    if category_name:
        results = [d for d in results if d["category"] and category_name.lower() in d["category"].lower()]
    return results

def get_opening_hours(session: Session, day_of_week: Optional[str] = None) -> List[dict]:
    """devuelve el horario de atencion por día de la semana con filtro opcional."""
    hours = session.exec(select(OpeningHour)).all()
    results = [
        {
            "day_of_week": h.day_of_week,
            "open_time": h.open_time.strftime("%H:%M"),
            "close_time": h.close_time.strftime("%H:%M"),
        }
        for h in hours
    ]
    if day_of_week:
        results = [h for h in results if day_of_week.lower() in h["day_of_week"].lower()]
    return results

def request_table_reservation(
    session: Session,
    customer_name: str,
    phone: str,
    reservation_date: date,
    reservation_time: time,
    guests: int,
) -> Reservation:
    """Valida y crea una reserva nueva con estado 'pending'."""
    # 1. Validar numero de personas
    if guests < 1 or guests > 20:
        raise ValueError("El número de personas debe estar entre 1 y 20 comensales.")

    # 2. Validar que la fecha no sea en el pasado
    if reservation_date < date.today():
        raise ValueError("No es posible realizar una reserva en una fecha pasada.")

    # 3. Validar dia de la semana según horarios
    day_name = WEEKDAYS[reservation_date.weekday()]
    opening_hour = session.exec(
        select(OpeningHour).where(OpeningHour.day_of_week == day_name)
    ).first()

    if not opening_hour:
        raise ValueError(f"El restaurante no atiende los días {day_name}.")

    # 4. Validar que la hora este dentro del horario de atencion
    if not (opening_hour.open_time <= reservation_time <= opening_hour.close_time):
        raise ValueError(
            f"Hora fuera de atención. El horario para el día {day_name} es de "
            f"{opening_hour.open_time.strftime('%H:%M')} a {opening_hour.close_time.strftime('%H:%M')}."
        )

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