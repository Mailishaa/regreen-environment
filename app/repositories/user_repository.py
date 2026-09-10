from app.models import User
from app.repositories.base import Repository
class UserRepository(Repository):
    def get_by_email(self, email): return self.db.query(User).filter(User.email == email).first()
    def get(self, user_id): return self.db.get(User, user_id)
    def create(self, **data):
        user = User(**data); self.db.add(user); self.db.commit(); self.db.refresh(user); return user
