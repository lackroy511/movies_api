from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateUserDTO:
    email: str
    first_name: str
    last_name: str | None
    password_hash: str

    # TODO: изменить на False после реализации регистрации через email
    is_active: bool = True
    is_superuser: bool = False


@dataclass
class UserAuthHistoryDTO:
    user_id: UUID
    user_agent: str
    auth_at: datetime
