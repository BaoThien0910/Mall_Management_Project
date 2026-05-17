"""Tài chính: công nợ, thanh toán, hóa đơn, nhập."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import Principal, require_any_permission, require_permissions
from app.schemas.congno import DebtDetailOut
from app.schemas.payment import PaymentBody, PaymentResult
from app.services import billing_service, excel_import_service, invoice_service
from app.services.payment_service import process_payment_simulation
from app.utils.response import success_response  # <-- Thêm import

router = APIRouter()


@router.get("/debts")
async def list_debts(
    principal: Annotated[
        Principal, Depends(require_any_permission("finance.read_all", "finance.read_own"))
    ],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    statusFil: str | None = None,
):
    envelope = billing_service.list_debts(
        db, principal, skip=skip, limit=limit, search=q, status_filter=statusFil
    )
    return success_response(data=envelope.model_dump(mode="json"), message="Lấy danh sách công nợ thành công")


@router.get("/debts/{ma}")
async def debt_detail(
    ma: str,
    principal: Annotated[
        Principal, Depends(require_any_permission("finance.read_all", "finance.read_own"))
    ],
    db: Session = Depends(get_db),
):
    detail = billing_service.get_debt_detail(db, ma, principal)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy.")
    return success_response(data=detail, message="Lấy chi tiết công nợ thành công")


class CalculateBody(BaseModel):
    period: str | None = None


@router.post("/debts/calculate")
async def calculate_cycle(
    _: Annotated[Principal, Depends(require_permissions("finance.calculate"))],
    db: Session = Depends(get_db),
    body: CalculateBody | None = Body(default=None),
):
    _ = body
    result = billing_service.simulate_calculate_cycle(db)
    return success_response(data=result, message="Đã thực hiện tính toán công nợ")


@router.post("/payments")
async def create_payment(
    payload: PaymentBody,
    principal: Annotated[Principal, Depends(require_permissions("finance.pay"))],
    db: Session = Depends(get_db),
):
    result = process_payment_simulation(db, principal, payload)
    payment_data = PaymentResult(
        success=result.success, 
        transactionId=result.transactionId, 
        paidAt=result.paidAt, 
        detail=result.detail
    )
    return success_response(data=payment_data, message="Thực hiện thanh toán thành công")


@router.get("/invoices")
async def list_invoice(
    principal: Annotated[
        Principal, Depends(require_any_permission("finance.read_all", "finance.read_own"))
    ],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    envelope = invoice_service.list_invoices(db, principal, skip=skip, limit=limit)
    data = envelope.model_dump(mode="json")
    # Gắn thêm 'key' cho bảng của Frontend (Ant Design thường dùng 'key')
    data["items"] = [
        {
            **item,
            "key": item.get("invoiceNo", ""),
        }
        for item in data.get("items", [])
    ]
    return success_response(data=data, message="Lấy danh sách hóa đơn thành công")


@router.post("/import")
async def finance_import_excel(
    _: Annotated[Principal, Depends(require_permissions("finance.import"))],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    data = await file.read()
    result = excel_import_service.ingest_financial_upload(db, data, file.filename or "unknown.xlsx")
    return success_response(data=result, message="Nhập dữ liệu Excel thành công")