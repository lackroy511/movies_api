from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.config.settings import settings
from src_auth.features.roles.v1.models import Role


async def init_user_roles(session: AsyncSession) -> None:
    result = await session.execute(select(Role.name))
    existing_roles = set(result.scalars().all())

    missing_roles = [
        role for role in settings.default_user_roles if role not in existing_roles
    ]

    if not missing_roles:
        return

    for role in missing_roles:
        new_role = Role(name=role, description="Default role", is_system=True)
        session.add(new_role)
