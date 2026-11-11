"""Тест-кейсы «белого ящика»: базисные пути метода AvailabilityChecker.is_free (раздел 4)."""
from booking.models import TimeSlot
from tests.stubs import dt


def slot(day, a, b):
    return TimeSlot(dt(day, a), dt(day, b))


def test_wb01_path1_day_off(checker):            # 1-2-3-12
    assert checker.is_free("M1", slot("2026-11-22", "10:00", "11:00")) is False


def test_wb02_path2_before_shift(checker):       # 1-2-4-5-12
    assert checker.is_free("M1", slot("2026-11-18", "08:30", "09:30")) is False


def test_wb03_path3_after_shift(checker):        # 1-2-4-6-7-12
    assert checker.is_free("M1", slot("2026-11-18", "20:30", "21:30")) is False


def test_wb04_path4_no_busy(checker):            # 1-2-4-6-8-11-12
    assert checker.is_free("M2", slot("2026-11-18", "10:00", "11:00")) is True


def test_wb05_path5_overlap_first(checker):      # 1-2-4-6-8-9-10-12
    assert checker.is_free("M1", slot("2026-11-18", "14:30", "15:30")) is False


def test_wb06_path6_busy_no_overlap(checker):    # 1-2-4-6-8-9-8-11-12
    assert checker.is_free("M1", slot("2026-11-18", "10:00", "11:00")) is True
