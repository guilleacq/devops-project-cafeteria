from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_catalog_service,
    get_clock,
    get_current_user,
    get_recess_schedule_service,
    require_cafeteria,
)
from app.api.presenters import present_recess, present_recess_today
from app.api.schemas import RecessCreateRequest, RecessResponse, RecessTodayResponse, RecessUpdateRequest
from app.core.clock import Clock
from app.services.catalog_service import CatalogService
from app.services.recess_schedule_service import RecessScheduleService

router = APIRouter(prefix="/recesses", tags=["Recreos"])


@router.get("", response_model=list[RecessResponse], dependencies=[Depends(get_current_user)])
def list_recesses(catalog: CatalogService = Depends(get_catalog_service)):
    return [present_recess(recess) for recess in catalog.list_recesses()]


@router.get("/today", response_model=list[RecessTodayResponse], dependencies=[Depends(get_current_user)])
def list_todays_recesses(
    recess_schedules: RecessScheduleService = Depends(get_recess_schedule_service),
    clock: Clock = Depends(get_clock),
):
    """
    Los recreos de hoy con su hora de cierre de pedidos.
    El frontend usa `is_accepting_orders` para habilitar o no el botón de pedir.
    """
    now = clock.now()

    return [
        present_recess_today(schedule, is_accepting_orders=schedule.accepts_orders_at(now))
        for schedule in recess_schedules.schedules_for_today()
    ]


@router.post(
    "",
    response_model=RecessResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_cafeteria)],
)
def create_recess(request: RecessCreateRequest, catalog: CatalogService = Depends(get_catalog_service)):
    new_recess = catalog.create_recess(
        name=request.name,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
    )
    return present_recess(new_recess)


@router.patch("/{recess_id}", response_model=RecessResponse, dependencies=[Depends(require_cafeteria)])
def update_recess(
    recess_id: int,
    request: RecessUpdateRequest,
    catalog: CatalogService = Depends(get_catalog_service),
):
    updated_recess = catalog.update_recess(
        recess_id,
        name=request.name,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
    )
    return present_recess(updated_recess)
