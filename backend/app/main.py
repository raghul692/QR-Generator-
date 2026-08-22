"""
QRMaster Pro — FastAPI Application Entry Point.

Configures the FastAPI app with CORS, includes all routers under the
API v1 prefix, and runs the database seed on startup.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import all_routers
from app.config import settings
from app.database.seed import init_database
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        init_database()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error(f"Database initialization failed: {exc}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise QR Code Generator & Management Platform. "
            "Generate, customize, scan, and manage QR codes with analytics, "
            "bulk generation, exports, and backups."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.api.endpoints.redirect import router as redirect_router

    app.include_router(redirect_router)

    # Include all routers under the API prefix
    for router in all_routers:
        app.include_router(router, prefix=settings.API_V1_PREFIX)

    # Root health check
    @app.get("/", tags=["Health"])
    def health():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
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