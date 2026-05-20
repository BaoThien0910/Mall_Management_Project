# File: app/routers/nhatky.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import AUDIT_VIEW_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.nhatky import NhatKyFilter
from app.services import audit_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/nhat-ky",
    tags=["Nhật ký thao tác"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_audit_logs(
    filters: NhatKyFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(AUDIT_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = audit_service.list_audit_logs(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách nhật ký thao tác thành công",
        data=result,
    )
