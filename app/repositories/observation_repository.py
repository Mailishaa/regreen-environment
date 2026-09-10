from app.models import Observation
from app.repositories.base import Repository
class ObservationRepository(Repository):
    def create(self, **data):
        obj = Observation(**data); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def all(self): return self.db.query(Observation).order_by(Observation.created_at.desc()).all()
    def baseline_for_zone(self, zone_id): return self.db.query(Observation).filter_by(zone_id=zone_id, observation_type='baseline', verified=True).order_by(Observation.captured_at.asc()).first()
    def latest_verified_for_zone(self, zone_id): return self.db.query(Observation).filter_by(zone_id=zone_id, verified=True).order_by(Observation.captured_at.desc()).first()
