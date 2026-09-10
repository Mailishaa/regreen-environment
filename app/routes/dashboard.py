from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.routes.deps import admin_user
from app.services.metrics_service import metrics
from app.models import Campaign, Organization, Zone, Observation

router = APIRouter()


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    user=Depends(admin_user),
):
    return metrics(db)


@router.get("/campaigns")
def campaigns(
    db: Session = Depends(get_db),
    user=Depends(admin_user),
):
    results = []

    for campaign in db.query(Campaign).all():
        zones = db.query(Zone).filter_by(
            campaign_id=campaign.id
        ).all()

        zone_ids = [zone.id for zone in zones]

        observations = (
            db.query(Observation)
            .filter(Observation.zone_id.in_(zone_ids))
            .all()
            if zone_ids
            else []
        )

        verified = [
            observation
            for observation in observations
            if observation.verified
        ]

        baselines = [
            observation
            for observation in verified
            if observation.observation_type == "baseline"
        ]

        progress = sorted(
            [
                observation
                for observation in verified
                if observation.observation_type == "progress"
            ],
            key=lambda observation: observation.captured_at,
            reverse=True,
        )

        latest_by_zone = {}

        for observation in progress:
            latest_by_zone.setdefault(
                observation.zone_id,
                observation,
            )

        baseline_by_zone = {}

        for observation in baselines:
            baseline_by_zone.setdefault(
                observation.zone_id,
                0,
            )
            baseline_by_zone[observation.zone_id] += observation.tree_count

        baseline_count = sum(baseline_by_zone.values())

        latest_count = sum(
            latest_by_zone[zone_id].tree_count
            if zone_id in latest_by_zone
            else count
            for zone_id, count in baseline_by_zone.items()
        )

        survival_rate = (
            round(latest_count / baseline_count * 100, 2)
            if baseline_count
            else 0
        )

        organization = db.get(
            Organization,
            campaign.organization_id,
        )

        results.append({
            "id": campaign.id,
            "name": campaign.name,
            "species": campaign.species,
            "organization_id": campaign.organization_id,
            "organization_name": (
                organization.name
                if organization
                else "Unknown"
            ),
            "baseline_count": baseline_count,
            "latest_count": latest_count,
            "survival_rate": survival_rate,
            "observations": len(observations),
        })

    return results