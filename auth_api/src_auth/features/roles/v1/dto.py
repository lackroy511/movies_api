from dataclasses import dataclass
from uuid import UUID
from src_auth.features.roles.v1.models import RoleName


@dataclass(frozen=True)
class CreateRoleDTO:
    name: RoleName
    description: str | None = None


@dataclass(frozen=True)
class RoleDTO:
    id: UUID
    name: RoleName
    description: str | None = None
