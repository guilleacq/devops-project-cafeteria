from datetime import date

from fastapi import APIRouter, Depends

from app.api.dependencies import get_cafeteria_service, get_clock, require_cafeteria
from app.api.presenters import present_cafeteria_order, present_recess_today
from app.api.schemas import (
    DailySalesSummaryResponse,
    NextRecessBoardResponse,
    ProductQuantityResponse,
    ProductSalesResponse,
    RecessOrdersResponse,
)
from app.core.clock import Clock
from app.services.cafeteria_service import CafeteriaService

router = APIRouter(prefix="/cafeteria", tags=["Cafetería"], dependencies=[Depends(require_cafeteria)])


@router.get("/next-recess", response_model=NextRecessBoardResponse)
def next_recess_board(
    cafeteria_service: CafeteriaService = Depends(get_cafeteria_service),
    clock: Clock = Depends(get_clock),
):
    """
    La pantalla principal de la cafetería: todo lo que falta entregar en el
    próximo recreo y el total de cada producto que hay que preparar.
    """
    board = cafeteria_service.next_recess_board()

    if board is None:
        return NextRecessBoardResponse(
            recess=None,
            orders=[],
            products_to_prepare=[],
            message="No quedan recreos por hoy.",
        )

    recess = board.schedule.recess

    return NextRecessBoardResponse(
        recess=present_recess_today(board.schedule, is_accepting_orders=board.schedule.accepts_orders_at(clock.now())),
        orders=[present_cafeteria_order(cafeteria_order, recess) for cafeteria_order in board.orders],
        products_to_prepare=[
            ProductQuantityResponse(product_name=product.product_name, quantity=product.quantity)
            for product in board.products_to_prepare
        ],
    )


@router.get("/orders-today", response_model=list[RecessOrdersResponse])
def orders_today_grouped_by_recess(
    cafeteria_service: CafeteriaService = Depends(get_cafeteria_service),
    clock: Clock = Depends(get_clock),
):
    """Todos los pedidos de hoy (en cualquier estado), agrupados por recreo."""
    now = clock.now()
    groups = cafeteria_service.orders_grouped_by_recess_for_today()

    return [
        RecessOrdersResponse(
            recess=present_recess_today(group.schedule, is_accepting_orders=group.schedule.accepts_orders_at(now)),
            orders=[present_cafeteria_order(cafeteria_order, group.schedule.recess) for cafeteria_order in group.orders],
        )
        for group in groups
    ]


@router.get("/sales-summary", response_model=DailySalesSummaryResponse)
def daily_sales_summary(
    service_date: date | None = None,
    cafeteria_service: CafeteriaService = Depends(get_cafeteria_service),
    clock: Clock = Depends(get_clock),
):
    """Resumen de ventas de un día. Si no se indica la fecha, es el de hoy."""
    summary = cafeteria_service.daily_sales_summary(service_date or clock.today())

    return DailySalesSummaryResponse(
        service_date=summary.service_date,
        total_orders=summary.total_orders,
        delivered_orders=summary.delivered_orders,
        total_revenue=summary.total_revenue,
        products=[
            ProductSalesResponse(product_name=sales.product_name, units_sold=sales.units_sold, revenue=sales.revenue)
            for sales in summary.products
        ],
    )
