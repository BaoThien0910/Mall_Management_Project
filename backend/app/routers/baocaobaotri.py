# File: app/routers/baocaobaotri.py
"""
Router Báo cáo trạng thái mặt bằng.

Phân quyền:
- Lập báo cáo : TP_VHBT
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.baocaobaotri import BaoCaoBaoTriCreate, BaoCaoBaoTriResponse
from app.services import maintenance_report_service
from app.constants.roles import TP_VHBT

router = APIRouter(prefix="/api/v1/bao-cao-bao-tri", tags=["Báo cáo bảo trì"])


def _require_roles(current_user: Any, allowed_roles: set[str]) -> None:
    if current_user.mavaitro not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── POST /api/v1/bao-cao-bao-tri/trang-thai-mat-bang ─────────────────────────

@router.post(
    "/trang-thai-mat-bang",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
def lap_bao_cao_trang_thai(
    body: BaoCaoBaoTriCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """
    TP_VHBT lập báo cáo trạng thái thực tế của mặt bằng.

    - Mặt bằng phải tồn tại
    - Ngày kiểm tra không được ở tương lai
    - Trạng thái thực tế phải hợp lệ
    """
    _require_roles(current_user, {TP_VHBT})

    bc = maintenance_report_service.create_bao_cao(db, body, current_user.matk)

    return {
        "success": True,
        "message": "Lập báo cáo trạng thái mặt bằng thành công",
        "data": BaoCaoBaoTriResponse.model_validate(bc).model_dump(),
    }
