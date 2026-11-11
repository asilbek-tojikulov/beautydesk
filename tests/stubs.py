"""Заглушки (stubs), фиктивные объекты (fakes) и шпионы (spies) для зависимостей компонентов."""
from datetime import datetime, time
from booking.interfaces import IScheduleProvider, IAppointmentRepository, ISlotLock, INotifier
from booking.models import TimeSlot


def dt(day: str, hhmm: str) -> datetime:
    return datetime.fromisoformat(f"{day}T{hhmm}")


class StubSchedule(IScheduleProvider):
    """Смена 09:00–21:00 каждый день, воскресенье – выходной; у M1 перерыв 14:00–15:00."""
    DURATIONS = {"S15": 15, "S60": 60, "S240": 240, "S14": 14, "S241": 241}

    def shift_of(self, master_id, day):
        if day.weekday() == 6:
            return None
        return TimeSlot(datetime.combine(day, time(9, 0)), datetime.combine(day, time(21, 0)))

    def breaks_of(self, master_id, day):
        if master_id == "M1":
            return [TimeSlot(datetime.combine(day, time(14, 0)), datetime.combine(day, time(15, 0)))]
        return []

    def duration_of(self, service_id):
        return self.DURATIONS[service_id]


class FakeRepository(IAppointmentRepository):
    """Хранилище в памяти вместо PostgreSQL."""
    def __init__(self, clients=("C1",)):
        self.items, self.clients = [], set(clients)

    def save(self, appointment):
        self.items.append(appointment)

    def find_by_id(self, appointment_id):
        return next((a for a in self.items if a.id == appointment_id), None)

    def find_by_master_and_day(self, master_id, day):
        return [a for a in self.items if a.master_id == master_id and a.slot.start.date() == day]

    def client_exists(self, client_id):
        return client_id in self.clients


class StubLock(ISlotLock):
    """Заглушка блокировки слота (в системе – Redis). free=False имитирует занятый слот."""
    def __init__(self, free=True):
        self.free, self.acquired, self.released = free, 0, 0

    def acquire(self, master_id, slot):
        self.acquired += 1
        return self.free

    def release(self, master_id, slot):
        self.released += 1


class SpyNotifier(INotifier):
    """Шпион: запоминает, о каких записях было отправлено событие (вместо Celery/Telegram)."""
    def __init__(self):
        self.sent = []

    def appointment_created(self, appointment):
        self.sent.append(appointment)
