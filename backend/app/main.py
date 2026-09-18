import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database.base import Base
from backend.app.database.session import engine, SessionLocal
from backend.app.models.land_profile import LandProfile
from backend.app.models.metrics import SoilMetric, ClimateMetric, BiodiversityMetric, HumanImpactMetric
from backend.app.api.chat import router as chat_router
from backend.app.api.land_profiles import router as land_profiles_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.services.rag_service import rag_service

def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed standard benchmark profile if missing
    db: Session = SessionLocal()
    try:
        benchmark = db.query(LandProfile).filter(LandProfile.id == "benchmark-karnataka-vertisol-01").first()
        if not benchmark:
            benchmark = LandProfile(
                id="benchmark-karnataka-vertisol-01",
                name="Karnataka Benchmark Plot (Semi-Arid Vertisol)",
                region="semi-arid Karnataka",
                latitude=15.3173,
                longitude=75.7139,
                area_hectares=12.5,
                primary_crop="Wheat",
                farming_system="Monoculture"
            )
            db.add(benchmark)
            db.flush()

            # Seed initial metrics
            db.add(SoilMetric(
                land_profile_id=benchmark.id,
                organic_carbon_pct=0.30,
                ph=7.8,
                moisture_pct=14.0,
                nitrogen_ppm=18.0,
                texture="vertisol clay"
            ))
            db.add(ClimateMetric(
                land_profile_id=benchmark.id,
                rainfall_category="low",
                annual_rainfall_mm=450.0,
                avg_temperature_celsius=33.5,
                drought_frequency="high",
                water_availability="severely constrained"
            ))
            db.add(BiodiversityMetric(
                land_profile_id=benchmark.id,
                species_richness_index="low",
                habitat_diversity_index="low",
                pollinator_presence="rare",
                native_plant_ratio=0.15,
                canopy_cover_pct=2.0
            ))
            db.add(HumanImpactMetric(
                land_profile_id=benchmark.id,
                pesticide_intensity="high",
                water_extraction_rate="critical",
                deforestation_proximity="nearby"
            ))
            db.commit()
    except Exception as e:
        print(f"Warning during DB init/seed: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="EcoMind AI API",
    description="Evidence-Grounded AI for Biodiversity Intelligence and Multi-Metric Ecological Reasoning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers (support both /api and root prefixes for flexible proxying)
for prefix in ["/api", ""]:
    app.include_router(chat_router, prefix=prefix)
    app.include_router(land_profiles_router, prefix=prefix)
    app.include_router(recommendations_router, prefix=prefix)
    app.include_router(knowledge_router, prefix=prefix)

@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "environment": settings.ENVIRONMENT,
        "knowledge_corpus_documents": len(rag_service.documents),
        "vector_index_active": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
