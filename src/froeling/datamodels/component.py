"""Represents Components and their Parameters."""

from typing import Any
from dataclasses import dataclass

from .. import endpoints
from ..session import Session
from ..exceptions import NetworkError
from .generics import TimeWindowDay


class Component:
    """Represents a facility component.

    A `Component` may be partially or fully populated depending on
    how it was fetched.

    - `get_component` methods only set `facility_id` and `component_id`.
    - `Facility.get_components` populates overview data such as
      `display_name`, `display_category`, `standard_name`, `type`,
      and `sub_type`.
    - Call `Component.update()` to load all available values, including
      parameters and other detailed fields.

    Attributes:
        facility_id (int): ID of the facility this component belongs to.
        component_id (str): Unique identifier for the component.
        display_name (str | None): Human-readable name of the component.
        display_category (str | None): High-level category for grouping components.
        standard_name (str | None): Standardized name, if available.
        type (str | None): Component type.
        sub_type (str | None): More specific component subtype.
        time_windows_view (list[TimeWindowDay] | None): Time window data, if fetched.
        picture_url (str | None): URL to a representative image of the component.
        parameters (list[Parameter]): List of associated parameters.

    """

    facility_id: int
    component_id: str
    display_name: str | None
    display_category: str | None
    standard_name: str | None
    type: str | None
    sub_type: str | None
    time_windows_view: list[TimeWindowDay] | None
    picture_url: str | None

    parameters: list['Parameter']

    def __init__(self, facility_id: int, component_id: str, session: Session):
        """Initialize a Component with minimal identifying information."""
        self.facility_id = facility_id
        self.component_id = component_id
        self._session = session

    @classmethod
    def _from_overview_data(
        cls, facility_id: int, session: Session, obj: dict
    ) -> 'Component' | None:
        """Create a new component and populate it with overview data."""
        component_id = obj.get('componentId')
        if not isinstance(component_id, str):
            return None

        component = cls(facility_id, component_id, session)
        component.display_name = obj.get('displayName')
        component.display_category = obj.get('displayCategory')
        component.standard_name = obj.get('standardName')
        component.type = obj.get('type')
        component.sub_type = obj.get('subType')
        return component

    def __str__(self) -> str:
        """Return a string representation of this component."""
        return f'Component([Facility {self.facility_id}] -> {self.component_id})'

    async def update(self) -> list['Parameter']:
        """Update the Parameters of this component."""
        res = await self._session.request(
            'get',
            endpoints.COMPONENT.format(
                self._session.user_id, self.facility_id, self.component_id
            ),
        )
        self.component_id = res.get('componentId')  # This should not be able to change.
        self.display_name = res.get('displayName')
        self.display_category = res.get('displayCategory')
        self.standard_name = res.get('standardName')
        self.type = res.get('type')
        self.sub_type = res.get('subType')
        if res.get('timeWindowsView'):
            self.time_windows_view = TimeWindowDay._from_list(res['timeWindowsView'])

        #  TODO: Find endpoint that gives all parameters
        topview = res.get('topView')

        parameters: dict[str, dict] = dict()
        if topview:
            self.picture_url = topview.get('pictureUrl')
            if 'pictureParams' in topview:
                parameters |= topview.get('pictureParams')
            if 'infoParams' in topview:
                parameters |= topview.get('infoParams')
            if 'configParams' in topview:
                parameters |= topview.get('configParams')
        if 'stateView' in res:
            parameters |= {i['name']: i for i in res.get('stateView')}
        if 'setupView' in res:
            parameters |= {i['name']: i for i in res.get('setupView')}

        self.parameters = Parameter._from_list(
            list(parameters.values()), self._session, self.facility_id
        )
        return self.parameters


@dataclass
class Parameter:
    """Represents a parameter (a value) of a component."""

    session: Session
    facility_id: int

    id: str | None
    display_name: str | None
    name: str | None
    editable: bool | None
    parameter_type: str | None
    unit: str | None
    value: str | None
    min_val: str | None
    max_val: str | None
    string_list_key_values: dict[str, str] | None

    @classmethod
    def _from_dict(cls, obj: dict, session: Session, facility_id: int) -> 'Parameter':
        parameter_id = obj['id']
        display_name = obj.get('displayName')
        name = obj.get('name')
        editable = obj.get('editable')
        parameter_type = obj.get('parameterType')
        unit = obj.get('unit')
        value = obj.get('value')
        min_val = obj.get('minVal')
        max_val = obj.get('maxVal')
        string_list_key_values = obj.get('stringListKeyValues')

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
    def _from_list(
        cls, obj: list[dict], session: Session, facility_id: int
    ) -> list['Parameter']:
        """Turn a list of api response dicts into a list of parameter object."""
        return [cls._from_dict(i, session, facility_id) for i in obj]

    @property
    def display_value(self) -> str:
        """Combine the value with it's unit."""
        if self.string_list_key_values:
            return self.string_list_key_values[str(self.value)]
        if self.unit:
            return f'{self.value} {self.unit}'
        return str(self.value)

    async def set_value(self, value: Any) -> Any | None:
        """Set the value of this parameter.

        Be careful with this, don't change parameters if you don't know what they do.
        You might want to check Parameter.editable together with this.
        Returns None if the value was already the same.
        """
        try:
            return await self.session.request(
                'put',
                endpoints.SET_PARAMETER.format(
                    self.session.user_id, self.facility_id, self.id
                ),
                json={'value': str(value)},
            )
        except NetworkError as e:
            if e.status == 304:  # unchanged
                return None
            raise e
