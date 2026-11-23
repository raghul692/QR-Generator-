"""
QRMaster Pro — FastAPI Application Entry Point.

Configures FastAPI with CORS, mounted routers under `/api/v1`,
public dynamic redirect routing under `/r`, and health check probes.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import all_routers
from app.api.endpoints.health import router as health_router
from app.api.endpoints.redirect import router as redirect_router
from app.config import settings
from app.database.session import check_db_connection
from app.database.seed import init_database
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: verify database connectivity on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    db_connected = check_db_connection()
    if db_connected:
        logger.info("Database connection established successfully.")
        try:
            # Seed default categories and settings idempotently
            init_database(create_tables=False)
            logger.info("Database default reference data verified.")
        except Exception as exc:
            logger.warning(f"Database reference seed skipped or encountered error: {exc}")
    else:
        logger.warning(
            "Database connection could not be established at startup. "
            "App will continue running; readiness probe will report unavailable."
        )
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise QR Code Generator, Analytics & Management Platform. "
            "Generate, customize, scan, and manage QR codes with dynamic links, "
            "real-time analytics, bulk processing, and export capabilities."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    cors_origins = settings.cors_origins_list
    allow_credentials = "*" not in cors_origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["*"],
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Health check endpoints (available at root for Render/K8s probes)
    app.include_router(health_router)

    # Public dynamic QR redirection endpoint (/r/{short_code})
    app.include_router(redirect_router)

    # Include all v1 API routers
    for router in all_routers:
        app.include_router(router, prefix=settings.API_V1_PREFIX)

    # Root welcome info
    @app.get("/", tags=["Health"])
    def root_info():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "health_ready": "/health/ready",
        }

    return app


# Module-level app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
