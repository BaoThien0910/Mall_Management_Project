# File: app/services/excel_import_service.py
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from openpyxl import load_workbook
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction, DuLieuImportTaiChinhStatus, LoaiKhoanTaiChinh
from app.exceptions.business_exceptions import BadRequestException
from app.models import DuLieuImportTaiChinh, HopDong
from app.schemas.dulieu_import_taichinh import DuLieuImportTaiChinhFilter
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.pagination import calculate_offset, calculate_total_pages, normalize_pagination
from app.utils.transaction import transaction_context
from app.utils.validators import validate_month, validate_year


_REQUIRED_HEADERS = ["MAHD", "THANG", "NAM", "LOAIKHOAN", "SOTIEN", "GHICHU"]
_ALLOWED_FINANCIAL_TYPES = {item.value for item in LoaiKhoanTaiChinh}


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def _to_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_decimal(value: Any) -> Optional[Decimal]:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result


def import_financial_excel(
    db: Session,
    file: Any,
    current_user: Any,
) -> Dict[str, Any]:
    """Đọc file Excel tài chính, lưu các dòng hợp lệ và trả kết quả import."""
    filename = getattr(file, "filename", None) or ""
    if not filename.lower().endswith(".xlsx"):
        raise BadRequestException("Chỉ chấp nhận file Excel định dạng .xlsx")

    try:
        file.file.seek(0)
        workbook = load_workbook(file.file, data_only=True)
        worksheet = workbook.worksheets[0]
    except Exception as exc:
        raise BadRequestException("Không thể đọc file Excel") from exc

    rows = list(worksheet.iter_rows(values_only=True))
    if not rows:
        raise BadRequestException("File Excel không có dữ liệu")

    headers = [str(value).strip() if value is not None else "" for value in rows[0]]
    if headers[: len(_REQUIRED_HEADERS)] != _REQUIRED_HEADERS:
        raise BadRequestException(
            "File Excel phải có đúng các cột: " + ", ".join(_REQUIRED_HEADERS)
        )

    valid_records: List[DuLieuImportTaiChinh] = []
    errors: List[Dict[str, Any]] = []
    ma_nhan_vien_import = _user_attr(current_user, "ma_nv", "ma_nhan_vien")
    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    if not ma_nhan_vien_import:
        raise BadRequestException("Không xác định được nhân viên import")

    for excel_row_number, raw_row in enumerate(rows[1:], start=2):
        values = list(raw_row) + [None] * max(0, len(_REQUIRED_HEADERS) - len(raw_row))
        ma_hop_dong = str(values[0]).strip() if values[0] is not None else ""
        thang = _to_int(values[1])
        nam = _to_int(values[2])
        loai_khoan = str(values[3]).strip() if values[3] is not None else ""
        so_tien = _to_decimal(values[4])
        ghi_chu = str(values[5]).strip() if values[5] is not None else None
        row_errors: List[str] = []

        if not ma_hop_dong:
            row_errors.append("MAHD không được để trống")
        elif db.execute(
            select(HopDong).where(HopDong.ma_hop_dong == ma_hop_dong)
        ).scalars().first() is None:
            row_errors.append("Hợp đồng không tồn tại")

        if thang is None or not validate_month(thang):
            row_errors.append("THANG không hợp lệ")
        if nam is None or not validate_year(nam):
            row_errors.append("NAM không hợp lệ")
        if loai_khoan not in _ALLOWED_FINANCIAL_TYPES:
            row_errors.append("LOAIKHOAN không hợp lệ")
        if so_tien is None or so_tien <= 0:
            row_errors.append("SOTIEN phải lớn hơn 0")

        if row_errors:
            errors.append(
                {
                    "dong_excel": excel_row_number,
                    "noi_dung_loi": "; ".join(row_errors),
                }
            )
            continue

        valid_records.append(
            DuLieuImportTaiChinh(
                ma_import=_generate_code("IMP"),
                ma_hop_dong=ma_hop_dong,
                thang=thang,
                nam=nam,
                loai_khoan=loai_khoan,
                so_tien=so_tien,
                ghi_chu=ghi_chu,
                ma_nhan_vien_import=ma_nhan_vien_import,
                thoi_gian_import=current_datetime(),
                ten_file=filename,
                dong_excel=excel_row_number,
                trang_thai=DuLieuImportTaiChinhStatus.HOP_LE.value,
                loi_chi_tiet=None,
            )
        )

    with transaction_context(db):
        for record in valid_records:
            db.add(record)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="DULIEU_IMPORT_TAICHINH",
            ma_doi_tuong=None,
            chi_tiet=f"Import tài chính từ file {filename}",
        )

    return {
        "ten_file": filename,
        "tong_so_dong": max(len(rows) - 1, 0),
        "so_dong_hop_le": len(valid_records),
        "so_dong_loi": len(errors),
        "danh_sach_loi": errors,
    }


def list_import_history(
    db: Session,
    filters: DuLieuImportTaiChinhFilter,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Liệt kê lịch sử import tài chính."""
    page, page_size = normalize_pagination(filters.page, filters.page_size)
    conditions: List[Any] = []
    if filters.ma_hop_dong:
        conditions.append(DuLieuImportTaiChinh.ma_hop_dong == filters.ma_hop_dong)
    if filters.thang is not None:
        conditions.append(DuLieuImportTaiChinh.thang == filters.thang)
    if filters.nam is not None:
        conditions.append(DuLieuImportTaiChinh.nam == filters.nam)
    if filters.trang_thai:
        conditions.append(DuLieuImportTaiChinh.trang_thai == _enum_value(filters.trang_thai))

    stmt = select(DuLieuImportTaiChinh)
    count_stmt = select(func.count()).select_from(DuLieuImportTaiChinh)
    if conditions:
        clause = and_(*conditions)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = db.execute(count_stmt).scalar_one()
    items = db.execute(
        stmt.order_by(DuLieuImportTaiChinh.thoi_gian_import.desc())
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
