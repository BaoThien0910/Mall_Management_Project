"""Thanh toán mô phỏng trong transaction."""

import random
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.dependencies import Principal, has_permission
from app.models.congno import CongNo
from app.models.hoadon import HoaDon
from app.schemas.payment import PaymentBody, PaymentResult, new_txn_id


def _recompute_status(cn: CongNo) -> None:
    tong = cn.tong_phat_sinh
    da = cn.da_thanh_toan
    remaining = tong - da
    if tong <= 0:
        cn.trang_thai = "unpaid"
        return
    if da >= tong or remaining <= 0:
        cn.trang_thai = "paid"
        return
    if da > 0:
        cn.trang_thai = "partial"
        return

    cn.trang_thai = (
        "overdue" if cn.ngay_den_han and cn.ngay_den_han < datetime.now(UTC).date() else "unpaid"
    )


def process_payment_simulation(db: Session, principal: Principal, body: PaymentBody) -> PaymentResult:
    if not has_permission(principal, "finance.pay"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Không được phép thanh toán.")

    if principal.role != "tenant":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Phiên MVP: chỉ tài khoản khách thuê được gọi thanh toán mô phỏng.",
        )

    settings = get_settings()
    if random.random() < settings.PAYMENT_SIM_FAIL_RATE:
        return PaymentResult(
            success=False,
            transactionId=new_txn_id(),
            detail="Mô phỏng cổng thanh toán: giao dịch bị từ chối.",
        )

    cn = db.get(CongNo, body.debtId)
    if cn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Không thấy công nợ.")

    code = principal.ma_khach_dai_dien or ""
    if cn.ma_khach != code:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Công nợ không thuộc tài khoản của bạn.")

    remaining = cn.tong_phat_sinh - cn.da_thanh_toan
    if remaining <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Công nợ đã thanh toán đủ.")
    if body.amount > remaining:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Số tiền không vượt quá {remaining}.",
        )

    txn = new_txn_id()
    paid_at = datetime.now(UTC)
    invoice_no = f"INV-{paid_at.strftime('%Y%m%d')}-{txn[-6:]}"

    try:
        db.add(
            HoaDon(
                so_hoa_don=invoice_no,
                ma_congno=cn.ma_congno,
                so_tien=body.amount,
                ngay_tt=paid_at,
                phuong_thuc=body.method,
                ma_giao_dich=txn,
            )
        )
        cn.da_thanh_toan += body.amount
        _recompute_status(cn)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không ghi được giao dịch, thử lại sau.",
        ) from None

    return PaymentResult(success=True, transactionId=txn, paidAt=paid_at)
