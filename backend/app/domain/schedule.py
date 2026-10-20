"""
Horarios: cuándo empieza un recreo, cuándo termina y hasta cuándo se puede pedir.

Este es el corazón de la regla principal del proyecto:

    Un pedido se acepta solo hasta X minutos antes del recreo.

Cómo se manejan las horas:

- Un recreo guarda solo una hora de reloj de pared (por ejemplo 09:30).
- Para saber el momento exacto se combina esa hora con una fecha y con la
  zona horaria del liceo. El resultado es un `datetime` con zona horaria,
  que se puede comparar sin ambigüedad con la hora actual.
- Todo cálculo usa fechas con zona horaria. Nunca se mezclan fechas
  "naive" (sin zona) con fechas con zona.

Todas las funciones de este archivo son puras: reciben todo lo que
necesitan por parámetro y no leen la hora del sistema. Por eso son
fáciles de probar.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.domain.models import Recess


@dataclass(frozen=True)
class RecessSchedule:
    """Los momentos exactos de un recreo en un día concreto."""

    recess: Recess
    service_date: date
    starts_at: datetime
    ends_at: datetime
    ordering_closes_at: datetime

    def accepts_orders_at(self, moment: datetime) -> bool:
        """
        Se puede pedir mientras no se haya llegado a la hora de cierre.

        Ejemplo con un recreo a las 09:30 y X = 15 minutos:
        a las 09:14:59 se puede pedir; desde las 09:15:00 ya no.
        """
        return moment < self.ordering_closes_at

    def has_ended_at(self, moment: datetime) -> bool:
        return moment >= self.ends_at


def build_recess_schedule(
    recess: Recess,
    service_date: date,
    order_cutoff_minutes: int,
    timezone: ZoneInfo,
) -> RecessSchedule:

    starts_at = datetime.combine(service_date, recess.start_time, tzinfo=timezone)
    ends_at = starts_at + timedelta(minutes=recess.duration_minutes)
    ordering_closes_at = starts_at - timedelta(minutes=order_cutoff_minutes)

    return RecessSchedule(
        recess=recess,
        service_date=service_date,
        starts_at=starts_at,
        ends_at=ends_at,
        ordering_closes_at=ordering_closes_at,
    )


def find_next_recess(schedules: list[RecessSchedule], moment: datetime) -> RecessSchedule | None:
    """
    El "próximo recreo" para la pantalla de la cafetería.

    Es el primer recreo del día que todavía no terminó. Se usa el final y
    no el inicio a propósito: mientras el recreo está en curso la cafetería
    está entregando pedidos, y la pantalla no tiene que saltar al siguiente
    recreo justo en ese momento.

    Devuelve `None` si ya terminaron todos los recreos del día.
    """
    schedules_in_order = sorted(schedules, key=lambda schedule: schedule.starts_at)

    for schedule in schedules_in_order:
        if not schedule.has_ended_at(moment):
            return schedule

    return None
