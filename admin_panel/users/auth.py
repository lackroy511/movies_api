from uuid import UUID
import http
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.http import HttpRequest

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, **kwargs: str | None) -> User | None:
        email = kwargs.get("username")
        password = kwargs.get("password")

        url = settings.AUTH_API_LOGIN_URL
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)
        if response.status_code != http.HTTPStatus.OK:
            data = response.json()
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(
                id=data["id"],
            )
            user.email = data.get("email")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.is_active = data.get("is_active")
            user.is_staff = True
            user.is_superuser = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id: UUID) -> User | None | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
