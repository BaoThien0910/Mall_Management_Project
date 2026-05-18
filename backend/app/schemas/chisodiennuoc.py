# File: app/schemas/chisodiennuoc.py
"""
Pydantic v2 schemas cho module Nhập chỉ số điện nước.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


# ── Create ────────────────────────────────────────────────────────────────────

class ChiSoDienNuocCreate(BaseModel):
    mamb: str = Field(..., min_length=1, max_length=20)
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2000)
    chi_so_dien_dau_ky: float = Field(..., ge=0)
    chi_so_dien_cuoi_ky: float = Field(..., ge=0)
    chi_so_nuoc_dau_ky: float = Field(..., ge=0)
    chi_so_nuoc_cuoi_ky: float = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_chi_so(self) -> ChiSoDienNuocCreate:
        if self.chi_so_dien_cuoi_ky < self.chi_so_dien_dau_ky:
            raise ValueError(
                "Chỉ số điện cuối kỳ phải >= đầu kỳ"
            )
        if self.chi_so_nuoc_cuoi_ky < self.chi_so_nuoc_dau_ky:
            raise ValueError(
                "Chỉ số nước cuối kỳ phải >= đầu kỳ"
            )
        return self


# ── Response ──────────────────────────────────────────────────────────────────

class ChiSoDienNuocResponse(BaseModel):
    machs: str
    mamb: str
    thang: int
    nam: int
    chi_so_dien_dau_ky: float
    chi_so_dien_cuoi_ky: float
    chi_so_nuoc_dau_ky: float
    chi_so_nuoc_cuoi_ky: float
    dien_tieu_thu: float
    nuoc_tieu_thu: float
    manv_nhap: Optional[str]
    thoi_gian_nhap: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Filter ────────────────────────────────────────────────────────────────────

class ChiSoFilter(BaseModel):
    mamb: Optional[str] = None
    thang: Optional[int] = Field(None, ge=1, le=12)
    nam: Optional[int] = Field(None, ge=2000)
    manv_nhap: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
