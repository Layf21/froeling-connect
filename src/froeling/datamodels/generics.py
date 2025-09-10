"""Generic datamodels used in multiple places/endpoints."""

from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """Represents a physical mailing address.

    Attributes:
        street (str): Street name and number.
        zip (int): Postal code.
        city (str): City name.
        country (str): Country name.

    """

    street: str
    zip: int
    city: str
    country: str

    @staticmethod
    def _from_dict(obj: dict) -> 'Address':
        street: str = obj.get('street', '')
        zipcode: int = obj.get('zip', -1)
        city: str = obj.get('city', '')
        country: str = obj.get('country', '')
        return Address(street, zipcode, city, country)


class Weekday(Enum):
    """Enumeration of the days of the week."""

    MONDAY = 'MONDAY'
    TUESDAY = 'TUESDAY'
    WEDNESDAY = 'WEDNESDAY'
    THURSDAY = 'THURSDAY'
    FRIDAY = 'FRIDAY'
    SATURDAY = 'SATURDAY'
    SUNDAY = 'SUNDAY'


@dataclass
class TimeWindowDay:
    """Represents the time window schedule for a single day of the week.

    Attributes:
        id (int): Unique identifier for the day entry.
        weekday (Weekday): The day of the week.
        phases (list[TimeWindowPhase]): List of time phases for this day.

    """

    id: int
    weekday: Weekday
    phases: list['TimeWindowPhase']

    @classmethod
    def _from_dict(cls, obj: dict) -> 'TimeWindowDay':
        _id = obj['id']
        weekday = Weekday(obj['weekDay'])
        phases = TimeWindowPhase._from_list(obj['phases'])

        return cls(_id, weekday, phases)

    @classmethod
    def _from_list(cls, obj: list) -> list['TimeWindowDay']:
        return [cls._from_dict(i) for i in obj]


@dataclass
class TimeWindowPhase:
    """Represents a time phase within a single day.

    Attributes:
        start_hour (int): Hour when the phase starts (0–23).
        start_minute (int): Minute when the phase starts (0–59).
        end_hour (int): Hour when the phase ends (0–23).
        end_minute (int): Minute when the phase ends (0–59).

    """

    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

    @classmethod
    def _from_dict(cls, obj: dict) -> 'TimeWindowPhase':
        sh = obj['startHour']
        sm = obj['startMinute']
        eh = obj['endHour']
        em = obj['endMinute']

        return cls(sh, sm, eh, em)

    @classmethod
    def _from_list(cls, obj: list) -> list['TimeWindowPhase']:
        return [cls._from_dict(i) for i in obj]
