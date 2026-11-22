from fastapi import APIRouter
from pygments.lexer import include
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.preparation_areas import (
    router as preparation_areas_router
)
from app.api.v1.endpoints.products import router as products_router


api_router = APIRouter()

api_router.include_router(
    categories_router,
    prefix="/categories",
    tags = ["Categories"],
)

api_router.include_router(
    preparation_areas_router,
    prefix="/preparation-areas",
    tags= ["Preparation Areas"],
)

api_router.include_router(
    products_router,
    prefix="/products",
    tags=["Products"],
)
