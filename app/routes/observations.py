
import hashlib
import os
from datetime import datetime


from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.models import Campaign, Organization, Observation, Zone
from app.repositories.observation_repository import ObservationRepository
from app.repositories.zone_repository import ZoneRepository
from app.schemas.schemas import ObservationOut
from app.routes.deps import admin_user, current_user
from app.services.geofence_service import point_in_polygon

router = APIRouter()


@router.post("", response_model=ObservationOut)
def create(
    zone_id: int = Form(...),
    observation_type: str = Form(...),
    tree_count: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    captured_at: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if observation_type not in ("baseline", "progress"):
        raise HTTPException(
            400,
            "observation_type must be baseline or progress",
        )

    if tree_count < 0:
        raise HTTPException(
            400,
            "tree_count cannot be negative",
        )

    zone = ZoneRepository(db).get(zone_id)

    if not zone:
        raise HTTPException(
            404,
            "Zone not found",
        )

    campaign = db.get(Campaign, zone.campaign_id)

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
            "Organization not found",
        )

    if user.role != "admin" and organization.owner_id != user.id:
        raise HTTPException(
            403,
            "You do not have permission to submit observations for this zone",
        )

    if not point_in_polygon(
        latitude,
        longitude,
        zone.polygon_json,
    ):
        raise HTTPException(
            400,
            "Observation coordinates are outside the registered zone",
        )

    try:
        captured = datetime.fromisoformat(captured_at)
    except ValueError:
        raise HTTPException(
            400,
            "captured_at must be a valid ISO 8601 datetime string",
        )

    

    data = image.file.read()
    digest = hashlib.sha256(data).hexdigest()

    existing = (
        db.query(Observation)
        .filter_by(image_sha256=digest)
        .first()
    )

    if existing:
        raise HTTPException(
            409,
            "Duplicate image",
        )

    os.makedirs(
        settings.UPLOAD_DIR,
        exist_ok=True,
    )

    filename = os.path.basename(image.filename or "observation.jpg")

    path = os.path.join(
        settings.UPLOAD_DIR,
        f"{digest}_{filename}",
    )

    with open(path, "wb") as file:
        file.write(data)

    return ObservationRepository(db).create(
        zone_id=zone_id,
        observation_type=observation_type,
        tree_count=tree_count,
        latitude=latitude,
        longitude=longitude,
        image_path=path,
        image_sha256=digest,
        verified=False,
        captured_at=captured,
    )


@router.get("", response_model=list[ObservationOut])
def all(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    query = db.query(Observation)

    if user.role != "admin":
        query = (
            query
            .join(Zone, Observation.zone_id == Zone.id)
            .join(Campaign, Zone.campaign_id == Campaign.id)
            .join(
                Organization,
                Campaign.organization_id == Organization.id,
            )
            .filter(Organization.owner_id == user.id)
        )

    return query.all()


@router.patch(
    "/{observation_id}/verify",
    response_model=ObservationOut,
)
def verify(
    observation_id: int,
    verified: bool,
    db: Session = Depends(get_db),
    user=Depends(admin_user),
):
    observation = db.get(
        Observation,
        observation_id,
    )

    if not observation:
        raise HTTPException(
            404,
            "Observation not found",
        )

    observation.verified = verified

    db.commit()
    db.refresh(observation)

    return observation

