import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
include("components/**.py")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", False) == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INTERNAL_IPS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

AUTH_API_LOGIN_URL = os.getenv("AUTH_API_LOGIN_URL")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")