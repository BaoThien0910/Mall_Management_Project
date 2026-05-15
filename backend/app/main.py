from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import settings
from .crud import authenticate_user, create_user, get_user_by_email
from .db import AsyncSessionLocal, Base, engine, get_db
from .routers.tenants import router as tenants_router
from .routers.users import router as users_router
from .schemas import LoginRequest, UserCreate
from .enums import UserRole

app = FastAPI()

# 1. Allow React to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tenants_router)
app.include_router(users_router)


@app.on_event("startup")
async def startup() -> None:
    # Ensure database schema exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a default admin user if it does not exist yet
    async with AsyncSessionLocal() as db:
        existing_user = await get_user_by_email(db, "admin@gmail.com")
        if not existing_user:
            await create_user(db, UserCreate(
                email="admin@gmail.com",
                password="admin123",
                full_name="Administrator",
                phone="0123456789",
                role=UserRole.ADMIN,
                department="IT"
            ))


@app.post("/api/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu",
        )

    return {
        "status": "success",
        "message": "Đăng nhập thành công!",
        "token": "fake-jwt-token-12345",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active
        }
    }


#python -m uvicorn app.main:app --host 0.0.0.0 --port 8000