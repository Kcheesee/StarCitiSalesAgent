"""
StarCiti Sales Agent - FastAPI Main Application
Voice-powered AI ship consultant for Star Citizen
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .database import engine, test_connection
from .api import conversations, voice, ships, webhooks

# ============================================================================
# Create FastAPI App
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered ship consultant for Star Citizen with voice capabilities",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Include Routers
# ============================================================================

app.include_router(conversations.router)
app.include_router(voice.router)
app.include_router(ships.router)
app.include_router(webhooks.router)


# ============================================================================
# Health Check & Root Endpoints
# ============================================================================

@app.get("/", tags=["health"])
def read_root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "endpoints": {
            "start_conversation": "POST /api/conversations/start",
            "send_message": "POST /api/conversations/{id}/message",
            "get_conversation": "GET /api/conversations/{id}",
            "complete_conversation": "POST /api/conversations/{id}/complete",
            "search_ships": "GET /api/ships/search",
            "ships_by_budget": "GET /api/ships/budget",
            "ships_by_manufacturer": "GET /api/ships/manufacturer/{name}"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint
    Verifies database connection and API status
    """
    try:
        # Test database connection
        db_healthy = test_connection()

        if db_healthy:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "healthy",
                    "database": "connected",
                    "api": "operational"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "api": "operational"
                }
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/api/stats", tags=["stats"])
def get_stats():
    """
    Get API statistics
    Returns ship count, manufacturer count, etc.
    """
    from .database import SessionLocal
    from .models import Ship, Manufacturer, Conversation

    db = SessionLocal()
    try:
        ship_count = db.query(Ship).count()
        manufacturer_count = db.query(Manufacturer).count()
        conversation_count = db.query(Conversation).count()
        active_conversations = db.query(Conversation).filter_by(status="active").count()

        return {
            "ships": ship_count,
            "manufacturers": manufacturer_count,
            "total_conversations": conversation_count,
            "active_conversations": active_conversations
        }
    finally:
        db.close()


# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 80)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"📡 CORS: {settings.ALLOWED_ORIGINS}")
    print("=" * 80)

    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("⚠️  Database connection failed - check DATABASE_URL")

    print("=" * 80)
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Shutting down StarCiti Sales Agent API...")


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
