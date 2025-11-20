"""Time window datamodels: Weekday, TimeWindowPhase, TimeWindowDay, TimeWindows.

These are immutable value objects and provide helpers to convert to/from the
API representation (lists/dicts with camelCase keys).
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Weekday(Enum):
    """Enumeration of the days of the week."""

    MONDAY = 'MONDAY'
    TUESDAY = 'TUESDAY'
    WEDNESDAY = 'WEDNESDAY'
    THURSDAY = 'THURSDAY'
    FRIDAY = 'FRIDAY'
    SATURDAY = 'SATURDAY'
    SUNDAY = 'SUNDAY'


@dataclass(frozen=True)
class TimeWindowPhase:
    """Represents a time phase within a single day.

    Attributes:
        start_hour (int): Hour when the phase starts (0-23).
        start_minute (int): Minute when the phase starts (0-59).
        end_hour (int): Hour when the phase ends (0-23).
        end_minute (int): Minute when the phase ends (0-59).
        raw (dict): Raw data as received from the API.
    """

    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int
    raw: dict = field(repr=False, default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'startHour': self.start_hour,
            'startMinute': self.start_minute,
            'endHour': self.end_hour,
            'endMinute': self.end_minute,
        }

    @classmethod
    def from_hm(cls, sh: int, sm: int, eh: int, em: int) -> 'TimeWindowPhase':
        """Create a TimeWindowPhase from hour/minute values with validation."""
        cls._validate_bounds(sh, sm, eh, em)
        return cls(sh, sm, eh, em)

    @staticmethod
    def _validate_bounds(sh: int, sm: int, eh: int, em: int) -> None:
        if not (0 <= sh <= 24 and 0 <= eh <= 24):  # noqa: PLR2004
            raise ValueError('hour values must be between 0 and 24')
        if not (0 <= sm <= 59 and 0 <= em <= 59):  # noqa: PLR2004
            raise ValueError('minute values must be between 0 and 59')
        if (eh == 24 and em != 0) or (sh == 24 and sm != 0):  # noqa: PLR2004
            raise ValueError('hour == 24 requires minuite == 0')
        if (eh, em) <= (sh, sm):
            raise ValueError('end time must be after start time')

    def _overlap(self, b: 'TimeWindowPhase') -> bool:
        """Return True if phase a overlaps phase b. Both are within same day."""
        self_start = (self.start_hour, self.start_minute)
        self_end = (self.end_hour, self.end_minute)
        b_start = (b.start_hour, b.start_minute)
        b_end = (b.end_hour, b.end_minute)
        return (self_start < b_end) and (self_end > b_start)

    @classmethod
    def _from_dict(cls, obj: dict) -> 'TimeWindowPhase':
        sh = obj['startHour']
        sm = obj['startMinute']
        eh = obj['endHour']
        em = obj['endMinute']
        if not all(isinstance(v, int) for v in (sh, sm, eh, em)):
            msg = 'TimeWindowPhase hour/minute values must be integers'
            raise TypeError(msg)
        cls._validate_bounds(sh, sm, eh, em)
        return cls(sh, sm, eh, em, obj)

    @classmethod
    def _from_list(cls, obj: list) -> list['TimeWindowPhase']:
        return [cls._from_dict(i) for i in obj]


@dataclass(frozen=True)
class TimeWindowDay:
    """Represents the time window schedule for a single day of the week.

    Attributes:
        id (int): Unique identifier for the day entry.
        weekday (Weekday): The day of the week.
        phases (tuple[TimeWindowPhase,...]): Tuple of phases for this day.
        raw (dict): Raw data as received from the API.
    """

    id: int
    weekday: Weekday
    phases: tuple[TimeWindowPhase, ...]
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def _from_dict(cls, obj: dict) -> 'TimeWindowDay':
        _id = obj['id']
        weekday = Weekday(obj['weekDay'])
        phases = tuple(TimeWindowPhase._from_list(obj.get('phases', [])))  # noqa: SLF001
        return cls(_id, weekday, phases, obj)

    @classmethod
    def _from_list(cls, obj: list) -> list['TimeWindowDay']:
        return [cls._from_dict(i) for i in obj]

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'weekDay': self.weekday.value if isinstance(self.weekday, Weekday) else str(self.weekday),
            'phases': [p.to_dict() for p in self.phases],
        }

    def add_phase(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> 'TimeWindowDay':
        """Return a new TimeWindowDay with an additional phase added."""
        TimeWindowPhase._validate_bounds(start_hour, start_minute, end_hour, end_minute)  # noqa: SLF001
        new_phase = TimeWindowPhase(start_hour, start_minute, end_hour, end_minute)
        for p in self.phases:
            if p._overlap(new_phase):  # noqa: SLF001
                raise ValueError('new phase overlaps existing phase')
        new_phases = (*list(self.phases), new_phase)
        return TimeWindowDay(self.id, self.weekday, new_phases, self.raw)

    def remove_phase(self, index: int) -> 'TimeWindowDay':
        """Return a new TimeWindowDay with the phase at `index` removed."""
        if not (0 <= index < len(self.phases)):
            raise IndexError('phase index out of range')
        new_phases = tuple(p for i, p in enumerate(self.phases) if i != index)
        return TimeWindowDay(self.id, self.weekday, new_phases, self.raw)

    def replace_phase(
        self, index: int, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ) -> 'TimeWindowDay':
        """Return a new TimeWindowDay with the phase at `index` replaced by the provided values."""
        if not (0 <= index < len(self.phases)):
            raise IndexError('phase index out of range')
        TimeWindowPhase._validate_bounds(start_hour, start_minute, end_hour, end_minute)  # noqa: SLF001
        new_phase = TimeWindowPhase(start_hour, start_minute, end_hour, end_minute)
        new_phases = list(self.phases)
        new_phases[index] = new_phase
        return TimeWindowDay(self.id, self.weekday, tuple(new_phases), self.raw)

    def replace_phases(self, new_phases: list[TimeWindowPhase]) -> 'TimeWindowDay':
        """Return a new TimeWindowDay with the provided list of phases."""
        for p in new_phases:
            TimeWindowPhase._validate_bounds(p.start_hour, p.start_minute, p.end_hour, p.end_minute)  # noqa: SLF001
        return TimeWindowDay(self.id, self.weekday, tuple(new_phases), self.raw)


@dataclass(frozen=True)
class TimeWindows:
    """Wrapper around multiple `TimeWindowDay` entries.

    This behaves like a dict and provides helpers to
    convert to/from the API representation (a JSON array of day objects).
    You can only access days by their `Weekday` enum value.
    """

    days: tuple[TimeWindowDay, ...]

    @classmethod
    def _from_list(cls, obj: list) -> 'TimeWindows':
        days = {d.weekday: d for d in TimeWindowDay._from_list(obj)}  # noqa: SLF001
        if len(days) != 7:  # noqa: PLR2004
            raise ValueError('TimeWindows must contain exactly one entry for each weekday')
        return cls(tuple(days.values()))

    def to_list(self) -> list[dict]:
        return [d.to_dict() for d in self.days]

    def __iter__(self) -> Iterator[TimeWindowDay]:
        return iter(self.days)

    def __len__(self) -> int:
        return len(self.days)

    def __getitem__(self, key: Weekday) -> TimeWindowDay:
        """Allow lookup by `Weekday`."""
        for d in self.days:
            if d.weekday == key:
                return d
        msg = f'TimeWindows has no entry for weekday {key}'
        raise KeyError(msg)

    def get(self, key: Weekday, default: Any = None) -> TimeWindowDay | Any:
        """Return the `TimeWindowDay` for `weekday`. Always returns a day (may be a default one)."""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> list[Weekday]:
        return [d.weekday for d in self.days]

    def values(self) -> list[TimeWindowDay]:
        return list(self.days)

    def items(self) -> list[tuple[Weekday, TimeWindowDay]]:
        return [(d.weekday, d) for d in self.days]

    def __contains__(self, key: Weekday) -> bool:
        return any(d.weekday == key for d in self.days)

    @property
    def monday(self) -> TimeWindowDay:
        return self[Weekday.MONDAY]

    @property
    def tuesday(self) -> TimeWindowDay:
        return self[Weekday.TUESDAY]

    @property
    def wednesday(self) -> TimeWindowDay:
        return self[Weekday.WEDNESDAY]

    @property
    def thursday(self) -> TimeWindowDay:
        return self[Weekday.THURSDAY]

    @property
    def friday(self) -> TimeWindowDay:
        return self[Weekday.FRIDAY]

    @property
    def saturday(self) -> TimeWindowDay:
        return self[Weekday.SATURDAY]

    @property
    def sunday(self) -> TimeWindowDay:
        return self[Weekday.SUNDAY]
