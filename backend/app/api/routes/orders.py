from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_catalog_service,
    get_current_user,
    get_order_service,
    require_cafeteria,
    require_student,
)
from app.api.presenters import present_order
from app.api.schemas import ErrorResponse, OrderCreateRequest, OrderResponse, OrderStatusUpdateRequest
from app.domain.models import User
from app.services.catalog_service import CatalogService
from app.services.order_service import OrderService, RequestedItem

router = APIRouter(prefix="/orders", tags=["Pedidos"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse, "description": "Pedido inválido o fuera de horario."}},
)
def place_order(
    request: OrderCreateRequest,
    student: User = Depends(require_student),
    order_service: OrderService = Depends(get_order_service),
    catalog: CatalogService = Depends(get_catalog_service),
):
    """
    Hace un pedido para un recreo de hoy.

    Si ya pasó la hora de cierre responde 422 con `code = "ORDERING_CLOSED"`
    y un mensaje que explica hasta qué hora se podía pedir.
    """
    requested_items = [RequestedItem(product_id=item.product_id, quantity=item.quantity) for item in request.items]

    new_order = order_service.place_order(student, request.recess_id, requested_items)
    return present_order(new_order, catalog.get_recess(new_order.recess_id))


@router.get("/mine", response_model=list[OrderResponse])
def list_my_orders(
    student: User = Depends(require_student),
    order_service: OrderService = Depends(get_order_service),
    catalog: CatalogService = Depends(get_catalog_service),
):
    recesses_by_id = catalog.recesses_by_id()

    return [
        present_order(order, recesses_by_id[order.recess_id])
        for order in order_service.list_orders_of_student(student)
    ]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    catalog: CatalogService = Depends(get_catalog_service),
):
    order = order_service.get_order_for_user(order_id, current_user)
    return present_order(order, catalog.get_recess(order.recess_id))


@router.patch("/{order_id}/status", response_model=OrderResponse, dependencies=[Depends(require_cafeteria)])
def change_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    order_service: OrderService = Depends(get_order_service),
    catalog: CatalogService = Depends(get_catalog_service),
):
    """La cafetería marca un pedido como `ready` (listo) o `delivered` (entregado)."""
    updated_order = order_service.change_status(order_id, request.status)
    return present_order(updated_order, catalog.get_recess(updated_order.recess_id))
