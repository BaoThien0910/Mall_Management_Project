from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class PaymentBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    debtId: str
    amount: int = Field(gt=0)
    method: str


class PaymentResult(BaseModel):
    success: bool
    transactionId: str | None = None
    paidAt: datetime | None = None
    detail: str | None = None

    model_config = {"populate_by_name": True}


class InvoiceRow(BaseModel):
    invoiceNo: str
    debtId: str
    tenant: str | None = None
    period: str | None = None
    amount: float
    paidAt: datetime
    method: str

    @classmethod
    def from_hoadon(cls, h, tenant_name: str = "", period_str: str = "") -> "InvoiceRow":
        return cls(
            invoiceNo=h.ma_hd,       # Đã sửa thành ma_hd
            debtId=h.ma_congno,      # Đã sửa thành ma_congno
            tenant=tenant_name,
            period=period_str,
            amount=float(h.so_tien),
            paidAt=h.ngay_tt,        # Đã sửa thành ngay_tt
            method=h.phuong_thuc
        )


class InvoiceListEnvelope(BaseModel):
    items: list[InvoiceRow]
    total: int


def new_txn_id() -> str:
    return f"TXN-{uuid4().hex[:12].upper()}"
