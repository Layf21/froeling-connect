"""Fröling connect API Wrapper

This library is an unofficial API wrapper for the Fröling Web Portal (https://connect-web.froeling.com/).
As for now, this wrapper is read only. Altering settings is not implemented yet. It supports reading statistics from
your devices and reading notifications.

Github and documentation: https://https://github.com/Layf21/froeling-connect.py
"""

from .client import Froeling
from .datamodels import Facility, Component, Parameter, UserData, NotificationOverview, NotificationDetails, Address
