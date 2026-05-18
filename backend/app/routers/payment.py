# File: app/routers/payment.py
"""
Router Thanh toán mô phỏng.
Phân quyền: KHACH_THUE
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.payment import (
    HoaDonResponse,
    MoPhongKetQuaInput,
    TaoGiaoDichInput,
)
from app.services import payment_service
from app.constants.roles import KHACH_THUE

router = APIRouter(prefix="/api/v1/thanh-toan", tags=["Thanh toán mô phỏng"])


def _require_khach_thue(current_user: Any) -> None:
    if current_user.mavaitro != KHACH_THUE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ khách thuê mới được sử dụng chức năng thanh toán",
        )


def _require_makh(current_user: Any) -> str:
    if not current_user.makh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không liên kết với khách thuê nào",
        )
    return current_user.makh


# ── POST /api/v1/thanh-toan/tao-giao-dich ────────────────────────────────────

@router.post("/tao-giao-dich", response_model=dict, status_code=status.HTTP_201_CREATED)
def tao_giao_dich(
    body: TaoGiaoDichInput,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê tạo giao dịch thanh toán mô phỏng cho công nợ."""
    _require_khach_thue(current_user)
    makh = _require_makh(current_user)

    hoadon = payment_service.tao_giao_dich(
        db=db,
        data=body,
        makh=makh,
        matk=current_user.matk,
    )

    return {
        "success": True,
        "message": f"Tạo giao dịch thanh toán thành công - mã GD: {hoadon.ma_giao_dich_mo_phong}",
        "data": HoaDonResponse.model_validate(hoadon).model_dump(),
    }


# ── GET /api/v1/thanh-toan/cua-toi ───────────────────────────────────────────
# Đặt TRƯỚC /{mahoadon}

@router.get("/cua-toi", response_model=dict)
def hoadon_cua_toi(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê xem toàn bộ lịch sử hóa đơn của mình."""
    _require_khach_thue(current_user)
    makh = _require_makh(current_user)

    items = payment_service.list_hoadon_cua_toi(db, makh)

    return {
        "success": True,
        "message": "Lấy lịch sử thanh toán thành công",
        "data": [HoaDonResponse.model_validate(hd).model_dump() for hd in items],
    }


# ── GET /api/v1/thanh-toan/{mahoadon} ────────────────────────────────────────

@router.get("/{mahoadon}", response_model=dict)
def get_hoadon(
    mahoadon: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Chi tiết một hóa đơn (chỉ của khách thuê đang đăng nhập)."""
    _require_khach_thue(current_user)
    makh = _require_makh(current_user)

    hoadon = payment_service.get_hoadon_detail(db, mahoadon, makh)

    return {
        "success": True,
        "message": "Lấy chi tiết hóa đơn thành công",
        "data": HoaDonResponse.model_validate(hoadon).model_dump(),
    }


# ── POST /api/v1/thanh-toan/{mahoadon}/mo-phong-ket-qua ──────────────────────

@router.post("/{mahoadon}/mo-phong-ket-qua", response_model=dict)
def mo_phong_ket_qua(
    mahoadon: str,
    body: MoPhongKetQuaInput,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Mô phỏng kết quả thanh toán: THANH_CONG hoặc THAT_BAI."""
    _require_khach_thue(current_user)
    makh = _require_makh(current_user)

    hoadon = payment_service.mo_phong_ket_qua(
        db=db,
        mahoadon=mahoadon,
        data=body,
        makh=makh,
        matk=current_user.matk,
    )

    ket_qua_label = "Thành công" if body.ket_qua == "THANH_CONG" else "Thất bại"

    return {
        "success": True,
        "message": f"Kết quả thanh toán: {ket_qua_label}",
        "data": HoaDonResponse.model_validate(hoadon).model_dump(),
    }
