from sqlalchemy import String, Text
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

    def __repr__(self) -> str:
        return f"<User {self.email}>"