"""
Enterprise Database Connector & Supabase Client.
Provides connection pooling for Supabase PostgreSQL with automated resilient
fallback to local SQLite for offline development and local regression testing.
"""
import os
import re
import urllib.parse
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.database.base import Base

logger = logging.getLogger(__name__)


def _sanitize_db_url(url: str) -> str:
    """
    Safely normalizes database URLs, automatically encoding special characters
    like '@' inside database passwords to prevent SQLAlchemy URI parse errors.
    """
    if not url or url.startswith("sqlite"):
        return url
    try:
        # Match postgresql://user:password@host[:port]/database
        match = re.match(r"^(postgresql(?:\+[a-z0-9_]+)?://)([^:]+):(.*)@([^@/:]+)(?::(\d+))?(/.*)$", url)
        if match:
            scheme, user, password, host, port, rest = match.groups()
            # If the password isn't already percent-encoded, encode it safely
            if "%" not in password:
                password = urllib.parse.quote(password, safe="")
            port_str = f":{port}" if port else ""
            return f"{scheme}{user}:{password}@{host}{port_str}{rest}"
    except Exception as exc:
        logger.warning(f"Database URL sanitization encountered error: {exc}")
    return url


# Determine Database Connection URL: Priority to Supabase DB URL if defined
raw_url = settings.SUPABASE_DB_URL if settings.SUPABASE_DB_URL else settings.DATABASE_URL
db_url = _sanitize_db_url(raw_url)

# Initialize engine with resilient fallback
try:
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        engine = create_engine(
            db_url,
            connect_args=connect_args,
            echo=settings.DEBUG
        )
    else:
        # Supabase PostgreSQL connection pool with keep-alive and pre-ping
        engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 8},
            echo=settings.DEBUG
        )
        # Verify connection liveness
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
        logger.info("Successfully established connection to Supabase PostgreSQL.")
except Exception as e:
    logger.warning(f"Could not connect to external database ({e}). Falling back to local SQLite ({settings.DATABASE_URL}).")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency yielding an isolated database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes tables for all registered models across microservices
    and seeds initial catalog, admin, and role data.
    """
    # Import all microservice models so SQLAlchemy registers them with Base.metadata
    import backend.auth.models.user_model  # noqa: F401
    import backend.catalog.models.catalog_model  # noqa: F401
    import backend.order.models.order_model  # noqa: F401
    import backend.payment.models.payment_model  # noqa: F401
    import backend.customer_admin.models.admin_model  # noqa: F401
    import backend.ai_fit.models.fit_model  # noqa: F401
    import backend.chatbot.models.chatbot_model  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Seed baseline records if not present
    from backend.database.seed import seed_database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
