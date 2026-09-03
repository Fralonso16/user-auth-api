# BaseModel: clase base de Pydantic para crear schemas (validadores de datos)
from pydantic import BaseModel
from typing import Optional


# --- Schemas de usuario ---

# Lo que el usuario envía para REGISTRARSE
class UserCreate(BaseModel):
    username: str
    password: str  # se recibe en texto plano, y en main.py la hasheamos antes de guardarla


# Lo que la API DEVUELVE sobre un usuario (nunca el password, ni siquiera hasheado)
class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


# --- Schema del token ---

# Lo que la API devuelve tras un login correcto
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Schemas de item ---

class ItemCreate(BaseModel):
    title: str


class ItemOut(BaseModel):
    id: int
    title: str
    owner_id: int

    model_config = {"from_attributes": True}