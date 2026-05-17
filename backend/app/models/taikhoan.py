from datetime import datetime
from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class TaiKhoan(Base):
    __tablename__ = "TAIKHOAN"

    ma_tk: Mapped[str] = mapped_column(String(20), name="MATK", primary_key=True)
    email_dang_nhap: Mapped[str] = mapped_column(String(50), name="TENDANGNHAP", unique=True, index=True, nullable=False)
    mat_khau_bam: Mapped[str] = mapped_column(String(255), name="MATKHAU", nullable=False)
    
    # Đã thêm ForeignKey chuẩn
    vai_tro_ma: Mapped[str] = mapped_column(String(20), ForeignKey("VAITRO.MAVAITRO"), name="MAVAITRO", nullable=False, index=True)
    
    # Phải có cả MANV và MAKH
    ma_nv: Mapped[str | None] = mapped_column(String(20), ForeignKey("NHANVIEN.MANV"), name="MANV", nullable=True)
    ma_khach_dai_dien: Mapped[str | None] = mapped_column(String(20), ForeignKey("KHACHTHUE.MAKH"), name="MAKH", nullable=True)

    trang_thai: Mapped[str] = mapped_column(String(20), name="TRANGTHAI", default="Hoạt động")
    bat_buoc_doimk: Mapped[bool] = mapped_column(Boolean, name="BATBUOC_DOIMK", default=True)
    solan_dangnhapsai: Mapped[int] = mapped_column(Integer, name="SOLAN_DANGNHAPSAI", default=0)
    
    # Bổ sung 2 cột còn thiếu so với DB
    khoa_den: Mapped[datetime | None] = mapped_column(DateTime, name="KHOA_DEN", nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, name="NGAYTAO", default=datetime.now)