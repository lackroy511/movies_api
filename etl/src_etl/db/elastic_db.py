import requests
from requests.exceptions import ConnectionError, ConnectTimeout

from src_etl.utils.backoff import Backoff


class ElasticServerError(Exception):
    pass


RETRY_EXCEPTIONS = (
    ConnectionError,
    ConnectTimeout,
    ElasticServerError,
)


class ElasticConnection:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @Backoff(RETRY_EXCEPTIONS)
    def bulk(self, data: str) -> None:
        url = f"{self.base_url}/_bulk"
        params = {"filter_path": "items.*.error"}
        headers = {"Content-Type": "application/x-ndjson"}
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=data,
            timeout=5,
        )
        if 500 <= response.status_code < 600:
            raise ElasticServerError(
                f"Elasticsearch server error {response.status_code}: {response.text}",
            )

        response.raise_for_status()
