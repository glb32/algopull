import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    CLOUDFLARE_SITE_KEY = os.environ.get('CLOUDFLARE_SITE_KEY')
    CLOUDFLARE_SECRET_KEY = os.environ.get('CLOUDFLARE_SECRET_KEY')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
