from datetime import datetime, timedelta
from typing import Any, Union

from pydantic import BaseModel
from typing_extensions import Annotated, Doc

from lilya_simple_jwt.backends import BaseBackendAuthentication, BaseRefreshAuthentication
from lilya_simple_jwt.schemas import AccessToken, LoginEmailIn, RefreshToken, TokenAccess


class JWTConfig(BaseModel):
    signing_key: Annotated[
        str,
        Doc(
            """
            The secret used to encode and generate the JWT Token. Having a centralized `secret` like in the settings would be recommended as it would be the source of truth for any configuration needing a secret.
            """
        ),
    ]
    api_key_header: Annotated[
        str,
        Doc(
            """
            API Key header for the jwt.
            """
        ),
    ] = "X_API_TOKEN"
    authorization_header: Annotated[
        str,
        Doc(
            """
            Authorization header name.
            """
        ),
    ] = "Authorization"
    algorithm: Annotated[
        str,
        Doc(
            """
            Algorithm used for the jwt token encoding/decoding.
            """
        ),
    ] = "HS256"
    access_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            Lifetime of the token after generation.
            """
        ),
    ] = timedelta(minutes=5)
    refresh_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            Lifetime of the generated refresh token.
            """
        ),
    ] = timedelta(days=1)
    auth_header_types: Annotated[
        list[str],
        Doc(
            """
            Header to be sent with the token value.
            """
        ),
    ] = ["Bearer"]
    jti_claim: Annotated[
        str,
        Doc(
            """
            Used to prevent the JWT from being relayed and relay attacks.
            """
        ),
    ] = "jti"
    verifying_key: Annotated[
        str,
        Doc(
            """
            Verification key.
            """
        ),
    ] = ""
    leeway: Annotated[
        Union[str, int],
        Doc(
            """
            Used for when there is a clock skew times.
            """
        ),
    ] = 0
    sliding_token_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            A `datetime.timedelta` object which specifies how long sliding tokens are valid to prove authentication. This timedelta value is added to the current UTC time during token generation to obtain the token's default `exp` claim value.
            """
        ),
    ] = timedelta(minutes=5)
    sliding_token_refresh_lifetime: Annotated[
        Union[datetime, timedelta, str, float],
        Doc(
            """
            A `datetime.timedelta` object which specifies how long sliding tokens are valid to be refreshed. This timedelta value is added to the current UTC time during token generation to obtain the token's default `exp` claim value.
            """
        ),
    ] = timedelta(days=1)
    user_id_field: Annotated[
        str,
        Doc(
            """
             The database field from the user model that will be included in generated tokens to identify users. It is recommended that the value of this setting specifies a field that does not normally change once its initial value is chosen. For example, specifying a `username` or `email` field would be a poor choice since an account's username or email might change depending on how account management in a given service is designed. This could allow a new account to be created with an old username while an existing token is still valid which uses that username as a user identifier.
            """
        ),
    ] = "id"
    user_id_claim: Annotated[
        str,
        Doc(
            """
            The claim in generated tokens which will be used to store user identifiers. For example, a setting value of 'user_id' would mean generated tokens include a `user_id` claim that contains the user's identifier.
            """
        ),
    ] = "user_id"
    access_token_name: Annotated[
        str,
        Doc(
            """
            Name of the key for the access token.
            """
        ),
    ] = "access_token"
    refresh_token_name: Annotated[
        str,
        Doc(
            """
            Name of the key for the refresh token.
            """
        ),
    ] = "refresh_token"


class SimpleJWT(JWTConfig):
    backend_authentication: Annotated[
        type[BaseBackendAuthentication],
        Doc(
            """
            The backend authentication being used by the system. A subclass of `lilya_simple_jwt.backends.BaseBackendAuthentication`.

            !!! Warning
                All backend authentication used by Lilya Simple JWT **must implement**
                the `async def authenticate()` functionality.
            """
        ),
    ]
    backend_refresh: Annotated[
        type[BaseRefreshAuthentication],
        Doc(
            """
            The backend refresh being used by the system. A subclass of `lilya_simple_jwt.backends.BaseRefreshAuthentication`.

            !!! Warning
                All backend authentication used by Lilya Simple JWT **must implement**
                the `async def refresh()` functionality.
            """
        ),
    ]
    login_model: Annotated[
        type[BaseModel],
        Doc(
            """
            A pydantic base model with the needed fields for the login.
            Usually `email/username` and `password.

            This model can be found in `lilya_simple_jwt.schemas.LoginEmailIn` and it is
            used by default for the login endpoint of a user into the system.

            !!! Tip
                If you don't want to use the default email/password but instead something
                unique to you, you can simply create your own model and override the `login_model`
                settings from the `SimpleJWT` configuration.
            """
        ),
    ] = LoginEmailIn
    refresh_model: Annotated[
        type[BaseModel],
        Doc(
            """
            A pydantic base model with the needed fields for the refresh token payload.
            Usually a dictionary of the format:

            ```python
            {
                "refresh_token": ...
            }
            ```

            This model can be found in `lilya_simple_jwt.schemas.RefreshToken` and it is
            used by default for the refresh endpoint of an `access_token` in the system.
            """
        ),
    ] = RefreshToken
    access_token_model: Annotated[
        type[BaseModel],
        Doc(
            """
            **Used for OpenAPI specification and return of the refresh token URL**.

            A pydantic base model with the representing the return of an `access_token`:

            ```python
            {
                "access_token": ...
            }
            ```

            This model can be found in `lilya_simple_jwt.schemas.AccessToken` and it is
            used by default for the refresh endpoint return of an `access_token` in the system.
            """
        ),
    ] = AccessToken
    token_model: Annotated[
        type[BaseModel],
        Doc(
            """
            **Used for OpenAPI specification only**.

            A pydantic base model with the representing the return of an `access_token` and `refresh_token`:

            ```python
            {
                "access_token": ...,
                "refresh_token": ...
            }
            ```

            This model can be found in `lilya_simple_jwt.schemas.TokenAccess` and it is
            used by default for the refresh endpoint return of a dictionary containing the access and refresh tokens.
            """
        ),
    ] = TokenAccess
    tags: Annotated[
        Union[str, None],
        Doc(
            """
            OpenAPI tags to be displayed on each view provided by Lilya Simple JWT.

            These will be common to both controllers.
            """
        ),
    ] = None
    signin_url: Annotated[
        str,
        Doc(
            """
            The URL path in the format of `/path` used for the sign-in endpoint.
            """
        ),
    ] = "/signin"
    signin_summary: Annotated[
        str,
        Doc(
            """
            The OpenAPI URL summary for the path the sign-in endpoint.
            """
        ),
    ] = "Login API and returns a JWT Token."
    signin_description: Annotated[
        str,
        Doc(
            """
            The OpenAPI URL description for the path the sign-in endpoint.
            """
        ),
    ] = None
    refresh_url: Annotated[
        str,
        Doc(
            """
            The URL path in the format of `/path` used for the refresh token endpoint.
            """
        ),
    ] = "/refresh-access"
    refresh_summary: Annotated[
        str,
        Doc(
            """
            The OpenAPI URL summary for the path the refresh token endpoint.
            """
        ),
    ] = "Refreshes the access token"
    refresh_description: Annotated[
        str,
        Doc(
            """
            The OpenAPI URL description for the path the refresh token endpoint.
            """
        ),
    ] = """When a token expires, a new access token must be generated from the refresh token previously provided. The refresh token must be just that, a refresh and it should only return a new access token and nothing else
    """
    security: Annotated[
        list[Any] | None,
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            The security is applied to all the endpoints.
            """
        ),
    ] = [{"BearerAuth": []}]
