from dotenv import load_dotenv

load_dotenv()  # carga las variables del archivo .env ANTES de importar los routers de abajo

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routes import auth, categories, chat, dishes, opening_hours, reservations
from fastapi.staticfiles import StaticFiles
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # codigo de arranque: se ejecuta una sola vez, antes de aceptar requests.
    create_db_and_tables()
    seed_database()
    yield

app = FastAPI(title="Restaurant API", lifespan=lifespan)

# permite que el frontend (en otro puerto/dominio) le hable a esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción, cambia esto por el dominio real del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# monta la carpeta "static" para servir archivos estaticos (imagenes, CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static") 

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(dishes.router)
app.include_router(opening_hours.router)
app.include_router(reservations.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Restaurant API corriendo"}