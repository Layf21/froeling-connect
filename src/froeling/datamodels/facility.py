from dataclasses import dataclass

from .. import endpoints
from ..session import Session
from .component import Component
from .generics import Address


@dataclass(frozen=True)
class Facility:
    session: Session
    facility_id: int
    equipmentNumber: int
    status: str
    name: str
    address: Address
    owner: str
    role: str
    favorite: bool
    allowMessages: bool
    subscribedNotifications: bool
    pictureUrl: str
    protocol3200Info: dict[str, str]
    hoursSinceLastMaintenance: int
    operationHours: int
    facilityGeneration: str

    @staticmethod
    def from_dict(obj: dict, session: Session) -> "Facility":
        facility_id = obj.get("facilityId")
        equipmentNumber = obj.get("equipmentNumber")
        status = obj.get("status")
        name = obj.get("name")
        address = Address.from_dict(obj.get("address"))
        owner = obj.get("owner")
        role = obj.get("role")
        favorite = obj.get("favorite")
        allowMessages = obj.get("allowMessages")
        subscribedNotifications = obj.get("subscribedNotifications")
        pictureUrl = obj.get("pictureUrl")
        protocol3200Info = obj.get("protocol3200Info")
        hoursSinceLastMaintenance = int(protocol3200Info.get("hoursSinceLastMaintenance"))
        operationHours = int(protocol3200Info.get("operationHours"))

        facilityGeneration = obj.get("facilityGeneration")
        return Facility(
            session,
            facility_id,
            equipmentNumber,
            status,
            name,
            address,
            owner,
            role,
            favorite,
            allowMessages,
            subscribedNotifications,
            pictureUrl,
            protocol3200Info,
            hoursSinceLastMaintenance,
            operationHours,
            facilityGeneration,
        )

    @staticmethod
    def from_list(obj: list, session: Session):
        return [Facility.from_dict(i, session) for i in obj]

    async def get_components(self) -> list[Component]:
        res = await self.session.request("get", endpoints.COMPONENT_LIST.format(self.session.user_id, self.facility_id))
        return [Component.from_overview_data(self.facility_id, self.session, i) for i in res]

    def get_component(self, component_id: str):
        return Component(self.facility_id, component_id, self.session)
