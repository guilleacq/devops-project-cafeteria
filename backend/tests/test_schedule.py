"""
Pruebas de los cálculos de horario (funciones puras, sin API).
"""

from datetime import date, time, timezone

from app.domain.models import Recess
from app.domain.schedule import build_recess_schedule, find_next_recess
from tests.conftest import MONTEVIDEO, montevideo_time


SERVICE_DATE = date(2026, 10, 20)

first_recess = Recess(id=1, name="Primer recreo", start_time=time(9, 30), duration_minutes=15)
second_recess = Recess(id=2, name="Segundo recreo", start_time=time(11, 15), duration_minutes=15)


def schedule_of(recess: Recess, cutoff_minutes: int = 15):
    return build_recess_schedule(recess, SERVICE_DATE, cutoff_minutes, MONTEVIDEO)


def test_ordering_closes_x_minutes_before_the_recess():
    schedule = schedule_of(first_recess, cutoff_minutes=15)

    assert schedule.starts_at == montevideo_time(9, 30)
    assert schedule.ordering_closes_at == montevideo_time(9, 15)
    assert schedule.ends_at == montevideo_time(9, 45)


def test_orders_are_accepted_until_one_second_before_closing():
    schedule = schedule_of(first_recess, cutoff_minutes=15)

    assert schedule.accepts_orders_at(montevideo_time(9, 14, 59))
    assert not schedule.accepts_orders_at(montevideo_time(9, 15, 0))
    assert not schedule.accepts_orders_at(montevideo_time(9, 40))


def test_comparison_is_correct_even_if_the_moment_comes_in_utc():
    """09:14 en Montevideo son las 12:14 en UTC: tiene que dar el mismo resultado."""
    schedule = schedule_of(first_recess, cutoff_minutes=15)

    twelve_fourteen_utc = montevideo_time(9, 14).astimezone(timezone.utc)
    twelve_sixteen_utc = montevideo_time(9, 16).astimezone(timezone.utc)

    assert twelve_fourteen_utc.hour == 12
    assert schedule.accepts_orders_at(twelve_fourteen_utc)
    assert not schedule.accepts_orders_at(twelve_sixteen_utc)


def test_next_recess_is_the_current_one_while_it_is_still_running():
    schedules = [schedule_of(first_recess), schedule_of(second_recess)]

    during_first_recess = montevideo_time(9, 40)
    after_first_recess = montevideo_time(9, 45)

    assert find_next_recess(schedules, during_first_recess).recess.id == first_recess.id
    assert find_next_recess(schedules, after_first_recess).recess.id == second_recess.id


def test_there_is_no_next_recess_after_the_last_one():
    schedules = [schedule_of(first_recess), schedule_of(second_recess)]

    assert find_next_recess(schedules, montevideo_time(18, 0)) is None
