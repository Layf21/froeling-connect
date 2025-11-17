"""Fröling connect API Wrapper.

This library is an unofficial API wrapper for the Fröling Web Portal (https://connect-web.froeling.com/).
Some features are not yet implemented, like remote ignition for example.

Github and documentation: https://https://github.com/Layf21/froeling-connect.py
"""

from froeling.client import Froeling
from froeling.datamodels import (
    Address,
    Component,
    Facility,
    NotificationDetails,
    NotificationOverview,
    Parameter,
    UserData,
)
from froeling.session import Session

__all__ = [
    'Froeling',
    'Session',
    'Address',
    'Component',
    'Facility',
    'NotificationDetails',
    'NotificationOverview',
    'Parameter',
    'UserData',
]
