"""
Shared Declarative Base for SQLAlchemy ORM across all microservices.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
