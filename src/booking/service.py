"""Компонент 3. BookingService – запись клиента (UC-01), использует компоненты 1 и 2."""
from datetime import timedelta
from .models import Appointment, AppointmentChange, BookingError, Status, TimeSlot


class BookingService:
    def __init__(self, rules, checker, schedule, repo, lock, notifier, clock):
        self.rules, self.checker, self.schedule = rules, checker, schedule
        self.repo, self.lock, self.notifier, self.clock = repo, lock, notifier, clock

    def book(self, client_id, master_id, service_id, start) -> Appointment:
        if not self.repo.client_exists(client_id):
            raise BookingError("NO_CLIENT", "Клиент не найден")
        duration = self.schedule.duration_of(service_id)
        self.rules.check(start, duration, self.clock())
        slot = TimeSlot(start, start + timedelta(minutes=duration))
        if not self.lock.acquire(master_id, slot):
            raise BookingError("LOCKED", "Это время сейчас оформляет другой администратор")
        try:
            if not self.checker.is_free(master_id, slot):
                raise BookingError("NOT_FREE", "Время занято",
                                   self.checker.nearest_slots(master_id, start, duration))
            appointment = Appointment(client_id, master_id, service_id, slot)
            self.repo.save(appointment)
        finally:
            self.lock.release(master_id, slot)
        self.notifier.appointment_created(appointment)
        return appointment

    def cancel(self, appointment_id, reason: str, user_id: str) -> Appointment:
        """Отмена записи с обязательной причиной; время сразу освобождается (FR-07)."""
        a = self._get(appointment_id)
        if not reason or not reason.strip():
            raise BookingError("NO_REASON", "Укажите причину отмены")
        if a.status not in (Status.PLANNED, Status.CONFIRMED):
            raise BookingError("WRONG_STATUS", f"Нельзя отменить запись в статусе «{a.status.value}»")
        a.status = Status.CANCELLED
        a.history.append(AppointmentChange("cancel", a.slot.start, a.slot.start, user_id, reason.strip()))
        self.repo.save(a)
        return a

    def _get(self, appointment_id) -> Appointment:
        a = self.repo.find_by_id(appointment_id)
        if a is None:
            raise BookingError("NOT_FOUND", "Запись не найдена")
        return a
