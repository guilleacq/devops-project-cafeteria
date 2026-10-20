from fastapi import APIRouter, Depends

from app.api.dependencies import get_configuration_service, get_current_user, require_cafeteria
from app.api.schemas import ConfigurationResponse, OrderCutoffUpdateRequest
from app.services.configuration_service import ConfigurationService

router = APIRouter(prefix="/configuration", tags=["Configuración"])


@router.get("", response_model=ConfigurationResponse, dependencies=[Depends(get_current_user)])
def get_configuration(configuration: ConfigurationService = Depends(get_configuration_service)):
    return ConfigurationResponse(order_cutoff_minutes=configuration.get_order_cutoff_minutes())


@router.put("/order-cutoff", response_model=ConfigurationResponse, dependencies=[Depends(require_cafeteria)])
def update_order_cutoff(
    request: OrderCutoffUpdateRequest,
    configuration: ConfigurationService = Depends(get_configuration_service),
):
    """
    Cambia X (minutos antes del recreo en que se cierran los pedidos).
    El cambio aplica desde el siguiente pedido, sin reiniciar ni desplegar.
    """
    new_minutes = configuration.update_order_cutoff_minutes(request.order_cutoff_minutes)
    return ConfigurationResponse(order_cutoff_minutes=new_minutes)
