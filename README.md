# User Auth API

[![Tests](https://github.com/Fralonso16/user-auth-api/actions/workflows/tests.yml/badge.svg)](https://github.com/Fralonso16/user-auth-api/actions/workflows/tests.yml)

API REST con registro, login y autenticación mediante JWT (JSON Web Tokens). Cada usuario solo puede ver y crear sus propios datos, construida como proyecto de práctica para aprender autenticación en backend.

## Tecnologías

- **Python 3**
- **FastAPI** — framework para construir la API
- **SQLAlchemy** — ORM para trabajar con la base de datos
- **SQLite** — base de datos ligera basada en archivo
- **python-jose** — creación y verificación de tokens JWT
- **passlib + bcrypt** — hasheo seguro de contraseñas
- **Uvicorn** — servidor ASGI para ejecutar la aplicación

## Funcionalidades

- Registro de usuarios (contraseñas hasheadas, nunca en texto plano)
- Login con generación de token JWT
- Ruta protegida para consultar el usuario autenticado (`/me`)
- Creación y listado de "items" asociados siempre al usuario autenticado
- Aislamiento de datos: cada usuario solo ve sus propios items
- Documentación interactiva automática (Swagger UI)

## Cómo ejecutarlo en local

1. Clona el repositorio:

git clone https://github.com/Fralonso16/user-auth-api.git
cd user-auth-api


2. Crea y activa un entorno virtual:

python -m venv venv
venv\Scripts\Activate


3. Instala las dependencias:

pip install -r requirements.txt


4. Arranca el servidor:

uvicorn main:app --reload


5. Abre la documentación interactiva en:

http://127.0.0.1:8000/docs


## Cómo ejecutarlo con Docker

No necesitas instalar Python ni nada manualmente, solo tener Docker instalado.

1. Clona el repositorio y entra en la carpeta:

git clone https://github.com/Fralonso16/user-auth-api.git
cd user-auth-api


2. Construye la imagen:

docker build -t user-auth-api .


3. Ejecuta el contenedor:

docker run -p 8000:8000 user-auth-api


4. Abre la documentación interactiva en:

http://127.0.0.1:8000/docs

## Frontend

Este proyecto incluye un frontend simple (HTML/CSS/JavaScript, sin frameworks) en la carpeta `frontend/`, que consume esta misma API: registro, login, y gestión de items del usuario autenticado.

### Cómo ejecutarlo

1. Arranca la API (ver arriba)
2. Abre `frontend/index.html` con la extensión Live Server de VS Code (o cualquier servidor estático)
3. Regístrate, inicia sesión, y crea/consulta tus items desde la interfaz


## Cómo probarlo

1. Regístrate con `POST /register`
2. Inicia sesión con `POST /login` (o usa el botón "Authorize" en `/docs`)
3. Prueba `GET /me`, `POST /items` y `GET /items` ya autenticado

## Estructura del proyecto

user-auth-api/
├── main.py # Rutas de la API (registro, login, rutas protegidas)
├── auth.py # Hasheo de contraseñas y gestion de tokens JWT
├── models.py # Modelos de datos (tablas User e Item)
├── schemas.py # Validacion de datos de entrada/salida
├── database.py # Configuracion de la conexion a la BD
├── requirements.txt # Dependencias del proyecto
└── README.md


## Endpoints

| Método | Ruta       | Protegido | Descripción                          |
|--------|------------|-----------|----------------------------------------|
| POST   | /register  | No        | Registra un usuario nuevo              |
| POST   | /login     | No        | Inicia sesion y devuelve un token JWT  |
| GET    | /me        | Sí        | Devuelve el usuario autenticado        |
| POST   | /items     | Sí        | Crea un item asociado al usuario       |
| GET    | /items     | Sí        | Lista los items del usuario autenticado|

## Nota de seguridad

La clave secreta (`SECRET_KEY`) usada para firmar los tokens está escrita directamente en `auth.py` con fines de aprendizaje. En un proyecto en producción, esta clave debe guardarse en una variable de entorno y nunca subirse al repositorio.