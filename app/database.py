from sqlmodel import SQLModel, create_engine, Session

# es solo un archivo la db
DATABASE_URL = "sqlite:///./restaurant.db"

# echo=True imprime el SQL generado en la consola
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables() -> None:
    """crea todas las tablas definidas en app/models.py si no existen aun."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """se inyecta en cada endpoint con Depends(get_session)."""
    with Session(engine) as session:
        yield session