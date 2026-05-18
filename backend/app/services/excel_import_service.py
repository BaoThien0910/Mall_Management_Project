# File: app/services/excel_import_service.py
"""
Service xử lý Import dữ liệu tài chính từ file Excel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Any, IO

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.dulieu_import_taichinh import DuLieuImportTaiChinh
from app.models.hopdong import HopDong
from app.schemas.import_taichinh import (
    DongImportResponse,
    ImportKetQuaResponse,
    ImportTaiChinhFilter,
)
from app.constants.statuses import TrangThaiImport, LoaiKhoanThu
from app.services.audit_service import write_audit_log

try:
    import openpyxl
except ImportError as exc:  # pragma: no cover
    raise ImportError("openpyxl chưa được cài đặt. Chạy: pip install openpyxl") from exc


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gen_ma_import(db: Session) -> str:
    """Sinh mã import duy nhất."""
    while True:
        ma = "IMP" + uuid.uuid4().hex[:8].upper()
        if not db.get(DuLieuImportTaiChinh, ma):
            return ma


def _mahd_exists(db: Session, mahd: str) -> bool:
    """Kiểm tra mã hợp đồng tồn tại."""
    return db.get(HopDong, mahd) is not None


def _validate_row(
    db: Session,
    row_data: dict[str, Any],
    so_dong: int,
    mahd_cache: set[str],
) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của một dòng Excel.
    Trả về (is_valid, error_message).
    """
    mahd = row_data.get("mahd")
    thang = row_data.get("thang")
    nam = row_data.get("nam")
    loai_khoan = row_data.get("loai_khoan")
    so_tien = row_data.get("so_tien")

    errors: list[str] = []

    if not mahd:
        errors.append("Mã hợp đồng trống")
    else:
        if mahd not in mahd_cache:
            if _mahd_exists(db, mahd):
                mahd_cache.add(mahd)
            else:
                errors.append(f"Mã hợp đồng '{mahd}' không tồn tại")

    if thang is None:
        errors.append("Thiếu tháng")
    elif not (1 <= int(thang) <= 12):
        errors.append(f"Tháng '{thang}' không hợp lệ (1-12)")

    if nam is None:
        errors.append("Thiếu năm")
    elif int(nam) > date.today().year:
        errors.append(f"Năm '{nam}' không được ở tương lai")

    if not loai_khoan:
        errors.append("Thiếu loại khoản")
    elif loai_khoan not in LoaiKhoanThu.ALL:
        errors.append(
            f"Loại khoản '{loai_khoan}' không hợp lệ. "
            f"Chấp nhận: {LoaiKhoanThu.ALL}"
        )

    if so_tien is None:
        errors.append("Thiếu số tiền")
    else:
        try:
            if float(so_tien) <= 0:
                errors.append("Số tiền phải > 0")
        except (TypeError, ValueError):
            errors.append(f"Số tiền '{so_tien}' không phải số hợp lệ")

    if errors:
        return False, "; ".join(errors)
    return True, ""


def _read_excel_rows(file_content: bytes) -> list[dict[str, Any]]:
    """
    Đọc file Excel và trả về danh sách dòng dưới dạng dict.
    Cột mong đợi (theo thứ tự): mahd, thang, nam, loai_khoan, so_tien, ghi_chu
    """
    import io
    wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True, data_only=True)
    ws = wb.active

    rows: list[dict[str, Any]] = []
    HEADER_ROW = 1  # Dòng 1 là tiêu đề

    for i, row in enumerate(ws.iter_rows(min_row=HEADER_ROW + 1, values_only=True), start=2):
        rows.append({
            "so_dong": i,
            "mahd": row[0],
            "thang": row[1],
            "nam": row[2],
            "loai_khoan": row[3],
            "so_tien": row[4],
            "ghi_chu": row[5] if len(row) > 5 else None,
        })

    wb.close()
    return rows


# ── Business logic ────────────────────────────────────────────────────────────

def import_excel_tai_chinh(
    db: Session,
    file_content: bytes,
    ten_file: str,
    matk: str,
    manv: str | None,
) -> ImportKetQuaResponse:
    """
    Đọc file Excel, validate từng dòng, lưu toàn bộ vào DULIEU_IMPORT_TAICHINH.

    Dòng hợp lệ → trang_thai = 'Hợp lệ'
    Dòng lỗi    → trang_thai = 'Lỗi' + loi_chi_tiet
    """
    rows = _read_excel_rows(file_content)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File Excel không có dữ liệu (bỏ qua hàng tiêu đề)",
        )

    mahd_cache: set[str] = set()
    records: list[DuLieuImportTaiChinh] = []
    dong_loi: list[DongImportResponse] = []
    so_hop_le = 0
    thoi_gian = datetime.now()

    for row in rows:
        so_dong = row["so_dong"]
        is_valid, error_msg = _validate_row(db, row, so_dong, mahd_cache)

        trang_thai = TrangThaiImport.HOP_LE if is_valid else TrangThaiImport.LOI
        if is_valid:
            so_hop_le += 1
        else:
            dong_loi.append(
                DongImportResponse(
                    so_dong=so_dong,
                    mahd=row.get("mahd"),
                    thang=row.get("thang"),
                    nam=row.get("nam"),
                    loai_khoan=row.get("loai_khoan"),
                    so_tien=row.get("so_tien"),
                    ghi_chu=row.get("ghi_chu"),
                    trang_thai=trang_thai,
                    loi_chi_tiet=error_msg,
                )
            )

        ma = _gen_ma_import(db)
        rec = DuLieuImportTaiChinh(
            ma_import=ma,
            mahd=row.get("mahd"),
            thang=row.get("thang"),
            nam=row.get("nam"),
            loai_khoan=row.get("loai_khoan"),
            so_tien=row.get("so_tien"),
            ghi_chu=row.get("ghi_chu"),
            manv_import=manv,
            thoi_gian_import=thoi_gian,
            ten_file=ten_file,
            so_dong_excel=so_dong,
            trang_thai=trang_thai,
            loi_chi_tiet=error_msg or None,
        )
        records.append(rec)

    db.add_all(records)
    db.commit()

    write_audit_log(
        db=db,
        matk=matk,
        hanh_dong="IMPORT",
        doi_tuong="IMPORT_TAICHINH",
        ma_doi_tuong=ten_file,
        noi_dung=(
            f"Import file '{ten_file}': "
            f"{len(rows)} dòng, {so_hop_le} hợp lệ, {len(dong_loi)} lỗi"
        ),
    )

    return ImportKetQuaResponse(
        ten_file=ten_file,
        tong_dong=len(rows),
        so_dong_hop_le=so_hop_le,
        so_dong_loi=len(dong_loi),
        danh_sach_loi=dong_loi,
    )


def list_import_tai_chinh(
    db: Session,
    filters: ImportTaiChinhFilter,
) -> dict[str, Any]:
    """Lấy danh sách bản ghi import có phân trang và lọc."""
    stmt = select(DuLieuImportTaiChinh)

    if filters.mahd:
        stmt = stmt.where(DuLieuImportTaiChinh.mahd == filters.mahd)
    if filters.thang:
        stmt = stmt.where(DuLieuImportTaiChinh.thang == filters.thang)
    if filters.nam:
        stmt = stmt.where(DuLieuImportTaiChinh.nam == filters.nam)
    if filters.trang_thai:
        stmt = stmt.where(DuLieuImportTaiChinh.trang_thai == filters.trang_thai)
    if filters.manv_import:
        stmt = stmt.where(DuLieuImportTaiChinh.manv_import == filters.manv_import)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (filters.page - 1) * filters.page_size
    items = list(db.execute(stmt.offset(offset).limit(filters.page_size)).scalars().all())

    return {"total": total, "page": filters.page, "page_size": filters.page_size, "items": items}
