from datetime import date
from typing import Any
from pydantic import BaseModel
from app.models.congno import CongNo

class DebtSummaryOut(BaseModel):
    id: str
    tenant: str | None = None
    premise: str | None = None
    period: str
    dueDate: date | None
    totalAmount: float
    paidAmount: float
    status: str

    @classmethod
    def from_congno(cls, c: CongNo, tenant_name: str = "", premise_code: str = "") -> "DebtSummaryOut":
        paid_amount = float(c.tong_tien) if c.trang_thai == "Đã thanh toán" else 0.0

        return cls(
            id=c.ma_congno,              # Đã sửa thành ma_congno
            tenant=tenant_name,
            premise=premise_code,
            period=f"{c.thang:02d}/{c.nam}",
            dueDate=c.han_thanh_toan,    # Đã sửa thành han_thanh_toan
            totalAmount=float(c.tong_tien),
            paidAmount=paid_amount,
            status=c.trang_thai,
        )

class DebtDetailOut(BaseModel):
    id: str
    tenant: str | None = None
    premise: str | None = None
    period: str
    dueDate: date | None
    status: str
    lines: list[dict[str, Any]]
    totalAmount: float
    paidAmount: float
    note: str | None = None

    @classmethod
    def from_congno(cls, c: CongNo, tenant_name: str = "", premise_code: str = "") -> "DebtDetailOut":
        lines = []
        if c.tien_thue > 0:
            lines.append({"type": "rent", "description": "Tiền thuê mặt bằng", "amount": float(c.tien_thue)})
        if c.tien_dien > 0:
            lines.append({"type": "utility", "description": "Tiền điện", "amount": float(c.tien_dien)})
        if c.tien_nuoc > 0:
            lines.append({"type": "utility", "description": "Tiền nước", "amount": float(c.tien_nuoc)})
        if c.phi_bao_tri > 0:
            lines.append({"type": "service", "description": "Phí bảo trì", "amount": float(c.phi_bao_tri)})
        if c.tien_hoan > 0:
            lines.append({"type": "refund", "description": "Tiền hoàn", "amount": -float(c.tien_hoan)})

        paid_amount = float(c.tong_tien) if c.trang_thai == "Đã thanh toán" else 0.0

        return cls(
            id=c.ma_congno,              # Đã sửa thành ma_congno
            tenant=tenant_name,
            premise=premise_code,
            period=f"{c.thang:02d}/{c.nam}",
            dueDate=c.han_thanh_toan,    # Đã sửa thành han_thanh_toan
            status=c.trang_thai,
            lines=lines,
            totalAmount=float(c.tong_tien),
            paidAmount=paid_amount,
            note=None,
        )

class DebtCalculateOut(BaseModel):
    success: bool = True
    message: str = "Đã tính toán công nợ"

class DebtListEnvelope(BaseModel):
    items: list[DebtSummaryOut]
    total: int
    skip: int
    limit: int