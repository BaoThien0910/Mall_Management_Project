# File: app/schemas/baocaotaichinh.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.statuses import BaoCaoTaiChinhStatus, LoaiBaoCaoTaiChinh
from app.utils.validators import ensure_not_blank, validate_month, validate_year


class BaoCaoTaiChinhCreate(BaseModel):
    loai_bao_cao: LoaiBaoCaoTaiChinh
    thang: int
    nam: int
    noi_dung: str = Field(..., min_length=1)
    tong_tien: Optional[Decimal] = Field(default=None, ge=0)

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

    @field_validator("noi_dung")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Nội dung không được để trống.")
        return value


class BaoCaoTaiChinhResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_bao_cao_tai_chinh: str
    loai_bao_cao: LoaiBaoCaoTaiChinh
    thang: int
    nam: int
    ma_nhan_vien_lap: str
    ngay_lap: datetime
    noi_dung: str
    tong_tien: Optional[Decimal] = None
    trang_thai: BaoCaoTaiChinhStatus


class BaoCaoTaiChinhFilter(BaseModel):
    loai_bao_cao: Optional[LoaiBaoCaoTaiChinh] = None
    thang: Optional[int] = None
    nam: Optional[int] = None
    trang_thai: Optional[BaoCaoTaiChinhStatus] = None
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
