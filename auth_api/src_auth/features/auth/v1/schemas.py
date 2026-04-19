from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str | None = Field(None, min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    password_confirm: str = Field(..., min_length=4, max_length=100)

    @model_validator(mode="after")
    def check_passwords_match(self) -> RegisterRequest:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) 
    
    id: UUID
    email: str
    first_name: str
    last_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)
