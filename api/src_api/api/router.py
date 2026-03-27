from fastapi import APIRouter

from src_api.features.genres.v1.api import router as genres_v1_router
from src_api.features.movies.v1.api import router as movies_v1_router
from src_api.features.persons.v1.api import router as persons_v1_router

router = APIRouter(prefix="/api")
router.include_router(movies_v1_router)
router.include_router(genres_v1_router)
router.include_router(persons_v1_router)
