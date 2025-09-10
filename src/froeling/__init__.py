"""Fröling connect API Wrapper.

This library is an unofficial API wrapper for the Fröling Web Portal (https://connect-web.froeling.com/).
Some features are not yet implemented, like remote ignition for example.

Github and documentation: https://https://github.com/Layf21/froeling-connect.py
"""

from .client import Froeling
from .datamodels import (
    Facility,
    Component,
    Parameter,
    UserData,
    NotificationOverview,
    NotificationDetails,
    Address,
)

__all__ = [
    'Froeling',
    'Facility',
    'Component',
    'Parameter',
    'UserData',
    'NotificationOverview',
    'NotificationDetails',
    'Address',
]
