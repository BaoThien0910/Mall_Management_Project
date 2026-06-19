# File: app/routers/matbang.py

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import PREMISE_VIEW_ROLES, VHBT_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.matbang import (
    MatBangCreate,
    MatBangFilter,
    MatBangTrangThaiBaoTriUpdate,
    MatBangUpdate,
)
from app.services import premise_service
from app.utils.response import success_response

router = APIRouter(
    prefix="/mat-bang",
    tags=["Mặt bằng"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_premises(
    filters: MatBangFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(PREMISE_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.list_premises(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách mặt bằng thành công",
        data=result,
    )


@router.get(
    "/{ma_mb}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_premise_detail(
    ma_mb: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(PREMISE_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.get_premise_detail(
        db=db,
        ma_mb=ma_mb,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết mặt bằng thành công",
        data=result,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_premise(
    payload: MatBangCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.create_premise(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Tạo mặt bằng thành công",
        data=result,
    )


@router.patch(
    "/{ma_mb}/trang-thai-bao-tri",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def update_maintenance_status(
    ma_mb: str,
    payload: MatBangTrangThaiBaoTriUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.update_maintenance_status(
        db=db,
        ma_mb=ma_mb,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Cập nhật trạng thái bảo trì của mặt bằng thành công",
        data=result,
    )


@router.patch(
    "/{ma_mb}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def update_premise(
    ma_mb: str,
    payload: MatBangUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.update_premise(
        db=db,
        ma_mb=ma_mb,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Cập nhật mặt bằng thành công",
        data=result,
    )


@router.delete(
    "/{ma_mb}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def delete_premise(
    ma_mb: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = premise_service.delete_premise(
        db=db,
        ma_mb=ma_mb,
        current_user=current_user,
    )
    return success_response(
        message="Xóa mặt bằng thành công",
        data=result,
    )
