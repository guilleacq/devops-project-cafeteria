"""
Pedidos: hacerlos, consultarlos y cambiarles el estado.

Acá se hace cumplir la regla principal del proyecto: un pedido se acepta
solo hasta X minutos antes del recreo. La regla vive en el backend; el
frontend puede avisar antes, pero quien decide es este servicio.
"""

from collections import Counter
from dataclasses import dataclass

from app.core.clock import Clock
from app.domain.errors import (
    InvalidOrderError,
    InvalidStatusChangeError,
    NotFoundError,
    OrderingClosedError,
    PermissionDeniedError,
    ProductSoldOutError,
)
from app.domain.models import Order, OrderItem, OrderStatus, Product, Recess, Role, User
from app.repositories.interfaces import OrderRepository, ProductRepository
from app.services.catalog_service import CatalogService
from app.services.recess_schedule_service import RecessScheduleService


MAX_QUANTITY_PER_PRODUCT = 20

# A qué estados se puede pasar desde cada estado. Solo se avanza, nunca se vuelve atrás.
ALLOWED_STATUS_CHANGES = {
    OrderStatus.PENDING: {OrderStatus.READY, OrderStatus.DELIVERED},
    OrderStatus.READY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
}


@dataclass
class RequestedItem:
    product_id: int
    quantity: int


class OrderService:

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        catalog: CatalogService,
        recess_schedules: RecessScheduleService,
        clock: Clock,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.catalog = catalog
        self.recess_schedules = recess_schedules
        self.clock = clock

    # -----------------------------------------------------------------------
    # Hacer un pedido
    # -----------------------------------------------------------------------

    def place_order(self, student: User, recess_id: int, requested_items: list[RequestedItem]) -> Order:
        """
        Crea un pedido para un recreo de HOY.

        Pasos:
          1. Validar las cantidades.
          2. Verificar que el recreo existe y que todavía se puede pedir.
          3. Verificar que los productos existen y no están agotados.
          4. Guardar el pedido con una copia del precio actual de cada producto.
        """
        quantities_by_product = self._merge_and_validate_quantities(requested_items)

        recess = self.catalog.get_recess(recess_id)
        self._ensure_ordering_is_open(recess)

        order_items = [
            self._build_order_item(product_id, quantity)
            for product_id, quantity in quantities_by_product.items()
        ]

        new_order = Order(
            id=None,
            student_id=student.id,
            recess_id=recess.id,
            service_date=self.clock.today(),
            created_at=self.clock.now(),
            items=order_items,
        )
        return self.order_repository.add(new_order)

    @staticmethod
    def _merge_and_validate_quantities(requested_items: list[RequestedItem]) -> dict[int, int]:
        """Junta las líneas repetidas del mismo producto y valida las cantidades."""
        if not requested_items:
            raise InvalidOrderError("El pedido tiene que tener al menos un producto.")

        quantities_by_product = Counter()

        for item in requested_items:
            if item.quantity <= 0:
                raise InvalidOrderError("Las cantidades tienen que ser mayores que cero.")

            quantities_by_product[item.product_id] += item.quantity

        for quantity in quantities_by_product.values():
            if quantity > MAX_QUANTITY_PER_PRODUCT:
                raise InvalidOrderError(f"No se pueden pedir más de {MAX_QUANTITY_PER_PRODUCT} unidades de un producto.")

        return dict(quantities_by_product)

    def _ensure_ordering_is_open(self, recess: Recess) -> None:
        schedule = self.recess_schedules.schedule_for(recess, self.clock.today())

        if schedule.accepts_orders_at(self.clock.now()):
            return

        recess_start = schedule.starts_at.strftime("%H:%M")
        closing_time = schedule.ordering_closes_at.strftime("%H:%M")

        raise OrderingClosedError(
            f"Ya no se puede pedir para el {recess.name.lower()} de las {recess_start}. "
            f"Los pedidos cerraron a las {closing_time}."
        )

    def _build_order_item(self, product_id: int, quantity: int) -> OrderItem:
        product: Product | None = self.product_repository.get_by_id(product_id)

        if product is None:
            raise NotFoundError(f"No existe el producto {product_id}.")

        if product.is_sold_out:
            raise ProductSoldOutError(f"{product.name} está agotado.")

        return OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
        )

    # -----------------------------------------------------------------------
    # Consultar pedidos
    # -----------------------------------------------------------------------

    def list_orders_of_student(self, student: User) -> list[Order]:
        return self.order_repository.list_by_student(student.id)

    def get_order_for_user(self, order_id: int, user: User) -> Order:
        """Un alumno solo puede ver sus propios pedidos; la cafetería ve todos."""
        order = self._get_order(order_id)

        is_owner = order.student_id == user.id
        is_cafeteria = user.role == Role.CAFETERIA

        if not (is_owner or is_cafeteria):
            raise PermissionDeniedError("No podés ver pedidos de otra persona.")

        return order

    # -----------------------------------------------------------------------
    # Cambiar el estado (lo hace la cafetería)
    # -----------------------------------------------------------------------

    def change_status(self, order_id: int, new_status: OrderStatus) -> Order:
        order = self._get_order(order_id)

        if new_status not in ALLOWED_STATUS_CHANGES[order.status]:
            raise InvalidStatusChangeError(
                f"Un pedido en estado '{order.status.value}' no puede pasar a '{new_status.value}'."
            )

        order.status = new_status
        return self.order_repository.update(order)

    def _get_order(self, order_id: int) -> Order:
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise NotFoundError(f"No existe el pedido {order_id}.")

        return order
