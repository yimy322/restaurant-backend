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

## Poblar la base de datos (Seed)

El proyecto incluye un script (`seed.py`) que llena la base de datos con categorías, platos de ejemplo (con sus imágenes) y horarios de atención de lunes a domingo. Es útil para tener datos con los que probar el frontend y el chatbot sin cargar todo a mano.

**1. Configura tus variables de entorno**

Crea un archivo `.env` en la raíz del proyecto (junto a `requirements.txt`) con tu API Key real de Groq:

```dotenv
SECRET_KEY=contra
ADMIN_USERNAME=ADMIN
ADMIN_PASSWORD_HASH=$2b$12$cdv0Fetc6EQv15MJe5n4hOdLHXgW8aEgRLWrMCRb1nqVJiyfDBdZ6
GROQ_API_KEY=gsk_tu_clave_real_aqui
DATABASE_URL=sqlite:///./restaurant.db
```

**2. Corre el script de seed**

Desde la raíz del proyecto (donde está `seed.py`, al mismo nivel que la carpeta `app/`):

```bash
python seed.py
```

Si todo sale bien, verás en consola `Se insertaron 12 platos exitosamente.` y `Horarios de atencion registrados con exito`. El script es seguro de re-ejecutar: si ya existen categorías u horarios, los omite en vez de duplicarlos.

**3. Levanta el servidor** (si no lo tenías corriendo ya)

```bash
uvicorn app.main:app --reload
```

Y verifica que las imágenes cargan correctamente, por ejemplo:
`http://localhost:8000/static/seed-images/dish_1.jpg`

> Si necesitas volver a partir de cero, borra `restaurant.db` antes de correr `seed.py` de nuevo.

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