import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import ZoneCreate, ZoneOut
from app.repositories.zone_repository import ZoneRepository
from app.models import Zone, Campaign, Organization
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

    if not isinstance(polygon, list) or len(polygon) < 4:
        raise HTTPException(
            400,
            "A polygon must contain at least 3 points and be closed",
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


def get_owned_campaign(
    db: Session,
    campaign_id: int,
    user,
):
    campaign = db.get(Campaign, campaign_id)

    if not campaign:
        raise HTTPException(
            404,
            "Campaign not found",
        )

    organization = db.get(
        Organization,
        campaign.organization_id,
    )

    if not organization:
        raise HTTPException(
            404,
            "Institution not found",
        )

    if user.role != "admin" and organization.owner_id != user.id:
        raise HTTPException(
            403,
            "You do not have permission to access this campaign",
        )

    return campaign


@router.post("", response_model=ZoneOut)
def create(
    data: ZoneCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    get_owned_campaign(
        db,
        data.campaign_id,
        user,
    )

    validate_polygon(data.polygon_json)

    return ZoneRepository(db).create(
        **data.model_dump()
    )


@router.get("/{campaign_id}", response_model=list[ZoneOut])
def by_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    get_owned_campaign(
        db,
        campaign_id,
        user,
    )

    return (
        db.query(Zone)
        .filter(Zone.campaign_id == campaign_id)
        .order_by(Zone.id)
        .all()
    )