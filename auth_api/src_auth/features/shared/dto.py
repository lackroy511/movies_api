from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    id: UUID
    email: str
    first_name: str
    last_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
