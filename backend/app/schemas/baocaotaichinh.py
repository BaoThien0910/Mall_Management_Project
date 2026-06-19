# File: app/schemas/baocaotaichinh.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.validators import validate_month, validate_year


class BaoCaoTaiChinhCreate(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000, le=2100)

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


class BaoCaoTaiChinhFilter(BaseModel):
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


class BaoCaoTaiChinhListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_bao_cao: str
    ma_nhan_vien_lap: str
    thang: int
    nam: int
    ky_chot: str
    ngay_lap: datetime


class BaoCaoTaiChinhChiTietItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stt: int
    ma_hop_dong: str
    ma_khach_thue: str
    ma_mat_bang: str
    ky: str
    tien_thue: Decimal
    tien_dien: Decimal
    tien_nuoc: Decimal
    tien_hoan_tra: Decimal
    chi_phi_bao_tri: Decimal
    tong_tien: Decimal
    da_thanh_toan: Decimal
    no: Decimal


class BaoCaoTaiChinhThongKe(BaseModel):
    tong_so_hd: int
    tong_so_hd_con_no: int
    tong: Decimal
    tong_tt: Decimal
    tong_no: Decimal


class BaoCaoTaiChinhDetail(BaseModel):
    bao_cao: BaoCaoTaiChinhListItem
    chi_tiet: list[BaoCaoTaiChinhChiTietItem]
    thong_ke: BaoCaoTaiChinhThongKe


# Backward compatibility for app/schemas/__init__.py and any old imports.
# The redesigned report API returns detail/list data through service response dicts,
# but the old project init still imports this symbol during application startup.
class BaoCaoTaiChinhResponse(BaoCaoTaiChinhDetail):
    pass
