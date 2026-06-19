# File: app/routers/lookup.py

from typing import Any, Dict

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.constants.roles import KDTC_ROLES, PREMISE_VIEW_ROLES, VHBT_ROLES, RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.services import lookup_service
from app.utils.response import success_response

router = APIRouter(
    prefix="/danh-muc",
    tags=["Danh mục chọn"],
)


@router.get(
    "/mat-bang-bao-tri",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_maintenance_premises(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(PREMISE_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = lookup_service.list_maintenance_premises(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách mặt bằng bảo trì thành công",
        data=result,
    )


@router.get(
    "/nhan-vien-vhbt",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_vhbt_employees(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = lookup_service.list_vhbt_employees(db=db)
    return success_response(
        message="Lấy danh sách nhân viên Vận hành - Bảo trì thành công",
        data=result,
    )


@router.get(
    "/nhan-vien-tao-tai-khoan",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_account_employees(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = lookup_service.list_account_employees(db=db)
    return success_response(
        message="Lấy danh sách nhân viên có thể tạo tài khoản thành công",
        data=result,
    )


@router.get(
    "/khach-thue-tao-tai-khoan",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_account_tenants(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = lookup_service.list_account_tenants(db=db)
    return success_response(
        message="Lấy danh sách khách thuê có thể tạo tài khoản thành công",
        data=result,
    )


@router.get(
    "/khach-thue-hop-dong",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_contract_tenants(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = lookup_service.list_contract_tenants(db=db)
    return success_response(
        message="Lấy danh sách khách thuê dùng cho hợp đồng thành công",
        data=result,
    )


@router.get(
    "/yeu-cau-thue-them-hop-dong",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_approved_rent_requests_for_contract(
    ma_khach_thue: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = lookup_service.list_approved_rent_requests_for_contract(
        db=db,
        ma_khach_thue=ma_khach_thue,
    )
    return success_response(
        message="Lấy danh sách yêu cầu thuê thêm đã duyệt thành công",
        data=result,
    )


@router.get(
    "/mat-bang-con-trong",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_vacant_premises(
    db: Session = Depends(get_db),
    current_user: Any = Depends(
        require_roles(list(KDTC_ROLES) + [RoleCode.KHACH_THUE])
    ),
) -> Dict[str, Any]:
    result = lookup_service.list_vacant_premises(db=db)
    return success_response(
        message="Lấy danh sách mặt bằng còn trống thành công",
        data=result,
    )


@router.get(
    "/mat-bang-dien-nuoc",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_meter_premises(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = lookup_service.list_meter_premises(db=db)
    return success_response(
        message="Lấy danh sách mặt bằng nhập chỉ số điện nước thành công",
        data=result,
    )
