# File: app/services/lookup_service.py

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import HopDongStatus
from app.models import HopDong, MatBang, NhanVien


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def _role_value(current_user: Any) -> str:
    return _enum_value(_user_attr(current_user, "ma_vai_tro", "ma_vai_tro"))


def _premise_to_option(premise: MatBang) -> Dict[str, Any]:
    return {
        "ma_mat_bang": premise.ma_mat_bang,
        "vi_tri": premise.vi_tri,
        "tang": premise.tang,
        "dien_tich": premise.dien_tich,
        "loai_mat_bang": premise.loai_mat_bang,
        "trang_thai": premise.trang_thai,
        "label": f"{premise.ma_mat_bang} - {premise.vi_tri} - Tầng {premise.tang}",
    }


def _employee_to_option(employee: NhanVien) -> Dict[str, Any]:
    return {
        "ma_nhan_vien": employee.ma_nhan_vien,
        "ho_ten": employee.ho_ten,
        "phong_ban": employee.phong_ban,
        "chuc_vu": employee.chuc_vu,
        "so_dien_thoai": employee.so_dien_thoai,
        "email": employee.email,
        "trang_thai": employee.trang_thai,
        "label": f"{employee.ma_nhan_vien} - {employee.ho_ten}",
    }


def list_maintenance_premises(
    db: Session,
    current_user: Any,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Danh sách mặt bằng dùng cho form bảo trì.

    - Khách thuê: chỉ thấy mặt bằng thuộc hợp đồng đang hiệu lực của chính họ.
    - BQL/VHBT: thấy danh sách mặt bằng để lập lịch/xem nghiệp vụ bảo trì.
    """
    role = _role_value(current_user)

    if role == RoleCode.KHACH_THUE.value:
        ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
        stmt = (
            select(MatBang)
            .join(HopDong, HopDong.ma_mat_bang == MatBang.ma_mat_bang)
            .where(
                HopDong.ma_khach_thue == ma_khach_thue,
                HopDong.trang_thai == HopDongStatus.DANG_HIEU_LUC.value,
            )
            .order_by(MatBang.ma_mat_bang.asc())
        )
    else:
        stmt = select(MatBang).order_by(MatBang.ma_mat_bang.asc())

    items = db.execute(stmt).scalars().all()
    return {"items": [_premise_to_option(item) for item in items]}


def list_vhbt_employees(
    db: Session,
) -> Dict[str, List[Dict[str, Any]]]:
    """Danh sách nhân viên đang làm thuộc phòng Vận hành - Bảo trì."""
    stmt = (
        select(NhanVien)
        .where(
            NhanVien.phong_ban == "Vận hành - Bảo trì",
            NhanVien.trang_thai == "Đang làm",
        )
        .order_by(NhanVien.ma_nhan_vien.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_employee_to_option(item) for item in items]}