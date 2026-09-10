from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import OrganizationCreate, OrganizationOut
from app.repositories.organization_repository import OrganizationRepository
from app.routes.deps import current_user, admin_user
router=APIRouter()
@router.post('', response_model=OrganizationOut)
def create(data: OrganizationCreate, db: Session=Depends(get_db), user=Depends(current_user)):
    return OrganizationRepository(db).create(**data.model_dump(), owner_id=user.id)
@router.get('', response_model=list[OrganizationOut])
def all(db: Session=Depends(get_db), user=Depends(admin_user)): return OrganizationRepository(db).all()
