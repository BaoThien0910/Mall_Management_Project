# File: app/schemas/hopdong.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants.statuses import HopDongStatus
from app.utils.validators import ensure_not_blank


class HopDongCreate(BaseModel):
    ma_hop_dong: str = Field(..., max_length=20)
    ma_khach_thue: str = Field(..., max_length=20)
    ma_mat_bang: str = Field(..., max_length=20)
    ma_nhan_vien_so_hoa: Optional[str] = Field(default=None, max_length=20)
    ma_yeu_cau: Optional[str] = Field(default=None, max_length=20)
    ngay_bat_dau: date
    ngay_ket_thuc: date
    gia_thue_thang: Decimal = Field(..., gt=0)

    @field_validator("ma_hop_dong", "ma_khach_thue", "ma_mat_bang")
    @classmethod
    def validate_required_codes(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Mã không được để trống.")
        return value

    @field_validator("ma_nhan_vien_so_hoa", "ma_yeu_cau")
    @classmethod
    def validate_optional_codes(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not ensure_not_blank(value):
            raise ValueError("Mã không được là chuỗi rỗng.")
        return value

    @model_validator(mode="after")
    def validate_contract_date_range(self) -> "HopDongCreate":
        if self.ngay_ket_thuc <= self.ngay_bat_dau:
            raise ValueError("Ngày kết thúc phải lớn hơn ngày bắt đầu.")
        return self


class HopDongResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_hop_dong: str
    ma_khach_thue: str
    ma_mat_bang: str
    ma_nhan_vien_so_hoa: str
    ma_yeu_cau: Optional[str] = None
    ngay_bat_dau: date
    ngay_ket_thuc: date
    gia_thue_thang: Decimal
    trang_thai: HopDongStatus
    ngay_so_hoa: datetime


class HopDongFilter(BaseModel):
    ma_khach_thue: Optional[str] = Field(default=None, max_length=20)
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[HopDongStatus] = None
    ngay_bat_dau_tu: Optional[date] = None
    ngay_bat_dau_den: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def validate_filter_date_range(self) -> "HopDongFilter":
        if (
            self.ngay_bat_dau_tu is not None
            and self.ngay_bat_dau_den is not None
            and self.ngay_bat_dau_den < self.ngay_bat_dau_tu
        ):
            raise ValueError("Ngày bắt đầu đến phải lớn hơn hoặc bằng ngày bắt đầu từ.")
        return self


class HopDongCuaToiFilter(BaseModel):
    trang_thai: Optional[HopDongStatus] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
