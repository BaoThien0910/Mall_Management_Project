# File: app/services/billing_service.py
import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Any, DefaultDict, Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction, CongNoStatus, DuLieuImportTaiChinhStatus, LoaiKhoanTaiChinh
from app.exceptions.business_exceptions import BadRequestException, ForbiddenException
from app.models import CongNo, DuLieuImportTaiChinh, HopDong
from app.schemas.congno import CongNoCuaToiFilter, CongNoFilter, TinhCongNoThangRequest
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


def calculate_monthly_debts(
    db: Session,
    payload: TinhCongNoThangRequest,
    current_user: Any,
) -> Dict[str, Any]:
    """Tính công nợ tháng từ dữ liệu import tài chính hợp lệ."""
    import_rows = db.execute(
        select(DuLieuImportTaiChinh).where(
            DuLieuImportTaiChinh.thang == payload.thang,
            DuLieuImportTaiChinh.nam == payload.nam,
            DuLieuImportTaiChinh.trang_thai == DuLieuImportTaiChinhStatus.HOP_LE.value,
        )
    ).scalars().all()

    grouped: DefaultDict[str, List[DuLieuImportTaiChinh]] = defaultdict(list)
    for row in import_rows:
        grouped[row.ma_hop_dong].append(row)

    created_codes: List[str] = []
    skipped_contracts: List[str] = []
    debts_to_add: List[CongNo] = []
    rows_to_mark_used: List[DuLieuImportTaiChinh] = []

    for ma_hop_dong, rows in grouped.items():
        existing_debt = db.execute(
            select(CongNo).where(
                CongNo.ma_hop_dong == ma_hop_dong,
                CongNo.thang == payload.thang,
                CongNo.nam == payload.nam,
            )
        ).scalars().first()
        if existing_debt is not None:
            skipped_contracts.append(ma_hop_dong)
            continue

        totals: Dict[str, Decimal] = {
            LoaiKhoanTaiChinh.TIEN_THUE.value: Decimal("0"),
            LoaiKhoanTaiChinh.TIEN_DIEN.value: Decimal("0"),
            LoaiKhoanTaiChinh.TIEN_NUOC.value: Decimal("0"),
            LoaiKhoanTaiChinh.PHI_BAO_TRI.value: Decimal("0"),
            LoaiKhoanTaiChinh.HOAN_TRA.value: Decimal("0"),
        }
        for row in rows:
            totals[row.loai_khoan] += row.so_tien

        total_amount = (
            totals[LoaiKhoanTaiChinh.TIEN_THUE.value]
            + totals[LoaiKhoanTaiChinh.TIEN_DIEN.value]
            + totals[LoaiKhoanTaiChinh.TIEN_NUOC.value]
            + totals[LoaiKhoanTaiChinh.PHI_BAO_TRI.value]
            - totals[LoaiKhoanTaiChinh.HOAN_TRA.value]
        )
        if total_amount < 0:
            raise BadRequestException(
                f"Tổng tiền công nợ của hợp đồng {ma_hop_dong} bị âm"
            )

        debt = CongNo(
            ma_cong_no=_generate_code("CN"),
            ma_hop_dong=ma_hop_dong,
            thang=payload.thang,
            nam=payload.nam,
            tien_thue=totals[LoaiKhoanTaiChinh.TIEN_THUE.value],
            tien_dien=totals[LoaiKhoanTaiChinh.TIEN_DIEN.value],
            tien_nuoc=totals[LoaiKhoanTaiChinh.TIEN_NUOC.value],
            phi_bao_tri=totals[LoaiKhoanTaiChinh.PHI_BAO_TRI.value],
            tien_hoan=totals[LoaiKhoanTaiChinh.HOAN_TRA.value],
            tong_tien=total_amount,
            han_thanh_toan=None,
            trang_thai=CongNoStatus.CHUA_THANH_TOAN.value,
            ngay_lap=current_datetime(),
        )
        debts_to_add.append(debt)
        rows_to_mark_used.extend(rows)
        created_codes.append(debt.ma_cong_no)

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        for debt in debts_to_add:
            db.add(debt)
        for row in rows_to_mark_used:
            row.trang_thai = DuLieuImportTaiChinhStatus.DA_DUNG_TINH_CONG_NO.value
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="CONGNO",
            ma_doi_tuong=None,
            chi_tiet="Tính công nợ tháng từ dữ liệu import tài chính",
        )

    return {
        "so_cong_no_da_tao": len(created_codes),
        "so_cong_no_bo_qua": len(skipped_contracts),
        "danh_sach_ma_cn": created_codes,
        "danh_sach_ma_hd_bo_qua": skipped_contracts,
    }


def list_debts(
    db: Session,
    filters: CongNoFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê công nợ toàn hệ thống theo bộ lọc."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_hop_dong:
        conditions.append(CongNo.ma_hop_dong == filters.ma_hop_dong)
    if filters.thang is not None:
        conditions.append(CongNo.thang == filters.thang)
    if filters.nam is not None:
        conditions.append(CongNo.nam == filters.nam)
    if filters.trang_thai:
        conditions.append(CongNo.trang_thai == _enum_value(filters.trang_thai))

    stmt = select(CongNo)
    count_stmt = select(func.count()).select_from(CongNo)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(CongNo.nam.desc(), CongNo.thang.desc(), CongNo.ngay_lap.desc())
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


def list_my_debts(
    db: Session,
    filters: CongNoCuaToiFilter,
    current_user: Any,
) -> Dict[str, Any]:
    """Liệt kê công nợ của khách thuê hiện tại."""
    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")

    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = [HopDong.ma_khach_thue == ma_khach_thue]
    if filters.ma_hop_dong:
        conditions.append(CongNo.ma_hop_dong == filters.ma_hop_dong)
    if filters.thang is not None:
        conditions.append(CongNo.thang == filters.thang)
    if filters.nam is not None:
        conditions.append(CongNo.nam == filters.nam)
    if filters.trang_thai:
        conditions.append(CongNo.trang_thai == _enum_value(filters.trang_thai))

    clause = and_(*conditions)
    count_stmt = (
        select(func.count())
        .select_from(CongNo)
        .join(HopDong, HopDong.ma_hop_dong == CongNo.ma_hop_dong)
        .where(clause)
    )
    stmt = (
        select(CongNo)
        .join(HopDong, HopDong.ma_hop_dong == CongNo.ma_hop_dong)
        .where(clause)
    )
    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(CongNo.nam.desc(), CongNo.thang.desc(), CongNo.ngay_lap.desc())
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
