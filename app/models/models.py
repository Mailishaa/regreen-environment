from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(30), default='institution')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Organization(Base):
    __tablename__ = 'organizations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    organization_type: Mapped[str] = mapped_column(String(80))
    location: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = relationship('User')

class Campaign(Base):
    __tablename__ = 'campaigns'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    species: Mapped[str | None] = mapped_column(String(150), nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    organization = relationship('Organization')
    zones = relationship('Zone', back_populates='campaign', cascade='all, delete-orphan')

class Zone(Base):
    __tablename__ = 'zones'
    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    name: Mapped[str] = mapped_column(String(255))
    polygon_json: Mapped[str] = mapped_column(Text)
    campaign = relationship('Campaign', back_populates='zones')
    observations = relationship('Observation', back_populates='zone', cascade='all, delete-orphan')

class Observation(Base):
    __tablename__ = 'observations'
    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey('zones.id'))
    observation_type: Mapped[str] = mapped_column(String(30))
    tree_count: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_sha256: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    zone = relationship('Zone', back_populates='observations')
