# FastAPI: el framework. Depends: inyecta dependencias. HTTPException: errores.
# status: códigos HTTP legibles (status.HTTP_404_NOT_FOUND en vez de escribir 404)
from fastapi import FastAPI, Depends, HTTPException, status
# OAuth2PasswordBearer: le dice a FastAPI cómo esperar el token en las peticiones
# OAuth2PasswordRequestForm: define el formulario estándar de login (username + password)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import User, Item
from schemas import UserCreate, UserOut, Token, ItemCreate, ItemOut
from auth import hash_password, verify_password, create_access_token, decode_access_token

# Crea las tablas físicamente si no existen aún
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Auth API")

# Le dice a FastAPI que espere el token en la cabecera Authorization,
# y que la ruta para OBTENER ese token es "/login" (usada en la doc interactiva)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Abre una sesión de BD por petición, la cierra al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Dependencia clave: obtener el usuario actual a partir del token ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # Intentamos decodificar el token recibido
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o caducado",
        )

    # "sub" (subject) es el campo estándar de JWT donde guardamos
    # la identidad del usuario (en nuestro caso, su username)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user


# --- Endpoint: registrar un usuario nuevo ---
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Comprobamos que el username no exista ya
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Hasheamos la contraseña ANTES de guardarla, nunca en texto plano
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# --- Endpoint: login, devuelve un token JWT ---
# OAuth2PasswordRequestForm exige que el cliente envie los datos como
# form-data con campos "username" y "password" (no como JSON)
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    # Comprobamos que el usuario existe Y que la contraseña coincide
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    # Creamos el token, guardando el username dentro (campo "sub")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Endpoint protegido: quién soy ---
# Depends(get_current_user) obliga a enviar un token valido para acceder
@app.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# --- Endpoint: crear un item, asociado SIEMPRE al usuario autenticado ---
@app.post("/items", response_model=ItemOut)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = Item(title=item.title, owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# --- Endpoint: listar SOLO los items del usuario autenticado ---
@app.get("/items", response_model=list[ItemOut])
def list_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Item).filter(Item.owner_id == current_user.id).all()