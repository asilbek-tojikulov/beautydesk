"""Компонент 2. AvailabilityChecker – проверка свободного времени мастера (FR-04, FR-05, FR-07)."""
from datetime import timedelta
from .models import TimeSlot, Status


class AvailabilityChecker:
    def __init__(self, schedule, repo):
        self.schedule = schedule
        self.repo = repo

    def is_free(self, master_id: str, slot: TimeSlot, exclude_id=None) -> bool:
        shift = self.schedule.shift_of(master_id, slot.start.date())   # 1
        if shift is None:                                               # 2
            return False                                                # 3
        if slot.start < shift.start:                                    # 4
            return False                                                # 5
        if slot.end > shift.end:                                        # 6
            return False                                                # 7
        for busy in self._busy_slots(master_id, slot.start.date(), exclude_id):  # 8
            if self._overlaps(slot, busy):                              # 9
                return False                                            # 10
        return True                                                     # 11

    def nearest_slots(self, master_id: str, start, minutes: int, n: int = 3, step: int = 15):
        """Ближайшие n свободных окон в тот же день после желаемого времени (FR-05)."""
        result, t = [], start + timedelta(minutes=step)
        shift = self.schedule.shift_of(master_id, start.date())
        while shift and t + timedelta(minutes=minutes) <= shift.end and len(result) < n:
            cand = TimeSlot(t, t + timedelta(minutes=minutes))
            if self.is_free(master_id, cand):
                result.append(cand)
            t += timedelta(minutes=step)
        return result

    def _busy_slots(self, master_id, day, exclude_id=None):
        busy = list(self.schedule.breaks_of(master_id, day))
        busy += [a.slot for a in self.repo.find_by_master_and_day(master_id, day)
                 if a.status not in (Status.CANCELLED, Status.NO_SHOW) and a.id != exclude_id]
        return busy

    @staticmethod
    def _overlaps(a: TimeSlot, b: TimeSlot) -> bool:
        return a.start < b.end and b.start < a.end
