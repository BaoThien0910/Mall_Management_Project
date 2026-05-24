# File: app/schemas/chisodiennuoc.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChiSoDienNuocCreate(BaseModel):
    ma_mat_bang: str = Field(..., min_length=1, max_length=20)
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000, le=2100)
    chi_so_dien_dau: Decimal = Field(..., ge=0)
    chi_so_dien_cuoi: Decimal = Field(..., ge=0)
    chi_so_nuoc_dau: Decimal = Field(..., ge=0)
    chi_so_nuoc_cuoi: Decimal = Field(..., ge=0)

    @field_validator("chi_so_dien_cuoi")
    @classmethod
    def validate_electricity_end(cls, value: Decimal, info: object) -> Decimal:
        data = getattr(info, "data", {})
        start_value = data.get("chi_so_dien_dau")
        if start_value is not None and value < start_value:
            raise ValueError("Chỉ số điện cuối phải lớn hơn hoặc bằng chỉ số điện đầu")
        return value

    @field_validator("chi_so_nuoc_cuoi")
    @classmethod
    def validate_water_end(cls, value: Decimal, info: object) -> Decimal:
        data = getattr(info, "data", {})
        start_value = data.get("chi_so_nuoc_dau")
        if start_value is not None and value < start_value:
            raise ValueError("Chỉ số nước cuối phải lớn hơn hoặc bằng chỉ số nước đầu")
        return value


class ChiSoDienNuocFilter(BaseModel):
    ma_mat_bang: Optional[str] = None
    thang: Optional[int] = Field(default=None, ge=1, le=12)
    nam: Optional[int] = Field(default=None, ge=2000, le=2100)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ChiSoDienNuocResponse(BaseModel):
    ma_chi_so_dien_nuoc: str
    ma_mat_bang: str
    ma_nhan_vien_nhap: str
    thang: int
    nam: int
    chi_so_dien_dau: Decimal
    chi_so_dien_cuoi: Decimal
    chi_so_nuoc_dau: Decimal
    chi_so_nuoc_cuoi: Decimal
    so_dien_tieu_thu: Decimal
    so_nuoc_tieu_thu: Decimal
    don_gia_dien: Decimal
    don_gia_nuoc: Decimal
    tien_dien: Decimal
    tien_nuoc: Decimal
    ngay_nhap: datetime

    model_config = ConfigDict(from_attributes=True)
