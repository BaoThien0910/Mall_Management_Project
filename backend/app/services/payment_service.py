"""Thanh toán mô phỏng trong transaction."""

import random
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.dependencies import Principal, has_permission
from app.models.congno import CongNo
from app.models.hoadon import HoaDon
from app.models.hopdong import HopDong
from app.schemas.payment import PaymentBody, PaymentResult, new_txn_id


def process_payment_simulation(db: Session, principal: Principal, body: PaymentBody) -> PaymentResult:
    if not has_permission(principal, "finance.pay"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Không được phép thanh toán.")

    if principal.role != "tenant":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Chỉ khách thuê mới được thanh toán.")

    # 1. Lấy Công nợ kèm Hợp đồng (Đã sửa thành CongNo.ma_congno)
    result = db.query(CongNo, HopDong).join(HopDong, CongNo.ma_hd == HopDong.ma_hd).filter(CongNo.ma_congno == body.debtId).first()
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Không thấy công nợ.")
    
    cn, hd = result

    # 2. Check quyền sở hữu Hợp đồng
    code = principal.ma_khach_dai_dien or ""
    if hd.ma_khach != code:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Công nợ không thuộc về bạn.")

    # 3. Check số tiền & Trạng thái (DB bắt buộc SOTIEN = TONGTIEN ở bảng HOADON)
    if cn.trang_thai == "Đã thanh toán":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Công nợ đã thanh toán đủ.")
    
    if float(body.amount) != float(cn.tong_tien):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Vui lòng thanh toán đúng số tiền {cn.tong_tien}.")

    txn = new_txn_id()
    paid_at = datetime.now()
    invoice_no = f"INV-{paid_at.strftime('%Y%m%d')}-{txn[-6:]}"

    try:
        # 4. Tạo Hóa đơn (Đã sửa toàn bộ trường dựa trên file hoadon.py chuẩn của bạn)
        db.add(
            HoaDon(
                ma_hd=invoice_no,
                ma_congno=cn.ma_congno,
                ma_khach=hd.ma_khach,
                tien_thue=cn.tien_thue,
                tien_dien=cn.tien_dien,
                tien_nuoc=cn.tien_nuoc,
                phi_bao_tri=cn.phi_bao_tri,
                tien_hoan=cn.tien_hoan,
                tong_tien=cn.tong_tien,
                so_tien=body.amount,
                phuong_thuc=body.method,
                ma_giao_dich=txn,
                ngay_tt=paid_at,
                trang_thai="Thành công"
            )
        )
        
        # 5. Cập nhật trạng thái Công nợ
        cn.trang_thai = "Đã thanh toán"
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi ghi giao dịch xuống database.") from e

    return PaymentResult(success=True, transactionId=txn, paidAt=paid_at)