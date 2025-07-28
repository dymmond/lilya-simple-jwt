from datetime import datetime, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import PyJWTError
from lilya.exceptions import ImproperlyConfigured
from pydantic import BaseModel, Field, conint, constr, field_validator
from typing_extensions import Annotated, Doc

from lilya_simple_jwt.utils import convert_time


class BaseToken(BaseModel):
    """
    Classic representation of a token via pydantic model.
    """

    exp: datetime
    iat: datetime = Field(default_factory=lambda: convert_time(datetime.now(timezone.utc)))
    sub: Optional[constr(min_length=1) | conint(ge=1) | None] = None  # type: ignore
    iss: Optional[str] = None
    aud: Optional[str] = None
    jti: Optional[str] = None

    @field_validator("exp")
    def validate_expiration(cls, date: datetime) -> datetime:
        """
        When a token is issued, needs to be date in the future.
        """
        date = convert_time(date)
        if date.timestamp() >= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("The exp must be a date in the future.")  # pragma: no cover

    @field_validator("iat")
    def validate_iat(cls, date: datetime) -> datetime:  # pragma: no cover
        """Ensures that the `Issued At` it's nt bigger than the current time."""
        date = convert_time(date)
        if date.timestamp() <= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("iat must be a current or past time")

    @field_validator("sub")
    def validate_sub(cls, subject: str | int) -> str:  # pragma: no cover
        try:
            return str(subject)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{subject} is not a valid string.") from e

    def encode(
        self,
        key: str,
        algorithm: str,
        claims_extra: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str | Any:  # pragma: no cover
        """
        Encodes the token into a proper str formatted and allows passing kwargs.
        """
        if claims_extra is None:
            claims_extra = {}

        payload: dict = {**self.model_dump(exclude_none=True), **claims_extra}
        try:
            return jwt.encode(
                payload=payload,
                key=key,
                algorithm=algorithm,
                **kwargs,
            )
        except PyJWTError as e:
            raise ImproperlyConfigured("Error encoding the token.") from e

    @classmethod
    def decode(
        cls, token: str, key: str | bytes | jwt.PyJWK, algorithms: list[str], **kwargs: Any
    ) -> "BaseToken":  # pragma: no cover
        """
        Decodes the given token.
        """
        try:
            data = jwt.decode(
                jwt=token, key=key, algorithms=algorithms, options={"verify_aud": False}, **kwargs
            )
        except PyJWTError as e:
            raise e
        return cls(**data)


class Token(BaseToken):
    """
    Token implementation with an extra field
    `token_type`. This attribute will allow
    the distinction of type token being generated.

    !!! Note
        You are not entitled to use this object at all in your backends but if you
        are to use the examples given and the defaults without wasting too much time
        the package examples use this object to classiify the `token_type` in the claims.
    """

    token_type: Annotated[
        str | None,
        Doc(
            """
            A string value classifying the type of token being generated and used
            for the claims.

            It can be something like `access_token` or `access` or
            `refresh_token` or `refresh` or any other string value
            that can help you distinguish the token being generated in the
            claims when `decode()` and `encode()` are called.
            """
        ),
    ] = None
