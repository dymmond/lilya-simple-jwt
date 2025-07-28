from lilya.controllers import Controller
from lilya.contrib.openapi.decorator import openapi
from lilya.contrib.openapi.datastructures import OpenAPIResponse
from lilya.responses import JSONResponse
from lilya.conf import settings
from lilya import status


class SignInController(Controller):

    @openapi(
        summary=settings.simple_jwt.signin_summary,
        description=settings.simple_jwt.signin_description,
        status_code=status.HTTP_200_OK,
        security=settings.simple_jwt.security,
        tags=settings.simple_jwt.tags,
        responses={200: OpenAPIResponse(model=settings.simple_jwt.token_model)},
    )
    async def post(self, data: settings.simple_jwt.login_model) -> JSONResponse:
        """
        Login a user and returns a JWT token, else raises ValueError.
        """
        auth = settings.simple_jwt.backend_authentication(**data.model_dump())
        access_tokens: dict[str, str] = await auth.authenticate()
        return JSONResponse(access_tokens)


class RefreshController(Controller):
    @openapi(
        summary=settings.simple_jwt.refresh_summary,
        description=settings.simple_jwt.refresh_description,
        security=settings.simple_jwt.security,
        tags=settings.simple_jwt.tags,
        status_code=status.HTTP_200_OK,
        responses={200: OpenAPIResponse(model=settings.simple_jwt.access_token_model)},
    )
    async def post(self, payload: settings.simple_jwt.refresh_model) -> settings.simple_jwt.access_token_model:
        """
        Login a user and returns a JWT token, else raises ValueError.
        """
        authentication = settings.simple_jwt.backend_refresh(token=payload)
        access_token = await authentication.refresh()
        return access_token
