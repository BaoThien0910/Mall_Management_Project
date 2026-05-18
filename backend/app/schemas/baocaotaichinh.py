# File: app/schemas/baocaotaichinh.py
"""
Pydantic v2 schemas cho module Báo cáo tài chính.
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from app.constants.statuses import LoaiBaoCao


# ── Create báo cáo công nợ ────────────────────────────────────────────────────

class BaoCaoCongNoCreate(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000)
    noi_dung_tong_hop: Optional[str] = Field(None, max_length=2000)


# ── Create báo cáo doanh số ───────────────────────────────────────────────────

class BaoCaoDoanhSoCreate(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000)
    noi_dung_tong_hop: Optional[str] = Field(None, max_length=2000)


# ── Response ──────────────────────────────────────────────────────────────────

class BaoCaoTaiChinhResponse(BaseModel):
    mabctc: str
    loai_bao_cao: str
    thang: int
    nam: int
    nguoi_lap: str
    ngay_lap: date
    noi_dung_tong_hop: Optional[str]
    tong_gia_tri: Optional[float]
    trang_thai: str

    model_config = {"from_attributes": True}


# ── Filter ────────────────────────────────────────────────────────────────────

class BaoCaoFilter(BaseModel):
    loai_bao_cao: Optional[str] = None
    thang: Optional[int] = Field(None, ge=1, le=12)
    nam: Optional[int] = Field(None, ge=2000)
    trang_thai: Optional[str] = None
    nguoi_lap: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
