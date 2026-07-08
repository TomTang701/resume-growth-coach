import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

DEFAULT_DATABASE_URL = "sqlite:///./local_data/resume_growth_coach.sqlite3"


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    raw_path = database_url.replace("sqlite:///", "", 1)
    if raw_path in (":memory:", ""):
        return
    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


def _make_engine(database_url: str):
    _ensure_sqlite_parent(database_url)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


DATABASE_URL = os.getenv("RGC_DATABASE_URL", DEFAULT_DATABASE_URL)
engine = _make_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def configure_database(database_url: str) -> None:
    global DATABASE_URL, engine, SessionLocal
    DATABASE_URL = database_url
    engine = _make_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

