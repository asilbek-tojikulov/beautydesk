"""Драйверы: фикстуры pytest собирают тестируемые компоненты с заглушками."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)
import pytest
from booking.models import Appointment, Status
from booking.rules import BookingRules
from booking.availability import AvailabilityChecker
from booking.service import BookingService
from tests.stubs import StubSchedule, FakeRepository, StubLock, SpyNotifier, dt
from booking.models import TimeSlot

NOW = dt("2026-11-16", "10:00")          # понедельник, «текущее время» теста


@pytest.fixture
def schedule():
    return StubSchedule()


@pytest.fixture
def repo():
    r = FakeRepository(clients=("C1", "C2"))
    # 17.11: у M1 запись 11:00–12:00 и отменённая запись 16:00–17:00
    r.save(Appointment("C2", "M1", "S60", TimeSlot(dt("2026-11-17", "11:00"), dt("2026-11-17", "12:00"))))
    r.save(Appointment("C2", "M1", "S60", TimeSlot(dt("2026-11-17", "16:00"), dt("2026-11-17", "17:00")),
                       status=Status.CANCELLED))
    return r


@pytest.fixture
def rules():
    return BookingRules()


@pytest.fixture
def checker(schedule, repo):
    return AvailabilityChecker(schedule, repo)


@pytest.fixture
def lock():
    return StubLock()


@pytest.fixture
def notifier():
    return SpyNotifier()


@pytest.fixture
def service(rules, checker, schedule, repo, lock, notifier):
    return BookingService(rules, checker, schedule, repo, lock, notifier, clock=lambda: NOW)
