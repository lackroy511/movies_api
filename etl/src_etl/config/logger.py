import logging
import logging.handlers
import os

from src_etl.config.settings import settings

log = logging.getLogger(__name__)


if not os.path.exists(settings.base_dir / "logs"):
    os.mkdir("logs")


def configure_logging() -> None:
    logging.getLogger("psycopg.pool").setLevel(logging.ERROR)
    
    file_handler = logging.handlers.RotatingFileHandler(
        settings.base_dir / "logs/psql_to_es.log",
        maxBytes=1024 * 1024 * 50,
        backupCount=1,
    )
    file_handler.setLevel(settings.log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_level)

    logging.basicConfig(
        level=settings.log_level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s] %(module)5s.py:%(lineno)-3d %(levelname)3s - %(message)s",
        handlers=[
            file_handler,
            console_handler,
        ],
    )
