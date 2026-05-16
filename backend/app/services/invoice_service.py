"""Lịch sử hóa đơn từ bảng HoaDon."""

from sqlalchemy.orm import Session

from app.dependencies import Principal
from app.models.congno import CongNo
from app.models.hoadon import HoaDon
from app.schemas.payment import InvoiceListEnvelope, InvoiceRow


def list_invoices(db: Session, principal: Principal, *, skip: int = 0, limit: int = 100) -> InvoiceListEnvelope:
    q = db.query(HoaDon).join(CongNo, HoaDon.ma_congno == CongNo.ma_congno)

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien
        if not code:
            return InvoiceListEnvelope(items=[], total=0)
        q = q.filter(CongNo.ma_khach == code)

    total = q.count()
    rows = q.order_by(HoaDon.ngay_tt.desc()).offset(skip).limit(min(limit, 500)).all()

    items: list[InvoiceRow] = []
    for h in rows:
        cn = db.query(CongNo).filter(CongNo.ma_congno == h.ma_congno).first()
        items.append(
            InvoiceRow(
                invoiceNo=h.so_hoa_don,
                debtId=h.ma_congno,
                tenant=cn.ten_khach_thue if cn else "",
                period=cn.ky_thanh_toan if cn else "",
                amount=h.so_tien,
                paidAt=h.ngay_tt.date().isoformat(),
                method=h.phuong_thuc,
            )
        )

    return InvoiceListEnvelope(items=items, total=total)
