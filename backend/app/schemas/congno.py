# File: app/schemas/congno.py
"""
Pydantic v2 schemas cho module Công nợ.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from app.constants.statuses import TrangThaiCongNo


# ── Input tính công nợ ────────────────────────────────────────────────────────

class TinhCongNoInput(BaseModel):
    thang: int = Field(..., ge=1, le=12, description="Tháng tính công nợ")
    nam: int = Field(..., ge=2000, description="Năm tính công nợ")


# ── Response công nợ ──────────────────────────────────────────────────────────

class CongNoResponse(BaseModel):
    macn: str
    mahd: str
    thang: int
    nam: int
    tien_thue: float
    tien_dien: float
    tien_nuoc: float
    phi_bao_tri: float
    tien_hoan_tra: float
    tong_tien: float
    trang_thai: str

    model_config = {"from_attributes": True}


# ── Kết quả tính công nợ hàng loạt ───────────────────────────────────────────

class TinhCongNoKetQuaResponse(BaseModel):
    thang: int
    nam: int
    tong_hop_dong: int
    tao_thanh_cong: int
    bo_qua_trung: int               # Đã có công nợ kỳ này
    thieu_du_lieu: list[str]        # Danh sách mahd thiếu dữ liệu


# ── Filter ────────────────────────────────────────────────────────────────────

class CongNoFilter(BaseModel):
    mahd: Optional[str] = None
    makh: Optional[str] = None      # Lọc qua join HopDong
    thang: Optional[int] = Field(None, ge=1, le=12)
    nam: Optional[int] = Field(None, ge=2000)
    trang_thai: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
