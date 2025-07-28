import os
from functools import cached_property
from typing import Optional, Tuple

from edgy import Registry as EdgyRegistry
from edgy.testclient import DatabaseTestClient
from lilya.conf.global_settings import Settings

from lilya_simple_jwt.backends import BackendEmailAuthentication, RefreshAuthentication
from lilya_simple_jwt.config import SimpleJWT

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URI", "postgresql+asyncpg://postgres:postgres@localhost:5432/simple_jwt"
)


class TestSettings(Settings):
    app_name: str = "test_client"
    debug: bool = True
    enable_sync_handlers: bool = True
    enable_openapi: bool = False
    environment: Optional[str] = "testing"
    redirect_slashes: bool = True
    include_in_schema: bool = False
    secret_key: Optional[str] = "sf8&h5_pki5m3iuzd7$a^sl!#=w9%c=4shdi&!t!9v4f)z(%ii"
    infer_body: bool = True

    @cached_property
    def edgy_registry(self) -> Tuple[DatabaseTestClient, EdgyRegistry]:
        database = DatabaseTestClient(TEST_DATABASE_URL)
        return database, EdgyRegistry(database=database)

    @property
    def simple_jwt(self) -> SimpleJWT:
        if getattr(self, "_simple_jwt", None) is None:
            return SimpleJWT(
                signing_key=self.secret_key,
                backend_authentication=BackendEmailAuthentication,
                backend_refresh=RefreshAuthentication,
            )
        return self._simple_jwt

    @simple_jwt.setter
    def simple_jwt(self, value) -> SimpleJWT:
        self._simple_jwt = value
