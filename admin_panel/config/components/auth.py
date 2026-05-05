import os

AUTHENTICATION_BACKENDS = [
    "users.auth.CustomAuthBackend",
]

AUTH_USER_MODEL = "users.User" 

ACCESS_COOKIE_NAME = os.getenv("ACCESS_COOKIE_NAME") 
REFRESH_COOKIE_NAME = os.getenv("REFRESH_COOKIE_NAME")

SUPERUSER_ROLE = "superuser"
STAFF_ROLE = "staff"