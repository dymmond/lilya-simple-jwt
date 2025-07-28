import os

from lilya.conf.global_settings import Settings
from lilya_simple_jwt.config import SimpleJWT

from myapp.backends import BackendAuthentication, RefreshAuthentication

DATABASE_URL = os.environ.get("DATABASE_URI", "sqlite:///db.sqlite")


class AppSettings(Settings):
    """
    The settings object for the application.
    """
    enable_openapi: bool = True
    infer_body: bool = True
    secret_key: str = os.environ.get("SECRET_KEY") or "your-secret-key"

    @property
    def simple_jwt(self) -> SimpleJWT:
        return SimpleJWT(
            signing_key=self.secret_key,
            backend_authentication=BackendAuthentication,
            backend_refresh=RefreshAuthentication,
        )
