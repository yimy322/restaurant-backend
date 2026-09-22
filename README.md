# Restaurant Backend

API para el sistema de un restaurante: menu, horarios, reservas, autenticación de administrador y gestión de imágenes de platos.

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

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto (junto a `requirements.txt`):

```dotenv
SECRET_KEY=clave_secreta
ADMIN_USERNAME=ADMIN
ADMIN_PASSWORD_HASH=<hash bcrypt de la contraseña del admin>
DATABASE_URL=sqlite:///./restaurant.db
```

> `GROQ_API_KEY` y `BACKEND_URL` - las usa el asistente de voz (Streamlit).

## Poblar la base de datos (Seed)

El proyecto incluye un script (`seed.py`) que llena la base de datos con categorías, platos de ejemplo (con sus imágenes) y horarios de atención de lunes a domingo. Es útil para tener datos con los que probar el frontend y el chatbot sin cargar todo a mano.

Desde la raíz del proyecto (donde está `seed.py`, al mismo nivel que la carpeta `app/`):

```bash
python seed.py
```

Si todo sale bien, verás en consola `Se insertaron 12 platos exitosamente.` y `Horarios de atencion registrados con exito`. El script es seguro de re-ejecutar: si ya existen categorías u horarios, los omite en vez de duplicarlos.

Con el servidor corriendo, verifica que las imágenes cargan correctamente, por ejemplo:
`http://localhost:8000/static/seed-images/dish_1.jpg`

> Si necesitas volver a partir de cero, borra `restaurant.db` antes de correr `seed.py` de nuevo.

## Estructura del proyecto

```
restaurant-backend/
├── app/
│   ├── main.py                       # punto de entrada, arranca FastAPI
│   ├── database.py                   # conexion al motor SQLite + creacion de tablas
│   ├── models.py                     # entidades: Category, Dish, OpeningHour, Reservation
│   ├── security.py                   # autenticacion admin (JWT, hash de password)
│   ├── routes/
│   │   ├── auth.py                   # POST /api/auth/login
│   │   ├── categories.py             # CRUD /api/categories
│   │   ├── dishes.py                 # CRUD /api/dishes + subida de imagen
│   │   ├── opening_hours.py          # GET/POST /api/opening-hours
│   │   └── reservations.py           # GET/POST/PATCH /api/reservations
│   └── services/
│       └── restaurant_service.py     # get_menu, get_opening_hours, request_table_reservation
├── static/
│   ├── images/                       # imagenes subidas por admin (runtime, no se versiona)
│   └── seed-images/                  # imagenes de ejemplo usadas por seed.py (sí se versiona)
├── seed.py                           # script para poblar la base de datos con datos iniciales
├── requirements.txt
└── restaurant.db                     # se genera solo, no se sube a git
```


## Endpoints disponibles

🔒 = requiere autenticación de administrador (token Bearer obtenido en `/api/auth/login`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Estado de la API |
| POST | `/api/auth/login` | Login de administrador, retorna token |
| GET | `/api/categories/` | Listar categorías |
| POST | `/api/categories/` 🔒 | Crear categoría |
| PUT | `/api/categories/{category_id}` 🔒 | Actualizar categoría |
| DELETE | `/api/categories/{category_id}` 🔒 | Eliminar categoría |
| GET | `/api/dishes/` | Listar platos |
| POST | `/api/dishes/` 🔒 | Crear plato |
| PUT | `/api/dishes/{dish_id}` 🔒 | Actualizar plato |
| DELETE | `/api/dishes/{dish_id}` 🔒 | Eliminar plato |
| POST | `/api/dishes/{dish_id}/image` 🔒 | Subir/actualizar imagen de un plato |
| GET | `/api/opening-hours/` | Listar horarios de atención |
| POST | `/api/opening-hours/` | Crear horario de atención |
| GET | `/api/reservations/` | Listar reservas |
| POST | `/api/reservations/` | Crear reserva (público, lo usa el chatbot) |
| PATCH | `/api/reservations/{reservation_id}/status` 🔒 | Cambiar estado de una reserva (pending/confirmed/cancelled) |

## Base de datos

Se usa **SQLite** a través de **SQLModel** (el ORM de Python, equivalente a Hibernate). No requiere instalar ningun motor de base de datos aparte: todo vive en el archivo `restaurant.db`, generado automaticamente al arrancar el servidor.

Cada entidad sigue el patrón `Base` / tabla (`table=True`) / `Create`, similar a separar `Entity` de `DTO` en Spring Boot. Ver `app/models.py`.
