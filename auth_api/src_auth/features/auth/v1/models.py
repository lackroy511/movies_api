from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class AuthHistory(Base):
    __tablename__ = "auth_history"
    
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    user_agent: Mapped[str] = mapped_column(
        Text,
    )
    auth_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<AuthHistory {self.user_id} {self.user_agent} {self.auth_at}>"
    