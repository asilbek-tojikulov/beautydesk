"""Компонент 1. BookingRules – бизнес-правила записи (FR-03, BR-01, BR-02)."""
from datetime import datetime
from .models import BookingError

HORIZON_DAYS = 60          # BR-01: запись не дальше чем на 60 дней вперёд
GRID_MINUTES = 15          # BR-02: начало записи – по сетке 15 минут
MIN_DURATION, MAX_DURATION = 15, 240   # FR-03: длительность услуги из справочника


class BookingRules:
    def check(self, start: datetime, duration: int, now: datetime) -> None:
        if start < now:
            raise BookingError("PAST", "Нельзя записать на прошедшее время")
        if (start.date() - now.date()).days > HORIZON_DAYS:
            raise BookingError("TOO_FAR", f"Запись возможна не дальше чем на {HORIZON_DAYS} дней")
        if start.minute % GRID_MINUTES != 0 or start.second != 0:
            raise BookingError("GRID", "Время начала должно быть кратно 15 минутам")
        if not (MIN_DURATION <= duration <= MAX_DURATION):
            raise BookingError("DURATION", "Длительность услуги вне допустимого диапазона 15–240 мин")
