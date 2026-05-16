from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.models.congno import CongNo


class DebtSummaryOut(BaseModel):
    id: str
    tenant: str
    premise: str
    period: str
    dueDate: date
    totalAmount: int
    paidAmount: int
    status: str

    @classmethod
    def from_congno(cls, c: CongNo) -> "DebtSummaryOut":
        return cls(
            id=c.ma_congno,
            tenant=c.ten_khach_thue,
            premise=c.ma_matbang,
            period=c.ky_thanh_toan,
            dueDate=c.ngay_den_han,
            totalAmount=c.tong_phat_sinh,
            paidAmount=c.da_thanh_toan,
            status=c.trang_thai,
        )


class DebtDetailOut(BaseModel):
    id: str
    tenant: str
    premise: str
    period: str
    dueDate: date
    status: str
    lines: list[dict[str, Any]]
    totalAmount: int
    paidAmount: int
    note: str | None = None

    @classmethod
    def from_congno(cls, c: CongNo) -> "DebtDetailOut":
        return cls(
            id=c.ma_congno,
            tenant=c.ten_khach_thue,
            premise=c.ma_matbang,
            period=c.ky_thanh_toan,
            dueDate=c.ngay_den_han,
            status=c.trang_thai,
            lines=c.chi_tiet_dong_list(),
            totalAmount=c.tong_phat_sinh,
            paidAmount=c.da_thanh_toan,
            note=c.ghi_chu,
        )


class DebtCalculateOut(BaseModel):
    success: bool = True
    message: str = "Đã tính toán công nợ"


class DebtListEnvelope(BaseModel):
    items: list[DebtSummaryOut]
    total: int
    skip: int
    limit: int
