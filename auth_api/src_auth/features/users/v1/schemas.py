from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator


class ChangeEmailRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    password: str
    password_confirm: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> ChangePasswordRequest:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

        return self


class UserAuthHistoryResponse(BaseModel):
    user_agent: str
    auth_at: datetime
