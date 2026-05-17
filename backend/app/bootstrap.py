"""Seed DB on startup."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.utils.security import hash_password


def _seed_rbac_data(db: Session) -> None:
    """Seed dữ liệu nền tảng cho hệ thống phân quyền (RBAC)."""
    
    # 1. VAITRO (Đã bổ sung cột TRANGTHAI)
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.VAITRO)
        BEGIN
            INSERT INTO dbo.VAITRO (MAVAITRO, TENVAITRO, MOTA, TRANGTHAI)
            VALUES 
                ('admin', N'Quản trị viên', N'Toàn quyền quản trị hệ thống', N'Đang dùng'),
                ('management', N'Ban quản lý', N'Điều hành các hoạt động TTTM', N'Đang dùng'),
                ('staff', N'Nhân viên', N'Nhân viên vận hành và kế toán', N'Đang dùng'),
                ('tenant', N'Khách thuê', N'Khách hàng thuê mặt bằng', N'Đang dùng');
        END
    """))

    # 2. QUYEN (Đã bổ sung cột MODULE và HANHDONG chuẩn theo Constraint)
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.QUYEN)
        BEGIN
            INSERT INTO dbo.QUYEN (MAQUYEN, TENQUYEN, MODULE, HANHDONG, MOTA)
            VALUES 
                ('SYS_VIEW', N'Xem hệ thống', 'Hệ thống', 'Xem', N'Dành cho Admin'),
                ('FIN_READ', N'Xem tài chính', 'Tài chính', 'Xem', N'Xem công nợ, hóa đơn'),
                ('FIN_WRITE', N'Quản lý tài chính', 'Tài chính', 'Tạo', N'Tạo công nợ, hóa đơn'),
                ('PRE_READ', N'Xem mặt bằng', 'Mặt bằng', 'Xem', N'Xem danh sách mặt bằng'),
                ('PRE_WRITE', N'Quản lý mặt bằng', 'Mặt bằng', 'Sửa', N'Cập nhật trạng thái mặt bằng'),
                ('TENANT_OWN', N'Dữ liệu cá nhân', 'Hợp đồng', 'Xem', N'Khách xem dữ liệu của mình');
        END
    """))

    # 3. VAITRO_QUYEN
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.VAITRO_QUYEN)
        BEGIN
            INSERT INTO dbo.VAITRO_QUYEN (MAVAITRO, MAQUYEN)
            VALUES 
                ('admin', 'SYS_VIEW'),
                ('management', 'FIN_READ'), ('management', 'PRE_READ'), ('management', 'PRE_WRITE'),
                ('staff', 'FIN_READ'), ('staff', 'FIN_WRITE'), ('staff', 'PRE_READ'),
                ('tenant', 'TENANT_OWN');
        END
    """))


def _seed_master_data(db: Session) -> None:
    """Seed các dữ liệu Master bắt buộc (Nhân viên, Khách thuê, Mặt bằng, Hợp đồng)"""
    
    # Nhân viên
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.NHANVIEN)
        BEGIN
            INSERT INTO dbo.NHANVIEN (MANV, HOTEN, PHONGBAN, CHUCVU, TRANGTHAI)
            VALUES 
                ('NV_ADMIN', N'Nguyễn Admin', N'Quản trị hệ thống', N'Quản trị viên', N'Đang làm'),
                ('NV_STAFF', N'Trần Staff', N'Kinh doanh - Tài chính', N'Nhân viên', N'Đang làm'),
                ('NV_MNG', N'Lê Manager', N'Ban Quản Lý', N'Ban Quản Lý', N'Đang làm'),
                ('NV_GUEST', N'Khách vãng lai', N'Quản trị hệ thống', N'Nhân viên', N'Đang làm');
        END
    """))

    # Khách thuê
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.KHACHTHUE)
        BEGIN
            INSERT INTO dbo.KHACHTHUE (MAKH, TENKHACH, CCCD_MST, TRANGTHAI)
            VALUES 
                ('KH_STARBUCKS', N'Starbucks Vietnam', '0312345678', N'Đang thuê');
        END
    """))

    # Mặt bằng
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.MATBANG)
        BEGIN
            INSERT INTO dbo.MATBANG (MAMB, VITRI, TANG, DIENTICH, LOAIMB, TRANGTHAI)
            VALUES 
                ('GF-01', N'Mặt tiền cổng chính', 1, 150.50, N'F&B', N'Đang thuê');
        END
    """))

    # Hợp đồng
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.HOPDONG)
        BEGIN
            INSERT INTO dbo.HOPDONG (MAHD, MAKH, MAMB, MANV_SOHOA, NGAYBATDAU, NGAYKETTHUC, GIATHUETHANG, TRANGTHAI)
            VALUES 
                ('HD-2025-001', 'KH_STARBUCKS', 'GF-01', 'NV_STAFF', '2025-01-01', '2028-12-31', 38000000, N'Đang hiệu lực');
        END
    """))


def _seed_accounts(db: Session) -> None:
    """Seed tài khoản (Yêu cầu phải có Nhân viên và Khách thuê trước)"""
    
    pwd_hash = hash_password("1")
    
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.TAIKHOAN)
        BEGIN
            INSERT INTO dbo.TAIKHOAN (MATK, TENDANGNHAP, MATKHAU, MANV, MAKH, MAVAITRO, TRANGTHAI)
            VALUES 
                ('TK_01', 'a', :pwd, 'NV_ADMIN', NULL, 'admin', N'Hoạt động'),
                ('TK_02', 'b', :pwd, 'NV_MNG', NULL, 'management', N'Hoạt động'),
                ('TK_03', 's', :pwd, 'NV_STAFF', NULL, 'staff', N'Hoạt động'),
                ('TK_04', 't', :pwd, NULL, 'KH_STARBUCKS', 'tenant', N'Hoạt động'),
                ('GUEST', 'system_guest', :pwd, 'NV_GUEST', NULL, 'admin', N'Hoạt động');
        END
    """), {"pwd": pwd_hash})


def _seed_finance_data(db: Session) -> None:
    """Seed Công nợ và Hóa đơn chuẩn theo cấu trúc DDL"""
    
    # Công nợ
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.CONGNO)
        BEGIN
            -- Lưu ý: TONGTIEN = TIENTHUE + TIENDIEN + TIENNUOC + PHIBAOTRI - TIENHOAN
            INSERT INTO dbo.CONGNO (MACN, MAHD, THANG, NAM, TIENTHUE, TIENDIEN, TIENNUOC, PHIBAOTRI, TIENHOAN, TONGTIEN, HAN_THANHTOAN, TRANGTHAI)
            VALUES 
                ('CN-10-2025', 'HD-2025-001', 10, 2025, 38000000, 5200000, 1800000, 0, 0, 45000000, '2025-11-05', N'Chưa thanh toán');
        END
    """))

    # Hóa đơn
    db.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM dbo.HOADON)
        BEGIN
            INSERT INTO dbo.HOADON (MAHOADON, MACN, MAKH, TIENTHUE, TIENDIEN, TIENNUOC, PHIBAOTRI, TIENHOAN, TONGTIEN, SOTIEN, PHUONGTHUC, TRANGTHAI)
            VALUES 
                ('INV-2025-01', 'CN-10-2025', 'KH_STARBUCKS', 38000000, 5200000, 1800000, 0, 0, 45000000, 45000000, N'VNPay', N'Thành công');
        END
    """))


def bootstrap_db(seed: bool = True) -> None:
    # Lệnh tạo bảng qua ORM (có thể bỏ qua nếu bạn đã chạy file DDL bằng SSMS)
    Base.metadata.create_all(bind=engine)
    
    if not seed:
        return

    db: Session = SessionLocal()
    try:
        # Chạy theo thứ tự để không vi phạm Khóa Ngoại (Foreign Keys)
        _seed_rbac_data(db)
        _seed_master_data(db)
        _seed_accounts(db)
        _seed_finance_data(db)
        
        db.commit()
        print("✅ Seed toàn bộ dữ liệu thành công!")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi seed dữ liệu: {str(e)}")
        raise e
    finally:
        db.close()