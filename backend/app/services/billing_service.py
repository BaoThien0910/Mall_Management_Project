# File: app/services/billing_service.py
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any, DefaultDict, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions.business_exceptions import BadRequestException
from app.models.chisodiennuoc import ChiSoDienNuoc
from app.models.congno import CongNo
from app.models.dulieu_import_taichinh import DuLieuImportTaiChinh
from app.models.hopdong import HopDong
from app.services._common import generate_code, get_column, get_value


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def _current_customer_id(current_user: Any) -> Optional[str]:
    return get_value(current_user, ["ma_kh", "ma_khach_thue", "makh"])


def _serialize_debt(item: CongNo) -> Dict[str, Any]:
    return {
        "ma_cong_no": get_value(item, ["ma_cong_no", "ma_cn"], ""),
        "ma_hop_dong": get_value(item, ["ma_hop_dong", "ma_hd"], ""),
        "thang": item.thang,
        "nam": item.nam,
        "tien_thue": item.tien_thue,
        "tien_dien": item.tien_dien,
        "tien_nuoc": item.tien_nuoc,
        "phi_bao_tri": item.phi_bao_tri,
        "tien_hoan": item.tien_hoan,
        "tong_tien": item.tong_tien,
        "han_thanh_toan": get_value(item, ["han_thanh_toan"], None),
        "trang_thai": item.trang_thai,
        "ngay_lap": item.ngay_lap,
    }


def calculate_monthly_debts(
    db: Session,
    payload: Any,
    current_user: Any,
) -> Dict[str, Any]:
    """Tính công nợ tháng từ dữ liệu import tài chính và chỉ số điện nước.

    Nguồn tiền:
    - Tiền thuê, phí bảo trì, hoàn trả: DULIEU_IMPORT_TAICHINH theo MAHD.
    - Tiền điện, tiền nước: CHISODIENNUOC theo MAMB của hợp đồng.
    """
    thang = get_value(payload, ["thang"])
    nam = get_value(payload, ["nam"])
    han_thanh_toan = get_value(payload, ["han_thanh_toan"], None)

    if thang < 1 or thang > 12:
        raise BadRequestException("Tháng phải nằm trong khoảng 1 đến 12")

    import_rows = db.execute(
        select(DuLieuImportTaiChinh).where(
            DuLieuImportTaiChinh.thang == thang,
            DuLieuImportTaiChinh.nam == nam,
            DuLieuImportTaiChinh.trang_thai == "Hợp lệ",
        )
    ).scalars().all()

    grouped: DefaultDict[str, List[DuLieuImportTaiChinh]] = defaultdict(list)
    for row in import_rows:
        ma_hd = get_value(row, ["ma_hop_dong", "ma_hd"])
        if ma_hd:
            grouped[ma_hd].append(row)

    if not grouped:
        return {
            "thang": thang,
            "nam": nam,
            "so_cong_no_da_tao": 0,
            "so_cong_no_bo_qua": 0,
            "so_hop_dong_thieu_chi_so": 0,
            "so_hop_dong_thieu_du_lieu": 0,
            "danh_sach_ma_cn": [],
            "danh_sach_ma_hd_bo_qua": [],
            "danh_sach_thieu_chi_so": [],
            "danh_sach_thieu_du_lieu": [],
        }

    hopdong_id_col = get_column(HopDong, ["ma_hop_dong", "ma_hd"])
    hopdong_mamb_col = get_column(HopDong, ["ma_mat_bang", "ma_mb"])
    congno_mahd_col = get_column(CongNo, ["ma_hop_dong", "ma_hd"])
    congno_id_col = get_column(CongNo, ["ma_cong_no", "ma_cn"])
    meter_mamb_col = get_column(ChiSoDienNuoc, ["ma_mat_bang", "ma_mb"])

    created_debt_ids: List[str] = []
    skipped_contract_ids: List[str] = []
    missing_meter_items: List[Dict[str, str]] = []
    missing_import_items: List[Dict[str, str]] = []

    try:
        for ma_hd, rows in grouped.items():
            existing_debt = db.execute(
                select(CongNo).where(
                    congno_mahd_col == ma_hd,
                    CongNo.thang == thang,
                    CongNo.nam == nam,
                )
            ).scalars().first()
            if existing_debt is not None:
                skipped_contract_ids.append(ma_hd)
                continue

            hop_dong = db.execute(
                select(HopDong).where(hopdong_id_col == ma_hd)
            ).scalars().first()
            if hop_dong is None:
                missing_import_items.append(
                    {
                        "ma_hop_dong": ma_hd,
                        "ly_do": "Không tìm thấy hợp đồng",
                    }
                )
                continue

            ma_mat_bang = getattr(hop_dong, hopdong_mamb_col.key)
            meter = db.execute(
                select(ChiSoDienNuoc).where(
                    meter_mamb_col == ma_mat_bang,
                    ChiSoDienNuoc.thang == thang,
                    ChiSoDienNuoc.nam == nam,
                )
            ).scalars().first()
            if meter is None:
                missing_meter_items.append(
                    {
                        "ma_hop_dong": ma_hd,
                        "ma_mat_bang": ma_mat_bang,
                        "ly_do": f"Chưa có chỉ số điện nước tháng {thang}/{nam}",
                    }
                )
                continue

            tien_thue = Decimal("0")
            phi_bao_tri = Decimal("0")
            tien_hoan = Decimal("0")

            for row in rows:
                loai_khoan = get_value(row, ["loai_khoan"], "")
                so_tien = _to_decimal(get_value(row, ["so_tien"], 0))
                if loai_khoan == "Tiền thuê":
                    tien_thue += so_tien
                elif loai_khoan == "Phí bảo trì":
                    phi_bao_tri += so_tien
                elif loai_khoan == "Hoàn trả":
                    tien_hoan += so_tien

            if tien_thue <= 0:
                missing_import_items.append(
                    {
                        "ma_hop_dong": ma_hd,
                        "ly_do": "Thiếu dòng Tiền thuê trong dữ liệu import",
                    }
                )
                continue

            tien_dien = _to_decimal(get_value(meter, ["tien_dien"], 0))
            tien_nuoc = _to_decimal(get_value(meter, ["tien_nuoc"], 0))
            tong_tien = tien_thue + tien_dien + tien_nuoc + phi_bao_tri - tien_hoan

            if tong_tien < 0:
                missing_import_items.append(
                    {
                        "ma_hop_dong": ma_hd,
                        "ly_do": "Tổng tiền công nợ không được âm",
                    }
                )
                continue

            ma_cn = generate_code("CN")
            debt = CongNo(
                ma_cong_no=ma_cn,
                ma_hop_dong=ma_hd,
                thang=thang,
                nam=nam,
                tien_thue=tien_thue,
                tien_dien=tien_dien,
                tien_nuoc=tien_nuoc,
                phi_bao_tri=phi_bao_tri,
                tien_hoan=tien_hoan,
                tong_tien=tong_tien,
                han_thanh_toan=han_thanh_toan,
                trang_thai="Chưa thanh toán",
            )
            db.add(debt)
            created_debt_ids.append(ma_cn)

            for row in rows:
                row.trang_thai = "Đã dùng tính công nợ"

        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "thang": thang,
        "nam": nam,
        "so_cong_no_da_tao": len(created_debt_ids),
        "so_cong_no_bo_qua": len(skipped_contract_ids),
        "so_hop_dong_thieu_chi_so": len(missing_meter_items),
        "so_hop_dong_thieu_du_lieu": len(missing_import_items),
        "danh_sach_ma_cn": created_debt_ids,
        "danh_sach_ma_hd_bo_qua": skipped_contract_ids,
        "danh_sach_thieu_chi_so": missing_meter_items,
        "danh_sach_thieu_du_lieu": missing_import_items,
    }


def list_debts(
    db: Session,
    filters: Optional[Any] = None,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    stmt = select(CongNo)

    ma_hop_dong = get_value(filters, ["ma_hop_dong", "ma_hd"], None) if filters else None
    thang = get_value(filters, ["thang"], None) if filters else None
    nam = get_value(filters, ["nam"], None) if filters else None
    trang_thai = get_value(filters, ["trang_thai"], None) if filters else None
    page = get_value(filters, ["page"], 1) if filters else 1
    page_size = get_value(filters, ["page_size"], 10) if filters else 10

    if ma_hop_dong:
        stmt = stmt.where(get_column(CongNo, ["ma_hop_dong", "ma_hd"]) == ma_hop_dong)
    if thang:
        stmt = stmt.where(CongNo.thang == thang)
    if nam:
        stmt = stmt.where(CongNo.nam == nam)
    if trang_thai:
        stmt = stmt.where(CongNo.trang_thai == trang_thai)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    items = db.execute(
        stmt.order_by(CongNo.nam.desc(), CongNo.thang.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return {
        "items": [_serialize_debt(item) for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total else 0,
        },
    }


def list_my_debts(
    db: Session,
    filters: Optional[Any] = None,
    current_user: Optional[Any] = None,
) -> Dict[str, Any]:
    ma_khach_thue = _current_customer_id(current_user)
    if not ma_khach_thue:
        raise BadRequestException("Tài khoản hiện tại không gắn với khách thuê")

    hopdong_makh_col = get_column(HopDong, ["ma_khach_thue", "ma_kh"])
    hopdong_mahd_col = get_column(HopDong, ["ma_hop_dong", "ma_hd"])
    congno_mahd_col = get_column(CongNo, ["ma_hop_dong", "ma_hd"])

    contract_ids = db.execute(
        select(hopdong_mahd_col).where(hopdong_makh_col == ma_khach_thue)
    ).scalars().all()

    if not contract_ids:
        return {
            "items": [],
            "pagination": {"page": 1, "page_size": 10, "total": 0, "total_pages": 0},
        }

    stmt = select(CongNo).where(congno_mahd_col.in_(contract_ids))

    thang = get_value(filters, ["thang"], None) if filters else None
    nam = get_value(filters, ["nam"], None) if filters else None
    trang_thai = get_value(filters, ["trang_thai"], None) if filters else None
    page = get_value(filters, ["page"], 1) if filters else 1
    page_size = get_value(filters, ["page_size"], 10) if filters else 10

    if thang:
        stmt = stmt.where(CongNo.thang == thang)
    if nam:
        stmt = stmt.where(CongNo.nam == nam)
    if trang_thai:
        stmt = stmt.where(CongNo.trang_thai == trang_thai)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    items = db.execute(
        stmt.order_by(CongNo.nam.desc(), CongNo.thang.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return {
        "items": [_serialize_debt(item) for item in items],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total else 0,
        },
    }
