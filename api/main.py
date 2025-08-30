"""
Main FastAPI application for Blog Reviewer.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Blog Reviewer API",
    description="AI-powered blog content review and analysis system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Blog Reviewer API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"MongoDB URI: {os.getenv('MONGODB_URI', 'Not configured')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Blog Reviewer API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Blog Reviewer API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # TODO: Add database health check when database is implemented
        # TODO: Add external service health checks
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "services": {
                "api": "healthy",
                "database": "not_implemented",  # Will be updated when DB is ready
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes."""
    try:
        # TODO: Add database readiness check when database is implemented
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "ready",
                "database": "not_implemented",  # Will be updated when DB is ready
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# Import and include routers when they are implemented
# from api.routers import articles, authors, reviews
# app.include_router(articles.router, prefix="/api/v1/articles", tags=["articles"])
# app.include_router(authors.router, prefix="/api/v1/authors", tags=["authors"])
# app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
