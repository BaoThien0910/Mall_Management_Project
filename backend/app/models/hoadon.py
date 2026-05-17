from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HoaDon(Base):
    __tablename__ = "HOADON"

    # ma_hd thành chuỗi (varchar), không tự tăng
    ma_hd: Mapped[str] = mapped_column(String(20), name="MAHOADON", primary_key=True)
    ma_congno: Mapped[str] = mapped_column(String(20), ForeignKey("CONGNO.MACN"), name="MACN", nullable=False, index=True)
    ma_khach: Mapped[str] = mapped_column(String(20), ForeignKey("KHACHTHUE.MAKH"), name="MAKH", nullable=False)

    # Chi tiết tiền thanh toán
    tien_thue: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENTHUE", nullable=False)
    tien_dien: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENDIEN", nullable=False)
    tien_nuoc: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENNUOC", nullable=False)
    phi_bao_tri: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="PHIBAOTRI", default=Decimal("0.0"))
    tien_hoan: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENHOAN", default=Decimal("0.0"))
    tong_tien: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TONGTIEN", nullable=False)
    so_tien: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="SOTIEN", nullable=False)

    # Thông tin giao dịch
    phuong_thuc: Mapped[str] = mapped_column(String(50), name="PHUONGTHUC", nullable=False)
    ma_giao_dich: Mapped[str | None] = mapped_column(String(100), name="MAGIAODICHCONG", nullable=True)
    ngay_tt: Mapped[datetime] = mapped_column(DateTime, name="THOIGIANGD", default=datetime.now)
    trang_thai: Mapped[str] = mapped_column(String(30), name="TRANGTHAI", default="Đang xử lý")
    noi_dung: Mapped[str | None] = mapped_column(String(255), name="NOIDUNG", nullable=True)
    ghi_chu: Mapped[str | None] = mapped_column(String(255), name="GHICHU", nullable=True)