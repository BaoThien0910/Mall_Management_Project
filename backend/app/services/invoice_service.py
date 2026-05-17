"""Lịch sử hóa đơn từ bảng HoaDon."""

from sqlalchemy.orm import Session
from app.dependencies import Principal
from app.models.congno import CongNo
from app.models.hoadon import HoaDon
from app.schemas.payment import InvoiceListEnvelope, InvoiceRow

def list_invoices(db: Session, principal: Principal, *, skip: int = 0, limit: int = 100) -> InvoiceListEnvelope:
    q = db.query(HoaDon)

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien
        if not code:
            return InvoiceListEnvelope(items=[], total=0)
        q = q.filter(HoaDon.ma_khach == code)

    total = q.count()
    rows = q.order_by(HoaDon.ngay_tt.desc()).offset(skip).limit(min(limit, 500)).all()

    items: list[InvoiceRow] = []
    for h in rows:
        # Đã sửa: CongNo.ma_cn -> CongNo.ma_congno
        cn = db.query(CongNo).filter(CongNo.ma_congno == h.ma_congno).first()
        period_str = f"{cn.thang:02d}/{cn.nam}" if cn else ""
        
        items.append(InvoiceRow.from_hoadon(h, tenant_name=h.ma_khach, period_str=period_str))

    return InvoiceListEnvelope(items=items, total=total)