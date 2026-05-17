"""Truy vấn công nợ."""

from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.dependencies import Principal
from app.models.congno import CongNo
from app.models.hopdong import HopDong
from app.schemas.congno import DebtDetailOut, DebtListEnvelope, DebtSummaryOut

def list_debts(
    db: Session,
    principal: Principal,
    *,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    status_filter: str | None = None,
) -> DebtListEnvelope:
    q = db.query(CongNo, HopDong).join(HopDong, CongNo.ma_hd == HopDong.ma_hd)

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien
        if not code:
            return DebtListEnvelope(items=[], total=0, skip=skip, limit=limit)
        q = q.filter(HopDong.ma_khach == code)

    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                CongNo.ma_congno.ilike(s),  # Đã sửa thành ma_congno
                HopDong.ma_matbang.ilike(s),
            )
        )

    if status_filter:
        q = q.filter(CongNo.trang_thai == status_filter)

    total = q.count()
    # Đã sửa thành han_thanh_toan
    rows = q.order_by(CongNo.han_thanh_toan.desc()).offset(skip).limit(min(limit, 500)).all()

    items = [DebtSummaryOut.from_congno(cn, tenant_name=hd.ma_khach, premise_code=hd.ma_matbang) for cn, hd in rows]

    return DebtListEnvelope(items=items, total=total, skip=skip, limit=limit)


def get_debt_detail(db: Session, ma: str, principal: Principal) -> DebtDetailOut | None:
    # Đã sửa thành ma_congno
    result = db.query(CongNo, HopDong).join(HopDong, CongNo.ma_hd == HopDong.ma_hd).filter(CongNo.ma_congno == ma).first()
    if not result:
        return None
    
    cn, hd = result

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien or ""
        if hd.ma_khach != code:
            return None

    return DebtDetailOut.from_congno(cn, tenant_name=hd.ma_khach, premise_code=hd.ma_matbang)


def simulate_calculate_cycle(db: Session) -> dict:
    return {"success": True, "message": "Đã xếp kỳ tính công nợ (mô phỏng)."}