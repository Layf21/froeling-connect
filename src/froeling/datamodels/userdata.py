"""Datamodels related to the user account."""

from dataclasses import dataclass

from froeling.datamodels.generics import Address


@dataclass(frozen=True)
class UserData:
    """Data relating to the user account."""

    email: str | None
    salutation: str | None
    firstname: str | None
    surname: str | None
    address: Address | None
    user_id: int
    lang: str | None
    role: str | None
    active: bool | None
    picture_url: str | None
    facility_count: int | None

    @staticmethod
    def _from_dict(obj: dict) -> 'UserData':
        user_data = obj['userData']
        email: str | None = user_data.get('email')
        salutation: str | None = user_data.get('salutation')
        firstname: str | None = user_data.get('firstname')
        surname: str | None = user_data.get('surname')

        address: Address | None = Address._from_dict(user_data['address']) if 'address' in user_data else None  # noqa: SLF001

        user_id: int = user_data.get('userId', -1)
        lang: str | None = obj.get('lang')
        role: str | None = obj.get('role')
        active: bool | None = obj.get('active')
        picture_url: str | None = obj.get('pictureUrl')
        facility_count: int | None = obj.get('facilityCount')
        return UserData(
            email,
            salutation,
            firstname,
            surname,
            address,
            user_id,
            lang,
            role,
            active,
            picture_url,
            facility_count,
        )
