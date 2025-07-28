import os
from functools import cached_property
from typing import Tuple

from accounts.backends import BackendAuthentication, RefreshAuthentication
from edgy import Database, Registry
from lilya.conf.global_settings import Settings

from lilya_simple_jwt.config import SimpleJWT

DATABASE_URL = os.environ.get("DATABASE_URI", "sqlite:///db.sqlite")


class AppSettings(Settings):
    """
    The settings object for the application.
    """
    enable_openapi: bool = True
    infer_body: bool = True
    secret_key: str = os.environ.get("SECRET_KEY") or "your-secret-key"

    @cached_property
    def db_connection(self) -> Tuple[Database, Registry]:
        """
        This conenction is used in `myapp/apps/accounts/models.py.
        """
        database = Database(DATABASE_URL)
        return database, Registry(database=database)

    @property
    def simple_jwt(self) -> SimpleJWT:
        return SimpleJWT(
            signing_key=self.secret_key,
            backend_authentication=BackendAuthentication,
            backend_refresh=RefreshAuthentication,
        )
