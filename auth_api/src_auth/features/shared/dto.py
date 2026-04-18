from uuid import UUID
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserDTO:
    id: UUID
    email: str
    first_name: str
    last_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
