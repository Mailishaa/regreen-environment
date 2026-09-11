from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str



class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; email: EmailStr; full_name: str; role: str

class OrganizationCreate(BaseModel):
    name: str; organization_type: str; location: str

class OrganizationOut(OrganizationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int; owner_id: int

class CampaignCreate(BaseModel):
    name: str; species: str | None = None; organization_id: int

class CampaignOut(CampaignCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ZoneCreate(BaseModel):
    campaign_id: int; name: str; polygon_json: str

class ZoneOut(ZoneCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    observation_type: str
    tree_count: int
    latitude: float
    longitude: float
    image_path: str | None
    verified: bool
    captured_at: datetime
    created_at: datetime