from dataclasses import dataclass

from .. import endpoints
from ..exceptions import NetworkError
from ..session import Session
from .generics import TimeWindowDay


class Component:
    """Represents a component. Contains its parameters. Remember to call Component.update to populate values."""

    component_id: str
    display_name: str
    display_category: str
    standard_name: str
    type: str
    sub_type: str
    time_windows_view: list[TimeWindowDay]
    picture_url: str

    parameters: list["Parameter"]

    def __init__(self, facility_id: int, component_id: str, session: Session):
        self.facility_id = facility_id
        self.component_id = component_id
        self.session = session

    @classmethod
    def from_overview_data(cls, facility_id: int, session: Session, obj: dict) -> "Component":
        component = cls(facility_id, obj.get("componentId"), session)
        component.display_name = obj.get("displayName")
        component.display_category = obj.get("displayCategory")
        component.standard_name = obj.get("standardName")
        component.type = obj.get("type")
        component.sub_type = obj.get("subType")
        return component

    def __str__(self):
        return f"Component([Facility {self.facility_id}] -> {self.component_id})"

    async def update(self) -> list["Parameter"]:
        res = await self.session.request(
            "get", endpoints.COMPONENT.format(self.session.user_id, self.facility_id, self.component_id)
        )
        self.component_id = res.get("componentId")
        self.display_name = res.get("displayName")
        self.display_category = res.get("displayCategory")
        self.standard_name = res.get("standardName")
        self.type = res.get("type")
        self.sub_type = res.get("subType")
        if res.get("timeWindowsView"):
            self.time_windows_view = TimeWindowDay.from_list(res["timeWindowsView"])

        #  TODO: Find endpoint that gives all parameters
        topview = res.get("topView")

        parameters = dict()
        if topview:
            self.picture_url = topview.get("pictureUrl")
            if "pictureParams" in topview:
                parameters |= topview.get("pictureParams")
            if "infoParams" in topview:
                parameters |= topview.get("infoParams")
            if "configParams" in topview:
                parameters |= topview.get("configParams")
        if "stateView" in res:
            parameters |= {i["name"]: i for i in res.get("stateView")}
        if "setupView" in res:
            parameters |= {i["name"]: i for i in res.get("setupView")}

        self.parameters = Parameter.from_list(parameters.values(), self.session, self.facility_id)
        return self.parameters


@dataclass
class Parameter:
    session: Session
    facility_id: int

    id: str
    display_name: str
    name: str
    editable: bool
    parameter_type: str
    unit: str
    value: str
    min_val: str
    max_val: str
    string_list_key_values: dict[str, str]

    @classmethod
    def from_dict(cls, obj, session: Session, facility_id: int):
        parameter_id = obj["id"]
        display_name = obj.get("displayName")
        name = obj.get("name")
        editable = obj.get("editable")
        parameter_type = obj.get("parameterType")
        unit = obj.get("unit")
        value = obj.get("value")
        min_val = obj.get("minVal")
        max_val = obj.get("maxVal")
        string_list_key_values = obj.get("stringListKeyValues")

        return cls(
            session,
            facility_id,
            parameter_id,
            display_name,
            name,
            editable,
            parameter_type,
            unit,
            value,
            min_val,
            max_val,
            string_list_key_values,
        )

    @classmethod
    def from_list(cls, obj, session: Session, facility_id: int):
        return [cls.from_dict(i, session, facility_id) for i in obj]

    @property
    def display_value(self) -> str:
        if self.string_list_key_values:
            return self.string_list_key_values[str(self.value)]
        if self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)

    async def set_value(self, value):
        """Returns None if value is the same"""
        try:
            return await self.session.request(
                "put",
                endpoints.SET_PARAMETER.format(self.session.user_id, self.facility_id, self.id),
                json={"value": str(value)},
            )
        except NetworkError as exc:
            if exc.status == 304:  # unchanged
                return None
