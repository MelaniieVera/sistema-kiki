import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.branch import Branch
from app.database.models.branch_product_variant import BranchProductVariant
from app.database.models.business import Business
from app.database.models.category import Category
from app.database.models.organization import Organization
from app.database.models.preparation_area import PreparationArea
from app.database.models.product import Product
from app.database.models.product_variant import ProductVariant
from app.schemas.product import ProductCreate, ProductRead, ProductVariantRead


router = APIRouter()


def _generate_code(name: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", name.lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    code = re.sub(r"[^a-z0-9]+", "_", without_accents).strip("_")
    return code[:50].rstrip("_") or fallback


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductRead:
    with db.begin():
        category_statement = (
            select(Category)
            .join(Business, Category.business_id == Business.id)
            .join(Organization, Category.organization_id == Organization.id)
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
            .join(Branch, PreparationArea.branch_id == Branch.id)
            .where(
                PreparationArea.id == payload.variant.preparation_area_id,
                Branch.organization_id == category.organization_id,
                Branch.business_id == category.business_id,
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

        product_code = _generate_code(payload.name, "producto")
        product_statement = (
            insert(Product)
            .values(
                organization_id=category.organization_id,
                business_id=category.business_id,
                category_id=category.id,
                code=product_code,
                name=payload.name,
                description=payload.description,
                is_active=payload.is_active,
            )
            .on_conflict_do_nothing(constraint="uq_products_business_code")
            .returning(Product.id)
        )
        product_id = db.scalar(product_statement)

        if product_id is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product code already exists for this business",
            )

        variant = ProductVariant(
            organization_id=category.organization_id,
            business_id=category.business_id,
            product_id=product_id,
            code=_generate_code(payload.variant.name, "variante"),
            name=payload.variant.name,
        )
        db.add(variant)
        db.flush()

        branch_variant = BranchProductVariant(
            organization_id=category.organization_id,
            business_id=category.business_id,
            branch_id=preparation_area.branch_id,
            product_variant_id=variant.id,
            preparation_area_id=preparation_area.id,
            price=payload.variant.price,
            is_available=payload.variant.is_available,
        )
        db.add(branch_variant)
        db.flush()

        response = ProductRead(
            id=product_id,
            category_id=category.id,
            code=product_code,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
            variant=ProductVariantRead(
                id=variant.id,
                code=variant.code,
                name=variant.name,
                price=branch_variant.price,
                preparation_area_id=preparation_area.id,
                is_available=branch_variant.is_available,
            ),
        )

    return response
