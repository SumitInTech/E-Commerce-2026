"""
AI Fit & Anthropometric History Database Entity.
Stores user biometric sizing predictions to personalize future apparel sizing.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from backend.database.base import Base


class SizingHistory(Base):
    __tablename__ = "sizing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    gender = Column(String(20), default="male")
    predicted_chest_cm = Column(Float, nullable=False)
    predicted_waist_cm = Column(Float, nullable=False)
    predicted_hip_cm = Column(Float, nullable=False)
    recommended_size = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
