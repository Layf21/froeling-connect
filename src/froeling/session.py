"""Manages authentication and error handling"""

from aiohttp import ClientSession
import json
import base64
import logging

from . import endpoints, exceptions


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36', 'Referer': 'https://connect-web.froeling.com/'}


class Session:
    token: str = None
    user_id = None

    def __init__(self, username=None, password=None, max_retries=3, auto_reauth=True, token_callback=None):
        self.session = ClientSession(headers=headers)
        self.username = username
        self.password = password
        self.auto_reauth = auto_reauth
        self.max_retries = max_retries
        self.token_callback = token_callback

        self.retries = 0
        self.debug = False

    async def close(self):
        await self.session.close()

    def set_token(self, token):
        self.token = token
        self.session.headers['Authorization'] = token
        try:
            self.user_id = json.loads(base64.b64decode(token.split('.')[1] + "==").decode("utf-8"))['userId']
        except:
            raise ValueError("Token is in an invalid format.")
        if self.token_callback and self.token:  # Only run when overwriting existing token
            self.token_callback(token)

    async def login(self):
        data = {'osType': 'web', 'username': self.username, 'password': self.password}
        async with await self.session.post(endpoints.LOGIN, json=data) as res:
            if res.status != 200:
                raise exceptions.AuthenticationError(f'Server returned {res.status}: "{await res.text()}"')
            self.set_token(res.headers['Authorization'])
            userdata = (await res.json())['userData']
        logging.info("Logged in with username and password.")
        return userdata['userId']

    async def request(self, method, url, **kwargs):
        if self.debug:
            print(method, url)
        try:
            async with await self.session.request(method, url, **kwargs) as res:
                if res.status == 200:
                    self.retries = 0
                    if self.debug:
                        r = await res.text()
                        print(r)
                        return json.loads(r)
                    else:
                        return await res.json()

                self.retries += 1
                if res.status == 401:
                    if self.auto_reauth:
                        logging.info(f'Error {await res.text()}, renewing token...')
                        await self.login()
                        logging.info('Reauthorized. New token: '+self.token)
                        return await self.request(method, url, **kwargs)
                    else:
                        raise exceptions.AuthenticationError("Request not authorized: "+await res.text())
                elif res.status == 403:
                    raise exceptions.AuthenticationError(f'You do not have permission to do this. Maybe the user id "{self.user_id}" is wrong?')
                else:
                    raise exceptions.NetworkError("Unexpected return code", status=res.status, url=res.url, res=await res.text())

        except json.decoder.JSONDecodeError as e:
            raise exceptions.ParsingError(e.msg, e.doc, e.pos, url)

