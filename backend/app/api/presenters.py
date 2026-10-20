"""
Convierte entidades del dominio en respuestas de la API.

Mantiene las rutas cortas: cada ruta pide los datos a un servicio y se
los pasa a una de estas funciones para darles forma.
"""

from app.api.schemas import (
    CafeteriaOrderResponse,
    OrderItemResponse,
    OrderResponse,
    ProductResponse,
    RecessResponse,
    RecessTodayResponse,
    UserResponse,
)
from app.domain.models import Order, Product, Recess, User
from app.domain.schedule import RecessSchedule
from app.services.cafeteria_service import CafeteriaOrder


def present_user(user: User) -> UserResponse:
    return UserResponse(id=user.id, full_name=user.full_name, email=user.email, role=user.role)


def present_product(product: Product) -> ProductResponse:
    return ProductResponse(id=product.id, name=product.name, price=product.price, is_sold_out=product.is_sold_out)


def present_recess(recess: Recess) -> RecessResponse:
    return RecessResponse(
        id=recess.id,
        name=recess.name,
        start_time=recess.start_time,
        duration_minutes=recess.duration_minutes,
    )


def present_recess_today(schedule: RecessSchedule, is_accepting_orders: bool) -> RecessTodayResponse:
    recess = schedule.recess

    return RecessTodayResponse(
        id=recess.id,
        name=recess.name,
        start_time=recess.start_time,
        duration_minutes=recess.duration_minutes,
        service_date=schedule.service_date,
        starts_at=schedule.starts_at,
        ends_at=schedule.ends_at,
        ordering_closes_at=schedule.ordering_closes_at,
        is_accepting_orders=is_accepting_orders,
    )


def present_order(order: Order, recess: Recess) -> OrderResponse:
    return OrderResponse(**_order_fields(order, recess))


def present_cafeteria_order(cafeteria_order: CafeteriaOrder, recess: Recess) -> CafeteriaOrderResponse:
    return CafeteriaOrderResponse(
        **_order_fields(cafeteria_order.order, recess),
        student_name=cafeteria_order.student_name,
    )


def _order_fields(order: Order, recess: Recess) -> dict:
    items = [
        OrderItemResponse(
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
        )
        for item in order.items
    ]

    return {
        "id": order.id,
        "status": order.status,
        "recess_id": recess.id,
        "recess_name": recess.name,
        "recess_start_time": recess.start_time,
        "service_date": order.service_date,
        "created_at": order.created_at,
        "items": items,
        "total": order.total,
    }
