from lilya import status
from lilya.exceptions import HTTPException


class AuthenticationError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
