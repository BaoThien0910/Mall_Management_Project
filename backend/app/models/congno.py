from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base


class CongNo(Base):
    __tablename__ = "CONGNO"

    ma_congno: Mapped[str] = mapped_column(String(20), name="MACN", primary_key=True)
    ma_hd: Mapped[str] = mapped_column(String(20), ForeignKey("HOPDONG.MAHD"), name="MAHD", nullable=False)
    
    # DB chia theo Tháng / Năm
    thang: Mapped[int] = mapped_column(Integer, name="THANG", nullable=False)
    nam: Mapped[int] = mapped_column(Integer, name="NAM", nullable=False)

    # Chi tiết các khoản tiền (dùng Numeric cho decimal)
    tien_thue: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENTHUE", nullable=False)
    tien_dien: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENDIEN", nullable=False)
    tien_nuoc: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENNUOC", nullable=False)
    phi_bao_tri: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="PHIBAOTRI", default=Decimal("0.0"))
    tien_hoan: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TIENHOAN", default=Decimal("0.0"))
    tong_tien: Mapped[Decimal] = mapped_column(Numeric(18, 2), name="TONGTIEN", nullable=False)

    han_thanh_toan: Mapped[date | None] = mapped_column(Date, name="HAN_THANHTOAN", nullable=True)
    trang_thai: Mapped[str] = mapped_column(String(30), name="TRANGTHAI", default="Chưa thanh toán")
    
    # Sửa thành datetime.now để đồng bộ giờ Việt Nam với SQL Server
    ngay_lap: Mapped[datetime] = mapped_column(DateTime, name="NGAYLAP", default=datetime.now)