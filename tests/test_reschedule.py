"""Тесты переноса и отмены записи (US-07, FR-06, FR-07)."""
import pytest
from booking.models import BookingError, Status
from tests.stubs import dt


@pytest.fixture
def booked(service):
    return service.book("C1", "M1", "S60", dt("2026-11-17", "09:00"))


def test_cancel_frees_time(service, booked):
    service.cancel(booked.id, "клиент заболел", user_id="admin1")
    assert booked.status == Status.CANCELLED
    again = service.book("C2", "M1", "S60", dt("2026-11-17", "09:00"))   # время снова свободно
    assert again.slot.start == dt("2026-11-17", "09:00")


def test_cancel_requires_reason(service, booked):
    with pytest.raises(BookingError) as e:
        service.cancel(booked.id, "  ", user_id="admin1")
    assert e.value.code == "NO_REASON"


def test_reschedule_to_free_time_keeps_history(service, booked):
    service.reschedule(booked.id, dt("2026-11-17", "15:00"), user_id="admin1")
    assert booked.slot.start == dt("2026-11-17", "15:00") and booked.slot.minutes == 60
    h = booked.history[-1]
    assert (h.action, h.old_start, h.new_start, h.user_id) == (
        "reschedule", dt("2026-11-17", "09:00"), dt("2026-11-17", "15:00"), "admin1")


def test_reschedule_to_busy_time_rejected(service, booked):
    with pytest.raises(BookingError) as e:
        service.reschedule(booked.id, dt("2026-11-17", "11:30"), user_id="admin1")
    assert e.value.code == "NOT_FREE"
    assert booked.slot.start == dt("2026-11-17", "09:00")      # запись не изменилась


def test_reschedule_cancelled_rejected(service, booked):
    service.cancel(booked.id, "передумал", user_id="admin1")
    with pytest.raises(BookingError) as e:
        service.reschedule(booked.id, dt("2026-11-17", "15:00"), user_id="admin1")
    assert e.value.code == "WRONG_STATUS"
