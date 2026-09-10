from app.models import Organization, Campaign, Observation


def metrics(db):
    observations = db.query(Observation).filter(
        Observation.verified == True
    ).all()

    baselines = [
        x for x in observations
        if x.observation_type == "baseline"
    ]

    progress = sorted(
        [
            x for x in observations
            if x.observation_type == "progress"
        ],
        key=lambda x: x.captured_at,
        reverse=True,
    )

    latest = {}

    for observation in progress:
        latest.setdefault(observation.zone_id, observation)

    baseline_by_zone = {}

    for observation in baselines:
        baseline_by_zone.setdefault(observation.zone_id, 0)
        baseline_by_zone[observation.zone_id] += observation.tree_count

    latest_total = sum(
        latest.get(zone_id).tree_count
        if zone_id in latest
        else count
        for zone_id, count in baseline_by_zone.items()
    )

    baseline_total = sum(baseline_by_zone.values())

    survival = (
        round(latest_total / baseline_total * 100, 2)
        if baseline_total
        else 0
    )

    return {
        "organizations": db.query(Organization).count(),
        "campaigns": db.query(Campaign).count(),
        "baseline_trees": baseline_total,
        "latest_trees": latest_total,
        "survival_rate": survival,
        "observations": db.query(Observation).count(),
    }