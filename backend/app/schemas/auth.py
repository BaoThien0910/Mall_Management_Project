# File: app/schemas/auth.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.validators import ensure_not_blank


class DangNhapRequest(BaseModel):
    ten_dang_nhap: str = Field(..., max_length=50)
    mat_khau: str = Field(..., max_length=255)

    @field_validator("ten_dang_nhap", "mat_khau")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class DoiMatKhauRequest(BaseModel):
    mat_khau_cu: str = Field(..., max_length=255)
    mat_khau_moi: str = Field(..., min_length=8, max_length=255)
    xac_nhan_mat_khau_moi: str = Field(..., min_length=8, max_length=255)

    @field_validator("mat_khau_cu", "mat_khau_moi", "xac_nhan_mat_khau_moi")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "DoiMatKhauRequest":
        if self.mat_khau_moi != self.xac_nhan_mat_khau_moi:
            raise ValueError("Xác nhận mật khẩu mới không khớp.")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_tai_khoan: str
    ten_dang_nhap: str
    ma_vai_tro: str
    ma_nhan_vien: Optional[str] = None
    ma_khach_thue: Optional[str] = None
