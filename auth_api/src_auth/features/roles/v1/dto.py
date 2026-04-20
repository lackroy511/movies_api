from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateRoleDTO:
    name: str
    description: str | None = None


@dataclass(frozen=True)
class RoleDTO:
    id: UUID
    name: str
    description: str | None = None
