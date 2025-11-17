"""Test the FACILITY endpoint."""

import pytest
from http import HTTPStatus
from aioresponses import aioresponses
from froeling import Froeling, endpoints


@pytest.mark.asyncio
async def test_facility_get_components(load_json):
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
            f = await api.get_facility(12345)
            c = await f.get_components()
            assert len(c) == 5
            c = c[0]

            assert c.component_id == '1_100'
            assert c.display_name == 'some display name'
            assert c.display_category == 'Kessel'
            assert c.standard_name == 'Kessel'
            assert c.type == 'BOILER'
            assert c.sub_type == 'WOODCHIP'


@pytest.mark.asyncio
async def test_component_update(load_json):
    component_data = load_json('component.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(
            endpoints.COMPONENT.format(1234, 12345, '1_100'),
            status=200,
            payload=component_data,
        )

        async with Froeling(token=token) as api:
            c = api.get_component(12345, '1_100')
            await c.update()
            for p in c.parameters.values():
                p.display_value
            # TODO: Add asserts


@pytest.mark.asyncio
async def test_component_set_value(load_json):
    component_data = load_json('component.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(
            endpoints.COMPONENT.format(1234, 12345, '1_100'),
            status=200,
            payload=component_data,
        )
        m.put(
            endpoints.SET_PARAMETER.format(1234, 12345, '3_0'),
            status=HTTPStatus.NOT_MODIFIED,
            payload='successmessage',
        )
        m.put(
            endpoints.SET_PARAMETER.format(1234, 12345, '3_0'),
            status=200,
            payload='successmessage',
        )

        async with Froeling(token=token) as api:
            c = api.get_component(12345, '1_100')
            await c.update()
            msg = await list(c.parameters.values())[0].set_value('testvalue')
            assert msg is None

            msg = await list(c.parameters.values())[0].set_value('testvalue')
            assert msg == 'successmessage'
