from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TokenVersionDTO:
    user_id: UUID
    version: int


@dataclass
class AuthHistoryDTO:
    user_id: UUID
    user_agent: str
    auth_at: datetime