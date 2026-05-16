"""Auth API."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import Principal, get_principal
from app.schemas.auth import LoginBody, LoginResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginBody, db: Session = Depends(get_db)):
    user = auth_service.authenticate_login(db, body)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai email hoặc mật khẩu!")
    return LoginResponse(**auth_service.build_login_response(user))


@router.get("/me", response_model=dict)
async def read_me(me: Principal = Depends(get_principal)):
    return {"email": me.email, "role": me.role, "permissions": me.permissions}
