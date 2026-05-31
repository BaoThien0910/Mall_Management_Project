# File: app/schemas/yc_thuethem.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants.statuses import YeuCauThueThemStatus
from app.utils.validators import ensure_not_blank


class YeuCauThueThemCreate(BaseModel):
    ma_mat_bang: str = Field(..., max_length=20)
    ly_do: str = Field(..., max_length=2000)

    @field_validator("ma_mat_bang", "ly_do")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not ensure_not_blank(value):
            raise ValueError("Giá trị không được để trống.")
        return value


class DuyetYeuCauThueThemRequest(BaseModel):
    ket_qua: str = Field(..., max_length=20)
    ly_do_tu_choi: Optional[str] = Field(default=None, max_length=2000)
    ghi_chu_cho_kdtc: Optional[str] = Field(default=None, max_length=255)

    @field_validator("ket_qua")
    @classmethod
    def validate_result(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"DUYET", "TU_CHOI"}:
            raise ValueError("Kết quả chỉ được là DUYET hoặc TU_CHOI.")
        return normalized

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "DuyetYeuCauThueThemRequest":
        if self.ket_qua == "TU_CHOI" and not ensure_not_blank(self.ly_do_tu_choi):
            raise ValueError("Lý do từ chối là bắt buộc khi từ chối yêu cầu.")
        return self


class YeuCauThueThemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_yeu_cau: str
    ma_khach_thue: str
    ma_mat_bang: str
    ma_nhan_vien_duyet: Optional[str] = None
    ngay_gui: datetime
    ly_do: str
    trang_thai: YeuCauThueThemStatus
    ngay_duyet: Optional[datetime] = None
    ly_do_tu_choi: Optional[str] = None
    ghi_chu: Optional[str] = None


class YeuCauThueThemFilter(BaseModel):
    ma_khach_thue: Optional[str] = Field(default=None, max_length=20)
    ma_mat_bang: Optional[str] = Field(default=None, max_length=20)
    trang_thai: Optional[str] = None
    keyword: Optional[str] = Field(default=None, max_length=100)
    ngay_gui_tu: Optional[str] = Field(default=None)
    ngay_gui_den: Optional[str] = Field(default=None)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
