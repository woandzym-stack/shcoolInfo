from fastapi import APIRouter

from app.api.v1.endpoints import schools
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(
    schools.router,
    prefix="/schools",
    tags=["schools"]
)


if settings.RUN_MODE in ("local"):
    from app.api.v1.endpoints import code_generate

    api_router.include_router(
        code_generate.router, 
        prefix="/code_generate",
        tags=["code_generate"]
    )
