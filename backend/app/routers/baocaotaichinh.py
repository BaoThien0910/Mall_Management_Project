# File: app/routers/baocaotaichinh.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.baocaotaichinh import BaoCaoTaiChinhCreate, BaoCaoTaiChinhFilter
from app.services import financial_report_service
from app.utils.response import success_response

router = APIRouter(
    prefix="/bao-cao-tai-chinh",
    tags=["Báo cáo tài chính"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_financial_report(
    payload: BaoCaoTaiChinhCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.create_financial_report(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập báo cáo tài chính thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_financial_reports(
    filters: BaoCaoTaiChinhFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.list_financial_reports(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách báo cáo tài chính thành công",
        data=result,
    )


@router.get(
    "/{ma_bc}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_financial_report_detail(
    ma_bc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.get_financial_report_detail(
        db=db,
        ma_bc=ma_bc,
        current_user=current_user,
    )
    return success_response(
        message="Lấy nội dung báo cáo tài chính thành công",
        data=result,
    )


@router.get(
    "/{ma_bc}/excel",
    status_code=status.HTTP_200_OK,
)
def export_financial_report_excel(
    ma_bc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_KDTC])),
) -> StreamingResponse:
    output = financial_report_service.export_financial_report_excel(
        db=db,
        ma_bc=ma_bc,
        current_user=current_user,
    )
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="bao-cao-tai-chinh-{ma_bc}.xlsx"'},
    )
