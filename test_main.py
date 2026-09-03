import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base

# Base de datos de PRUEBA, en memoria (no se guarda en ningun archivo,
# desaparece al terminar). Totalmente separada de users.db
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # StaticPool es necesario para que la BD en memoria se mantenga
    # accesible mientras el test esta corriendo (sin esto, cada conexion
    # nueva veria una BD vacia distinta)
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Version de get_db que usa la BD de test en vez de la real."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Le decimos a FastAPI: cuando algo pida get_db, dale esta version en su lugar
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    """
    Se ejecuta automaticamente ANTES y DESPUES de cada test (autouse=True).
    Crea las tablas vacias antes del test, y las borra despues -
    asi cada test empieza siempre desde cero, sin datos de tests anteriores.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def registrar_y_loguear(username: str, password: str) -> str:
    """
    Funcion auxiliar (no es un test en si misma, no empieza por 'test_').
    Registra un usuario y hace login, devolviendo su token.
    La reutilizamos en varios tests para no repetir el mismo codigo.
    """
    client.post("/register", json={"username": username, "password": password})
    login_response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    return login_response.json()["access_token"]


def test_registro_usuario_nuevo():
    """Comprueba que registrarse devuelve el usuario, sin la contraseña."""
    response = client.post(
        "/register",
        json={"username": "test_user_1", "password": "clave12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user_1"
    # Verificamos que la contraseña NUNCA aparece en la respuesta
    assert "password" not in data
    assert "hashed_password" not in data


def test_registro_usuario_duplicado():
    """Comprueba que no se puede registrar dos veces el mismo username."""
    client.post("/register", json={"username": "test_user_2", "password": "clave12345"})
    # Intentamos registrar el mismo username otra vez
    response = client.post("/register", json={"username": "test_user_2", "password": "otraClave"})
    assert response.status_code == 400


def test_login_correcto():
    """Comprueba que el login con credenciales correctas devuelve un token."""
    client.post("/register", json={"username": "test_user_3", "password": "clave12345"})
    response = client.post(
        "/login",
        data={"username": "test_user_3", "password": "clave12345"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_password_incorrecta():
    """Comprueba que el login con contraseña incorrecta se rechaza."""
    client.post("/register", json={"username": "test_user_4", "password": "clave12345"})
    response = client.post(
        "/login",
        data={"username": "test_user_4", "password": "clave_incorrecta"},
    )
    assert response.status_code == 401


def test_ruta_protegida_sin_token():
    """Comprueba que /me rechaza el acceso si no se envia ningun token."""
    response = client.get("/me")
    assert response.status_code == 401


def test_ruta_protegida_con_token():
    """Comprueba que /me funciona correctamente con un token valido."""
    token = registrar_y_loguear("test_user_5", "clave12345")
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_user_5"


def test_crear_item_asociado_al_usuario():
    """Comprueba que un item creado queda asociado al usuario autenticado."""
    token = registrar_y_loguear("test_user_6", "clave12345")
    response = client.post(
        "/items",
        json={"title": "Item de test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Item de test"
    assert "owner_id" in response.json()


def test_aislamiento_entre_usuarios():
    """
    El test mas importante de este proyecto: comprueba que un usuario
    NO puede ver los items de otro usuario, aunque ambos esten autenticados.
    """
    # Creamos dos usuarios distintos
    token_a = registrar_y_loguear("usuario_a", "claveA12345")
    token_b = registrar_y_loguear("usuario_b", "claveB12345")

    # El usuario A crea un item
    client.post(
        "/items",
        json={"title": "Item privado de A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # El usuario B consulta SUS items - no deberia ver el de A
    response = client.get("/items", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    items_de_b = response.json()

    # Ninguno de los items que ve B debe ser el de A
    titulos = [item["title"] for item in items_de_b]
    assert "Item privado de A" not in titulos