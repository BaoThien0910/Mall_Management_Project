from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HopDong(Base):
    __tablename__ = "HOPDONG"

    ma_hd: Mapped[str] = mapped_column(String(20), name="MAHD", primary_key=True)
    
    # Khóa ngoại trỏ tới Khách thuê và Mặt bằng
    ma_khach: Mapped[str] = mapped_column(String(20), ForeignKey("KHACHTHUE.MAKH"), name="MAKH", nullable=False)
    ma_matbang: Mapped[str] = mapped_column(String(20), ForeignKey("MATBANG.MAMB"), name="MAMB", nullable=False)
    
    # Nhân viên số hóa hợp đồng
    manv_sohoa: Mapped[str] = mapped_column(String(20), ForeignKey("NHANVIEN.MANV"), name="MANV_SOHOA", nullable=False)
    
    # Mã yêu cầu thuê thêm (có thể rỗng)
    ma_yc: Mapped[str | None] = mapped_column(String(20), name="MAYC", nullable=True)
    
    ngay_bat_dau: Mapped[date] = mapped_column(Date, name="NGAYBATDAU", nullable=False)
    ngay_ket_thuc: Mapped[date] = mapped_column(Date, name="NGAYKETTHUC", nullable=False)
    gia_thue_thang: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="GIATHUETHANG", nullable=False)
    trang_thai: Mapped[str] = mapped_column(String(30), name="TRANGTHAI", nullable=False)
    ngay_so_hoa: Mapped[datetime] = mapped_column(DateTime, name="NGAYSOHOA", default=datetime.now)