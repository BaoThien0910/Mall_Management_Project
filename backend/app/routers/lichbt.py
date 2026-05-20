# File: app/routers/lichbt.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode, VHBT_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.lichbt import (
    LichBaoTriCreate,
    LichBaoTriFilter,
)
from app.services import maintenance_schedule_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/lich-bao-tri",
    tags=["Lịch bảo trì"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_maintenance_schedule(
    payload: LichBaoTriCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_VHBT])),
) -> Dict[str, Any]:
    result = maintenance_schedule_service.create_maintenance_schedule(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập lịch bảo trì thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_maintenance_schedules(
    filters: LichBaoTriFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = maintenance_schedule_service.list_maintenance_schedules(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách lịch bảo trì thành công",
        data=result,
    )


@router.get(
    "/{ma_lich_bt}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_maintenance_schedule_detail(
    ma_lich_bt: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = maintenance_schedule_service.get_maintenance_schedule_detail(
        db=db,
        ma_lich_bt=ma_lich_bt,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết lịch bảo trì thành công",
        data=result,
    )
