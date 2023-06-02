"""Provides the main API Class"""

from typing import List, Any
import types

from .objects import Facility, Component, Notification
from . import endpoints
from .session import Session


class Froeling:
    """The Froeling class provides access to the Fröling API."""

    facilities: dict[int, Facility] = {}
    """A dictionary with Facility IDs as keys (Update/initiate with get_facilities())."""
    notifications: list[Notification] = []
    """A list of all notifications (Update/initiate with get_notifications())."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def __init__(self, username: str = None, password: str = None, token: str = None, auto_reauth: bool = True,
                 max_retries: int = 2, token_callback=None):
        """Initialize a :class:`Froeling` instance.
        Either username and password or a token is required.
                :param username: The email you use to log into your Fröling account.
                :param password: Your Fröling password.
                :param token: A valid token to not create a token each time the script is run.
                :param auto_reauth: Automatically fetches a new token if the current one expires (requires password and username).
                :param max_retries: How often to retry a request if the request failed.
                :param token_callback: A function that is called when the token gets renewed (useful for saving the token)."""

        self.session = Session(username, password, max_retries, auto_reauth, token_callback)
        if token:
            self.session.set_token(token)
        else:
            assert username and password, "Set either token or username and password."
        if auto_reauth:
            assert username and password, "Set username and password to use auto_reauth."
        self.username = username
        self.password = password

        self.auto_reauth = auto_reauth
        self.reauth_tries = 0

    async def login(self):
        await self.session.login()

    async def get_facilities(self) -> dict[int, Facility]:
        """Gets all facilities connected with the account and stores them in this.facilities."""
        res = await self.session.request("get", endpoints.FACILITY.format(self.session.user_id))
        ids = [r['facilityId'] for r in res]
        self.facilities = {i: Facility(i, self.session) for i in ids}
        return self.facilities

    async def get_notifications(self):
        """Gets all Notifications and stores them in this.notifications"""
        res = await self.session.request("get", endpoints.NOTIFICATION_LIST.format(self.session.user_id))
        self.notifications = [Notification(n, self.session) for n in res]
        return self.notifications
