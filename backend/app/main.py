"""
RemoteLED Backend API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import psycopg2

from app.core.config import settings
from app.core.database import db
from app.api import devices, orders, authorizations, payments, telemetry, admin, auth, device_models, locations, service_types, reference

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    debug=settings.API_DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(orders.router)
app.include_router(authorizations.router)
app.include_router(payments.router)
app.include_router(telemetry.router)
app.include_router(admin.router)
# Use unified reference router instead of individual routers
app.include_router(reference.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "RemoteLED API",
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    # Check database connection
    db_status = "healthy"
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except psycopg2.Error as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.API_DEBUG else "An unexpected error occurred",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )

