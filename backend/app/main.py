"""
Punto de entrada de la API.

`create_app()` arma la aplicación: crea los objetos compartidos
(configuración, repositorios, reloj), registra las rutas y el manejo de
errores. Los tests llaman a `create_app()` para tener una app nueva y
limpia en cada prueba.
"""

from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.routes import auth, cafeteria, configuration, health, orders, products, recesses
from app.core.clock import Clock, SystemClock
from app.core.config import Settings, get_settings
from app.repositories.factory import build_repositories
from app.repositories.interfaces import Repositories
from app.repositories.seed_data import seed_demo_data


API_PREFIX = "/api"


def create_app(
    settings: Settings | None = None,
    repositories: Repositories | None = None,
    clock: Clock | None = None,
) -> FastAPI:

    settings = settings or get_settings()
    repositories = repositories or build_repositories(settings)
    clock = clock or SystemClock(ZoneInfo(settings.app_timezone))

    seed_demo_data(repositories)

    app = FastAPI(
        title=settings.app_name,
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )

    app.state.settings = settings
    app.state.repositories = repositories
    app.state.clock = clock

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    # Las probes de Kubernetes llaman a /health directamente al contenedor.
    app.include_router(health.router)

    # El resto de la API vive bajo /api, así el Ingress puede mandar
    # /api al backend y todo lo demás al frontend.
    for router_module in (auth, products, recesses, orders, cafeteria, configuration):
        app.include_router(router_module.router, prefix=API_PREFIX)

    return app


app = create_app()
