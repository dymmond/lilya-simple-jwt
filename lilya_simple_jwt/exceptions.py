from lilya.exceptions import HTTPException
from lilya import status

class AuthenticationError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
