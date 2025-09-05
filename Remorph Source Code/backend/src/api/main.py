import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import analyze, health
from src.api.middleware import LoggingMiddleware, SecurityHeadersMiddleware
from src.config import OUTPUT_DIR, validate_config
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Remorph API...")
    
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validation passed")
        
        # Ensure output directory exists early so other components can write to it
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            logger.info(f"Output directory ready: {OUTPUT_DIR}")
        except Exception as e:
            logger.warning(f"Could not create output directory '{OUTPUT_DIR}' at startup: {e}")
        
        # Initialize face detector (singleton)
        from src.models.face_detector import face_detector
        logger.info("Face detector initialized")

        logger.info("Remorph API startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Remorph API...")

app = FastAPI(
    title="Remorph API",
    description="Deepfake Image Traceability - CPU-first forensic analysis",
    version="0.1.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(analyze.router, tags=["analyze"])

# Add stats router
from src.api.routes import stats
app.include_router(stats.router, tags=["stats"])

# Serve static files (heatmaps/overlays)
# Mount static files; set check_dir=False so FastAPI doesn't error if directory
# is temporarily missing (we already create it at startup above)
app.mount("/files", StaticFiles(directory=OUTPUT_DIR, check_dir=False), name="files")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Remorph API",
        "version": "0.1.0",
        "description": "Deepfake Image Traceability - CPU-first forensic analysis",
        "endpoints": {
            "analyze": "POST /analyze - Analyze single image",
            "batch": "POST /analyze/batch - Analyze multiple images",
            "health": "GET /health - Health check",
            "stats": "GET /stats - System statistics",
            "families": "GET /families - Attribution families",
            "detailed_health": "GET /health/detailed - Detailed component health"
        }
    }