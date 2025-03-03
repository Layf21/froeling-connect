import typing
from dataclasses import dataclass
from .generics import Address


@dataclass(frozen=True)
class UserData:
    email: str
    salutation: str
    firstname: str
    surname: str
    address: typing.Optional['Address']
    user_id: int
    lang: str
    role: str
    active: bool
    pictureUrl: str
    facilityCount: int

    @staticmethod
    def from_dict(obj: dict):
        email = obj['userData'].get("email")
        salutation = obj['userData'].get("salutation")
        firstname = obj['userData'].get("firstname")
        surname = obj['userData'].get("surname")
        if obj['userData'].get("address"):
            address = Address.from_dict(obj['userData'].get("address"))
        else:
            address = None
        user_id = obj['userData'].get("userId")
        lang = obj.get("lang")
        role = obj.get("role")
        active = obj.get("active")
        pictureUrl = obj.get("pictureUrl")
        facilityCount = obj.get("facilityCount")
        return UserData(email, salutation, firstname, surname, address, user_id, lang, role, active, pictureUrl,
                        facilityCount)
