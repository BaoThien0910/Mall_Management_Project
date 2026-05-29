# File: app/schemas/sk_baotri.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants.statuses import SuCoBaoTriStatus
from app.utils.validators import ensure_not_blank


class SuCoBaoTriCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    mo_ta: str = Field(..., min_length=1, max_length=4000)

    @field_validator("ma_mat_bang", "mo_ta")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class DuyetSuCoBaoTriRequest(BaseModel):
    ket_qua: str = Field(..., max_length=20)
    ly_do_tu_choi: Optional[str] = Field(default=None, max_length=4000)

    @field_validator("ket_qua")
    @classmethod
    def validate_result(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"DUYET", "TU_CHOI"}:
            raise ValueError("Kết quả chỉ được là DUYET hoặc TU_CHOI.")
        return normalized

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "DuyetSuCoBaoTriRequest":
        if self.ket_qua == "TU_CHOI" and not ensure_not_blank(self.ly_do_tu_choi):
            raise ValueError("Lý do từ chối là bắt buộc khi từ chối sự cố.")
        return self


class PhanCongSuCoBaoTriRequest(BaseModel):
    ma_nhan_vien_phan_cong: str = Field(..., max_length=20)
    ma_nhan_vien_xu_ly: str = Field(..., max_length=20)
    ghi_chu: Optional[str] = Field(default=None, max_length=500)

    @field_validator("ma_nhan_vien_phan_cong", "ma_nhan_vien_xu_ly")
    @classmethod
    def validate_staff_codes(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Mã nhân viên không được để trống.")
        return value


class CapNhatKetQuaXuLySuCoRequest(BaseModel):
    ket_qua: str = Field(..., min_length=1, max_length=4000)
    ngay_hoan_thanh: datetime

    @field_validator("ket_qua")
    @classmethod
    def validate_result_content(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Kết quả xử lý không được để trống.")
        return value


class NhapChiPhiBaoTriRequest(BaseModel):
    chi_phi: Decimal = Field(..., ge=0)


class SuCoBaoTriResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_su_co: str
    ma_mat_bang: str
    ma_khach_thue: str
    ma_nhan_vien_duyet: Optional[str] = None
    ma_nhan_vien_phan_cong: Optional[str] = None
    ma_nhan_vien_xu_ly: Optional[str] = None
    ngay_gui: datetime
    mo_ta: str
    trang_thai: SuCoBaoTriStatus
    ly_do_tu_choi: Optional[str] = None
    ngay_duyet: Optional[datetime] = None
    ngay_phan_cong: Optional[datetime] = None
    ngay_hoan_thanh: Optional[datetime] = None
    ket_qua: Optional[str] = None
    chi_phi: Optional[Decimal] = None


class SuCoBaoTriFilter(BaseModel):
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    ma_khach_thue: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[str] = None
    ma_nhan_vien_xu_ly: Optional[str] = Field(default=None, max_length=20)
    keyword: Optional[str] = None
    tu_ngay: Optional[datetime] = None
    den_ngay: Optional[datetime] = None
    sort_by: Optional[str] = None
    order: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
