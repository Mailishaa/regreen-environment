from app.models import Campaign, Zone, Observation


def get_campaign_progress(db, campaign_id: int):
    campaign = db.get(Campaign, campaign_id)

    if not campaign:
        return None

    zones = (
        db.query(Zone)
        .filter(Zone.campaign_id == campaign_id)
        .all()
    )

    baseline_count = 0
    latest_count = 0
    verified_observations = 0

    for zone in zones:
        observations = (
            db.query(Observation)
            .filter(
                Observation.zone_id == zone.id,
                Observation.verified.is_(True),
            )
            .order_by(Observation.captured_at.asc())
            .all()
        )

        verified_observations += len(observations)

        baseline = next(
            (
                observation
                for observation in observations
                if observation.observation_type == "baseline"
            ),
            None,
        )

        if not baseline:
            continue

        baseline_count += baseline.tree_count

        progress = [
            observation
            for observation in observations
            if observation.observation_type == "progress"
        ]

        if progress:
            latest_count += progress[-1].tree_count
        else:
            latest_count += baseline.tree_count

    survival_rate = (
        round(
            latest_count / baseline_count * 100,
            2,
        )
        if baseline_count
        else 0
    )

    return {
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "baseline_count": baseline_count,
        "latest_count": latest_count,
        "survival_rate": survival_rate,
        "verified_observations": verified_observations,
    }