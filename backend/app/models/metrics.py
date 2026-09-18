import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class SoilMetric(Base):
    __tablename__ = "soil_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_profile_id = Column(String(36), ForeignKey("land_profiles.id", ondelete="CASCADE"), nullable=False)
    organic_carbon_pct = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    moisture_pct = Column(Float, nullable=True)
    nitrogen_ppm = Column(Float, nullable=True)
    texture = Column(String(50), nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    land_profile = relationship("LandProfile", back_populates="soil_metrics")

class ClimateMetric(Base):
    __tablename__ = "climate_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_profile_id = Column(String(36), ForeignKey("land_profiles.id", ondelete="CASCADE"), nullable=False)
    rainfall_category = Column(String(50), nullable=True)  # "low", "medium", "high"
    annual_rainfall_mm = Column(Float, nullable=True)
    avg_temperature_celsius = Column(Float, nullable=True)
    drought_frequency = Column(String(50), nullable=True)
    water_availability = Column(String(50), nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    land_profile = relationship("LandProfile", back_populates="climate_metrics")

class BiodiversityMetric(Base):
    __tablename__ = "biodiversity_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_profile_id = Column(String(36), ForeignKey("land_profiles.id", ondelete="CASCADE"), nullable=False)
    species_richness_index = Column(String(50), nullable=True)
    habitat_diversity_index = Column(String(50), nullable=True)
    pollinator_presence = Column(String(50), nullable=True)
    native_plant_ratio = Column(Float, nullable=True)
    canopy_cover_pct = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    land_profile = relationship("LandProfile", back_populates="biodiversity_metrics")

class HumanImpactMetric(Base):
    __tablename__ = "human_impact_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_profile_id = Column(String(36), ForeignKey("land_profiles.id", ondelete="CASCADE"), nullable=False)
    pesticide_intensity = Column(String(50), nullable=True)
    water_extraction_rate = Column(String(50), nullable=True)
    deforestation_proximity = Column(String(50), nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    land_profile = relationship("LandProfile", back_populates="human_impact_metrics")
