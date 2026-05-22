# File: app/services/payment_service.py
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants.statuses import AuditAction, CongNoStatus, HoaDonStatus
from app.exceptions.business_exceptions import ConflictException, ForbiddenException, InvalidStateException, NotFoundException
from app.models import CongNo, HoaDon, HopDong
from app.schemas.hoadon import MoPhongKetQuaThanhToanRequest, TaoGiaoDichThanhToanRequest
from app.services.audit_service import write_audit_log
from app.utils.datetime_helper import current_datetime
from app.utils.transaction import transaction_context


def _generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _user_attr(current_user: Any, short_name: str, long_name: str) -> Any:
    value = getattr(current_user, short_name, None)
    return value if value is not None else getattr(current_user, long_name, None)


def _assert_debt_ownership(db: Session, debt: CongNo, ma_khach_thue: str) -> None:
    contract = db.execute(
        select(HopDong).where(HopDong.ma_hop_dong == debt.ma_hop_dong)
    ).scalars().first()
    if contract is None or contract.ma_khach_thue != ma_khach_thue:
        raise ForbiddenException("Công nợ không thuộc khách thuê hiện tại")


def create_simulated_payment(
    db: Session,
    payload: TaoGiaoDichThanhToanRequest,
    current_user: Any,
) -> HoaDon:
    """Tạo hóa đơn/giao dịch thanh toán mô phỏng cho công nợ hợp lệ."""
    debt = db.execute(
        select(CongNo).where(CongNo.ma_cong_no == payload.ma_cong_no)
    ).scalars().first()
    if debt is None:
        raise NotFoundException("Không tìm thấy công nợ")

    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if not ma_khach_thue:
        raise ForbiddenException("Tài khoản hiện tại không phải khách thuê")
    _assert_debt_ownership(db, debt, ma_khach_thue)

    if debt.trang_thai not in {CongNoStatus.CHUA_THANH_TOAN.value, CongNoStatus.QUA_HAN.value}:
        raise InvalidStateException("Công nợ không thể tạo giao dịch thanh toán")

    successful_invoice = db.execute(
        select(HoaDon).where(
            HoaDon.ma_cong_no == debt.ma_cong_no,
            HoaDon.trang_thai == HoaDonStatus.THANH_CONG.value,
        )
    ).scalars().first()
    if successful_invoice is not None:
        raise ConflictException("Công nợ đã có hóa đơn thanh toán thành công")

    invoice = HoaDon(
        ma_hoa_don=_generate_code("HDTT"),
        ma_cong_no=debt.ma_cong_no,
        ma_khach_thue=ma_khach_thue,
        tien_thue=debt.tien_thue,
        tien_dien=debt.tien_dien,
        tien_nuoc=debt.tien_nuoc,
        phi_bao_tri=debt.phi_bao_tri,
        tien_hoan=debt.tien_hoan,
        tong_tien=debt.tong_tien,
        so_tien=debt.tong_tien,
        phuong_thuc=_enum_value(payload.phuong_thuc),
        ma_giao_dich_cong=_generate_code("SIM"),
        thoi_gian_giao_dich=current_datetime(),
        trang_thai=HoaDonStatus.DANG_XU_LY.value,
        noi_dung="Thanh toán công nợ mô phỏng",
        ghi_chu=None,
    )

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        db.add(invoice)
        db.flush()
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.TAO_MOI,
            doi_tuong="HOADON",
            ma_doi_tuong=invoice.ma_hoa_don,
            chi_tiet="Tạo giao dịch thanh toán mô phỏng",
        )
    return invoice


def get_payment_detail(
    db: Session,
    ma_hoa_don: str,
    current_user: Any,
) -> HoaDon:
    """Lấy chi tiết hóa đơn mô phỏng của khách thuê hiện tại."""
    invoice = db.execute(
        select(HoaDon).where(HoaDon.ma_hoa_don == ma_hoa_don)
    ).scalars().first()
    if invoice is None:
        raise NotFoundException("Không tìm thấy hóa đơn")

    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if invoice.ma_khach_thue != ma_khach_thue:
        raise ForbiddenException("Hóa đơn không thuộc khách thuê hiện tại")
    return invoice


def simulate_payment_result(
    db: Session,
    ma_hoa_don: str,
    payload: MoPhongKetQuaThanhToanRequest,
    current_user: Any,
) -> HoaDon:
    """Mô phỏng kết quả giao dịch và đồng bộ trạng thái công nợ."""
    invoice = db.execute(
        select(HoaDon).where(HoaDon.ma_hoa_don == ma_hoa_don)
    ).scalars().first()
    if invoice is None:
        raise NotFoundException("Không tìm thấy hóa đơn")

    ma_khach_thue = _user_attr(current_user, "ma_kh", "ma_khach_thue")
    if invoice.ma_khach_thue != ma_khach_thue:
        raise ForbiddenException("Hóa đơn không thuộc khách thuê hiện tại")
    if invoice.trang_thai != HoaDonStatus.DANG_XU_LY.value:
        raise InvalidStateException("Hóa đơn không còn ở trạng thái đang xử lý")

    debt = db.execute(
        select(CongNo).where(CongNo.ma_cong_no == invoice.ma_cong_no)
    ).scalars().first()
    if debt is None:
        raise NotFoundException("Không tìm thấy công nợ của hóa đơn")

    actor_ma_tk = _user_attr(current_user, "ma_tk", "ma_tai_khoan")
    with transaction_context(db):
        if payload.ket_qua == "THANH_CONG":
            invoice.trang_thai = HoaDonStatus.THANH_CONG.value
            debt.trang_thai = CongNoStatus.DA_THANH_TOAN.value
            detail = "Mô phỏng thanh toán thành công"
        else:
            invoice.trang_thai = HoaDonStatus.THAT_BAI.value
            detail = "Mô phỏng thanh toán thất bại"
        write_audit_log(
            db=db,
            ma_tk=actor_ma_tk,
            hanh_dong=AuditAction.CAP_NHAT,
            doi_tuong="HOADON",
            ma_doi_tuong=invoice.ma_hoa_don,
            chi_tiet=detail,
        )
    return invoice
