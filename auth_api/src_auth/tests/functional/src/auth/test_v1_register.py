import pytest
from src_auth.tests.functional.conftest import MakePostRequestType


@pytest.mark.asyncio
async def test_register_success(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    body, status = await make_post_request("/v1/register", payload)

    assert status == 200
    assert body["email"] == payload["email"]
    assert body["first_name"] == payload["first_name"]


@pytest.mark.asyncio
async def test_register_conflict(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "duplicate@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_post_request("/v1/register", payload)

    body, status = await make_post_request("/v1/register", payload)

    assert status == 409
    assert body["detail"] == "User already exists"


@pytest.mark.asyncio
async def test_register_optional_last_name(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "no-lastname@example.com",
        "first_name": "John",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    body, status = await make_post_request("/v1/register", payload)

    assert status == 200
    assert body["email"] == payload["email"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_error",
    [
        # Password mismatch
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "DifferentPass!",
            },
            "Passwords do not match",
        ),
        # Invalid email format
        (
            {
                "email": "not-an-email",
                "first_name": "John",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "value is not a valid email address",
        ),
        # First name too short (< 3)
        (
            {
                "email": "test@example.com",
                "first_name": "Jo",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at least 3 characters",
        ),
        # First name too long (> 50)
        (
            {
                "email": "test@example.com",
                "first_name": "A" * 51,
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at most 50 characters",
        ),
        # Last name too short (< 3)
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Do",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at least 3 characters",
        ),
        # Last name too long (> 50)
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "B" * 51,
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at most 50 characters",
        ),
        # Password too short (< 4)
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "123",
                "password_confirm": "123",
            },
            "String should have at least 4 characters",
        ),
        # Password too long (> 100)
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "P" * 101,
                "password_confirm": "P" * 101,
            },
            "String should have at most 100 characters",
        ),
    ],
)
async def test_register_validation(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
    payload: dict,
    expected_error: str,
) -> None:
    body, status = await make_post_request("/v1/register", payload)

    assert status == 422
    errors = body.get("detail", [])
    if isinstance(errors, list):
        error_messages = [e.get("msg", "") for e in errors]
        assert any(expected_error in msg for msg in error_messages)
    else:
        assert expected_error in str(body["detail"])
