from esmerald import Esmerald, Pluggable

from lilya_simple_jwt.extension import SimpleJWTExtension

app = Esmerald(
    pluggables={
        "simple-jwt": Pluggable(SimpleJWTExtension, path="/auth"),
    },
)
