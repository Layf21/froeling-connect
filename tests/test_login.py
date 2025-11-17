"""Tests the login process and USER endpoint."""

from unittest.mock import Mock

import pytest
from aioresponses import aioresponses
from froeling import Froeling, endpoints, exceptions


@pytest.mark.asyncio
async def test_login_success(load_json):
    login_data = load_json('login.json')
    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.post(
            endpoints.LOGIN,
            status=200,
            payload=login_data,
            headers={'Authorization': token},
        )

        async with Froeling(username='joe', password='pwd') as api:
            userdata = await api.get_userdata()  # should be cached. No new requests
            assert api.token == token
            assert api.user_id == 1234

            assert userdata.email == 'user@example.com'
            assert userdata.salutation == 'MR'
            assert userdata.firstname == 'James'
            assert userdata.surname == 'Doe'
            assert userdata.lang == 'de'
            assert userdata.role == 'USER'
            assert userdata.active is True
            assert (
                userdata.picture_url
                == 'https://connect-api.froeling.com/aks/connect/v1.0/resources/service/user/12345/picture'
            )
            assert userdata.facility_count is None

            assert userdata.address.street == 'Sesame street'
            assert userdata.address.zip == '12345'
            assert userdata.address.city == 'Somewhere'
            assert userdata.address.country == 'DE'


@pytest.mark.asyncio
async def test_login_failure_raises(load_json):
    with aioresponses() as m:
        m.post(endpoints.LOGIN, status=401, payload=load_json('login_bad_creds.json'))

        with pytest.raises(exceptions.AuthenticationError):
            async with Froeling(username='joe', password='pwd'):
                pass


@pytest.mark.asyncio
async def test_request_auto_reauth(load_json):
    login_data = load_json('login.json')
    user_data = load_json('user.json')
    old_token = 'old.eyJ1c2VySWQiOjEyMzR9.signature'
    new_token = 'new.eyJ1c2VySWQiOjEyMzR9.signature'

    mock_token_callback = Mock()

    with aioresponses() as m:
        m.get(endpoints.USER.format(1234), status=401, body='security check failed')
        m.post(
            endpoints.LOGIN,
            status=200,
            payload=login_data,
            headers={'Authorization': new_token},
        )
        m.get(endpoints.USER.format(1234), status=200, payload=user_data)

        async with Froeling(
            username='joe',
            password='pwd',
            token=old_token,
            auto_reauth=True,
            token_callback=mock_token_callback,
        ) as api:
            await api.get_userdata()

        mock_token_callback.assert_called_once_with(new_token)
