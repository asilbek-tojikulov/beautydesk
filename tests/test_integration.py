"""Тесты взаимодействия BookingService с заглушками зависимостей."""
import pytest
from booking.models import BookingError
from tests.stubs import dt


def test_it01_success_saved_notified_unlocked(service, repo, lock, notifier):
    a = service.book("C1", "M1", "S60", dt("2026-11-17", "09:00"))
    assert a in repo.items                       # запись сохранена
    assert notifier.sent == [a]                  # событие для напоминания отправлено 1 раз
    assert lock.acquired == lock.released == 1   # блокировка снята


def test_it02_slot_locked_by_other_admin(service, repo, lock, notifier):
    lock.free = False                            # другой администратор оформляет то же время
    before = len(repo.items)
    with pytest.raises(BookingError) as e:
        service.book("C1", "M1", "S60", dt("2026-11-17", "09:00"))
    assert e.value.code == "LOCKED"
    assert len(repo.items) == before and notifier.sent == []


def test_it03_not_free_suggests_three_nearest(service, lock):
    with pytest.raises(BookingError) as e:
        service.book("C1", "M1", "S60", dt("2026-11-17", "11:45"))
    starts = [s.start.strftime("%H:%M") for s in e.value.suggestions]
    assert starts == ["12:00", "12:15", "12:30"]
    assert lock.released == 1                    # блокировка снята и при ошибке
