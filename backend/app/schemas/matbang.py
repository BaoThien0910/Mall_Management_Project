# File: app/schemas/matbang.py
"""
Pydantic v2 schemas cho module Quản lý Mặt bằng.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants.statuses import TrangThaiMatBang


# ── Create ────────────────────────────────────────────────────────────────────

class MatBangCreate(BaseModel):
    mamb: str = Field(..., min_length=1, max_length=20, description="Mã mặt bằng (duy nhất)")
    tenmb: str = Field(..., min_length=1, max_length=100, description="Tên / ký hiệu mặt bằng")
    tang: Optional[str] = Field(None, max_length=10, description="Tầng")
    loaimb: Optional[str] = Field(None, max_length=50, description="Loại mặt bằng")
    dientich: float = Field(..., gt=0, description="Diện tích (m²), phải > 0")
    giathuethang: Optional[float] = Field(None, ge=0, description="Giá thuê tháng mặc định")
    trangthai: str = Field(
        default=TrangThaiMatBang.CON_TRONG,
        description="Trạng thái mặt bằng"
    )
    ghichu: Optional[str] = Field(None, max_length=500)

    @field_validator("trangthai")
    @classmethod
    def validate_trangthai(cls, v: str) -> str:
        if v not in TrangThaiMatBang.ALL:
            raise ValueError(
                f"Trạng thái không hợp lệ. Chấp nhận: {TrangThaiMatBang.ALL}"
            )
        return v


# ── Update ────────────────────────────────────────────────────────────────────

class MatBangUpdate(BaseModel):
    tenmb: Optional[str] = Field(None, min_length=1, max_length=100)
    tang: Optional[str] = Field(None, max_length=10)
    loaimb: Optional[str] = Field(None, max_length=50)
    dientich: Optional[float] = Field(None, gt=0)
    giathuethang: Optional[float] = Field(None, ge=0)
    trangthai: Optional[str] = None
    ghichu: Optional[str] = Field(None, max_length=500)

    @field_validator("trangthai")
    @classmethod
    def validate_trangthai(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TrangThaiMatBang.ALL:
            raise ValueError(
                f"Trạng thái không hợp lệ. Chấp nhận: {TrangThaiMatBang.ALL}"
            )
        return v


# ── Response ──────────────────────────────────────────────────────────────────

class MatBangResponse(BaseModel):
    mamb: str
    tenmb: str
    tang: Optional[str]
    loaimb: Optional[str]
    dientich: float
    giathuethang: Optional[float]
    trangthai: str
    ghichu: Optional[str]

    model_config = {"from_attributes": True}


# ── Filter / Query params ─────────────────────────────────────────────────────

class MatBangFilter(BaseModel):
    trangthai: Optional[str] = None
    tang: Optional[str] = None
    loaimb: Optional[str] = None
    dientich_tu: Optional[float] = Field(None, ge=0)
    dientich_den: Optional[float] = Field(None, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def check_dientich_range(self) -> MatBangFilter:
        if (
            self.dientich_tu is not None
            and self.dientich_den is not None
            and self.dientich_tu > self.dientich_den
        ):
            raise ValueError("dientich_tu phải nhỏ hơn hoặc bằng dientich_den")
        return self
