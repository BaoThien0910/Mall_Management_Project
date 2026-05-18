# File: app/schemas/payment.py
"""
Pydantic v2 schemas cho module Thanh toán mô phỏng.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Tạo giao dịch ─────────────────────────────────────────────────────────────

class TaoGiaoDichInput(BaseModel):
    macn: str = Field(..., min_length=1, description="Mã công nợ cần thanh toán")
    phuong_thuc: Literal["VNPay", "MoMo", "ZaloPay"] = Field(
        ..., description="Phương thức thanh toán mô phỏng"
    )


# ── Mô phỏng kết quả thanh toán ──────────────────────────────────────────────

class MoPhongKetQuaInput(BaseModel):
    ket_qua: Literal["THANH_CONG", "THAT_BAI"] = Field(
        ..., description="Kết quả thanh toán mô phỏng"
    )


# ── Response hóa đơn ──────────────────────────────────────────────────────────

class HoaDonResponse(BaseModel):
    mahoadon: str
    macn: str
    makh: str
    so_tien_thanh_toan: float
    phuong_thuc: str
    ma_giao_dich_mo_phong: str
    trang_thai_giao_dich: str
    thoi_gian_giao_dich: Optional[datetime]
    # Snapshot từ CONGNO
    tien_thue: Optional[float]
    tien_dien: Optional[float]
    tien_nuoc: Optional[float]
    phi_bao_tri: Optional[float]
    tien_hoan_tra: Optional[float]
    tong_tien: Optional[float]

    model_config = {"from_attributes": True}
