import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import ZoneCreate, ZoneOut
from app.repositories.zone_repository import ZoneRepository
from app.repositories.campaign_repository import CampaignRepository
from app.models import Zone
from app.routes.deps import current_user

router = APIRouter()


def validate_polygon(polygon_json: str):
    try:
        polygon = json.loads(polygon_json)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            400,
            "polygon_json must contain valid JSON",
        )

    if not isinstance(polygon, list) or len(polygon) < 3:
        raise HTTPException(
            400,
            "A polygon must contain at least 3 coordinate points",
        )

    for point in polygon:
        if not isinstance(point, list) or len(point) != 2:
            raise HTTPException(
                400,
                "Each polygon point must contain latitude and longitude",
            )

        latitude, longitude = point

        if not isinstance(latitude, (int, float)):
            raise HTTPException(
                400,
                "Latitude must be a number",
            )

        if not isinstance(longitude, (int, float)):
            raise HTTPException(
                400,
                "Longitude must be a number",
            )

        if not -90 <= latitude <= 90:
            raise HTTPException(
                400,
                "Latitude must be between -90 and 90",
            )

        if not -180 <= longitude <= 180:
            raise HTTPException(
                400,
                "Longitude must be between -180 and 180",
            )

    if polygon[0] != polygon[-1]:
        raise HTTPException(
            400,
            "The polygon must be closed: first and last points must match",
        )

    return polygon


@router.post("", response_model=ZoneOut)
def create(
    data: ZoneCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if not CampaignRepository(db).get(data.campaign_id):
        raise HTTPException(404, "Campaign not found")

    validate_polygon(data.polygon_json)

    return ZoneRepository(db).create(**data.model_dump())


@router.get("/{campaign_id}", response_model=list[ZoneOut])
def by_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return (
        db.query(Zone)
        .filter_by(campaign_id=campaign_id)
        .all()
    )