# File: app/schemas/chisodiennuoc.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.validators import ensure_not_blank, validate_month, validate_year


class ChiSoDienNuocCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    thang: int
    nam: int
    chi_so_dien_dau: Decimal = Field(..., ge=0)
    chi_so_dien_cuoi: Decimal = Field(..., ge=0)
    chi_so_nuoc_dau: Decimal = Field(..., ge=0)
    chi_so_nuoc_cuoi: Decimal = Field(..., ge=0)

    @field_validator("ma_mat_bang")
    @classmethod
    def validate_premise_code(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Mã mặt bằng không được để trống.")
        return value

    @field_validator("thang")
    @classmethod
    def validate_month_value(cls, value: int) -> int:
        if not validate_month(value):
            raise ValueError("Tháng phải nằm trong khoảng 1 đến 12.")
        return value

    @field_validator("nam")
    @classmethod
    def validate_year_value(cls, value: int) -> int:
        if not validate_year(value):
            raise ValueError("Năm phải nằm trong khoảng 2000 đến 2100.")
        return value

    @model_validator(mode="after")
    def validate_meter_ranges(self) -> "ChiSoDienNuocCreate":
        if self.chi_so_dien_cuoi < self.chi_so_dien_dau:
            raise ValueError("Chỉ số điện cuối phải lớn hơn hoặc bằng chỉ số điện đầu.")
        if self.chi_so_nuoc_cuoi < self.chi_so_nuoc_dau:
            raise ValueError("Chỉ số nước cuối phải lớn hơn hoặc bằng chỉ số nước đầu.")
        return self


class ChiSoDienNuocResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_chi_so_dien_nuoc: str
    ma_mat_bang: str
    ma_nhan_vien_nhap: str
    thang: int
    nam: int
    chi_so_dien_dau: Decimal
    chi_so_dien_cuoi: Decimal
    chi_so_nuoc_dau: Decimal
    chi_so_nuoc_cuoi: Decimal
    ngay_nhap: datetime


class ChiSoDienNuocFilter(BaseModel):
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    thang: Optional[int] = None
    nam: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("thang")
    @classmethod
    def validate_optional_month(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not validate_month(value):
            raise ValueError("Tháng phải nằm trong khoảng 1 đến 12.")
        return value

    @field_validator("nam")
    @classmethod
    def validate_optional_year(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not validate_year(value):
            raise ValueError("Năm phải nằm trong khoảng 2000 đến 2100.")
        return value
