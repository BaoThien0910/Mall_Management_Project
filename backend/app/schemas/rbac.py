# File: app/schemas/rbac.py
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VaiTroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_vai_tro: str
    ten_vai_tro: str
    mo_ta: Optional[str] = None
    trang_thai: str


class QuyenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_quyen: str
    ten_quyen: str
    module: str
    hanh_dong: str
    mo_ta: Optional[str] = None


class VaiTroQuyenAssignRequest(BaseModel):
    danh_sach_ma_quyen: List[str] = Field(..., min_length=1)

    @field_validator("danh_sach_ma_quyen")
    @classmethod
    def validate_permission_codes(cls, values: List[str]) -> List[str]:
        normalized = [value.strip() for value in values]

        if any(not value for value in normalized):
            raise ValueError("Mã quyền không được để trống.")

        if len(set(normalized)) != len(normalized):
            raise ValueError("Danh sách quyền không được chứa phần tử trùng lặp.")

        return normalized


class VaiTroQuyenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma_vai_tro: str
    danh_sach_quyen: List[QuyenResponse]
