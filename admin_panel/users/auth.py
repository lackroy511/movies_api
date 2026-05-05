from typing import Literal
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
import http

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.http import HttpRequest

import jwt

from utils.backoff import Backoff


RETRY_EXCEPTIONS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)


User = get_user_model()


TokenType = Literal["access", "refresh"]
RolesType = Literal["superuser", "staff", "subscriber"]


class TokenPayload(BaseModel):
    user_id: str
    user_roles: list[RolesType]
    iat: datetime
    exp: datetime
    type: TokenType
    ver: int


class CustomAuthBackend(BaseBackend):
    @Backoff(RETRY_EXCEPTIONS)
    def authenticate(self, request: HttpRequest, **kwargs: str | None) -> User | None:  # ty: ignore
        email = kwargs.get("username")
        password = kwargs.get("password")

        url = settings.AUTH_API_LOGIN_URL
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)
        if response.status_code != http.HTTPStatus.OK:
            return None

        token = response.cookies.get(settings.ACCESS_COOKIE_NAME)
        data = response.json()
        user_roles = self._get_user_roles(token)

        is_staff = self._has_required_role(user_roles)
        if not is_staff:
            return None

        try:
            user, _ = User.objects.update_or_create(
                id=data["id"],
                defaults={
                    "email": data.get("email"),
                    "first_name": data.get("first_name"),
                    "last_name": data.get("last_name"),
                    "is_active": data.get("is_active"),
                    "is_staff": is_staff,
                    "is_superuser": settings.SUPERUSER_ROLE in user_roles,
                },
            )
        except KeyError, User.DoesNotExist:
            return None

        return user

    def get_user(self, user_id: UUID) -> User | None:  # ty: ignore
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _has_required_role(self, user_roles: list[RolesType]) -> bool:
        return (
            settings.STAFF_ROLE in user_roles or settings.SUPERUSER_ROLE in user_roles
        )

    def _get_user_roles(self, token: str) -> list[RolesType]:
        token_data = self._decode_token(token, "access")
        if not token_data:
            return []

        return token_data.user_roles

    def _decode_token(self, token: str, token_type: TokenType) -> TokenPayload | None:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

            return TokenPayload(**payload)
        except jwt.DecodeError:
            return None
