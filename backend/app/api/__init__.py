from backend.app.api.chat import router as chat_router
from backend.app.api.land_profiles import router as land_profiles_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.knowledge import router as knowledge_router

__all__ = [
    "chat_router",
    "land_profiles_router",
    "recommendations_router",
    "knowledge_router"
]
