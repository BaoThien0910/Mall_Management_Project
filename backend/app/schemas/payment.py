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
    tenant: str
    period: str
    amount: int
    paidAt: str
    method: str


class InvoiceListEnvelope(BaseModel):
    items: list[InvoiceRow]
    total: int


def new_txn_id() -> str:
    return f"TXN-{uuid4().hex[:12].upper()}"
