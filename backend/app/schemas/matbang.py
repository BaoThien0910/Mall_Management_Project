# File: app/schemas/matbang.py
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants.statuses import MatBangStatus
from app.utils.validators import ensure_not_blank


class MatBangCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    vi_tri: str = Field(..., max_length=100)
    tang: int
    dien_tich: Decimal = Field(..., gt=0)
    loai_mat_bang: str = Field(..., max_length=50)
    trang_thai: MatBangStatus
    ghi_chu: Optional[str] = Field(default=None, max_length=255)

    @field_validator("ma_mat_bang", "vi_tri", "loai_mat_bang")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class MatBangUpdate(BaseModel):
    vi_tri: Optional[str] = Field(default=None, max_length=100)
    tang: Optional[int] = None
    dien_tich: Optional[Decimal] = Field(default=None, gt=0)
    loai_mat_bang: Optional[str] = Field(default=None, max_length=50)
    trang_thai: Optional[MatBangStatus] = None
    ghi_chu: Optional[str] = Field(default=None, max_length=255)

    @field_validator("vi_tri", "loai_mat_bang")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not ensure_not_blank(value):
            raise ValueError("Giá trị không được là chuỗi rỗng.")
        return value


class MatBangResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_mat_bang: str
    vi_tri: str
    tang: int
    dien_tich: Decimal
    loai_mat_bang: str
    trang_thai: MatBangStatus
    ghi_chu: Optional[str] = None


class MatBangFilter(BaseModel):
    keyword: Optional[str] = None
    trang_thai: Optional[str] = None
    tang: Optional[str] = None
    loai_mat_bang: Optional[str] = Field(default=None, max_length=255)
    dien_tich_tu: Optional[Decimal] = Field(default=None, ge=0)
    dien_tich_den: Optional[Decimal] = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def validate_area_range(self) -> "MatBangFilter":
        if (
            self.dien_tich_tu is not None
            and self.dien_tich_den is not None
            and self.dien_tich_den < self.dien_tich_tu
        ):
            raise ValueError("Diện tích đến phải lớn hơn hoặc bằng diện tích từ.")
        return self
