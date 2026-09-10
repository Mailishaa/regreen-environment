from app.models import Zone
from app.repositories.base import Repository
class ZoneRepository(Repository):
    def create(self, **data):
        obj = Zone(**data); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def all(self): return self.db.query(Zone).all()
    def get(self, zone_id): return self.db.get(Zone, zone_id)
