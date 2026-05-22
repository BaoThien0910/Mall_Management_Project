# File: app/routers/congno.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import KDTC_ROLES, RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.congno import (
    CongNoCuaToiFilter,
    CongNoFilter,
    TinhCongNoThangRequest,
)
from app.services import billing_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/cong-no",
    tags=["Công nợ"],
)


@router.post(
    "/tinh-toan",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def calculate_monthly_debts(
    payload: TinhCongNoThangRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = billing_service.calculate_monthly_debts(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Tính công nợ tháng thành công",
        data=result,
    )


@router.get(
    "/cua-toi",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_my_debts(
    filters: CongNoCuaToiFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = billing_service.list_my_debts(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách công nợ của tôi thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_debts(
    filters: CongNoFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = billing_service.list_debts(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách công nợ thành công",
        data=result,
    )
