import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class LandProfile(Base):
    __tablename__ = "land_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False, default="Unnamed Plot")
    region = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_hectares = Column(Float, nullable=True)
    primary_crop = Column(String(100), nullable=True)
    farming_system = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="land_profiles")
    soil_metrics = relationship("SoilMetric", back_populates="land_profile", cascade="all, delete-orphan")
    climate_metrics = relationship("ClimateMetric", back_populates="land_profile", cascade="all, delete-orphan")
    biodiversity_metrics = relationship("BiodiversityMetric", back_populates="land_profile", cascade="all, delete-orphan")
    human_impact_metrics = relationship("HumanImpactMetric", back_populates="land_profile", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="land_profile", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="land_profile")
