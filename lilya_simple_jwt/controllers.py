from lilya import status
from lilya.conf import _monkay
from lilya.contrib.openapi.datastructures import OpenAPIResponse
from lilya.contrib.openapi.decorator import openapi
from lilya.controllers import Controller
from lilya.responses import JSONResponse


class SignInController(Controller):
    @openapi(
        summary=_monkay.settings.simple_jwt.signin_summary,
        description=_monkay.settings.simple_jwt.signin_description,
        status_code=status.HTTP_200_OK,
        security=_monkay.settings.simple_jwt.security,
        tags=_monkay.settings.simple_jwt.tags,
        responses={200: OpenAPIResponse(model=_monkay.settings.simple_jwt.token_model)},
    )
    async def post(self, data: _monkay.settings.simple_jwt.login_model) -> JSONResponse:  # type: ignore
        """
        Login a user and returns a JWT token, else raises ValueError.
        """
        auth = _monkay.settings.simple_jwt.backend_authentication(**data.model_dump())
        access_tokens: dict[str, str] = await auth.authenticate()
        return JSONResponse(access_tokens)


class RefreshController(Controller):
    @openapi(
        summary=_monkay.settings.simple_jwt.refresh_summary,
        description=_monkay.settings.simple_jwt.refresh_description,
        security=_monkay.settings.simple_jwt.security,
        tags=_monkay.settings.simple_jwt.tags,
        status_code=status.HTTP_200_OK,
        responses={200: OpenAPIResponse(model=_monkay.settings.simple_jwt.access_token_model)},
    )
    async def post(
        self, payload: _monkay.settings.simple_jwt.refresh_model  # type: ignore
    ) -> _monkay.settings.simple_jwt.access_token_model:  # type: ignore
        """
        Login a user and returns a JWT token, else raises ValueError.
        """
        authentication = _monkay.settings.simple_jwt.backend_refresh(token=payload)
        access_token = await authentication.refresh()
        return access_token
