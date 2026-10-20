"""
Dependencias de FastAPI: arman los servicios y obtienen el usuario actual.

Los objetos compartidos (configuración, repositorios y reloj) se crean
una sola vez al iniciar la app y se guardan en `app.state`
(ver `main.py`). Acá se toman de ahí para construir los servicios en
cada pedido HTTP.
"""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.clock import Clock
from app.core.config import Settings
from app.domain.errors import InvalidCredentialsError, PermissionDeniedError
from app.domain.models import Role, User
from app.repositories.interfaces import Repositories
from app.services.auth_service import AuthService
from app.services.cafeteria_service import CafeteriaService
from app.services.catalog_service import CatalogService
from app.services.configuration_service import ConfigurationService
from app.services.order_service import OrderService
from app.services.recess_schedule_service import RecessScheduleService


bearer_token_reader = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Objetos compartidos
# ---------------------------------------------------------------------------

def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_repositories(request: Request) -> Repositories:
    return request.app.state.repositories


def get_clock(request: Request) -> Clock:
    return request.app.state.clock


# ---------------------------------------------------------------------------
# Servicios
# ---------------------------------------------------------------------------

def get_auth_service(
    repositories: Repositories = Depends(get_repositories),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(repositories.users, settings)


def get_configuration_service(
    repositories: Repositories = Depends(get_repositories),
    settings: Settings = Depends(get_settings),
) -> ConfigurationService:
    return ConfigurationService(repositories.settings, settings.default_order_cutoff_minutes)


def get_catalog_service(repositories: Repositories = Depends(get_repositories)) -> CatalogService:
    return CatalogService(repositories.products, repositories.recesses)


def get_recess_schedule_service(
    repositories: Repositories = Depends(get_repositories),
    configuration: ConfigurationService = Depends(get_configuration_service),
    clock: Clock = Depends(get_clock),
) -> RecessScheduleService:
    return RecessScheduleService(repositories.recesses, configuration, clock)


def get_order_service(
    repositories: Repositories = Depends(get_repositories),
    catalog: CatalogService = Depends(get_catalog_service),
    recess_schedules: RecessScheduleService = Depends(get_recess_schedule_service),
    clock: Clock = Depends(get_clock),
) -> OrderService:
    return OrderService(repositories.orders, repositories.products, catalog, recess_schedules, clock)


def get_cafeteria_service(
    repositories: Repositories = Depends(get_repositories),
    recess_schedules: RecessScheduleService = Depends(get_recess_schedule_service),
) -> CafeteriaService:
    return CafeteriaService(repositories.orders, repositories.users, recess_schedules)


# ---------------------------------------------------------------------------
# Usuario actual y roles
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_token_reader),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None:
        raise InvalidCredentialsError("Tenés que iniciar sesión.")

    return auth_service.get_user_from_token(credentials.credentials)


def require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.STUDENT:
        raise PermissionDeniedError("Esta acción es solo para alumnos.")

    return current_user


def require_cafeteria(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.CAFETERIA:
        raise PermissionDeniedError("Esta acción es solo para la cafetería.")

    return current_user
