import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_schema_compatibility(db_engine):
    """
    Idempotent schema upgrade ensuring newly introduced columns exist
    in SQLite or PostgreSQL tables without needing external migration tooling.
    """
    try:
        inspector = inspect(db_engine)
        existing_tables = set(inspector.get_table_names())

        with db_engine.begin() as conn:
            # 1. users.branch_id
            if "users" in existing_tables:
                user_cols = {c["name"] for c in inspector.get_columns("users")}
                if "branch_id" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN branch_id INTEGER"))

            # 2. medicines.status
            if "medicines" in existing_tables:
                med_cols = {c["name"] for c in inspector.get_columns("medicines")}
                if "status" not in med_cols:
                    conn.execute(text("ALTER TABLE medicines ADD COLUMN status VARCHAR(50) DEFAULT 'active'"))

            # 3. batches.branch_id and batches.created_by
            if "batches" in existing_tables:
                batch_cols = {c["name"] for c in inspector.get_columns("batches")}
                if "branch_id" not in batch_cols:
                    conn.execute(text("ALTER TABLE batches ADD COLUMN branch_id INTEGER"))
                if "created_by" not in batch_cols:
                    conn.execute(text("ALTER TABLE batches ADD COLUMN created_by INTEGER"))
    except Exception as exc:
        logger.warning(f"Schema compatibility check notice: {exc}")


def get_db():
    """Dependency that provides an active database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
