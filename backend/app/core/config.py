"""
Configuración de la aplicación.

Todos los valores se leen de variables de entorno, así la misma imagen
de Docker sirve para desarrollo, pruebas y el cluster de Kubernetes.

Ojo: acá NO va la cantidad de minutos de anticipación para pedir.
Ese valor vive en la tabla `configuracion` porque tiene que poder
cambiarse sin volver a desplegar.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Cafetería - API de pedidos"

    # Zona horaria del liceo. Todas las horas de los recreos se interpretan acá.
    app_timezone: str = "America/Montevideo"

    # Qué implementación de repositorios usar: "memory" (por ahora) o "postgres".
    repository_backend: str = "memory"

    # Cadena de conexión a la base. La usa la implementación "postgres".
    database_url: str = ""

    # Autenticación
    jwt_secret: str = "dev-secret-cambiar-en-produccion"
    jwt_algorithm: str = "HS256"
    access_token_expiration_minutes: int = 480

    # Valor inicial de X si la tabla `configuracion` todavía no lo tiene.
    default_order_cutoff_minutes: int = 15

    # Orígenes permitidos para CORS, separados por coma. "*" permite todos.
    cors_allowed_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
