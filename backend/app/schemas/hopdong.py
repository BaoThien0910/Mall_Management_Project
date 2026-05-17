# File: app/schemas/hopdong.py
"""
Pydantic v2 schemas cho module Quản lý Hợp đồng.
"""

from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants.statuses import TrangThaiHopDong


# ── Create ────────────────────────────────────────────────────────────────────

class HopDongCreate(BaseModel):
    mahd: str = Field(..., min_length=1, max_length=20, description="Mã hợp đồng (duy nhất)")
    makh: str = Field(..., min_length=1, max_length=20, description="Mã khách thuê")
    mamb: str = Field(..., min_length=1, max_length=20, description="Mã mặt bằng")
    ngaybatdau: date = Field(..., description="Ngày bắt đầu hợp đồng")
    ngayketthuc: date = Field(..., description="Ngày kết thúc hợp đồng")
    giathuethang: float = Field(..., gt=0, description="Giá thuê mỗi tháng (VNĐ), phải > 0")
    trangthai: str = Field(
        default=TrangThaiHopDong.DANG_HIEU_LUC,
        description="Trạng thái hợp đồng"
    )
    ghichu: Optional[str] = Field(None, max_length=1000)
    mayc: Optional[str] = Field(
        None,
        max_length=20,
        description="Mã yêu cầu thuê thêm liên kết (tuỳ chọn)"
    )

    @field_validator("trangthai")
    @classmethod
    def validate_trangthai(cls, v: str) -> str:
        if v not in TrangThaiHopDong.ALL:
            raise ValueError(
                f"Trạng thái không hợp lệ. Chấp nhận: {TrangThaiHopDong.ALL}"
            )
        return v

    @model_validator(mode="after")
    def check_dates(self) -> HopDongCreate:
        if self.ngayketthuc <= self.ngaybatdau:
            raise ValueError("ngayketthuc phải sau ngaybatdau")
        return self


# ── Response ──────────────────────────────────────────────────────────────────

class HopDongResponse(BaseModel):
    mahd: str
    makh: str
    mamb: str
    ngaybatdau: date
    ngayketthuc: date
    giathuethang: float
    trangthai: str
    ghichu: Optional[str]
    mayc: Optional[str]

    model_config = {"from_attributes": True}


# ── Filter / Query params ─────────────────────────────────────────────────────

class HopDongFilter(BaseModel):
    makh: Optional[str] = None
    mamb: Optional[str] = None
    trangthai: Optional[str] = None
    ngaybatdau_tu: Optional[date] = None
    ngaybatdau_den: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
