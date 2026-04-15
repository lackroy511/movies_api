from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Roles"])


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


@router.get("/roles/assign")
async def assign_role() -> dict:
    return {"message": "Assign role success"}


@router.delete("/roles/revoke")
async def revoke_role() -> dict:
    return {"message": "Revoke role success"}