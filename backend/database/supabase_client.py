"""
Enterprise Database Connector & Supabase Client.
Provides connection pooling for Supabase PostgreSQL with automated resilient
fallback to local SQLite for offline development and local regression testing.
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.database.base import Base

# Determine Database Connection URL: Priority to Supabase DB URL if defined
db_url = settings.SUPABASE_DB_URL if settings.SUPABASE_DB_URL else settings.DATABASE_URL

# Handle special connection arguments for SQLite vs PostgreSQL (Supabase)
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

    Base.metadata.create_all(bind=engine)

    # Seed baseline records if not present
    from backend.database.seed import seed_database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
