# File: app/schemas/baocaobaotri.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.validators import validate_month, validate_year


class BaoCaoBaoTriCreate(BaseModel):
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


class BaoCaoBaoTriFilter(BaseModel):
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


class BaoCaoBaoTriListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_bao_cao: str
    ma_nhan_vien_lap: str
    thang: int
    nam: int
    ky_chot: str
    ngay_lap: datetime


class BaoCaoBaoTriChiTietItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stt: int
    ma_yeu_cau: str
    ma_mat_bang: str
    ngay_yeu_cau: datetime
    mo_ta: str
    trang_thai: str
    ngay_giai_quyet: Optional[datetime] = None
    ket_qua: Optional[str] = None


class BaoCaoBaoTriThongKe(BaseModel):
    tong_yeu_cau: int
    yeu_cau_da_giai_quyet: int


class BaoCaoBaoTriDetail(BaseModel):
    bao_cao: BaoCaoBaoTriListItem
    chi_tiet: list[BaoCaoBaoTriChiTietItem]
    thong_ke: BaoCaoBaoTriThongKe


# Backward compatibility for app/schemas/__init__.py and any old imports.
# The old report design used BaoCaoTrangThaiMatBangCreate/BaoCaoBaoTriResponse.
# The redesigned report flow only needs thang/nam, so these names are kept to
# prevent import-time crashes while the new routers use BaoCaoBaoTriCreate.
class BaoCaoTrangThaiMatBangCreate(BaoCaoBaoTriCreate):
    pass


class BaoCaoBaoTriResponse(BaoCaoBaoTriDetail):
    pass
