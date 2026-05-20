# File: app/routers/sk_baotri.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import PREMISE_VIEW_ROLES, RoleCode, VHBT_ROLES
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.sk_baotri import (
    CapNhatKetQuaXuLySuCoRequest,
    DuyetSuCoBaoTriRequest,
    NhapChiPhiBaoTriRequest,
    PhanCongSuCoBaoTriRequest,
    SuCoBaoTriCreate,
    SuCoBaoTriFilter,
)
from app.services import incident_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/su-co-bao-tri",
    tags=["Sự cố bảo trì"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_incident(
    payload: SuCoBaoTriCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = incident_service.create_incident(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Gửi yêu cầu xử lý sự cố thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_incidents(
    filters: SuCoBaoTriFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(PREMISE_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = incident_service.list_incidents(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách sự cố bảo trì thành công",
        data=result,
    )


@router.patch(
    "/{ma_su_co}/duyet",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def review_incident(
    ma_su_co: str,
    payload: DuyetSuCoBaoTriRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.BQL])),
) -> Dict[str, Any]:
    result = incident_service.review_incident(
        db=db,
        ma_su_co=ma_su_co,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Xử lý duyệt sự cố bảo trì thành công",
        data=result,
    )


@router.patch(
    "/{ma_su_co}/phan-cong",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def assign_incident(
    ma_su_co: str,
    payload: PhanCongSuCoBaoTriRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.TP_VHBT])),
) -> Dict[str, Any]:
    result = incident_service.assign_incident(
        db=db,
        ma_su_co=ma_su_co,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Phân công xử lý sự cố thành công",
        data=result,
    )


@router.patch(
    "/{ma_su_co}/ket-qua",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def update_incident_result(
    ma_su_co: str,
    payload: CapNhatKetQuaXuLySuCoRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = incident_service.update_incident_result(
        db=db,
        ma_su_co=ma_su_co,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Cập nhật kết quả xử lý sự cố thành công",
        data=result,
    )


@router.patch(
    "/{ma_su_co}/chi-phi",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def update_incident_cost(
    ma_su_co: str,
    payload: NhapChiPhiBaoTriRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(VHBT_ROLES))),
) -> Dict[str, Any]:
    result = incident_service.update_incident_cost(
        db=db,
        ma_su_co=ma_su_co,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Cập nhật chi phí bảo trì thành công",
        data=result,
    )
