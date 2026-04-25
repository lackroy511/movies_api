import pytest
from src_auth.tests.functional.conftest import MakeRequestType


async def test_change_password_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "change-pass-test@example.com",
        "first_name": "Change",
        "last_name": "Password",
        "password": "OldPassword123!",
        "password_confirm": "OldPassword123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "change-pass-test@example.com",
        "password": "OldPassword123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {
        "password": "NewPassword456!",
        "password_confirm": "NewPassword456!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["status"] == "success"


async def test_change_password_unauthorized(
    make_request: MakeRequestType,
) -> None:
    change_payload = {
        "password": "NewPassword456!",
        "password_confirm": "NewPassword456!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=change_payload,
        cookies={"access_token": "invalid-token"},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {
                "password": "NewPassword456!",
                "password_confirm": "DifferentPass789!",
            },
            "Passwords do not match",
        ),
        (
            {},
            "Field required",
        ),
    ],
)
async def test_change_password_validation(
    make_request: MakeRequestType,
    payload: dict,
    expected_error: str,
) -> None:
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=payload,
    )

    assert status == 422
    errors = body.get("detail", [])
    if isinstance(errors, list):
        error_messages = [e.get("msg", "") for e in errors]
        assert any(expected_error in msg for msg in error_messages)
    else:
        assert expected_error in str(body["detail"])
