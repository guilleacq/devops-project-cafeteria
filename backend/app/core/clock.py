"""
El reloj de la aplicación.

Nadie en el código llama a `datetime.now()` directamente: todos piden la
hora a un `Clock`. Esto resuelve dos problemas:

1. Zona horaria: los contenedores corren en UTC. El reloj siempre devuelve
   la hora en la zona del liceo (America/Montevideo), sin depender de cómo
   esté configurado el servidor.

2. Pruebas: en los tests se usa `FixedClock` para simular que son, por
   ejemplo, las 09:14 o las 09:16, sin depender de la hora real.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from zoneinfo import ZoneInfo


class Clock(ABC):

    def __init__(self, timezone: ZoneInfo):
        self.timezone = timezone

    @abstractmethod
    def now(self) -> datetime:
        """Fecha y hora actual, con zona horaria (nunca "naive")."""

    def today(self) -> date:
        return self.now().date()


class SystemClock(Clock):
    """Reloj real, usado en la aplicación."""

    def now(self) -> datetime:
        return datetime.now(self.timezone)


class FixedClock(Clock):
    """Reloj detenido en un momento dado. Pensado para los tests."""

    def __init__(self, fixed_moment: datetime):
        if fixed_moment.tzinfo is None:
            raise ValueError("FixedClock necesita una fecha con zona horaria.")

        super().__init__(timezone=fixed_moment.tzinfo)
        self.fixed_moment = fixed_moment

    def now(self) -> datetime:
        return self.fixed_moment

    def move_to(self, new_moment: datetime) -> None:
        self.fixed_moment = new_moment
