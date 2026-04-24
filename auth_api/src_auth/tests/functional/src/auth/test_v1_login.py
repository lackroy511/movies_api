import pytest
from src_auth.tests.functional.conftest import MakePostRequestType


@pytest.mark.asyncio
async def test_login_success(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "login-test@example.com",
        "first_name": "Login",
        "last_name": "TestUser",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_post_request("/v1/register", register_payload)

    login_payload = {
        "email": "login-test@example.com",
        "password": "Password123!",
    }
    body, status = await make_post_request("/v1/login", login_payload)

    assert status == 200
    assert body["email"] == login_payload["email"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "wrong-pass@example.com",
        "first_name": "Wrong",
        "last_name": "Pass",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_post_request("/v1/register", register_payload)

    login_payload = {
        "email": "wrong-pass@example.com",
        "password": "WrongPassword456!",
    }
    body, status = await make_post_request("/v1/login", login_payload)

    assert status == 401
    assert body["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_user_not_found(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "nonexistent@example.com",
        "password": "Password123!",
    }
    body, status = await make_post_request("/v1/login", payload)

    assert status == 404
    assert body["detail"] == "User not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {
                "email": "not-an-email",
                "password": "Password123!",
            },
            "value is not a valid email address",
        ),
        (
            {
                "email": "test@example.com",
                "password": "",
            },
            "String should have at least 4 characters",
        ),
        (
            {
                "email": "test@example.com",
            },
            "Field required",
        ),
    ],
)
async def test_login_validation(
    make_post_request: MakePostRequestType,
    clear_users_table: None,
    payload: dict,
    expected_error: str,
) -> None:
    body, status = await make_post_request("/v1/login", payload)

    assert status == 422
    errors = body.get("detail", [])
    if isinstance(errors, list):
        error_messages = [e.get("msg", "") for e in errors]
        assert any(expected_error in msg for msg in error_messages)
    else:
        assert expected_error in str(body["detail"])
