"""Provides the main API Class"""
import logging
from aiohttp import ClientSession

from . import datamodels
from . import endpoints
from .session import Session


class Froeling:
    """The Froeling class provides access to the Fröling API."""

    # cached data (does not change often)
    _userdata: datamodels.UserData
    _facilities: dict[int, datamodels.Facility] = {}


    async def __aenter__(self):
        if not self.session.token:
            await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def __init__(self, username: str = None, password: str = None, token: str = None, auto_reauth: bool = False,
                 token_callback=None, language: str = 'en', logger: logging.Logger = None, clientsession: ClientSession = None):
        """Initialize a :class:`Froeling` instance.
        Either username and password or a token is required.
                :param username: The email you use to log into your Fröling account.
                :param password: Your Fröling password (not required when using token).
                :param token: A valid token (not required when using username and password).
                :param auto_reauth: Automatically fetches a new token if the current one expires (requires password and username).
                :param max_retries: How often to retry a request if the request failed.
                :param token_callback: A function that is called when the token gets renewed (useful for saving the token).
                :param clientsession: When provided, network communication will go through this aiohttp session."""

        self.session = Session(username, password, token, auto_reauth, token_callback, language, logger, clientsession)
        self._logger = logger or logging.getLogger(__name__)

    async def login(self) -> datamodels.UserData:
        data = await self.session.login()
        self._userdata = datamodels.UserData.from_dict(data)
        return self._userdata

    async def close(self):
        await self.session.close()

    @property
    def user_id(self):
        return self.session.user_id

    @property
    def token(self):
        return self.session.token

    async def _get_userdata(self) -> datamodels.UserData:
        res = await self.session.request("get", endpoints.USER.format(self.session.user_id))
        return datamodels.UserData.from_dict(res)
    async def get_userdata(self):
        """Gets userdata (cached)"""
        if not self._userdata:
            self._userdata = await self._get_userdata()
        return self._userdata


    async def _get_facilities(self) -> list[datamodels.Facility]:
        """Gets all facilities connected with the account and stores them in this.facilities."""
        res = await self.session.request("get", endpoints.FACILITY.format(self.session.user_id))
        return datamodels.Facility.from_list(res, self.session)

    async def get_facilities(self) -> list[datamodels.Facility]:
        if not self._facilities:
            facilities = await self._get_facilities()
            self._facilities = {f.facility_id: f for f in facilities}
        return list(self._facilities.values())

    async def get_facility(self, facility_id) -> datamodels.Facility:
        if facility_id not in self._facilities:
            await self.get_facilities()
        assert facility_id in self._facilities, f"Facility with id {facility_id} not found."
        return self._facilities[facility_id]


    async def get_notification_count(self) -> int:
        """Gets unread notification count"""
        return (await self.session.request("get", endpoints.NOTIFICATION_COUNT.format(self.session.user_id)))["unreadNotifications"]

    async def get_notifications(self) -> list[datamodels.NotificationOverview]:
        res = await self.session.request("get", endpoints.NOTIFICATION_LIST.format(self.session.user_id))
        return [datamodels.NotificationOverview(n, self.session) for n in res]

    async def get_notification(self, notification_id: int) -> datamodels.NotificationDetails:
        res = await self.session.request("get", endpoints.NOTIFICATION.format(self.session.user_id, notification_id))
        return datamodels.NotificationDetails.from_dict(res)

    def get_component(self, facility_id: int, component_id: str):
        return datamodels.Component(facility_id, component_id, self.session)
