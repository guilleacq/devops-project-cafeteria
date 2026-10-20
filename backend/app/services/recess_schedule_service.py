"""
Arma los horarios de los recreos de hoy usando el reloj y la configuración.

Une tres cosas: los recreos guardados, la hora actual (del `Clock`) y X
(de la configuración). Los cálculos en sí están en `domain/schedule.py`.
"""

from datetime import date

from app.core.clock import Clock
from app.domain.models import Recess
from app.domain.schedule import RecessSchedule, build_recess_schedule, find_next_recess
from app.repositories.interfaces import RecessRepository
from app.services.configuration_service import ConfigurationService


class RecessScheduleService:

    def __init__(self, recess_repository: RecessRepository, configuration: ConfigurationService, clock: Clock):
        self.recess_repository = recess_repository
        self.configuration = configuration
        self.clock = clock

    def schedule_for(self, recess: Recess, service_date: date) -> RecessSchedule:
        return build_recess_schedule(
            recess=recess,
            service_date=service_date,
            order_cutoff_minutes=self.configuration.get_order_cutoff_minutes(),
            timezone=self.clock.timezone,
        )

    def schedules_for_today(self) -> list[RecessSchedule]:
        today = self.clock.today()
        return [self.schedule_for(recess, today) for recess in self.recess_repository.list_all()]

    def next_recess_schedule(self) -> RecessSchedule | None:
        return find_next_recess(self.schedules_for_today(), moment=self.clock.now())
