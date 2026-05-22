# File: app/routers/thongbao.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.schemas.thongbao import (
    ThongBaoCreate,
    ThongBaoFilter,
    ThuHoiThongBaoRequest,
)
from app.services import notification_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/thong-bao",
    tags=["Thông báo"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_announcement(
    payload: ThongBaoCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL])),
) -> Dict[str, Any]:
    result = notification_service.create_announcement(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Ban hành thông báo thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_announcements(
    filters: ThongBaoFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result = notification_service.list_announcements(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách thông báo thành công",
        data=result,
    )


@router.get(
    "/{ma_tb}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_announcement_detail(
    ma_tb: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Dict[str, Any]:
    result = notification_service.get_announcement_detail(
        db=db,
        ma_tb=ma_tb,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết thông báo thành công",
        data=result,
    )


@router.patch(
    "/{ma_tb}/thu-hoi",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def revoke_announcement(
    ma_tb: str,
    payload: ThuHoiThongBaoRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL])),
) -> Dict[str, Any]:
    result = notification_service.revoke_announcement(
        db=db,
        ma_tb=ma_tb,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Thu hồi thông báo thành công",
        data=result,
    )
