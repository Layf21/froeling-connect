"""Dataclasses relating to Facilities."""

from dataclasses import dataclass

from ..session import Session
from .. import endpoints
from .generics import Address
from .component import Component


@dataclass(frozen=True)
class Facility:
    """Represents data related to a facility."""

    session: Session
    facility_id: int
    equipment_number: int | None
    status: str | None
    name: str | None
    address: Address | None
    owner: str | None
    role: str | None
    favorite: bool | None
    allow_messages: bool | None
    subscribed_notifications: bool | None
    picture_url: str | None
    protocol_3200_info: dict[str, str] | None
    hours_since_last_maintenance: int | None
    operation_hours: int | None
    facility_generation: str | None

    @staticmethod
    def _from_dict(obj: dict, session: Session) -> 'Facility':
        facility_id = obj.get('facilityId')
        assert isinstance(facility_id, int), f'facilityid was not an int.\nobj:{obj}'
        equipment_number = obj.get('equipmentNumber')
        status = obj.get('status')
        name = obj.get('name')
        address_data = obj.get('address')
        address = (
            Address._from_dict(address_data) if isinstance(address_data, dict) else None
        )
        owner = obj.get('owner')
        role = obj.get('role')
        favorite = obj.get('favorite')
        allow_messages = obj.get('allowMessages')
        subscribed_notifications = obj.get('subscribedNotifications')
        picture_url = obj.get('pictureUrl')

        protocol_3200_info = obj.get('protocol3200Info')

        hours_since_last_maintenance: int | None = None
        operation_hours: int | None = None
        if isinstance(protocol_3200_info, dict):
            hslm = protocol_3200_info.get('hoursSinceLastMaintenance')
            if isinstance(hslm, (int, str)):
                try:
                    hours_since_last_maintenance = int(hslm)
                except ValueError:
                    hours_since_last_maintenance = None

            op_hours = protocol_3200_info.get('operationHours')
            if isinstance(op_hours, (int, str)):
                try:
                    operation_hours = int(op_hours)
                except ValueError:
                    operation_hours = None

        facility_generation = obj.get('facilityGeneration')
        return Facility(
            session,
            facility_id,
            equipment_number,
            status,
            name,
            address,
            owner,
            role,
            favorite,
            allow_messages,
            subscribed_notifications,
            picture_url,
            protocol_3200_info,
            hours_since_last_maintenance,
            operation_hours,
            facility_generation,
        )

    @staticmethod
    def _from_list(obj: list, session: Session) -> list['Facility']:
        return [Facility._from_dict(i, session) for i in obj]

    async def get_components(self) -> list[Component | None]:
        """Fetch all components of this facility (not cached)."""
        res = await self.session.request(
            'get',
            endpoints.COMPONENT_LIST.format(self.session.user_id, self.facility_id),
        )
        return [
            Component._from_overview_data(self.facility_id, self.session, i)
            for i in res  # noqa: E501
        ]

    def get_component(self, component_id: str) -> Component:
        """Get a component given it's id.

        Data will not be initialized, call the Component.update method to fetch them.
        """
        return Component(self.facility_id, component_id, self.session)
