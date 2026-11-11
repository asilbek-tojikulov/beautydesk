"""Тест-кейсы «чёрного ящика»: эквивалентное разбиение и граничные значения (раздел 3 отчёта)."""
import pytest
from booking.models import BookingError
from tests.stubs import dt
from tests.conftest import NOW


def code_of(fn):
    with pytest.raises(BookingError) as e:
        fn()
    return e.value.code


# --- У1, У2, У3: правила записи (компонент BookingRules) ---
RULES = [
    ("BB01", dt("2026-11-17", "10:00"), 60, None),        # К1.1 будущее
    ("BB02", dt("2026-11-16", "10:00"), 60, None),        # граница: ровно «сейчас»
    ("BB03", dt("2026-11-16", "09:45"), 60, "PAST"),      # граница: на 15 мин раньше
    ("BB04", dt("2027-01-15", "10:00"), 60, None),        # граница: +60 дней
    ("BB05", dt("2027-01-16", "10:00"), 60, "TOO_FAR"),   # граница: +61 день
    ("BB06", dt("2026-11-17", "10:45"), 60, None),        # минуты кратны 15
    ("BB07", dt("2026-11-17", "10:10"), 60, "GRID"),      # минуты не кратны 15
    ("BB08", dt("2026-11-17", "10:00"), 15, None),        # граница: 15 мин
    ("BB09", dt("2026-11-17", "10:00"), 240, None),       # граница: 240 мин
    ("BB10", dt("2026-11-17", "10:00"), 14, "DURATION"),  # граница: 14 мин
    ("BB11", dt("2026-11-17", "10:00"), 241, "DURATION"), # граница: 241 мин
]


@pytest.mark.parametrize("tc, start, duration, expected", RULES, ids=[r[0] for r in RULES])
def test_rules(rules, tc, start, duration, expected):
    if expected is None:
        rules.check(start, duration, NOW)
    else:
        assert code_of(lambda: rules.check(start, duration, NOW)) == expected


# --- У4, У5, У6: запись через BookingService (смена, перерыв, пересечения, клиент) ---
BOOKING = [
    ("BB12", "C1", dt("2026-11-17", "09:00"), None),        # граница: начало смены
    ("BB13", "C1", dt("2026-11-17", "08:45"), "NOT_FREE"),  # до начала смены
    ("BB14", "C1", dt("2026-11-17", "20:00"), None),        # граница: конец ровно 21:00
    ("BB15", "C1", dt("2026-11-17", "20:15"), "NOT_FREE"),  # конец 21:15 – после смены
    ("BB16", "C1", dt("2026-11-22", "10:00"), "NOT_FREE"),  # воскресенье – выходной
    ("BB17", "C1", dt("2026-11-17", "12:00"), None),        # граница: встык с записью 11–12
    ("BB18", "C1", dt("2026-11-17", "11:45"), "NOT_FREE"),  # пересечение на 15 мин
    ("BB19", "C1", dt("2026-11-17", "13:30"), "NOT_FREE"),  # заходит на перерыв 14–15
    ("BB20", "C1", dt("2026-11-17", "16:00"), None),        # отменённая запись не блокирует
    ("BB21", "C9", dt("2026-11-17", "10:00"), "NO_CLIENT"), # клиента нет в базе
]


@pytest.mark.parametrize("tc, client, start, expected", BOOKING, ids=[r[0] for r in BOOKING])
def test_booking(service, tc, client, start, expected):
    if expected is None:
        a = service.book(client, "M1", "S60", start)
        assert a.slot.start == start and a.slot.minutes == 60
    else:
        assert code_of(lambda: service.book(client, "M1", "S60", start)) == expected
