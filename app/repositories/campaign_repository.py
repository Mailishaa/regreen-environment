from app.models import Campaign
from app.repositories.base import Repository
class CampaignRepository(Repository):
    def create(self, **data):
        obj = Campaign(**data); self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def all(self): return self.db.query(Campaign).all()
    def get(self, campaign_id): return self.db.get(Campaign, campaign_id)
