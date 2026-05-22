# File: app/routers/auth.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    DangNhapRequest,
    DoiMatKhauRequest,
)
from app.services import auth_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/auth",
    tags=["Xác thực"],
)


@router.post(
    "/dang-nhap",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def login(
    payload: DangNhapRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    result = auth_service.login(
        db=db,
        payload=payload,
    )
    return success_response(
        message="Đăng nhập thành công",
        data=result,
    )


@router.post(
    "/dang-xuat",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def logout(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result = auth_service.logout(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Đăng xuất thành công",
        data=result,
    )


@router.patch(
    "/doi-mat-khau",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def change_password(
    payload: DoiMatKhauRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result = auth_service.change_password(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Đổi mật khẩu thành công",
        data=result,
    )


@router.get(
    "/thong-tin-hien-tai",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result: CurrentUserResponse = auth_service.get_current_user_info(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Lấy thông tin tài khoản hiện tại thành công",
        data=result,
    )
