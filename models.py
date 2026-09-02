# Importamos los tipos de columna que vamos a usar
from sqlalchemy import Column, Integer, String, ForeignKey
# relationship nos permite navegar entre tablas relacionadas desde Python
from sqlalchemy.orm import relationship
# Importamos Base, la clase que creamos en database.py
from database import Base


# Tabla "users": cada fila es un usuario registrado
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # username: nombre único con el que el usuario inicia sesión
    # unique=True evita que se puedan registrar dos usuarios con el mismo nombre
    username = Column(String, unique=True, index=True, nullable=False)

    # hashed_password: la contraseña NUNCA se guarda en texto plano,
    # aquí se guarda ya "hasheada" (convertida en un código irreversible)
    hashed_password = Column(String, nullable=False)

    # relationship: no crea una columna en la base de datos, es solo una
    # forma cómoda de acceder desde Python a todos los items de este usuario
    # (ej. user.items te da la lista de sus items)
    items = relationship("Item", back_populates="owner")


# Tabla "items": cada fila es un dato que PERTENECE a un usuario concreto
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # owner_id: clave foránea, guarda el id del usuario propietario de este item
    # ForeignKey("users.id") le dice a la base de datos que este número
    # debe corresponder a un id real de la tabla users
    owner_id = Column(Integer, ForeignKey("users.id"))

    # relationship inversa: desde un item, item.owner te da el objeto User completo
    owner = relationship("User", back_populates="items")