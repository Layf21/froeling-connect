"""Test notifications."""

import pytest
from aioresponses import aioresponses
import datetime
from froeling import Froeling, endpoints
from froeling.datamodels.notifications import NotificationSubmissionState


@pytest.mark.asyncio
async def test_get_notification_count(load_json):
    notification_count_data = load_json('notification_count.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(
            endpoints.NOTIFICATION_COUNT.format(1234),
            status=200,
            payload=notification_count_data,
        )

        async with Froeling(token=token) as api:
            count = await api.get_notification_count()
            assert count == 123


@pytest.mark.asyncio
async def test_get_notifications(load_json):
    notification_list_data = load_json('notification_list.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    date = datetime.datetime(
        2025, 1, 2, 12, 34, 56, 789000, tzinfo=datetime.timezone.utc
    )

    with aioresponses() as m:
        m.get(
            endpoints.NOTIFICATION_LIST.format(1234),
            status=200,
            payload=notification_list_data,
        )

        async with Froeling(token=token) as api:
            notifications = await api.get_notifications()
            assert len(notifications) == 3
            for i, n in enumerate(notifications):
                assert n.raw == notification_list_data[i]

                assert n.id == (i + 1) * 10000000 + 123456
                assert n.subject == f'Subject {i + 1}'
                assert n.unread == (False, True, None)[i]
                assert n.date == date
                assert n.error_id == (None, 0, 404)[i]
                assert n.type == ('INFO', 'ALARM', 'ERROR')[i]
                assert n.facility_id == (12345, None, None)[i]
                assert n.facility_name == ('F1', None, None)[i]


@pytest.mark.asyncio
async def test_get_notification_info(load_json):
    notification_list_data = load_json('notification_list.json')
    notification_data = load_json('notification.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    date = datetime.datetime(
        2025, 1, 2, 12, 34, 56, 789000, tzinfo=datetime.timezone.utc
    )

    with aioresponses() as m:
        m.get(
            endpoints.NOTIFICATION_LIST.format(1234),
            status=200,
            payload=notification_list_data,
        )
        m.get(
            endpoints.NOTIFICATION.format(1234, 10123456),
            status=200,
            payload=notification_data,
        )
        m.get(
            endpoints.NOTIFICATION.format(1234, 10123456),
            status=200,
            payload=notification_data,
        )

        async with Froeling(token=token) as api:
            notification = (await api.get_notifications())[0]
            notification_details = await notification.info()
            assert notification.details == notification_details

            notification_details_2 = await api.get_notification(10123456)
            assert notification_details == notification_details_2

            d = notification_details
            assert d.raw == notification_data
            assert d.id == 10123456
            assert d.subject == 'Subject 1'
            assert d.body == 'Title\r\ntext'
            assert not d.sms
            assert d.mail
            assert d.push
            assert not d.unread
            assert d.date == date
            assert d.type == 'INFO'
            assert d.facility_id == 12345
            assert d.facility_name == 'F1'
            assert len(d.notification_submission_state_dto) == 2
            s1, s2 = d.notification_submission_state_dto

            assert isinstance(s1, NotificationSubmissionState)
            assert s1.raw == notification_data["notificationSubmissionStateDto"][0]
            assert s1.id == 12345678
            assert s1.recipient == 'joe@example.com'
            assert s1.type == 'EMAIL'
            assert s1.submitted_to == 'joe@example.com'
            assert s1.submission_result == 'SUCCESS'

            assert isinstance(s2, NotificationSubmissionState)
            assert s2.raw == notification_data["notificationSubmissionStateDto"][1]
            assert s2.id == 12345679
            assert s2.recipient == 'sometoken'
            assert s2.type == 'TOKEN'
            assert s2.submitted_to == 'joe@example.com'
            assert s2.submission_result == 'SUCCESS'


# TODO: Test NotificationErrorSolution
