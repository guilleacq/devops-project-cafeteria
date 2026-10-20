"""
Datos de ejemplo para desarrollo y para la demo.

Solo usa los métodos de las interfaces, así que sirve igual para la
implementación en memoria y para la de PostgreSQL. Si la base ya tiene
datos, no hace nada.

Usuarios de prueba (cambiar antes de la demo pública):

    alumno1@cafeteria.test   / alumno123     → alumno
    alumno2@cafeteria.test   / alumno123     → alumno
    cafeteria@cafeteria.test / cafeteria123  → cafetería
"""

from datetime import time
from functools import lru_cache

from app.core.security import hash_password
from app.domain.models import Product, Recess, Role, User
from app.repositories.interfaces import Repositories


DEMO_USERS = [
    ("Lucía Fernández", "alumno1@cafeteria.test", "alumno123", Role.STUDENT),
    ("Martín Rodríguez", "alumno2@cafeteria.test", "alumno123", Role.STUDENT),
    ("Cafetería", "cafeteria@cafeteria.test", "cafeteria123", Role.CAFETERIA),
]

DEMO_PRODUCTS = [
    ("Medialuna", 35),
    ("Bizcocho", 30),
    ("Alfajor", 50),
    ("Sándwich caliente", 120),
    ("Café", 60),
    ("Café con leche", 70),
    ("Jugo de naranja", 80),
    ("Agua", 45),
]

DEMO_RECESSES = [
    ("Primer recreo", time(9, 30), 15),
    ("Segundo recreo", time(11, 15), 15),
    ("Almuerzo", time(13, 0), 30),
    ("Recreo de la tarde", time(16, 0), 15),
]


def seed_demo_data(repositories: Repositories) -> None:
    if repositories.products.list_all():
        return

    for full_name, email, plain_password, role in DEMO_USERS:
        repositories.users.add(
            User(id=None, full_name=full_name, email=email, password_hash=_hash_demo_password(plain_password), role=role)
        )

    for name, price in DEMO_PRODUCTS:
        repositories.products.add(Product(id=None, name=name, price=price))

    for name, start_time, duration_minutes in DEMO_RECESSES:
        repositories.recesses.add(Recess(id=None, name=name, start_time=start_time, duration_minutes=duration_minutes))


@lru_cache
def _hash_demo_password(plain_password: str) -> str:
    """Calcular un hash es lento a propósito; se calcula una sola vez por contraseña."""
    return hash_password(plain_password)
