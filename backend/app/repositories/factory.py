"""
Elige qué implementación de repositorios usar según la configuración.

Este es el único lugar que hay que tocar para enchufar la base de datos:
agregar la rama "postgres" que construya los repositorios de PostgreSQL.
"""

from app.core.config import Settings
from app.repositories.in_memory import build_in_memory_repositories
from app.repositories.interfaces import Repositories


def build_repositories(settings: Settings) -> Repositories:
    backend = settings.repository_backend.lower()

    if backend == "memory":
        return build_in_memory_repositories()

    # Cuando exista la implementación con base de datos:
    #
    #     if backend == "postgres":
    #         return build_postgres_repositories(settings.database_url)

    raise ValueError(f"REPOSITORY_BACKEND desconocido: '{settings.repository_backend}'. Opciones: memory.")
