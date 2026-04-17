from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Auth V1"])


@router.post("/register")
async def register() -> dict:
    return {"message": "Register success"}


@router.post("/login")
async def login() -> dict:
    return {"message": "Login success"}


@router.post("/refresh")
async def refresh() -> dict:
    return {"message": "Refresh success"}


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Logout success"}


@router.post("/logout-all")
async def logout_all() -> dict:
    return {"message": "Logout all success"}
