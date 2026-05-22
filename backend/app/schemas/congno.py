# File: app/schemas/congno.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import CongNoStatus
from app.utils.validators import validate_month, validate_year


class TinhCongNoThangRequest(BaseModel):
    thang: int
    nam: int

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


class CongNoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_cong_no: str
    ma_hop_dong: str
    thang: int
    nam: int
    tien_thue: Decimal
    tien_dien: Decimal
    tien_nuoc: Decimal
    phi_bao_tri: Decimal
    tien_hoan: Decimal
    tong_tien: Decimal
    han_thanh_toan: Optional[date] = None
    trang_thai: CongNoStatus
    ngay_lap: datetime


class CongNoFilter(BaseModel):
    ma_hop_dong: Optional[str] = Field(default=None, max_length=20)
    thang: Optional[int] = None
    nam: Optional[int] = None
    trang_thai: Optional[CongNoStatus] = None
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


class CongNoCuaToiFilter(BaseModel):
    ma_hop_dong: Optional[str] = Field(default=None, max_length=20)
    thang: Optional[int] = None
    nam: Optional[int] = None
    trang_thai: Optional[CongNoStatus] = None
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
