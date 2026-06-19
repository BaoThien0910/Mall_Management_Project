# File: app/schemas/taikhoan.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.validators import ensure_not_blank


class TaiKhoanCreate(BaseModel):
    ten_dang_nhap: str = Field(..., max_length=50)
    mat_khau_tam: str = Field(..., min_length=8, max_length=255)
    ma_vai_tro: str = Field(..., max_length=20)
    ma_nhan_vien: Optional[str] = Field(default=None, max_length=20)
    ma_khach_thue: Optional[str] = Field(default=None, max_length=20)

    @field_validator("ten_dang_nhap", "mat_khau_tam", "ma_vai_tro")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value

    @field_validator("ma_nhan_vien", "ma_khach_thue")
    @classmethod
    def validate_optional_code(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not ensure_not_blank(value):
            raise ValueError("Mã liên kết không được là chuỗi rỗng.")
        return value

    @model_validator(mode="after")
    def validate_account_subject(self) -> "TaiKhoanCreate":
        has_nhan_vien = ensure_not_blank(self.ma_nhan_vien)
        has_khach_thue = ensure_not_blank(self.ma_khach_thue)

        if has_nhan_vien == has_khach_thue:
            raise ValueError(
                "Tài khoản phải gắn với đúng một chủ thể: nhân viên hoặc khách thuê."
            )
        return self


class TaiKhoanDisableRequest(BaseModel):
    ly_do: Optional[str] = Field(default=None, max_length=500)


class TaiKhoanEnableRequest(BaseModel):
    ly_do: Optional[str] = Field(default=None, max_length=500)


class TaiKhoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_tai_khoan: str
    ten_dang_nhap: str
    trang_thai: str
    bat_buoc_doi_mk: bool
    so_lan_dang_nhap_sai: int
    khoa_den: Optional[datetime] = None
    ma_nhan_vien: Optional[str] = None
    ma_khach_thue: Optional[str] = None
    ma_vai_tro: str
    ngay_tao: datetime


class TaiKhoanFilter(BaseModel):
    keyword: Optional[str] = Field(default=None, max_length=255)
    ma_vai_tro: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[str] = Field(default=None, max_length=30)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
