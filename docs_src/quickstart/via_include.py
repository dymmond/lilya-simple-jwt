from lilya.apps import Lilya
from lilya.routing import Include

app = Lilya(
    routes=[
        Include(path="/auth", namespace="lilya_simple_jwt.urls"),
    ],
    enable_openapi=True
)
