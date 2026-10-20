"""
Entidades del dominio.

Son clases simples de Python: no saben nada de HTTP ni de base de datos.
Un `id` en `None` significa que la entidad todavía no fue guardada;
el repositorio le asigna uno al guardarla.

Glosario:  Recess = recreo  ·  Order = pedido  ·  Product = producto
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class Role(str, Enum):
    STUDENT = "student"
    CAFETERIA = "cafeteria"


class OrderStatus(str, Enum):
    PENDING = "pending"        # el alumno lo hizo, la cafetería todavía no lo preparó
    READY = "ready"            # preparado, esperando que lo retiren
    DELIVERED = "delivered"    # entregado al alumno


@dataclass
class User:
    id: int | None
    full_name: str
    email: str
    password_hash: str
    role: Role


@dataclass
class Product:
    id: int | None
    name: str
    price: int                 # en pesos uruguayos, sin decimales
    is_sold_out: bool = False


@dataclass
class Recess:
    """
    Un recreo que se repite todos los días a la misma hora.

    `start_time` es una hora "de reloj de pared" del liceo (por ejemplo 09:30),
    sin zona horaria. Se combina con la fecha y la zona del liceo para obtener
    un momento exacto (ver `domain/schedule.py`).
    """

    id: int | None
    name: str
    start_time: time
    duration_minutes: int = 15


@dataclass
class OrderItem:
    """
    Una línea del pedido.

    Guarda una copia del nombre y del precio del producto en el momento de
    pedir. Así, si después cambia el precio, el pedido y el resumen de
    ventas siguen mostrando lo que realmente se cobró.
    """

    product_id: int
    product_name: str
    quantity: int
    unit_price: int

    @property
    def subtotal(self) -> int:
        return self.quantity * self.unit_price


@dataclass
class Order:
    id: int | None
    student_id: int
    recess_id: int
    service_date: date         # día del recreo para el que se pidió
    created_at: datetime       # momento exacto en que se hizo, con zona horaria
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING

    @property
    def total(self) -> int:
        return sum(item.subtotal for item in self.items)
