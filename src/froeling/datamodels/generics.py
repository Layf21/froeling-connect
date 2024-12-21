from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Address:
    street: str
    zip: int
    city: str
    country: str

    @staticmethod
    def from_dict(obj: dict) -> "Address":
        street = obj.get("street")
        zip = obj.get("zip")
        city = obj.get("city")
        country = obj.get("country")
        return Address(street, zip, city, country)


class Weekday(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


@dataclass
class TimeWindowDay:
    id: int
    weekday: Weekday
    phases: list["TimeWindowPhase"]

    @classmethod
    def from_dict(cls, obj: dict) -> "TimeWindowDay":
        _id = obj["id"]
        weekday = Weekday(obj["weekDay"])
        phases = TimeWindowPhase.from_list(obj["phases"])

        return cls(_id, weekday, phases)

    @classmethod
    def from_list(cls, obj: list) -> list["TimeWindowDay"]:
        return [cls.from_dict(i) for i in obj]


@dataclass
class TimeWindowPhase:
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

    @classmethod
    def from_dict(cls, obj: dict) -> "TimeWindowPhase":
        sh = obj["startHour"]
        sm = obj["startMinute"]
        eh = obj["endHour"]
        em = obj["endMinute"]

        return cls(sh, sm, eh, em)

    @classmethod
    def from_list(cls, obj: list) -> list["TimeWindowPhase"]:
        return [cls.from_dict(i) for i in obj]
