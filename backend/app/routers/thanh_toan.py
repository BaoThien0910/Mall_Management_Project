# File: app/routers/thanh_toan.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.hoadon import (
    MoPhongKetQuaThanhToanRequest,
    TaoGiaoDichThanhToanRequest,
)
from app.services import payment_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/thanh-toan",
    tags=["Thanh toán mô phỏng"],
)


@router.post(
    "/tao-giao-dich",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_simulated_payment(
    payload: TaoGiaoDichThanhToanRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = payment_service.create_simulated_payment(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Tạo giao dịch thanh toán mô phỏng thành công",
        data=result,
    )


@router.post(
    "/{ma_hoa_don}/mo-phong-ket-qua",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def simulate_payment_result(
    ma_hoa_don: str,
    payload: MoPhongKetQuaThanhToanRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = payment_service.simulate_payment_result(
        db=db,
        ma_hoa_don=ma_hoa_don,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Mô phỏng kết quả thanh toán thành công",
        data=result,
    )


@router.get(
    "/{ma_hoa_don}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_payment_detail(
    ma_hoa_don: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = payment_service.get_payment_detail(
        db=db,
        ma_hoa_don=ma_hoa_don,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết giao dịch thanh toán thành công",
        data=result,
    )
