from datetime import datetime

import pytest
from edgy.exceptions import ObjectNotFound
from esmerald.contrib.auth.edgy.base_user import AbstractUser
from lilya.conf import settings
from lilya.exceptions import NotAuthorized
from lilya.routing import Include
from lilya.testclient import create_client
from tests.settings import TestSettings

from lilya_simple_jwt.backends import BackendEmailAuthentication as SimpleBackend
from lilya_simple_jwt.backends import RefreshAuthentication
from lilya_simple_jwt.config import SimpleJWT
from lilya_simple_jwt.schemas import TokenAccess
from lilya_simple_jwt.token import Token

database, models = settings.edgy_registry
pytestmark = pytest.mark.anyio

setatt_object = object.__setattr__


class HubUser(AbstractUser):
    class Meta:
        registry = models


class BackendAuthentication(SimpleBackend):
    async def authenticate(self) -> str:
        """Authenticates a user and returns a JWT string"""

        try:
            user: HubUser = await HubUser.query.get(email=self.email)
        except ObjectNotFound:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            await HubUser().set_password(self.password)
        else:
            is_password_valid = await user.check_password(self.password)
            if is_password_valid and self.user_can_authenticate(user):
                # The lifetime of a token should be short, let us make 5 minutes.
                # You can use also the access_token_lifetime from the JWT config directly
                access_time = datetime.now() + settings.simple_jwt.access_token_lifetime
                refresh_time = datetime.now() + settings.simple_jwt.refresh_token_lifetime

                access_token = TokenAccess(
                    access_token=self.generate_user_token(
                        user,
                        time=access_time,
                        token_type=settings.simple_jwt.access_token_name,
                    ),
                    refresh_token=self.generate_user_token(
                        user,
                        time=refresh_time,
                        token_type=settings.simple_jwt.refresh_token_name,
                    ),
                )
                return access_token.model_dump()
            else:
                raise NotAuthorized(detail="Invalid credentials.")

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)

    def generate_user_token(self, user: HubUser, token_type: str, time: datetime = None):
        """
        Generates the JWT token for the authenticated user.
        """

        if not time:
            later = datetime.now() + settings.simple_jwt.access_token_lifetime
        else:
            later = time

        token = Token(sub=str(user.id), exp=later)
        claims_extra = {"token_type": token_type}
        return token.encode(
            key=settings.simple_jwt.signing_key,
            algorithm=settings.simple_jwt.algorithm,
            claims_extra=claims_extra,
        )


simple_jwt = SimpleJWT(
    signing_key=settings.secret_key,
    backend_authentication=BackendAuthentication,
    backend_refresh=RefreshAuthentication,
)


class ViewSettings(TestSettings):
    @property
    def simple_jwt(self) -> SimpleJWT:
        return simple_jwt


def test_openapi():
    with create_client(
        routes=[Include(path="/simple-jwt", namespace="lilya_simple_jwt.urls")],
        settings_module=ViewSettings,
        enable_openapi=True,
    ) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Lilya",
                "version": client.app.version,
                "summary": "Lilya application",
                "description": "Yet another framework/toolkit that delivers.",
                "contact": {
                    "name": "Lilya",
                    "url": "https://lilya.dev",
                    "email": "admin@myapp.com",
                },
            },
            "paths": {
                "/simple-jwt/signin": {
                    "post": {
                        "summary": "Login API and returns a JWT Token.",
                        "security": [{"BearerAuth": []}],
                        "parameters": [],
                        "responses": {
                            "200": {
                                "description": "Additional response",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/TokenAccess"}
                                    }
                                },
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "access_token": {
                                                "title": "Access Token",
                                                "type": "string",
                                            },
                                            "refresh_token": {
                                                "title": "Refresh Token",
                                                "type": "string",
                                            },
                                        },
                                        "required": ["access_token", "refresh_token"],
                                        "title": "TokenAccess",
                                        "type": "object",
                                    }
                                }
                            }
                        },
                    }
                },
                "/simple-jwt/refresh-access": {
                    "post": {
                        "summary": "Refreshes the access token",
                        "description": "When a token expires, a new access token must be generated from the refresh token previously provided. The refresh token must be just that, a refresh and it should only return a new access token and nothing else\n    ",
                        "security": [{"BearerAuth": []}],
                        "parameters": [],
                        "responses": {
                            "200": {
                                "description": "Additional response",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/AccessToken"}
                                    }
                                },
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "access_token": {
                                                "title": "Access Token",
                                                "type": "string",
                                            }
                                        },
                                        "required": ["access_token"],
                                        "title": "AccessToken",
                                        "type": "object",
                                    }
                                }
                            }
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "TokenAccess": {
                        "properties": {
                            "access_token": {"title": "Access Token", "type": "string"},
                            "refresh_token": {"title": "Refresh Token", "type": "string"},
                        },
                        "required": ["access_token", "refresh_token"],
                        "title": "TokenAccess",
                        "type": "object",
                    },
                    "AccessToken": {
                        "properties": {
                            "access_token": {"title": "Access Token", "type": "string"}
                        },
                        "required": ["access_token"],
                        "title": "AccessToken",
                        "type": "object",
                    },
                },
                "securitySchemes": {"BearerAuth": []},
            },
            "servers": [{"url": "/"}],
        }
