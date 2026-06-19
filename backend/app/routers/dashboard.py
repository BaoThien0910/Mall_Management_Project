# File: app/routers/dashboard.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.services import dashboard_service
from app.utils.response import success_response

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
)
def get_my_dashboard(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result = dashboard_service.get_my_dashboard(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Lấy dữ liệu dashboard thành công",
        data=result,
    )
