from typing import List, Dict

from metabase_client.http import HttpClient
from metabase_client.resources import CardResource, SessionResource
from metabase_client.exceptions import (
    MetabaseAuthError,
    MetabaseConfigError,
    MetabaseRequestError,
)


class MetabaseClient:
    def __init__(self, endpoint: str, **kwargs):
        """Creates a Metabase Client instance.

        :param endpoint: URL string of Metabase server.
        :param username: (optional) Username string.
        :param password: (optional) Password string.
        :param token: (optional) Auth token already obtained by Metabase server
        :return: :class:`MetabaseClient <MetabaseClient>` object
        :raises:
            MetabaseConfigError: No credentials provided.

        Usage::
            >>> from metabase_client import MetabaseClient
            >>> client = (MetabaseClient(endpoint='http://www.mymetabase.com',
                                         username='username@email.com',
                                         password='strongPassword'))

            >>> from metabase_client import MetabaseClient
            >>> client = (MetabaseClient(endpoint='http://www.mymetabase.com',
                                         token='asdf-zxcv-1234-uipo-hjkl'))
        """
        self.token = None
        self.username = None
        self.password = None
        self.session_resource = SessionResource(HttpClient(endpoint))
        self.card_resource = CardResource(HttpClient(endpoint))

        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise MetabaseConfigError(f"The argument {key} is not valid.")
            setattr(self, key, value)

        if (
            not self.token
            and not all([self.username, self.password])
            or not endpoint
            or not kwargs.items()
        ):
            raise MetabaseConfigError("Invalid arguments provided.")

    def auth(self) -> None:
        """Authenticate in metabase API using password and username provided.

        :raises:
            MetabaseConfigError: No username and password provided.
            MetabaseAuthError: Request error, invalid credentials or no token returned.
        """
        if not all([self.username, self.password]):
            raise MetabaseConfigError("You must provide username and password.")

        try:
            idx = self.session_resource.get_token(self.username, self.password)
            if not idx:
                raise MetabaseAuthError(
                    "The endpoint did not return a valid credential."
                )
            self.token = idx
        except Exception as exc:
            raise MetabaseAuthError(repr(exc))

    def get_cards(self) -> List[Dict]:
        """Get a list of cards available by metabase API."""
        try:
            return self.card_resource.list(self.token)
        except Exception as exc:
            raise MetabaseRequestError(repr(exc))
