# File: app/routers/chisodiennuoc.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import VHBT_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.chisodiennuoc import (
    ChiSoDienNuocCreate,
    ChiSoDienNuocFilter,
)
from app.services import meter_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/chi-so-dien-nuoc",
    tags=["Chỉ số điện nước"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_meter_reading(
    payload: ChiSoDienNuocCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = meter_service.create_meter_reading(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Nhập chỉ số điện nước thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_meter_readings(
    filters: ChiSoDienNuocFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = meter_service.list_meter_readings(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách chỉ số điện nước thành công",
        data=result,
    )
