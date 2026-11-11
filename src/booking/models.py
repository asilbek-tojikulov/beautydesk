from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid


class Status(Enum):
    PLANNED = "запланирована"
    CONFIRMED = "подтверждена"
    IN_PROGRESS = "в работе"
    DONE = "завершена"
    CANCELLED = "отменена клиентом"
    NO_SHOW = "неявка"


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("конец интервала должен быть позже начала")

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass
class Appointment:
    client_id: str
    master_id: str
    service_id: str
    slot: TimeSlot
    status: Status = Status.PLANNED
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


class BookingError(Exception):
    def __init__(self, code: str, message: str, suggestions=None):
        super().__init__(message)
        self.code = code
        self.suggestions = suggestions or []
