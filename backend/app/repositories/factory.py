"""
Elige qué implementación de repositorios usar según la configuración.

Este es el único lugar que hay que tocar para enchufar la base de datos:
`REPOSITORY_BACKEND` decide entre la implementación en memoria y la de
PostgreSQL. El resto de la aplicación no se entera del cambio.
"""

from app.core.config import Settings
from app.repositories.in_memory import build_in_memory_repositories
from app.repositories.interfaces import Repositories
from app.repositories.postgres import build_postgres_repositories


def build_repositories(settings: Settings) -> Repositories:
    backend = settings.repository_backend.lower()

    if backend == "memory":
        return build_in_memory_repositories()

    if backend == "postgres":
        return build_postgres_repositories(settings.database_url, settings.app_timezone)

    raise ValueError(
        f"REPOSITORY_BACKEND desconocido: '{settings.repository_backend}'. Opciones: memory, postgres."
    )
