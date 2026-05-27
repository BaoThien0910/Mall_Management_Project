# File: app/routers/taikhoan.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.taikhoan import (
    TaiKhoanCreate,
    TaiKhoanDisableRequest,
    TaiKhoanEnableRequest,
    TaiKhoanFilter,
)
from app.services import account_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/tai-khoan",
    tags=["Tài khoản"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_accounts(
    filters: TaiKhoanFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = account_service.list_accounts(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách tài khoản thành công",
        data=result,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_account(
    payload: TaiKhoanCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = account_service.create_account(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Tạo tài khoản thành công",
        data=result,
    )


@router.patch(
    "/{ma_tk}/vo-hieu",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def disable_account(
    ma_tk: str,
    payload: TaiKhoanDisableRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = account_service.disable_account(
        db=db,
        ma_tk=ma_tk,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Vô hiệu hóa tài khoản thành công",
        data=result,
    )


@router.patch(
    "/{ma_tk}/khoi-phuc",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def enable_account(
    ma_tk: str,
    payload: TaiKhoanEnableRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = account_service.enable_account(
        db=db,
        ma_tk=ma_tk,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Khôi phục tài khoản thành công",
        data=result,
    )
