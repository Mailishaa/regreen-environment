from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Organization
from app.routes.deps import current_user, admin_user
from app.schemas.schemas import OrganizationCreate, OrganizationOut

router = APIRouter()


@router.post("", response_model=OrganizationOut)
def create_institution(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    existing = (
        db.query(Organization)
        .filter(Organization.owner_id == user.id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You already have an institution",
        )

    institution = Organization(
        name=data.name,
        organization_type=data.organization_type,
        location=data.location,
        owner_id=user.id,
    )

    db.add(institution)
    db.commit()
    db.refresh(institution)

    return institution


@router.get("/me", response_model=OrganizationOut)
def my_institution(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    institution = (
        db.query(Organization)
        .filter(Organization.owner_id == user.id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=404,
            detail="Institution not found",
        )

    return institution


@router.get("", response_model=list[OrganizationOut])
def all_institutions(
    db: Session = Depends(get_db),
    user=Depends(admin_user),
):
    return (
        db.query(Organization)
        .order_by(Organization.created_at.desc())
        .all()
    )