from app.models import Organization
from app.repositories.base import Repository
class OrganizationRepository(Repository):
    def create(self, **data):
        obj = Organization(**data); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def all(self): return self.db.query(Organization).all()
