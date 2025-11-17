"""Manages authentication, requests and error handling."""

import base64
import json
import logging
from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from aiohttp import ClientSession
from aiohttp.typedefs import StrOrURL

from froeling import endpoints, exceptions

HTTP_STATUS_SUCCESS_MIN = 200
HTTP_STATUS_SUCCESS_MAX = 299


class Session:
    """Represents an authenticated session with the API.

    A `Session` manages authentication, tokens, and connection details
    required to communicate with the backend. It can be created with
    either a username/password combination or an existing token.
    Both user_id and token are set if the user is logged in.

    Attributes:
        user_id (int | None): ID of the authenticated user.
        token (str | None): Active authentication token for this session.

    """

    user_id: int | None = None
    token: str | None = None

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        *,
        auto_reauth: bool = False,
        token_callback: Callable[[str], Any] | None = None,
        lang: str = 'en',
        logger: logging.Logger | None = None,
        clientsession: ClientSession | None = None,
    ) -> None:
        """Initialize a new Session.

        You can authenticate by providing a `username` and `password`,
        or by supplying an existing `token`. When `auto_reauth` is enabled,
        the session will attempt to automatically refresh expired tokens.

        Args:
        ----
            username (str | None): Username for authentication.
            password (str | None): Password for authentication.
            token (str | None): Existing authentication token.
            auto_reauth (bool): Whether to automatically refresh tokens
                when they expire. Defaults to False.
            token_callback (Callable[[str], Any] | None): Optional function
                that is called whenever a new token is obtained.
            lang (str): Preferred language for API responses. Defaults to `'en'`.
            logger (logging.Logger | None): Logger instance for debugging and events.
            clientsession (ClientSession | None): Optional aiohttp
                client session to reuse instead of creating a new one.

        """
        if not (token or (username and password)):
            msg = 'Set either token or username and password.'
            raise ValueError(msg)
        if auto_reauth and not (username and password):
            msg = 'Set username and password to use auto_reauth.'
            raise ValueError(msg)

        self.clientsession = clientsession or ClientSession()
        self._headers = {'Accept-Language': lang}
        self.username = username
        self.password = password
        self.auto_reauth = auto_reauth
        self.token_callback = token_callback

        if token:
            self.set_token(token)

        self._logger = logger or logging.getLogger(__name__)
        self._reauth_previous = False  # Did the previous request result in renewing the token?

    async def close(self) -> None:
        """Close the session."""
        await self.clientsession.close()

    def set_token(self, token: str) -> None:
        """Set the token used in Authorization and updates/sets user-id.

        :param token The bearer token
        """
        self._headers['Authorization'] = token
        try:
            self.user_id = json.loads(base64.b64decode(token.split('.')[1] + '==').decode('utf-8'))['userId']
        except Exception as e:
            msg = 'Token is in an invalid format.'
            raise ValueError(msg) from e
        self.token = token

    async def login(self) -> dict:
        """Get a token using username and password.

        :return: Json sent by server (includes userdata)
        """
        data = {'osType': 'web', 'username': self.username, 'password': self.password}
        async with await self.clientsession.post(endpoints.LOGIN, json=data) as res:
            if not HTTP_STATUS_SUCCESS_MIN <= res.status <= HTTP_STATUS_SUCCESS_MAX:
                msg = f'Server returned {res.status}: "{await res.text()}"'
                raise exceptions.AuthenticationError(msg)
            token = res.headers['Authorization']
            if self.token_callback:
                self.token_callback(token)
            self.set_token(token)
            userdata = await res.json()
        self._logger.debug('Logged in with username and password.')
        return userdata

    async def request(self, method: str, url: StrOrURL, headers: dict | None = None, **kwargs: Any) -> Any:
        """Do a web request.

        :param method:
        :param url:
        :param headers: Additional headers used in the request
        :param kwargs:
        """
        self._logger.debug('Sent %s: %s', method.upper(), url)
        request_headers = self._headers
        if headers:
            request_headers |= headers

        try:
            async with await self.clientsession.request(method, url, headers=request_headers, **kwargs) as res:
                if HTTP_STATUS_SUCCESS_MIN <= res.status <= HTTP_STATUS_SUCCESS_MAX:
                    r = await res.text()
                    self._logger.debug('Got %s', r)
                    self._reauth_previous = False
                    return await res.json()

                if res.status == HTTPStatus.UNAUTHORIZED:
                    if self.auto_reauth:
                        if self._reauth_previous:
                            msg = 'Reauth did not work.'
                            raise exceptions.AuthenticationError(msg, await res.text())
                        self._logger.info('Error %s, renewing token...', await res.text())
                        await self.login()
                        self._logger.info('Reauthorized.')
                        self._reauth_previous = True
                        return await self.request(method, url, **kwargs)

                    self._logger.error('Request unauthorized')
                    msg = 'Request not authorized: '
                    raise exceptions.AuthenticationError(msg, await res.text())

                error_data = await res.text()
                msg = 'Unexpected return code'
                raise exceptions.NetworkError(
                    msg,
                    status=res.status,
                    url=res.url,
                    res=error_data,
                )

        except json.decoder.JSONDecodeError as e:
            raise exceptions.ParsingError(e.msg, e.doc, e.pos, url) from e
