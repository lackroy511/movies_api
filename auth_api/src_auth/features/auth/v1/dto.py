from dataclasses import dataclass
from uuid import UUID


@dataclass
class TokenVersionDTO:
    user_id: UUID
    version: int


@dataclass
class OAuthAccountDTO:
    user_id: UUID
    provider: str
    provider_user_id: str
