# File: app/services/financial_report_service.py
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction, BaoCaoTaiChinhStatus, HoaDonStatus, LoaiBaoCaoTaiChinh
from app.exceptions.business_exceptions import InvalidStateException, NotFoundException, BadRequestException
from app.models import BaoCaoTaiChinh, CongNo, HoaDon
from app.schemas.baocaotaichinh import BaoCaoTaiChinhCreate, BaoCaoTaiChinhFilter
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import transaction_context


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def create_debt_report(
    db: Session,
    payload: BaoCaoTaiChinhCreate,
    current_user: Any,
) -> BaoCaoTaiChinh:
    """Lập báo cáo công nợ theo tháng/năm."""
    ma_nhan_vien_lap = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_lap:
        raise BadRequestException("Không xác định được nhân viên lập báo cáo")

    total_amount = db.execute(
        select(func.coalesce(func.sum(CongNo.tong_tien), 0)).where(
            CongNo.thang == payload.thang,
            CongNo.nam == payload.nam,
        )
    ).scalar_one()
    report = BaoCaoTaiChinh(
        ma_bao_cao_tai_chinh=_generate_code("BCTC"),
        loai_bao_cao=LoaiBaoCaoTaiChinh.BAO_CAO_CONG_NO.value,
        thang=payload.thang,
        nam=payload.nam,
        ma_nhan_vien_lap=ma_nhan_vien_lap,
        ngay_lap=current_datetime(),
        noi_dung=payload.noi_dung,
        tong_tien=total_amount if total_amount is not None else Decimal("0"),
        trang_thai=BaoCaoTaiChinhStatus.BAN_NHAP.value,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(report)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="BAOCAOTAICHINH",
            ma_doi_tuong=report.ma_bao_cao_tai_chinh,
            chi_tiet="Lập báo cáo công nợ",
        )
    return report


def create_revenue_report(
    db: Session,
    payload: BaoCaoTaiChinhCreate,
    current_user: Any,
) -> BaoCaoTaiChinh:
    """Lập báo cáo doanh số từ hóa đơn thanh toán thành công."""
    ma_nhan_vien_lap = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    if not ma_nhan_vien_lap:
        raise BadRequestException("Không xác định được nhân viên lập báo cáo")

    total_amount = db.execute(
        select(func.coalesce(func.sum(HoaDon.so_tien), 0)).where(
            HoaDon.trang_thai == HoaDonStatus.THANH_CONG.value,
            func.month(HoaDon.thoi_gian_giao_dich) == payload.thang,
            func.year(HoaDon.thoi_gian_giao_dich) == payload.nam,
        )
    ).scalar_one()
    report = BaoCaoTaiChinh(
        ma_bao_cao_tai_chinh=_generate_code("BCTC"),
        loai_bao_cao=LoaiBaoCaoTaiChinh.BAO_CAO_DOANH_SO.value,
        thang=payload.thang,
        nam=payload.nam,
        ma_nhan_vien_lap=ma_nhan_vien_lap,
        ngay_lap=current_datetime(),
        noi_dung=payload.noi_dung,
        tong_tien=total_amount if total_amount is not None else Decimal("0"),
        trang_thai=BaoCaoTaiChinhStatus.BAN_NHAP.value,
    )
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(report)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="BAOCAOTAICHINH",
            ma_doi_tuong=report.ma_bao_cao_tai_chinh,
            chi_tiet="Lập báo cáo doanh số",
        )
    return report


def list_financial_reports(
    db: Session,
    filters: BaoCaoTaiChinhFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê báo cáo tài chính."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.loai_bao_cao:
        conditions.append(BaoCaoTaiChinh.loai_bao_cao == _enum_value(filters.loai_bao_cao))
    if filters.thang is not None:
        conditions.append(BaoCaoTaiChinh.thang == filters.thang)
    if filters.nam is not None:
        conditions.append(BaoCaoTaiChinh.nam == filters.nam)
    if filters.trang_thai:
        conditions.append(BaoCaoTaiChinh.trang_thai == _enum_value(filters.trang_thai))

    stmt = select(BaoCaoTaiChinh)
    count_stmt = select(func.count()).select_from(BaoCaoTaiChinh)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(BaoCaoTaiChinh.ngay_lap.desc())
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    ).scalars().all()
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": calculate_total_pages(total, page_size),
        },
    }


def get_financial_report_detail(
    db: Session,
    ma_bctc: str,
    current_user: Optional[Any] = None,
) -> BaoCaoTaiChinh:
    """Lấy chi tiết báo cáo tài chính."""
    report = db.execute(
        select(BaoCaoTaiChinh).where(BaoCaoTaiChinh.ma_bao_cao_tai_chinh == ma_bctc)
    ).scalars().first()
    if report is None:
        raise NotFoundException("Không tìm thấy báo cáo tài chính")
    return report


def publish_financial_report(
    db: Session,
    ma_bctc: str,
    current_user: Any,
) -> BaoCaoTaiChinh:
    """Ban hành báo cáo tài chính đang ở trạng thái bản nháp."""
    report = db.execute(
        select(BaoCaoTaiChinh).where(BaoCaoTaiChinh.ma_bao_cao_tai_chinh == ma_bctc)
    ).scalars().first()
    if report is None:
        raise NotFoundException("Không tìm thấy báo cáo tài chính")
    if report.trang_thai != BaoCaoTaiChinhStatus.BAN_NHAP.value:
        raise InvalidStateException("Chỉ báo cáo bản nháp mới được ban hành")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        report.trang_thai = BaoCaoTaiChinhStatus.DA_BAN_HANH.value
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="BAOCAOTAICHINH",
            ma_doi_tuong=report.ma_bao_cao_tai_chinh,
            chi_tiet="Ban hành báo cáo tài chính",
        )
    return report
