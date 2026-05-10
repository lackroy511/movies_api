from fastapi_sso.sso.yandex import YandexSSO

from src_auth.core.config.settings import settings

yandex_sso = YandexSSO(
    client_id=settings.yandex_client_id,
    client_secret=settings.yandex_client_secret,
    redirect_uri=settings.yandex_redirect_uri,
    allow_insecure_http=settings.allow_insecure_sso_http,
    scope=["login:email", "login:info"],
)


async def get_yandex_sso() -> YandexSSO:
    return yandex_sso
