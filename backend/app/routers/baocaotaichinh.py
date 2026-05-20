# File: app/routers/baocaotaichinh.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.baocaotaichinh import (
    BaoCaoTaiChinhCreate,
    BaoCaoTaiChinhFilter,
)
from app.services import financial_report_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/bao-cao-tai-chinh",
    tags=["Báo cáo tài chính"],
)


@router.post(
    "/cong-no",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_debt_report(
    payload: BaoCaoTaiChinhCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.create_debt_report(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập báo cáo công nợ thành công",
        data=result,
    )


@router.post(
    "/doanh-so",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_revenue_report(
    payload: BaoCaoTaiChinhCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.create_revenue_report(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Lập báo cáo doanh số thành công",
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
    "/{ma_bctc}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_financial_report_detail(
    ma_bctc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL, RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.get_financial_report_detail(
        db=db,
        ma_bctc=ma_bctc,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết báo cáo tài chính thành công",
        data=result,
    )


@router.patch(
    "/{ma_bctc}/ban-hanh",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def publish_financial_report(
    ma_bctc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_KDTC])),
) -> Dict[str, Any]:
    result = financial_report_service.publish_financial_report(
        db=db,
        ma_bctc=ma_bctc,
        current_user=current_user,
    )
    return success_response(
        message="Ban hành báo cáo tài chính thành công",
        data=result,
    )
