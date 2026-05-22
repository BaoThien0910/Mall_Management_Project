# File: app/routers/import_taichinh.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.constants.roles import KDTC_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.dulieu_import_taichinh import DuLieuImportTaiChinhFilter
from app.services import excel_import_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/import-tai-chinh",
    tags=["Import tài chính"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def import_financial_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = excel_import_service.import_financial_excel(
        db=db,
        file=file,
        current_user=current_user,
    )
    return success_response(
        message="Import dữ liệu tài chính thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_import_history(
    filters: DuLieuImportTaiChinhFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = excel_import_service.list_import_history(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy lịch sử import tài chính thành công",
        data=result,
    )
