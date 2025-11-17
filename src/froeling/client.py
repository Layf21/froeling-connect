"""Provides the main API Class."""

import logging
from collections.abc import Callable
from types import TracebackType
from typing import Any

from aiohttp import ClientSession

from froeling import datamodels, endpoints
from froeling.exceptions import FacilityNotFoundError
from froeling.session import Session


class Froeling:
    """The Froeling class provides access to the Fröling API."""

    async def __aenter__(self) -> 'Froeling':
        """Create an API session."""
        try:
            if not self.session.token:
                await self.login()
        except Exception:
            await self.session.close()
            raise
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """End an API session."""
        await self.session.close()
        return None

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        *,
        auto_reauth: bool = False,
        token_callback: Callable[[str], Any] | None = None,
        language: str = 'en',
        logger: logging.Logger | None = None,
        clientsession: ClientSession | None = None,
    ) -> None:
        """Initialize a Froeling API client instance.

        Either `username` and `password` or a `token` is required.

        Args:
        ----
            username (str | None): Email used to log into your Fröling account.
            password (str | None): Fröling password (not required when using `token`).
            token (str | None): Valid token (not required when using username/password).
            auto_reauth (bool): Automatically fetch a new token if the current one
                expires (requires username and password). Defaults to False.
            token_callback (Callable[[str], Any] | None): Function called when the token
                is renewed (useful for saving the token). Defaults to None.
            language (str): Preferred language for API responses. Defaults to "en".
            logger (logging.Logger | None): Logger for debugging and events.
                Defaults to None.
            clientsession (ClientSession | None): Optional aiohttp session to reuse
                instead of creating a new one. Defaults to None.

        """
        # cached data (does not change often)
        self._userdata: datamodels.UserData | None = None
        self._facilities: dict[int, datamodels.Facility] = {}

        self.session = Session(
            username,
            password,
            token,
            auto_reauth=auto_reauth,
            token_callback=token_callback,
            lang=language,
            logger=logger,
            clientsession=clientsession,
        )
        self._logger = logger or logging.getLogger(__name__)

    async def login(self) -> datamodels.UserData:
        """Log in with the username and password."""
        data = await self.session.login()
        self._userdata = datamodels.UserData._from_dict(data)  # noqa: SLF001
        return self._userdata

    async def close(self) -> None:
        """Close the session."""
        await self.session.close()

    @property
    def user_id(self) -> int | None:
        """The user's id."""
        return self.session.user_id

    @property
    def token(self) -> str | None:
        """The user's token."""
        return self.session.token

    async def _get_userdata(self) -> datamodels.UserData:
        """Fetch userdata (cached)."""
        res = await self.session.request('get', endpoints.USER.format(self.session.user_id))
        return datamodels.UserData._from_dict(res)  # noqa: SLF001

    async def get_userdata(self) -> datamodels.UserData:
        """Get userdata (cached)."""
        if not self._userdata:
            self._userdata = await self._get_userdata()
        return self._userdata

    async def _get_facilities(self) -> list[datamodels.Facility]:
        """Fetch all facilities connected with the account and cache them."""
        res = await self.session.request('get', endpoints.FACILITY.format(self.session.user_id))
        return datamodels.Facility._from_list(res, self.session)  # noqa: SLF001

    async def get_facilities(self) -> list[datamodels.Facility]:
        """Get all cacilities connected with this account (cached)."""
        if not self._facilities:
            facilities = await self._get_facilities()
            self._facilities = {f.facility_id: f for f in facilities}
        return list(self._facilities.values())

    async def get_facility(self, facility_id: int) -> datamodels.Facility:
        """Get a specific facility given it's id (cached)."""
        if facility_id not in self._facilities:
            await self.get_facilities()

        if facility_id not in self._facilities:
            raise FacilityNotFoundError(facility_id)
        return self._facilities[facility_id]

    async def get_notification_count(self) -> int:
        """Fetch the unread notification count."""
        return (await self.session.request('get', endpoints.NOTIFICATION_COUNT.format(self.session.user_id)))[
            'unreadNotifications'
        ]

    async def get_notifications(self) -> list[datamodels.NotificationOverview]:
        """Fetch an overview of all notifications."""
        res = await self.session.request('get', endpoints.NOTIFICATION_LIST.format(self.session.user_id))
        return [datamodels.NotificationOverview(n, self.session) for n in res]

    async def get_notification(self, notification_id: int) -> datamodels.NotificationDetails:
        """Fetch all details for a specific notification."""
        res = await self.session.request('get', endpoints.NOTIFICATION.format(self.session.user_id, notification_id))
        return datamodels.NotificationDetails._from_dict(res)  # noqa: SLF001

    def get_component(self, facility_id: int, component_id: str) -> datamodels.Component:
        """Get a specific component given it's facility_id and component_id.

        Call the update method for this component to populate it's attributes.
        """
        return datamodels.Component(facility_id, component_id, self.session)
