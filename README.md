# Restaurant Backend

API para el sistema de un restaurante: menu, horarios, reservas y un endpoint de chat listo para conectar un chatbot con voz.

## Requisitos

- Python 3.10 o superior
- pip

## Instalación y arranque

```bash
cd restaurant-backend

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Levantar el servidor
uvicorn app.main:app --reload
```

Con el servidor corriendo, abre en el navegador:

- **http://localhost:8000/docs** — documentacion interactiva (Swagger UI), para probar cada endpoint sin necesitar el frontend.
- **http://localhost:8000/** — verifica que la API esta viva.

La primera vez que arranca, se crea automaticamente el archivo `restaurant.db` (SQLite) con todas las tablas.

## Estructura del proyecto

```
restaurant-backend/
├── app/
│   ├── main.py                       # punto de entrada, arranca FastAPI
│   ├── database.py                   # conexion al motor SQLite + creacion de tablas
│   ├── models.py                     # entidades: Category, Dish, OpeningHour, Reservation
│   ├── routes/
│   │   ├── categories.py             # GET/POST /api/categories
│   │   ├── dishes.py                 # GET/POST /api/dishes
│   │   ├── opening_hours.py          # GET/POST /api/opening-hours
│   │   ├── reservations.py           # GET/POST /api/reservations
│   │   └── chat.py                   # POST /api/chat (pendiente de conectar el LLM)
│   └── services/
│       └── restaurant_service.py     # get_menu, get_opening_hours, request_table_reservation
├── requirements.txt
└── restaurant.db                     # se genera solo, no se sube a git
```

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Estado de la API |
| GET / POST | `/api/categories/` | Listar / crear categorías |
| GET / POST | `/api/dishes/` | Listar / crear platos |
| GET / POST | `/api/opening-hours/` | Listar / crear horarios de atención |
| GET / POST | `/api/reservations/` | Listar / crear reservas |
| POST | `/api/chat/` | Endpoint del chatbot (pendiente de conectar el LLM) |

## Base de datos

Se usa **SQLite** a través de **SQLModel** (el ORM de Python, equivalente a Hibernate). No requiere instalar ningun motor de base de datos aparte: todo vive en el archivo `restaurant.db`, generado automaticamente al arrancar el servidor.

Cada entidad sigue el patrón `Base` / tabla (`table=True`) / `Create`, similar a separar `Entity` de `DTO` en Spring Boot. Ver `app/models.py`.