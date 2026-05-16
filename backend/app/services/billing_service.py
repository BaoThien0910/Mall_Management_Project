"""Truy vấn công nợ."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.dependencies import Principal
from app.models.congno import CongNo
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
    q = db.query(CongNo)

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien
        if not code:
            return DebtListEnvelope(items=[], total=0, skip=skip, limit=limit)
        q = q.filter(CongNo.ma_khach == code)

    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                CongNo.ma_congno.ilike(s),
                CongNo.ten_khach_thue.ilike(s),
                CongNo.ma_matbang.ilike(s),
            )
        )

    if status_filter:
        q = q.filter(CongNo.trang_thai == status_filter)

    total = q.count()
    rows = (
        q.order_by(CongNo.ngay_den_han.desc()).offset(skip).limit(min(limit, 500)).all()
    )

    items = [DebtSummaryOut.from_congno(r) for r in rows]

    return DebtListEnvelope(items=items, total=total, skip=skip, limit=limit)


def get_debt_detail(db: Session, ma: str, principal: Principal) -> DebtDetailOut | None:
    row = db.get(CongNo, ma)
    if not row:
        return None

    if principal.role == "tenant":
        code = principal.ma_khach_dai_dien or ""
        if row.ma_khach != code:
            return None

    return DebtDetailOut.from_congno(row)


def simulate_calculate_cycle(db: Session) -> dict:
    """stub tính công nợ — sau nối nghiệp vụ thực."""

    _ = db
    return {"success": True, "message": "Đã xếp kỳ tính công nợ (mô phỏng)."}
