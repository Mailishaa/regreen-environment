import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.connection import engine
from app.models import User, Organization, Campaign, Zone, Observation
from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.routes import auth, organizations, campaigns, zones, observations, dashboard

Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def seed_admin():
    db=SessionLocal()
    try:
        if not db.query(User).filter_by(email='admin@rejesha.local').first():
            db.add(User(email='admin@rejesha.local',password_hash=hash_password(os.getenv('ADMIN_PASSWORD','Admin123!')),full_name='Rejesha Super Admin',role='admin'))
            db.commit()
    finally: db.close()
seed_admin()

app=FastAPI(title=settings.APP_NAME, version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(auth.router,prefix='/auth',tags=['Auth'])
app.include_router(organizations.router,prefix='/organizations',tags=['Organizations'])
app.include_router(campaigns.router,prefix='/campaigns',tags=['Campaigns'])
app.include_router(zones.router,prefix='/zones',tags=['Zones'])
app.include_router(observations.router,prefix='/observations',tags=['Observations'])
app.include_router(dashboard.router,prefix='/dashboard',tags=['Dashboard'])
@app.get('/health')
def health(): return {'status':'ok','service':settings.APP_NAME}
