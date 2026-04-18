from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(
        String,
    )
    last_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"