# datetime: para calcular cuándo caduca un token
from datetime import datetime, timedelta, timezone
# CryptContext: gestiona el hasheo y verificación de contraseñas
from passlib.context import CryptContext
# jwt: crea y verifica los tokens JWT; JWTError: error si el token es inválido
from jose import jwt, JWTError

# --- Configuración ---

# SECRET_KEY: una clave secreta usada para "firmar" los tokens, de forma que
# nadie pueda fabricar uno falso sin conocer esta clave.
# En un proyecto real, esto NUNCA se escribe así en el código: se guarda en
# una variable de entorno (archivo .env). Aquí la ponemos directamente
# solo para aprender; en el proyecto 3 veremos cómo hacerlo bien.
import os

# Lee la clave secreta desde una variable de entorno. Si no existe (por
# ejemplo, en tu ordenador en local), usa un valor de respaldo solo para
# desarrollo - en Render, configuraremos la variable real por fuera del
# codigo, para que nunca quede expuesta en el repositorio.
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-de-desarrollo-cambiar-en-produccion")

# ALGORITHM: el algoritmo usado para firmar el token
ALGORITHM = "HS256"

# Cuánto tiempo (en minutos) es válido un token antes de caducar
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context: el objeto que usaremos para hashear y verificar contraseñas,
# usando el algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Funciones de contraseñas ---

def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano en un hash irreversible."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comprueba si una contraseña en texto plano coincide con un hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)


# --- Funciones de tokens JWT ---

def create_access_token(data: dict) -> str:
    """Crea un token JWT firmado, con fecha de caducidad incluida."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Verifica un token y devuelve sus datos, o None si es inválido/caducado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None