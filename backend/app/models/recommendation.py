import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_profile_id = Column(String(36), ForeignKey("land_profiles.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    directive = Column(Text, nullable=False)
    scientific_rationale = Column(Text, nullable=False)
    impacted_metrics = Column(JSON, nullable=False)  # List[str]
    time_horizon = Column(String(50), nullable=False)  # "Short term", "Medium term", "Long term"
    confidence_level = Column(String(20), nullable=False)  # "High", "Medium", "Low"
    reasoning_trace = Column(JSON, nullable=False)  # List[str]
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    land_profile = relationship("LandProfile", back_populates="recommendations")
    sources = relationship("Source", back_populates="recommendation", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id = Column(String(36), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    organization = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    document_type = Column(String(50), nullable=False)  # report, peer_reviewed, dataset
    evidence_snippet = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False)
    doi_or_url = Column(String(500), nullable=True)

    recommendation = relationship("Recommendation", back_populates="sources")
