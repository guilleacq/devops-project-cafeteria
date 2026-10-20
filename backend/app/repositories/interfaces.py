"""
Contratos de los repositorios.

Un repositorio es la única parte del código que sabe dónde y cómo se
guardan los datos. Los servicios solo conocen estas interfaces, nunca
una implementación concreta.

Hoy existe una implementación en memoria (`in_memory.py`) para poder
desarrollar y probar sin base de datos. La implementación con PostgreSQL
tiene que respetar exactamente estos mismos métodos; con eso el resto
de la aplicación funciona sin cambios.

Reglas que toda implementación debe cumplir:

- `add(...)` recibe una entidad con `id = None`, la guarda, le asigna un id
  y devuelve la entidad con ese id.
- `update(...)` guarda los cambios de una entidad que ya existe.
- `get_by_...` devuelve `None` si no encuentra nada (no lanza error).
- Los `list_...` devuelven listas, vacías si no hay resultados.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from app.domain.models import Order, Product, Recess, User


class UserRepository(ABC):

    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...


class ProductRepository(ABC):

    @abstractmethod
    def add(self, product: Product) -> Product: ...

    @abstractmethod
    def update(self, product: Product) -> Product: ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    def list_all(self) -> list[Product]:
        """Todos los productos, ordenados por nombre."""


class RecessRepository(ABC):

    @abstractmethod
    def add(self, recess: Recess) -> Recess: ...

    @abstractmethod
    def update(self, recess: Recess) -> Recess: ...

    @abstractmethod
    def get_by_id(self, recess_id: int) -> Recess | None: ...

    @abstractmethod
    def list_all(self) -> list[Recess]:
        """Todos los recreos, ordenados por hora de inicio."""


class OrderRepository(ABC):

    @abstractmethod
    def add(self, order: Order) -> Order:
        """Guarda el pedido junto con todas sus líneas (`items`)."""

    @abstractmethod
    def update(self, order: Order) -> Order:
        """Por ahora solo cambia el estado; las líneas no se modifican."""

    @abstractmethod
    def get_by_id(self, order_id: int) -> Order | None: ...

    @abstractmethod
    def list_by_student(self, student_id: int) -> list[Order]:
        """Pedidos de un alumno, del más nuevo al más viejo."""

    @abstractmethod
    def list_by_service_date(self, service_date: date) -> list[Order]:
        """Pedidos para los recreos de un día, del más viejo al más nuevo."""


class SettingsRepository(ABC):
    """
    Pares clave → valor, guardados como texto (tabla `configuracion`).

    Sirve para valores que tienen que poder cambiarse sin volver a
    desplegar, como los minutos de anticipación para pedir.
    """

    @abstractmethod
    def get_value(self, key: str) -> str | None: ...

    @abstractmethod
    def set_value(self, key: str, value: str) -> None: ...


@dataclass
class Repositories:
    """Agrupa todos los repositorios para pasarlos juntos."""

    users: UserRepository
    products: ProductRepository
    recesses: RecessRepository
    orders: OrderRepository
    settings: SettingsRepository
