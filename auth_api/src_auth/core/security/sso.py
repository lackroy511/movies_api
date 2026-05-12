"""
To add new SSO providers:
1. Import the corresponding provider class from `fastapi_sso`.
2. Add the provider name to the `OAuthProviderType`.
3. Register the provider instance in the `provider_mapping` dictionary.
4. Ensure required credentials are added to the settings and environment.

Example:
from fastapi_sso.sso.google import GoogleSSO
"""

from dataclasses import dataclass
from typing import Literal, cast

from fastapi import Request
from fastapi_sso import OpenID, SSOBase
from fastapi_sso.sso.yandex import YandexSSO
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

from src_auth.core.config.settings import settings
from src_auth.core.exc.exceptions import OAuthError

OAuthProviderType = Literal["yandex",]


@dataclass
class OAuthOpenID:
    email: str
    first_name: str | None
    last_name: str | None
    provider: OAuthProviderType
    provider_user_id: str


provider_mapping: dict[OAuthProviderType, SSOBase] = {
    "yandex": YandexSSO(
        client_id=settings.yandex_client_id,
        client_secret=settings.yandex_client_secret,
        redirect_uri=settings.yandex_redirect_uri,
        allow_insecure_http=settings.allow_insecure_sso_http,
        scope=["login:email", "login:info"],
    ),
}


async def get_oauth_openid(
    request: Request,
    provider_name: OAuthProviderType,
) -> OAuthOpenID:
    oauth_provider = await get_oauth_provider(provider_name)

    try:
        async with oauth_provider:
            openid = cast(OpenID, await oauth_provider.verify_and_process(request))
    except InvalidGrantError:
        raise OAuthError("Invalid grant error") from None

    if not openid:
        raise OAuthError("Failed to get OpenID")

    if not openid.id:
        raise OAuthError("Failed to get user ID from OpenID")

    if not openid.email:
        raise OAuthError("Failed to get email from OpenID")

    return OAuthOpenID(
        email=openid.email,
        first_name=openid.first_name,
        last_name=openid.last_name,
        provider=cast(OAuthProviderType, openid.provider),
        provider_user_id=openid.id,
    )


async def get_oauth_provider(provider_name: OAuthProviderType) -> SSOBase:
    return provider_mapping[provider_name]
