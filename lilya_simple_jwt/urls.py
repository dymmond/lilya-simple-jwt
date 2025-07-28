from lilya_simple_jwt.controllers import SignInController, RefreshController
from lilya.conf import settings
from lilya.routing import Path

route_patterns = [
    Path(path=settings.simple_jwt.signin_url, handler=SignInController, name="simplejwt-signin"),
    Path(path=settings.simple_jwt.refresh_url, handler=RefreshController, name="simplejwt-refresh"),
]
