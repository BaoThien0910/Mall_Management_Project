"""Khởi tạo ứng dụng."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import bootstrap_db
from app.config import get_settings
from app.routers import auth, finance


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_db(seed=True)
    yield


def create_application() -> FastAPI:
    settings = get_settings()
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
    return app


app = create_application()
