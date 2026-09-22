"""Script para inspeccionar rapidamente el contenido de la base de datos SQLite (restaurant.db).
Uso:
    python ver_db.py
"""

import sys
from pathlib import Path
from sqlmodel import Session, select

# Asegurar path y codificación UTF-8 para consola Windows
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.database import engine
from app.models import Category, Dish, OpeningHour, Reservation

def mostrar_reservas(session: Session):
    reservas = session.exec(select(Reservation)).all()
    print("\n" + "="*70)
    print(f"📋 RESERVAS REGISTRADAS EN LA BASE DE DATOS (Total: {len(reservas)})")
    print("="*70)
    if not reservas:
        print("   (No hay reservas registradas todavía)")
    else:
        print(f"{'ID':<5} | {'Cliente':<20} | {'Teléfono':<14} | {'Fecha':<12} | {'Hora':<8} | {'Pers':<5} | {'Estado'}")
        print("-" * 80)
        for r in reservas:
            hora_str = r.reservation_time.strftime("%H:%M") if hasattr(r.reservation_time, "strftime") else str(r.reservation_time)
            fecha_str = str(r.reservation_date)
            print(f"{r.id:<5} | {r.customer_name:<20} | {r.phone:<14} | {fecha_str:<12} | {hora_str:<8} | {r.guests:<5} | {r.status}")

def mostrar_platos(session: Session):
    platos = session.exec(select(Dish)).all()
    print("\n" + "="*70)
    print(f"🍲 PLATOS DEL MENÚ (Total: {len(platos)})")
    print("="*70)
    print(f"{'ID':<4} | {'Nombre':<30} | {'Categoría':<16} | {'Precio'}")
    print("-" * 70)
    for p in platos:
        cat = p.category.name if p.category else "Sin categoría"
        print(f"{p.id:<4} | {p.name:<30} | {cat:<16} | S/. {p.price:.2f}")

def mostrar_horarios(session: Session):
    horarios = session.exec(select(OpeningHour)).all()
    print("\n" + "="*70)
    print(f"🕒 HORARIOS DE ATENCIÓN")
    print("="*70)
    for h in horarios:
        abre = h.open_time.strftime("%H:%M") if hasattr(h.open_time, "strftime") else str(h.open_time)
        cierra = h.close_time.strftime("%H:%M") if hasattr(h.close_time, "strftime") else str(h.close_time)
        print(f"  • {h.day_of_week.capitalize():<12}: {abre} – {cierra}")

if __name__ == "__main__":
    with Session(engine) as session:
        mostrar_reservas(session)
        mostrar_horarios(session)
        mostrar_platos(session)
        print("\n" + "="*70 + "\n")
