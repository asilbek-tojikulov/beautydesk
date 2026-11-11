"""Интерфейсы зависимостей компонентов (по диаграмме классов ПР 6)."""
from abc import ABC, abstractmethod
from datetime import date


class IScheduleProvider(ABC):
    @abstractmethod
    def shift_of(self, master_id: str, day: date): ...      # TimeSlot или None (выходной)
    @abstractmethod
    def breaks_of(self, master_id: str, day: date) -> list: ...
    @abstractmethod
    def duration_of(self, service_id: str) -> int: ...       # минуты


class IAppointmentRepository(ABC):
    @abstractmethod
    def save(self, appointment): ...
    @abstractmethod
    def find_by_master_and_day(self, master_id: str, day: date) -> list: ...
    @abstractmethod
    def client_exists(self, client_id: str) -> bool: ...


class ISlotLock(ABC):
    @abstractmethod
    def acquire(self, master_id: str, slot) -> bool: ...
    @abstractmethod
    def release(self, master_id: str, slot) -> None: ...


class INotifier(ABC):
    @abstractmethod
    def appointment_created(self, appointment) -> None: ...
