# File: app/schemas/yc_thuethem.py
"""
Pydantic v2 schemas cho module Yêu cầu thuê thêm mặt bằng.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

from app.constants.statuses import TrangThaiYeuCau


# ── Create (khách thuê gửi yêu cầu) ──────────────────────────────────────────

class YeuCauThuaThemCreate(BaseModel):
    mamb: str = Field(..., min_length=1, max_length=20, description="Mã mặt bằng muốn thuê thêm")
    ngayyeucau: Optional[date] = Field(
        default=None,
        description="Ngày gửi yêu cầu (mặc định hôm nay nếu không truyền)"
    )
    ghichu: Optional[str] = Field(None, max_length=1000, description="Ghi chú của khách thuê")


# ── Duyệt / Từ chối (Ban Quản Lý) ────────────────────────────────────────────

class YeuCauDuyetBody(BaseModel):
    ket_qua: Literal["DUYET", "TU_CHOI"] = Field(
        ..., description="Kết quả xét duyệt: DUYET hoặc TU_CHOI"
    )
    ly_do_tu_choi: Optional[str] = Field(
        None,
        max_length=500,
        description="Lý do từ chối (bắt buộc khi ket_qua = TU_CHOI)"
    )
    ghi_chu_cho_kdtc: Optional[str] = Field(
        None,
        max_length=500,
        description="Ghi chú nội bộ gửi phòng KDTC"
    )

    @field_validator("ly_do_tu_choi", mode="after")
    @classmethod
    def validate_ly_do(cls, v: Optional[str], info) -> Optional[str]:
        # Pydantic v2: info.data chứa các field đã validate trước đó
        ket_qua = info.data.get("ket_qua")
        if ket_qua == "TU_CHOI" and not v:
            raise ValueError("ly_do_tu_choi là bắt buộc khi từ chối yêu cầu")
        return v


# ── Response ──────────────────────────────────────────────────────────────────

class YeuCauThuaThemResponse(BaseModel):
    mayc: str
    makh: str
    mamb: str
    ngayyeucau: Optional[date]
    trangthai: str
    ghichu: Optional[str]
    ly_do_tu_choi: Optional[str]
    ghi_chu_cho_kdtc: Optional[str]

    model_config = {"from_attributes": True}


# ── Filter / Query params ─────────────────────────────────────────────────────

class YeuCauFilter(BaseModel):
    trangthai: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
