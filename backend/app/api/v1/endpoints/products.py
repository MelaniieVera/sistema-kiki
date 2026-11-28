import re
import unicodedata
from typing import Union
from uuid import UUID

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
from app.schemas.product import (
    CatalogProductRead,
    CatalogVariantRead,
    ProductCreate,
    ProductPatch,
    ProductRead,
    ProductVariantRead,
    ProductVariantCreate,
)


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
    response_model=Union[ProductRead, CatalogProductRead],
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> Union[ProductRead, CatalogProductRead]:
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

        branch = db.scalar(select(Branch).where(
            Branch.organization_id == category.organization_id,
            Branch.business_id == category.business_id,
            Branch.code == "santa_rosa",
        ))
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")

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

        product = db.get(Product, product_id)
        if payload.variant is not None:
            variant, branch_variant = _create_variant(db, product, branch, payload.variant)
            return ProductRead(
                id=product.id,
                category_id=product.category_id,
                code=product.code,
                name=product.name,
                description=product.description,
                is_active=product.is_active,
                variant=ProductVariantRead(
                    id=variant.id,
                    code=variant.code,
                    name=variant.name,
                    price=branch_variant.price,
                    preparation_area_id=payload.variant.preparation_area_id,
                    is_available=branch_variant.is_available,
                ),
            )

        for presentation in payload.variants or []:
            _create_variant(db, product, branch, presentation)
        return _read_catalog(db, [(product, branch)])[0]


def _require_area(db: Session, branch: Branch, area_id: UUID):
    area = db.scalar(select(PreparationArea.id).where(
        PreparationArea.id == area_id,
        PreparationArea.branch_id == branch.id,
        PreparationArea.organization_id == branch.organization_id,
        PreparationArea.is_active.is_(True),
    ))
    if area is None:
        raise HTTPException(status_code=404, detail="Preparation area not found")


def _create_variant(db: Session, product: Product, branch: Branch, payload: ProductVariantCreate):
    _require_area(db, branch, payload.preparation_area_id)
    code = _generate_code(payload.name, "variante")
    variant_id = db.scalar(
        insert(ProductVariant)
        .values(
            organization_id=product.organization_id,
            business_id=product.business_id,
            product_id=product.id,
            code=code,
            name=payload.name,
        )
        .on_conflict_do_nothing(constraint="uq_product_variants_product_code")
        .returning(ProductVariant.id)
    )
    if variant_id is None:
        raise HTTPException(status_code=409, detail="Variant code already exists for this product")

    variant = db.get(ProductVariant, variant_id)
    branch_variant = BranchProductVariant(
        organization_id=product.organization_id,
        business_id=product.business_id,
        branch_id=branch.id,
        product_variant_id=variant_id,
        preparation_area_id=payload.preparation_area_id,
        price=payload.price,
        is_available=payload.is_available,
    )
    db.add(branch_variant)
    db.flush()
    return variant, branch_variant


def _catalog_scope():
    return (
        select(Product, Branch)
        .join(Business, Product.business_id == Business.id)
        .join(Organization, Product.organization_id == Organization.id)
        .join(Branch, Branch.business_id == Business.id)
        .where(
            Organization.code == "grupo_kiki",
            Business.code == "kiki_sushi",
            Branch.code == "santa_rosa",
        )
    )


def _catalog_variants():
    return select(ProductVariant, BranchProductVariant).join(
        BranchProductVariant,
        BranchProductVariant.product_variant_id == ProductVariant.id,
    )


def _read_catalog(db, products):
    if not products:
        return []
    branch = products[0][1]
    variants = db.execute(
        _catalog_variants()
        .where(
            BranchProductVariant.branch_id == branch.id,
            ProductVariant.product_id.in_([product.id for product, _ in products]),
        )
        .order_by(ProductVariant.name, ProductVariant.id)
    )
    catalog = {
        product.id: CatalogProductRead(
            id=product.id,
            category_id=product.category_id,
            code=product.code,
            name=product.name,
            description=product.description,
            is_active=product.is_active,
            variants=[],
        )
        for product, _ in products
    }
    for variant, branch_variant in variants:
        catalog[variant.product_id].variants.append(
            CatalogVariantRead(
                id=variant.id,
                code=variant.code,
                name=variant.name,
                price=branch_variant.price,
                preparation_area_id=branch_variant.preparation_area_id,
                is_available=branch_variant.is_available,
            )
        )
    return list(catalog.values())


@router.get("", response_model=list[CatalogProductRead])
def list_products(db: Session = Depends(get_db)):
    products = db.execute(_catalog_scope().order_by(Product.name, Product.id)).all()
    return _read_catalog(db, products)


def _require_product(db, statement):
    row = db.execute(statement).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return row


@router.get("/{product_id}", response_model=CatalogProductRead)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    row = _require_product(db, _catalog_scope().where(Product.id == product_id))
    return _read_catalog(db, [row])[0]


@router.patch("/{product_id}", response_model=CatalogProductRead)
def update_product(product_id: UUID, payload: ProductPatch, db: Session = Depends(get_db)):
    with db.begin():
        row = _require_product(
            db, _catalog_scope().where(Product.id == product_id).with_for_update(of=Product)
        )
        product, branch = row
        if payload.category_id is not None and payload.category_id != product.category_id:
            category = db.scalar(select(Category.id).where(
                Category.id == payload.category_id,
                Category.business_id == product.business_id,
                Category.organization_id == product.organization_id,
                Category.is_active.is_(True),
            ))
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")

        for field, value in payload.model_dump(exclude_unset=True, exclude={"variant", "variants"}).items():
            setattr(product, field, value)

        presentations = payload.variants or ([payload.variant] if payload.variant else [])
        for changes in presentations:
            if isinstance(changes, ProductVariantCreate):
                _create_variant(db, product, branch, changes)
                continue
            variant_row = db.execute(
                _catalog_variants().where(
                    ProductVariant.product_id == product.id,
                    ProductVariant.id == changes.id,
                    BranchProductVariant.branch_id == branch.id,
                ).with_for_update()
            ).one_or_none()
            if variant_row is None:
                raise HTTPException(status_code=404, detail="Variant not found")

            variant, branch_variant = variant_row
            if changes.preparation_area_id is not None and (
                changes.preparation_area_id != branch_variant.preparation_area_id
            ):
                _require_area(db, branch, changes.preparation_area_id)

            for field, value in changes.model_dump(exclude_unset=True, exclude={"id"}).items():
                setattr(variant if field == "name" else branch_variant, field, value)

        db.flush()
        return _read_catalog(db, [row])[0]
