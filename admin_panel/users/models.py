import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from django.contrib.auth.base_user import BaseUserManager

from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self) -> User:
        raise NotImplementedError

    def create_superuser(self, email: str, password: str | None = None) -> User:
        raise NotImplementedError


class User(AbstractBaseUser):
    password = None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("is active"),
        default=True,
    )
    is_superuser = models.BooleanField(
        verbose_name=_("is superuser"),
        default=False,
    )
    is_staff = models.BooleanField(
        verbose_name=_("is staff"),
        default=False,
    )
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=255,
    )
    last_name = models.CharField(
        verbose_name=_("last name"),
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = "email"

    objects = MyUserManager()

    def __str__(self) -> str:
        return f"{self.email} {self.first_name} {self.last_name}"

    def has_perm(self, perm: str, obj: User | None = None) -> bool:
        return True

    def has_module_perms(self, app_label: str) -> bool:
        return True

    class Meta:
        db_table = 'users"."user'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
