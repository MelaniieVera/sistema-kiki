from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.branch import Branch
from app.database.models.business import Business
from app.database.models.category import Category
from app.database.models.organization import Organization
from app.database.models.preparation_area import PreparationArea
from app.database.models.product import Product
from app.database.models.product_variant import ProductVariant
from app.database.models.branch_product_variant import BranchProductVariant
from app.schemas.product import ProductCreate, ProductRead



router = APIRouter()

@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    category_statement = (
        select(Category)
        .join(
            Business,
            Category.business_id == Business.id,
        )
        .join(
            Organization,
            Category.organization_id == Organization.id,
        )
        .where(
            Category.id == payload.category_id,
            Organization.code == "grupo_kiki",
            Business.code == "kiki_sushi",
            Category.is_active.is_(True),
        )
    )

    category = db.scalar(category_statement)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    preparation_area_statement = (
        select(PreparationArea)
        .join(
            Branch,
            PreparationArea.branch_id == Branch.id,
        )
        .join(
            Business,
            Branch.business_id == Business.id,
        )
        .join(
            Organization,
            Branch.organization_id == Organization.id,
        )
        .where(
            PreparationArea.id == payload.variant.preparation_area_id,
            Organization.code == "grupo_kiki",
            Business.code == "kiki_sushi",
            Branch.code == "santa_rosa",
            PreparationArea.is_active.is_(True),
        )
    )

    preparation_area = db.scalar(preparation_area_statement)

    if preparation_area is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation area not found",
        )