import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool


Base = declarative_base()
SCHEMA_VERSION = 1
REQUIRED_SCHEMA: dict[str, tuple[str, ...]] = {
    "documents": ("id", "source_type", "filename", "content", "detected_sections_json", "created_at"),
    "job_descriptions": ("id", "source_type", "filename", "content", "detected_keywords_json", "created_at"),
    "analyses": ("id", "resume_id", "job_description_id", "fit_score", "summary", "model_name", "model_status", "deterministic_result_json", "created_at"),
    "skill_matches": ("id", "analysis_id", "match_type", "skill"),
    "growth_goals": ("id", "analysis_id", "horizon", "goals_json"),
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "local_data" / "resume_growth_coach.sqlite3"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    raw_path = database_url.replace("sqlite:///", "", 1)
    if raw_path in (":memory:", ""):
        return
    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


def _make_engine(database_url: str):
    _ensure_sqlite_parent(database_url)
    if not database_url.startswith("sqlite"):
        return create_engine(database_url)
    connect_args = {"check_same_thread": False}
    if database_url.endswith(":memory:"):
        return create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
    return create_engine(database_url, connect_args=connect_args, poolclass=NullPool)


DATABASE_URL = os.getenv("RGC_DATABASE_URL", DEFAULT_DATABASE_URL)
engine = _make_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def configure_database(database_url: str) -> None:
    global DATABASE_URL, engine, SessionLocal
    engine.dispose()
    DATABASE_URL = database_url
    engine = _make_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS schema_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"))
        current = connection.execute(text("SELECT value FROM schema_metadata WHERE key = 'schema_version'")).scalar_one_or_none()
        if current is None:
            connection.execute(
                text("INSERT INTO schema_metadata (key, value) VALUES ('schema_version', :version)"),
                {"version": str(SCHEMA_VERSION)},
            )
        elif int(current) != SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported database schema version {current}; expected {SCHEMA_VERSION}.")
    validate_schema()


def validate_schema() -> None:
    inspector = inspect(engine)
    missing_tables = [table for table in REQUIRED_SCHEMA if not inspector.has_table(table)]
    if missing_tables:
        raise RuntimeError(f"Database is missing required tables: {', '.join(missing_tables)}")
    missing_columns = {
        table: sorted(set(columns) - {column["name"] for column in inspector.get_columns(table)})
        for table, columns in REQUIRED_SCHEMA.items()
    }
    missing_columns = {table: columns for table, columns in missing_columns.items() if columns}
    if missing_columns:
        raise RuntimeError(f"Database schema is missing columns: {missing_columns}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
