# File: app/routers/hopdong.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import CONTRACT_LIST_VIEW_ROLES, KDTC_ROLES, RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.hopdong import (
    HopDongCreate,
    HopDongCuaToiFilter,
    HopDongFilter,
)
from app.services import contract_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/hop-dong",
    tags=["Hợp đồng"],
)


@router.get(
    "/cua-toi",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_my_contracts(
    filters: HopDongCuaToiFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.KHACH_THUE])),
) -> Dict[str, Any]:
    result = contract_service.list_my_contracts(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách hợp đồng của tôi thành công",
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_contracts(
    filters: HopDongFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(CONTRACT_LIST_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = contract_service.list_contracts(
        db=db,
        filters=filters,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách hợp đồng thành công",
        data=result,
    )


@router.get(
    "/{ma_hd}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_contract_detail(
    ma_hd: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(CONTRACT_LIST_VIEW_ROLES))),
) -> Dict[str, Any]:
    result = contract_service.get_contract_detail(
        db=db,
        ma_hd=ma_hd,
        current_user=current_user,
    )
    return success_response(
        message="Lấy chi tiết hợp đồng thành công",
        data=result,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
)
def create_contract(
    payload: HopDongCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles(list(KDTC_ROLES))),
) -> Dict[str, Any]:
    result = contract_service.create_contract(
        db=db,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Tạo hợp đồng thành công",
        data=result,
    )
