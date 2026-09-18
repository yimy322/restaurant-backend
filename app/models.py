from datetime import date, time
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# por cada entidad hay 3 clases:
#   - base: campos comunes (sin id)
#   - table=True: la tabla real de la base de datos (hereda de Base)
#   - create: lo que se recibe en el body de un POST (hereda de Base)

# categorias
class CategoryBase(SQLModel):
    name: str

class Category(CategoryBase, table=True):
    """Categoria de un plato: entrada, plato fuerte, postre, bebida, etc."""
    __tablename__ = "category"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    dishes: List["Dish"] = Relationship(back_populates="category")

class CategoryCreate(CategoryBase):
    pass

# platos
class DishBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    image_url: Optional[str] = None

class Dish(DishBase, table=True):
    """un plato del menu."""
    __tablename__ = "dish"
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="dishes")

class DishCreate(DishBase):
    pass

# horarios
class OpeningHourBase(SQLModel):
    day_of_week: str  # "monday", "tuesday", ... "sunday"
    open_time: time
    close_time: time

class OpeningHour(OpeningHourBase, table=True):
    """horario de atencion por dia de la semana."""
    __tablename__ = "opening_hour"
    id: Optional[int] = Field(default=None, primary_key=True)

class OpeningHourCreate(OpeningHourBase):
    pass

# reservaciones
class ReservationBase(SQLModel):
    customer_name: str
    phone: str
    reservation_date: date
    reservation_time: time
    guests: int

class Reservation(ReservationBase, table=True):
    """una reserva de mesa hecha por un cliente."""
    __tablename__ = "reservation"
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")  # pending, confirmed, cancelled

class ReservationCreate(ReservationBase):
    pass