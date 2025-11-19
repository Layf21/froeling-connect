"""Test the Facility class."""

import pytest
from aioresponses import aioresponses
from froeling import Froeling, endpoints


@pytest.mark.asyncio
async def test_get_facility(load_json):
    facility_data = load_json('facility.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(endpoints.FACILITY.format(1234), status=200, payload=facility_data)

        async with Froeling(token=token) as api:
            f = await api.get_facilities()

            assert len(f) == 2
            f1, f2 = f

            assert f1.raw == facility_data[0]  # order should be the same, but I wouldn't call it a requirement
            assert f2.raw == facility_data[1]

            assert f1.facility_id == 12345
            assert f1.equipment_number == 100321123
            assert f1.status == 'OK'
            assert f1.name == 'Facility name'
            assert f1.address.street == 'some street'
            assert f1.address.zip == '3210'
            assert f1.address.city == 'somewhere'
            assert f1.address.country == 'DE'
            assert f1.owner == 'Jimmy Smith'
            assert f1.role == 'OWNER'
            assert f1.favorite is False
            assert f1.allow_messages is True
            assert f1.subscribed_notifications is True
            assert (
                f1.picture_url
                == 'https://connect-api.froeling.com/aks/connect/v1.0/resources/service/user/1234/facility/12345/picture'
            )
            assert f1.protocol_3200_info['hoursSinceLastMaintenance'] == '1000'
            assert f1.protocol_3200_info['operationHours'] == '3000'
            assert f1.protocol_3200_info['active'] is False
            assert f1.protocol_3200_info['productType'] == 'T4e 230-250'
            assert f1.protocol_3200_info['status'] == 'OK'
            assert f1.facility_generation == 'GEN_3200'

            assert f2.facility_id == 54321
            assert f2.equipment_number == 100123321
            assert f2.status == 'OK'
            assert f2.name == 'Another facility name'
            assert f2.address.street == 'some street'
            assert f2.address.zip == '3210'
            assert f2.address.city == 'somewhere'
            assert f2.address.country == 'DE'
            assert f2.owner == 'Heisenberg'
            assert f2.role == 'OWNER'
            assert f2.favorite is False
            assert f2.allow_messages is True
            assert f2.subscribed_notifications is True
            assert (
                f2.picture_url
                == 'https://connect-api.froeling.com/aks/connect/v1.0/resources/service/user/1234/facility/12345/picture'
            )
            assert f2.protocol_3200_info['hoursSinceLastMaintenance'] == '2000'
            assert f2.protocol_3200_info['operationHours'] == '200'
            assert f2.protocol_3200_info['active'] is False
            assert f2.protocol_3200_info['productType'] == 'S4 Turbo 60'
            assert f2.protocol_3200_info['status'] == 'OK'
            assert f2.facility_generation == 'GEN_3200'


@pytest.mark.asyncio
async def test_get_facility_modified(load_json):
    facility_data = load_json('facility_modified.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(endpoints.FACILITY.format(1234), status=200, payload=facility_data)

        async with Froeling(token=token) as api:
            f = await api.get_facilities()
            assert len(f) == 3
            f1, f2, f3 = f
            assert f1.raw == facility_data[0]
            assert f2.raw == facility_data[1]
            assert f3.raw == facility_data[2]

            assert f1.facility_id == 12345
            assert f1.equipment_number is None
            assert f1.status == 'OK'
            assert f1.name == 'Facility name'
            assert f1.address.street == 'some street'
            assert f1.address.zip == 'ABCD'
            assert f1.address.city == 'somewhere'
            assert f1.address.country == 'DE'
            assert f1.owner == 'Jimmy Smith'
            assert f1.role == 'OWNER'
            assert f1.favorite is False
            assert f1.allow_messages is True
            assert f1.subscribed_notifications is True
            assert f1.picture_url is None
            assert f1.protocol_3200_info is None
            assert f1.facility_generation == 'GEN_500'

            assert f2.facility_id == 17
            assert f2.equipment_number == 100123321
            assert f2.status == 'OK'
            assert f2.name == 'Another facility name'
            assert f2.address.street is None
            assert f2.address.zip is None
            assert f2.address.city is None
            assert f2.address.country is None
            assert f2.owner == 'Slippy Jim'
            assert f2.role == 'OWNER'
            assert f2.favorite is False
            assert f2.allow_messages is True
            assert f2.subscribed_notifications is True
            assert (
                f2.picture_url
                == 'https://connect-api.froeling.com/aks/connect/v1.0/resources/service/user/1234/facility/12345/picture'
            )
            assert f2.protocol_3200_info['hoursSinceLastMaintenance'] == '2000'
            assert f2.protocol_3200_info['operationHours'] == '200'
            assert f2.protocol_3200_info['active'] is False
            assert f2.protocol_3200_info['productType'] == 'AMG GT 63'
            assert f2.protocol_3200_info['status'] == 'BAD'
            assert f2.facility_generation == 'GEN_3200'

            assert f3.facility_id == 0
            assert f3.equipment_number == -567
            assert f3.status == 'NOTOK'
            assert f3.name == 'Another facility name'
            assert f3.address is None
            assert f3.owner == 'Slippy Jim'
            assert f3.role == 'OWNER'
            assert f3.favorite is False
            assert f3.allow_messages is True
            assert f3.subscribed_notifications is True
            assert (
                f3.picture_url
                == 'https://connect-api.froeling.com/aks/connect/v1.0/resources/service/user/1234/facility/12345/picture'
            )
            assert f3.protocol_3200_info is None
            assert f3.facility_generation == 'GEN_6400'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'component_id,expected',
    [
        (
            '1_100',
            {
                'display_name': 'some display name',
                'display_category': 'Kessel',
                'standard_name': 'Kessel',
                'type': 'BOILER',
                'sub_type': 'WOODCHIP',
            },
        ),
        (
            '300_3100',
            {
                'display_name': 'Circuit 1',
                'display_category': 'Heizkreis',
                'standard_name': 'Heizkreis 01',
                'type': 'CIRCUIT',
                'sub_type': 'OUT_TEMP_CRTL',
            },
        ),
        (
            '300_3110',
            {
                'display_name': 'Circuit 2',
                'display_category': 'Heizkreis',
                'standard_name': 'Heizkreis 02',
                'type': 'CIRCUIT',
                'sub_type': 'OUT_TEMP_CRTL',
            },
        ),
        (
            '200_2100',
            {
                'display_name': 'Boiler 01',
                'display_category': 'Boiler',
                'standard_name': 'Boiler 01',
                'type': 'DHW',
                'sub_type': None,
            },
        ),
        (
            '400_4100',
            {
                'display_name': 'Puffer 01',
                'display_category': 'Puffer',
                'standard_name': 'Puffer 01',
                'type': 'BUFFER_TANK',
                'sub_type': 'NEW_GENERATION',
            },
        ),
    ],
)
async def test_facility_get_components(load_json, component_id, expected):
    facility_data = load_json('facility.json')
    component_list_data = load_json('component_list.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(endpoints.FACILITY.format(1234), status=200, payload=facility_data)
        m.get(
            endpoints.COMPONENT_LIST.format(1234, 12345),
            status=200,
            payload=component_list_data,
        )

        async with Froeling(token=token) as api:
            facilities = await api.get_facilities()
            components = await facilities[0].get_components()

            comp = next(c for c in components if c.component_id == component_id)

            api_data = next(d for d in component_list_data if d["componentId"] == component_id)
            assert comp.raw == api_data

            for field, value in expected.items():
                assert getattr(comp, field) == value
                assert comp.time_windows_view is None
                assert comp.picture_url is None
                assert comp.parameters == {}


@pytest.mark.asyncio
async def test_facility_get_component(load_json):
    facility_data = load_json('facility.json')
    component_data = load_json('component.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(endpoints.FACILITY.format(1234), status=200, payload=facility_data)
        m.get(
            endpoints.COMPONENT.format(1234, 12345, '1_100'),
            status=200,
            payload=component_data,
        )
        m.get(
            endpoints.COMPONENT.format(1234, 12345, '1_100'),
            status=200,
            payload=component_data,
        )

        async with Froeling(token=token) as api:
            f = await api.get_facility(12345)
            assert f.raw == facility_data[0]
            c = f.get_component('1_100')
            assert c.raw == {}
            c2 = api.get_component(12345, '1_100')
            assert c2.raw == {}
            await c.update()
            assert c.raw == component_data
            await c2.update()
            assert c2.raw == component_data
