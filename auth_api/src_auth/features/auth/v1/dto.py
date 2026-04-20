from uuid import UUID
from dataclasses import dataclass


@dataclass
class TokenVersionDTO:
    user_id: UUID
    version: int