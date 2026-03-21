from fastapi import APIRouter

from src_api.features.movies.v1.api import router as movies_v1_router

router = APIRouter(prefix="/api")
router.include_router(movies_v1_router)
