import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""Ручной драйвер: вызывает BookingService с заглушками и печатает результат (для отладки)."""
from booking.rules import BookingRules
from booking.availability import AvailabilityChecker
from booking.service import BookingService
from booking.models import BookingError
from tests.stubs import StubSchedule, FakeRepository, StubLock, SpyNotifier, dt

schedule, repo = StubSchedule(), FakeRepository(clients=("C1",))
svc = BookingService(BookingRules(), AvailabilityChecker(schedule, repo), schedule, repo,
                     StubLock(), SpyNotifier(), clock=lambda: dt("2026-11-16", "10:00"))
for start in ["2026-11-17T11:00", "2026-11-17T11:30", "2026-11-17T12:00"]:
    try:
        a = svc.book("C1", "M1", "S60", dt(*start.split("T")))
        print(f"{start}: записан, {a.slot.start:%H:%M}-{a.slot.end:%H:%M}, id={a.id}")
    except BookingError as e:
        print(f"{start}: {e.code} – {e}; варианты: {[f'{s.start:%H:%M}' for s in e.suggestions]}")
