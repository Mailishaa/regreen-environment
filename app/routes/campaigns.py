from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Organization
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.schemas import CampaignCreate, CampaignOut
from app.routes.deps import current_user, admin_user

router = APIRouter()


@router.post("", response_model=CampaignOut)
def create(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    organization = db.get(Organization, data.organization_id)

    if not organization:
        raise HTTPException(404, "Organization not found")

    if user.role != "admin" and organization.owner_id != user.id:
        raise HTTPException(
            403,
            "You do not have permission to use this organization",
        )

    return CampaignRepository(db).create(**data.model_dump())


@router.get("", response_model=list[CampaignOut])
def all(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    campaigns = CampaignRepository(db).all()

    if user.role == "admin":
        return campaigns

    organizations = {
        organization.id
        for organization in db.query(Organization)
        .filter_by(owner_id=user.id)
        .all()
    }

    return [
        campaign
        for campaign in campaigns
        if campaign.organization_id in organizations
    ]