"""
Preparación común de los tests.

Cada test recibe una app nueva, con repositorios en memoria vacíos (más
los datos de ejemplo) y un reloj detenido que se puede mover a gusto.

Recreos de los datos de ejemplo:
    id 1 → 09:30 · id 2 → 11:15 · id 3 → 13:00 · id 4 → 16:00
X por defecto: 15 minutos.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.core.clock import FixedClock
from app.core.config import Settings
from app.main import create_app


MONTEVIDEO = ZoneInfo("America/Montevideo")

FIRST_RECESS_ID = 1          # 09:30
SECOND_RECESS_ID = 2         # 11:15

MEDIALUNA_ID = 1             # $35
CAFE_ID = 5                  # $60


def montevideo_time(hour: int, minute: int, second: int = 0) -> datetime:
    """Un momento del 20/10/2026 en hora de Montevideo."""
    return datetime(2026, 10, 20, hour, minute, second, tzinfo=MONTEVIDEO)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(montevideo_time(9, 0))


@pytest.fixture
def client(clock: FixedClock) -> TestClient:
    settings = Settings(repository_backend="memory", default_order_cutoff_minutes=15)
    app = create_app(settings=settings, clock=clock)
    return TestClient(app)


def login(client: TestClient, email: str, password: str) -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_headers(client: TestClient) -> dict:
    return login(client, "alumno1@cafeteria.test", "alumno123")


@pytest.fixture
def other_student_headers(client: TestClient) -> dict:
    return login(client, "alumno2@cafeteria.test", "alumno123")


@pytest.fixture
def cafeteria_headers(client: TestClient) -> dict:
    return login(client, "cafeteria@cafeteria.test", "cafeteria123")


def place_order(client: TestClient, headers: dict, recess_id: int = FIRST_RECESS_ID, items: list | None = None):
    items = items or [{"product_id": MEDIALUNA_ID, "quantity": 2}, {"product_id": CAFE_ID, "quantity": 1}]
    return client.post("/api/orders", json={"recess_id": recess_id, "items": items}, headers=headers)
