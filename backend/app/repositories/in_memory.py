"""
Repositorios en memoria.

Guardan los datos en diccionarios de Python. Sirven para desarrollar y
para los tests mientras no existe la base de datos.

Importante: los datos se pierden cada vez que se reinicia el backend.
No cumplen el requisito de persistencia; para eso está la
implementación con PostgreSQL.
"""

import copy
import itertools
from datetime import date

from app.domain.models import Order, Product, Recess, User
from app.repositories.interfaces import (
    OrderRepository,
    ProductRepository,
    RecessRepository,
    Repositories,
    SettingsRepository,
    UserRepository,
)


class _InMemoryStore:
    """
    Base común: un diccionario por id y un contador para los ids nuevos.

    Se guardan y se devuelven copias de las entidades. Así nadie puede
    modificar un dato "guardado" sin pasar por `update`, igual que pasaría
    con una base de datos real.
    """

    def __init__(self):
        self._entities_by_id = {}
        self._id_sequence = itertools.count(start=1)

    def _insert(self, entity):
        entity.id = next(self._id_sequence)
        self._entities_by_id[entity.id] = copy.deepcopy(entity)
        return entity

    def _replace(self, entity):
        if entity.id not in self._entities_by_id:
            raise KeyError(f"No existe una entidad con id {entity.id}.")

        self._entities_by_id[entity.id] = copy.deepcopy(entity)
        return entity

    def _find(self, entity_id):
        entity = self._entities_by_id.get(entity_id)
        return copy.deepcopy(entity) if entity else None

    def _all(self):
        return [copy.deepcopy(entity) for entity in self._entities_by_id.values()]


class InMemoryUserRepository(_InMemoryStore, UserRepository):

    def add(self, user: User) -> User:
        return self._insert(user)

    def get_by_id(self, user_id: int) -> User | None:
        return self._find(user_id)

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()

        for user in self._all():
            if user.email.lower() == normalized_email:
                return user

        return None


class InMemoryProductRepository(_InMemoryStore, ProductRepository):

    def add(self, product: Product) -> Product:
        return self._insert(product)

    def update(self, product: Product) -> Product:
        return self._replace(product)

    def get_by_id(self, product_id: int) -> Product | None:
        return self._find(product_id)

    def list_all(self) -> list[Product]:
        return sorted(self._all(), key=lambda product: product.name)


class InMemoryRecessRepository(_InMemoryStore, RecessRepository):

    def add(self, recess: Recess) -> Recess:
        return self._insert(recess)

    def update(self, recess: Recess) -> Recess:
        return self._replace(recess)

    def get_by_id(self, recess_id: int) -> Recess | None:
        return self._find(recess_id)

    def list_all(self) -> list[Recess]:
        return sorted(self._all(), key=lambda recess: recess.start_time)


class InMemoryOrderRepository(_InMemoryStore, OrderRepository):

    def add(self, order: Order) -> Order:
        return self._insert(order)

    def update(self, order: Order) -> Order:
        return self._replace(order)

    def get_by_id(self, order_id: int) -> Order | None:
        return self._find(order_id)

    def list_by_student(self, student_id: int) -> list[Order]:
        student_orders = [order for order in self._all() if order.student_id == student_id]
        return sorted(student_orders, key=lambda order: order.created_at, reverse=True)

    def list_by_service_date(self, service_date: date) -> list[Order]:
        orders_of_the_day = [order for order in self._all() if order.service_date == service_date]
        return sorted(orders_of_the_day, key=lambda order: order.created_at)


class InMemorySettingsRepository(SettingsRepository):

    def __init__(self):
        self._values_by_key: dict[str, str] = {}

    def get_value(self, key: str) -> str | None:
        return self._values_by_key.get(key)

    def set_value(self, key: str, value: str) -> None:
        self._values_by_key[key] = value


def build_in_memory_repositories() -> Repositories:
    return Repositories(
        users=InMemoryUserRepository(),
        products=InMemoryProductRepository(),
        recesses=InMemoryRecessRepository(),
        orders=InMemoryOrderRepository(),
        settings=InMemorySettingsRepository(),
    )
