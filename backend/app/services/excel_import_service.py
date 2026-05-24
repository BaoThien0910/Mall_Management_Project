# File: app/services/excel_import_service.py
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from openpyxl import load_workbook
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.constants.billing import (
    IMPORT_ALLOWED_FINANCIAL_TYPES,
    IMPORT_FORBIDDEN_METER_TYPES,
)
from app.exceptions.business_exceptions import BadRequestException
from app.models.dulieu_import_taichinh import DuLieuImportTaiChinh
from app.models.hopdong import HopDong
from app.services._common import generate_code, get_column, get_value

EXPECTED_HEADERS = ["MAHD", "THANG", "NAM", "LOAIKHOAN", "SOTIEN", "GHICHU"]


def _current_employee_id(current_user: Any) -> str:
    ma_nv = get_value(current_user, ["ma_nv", "ma_nhan_vien", "manv"])
    if not ma_nv:
        raise BadRequestException("Tài khoản hiện tại không gắn với nhân viên")
    return ma_nv


def _normalize_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError("Số tiền không hợp lệ")


def _validate_headers(headers: List[str]) -> None:
    normalized_headers = [_normalize_text(header).upper() for header in headers]
    if normalized_headers[: len(EXPECTED_HEADERS)] != EXPECTED_HEADERS:
        raise BadRequestException(
            "File Excel không đúng cấu trúc. Header bắt buộc: "
            "MAHD, THANG, NAM, LOAIKHOAN, SOTIEN, GHICHU"
        )


def _build_import_row(
    ma_hd: str,
    thang: int,
    nam: int,
    loai_khoan: str,
    so_tien: Decimal,
    ghi_chu: Optional[str],
    ma_nhan_vien_import: str,
    ten_file: Optional[str],
    dong_excel: int,
    trang_thai: str,
    loi_chi_tiet: Optional[str],
) -> DuLieuImportTaiChinh:
    return DuLieuImportTaiChinh(
        ma_import=generate_code("IMP"),
        ma_hop_dong=ma_hd,
        thang=thang,
        nam=nam,
        loai_khoan=loai_khoan,
        so_tien=so_tien,
        ghi_chu=ghi_chu,
        ma_nhan_vien_import=ma_nhan_vien_import,
        ten_file=ten_file,
        dong_excel=dong_excel,
        trang_thai=trang_thai,
        loi_chi_tiet=loi_chi_tiet,
    )


def import_financial_excel(
    db: Session,
    file: UploadFile,
    current_user: Any,
) -> Dict[str, Any]:
    """Import dữ liệu tài chính từ Excel.

    Excel chỉ nhận: Tiền thuê, Phí bảo trì, Hoàn trả.
    Tiền điện/nước được tính từ CHISODIENNUOC, không nhập qua Excel.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise BadRequestException("Chỉ hỗ trợ file Excel định dạng .xlsx")

    ma_nhan_vien_import = _current_employee_id(current_user)

    try:
        file.file.seek(0)
        workbook = load_workbook(file.file, data_only=True)
    except Exception:
        raise BadRequestException("Không đọc được file Excel")

    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise BadRequestException("File Excel không có dữ liệu")

    headers = list(rows[0])
    _validate_headers(headers)

    hopdong_id_col = get_column(HopDong, ["ma_hop_dong", "ma_hd"])

    total_rows = 0
    valid_rows = 0
    invalid_rows = 0
    error_details: List[Dict[str, Any]] = []
    import_items: List[DuLieuImportTaiChinh] = []

    for excel_row_number, row in enumerate(rows[1:], start=2):
        if row is None or all(value is None for value in row):
            continue

        total_rows += 1
        values = list(row) + [None] * (len(EXPECTED_HEADERS) - len(row))
        ma_hd = _normalize_text(values[0])
        raw_thang = values[1]
        raw_nam = values[2]
        loai_khoan = _normalize_text(values[3])
        raw_so_tien = values[4]
        ghi_chu = _normalize_text(values[5]) or None

        row_errors: List[str] = []

        if not ma_hd:
            row_errors.append("Thiếu mã hợp đồng")

        try:
            thang = int(raw_thang)
        except (TypeError, ValueError):
            thang = 0
            row_errors.append("Tháng không hợp lệ")

        try:
            nam = int(raw_nam)
        except (TypeError, ValueError):
            nam = 0
            row_errors.append("Năm không hợp lệ")

        if thang < 1 or thang > 12:
            row_errors.append("Tháng phải nằm trong khoảng 1 đến 12")
        if nam < 2000 or nam > 2100:
            row_errors.append("Năm phải nằm trong khoảng 2000 đến 2100")

        try:
            so_tien = _to_decimal(raw_so_tien)
            if so_tien <= 0:
                row_errors.append("Số tiền phải lớn hơn 0")
        except ValueError as exc:
            so_tien = Decimal("0")
            row_errors.append(str(exc))

        if loai_khoan in IMPORT_FORBIDDEN_METER_TYPES:
            row_errors.append(
                "Tiền điện và tiền nước được tính từ chức năng chỉ số điện nước, không nhập qua Excel"
            )
        elif loai_khoan not in IMPORT_ALLOWED_FINANCIAL_TYPES:
            row_errors.append(
                "Loại khoản không hợp lệ. Chỉ cho phép: Tiền thuê, Phí bảo trì, Hoàn trả"
            )

        hop_dong = None
        if ma_hd:
            hop_dong = db.execute(
                select(HopDong).where(hopdong_id_col == ma_hd)
            ).scalars().first()
            if hop_dong is None:
                row_errors.append("Mã hợp đồng không tồn tại")

        if row_errors:
            invalid_rows += 1
            error_details.append(
                {
                    "dong_excel": excel_row_number,
                    "ma_hop_dong": ma_hd,
                    "loi": "; ".join(row_errors),
                }
            )
            # Chỉ lưu dòng lỗi nếu vẫn đủ FK hợp lệ để không vi phạm database.
            if hop_dong is not None and thang and nam and loai_khoan and so_tien > 0:
                import_items.append(
                    _build_import_row(
                        ma_hd=ma_hd,
                        thang=thang,
                        nam=nam,
                        loai_khoan=loai_khoan,
                        so_tien=so_tien,
                        ghi_chu=ghi_chu,
                        ma_nhan_vien_import=ma_nhan_vien_import,
                        ten_file=filename,
                        dong_excel=excel_row_number,
                        trang_thai="Lỗi",
                        loi_chi_tiet="; ".join(row_errors)[:255],
                    )
                )
            continue

        valid_rows += 1
        import_items.append(
            _build_import_row(
                ma_hd=ma_hd,
                thang=thang,
                nam=nam,
                loai_khoan=loai_khoan,
                so_tien=so_tien,
                ghi_chu=ghi_chu,
                ma_nhan_vien_import=ma_nhan_vien_import,
                ten_file=filename,
                dong_excel=excel_row_number,
                trang_thai="Hợp lệ",
                loi_chi_tiet=None,
            )
        )

    try:
        db.add_all(import_items)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "ten_file": filename,
        "tong_so_dong": total_rows,
        "so_dong_hop_le": valid_rows,
        "so_dong_loi": invalid_rows,
        "chi_tiet_loi": error_details,
    }


def _serialize_import_item(item: DuLieuImportTaiChinh) -> Dict[str, Any]:
    return {
        "ma_import": get_value(item, ["ma_import"], ""),
        "ma_hop_dong": get_value(item, ["ma_hop_dong", "ma_hd"], ""),
        "thang": item.thang,
        "nam": item.nam,
        "loai_khoan": get_value(item, ["loai_khoan"], ""),
        "so_tien": get_value(item, ["so_tien"], Decimal("0")),
        "ghi_chu": get_value(item, ["ghi_chu"], None),
        "ten_file": get_value(item, ["ten_file"], None),
        "dong_excel": get_value(item, ["dong_excel"], None),
        "trang_thai": get_value(item, ["trang_thai"], ""),
        "loi_chi_tiet": get_value(item, ["loi_chi_tiet"], None),
        "thoi_gian_import": get_value(item, ["thoi_gian_import"], None),
    }


def list_import_history(
    db: Session,
    filters: Optional[Any] = None,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    stmt = select(DuLieuImportTaiChinh)

    ma_hop_dong = get_value(filters, ["ma_hop_dong", "ma_hd"], None) if filters else None
    thang = get_value(filters, ["thang"], None) if filters else None
    nam = get_value(filters, ["nam"], None) if filters else None
    trang_thai = get_value(filters, ["trang_thai"], None) if filters else None
    page = get_value(filters, ["page"], 1) if filters else 1
    page_size = get_value(filters, ["page_size"], 10) if filters else 10

    if ma_hop_dong:
        stmt = stmt.where(get_column(DuLieuImportTaiChinh, ["ma_hop_dong", "ma_hd"]) == ma_hop_dong)
    if thang:
        stmt = stmt.where(DuLieuImportTaiChinh.thang == thang)
    if nam:
        stmt = stmt.where(DuLieuImportTaiChinh.nam == nam)
    if trang_thai:
        stmt = stmt.where(DuLieuImportTaiChinh.trang_thai == trang_thai)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    items = db.execute(
        stmt.order_by(DuLieuImportTaiChinh.thoi_gian_import.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return {
        "items": [_serialize_import_item(item) for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total else 0,
        },
    }
