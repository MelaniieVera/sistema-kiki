from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.branch import Branch
from app.database.models.business import Business
from app.database.models.organization import Organization
from app.database.models.preparation_area import PreparationArea
from app.schemas.preparation_area import PreparationAreaRead
from app.schemas.preparation_area import PreparationAreaRead



router = APIRouter()

@router.get(
    "",
    response_model = List[PreparationAreaRead],
)
def get_preparation_areas(
    db: Session = Depends(get_db),
):
    statement = (
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
            Organization.code == "grupo_kiki",
            Business.code == "kiki_sushi",
            Branch.code == "santa_rosa",
            PreparationArea.is_active.is_(True),
        )
        .order_by(PreparationArea.name)
    )

    preparation_area = db.scalars(statement).all()

    return preparation_area