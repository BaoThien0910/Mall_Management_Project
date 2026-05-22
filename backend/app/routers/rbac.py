# File: app/routers/rbac.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.database import get_db
from app.dependencies import require_roles
from app.schemas.rbac import VaiTroQuyenAssignRequest
from app.services import rbac_service
from app.utils.response import success_response


router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)


@router.get(
    "/vai-tro",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_roles(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = rbac_service.list_roles(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách vai trò thành công",
        data=result,
    )


@router.get(
    "/quyen",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def list_permissions(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = rbac_service.list_permissions(
        db=db,
        current_user=current_user,
    )
    return success_response(
        message="Lấy danh sách quyền thành công",
        data=result,
    )


@router.get(
    "/vai-tro/{ma_vai_tro}/quyen",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def get_permissions_by_role(
    ma_vai_tro: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = rbac_service.get_permissions_by_role(
        db=db,
        ma_vai_tro=ma_vai_tro,
        current_user=current_user,
    )
    return success_response(
        message="Lấy quyền của vai trò thành công",
        data=result,
    )


@router.put(
    "/vai-tro/{ma_vai_tro}/quyen",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
def assign_permissions_to_role(
    ma_vai_tro: str,
    payload: VaiTroQuyenAssignRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles([RoleCode.QTV])),
) -> Dict[str, Any]:
    result = rbac_service.assign_permissions_to_role(
        db=db,
        ma_vai_tro=ma_vai_tro,
        payload=payload,
        current_user=current_user,
    )
    return success_response(
        message="Gán quyền cho vai trò thành công",
        data=result,
    )
