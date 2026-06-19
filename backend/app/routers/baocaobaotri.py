# File: app/routers/baocaobaotri.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.baocaobaotri import BaoCaoBaoTriCreate, BaoCaoBaoTriFilter
from app.services import maintenance_report_service
from app.utils.response import success_response

router = APIRouter(
    prefix="/bao-cao-bao-tri",
    tags=["Báo cáo bảo trì"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_maintenance_report(
    payload: BaoCaoBaoTriCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_VHBT])),
) -> Dict[str, Any]:
    result = maintenance_report_service.create_maintenance_report(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập báo cáo bảo trì thành công",
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
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_VHBT])),
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
    "/{ma_bc}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_maintenance_report_detail(
    ma_bc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_VHBT])),
) -> Dict[str, Any]:
    result = maintenance_report_service.get_maintenance_report_detail(
        db=db,
        ma_bc=ma_bc,
        current_user=current_user,
    )
    return success_response(
        message="Lấy nội dung báo cáo bảo trì thành công",
        data=result,
    )


@router.get(
    "/{ma_bc}/excel",
    status_code=status.HTTP_200_OK,
)
def export_maintenance_report_excel(
    ma_bc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_VHBT])),
) -> StreamingResponse:
    output = maintenance_report_service.export_maintenance_report_excel(
        db=db,
        ma_bc=ma_bc,
        current_user=current_user,
    )
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="bao-cao-bao-tri-{ma_bc}.xlsx"'},
    )
