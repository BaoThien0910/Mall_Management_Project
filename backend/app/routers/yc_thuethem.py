# File: app/routers/yc_thuethem.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.yc_thuethem import (
    DuyetYeuCauThueThemRequest,
    YeuCauThueThemCreate,
    YeuCauThueThemFilter,
)
from app.services import rent_request_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/yeu-cau-thue-them",
    tags=["Yêu cầu thuê thêm"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_rent_request(
    payload: YeuCauThueThemCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = rent_request_service.create_rent_request(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Gửi yêu cầu thuê thêm thành công",
        data=result,
    )


@router.get(
    "/cua-toi",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_my_rent_requests(
    filters: YeuCauThueThemFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = rent_request_service.list_my_rent_requests(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách yêu cầu thuê thêm của tôi thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_rent_requests(
    filters: YeuCauThueThemFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL])),
) -> Dict[str, Any]:
    result = rent_request_service.list_rent_requests(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách yêu cầu thuê thêm thành công",
        data=result,
    )


@router.patch(
    "/{ma_yc}/duyet",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def review_rent_request(
    ma_yc: str,
    payload: DuyetYeuCauThueThemRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL])),
) -> Dict[str, Any]:
    result = rent_request_service.review_rent_request(
        db=db,
        ma_yc=ma_yc,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Xử lý yêu cầu thuê thêm thành công",
        data=result,
    )
