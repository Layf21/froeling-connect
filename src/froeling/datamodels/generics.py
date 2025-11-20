"""Generic datamodels used in multiple places/endpoints."""

from dataclasses import dataclass, field

# Backwards-compat re-exports for moved timewindow types
from froeling.datamodels.timewindow import TimeWindowDay, TimeWindowPhase, Weekday

__all__ = [
    'Address',
    'TimeWindowDay',
    'TimeWindowPhase',
    'Weekday',
]


@dataclass(frozen=True)
class Address:
    """Represents a physical mailing address.

    Attributes:
        street (str): Street name and number.
        zip (int): Postal code.
        city (str): City name.
        country (str): Country name.
        raw (dict): Raw data as received from the API.

    """

    street: str | None
    zip: int | None
    city: str | None
    country: str | None
    raw: dict = field(repr=False, default_factory=dict)

    @staticmethod
    def _from_dict(obj: dict) -> 'Address':
        street = obj.get('street')
        zipcode = obj.get('zip')
        city = obj.get('city')
        country = obj.get('country')
        return Address(street, zipcode, city, country, obj)
