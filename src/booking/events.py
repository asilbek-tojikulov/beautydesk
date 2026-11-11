"""BeautyDesk: паттерн «Наблюдатель» для событий журнала записи."""
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookingEvent:                          # что произошло с записью
    type: str                                # CREATED | MOVED | CANCELLED
    client: str
    master: str
    start: datetime


class BookingListener(ABC):                  # Observer
    @abstractmethod
    def on_event(self, e: BookingEvent): ...


class BookingEventBus:                       # Subject
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event_type, listener):
        self._listeners[event_type].append(listener)

    def publish(self, e: BookingEvent):
        for listener in self._listeners[e.type]:
            listener.on_event(e)


class ClientNotifier(BookingListener):       # ConcreteObserver 1
    def on_event(self, e):
        text = {"CREATED": "Вы записаны", "MOVED": "Запись перенесена",
                "CANCELLED": "Запись отменена"}[e.type]
        print(f"  [SMS] {e.client}: {text} – {e.start:%d.%m %H:%M}, мастер {e.master}")


class CalendarCacheUpdater(BookingListener): # ConcreteObserver 2
    def on_event(self, e):
        print(f"  [Кэш] журнал на {e.start:%d.%m} обновлён")


class WorkloadStats(BookingListener):        # ConcreteObserver 3
    def __init__(self):
        self.booked = defaultdict(int)

    def on_event(self, e):
        self.booked[e.master] += 1 if e.type == "CREATED" else -1 if e.type == "CANCELLED" else 0
        print(f"  [Статистика] записей у {e.master}: {self.booked[e.master]}")


class BookingService:                        # источник событий – ничего не знает о подписчиках
    def __init__(self, bus: BookingEventBus):
        self.bus = bus

    def book(self, client, master, start):
        print(f"Запись: {client} → {master}")
        self.bus.publish(BookingEvent("CREATED", client, master, start))

    def cancel(self, client, master, start):
        print(f"Отмена: {client}")
        self.bus.publish(BookingEvent("CANCELLED", client, master, start))


if __name__ == "__main__":
    bus, stats = BookingEventBus(), WorkloadStats()
    for t in ("CREATED", "MOVED", "CANCELLED"):
        bus.subscribe(t, ClientNotifier())
        bus.subscribe(t, CalendarCacheUpdater())
    bus.subscribe("CREATED", stats)
    bus.subscribe("CANCELLED", stats)

    service = BookingService(bus)
    service.book("Азиза Каримова", "Дилноза", datetime(2026, 12, 26, 14, 0))
    service.book("Ирода Алиева", "Дилноза", datetime(2026, 12, 26, 16, 0))
    service.cancel("Ирода Алиева", "Дилноза", datetime(2026, 12, 26, 16, 0))
