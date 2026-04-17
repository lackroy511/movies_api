from enum import Enum as Enum

from sqlalchemy import Column
from sqlalchemy import Enum as AlchEnum
from sqlalchemy import ForeignKey, Table, Text
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class RoleName(Enum):
    ADMIN = "admin"
    SUBSCRIBER = "subscriber"
    REGULAR_USER = "regular_user"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(
        AlchEnum(RoleName),
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>" 


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)
