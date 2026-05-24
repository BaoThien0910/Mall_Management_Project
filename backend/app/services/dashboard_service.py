# File: app/services/dashboard_service.py
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.baocaotaichinh import BaoCaoTaiChinh
from app.models.congno import CongNo
from app.models.dulieu_import_taichinh import DuLieuImportTaiChinh
from app.models.hopdong import HopDong
from app.models.nhatky import NhatKy
from app.models.sk_baotri import SuCoBaoTri
from app.models.taikhoan import TaiKhoan
from app.models.thongbao import ThongBao
from app.models.yc_thuethem import YeuCauThueThem
from app.services._common import get_column, get_value


def _count(db: Session, stmt: Any) -> int:
    return int(db.execute(stmt).scalar_one() or 0)


def _card(key: str, title: str, value: Any, description: str = None, status: str = None) -> Dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "value": value,
        "description": description,
        "status": status,
    }


def _role(current_user: Any) -> str:
    return str(get_value(current_user, ["ma_vai_tro", "role_code", "mavaitro"], ""))


def _employee_id(current_user: Any) -> str:
    return str(get_value(current_user, ["ma_nv", "ma_nhan_vien", "manv"], ""))


def _customer_id(current_user: Any) -> str:
    return str(get_value(current_user, ["ma_kh", "ma_khach_thue", "makh"], ""))


def get_my_dashboard(db: Session, current_user: Any) -> Dict[str, Any]:
    """Trả số liệu dashboard và badge menu theo role hiện tại."""
    role = _role(current_user)

    if role == "QTV":
        total_accounts = _count(db, select(func.count()).select_from(TaiKhoan))
        disabled_accounts = _count(
            db,
            select(func.count()).select_from(TaiKhoan).where(TaiKhoan.trang_thai == "Vô hiệu"),
        )
        audit_logs = _count(db, select(func.count()).select_from(NhatKy))
        return {
            "role": role,
            "summary_cards": [
                _card("total_accounts", "Tổng tài khoản", total_accounts),
                _card("disabled_accounts", "Tài khoản vô hiệu", disabled_accounts),
                _card("audit_logs", "Nhật ký thao tác", audit_logs),
            ],
            "menu_badges": {
                "accounts": disabled_accounts,
                "audit_logs": 0,
            },
        }

    if role == "BQL":
        pending_rent_requests = _count(
            db,
            select(func.count()).select_from(YeuCauThueThem).where(
                YeuCauThueThem.trang_thai == "Chờ duyệt"
            ),
        )
        pending_incidents = _count(
            db,
            select(func.count()).select_from(SuCoBaoTri).where(
                SuCoBaoTri.trang_thai == "Chờ duyệt"
            ),
        )
        published_notifications = _count(
            db,
            select(func.count()).select_from(ThongBao).where(
                ThongBao.trang_thai == "Đã ban hành"
            ),
        )
        return {
            "role": role,
            "summary_cards": [
                _card("pending_rent_requests", "Yêu cầu thuê thêm", pending_rent_requests, "Chờ duyệt"),
                _card("pending_incidents", "Sự cố bảo trì", pending_incidents, "Chờ duyệt"),
                _card("published_notifications", "Thông báo đang ban hành", published_notifications),
            ],
            "menu_badges": {
                "rent_requests": pending_rent_requests,
                "incidents": pending_incidents,
            },
        }

    if role in {"TP_KDTC", "NV_KDTC"}:
        active_contracts = _count(
            db,
            select(func.count()).select_from(HopDong).where(HopDong.trang_thai == "Đang hiệu lực"),
        )
        unpaid_debts = _count(
            db,
            select(func.count()).select_from(CongNo).where(CongNo.trang_thai == "Chưa thanh toán"),
        )
        import_errors = _count(
            db,
            select(func.count()).select_from(DuLieuImportTaiChinh).where(
                DuLieuImportTaiChinh.trang_thai == "Lỗi"
            ),
        )
        cards: List[Dict[str, Any]] = [
            _card("active_contracts", "Hợp đồng hiệu lực", active_contracts),
            _card("unpaid_debts", "Công nợ chưa thanh toán", unpaid_debts),
            _card("import_errors", "Dòng import lỗi", import_errors),
        ]
        if role == "TP_KDTC":
            draft_reports = _count(
                db,
                select(func.count()).select_from(BaoCaoTaiChinh).where(
                    BaoCaoTaiChinh.trang_thai == "Bản nháp"
                ),
            )
            cards.append(_card("draft_reports", "Báo cáo bản nháp", draft_reports))
        return {
            "role": role,
            "summary_cards": cards,
            "menu_badges": {
                "debts": unpaid_debts,
                "financial_import": import_errors,
            },
        }

    if role in {"TP_VHBT", "NV_VHBT"}:
        stmt_pending = select(func.count()).select_from(SuCoBaoTri).where(
            SuCoBaoTri.trang_thai.in_(["Đã duyệt", "Đang xử lý"])
        )
        if role == "NV_VHBT":
            manv = _employee_id(current_user)
            if manv:
                stmt_pending = stmt_pending.where(SuCoBaoTri.ma_nhan_vien_xu_ly == manv)
        processing_incidents = _count(db, stmt_pending)

        pending_assignment = _count(
            db,
            select(func.count()).select_from(SuCoBaoTri).where(
                SuCoBaoTri.trang_thai == "Đã duyệt"
            ),
        )
        return {
            "role": role,
            "summary_cards": [
                _card("processing_incidents", "Sự cố đang xử lý", processing_incidents),
                _card("pending_assignment", "Sự cố chờ phân công", pending_assignment),
            ],
            "menu_badges": {
                "incidents": processing_incidents,
                "maintenance_schedules": 0,
            },
        }

    if role == "KHACH_THUE":
        makh = _customer_id(current_user)
        hopdong_makh_col = get_column(HopDong, ["ma_khach_thue", "ma_kh"])
        hopdong_mahd_col = get_column(HopDong, ["ma_hop_dong", "ma_hd"])
        congno_mahd_col = get_column(CongNo, ["ma_hop_dong", "ma_hd"])

        contract_ids = db.execute(
            select(hopdong_mahd_col).where(hopdong_makh_col == makh)
        ).scalars().all()

        active_contracts = _count(
            db,
            select(func.count()).select_from(HopDong).where(
                hopdong_makh_col == makh,
                HopDong.trang_thai == "Đang hiệu lực",
            ),
        )
        unpaid_debts = 0
        if contract_ids:
            unpaid_debts = _count(
                db,
                select(func.count()).select_from(CongNo).where(
                    congno_mahd_col.in_(contract_ids),
                    CongNo.trang_thai == "Chưa thanh toán",
                ),
            )
        pending_requests = _count(
            db,
            select(func.count()).select_from(YeuCauThueThem).where(
                YeuCauThueThem.ma_khach_thue == makh,
                YeuCauThueThem.trang_thai == "Chờ duyệt",
            ),
        )
        open_incidents = _count(
            db,
            select(func.count()).select_from(SuCoBaoTri).where(
                SuCoBaoTri.ma_khach_thue == makh,
                SuCoBaoTri.trang_thai.in_(["Chờ duyệt", "Đã duyệt", "Đang xử lý"]),
            ),
        )
        return {
            "role": role,
            "summary_cards": [
                _card("active_contracts", "Hợp đồng hiệu lực", active_contracts),
                _card("unpaid_debts", "Công nợ chưa thanh toán", unpaid_debts),
                _card("pending_requests", "Yêu cầu thuê thêm", pending_requests, "Chờ duyệt"),
                _card("open_incidents", "Sự cố bảo trì", open_incidents),
            ],
            "menu_badges": {
                "my_debts": unpaid_debts,
                "rent_requests": pending_requests,
                "incidents": open_incidents,
            },
        }

    return {
        "role": role,
        "summary_cards": [],
        "menu_badges": {},
    }
