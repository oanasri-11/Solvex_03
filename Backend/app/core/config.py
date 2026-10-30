from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[3]

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
DATABASE_URL = os.getenv("DATABASE_URL")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env")

if not ALGORITHM:
    raise ValueError("ALGORITHM is missing from .env")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")