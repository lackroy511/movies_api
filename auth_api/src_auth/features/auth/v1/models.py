from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class TokenVersion(Base):
    __tablename__ = "token_versions"
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    def __repr__(self) -> str:
        return f"TokenVersion(user_id={self.user_id}, version={self.version})"


class OauthAccount(Base):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
    )
    provider_user_id: Mapped[str] = mapped_column(
        String,
    )

    __table_args__ = (UniqueConstraint("provider", "provider_user_id"),)

    def __repr__(self) -> str:
        return (
            f"OauthAccount(user_id={self.user_id}, "
            f"provider={self.provider}, "
            f"provider_user_id={self.provider_user_id})"
        )
