import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.v1.router import api_router


def create_application() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production API for verifying Ethiopian identity documents using OCR and customizable rules.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: Track processing time (vital for OCR monitoring)
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        logger.info(
            f"{request.method} {request.url.path} completed in {process_time:.3f}s (Status: {response.status_code})"
        )
        return response

    # Global Exception Handler: Return structured JSON on unexpected engine crashes
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred while processing the document.",
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        )

    # Include routes at root and at /api/v1
    app.include_router(api_router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
