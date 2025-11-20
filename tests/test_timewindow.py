import pytest
from aioresponses import aioresponses

from froeling import Froeling, endpoints
from froeling.datamodels.timewindow import (
    TimeWindows,
    TimeWindowDay,
    TimeWindowPhase,
    Weekday,
)


@pytest.mark.asyncio
async def test_update_time_windows_posts_payload(load_json):
    payload = [
        {"id": 56, "weekDay": "MONDAY", "phases": [{"startHour": 6, "startMinute": 10, "endHour": 20, "endMinute": 0}]},
        {"id": 57, "weekDay": "TUESDAY", "phases": [{"startHour": 6, "startMinute": 10, "endHour": 20, "endMinute": 0}]},
        {"id": 58, "weekDay": "WEDNESDAY", "phases": [{"startHour": 6, "startMinute": 10, "endHour": 20, "endMinute": 0}]},
        {"id": 59, "weekDay": "THURSDAY", "phases": [{"startHour": 6, "startMinute": 10, "endHour": 20, "endMinute": 0}]},
        {"id": 60, "weekDay": "FRIDAY", "phases": [{"startHour": 6, "startMinute": 10, "endHour": 19, "endMinute": 0}]},
        {"id": 61, "weekDay": "SATURDAY", "phases": [{"startHour": 7, "startMinute": 0, "endHour": 16, "endMinute": 0}]},
        {"id": 62, "weekDay": "SUNDAY", "phases": [{"startHour": 9, "startMinute": 0, "endHour": 16, "endMinute": 0}]},
    ]

    facility_data = load_json('facility.json')

    token = 'header.eyJ1c2VySWQiOjEyMzR9.signature'

    with aioresponses() as m:
        m.get(endpoints.FACILITY.format(1234), status=200, payload=facility_data)
        m.post(
            endpoints.SET_FACILITY_TIME_WINDOWS.format(1234, 12345),
            status=200,
            payload={"updatedTimeWindowIds": [56]},
        )

        async with Froeling(token=token) as api:
            f = await api.get_facility(12345)

            tw = TimeWindows._from_list(payload)
            res = await f.update_time_windows(tw)

            assert res == {"updatedTimeWindowIds": [56]}


def test_timewindow_phase_validation_and_to_dict():
    p = TimeWindowPhase.from_hm(6, 10, 24, 0)
    assert p.to_dict() == {"startHour": 6, "startMinute": 10, "endHour": 24, "endMinute": 0}

    with pytest.raises(ValueError):
        TimeWindowPhase.from_hm(24, 0, 1, 0)

    with pytest.raises(ValueError):
        TimeWindowPhase.from_hm(10, 0, 9, 59)


def test_timewindow_phase_overlap():
    a = TimeWindowPhase.from_hm(6, 0, 8, 0)
    b = TimeWindowPhase.from_hm(7, 30, 9, 0)
    c = TimeWindowPhase.from_hm(8, 0, 10, 0)

    assert a._overlap(b) is True
    assert a._overlap(c) is False


def test_timewindow_day_modifications():
    day_dict = {"id": 1, "weekDay": "MONDAY", "phases": [{"startHour": 6, "startMinute": 0, "endHour": 8, "endMinute": 0}]}
    day = TimeWindowDay._from_dict(day_dict)

    with pytest.raises(ValueError):
        day.add_phase(7, 0, 9, 0)

    new_day = day.add_phase(9, 0, 10, 0)
    assert len(new_day.phases) == 2

    replaced = new_day.replace_phase(1, 10, 0, 11, 0)
    assert replaced.phases[1].start_hour == 10

    removed = replaced.remove_phase(1)
    assert len(removed.phases) == 1


def test_timewindow_wrapper_keys_and_props():
    week = []
    base_id = 56
    hours = [6, 6, 6, 6, 6, 7, 9]
    weekdays = [w.value for w in Weekday]
    for i, wd in enumerate(weekdays):
        week.append({"id": base_id + i, "weekDay": wd, "phases": [{"startHour": hours[i], "startMinute": 0, "endHour": 16 if i >= 5 else 20, "endMinute": 0}]})

    tw = TimeWindows._from_list(week)
    assert len(tw) == 7
    assert Weekday.MONDAY in tw.keys()
    assert tw.monday.weekday == Weekday.MONDAY
