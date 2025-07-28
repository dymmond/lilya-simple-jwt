from esmerald import Esmerald, Include

app = Esmerald(
    routes=[
        Include(path="/auth", namespace="lilya_simple_jwt.urls"),
    ]
)
