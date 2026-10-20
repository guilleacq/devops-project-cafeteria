"""
Valores de negocio que se cambian sin volver a desplegar.

Se guardan en la tabla `configuracion` (a través de `SettingsRepository`)
y se leen en cada uso, nunca se guardan en memoria. Por eso un cambio
hecho por la cafetería aplica en el siguiente pedido, sin reiniciar nada.
"""

from app.domain.errors import InvalidSettingError
from app.repositories.interfaces import SettingsRepository


ORDER_CUTOFF_MINUTES_KEY = "order_cutoff_minutes"

MIN_ORDER_CUTOFF_MINUTES = 0
MAX_ORDER_CUTOFF_MINUTES = 240


class ConfigurationService:

    def __init__(self, settings_repository: SettingsRepository, default_order_cutoff_minutes: int):
        self.settings_repository = settings_repository
        self.default_order_cutoff_minutes = default_order_cutoff_minutes

    def get_order_cutoff_minutes(self) -> int:
        """X: cuántos minutos antes del recreo se cierran los pedidos."""
        stored_value = self.settings_repository.get_value(ORDER_CUTOFF_MINUTES_KEY)

        if stored_value is None:
            return self.default_order_cutoff_minutes

        return int(stored_value)

    def update_order_cutoff_minutes(self, new_minutes: int) -> int:
        if not MIN_ORDER_CUTOFF_MINUTES <= new_minutes <= MAX_ORDER_CUTOFF_MINUTES:
            raise InvalidSettingError(
                f"Los minutos de anticipación tienen que estar entre "
                f"{MIN_ORDER_CUTOFF_MINUTES} y {MAX_ORDER_CUTOFF_MINUTES}."
            )

        self.settings_repository.set_value(ORDER_CUTOFF_MINUTES_KEY, str(new_minutes))
        return new_minutes
