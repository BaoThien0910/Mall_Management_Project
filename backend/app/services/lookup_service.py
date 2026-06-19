# File: app/services/lookup_service.py

from typing import Any, Dict, List

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.constants.roles import RoleCode
from app.constants.statuses import (
    HopDongStatus,
    MatBangStatus,
    YeuCauThueThemStatus,
)
from app.models import (
    HopDong,
    KhachThue,
    MatBang,
    NhanVien,
    TaiKhoan,
    YeuCauThueThem,
)


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


def _tenant_to_option(tenant: KhachThue) -> Dict[str, Any]:
    return {
        "ma_khach_thue": tenant.ma_khach_thue,
        "ten_khach": tenant.ten_khach,
        "cccd_mst": tenant.cccd_mst,
        "so_dien_thoai": tenant.so_dien_thoai,
        "email": tenant.email,
        "dia_chi": tenant.dia_chi,
        "trang_thai": tenant.trang_thai,
        "label": f"{tenant.ma_khach_thue} - {tenant.ten_khach}",
    }


def _rent_request_to_option(
    request: YeuCauThueThem,
    premise: MatBang,
) -> Dict[str, Any]:
    return {
        "ma_yeu_cau": request.ma_yeu_cau,
        "ma_khach_thue": request.ma_khach_thue,
        "ma_mat_bang": request.ma_mat_bang,
        "ngay_gui": request.ngay_gui,
        "ngay_duyet": request.ngay_duyet,
        "ly_do": request.ly_do,
        "ghi_chu": request.ghi_chu,
        "trang_thai": request.trang_thai,
        "vi_tri": premise.vi_tri,
        "tang": premise.tang,
        "dien_tich": premise.dien_tich,
        "loai_mat_bang": premise.loai_mat_bang,
        "trang_thai_mat_bang": premise.trang_thai,
        "label": f"{request.ma_yeu_cau} - {request.ma_mat_bang} - {premise.vi_tri}",
    }


def list_maintenance_premises(
    db: Session,
    current_user: Any,
) -> Dict[str, List[Dict[str, Any]]]:
    """Danh sách mặt bằng dùng cho form gửi/xử lý sự cố bảo trì."""
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


def list_vhbt_employees(db: Session) -> Dict[str, List[Dict[str, Any]]]:
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


def list_account_employees(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Danh sách nhân viên đang làm và chưa có tài khoản."""
    stmt = (
        select(NhanVien)
        .where(
            NhanVien.trang_thai == "Đang làm",
            ~exists().where(TaiKhoan.ma_nhan_vien == NhanVien.ma_nhan_vien),
        )
        .order_by(NhanVien.ma_nhan_vien.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_employee_to_option(item) for item in items]}


def list_account_tenants(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Danh sách khách thuê đang thuê, đã có hợp đồng và chưa có tài khoản."""
    stmt = (
        select(KhachThue)
        .where(
            KhachThue.trang_thai == "Đang thuê",
            ~exists().where(TaiKhoan.ma_khach_thue == KhachThue.ma_khach_thue),
            exists().where(HopDong.ma_khach_thue == KhachThue.ma_khach_thue),
        )
        .order_by(KhachThue.ma_khach_thue.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_tenant_to_option(item) for item in items]}


def list_contract_tenants(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """
    Danh sách khách thuê dùng cho form số hóa hợp đồng.

    Không lọc theo tài khoản vì nhân viên KDTC cần chọn khách thuê theo nghiệp vụ,
    bao gồm cả khách thuê mới chưa có hợp đồng hiệu lực.
    """
    stmt = (
        select(KhachThue)
        .where(KhachThue.trang_thai == "Đang thuê")
        .order_by(KhachThue.ma_khach_thue.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_tenant_to_option(item) for item in items]}


def list_approved_rent_requests_for_contract(
    db: Session,
    ma_khach_thue: str,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Danh sách yêu cầu thuê thêm đã duyệt của một khách thuê.

    Dùng cho luồng số hóa hợp đồng:
    chọn khách thuê trước -> nếu có yêu cầu đã duyệt thì chọn yêu cầu -> tự fill mặt bằng.
    """
    stmt = (
        select(YeuCauThueThem, MatBang)
        .join(MatBang, MatBang.ma_mat_bang == YeuCauThueThem.ma_mat_bang)
        .where(
            YeuCauThueThem.ma_khach_thue == ma_khach_thue,
            YeuCauThueThem.trang_thai
            == YeuCauThueThemStatus.DA_DUYET_CHO_SO_HOA_HOP_DONG.value,
        )
        .order_by(YeuCauThueThem.ngay_duyet.desc())
    )

    rows = db.execute(stmt).all()
    return {
        "items": [
            _rent_request_to_option(request, premise)
            for request, premise in rows
        ]
    }


def list_vacant_premises(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """
    Danh sách mặt bằng còn trống.

    Dùng cho:
    - hợp đồng đăng ký mới,
    - yêu cầu thuê thêm của khách thuê.
    """
    stmt = (
        select(MatBang)
        .where(MatBang.trang_thai == MatBangStatus.CON_TRONG.value)
        .order_by(MatBang.ma_mat_bang.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_premise_to_option(item) for item in items]}


def list_meter_premises(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """
    Danh sách mặt bằng dùng cho nhập chỉ số điện nước.

    Ưu tiên các mặt bằng đang thuê vì chỉ số điện nước phục vụ tính công nợ.
    """
    stmt = (
        select(MatBang)
        .where(MatBang.trang_thai == MatBangStatus.DANG_THUE.value)
        .order_by(MatBang.ma_mat_bang.asc())
    )

    items = db.execute(stmt).scalars().all()
    return {"items": [_premise_to_option(item) for item in items]}
