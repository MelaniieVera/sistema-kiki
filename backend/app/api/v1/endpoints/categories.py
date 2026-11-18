from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.business import Business
from app.database.models.category import Category
from app.database.models.organization import Organization
from app.schemas.category import CategoryRead

router = APIRouter()

@router.get(
    "",
    response_model=List[CategoryRead],
)
def get_categories(
    db: Session = Depends(get_db),
):
    statement = (
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
            Organization.code == "grupo_kiki",
            Business.code == "kiki_sushi",
            Category.is_active.is_(True),
        )
        .order_by(Category.display_order)
    )
    categories = db.scalars(statement).all()

    return categories
