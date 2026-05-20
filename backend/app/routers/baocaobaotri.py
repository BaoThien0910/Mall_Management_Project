# File: app/routers/baocaobaotri.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode, VHBT_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.baocaobaotri import (
    BaoCaoBaoTriFilter,
    BaoCaoTrangThaiMatBangCreate,
)
from app.services import maintenance_report_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/bao-cao-bao-tri",
    tags=["Báo cáo bảo trì"],
)


@router.post(
    "/trang-thai-mat-bang",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_premise_status_report(
    payload: BaoCaoTrangThaiMatBangCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_VHBT])),
) -> Dict[str, Any]:
    result = maintenance_report_service.create_premise_status_report(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập báo cáo trạng thái mặt bằng thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_maintenance_reports(
    filters: BaoCaoBaoTriFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = maintenance_report_service.list_maintenance_reports(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách báo cáo bảo trì thành công",
        data=result,
    )


@router.get(
    "/{ma_bc_bt}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_maintenance_report_detail(
    ma_bc_bt: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = maintenance_report_service.get_maintenance_report_detail(
        db=db,
        ma_bc_bt=ma_bc_bt,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết báo cáo bảo trì thành công",
        data=result,
    )
