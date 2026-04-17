from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Roles V1"])


@router.post("/roles")
async def create_role() -> dict:
    return {"message": "Create role success"}


@router.get("/roles")
async def get_roles() -> dict:
    return {"message": "Get roles success"}


@router.put("/roles/{role_id}")
async def update_role(role_id: int) -> dict:
    return {"message": f"Update role {role_id} success"}


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int) -> dict:
    return {"message": f"Delete role {role_id} success"}


@router.post("/roles/{role_id}/users/{user_id}")
async def assign_role() -> dict:
    return {"message": "Assign role success"}


@router.get("/roles/{role_id}/users/{user_id}")
async def check_role_assignment() -> dict:
    return {"message": "Check role assignment success"}


@router.delete("/roles/{role_id}/users/{user_id}")
async def revoke_role() -> dict:
    return {"message": "Revoke role success"}
