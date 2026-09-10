import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv('APP_NAME', 'Rejesha API')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./rejesha.db')
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
    CORS_ORIGINS = [x.strip() for x in os.getenv('CORS_ORIGINS', '*').split(',') if x.strip()]
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')

settings = Settings()
if not settings.SECRET_KEY:
    raise RuntimeError('SECRET_KEY is required. Set it in your .env or Render environment variables.')
