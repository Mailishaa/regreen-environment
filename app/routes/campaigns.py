from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Organization, Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.schemas import CampaignCreate, CampaignOut
from app.routes.deps import current_user
from app.services.campaign_metrics_service import (
    get_campaign_progress,
)

router = APIRouter()


def get_owned_campaign(
    db: Session,
    campaign_id: int,
    user,
):
    campaign = db.get(Campaign, campaign_id)

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )

    organization = db.get(
        Organization,
        campaign.organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    if user.role != "admin" and organization.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this campaign",
        )

    return campaign


@router.post("", response_model=CampaignOut)
def create(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    organization = db.get(
        Organization,
        data.organization_id,
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    if user.role != "admin" and organization.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to use this institution",
        )

    return CampaignRepository(db).create(
        **data.model_dump()
    )


@router.get("", response_model=list[CampaignOut])
def all(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    query = db.query(Campaign)

    if user.role != "admin":
        query = (
            query
            .join(
                Organization,
                Campaign.organization_id == Organization.id,
            )
            .filter(Organization.owner_id == user.id)
        )

    return query.order_by(
        Campaign.created_at.desc()
    ).all()


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return get_owned_campaign(
        db,
        campaign_id,
        user,
    )

@router.get("/{campaign_id}/progress")
def progress(
    campaign_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    get_owned_campaign(
        db,
        campaign_id,
        user,
    )

    result = get_campaign_progress(
        db,
        campaign_id,
    )

    if result is None:
        raise HTTPException(
            404,
            "Campaign not found",
        )

    return result