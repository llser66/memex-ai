from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 加载项目根目录 .env
load_dotenv(PROJECT_ROOT / ".env")


POSTGRES_USER = os.getenv("POSTGRES_USER", "memex")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "memex_password_2026")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "memex_db")


DATABASE_URL = (
    f"postgresql://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()