"""
Vistas para la cafetería: el próximo recreo, los pedidos del día
agrupados por recreo y el resumen de ventas.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from app.domain.models import Order, OrderStatus
from app.domain.schedule import RecessSchedule
from app.repositories.interfaces import OrderRepository, UserRepository
from app.services.recess_schedule_service import RecessScheduleService


@dataclass
class CafeteriaOrder:
    """Un pedido junto con el nombre del alumno, para saber a quién entregarlo."""

    order: Order
    student_name: str


@dataclass
class ProductQuantity:
    product_name: str
    quantity: int


@dataclass
class RecessOrders:
    schedule: RecessSchedule
    orders: list[CafeteriaOrder]


@dataclass
class NextRecessBoard:
    """Lo que muestra la pantalla de la cafetería."""

    schedule: RecessSchedule
    orders: list[CafeteriaOrder]                     # pendientes y listos (falta entregar)
    products_to_prepare: list[ProductQuantity]       # suma de los pedidos pendientes


@dataclass
class ProductSales:
    product_name: str
    units_sold: int
    revenue: int


@dataclass
class DailySalesSummary:
    service_date: date
    total_orders: int
    delivered_orders: int
    total_revenue: int
    products: list[ProductSales] = field(default_factory=list)


class CafeteriaService:

    def __init__(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        recess_schedules: RecessScheduleService,
    ):
        self.order_repository = order_repository
        self.user_repository = user_repository
        self.recess_schedules = recess_schedules

    # -----------------------------------------------------------------------
    # Pantalla del próximo recreo
    # -----------------------------------------------------------------------

    def next_recess_board(self) -> NextRecessBoard | None:
        """Devuelve `None` si ya no quedan recreos hoy."""
        schedule = self.recess_schedules.next_recess_schedule()

        if schedule is None:
            return None

        orders_of_recess = self._orders_for_recess(schedule)
        orders_to_deliver = [order for order in orders_of_recess if order.status != OrderStatus.DELIVERED]
        pending_orders = [order for order in orders_of_recess if order.status == OrderStatus.PENDING]

        return NextRecessBoard(
            schedule=schedule,
            orders=self._with_student_names(orders_to_deliver),
            products_to_prepare=self._sum_products(pending_orders),
        )

    def _orders_for_recess(self, schedule: RecessSchedule) -> list[Order]:
        orders_of_the_day = self.order_repository.list_by_service_date(schedule.service_date)
        return [order for order in orders_of_the_day if order.recess_id == schedule.recess.id]

    @staticmethod
    def _sum_products(orders: list[Order]) -> list[ProductQuantity]:
        quantity_by_product = defaultdict(int)

        for order in orders:
            for item in order.items:
                quantity_by_product[item.product_name] += item.quantity

        product_quantities = [
            ProductQuantity(product_name=name, quantity=quantity)
            for name, quantity in quantity_by_product.items()
        ]
        return sorted(product_quantities, key=lambda product: product.quantity, reverse=True)

    # -----------------------------------------------------------------------
    # Pedidos del día agrupados por recreo
    # -----------------------------------------------------------------------

    def orders_grouped_by_recess_for_today(self) -> list[RecessOrders]:
        groups = []

        for schedule in self.recess_schedules.schedules_for_today():
            orders_of_recess = self._orders_for_recess(schedule)
            groups.append(RecessOrders(schedule=schedule, orders=self._with_student_names(orders_of_recess)))

        return groups

    # -----------------------------------------------------------------------
    # Resumen de ventas (extra)
    # -----------------------------------------------------------------------

    def daily_sales_summary(self, service_date: date) -> DailySalesSummary:
        orders_of_the_day = self.order_repository.list_by_service_date(service_date)

        units_by_product = defaultdict(int)
        revenue_by_product = defaultdict(int)

        for order in orders_of_the_day:
            for item in order.items:
                units_by_product[item.product_name] += item.quantity
                revenue_by_product[item.product_name] += item.subtotal

        product_sales = [
            ProductSales(product_name=name, units_sold=units_by_product[name], revenue=revenue_by_product[name])
            for name in units_by_product
        ]

        return DailySalesSummary(
            service_date=service_date,
            total_orders=len(orders_of_the_day),
            delivered_orders=sum(1 for order in orders_of_the_day if order.status == OrderStatus.DELIVERED),
            total_revenue=sum(order.total for order in orders_of_the_day),
            products=sorted(product_sales, key=lambda sales: sales.units_sold, reverse=True),
        )

    # -----------------------------------------------------------------------

    def _with_student_names(self, orders: list[Order]) -> list[CafeteriaOrder]:
        cafeteria_orders = []

        for order in orders:
            student = self.user_repository.get_by_id(order.student_id)
            student_name = student.full_name if student else "Alumno desconocido"
            cafeteria_orders.append(CafeteriaOrder(order=order, student_name=student_name))

        return cafeteria_orders
